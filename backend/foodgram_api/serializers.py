from typing import Any, Dict, List

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model.

    This serializer provides a representation of the Tag model,
    including fields like id, name, color, and slug.
    """

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Ingredient model.

    This serializer provides a representation of the Ingredient model,
    including fields like id, name, and measurement_unit.
    """

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for the RecipeIngredient model.

    This serializer provides a representation of the RecipeIngredient model.
    It includes fields from the related
    Ingredient model (id, name, measurement_unit) and the amount
    of the ingredient used in the recipe.
    """

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "measurement_unit", "amount"]
        read_only_fields = ["id", "name", "measurement_unit"]


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Recipe model.

    Attributes:
        tags (TagSerializer):
            Serializer for the tags of the recipe.
        author (CustomUserSerializer):
            Serializer for the author of the recipe.
        ingredients (SerializerMethodField):
            Field to get recipe ingredients.
        is_favorited (SerializerMethodField):
            Field to check if the recipe is favorited by the current user.
        is_in_shopping_cart (SerializerMethodField):
            Field to check if the recipe is in the
            shopping cart of the current user.
    """

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
        """
        Retrieve the ingredients for a recipe.

        Args:
            obj (Recipe): The recipe instance.

        Returns:
            List[Dict[str, Any]]: A list of ingredients in the recipe.
        """

        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj: Recipe) -> bool:
        """
        Check if the recipe is favorited by the current user.

        Args:
            obj (Recipe): The recipe instance.

        Returns:
            bool:
            True if the recipe is favorited by the current user,
            False otherwise.
        """

        request = self.context.get("request")
        if request and not request.user.is_anonymous:
            return Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """
        Check if the recipe is in the shopping cart of the current user.

        Args:
            obj (Recipe): The recipe instance.

        Returns:
            bool:
                True if the recipe is in the shopping cart of the current user,
                False otherwise.
        """

        request = self.context.get("request")
        if request and not request.user.is_anonymous:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        return False


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for adding ingredients to a recipe.

    Attributes:
        id (IntegerField):
            The ID of the ingredient, write-only.
        amount (IntegerField):
            The amount of the ingredient,
            write-only, with a minimum value of 1.
    """

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new recipe.

    Attributes:
        author (CustomUserSerializer):
            Serializer for the author of the recipe, read-only.
        ingredients (AddRecipeIngredientSerializer):
            Serializer for adding multiple ingredients to the recipe.
        tags (PrimaryKeyRelatedField):
            Field for selecting tags for the recipe.
        image (Base64ImageField):
            Field for the recipe image in base64 format, required.
        cooking_time (IntegerField):
            The cooking time for the recipe,
            with minimum and maximum value constraints.
    """

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

    def validate_image(self, value: Any) -> Any:
        """
        Validate the image field of a recipe.

        Args:
            value (Any): The value of the image field to be validated.

        Returns:
            Any: The validated image value.

        Raises:
            serializers.ValidationError: If the image field is empty.
        """

        if not value:
            raise serializers.ValidationError("Image field cannot be empty.")
        return value

    def validate_ingredients(
            self, ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate the list of ingredients for a recipe.

        Args:
            ingredients (List[Dict[str, Any]]):
                A list of ingredients with their IDs and amounts.

        Returns:
            List[Dict[str, Any]]:
                The validated list of ingredients.

        Raises:
            serializers.ValidationError:
                If any ingredient does not exist or if
                there are repetitive ingredients.
        """

        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if not Ingredient.objects.filter(id__in=ingredient_ids).exists():
            raise serializers.ValidationError(
                "One or more ingredients do not exist.")
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError(
                "Ingredients must not be repetitive.")
        return ingredients

    def validate_tags(self, tags: List[Tag]) -> List[Tag]:
        """
        Validate the list of tags for a recipe.

        Args:
            tags (List[Tag]):
                A list of tag objects.

        Returns:
            List[Tag]:
                The validated list of tags.

        Raises:
            serializers.ValidationError:
                If the tags list is empty or contains duplicates.
        """

        if not tags:
            raise serializers.ValidationError(
                {"error": "Please specify a tag!"})
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                {"error": "Tags must not be repetitive."})
        return tags

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the recipe data.

        Args:
            data (Dict[str, Any]):
                The data to validate.

        Returns:
            Dict[str, Any]:
                The validated data.

        Raises:
            serializers.ValidationError:
                If ingredients or tags are not provided.
        """

        ingredients = data.get("ingredients")
        tags = data.get("tags")
        if not ingredients:
            raise serializers.ValidationError({"error": "Select ingredients!"})
        if not tags:
            raise serializers.ValidationError(
                {"error": "Please specify a tag!"})
        return data

    def create_ingredients(self, ingredients, recipe):
        """
        Create ingredient objects for the recipe.

        Args:
            ingredients (List[Dict[str, Any]]):
                A list of ingredient data.
            recipe (Recipe):
                The recipe instance to which the ingredients belong.

        Raises:
            serializers.ValidationError:
                If an ingredient does not exist.
        """

        ingredient_objs = []
        for ingredient_data in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=ingredient_data["id"])
                ingredient_objs.append(
                    RecipeIngredient(
                        ingredient=ingredient, recipe=recipe,
                        amount=ingredient_data["amount"]
                    )
                )
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f"Ingredient with id {ingredient_data['id']}"
                    " does not exist."
                )
        RecipeIngredient.objects.bulk_create(ingredient_objs)

    def create_tags(self, tags, recipe):
        """
        Create tag objects for the recipe.

        Args:
            tags (List[Tag]):
                A list of tag instances.
            recipe (Recipe):
                The recipe instance to which the tags belong.
        """

        tag_objs = [RecipeTag(recipe=recipe, tag=tag) for tag in tags]
        RecipeTag.objects.bulk_create(tag_objs)

    def create(self, validated_data: Dict[str, Any]) -> Recipe:
        """
        Create a new recipe instance based on validated data.

        Args:
            validated_data (Dict[str, Any]):
                The validated data for creating the recipe.

        Returns:
            Recipe:
                The newly created recipe instance.

        """

        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(
            self, instance: Recipe, validated_data: Dict[str, Any]) -> Recipe:
        """
        Update an existing recipe instance.

        Args:
            instance (Recipe):
                The existing recipe instance to update.
            validated_data (Dict[str, Any]):
                The validated data for updating the recipe.

        Returns:
            Recipe: The updated recipe instance.
        """

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

    def to_representation(self, instance: Recipe) -> Dict[str, Any]:
        """
        Convert a recipe instance into a dictionary representation.

        Args:
            instance (Recipe): The recipe instance to represent.

        Returns:
            Dict[str, Any]: The dictionary representation of the recipe.
        """

        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}).data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Favorite model.

    Attributes:
        id (IntegerField):
            The ID of the recipe.
        name (CharField):
            The name of the recipe.
        image (ImageField):
            The image of the recipe.
        cooking_time (IntegerField):
            The cooking time of the recipe.
    """

    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Serializer for the ShoppingCart model.

    Attributes:
        id (IntegerField):
            The ID of the item in the shopping cart.
        name (CharField):
            The name of the item.
        image (ImageField):
            The image of the item.
        cooking_time (IntegerField):
            The cooking time of the item.
    """

    class Meta:
        model = ShoppingCart
        fields = ["id", "name", "image", "cooking_time"]

    def to_representation(self, instance: ShoppingCart) -> Dict[str, Any]:
        """
        Convert a shopping cart instance into a dictionary representation.

        Args:
            instance (ShoppingCart): The shopping cart instance to represent.

        Returns:
            Dict[str, Any]:
                The dictionary representation of the shopping cart item.
        """

        request = self.context.get("request")
        context = {"request": request}
        return FavoriteSerializer(
            instance.recipe, context=context).data
