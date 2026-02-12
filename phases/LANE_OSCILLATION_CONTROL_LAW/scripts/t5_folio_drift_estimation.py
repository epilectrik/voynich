#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T5: Folio Drift Estimation

Quantifies within-folio temporal drift in lane balance and tests whether
drift is intrinsic (regime-level property) or emergent from EN density
variation across folio position.

Method:
  - Divide each folio's lines into 4 positional quartiles (Q1=earliest, Q4=latest)
  - Compute QO fraction and EN density per quartile
  - Aggregate by regime: mean QO fraction, linear drift, Spearman rho
  - Partial correlation (QO vs quartile, controlling for EN density) to
    distinguish intrinsic vs density-emergent drift
  - Overall Spearman across all folios

Targets (C668):
  - Overall rho ~ -0.058 (slight CHSH-ward drift)
  - REGIME_2 shows strongest drift
  - REGIME_4 should be flat (delta near zero)
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================
print("=" * 60)
print("T5: Folio Drift Estimation")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # C560/C581 correction

# Load EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

# Load regime mapping
with open(PROJECT_ROOT / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json') as f:
    regime_data = json.load(f)

# Build folio -> regime lookup
folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

print(f"Regime mapping: {sum(len(v) for v in regime_data.values())} folios across {len(regime_data)} regimes")

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Build line-organized B token data
print("Building line-organized B token data...")
lines = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    cls = token_to_class.get(w)
    m = morph.extract(w)

    en_subfamily = None
    if cls is not None and cls in all_en_classes:
        if m.prefix == 'qo':
            en_subfamily = 'QO'
        elif m.prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'

    lines[(token.folio, token.line)].append({
        'word': w,
        'class': cls,
        'en_subfamily': en_subfamily,
        'folio': token.folio,
    })

print(f"B lines: {len(lines)}")

# ============================================================
# SECTION 2: Organize by Folio and Line
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Organize by Folio and Line")
print("=" * 60)

# Group lines by folio, sorted by line number
folio_lines = defaultdict(dict)
for (folio, line_num), toks in lines.items():
    folio_lines[folio][line_num] = toks

# Filter to folios with at least 4 lines (needed for quartile division)
MIN_LINES = 4
valid_folios = {f: sorted(lns.keys()) for f, lns in folio_lines.items()
                if len(lns) >= MIN_LINES}

print(f"Folios with >= {MIN_LINES} lines: {len(valid_folios)}")
print(f"Folios excluded: {len(folio_lines) - len(valid_folios)}")

# ============================================================
# SECTION 3: Compute Per-Quartile Statistics
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Compute Per-Quartile Statistics")
print("=" * 60)

N_QUARTILES = 4


def assign_quartiles(sorted_line_nums):
    """Assign each line to a quartile (0-3) by splitting into 4 roughly equal groups."""
    n = len(sorted_line_nums)
    assignments = {}
    for i, ln in enumerate(sorted_line_nums):
        q = min(int(i * N_QUARTILES / n), N_QUARTILES - 1)
        assignments[ln] = q
    return assignments


# Per-folio, per-quartile stats
folio_quartile_data = []  # List of dicts with folio-level quartile info

for folio, sorted_lns in valid_folios.items():
    q_assignments = assign_quartiles(sorted_lns)
    regime = folio_to_regime.get(folio, 'UNKNOWN')

    # Accumulate per-quartile
    q_en_qo = defaultdict(int)
    q_en_chsh = defaultdict(int)
    q_total_tokens = defaultdict(int)

    for ln in sorted_lns:
        q = q_assignments[ln]
        toks = folio_lines[folio][ln]
        q_total_tokens[q] += len(toks)
        for t in toks:
            if t['en_subfamily'] == 'QO':
                q_en_qo[q] += 1
            elif t['en_subfamily'] == 'CHSH':
                q_en_chsh[q] += 1

    # Compute QO fraction and EN density per quartile
    quartile_stats = {}
    for q in range(N_QUARTILES):
        en_total = q_en_qo[q] + q_en_chsh[q]
        total = q_total_tokens[q]
        qo_frac = q_en_qo[q] / en_total if en_total > 0 else None
        en_density = en_total / total if total > 0 else 0.0
        quartile_stats[q] = {
            'qo_count': q_en_qo[q],
            'chsh_count': q_en_chsh[q],
            'en_total': en_total,
            'total_tokens': total,
            'qo_fraction': qo_frac,
            'en_density': en_density,
        }

    folio_quartile_data.append({
        'folio': folio,
        'regime': regime,
        'n_lines': len(sorted_lns),
        'quartile_stats': quartile_stats,
    })

print(f"Folio quartile records: {len(folio_quartile_data)}")

# ============================================================
# SECTION 4: Per-Regime Aggregation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Per-Regime Aggregation")
print("=" * 60)

regime_results = {}

for regime in sorted(regime_data.keys()):
    regime_folios = [fd for fd in folio_quartile_data if fd['regime'] == regime]
    n_folios = len(regime_folios)
    if n_folios == 0:
        continue

    # Collect QO fractions and EN densities per quartile across folios
    q_qo_fracs = defaultdict(list)  # quartile -> list of QO fractions
    q_en_densities = defaultdict(list)

    for fd in regime_folios:
        for q in range(N_QUARTILES):
            qs = fd['quartile_stats'][q]
            if qs['qo_fraction'] is not None:
                q_qo_fracs[q].append(qs['qo_fraction'])
                q_en_densities[q].append(qs['en_density'])

    # Mean QO fraction per quartile
    mean_qo_per_q = {}
    mean_en_density_per_q = {}
    for q in range(N_QUARTILES):
        if q_qo_fracs[q]:
            mean_qo_per_q[q] = float(np.mean(q_qo_fracs[q]))
            mean_en_density_per_q[q] = float(np.mean(q_en_densities[q]))
        else:
            mean_qo_per_q[q] = None
            mean_en_density_per_q[q] = None

    # Linear drift: collect (quartile_index, qo_fraction) pairs across all folios
    all_q_vals = []
    all_qo_vals = []
    all_en_vals = []
    for fd in regime_folios:
        for q in range(N_QUARTILES):
            qs = fd['quartile_stats'][q]
            if qs['qo_fraction'] is not None:
                all_q_vals.append(q)
                all_qo_vals.append(qs['qo_fraction'])
                all_en_vals.append(qs['en_density'])

    # Spearman correlation: QO fraction vs quartile position
    if len(all_q_vals) >= 4:
        rho, p_val = stats.spearmanr(all_q_vals, all_qo_vals)
        # Linear regression for delta_QO (slope)
        slope, intercept, r_val, p_lr, std_err = stats.linregress(all_q_vals, all_qo_vals)
        delta_qo = float(slope)
    else:
        rho, p_val = float('nan'), float('nan')
        delta_qo = float('nan')

    # Partial correlation: QO_fraction vs quartile, controlling for EN_density
    partial_rho = float('nan')
    partial_p = float('nan')
    if len(all_q_vals) >= 6:  # Need enough points for partial correlation
        q_arr = np.array(all_q_vals, dtype=float)
        qo_arr = np.array(all_qo_vals, dtype=float)
        en_arr = np.array(all_en_vals, dtype=float)

        # Partial correlation via residual method:
        # Regress QO on EN -> residuals_qo
        # Regress Q on EN -> residuals_q
        # Correlate residuals
        if np.std(en_arr) > 1e-12:
            slope_qo_en, int_qo_en, _, _, _ = stats.linregress(en_arr, qo_arr)
            resid_qo = qo_arr - (slope_qo_en * en_arr + int_qo_en)

            slope_q_en, int_q_en, _, _, _ = stats.linregress(en_arr, q_arr)
            resid_q = q_arr - (slope_q_en * en_arr + int_q_en)

            if np.std(resid_qo) > 1e-12 and np.std(resid_q) > 1e-12:
                partial_rho, partial_p = stats.spearmanr(resid_q, resid_qo)

    regime_results[regime] = {
        'n_folios': n_folios,
        'n_observations': len(all_q_vals),
        'mean_qo_per_quartile': {f'Q{q+1}': mean_qo_per_q[q] for q in range(N_QUARTILES)},
        'mean_en_density_per_quartile': {f'Q{q+1}': mean_en_density_per_q[q] for q in range(N_QUARTILES)},
        'delta_QO': float(delta_qo),
        'spearman_rho': float(rho),
        'spearman_p': float(p_val),
        'partial_rho_controlling_en_density': float(partial_rho),
        'partial_p_controlling_en_density': float(partial_p),
    }

    print(f"\n{regime} (n_folios={n_folios}, n_obs={len(all_q_vals)}):")
    for q in range(N_QUARTILES):
        qo_str = f"{mean_qo_per_q[q]:.4f}" if mean_qo_per_q[q] is not None else "N/A"
        en_str = f"{mean_en_density_per_q[q]:.4f}" if mean_en_density_per_q[q] is not None else "N/A"
        print(f"  Q{q+1}: mean QO frac = {qo_str}, mean EN density = {en_str}")
    print(f"  delta_QO (slope): {delta_qo:.6f}")
    print(f"  Spearman rho: {rho:.4f}, p = {p_val:.4f}")
    print(f"  Partial rho (ctrl EN density): {partial_rho:.4f}, p = {partial_p:.4f}")

# ============================================================
# SECTION 5: Overall Drift (All Folios)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Overall Drift (All Folios)")
print("=" * 60)

all_q_overall = []
all_qo_overall = []
all_en_overall = []

for fd in folio_quartile_data:
    for q in range(N_QUARTILES):
        qs = fd['quartile_stats'][q]
        if qs['qo_fraction'] is not None:
            all_q_overall.append(q)
            all_qo_overall.append(qs['qo_fraction'])
            all_en_overall.append(qs['en_density'])

overall_rho, overall_p = stats.spearmanr(all_q_overall, all_qo_overall)
overall_slope, overall_intercept, _, _, _ = stats.linregress(all_q_overall, all_qo_overall)

print(f"Overall observations: {len(all_q_overall)}")
print(f"Overall Spearman rho: {overall_rho:.4f}, p = {overall_p:.6f}")
print(f"Overall linear slope: {overall_slope:.6f}")

# Overall partial correlation
q_arr_all = np.array(all_q_overall, dtype=float)
qo_arr_all = np.array(all_qo_overall, dtype=float)
en_arr_all = np.array(all_en_overall, dtype=float)

overall_partial_rho = float('nan')
overall_partial_p = float('nan')
if np.std(en_arr_all) > 1e-12:
    sl1, int1, _, _, _ = stats.linregress(en_arr_all, qo_arr_all)
    resid_qo_all = qo_arr_all - (sl1 * en_arr_all + int1)

    sl2, int2, _, _, _ = stats.linregress(en_arr_all, q_arr_all)
    resid_q_all = q_arr_all - (sl2 * en_arr_all + int2)

    if np.std(resid_qo_all) > 1e-12 and np.std(resid_q_all) > 1e-12:
        overall_partial_rho, overall_partial_p = stats.spearmanr(resid_q_all, resid_qo_all)

print(f"Overall partial rho (ctrl EN density): {overall_partial_rho:.4f}, p = {overall_partial_p:.6f}")

# ============================================================
# SECTION 6: Drift Classification
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Drift Classification")
print("=" * 60)

# Classification logic:
# If raw rho is significant but partial rho is ~0 -> density-emergent
# If partial rho remains significant -> intrinsic
# If raw rho is not significant -> no drift

SIGNIFICANCE_THRESHOLD = 0.05
PARTIAL_NEAR_ZERO = 0.03  # Threshold for "near zero" partial correlation

overall_classification = 'no_drift'
if overall_p < SIGNIFICANCE_THRESHOLD:
    if abs(overall_partial_rho) < PARTIAL_NEAR_ZERO or overall_partial_p >= SIGNIFICANCE_THRESHOLD:
        overall_classification = 'density_emergent'
    else:
        overall_classification = 'intrinsic'
else:
    overall_classification = 'no_significant_drift'

per_regime_classification = {}
for regime, rr in regime_results.items():
    if rr['spearman_p'] < SIGNIFICANCE_THRESHOLD:
        if (abs(rr['partial_rho_controlling_en_density']) < PARTIAL_NEAR_ZERO or
                rr['partial_p_controlling_en_density'] >= SIGNIFICANCE_THRESHOLD):
            per_regime_classification[regime] = 'density_emergent'
        else:
            per_regime_classification[regime] = 'intrinsic'
    else:
        per_regime_classification[regime] = 'no_significant_drift'

print(f"Overall drift classification: {overall_classification}")
for regime in sorted(per_regime_classification.keys()):
    print(f"  {regime}: {per_regime_classification[regime]}")

# ============================================================
# SECTION 7: Per-Folio Drift Parameters
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: Per-Folio Drift Parameters")
print("=" * 60)

per_folio_drift = []
for fd in folio_quartile_data:
    # Get Q1 and Q4 QO fractions
    qo_q1 = fd['quartile_stats'][0]['qo_fraction']
    qo_q4 = fd['quartile_stats'][3]['qo_fraction']

    if qo_q1 is not None and qo_q4 is not None:
        delta = qo_q4 - qo_q1
    else:
        delta = None

    per_folio_drift.append({
        'folio': fd['folio'],
        'regime': fd['regime'],
        'n_lines': fd['n_lines'],
        'QO_Q1': float(qo_q1) if qo_q1 is not None else None,
        'QO_Q4': float(qo_q4) if qo_q4 is not None else None,
        'delta': float(delta) if delta is not None else None,
    })

n_with_drift = sum(1 for d in per_folio_drift if d['delta'] is not None)
drifts = [d['delta'] for d in per_folio_drift if d['delta'] is not None]
print(f"Folios with computable drift: {n_with_drift}")
if drifts:
    print(f"  Mean delta: {np.mean(drifts):.4f}")
    print(f"  Median delta: {np.median(drifts):.4f}")
    print(f"  Negative drift (CHSH-ward): {sum(1 for d in drifts if d < 0)}")
    print(f"  Positive drift (QO-ward): {sum(1 for d in drifts if d > 0)}")
    print(f"  Zero drift: {sum(1 for d in drifts if d == 0)}")

# ============================================================
# SECTION 8: C668 Target Comparison & Verdict
# ============================================================
print("\n" + "=" * 60)
print("SECTION 8: C668 Target Comparison & Verdict")
print("=" * 60)

# C668 targets
target_overall_rho = -0.058
target_strongest = 'REGIME_2'
target_flat = 'REGIME_4'

print(f"C668 target overall rho: {target_overall_rho:.3f}")
print(f"  Actual overall rho: {overall_rho:.4f}")
print(f"  Delta: {abs(overall_rho - target_overall_rho):.4f}")

# Check REGIME_2 strongest drift
regime_drift_magnitudes = {r: abs(rr['spearman_rho']) for r, rr in regime_results.items()
                           if not np.isnan(rr['spearman_rho'])}
if regime_drift_magnitudes:
    strongest_regime = max(regime_drift_magnitudes, key=regime_drift_magnitudes.get)
    print(f"\nStrongest drift regime: {strongest_regime} (|rho|={regime_drift_magnitudes[strongest_regime]:.4f})")
    print(f"  Target: {target_strongest}")
    strongest_match = strongest_regime == target_strongest

# Check REGIME_4 flatness
if 'REGIME_4' in regime_results:
    r4_delta = regime_results['REGIME_4']['delta_QO']
    r4_flat = abs(r4_delta) < 0.01
    print(f"\nREGIME_4 delta_QO: {r4_delta:.6f}")
    print(f"  Flat (|delta| < 0.01): {'YES' if r4_flat else 'NO'}")

# Verdict: is drift significant enough to include in model?
drift_significant = overall_p < SIGNIFICANCE_THRESHOLD
drift_verdict = 'INCLUDE' if drift_significant else 'EXCLUDE'
print(f"\nDrift verdict: {drift_verdict}")
print(f"  Overall rho significant (p < {SIGNIFICANCE_THRESHOLD}): {drift_significant}")
print(f"  Drift type: {overall_classification}")

# ============================================================
# SECTION 9: Save Results
# ============================================================
print("\n" + "=" * 60)
print("SECTION 9: Save Results")
print("=" * 60)

results = {
    'test': 'T5_folio_drift_estimation',
    'description': 'Within-folio temporal drift in lane balance (QO fraction across quartiles)',

    'overall': {
        'n_folios': len(folio_quartile_data),
        'n_observations': len(all_q_overall),
        'spearman_rho': float(overall_rho),
        'spearman_p': float(overall_p),
        'linear_slope': float(overall_slope),
        'linear_intercept': float(overall_intercept),
    },

    'overall_partial_correlation': {
        'partial_rho': float(overall_partial_rho),
        'partial_p': float(overall_partial_p),
        'controlling_for': 'EN_density',
        'method': 'residual_regression_then_spearman',
    },

    'drift_classification': {
        'overall': overall_classification,
        'per_regime': per_regime_classification,
        'criteria': {
            'significance_threshold': SIGNIFICANCE_THRESHOLD,
            'partial_near_zero_threshold': PARTIAL_NEAR_ZERO,
            'logic': 'intrinsic if raw rho significant AND partial rho significant and not near zero; '
                     'density_emergent if raw rho significant but partial rho near zero or insignificant; '
                     'no_significant_drift if raw rho not significant',
        },
    },

    'per_regime': {},
    'per_folio_drift': per_folio_drift,

    'c668_comparison': {
        'target_overall_rho': target_overall_rho,
        'actual_overall_rho': float(overall_rho),
        'delta': float(abs(overall_rho - target_overall_rho)),
        'target_strongest_regime': target_strongest,
        'actual_strongest_regime': strongest_regime if regime_drift_magnitudes else None,
        'strongest_match': bool(strongest_match) if regime_drift_magnitudes else False,
        'target_flat_regime': target_flat,
        'regime_4_delta_QO': float(regime_results['REGIME_4']['delta_QO']) if 'REGIME_4' in regime_results else None,
        'regime_4_flat': bool(r4_flat) if 'REGIME_4' in regime_results else None,
    },

    'verdict': {
        'drift_significant': bool(drift_significant),
        'drift_type': overall_classification,
        'model_recommendation': drift_verdict,
        'rationale': (
            f"Overall Spearman rho = {float(overall_rho):.4f} (p = {float(overall_p):.6f}). "
            f"Drift classified as {overall_classification}. "
            f"{'Include drift parameter in model.' if drift_significant else 'Drift too weak to model.'}"
        ),
    },
}

# Add per-regime results with serialization-safe values
for regime in sorted(regime_results.keys()):
    rr = regime_results[regime]
    results['per_regime'][regime] = {
        'n_folios': int(rr['n_folios']),
        'n_observations': int(rr['n_observations']),
        'mean_qo_per_quartile': {
            k: float(v) if v is not None else None
            for k, v in rr['mean_qo_per_quartile'].items()
        },
        'mean_en_density_per_quartile': {
            k: float(v) if v is not None else None
            for k, v in rr['mean_en_density_per_quartile'].items()
        },
        'delta_QO': float(rr['delta_QO']),
        'spearman_rho': float(rr['spearman_rho']),
        'spearman_p': float(rr['spearman_p']),
        'partial_rho_controlling_en_density': float(rr['partial_rho_controlling_en_density']),
        'partial_p_controlling_en_density': float(rr['partial_p_controlling_en_density']),
        'drift_classification': per_regime_classification[regime],
    }

out_path = RESULTS_DIR / 't5_folio_drift.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {out_path}")

print(f"\nT5 VERDICT: drift_significant={drift_significant}, type={overall_classification}, recommendation={drift_verdict}")
