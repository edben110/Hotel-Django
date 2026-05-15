from django.contrib import admin
from .models import TipoHabitacion, Habitacion, PrecioTemporada


@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ['numero', 'tipo', 'capacidad', 'precio_por_noche', 'estado']
    list_filter = ['tipo', 'estado']
    search_fields = ['numero']


@admin.register(PrecioTemporada)
class PrecioTemporadaAdmin(admin.ModelAdmin):
    list_display = ['tipo_habitacion', 'temporada', 'precio', 'fecha_inicio', 'fecha_fin']
    list_filter = ['temporada', 'tipo_habitacion']
