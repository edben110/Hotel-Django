from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('datos/', views.dashboard_data, name='dashboard_data'),
    path('reservas/', views.reporte_reservas, name='reporte_reservas'),
    path('clientes/', views.reporte_clientes, name='reporte_clientes'),
    path('habitaciones/', views.reporte_habitaciones, name='reporte_habitaciones'),
    path('reservas/pdf/', views.exportar_reservas_pdf, name='exportar_reservas_pdf'),
    path('reservas/excel/', views.exportar_reservas_excel, name='exportar_reservas_excel'),
    path('clientes/pdf/', views.exportar_clientes_pdf, name='exportar_clientes_pdf'),
    path('clientes/excel/', views.exportar_clientes_excel, name='exportar_clientes_excel'),
    path('habitaciones/pdf/', views.exportar_habitaciones_pdf, name='exportar_habitaciones_pdf'),
    path('habitaciones/excel/', views.exportar_habitaciones_excel, name='exportar_habitaciones_excel'),
]
