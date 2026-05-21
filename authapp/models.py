from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Modelo de usuario personalizado con rol."""

    ADMIN = 'admin'
    CLIENTE = 'cliente'

    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (CLIENTE, 'Cliente'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CLIENTE,
    )
    # Se mantiene el campo para no romper migraciones existentes,
    # pero siempre será True para nuevos usuarios.
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return self.username
