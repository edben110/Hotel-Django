from django import forms
from .models import TipoHabitacion, Habitacion, PrecioTemporada


class TipoHabitacionForm(forms.ModelForm):
    class Meta:
        model = TipoHabitacion
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del tipo'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }


class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'capacidad', 'precio_por_noche', 'estado', 'descripcion', 'imagen']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 101'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'precio_por_noche': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class PrecioTemporadaForm(forms.ModelForm):
    class Meta:
        model = PrecioTemporada
        fields = ['tipo_habitacion', 'temporada', 'precio', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'tipo_habitacion': forms.Select(attrs={'class': 'form-select'}),
            'temporada': forms.Select(attrs={'class': 'form-select'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise forms.ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')

        return cleaned_data


class BusquedaDisponibilidadForm(forms.Form):
    """Formulario para buscar habitaciones disponibles por fecha."""
    fecha_entrada = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_salida = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    tipo = forms.ModelChoiceField(
        queryset=TipoHabitacion.objects.all(),
        required=False,
        empty_label='Todos los tipos',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    capacidad_minima = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mínimo de personas'})
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_entrada = cleaned_data.get('fecha_entrada')
        fecha_salida = cleaned_data.get('fecha_salida')

        if fecha_entrada and fecha_salida and fecha_entrada >= fecha_salida:
            raise forms.ValidationError('La fecha de entrada debe ser anterior a la fecha de salida.')

        return cleaned_data
