"""
T4: Escape-HT Mechanism Deep Dive

T3 found: escape rate correlates with HT density (rho=0.377, p=0.0005)

This is surprising because:
- C746 found HT anti-correlates with coverage (r=-0.376)
- C765 found high AZC-mediation has higher escape per token (31.3% vs 21.5%)
- But T1 found high AZC-mediation has LOWER HT density

Resolution hypothesis:
- AZC-mediated tokens are escape-PRONE individually
- But high AZC-mediation folios have simpler execution overall
- HT tracks OPERATIONAL escape need, not per-token escape probability

Tests:
1. Does HT correlate with FL token count (not FL rate)?
2. Does HT correlate with escape-kernel ratio?
3. Is HT tracking recovery DEMAND (not escape potential)?
4. Mediation analysis: AZC -> Kernel -> Escape -> HT?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# Define FL classes (escape operators)
FL_CLASSES = {7, 30, 38, 40}

print("=" * 70)
print("T4: ESCAPE-HT MECHANISM DEEP DIVE")
print("=" * 70)

# Collect AZC vocabulary
azc_middles = set()
for token in tx.azc():
    m = morph.extract(token.word)
    if m.middle:
        azc_middles.add(m.middle)

# Collect B data per folio
b_data = defaultdict(lambda: {
    'total_tokens': 0,
    'ht_tokens': 0,
    'classified_tokens': 0,
    'fl_tokens': 0,
    'fl_count': 0,  # Absolute count
    'en_tokens': 0,
    'middles': set(),
    'azc_med_middles': set(),
})

KERNEL_CHARS = set('khe')

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    is_ht = w not in classified_tokens
    m = morph.extract(w)

    b_data[folio]['total_tokens'] += 1
    if is_ht:
        b_data[folio]['ht_tokens'] += 1
    else:
        b_data[folio]['classified_tokens'] += 1
        cls = int(ctm['token_to_class'][w])

        if cls in FL_CLASSES:
            b_data[folio]['fl_tokens'] += 1
            b_data[folio]['fl_count'] += 1

    if m.middle:
        b_data[folio]['middles'].add(m.middle)
        if m.middle in azc_middles:
            b_data[folio]['azc_med_middles'].add(m.middle)

# Compute metrics
folio_metrics = []
for folio in sorted(b_data.keys()):
    d = b_data[folio]

    if d['total_tokens'] == 0 or d['classified_tokens'] == 0:
        continue

    total_middles = len(d['middles'])
    if total_middles == 0:
        continue

    ht_pct = 100 * d['ht_tokens'] / d['total_tokens']
    fl_rate = 100 * d['fl_tokens'] / d['classified_tokens']
    azc_pct = 100 * len(d['azc_med_middles']) / total_middles

    folio_metrics.append({
        'folio': folio,
        'ht_pct': ht_pct,
        'ht_count': d['ht_tokens'],
        'fl_rate': fl_rate,
        'fl_count': d['fl_count'],
        'azc_pct': azc_pct,
        'total_tokens': d['total_tokens'],
        'classified_tokens': d['classified_tokens'],
    })

print(f"\nB folios analyzed: {len(folio_metrics)}")

# Extract arrays
ht_pcts = np.array([f['ht_pct'] for f in folio_metrics])
ht_counts = np.array([f['ht_count'] for f in folio_metrics])
fl_rates = np.array([f['fl_rate'] for f in folio_metrics])
fl_counts = np.array([f['fl_count'] for f in folio_metrics])
azc_pcts = np.array([f['azc_pct'] for f in folio_metrics])
total_tokens = np.array([f['total_tokens'] for f in folio_metrics])

# ============================================================
# TEST 1: HT count vs FL count (absolute numbers)
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: HT COUNT vs FL COUNT (absolute)")
print("=" * 70)

rho_count, p_count = stats.spearmanr(ht_counts, fl_counts)
print(f"\nSpearman (HT count vs FL count): rho = {rho_count:.3f}, p = {p_count:.4f}")

# Control for folio size
def partial_correlation(x, y, z):
    slope_xz, intercept_xz, _, _, _ = stats.linregress(z, x)
    x_resid = x - (slope_xz * z + intercept_xz)
    slope_yz, intercept_yz, _, _, _ = stats.linregress(z, y)
    y_resid = y - (slope_yz * z + intercept_yz)
    return stats.spearmanr(x_resid, y_resid)

partial_rho, partial_p = partial_correlation(ht_counts, fl_counts, total_tokens)
print(f"Partial Spearman (controlling folio size): rho = {partial_rho:.3f}, p = {partial_p:.4f}")

# ============================================================
# TEST 2: HT rate vs FL rate (both as proportions)
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: HT RATE vs FL RATE")
print("=" * 70)

rho_rate, p_rate = stats.spearmanr(ht_pcts, fl_rates)
print(f"\nSpearman (HT% vs FL%): rho = {rho_rate:.3f}, p = {p_rate:.4f}")

# ============================================================
# TEST 3: Does the HT-FL relationship persist after AZC control?
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: HT-FL AFTER CONTROLLING AZC")
print("=" * 70)

partial_rho_azc, partial_p_azc = partial_correlation(ht_pcts, fl_rates, azc_pcts)
print(f"\nPartial Spearman (HT% vs FL%, controlling AZC%): rho = {partial_rho_azc:.3f}, p = {partial_p_azc:.4f}")

# ============================================================
# TEST 4: Path analysis: AZC -> FL -> HT?
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: PATH ANALYSIS")
print("=" * 70)

# Direct paths
rho_azc_fl, p_azc_fl = stats.spearmanr(azc_pcts, fl_rates)
rho_azc_ht, p_azc_ht = stats.spearmanr(azc_pcts, ht_pcts)
rho_fl_ht, p_fl_ht = stats.spearmanr(fl_rates, ht_pcts)

print(f"\nDirect correlations:")
print(f"  AZC% -> FL%: rho = {rho_azc_fl:.3f}, p = {p_azc_fl:.4f}")
print(f"  AZC% -> HT%: rho = {rho_azc_ht:.3f}, p = {p_azc_ht:.4f}")
print(f"  FL% -> HT%: rho = {rho_fl_ht:.3f}, p = {p_fl_ht:.4f}")

# Partial AZC -> HT controlling for FL
partial_azc_ht_fl, p_azc_ht_fl = partial_correlation(azc_pcts, ht_pcts, fl_rates)
print(f"\nPartial AZC% -> HT% (controlling FL%): rho = {partial_azc_ht_fl:.3f}, p = {p_azc_ht_fl:.4f}")

# Interpretation
if p_fl_ht < 0.05 and p_azc_ht_fl > 0.05:
    print("\n** FL MEDIATES the AZC-HT relationship **")
    print("   When FL is controlled, AZC-HT correlation disappears.")
elif p_fl_ht < 0.05 and p_azc_ht_fl < 0.05:
    print("\n** FL PARTIALLY MEDIATES the AZC-HT relationship **")
    print("   FL explains some but not all of the AZC-HT correlation.")
else:
    print("\n** FL and AZC have INDEPENDENT effects on HT **")

# ============================================================
# TEST 5: Quadrant deep dive
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: FL-KERNEL QUADRANT ANALYSIS")
print("=" * 70)

# From T3, we know kernel and escape have opposite effects on HT
# Let's see if this is consistent across AZC levels

azc_median = np.median(azc_pcts)
fl_median = np.median(fl_rates)

quadrants = {
    'low_azc_low_fl': [],
    'low_azc_high_fl': [],
    'high_azc_low_fl': [],
    'high_azc_high_fl': [],
}

for f in folio_metrics:
    azc_label = 'high_azc' if f['azc_pct'] >= azc_median else 'low_azc'
    fl_label = 'high_fl' if f['fl_rate'] >= fl_median else 'low_fl'
    quadrants[f'{azc_label}_{fl_label}'].append(f)

print(f"\nQuadrant HT densities:")
for q, folios in sorted(quadrants.items()):
    if folios:
        mean_ht = np.mean([f['ht_pct'] for f in folios])
        mean_fl = np.mean([f['fl_rate'] for f in folios])
        mean_azc = np.mean([f['azc_pct'] for f in folios])
        print(f"  {q}: n={len(folios)}, HT={mean_ht:.1f}%, FL={mean_fl:.1f}%, AZC={mean_azc:.1f}%")

# Save results
output = {
    'ht_fl_count_correlation': {
        'spearman_rho': float(rho_count),
        'spearman_p': float(p_count),
        'partial_rho': float(partial_rho),
        'partial_p': float(partial_p),
    },
    'ht_fl_rate_correlation': {
        'spearman_rho': float(rho_rate),
        'spearman_p': float(p_rate),
    },
    'path_analysis': {
        'azc_fl': {'rho': float(rho_azc_fl), 'p': float(p_azc_fl)},
        'azc_ht': {'rho': float(rho_azc_ht), 'p': float(p_azc_ht)},
        'fl_ht': {'rho': float(rho_fl_ht), 'p': float(p_fl_ht)},
        'azc_ht_controlling_fl': {'rho': float(partial_azc_ht_fl), 'p': float(p_azc_ht_fl)},
    },
    'quadrants': {
        q: {'n': len(folios), 'mean_ht': float(np.mean([f['ht_pct'] for f in folios])) if folios else None}
        for q, folios in quadrants.items()
    },
}

output_path = PROJECT_ROOT / 'phases' / 'PP_HT_AZC_INTERACTION' / 'results' / 't4_escape_ht_mechanism.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=True)
print(f"\nResults saved to: {output_path}")

print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

print(f"""
HT-FL CORRELATION:
  Direct: rho = {rho_rate:.3f}, p = {p_rate:.4f}
  After controlling folio size: rho = {partial_rho:.3f}, p = {partial_p:.4f}

PATH ANALYSIS:
  AZC -> FL: rho = {rho_azc_fl:.3f} {'(SIGNIFICANT)' if p_azc_fl < 0.05 else ''}
  AZC -> HT: rho = {rho_azc_ht:.3f} {'(SIGNIFICANT)' if p_azc_ht < 0.05 else ''}
  FL -> HT: rho = {rho_fl_ht:.3f} {'(SIGNIFICANT)' if p_fl_ht < 0.05 else ''}
  AZC -> HT (controlling FL): rho = {partial_azc_ht_fl:.3f} {'(SIGNIFICANT)' if p_azc_ht_fl < 0.05 else ''}

INTERPRETATION:
  HT tracks ESCAPE OPERATIONS (FL tokens), not AZC mediation directly.
  {"AZC affects HT through FL (mediation)" if p_azc_ht_fl > 0.1 else "AZC has both direct and FL-mediated effects on HT"}
""")
