import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

d = json.loads(open('phases/SISMEL_RECIPE_CORPUS/results/sismel_subrecipes.json', encoding='utf-8').read())
for s in d['subrecipes']:
    if s['id'].startswith('III.22'):
        print(f"=== {s['id']} ===")
        print(f"Title: {s.get('title', '')}")
        cat = s.get('catalan', '')
        if cat:
            print(f"\nCatalan ({len(cat)} chars):")
            print(cat)
        lat = s.get('latin', '')
        if lat:
            print(f"\nLatin ({len(lat)} chars):")
            print(lat)
        print()
