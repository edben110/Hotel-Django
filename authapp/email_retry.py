import logging
import threading

from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

from .models import EmailVerificationToken
from .services import send_verification_email


logger = logging.getLogger(__name__)
_worker_started = False
_worker_lock = threading.Lock()
_worker_stop_event = threading.Event()


def start_email_retry_worker():
    global _worker_started

    if _worker_started:
        return

    with _worker_lock:
        if _worker_started:
            return

        thread = threading.Thread(
            target=_email_retry_loop,
            name='authapp-email-retry-worker',
            daemon=True,
        )
        thread.start()
        _worker_started = True
        logger.info('Worker de reintento de correos iniciado.')


def stop_email_retry_worker():
    _worker_stop_event.set()


def _email_retry_loop():
    while not _worker_stop_event.is_set():
        try:
            retry_pending_verification_emails()
        except Exception:
            logger.exception('Error en el worker de reintento de correos.')
        _worker_stop_event.wait(settings.EMAIL_RETRY_INTERVAL_SECONDS)


def retry_pending_verification_emails(limit=None):
    close_old_connections()
    now = timezone.now()
    queryset = (
        EmailVerificationToken.objects.select_related('user')
        .filter(
            is_used=False,
            user__is_verified=False,
            next_retry_at__isnull=False,
            next_retry_at__lte=now,
        )
        .order_by('next_retry_at', 'created_at')
    )
    if limit is None:
        limit = settings.EMAIL_RETRY_BATCH_SIZE
    tokens = list(queryset[:limit])

    sent_count = 0
    for token in tokens:
        if send_verification_email(token.user, token):
            sent_count += 1

    if tokens:
        logger.info('Reintento de verificación procesado: %s correo(s) enviados.', sent_count)

    close_old_connections()
    return sent_count


def get_pending_retry_summary():
    close_old_connections()
    now = timezone.now()
    total_due = EmailVerificationToken.objects.filter(
        is_used=False,
        user__is_verified=False,
        next_retry_at__isnull=False,
        next_retry_at__lte=now,
    ).count()
    close_old_connections()
    return total_due
