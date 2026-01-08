"""Check what grammar class daiin belongs to in Currier B."""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

# Load the canonical grammar
grammar_path = project_root / 'results' / 'canonical_grammar.json'
with open(grammar_path) as f:
    grammar = json.load(f)

print("=" * 70)
print("DAIIN IN CURRIER B GRAMMAR")
print("=" * 70)

# Find which class daiin belongs to
daiin_class = None
for class_id, members in grammar.items():
    if 'daiin' in members:
        daiin_class = class_id
        print(f'\ndaiin belongs to: CLASS {class_id}')
        print(f'Class size: {len(members)} members')
        print(f'\nFirst 30 members:')
        for m in sorted(members)[:30]:
            print(f'  {m}')
        if len(members) > 30:
            print(f'  ... and {len(members)-30} more')
        break

if not daiin_class:
    print('\ndaiin not found directly in any grammar class!')
    print('Searching for daiin-containing tokens...')
    for class_id, members in grammar.items():
        matches = [m for m in members if 'daiin' in m]
        if matches:
            print(f'\nClass {class_id} has {len(matches)} daiin-related tokens:')
            for m in matches[:10]:
                print(f'  {m}')

# Also check what other da- tokens are in the same class
if daiin_class:
    print(f"\n" + "=" * 70)
    print(f"OTHER da- TOKENS IN CLASS {daiin_class}")
    print("=" * 70)
    da_members = [m for m in grammar[daiin_class] if m.startswith('da')]
    print(f"\nda- tokens in this class ({len(da_members)}):")
    for m in sorted(da_members):
        print(f'  {m}')

# Check what classes other common tokens belong to
print(f"\n" + "=" * 70)
print("COMPARISON: Classes of other common tokens")
print("=" * 70)

check_tokens = ['chol', 'chor', 'shol', 'aiin', 'chedy', 'qokedy', 'ol', 'or', 'ar']
for tok in check_tokens:
    for class_id, members in grammar.items():
        if tok in members:
            print(f'{tok}: Class {class_id} ({len(members)} members)')
            break
    else:
        print(f'{tok}: NOT FOUND in grammar')

# Load hazards to see if daiin is involved in any forbidden transitions
print(f"\n" + "=" * 70)
print("DAIIN AND FORBIDDEN TRANSITIONS")
print("=" * 70)

# Check the hazards module
import sys
sys.path.insert(0, str(project_root / 'vee' / 'app' / 'core'))
try:
    from hazards import FORBIDDEN_PAIRS

    # Find if daiin's class is in any forbidden pair
    daiin_hazards = []
    for pair in FORBIDDEN_PAIRS:
        if daiin_class in pair:
            daiin_hazards.append(pair)

    if daiin_hazards:
        print(f"\nClass {daiin_class} (containing daiin) appears in {len(daiin_hazards)} forbidden pairs:")
        for p in daiin_hazards:
            print(f"  {p}")
    else:
        print(f"\nClass {daiin_class} (containing daiin) is NOT in any forbidden transitions")
except ImportError:
    print("\nCould not load hazards module")

# Summary
print(f"\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
if daiin_class:
    print(f"\nIn Currier B's 49-class grammar:")
    print(f"  - daiin belongs to Class {daiin_class}")
    print(f"  - This class has {len(grammar[daiin_class])} member tokens")
