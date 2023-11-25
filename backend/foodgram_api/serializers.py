from typing import Any, Dict, List
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient,
    RecipeTag, Favorite, ShoppingCart
)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model."""
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the Ingredient model."""
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer for the RecipeIngredient model."""
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "measurement_unit", "amount"]
        read_only_fields = ["id", "name", "measurement_unit"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe model."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_favorited")
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = [
            "id", "tags", "author", "ingredients", "is_favorited",
            "is_in_shopping_cart", "name", "image", "text", "cooking_time"]

    def get_ingredients(self, obj: Recipe) -> List[Dict[str, Any]]:
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj: Recipe) -> bool:
        request = self.context.get("request")
        if request and not request.user.is_anonymous:
            return Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        request = self.context.get("request")
        if request and not request.user.is_anonymous:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer for adding ingredients to a recipe."""
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]

    def validate_amount(self, value: int) -> int:
        if value < 1:
            raise serializers.ValidationError(
                "The amount must be greater than 0.")
        return value


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Serializer for creating a new recipe."""
    author = CustomUserSerializer(read_only=True)
    ingredients = AddRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        write_only=True, min_value=1, max_value=32000)

    class Meta:
        model = Recipe
        fields = [
            "id", "author", "ingredients", "tags", "image",
            "name", "text", "cooking_time"]

    def validate_ingredients(
            self, ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if not Ingredient.objects.filter(id__in=ingredient_ids).exists():
            raise serializers.ValidationError(
                    "One or more ingredients do not exist.")
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError(
                    "Ingredients must not be repetitive.")
        return ingredients

    def validate_tags(self, tags: List[Tag]) -> List[Tag]:
        if not tags:
            raise serializers.ValidationError(
                    {"error": "Please specify a tag!"})
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                    {"error": "Tags must not be repetitive."})
        return tags

    def validate_cooking_time(self, value: int) -> int:
        if value < 1:
            raise serializers.ValidationError(
                    "Cooking time must be greater than zero.")
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ingredients = data.get("ingredients")
        tags = data.get("tags")
        if not ingredients:
            raise serializers.ValidationError({"error": "Select ingredients!"})
        if not tags:
            raise serializers.ValidationError(
                    {"error": "Please specify a tag!"})
        return data

    def validate_image(self, value) -> Any:
        if not value:
            raise serializers.ValidationError("Image field cannot be empty.")
        return value

    def create_ingredients(self, ingredients, recipe):
        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(id=ingredient_data["id"])
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe,
                amount=ingredient_data["amount"]
            )

    def create_tags(self, tags, recipe):
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

    def create(self, validated_data: Dict[str, Any]) -> Recipe:
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(
            self, instance: Recipe, validated_data: Dict[str, Any]) -> Recipe:
        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.create_ingredients(ingredients, instance)
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)
        image = validated_data.pop("image", None)
        if image is not None:
            instance.image = image
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data

    def to_representation(self, instance: Recipe) -> Dict[str, Any]:
        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for the Favorite model."""
    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for the ShoppingCart model."""
    class Meta:
        model = ShoppingCart
        fields = ["id", "name", "image", "cooking_time"]

    def to_representation(self, instance: ShoppingCart) -> Dict[str, Any]:
        request = self.context.get("request")
        context = {"request": request}
        return FavoriteSerializer(
            instance.recipe, context=context).data

