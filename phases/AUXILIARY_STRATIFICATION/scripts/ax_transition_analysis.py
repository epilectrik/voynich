"""
Q5: AUXILIARY Transition Analysis

Analyze AX's role in sequential grammar:
- What precedes/follows AX tokens?
- How do AX sub-groups interact with named roles?
- Where does AX fit in the CC->EN->FL->FQ transition grammar?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
CENSUS_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_census.json'
FEATURES_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_features.json'
RESULTS = BASE / 'phases/AUXILIARY_STRATIFICATION/results'

# Load data
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(CENSUS_FILE) as f:
    census = json.load(f)
AX_CLASSES = set(census['definitive_ax_classes'])

with open(FEATURES_FILE) as f:
    features = json.load(f)

# Role mapping
ICC_CC = {10, 11, 12, 17}
ICC_EN = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 23}

def get_role(cls):
    if cls is None: return 'UN'
    if cls in ICC_CC: return 'CC'
    if cls in ICC_EN: return 'EN'
    if cls in ICC_FL: return 'FL'
    if cls in ICC_FQ: return 'FQ'
    if cls in AX_CLASSES: return 'AX'
    return 'UN'

# Positional sub-groups from feature matrix
INIT_AX = {cls for cls in AX_CLASSES if features.get(str(cls), {}).get('initial_rate', 0) > 0.20}
FINAL_AX = {cls for cls in AX_CLASSES if features.get(str(cls), {}).get('final_rate', 0) > 0.20}
MEDIAL_AX = AX_CLASSES - INIT_AX - FINAL_AX

def get_ax_subgroup(cls):
    if cls in INIT_AX: return 'AX_INIT'
    if cls in FINAL_AX: return 'AX_FINAL'
    if cls in MEDIAL_AX: return 'AX_MED'
    return 'AX'

# Build lines
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    folio = token.folio
    line = token.line
    lines[(folio, line)].append({
        'word': word,
        'class': cls,
        'role': get_role(cls),
        'ax_sub': get_ax_subgroup(cls) if cls in AX_CLASSES else get_role(cls),
    })

print("=" * 70)
print("Q5: AUXILIARY TRANSITION ANALYSIS")
print("=" * 70)

# ============================================================
# 1. ROLE-LEVEL TRANSITIONS
# ============================================================
print("\n" + "-" * 70)
print("1. ROLE-LEVEL BIGRAM TRANSITIONS")
print("-" * 70)

role_bigrams = Counter()
role_totals = Counter()

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        r1 = line_tokens[i]['role']
        r2 = line_tokens[i+1]['role']
        role_bigrams[(r1, r2)] += 1
        role_totals[r1] += 1

roles = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']
print(f"\n{'':>5}", end='')
for r in roles:
    print(f" {r:>6}", end='')
print()

for r1 in roles:
    total = role_totals.get(r1, 0)
    if total == 0:
        continue
    print(f"{r1:>5}", end='')
    for r2 in roles:
        count = role_bigrams.get((r1, r2), 0)
        pct = count / total * 100 if total > 0 else 0
        print(f" {pct:5.1f}%", end='')
    print(f"  (n={total})")

# Compute expected rates for enrichment
total_transitions = sum(role_totals.values())
role_right_totals = Counter()
for (r1, r2), c in role_bigrams.items():
    role_right_totals[r2] += c

base_rates = {r: role_right_totals.get(r, 0) / total_transitions for r in roles}

print(f"\nBase rates (marginal right):")
for r in roles:
    print(f"  {r}: {base_rates[r]*100:.1f}%")

# AX enrichment
print(f"\nAX transition enrichment (observed/expected):")
print(f"{'Transition':>12} {'Observed':>9} {'Expected':>9} {'Enrichment':>11}")
ax_total = role_totals.get('AX', 0)
for r in roles:
    obs = role_bigrams.get(('AX', r), 0) / ax_total if ax_total > 0 else 0
    exp = base_rates[r]
    enr = obs / exp if exp > 0 else 0
    print(f"{'AX->'+r:>12} {obs*100:8.1f}% {exp*100:8.1f}% {enr:10.2f}x")

# What precedes AX?
print(f"\nWhat precedes AX? (enrichment over baseline)")
print(f"{'Transition':>12} {'Observed':>9} {'Expected':>9} {'Enrichment':>11}")
for r in roles:
    r_total = role_totals.get(r, 0)
    obs = role_bigrams.get((r, 'AX'), 0) / r_total if r_total > 0 else 0
    exp = base_rates['AX']
    enr = obs / exp if exp > 0 else 0
    print(f"{r+'->AX':>12} {obs*100:8.1f}% {exp*100:8.1f}% {enr:10.2f}x")

# ============================================================
# 2. AX SUBGROUP TRANSITIONS
# ============================================================
print("\n" + "-" * 70)
print("2. AX SUBGROUP TRANSITIONS")
print("-" * 70)

sub_bigrams = Counter()
sub_totals = Counter()

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        s1 = line_tokens[i]['ax_sub']
        s2 = line_tokens[i+1]['ax_sub']
        sub_bigrams[(s1, s2)] += 1
        sub_totals[s1] += 1

sub_roles = ['CC', 'EN', 'FL', 'FQ', 'AX_INIT', 'AX_MED', 'AX_FINAL', 'UN']
print(f"\n{'':>10}", end='')
for r in sub_roles:
    print(f" {r:>9}", end='')
print()

for r1 in sub_roles:
    total = sub_totals.get(r1, 0)
    if total == 0:
        continue
    print(f"{r1:>10}", end='')
    for r2 in sub_roles:
        count = sub_bigrams.get((r1, r2), 0)
        pct = count / total * 100 if total > 0 else 0
        print(f" {pct:8.1f}%", end='')
    print(f"  (n={total})")

# ============================================================
# 3. AX-INTERNAL TRANSITIONS (class-level)
# ============================================================
print("\n" + "-" * 70)
print("3. AX SELF-CHAINING")
print("-" * 70)

ax_self_count = 0
ax_total_count = 0
ax_class_self = Counter()
ax_class_total = Counter()

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        if line_tokens[i]['role'] == 'AX':
            ax_total_count += 1
            ax_class_total[line_tokens[i]['class']] += 1
            if line_tokens[i+1]['role'] == 'AX':
                ax_self_count += 1
                ax_class_self[line_tokens[i]['class']] += 1

ax_self_rate = ax_self_count / ax_total_count if ax_total_count > 0 else 0
print(f"\nOverall AX->AX rate: {ax_self_rate:.1%} ({ax_self_count}/{ax_total_count})")
print(f"Expected if random: {base_rates['AX']:.1%}")
print(f"Enrichment: {ax_self_rate / base_rates['AX']:.2f}x" if base_rates['AX'] > 0 else "N/A")

print(f"\nPer-class AX self-chaining:")
print(f"{'Class':>5} {'Sub':>8} {'AX->AX':>7} {'Total':>6} {'Rate':>6}")
for cls in sorted(AX_CLASSES):
    total = ax_class_total.get(cls, 0)
    if total < 10:
        continue
    self_count = ax_class_self.get(cls, 0)
    rate = self_count / total if total > 0 else 0
    sub = get_ax_subgroup(cls)
    print(f"{cls:5d} {sub:>8} {self_count:7d} {total:6d} {rate:5.1%}")

# ============================================================
# 4. POSITIONAL FLOW: WHERE DOES AX FIT IN THE LINE?
# ============================================================
print("\n" + "-" * 70)
print("4. LINE-LEVEL ROLE SEQUENCE PATTERNS")
print("-" * 70)

# Extract role sequence per line
role_sequences = []
for (folio, line_id), line_tokens in lines.items():
    if len(line_tokens) < 3:
        continue
    seq = tuple(t['role'] for t in line_tokens)
    role_sequences.append(seq)

# Find common trigrams involving AX
trigrams = Counter()
for seq in role_sequences:
    for i in range(len(seq) - 2):
        tri = (seq[i], seq[i+1], seq[i+2])
        if 'AX' in tri:
            trigrams[tri] += 1

print(f"\nTop 20 trigrams involving AX:")
print(f"{'Trigram':>20} {'Count':>6} {'Description'}")
for tri, count in trigrams.most_common(20):
    desc = ''
    if tri == ('EN', 'AX', 'EN'):
        desc = 'AX mediates EN chain'
    elif tri == ('AX', 'EN', 'AX'):
        desc = 'EN mediates AX chain'
    elif tri[0] == 'AX' and tri[2] == 'AX':
        desc = f'AX sandwiches {tri[1]}'
    elif tri[1] == 'AX':
        desc = f'{tri[0]} -> AX -> {tri[2]}'
    print(f"{'->'.join(tri):>20} {count:6d} {desc}")

# ============================================================
# 5. AX SUBGROUP POSITIONAL FLOW
# ============================================================
print("\n" + "-" * 70)
print("5. SUBGROUP POSITIONAL FLOW")
print("-" * 70)

# For lines with AX tokens, what's the typical subgroup sequence?
ax_sequences = []
for (folio, line_id), line_tokens in lines.items():
    ax_in_line = [(i, t) for i, t in enumerate(line_tokens) if t['role'] == 'AX']
    if len(ax_in_line) >= 2:
        seq = tuple(get_ax_subgroup(t['class']) for _, t in ax_in_line)
        ax_sequences.append(seq)

# Count bigrams
ax_sub_bigrams = Counter()
for seq in ax_sequences:
    for i in range(len(seq) - 1):
        ax_sub_bigrams[(seq[i], seq[i+1])] += 1

print(f"\nAX subgroup bigrams (within lines with 2+ AX):")
print(f"{'Bigram':>25} {'Count':>6}")
for (s1, s2), count in sorted(ax_sub_bigrams.items(), key=lambda x: -x[1])[:15]:
    print(f"{s1+' -> '+s2:>25} {count:6d}")

# Check if INIT -> MED -> FINAL order holds
init_before_final = 0
final_before_init = 0
for seq in ax_sequences:
    positions = [(i, s) for i, s in enumerate(seq)]
    for i, s1 in positions:
        for j, s2 in positions:
            if j > i:
                if s1 == 'AX_INIT' and s2 == 'AX_FINAL':
                    init_before_final += 1
                elif s1 == 'AX_FINAL' and s2 == 'AX_INIT':
                    final_before_init += 1

total_pairs = init_before_final + final_before_init
if total_pairs > 0:
    print(f"\nINIT before FINAL: {init_before_final} ({init_before_final/total_pairs:.1%})")
    print(f"FINAL before INIT: {final_before_init} ({final_before_init/total_pairs:.1%})")
    print(f"(n={total_pairs} INIT-FINAL pairs in same line)")
else:
    print("\nNo INIT-FINAL co-occurrences found in same line")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
AX Transition Grammar:

1. AX self-chaining: {ax_self_rate:.1%} (enrichment: {ax_self_rate/base_rates['AX']:.2f}x vs base {base_rates['AX']:.1%})
2. Top trigram with AX: {'->'.join(trigrams.most_common(1)[0][0])} ({trigrams.most_common(1)[0][1]} occurrences)
3. AX subgroups: INIT={sorted(INIT_AX)}, FINAL={sorted(FINAL_AX)}, MED={sorted(MEDIAL_AX)}

Positional flow check:
- INIT before FINAL: {init_before_final}/{total_pairs} = {init_before_final/total_pairs:.1%} (expected if ordered)
""")

# Save results
results = {
    'role_transition_matrix': {
        f'{r1}->{r2}': role_bigrams.get((r1, r2), 0)
        for r1 in roles for r2 in roles
    },
    'ax_self_chain': {
        'rate': round(ax_self_rate, 4),
        'expected': round(base_rates['AX'], 4),
        'enrichment': round(ax_self_rate / base_rates['AX'], 2) if base_rates['AX'] > 0 else 0,
    },
    'top_ax_trigrams': [
        {'trigram': list(tri), 'count': count}
        for tri, count in trigrams.most_common(20)
    ],
    'subgroup_bigrams': [
        {'from': s1, 'to': s2, 'count': count}
        for (s1, s2), count in sorted(ax_sub_bigrams.items(), key=lambda x: -x[1])[:15]
    ],
    'positional_order': {
        'init_before_final': init_before_final,
        'final_before_init': final_before_init,
        'total_pairs': total_pairs,
        'init_first_rate': round(init_before_final/total_pairs, 4) if total_pairs > 0 else 0,
    },
    'subgroup_membership': {
        'INIT': sorted(INIT_AX),
        'FINAL': sorted(FINAL_AX),
        'MEDIAL': sorted(MEDIAL_AX),
    }
}

with open(RESULTS / 'ax_transitions.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to {RESULTS / 'ax_transitions.json'}")
