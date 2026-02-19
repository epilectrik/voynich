"""Fix per-region metadata with correct physical positions from voynich.nu mapping."""
import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / 'results'
ref_path = RESULTS / 'rosettes_reference.json'

with open(ref_path, 'r', encoding='utf-8') as f:
    ref = json.load(f)

# Correct mapping from voynich.nu fRos_tr.txt
# Letter = ROW: V=top, N=middle, C=bottom
# Number = COL: 1=left, 2=center, 3=right
# Labels: U=top row, M=middle row, B=bottom row

POSITION_MAP = {
    # Ring text regions
    'V1': {'position': 'NW_CORNER', 'rosette': 'NW', 'type': 'RING_TEXT'},
    'V2': {'position': 'NORTH_CARDINAL', 'rosette': 'NORTH', 'type': 'RING_TEXT'},
    'N1': {'position': 'WEST_CARDINAL', 'rosette': 'WEST', 'type': 'RING_TEXT'},
    'N2': {'position': 'CENTER', 'rosette': 'CENTER', 'type': 'RING_TEXT'},
    'C2': {'position': 'SOUTH_CARDINAL', 'rosette': 'SOUTH', 'type': 'RING_TEXT'},
    # Label regions
    'U1': {'position': 'NW_CORNER', 'rosette': 'NW', 'type': 'LABEL'},
    'U2': {'position': 'NORTH_CARDINAL', 'rosette': 'NORTH', 'type': 'LABEL'},
    'U3': {'position': 'NE_CORNER', 'rosette': 'NE', 'type': 'LABEL'},
    'M1': {'position': 'WEST_CARDINAL', 'rosette': 'WEST', 'type': 'LABEL'},
    'M2': {'position': 'CENTER', 'rosette': 'CENTER', 'type': 'LABEL'},
    'M3': {'position': 'SE_CORNER', 'rosette': 'SE', 'type': 'LABEL'},
    'B1': {'position': 'SW_CORNER', 'rosette': 'SW', 'type': 'LABEL'},
    'B2': {'position': 'SOUTH_CARDINAL', 'rosette': 'SOUTH', 'type': 'LABEL'},
    'B3': {'position': 'SE_CORNER', 'rosette': 'SE', 'type': 'LABEL'},
    # Special
    'D1': {'position': 'SW_CORNER_DOODLE', 'rosette': 'SW', 'type': 'CORNER_DOODLE'},
    'W1': {'position': 'NW_MARGIN', 'rosette': 'NW', 'type': 'MARGIN'},
}

for region_code, region_data in ref['regions'].items():
    mapping = POSITION_MAP.get(region_code)
    if mapping:
        region_data['metadata']['physical_position'] = mapping['position']
        region_data['metadata']['rosette'] = mapping['rosette']
        region_data['metadata']['text_type'] = mapping['type']
        old_type = region_data['metadata'].get('type', '')
        # Update notes
        region_data['metadata']['notes'] = (
            f"[{mapping['type']}] on {mapping['rosette']} rosette ({mapping['position']}). "
            + region_data['metadata'].get('notes', '')
        )
        print(f'{region_code}: {mapping["rosette"]:6s} {mapping["type"]:<12s} ({mapping["position"]})')

with open(ref_path, 'w', encoding='utf-8') as f:
    json.dump(ref, f, indent=2, ensure_ascii=False)

print(f'\nUpdated {ref_path}')

# Print the corrected summary
print('\n' + '=' * 70)
print('CORRECTED ROSETTE-TO-REGION MAPPING')
print('=' * 70)
print()
print('Physical     Ring Text    Labels       Special')
print('-' * 55)
rosette_summary = {}
for code, m in POSITION_MAP.items():
    ros = m['rosette']
    if ros not in rosette_summary:
        rosette_summary[ros] = {'ring': [], 'labels': [], 'special': []}
    if m['type'] == 'RING_TEXT':
        rosette_summary[ros]['ring'].append(code)
    elif m['type'] == 'LABEL':
        rosette_summary[ros]['labels'].append(code)
    else:
        rosette_summary[ros]['special'].append(f"{code}({m['type']})")

for ros in ['NW', 'NORTH', 'NE', 'WEST', 'CENTER', 'EAST', 'SW', 'SOUTH', 'SE']:
    s = rosette_summary.get(ros, {'ring': [], 'labels': [], 'special': []})
    ring = ','.join(s['ring']) or '(other panel)'
    labels = ','.join(s['labels']) or '(none on f85v2)'
    special = ','.join(s['special']) or ''
    print(f'{ros:<12s} {ring:<12s} {labels:<12s} {special}')

# Print vocabulary profile per ROSETTE (combining ring + labels)
print('\n' + '=' * 70)
print('VOCABULARY PROFILE PER PHYSICAL ROSETTE')
print('=' * 70)
print()
print(f'{"Rosette":<10s} {"Tokens":<8s} {"Ring":<6s} {"Label":<6s} {"Bridge%":<10s} {"HUB%":<8s}')
print('-' * 50)

for ros in ['NW', 'NORTH', 'NE', 'WEST', 'CENTER', 'EAST', 'SW', 'SOUTH', 'SE']:
    s = rosette_summary.get(ros, {'ring': [], 'labels': [], 'special': []})
    all_codes = s['ring'] + s['labels'] + [c.split('(')[0] for c in s['special']]
    total_tokens = 0
    ring_tokens = 0
    label_tokens = 0
    bridge_total = 0
    hub_total = 0
    for code in all_codes:
        if code in ref['regions']:
            r = ref['regions'][code]
            n = r['summary']['n_tokens']
            total_tokens += n
            bridge_total += r['summary']['bridge_count']
            hub_total += r['summary']['hub_count']
            if code in [c for c in s['ring']]:
                ring_tokens += n
            else:
                label_tokens += n

    if total_tokens > 0:
        bf = bridge_total / total_tokens
        hf = hub_total / total_tokens
        print(f'{ros:<10s} {total_tokens:<8d} {ring_tokens:<6d} {label_tokens:<6d} {bf:<10.1%} {hf:<8.1%}')
    else:
        print(f'{ros:<10s} {"(no data on f85v2)":<8s}')
