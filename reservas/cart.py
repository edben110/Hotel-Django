"""Carrito de reservas almacenado en la sesión.

Cada item es un dict con:
    habitacion_id, fecha_entrada (ISO), fecha_salida (ISO), huespedes
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Iterable

from django.db.models import Q

from habitaciones.models import Habitacion
from .models import Reserva


SESSION_KEY = 'reserva_cart'


def _parse(d: str) -> date:
    return datetime.strptime(d, '%Y-%m-%d').date()


class CarritoItem:
    """Wrapper de un item del carrito con datos calculados."""

    def __init__(self, raw: dict, habitacion: Habitacion):
        self.raw = raw
        self.habitacion = habitacion
        self.fecha_entrada = _parse(raw['fecha_entrada'])
        self.fecha_salida = _parse(raw['fecha_salida'])
        self.huespedes = int(raw.get('huespedes', 1))

    @property
    def noches(self) -> int:
        return (self.fecha_salida - self.fecha_entrada).days

    @property
    def precio_por_noche(self) -> Decimal:
        return Decimal(self.habitacion.precio_por_noche)

    @property
    def subtotal(self) -> Decimal:
        return (self.precio_por_noche * self.noches).quantize(Decimal('0.01'))


class Carrito:
    """API de alto nivel para gestionar el carrito en la sesión."""

    def __init__(self, request):
        self.session = request.session
        self._items: list[dict] = self.session.get(SESSION_KEY, [])

    # ---- persistencia ----
    def _save(self) -> None:
        self.session[SESSION_KEY] = self._items
        self.session.modified = True

    def vaciar(self) -> None:
        self._items = []
        self._save()

    # ---- consultas ----
    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterable[CarritoItem]:
        if not self._items:
            return iter([])
        ids = [int(i['habitacion_id']) for i in self._items]
        habitaciones = {h.pk: h for h in Habitacion.objects.filter(pk__in=ids).select_related('tipo')}
        return iter(
            CarritoItem(raw, habitaciones[int(raw['habitacion_id'])])
            for raw in self._items
            if int(raw['habitacion_id']) in habitaciones
        )

    @property
    def total(self) -> Decimal:
        return sum((item.subtotal for item in self), Decimal('0.00'))

    def contiene(self, habitacion_id: int) -> bool:
        return any(int(i['habitacion_id']) == int(habitacion_id) for i in self._items)

    # ---- modificación ----
    def agregar(self, habitacion: Habitacion, fecha_entrada: date,
                fecha_salida: date, huespedes: int = 1) -> None:
        # quita previos para la misma habitación
        self._items = [i for i in self._items if int(i['habitacion_id']) != habitacion.pk]
        self._items.append({
            'habitacion_id': habitacion.pk,
            'fecha_entrada': fecha_entrada.isoformat(),
            'fecha_salida': fecha_salida.isoformat(),
            'huespedes': int(huespedes),
        })
        self._save()

    def quitar(self, habitacion_id: int) -> None:
        self._items = [i for i in self._items if int(i['habitacion_id']) != int(habitacion_id)]
        self._save()


# ----------------- validaciones -----------------

class ValidacionFechasError(Exception):
    """Se lanza cuando las fechas del carrito no son válidas."""


def validar_fechas(fecha_entrada: date, fecha_salida: date,
                   hoy: date | None = None) -> None:
    hoy = hoy or date.today()
    if fecha_entrada < hoy:
        raise ValidacionFechasError("La fecha de entrada no puede estar en el pasado.")
    if fecha_salida <= fecha_entrada:
        raise ValidacionFechasError("La fecha de salida debe ser posterior a la de entrada.")


def hay_solapamiento(habitacion: Habitacion, fecha_entrada: date,
                     fecha_salida: date, excluir_pk: int | None = None) -> bool:
    """¿La habitación ya tiene reservas activas que choquen con el rango?"""
    qs = Reserva.objects.filter(
        habitacion=habitacion,
        estado__in=['pendiente', 'confirmada'],
    ).filter(
        Q(fecha_entrada__lt=fecha_salida) & Q(fecha_salida__gt=fecha_entrada)
    )
    if excluir_pk:
        qs = qs.exclude(pk=excluir_pk)
    return qs.exists()


def validar_disponibilidad(habitacion: Habitacion, fecha_entrada: date,
                           fecha_salida: date) -> None:
    if habitacion.estado != 'disponible':
        raise ValidacionFechasError(
            f"La habitación {habitacion.numero} no está disponible "
            f"({habitacion.get_estado_display().lower()})."
        )
    if hay_solapamiento(habitacion, fecha_entrada, fecha_salida):
        raise ValidacionFechasError(
            f"La habitación {habitacion.numero} ya está reservada en esas fechas."
        )
