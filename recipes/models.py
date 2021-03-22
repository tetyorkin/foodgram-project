from django.core.validators import MinValueValidator
from django.db import models
from multiselectfield import MultiSelectField

from users.models import User


class Ingredient(models.Model):
    title = models.CharField(max_length=100, verbose_name='название')
    dimension = models.CharField(
        max_length=50,
        verbose_name='единица измерения',
        default='г.',
    )
