# Generated by Django 3.1.7 on 2021-04-07 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20210407_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(to='recipes.Tag', verbose_name='Тэг'),
        ),
    ]