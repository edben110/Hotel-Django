from django.urls import path
from . import views

app_name = 'habitaciones'

urlpatterns = [
    # Tipos de habitación
    path('tipos/', views.tipo_list, name='tipo_list'),
    path('tipos/crear/', views.tipo_create, name='tipo_create'),
    path('tipos/<int:pk>/editar/', views.tipo_update, name='tipo_update'),
    path('tipos/<int:pk>/eliminar/', views.tipo_delete, name='tipo_delete'),

    # Habitaciones
    path('', views.habitacion_list, name='habitacion_list'),
    path('<int:pk>/', views.habitacion_detail, name='habitacion_detail'),
    path('crear/', views.habitacion_create, name='habitacion_create'),
    path('<int:pk>/editar/', views.habitacion_update, name='habitacion_update'),
    path('<int:pk>/eliminar/', views.habitacion_delete, name='habitacion_delete'),

    # Precios por temporada
    path('precios/', views.precio_list, name='precio_list'),
    path('precios/crear/', views.precio_create, name='precio_create'),
    path('precios/<int:pk>/editar/', views.precio_update, name='precio_update'),
    path('precios/<int:pk>/eliminar/', views.precio_delete, name='precio_delete'),

    # Búsqueda por disponibilidad
    path('buscar/', views.buscar_disponibilidad, name='buscar_disponibilidad'),
]
