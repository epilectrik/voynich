"""
Bubble-Point Oscillation Test (Tier 4)

Hypothesis: QO run lengths decrease with REGIME intensity because
hotter regimes reach bubble point faster, causing faster lane switching.

REGIME intensity ordering (CEI from process_isomorphism.md):
  REGIME_2 (0.367) < REGIME_1 (0.510) < REGIME_4 (0.584) < REGIME_3 (0.717)

Tests:
  T1: QO run length by REGIME (primary)
  T2: CHSH run length by REGIME (secondary)
  T3: Alternation rate by REGIME
  T4: QO fraction by REGIME (control baseline)
  T5: Partial correlation controlling QO fraction
  T6: Section-stratified analysis
"""

import json
import sys
import os
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology

# REGIME intensity ordering (CEI)
REGIME_ORDER = ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']
REGIME_RANK = {r: i for i, r in enumerate(REGIME_ORDER)}
REGIME_CEI = {'REGIME_2': 0.367, 'REGIME_1': 0.510, 'REGIME_4': 0.584, 'REGIME_3': 0.717}

# ── Load data ──────────────────────────────────────────────────────────────

with open('data/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
regime_map = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

tx = Transcript()
morph = Morphology()

# ── Extract EN lanes per folio/line ────────────────────────────────────────

folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)

    lane = None
    if m.prefix == 'qo':
        lane = 'QO'
    elif m.prefix in ('ch', 'sh'):
        lane = 'CHSH'

    if lane:
        folio_lines[token.folio][(token.line)].append(lane)
        folio_section[token.folio] = token.section

# ── Run-length computation ─────────────────────────────────────────────────

def compute_run_lengths(line_sequences, target_lane):
    """Compute run lengths for target_lane across all line sequences."""
    runs = []
    for seq in line_sequences:
        current_run = 0
        for tok in seq:
            if tok == target_lane:
                current_run += 1
            else:
                if current_run > 0:
                    runs.append(current_run)
                current_run = 0
        if current_run > 0:
            runs.append(current_run)
    return runs


def compute_alternation_rate(line_sequences):
    """Fraction of consecutive EN pairs that switch lanes."""
    switches = 0
    total = 0
    for seq in line_sequences:
        for i in range(len(seq) - 1):
            total += 1
            if seq[i] != seq[i + 1]:
                switches += 1
    return switches / total if total > 0 else None


def compute_qo_fraction(line_sequences):
    """QO tokens / total EN tokens."""
    qo = sum(tok == 'QO' for seq in line_sequences for tok in seq)
    total = sum(len(seq) for seq in line_sequences)
    return qo / total if total > 0 else None

# ── Per-folio metrics ──────────────────────────────────────────────────────

folio_metrics = []

for folio, lines_dict in folio_lines.items():
    regime = regime_map.get(folio)
    if not regime:
        continue

    line_seqs = list(lines_dict.values())
    # Filter to lines with >= 2 EN tokens (same as LANE_OSCILLATION phase)
    line_seqs = [s for s in line_seqs if len(s) >= 2]
    if not line_seqs:
        continue

    qo_runs = compute_run_lengths(line_seqs, 'QO')
    chsh_runs = compute_run_lengths(line_seqs, 'CHSH')
    alt_rate = compute_alternation_rate(line_seqs)
    qo_frac = compute_qo_fraction(line_seqs)
    total_en = sum(len(s) for s in line_seqs)

    folio_metrics.append({
        'folio': folio,
        'regime': regime,
        'section': folio_section.get(folio, 'UNK'),
        'qo_run_mean': float(np.mean(qo_runs)) if qo_runs else None,
        'qo_run_median': float(np.median(qo_runs)) if qo_runs else None,
        'qo_run_max': max(qo_runs) if qo_runs else None,
        'qo_run_count': len(qo_runs),
        'chsh_run_mean': float(np.mean(chsh_runs)) if chsh_runs else None,
        'chsh_run_median': float(np.median(chsh_runs)) if chsh_runs else None,
        'chsh_run_max': max(chsh_runs) if chsh_runs else None,
        'chsh_run_count': len(chsh_runs),
        'alternation_rate': alt_rate,
        'qo_fraction': qo_frac,
        'total_en': total_en,
        'n_lines': len(line_seqs),
    })

print(f"Folios with EN data: {len(folio_metrics)}")
print(f"Total EN tokens: {sum(m['total_en'] for m in folio_metrics)}")

# ── T1: QO run length by REGIME ───────────────────────────────────────────

print("\n" + "=" * 60)
print("T1: QO RUN LENGTH BY REGIME (PRIMARY TEST)")
print("=" * 60)

regime_qo_runs = defaultdict(list)
for m in folio_metrics:
    if m['qo_run_mean'] is not None:
        regime_qo_runs[m['regime']].append(m['qo_run_mean'])

t1_stats = {}
for regime in REGIME_ORDER:
    vals = regime_qo_runs[regime]
    t1_stats[regime] = {
        'n_folios': len(vals),
        'mean': float(np.mean(vals)) if vals else None,
        'std': float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
        'median': float(np.median(vals)) if vals else None,
    }
    print(f"  {regime} (CEI={REGIME_CEI[regime]:.3f}): "
          f"n={len(vals)}, mean={np.mean(vals):.4f}, "
          f"median={np.median(vals):.4f}, std={np.std(vals, ddof=1):.4f}")

# Spearman: folio QO run mean vs REGIME rank
ranks = [REGIME_RANK[m['regime']] for m in folio_metrics if m['qo_run_mean'] is not None]
qo_means = [m['qo_run_mean'] for m in folio_metrics if m['qo_run_mean'] is not None]
sp_rho, sp_p = stats.spearmanr(ranks, qo_means)
print(f"\n  Spearman (REGIME rank vs QO run mean): rho={sp_rho:.4f}, p={sp_p:.4f}")

# Kruskal-Wallis
groups = [regime_qo_runs[r] for r in REGIME_ORDER if regime_qo_runs[r]]
kw_stat, kw_p = stats.kruskal(*groups)
print(f"  Kruskal-Wallis: H={kw_stat:.4f}, p={kw_p:.4f}")

t1_result = {
    'per_regime': t1_stats,
    'spearman_rho': float(sp_rho),
    'spearman_p': float(sp_p),
    'kruskal_wallis_H': float(kw_stat),
    'kruskal_wallis_p': float(kw_p),
    'prediction': 'QO runs decrease with intensity',
    'direction_observed': 'decrease' if sp_rho < 0 else 'increase' if sp_rho > 0 else 'flat',
}

# ── T2: CHSH run length by REGIME ─────────────────────────────────────────

print("\n" + "=" * 60)
print("T2: CHSH RUN LENGTH BY REGIME (SECONDARY TEST)")
print("=" * 60)

regime_chsh_runs = defaultdict(list)
for m in folio_metrics:
    if m['chsh_run_mean'] is not None:
        regime_chsh_runs[m['regime']].append(m['chsh_run_mean'])

t2_stats = {}
for regime in REGIME_ORDER:
    vals = regime_chsh_runs[regime]
    t2_stats[regime] = {
        'n_folios': len(vals),
        'mean': float(np.mean(vals)) if vals else None,
        'std': float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
        'median': float(np.median(vals)) if vals else None,
    }
    print(f"  {regime} (CEI={REGIME_CEI[regime]:.3f}): "
          f"n={len(vals)}, mean={np.mean(vals):.4f}, "
          f"median={np.median(vals):.4f}, std={np.std(vals, ddof=1):.4f}")

ranks_chsh = [REGIME_RANK[m['regime']] for m in folio_metrics if m['chsh_run_mean'] is not None]
chsh_means = [m['chsh_run_mean'] for m in folio_metrics if m['chsh_run_mean'] is not None]
sp_rho2, sp_p2 = stats.spearmanr(ranks_chsh, chsh_means)
print(f"\n  Spearman (REGIME rank vs CHSH run mean): rho={sp_rho2:.4f}, p={sp_p2:.4f}")

kw_stat2, kw_p2 = stats.kruskal(*[regime_chsh_runs[r] for r in REGIME_ORDER if regime_chsh_runs[r]])
print(f"  Kruskal-Wallis: H={kw_stat2:.4f}, p={kw_p2:.4f}")

t2_result = {
    'per_regime': t2_stats,
    'spearman_rho': float(sp_rho2),
    'spearman_p': float(sp_p2),
    'kruskal_wallis_H': float(kw_stat2),
    'kruskal_wallis_p': float(kw_p2),
}

# ── T3: Alternation rate by REGIME ────────────────────────────────────────

print("\n" + "=" * 60)
print("T3: ALTERNATION RATE BY REGIME")
print("=" * 60)

regime_alt = defaultdict(list)
for m in folio_metrics:
    if m['alternation_rate'] is not None:
        regime_alt[m['regime']].append(m['alternation_rate'])

t3_stats = {}
for regime in REGIME_ORDER:
    vals = regime_alt[regime]
    t3_stats[regime] = {
        'n_folios': len(vals),
        'mean': float(np.mean(vals)) if vals else None,
        'std': float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
    }
    print(f"  {regime} (CEI={REGIME_CEI[regime]:.3f}): "
          f"n={len(vals)}, mean={np.mean(vals):.4f}, std={np.std(vals, ddof=1):.4f}")

ranks_alt = [REGIME_RANK[m['regime']] for m in folio_metrics if m['alternation_rate'] is not None]
alt_vals = [m['alternation_rate'] for m in folio_metrics if m['alternation_rate'] is not None]
sp_rho3, sp_p3 = stats.spearmanr(ranks_alt, alt_vals)
print(f"\n  Spearman (REGIME rank vs alternation rate): rho={sp_rho3:.4f}, p={sp_p3:.4f}")
print(f"  Prediction: positive (higher intensity -> faster cycling)")

t3_result = {
    'per_regime': t3_stats,
    'spearman_rho': float(sp_rho3),
    'spearman_p': float(sp_p3),
    'prediction': 'alternation increases with intensity',
    'direction_observed': 'increase' if sp_rho3 > 0 else 'decrease' if sp_rho3 < 0 else 'flat',
}

# ── T4: QO fraction by REGIME (control) ──────────────────────────────────

print("\n" + "=" * 60)
print("T4: QO FRACTION BY REGIME (CONTROL BASELINE)")
print("=" * 60)

regime_qof = defaultdict(list)
for m in folio_metrics:
    if m['qo_fraction'] is not None:
        regime_qof[m['regime']].append(m['qo_fraction'])

t4_stats = {}
for regime in REGIME_ORDER:
    vals = regime_qof[regime]
    t4_stats[regime] = {
        'n_folios': len(vals),
        'mean': float(np.mean(vals)) if vals else None,
        'std': float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
    }
    print(f"  {regime} (CEI={REGIME_CEI[regime]:.3f}): "
          f"n={len(vals)}, mean={np.mean(vals):.4f}, std={np.std(vals, ddof=1):.4f}")

ranks_qof = [REGIME_RANK[m['regime']] for m in folio_metrics if m['qo_fraction'] is not None]
qof_vals = [m['qo_fraction'] for m in folio_metrics if m['qo_fraction'] is not None]
sp_rho4, sp_p4 = stats.spearmanr(ranks_qof, qof_vals)
print(f"\n  Spearman (REGIME rank vs QO fraction): rho={sp_rho4:.4f}, p={sp_p4:.4f}")

t4_result = {
    'per_regime': t4_stats,
    'spearman_rho': float(sp_rho4),
    'spearman_p': float(sp_p4),
}

# ── T5: Partial correlation (QO run length ~ REGIME | QO fraction) ────────

print("\n" + "=" * 60)
print("T5: PARTIAL CORRELATION (QO RUN ~ REGIME | QO FRACTION)")
print("=" * 60)

valid = [m for m in folio_metrics
         if m['qo_run_mean'] is not None and m['qo_fraction'] is not None]

x = np.array([REGIME_RANK[m['regime']] for m in valid])
y = np.array([m['qo_run_mean'] for m in valid])
z = np.array([m['qo_fraction'] for m in valid])

# Residualize both x and y on z
slope_xz, intercept_xz, _, _, _ = stats.linregress(z, x)
slope_yz, intercept_yz, _, _, _ = stats.linregress(z, y)
x_resid = x - (slope_xz * z + intercept_xz)
y_resid = y - (slope_yz * z + intercept_yz)

partial_rho, partial_p = stats.spearmanr(x_resid, y_resid)
print(f"  Partial Spearman (REGIME rank vs QO run | QO fraction): rho={partial_rho:.4f}, p={partial_p:.4f}")
print(f"  Raw Spearman was: rho={sp_rho:.4f}, p={sp_p:.4f}")

if abs(partial_rho) < abs(sp_rho) * 0.5:
    partial_verdict = "CONFOUNDED (QO fraction explains most of the effect)"
elif partial_p < 0.05:
    partial_verdict = "INDEPENDENT (effect survives QO fraction control)"
else:
    partial_verdict = "ATTENUATED (partial not significant)"
print(f"  Verdict: {partial_verdict}")

t5_result = {
    'partial_spearman_rho': float(partial_rho),
    'partial_spearman_p': float(partial_p),
    'raw_spearman_rho': float(sp_rho),
    'raw_spearman_p': float(sp_p),
    'verdict': partial_verdict,
}

# ── T6: Section-stratified analysis ───────────────────────────────────────

print("\n" + "=" * 60)
print("T6: SECTION-STRATIFIED ANALYSIS")
print("=" * 60)

t6_result = {}
for section in ['B', 'H', 'S']:
    section_name = {'B': 'BIO', 'H': 'HERBAL', 'S': 'STARS'}[section]
    sub = [m for m in folio_metrics if m['section'] == section and m['qo_run_mean'] is not None]

    if len(sub) < 5:
        print(f"\n  {section_name}: n={len(sub)} (too few folios, skipping)")
        t6_result[section_name] = {'n_folios': len(sub), 'status': 'skipped'}
        continue

    print(f"\n  {section_name} (n={len(sub)}):")
    sec_regime_runs = defaultdict(list)
    for m in sub:
        sec_regime_runs[m['regime']].append(m['qo_run_mean'])

    sec_stats = {}
    for regime in REGIME_ORDER:
        vals = sec_regime_runs[regime]
        if vals:
            sec_stats[regime] = {'n': len(vals), 'mean': float(np.mean(vals))}
            print(f"    {regime}: n={len(vals)}, mean={np.mean(vals):.4f}")

    sec_ranks = [REGIME_RANK[m['regime']] for m in sub]
    sec_qo = [m['qo_run_mean'] for m in sub]
    unique_ranks = set(sec_ranks)
    if len(unique_ranks) < 2:
        sec_rho, sec_p = float('nan'), float('nan')
        print(f"    Spearman: N/A (all folios in one REGIME)")
    else:
        sec_rho, sec_p = stats.spearmanr(sec_ranks, sec_qo)
        print(f"    Spearman: rho={sec_rho:.4f}, p={sec_p:.4f}")

    t6_result[section_name] = {
        'n_folios': len(sub),
        'per_regime': sec_stats,
        'spearman_rho': float(sec_rho),
        'spearman_p': float(sec_p),
    }

# ── T7: Partial correlation controlling for section ───────────────────────

print("\n" + "=" * 60)
print("T7: PARTIAL CORRELATION (QO RUN ~ REGIME | SECTION)")
print("=" * 60)

# Encode section as numeric (for regression residualization)
section_map = {'B': 0, 'H': 1, 'S': 2}
valid7 = [m for m in folio_metrics
          if m['qo_run_mean'] is not None and m['section'] in section_map]

x7 = np.array([REGIME_RANK[m['regime']] for m in valid7])
y7 = np.array([m['qo_run_mean'] for m in valid7])
s7 = np.array([section_map[m['section']] for m in valid7])

# Residualize both x and y on section (dummy-coded)
from numpy.linalg import lstsq
S_dummies = np.column_stack([
    (s7 == 0).astype(float),
    (s7 == 1).astype(float),
    (s7 == 2).astype(float),
])
# Residualize REGIME rank on section
coef_x, _, _, _ = lstsq(S_dummies, x7, rcond=None)
x7_resid = x7 - S_dummies @ coef_x
# Residualize QO run mean on section
coef_y, _, _, _ = lstsq(S_dummies, y7, rcond=None)
y7_resid = y7 - S_dummies @ coef_y

partial_rho7, partial_p7 = stats.spearmanr(x7_resid, y7_resid)
print(f"  Partial Spearman (REGIME rank vs QO run | section): rho={partial_rho7:.4f}, p={partial_p7:.4f}")
print(f"  Raw Spearman was: rho={sp_rho:.4f}, p={sp_p:.4f}")
print(f"  T5 (controlling QO fraction) was: rho={partial_rho:.4f}, p={partial_p:.4f}")

# Also: double-partial controlling for BOTH section and QO fraction
qf7 = np.array([m['qo_fraction'] for m in valid7])
SQ_dummies = np.column_stack([S_dummies, qf7])
coef_x2, _, _, _ = lstsq(SQ_dummies, x7, rcond=None)
x7_resid2 = x7 - SQ_dummies @ coef_x2
coef_y2, _, _, _ = lstsq(SQ_dummies, y7, rcond=None)
y7_resid2 = y7 - SQ_dummies @ coef_y2

partial_rho7b, partial_p7b = stats.spearmanr(x7_resid2, y7_resid2)
print(f"  Double partial (REGIME vs QO run | section + QO frac): rho={partial_rho7b:.4f}, p={partial_p7b:.4f}")

if partial_p7 >= 0.05 and partial_p7b >= 0.05:
    t7_verdict = "SECTION_CONFOUNDED (REGIME effect vanishes after section control)"
elif partial_p7 < 0.05 and partial_rho7 > 0:
    t7_verdict = "REGIME_INDEPENDENT (effect survives section control, positive direction)"
elif partial_p7 < 0.05 and partial_rho7 < 0:
    t7_verdict = "REGIME_INDEPENDENT_NEGATIVE (effect survives, negative direction)"
else:
    t7_verdict = "MIXED"
print(f"  Verdict: {t7_verdict}")

t7_result = {
    'partial_spearman_rho_section': float(partial_rho7),
    'partial_spearman_p_section': float(partial_p7),
    'double_partial_rho': float(partial_rho7b),
    'double_partial_p': float(partial_p7b),
    'raw_spearman_rho': float(sp_rho),
    'raw_spearman_p': float(sp_p),
    'verdict': t7_verdict,
}

# ── Verdict ───────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("VERDICT")
print("=" * 60)

# Use the stronger of raw (T1) and partial (T5) for verdict
best_p = min(sp_p, partial_p)
best_rho = partial_rho if partial_p < sp_p else sp_rho

if best_p < 0.05 and best_rho < 0:
    verdict = "SUPPORTED"
    explanation = ("QO run lengths decrease significantly with REGIME intensity "
                   "(bubble-point oscillation consistent).")
elif best_p < 0.05 and best_rho > 0:
    verdict = "FALSIFIED"
    explanation = ("QO run lengths INCREASE with REGIME intensity after controlling "
                   "for QO fraction (opposite to bubble-point prediction). "
                   "Hotter regimes have LONGER energy application phases, not shorter.")
elif best_p >= 0.05:
    verdict = "NOT_SUPPORTED"
    explanation = "No significant relationship between REGIME intensity and QO run length."
else:
    verdict = "INCONCLUSIVE"
    explanation = "Mixed signals -- see individual test results."

print(f"  {verdict}: {explanation}")

# ── Save results ──────────────────────────────────────────────────────────

results = {
    'phase': 'BUBBLE_POINT_OSCILLATION_TEST',
    'hypothesis': 'QO run lengths decrease with REGIME intensity (bubble-point oscillation)',
    'regime_intensity_order': REGIME_ORDER,
    'regime_CEI': REGIME_CEI,
    'n_folios': len(folio_metrics),
    'total_en_tokens': sum(m['total_en'] for m in folio_metrics),
    'T1_qo_run_by_regime': t1_result,
    'T2_chsh_run_by_regime': t2_result,
    'T3_alternation_by_regime': t3_result,
    'T4_qo_fraction_by_regime': t4_result,
    'T5_partial_correlation': t5_result,
    'T6_section_stratified': t6_result,
    'T7_section_controlled': t7_result,
    'verdict': verdict,
    'explanation': explanation,
    'folio_details': folio_metrics,
}

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'bubble_point_results.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")
