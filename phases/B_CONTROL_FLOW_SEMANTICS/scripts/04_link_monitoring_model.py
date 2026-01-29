"""
04_link_monitoring_model.py

Analyze what LINK is monitoring. LINK = class 29, part of AUXILIARY role.
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

# LINK is class 29
LINK_CLASS = 29

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("LINK Monitoring Model Analysis")
print("=" * 70)

# Identify LINK tokens
link_tokens = set()
for word, cls in token_to_class.items():
    if cls == LINK_CLASS:
        link_tokens.add(word)

print(f"\nLINK tokens (class 29): {len(link_tokens)} types")
print(f"Examples: {list(link_tokens)[:10]}")

# Build token sequences by line
line_sequences = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_sequences[key].append(t)

# Analyze LINK contexts
link_contexts = {
    'positions': [],
    'roles_before': Counter(),
    'roles_after': Counter(),
    'middles_before': Counter(),
    'middles_after': Counter(),
    'kernel_before': {'k': 0, 'h': 0, 'e': 0, 'none': 0},
    'kernel_after': {'k': 0, 'h': 0, 'e': 0, 'none': 0},
    'line_initial': 0,
    'line_final': 0,
    'total': 0
}

# FL stage map
FL_STAGE_MAP = {
    'ii': 'INITIAL', 'i': 'INITIAL', 'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL', 'al': 'MEDIAL', 'l': 'MEDIAL', 'ol': 'MEDIAL',
    'o': 'LATE', 'ly': 'LATE',
    'am': 'TERMINAL', 'm': 'TERMINAL', 'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL'
}

fl_stages_before = Counter()
fl_stages_after = Counter()

for key, tokens in line_sequences.items():
    for i, t in enumerate(tokens):
        cls = token_to_class.get(t.word, -1)
        if cls != LINK_CLASS:
            continue

        link_contexts['total'] += 1

        # Position
        pos = i / len(tokens) if len(tokens) > 1 else 0.5
        link_contexts['positions'].append(pos)

        # Line position
        if i == 0:
            link_contexts['line_initial'] += 1
        if i == len(tokens) - 1:
            link_contexts['line_final'] += 1

        # Before context
        if i > 0:
            prev = tokens[i-1]
            prev_role = token_to_role.get(prev.word, 'UN')
            link_contexts['roles_before'][prev_role] += 1

            prev_m = morph.extract(prev.word)
            if prev_m and prev_m.middle:
                link_contexts['middles_before'][prev_m.middle] += 1
                if prev_m.middle in FL_STAGE_MAP:
                    fl_stages_before[FL_STAGE_MAP[prev_m.middle]] += 1

            # Kernel
            if 'k' in prev.word:
                link_contexts['kernel_before']['k'] += 1
            if 'h' in prev.word:
                link_contexts['kernel_before']['h'] += 1
            if 'e' in prev.word:
                link_contexts['kernel_before']['e'] += 1
            if not any(c in prev.word for c in 'khe'):
                link_contexts['kernel_before']['none'] += 1

        # After context
        if i < len(tokens) - 1:
            next_t = tokens[i+1]
            next_role = token_to_role.get(next_t.word, 'UN')
            link_contexts['roles_after'][next_role] += 1

            next_m = morph.extract(next_t.word)
            if next_m and next_m.middle:
                link_contexts['middles_after'][next_m.middle] += 1
                if next_m.middle in FL_STAGE_MAP:
                    fl_stages_after[FL_STAGE_MAP[next_m.middle]] += 1

            # Kernel
            if 'k' in next_t.word:
                link_contexts['kernel_after']['k'] += 1
            if 'h' in next_t.word:
                link_contexts['kernel_after']['h'] += 1
            if 'e' in next_t.word:
                link_contexts['kernel_after']['e'] += 1
            if not any(c in next_t.word for c in 'khe'):
                link_contexts['kernel_after']['none'] += 1

# Report
print("\n" + "=" * 70)
print("LINK Positional Profile")
print("=" * 70)

positions = link_contexts['positions']
mean_pos = sum(positions) / len(positions) if positions else 0
pos_early = sum(1 for p in positions if p < 0.33) / len(positions) * 100
pos_mid = sum(1 for p in positions if 0.33 <= p < 0.66) / len(positions) * 100
pos_late = sum(1 for p in positions if p >= 0.66) / len(positions) * 100

print(f"\nTotal LINK tokens: {link_contexts['total']:,}")
print(f"Mean position: {mean_pos:.3f}")
print(f"Distribution: EARLY {pos_early:.1f}% | MID {pos_mid:.1f}% | LATE {pos_late:.1f}%")
print(f"Line-initial: {link_contexts['line_initial']} ({link_contexts['line_initial']/link_contexts['total']*100:.1f}%)")
print(f"Line-final: {link_contexts['line_final']} ({link_contexts['line_final']/link_contexts['total']*100:.1f}%)")

print("\n" + "=" * 70)
print("LINK Role Transitions")
print("=" * 70)

print("\nWhat precedes LINK:")
total_before = sum(link_contexts['roles_before'].values())
for role, count in link_contexts['roles_before'].most_common():
    pct = count / total_before * 100 if total_before > 0 else 0
    print(f"  {role:20} {count:5} ({pct:5.1f}%)")

print("\nWhat follows LINK:")
total_after = sum(link_contexts['roles_after'].values())
for role, count in link_contexts['roles_after'].most_common():
    pct = count / total_after * 100 if total_after > 0 else 0
    print(f"  {role:20} {count:5} ({pct:5.1f}%)")

print("\n" + "=" * 70)
print("LINK-Kernel Relationship")
print("=" * 70)

print("\nKernel BEFORE LINK:")
kb = link_contexts['kernel_before']
total_kb = kb['k'] + kb['h'] + kb['e'] + kb['none']
for k, count in kb.items():
    pct = count / total_kb * 100 if total_kb > 0 else 0
    print(f"  {k:6} {count:5} ({pct:5.1f}%)")

print("\nKernel AFTER LINK:")
ka = link_contexts['kernel_after']
total_ka = ka['k'] + ka['h'] + ka['e'] + ka['none']
for k, count in ka.items():
    pct = count / total_ka * 100 if total_ka > 0 else 0
    print(f"  {k:6} {count:5} ({pct:5.1f}%)")

print("\n" + "=" * 70)
print("LINK-FL Stage Relationship")
print("=" * 70)

print("\nFL stages BEFORE LINK:")
for stage, count in fl_stages_before.most_common():
    print(f"  {stage:12} {count:4}")

print("\nFL stages AFTER LINK:")
for stage, count in fl_stages_after.most_common():
    print(f"  {stage:12} {count:4}")

print("\n" + "=" * 70)
print("Top MIDDLE Contexts")
print("=" * 70)

print("\nTop MIDDLEs BEFORE LINK:")
for mid, count in link_contexts['middles_before'].most_common(10):
    stage = FL_STAGE_MAP.get(mid, '-')
    print(f"  {mid:10} {count:4}  (FL: {stage})")

print("\nTop MIDDLEs AFTER LINK:")
for mid, count in link_contexts['middles_after'].most_common(10):
    stage = FL_STAGE_MAP.get(mid, '-')
    print(f"  {mid:10} {count:4}  (FL: {stage})")

# Semantic interpretation
print("\n" + "=" * 70)
print("LINK Monitoring Model")
print("=" * 70)

# Check LINK→Kernel vs LINK→FL
link_to_kernel = link_contexts['roles_after'].get('ENERGY_OPERATOR', 0)
link_to_fl = link_contexts['roles_after'].get('FLOW_OPERATOR', 0)
link_to_fq = link_contexts['roles_after'].get('FREQUENT_OPERATOR', 0)

print(f"""
LINK FUNCTION ANALYSIS:

1. POSITION:
   - Mean position: {mean_pos:.3f} (relatively early)
   - {pos_early:.1f}% in first third of line

2. WHAT LINK ROUTES TO:
   - ENERGY_OPERATOR: {link_to_kernel/total_after*100:.1f}%
   - FLOW_OPERATOR: {link_to_fl/total_after*100:.1f}%
   - FREQUENT_OPERATOR (escape): {link_to_fq/total_after*100:.1f}%

3. KERNEL SEPARATION:
   - Kernel before LINK: {(total_kb-kb['none'])/total_kb*100:.1f}%
   - Kernel after LINK: {(total_ka-ka['none'])/total_ka*100:.1f}%
   - No kernel after: {ka['none']/total_ka*100:.1f}%

PROPOSED LINK SEMANTICS:

LINK = "checkpoint/verify" operator
  - Appears early in processing
  - Routes primarily to ENERGY_OPERATOR (kernel processing)
  - Separated from direct kernel involvement
  - Function: Monitor state, then route to appropriate handler
""")

# Save results
results = {
    'link_tokens': list(link_tokens)[:50],
    'total': link_contexts['total'],
    'position': {
        'mean': round(float(mean_pos), 4),
        'early_pct': round(float(pos_early), 2),
        'mid_pct': round(float(pos_mid), 2),
        'late_pct': round(float(pos_late), 2)
    },
    'roles_before': dict(link_contexts['roles_before'].most_common()),
    'roles_after': dict(link_contexts['roles_after'].most_common()),
    'kernel_before': link_contexts['kernel_before'],
    'kernel_after': link_contexts['kernel_after'],
    'fl_stages_before': dict(fl_stages_before.most_common()),
    'fl_stages_after': dict(fl_stages_after.most_common()),
    'proposed_function': 'checkpoint_verify_operator'
}

results_dir = Path(__file__).parent.parent / "results"
output_path = results_dir / "link_monitoring_model.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")
