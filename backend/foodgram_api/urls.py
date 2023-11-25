from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientsViewSet, TagsViewSet, RecipeViewSet
from users.views import CustomUserViewSet

app_name = "foodgram_api"

router = DefaultRouter()
router.register("users", CustomUserViewSet)
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientsViewSet)
router.register("tags", TagsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
