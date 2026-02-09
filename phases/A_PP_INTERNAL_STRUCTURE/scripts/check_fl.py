import json
from collections import Counter

with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)

# Check FL classes (7, 30, 38, 40)
fl_classes = {7, 30, 38, 40}
print('Tokens in FL classes:')
class_to_tokens = data.get('class_to_tokens', {})
for cls_id in fl_classes:
    tokens = class_to_tokens.get(str(cls_id), [])
    print(f'  Class {cls_id}: {len(tokens)} tokens - {tokens[:10]}')

# Check what roles are in the data
print('\nRoles in token_to_role:')
roles = Counter(data.get('token_to_role', {}).values())
for role, count in roles.most_common():
    print(f'  {role}: {count}')

# Check how many tokens total
print(f'\nTotal tokens in map: {len(data.get("token_to_class", {}))}')

# What about FL MIDDLEs like 'y', 'am', 'm', etc?
print('\nChecking FL-related MIDDLEs in token_to_middle:')
fl_middles = ['y', 'am', 'm', 'dy', 'ry', 'ly', 'al', 'ol', 'l', 'ar', 'r', 'in', 'i', 'ii']
token_to_middle = data.get('token_to_middle', {})
token_to_class = data.get('token_to_class', {})
for mid in fl_middles:
    tokens_with_mid = [t for t, m in token_to_middle.items() if m == mid]
    if tokens_with_mid:
        sample = tokens_with_mid[:3]
        classes = [token_to_class.get(t, '?') for t in sample]
        print(f'  {mid}: {len(tokens_with_mid)} tokens, classes: {classes}')
