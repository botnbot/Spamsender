from django.core.management.base import BaseCommand, CommandError

from core.models import Newsletter
from core.services.send_newsletter import send_newsletter_now


class Command(BaseCommand):
    help = "Отправка рассылки вручную"

    def add_arguments(self, parser):
        parser.add_argument('pk', type=int, help=' primary key рассылки')

    def handle(self, *args, **options):
        pk = options['pk']
        try:
            nl = Newsletter.objects.get(pk=pk)
        except Newsletter.DoesNotExist:
            raise CommandError(f"Рассылки {pk} не существует")
        send_newsletter_now(nl)
        self.stdout.write(self.style.SUCCESS(f'Отправлена рассылка {pk}'))
