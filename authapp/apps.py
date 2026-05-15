from django.apps import AppConfig


class AuthappConfig(AppConfig):
    name = 'authapp'

    def ready(self):
        from django.conf import settings

        if settings.RUNNING_TESTS or settings.DEBUG or not settings.ENABLE_EMAIL_RETRY_WORKER:
            return

        from .email_retry import start_email_retry_worker

        start_email_retry_worker()
