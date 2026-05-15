from django.contrib import admin

from .models import Pago, PoliticaCancelacion, Reserva


@admin.register(PoliticaCancelacion)
class PoliticaCancelacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dias_anticipacion', 'porcentaje_reembolso', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)


class PagoInline(admin.StackedInline):
    model = Pago
    extra = 0
    readonly_fields = ('referencia', 'fecha')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'habitacion', 'nombre_cliente', 'fecha_entrada',
        'fecha_salida', 'estado', 'total',
    )
    list_filter = ('estado', 'fecha_entrada')
    search_fields = ('codigo', 'nombre_cliente', 'email_cliente')
    date_hierarchy = 'fecha_entrada'
    readonly_fields = ('codigo', 'fecha_creacion', 'fecha_cancelacion', 'monto_reembolsado')
    inlines = [PagoInline]


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('referencia', 'reserva', 'metodo', 'estado', 'monto', 'fecha')
    list_filter = ('estado', 'metodo')
    search_fields = ('referencia', 'reserva__codigo')
