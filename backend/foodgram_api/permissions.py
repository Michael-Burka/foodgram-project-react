from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows object modification only
    if the request user is the owner of the object
    or a superuser. Read-only access is allowed for all users.

    This permission assumes that the object has an 'author'
    attribute to identify the owner.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        """
        Determine if the request should be permitted.

        Args:
            request (Request): The incoming request object.
            view (APIView): The view that is handling the request.
            obj (Any): The object being accessed or modified.

        Returns:
            bool: True if the request is permitted, False otherwise.
        """

        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and (request.user == obj.author or request.user.is_superuser)
        )


class IsOwnerOrAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Custom permission class that allows object modification
    only if the request user is the owner of the object
    or a superuser. Read-only access is allowed for authenticated users.

    This permission assumes that the object
    has an 'author' attribute to identify the owner.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        """
        Determine if the request should be permitted.

        Args:
            request (Request): The incoming request object.
            view (APIView): The view that is handling the request.
            obj (Any): The object being accessed or modified.

        Returns:
            bool: True if the request is permitted, False otherwise.
        """

        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )
