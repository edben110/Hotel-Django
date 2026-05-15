from datetime import date, timedelta
from decimal import Decimal

from django.test import Client, TestCase

from habitaciones.models import Habitacion, TipoHabitacion

from . import gateway
from .cart import (
    ValidacionFechasError,
    hay_solapamiento,
    validar_disponibilidad,
    validar_fechas,
)
from .models import Pago, PoliticaCancelacion, Reserva


def _datos_cliente():
    return {'nombre': 'Daniel', 'email': 'd@example.com', 'telefono': ''}


def _tarjeta_aprobada():
    return {
        'metodo': 'tarjeta', 'titular': 'Daniel',
        'numero_tarjeta': '4111111111111111',
        'expiracion': '12/30', 'cvv': '123',
    }


class CarritoYValidacionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tipo = TipoHabitacion.objects.create(nombre='Suite Test')
        cls.hab = Habitacion.objects.create(
            numero='T-1', tipo=cls.tipo, capacidad=2,
            precio_por_noche=Decimal('100.00'),
        )

    def test_fecha_pasada_falla(self):
        with self.assertRaises(ValidacionFechasError):
            validar_fechas(date.today() - timedelta(days=1), date.today())

    def test_salida_anterior_a_entrada_falla(self):
        with self.assertRaises(ValidacionFechasError):
            validar_fechas(date.today() + timedelta(days=2), date.today() + timedelta(days=1))

    def test_solapamiento_bloquea(self):
        Reserva.objects.create(
            habitacion=self.hab, nombre_cliente='X', email_cliente='x@y.z',
            fecha_entrada=date.today() + timedelta(days=5),
            fecha_salida=date.today() + timedelta(days=8),
            precio_por_noche=Decimal('100.00'), total=Decimal('300.00'),
            estado='confirmada',
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


class PoliticaCancelacionTests(TestCase):
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

    def test_calcular_reembolso_segun_anticipacion(self):
        r = Reserva.objects.create(
            habitacion=self.hab, nombre_cliente='Y', email_cliente='y@z.com',
            fecha_entrada=date.today() + timedelta(days=4),
            fecha_salida=date.today() + timedelta(days=6),
            precio_por_noche=Decimal('100.00'), total=Decimal('200.00'),
            estado='confirmada',
        )
        self.assertEqual(r.calcular_reembolso(), Decimal('100.00'))  # 4d → 50%
        r.fecha_entrada = date.today() + timedelta(days=10)
        r.save()
        self.assertEqual(r.calcular_reembolso(), Decimal('200.00'))  # 10d → 100%
        r.fecha_entrada = date.today() + timedelta(days=1)
        r.save()
        self.assertEqual(r.calcular_reembolso(), Decimal('0.00'))  # 1d → 0%


class PasarelaSimuladaTests(TestCase):
    """Pruebas unitarias del módulo gateway aislado."""

    def test_crear_y_obtener_sesion(self):
        s = gateway.crear_sesion(
            monto=Decimal('100.00'),
            descripcion='Test',
            callback_url='http://x/cb',
            metadata={'foo': 'bar'},
        )
        self.assertTrue(s.token.startswith('hp_sess_'))
        self.assertEqual(s.estado, 'creada')
        self.assertEqual(gateway.obtener_sesion(s.token).metadata, {'foo': 'bar'})

    def test_pago_aprobado_con_visa_de_prueba(self):
        s = gateway.crear_sesion(Decimal('50.00'), 'X', 'http://x/cb')
        resp = gateway.procesar_pago(
            s.token, '4111 1111 1111 1111', 'Daniel', '12/30', '123',
            simular_latencia=False,
        )
        self.assertTrue(resp.aprobado)
        self.assertEqual(resp.marca, 'visa')
        self.assertEqual(resp.ultimos_4, '1111')
        self.assertTrue(resp.codigo_autorizacion.startswith('AUTH-'))
        self.assertEqual(gateway.obtener_sesion(s.token).estado, 'aprobada')

    def test_pago_rechazado_por_tarjeta_de_prueba(self):
        s = gateway.crear_sesion(Decimal('50.00'), 'X', 'http://x/cb')
        resp = gateway.procesar_pago(
            s.token, '4000000000000002', 'Daniel', '12/30', '123',
            simular_latencia=False,
        )
        self.assertFalse(resp.aprobado)
        self.assertEqual(resp.codigo_autorizacion, '')
        self.assertEqual(gateway.obtener_sesion(s.token).estado, 'rechazada')

    def test_pago_rechazado_por_luhn(self):
        s = gateway.crear_sesion(Decimal('50.00'), 'X', 'http://x/cb')
        resp = gateway.procesar_pago(
            s.token, '1234567890123456', 'Daniel', '12/30', '123',
            simular_latencia=False,
        )
        self.assertFalse(resp.aprobado)
        self.assertIn('inválido', resp.mensaje.lower())


class FlujoCompletoCheckoutTests(TestCase):
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

    def setUp(self):
        self.client = Client()
        fe = (date.today() + timedelta(days=10)).isoformat()
        fs = (date.today() + timedelta(days=12)).isoformat()
        self.client.post(
            f'/reservas/carrito/agregar/{self.hab.pk}/',
            {'fecha_entrada': fe, 'fecha_salida': fs, 'huespedes': 1},
        )

    def _checkout_y_obtener_token(self):
        r = self.client.post('/reservas/checkout/', _datos_cliente(), follow=False)
        self.assertEqual(r.status_code, 302)
        # /reservas/hotelpay/<token>/
        token = r.url.rstrip('/').split('/')[-1]
        return token

    def test_checkout_redirige_a_la_pasarela(self):
        r = self.client.post('/reservas/checkout/', _datos_cliente())
        self.assertEqual(r.status_code, 302)
        self.assertIn('/reservas/hotelpay/', r.url)
        # crea reservas en estado pendiente
        self.assertEqual(Reserva.objects.filter(estado='pendiente').count(), 1)

    def test_pasarela_muestra_branding_hotelpay(self):
        token = self._checkout_y_obtener_token()
        r = self.client.get(f'/reservas/hotelpay/{token}/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'HotelPay')
        self.assertContains(r, 'Modo simulación')
        self.assertContains(r, 'Tarjetas de prueba')

    def test_pasarela_aprueba_y_confirma_reserva(self):
        token = self._checkout_y_obtener_token()
        r = self.client.post(f'/reservas/hotelpay/{token}/', _tarjeta_aprobada(), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Pago aprobado')

        reserva = Reserva.objects.get(habitacion=self.hab)
        self.assertEqual(reserva.estado, 'confirmada')
        self.assertEqual(reserva.pago.estado, 'aprobado')
        self.assertEqual(reserva.pago.ultimos_4, '1111')
        # token debe haber sido invalidado tras el callback
        self.assertIsNone(gateway.obtener_sesion(token))

    def test_pasarela_rechaza_y_cancela_reserva(self):
        token = self._checkout_y_obtener_token()
        rechazada = _tarjeta_aprobada()
        rechazada['numero_tarjeta'] = '4000000000000002'
        r = self.client.post(f'/reservas/hotelpay/{token}/', rechazada, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Pago rechazado')

        reserva = Reserva.objects.get(habitacion=self.hab)
        self.assertEqual(reserva.estado, 'cancelada')
        self.assertEqual(reserva.pago.estado, 'rechazado')

    def test_cancelar_reserva_aplica_politica(self):
        token = self._checkout_y_obtener_token()
        self.client.post(f'/reservas/hotelpay/{token}/', _tarjeta_aprobada(), follow=True)
        reserva = Reserva.objects.get(habitacion=self.hab)

        r = self.client.post(f'/reservas/{reserva.codigo}/cancelar/', {
            'motivo': 'cambio', 'confirmar': 'on',
        }, follow=True)
        self.assertEqual(r.status_code, 200)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'cancelada')
        self.assertEqual(reserva.monto_reembolsado, Decimal('200.00'))
