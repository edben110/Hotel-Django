from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Max, Min, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from habitaciones.models import Habitacion
from reservas.models import Reserva


RESERVA_ESTADOS_ACTIVOS = ['pendiente', 'confirmada', 'completada']
RESERVA_ESTADOS_OCUPACION = ['confirmada', 'completada']


def obtener_metricas_dashboard() -> dict:
    hoy = timezone.localdate()
    total_habitaciones = Habitacion.objects.filter(activa=True).count()
    total_reservas = Reserva.objects.count()
    reservas_activas = Reserva.objects.filter(estado__in=['pendiente', 'confirmada']).count()
    reservas_canceladas = Reserva.objects.filter(estado='cancelada').count()
    habitaciones_disponibles = Habitacion.objects.filter(estado='disponible', activa=True).count()
    habitaciones_ocupadas = Habitacion.objects.filter(estado='ocupada', activa=True).count()
    total_clientes = Reserva.objects.values('nombre_cliente', 'email_cliente').distinct().count()

    reservas_activas_hoy = Reserva.objects.filter(
        estado__in=RESERVA_ESTADOS_OCUPACION,
        fecha_entrada__lte=hoy,
        fecha_salida__gt=hoy,
    ).values('habitacion_id').distinct().count()

    tasa_ocupacion_general = Decimal('0.00')
    if total_habitaciones:
        tasa_ocupacion_general = (Decimal(reservas_activas_hoy) / Decimal(total_habitaciones) * Decimal('100')).quantize(Decimal('0.01'))

    return {
        'total_clientes': total_clientes,
        'total_habitaciones': total_habitaciones,
        'total_reservas': total_reservas,
        'reservas_activas': reservas_activas,
        'reservas_canceladas': reservas_canceladas,
        'habitaciones_disponibles': habitaciones_disponibles,
        'habitaciones_ocupadas': habitaciones_ocupadas,
        'tasa_ocupacion_general': tasa_ocupacion_general,
    }


def obtener_actividad_reciente() -> dict:
    reservas_recientes = list(
        Reserva.objects.select_related('habitacion__tipo').order_by('-fecha_creacion')[:5]
    )

    clientes_recientes = []
    vistos = set()
    for reserva in Reserva.objects.order_by('-fecha_creacion').only('nombre_cliente', 'email_cliente', 'fecha_creacion'):
        clave = (reserva.nombre_cliente.lower(), reserva.email_cliente.lower())
        if clave in vistos:
            continue
        vistos.add(clave)
        clientes_recientes.append(reserva)
        if len(clientes_recientes) == 5:
            break

    cambios_recientes = list(
        Habitacion.objects.select_related('tipo').order_by('-fecha_actualizacion')[:5]
    )
    cancelaciones_recientes = list(
        Reserva.objects.filter(fecha_cancelacion__isnull=False).select_related('habitacion__tipo').order_by('-fecha_cancelacion')[:5]
    )

    return {
        'reservas_recientes': reservas_recientes,
        'clientes_recientes': clientes_recientes,
        'cambios_recientes': cambios_recientes,
        'cancelaciones_recientes': cancelaciones_recientes,
    }


def obtener_datos_dashboard() -> dict:
    return {
        'reservas_por_mes': _reservas_por_mes(),
        'ocupacion_por_mes': _ocupacion_por_mes(),
        'habitaciones_mas_reservadas': _habitaciones_mas_reservadas(),
        'estado_reservas': _estado_reservas(),
        'clientes_mas_reservas': _clientes_mas_reservas(),
    }


def _reservas_por_mes() -> dict:
    datos = (
        Reserva.objects.annotate(mes=TruncMonth('fecha_creacion'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    labels = []
    values = []
    for fila in datos:
        mes = fila['mes']
        if mes is None:
            continue
        labels.append(mes.strftime('%b %Y'))
        values.append(int(fila['total']))
    return {'labels': labels, 'values': values}


def _ocupacion_por_mes() -> dict:
    total_habitaciones = Habitacion.objects.filter(activa=True).count()
    meses = _ultimos_meses(12)
    reservas = list(
        Reserva.objects.filter(
            estado__in=RESERVA_ESTADOS_OCUPACION,
            fecha_salida__gt=meses[0]['inicio'],
            fecha_entrada__lt=meses[-1]['fin'],
        ).only('fecha_entrada', 'fecha_salida')
    )

    labels = []
    values = []
    for mes in meses:
        dias_mes = (mes['fin'] - mes['inicio']).days
        noches_reservadas = 0
        for reserva in reservas:
            inicio = max(reserva.fecha_entrada, mes['inicio'])
            fin = min(reserva.fecha_salida, mes['fin'])
            if inicio < fin:
                noches_reservadas += (fin - inicio).days
        capacidad_total = total_habitaciones * dias_mes
        porcentaje = Decimal('0.00')
        if capacidad_total:
            porcentaje = (Decimal(noches_reservadas) / Decimal(capacidad_total) * Decimal('100')).quantize(Decimal('0.01'))
        labels.append(mes['inicio'].strftime('%b %Y'))
        values.append(float(porcentaje))
    return {'labels': labels, 'values': values}


def _habitaciones_mas_reservadas() -> dict:
    datos = (
        Habitacion.objects.select_related('tipo')
        .annotate(
            reservas_validas=Count(
                'reservas',
                filter=Q(reservas__estado__in=RESERVA_ESTADOS_ACTIVOS),
            )
        )
        .order_by('-reservas_validas', 'numero')[:5]
    )
    labels = [f'Habitación {habitacion.numero}' for habitacion in datos]
    values = [int(habitacion.reservas_validas) for habitacion in datos]
    return {'labels': labels, 'values': values}


def _estado_reservas() -> dict:
    datos = Reserva.objects.values('estado').annotate(total=Count('id')).order_by('estado')
    etiquetas = dict(Reserva.ESTADO_CHOICES)
    labels = []
    values = []
    for fila in datos:
        labels.append(etiquetas.get(fila['estado'], fila['estado'].title()))
        values.append(int(fila['total']))
    return {'labels': labels, 'values': values}


def _clientes_mas_reservas() -> dict:
    datos = (
        Reserva.objects.values('nombre_cliente', 'email_cliente')
        .annotate(total_reservas=Count('id'), total_gastado=Sum('total'))
        .order_by('-total_reservas', '-total_gastado', 'nombre_cliente')[:5]
    )
    labels = [f"{fila['nombre_cliente']} ({fila['email_cliente']})" for fila in datos]
    values = [int(fila['total_reservas']) for fila in datos]
    return {'labels': labels, 'values': values}


def _ultimos_meses(cantidad: int) -> list[dict]:
    hoy = timezone.localdate()
    primero_del_mes = hoy.replace(day=1)
    meses = []
    for indice in range(cantidad - 1, -1, -1):
        anio = primero_del_mes.year
        mes = primero_del_mes.month - indice
        while mes <= 0:
            mes += 12
            anio -= 1
        inicio = date(anio, mes, 1)
        fin_mes = monthrange(anio, mes)[1]
        fin = date(anio, mes, fin_mes) + timedelta(days=1)
        meses.append({'inicio': inicio, 'fin': fin})
    return meses


def filtrar_reservas(queryset, cleaned_data):
    fecha_inicio = cleaned_data.get('fecha_inicio')
    fecha_fin = cleaned_data.get('fecha_fin')
    estado_reserva = cleaned_data.get('estado_reserva')
    cliente = (cleaned_data.get('cliente') or '').strip()
    habitacion = cleaned_data.get('habitacion')
    tipo_habitacion = cleaned_data.get('tipo_habitacion')
    estado_habitacion = cleaned_data.get('estado_habitacion')

    if fecha_inicio:
        queryset = queryset.filter(fecha_salida__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_entrada__lte=fecha_fin)
    if estado_reserva:
        queryset = queryset.filter(estado=estado_reserva)
    if cliente:
        queryset = queryset.filter(
            Q(nombre_cliente__icontains=cliente) | Q(email_cliente__icontains=cliente)
        )
    if habitacion:
        queryset = queryset.filter(habitacion=habitacion)
    if tipo_habitacion:
        queryset = queryset.filter(habitacion__tipo=tipo_habitacion)
    if estado_habitacion:
        queryset = queryset.filter(habitacion__estado=estado_habitacion)
    return queryset


def construir_filas_clientes(queryset):
    datos = (
        queryset.values('nombre_cliente', 'email_cliente')
        .annotate(
            total_reservas=Count('id'),
            total_gastado=Sum('total'),
            primera_reserva=Min('fecha_creacion'),
            ultima_reserva=Max('fecha_creacion'),
        )
        .order_by('-total_reservas', '-total_gastado', 'nombre_cliente')
    )
    filas = []
    for fila in datos:
        filas.append({
            'nombre_cliente': fila['nombre_cliente'],
            'email_cliente': fila['email_cliente'],
            'total_reservas': fila['total_reservas'],
            'total_gastado': fila['total_gastado'] or Decimal('0.00'),
            'primera_reserva': fila['primera_reserva'],
            'ultima_reserva': fila['ultima_reserva'],
        })
    return filas
