from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    title = models.CharField(max_length=100, verbose_name='название')
    dimension = models.CharField(
        max_length=50,
        verbose_name='единица измерения',
        default='г.',
    )

    def __str__(self):
        return f'{self.title} {self.dimension}'


class Tag(models.Model):
    title = models.CharField(max_length=8)
    slug = models.SlugField(unique=True, max_length=50, blank=True, null=True)
    color = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='media/', blank=True, null=True)
    description = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientItem',
        through_fields=('recipe', 'ingredients'),
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, related_name='recipe_tag',
                                  verbose_name='Тэг')
    slug = models.SlugField(db_index=True)
    duration = models.PositiveSmallIntegerField(
        'время приготовления', validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.title} | {self.author} '


class IngredientItem(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты'
    )
    ingredients = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингридиент'
    )
    count = models.FloatField()

    def __str__(self):
        return f'{self.recipe}'


class Favorites(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='fans'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class Subscribe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribes"
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class ShopList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipes = models.ManyToManyField(Recipe, verbose_name='Список рецептов')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
