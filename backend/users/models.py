from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    pass

    class Meta:
        ordering = ('-id',)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время подписки"
    )

    class Meta:
        ordering = ('-id',)
        unique_together = ("user", "author")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
