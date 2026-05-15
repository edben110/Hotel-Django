from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse

from habitaciones.models import Habitacion


class PoliticaCancelacion(models.Model):
    """Reglas de reembolso según los días de anticipación con que se cancela.

    Ejemplo: 7+ días -> 100%, 3-6 días -> 50%, 0-2 días -> 0%.
    Se evalúa por orden descendente de `dias_anticipacion`.
    """

    nombre = models.CharField(max_length=100)
    dias_anticipacion = models.PositiveIntegerField(
        help_text="Cancelando con al menos estos días de anticipación, "
                  "se aplica este porcentaje de reembolso."
    )
    porcentaje_reembolso = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Porcentaje de reembolso (0-100)."
    )
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Política de cancelación"
        verbose_name_plural = "Políticas de cancelación"
        ordering = ['-dias_anticipacion']

    def __str__(self):
        return f"{self.nombre} ({self.dias_anticipacion}d → {self.porcentaje_reembolso}%)"

    @classmethod
    def calcular_reembolso(cls, dias_restantes: int, monto: Decimal) -> Decimal:
        """Devuelve el monto a reembolsar según las políticas activas."""
        politica = (
            cls.objects.filter(activa=True, dias_anticipacion__lte=dias_restantes)
            .order_by('-dias_anticipacion')
            .first()
        )
        if politica is None:
            return Decimal('0.00')
        return (monto * politica.porcentaje_reembolso / Decimal('100')).quantize(Decimal('0.01'))


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de pago'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    codigo = models.CharField(max_length=12, unique=True, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reservas',
    )
    habitacion = models.ForeignKey(
        Habitacion, on_delete=models.PROTECT, related_name='reservas'
    )
    nombre_cliente = models.CharField(max_length=150)
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=30, blank=True)

    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    huespedes = models.PositiveIntegerField(default=1)

    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
    motivo_cancelacion = models.CharField(max_length=255, blank=True)
    monto_reembolsado = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00')
    )

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Reserva {self.codigo} - {self.habitacion}"

    def get_absolute_url(self):
        return reverse('reservas:reserva_detail', kwargs={'codigo': self.codigo})

    @property
    def noches(self) -> int:
        return (self.fecha_salida - self.fecha_entrada).days

    @property
    def puede_cancelarse(self) -> bool:
        if self.estado not in ('pendiente', 'confirmada'):
            return False
        return self.fecha_entrada >= date.today()

    def dias_anticipacion(self, referencia: date | None = None) -> int:
        ref = referencia or date.today()
        return (self.fecha_entrada - ref).days

    def calcular_reembolso(self, referencia: date | None = None) -> Decimal:
        return PoliticaCancelacion.calcular_reembolso(
            self.dias_anticipacion(referencia), self.total
        )

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._generar_codigo()
        super().save(*args, **kwargs)

    @staticmethod
    def _generar_codigo() -> str:
        import secrets, string
        alfabeto = string.ascii_uppercase + string.digits
        # Reintenta hasta encontrar uno único
        for _ in range(10):
            codigo = ''.join(secrets.choice(alfabeto) for _ in range(8))
            if not Reserva.objects.filter(codigo=codigo).exists():
                return codigo
        # fallback muy improbable
        return ''.join(secrets.choice(alfabeto) for _ in range(12))


class Pago(models.Model):
    """Registro de pago simulado para una reserva."""

    METODO_CHOICES = [
        ('tarjeta', 'Tarjeta de crédito/débito'),
        ('paypal', 'PayPal (simulado)'),
    ]
    ESTADO_CHOICES = [
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    reserva = models.OneToOneField(
        Reserva, on_delete=models.CASCADE, related_name='pago'
    )
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES, default='tarjeta')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    referencia = models.CharField(max_length=40, unique=True)
    titular = models.CharField(max_length=150, blank=True)
    ultimos_4 = models.CharField(max_length=4, blank=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha']

    def __str__(self):
        return f"Pago {self.referencia} ({self.get_estado_display()})"
