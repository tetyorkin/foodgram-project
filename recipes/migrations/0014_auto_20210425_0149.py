# Generated by Django 3.1.7 on 2021-04-24 19:49

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0013_auto_20210425_0138'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subscribe',
            unique_together={('author', 'user')},
        ),
    ]
