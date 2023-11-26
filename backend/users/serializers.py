from typing import Dict, List

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import Recipe
from users.models import Subscription
from users.validators import validate_username

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Serializer for creating a new user.

    Inherits from UserCreateSerializer of Djoser.

    Attributes:
        email (EmailField):
            Email field with unique validation.
        username (CharField):
            Username field with unique validation and custom validator.
    """
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            validate_username
        ],
        max_length=150,
    )

    class Meta:
        model = User
        fields = (
            "email", "id", "password", "username",
            "first_name", "last_name"
        )
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
            "password": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


class CustomUserSerializer(UserSerializer):
    """
    Serializer for user information.

    Inherits from UserSerializer of Djoser. Adds subscription status.

    Methods:
        get_is_subscribed: Check if the user is subscribed to the object user.
    """
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj: User) -> bool:
        """
        Determine if the current user is subscribed to the author.

        Args:
            obj (User):
                The user object being serialized.

        Returns:
            bool:
                True if the current user is subscribed to obj, False otherwise.
        """
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user, author=obj.id
        ).exists()

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name",
            "last_name", "is_subscribed"
        )


class PasswordSerializer(serializers.Serializer):
    """
    Serializer for changing a user's password.

    Attributes:
        current_password (CharField): Field for the current password.
        new_password (CharField): Field for the new password.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for recipes in a subscription context.

    Attributes:
        image (Base64ImageField): Field for the recipe image in base64 format.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for user subscriptions.

    Methods:
        get_is_subscribed: Check if the author is subscribed to the user.
        get_recipes: Get limited recipes of the author.
        get_recipes_count: Get the count of recipes by the author.
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj: User) -> bool:
        """
        Check if the author is subscribed to the user.

        Args:
            obj (User): The user object being serialized.

        Returns:
            bool: Subscription status.
        """
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=obj, author=user
        ).exists()

    def get_recipes(self, obj: User) -> List[Dict]:
        """
        Retrieve limited recipes of the author.

        Args:
            obj (User): The user object being serialized.

        Returns:
            List[Dict]: A list of serialized recipes.
        """
        limit = self.context["request"].query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit is not None:
            try:
                limit = int(limit)
                recipes = recipes[:limit]
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid recipes_limit value"
                )
        return SubscriptionRecipeSerializer(
            recipes, many=True, read_only=True
        ).data

    def get_recipes_count(self, obj: User) -> int:
        """
        Get the count of recipes by the author.

        Args:
            obj (User): The user object being serialized.

        Returns:
            int: Number of recipes.
        """
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name",
            "is_subscribed", "recipes", "recipes_count"
        )
