from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Type, Union

import openpyxl
from django.db import models
from django.http import HttpRequest, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from foodgram_api.filters import IngredientSearchFilter, RecipesFilter
from foodgram_api.pagination import CustomPageNumberPagination
from foodgram_api.permissions import IsOwnerOrAdminOrReadOnly
from foodgram_api.serializers import (CreateRecipeSerializer,
                                      FavoriteSerializer, IngredientSerializer,
                                      RecipeSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class TagsViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for performing read-only operations on `Tag` model.

    Inherits from `ReadOnlyModelViewSet`, allowing only read operations
    such as list and retrieve. Utilizes `TagSerializer` for serialization
    and deserialization of `Tag` instances.

    Attributes:
        permission_classes (tuple):
            Tuple containing permission classes.
            Allows any user to access.
        queryset (QuerySet):
            A QuerySet instance representing the `Tag` objects.
        serializer_class (TagSerializer):
            The serializer class for `Tag` objects.
    """

    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for performing read-only operations on `Ingredient` model.

    Inherits from `ReadOnlyModelViewSet`, allowing only read operations such as
    list and retrieve. Uses `IngredientSerializer` for serialization and
    deserialization of `Ingredient` instances.

    Attributes:
        permission_classes (tuple):
            Tuple containing permission classes.
            Allows any user to access.
        queryset (QuerySet):
            A QuerySet instance representing the `Ingredient` objects.
        serializer_class (IngredientSerializer):
            The serializer class for `Ingredient` objects.
        filter_backends (tuple):
            Tuple containing filter backends.
            Includes `IngredientSearchFilter`.
        search_fields (tuple): Fields to perform search operations on.
    """

    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling requests for the `Recipe` model.

    Inherits from `ModelViewSet`, allowing create, retrieve, update, delete,
    and list operations. It uses different serializers for read and write
    operations and includes custom actions for handling favorites and shopping
    cart functionality.
    """

    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(
        self,
    ) -> Type[Union[RecipeSerializer, CreateRecipeSerializer]]:
        """
        Determine which serializer class to use based on the HTTP method.

        Returns:
            The serializer class, either `RecipeSerializer`
            or `CreateRecipeSerializer`.
        """
        if self.request.method == "GET":
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Provide additional context for the serializer.

        Returns:
            A dictionary containing the context for the serializer,
            including the request.
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @staticmethod
    def __favorite_list(
        request: HttpRequest, pk: int, list_model: Type[models.Model]
    ) -> Response:
        """
        Handle adding or removing a recipe to/from
        a user's favorite or shopping cart list.

        Args:
            request:
                The incoming HTTP request.
            pk:
                Primary key of the recipe.
            list_model:
                The model class for the list (Favorite or ShoppingCart).

        Returns:
            The HTTP response object.
        """
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            if request.method == "POST":
                return Response(
                    {"error": "The recipe does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if request.method == "DELETE":
                return Response(
                    {"error": "The recipe does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if request.method == "POST":
            if list_model.objects.filter(
                    user=request.user, recipe=recipe).exists():
                return Response(
                    {"errors": "The recipe is already in favorites!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            list_model.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(
                recipe,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            favorite_entry = list_model.objects.filter(
                user=request.user, recipe=recipe)
            if favorite_entry.exists():
                favorite_entry.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "The recipe is not found in favorites."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def favorite(self, request: Request, pk: int) -> Response:
        """
        Add or remove a recipe from the user's favorites.

        Args:
            request: The incoming HTTP request.
            pk: Primary key of the recipe.

        Returns:
            The HTTP response object.
        """
        return self.__favorite_list(request, pk, Favorite)

    @action(
        methods=["DELETE", "POST"],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request: Request, pk: int) -> Response:
        """
        Add or remove a recipe from the user's shopping cart.

        Args:
            request: The incoming HTTP request.
            pk: Primary key of the recipe.

        Returns:
            The HTTP response object.
        """
        return self.__favorite_list(
            request=request, list_model=ShoppingCart, pk=pk)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request: Request) -> HttpResponse:
        """
        Download a shopping cart as an Excel file.

        Args:
            request: The incoming HTTP request.

        Returns:
            An HttpResponse containing the Excel file.
        """
        shopping_cart_items = ShoppingCart.objects.filter(user=request.user)
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_cart__in=shopping_cart_items
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount_sum=models.Sum("amount"))
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Shopping List"

        headers = ["Ingredient", "Measurement Unit", "Total Amount"]
        ws.append(headers)

        for ingredient in ingredients:
            ws.append(
                [
                    ingredient["ingredient__name"],
                    ingredient["ingredient__measurement_unit"],
                    ingredient["amount_sum"],
                ]
            )

        output = BytesIO()
        wb.save(output)

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        response = HttpResponse(
            output.getvalue(),
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

        response[
            "Content-Disposition"
        ] = f"attachment; filename=shopping_lists_{current_time}.xlsx"
        return response
