"""
00_role_semantic_census.py

GATE script: Build comprehensive role profiles with semantic annotations.
Combines structural facts from class_token_map with FL semantic model.
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# Load class map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}
token_to_role = class_data['token_to_role']
class_to_role = class_data['class_to_role']

# Load FL semantic model
fl_model_path = Path(__file__).resolve().parents[3] / "phases/FL_SEMANTIC_INTERPRETATION/results/04_fl_semantic_model.json"
with open(fl_model_path) as f:
    fl_model = json.load(f)

FL_STAGE_MAP = fl_model['fl_stage_map']
# Invert for lookup
MIDDLE_TO_STAGE = {}
for stage, middles in FL_STAGE_MAP.items():
    for m in middles:
        MIDDLE_TO_STAGE[m] = stage

tx = Transcript()
morph = Morphology()

# Kernel characters
KERNEL_CHARS = set('khe')

# Build role profiles
role_profiles = defaultdict(lambda: {
    'tokens': [],
    'types': set(),
    'middles': Counter(),
    'positions': [],
    'kernel_count': 0,
    'hazard_count': 0,
    'classes': set()
})

# Hazard classes (from BCSC)
HAZARD_CLASSES = {7, 30, 38, 40}  # FL classes that are hazard

print("=" * 70)
print("Building Role Semantic Census")
print("=" * 70)

# Process all B tokens
for t in tx.currier_b():
    role = token_to_role.get(t.word, 'UNKNOWN')
    cls = token_to_class.get(t.word, -1)

    m = morph.extract(t.word)
    middle = m.middle if m else None

    # Check for kernel
    has_kernel = any(c in t.word for c in KERNEL_CHARS)

    # Check hazard (FL in hazard classes)
    is_hazard = cls in HAZARD_CLASSES

    # Get line position (normalized)
    # We need to calculate this from line context
    role_profiles[role]['tokens'].append(t.word)
    role_profiles[role]['types'].add(t.word)
    if middle:
        role_profiles[role]['middles'][middle] += 1
    if has_kernel:
        role_profiles[role]['kernel_count'] += 1
    if is_hazard:
        role_profiles[role]['hazard_count'] += 1
    role_profiles[role]['classes'].add(cls)

# Calculate positions by role
print("\nCalculating positional profiles...")
role_positions = defaultdict(list)

# Group tokens by folio+line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)

# Calculate normalized positions
for key, tokens in line_tokens.items():
    if len(tokens) == 0:
        continue
    for i, t in enumerate(tokens):
        pos = i / len(tokens) if len(tokens) > 1 else 0.5
        role = token_to_role.get(t.word, 'UNKNOWN')
        role_positions[role].append(pos)

# Build output
output = {
    'metadata': {
        'total_tokens': sum(len(p['tokens']) for p in role_profiles.values()),
        'total_types': sum(len(p['types']) for p in role_profiles.values()),
        'roles': list(role_profiles.keys())
    },
    'roles': {}
}

print("\n" + "=" * 70)
print("Role Profiles")
print("=" * 70)

for role in sorted(role_profiles.keys()):
    p = role_profiles[role]
    token_count = len(p['tokens'])
    type_count = len(p['types'])
    kernel_rate = p['kernel_count'] / token_count if token_count > 0 else 0
    hazard_rate = p['hazard_count'] / token_count if token_count > 0 else 0
    positions = role_positions[role]
    mean_pos = sum(positions) / len(positions) if positions else 0.5

    # Top middles
    top_middles = p['middles'].most_common(10)

    # Semantic annotations based on role
    # Note: class_token_map uses full names (FLOW_OPERATOR, ENERGY_OPERATOR, etc.)
    # LINK is class 29 which falls under AUXILIARY
    semantic = {}
    if role == 'FLOW_OPERATOR':
        semantic = {
            'function': 'state_index',
            'stage_map': FL_STAGE_MAP,
            'domain_hint': 'material_position',
            'interpretation': 'Indexes where material is in transformation process',
            'abbreviation': 'FL'
        }
    elif role == 'ENERGY_OPERATOR':
        semantic = {
            'function': 'transition_operator',
            'kernel_types': {'k': 'energy/activation', 'h': 'phase/alignment', 'e': 'stability/verification'},
            'interpretation': 'Drives state transitions via kernel injection',
            'abbreviation': 'EN'
        }
    elif role == 'CORE_CONTROL':
        semantic = {
            'function': 'control_word',
            'key_tokens': ['daiin', 'ol'],
            'interpretation': 'High-frequency control tokens with positional bias',
            'abbreviation': 'CC'
        }
    elif role == 'FREQUENT_OPERATOR':
        semantic = {
            'function': 'escape_handler',
            'trigger': 'hazard_state',
            'interpretation': 'Provides escape route from unstable states',
            'abbreviation': 'FQ'
        }
    elif role == 'AUXILIARY':
        semantic = {
            'function': 'support_operation',
            'includes_link': True,
            'link_class': 29,
            'interpretation': 'Auxiliary operations including LINK (class 29) monitoring',
            'abbreviation': 'AX'
        }
    else:
        semantic = {
            'function': 'unknown',
            'interpretation': 'Unclassified tokens (not in 49-class system)',
            'abbreviation': 'UN'
        }

    output['roles'][role] = {
        'token_count': token_count,
        'type_count': type_count,
        'kernel_rate': round(kernel_rate, 4),
        'hazard_rate': round(hazard_rate, 4),
        'mean_position': round(mean_pos, 4),
        'classes': sorted(list(p['classes'])),
        'top_middles': [(m, c) for m, c in top_middles],
        'semantic_annotations': semantic
    }

    print(f"\n{role}")
    print("-" * 40)
    print(f"  Tokens: {token_count:,} | Types: {type_count}")
    print(f"  Kernel rate: {kernel_rate:.1%}")
    print(f"  Hazard rate: {hazard_rate:.1%}")
    print(f"  Mean position: {mean_pos:.3f}")
    print(f"  Classes: {sorted(list(p['classes']))[:10]}{'...' if len(p['classes']) > 10 else ''}")
    print(f"  Top MIDDLEs: {', '.join(m for m, _ in top_middles[:5])}")
    print(f"  Function: {semantic.get('function', 'unknown')}")

# Role distribution summary
print("\n" + "=" * 70)
print("Role Distribution Summary")
print("=" * 70)

total = output['metadata']['total_tokens']
for role in sorted(output['roles'].keys(), key=lambda r: -output['roles'][r]['token_count']):
    count = output['roles'][role]['token_count']
    pct = count / total * 100
    bar = '#' * int(pct / 2)
    print(f"  {role:20} {count:6,} ({pct:5.1f}%) {bar}")

# Save results
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)
output_path = results_dir / "role_semantic_census.json"
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to {output_path}")

# Verification
print("\n" + "=" * 70)
print("Verification")
print("=" * 70)
print(f"Total tokens: {total:,} (expected: ~23,096)")
print(f"Roles found: {len(output['roles'])}")
print(f"All roles have semantic annotations: {all('semantic_annotations' in r for r in output['roles'].values())}")
