from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.routers import APIRootView
from django.core.handlers.wsgi import WSGIRequest


class IsAdminOrReadOnly(BasePermission):
    def has_object_permission(
        self, request: WSGIRequest, view: APIRootView
    ):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )
