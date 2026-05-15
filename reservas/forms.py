from datetime import date

from django import forms

from .cart import validar_fechas, ValidacionFechasError


class AgregarAlCarritoForm(forms.Form):
    fecha_entrada = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_salida = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    huespedes = forms.IntegerField(
        min_value=1, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
    )

    def __init__(self, *args, habitacion=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.habitacion = habitacion
        if habitacion is not None:
            self.fields['huespedes'].widget.attrs['max'] = habitacion.capacidad

    def clean(self):
        cleaned = super().clean()
        fe, fs = cleaned.get('fecha_entrada'), cleaned.get('fecha_salida')
        if fe and fs:
            try:
                validar_fechas(fe, fs)
            except ValidacionFechasError as exc:
                raise forms.ValidationError(str(exc))
        huespedes = cleaned.get('huespedes')
        if self.habitacion and huespedes and huespedes > self.habitacion.capacidad:
            raise forms.ValidationError(
                f"La habitación {self.habitacion.numero} solo admite "
                f"{self.habitacion.capacidad} huésped(es)."
            )
        return cleaned


class DatosClienteForm(forms.Form):
    nombre = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class PagoForm(forms.Form):
    METODO_CHOICES = [
        ('tarjeta', 'Tarjeta de crédito/débito'),
        ('paypal', 'PayPal (simulado)'),
    ]

    metodo = forms.ChoiceField(
        choices=METODO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    titular = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Como aparece en la tarjeta'})
    )
    numero_tarjeta = forms.CharField(
        max_length=23, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': '4111 1111 1111 1111',
            'inputmode': 'numeric', 'autocomplete': 'cc-number',
        })
    )
    expiracion = forms.CharField(
        max_length=5, required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'MM/AA', 'autocomplete': 'cc-exp',
        })
    )
    cvv = forms.CharField(
        max_length=4, required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': '***', 'autocomplete': 'cc-csc',
        })
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('metodo') == 'tarjeta':
            for campo in ('titular', 'numero_tarjeta', 'expiracion', 'cvv'):
                if not cleaned.get(campo):
                    self.add_error(campo, 'Campo obligatorio para pagos con tarjeta.')

            numero = (cleaned.get('numero_tarjeta') or '').replace(' ', '').replace('-', '')
            if numero:
                if not numero.isdigit() or not (12 <= len(numero) <= 19):
                    self.add_error('numero_tarjeta', 'Número de tarjeta inválido.')
                elif not _luhn_valido(numero):
                    self.add_error('numero_tarjeta', 'El número de tarjeta no pasa la validación.')
                else:
                    cleaned['numero_tarjeta'] = numero

            exp = (cleaned.get('expiracion') or '').strip()
            if exp:
                if len(exp) != 5 or exp[2] != '/' or not (exp[:2].isdigit() and exp[3:].isdigit()):
                    self.add_error('expiracion', 'Formato esperado MM/AA.')
                else:
                    mes, anio = int(exp[:2]), 2000 + int(exp[3:])
                    if not 1 <= mes <= 12:
                        self.add_error('expiracion', 'Mes inválido.')
                    else:
                        ultimo_dia_mes = date(anio + (mes // 12), (mes % 12) + 1, 1)
                        if ultimo_dia_mes <= date.today():
                            self.add_error('expiracion', 'La tarjeta está vencida.')

            cvv = cleaned.get('cvv') or ''
            if cvv and (not cvv.isdigit() or not 3 <= len(cvv) <= 4):
                self.add_error('cvv', 'CVV inválido.')

        return cleaned


def _luhn_valido(numero: str) -> bool:
    suma = 0
    invertido = numero[::-1]
    for i, ch in enumerate(invertido):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        suma += n
    return suma % 10 == 0


class CancelarReservaForm(forms.Form):
    motivo = forms.CharField(
        required=False, max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Opcional'
        })
    )
    confirmar = forms.BooleanField(
        required=True,
        label='Entiendo la política de cancelación y deseo cancelar mi reserva.',
    )


class BuscarReservaForm(forms.Form):
    codigo = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Ej: A1B2C3D4',
            'style': 'text-transform: uppercase;',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def clean_codigo(self):
        return self.cleaned_data['codigo'].strip().upper()
