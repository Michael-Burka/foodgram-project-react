from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Name")
    color = models.CharField(max_length=7, unique=True, verbose_name="Color Code")
    slug = models.SlugField(
        max_length=200,
        verbose_name="Slug",
        unique=True,
        help_text="Enter slug",
        db_index=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Name")
    measurement_unit = models.CharField(max_length=200, verbose_name="Measurement Unit")

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Author",
        related_name='recipes'
    )
    name = models.CharField(max_length=200, verbose_name="Name")
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Tags',
        related_name='tags'
    )
    image = models.ImageField(upload_to="recipes/", verbose_name="Image")
    text = models.TextField(verbose_name="Description")
    cooking_time = models.PositiveIntegerField(
        verbose_name="Cooking Time in Minutes"
    )

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Recipe Tag"
        verbose_name_plural = "Recipe Tags"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name="Amount")

    class Meta:
        verbose_name = "Recipe Ingredient"
        verbose_name_plural = "Recipe Ingredients"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='favorites',
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='user_favorite_unique')
        ]
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_cart"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="in_shopping_cart"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Shopping Cart"
        verbose_name_plural = "Shopping Carts"
