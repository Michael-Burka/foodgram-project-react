from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Clears all data from the Ingredient model"

    def handle(self, *args, **kwargs):
        Ingredient.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS("Successfully cleared all Ingredient data")
        )
