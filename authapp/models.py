import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """Modelo de usuario personalizado con rol y verificación por correo."""

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
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class EmailVerificationToken(models.Model):
    """Token de verificación de correo electrónico."""

    RETRY_DELAY_MINUTES = 5

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='verification_tokens',
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    send_attempts = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    def __str__(self):
        return f"Token para {self.user.username} - {'Usado' if self.is_used else 'Pendiente'}"

    def mark_send_attempt(self, success: bool, error_message: str = ''):
        self.send_attempts += 1
        self.last_attempt_at = timezone.now()
        if success:
            self.next_retry_at = None
            self.last_error = ''
        else:
            self.next_retry_at = self.last_attempt_at + timedelta(minutes=self.RETRY_DELAY_MINUTES)
            self.last_error = error_message[:2000]
        self.save(update_fields=[
            'send_attempts',
            'last_attempt_at',
            'next_retry_at',
            'last_error',
        ])

    @property
    def retry_due(self):
        return (
            not self.is_used
            and not self.user.is_verified
            and self.next_retry_at is not None
            and self.next_retry_at <= timezone.now()
        )
