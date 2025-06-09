from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(verbose_name="Почта", help_text="Укажите почту")

    phone_number = models.CharField(
        max_length=35,
        unique=True,
        verbose_name="Телефон",
        help_text="Укажите Телефон",
    )

    avatar = models.ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Установите аватар",
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.phone_number})"


class AuthorSubscription(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions_made",
        verbose_name="Подписчик",
        help_text="Укажите подписчика",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions_received",
        verbose_name="Автор",
        help_text="Укажите автора",
    )

    amount = models.PositiveIntegerField(
        verbose_name="Стоимость подписки", help_text="Укажите стоимость подписки"
    )

    is_active = models.BooleanField(
        default=True, verbose_name="Активна", help_text="Укажите что подписка активна"
    )

    start_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата начала подписки",
        help_text="Укажите дату начала подписки",
    )

    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата окончания подписки",
        help_text="Укажите дату окончания подписки",
    )

    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии Stripe",
        help_text="Укажите ID сессии Stripe",
    )

    payment_link = models.URLField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату",
        help_text="Укажите ссылку на оплату",
    )

    class Meta:
        verbose_name = "Подписка на автора"
        verbose_name_plural = "Подписка на авторов"

    def __str__(self):
        return f"{self.subscriber} → {self.author} ({'активна' if self.is_active else 'неактивна'})"
