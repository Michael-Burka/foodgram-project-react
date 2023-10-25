from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeTag,
    RecipeIngredient,
    Favorite,
    ShoppingList,
    Subscription,
)

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username")
    search_fields = ("email", "username")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "favorites_count", "cooking_time")
    search_fields = ("name", "author__username")
    list_filter = ("author", "tags", "name")

    def favorites_count(self, obj):
        return obj.favorites_count

    favorites_count.short_description = "Число добавлений в избранное"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color_code", "slug")
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ("recipe", "tag")


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "quantity")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "added_at")


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "added_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "author", "subscribed_at")
    search_fields = ("user__username", "author__username")
    list_filter = ("subscribed_at",)
