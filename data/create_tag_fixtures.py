import json

def create_tag_fixtures(output_file):
    # Fixture data for 6 tags
    fixture_data = [
        {
            "model": "recipes.tag",
            "fields": {
                "name": "Vegan",
                "color": "#1E8E3E",
                "slug": "vegan"
            }
        },
        {
            "model": "recipes.tag",
            "fields": {
                "name": "Gluten Free",
                "color": "#FFD700",
                "slug": "gluten-free"
            }
        },
        {
            "model": "recipes.tag",
            "fields": {
                "name": "No Sugar",
                "color": "#FF4500",
                "slug": "no-sugar"
            }
        },
        {
            "model": "recipes.tag",
            "fields": {
                "name": "Low Carb",
                "color": "#6495ED",
                "slug": "low-carb"
            }
        },
        {
            "model": "recipes.tag",
            "fields": {
                "name": "Organic",
                "color": "#32CD32",
                "slug": "organic"
            }
        },
        {
            "model": "recipes.tag",
            "fields": {
                "name": "Dairy Free",
                "color": "#FF69B4",
                "slug": "dairy-free"
            }
        }
    ]

    # Save the fixture data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(fixture_data, file, ensure_ascii=False, indent=4)

# Usage
output_file = 'tag_fixtures.json'  # Path for the output file
create_tag_fixtures(output_file)

