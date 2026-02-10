"""
07_gaussian_mixture.py

Gaussian Mixture Model: 1 vs 2 components per FL MIDDLE.

Q: Does a 2-component Gaussian fit better than 1-component?
- Fit 1-component and 2-component GMMs per MIDDLE (n >= 50)
- Compare BIC scores
- For 2-component fits: report component means, weights, separation
- Count how many MIDDLEs prefer 2 components
- Pass (dual): >60% of FL MIDDLEs prefer 2-component with separation > 0.15
- Fail (single): <30% prefer 2-component, or not well-separated
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

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

tx = Transcript()
morph = Morphology()

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL positions per MIDDLE
fl_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            fl_positions[m.middle].append(idx / (n - 1))

# ============================================================
# GMM fitting: 1 vs 2 components
# ============================================================
MIN_N = 50
gmm_results = {}

print(f"{'='*70}")
print(f"GMM Analysis: 1-component vs 2-component per FL MIDDLE")
print(f"{'='*70}")

for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    positions = fl_positions.get(mid, [])
    if len(positions) < MIN_N:
        print(f"  {mid:>4}: n={len(positions):>4} — SKIPPED (< {MIN_N})")
        continue

    X = np.array(positions).reshape(-1, 1)

    # Fit 1-component GMM
    gmm1 = GaussianMixture(n_components=1, random_state=42, n_init=5)
    gmm1.fit(X)
    bic1 = gmm1.bic(X)

    # Fit 2-component GMM
    gmm2 = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm2.fit(X)
    bic2 = gmm2.bic(X)

    # Fit 3-component GMM (for reference)
    gmm3 = GaussianMixture(n_components=3, random_state=42, n_init=10)
    gmm3.fit(X)
    bic3 = gmm3.bic(X)

    delta_bic = bic1 - bic2  # Positive = 2-component preferred
    delta_bic_3v2 = bic2 - bic3  # Positive = 3 preferred over 2

    # 2-component details
    means_2 = sorted(gmm2.means_.flatten())
    weights_2 = gmm2.weights_
    stds_2 = np.sqrt(gmm2.covariances_.flatten())

    # Sort by mean
    order = np.argsort(gmm2.means_.flatten())
    means_sorted = gmm2.means_.flatten()[order]
    weights_sorted = gmm2.weights_[order]
    stds_sorted = np.sqrt(gmm2.covariances_.flatten())[order]

    separation = abs(means_sorted[1] - means_sorted[0])
    weight_balance = min(weights_sorted) / max(weights_sorted)

    prefers_2 = delta_bic > 10 and separation > 0.10
    well_separated = separation > 0.15 and weight_balance > 0.15

    stage = FL_STAGE_MAP[mid][0]
    gmm_results[mid] = {
        'n': len(positions),
        'stage': stage,
        'bic_1': round(float(bic1), 1),
        'bic_2': round(float(bic2), 1),
        'bic_3': round(float(bic3), 1),
        'delta_bic_2v1': round(float(delta_bic), 1),
        'delta_bic_3v2': round(float(delta_bic_3v2), 1),
        'comp_means': [round(float(m), 3) for m in means_sorted],
        'comp_weights': [round(float(w), 3) for w in weights_sorted],
        'comp_stds': [round(float(s), 3) for s in stds_sorted],
        'separation': round(float(separation), 3),
        'weight_balance': round(float(weight_balance), 3),
        'prefers_2': bool(prefers_2),
        'well_separated': bool(well_separated),
    }

    pref = "2-COMP**" if prefers_2 else "1-comp"
    sep_label = f"sep={separation:.3f}" if prefers_2 else ""
    print(f"  {mid:>4} ({stage:>10}): n={len(positions):>4} "
          f"BIC1={bic1:>8.1f} BIC2={bic2:>8.1f} dBIC={delta_bic:>+7.1f} "
          f"[{pref}] means={[round(m, 3) for m in means_sorted]} "
          f"wts={[round(w, 2) for w in weights_sorted]} {sep_label}")

# ============================================================
# Summary
# ============================================================
tested = len(gmm_results)
prefer_2 = sum(1 for v in gmm_results.values() if v['prefers_2'])
well_sep = sum(1 for v in gmm_results.values() if v['well_separated'])

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  MIDDLEs tested (n >= {MIN_N}): {tested}")
print(f"  Prefer 2-component (dBIC > 10 + sep > 0.10): {prefer_2}/{tested} ({prefer_2/tested*100:.0f}%)")
print(f"  Well-separated (sep > 0.15 + balanced): {well_sep}/{tested} ({well_sep/tested*100:.0f}%)")

# ============================================================
# Verdict
# ============================================================
pct_prefer_2 = prefer_2 / tested if tested > 0 else 0

if pct_prefer_2 > 0.60 and well_sep >= prefer_2 * 0.5:
    verdict = "DUAL_STATE"
    explanation = (f"{prefer_2}/{tested} ({pct_prefer_2:.0%}) FL MIDDLEs prefer 2-component GMM, "
                   f"{well_sep} well-separated. Strong dual-state evidence.")
elif pct_prefer_2 < 0.30:
    verdict = "SINGLE_STATE"
    explanation = (f"Only {prefer_2}/{tested} ({pct_prefer_2:.0%}) prefer 2-component. "
                   f"FL positions are primarily unimodal.")
else:
    verdict = "MIXED"
    explanation = (f"{prefer_2}/{tested} ({pct_prefer_2:.0%}) prefer 2-component, "
                   f"{well_sep} well-separated. Mixed: some MIDDLEs dual-state, others not.")

print(f"\nVERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'min_n': MIN_N,
    'middles_tested': tested,
    'prefer_2_component': prefer_2,
    'well_separated': well_sep,
    'pct_prefer_2': round(pct_prefer_2, 3),
    'per_middle': gmm_results,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "07_gaussian_mixture.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
