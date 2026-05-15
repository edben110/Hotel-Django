# App `reservas` — Daniel

Cubre los puntos 4, 8 y 10 del proyecto:

- **4. Carrito de reserva con validación de fechas**
- **8. Cancelación de reservas con política definida**
- **10. Integración con pasarela de pago simulada**

## Estructura

```
reservas/
├── models.py              Reserva, Pago, PoliticaCancelacion
├── cart.py                Carrito en sesión + validaciones
├── forms.py               Formularios (carrito, cliente, pago, cancelación)
├── views.py               Vistas del flujo completo
├── urls.py                Rutas montadas en /reservas/
├── admin.py               Registro en el admin de Django
├── context_processors.py  Expone carrito_count al template (opcional)
├── templates/reservas/    Templates Bootstrap 5
└── tests.py               6 pruebas funcionales
```

## URLs principales

| URL                                  | Descripción                              |
|--------------------------------------|------------------------------------------|
| `/reservas/habitaciones/`            | Listado de disponibles + botón Reservar  |
| `/reservas/carrito/`                 | Detalle del carrito                      |
| `/reservas/carrito/agregar/<pk>/`    | Agregar habitación al carrito            |
| `/reservas/checkout/`                | Datos del cliente, abre la pasarela      |
| `/reservas/hotelpay/<token>/`        | UI de la pasarela HotelPay (simulada)    |
| `/reservas/hotelpay/callback/`       | Callback que confirma/cancela            |
| `/reservas/buscar/`                  | Buscar reserva por código + email        |
| `/reservas/<codigo>/`                | Detalle de la reserva                    |
| `/reservas/<codigo>/cancelar/`       | Cancelar con política                    |

## Integración mínima

En `Hotel/settings.py`:

```python
INSTALLED_APPS = [
    ...,
    'reservas',
]
```

En `Hotel/urls.py`:

```python
path('reservas/', include('reservas.urls')),
```

(Opcional) Para mostrar el contador del carrito en el navbar global, añadir
`'reservas.context_processors.carrito'` a `TEMPLATES.OPTIONS.context_processors`.

## Pasarela simulada — `HotelPay`

La pasarela vive en `reservas/gateway.py` y se comporta como una real:

1. El `checkout` recoge datos del cliente, crea las reservas en estado
   `pendiente` y abre una **sesión de pago** vía `gateway.crear_sesion()`.
2. El usuario es redirigido a `/reservas/hotelpay/<token>/`, una pantalla
   con su propio branding ("HotelPay"), aviso de modo simulación,
   tarjetas de prueba y formulario de tarjeta.
3. Al enviar, `gateway.procesar_pago()` aplica las reglas (tarjetas de
   prueba forzadas + algoritmo de Luhn) y devuelve un `RespuestaPago`
   con `codigo_autorizacion`, `referencia`, `marca` y `ultimos_4`.
4. La pasarela redirige al **callback** `/reservas/hotelpay/callback/`,
   que registra el `Pago`, confirma o cancela las reservas y muestra
   el resultado.

### Tarjetas de prueba

| Número                | Resultado            |
|-----------------------|----------------------|
| 4111 1111 1111 1111   | Aprobada (Visa)      |
| 5555 5555 5555 4444   | Aprobada (Mastercard)|
| 4000 0000 0000 0002   | Rechazada            |
| 4000 0000 0000 9995   | Fondos insuficientes |
| 4000 0000 0000 0069   | Tarjeta vencida      |

Cualquier otra tarjeta válida según Luhn se aprueba; las que fallan Luhn
se rechazan.

## Política de cancelación

Configurable desde el admin (`PoliticaCancelacion`). Ejemplo sugerido:

| Anticipación | Reembolso |
|--------------|-----------|
| 7+ días      | 100%      |
| 3+ días      | 50%       |
| 0+ días      | 0%        |

Al cancelar, se elige la política con `dias_anticipacion <= dias_restantes`
de mayor `dias_anticipacion`.

## Pasarela simulada

- Módulo `reservas/gateway.py` (`HotelPay v1.0-sim`) con su propia API:
  `crear_sesion`, `obtener_sesion`, `procesar_pago`, `cerrar_sesion`.
- UI dedicada con branding propio en `/reservas/hotelpay/<token>/`.
- Sesiones efímeras en `cache` con TTL de 30 minutos.
- Soporta tarjetas de prueba con resultado forzado (aprobado/rechazado).
- Valida número con algoritmo de Luhn y detecta marca (Visa, Mastercard, Amex).
- Genera `referencia` y `codigo_autorizacion` únicos.
- Redirige a callback que confirma `Reserva` o la cancela según resultado.

## Tests

```bash
python3 manage.py test reservas
```
