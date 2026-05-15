from django.urls import path

from . import views

app_name = 'reservas'

urlpatterns = [
    # Listado propio
    path('habitaciones/', views.habitaciones_disponibles, name='habitaciones_disponibles'),

    # Carrito
    path('carrito/', views.carrito_detail, name='carrito_detail'),
    path('carrito/agregar/<int:habitacion_pk>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/quitar/<int:habitacion_pk>/', views.carrito_quitar, name='carrito_quitar'),
    path('carrito/vaciar/', views.carrito_vaciar, name='carrito_vaciar'),

    # Checkout (recoge datos del cliente y abre la pasarela)
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/exito/', views.checkout_exito, name='checkout_exito'),

    # Pasarela simulada HotelPay (callback debe ir antes que <token>)
    path('hotelpay/callback/', views.pago_callback, name='pago_callback'),
    path('hotelpay/<str:token>/resultado/', views.gateway_resultado, name='gateway_resultado'),
    path('hotelpay/<str:token>/', views.gateway_checkout, name='gateway_checkout'),

    # Consulta y cancelación
    path('buscar/', views.buscar_reserva, name='buscar_reserva'),
    path('<str:codigo>/', views.reserva_detail, name='reserva_detail'),
    path('<str:codigo>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
]
