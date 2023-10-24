from django.db import models


class Recipe(models.Model):
    author = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, verbose_name="Автор публикации"
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    image = models.ImageField(upload_to="recipes/", verbose_name="Картинка")
    description = models.TextField(verbose_name="Текстовое описание")
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления в минутах"
    )

    @property
    def favorites_count(self):
        return self.favorited_by.count()

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class Tag(models.Model):
    name = models.CharField(
            max_length=100, unique=True, verbose_name="Название"
    )
    color_code = models.CharField(
        max_length=7, unique=True, verbose_name="Цветовой код"
    )
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    recipes = models.ManyToManyField(
            Recipe, through="RecipeTag", related_name="tags"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Unit(models.Model):
    name = models.CharField(
        max_length=50, unique=True, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"


class Ingredient(models.Model):
    name = models.CharField(
            max_length=255, unique=True, verbose_name="Название"
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Тег рецепта"
        verbose_name_plural = "Теги рецептов"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецептов"


class Favorite(models.Model):
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorited_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="shopping_lists"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="in_shopping_lists"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"


class Subscription(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата подписки"
    )

    class Meta:
        unique_together = ("user", "author")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
