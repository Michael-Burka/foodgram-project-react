import openpyxl
from io import BytesIO
from django.db.models import Sum

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.routers import APIRootView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets
from django.http import HttpResponse
from datetime import datetime

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
    FavoriteSerializer,
)
from .filters import IngredientSearchFilter, RecipesFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsOwnerOrAdminOrReadOnly


class BaseAPIRootView(APIRootView):
    pass


class TagsViewSet(ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @staticmethod
    def __favorite_list(request, pk, list_model):
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            if request.method == "POST":
                return Response(
                    {"error": "The recipe does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif request.method == "DELETE":
                return Response(
                    {"error": "The recipe does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )

        if request.method == "POST":
            if list_model.objects.filter(
                    user=request.user, recipe=recipe
            ).exists():
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
                    user=request.user, recipe=recipe
            )
            if favorite_entry.exists():
                favorite_entry.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "The recipe is not found in favorites."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def favorite(self, request, pk):
        return self.__favorite_list(request, pk, Favorite)

    @action(
        methods=["DELETE", "POST"],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self.__favorite_list(
                request=request, list_model=ShoppingCart, pk=pk
        )

    @action(
            detail=False,
            methods=["GET"],
            permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart_items = ShoppingCart.objects.filter(user=request.user)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__in=shopping_cart_items
        ).values(
            "ingredient__name", "ingredient__measurement_unit"
        ).annotate(
            amount_sum=Sum("amount")
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Shopping List"

        headers = ['Ingredient', 'Measurement Unit', 'Total Amount']
        ws.append(headers)

        for ingredient in ingredients:
            ws.append([
                ingredient["ingredient__name"], 
                ingredient["ingredient__measurement_unit"],
                ingredient["amount_sum"]
            ])

        output = BytesIO()
        wb.save(output)

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=shopping_lists_{current_time}.xlsx'
        return response
