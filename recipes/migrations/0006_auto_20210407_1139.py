# Generated by Django 3.1.7 on 2021-04-07 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20210405_1832'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='tags',
            new_name='tag',
        ),
    ]
