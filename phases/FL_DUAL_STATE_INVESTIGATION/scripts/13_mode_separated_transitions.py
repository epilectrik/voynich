"""
13_mode_separated_transitions.py

Assign each FL token to Mode-LOW or Mode-HIGH based on GMM posterior,
then analyze transitions within each mode separately.

Key questions:
1. Do within-mode transitions show stronger forward bias than the mixed 1.3:1?
2. Are there specific bigrams that dominate within each mode?
3. How often do tokens cross modes within a line?
4. Do the two modes form two coherent progressions?
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from sklearn.mixture import GaussianMixture

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}
STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}

tx = Transcript()
morph = Morphology()

# ============================================================
# Step 1: Fit per-MIDDLE GMMs and assign mode labels
# ============================================================
MIN_N = 50

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL records
fl_records = []
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            fl_records.append({
                'word': t.word,
                'middle': m.middle,
                'stage': FL_STAGE_MAP[m.middle][0],
                'actual_pos': idx / (n - 1),
                'line_key': line_key,
                'idx': idx,
                'section': t.section,
            })

# Fit 2-component GMM per MIDDLE and assign mode labels
gmm_models = {}
per_middle_positions = defaultdict(list)
for r in fl_records:
    per_middle_positions[r['middle']].append(r['actual_pos'])

for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    # Ensure component 0 = LOW, component 1 = HIGH
    if gmm.means_[0] > gmm.means_[1]:
        # Swap labels
        gmm_models[mid] = {'model': gmm, 'swap': True,
                           'low_mean': float(gmm.means_[1][0]),
                           'high_mean': float(gmm.means_[0][0])}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False,
                           'low_mean': float(gmm.means_[0][0]),
                           'high_mean': float(gmm.means_[1][0])}

# Assign mode to each FL token
for r in fl_records:
    mid = r['middle']
    if mid in gmm_models:
        model_info = gmm_models[mid]
        gmm = model_info['model']
        pred = gmm.predict(np.array([[r['actual_pos']]]))[0]
        if model_info['swap']:
            pred = 1 - pred
        r['mode'] = 'LOW' if pred == 0 else 'HIGH'
        r['mode_confidence'] = float(np.max(
            gmm.predict_proba(np.array([[r['actual_pos']]]))[0]))
    else:
        r['mode'] = 'UNKNOWN'
        r['mode_confidence'] = 0.0

# Filter to assigned tokens
assigned = [r for r in fl_records if r['mode'] != 'UNKNOWN']
print(f"Total FL tokens: {len(fl_records)}")
print(f"Mode-assigned (MIDDLE n >= {MIN_N}): {len(assigned)}")

low_count = sum(1 for r in assigned if r['mode'] == 'LOW')
high_count = sum(1 for r in assigned if r['mode'] == 'HIGH')
print(f"  LOW:  {low_count} ({low_count/len(assigned)*100:.1f}%)")
print(f"  HIGH: {high_count} ({high_count/len(assigned)*100:.1f}%)")

# Mode assignment per MIDDLE
print(f"\n{'MIDDLE':>6} {'Stage':>10} {'LOW':>5} {'HIGH':>5} {'low_mean':>8} {'high_mean':>9}")
print("-" * 55)
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    if mid not in gmm_models:
        continue
    low_n = sum(1 for r in assigned if r['middle'] == mid and r['mode'] == 'LOW')
    high_n = sum(1 for r in assigned if r['middle'] == mid and r['mode'] == 'HIGH')
    info = gmm_models[mid]
    print(f"{mid:>6} {FL_STAGE_MAP[mid][0]:>10} {low_n:>5} {high_n:>5} "
          f"{info['low_mean']:>8.3f} {info['high_mean']:>9.3f}")

# ============================================================
# Step 2: Within-mode transitions
# ============================================================
print(f"\n{'='*60}")
print("WITHIN-MODE TRANSITION ANALYSIS")

# Group by line
fl_by_line = defaultdict(list)
for r in assigned:
    fl_by_line[r['line_key']].append(r)

# Classify each adjacent pair
transition_types = Counter()
mode_transitions = {'LOW': Counter(), 'HIGH': Counter(), 'CROSS': Counter()}
mode_direction = {'LOW': Counter(), 'HIGH': Counter(), 'CROSS': Counter()}
bigrams_by_mode = {'LOW': Counter(), 'HIGH': Counter(), 'CROSS': Counter()}

for line_key, fts in fl_by_line.items():
    if len(fts) < 2:
        continue
    fts_sorted = sorted(fts, key=lambda x: x['idx'])
    for i in range(len(fts_sorted) - 1):
        a = fts_sorted[i]
        b = fts_sorted[i + 1]

        # Mode transition type
        if a['mode'] == b['mode'] == 'LOW':
            mode_type = 'LOW'
        elif a['mode'] == b['mode'] == 'HIGH':
            mode_type = 'HIGH'
        else:
            mode_type = 'CROSS'

        transition_types[mode_type] += 1

        # Direction
        ord_a = STAGE_ORDER[a['stage']]
        ord_b = STAGE_ORDER[b['stage']]
        if ord_b > ord_a:
            direction = 'forward'
        elif ord_b < ord_a:
            direction = 'backward'
        else:
            direction = 'same'

        mode_direction[mode_type][direction] += 1
        bigrams_by_mode[mode_type][f"{a['middle']}->{b['middle']}"] += 1

total_trans = sum(transition_types.values())
print(f"\nTransition type breakdown:")
for mt in ['LOW', 'HIGH', 'CROSS']:
    n = transition_types[mt]
    pct = n / total_trans * 100 if total_trans > 0 else 0
    print(f"  {mt:>5}: {n:>5} ({pct:.1f}%)")

print(f"\nForward bias by mode:")
for mt in ['LOW', 'HIGH', 'CROSS']:
    dirs = mode_direction[mt]
    fwd = dirs['forward']
    bwd = dirs['backward']
    same = dirs['same']
    total = fwd + bwd + same
    ratio = fwd / bwd if bwd > 0 else float('inf')
    ratio_str = f"{ratio:.1f}" if ratio != float('inf') else "inf"
    print(f"  {mt:>5}: fwd={fwd:>4} bwd={bwd:>4} same={same:>4} "
          f"ratio={ratio_str}:1  (n={total})")

# ============================================================
# Step 3: Top bigrams per mode
# ============================================================
print(f"\n{'='*60}")
print("TOP BIGRAMS PER MODE")
for mt in ['LOW', 'HIGH', 'CROSS']:
    print(f"\n  {mt} mode top 10:")
    for bigram, count in bigrams_by_mode[mt].most_common(10):
        parts = bigram.split('->')
        s_a = FL_STAGE_MAP[parts[0]][0] if parts[0] in FL_STAGE_MAP else '?'
        s_b = FL_STAGE_MAP[parts[1]][0] if parts[1] in FL_STAGE_MAP else '?'
        ord_a = STAGE_ORDER.get(s_a, -1)
        ord_b = STAGE_ORDER.get(s_b, -1)
        dir_str = "FWD" if ord_b > ord_a else "BWD" if ord_b < ord_a else "SAME"
        print(f"    {bigram:>12}: {count:>4} [{dir_str}] ({s_a}->{s_b})")

# ============================================================
# Step 4: Within-mode mean positions (does gradient hold?)
# ============================================================
print(f"\n{'='*60}")
print("WITHIN-MODE MEAN POSITIONS")

for mode in ['LOW', 'HIGH']:
    print(f"\n  {mode} mode gradient:")
    mode_tokens = [r for r in assigned if r['mode'] == mode]
    mid_positions = defaultdict(list)
    for r in mode_tokens:
        mid_positions[r['middle']].append(r['actual_pos'])

    means = {}
    for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
        if mid in mid_positions and len(mid_positions[mid]) >= 5:
            avg = np.mean(mid_positions[mid])
            means[mid] = float(avg)
            print(f"    {mid:>4} ({FL_STAGE_MAP[mid][0]:>10}): "
                  f"mean={avg:.3f} n={len(mid_positions[mid])}")

    # Test gradient within mode
    if len(means) >= 5:
        from scipy.stats import spearmanr
        expected = [FL_STAGE_MAP[m][1] for m in means]
        actual = [means[m] for m in means]
        rho, p = spearmanr(expected, actual)
        print(f"    Gradient: rho={rho:.3f}, p={p:.4f}")

# ============================================================
# Step 5: Cross-mode transitions — what triggers mode switching?
# ============================================================
print(f"\n{'='*60}")
print("CROSS-MODE TRANSITIONS")

cross_details = Counter()
for line_key, fts in fl_by_line.items():
    if len(fts) < 2:
        continue
    fts_sorted = sorted(fts, key=lambda x: x['idx'])
    for i in range(len(fts_sorted) - 1):
        a = fts_sorted[i]
        b = fts_sorted[i + 1]
        if a['mode'] != b['mode']:
            cross_details[f"{a['mode']}->{b['mode']}"] += 1

for cross_type, count in cross_details.most_common():
    print(f"  {cross_type}: {count}")

# ============================================================
# Step 6: Line-level mode coherence
# ============================================================
print(f"\n{'='*60}")
print("LINE-LEVEL MODE COHERENCE")

pure_low = 0
pure_high = 0
mixed = 0
for line_key, fts in fl_by_line.items():
    if len(fts) < 2:
        continue
    modes = set(r['mode'] for r in fts)
    if modes == {'LOW'}:
        pure_low += 1
    elif modes == {'HIGH'}:
        pure_high += 1
    else:
        mixed += 1

total_lines = pure_low + pure_high + mixed
print(f"  Pure LOW lines:  {pure_low:>4} ({pure_low/total_lines*100:.1f}%)")
print(f"  Pure HIGH lines: {pure_high:>4} ({pure_high/total_lines*100:.1f}%)")
print(f"  Mixed lines:     {mixed:>4} ({mixed/total_lines*100:.1f}%)")

# ============================================================
# Verdict
# ============================================================
low_fwd = mode_direction['LOW']['forward']
low_bwd = mode_direction['LOW']['backward']
high_fwd = mode_direction['HIGH']['forward']
high_bwd = mode_direction['HIGH']['backward']

low_ratio = low_fwd / low_bwd if low_bwd > 0 else float('inf')
high_ratio = high_fwd / high_bwd if high_bwd > 0 else float('inf')
cross_pct = transition_types['CROSS'] / total_trans if total_trans > 0 else 0
mixed_pct = mixed / total_lines if total_lines > 0 else 0

if low_ratio > 3.0 and high_ratio > 3.0 and cross_pct < 0.30:
    verdict = "TWO_DISCRETE_PROGRESSIONS"
    explanation = (f"Both modes show strong forward bias (LOW={low_ratio:.1f}:1, "
                   f"HIGH={high_ratio:.1f}:1) with limited cross-mode transitions "
                   f"({cross_pct:.0%}). Two coherent, separable progressions.")
elif (low_ratio > 2.0 or high_ratio > 2.0) and cross_pct < 0.50:
    verdict = "PARTIALLY_COHERENT"
    explanation = (f"Some forward bias within modes (LOW={low_ratio:.1f}:1, "
                   f"HIGH={high_ratio:.1f}:1), cross-mode={cross_pct:.0%}. "
                   f"Modes are partially coherent but frequently interleaved.")
else:
    verdict = "AMBIGUOUS"
    explanation = (f"Weak within-mode bias (LOW={low_ratio:.1f}:1, "
                   f"HIGH={high_ratio:.1f}:1), cross-mode={cross_pct:.0%}. "
                   f"Modes do not form discrete progressions.")

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# Prepare serializable result
def safe_val(v):
    if v == float('inf'):
        return 'inf'
    return round(float(v), 4) if isinstance(v, float) else v

result = {
    'total_assigned': len(assigned),
    'low_count': low_count,
    'high_count': high_count,
    'transition_types': dict(transition_types),
    'mode_direction': {k: dict(v) for k, v in mode_direction.items()},
    'forward_bias': {
        'LOW': safe_val(low_ratio),
        'HIGH': safe_val(high_ratio),
    },
    'cross_mode_pct': round(cross_pct, 4),
    'line_coherence': {
        'pure_low': pure_low,
        'pure_high': pure_high,
        'mixed': mixed,
        'mixed_pct': round(mixed_pct, 4),
    },
    'top_bigrams': {
        mode: bigrams_by_mode[mode].most_common(15)
        for mode in ['LOW', 'HIGH', 'CROSS']
    },
    'cross_transitions': dict(cross_details),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "13_mode_separated_transitions.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
