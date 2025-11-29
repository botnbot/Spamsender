from django.core.management.base import BaseCommand
from core.models import Newsletter
from core.services.send_newsletter import send_newsletter_now

class Command(BaseCommand):
    help = "Отправка рассылки вручную"

    def add_arguments(self, parser):
        parser.add_argument("newsletter_id", type=int, help="ID рассылки")

    def handle(self, *args, **options):
        newsletter_id = options["newsletter_id"]
        try:
            newsletter = Newsletter.objects.get(id=newsletter_id)
        except Newsletter.DoesNotExist:
            self.stdout.write(self.style.ERROR("Рассылка не найдена"))
            return

        send_newsletter_now(newsletter)

        self.stdout.write(self.style.SUCCESS("Рассылка успешно отправлена"))

