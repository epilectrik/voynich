"""
22_near_fl_morphology.py

Characterize the near-FL "narrowing" tokens morphologically.
What prefix/middle/suffix patterns distinguish the outer layer?
Are they a recognizable subset of the vocabulary?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency

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
MIN_N = 50

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Fit GMMs
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

gmm_models = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    if gmm.means_[0] > gmm.means_[1]:
        gmm_models[mid] = {'model': gmm, 'swap': True}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False}

# ============================================================
# Build layered gap tokens
# ============================================================
outer_left_tokens = []
outer_right_tokens = []
center_tokens = []
all_non_fl_tokens = []

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'

        role = token_to_role.get(t.word, 'UNKNOWN')
        prefix = m.prefix if m and m.prefix else 'NONE'
        middle = m.middle if m and m.middle else None
        suffix = m.suffix if m and m.suffix else 'NONE'

        entry = {'word': t.word, 'idx': idx, 'pos': pos, 'is_fl': is_fl,
                 'mode': mode, 'role': role, 'prefix': prefix,
                 'middle': middle, 'suffix': suffix}
        all_info.append(entry)
        if is_fl and mode:
            fl_info.append(entry)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl']
           and t['idx'] > max_low_idx and t['idx'] < min_high_idx]

    if len(gap) < 3:
        continue

    outer_left_tokens.append(gap[0])
    outer_right_tokens.append(gap[-1])
    for t in gap[1:-1]:
        center_tokens.append(t)

    for t in gap:
        all_non_fl_tokens.append(t)

print(f"Outer-left: {len(outer_left_tokens)}")
print(f"Outer-right: {len(outer_right_tokens)}")
print(f"Center: {len(center_tokens)}")
print(f"All non-FL gap: {len(all_non_fl_tokens)}")

# ============================================================
# TEST 1: Role distribution by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: ROLE DISTRIBUTION BY LAYER")
print(f"{'='*60}")

for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens),
                       ('All gap', all_non_fl_tokens)]:
    roles = Counter(t['role'] for t in tokens)
    total = len(tokens)
    print(f"\n  {label} (n={total}):")
    for role in ['ENERGY_OPERATOR', 'UNKNOWN', 'AUXILIARY', 'FREQUENT_OPERATOR',
                 'CORE_CONTROL', 'FLOW_OPERATOR']:
        count = roles.get(role, 0)
        if count > 0:
            print(f"    {role:>20}: {count:>5} ({count/total*100:.1f}%)")

# ============================================================
# TEST 2: PREFIX distribution by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: PREFIX DISTRIBUTION BY LAYER")
print(f"{'='*60}")

for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    prefixes = Counter(t['prefix'] for t in tokens)
    total = len(tokens)
    print(f"\n  {label} (n={total}):")
    for pfx, count in prefixes.most_common(12):
        print(f"    {pfx:>8}: {count:>5} ({count/total*100:.1f}%)")

# Chi-squared: layer x prefix
all_prefixes = sorted(set(t['prefix'] for t in all_non_fl_tokens))
top_prefixes = [p for p, _ in Counter(t['prefix'] for t in all_non_fl_tokens).most_common(10)]

layer_prefix_table = []
for tokens in [outer_left_tokens, outer_right_tokens, center_tokens]:
    pfx_counts = Counter(t['prefix'] for t in tokens)
    layer_prefix_table.append([pfx_counts.get(p, 0) for p in top_prefixes])

table = np.array(layer_prefix_table)
chi2, p_val, dof, _ = chi2_contingency(table)
v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
print(f"\n  Layer x Prefix chi2={chi2:.1f}, p={p_val:.2e}, Cramer's V={v:.3f}")

# ============================================================
# TEST 3: MIDDLE distribution by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: MIDDLE DISTRIBUTION BY LAYER")
print(f"{'='*60}")

for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    middles = Counter(t['middle'] for t in tokens if t['middle'])
    total = sum(middles.values())
    print(f"\n  {label} (n={total}):")
    for mid, count in middles.most_common(12):
        print(f"    {mid:>8}: {count:>5} ({count/total*100:.1f}%)")

# ============================================================
# TEST 4: SUFFIX distribution by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: SUFFIX DISTRIBUTION BY LAYER")
print(f"{'='*60}")

for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    suffixes = Counter(t['suffix'] for t in tokens)
    total = len(tokens)
    print(f"\n  {label} (n={total}):")
    for sfx, count in suffixes.most_common(8):
        print(f"    {sfx:>8}: {count:>5} ({count/total*100:.1f}%)")

# ============================================================
# TEST 5: Token length by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: TOKEN LENGTH (characters) BY LAYER")
print(f"{'='*60}")

for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    lengths = [len(t['word']) for t in tokens]
    print(f"  {label:>12}: mean={np.mean(lengths):.1f}, median={np.median(lengths):.0f}")

# ============================================================
# TEST 6: Morphological complexity by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: MORPHOLOGICAL COMPLEXITY BY LAYER")
print(f"{'='*60}")

def morph_complexity(token):
    """Count non-empty morphological slots."""
    slots = 0
    if token['prefix'] != 'NONE':
        slots += 1
    if token['middle']:
        slots += 1
    if token['suffix'] != 'NONE':
        slots += 1
    return slots

for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    complexities = [morph_complexity(t) for t in tokens]
    print(f"  {label:>12}: mean={np.mean(complexities):.2f}, "
          f"1-slot={sum(1 for c in complexities if c==1)/len(complexities)*100:.1f}%, "
          f"2-slot={sum(1 for c in complexities if c==2)/len(complexities)*100:.1f}%, "
          f"3-slot={sum(1 for c in complexities if c==3)/len(complexities)*100:.1f}%")

# ============================================================
# TEST 7: Unique tokens per layer (type/token ratio)
# ============================================================
print(f"\n{'='*60}")
print("TEST 7: VOCABULARY CONCENTRATION")
print(f"{'='*60}")

for label, tokens in [('Outer-left', outer_left_tokens),
                       ('Outer-right', outer_right_tokens),
                       ('Center', center_tokens)]:
    words = [t['word'] for t in tokens]
    types = len(set(words))
    total = len(words)
    ttr = types / total
    top_word = Counter(words).most_common(1)[0]
    top5_coverage = sum(c for _, c in Counter(words).most_common(5)) / total
    print(f"  {label:>12}: types={types}, tokens={total}, TTR={ttr:.3f}, "
          f"top5_coverage={top5_coverage:.1%}, top1={top_word[0]}({top_word[1]})")

# ============================================================
# Summary
# ============================================================
print(f"\n{'='*60}")
print("SUMMARY: WHAT MAKES OUTER TOKENS DIFFERENT?")
print(f"{'='*60}")

# Compare outer-left to center on key dimensions
ol_en = sum(1 for t in outer_left_tokens if t['role'] == 'ENERGY_OPERATOR') / len(outer_left_tokens)
c_en = sum(1 for t in center_tokens if t['role'] == 'ENERGY_OPERATOR') / len(center_tokens)
ol_unk = sum(1 for t in outer_left_tokens if t['role'] == 'UNKNOWN') / len(outer_left_tokens)
c_unk = sum(1 for t in center_tokens if t['role'] == 'UNKNOWN') / len(center_tokens)
ol_aux = sum(1 for t in outer_left_tokens if t['role'] == 'AUXILIARY') / len(outer_left_tokens)
c_aux = sum(1 for t in center_tokens if t['role'] == 'AUXILIARY') / len(center_tokens)

print(f"  ENERGY_OPERATOR: outer-left={ol_en:.1%}, center={c_en:.1%}")
print(f"  UNKNOWN:         outer-left={ol_unk:.1%}, center={c_unk:.1%}")
print(f"  AUXILIARY:        outer-left={ol_aux:.1%}, center={c_aux:.1%}")

ol_sh = sum(1 for t in outer_left_tokens if t['prefix'] == 'sh') / len(outer_left_tokens)
c_sh = sum(1 for t in center_tokens if t['prefix'] == 'sh') / len(center_tokens)
ol_qo = sum(1 for t in outer_left_tokens if t['prefix'] == 'qo') / len(outer_left_tokens)
c_qo = sum(1 for t in center_tokens if t['prefix'] == 'qo') / len(center_tokens)
ol_ch = sum(1 for t in outer_left_tokens if t['prefix'] == 'ch') / len(outer_left_tokens)
c_ch = sum(1 for t in center_tokens if t['prefix'] == 'ch') / len(center_tokens)

print(f"\n  PREFIX sh: outer-left={ol_sh:.1%}, center={c_sh:.1%}")
print(f"  PREFIX qo: outer-left={ol_qo:.1%}, center={c_qo:.1%}")
print(f"  PREFIX ch: outer-left={ol_ch:.1%}, center={c_ch:.1%}")

# Save
result = {
    'n_outer_left': len(outer_left_tokens),
    'n_outer_right': len(outer_right_tokens),
    'n_center': len(center_tokens),
    'layer_prefix_cramers_v': round(float(v), 3),
}

out_path = Path(__file__).resolve().parent.parent / "results" / "22_near_fl_morphology.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
