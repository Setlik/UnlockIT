from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):

    email = models.EmailField(
        verbose_name="Почта", help_text="Укажите почту"
    )

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
        User,
        on_delete=models.CASCADE,
        related_name='author_subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('subscriber', 'author')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def days_remaining(self):
        return (self.expires_at - timezone.now()).days if self.is_active else 0
