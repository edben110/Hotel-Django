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

    # Checkout / pago simulado
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/exito/', views.checkout_exito, name='checkout_exito'),

    # Consulta y cancelación
    path('buscar/', views.buscar_reserva, name='buscar_reserva'),
    path('<str:codigo>/', views.reserva_detail, name='reserva_detail'),
    path('<str:codigo>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
]
