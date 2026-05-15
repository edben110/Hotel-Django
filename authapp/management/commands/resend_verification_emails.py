from django.core.management.base import BaseCommand

from authapp.email_retry import retry_pending_verification_emails


class Command(BaseCommand):
    help = 'Reintenta el envío de correos de verificación pendientes.'

    def handle(self, *args, **options):
        sent_count = retry_pending_verification_emails()
        self.stdout.write(self.style.SUCCESS(f'Correos reenviados: {sent_count}'))
