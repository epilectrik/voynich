import json
with open('results/exclusive_middle_backprop.json', 'r') as f:
    data = json.load(f)
fc = data['a_folio_classifications']
for k, v in list(fc.items())[:5]:
    print(f'{k}: {v} (type: {type(v).__name__})')
