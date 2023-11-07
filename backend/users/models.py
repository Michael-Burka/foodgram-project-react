from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        "auth.User",
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
