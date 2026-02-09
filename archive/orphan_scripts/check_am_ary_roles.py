#!/usr/bin/env python3
"""Check what roles the -am/-y tokens have."""

import json
from pathlib import Path

class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    data = json.load(f)

token_to_role = data.get('token_to_role', {})
token_to_class = data.get('token_to_class', {})

tokens = ['am', 'dam', 'otam', 'oly', 'oldy', 'daly', 'ldy', 'ary']

print('Token         Role                  Class')
print('-' * 50)
for t in tokens:
    role = token_to_role.get(t, 'NOT FOUND')
    cls = token_to_class.get(t, '?')
    print(f'{t:<13} {role:<20} {cls}')

# Check what FL tokens look like
print('\n\nAll FLOW_OPERATOR tokens:')
fl_tokens = [t for t, r in token_to_role.items() if r == 'FLOW_OPERATOR']
print(f'Count: {len(fl_tokens)}')
print('Examples:', fl_tokens[:20])
