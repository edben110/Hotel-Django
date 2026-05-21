from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Administración del modelo CustomUser."""

    list_display = ('username', 'email', 'role', 'is_verified', 'is_staff')
