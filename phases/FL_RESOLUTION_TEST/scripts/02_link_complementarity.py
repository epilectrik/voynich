"""
FL RESOLUTION TEST 2: FL-LINK Complementarity Along Lines (SECONDARY)

Hypothesis H2: FL and LINK occupy distinct, non-overlapping phases of
the control loop (monitor -> assess -> act -> confirm).

Method:
- For each line, compute distance-to-nearest-LINK for FL tokens
- Compare to distance-to-nearest-LINK for matched random operational tokens
- KS test + shuffle control (shuffle FL locations within same prefix family)

Decision:
- PASS: FL tokens significantly avoid LINK-proximate zones
- FAIL: No spatial separation
"""
import sys, json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.stats import ks_2samp, mannwhitneyu

sys.path.insert(0, str(Path('C:/git/voynich').resolve()))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': 0, 'i': 0, 'in': 1, 'r': 2, 'ar': 2,
    'al': 3, 'l': 3, 'ol': 3, 'o': 4, 'ly': 4, 'am': 4,
    'm': 5, 'dy': 5, 'ry': 5, 'y': 5,
}
FL_MIDDLES = set(FL_STAGE_MAP.keys())

CLASS_MAP_PATH = Path('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json')
with open(CLASS_MAP_PATH, 'r', encoding='utf-8') as f:
    class_data = json.load(f)
TOKEN_TO_ROLE = class_data.get('token_to_role', {})
TOKEN_TO_CLASS = {k: int(v) for k, v in class_data.get('token_to_class', {}).items()}

STRONG_FWD = {'f26v','f76v','f112r','f82r','f115v','f85r2','f105r','f108v','f94r','f95v2','f106r'}

tx = Transcript()
morph = Morphology()

line_tokens = defaultdict(list)
for t in tx.currier_b():
    if t.folio in STRONG_FWD:
        line_tokens[(t.folio, t.line)].append(t)

def annotate(word):
    m = morph.extract(word)
    if not m:
        return {'word': word, 'is_fl': False, 'prefix': None, 'middle': None,
                'role': TOKEN_TO_ROLE.get(word, 'UNK'),
                'cls': TOKEN_TO_CLASS.get(word, -1)}
    is_fl = m.middle is not None and m.middle in FL_MIDDLES
    prefix = m.prefix if m.prefix else '_'
    return {'word': word, 'is_fl': is_fl, 'prefix': prefix, 'middle': m.middle,
            'role': TOKEN_TO_ROLE.get(word, 'UNK'),
            'cls': TOKEN_TO_CLASS.get(word, -1)}

annotated_lines = {}
for key, tokens in line_tokens.items():
    annotated_lines[key] = [annotate(t.word) for t in tokens]

N_SHUFFLES = 1000
rng = np.random.default_rng(42)

# LINK is class 29 per C876
LINK_CLASS = 29

print("=" * 80, flush=True)
print("FL RESOLUTION TEST 2: FL-LINK COMPLEMENTARITY", flush=True)
print("=" * 80, flush=True)

# =============================================
# 1. Distance to nearest LINK: FL vs Operational tokens
# =============================================
fl_link_distances = []
op_link_distances = []
fl_positions = []
op_positions = []

lines_with_both = 0

for key, annots in annotated_lines.items():
    # Find LINK positions (class 29, non-FL)
    link_pos = [i for i, a in enumerate(annots) if a['cls'] == LINK_CLASS and not a['is_fl']]
    if not link_pos:
        continue

    # Find FL positions
    fl_pos = [i for i, a in enumerate(annots) if a['is_fl']]
    # Find operational (non-FL, non-LINK) positions
    op_pos = [i for i, a in enumerate(annots) if not a['is_fl'] and a['cls'] != LINK_CLASS and a['role'] != 'UNK']

    if fl_pos:
        lines_with_both += 1

    for fp in fl_pos:
        min_dist = min(abs(fp - lp) for lp in link_pos)
        fl_link_distances.append(min_dist)
        fl_positions.append(fp / (len(annots) - 1) if len(annots) > 1 else 0.5)

    for op in op_pos:
        min_dist = min(abs(op - lp) for lp in link_pos)
        op_link_distances.append(min_dist)
        op_positions.append(op / (len(annots) - 1) if len(annots) > 1 else 0.5)

print(f"\n  Lines with both FL and LINK: {lines_with_both}", flush=True)
print(f"  FL-LINK distance measurements: {len(fl_link_distances)}", flush=True)
print(f"  OP-LINK distance measurements: {len(op_link_distances)}", flush=True)

if fl_link_distances and op_link_distances:
    print(f"\n  FL mean distance to LINK: {np.mean(fl_link_distances):.2f} (median {np.median(fl_link_distances):.1f})", flush=True)
    print(f"  OP mean distance to LINK: {np.mean(op_link_distances):.2f} (median {np.median(op_link_distances):.1f})", flush=True)

    # KS test
    ks_stat, ks_p = ks_2samp(fl_link_distances, op_link_distances)
    print(f"\n  KS test (FL vs OP distance-to-LINK):", flush=True)
    print(f"    KS statistic: {ks_stat:.4f}", flush=True)
    print(f"    p-value: {ks_p:.4e}", flush=True)

    # Mann-Whitney U
    u_stat, u_p = mannwhitneyu(fl_link_distances, op_link_distances, alternative='greater')
    print(f"\n  Mann-Whitney U (FL > OP, one-sided):", flush=True)
    print(f"    U statistic: {u_stat:.0f}", flush=True)
    print(f"    p-value: {u_p:.4e}", flush=True)

    if u_p < 0.05:
        print(f"    -> FL is significantly FARTHER from LINK than operational tokens", flush=True)
    else:
        print(f"    -> No significant difference", flush=True)

# =============================================
# 2. LINK-adjacent depletion: is FL depleted at distance 1 from LINK?
# =============================================
print(f"\n{'='*70}", flush=True)
print("LINK-ADJACENT DEPLETION TEST", flush=True)
print(f"{'='*70}", flush=True)

# For each LINK token, check: what's at distance 1, 2, 3?
link_neighbor_fl_rate = defaultdict(lambda: {'fl': 0, 'op': 0, 'total': 0})

for key, annots in annotated_lines.items():
    link_pos = [i for i, a in enumerate(annots) if a['cls'] == LINK_CLASS and not a['is_fl']]

    for lp in link_pos:
        for dist in [1, 2, 3, 4, 5]:
            for direction in [-1, 1]:
                j = lp + direction * dist
                if 0 <= j < len(annots):
                    if annots[j]['is_fl']:
                        link_neighbor_fl_rate[dist]['fl'] += 1
                    else:
                        link_neighbor_fl_rate[dist]['op'] += 1
                    link_neighbor_fl_rate[dist]['total'] += 1

# Baseline FL rate in these lines
total_fl = sum(1 for key, annots in annotated_lines.items()
               for a in annots if a['is_fl'])
total_tokens = sum(len(annots) for annots in annotated_lines.values())
baseline_fl_rate = total_fl / total_tokens

print(f"\n  Baseline FL rate: {baseline_fl_rate:.3f} ({total_fl}/{total_tokens})", flush=True)
print(f"\n  Distance from LINK -> FL rate:", flush=True)
print(f"  {'Dist':>5} {'FL':>5} {'Total':>6} {'Rate':>7} {'Enrich':>7}", flush=True)

for dist in [1, 2, 3, 4, 5]:
    d = link_neighbor_fl_rate[dist]
    if d['total'] > 0:
        rate = d['fl'] / d['total']
        enrich = rate / baseline_fl_rate if baseline_fl_rate > 0 else 0
        marker = "DEPLETED" if enrich < 0.7 else "ENRICHED" if enrich > 1.3 else ""
        print(f"  {dist:>5} {d['fl']:>5} {d['total']:>6} {rate:>7.3f} {enrich:>6.2f}x {marker}", flush=True)

# =============================================
# 3. Shuffle control: permute FL positions within prefix family
# =============================================
print(f"\n{'='*70}", flush=True)
print("SHUFFLE CONTROL: FL-LINK DISTANCE", flush=True)
print(f"{'='*70}", flush=True)

real_mean_dist = np.mean(fl_link_distances) if fl_link_distances else 0

shuf_mean_dists = []
for _ in range(N_SHUFFLES):
    shuf_dists = []

    for key, annots in annotated_lines.items():
        link_pos = [i for i, a in enumerate(annots) if a['cls'] == LINK_CLASS and not a['is_fl']]
        if not link_pos:
            continue

        fl_indices = [i for i, a in enumerate(annots) if a['is_fl']]
        non_link_non_fl = [i for i, a in enumerate(annots) if not a['is_fl'] and a['cls'] != LINK_CLASS]

        if not fl_indices:
            continue

        # Shuffle FL positions among all non-LINK positions (preserving count)
        available = fl_indices + non_link_non_fl
        if len(available) < len(fl_indices):
            continue
        shuf_fl_pos = rng.choice(available, size=len(fl_indices), replace=False)

        for fp in shuf_fl_pos:
            min_dist = min(abs(fp - lp) for lp in link_pos)
            shuf_dists.append(min_dist)

    if shuf_dists:
        shuf_mean_dists.append(np.mean(shuf_dists))

p_val = sum(1 for s in shuf_mean_dists if s >= real_mean_dist) / N_SHUFFLES
pctile = sum(1 for s in shuf_mean_dists if s < real_mean_dist) / N_SHUFFLES * 100

print(f"  Real FL mean distance to LINK: {real_mean_dist:.3f}", flush=True)
print(f"  Shuffle mean: {np.mean(shuf_mean_dists):.3f} +/- {np.std(shuf_mean_dists):.3f}", flush=True)
print(f"  Percentile: {pctile:.1f}th", flush=True)
print(f"  p-value: {p_val:.4f}", flush=True)

# =============================================
# 4. VERDICT
# =============================================
print(f"\n{'='*70}", flush=True)
print("VERDICT", flush=True)
print(f"{'='*70}", flush=True)

if fl_link_distances and op_link_distances:
    if u_p < 0.001 and p_val < 0.05:
        print(f"  H2 PASS: FL tokens significantly avoid LINK-proximate zones", flush=True)
        print(f"  -> Confirms FL as assessment phase, not monitoring", flush=True)
    elif u_p < 0.05:
        print(f"  H2 WEAK PASS: Some spatial separation between FL and LINK", flush=True)
    else:
        print(f"  H2 FAIL: No spatial separation between FL and LINK", flush=True)
        print(f"  -> FL and LINK are independent annotations", flush=True)
else:
    print(f"  H2 INCONCLUSIVE: Insufficient data", flush=True)

print(flush=True)
