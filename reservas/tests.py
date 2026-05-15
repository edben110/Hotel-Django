from datetime import date, timedelta
from decimal import Decimal

from django.test import Client, TestCase

from habitaciones.models import Habitacion, TipoHabitacion

from .cart import (
    ValidacionFechasError,
    hay_solapamiento,
    validar_disponibilidad,
    validar_fechas,
)
from .models import Pago, PoliticaCancelacion, Reserva


class CarritoFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tipo = TipoHabitacion.objects.create(nombre='Suite Test')
        cls.hab = Habitacion.objects.create(
            numero='T-1', tipo=cls.tipo, capacidad=2,
            precio_por_noche=Decimal('100.00'),
        )
        PoliticaCancelacion.objects.create(
            nombre='Anticipada', dias_anticipacion=7,
            porcentaje_reembolso=Decimal('100.00'),
        )
        PoliticaCancelacion.objects.create(
            nombre='Media', dias_anticipacion=3,
            porcentaje_reembolso=Decimal('50.00'),
        )
        PoliticaCancelacion.objects.create(
            nombre='Tardía', dias_anticipacion=0,
            porcentaje_reembolso=Decimal('0.00'),
        )

    def setUp(self):
        self.client = Client()

    # --- validaciones de fechas ---
    def test_fecha_pasada_falla(self):
        with self.assertRaises(ValidacionFechasError):
            validar_fechas(date.today() - timedelta(days=1), date.today())

    def test_salida_anterior_a_entrada_falla(self):
        with self.assertRaises(ValidacionFechasError):
            validar_fechas(date.today() + timedelta(days=2), date.today() + timedelta(days=1))

    # --- flujo completo ---
    def test_flujo_carrito_checkout_cancelar(self):
        fe = (date.today() + timedelta(days=10)).isoformat()
        fs = (date.today() + timedelta(days=12)).isoformat()

        # Agregar al carrito
        r = self.client.post(
            f'/reservas/carrito/agregar/{self.hab.pk}/',
            {'fecha_entrada': fe, 'fecha_salida': fs, 'huespedes': 1},
            follow=True,
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Tu carrito')

        # Checkout con tarjeta válida
        r = self.client.post('/reservas/checkout/', {
            'nombre': 'Daniel', 'email': 'd@example.com', 'telefono': '',
            'metodo': 'tarjeta', 'titular': 'Daniel',
            'numero_tarjeta': '4111111111111111',
            'expiracion': '12/30', 'cvv': '123',
        }, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Pago aprobado')

        reserva = Reserva.objects.get(habitacion=self.hab)
        self.assertEqual(reserva.estado, 'confirmada')
        self.assertEqual(reserva.total, Decimal('200.00'))
        self.assertEqual(reserva.pago.estado, 'aprobado')
        self.assertEqual(reserva.pago.ultimos_4, '1111')

        # Reembolso: faltan 10 días → 100%
        self.assertEqual(reserva.calcular_reembolso(), Decimal('200.00'))

        # Cancelar
        r = self.client.post(f'/reservas/{reserva.codigo}/cancelar/', {
            'motivo': 'cambio', 'confirmar': 'on',
        }, follow=True)
        self.assertEqual(r.status_code, 200)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'cancelada')
        self.assertEqual(reserva.monto_reembolsado, Decimal('200.00'))

    def test_solapamiento_bloquea(self):
        # Reserva confirmada existente
        r = Reserva.objects.create(
            habitacion=self.hab, nombre_cliente='X', email_cliente='x@y.z',
            fecha_entrada=date.today() + timedelta(days=5),
            fecha_salida=date.today() + timedelta(days=8),
            precio_por_noche=Decimal('100.00'), total=Decimal('300.00'),
            estado='confirmada',
        )
        Pago.objects.create(
            reserva=r, metodo='tarjeta', estado='aprobado',
            referencia='REF-X', monto=r.total,
        )
        self.assertTrue(hay_solapamiento(
            self.hab,
            date.today() + timedelta(days=6),
            date.today() + timedelta(days=7),
        ))
        with self.assertRaises(ValidacionFechasError):
            validar_disponibilidad(
                self.hab,
                date.today() + timedelta(days=6),
                date.today() + timedelta(days=7),
            )

    def test_tarjeta_invalida_rechazada(self):
        fe = (date.today() + timedelta(days=10)).isoformat()
        fs = (date.today() + timedelta(days=12)).isoformat()
        self.client.post(
            f'/reservas/carrito/agregar/{self.hab.pk}/',
            {'fecha_entrada': fe, 'fecha_salida': fs, 'huespedes': 1},
        )
        r = self.client.post('/reservas/checkout/', {
            'nombre': 'X', 'email': 'x@y.z', 'telefono': '',
            'metodo': 'tarjeta', 'titular': 'X',
            'numero_tarjeta': '1234567890123456',
            'expiracion': '12/30', 'cvv': '123',
        })
        self.assertEqual(r.status_code, 200)
        # Sigue en checkout (no redirige) y no crea reserva
        self.assertFalse(Reserva.objects.exists())

    def test_calcular_reembolso_segun_anticipacion(self):
        r = Reserva.objects.create(
            habitacion=self.hab, nombre_cliente='Y', email_cliente='y@z.com',
            fecha_entrada=date.today() + timedelta(days=4),
            fecha_salida=date.today() + timedelta(days=6),
            precio_por_noche=Decimal('100.00'), total=Decimal('200.00'),
            estado='confirmada',
        )
        # 4 días → política de 3+ días = 50%
        self.assertEqual(r.calcular_reembolso(), Decimal('100.00'))

        r.fecha_entrada = date.today() + timedelta(days=1)
        r.save()
        # 1 día → política de 0+ días = 0%
        self.assertEqual(r.calcular_reembolso(), Decimal('0.00'))
