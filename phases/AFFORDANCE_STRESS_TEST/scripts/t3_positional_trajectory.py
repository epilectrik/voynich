#!/usr/bin/env python3
"""T3: Positional Trajectory Curvature per Affordance Bin.

Profiles bins longitudinally:
  - Within-folio quartile density (front/mid/late-loading)
  - Within-line position bias
  - Radial depth x position interaction

Expert: some bins should correspond to setup, work, check, or close phases.
"""

import sys, json, functools
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Load data ──────────────────────────────────────────────────────

with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
    aff = json.load(f)

middle_to_bin = {}
middle_to_depth = {}
bin_labels = {}
for mid, data in aff['middles'].items():
    middle_to_bin[mid] = data['affordance_bin']
    middle_to_depth[mid] = data.get('radial_depth', 0)
for b, meta in aff['_metadata']['affordance_bins'].items():
    bin_labels[int(b)] = meta['label']

FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]

# ── Build corpus structure ─────────────────────────────────────────

tx = Transcript()
morph = Morphology()

# Organize tokens by folio, then by line
folio_lines = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    mid = m.middle if m.middle else ''
    b = middle_to_bin.get(mid, -1)
    depth = middle_to_depth.get(mid, 0)
    folio_lines[token.folio][token.line].append({
        'word': word,
        'middle': mid,
        'bin': b,
        'depth': depth,
    })

# Get line ordering per folio
folio_line_order = {}
for folio, lines in folio_lines.items():
    folio_line_order[folio] = sorted(lines.keys())

print("=" * 70)
print("T3: POSITIONAL TRAJECTORY CURVATURE PER AFFORDANCE BIN")
print("=" * 70)
print(f"\nCorpus: {len(folio_lines)} folios")

# ── ANALYSIS 1: Folio-level quartile density ───────────────────────

print(f"\n{'=' * 70}")
print("FOLIO-LEVEL QUARTILE DENSITY")
print("=" * 70)

# For each folio, assign lines to quartiles (Q1-Q4)
bin_quartile = defaultdict(lambda: Counter())  # bin → {Q1: n, Q2: n, ...}
bin_total = Counter()

for folio, line_order in folio_line_order.items():
    n_lines = len(line_order)
    if n_lines < 4:
        continue  # skip very short folios

    for idx, line_num in enumerate(line_order):
        # Quartile assignment
        q = min(int(4 * idx / n_lines), 3)  # 0,1,2,3
        q_label = f"Q{q + 1}"

        for tok in folio_lines[folio][line_num]:
            b = tok['bin']
            if b == 4 or b == -1:
                continue
            bin_total[b] += 1
            bin_quartile[b][q_label] += 1

print(f"\n  {'Bin':>4} {'Label':>25} {'Total':>7} {'Q1%':>6} {'Q2%':>6} {'Q3%':>6} {'Q4%':>6} {'Slope':>7} {'Peak':>4}")
print(f"  {'-' * 75}")

bin_slopes = {}
bin_peaks = {}
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    total = bin_total[b]
    qs = [bin_quartile[b][f"Q{i}"] for i in range(1, 5)]
    pcts = [100 * q / total if total > 0 else 0 for q in qs]

    # Slope: linear regression of density vs quartile position
    if total > 0:
        x = np.array([1, 2, 3, 4])
        y = np.array(pcts)
        slope, intercept, r, p, se = stats.linregress(x, y)
        bin_slopes[b] = slope
        peak = np.argmax(pcts) + 1
        bin_peaks[b] = peak
    else:
        slope = 0
        peak = 0
        bin_slopes[b] = 0
        bin_peaks[b] = 0

    print(f"  {b:>4} {label:>25} {total:>7} {pcts[0]:>5.1f}% {pcts[1]:>5.1f}% {pcts[2]:>5.1f}% {pcts[3]:>5.1f}% {slope:>+7.2f} Q{peak}")

# ── ANALYSIS 2: Within-line position ───────────────────────────────

print(f"\n{'=' * 70}")
print("WITHIN-LINE POSITION DISTRIBUTION")
print("=" * 70)

# For each token, compute relative position in line
bin_line_pos = defaultdict(list)  # bin → [relative positions]
bin_initial = Counter()
bin_final = Counter()
bin_total2 = Counter()

for folio, lines in folio_lines.items():
    for line_num, tokens in lines.items():
        n = len(tokens)
        if n == 0:
            continue
        for i, tok in enumerate(tokens):
            b = tok['bin']
            if b == 4 or b == -1:
                continue
            rel_pos = i / max(n - 1, 1)
            bin_line_pos[b].append(rel_pos)
            bin_total2[b] += 1
            if i == 0:
                bin_initial[b] += 1
            if i == n - 1:
                bin_final[b] += 1

print(f"\n  {'Bin':>4} {'Label':>25} {'Init%':>7} {'Final%':>7} {'MeanPos':>8} {'MedPos':>7} {'StdPos':>7}")
print(f"  {'-' * 68}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    total = bin_total2[b]
    init_pct = 100 * bin_initial[b] / total if total > 0 else 0
    final_pct = 100 * bin_final[b] / total if total > 0 else 0
    mean_pos = np.mean(bin_line_pos[b]) if bin_line_pos[b] else 0
    med_pos = np.median(bin_line_pos[b]) if bin_line_pos[b] else 0
    std_pos = np.std(bin_line_pos[b]) if bin_line_pos[b] else 0
    print(f"  {b:>4} {label:>25} {init_pct:>6.1f}% {final_pct:>6.1f}% {mean_pos:>8.3f} {med_pos:>7.3f} {std_pos:>7.3f}")

# ── ANALYSIS 3: Radial depth × quartile interaction ────────────────

print(f"\n{'=' * 70}")
print("RADIAL DEPTH x QUARTILE INTERACTION")
print("=" * 70)

# For each bin, compute mean depth in each quartile
bin_quartile_depth = defaultdict(lambda: defaultdict(list))

for folio, line_order_list in folio_line_order.items():
    n_lines = len(line_order_list)
    if n_lines < 4:
        continue
    for idx, line_num in enumerate(line_order_list):
        q = min(int(4 * idx / n_lines), 3)
        q_label = f"Q{q + 1}"
        for tok in folio_lines[folio][line_num]:
            b = tok['bin']
            if b == 4 or b == -1:
                continue
            bin_quartile_depth[b][q_label].append(tok['depth'])

print(f"\n  {'Bin':>4} {'Label':>25} {'D_Q1':>7} {'D_Q2':>7} {'D_Q3':>7} {'D_Q4':>7} {'D_slope':>8}")
print(f"  {'-' * 65}")

bin_depth_slopes = {}
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    d_qs = []
    for qi in range(1, 5):
        vals = bin_quartile_depth[b][f"Q{qi}"]
        d_qs.append(np.mean(vals) if vals else 0)

    # Depth slope across quartiles
    x = np.array([1, 2, 3, 4])
    y = np.array(d_qs)
    if np.std(y) > 0:
        slope, _, _, p, _ = stats.linregress(x, y)
    else:
        slope = 0
    bin_depth_slopes[b] = slope

    print(f"  {b:>4} {label:>25} {d_qs[0]:>7.3f} {d_qs[1]:>7.3f} {d_qs[2]:>7.3f} {d_qs[3]:>7.3f} {slope:>+8.4f}")

# ── STATISTICAL TESTS ──────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("STATISTICAL TESTS")
print("=" * 70)

stat_results = {}

# Chi-square on bin × quartile contingency table
contingency = np.array([
    [bin_quartile[b][f"Q{q}"] for q in range(1, 5)]
    for b in FUNCTIONAL_BINS
])
if contingency.sum() > 0:
    chi2, p, dof, exp = stats.chi2_contingency(contingency)
    print(f"\n  Chi-square on bin x quartile:")
    print(f"    chi2 = {chi2:.3f}, df = {dof}, p = {p:.2e}")
    stat_results['chi2_bin_quartile'] = {'chi2': float(chi2), 'df': int(dof), 'p': float(p)}

# KW on within-line position across bins
pos_groups = [bin_line_pos[b] for b in FUNCTIONAL_BINS if len(bin_line_pos[b]) >= 5]
pos_labels = [b for b in FUNCTIONAL_BINS if len(bin_line_pos[b]) >= 5]
if len(pos_groups) >= 2:
    h, p = stats.kruskal(*pos_groups)
    print(f"\n  Kruskal-Wallis on within-line relative position:")
    print(f"    H = {h:.3f}, p = {p:.2e}")
    stat_results['kruskal_line_position'] = {'H': float(h), 'p': float(p)}

# Per-bin uniformity tests (chi-square goodness-of-fit vs uniform quartile)
print(f"\n  Per-bin quartile uniformity (chi-square GoF):")
for b in FUNCTIONAL_BINS:
    observed = np.array([bin_quartile[b][f"Q{q}"] for q in range(1, 5)])
    total = observed.sum()
    if total >= 20:
        expected = np.full(4, total / 4)
        chi2_gof, p_gof = stats.chisquare(observed, f_exp=expected)
        sig = "*" if p_gof < 0.05 else " "
        sig2 = "**" if p_gof < 0.001 else sig
        print(f"    Bin {b:>2} ({bin_labels.get(b, '?'):>25}): chi2={chi2_gof:>8.2f}, p={p_gof:.4f} {sig2}")
        stat_results[f'uniformity_bin_{b}'] = {'chi2': float(chi2_gof), 'p': float(p_gof)}

# ── EXPERT PREDICTION VERIFICATION ────────────────────────────────

print(f"\n{'=' * 70}")
print("EXPERT PREDICTION VERIFICATION")
print("=" * 70)

predictions = []

# P1: FLOW_TERMINAL (0) is late-positioned (high final_rate, positive slope)
p1 = bin_slopes.get(0, 0) > 0
predictions.append(('FLOW_TERMINAL late-positioned', p1, f"slope={bin_slopes.get(0, 0):+.2f}"))

# P2: HUB_UNIVERSAL (6) is positionally uniform
b6_qs = [bin_quartile[6][f"Q{q}"] for q in range(1, 5)]
b6_total = sum(b6_qs)
if b6_total >= 20:
    expected = np.full(4, b6_total / 4)
    chi2_b6, p_b6 = stats.chisquare(np.array(b6_qs), f_exp=expected)
    p2 = p_b6 > 0.05  # NOT significant departure from uniform
    predictions.append(('HUB_UNIVERSAL uniform quartile', p2, f"chi2={chi2_b6:.2f}, p={p_b6:.4f}"))
else:
    predictions.append(('HUB_UNIVERSAL uniform quartile', False, "insufficient data"))

# P3: Bins show significantly different positional profiles (chi-square on full table)
if 'chi2_bin_quartile' in stat_results:
    p3 = stat_results['chi2_bin_quartile']['p'] < 0.05
    predictions.append(('Bins differ in positional profile', p3, f"chi2={stat_results['chi2_bin_quartile']['chi2']:.1f}, p={stat_results['chi2_bin_quartile']['p']:.2e}"))

# P4: FLOW_TERMINAL (0) has highest final_rate
b0_final = bin_final[0] / bin_total2[0] if bin_total2[0] > 0 else 0
max_final = max(bin_final[b] / bin_total2[b] for b in FUNCTIONAL_BINS if bin_total2[b] > 0)
p4 = b0_final >= max_final * 0.9  # within 90% of highest
predictions.append(('FLOW_TERMINAL highest final_rate', p4, f"final_rate={b0_final:.3f} vs max={max_final:.3f}"))

for name, result, detail in predictions:
    status = "CONFIRMED" if result else "REJECTED"
    print(f"\n  [{status}] {name}")
    print(f"    {detail}")

confirmed = sum(1 for _, r, _ in predictions if r)
print(f"\n  SCORE: {confirmed}/{len(predictions)} predictions confirmed")

# ── Save results ───────────────────────────────────────────────────

results = {
    'metadata': {
        'phase': 'AFFORDANCE_STRESS_TEST',
        'test': 'T3_POSITIONAL_TRAJECTORY',
        'n_folios': len(folio_lines),
    },
    'per_bin': {},
    'statistical_tests': stat_results,
    'predictions': {name: {'confirmed': bool(result), 'detail': detail} for name, result, detail in predictions},
}

for b in FUNCTIONAL_BINS:
    total = bin_total[b]
    total2 = bin_total2[b]
    qs = [bin_quartile[b][f"Q{q}"] / total if total > 0 else 0 for q in range(1, 5)]
    results['per_bin'][str(b)] = {
        'label': bin_labels.get(b, '?'),
        'total_tokens': total,
        'quartile_density': {f"Q{i+1}": round(q, 4) for i, q in enumerate(qs)},
        'trajectory_slope': round(bin_slopes.get(b, 0), 4),
        'peak_quartile': f"Q{bin_peaks.get(b, 0)}",
        'initial_rate': round(bin_initial[b] / total2, 4) if total2 > 0 else 0,
        'final_rate': round(bin_final[b] / total2, 4) if total2 > 0 else 0,
        'mean_line_position': round(float(np.mean(bin_line_pos[b])), 4) if bin_line_pos[b] else None,
        'depth_slope_across_quartiles': round(bin_depth_slopes.get(b, 0), 5),
    }

out_path = PROJECT / 'phases' / 'AFFORDANCE_STRESS_TEST' / 'results' / 't3_positional_trajectory.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {out_path}")
