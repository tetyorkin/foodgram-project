import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredient data to DB'

    def handle(self, *args, **options):
        with open('ingredients.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                title, dimension = row
                Ingredient.objects.get_or_create(
                    title=title,
                    dimension=dimension
                )
