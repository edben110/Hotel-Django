import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


logger = logging.getLogger(__name__)


def send_verification_email(request, user, token):
    """Envía correo de verificación con enlace que contiene el token."""
    try:
        verification_path = reverse('verify_email')
        verification_url = request.build_absolute_uri(verification_path)
        verification_url = f"{verification_url}?token={token.token}"

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

        if not settings.EMAIL_HOST and 'console' not in settings.EMAIL_BACKEND.lower():
            logger.warning("Correo de verificación no enviado porque EMAIL_HOST no está configurado.")
            logger.info("Token de verificación para %s: %s", user.email, verification_url)
            return

        send_mail(subject, message, None, [user.email], fail_silently=False)
    except Exception as e:
        logger.exception("Error al enviar correo de verificación: %s", e)
        raise
