from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CustomAuthenticationForm, RegisterForm


def register_view(request):
    """Vista de registro de usuario — crea la cuenta inmediatamente."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Login automático tras registro exitoso
                login(request, user)
                messages.success(
                    request,
                    'Tu cuenta fue creada exitosamente. Bienvenido/a.',
                )
                return redirect('home')
            except Exception:
                messages.error(
                    request,
                    'Ocurrió un error inesperado al crear la cuenta. Intenta de nuevo.',
                )
    else:
        form = RegisterForm()

    return render(request, 'authapp/register.html', {'form': form})


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
    """Vista principal protegida — dashboard dinámico según rol."""
    from habitaciones.models import Habitacion
    from reservas.models import Reserva

    context = {}

    if request.user.role == 'admin':
        from reportes.services import obtener_metricas_dashboard, obtener_actividad_reciente
        from django.urls import reverse

        context['metricas'] = obtener_metricas_dashboard()
        context['actividad'] = obtener_actividad_reciente()
        context['dashboard_data_url'] = reverse('reportes:dashboard_data')

    else:
        habitaciones_disponibles = Habitacion.objects.filter(
            estado='disponible', activa=True
        ).select_related('tipo')[:6]

        reservas_activas = Reserva.objects.filter(
            usuario=request.user,
            estado__in=['pendiente', 'confirmada'],
        ).select_related('habitacion__tipo').order_by('-fecha_creacion')[:5]

        context['habitaciones_disponibles'] = habitaciones_disponibles
        context['reservas_activas'] = reservas_activas
        context['total_reservas_activas'] = reservas_activas.count() if hasattr(reservas_activas, 'count') else len(reservas_activas)
        context['total_habitaciones_disponibles'] = Habitacion.objects.filter(estado='disponible', activa=True).count()

    return render(request, 'authapp/home.html', context)
