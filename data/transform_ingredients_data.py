import json


def transform_json(input_file, output_file, app_name):
    # Load the current JSON data
    with open(input_file, 'r', encoding='utf-8') as file:
        current_data = json.load(file)

    # Set to keep track of unique names
    unique_names = set()

    # Transform the data to fit the Django fixture format
    transformed_data = []
    for item in current_data:
        name = item['name']
        # Check for duplicate names
        if name not in unique_names:
            transformed_data.append({
                "model": f"{app_name}.ingredient",
                "fields": item
            })
            unique_names.add(name)
        else:
            print(f"Duplicate found, skipping: {name}")

    # Save the transformed data to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(transformed_data, file, ensure_ascii=False, indent=4)


# Usage
input_file = 'ingredients.json'  # Path to your original JSON file
output_file = 'transformed_ingredients.json'  # Path for the transformed file
app_name = 'recipes'  # Your Django app name

transform_json(input_file, output_file, app_name)
