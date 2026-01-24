"""Check source lines for recipes with known fire degrees."""
import json

with open('data/brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# Check first 10 recipes (which have fire degrees)
for r in d['recipes'][:10]:
    print(f"\nRecipe {r['id']}: {r['name_english']}")
    print(f"  fire_degree: {r['fire_degree']}")
    print(f"  source_lines: {r.get('source_lines', {})}")
