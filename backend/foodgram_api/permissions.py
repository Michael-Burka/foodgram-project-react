from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an 'author' attribute.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        """
        Return True if permission is granted, False otherwise.
        """

        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and (request.user == obj.author or request.user.is_superuser)
        )


class IsOwnerOrAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Custom permission to only allow owners of an object or admin to edit it.
    Assumes the model instance has an 'author' attribute.
    """

    def has_object_permission(
            self, request: Request, view: APIView, obj: Any
            ) -> bool:
        """
        Return True if permission is granted, False otherwise.
        """

        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )
