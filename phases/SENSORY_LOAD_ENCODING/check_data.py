import json

with open('results/unified_folio_profiles.json', 'r') as f:
    data = json.load(f)

print('Keys:', list(data.keys()))
if 'profiles' in data:
    print('Profile count:', len(data['profiles']))

    # Find B folios
    b_folios = [f for f, p in data['profiles'].items() if p.get('system') == 'B']
    print(f'B folios: {len(b_folios)}')

    for folio in b_folios[:2]:
        profile = data['profiles'][folio]
        print(f'\nSample B folio {folio}:')
        for k, v in profile.items():
            print(f'  {k}: {v}')
