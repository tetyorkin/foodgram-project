# Generated by Django 3.1.7 on 2021-04-05 12:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20210405_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientitem',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Ингридиент'),
        ),
        migrations.AlterField(
            model_name='ingredientitem',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='recipes.recipe'),
        ),
    ]
