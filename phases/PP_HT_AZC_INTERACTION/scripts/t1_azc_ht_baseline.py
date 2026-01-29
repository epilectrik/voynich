"""
T1: AZC Mediation vs HT Density Baseline

Question: Does AZC mediation level correlate with HT density?

C765 established that B folios have 54.5%-94.9% AZC-mediated vocabulary.
C746 established that HT density varies by folio (15.5%-47.2%).

If AZC modulates the PP-HT trade-off, we expect:
- High AZC-mediation folios to have different HT density than low AZC-mediation
- The correlation to be independent of vocabulary size effects

Tests:
1. Compute AZC-mediation % per B folio (replicate C765 T1)
2. Compute HT density per B folio (replicate C746)
3. Correlate AZC-mediation with HT density
4. Partial correlation controlling for vocabulary size
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

print("=" * 70)
print("T1: AZC MEDIATION vs HT DENSITY")
print("=" * 70)

# Collect AZC vocabulary (all MIDDLEs across all AZC folios)
azc_middles = set()
for token in tx.azc():
    m = morph.extract(token.word)
    if m.middle:
        azc_middles.add(m.middle)

print(f"\nAZC total unique MIDDLEs: {len(azc_middles)}")

# Collect B data per folio
b_data = defaultdict(lambda: {
    'total_tokens': 0,
    'ht_tokens': 0,
    'middles': set(),
    'azc_mediated_middles': set(),
})

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

    if m.middle:
        b_data[folio]['middles'].add(m.middle)
        if m.middle in azc_middles:
            b_data[folio]['azc_mediated_middles'].add(m.middle)

# Compute metrics per folio
results = []
for folio in sorted(b_data.keys()):
    d = b_data[folio]

    total_middles = len(d['middles'])
    azc_med_middles = len(d['azc_mediated_middles'])

    if total_middles == 0 or d['total_tokens'] == 0:
        continue

    azc_pct = 100 * azc_med_middles / total_middles
    ht_pct = 100 * d['ht_tokens'] / d['total_tokens']

    results.append({
        'folio': folio,
        'total_tokens': d['total_tokens'],
        'total_middles': total_middles,
        'azc_mediated_middles': azc_med_middles,
        'azc_pct': azc_pct,
        'ht_tokens': d['ht_tokens'],
        'ht_pct': ht_pct,
    })

print(f"\nB folios analyzed: {len(results)}")

# Extract arrays for correlation
azc_pcts = np.array([r['azc_pct'] for r in results])
ht_pcts = np.array([r['ht_pct'] for r in results])
vocab_sizes = np.array([r['total_middles'] for r in results])
token_counts = np.array([r['total_tokens'] for r in results])

print("\n" + "=" * 70)
print("DESCRIPTIVE STATISTICS")
print("=" * 70)

print(f"\nAZC Mediation %:")
print(f"  Mean: {np.mean(azc_pcts):.1f}%")
print(f"  Min: {np.min(azc_pcts):.1f}%")
print(f"  Max: {np.max(azc_pcts):.1f}%")
print(f"  Std: {np.std(azc_pcts):.1f}%")

print(f"\nHT Density %:")
print(f"  Mean: {np.mean(ht_pcts):.1f}%")
print(f"  Min: {np.min(ht_pcts):.1f}%")
print(f"  Max: {np.max(ht_pcts):.1f}%")
print(f"  Std: {np.std(ht_pcts):.1f}%")

# T1: Raw correlation
print("\n" + "=" * 70)
print("T1: AZC MEDIATION vs HT DENSITY CORRELATION")
print("=" * 70)

rho, pval = stats.spearmanr(azc_pcts, ht_pcts)
print(f"\nSpearman correlation: rho = {rho:.3f}, p = {pval:.4f}")

pearson_r, pearson_p = stats.pearsonr(azc_pcts, ht_pcts)
print(f"Pearson correlation: r = {pearson_r:.3f}, p = {pearson_p:.4f}")

if pval < 0.05:
    direction = "POSITIVE" if rho > 0 else "NEGATIVE"
    print(f"\n** SIGNIFICANT {direction} CORRELATION **")
    print(f"   Higher AZC mediation {'increases' if rho > 0 else 'decreases'} HT density")
else:
    print(f"\n   No significant correlation (p = {pval:.4f})")

# T2: Partial correlation controlling for vocabulary size
print("\n" + "=" * 70)
print("T2: PARTIAL CORRELATION (controlling for vocab size)")
print("=" * 70)

# Residualize both variables on vocab size
def partial_correlation(x, y, z):
    """Compute partial correlation of x and y controlling for z."""
    # Residualize x on z
    slope_xz, intercept_xz, _, _, _ = stats.linregress(z, x)
    x_resid = x - (slope_xz * z + intercept_xz)

    # Residualize y on z
    slope_yz, intercept_yz, _, _, _ = stats.linregress(z, y)
    y_resid = y - (slope_yz * z + intercept_yz)

    # Correlate residuals
    return stats.spearmanr(x_resid, y_resid)

partial_rho, partial_p = partial_correlation(azc_pcts, ht_pcts, vocab_sizes)
print(f"\nPartial Spearman (controlling vocab size): rho = {partial_rho:.3f}, p = {partial_p:.4f}")

# Also control for token count
partial_rho2, partial_p2 = partial_correlation(azc_pcts, ht_pcts, token_counts)
print(f"Partial Spearman (controlling token count): rho = {partial_rho2:.3f}, p = {partial_p2:.4f}")

# T3: Tertile analysis
print("\n" + "=" * 70)
print("T3: TERTILE ANALYSIS")
print("=" * 70)

# Split into low/medium/high AZC mediation
sorted_by_azc = sorted(results, key=lambda r: r['azc_pct'])
n = len(sorted_by_azc)
tertile_size = n // 3

low_azc = sorted_by_azc[:tertile_size]
med_azc = sorted_by_azc[tertile_size:2*tertile_size]
high_azc = sorted_by_azc[2*tertile_size:]

print(f"\nLow AZC tertile (n={len(low_azc)}):")
print(f"  AZC range: {min(r['azc_pct'] for r in low_azc):.1f}% - {max(r['azc_pct'] for r in low_azc):.1f}%")
print(f"  Mean HT: {np.mean([r['ht_pct'] for r in low_azc]):.1f}%")

print(f"\nMedium AZC tertile (n={len(med_azc)}):")
print(f"  AZC range: {min(r['azc_pct'] for r in med_azc):.1f}% - {max(r['azc_pct'] for r in med_azc):.1f}%")
print(f"  Mean HT: {np.mean([r['ht_pct'] for r in med_azc]):.1f}%")

print(f"\nHigh AZC tertile (n={len(high_azc)}):")
print(f"  AZC range: {min(r['azc_pct'] for r in high_azc):.1f}% - {max(r['azc_pct'] for r in high_azc):.1f}%")
print(f"  Mean HT: {np.mean([r['ht_pct'] for r in high_azc]):.1f}%")

# Kruskal-Wallis test
low_ht = [r['ht_pct'] for r in low_azc]
med_ht = [r['ht_pct'] for r in med_azc]
high_ht = [r['ht_pct'] for r in high_azc]

kw_stat, kw_p = stats.kruskal(low_ht, med_ht, high_ht)
print(f"\nKruskal-Wallis test: H = {kw_stat:.2f}, p = {kw_p:.4f}")

# Effect size: difference between high and low tertile
ht_diff = np.mean(high_ht) - np.mean(low_ht)
print(f"\nHigh-Low HT difference: {ht_diff:+.1f} percentage points")

# Save results
output = {
    'n_folios': len(results),
    'azc_mediation': {
        'mean': float(np.mean(azc_pcts)),
        'std': float(np.std(azc_pcts)),
        'min': float(np.min(azc_pcts)),
        'max': float(np.max(azc_pcts)),
    },
    'ht_density': {
        'mean': float(np.mean(ht_pcts)),
        'std': float(np.std(ht_pcts)),
        'min': float(np.min(ht_pcts)),
        'max': float(np.max(ht_pcts)),
    },
    'correlations': {
        'spearman_rho': float(rho),
        'spearman_p': float(pval),
        'pearson_r': float(pearson_r),
        'pearson_p': float(pearson_p),
        'partial_rho_vocab': float(partial_rho),
        'partial_p_vocab': float(partial_p),
    },
    'tertile_analysis': {
        'low_azc_mean_ht': float(np.mean(low_ht)),
        'med_azc_mean_ht': float(np.mean(med_ht)),
        'high_azc_mean_ht': float(np.mean(high_ht)),
        'kruskal_wallis_H': float(kw_stat),
        'kruskal_wallis_p': float(kw_p),
        'high_low_diff': float(ht_diff),
    },
    'per_folio': results,
}

output_path = PROJECT_ROOT / 'phases' / 'PP_HT_AZC_INTERACTION' / 'results' / 't1_azc_ht_baseline.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=True)
print(f"\nResults saved to: {output_path}")

print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

if pval < 0.05 and abs(rho) > 0.2:
    if rho > 0:
        print(f"""
AZC mediation and HT density are POSITIVELY CORRELATED (rho={rho:.3f}).
Higher AZC mediation -> higher HT density.

This suggests:
- AZC-mediated vocabulary correlates with more HT tokens
- The PP-HT trade-off is modulated by AZC involvement
""")
    else:
        print(f"""
AZC mediation and HT density are NEGATIVELY CORRELATED (rho={rho:.3f}).
Higher AZC mediation -> lower HT density.

This suggests:
- AZC-mediated vocabulary "crowds out" HT
- PP vocabulary from AZC reduces need for HT padding
""")
elif pval >= 0.05:
    print(f"""
NO SIGNIFICANT CORRELATION between AZC mediation and HT density.
(rho={rho:.3f}, p={pval:.4f})

This suggests:
- AZC involvement and HT density are independent dimensions
- The PP-HT trade-off is NOT modulated by AZC at the folio level
""")
