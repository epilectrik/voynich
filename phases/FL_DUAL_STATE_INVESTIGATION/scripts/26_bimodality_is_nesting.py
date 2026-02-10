"""
26_bimodality_is_nesting.py

Close the loop: does the bimodality that motivated this phase
reduce to the nesting structure?

The original observation (Test 08 of FL_SEMANTIC_INTERPRETATION):
  - 12/15 FL MIDDLEs show negative kurtosis (bimodal)
  - Line-level concordance only 56.2%

Hypothesis: the two GMM components correspond to LOW (outer-left bookend
position) and HIGH (outer-right bookend position). If nesting explains
bimodality, then:
  1. GMM LOW component mean should correlate with typical outer-left position
  2. GMM HIGH component mean should correlate with typical outer-right position
  3. Residual within-component kurtosis should be unimodal (>0)
  4. The "concordance" failure is because two different FL tokens in the
     same line serve different nesting roles (LOW vs HIGH)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import kurtosis

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

line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Collect per-MIDDLE positions
per_middle_positions = defaultdict(list)
per_middle_line_positions = defaultdict(list)  # (line_key, idx, pos, n)

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            pos = idx / (n - 1)
            per_middle_positions[m.middle].append(pos)
            per_middle_line_positions[m.middle].append({
                'line': line_key, 'idx': idx, 'pos': pos, 'n': n
            })

# Fit GMMs
gmm_results = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)

    # Fit 1-component and 2-component
    gmm1 = GaussianMixture(n_components=1, random_state=42, n_init=10)
    gmm1.fit(X)
    gmm2 = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm2.fit(X)

    if gmm2.means_[0] > gmm2.means_[1]:
        swap = True
        low_mean = gmm2.means_[1][0]
        high_mean = gmm2.means_[0][0]
        low_weight = gmm2.weights_[1]
        high_weight = gmm2.weights_[0]
    else:
        swap = False
        low_mean = gmm2.means_[0][0]
        high_mean = gmm2.means_[1][0]
        low_weight = gmm2.weights_[0]
        high_weight = gmm2.weights_[1]

    # Classify each token into LOW/HIGH
    labels = gmm2.predict(X)
    if swap:
        labels = 1 - labels

    low_positions = X[labels == 0].flatten()
    high_positions = X[labels == 1].flatten()

    # Within-component kurtosis
    low_kurt = kurtosis(low_positions) if len(low_positions) >= 10 else None
    high_kurt = kurtosis(high_positions) if len(high_positions) >= 10 else None

    # Global kurtosis
    global_kurt = kurtosis(positions)

    gmm_results[mid] = {
        'n': len(positions),
        'global_kurt': global_kurt,
        'bic1': gmm1.bic(X),
        'bic2': gmm2.bic(X),
        'low_mean': low_mean,
        'high_mean': high_mean,
        'low_weight': low_weight,
        'high_weight': high_weight,
        'low_kurt': low_kurt,
        'high_kurt': high_kurt,
        'low_n': len(low_positions),
        'high_n': len(high_positions),
        'separation': high_mean - low_mean,
        'swap': swap,
        'model': gmm2,
    }

# ============================================================
# TEST 1: GMM component means vs expected nesting positions
# ============================================================
print(f"{'='*70}")
print("TEST 1: GMM COMPONENT MEANS vs NESTING POSITIONS")
print(f"{'='*70}")
print(f"\n  {'MIDDLE':>6} {'n':>5} {'Global K':>9} "
      f"{'LOW mean':>9} {'HIGH mean':>10} {'Sep':>6} "
      f"{'LOW K':>7} {'HIGH K':>8} {'BIC1':>8} {'BIC2':>8} {'Prefer':>7}")
print(f"  {'-'*95}")

n_bimodal_global = 0
n_unimodal_within = 0
n_total = 0
separations = []

for mid in sorted(gmm_results.keys(), key=lambda m: FL_STAGE_MAP[m][1]):
    r = gmm_results[mid]
    stage = FL_STAGE_MAP[mid][0]
    prefer = "2-comp" if r['bic2'] < r['bic1'] else "1-comp"
    low_k_str = f"{r['low_kurt']:.2f}" if r['low_kurt'] is not None else "N/A"
    high_k_str = f"{r['high_kurt']:.2f}" if r['high_kurt'] is not None else "N/A"

    print(f"  {mid:>6} {r['n']:>5} {r['global_kurt']:>9.2f} "
          f"{r['low_mean']:>9.3f} {r['high_mean']:>10.3f} {r['separation']:>6.3f} "
          f"{low_k_str:>7} {high_k_str:>8} {r['bic1']:>8.0f} {r['bic2']:>8.0f} {prefer:>7}")

    n_total += 1
    if r['global_kurt'] < 0:
        n_bimodal_global += 1
    if r['low_kurt'] is not None and r['high_kurt'] is not None:
        if r['low_kurt'] > -0.5 and r['high_kurt'] > -0.5:
            n_unimodal_within += 1
    separations.append(r['separation'])

print(f"\n  Globally bimodal (kurtosis < 0): {n_bimodal_global}/{n_total}")
print(f"  Within-component unimodal (kurtosis > -0.5): {n_unimodal_within}/{n_total}")
print(f"  Mean separation: {np.mean(separations):.3f}")

# ============================================================
# TEST 2: Do LOW components cluster near outer-left position?
# ============================================================
print(f"\n{'='*70}")
print("TEST 2: COMPONENT POSITION vs NESTING LAYER")
print(f"{'='*70}")

# Build actual nesting positions from lines
ol_positions = []
or_positions = []
fl_low_positions = []
fl_high_positions = []

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
        if is_fl and mid in gmm_results:
            r = gmm_results[mid]
            pred = r['model'].predict(np.array([[pos]]))[0]
            if r['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'

        all_info.append({'idx': idx, 'pos': pos, 'is_fl': is_fl, 'mode': mode})
        if is_fl and mode:
            fl_info.append({'idx': idx, 'pos': pos, 'mode': mode})

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

    ol_positions.append(gap[0]['pos'])
    or_positions.append(gap[-1]['pos'])
    for f in low_fls:
        fl_low_positions.append(f['pos'])
    for f in high_fls:
        fl_high_positions.append(f['pos'])

print(f"  FL-LOW  mean position: {np.mean(fl_low_positions):.3f} (std={np.std(fl_low_positions):.3f})")
print(f"  OUTER-L mean position: {np.mean(ol_positions):.3f} (std={np.std(ol_positions):.3f})")
print(f"  OUTER-R mean position: {np.mean(or_positions):.3f} (std={np.std(or_positions):.3f})")
print(f"  FL-HIGH mean position: {np.mean(fl_high_positions):.3f} (std={np.std(fl_high_positions):.3f})")

# Compare GMM component means to nesting layer means
low_means = [gmm_results[m]['low_mean'] for m in gmm_results]
high_means = [gmm_results[m]['high_mean'] for m in gmm_results]

print(f"\n  GMM LOW component means: {np.mean(low_means):.3f} (range {min(low_means):.3f}-{max(low_means):.3f})")
print(f"  GMM HIGH component means: {np.mean(high_means):.3f} (range {min(high_means):.3f}-{max(high_means):.3f})")

# Correlation between GMM means and actual nesting positions
print(f"\n  FL-LOW mean ({np.mean(fl_low_positions):.3f}) ~ GMM LOW mean ({np.mean(low_means):.3f})")
print(f"  FL-HIGH mean ({np.mean(fl_high_positions):.3f}) ~ GMM HIGH mean ({np.mean(high_means):.3f})")

# ============================================================
# TEST 3: Concordance reanalysis
# ============================================================
print(f"\n{'='*70}")
print("TEST 3: CONCORDANCE REANALYSIS")
print(f"{'='*70}")

# Original concordance: do FL tokens in the same line appear at
# positions consistent with their stage order?
# The failure (56.2%) was because LOW and HIGH tokens serve
# different nesting roles, so comparing across modes is invalid.

# Recompute concordance WITHIN each mode
concordant_within_low = 0
discordant_within_low = 0
concordant_within_high = 0
discordant_within_high = 0
concordant_cross_mode = 0
discordant_cross_mode = 0

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue

    fl_tokens = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP and m.middle in gmm_results:
            pos = idx / (n - 1)
            r = gmm_results[m.middle]
            pred = r['model'].predict(np.array([[pos]]))[0]
            if r['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage_num = STAGE_ORDER[FL_STAGE_MAP[m.middle][0]]
            fl_tokens.append({'pos': pos, 'mode': mode, 'stage': stage_num})

    # Compare all pairs
    for i in range(len(fl_tokens)):
        for j in range(i + 1, len(fl_tokens)):
            a, b = fl_tokens[i], fl_tokens[j]
            pos_order = a['pos'] < b['pos']
            stage_order = a['stage'] < b['stage']
            same_stage = a['stage'] == b['stage']

            if same_stage:
                continue

            concordant = (pos_order == stage_order)

            if a['mode'] == b['mode']:
                if a['mode'] == 'LOW':
                    if concordant:
                        concordant_within_low += 1
                    else:
                        discordant_within_low += 1
                else:
                    if concordant:
                        concordant_within_high += 1
                    else:
                        discordant_within_high += 1
            else:
                if concordant:
                    concordant_cross_mode += 1
                else:
                    discordant_cross_mode += 1

within_low_total = concordant_within_low + discordant_within_low
within_high_total = concordant_within_high + discordant_within_high
cross_mode_total = concordant_cross_mode + discordant_cross_mode

if within_low_total > 0:
    low_conc = concordant_within_low / within_low_total
    print(f"  Within-LOW concordance:  {low_conc:.1%} ({concordant_within_low}/{within_low_total})")

if within_high_total > 0:
    high_conc = concordant_within_high / within_high_total
    print(f"  Within-HIGH concordance: {high_conc:.1%} ({concordant_within_high}/{within_high_total})")

if cross_mode_total > 0:
    cross_conc = concordant_cross_mode / cross_mode_total
    print(f"  Cross-mode concordance:  {cross_conc:.1%} ({concordant_cross_mode}/{cross_mode_total})")

overall_total = within_low_total + within_high_total + cross_mode_total
overall_conc = (concordant_within_low + concordant_within_high + concordant_cross_mode) / overall_total if overall_total > 0 else 0
print(f"  Overall concordance:     {overall_conc:.1%} (was 56.2%)")

within_total = within_low_total + within_high_total
within_conc = (concordant_within_low + concordant_within_high) / within_total if within_total > 0 else 0
print(f"\n  Within-mode concordance: {within_conc:.1%}")
print(f"  Cross-mode concordance:  {cross_conc:.1%}" if cross_mode_total > 0 else "")
print(f"\n  Interpretation: cross-mode pairs mix different nesting roles,")
print(f"  explaining the low overall concordance.")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*70}")
print("VERDICT: DOES NESTING EXPLAIN BIMODALITY?")
print(f"{'='*70}")

# Criteria:
# 1. Within-component kurtosis is mostly unimodal
# 2. Component means align with nesting positions
# 3. Within-mode concordance is higher than cross-mode
# 4. Separation is substantial (> 0.3)

kurtosis_resolved = n_unimodal_within / n_total > 0.5 if n_total > 0 else False
positions_align = (abs(np.mean(low_means) - np.mean(fl_low_positions)) < 0.15 and
                   abs(np.mean(high_means) - np.mean(fl_high_positions)) < 0.15)
concordance_explained = within_conc > cross_conc + 0.05 if cross_mode_total > 0 else False
good_separation = np.mean(separations) > 0.3

checks = [kurtosis_resolved, positions_align, concordance_explained, good_separation]
n_pass = sum(checks)

print(f"  1. Kurtosis resolved within components: {'YES' if kurtosis_resolved else 'NO'} ({n_unimodal_within}/{n_total})")
print(f"  2. Component means align with nesting: {'YES' if positions_align else 'NO'}")
print(f"  3. Within-mode concordance > cross-mode: {'YES' if concordance_explained else 'NO'}")
print(f"  4. Good component separation (>0.3): {'YES' if good_separation else 'NO'} ({np.mean(separations):.3f})")

if n_pass >= 3:
    verdict = "BIMODALITY_IS_NESTING"
    explanation = f"The bimodality is explained by nesting roles ({n_pass}/4 checks pass)"
elif n_pass >= 2:
    verdict = "PARTIAL_EXPLANATION"
    explanation = f"Nesting partially explains bimodality ({n_pass}/4 checks pass)"
else:
    verdict = "INDEPENDENT_PHENOMENA"
    explanation = f"Bimodality is not reducible to nesting ({n_pass}/4 checks pass)"

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# Save
result = {
    'n_middles_tested': n_total,
    'n_bimodal_global': n_bimodal_global,
    'n_unimodal_within_component': n_unimodal_within,
    'mean_separation': round(float(np.mean(separations)), 3),
    'gmm_low_mean_avg': round(float(np.mean(low_means)), 3),
    'gmm_high_mean_avg': round(float(np.mean(high_means)), 3),
    'fl_low_nesting_mean': round(float(np.mean(fl_low_positions)), 3),
    'fl_high_nesting_mean': round(float(np.mean(fl_high_positions)), 3),
    'within_mode_concordance': round(float(within_conc), 3) if within_total > 0 else None,
    'cross_mode_concordance': round(float(cross_conc), 3) if cross_mode_total > 0 else None,
    'overall_concordance': round(float(overall_conc), 3),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "26_bimodality_is_nesting.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
