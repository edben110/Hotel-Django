from datetime import date
from decimal import Decimal
import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from habitaciones.models import Habitacion

from . import gateway
from .cart import (
    Carrito,
    ValidacionFechasError,
    validar_disponibilidad,
    validar_fechas,
)
from .forms import (
    AgregarAlCarritoForm,
    BuscarReservaForm,
    CancelarReservaForm,
    DatosClienteForm,
    PagoForm,
)
from .models import Pago, PoliticaCancelacion, Reserva


# ============================ LISTADO PROPIO ============================

def habitaciones_disponibles(request):
    """Listado de habitaciones (con botón reservar) propio de la app reservas."""
    habitaciones = Habitacion.objects.filter(estado='disponible', activa=True).select_related('tipo')
    return render(request, 'reservas/habitaciones_disponibles.html', {
        'habitaciones': habitaciones,
    })


# ============================ CARRITO ============================

@login_required
def agregar_al_carrito(request, habitacion_pk):
    habitacion = get_object_or_404(Habitacion, pk=habitacion_pk, activa=True)

    # Verificar si la habitación ya está en el carrito
    carrito = Carrito(request)
    if carrito.contiene(habitacion_pk):
        messages.warning(request, 'La habitación ya está en el carrito.')
        return redirect('reservas:carrito_detail')

    initial = {
        'fecha_entrada': request.GET.get('fecha_entrada') or '',
        'fecha_salida': request.GET.get('fecha_salida') or '',
    }
    if request.method == 'POST':
        form = AgregarAlCarritoForm(request.POST, habitacion=habitacion)
        if form.is_valid():
            try:
                validar_disponibilidad(
                    habitacion,
                    form.cleaned_data['fecha_entrada'],
                    form.cleaned_data['fecha_salida'],
                )
            except ValidacionFechasError as exc:
                messages.error(request, str(exc))
            else:
                Carrito(request).agregar(
                    habitacion,
                    form.cleaned_data['fecha_entrada'],
                    form.cleaned_data['fecha_salida'],
                    form.cleaned_data['huespedes'],
                )
                messages.success(
                    request,
                    f"Habitación {habitacion.numero} agregada al carrito."
                )
                return redirect('reservas:carrito_detail')
    else:
        form = AgregarAlCarritoForm(initial=initial, habitacion=habitacion)

    return render(request, 'reservas/agregar_al_carrito.html', {
        'form': form,
        'habitacion': habitacion,
    })


@login_required
def carrito_detail(request):
    carrito = Carrito(request)
    items = list(carrito)
    avisos = []
    for item in items:
        try:
            validar_fechas(item.fecha_entrada, item.fecha_salida)
            validar_disponibilidad(item.habitacion, item.fecha_entrada, item.fecha_salida)
        except ValidacionFechasError as exc:
            avisos.append((item, str(exc)))
    return render(request, 'reservas/carrito_detail.html', {
        'items': items,
        'total': carrito.total,
        'avisos': avisos,
    })


@login_required
@require_POST
def carrito_quitar(request, habitacion_pk):
    Carrito(request).quitar(habitacion_pk)
    messages.info(request, "Habitación retirada del carrito.")
    return redirect('reservas:carrito_detail')


@login_required
@require_POST
def carrito_vaciar(request):
    Carrito(request).vaciar()
    messages.info(request, "Carrito vaciado.")
    return redirect('reservas:carrito_detail')


# ============================ CHECKOUT ============================

@login_required
def checkout(request):
    """Recoge datos del cliente, crea las reservas pendientes y abre la pasarela."""
    carrito = Carrito(request)
    items = list(carrito)
    if not items:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('reservas:carrito_detail')

    for item in items:
        try:
            validar_fechas(item.fecha_entrada, item.fecha_salida)
            validar_disponibilidad(item.habitacion, item.fecha_entrada, item.fecha_salida)
        except ValidacionFechasError as exc:
            messages.error(request, f"Habitación {item.habitacion.numero}: {exc}")
            return redirect('reservas:carrito_detail')

    if request.method == 'POST':
        cliente_form = DatosClienteForm(request.POST)
        pago_form = PagoForm(request.POST)
        if cliente_form.is_valid() and pago_form.is_valid():
            reservas = _procesar_checkout(request.user, carrito, items, cliente_form.cleaned_data, pago_form.cleaned_data)
            carrito.vaciar()

            sesion = gateway.crear_sesion(
                monto=sum((r.total for r in reservas), Decimal('0.00')),
                descripcion=f"Reserva(s) Hotel — {len(reservas)} habitación(es)",
                callback_url=request.build_absolute_uri(reverse('reservas:pago_callback')),
                metadata={
                    'reservas': [r.codigo for r in reservas],
                    'cliente': cliente_form.cleaned_data['email'],
                },
            )
            request.session['hotelpay_token'] = sesion.token
            return redirect('reservas:gateway_checkout', token=sesion.token)
    else:
        cliente_form = DatosClienteForm()

    return render(request, 'reservas/checkout.html', {
        'items': items,
        'total': carrito.total,
        'cliente_form': cliente_form,
    })


@transaction.atomic
def _procesar_checkout(usuario, carrito, items, datos_cliente, datos_pago):
    """Crea las reservas, registra el pago simulado y las confirma."""
    creadas = []
    for item in items:
        reserva = Reserva.objects.create(
            usuario=usuario,
            habitacion=item.habitacion,
            nombre_cliente=datos_cliente['nombre'],
            email_cliente=datos_cliente['email'],
            telefono_cliente=datos_cliente.get('telefono', ''),
            fecha_entrada=item.fecha_entrada,
            fecha_salida=item.fecha_salida,
            huespedes=item.huespedes,
            precio_por_noche=item.precio_por_noche,
            total=item.subtotal,
            estado='pendiente',
        )

        ultimos_4 = ''
        if datos_pago['metodo'] == 'tarjeta':
            numero = datos_pago.get('numero_tarjeta') or ''
            ultimos_4 = numero[-4:] if numero else ''

        Pago.objects.create(
            reserva=reserva,
            metodo=datos_pago['metodo'],
            estado='aprobado',
            referencia=f"PAY-{secrets.token_hex(8).upper()}",
            titular=datos_pago.get('titular', ''),
            ultimos_4=ultimos_4,
            monto=reserva.total,
        )

        reserva.estado = 'confirmada'
        reserva.save(update_fields=['estado'])

        # Actualizar estado de la habitación a ocupada
        habitacion = reserva.habitacion
        habitacion.estado = 'ocupada'
        habitacion.save(update_fields=['estado'])

        creadas.append(reserva)
    return creadas


@login_required
def checkout_exito(request):
    codigos = request.session.pop('ultimas_reservas', [])
    if not codigos:
        return redirect('reservas:carrito_detail')

    if sesion.estado in ('aprobada', 'rechazada'):
        return redirect('reservas:gateway_resultado', token=token)

    error = None
    respuesta = None
    form = PagoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        respuesta = gateway.procesar_pago(
            token=token,
            numero_tarjeta=form.cleaned_data['numero_tarjeta'],
            titular=form.cleaned_data['titular'],
            expiracion=form.cleaned_data['expiracion'],
            cvv=form.cleaned_data['cvv'],
        )
        # Redirigimos al callback como haría una pasarela real
        request.session['hotelpay_resultado_' + token] = {
            'aprobado': respuesta.aprobado,
            'codigo_autorizacion': respuesta.codigo_autorizacion,
            'mensaje': respuesta.mensaje,
            'referencia': respuesta.referencia,
            'ultimos_4': respuesta.ultimos_4,
            'marca': respuesta.marca,
        }
        return redirect(reverse('reservas:pago_callback') + f'?token={token}')

    return render(request, 'reservas/gateway_checkout.html', {
        'sesion': sesion,
        'form': form,
        'error': error,
        'gateway_name': gateway.GATEWAY_NAME,
        'gateway_version': gateway.GATEWAY_VERSION,
        'tarjetas_prueba': [
            ('4111 1111 1111 1111', 'Aprobada (Visa)'),
            ('5555 5555 5555 4444', 'Aprobada (Mastercard)'),
            ('4000 0000 0000 0002', 'Rechazada'),
            ('4000 0000 0000 9995', 'Fondos insuficientes'),
        ],
    })


def pago_callback(request):
    """Endpoint que la pasarela invoca tras procesar.

    Lee el resultado de la sesión, registra el `Pago` y confirma o
    cancela las reservas asociadas.
    """
    token = request.GET.get('token') or request.session.get('hotelpay_token')
    if not token:
        return redirect('reservas:carrito_detail')

    sesion = gateway.obtener_sesion(token)
    if not sesion:
        messages.error(request, "Sesión de pago no válida.")
        return redirect('reservas:carrito_detail')

    resultado = request.session.pop('hotelpay_resultado_' + token, None)
    if not resultado:
        # alguien aterrizó sin haber procesado: mandar de vuelta a la pasarela
        return redirect('reservas:gateway_checkout', token=token)

    codigos = sesion.metadata.get('reservas', [])
    reservas = list(Reserva.objects.filter(codigo__in=codigos))

    with transaction.atomic():
        for reserva in reservas:
            Pago.objects.update_or_create(
                reserva=reserva,
                defaults=dict(
                    metodo='tarjeta',
                    estado='aprobado' if resultado['aprobado'] else 'rechazado',
                    referencia=f"{resultado['referencia']}-{reserva.codigo}",
                    titular='',  # no almacenamos PII detallada
                    ultimos_4=resultado['ultimos_4'],
                    monto=reserva.total,
                ),
            )
            reserva.estado = 'confirmada' if resultado['aprobado'] else 'cancelada'
            if not resultado['aprobado']:
                reserva.motivo_cancelacion = f"Pago rechazado: {resultado['mensaje']}"
            reserva.save(update_fields=['estado', 'motivo_cancelacion'])

    request.session['ultimas_reservas'] = codigos
    request.session['ultimo_pago'] = resultado
    gateway.cerrar_sesion(token)
    request.session.pop('hotelpay_token', None)

    return redirect('reservas:gateway_resultado', token=token)


def gateway_resultado(request, token):
    """Muestra el resultado al cliente tras volver de la pasarela."""
    resultado = request.session.pop('ultimo_pago', None)
    codigos = request.session.pop('ultimas_reservas', [])
    if not resultado:
        return redirect('reservas:carrito_detail')

    reservas = Reserva.objects.filter(codigo__in=codigos).select_related(
        'habitacion__tipo', 'pago'
    )
    template = 'reservas/checkout_exito.html' if resultado['aprobado'] else 'reservas/checkout_rechazado.html'
    return render(request, template, {
        'reservas': reservas,
        'resultado': resultado,
        'gateway_name': gateway.GATEWAY_NAME,
    })


# Compatibilidad con el nombre antiguo de URL
def checkout_exito(request):
    return redirect('reservas:carrito_detail')


# ============================ CONSULTA / CANCELACIÓN ============================

def buscar_reserva(request):
    form = BuscarReservaForm(request.GET or None)
    if form.is_valid():
        reserva = Reserva.objects.filter(
            codigo=form.cleaned_data['codigo'],
            email_cliente__iexact=form.cleaned_data['email'],
        ).select_related('habitacion__tipo').first()
        if not reserva:
            messages.error(request, "No encontramos una reserva con esos datos.")
        else:
            return redirect('reservas:reserva_detail', codigo=reserva.codigo)
    return render(request, 'reservas/buscar_reserva.html', {'form': form})


def reserva_detail(request, codigo):
    reserva = get_object_or_404(
        Reserva.objects.select_related('habitacion__tipo', 'pago'),
        codigo=codigo,
    )
    reembolso = reserva.calcular_reembolso() if reserva.puede_cancelarse else Decimal('0.00')
    return render(request, 'reservas/reserva_detail.html', {
        'reserva': reserva,
        'reembolso_estimado': reembolso,
        'politicas': PoliticaCancelacion.objects.filter(activa=True),
    })


@login_required
def cancelar_reserva(request, codigo):
    reserva = get_object_or_404(Reserva, codigo=codigo)

    # Verificar que la reserva pertenece al usuario autenticado
    if reserva.usuario != request.user:
        messages.error(request, "No tienes permiso para cancelar esta reserva.")
        return redirect('reservas:mis_reservas')

    if not reserva.puede_cancelarse:
        messages.warning(request, "Esta reserva ya no puede cancelarse.")
        return redirect('reservas:mis_reservas')

    reembolso = reserva.calcular_reembolso()
    if request.method == 'POST':
        form = CancelarReservaForm(request.POST)
        if form.is_valid():
            from django.utils import timezone
            reserva.estado = 'cancelada'
            reserva.fecha_cancelacion = timezone.now()
            reserva.motivo_cancelacion = form.cleaned_data.get('motivo', '')
            reserva.monto_reembolsado = reembolso
            reserva.save(update_fields=[
                'estado', 'fecha_cancelacion', 'motivo_cancelacion', 'monto_reembolsado',
            ])

            # Restaurar habitación a disponible
            habitacion = reserva.habitacion
            habitacion.estado = 'disponible'
            habitacion.save(update_fields=['estado'])

            messages.success(
                request,
                f"Reserva {reserva.codigo} cancelada. Reembolso: ${reembolso}."
            )
            return redirect('reservas:mis_reservas')
    else:
        form = CancelarReservaForm()

    return render(request, 'reservas/cancelar_reserva.html', {
        'reserva': reserva,
        'form': form,
        'reembolso_estimado': reembolso,
        'politicas': PoliticaCancelacion.objects.filter(activa=True),
    })


# ============================ MIS RESERVAS ============================

@login_required
def mis_reservas(request):
    """Muestra las reservas del usuario autenticado."""
    reservas = Reserva.objects.filter(usuario=request.user).select_related(
        'habitacion__tipo', 'pago'
    )
    return render(request, 'reservas/mis_reservas.html', {'reservas': reservas})
