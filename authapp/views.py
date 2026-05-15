import datetime
from uuid import UUID

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import CustomAuthenticationForm, RegisterForm
from .models import EmailVerificationToken
from .services import send_verification_email


def register_view(request):
    """Vista de registro de usuario."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                # Obtener el token generado para el usuario
                token = EmailVerificationToken.objects.filter(
                    user=user
                ).latest('created_at')

                # Enviar correo de verificación
                try:
                    send_verification_email(user, token)
                except Exception:
                    messages.warning(
                        request,
                        'Tu cuenta fue creada, pero no pudimos enviar el correo de verificación. '
                        'Contacta al soporte si no recibes el correo.',
                    )

                messages.success(
                    request,
                    'Tu cuenta fue creada exitosamente. Revisa tu correo para verificarla.',
                )
                return redirect('email_sent')
            except Exception:
                messages.error(
                    request,
                    'Ocurrió un error inesperado al crear la cuenta. Intenta de nuevo.',
                )
    else:
        form = RegisterForm()

    return render(request, 'authapp/register.html', {'form': form})


def email_sent_view(request):
    """Vista que confirma el envío del correo de verificación."""
    return render(request, 'authapp/email_sent.html')


def verify_email_view(request):
    """Vista de verificación de correo electrónico mediante token."""
    token_value = request.GET.get('token')

    # Validar que el token fue proporcionado
    if not token_value:
        messages.error(request, 'El enlace de verificación es inválido.')
        return render(request, 'authapp/verify_email.html')

    try:
        # Validar que sea un UUID válido
        token_uuid = UUID(token_value)

        # Buscar el token en la base de datos
        token = EmailVerificationToken.objects.get(token=token_uuid)

        # Verificar que no haya sido usado
        if token.is_used:
            messages.error(request, 'El token ya fue utilizado.')
            return render(request, 'authapp/verify_email.html')

        # Verificar que no haya expirado (24 horas)
        expiration_time = token.created_at + datetime.timedelta(hours=24)
        if timezone.now() > expiration_time:
            messages.error(request, 'El token ha expirado.')
            return render(request, 'authapp/verify_email.html')

        # Token válido: activar usuario
        user = token.user
        user.is_active = True
        user.is_verified = True
        user.save()

        # Marcar token como usado
        token.is_used = True
        token.save()

        messages.success(
            request,
            'Cuenta verificada correctamente. Ya puedes iniciar sesión.',
        )
        return redirect('login')

    except (ValueError, ValidationError):
        messages.error(request, 'El enlace de verificación es inválido.')
        return render(request, 'authapp/verify_email.html')

    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'El enlace de verificación es inválido.')
        return render(request, 'authapp/verify_email.html')

    except Exception:
        messages.error(request, 'Ocurrió un error al verificar la cuenta.')
        return render(request, 'authapp/verify_email.html')


def login_view(request):
    """Vista de inicio de sesión."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = authenticate(request, username=username, password=password)

                if user is not None:
                    # Verificar que el usuario haya verificado su correo
                    if not user.is_verified:
                        messages.error(
                            request,
                            'Debes verificar tu correo antes de iniciar sesión.',
                        )
                        return render(request, 'authapp/login.html', {'form': form})

                    login(request, user)
                    messages.success(request, 'Inicio de sesión exitoso.')
                    return redirect('home')
                else:
                    messages.error(request, 'Credenciales inválidas.')

            except Exception:
                messages.error(request, 'Ocurrió un error al iniciar sesión.')
        else:
            messages.error(request, 'Credenciales inválidas.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'authapp/login.html', {'form': form})


def logout_view(request):
    """Vista de cierre de sesión."""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


@login_required
def home_view(request):
    """Vista principal protegida para usuarios autenticados."""
    return render(request, 'authapp/home.html')
