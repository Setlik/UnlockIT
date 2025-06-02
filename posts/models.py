from django.db import models
from django.utils import timezone

from users.models import User, AuthorSubscription


class Post(models.Model):
    PRICE_TYPES = [
        ('free', 'Бесплатно'),
        ('subscription', 'По подписке'),
        ('paid', 'Платная публикация'),
    ]

    title = models.CharField(
        max_length=100,
        verbose_name="Заголовок публикации",
        help_text="Укажите заголовок публикации",
    )

    content = models.TextField(
        verbose_name="Описание публикации",
        help_text="Укажите описание публикации",
    )

    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
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

    # category = models.ForeignKey(
    #     "Category",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    # )

    price_type = models.CharField(
        max_length=12,
        choices=PRICE_TYPES,
        default='free',
        verbose_name="Тип доступа"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Цена"
    )

    # tags = models.ManyToManyField("Tag", blank=True)

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({'платная' if self.is_paid else 'бесплатная'})"

    def has_access(self, user):
        """Проверяет доступ пользователя к публикации"""
        if self.price_type == 'free':
            return True

        if self.price_type == 'subscription':
            return AuthorSubscription.objects.filter(
                subscriber=user,
                author=self.owner,
                is_active=True,
                expires_at__gt=timezone.now()  # Важно: проверяем срок!
            ).exists()

        if self.price_type == 'paid':
            return PostPurchase.objects.filter(
                user=user,
                post=self
            ).exists()

        return False


class PostPurchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Пользователь',
        verbose_name="Пользователь"
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='Публикация',
        verbose_name="Публикация"
    )

    purchase_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата покупки"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )

    transaction_id = models.CharField(
        max_length=100,
        verbose_name="ID транзакции"
    )

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = "Покупка публикации"
        verbose_name_plural = "Покупки публикаций"

    def __str__(self):
        return f"{self.user} купил {self.post} за {self.price}"

