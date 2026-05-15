import logging
from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


logger = logging.getLogger(__name__)


def _build_verification_url(request=None):
    verification_path = reverse('verify_email')
    if request is not None:
        return request.build_absolute_uri(verification_path)

    base_url = getattr(settings, 'SITE_URL', '') or settings.BACKEND_URL or settings.API_URL
    if base_url:
        return urljoin(base_url.rstrip('/') + '/', verification_path.lstrip('/'))

    return verification_path


def send_verification_email(user, token, request=None):
    """Envía correo de verificación con enlace que contiene el token.

    Devuelve True cuando el correo se envía o se registra sin bloquear.
    Devuelve False si el backend SMTP falla o no puede conectar.
    """
    try:
        verification_url = f"{_build_verification_url(request)}?token={token.token}"

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
            token.mark_send_attempt(False, 'EMAIL_HOST no configurado')
            return False

        send_mail(subject, message, None, [user.email], fail_silently=False)
        token.mark_send_attempt(True)
        return True
    except OSError as exc:
        logger.warning("No se pudo conectar al servidor SMTP para %s: %s", user.email, exc)
        logger.info("Token de verificación para %s: %s", user.email, verification_url)
        token.mark_send_attempt(False, str(exc))
        return False
    except Exception as e:
        logger.warning("Error al enviar correo de verificación para %s: %s", user.email, e)
        logger.info("Token de verificación para %s: %s", user.email, verification_url)
        token.mark_send_attempt(False, str(e))
        return False
