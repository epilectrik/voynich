"""
SISTER_PAIR_CHOICE_DYNAMICS - Script 1: B MIDDLE Sister Preference

Characterize which MIDDLEs prefer ch vs sh (and ok vs ot) in Currier B.
B equivalent of C410.a (A-side: MIDDLE primary predictor, 25.4% deviation).

Sections:
  1. Per-MIDDLE ch/sh ratio in B
  2. Per-MIDDLE ok/ot ratio in B
  3. Folio-level MIDDLE composition score
  4. Cross-system A vs B MIDDLE preference comparison

Output: results/middle_sister_preference.json
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats as sp_stats

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# =============================================================================
# JSON encoder
# =============================================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# =============================================================================
# Constants
# =============================================================================

MIN_TOKENS = 5  # Minimum ch+sh per MIDDLE (matching C410.a)
MIN_FOLIO_TOKENS = 5  # Minimum ch+sh per folio (matching C412)

CH_SH = {'ch', 'sh'}
OK_OT = {'ok', 'ot'}

# =============================================================================
# Load data
# =============================================================================

print("Loading data...")
tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())
a_tokens = list(tx.currier_a())
print(f"  Currier B tokens: {len(b_tokens)}")
print(f"  Currier A tokens: {len(a_tokens)}")

# =============================================================================
# Helper: extract prefix and middle from tokens
# =============================================================================

def extract_prefix_middle(tokens, prefix_set):
    """Extract (middle, prefix, folio) tuples for tokens with prefix in prefix_set."""
    results = []
    for t in tokens:
        word = t.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.prefix and m.prefix in prefix_set and m.middle:
            results.append((m.middle, m.prefix, t.folio))
    return results

# =============================================================================
# Section 1: Per-MIDDLE ch/sh Ratio in B
# =============================================================================

print("\n=== Section 1: Per-MIDDLE ch/sh Ratio in B ===")

b_ch_sh = extract_prefix_middle(b_tokens, CH_SH)
print(f"  Total B ch+sh tokens: {len(b_ch_sh)}")

# Count per MIDDLE
middle_ch_sh = defaultdict(Counter)
for middle, prefix, folio in b_ch_sh:
    middle_ch_sh[middle][prefix] += 1

# Filter and compute ratios
b_ch_sh_ratios = []
for middle in sorted(middle_ch_sh.keys()):
    counts = middle_ch_sh[middle]
    total = counts['ch'] + counts['sh']
    if total >= MIN_TOKENS:
        ch_ratio = counts['ch'] / total
        b_ch_sh_ratios.append({
            'middle': middle,
            'ch': counts['ch'],
            'sh': counts['sh'],
            'total': total,
            'ch_ratio': round(ch_ratio, 4)
        })

b_ch_sh_ratios.sort(key=lambda x: -x['ch_ratio'])

# Summary
n_gt90_ch = sum(1 for r in b_ch_sh_ratios if r['ch_ratio'] > 0.90)
n_gt90_sh = sum(1 for r in b_ch_sh_ratios if r['ch_ratio'] < 0.10)
n_balanced = sum(1 for r in b_ch_sh_ratios if 0.40 <= r['ch_ratio'] <= 0.60)

# Global ch_preference (weighted)
global_ch = sum(r['ch'] for r in b_ch_sh_ratios)
global_sh = sum(r['sh'] for r in b_ch_sh_ratios)
global_ch_pref = global_ch / (global_ch + global_sh) if (global_ch + global_sh) > 0 else 0

print(f"  MIDDLEs meeting threshold (>={MIN_TOKENS}): {len(b_ch_sh_ratios)}")
print(f"  Global ch_preference: {global_ch_pref:.3f} (ch={global_ch}, sh={global_sh})")
print(f"  >90% ch: {n_gt90_ch}")
print(f"  >90% sh: {n_gt90_sh}")
print(f"  Balanced (40-60%): {n_balanced}")

# Top ch-preferring and sh-preferring
print(f"\n  Top 10 ch-preferring MIDDLEs:")
for r in b_ch_sh_ratios[:10]:
    print(f"    {r['middle']:>12}: ch={r['ch']:>4}, sh={r['sh']:>4}, total={r['total']:>4}, ch_ratio={r['ch_ratio']:.3f}")

print(f"\n  Top 10 sh-preferring MIDDLEs:")
for r in b_ch_sh_ratios[-10:]:
    print(f"    {r['middle']:>12}: ch={r['ch']:>4}, sh={r['sh']:>4}, total={r['total']:>4}, ch_ratio={r['ch_ratio']:.3f}")

# Deviation from global: how much do MIDDLE preferences deviate from global mean?
deviations = [abs(r['ch_ratio'] - global_ch_pref) for r in b_ch_sh_ratios]
mean_deviation = np.mean(deviations)
weighted_deviation = np.average(deviations, weights=[r['total'] for r in b_ch_sh_ratios])
print(f"\n  Mean absolute deviation from global: {mean_deviation:.3f}")
print(f"  Weighted mean deviation: {weighted_deviation:.3f}")
print(f"  (C410.a A-side deviation was 0.254)")

# =============================================================================
# Section 2: Per-MIDDLE ok/ot Ratio in B
# =============================================================================

print("\n=== Section 2: Per-MIDDLE ok/ot Ratio in B ===")

b_ok_ot = extract_prefix_middle(b_tokens, OK_OT)
print(f"  Total B ok+ot tokens: {len(b_ok_ot)}")

middle_ok_ot = defaultdict(Counter)
for middle, prefix, folio in b_ok_ot:
    middle_ok_ot[middle][prefix] += 1

b_ok_ot_ratios = []
for middle in sorted(middle_ok_ot.keys()):
    counts = middle_ok_ot[middle]
    total = counts['ok'] + counts['ot']
    if total >= MIN_TOKENS:
        ok_ratio = counts['ok'] / total
        b_ok_ot_ratios.append({
            'middle': middle,
            'ok': counts['ok'],
            'ot': counts['ot'],
            'total': total,
            'ok_ratio': round(ok_ratio, 4)
        })

b_ok_ot_ratios.sort(key=lambda x: -x['ok_ratio'])

n_gt90_ok = sum(1 for r in b_ok_ot_ratios if r['ok_ratio'] > 0.90)
n_gt90_ot = sum(1 for r in b_ok_ot_ratios if r['ok_ratio'] < 0.10)
n_balanced_okot = sum(1 for r in b_ok_ot_ratios if 0.40 <= r['ok_ratio'] <= 0.60)

global_ok = sum(r['ok'] for r in b_ok_ot_ratios)
global_ot = sum(r['ot'] for r in b_ok_ot_ratios)
global_ok_pref = global_ok / (global_ok + global_ot) if (global_ok + global_ot) > 0 else 0

print(f"  MIDDLEs meeting threshold: {len(b_ok_ot_ratios)}")
print(f"  Global ok_preference: {global_ok_pref:.3f} (ok={global_ok}, ot={global_ot})")
print(f"  >90% ok: {n_gt90_ok}")
print(f"  >90% ot: {n_gt90_ot}")
print(f"  Balanced (40-60%): {n_balanced_okot}")

print(f"\n  Top 5 ok-preferring MIDDLEs:")
for r in b_ok_ot_ratios[:5]:
    print(f"    {r['middle']:>12}: ok={r['ok']:>4}, ot={r['ot']:>4}, ok_ratio={r['ok_ratio']:.3f}")

print(f"\n  Top 5 ot-preferring MIDDLEs:")
for r in b_ok_ot_ratios[-5:]:
    print(f"    {r['middle']:>12}: ok={r['ok']:>4}, ot={r['ot']:>4}, ok_ratio={r['ok_ratio']:.3f}")

ok_deviations = [abs(r['ok_ratio'] - global_ok_pref) for r in b_ok_ot_ratios]
mean_ok_dev = np.mean(ok_deviations) if ok_deviations else 0
print(f"\n  Mean absolute deviation: {mean_ok_dev:.3f}")

# =============================================================================
# Section 3: Folio-Level MIDDLE Composition Score
# =============================================================================

print("\n=== Section 3: Folio-Level MIDDLE Composition Score ===")

# Build lookup: MIDDLE -> ch_ratio (from Section 1)
middle_weight = {}
for r in b_ch_sh_ratios:
    middle_weight[r['middle']] = r['ch_ratio']

# Build per-folio: predicted ch_preference from MIDDLE composition
folio_ch_sh = defaultdict(lambda: {'ch': 0, 'sh': 0, 'weighted_sum': 0.0, 'weight_total': 0})
for middle, prefix, folio in b_ch_sh:
    folio_ch_sh[folio][prefix] += 1
    # Use per-MIDDLE weight if available, else global
    w = middle_weight.get(middle, global_ch_pref)
    folio_ch_sh[folio]['weighted_sum'] += w
    folio_ch_sh[folio]['weight_total'] += 1

folio_scores = []
for folio in sorted(folio_ch_sh.keys()):
    data = folio_ch_sh[folio]
    total = data['ch'] + data['sh']
    if total < MIN_FOLIO_TOKENS:
        continue

    actual = data['ch'] / total
    predicted = data['weighted_sum'] / data['weight_total'] if data['weight_total'] > 0 else global_ch_pref

    folio_scores.append({
        'folio': folio,
        'actual_ch_pref': round(actual, 4),
        'predicted_ch_pref': round(predicted, 4),
        'n_tokens': total
    })

# Spearman correlation
actual_vals = [f['actual_ch_pref'] for f in folio_scores]
predicted_vals = [f['predicted_ch_pref'] for f in folio_scores]

rho, p_val = sp_stats.spearmanr(actual_vals, predicted_vals)

# R-squared from rank regression
actual_rank = sp_stats.rankdata(actual_vals)
predicted_rank = sp_stats.rankdata(predicted_vals)
ss_tot = np.sum((actual_rank - np.mean(actual_rank))**2)
X = np.column_stack([predicted_rank, np.ones(len(predicted_rank))])
beta, _, _, _ = np.linalg.lstsq(X, actual_rank, rcond=None)
resid = actual_rank - X @ beta
ss_res = np.sum(resid**2)
r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

print(f"  Folios with >={MIN_FOLIO_TOKENS} ch+sh: {len(folio_scores)}")
print(f"  Spearman rho (predicted vs actual): {rho:.4f}")
print(f"  p-value: {p_val:.6f}")
print(f"  R-squared (rank-based): {r_squared:.4f}")
print(f"  -> MIDDLE composition explains {r_squared*100:.1f}% of folio-level ch_preference variance")

# Residual analysis
residuals = [f['actual_ch_pref'] - f['predicted_ch_pref'] for f in folio_scores]
print(f"\n  Prediction residuals: mean={np.mean(residuals):.4f}, std={np.std(residuals):.4f}")
print(f"  Max over-predicted (actual << predicted): {min(residuals):.4f}")
print(f"  Max under-predicted (actual >> predicted): {max(residuals):.4f}")

# =============================================================================
# Section 4: Cross-System A vs B MIDDLE Preference Comparison
# =============================================================================

print("\n=== Section 4: Cross-System A vs B MIDDLE Preference ===")

# Compute A-side MIDDLE ch/sh ratios
a_ch_sh = extract_prefix_middle(a_tokens, CH_SH)
print(f"  Total A ch+sh tokens: {len(a_ch_sh)}")

a_middle_ch_sh = defaultdict(Counter)
for middle, prefix, folio in a_ch_sh:
    a_middle_ch_sh[middle][prefix] += 1

a_ch_sh_ratios = {}
for middle in sorted(a_middle_ch_sh.keys()):
    counts = a_middle_ch_sh[middle]
    total = counts['ch'] + counts['sh']
    if total >= MIN_TOKENS:
        a_ch_sh_ratios[middle] = {
            'ch': counts['ch'],
            'sh': counts['sh'],
            'total': total,
            'ch_ratio': round(counts['ch'] / total, 4)
        }

# Find shared MIDDLEs
b_ratio_dict = {r['middle']: r['ch_ratio'] for r in b_ch_sh_ratios}
shared_middles = sorted(set(a_ch_sh_ratios.keys()) & set(b_ratio_dict.keys()))

print(f"  A MIDDLEs meeting threshold: {len(a_ch_sh_ratios)}")
print(f"  B MIDDLEs meeting threshold: {len(b_ch_sh_ratios)}")
print(f"  Shared MIDDLEs (both A and B): {len(shared_middles)}")

if len(shared_middles) >= 3:
    a_vals = [a_ch_sh_ratios[m]['ch_ratio'] for m in shared_middles]
    b_vals = [b_ratio_dict[m] for m in shared_middles]

    cross_rho, cross_p = sp_stats.spearmanr(a_vals, b_vals)
    print(f"\n  Cross-system Spearman rho: {cross_rho:.4f}")
    print(f"  p-value: {cross_p:.6f}")
    print(f"  -> MIDDLE preferences {'ARE' if cross_p < 0.05 else 'are NOT'} correlated across A and B")

    # Check C410.a top MIDDLEs
    c410a_middles = ['yk', 'okch', 'l', 'et', 's']
    print(f"\n  C410.a top ch-preferring MIDDLEs (A-side):")
    for m in c410a_middles:
        a_info = a_ch_sh_ratios.get(m, {})
        b_info = b_ratio_dict.get(m)
        a_str = f"ch_ratio={a_info.get('ch_ratio', 'N/A')}" if a_info else "below threshold"
        b_str = f"ch_ratio={b_info}" if b_info is not None else "below threshold"
        print(f"    {m:>6}: A={a_str}, B={b_str}")
else:
    cross_rho, cross_p = 0, 1.0
    print("  Insufficient shared MIDDLEs for cross-system comparison")

# =============================================================================
# Output JSON
# =============================================================================

output = {
    'metadata': {
        'phase': 'SISTER_PAIR_CHOICE_DYNAMICS',
        'script': 'middle_sister_preference.py',
        'description': 'B MIDDLE-level sister pair preferences',
        'min_tokens_per_middle': MIN_TOKENS,
        'min_tokens_per_folio': MIN_FOLIO_TOKENS
    },
    'b_ch_sh_preferences': {
        'n_middles': len(b_ch_sh_ratios),
        'n_tokens': len(b_ch_sh),
        'global_ch_preference': round(global_ch_pref, 4),
        'mean_deviation': round(float(mean_deviation), 4),
        'weighted_deviation': round(float(weighted_deviation), 4),
        'gt90_ch': n_gt90_ch,
        'gt90_sh': n_gt90_sh,
        'balanced_40_60': n_balanced,
        'per_middle': b_ch_sh_ratios
    },
    'b_ok_ot_preferences': {
        'n_middles': len(b_ok_ot_ratios),
        'n_tokens': len(b_ok_ot),
        'global_ok_preference': round(global_ok_pref, 4),
        'mean_deviation': round(float(mean_ok_dev), 4),
        'gt90_ok': n_gt90_ok,
        'gt90_ot': n_gt90_ot,
        'balanced_40_60': n_balanced_okot,
        'per_middle': b_ok_ot_ratios
    },
    'folio_composition_score': {
        'n_folios': len(folio_scores),
        'spearman_rho': round(float(rho), 4),
        'p_value': round(float(p_val), 6),
        'r_squared': round(float(r_squared), 4),
        'per_folio': folio_scores
    },
    'cross_system_comparison': {
        'n_shared_middles': len(shared_middles),
        'spearman_rho': round(float(cross_rho), 4),
        'p_value': round(float(cross_p), 6),
        'shared_middles': [
            {'middle': m, 'a_ch_ratio': a_ch_sh_ratios[m]['ch_ratio'], 'b_ch_ratio': b_ratio_dict[m]}
            for m in shared_middles
        ]
    }
}

output_path = Path(__file__).parent.parent / 'results' / 'middle_sister_preference.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

print(f"\nOutput: {output_path}")
print("Done.")
