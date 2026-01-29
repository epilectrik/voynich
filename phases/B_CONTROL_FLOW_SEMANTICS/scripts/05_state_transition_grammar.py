"""
05_state_transition_grammar.py

Build formal state transition rules from observed patterns.
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

token_to_role = class_data['token_to_role']

# Role abbreviations
ROLE_ABBREV = {
    'ENERGY_OPERATOR': 'EN',
    'FLOW_OPERATOR': 'FL',
    'FREQUENT_OPERATOR': 'FQ',
    'CORE_CONTROL': 'CC',
    'AUXILIARY': 'AX',
    'UN': 'UN'
}

tx = Transcript()

print("=" * 70)
print("State Transition Grammar")
print("=" * 70)

# Build role-level bigrams
role_bigrams = Counter()
role_counts = Counter()

# Build token sequences by line
line_sequences = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_sequences[key].append(t)

for key, tokens in line_sequences.items():
    for i in range(len(tokens)):
        role = token_to_role.get(tokens[i].word, 'UN')
        role_counts[role] += 1

        if i < len(tokens) - 1:
            next_role = token_to_role.get(tokens[i+1].word, 'UN')
            role_bigrams[(role, next_role)] += 1

# Calculate transition probabilities
print("\n" + "=" * 70)
print("Role Transition Matrix")
print("=" * 70)

roles = ['EN', 'FL', 'FQ', 'CC', 'AX', 'UN']
role_full = {'EN': 'ENERGY_OPERATOR', 'FL': 'FLOW_OPERATOR', 'FQ': 'FREQUENT_OPERATOR',
             'CC': 'CORE_CONTROL', 'AX': 'AUXILIARY', 'UN': 'UN'}

# Header
print(f"\n{'FROM/TO':>8}", end='')
for r in roles:
    print(f"{r:>8}", end='')
print()
print("-" * 56)

transition_matrix = {}
for from_role in roles:
    from_full = role_full[from_role]
    total_from = sum(role_bigrams.get((from_full, role_full[to_r]), 0) for to_r in roles)

    print(f"{from_role:>8}", end='')
    transition_matrix[from_role] = {}

    for to_role in roles:
        to_full = role_full[to_role]
        count = role_bigrams.get((from_full, to_full), 0)
        pct = count / total_from * 100 if total_from > 0 else 0
        transition_matrix[from_role][to_role] = round(pct, 1)
        print(f"{pct:7.1f}%", end='')
    print()

# Identify high-probability transitions (>15%)
print("\n" + "=" * 70)
print("High-Probability Transitions (>15%)")
print("=" * 70)

high_prob = []
for from_r, to_dict in transition_matrix.items():
    for to_r, pct in to_dict.items():
        if pct > 15:
            high_prob.append((from_r, to_r, pct))

high_prob.sort(key=lambda x: -x[2])
for from_r, to_r, pct in high_prob:
    print(f"  {from_r} -> {to_r}: {pct:.1f}%")

# Identify low-probability transitions (<5%)
print("\n" + "=" * 70)
print("Rare Transitions (<5%)")
print("=" * 70)

low_prob = []
for from_r, to_dict in transition_matrix.items():
    for to_r, pct in to_dict.items():
        if pct < 5 and pct > 0:
            low_prob.append((from_r, to_r, pct))

low_prob.sort(key=lambda x: x[2])
for from_r, to_r, pct in low_prob[:15]:
    print(f"  {from_r} -> {to_r}: {pct:.1f}%")

# Self-loops
print("\n" + "=" * 70)
print("Self-Loop Rates (Role Persistence)")
print("=" * 70)

for role in roles:
    self_rate = transition_matrix[role][role]
    print(f"  {role} -> {role}: {self_rate:.1f}%")

# Canonical flow patterns
print("\n" + "=" * 70)
print("Canonical Flow Patterns")
print("=" * 70)

# Check LINK -> KERNEL -> FL pattern
ax_to_en = transition_matrix['AX']['EN']
en_to_fl = transition_matrix['EN']['FL']
fl_to_en = transition_matrix['FL']['EN']

print(f"""
Expected: AX(LINK) -> EN -> FL

Observed:
  AX -> EN: {ax_to_en:.1f}%
  EN -> FL: {en_to_fl:.1f}%
  FL -> EN (loop back): {fl_to_en:.1f}%

Escape patterns:
  EN -> FQ (escape from processing): {transition_matrix['EN']['FQ']:.1f}%
  FL -> FQ (escape from state): {transition_matrix['FL']['FQ']:.1f}%
  FQ -> EN (recovery): {transition_matrix['FQ']['EN']:.1f}%

Control injection:
  CC -> EN: {transition_matrix['CC']['EN']:.1f}%
  CC -> FL: {transition_matrix['CC']['FL']:.1f}%
""")

# Build formal grammar
print("\n" + "=" * 70)
print("Formal Transition Grammar")
print("=" * 70)

print("""
LEGAL TRANSITIONS (>15%):
""")
for from_r, to_r, pct in high_prob:
    print(f"  {from_r} -> {to_r}  [{pct:.0f}%]")

print("""

RARE TRANSITIONS (<5%):
""")
for from_r, to_r, pct in low_prob[:10]:
    print(f"  {from_r} -> {to_r}  [{pct:.1f}%]")

# Save results
results = {
    'transition_matrix': transition_matrix,
    'high_probability': [(f, t, p) for f, t, p in high_prob],
    'low_probability': [(f, t, p) for f, t, p in low_prob],
    'self_loops': {r: transition_matrix[r][r] for r in roles},
    'canonical_patterns': {
        'ax_to_en': ax_to_en,
        'en_to_fl': en_to_fl,
        'fl_to_en': fl_to_en,
        'en_to_fq': transition_matrix['EN']['FQ'],
        'fq_to_en': transition_matrix['FQ']['EN']
    }
}

results_dir = Path(__file__).parent.parent / "results"
output_path = results_dir / "state_transition_grammar.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")
