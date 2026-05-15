from django.db import models


class TipoHabitacion(models.Model):
    """Modelo para los tipos de habitación (ej: Simple, Doble, Suite)."""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Tipo de Habitación'
        verbose_name_plural = 'Tipos de Habitación'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Habitacion(models.Model):
    """Modelo principal de habitación."""
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En Mantenimiento'),
    ]

    numero = models.CharField(max_length=10, unique=True)
    tipo = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, related_name='habitaciones')
    capacidad = models.PositiveIntegerField(default=1)
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='habitaciones/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'
        ordering = ['numero']

    def __str__(self):
        return f"Habitación {self.numero} - {self.tipo.nombre}"


class PrecioTemporada(models.Model):
    """Precios especiales por temporada para cada tipo de habitación."""
    TEMPORADA_CHOICES = [
        ('baja', 'Temporada Baja'),
        ('media', 'Temporada Media'),
        ('alta', 'Temporada Alta'),
    ]

    tipo_habitacion = models.ForeignKey(
        TipoHabitacion, on_delete=models.CASCADE, related_name='precios_temporada'
    )
    temporada = models.CharField(max_length=20, choices=TEMPORADA_CHOICES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        verbose_name = 'Precio por Temporada'
        verbose_name_plural = 'Precios por Temporada'
        ordering = ['fecha_inicio']

    def __str__(self):
        return f"{self.tipo_habitacion.nombre} - {self.get_temporada_display()} (${self.precio})"
