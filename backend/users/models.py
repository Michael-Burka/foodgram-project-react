from os import wait
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    email = models.EmailField('Почта', max_length=254, unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=False)
    last_name = models.CharField('Фамилия', max_length=150, blank=False)
    username = models.CharField(
        'Юзернейм',
        max_length=150,
        validators=[validate_username])
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        ordering = ('-pk',)

    def __str__(self):
        return self.username

class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время подписки"
    )

    class Meta:
        ordering = ('-pk',)
        unique_together = ("user", "author")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
