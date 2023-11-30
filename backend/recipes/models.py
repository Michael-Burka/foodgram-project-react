from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name="Name"
    )
    color = models.CharField(
        max_length=7, unique=True, verbose_name="Color Code"
    )
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="Slug",
        help_text="Enter slug", db_index=True
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name="Name"
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name="Measurement Unit"
    )

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Author",
        related_name="recipes"
    )
    name = models.CharField(max_length=200, verbose_name="Name")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", verbose_name="Ingredients"
    )
    tags = models.ManyToManyField(
        Tag, through="RecipeTag", verbose_name="Tags", related_name="tags"
    )
    image = models.ImageField(
        upload_to="recipes/", verbose_name="Image"
    )
    text = models.TextField(verbose_name="Description")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Cooking Time in Minutes",
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Publication Date"
    )

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_tags"
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tag_recipes"
    )

    class Meta:
        verbose_name = "Recipe Tag"
        verbose_name_plural = "Recipe Tags"

    def __str__(self):
        return f"{self.recipe.name} - {self.tag.name}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name="Amount",
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Recipe Ingredient"
        verbose_name_plural = "Recipe Ingredients"

    def __str__(self):
        return (
            f"{self.ingredient.name} ({self.ingredient.measurement_unit})"
            f" in {self.recipe.name}"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="User",
        related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Recipe",
        related_name="favorites"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="user_favorite_unique"
            )
        ]
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"

    def __str__(self):
        return self.name


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
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"
