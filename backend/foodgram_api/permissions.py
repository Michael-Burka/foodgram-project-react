from rest_framework import permissions
from rest_framework.routers import APIRootView
from django.core.handlers.wsgi import WSGIRequest


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(
        self, request: WSGIRequest, view: APIRootView
    ) -> bool:
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and (request.user == obj.author or request.user.is_staff)
        )
class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Неавторизованным пользователям разрешён только просмотр.
    Если пользователь является администратором
    или владельцем записи, то возможны остальные методы.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
