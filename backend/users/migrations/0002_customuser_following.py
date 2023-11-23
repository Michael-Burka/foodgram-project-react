# Generated by Django 4.2.6 on 2023-11-22 15:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='following',
            field=models.ManyToManyField(related_name='followers', through='users.Subscription', to=settings.AUTH_USER_MODEL),
        ),
    ]
