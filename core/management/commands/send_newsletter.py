from django.core.management.base import BaseCommand, CommandError

from core.models import Newsletter
from core.services.send_newsletter import send_newsletter_now


class Command(BaseCommand):
    help = "Отправка рассылки вручную"

    def add_arguments(self, parser):
        parser.add_argument('pk', type=int, nargs='?', help=' primary key рассылки')
        parser.add_argument('--all', action='store_true', help='Отправить все активные рассылки')

    def handle(self, *args, **options):
        pk = options['pk']
        try:
            if options['all']:
                newsletters = Newsletter.objects.filter(status='created')
                for nl in newsletters:
                    success_count, fail_count = send_newsletter_now(nl)
                    self.stdout.write(self.style.SUCCESS(
                        f'Рассылка {nl.id} отправлена: Успешно {success_count}, Неудачно {fail_count}'
                    ))
            else:
                pk = options['pk']
                if not pk:
                    raise CommandError("Укажите ID рассылки или используйте --all")
                nl = Newsletter.objects.get(pk=pk)
                success_count, fail_count = send_newsletter_now(nl)
                self.stdout.write(self.style.SUCCESS(
                    f'Отправлена рассылка {pk}: Успешно {success_count}, Неудачно {fail_count}'
                ))
        except Newsletter.DoesNotExist:
            raise CommandError(f"Рассылка с ID {pk} не существует")


