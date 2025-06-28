from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    PRICE_TYPES = [
        ("free", "Бесплатно"),
        ("subscription", "По подписке"),
        ("paid", "Платная публикация"),
    ]

    title = models.CharField(
        max_length=100,
        verbose_name="Заголовок публикации",
    )

    content = models.TextField(
        verbose_name="Описание публикации",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Владелец публикации",
        help_text="Укажите владельца публикации",
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name="Платная публикация",
        help_text="Отметьте, если публикация платная",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    price_type = models.CharField(
        max_length=12, choices=PRICE_TYPES, default="free", verbose_name="Тип доступа"
    )

    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Цена"
    )

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_price_type_display()})"


class PostPurchase(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Пользователь",
        help_text="Укажите пользователь",
    )

    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        verbose_name="Публикация",
        help_text="Укажите публикацию",
    )

    purchase_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата покупки",
        help_text="Укажите дату покупки",
    )

    amount = models.PositiveIntegerField(
        verbose_name="Стоимость покупки", help_text="Укажите стоимость покупки"
    )

    session_id = models.CharField(
        max_length=255,
        default="initial_value",
        blank=True,
        null=True,
        verbose_name="ID сессии",
        help_text="Укажите ID сессии",
    )

    link = models.URLField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату",
        help_text="Укажите ссылку на оплату",
    )

    class Meta:
        verbose_name = "Покупка публикации"
        verbose_name_plural = "Покупки публикаций"

    def __str__(self):
        return f"{self.user} купил {self.post} за {self.amount}"
