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
| `/reservas/checkout/`                | Pago simulado                            |
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

- Valida número de tarjeta con algoritmo de Luhn
- Verifica vigencia (MM/AA), CVV de 3-4 dígitos
- Genera `referencia` única (`PAY-XXXXXXXX`)
- Crea `Pago` aprobado y confirma la `Reserva` en una transacción atómica

## Tests

```bash
python3 manage.py test reservas
```
