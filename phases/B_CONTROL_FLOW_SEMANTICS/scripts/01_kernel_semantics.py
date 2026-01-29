"""
01_kernel_semantics.py

Analyze what k, h, e actually encode by examining their contexts.
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

# FL stage map from semantic model
FL_STAGE_MAP = {
    'ii': 'INITIAL', 'i': 'INITIAL',
    'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL', 'al': 'MEDIAL', 'l': 'MEDIAL', 'ol': 'MEDIAL',
    'o': 'LATE', 'ly': 'LATE',
    'am': 'TERMINAL', 'm': 'TERMINAL', 'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL'
}

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("Kernel Semantics Analysis")
print("=" * 70)

# Build token sequences by line
line_sequences = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_sequences[key].append(t)

# Analyze kernel contexts
kernel_contexts = {
    'k': {'before': Counter(), 'after': Counter(), 'positions': [], 'roles_before': Counter(), 'roles_after': Counter()},
    'h': {'before': Counter(), 'after': Counter(), 'positions': [], 'roles_before': Counter(), 'roles_after': Counter()},
    'e': {'before': Counter(), 'after': Counter(), 'positions': [], 'roles_before': Counter(), 'roles_after': Counter()},
}

# Track kernel combinations
kernel_combos = Counter()

for key, tokens in line_sequences.items():
    for i, t in enumerate(tokens):
        # Check which kernels this token has
        has_k = 'k' in t.word
        has_h = 'h' in t.word
        has_e = 'e' in t.word

        # Track combinations
        combo = ''
        if has_k: combo += 'k'
        if has_h: combo += 'h'
        if has_e: combo += 'e'
        if combo:
            kernel_combos[combo] += 1

        # Analyze each kernel's context
        for kernel, has_it in [('k', has_k), ('h', has_h), ('e', has_e)]:
            if not has_it:
                continue

            # Position in line
            pos = i / len(tokens) if len(tokens) > 1 else 0.5
            kernel_contexts[kernel]['positions'].append(pos)

            # What comes before?
            if i > 0:
                prev = tokens[i-1]
                prev_m = morph.extract(prev.word)
                if prev_m and prev_m.middle:
                    kernel_contexts[kernel]['before'][prev_m.middle] += 1
                prev_role = token_to_role.get(prev.word, 'UN')
                kernel_contexts[kernel]['roles_before'][prev_role] += 1

            # What comes after?
            if i < len(tokens) - 1:
                next_t = tokens[i+1]
                next_m = morph.extract(next_t.word)
                if next_m and next_m.middle:
                    kernel_contexts[kernel]['after'][next_m.middle] += 1
                next_role = token_to_role.get(next_t.word, 'UN')
                kernel_contexts[kernel]['roles_after'][next_role] += 1

# Report kernel profiles
print("\n" + "=" * 70)
print("Kernel Positional Profiles")
print("=" * 70)

for kernel in ['k', 'h', 'e']:
    ctx = kernel_contexts[kernel]
    positions = ctx['positions']
    if not positions:
        continue
    mean_pos = sum(positions) / len(positions)

    # Position distribution
    early = sum(1 for p in positions if p < 0.33) / len(positions) * 100
    mid = sum(1 for p in positions if 0.33 <= p < 0.66) / len(positions) * 100
    late = sum(1 for p in positions if p >= 0.66) / len(positions) * 100

    print(f"\n'{kernel}' kernel:")
    print(f"  Occurrences: {len(positions):,}")
    print(f"  Mean position: {mean_pos:.3f}")
    print(f"  Distribution: EARLY {early:.1f}% | MID {mid:.1f}% | LATE {late:.1f}%")

print("\n" + "=" * 70)
print("Kernel Role Transitions")
print("=" * 70)

for kernel in ['k', 'h', 'e']:
    ctx = kernel_contexts[kernel]
    print(f"\n'{kernel}' kernel:")

    print("  BEFORE (what precedes tokens with this kernel):")
    for role, count in ctx['roles_before'].most_common(5):
        pct = count / sum(ctx['roles_before'].values()) * 100
        print(f"    {role:20} {count:5} ({pct:5.1f}%)")

    print("  AFTER (what follows tokens with this kernel):")
    for role, count in ctx['roles_after'].most_common(5):
        pct = count / sum(ctx['roles_after'].values()) * 100
        print(f"    {role:20} {count:5} ({pct:5.1f}%)")

print("\n" + "=" * 70)
print("Kernel MIDDLE Contexts")
print("=" * 70)

for kernel in ['k', 'h', 'e']:
    ctx = kernel_contexts[kernel]
    print(f"\n'{kernel}' kernel:")

    # Check for FL stages before/after
    fl_before = Counter()
    fl_after = Counter()
    for mid, count in ctx['before'].items():
        if mid in FL_STAGE_MAP:
            fl_before[FL_STAGE_MAP[mid]] += count
    for mid, count in ctx['after'].items():
        if mid in FL_STAGE_MAP:
            fl_after[FL_STAGE_MAP[mid]] += count

    if fl_before:
        print(f"  FL stages BEFORE: {dict(fl_before.most_common())}")
    if fl_after:
        print(f"  FL stages AFTER: {dict(fl_after.most_common())}")

    print(f"  Top MIDDLEs before: {', '.join(f'{m}({c})' for m, c in ctx['before'].most_common(5))}")
    print(f"  Top MIDDLEs after: {', '.join(f'{m}({c})' for m, c in ctx['after'].most_common(5))}")

print("\n" + "=" * 70)
print("Kernel Combinations")
print("=" * 70)

total_kernel = sum(kernel_combos.values())
print(f"\nTotal tokens with any kernel: {total_kernel:,}")
for combo, count in kernel_combos.most_common():
    pct = count / total_kernel * 100
    print(f"  {combo:5} {count:6,} ({pct:5.1f}%)")

# Semantic interpretations
print("\n" + "=" * 70)
print("Semantic Interpretation")
print("=" * 70)

# Calculate key metrics for interpretation
k_ctx = kernel_contexts['k']
h_ctx = kernel_contexts['h']
e_ctx = kernel_contexts['e']

k_mean_pos = sum(k_ctx['positions']) / len(k_ctx['positions']) if k_ctx['positions'] else 0
h_mean_pos = sum(h_ctx['positions']) / len(h_ctx['positions']) if h_ctx['positions'] else 0
e_mean_pos = sum(e_ctx['positions']) / len(e_ctx['positions']) if e_ctx['positions'] else 0

print(f"""
Positional ordering: {'k' if k_mean_pos < h_mean_pos else 'h'} < {'h' if h_mean_pos < e_mean_pos else 'e'} < {'e' if e_mean_pos > h_mean_pos else 'h'}
  k: {k_mean_pos:.3f}
  h: {h_mean_pos:.3f}
  e: {e_mean_pos:.3f}

PROPOSED SEMANTICS:

'k' (mean pos {k_mean_pos:.3f}):
  - Most common kernel ({len(k_ctx['positions']):,} occurrences)
  - Earlier in lines
  - INTERPRETATION: Energy/activation - initiates transitions

'h' (mean pos {h_mean_pos:.3f}):
  - Second kernel ({len(h_ctx['positions']):,} occurrences)
  - Middle position
  - INTERPRETATION: Phase/harmony - aligns or coordinates

'e' (mean pos {e_mean_pos:.3f}):
  - Third kernel ({len(e_ctx['positions']):,} occurrences)
  - Later in lines
  - INTERPRETATION: Equilibrium/stability - verifies completion

Combined pattern: k-activate -> h-align -> e-verify
""")

# Save results
results = {
    'kernel_profiles': {},
    'combinations': dict(kernel_combos.most_common()),
    'semantic_assignments': {
        'k': {'function': 'activation', 'mean_position': round(k_mean_pos, 4), 'count': len(k_ctx['positions'])},
        'h': {'function': 'alignment', 'mean_position': round(h_mean_pos, 4), 'count': len(h_ctx['positions'])},
        'e': {'function': 'verification', 'mean_position': round(e_mean_pos, 4), 'count': len(e_ctx['positions'])}
    }
}

for kernel in ['k', 'h', 'e']:
    ctx = kernel_contexts[kernel]
    results['kernel_profiles'][kernel] = {
        'count': len(ctx['positions']),
        'mean_position': round(sum(ctx['positions']) / len(ctx['positions']), 4) if ctx['positions'] else 0,
        'roles_before': dict(ctx['roles_before'].most_common(5)),
        'roles_after': dict(ctx['roles_after'].most_common(5)),
        'top_middles_before': ctx['before'].most_common(10),
        'top_middles_after': ctx['after'].most_common(10)
    }

results_dir = Path(__file__).parent.parent / "results"
output_path = results_dir / "kernel_semantics.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")
