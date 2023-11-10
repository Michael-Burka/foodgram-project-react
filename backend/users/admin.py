from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group

from users.models import CustomUser, Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'user', 'subscribed_at')
    list_filter = ('author',)


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(CustomUser, UserAdmin)
