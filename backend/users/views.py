from typing import List, Optional

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (BasePermission, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from foodgram_api.pagination import CustomPageNumberPagination
from users.models import Subscription
from users.serializers import (CustomUserSerializer, PasswordSerializer,
                               SubscriptionSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    Custom viewset for user operations including password setting,
    managing subscriptions, and listing subscriptions.

    Inherits from UserViewSet of Djoser.

    Attributes:
        queryset (QuerySet): QuerySet for User objects.
        permission_classes (tuple): Permission classes for the viewset.
        serializer_class (CustomUserSerializer): Serializer for user data.
        pagination_class (CustomPageNumberPagination): Pagination class.
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination
    serializer_class = CustomUserSerializer

    def get_permissions(self) -> List[BasePermission]:
        """
        Get permissions for the viewset.

        Returns:
            List[BasePermission]: A list of permission instances.
        """
        if self.action == "me":
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(
            self, request: HttpRequest, pk: Optional[int] = None
    ) -> Response:
        """
        Set a new password for the user.

        Args:
            request (HttpRequest): The request object.
            pk (int, optional): Primary key of the user. Defaults to None.

        Returns:
            Response: The response object.
        """
        user = self.request.user
        serializer = PasswordSerializer(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        if not user.check_password(
                serializer.validated_data["current_password"]):
            return Response(
                {"errors": "Текущий пароль неверен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request: HttpRequest) -> Response:
        """
        List subscriptions of the user.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: The paginated response object.
        """
        user = request.user
        queryset = User.objects.filter(authors__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        name="Subscribe"
    )
    def subscribe(self, request: HttpRequest, *args, **kwargs) -> Response:
        """
        Subscribe to an author.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object with
            subscription data or error message.
        """

        user = request.user
        user_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=user_id)

        if user == author:
            return Response({"errors": "Нельзя подписаться на самого себя!"},
                            status=status.HTTP_400_BAD_REQUEST)

        if Subscription.objects.filter(user=user, author=author).exists():
            return Response({"errors": "Вы уже подписаны на автора!"},
                            status=status.HTTP_400_BAD_REQUEST)

        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request: HttpRequest, *args, **kwargs) -> Response:
        """
        Unsubscribe from an author.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object indicating success or error message.
        """

        user = request.user
        user_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=user_id)

        subscription = Subscription.objects.filter(user=user, author=author)
        if not subscription.exists():
            return Response({"errors": "Вы не подписаны на автора!"},
                            status=status.HTTP_400_BAD_REQUEST)

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
