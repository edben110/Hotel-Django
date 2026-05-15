from django import forms

from habitaciones.models import Habitacion, TipoHabitacion
from reservas.models import Reserva


class FiltrosReporteForm(forms.Form):
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    estado_reserva = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + Reserva.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre o correo del cliente',
        })
    )
    habitacion = forms.ModelChoiceField(
        required=False,
        queryset=Habitacion.objects.select_related('tipo').all(),
        empty_label='Todas las habitaciones',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo_habitacion = forms.ModelChoiceField(
        required=False,
        queryset=TipoHabitacion.objects.all(),
        empty_label='Todos los tipos',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado_habitacion = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + Habitacion.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
