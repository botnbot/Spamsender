from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создает группу Managers и назначает права"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Managers")

        permissions = Permission.objects.filter(
            codename__in=[
                "view_all_messages",
                "view_all_recipients",
                "view_all_newsletters",
            ]
        )

        group.permissions.set(permissions)

        if created:
            self.stdout.write(self.style.SUCCESS("Группа Managers создана"))
        else:
            self.stdout.write(self.style.WARNING("Группа Managers уже существует"))

        self.stdout.write(self.style.SUCCESS("Права назначены"))
