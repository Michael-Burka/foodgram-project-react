from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        'Your login',
        max_length=150,
        unique=True,
        error_messages={
            'unique': 'A user with this username already exists.',
        },
        help_text='Enter username',
        validators=[validate_username],
    )
    email = models.EmailField(
        'Email',
        unique=True,
        error_messages={
            'unique': 'This email is already taken.',
        },
    )
    first_name = models.CharField('First name', max_length=150)
    last_name = models.CharField('Last name', max_length=150)

    class Meta:
        ordering = ['email']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Subscriber',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Author',
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Subscription date and time'
    )

    class Meta:
        ordering = ['-id']
        unique_together = ['user', 'author']
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

