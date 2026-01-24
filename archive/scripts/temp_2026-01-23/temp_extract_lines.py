import json

with open('C:/git/voynich/data/brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get recipes 126-150
for recipe in data['recipes']:
    if 126 <= recipe['id'] <= 150:
        src = recipe.get('source_lines', {})
        print(f"Recipe {recipe['id']} ({recipe['name_english']}): lines {src.get('start', 'N/A')}-{src.get('end', 'N/A')}")
