from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.routers import APIRootView

from recipes.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer
from .permissions import IsAdminOrReadOnly
from .filters import IngredientSearchFilter


class BaseAPIRootView(APIRootView):
    pass

class TagsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)

