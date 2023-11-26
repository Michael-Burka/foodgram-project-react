from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


User = get_user_model()


class IngredientSearchFilter(SearchFilter):
    """
    Search filter for ingredients by name.
    """
    search_param = "name"


class RecipesFilter(FilterSet):
    """
    Custom filter set for filtering recipes.
    Supports filtering by tags, author, is_favorited, and is_in_shopping_cart.
    """
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    def filter_is_favorited(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        """
        Filter the queryset by whether a recipe is favorited by the user.
        """
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(
        self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet:
        """
        Filter the queryset by whether a recipe is in the user's shopping cart.
        """
        if value and not self.request.user.is_anonymous:
            return queryset.filter(in_shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ["tags", "author", "is_favorited", "is_in_shopping_cart"]
