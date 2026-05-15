"""Pasarela de pago simulada — `HotelPay`.

Imita el comportamiento de una pasarela real (estilo Stripe/MercadoPago):

1. El checkout pide a la pasarela una *sesión de pago* con `crear_sesion()`,
   recibe un `token` opaco y redirige al usuario a la URL de la pasarela.
2. La pasarela muestra su propia UI (con su branding) para capturar la tarjeta.
3. Al enviar, `procesar_pago()` decide aprobar o rechazar según las reglas
   internas (algoritmo de Luhn + tarjetas de prueba) y devuelve un
   `RespuestaPago` con código de autorización.
4. Tras procesar, la pasarela redirige al *callback* configurado en la
   sesión, que confirma o rechaza la reserva.

NOTA: Esto es un mock. No hay conexión a ningún servicio externo, todo
ocurre en memoria/cache de la app.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from django.core.cache import cache


GATEWAY_NAME = "HotelPay"
GATEWAY_VERSION = "1.0-sim"
SESSION_TTL = 60 * 30  # 30 minutos
CACHE_PREFIX = "hotelpay:session:"


# ----------------------------------------------------------------- tarjetas de prueba

TARJETAS_PRUEBA = {
    # número (sin espacios): (resultado, mensaje)
    "4111111111111111": ("aprobado", "Pago aprobado"),
    "5555555555554444": ("aprobado", "Pago aprobado"),
    "4000000000000002": ("rechazado", "Tarjeta rechazada por el banco emisor"),
    "4000000000009995": ("rechazado", "Fondos insuficientes"),
    "4000000000000069": ("rechazado", "Tarjeta vencida"),
}


# ----------------------------------------------------------------- estructuras

@dataclass
class SesionPago:
    token: str
    monto: Decimal
    moneda: str
    descripcion: str
    callback_url: str
    estado: str  # 'creada', 'procesando', 'aprobada', 'rechazada', 'expirada'
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "token": self.token,
            "monto": str(self.monto),
            "moneda": self.moneda,
            "descripcion": self.descripcion,
            "callback_url": self.callback_url,
            "estado": self.estado,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SesionPago":
        return cls(
            token=data["token"],
            monto=Decimal(data["monto"]),
            moneda=data["moneda"],
            descripcion=data["descripcion"],
            callback_url=data["callback_url"],
            estado=data["estado"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class RespuestaPago:
    aprobado: bool
    codigo_autorizacion: str
    mensaje: str
    referencia: str
    ultimos_4: str
    marca: str  # visa, mastercard, amex, otra


# ----------------------------------------------------------------- API pública

def crear_sesion(monto: Decimal, descripcion: str, callback_url: str,
                 metadata: Optional[dict] = None, moneda: str = "USD") -> SesionPago:
    """Crea una sesión de pago y devuelve un token opaco."""
    token = "hp_sess_" + secrets.token_urlsafe(24)
    sesion = SesionPago(
        token=token,
        monto=Decimal(monto),
        moneda=moneda,
        descripcion=descripcion,
        callback_url=callback_url,
        estado="creada",
        metadata=metadata or {},
    )
    cache.set(CACHE_PREFIX + token, sesion.to_dict(), SESSION_TTL)
    return sesion


def obtener_sesion(token: str) -> Optional[SesionPago]:
    raw = cache.get(CACHE_PREFIX + token)
    if not raw:
        return None
    return SesionPago.from_dict(raw)


def actualizar_estado(token: str, nuevo_estado: str) -> None:
    raw = cache.get(CACHE_PREFIX + token)
    if not raw:
        return
    raw["estado"] = nuevo_estado
    cache.set(CACHE_PREFIX + token, raw, SESSION_TTL)


def cerrar_sesion(token: str) -> None:
    cache.delete(CACHE_PREFIX + token)


def procesar_pago(token: str, numero_tarjeta: str, titular: str,
                  expiracion: str, cvv: str, simular_latencia: bool = True) -> RespuestaPago:
    """Procesa el pago. Devuelve siempre una `RespuestaPago` (no lanza)."""
    if simular_latencia:
        time.sleep(0.4)

    numero = (numero_tarjeta or "").replace(" ", "").replace("-", "")
    actualizar_estado(token, "procesando")

    # Reglas: tarjeta de prueba forzada > Luhn
    forzado = TARJETAS_PRUEBA.get(numero)
    if forzado:
        resultado, mensaje = forzado
    elif _luhn_valido(numero):
        resultado, mensaje = "aprobado", "Pago aprobado"
    else:
        resultado, mensaje = "rechazado", "Número de tarjeta inválido"

    aprobado = resultado == "aprobado"
    actualizar_estado(token, "aprobada" if aprobado else "rechazada")

    return RespuestaPago(
        aprobado=aprobado,
        codigo_autorizacion=("AUTH-" + secrets.token_hex(4).upper()) if aprobado else "",
        mensaje=mensaje,
        referencia="HP-" + secrets.token_hex(8).upper(),
        ultimos_4=numero[-4:] if len(numero) >= 4 else "",
        marca=_detectar_marca(numero),
    )


# ----------------------------------------------------------------- helpers

def _luhn_valido(numero: str) -> bool:
    if not numero.isdigit() or not 12 <= len(numero) <= 19:
        return False
    suma = 0
    for i, ch in enumerate(numero[::-1]):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    return suma % 10 == 0


def _detectar_marca(numero: str) -> str:
    if numero.startswith("4"):
        return "visa"
    if numero[:2] in {"51", "52", "53", "54", "55"} or (numero[:4].isdigit() and 2221 <= int(numero[:4]) <= 2720):
        return "mastercard"
    if numero[:2] in {"34", "37"}:
        return "amex"
    return "otra"
