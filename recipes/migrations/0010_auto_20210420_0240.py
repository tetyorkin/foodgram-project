# Generated by Django 3.1.7 on 2021-04-19 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20210420_0228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientitem',
            name='count',
            field=models.IntegerField(),
        ),
    ]
