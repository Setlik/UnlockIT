from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Создаем суперпользователя."""

    def handle(self, *args, **options):
        user = User.objects.create(email="zhirnovivan1991@gmail.com")
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password("11235")
        user.save()
