from django.core.management.base import BaseCommand

from academy.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    """Заполнение таблицы платежей тестовыми данными."""

    def handle(self, *args, **kwargs):
        try:
            user_1 = User.objects.get(id=1)
            user_2 = User.objects.get(id=2)
            course_1 = Course.objects.get(id=2)
            lesson_1 = Lesson.objects.get(id=1)

            Payment.objects.create(
                user=user_1,
                payment_date="2023-10-01T10:00:00Z",
                course=course_1,
                amount=100.00,
                payment_method="cash",
            )
            Payment.objects.create(
                user=user_2,
                payment_date="2023-10-02T10:00:00Z",
                lesson=lesson_1,
                amount=50.00,
                payment_method="transfer",
            )

            self.stdout.write(
                self.style.SUCCESS("Данные успешно добавлены в таблицу платежей")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
