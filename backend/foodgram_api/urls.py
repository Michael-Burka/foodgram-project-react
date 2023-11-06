from djoser.views import UserViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView
from .views import CustomTokenObtainPairView

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
