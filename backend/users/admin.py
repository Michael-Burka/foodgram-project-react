from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Subscription
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for User model.

    Extends Django's default UserAdmin to customize the admin interface.
    """

    list_display = [
        "email", "username", "first_name", "last_name",
        "is_active", "date_joined",
    ]
    list_filter = ["is_active", "first_name", "email"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_active", "is_staff", "is_superuser",
                    "groups", "user_permissions",
                ]
            },
        ),
        ("Important dates", {"fields": ["last_login", "date_joined"]}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Subscription model.

    Configures list display, filters, search fields, and readonly fields
    for Subscription model in Django admin.
    """

    list_display = ["author", "user", "subscribed_at"]
    list_filter = ["author", "user"]
    readonly_fields = ["subscribed_at"]
    search_fields = ["author__username", "user__username"]
