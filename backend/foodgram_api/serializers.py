from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Favorite,
    ShoppingCart,
)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = ("id", "name", "measurement_unit")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(method_name="get_is_favorited")
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe_id=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user, recipe_id=obj).exists()


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError("The amount must be greater than 0.")
        return value

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = AddRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        write_only=True, min_value=1, max_value=32_000
    )

    class Meta:
        model = Recipe
        fields = [
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        ]

    def validate_ingredients(self, ingredients):
        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if not Ingredient.objects.filter(id__in=ingredient_ids).exists():
            raise serializers.ValidationError("One or more ingredients do not exist.")
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError("Ingredients must not be repetitive.")
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError({"error": "Укажите тэг!"})
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError({"error": "Тэги не должны повторяться."})
        return tags

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError("Cooking time must be greater than zero.")
        return value

    def validate(self, data):
        """Метод валидации для создания рецепта."""
        ingredients = data.get("ingredients")
        tags = data.get("tags")

        if not ingredients:
            raise serializers.ValidationError({"error": "Выберите ингредиенты!"})

        if not tags:
            raise serializers.ValidationError({"error": "Укажите тэг!"})

        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError("Ингредиенты не должны повторяться.")

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError("Тэги не должны повторяться.")

        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Image field cannot be empty.")
        return value

    def create_ingredients(self, ingredients, recipe):
        for i in ingredients:
            ingredient = Ingredient.objects.get(id=i["id"])
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe, amount=i["amount"]
            )

    def create_tags(self, tags, recipe):
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        validated_data.pop("author", None)
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.create_ingredients(ingredients, instance)

        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        image = validated_data.pop('image', None)
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


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time")

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return FavoriteSerializer(instance.recipe, context=context).data
