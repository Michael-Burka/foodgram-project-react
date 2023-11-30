from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)


class RecipeTagInline(admin.TabularInline):
    """
    Inline admin for displaying RecipeTag within the Recipe admin page.
    """

    model = RecipeTag
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    """
    Inline admin for displaying RecipeIngredient within the Recipe admin page.
    """

    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Admin interface for Recipe model.
    """

    list_display = ["id", "name", "author", "favorites_count"]
    search_fields = ["name", "author__username", "tags__name"]
    list_filter = ["tags", "author", "pub_date"]
    inlines = [RecipeIngredientInline, RecipeTagInline]

    def favorites_count(self, obj: Recipe) -> int:
        """
        Returns the count of favorites for a recipe.

        Args:
            obj (Recipe): Recipe instance.

        Returns:
            int: Count of favorites.
        """
        return obj.favorites.count()

    favorites_count.short_description = "Favorites Count"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for Tag model.
    """

    list_display = ("name", "slug", "color")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Admin interface for Ingredient model.
    """

    list_display = ("name", "measurement_unit")
    search_fields = ["name"]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Admin interface for Favorite model.
    """

    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Admin interface for ShoppingCart model.
    """

    list_display = ("user", "recipe", "added_at")
    list_filter = ("user", "recipe")
