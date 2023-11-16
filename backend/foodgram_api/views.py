from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.routers import APIRootView
from rest_framework.permissions import AllowAny

from recipes.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer
from .filters import IngredientSearchFilter



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
    search_fields = ('^name',)

