import json
with open('results/azc_folio_features.json') as f:
    data = json.load(f)
sections = {}
for fid, fdata in data.get('folios', {}).items():
    sec = fdata.get('section', 'UNKNOWN')
    sections[sec] = sections.get(sec, 0) + 1
print('Sections:', sections)
print('Total folios with features:', len(data.get('folios', {})))
