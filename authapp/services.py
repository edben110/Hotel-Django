from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_verification_email(user, token):
    """Envía correo de verificación con enlace que contiene el token."""
    try:
        verification_path = reverse('verify_email')
        verification_url = f"http://127.0.0.1:8000{verification_path}?token={token.token}"

        subject = "Verifica tu cuenta"
        message = (
            f"Hola {user.username},\n\n"
            f"Bienvenido/a a nuestro sistema. Para completar tu registro, "
            f"necesitas verificar tu cuenta.\n\n"
            f"Haz clic en el siguiente enlace para verificar tu correo electrónico:\n"
            f"{verification_url}\n\n"
            f"Si no creaste esta cuenta, puedes ignorar este mensaje.\n\n"
            f"Gracias."
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
    except Exception as e:
        print(f"Error al enviar correo de verificación: {e}")
        raise
