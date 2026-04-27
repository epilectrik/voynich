import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

d = json.loads(open('phases/SISMEL_RECIPE_CORPUS/results/sismel_subrecipes.json', encoding='utf-8').read())
for s in d['subrecipes']:
    if s['id'].startswith('II.18'):
        print(f"=== {s['id']} ===")
        cat = s.get('catalan', '')
        if cat:
            print(cat)
        else:
            print('[no catalan text]')
        print()
