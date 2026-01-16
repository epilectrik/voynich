import json
with open('results/azc_folio_features.json') as f:
    data = json.load(f)
print('Folios in azc_folio_features.json:')
by_section = {}
for fid in sorted(data['folios'].keys()):
    sec = data['folios'][fid].get('section', '?')
    if sec not in by_section:
        by_section[sec] = []
    by_section[sec].append(fid)

for sec in sorted(by_section.keys()):
    print(f'\n{sec}: {len(by_section[sec])} folios')
    for fid in by_section[sec]:
        print(f'  {fid}')

print(f'\nTotal: {len(data["folios"])}')
print(f'\nExpected: 36 (per fits file)')
print(f'Missing: {36 - len(data["folios"])}')
