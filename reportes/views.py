from __future__ import annotations

from io import BytesIO

import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from habitaciones.models import Habitacion
from reservas.models import Reserva

from .forms import FiltrosReporteForm
from .services import (
    construir_filas_clientes,
    filtrar_reservas,
    obtener_actividad_reciente,
    obtener_datos_dashboard,
    obtener_metricas_dashboard,
)


def dashboard(request):
    return render(request, 'reportes/dashboard.html', {
        'metricas': obtener_metricas_dashboard(),
        'actividad': obtener_actividad_reciente(),
        'dashboard_data_url': reverse('reportes:dashboard_data'),
    })


def dashboard_data(request):
    return JsonResponse(obtener_datos_dashboard())


def reporte_reservas(request):
    form = FiltrosReporteForm(request.GET or None)
    reservas = Reserva.objects.select_related('habitacion__tipo', 'pago')
    if form.is_valid():
        reservas = filtrar_reservas(reservas, form.cleaned_data)
    else:
        form = FiltrosReporteForm()
    reservas = reservas.order_by('-fecha_creacion')
    return render(request, 'reportes/reporte_listado.html', {
        'titulo': 'Reporte de Reservas',
        'form': form,
        'modo': 'reservas',
        'reservas': reservas,
        'export_pdf_url': reverse('reportes:exportar_reservas_pdf'),
        'export_excel_url': reverse('reportes:exportar_reservas_excel'),
        'total_registros': reservas.count(),
    })


def reporte_clientes(request):
    form = FiltrosReporteForm(request.GET or None)
    reservas = Reserva.objects.select_related('habitacion__tipo', 'pago')
    if form.is_valid():
        reservas = filtrar_reservas(reservas, form.cleaned_data)
    else:
        form = FiltrosReporteForm()
    filas = construir_filas_clientes(reservas)
    return render(request, 'reportes/reporte_listado.html', {
        'titulo': 'Reporte de Clientes',
        'form': form,
        'modo': 'clientes',
        'filas_clientes': filas,
        'export_pdf_url': reverse('reportes:exportar_clientes_pdf'),
        'export_excel_url': reverse('reportes:exportar_clientes_excel'),
        'total_registros': len(filas),
    })


def reporte_habitaciones(request):
    form = FiltrosReporteForm(request.GET or None)
    habitaciones = Habitacion.objects.select_related('tipo').prefetch_related('reservas')
    reservas = Reserva.objects.select_related('habitacion__tipo')
    if form.is_valid():
        reservas = filtrar_reservas(reservas, form.cleaned_data)
        ids_habitaciones = reservas.values_list('habitacion_id', flat=True).distinct()
        habitaciones = habitaciones.filter(pk__in=ids_habitaciones)
        if form.cleaned_data.get('estado_habitacion'):
            habitaciones = Habitacion.objects.select_related('tipo').filter(estado=form.cleaned_data['estado_habitacion'])
    else:
        form = FiltrosReporteForm()

    filas = []
    reservas_por_habitacion = {}
    for reserva in reservas:
        reservas_por_habitacion.setdefault(reserva.habitacion_id, 0)
        reservas_por_habitacion[reserva.habitacion_id] += 1

    for habitacion in habitaciones.order_by('numero'):
        filas.append({
            'habitacion': habitacion,
            'total_reservas': reservas_por_habitacion.get(habitacion.pk, 0),
        })

    return render(request, 'reportes/reporte_listado.html', {
        'titulo': 'Reporte de Habitaciones',
        'form': form,
        'modo': 'habitaciones',
        'filas_habitaciones': filas,
        'export_pdf_url': reverse('reportes:exportar_habitaciones_pdf'),
        'export_excel_url': reverse('reportes:exportar_habitaciones_excel'),
        'total_registros': len(filas),
    })


def exportar_reservas_pdf(request):
    reservas = _filtrar_reservas_request(request)
    filas = [
        [
            reserva.codigo,
            reserva.nombre_cliente,
            reserva.email_cliente,
            reserva.habitacion.numero,
            reserva.habitacion.tipo.nombre,
            reserva.fecha_creacion.strftime('%Y-%m-%d %H:%M'),
            reserva.fecha_entrada.strftime('%Y-%m-%d'),
            reserva.fecha_salida.strftime('%Y-%m-%d'),
            reserva.get_estado_display(),
            f'{reserva.total}',
        ]
        for reserva in reservas
    ]
    encabezados = ['Código', 'Cliente', 'Email', 'Habitación', 'Tipo', 'Creación', 'Ingreso', 'Salida', 'Estado', 'Total']
    return _generar_pdf('Reporte de Reservas', encabezados, filas, 'reporte_reservas.pdf')


def exportar_reservas_excel(request):
    reservas = _filtrar_reservas_request(request)
    dataframe = pd.DataFrame([
        {
            'codigo': reserva.codigo,
            'cliente': reserva.nombre_cliente,
            'email': reserva.email_cliente,
            'habitacion': reserva.habitacion.numero,
            'tipo_habitacion': reserva.habitacion.tipo.nombre,
            'fecha_reserva': reserva.fecha_creacion,
            'fecha_ingreso': reserva.fecha_entrada,
            'fecha_salida': reserva.fecha_salida,
            'estado': reserva.get_estado_display(),
            'total': float(reserva.total),
        }
        for reserva in reservas
    ])
    return _generar_excel(dataframe, 'reporte_reservas.xlsx')


def exportar_clientes_pdf(request):
    filas = construir_filas_clientes(_filtrar_reservas_request(request))
    encabezados = ['Cliente', 'Email', 'Total reservas', 'Total gastado', 'Primera reserva', 'Última reserva']
    tabla = [
        [
            fila['nombre_cliente'],
            fila['email_cliente'],
            fila['total_reservas'],
            f"{fila['total_gastado']}",
            fila['primera_reserva'].strftime('%Y-%m-%d %H:%M') if fila['primera_reserva'] else '',
            fila['ultima_reserva'].strftime('%Y-%m-%d %H:%M') if fila['ultima_reserva'] else '',
        ]
        for fila in filas
    ]
    return _generar_pdf('Reporte de Clientes', encabezados, tabla, 'reporte_clientes.pdf')


def exportar_clientes_excel(request):
    filas = construir_filas_clientes(_filtrar_reservas_request(request))
    dataframe = pd.DataFrame([{
        'cliente': fila['nombre_cliente'],
        'email': fila['email_cliente'],
        'total_reservas': fila['total_reservas'],
        'total_gastado': float(fila['total_gastado']),
        'primera_reserva': fila['primera_reserva'],
        'ultima_reserva': fila['ultima_reserva'],
    } for fila in filas])
    return _generar_excel(dataframe, 'reporte_clientes.xlsx')


def exportar_habitaciones_pdf(request):
    filas = _filas_habitaciones(_filtrar_reservas_request(request))
    encabezados = ['Habitación', 'Tipo', 'Estado', 'Capacidad', 'Precio/Noche', 'Reservas']
    tabla = [
        [
            fila['habitacion'].numero,
            fila['habitacion'].tipo.nombre,
            fila['habitacion'].get_estado_display(),
            fila['habitacion'].capacidad,
            f'{fila["habitacion"].precio_por_noche}',
            fila['total_reservas'],
        ]
        for fila in filas
    ]
    return _generar_pdf('Reporte de Habitaciones', encabezados, tabla, 'reporte_habitaciones.pdf')


def exportar_habitaciones_excel(request):
    filas = _filas_habitaciones(_filtrar_reservas_request(request))
    dataframe = pd.DataFrame([{
        'habitacion': fila['habitacion'].numero,
        'tipo': fila['habitacion'].tipo.nombre,
        'estado': fila['habitacion'].get_estado_display(),
        'capacidad': fila['habitacion'].capacidad,
        'precio_por_noche': float(fila['habitacion'].precio_por_noche),
        'total_reservas': fila['total_reservas'],
    } for fila in filas])
    return _generar_excel(dataframe, 'reporte_habitaciones.xlsx')


def _filtrar_reservas_request(request):
    form = FiltrosReporteForm(request.GET or None)
    reservas = Reserva.objects.select_related('habitacion__tipo', 'pago')
    if form.is_valid():
        reservas = filtrar_reservas(reservas, form.cleaned_data)
    return reservas.order_by('-fecha_creacion')


def _filas_habitaciones(reservas):
    habitaciones = Habitacion.objects.select_related('tipo').prefetch_related('reservas')
    ids_habitaciones = reservas.values_list('habitacion_id', flat=True).distinct()
    if ids_habitaciones:
        habitaciones = habitaciones.filter(pk__in=ids_habitaciones)
    reservas_por_habitacion = {}
    for reserva in reservas:
        reservas_por_habitacion.setdefault(reserva.habitacion_id, 0)
        reservas_por_habitacion[reserva.habitacion_id] += 1
    filas = []
    for habitacion in habitaciones.order_by('numero'):
        filas.append({
            'habitacion': habitacion,
            'total_reservas': reservas_por_habitacion.get(habitacion.pk, 0),
        })
    return filas


def _generar_pdf(titulo, encabezados, filas, nombre_archivo):
    buffer = BytesIO()
    documento = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
    estilos = getSampleStyleSheet()
    elementos = [Paragraph(titulo, estilos['Title']), Spacer(1, 12)]
    tabla = Table([encabezados] + filas, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e2e8f0')]),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elementos.append(tabla)
    documento.build(elementos)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response


def _generar_excel(dataframe, nombre_archivo):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Reporte')
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response
