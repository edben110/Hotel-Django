from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import TipoHabitacion, Habitacion, PrecioTemporada
from .forms import (
    TipoHabitacionForm,
    HabitacionForm,
    PrecioTemporadaForm,
    BusquedaDisponibilidadForm,
)


# ===================== TIPO DE HABITACIÓN =====================

def tipo_list(request):
    tipos = TipoHabitacion.objects.all()
    return render(request, 'habitaciones/tipo_list.html', {'tipos': tipos})


def tipo_create(request):
    if request.method == 'POST':
        form = TipoHabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de habitación creado exitosamente.')
            return redirect('habitaciones:tipo_list')
    else:
        form = TipoHabitacionForm()
    return render(request, 'habitaciones/tipo_form.html', {'form': form, 'titulo': 'Crear Tipo de Habitación'})


def tipo_update(request, pk):
    tipo = get_object_or_404(TipoHabitacion, pk=pk)
    if request.method == 'POST':
        form = TipoHabitacionForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de habitación actualizado exitosamente.')
            return redirect('habitaciones:tipo_list')
    else:
        form = TipoHabitacionForm(instance=tipo)
    return render(request, 'habitaciones/tipo_form.html', {'form': form, 'titulo': 'Editar Tipo de Habitación'})


def tipo_delete(request, pk):
    tipo = get_object_or_404(TipoHabitacion, pk=pk)
    if request.method == 'POST':
        try:
            tipo.delete()
            messages.success(request, 'Tipo de habitación eliminado exitosamente.')
        except Exception:
            messages.error(request, 'No se puede eliminar este tipo porque tiene habitaciones asociadas.')
        return redirect('habitaciones:tipo_list')
    return render(request, 'habitaciones/tipo_confirm_delete.html', {'tipo': tipo})


# ===================== HABITACIÓN =====================

def habitacion_list(request):
    habitaciones = Habitacion.objects.select_related('tipo').all()
    return render(request, 'habitaciones/habitacion_list.html', {'habitaciones': habitaciones})


def habitacion_detail(request, pk):
    habitacion = get_object_or_404(Habitacion.objects.select_related('tipo'), pk=pk)
    return render(request, 'habitaciones/habitacion_detail.html', {'habitacion': habitacion})


def habitacion_create(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación creada exitosamente.')
            return redirect('habitaciones:habitacion_list')
    else:
        form = HabitacionForm()
    return render(request, 'habitaciones/habitacion_form.html', {'form': form, 'titulo': 'Crear Habitación'})


def habitacion_update(request, pk):
    habitacion = get_object_or_404(Habitacion, pk=pk)
    if request.method == 'POST':
        form = HabitacionForm(request.POST, request.FILES, instance=habitacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación actualizada exitosamente.')
            return redirect('habitaciones:habitacion_list')
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, 'habitaciones/habitacion_form.html', {'form': form, 'titulo': 'Editar Habitación'})


def habitacion_delete(request, pk):
    habitacion = get_object_or_404(Habitacion, pk=pk)
    if request.method == 'POST':
        habitacion.delete()
        messages.success(request, 'Habitación eliminada exitosamente.')
        return redirect('habitaciones:habitacion_list')
    return render(request, 'habitaciones/habitacion_confirm_delete.html', {'habitacion': habitacion})


# ===================== PRECIO POR TEMPORADA =====================

def precio_list(request):
    precios = PrecioTemporada.objects.select_related('tipo_habitacion').all()
    return render(request, 'habitaciones/precio_list.html', {'precios': precios})


def precio_create(request):
    if request.method == 'POST':
        form = PrecioTemporadaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Precio por temporada creado exitosamente.')
            return redirect('habitaciones:precio_list')
    else:
        form = PrecioTemporadaForm()
    return render(request, 'habitaciones/precio_form.html', {'form': form, 'titulo': 'Crear Precio por Temporada'})


def precio_update(request, pk):
    precio = get_object_or_404(PrecioTemporada, pk=pk)
    if request.method == 'POST':
        form = PrecioTemporadaForm(request.POST, instance=precio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Precio por temporada actualizado exitosamente.')
            return redirect('habitaciones:precio_list')
    else:
        form = PrecioTemporadaForm(instance=precio)
    return render(request, 'habitaciones/precio_form.html', {'form': form, 'titulo': 'Editar Precio por Temporada'})


def precio_delete(request, pk):
    precio = get_object_or_404(PrecioTemporada, pk=pk)
    if request.method == 'POST':
        precio.delete()
        messages.success(request, 'Precio por temporada eliminado exitosamente.')
        return redirect('habitaciones:precio_list')
    return render(request, 'habitaciones/precio_confirm_delete.html', {'precio': precio})


# ===================== BÚSQUEDA POR DISPONIBILIDAD =====================

def buscar_disponibilidad(request):
    form = BusquedaDisponibilidadForm(request.GET or None)
    habitaciones = None

    if form.is_valid():
        fecha_entrada = form.cleaned_data['fecha_entrada']
        fecha_salida = form.cleaned_data['fecha_salida']
        tipo = form.cleaned_data.get('tipo')
        capacidad_minima = form.cleaned_data.get('capacidad_minima')

        # Filtrar habitaciones disponibles
        habitaciones = Habitacion.objects.filter(estado='disponible')

        if tipo:
            habitaciones = habitaciones.filter(tipo=tipo)

        if capacidad_minima:
            habitaciones = habitaciones.filter(capacidad__gte=capacidad_minima)

        # Excluir habitaciones con reservas activas en el rango de fechas
        habitaciones = habitaciones.exclude(
            reservas__fecha_entrada__lt=fecha_salida,
            reservas__fecha_salida__gt=fecha_entrada,
            reservas__estado__in=['pendiente', 'confirmada']
        )

    return render(request, 'habitaciones/buscar_disponibilidad.html', {
        'form': form,
        'habitaciones': habitaciones,
    })
