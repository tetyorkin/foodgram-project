# Generated by Django 3.1.7 on 2021-04-19 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20210411_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientitem',
            name='count',
            field=models.PositiveIntegerField(),
        ),
    ]
