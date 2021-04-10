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
        return f'{self.title}'


class Tag(models.Model):
    tag_options = {
        'breakfast': ['orange', 'Завтрак'],
        'lunch': ['green', 'Обед'],
        'dinner': ['purple', 'Ужин'],
    }

    TAG_CHOICES = [('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
    ]
    title = models.CharField(
        max_length=20, choices=TAG_CHOICES, verbose_name='tag name'
    )

    def __str__(self):
        return self.title

    @property
    def color(self):
        return self.tag_options[self.title][0]

    @property
    def name(self):
        return self.tag_options[self.title][1]


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='media/', blank=True, null=True)
    description = models.TextField()
    ingredient = models.ManyToManyField(
        Ingredient,
        through='IngredientItem',
        verbose_name='Ингредиенты',
    )
    tag = models.ManyToManyField(Tag, verbose_name='Тэг',
                                 on_delete=models.CASCADE)
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
        return f'{self.title} '


class IngredientItem(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.DO_NOTHING,
        related_name='ingredients',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингридиент',
    )
    count = models.IntegerField()

    def __str__(self):
        return f'{self.ingredients}'


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
