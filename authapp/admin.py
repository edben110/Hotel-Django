from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, EmailVerificationToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Administración del modelo CustomUser."""

    list_display = ('username', 'email', 'role', 'is_verified', 'is_staff')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Administración del modelo EmailVerificationToken."""

    list_display = ('user', 'token', 'created_at', 'is_used')
