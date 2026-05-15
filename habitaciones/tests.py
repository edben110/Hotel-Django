from decimal import Decimal

from django.test import TestCase

from .models import Habitacion, TipoHabitacion


class HabitacionImagenTests(TestCase):
	def test_tiene_imagen_real_devuelve_false_si_no_hay_archivo(self):
		tipo = TipoHabitacion.objects.create(nombre='Suite Test')
		habitacion = Habitacion.objects.create(
			numero='101',
			tipo=tipo,
			capacidad=2,
			precio_por_noche=Decimal('120.00'),
		)

		self.assertFalse(habitacion.tiene_imagen_real)
