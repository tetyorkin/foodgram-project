from django.core.validators import MinValueValidator
from django.db import models
from multiselectfield import MultiSelectField

from users.models import User

TAG = (('breakfast', 'Завтрак'), ('dinner', 'Обед'), ('supper', 'Ужин'))


class Ingredient(models.Model):
    title = models.CharField(max_length=100, verbose_name='название')
    dimension = models.CharField(
        max_length=50,
        verbose_name='единица измерения',
        default='г.',
    )

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='media/', blank=True, null=True)
    description = models.TextField()
    ingredients = models.ManyToManyField('IngredientItem')
    tags = MultiSelectField(max_choices=3, choices=TAG)
    duration = models.PositiveSmallIntegerField(
        'время приготовления', validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.title} by {self.author} '


class IngredientItem(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    count = models.DecimalField(
        verbose_name='кол-во', max_digits=6, decimal_places=1
    )

    class Meta:
        verbose_name = 'Ингредиент из рецепта'
        verbose_name_plural = 'Ингредиенты из рецептов'

    def __str__(self):
        return (
            f'{self.ingredient.title} - {self.count} '
            f'{self.ingredient.dimension}'
        )
