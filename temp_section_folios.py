import json
with open('results/azc_folio_features.json') as f:
    data = json.load(f)

sections = {}
for fid, fdata in data['folios'].items():
    sec = fdata['section']
    if sec not in sections:
        sections[sec] = []
    sections[sec].append((fid, fdata['token_count'], fdata.get('unique_types', 0)))

for sec in ['Z', 'A', 'C', 'H', 'S']:
    if sec in sections:
        print(f'\n=== Section {sec} ===')
        total = sum(tc for _, tc, _ in sections[sec])
        print(f'Total tokens: {total}')
        for fid, tc, ut in sorted(sections[sec]):
            print(f'  {fid}: {tc} tokens, {ut} unique')
