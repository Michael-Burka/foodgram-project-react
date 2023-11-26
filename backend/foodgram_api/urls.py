from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet
from .views import IngredientsViewSet, RecipeViewSet, TagsViewSet

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
