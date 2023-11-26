import csv

from backend.recipes.models import Ingredient


def import_ingredients_from_csv(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            name, measurement_unit = row
            Ingredient.objects.create(
                name=name, measurement_unit=measurement_unit)


if __name__ == "__main__":
    csv_file_path = 'ingredients.csv'
    import_ingredients_from_csv(csv_file_path)
