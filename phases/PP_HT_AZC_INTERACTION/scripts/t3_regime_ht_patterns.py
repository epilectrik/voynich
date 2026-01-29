"""
T3: REGIME-Specific HT Patterns

C765 established that:
- AZC-mediated vocabulary: high escape (31.3%), low kernel (51.3%)
- B-native vocabulary: low escape (21.5%), high kernel (77.8%)

This creates different execution "regimes":
- High AZC-mediation folios: simpler execution, less kernel depth
- Low AZC-mediation folios: complex execution, more kernel depth

Question: Does HT compensation pattern differ by execution regime?

Hypothesis: If HT signals "operational complexity", then:
- High kernel folios should have different HT patterns than low kernel folios
- Escape rate should interact with HT density
- REGIME may modulate the PP-HT trade-off

Tests:
1. HT density by kernel contact regime (tertile split)
2. HT density by escape rate regime (tertile split)
3. Kernel x Escape interaction on HT
4. Line position HT patterns by regime
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

# Load class to role mapping for kernel identification
class_to_role = {}
# EN classes (kernel operators): {8, 31-37, 39, 41-49}
for c in [8] + list(range(31, 38)) + [39] + list(range(41, 50)):
    class_to_role[str(c)] = 'EN'
# CC classes: {10, 11, 12, 17}
for c in [10, 11, 12, 17]:
    class_to_role[str(c)] = 'CC'
# FL classes: {7, 30, 38, 40}
for c in [7, 30, 38, 40]:
    class_to_role[str(c)] = 'FL'
# FQ classes: {9, 13, 14, 23}
for c in [9, 13, 14, 23]:
    class_to_role[str(c)] = 'FQ'

# Kernel chars
KERNEL_CHARS = set('khe')

print("=" * 70)
print("T3: REGIME-SPECIFIC HT PATTERNS")
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
    'kernel_contact_tokens': 0,  # Tokens with k, h, or e in MIDDLE
    'escape_tokens': 0,  # FL tokens (escape operators)
    'line1_ht': 0,
    'line1_total': 0,
    'body_ht': 0,
    'body_total': 0,
})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = str(token.line)
    is_ht = w not in classified_tokens
    m = morph.extract(w)

    b_data[folio]['total_tokens'] += 1
    if is_ht:
        b_data[folio]['ht_tokens'] += 1

    if line == '1':
        b_data[folio]['line1_total'] += 1
        if is_ht:
            b_data[folio]['line1_ht'] += 1
    else:
        b_data[folio]['body_total'] += 1
        if is_ht:
            b_data[folio]['body_ht'] += 1

    if not is_ht:
        b_data[folio]['classified_tokens'] += 1

        # Check kernel contact
        if m.middle and any(c in m.middle for c in KERNEL_CHARS):
            b_data[folio]['kernel_contact_tokens'] += 1

        # Check if FL (escape)
        if w in ctm['token_to_class']:
            cls = ctm['token_to_class'][w]
            if class_to_role.get(str(cls)) == 'FL':
                b_data[folio]['escape_tokens'] += 1

# Compute per-folio metrics
folio_metrics = []
for folio in sorted(b_data.keys()):
    d = b_data[folio]

    if d['total_tokens'] == 0 or d['classified_tokens'] == 0:
        continue

    ht_pct = 100 * d['ht_tokens'] / d['total_tokens']
    kernel_pct = 100 * d['kernel_contact_tokens'] / d['classified_tokens']
    escape_pct = 100 * d['escape_tokens'] / d['classified_tokens']

    line1_ht_pct = 100 * d['line1_ht'] / d['line1_total'] if d['line1_total'] > 0 else 0
    body_ht_pct = 100 * d['body_ht'] / d['body_total'] if d['body_total'] > 0 else 0

    folio_metrics.append({
        'folio': folio,
        'ht_pct': ht_pct,
        'kernel_pct': kernel_pct,
        'escape_pct': escape_pct,
        'line1_ht_pct': line1_ht_pct,
        'body_ht_pct': body_ht_pct,
        'classified_tokens': d['classified_tokens'],
    })

print(f"\nB folios analyzed: {len(folio_metrics)}")

# Extract arrays
ht_pcts = np.array([f['ht_pct'] for f in folio_metrics])
kernel_pcts = np.array([f['kernel_pct'] for f in folio_metrics])
escape_pcts = np.array([f['escape_pct'] for f in folio_metrics])
line1_ht_pcts = np.array([f['line1_ht_pct'] for f in folio_metrics])
body_ht_pcts = np.array([f['body_ht_pct'] for f in folio_metrics])

print(f"\nDescriptive statistics:")
print(f"  Kernel contact: mean {np.mean(kernel_pcts):.1f}%, range {np.min(kernel_pcts):.1f}-{np.max(kernel_pcts):.1f}%")
print(f"  Escape rate: mean {np.mean(escape_pcts):.1f}%, range {np.min(escape_pcts):.1f}-{np.max(escape_pcts):.1f}%")
print(f"  HT density: mean {np.mean(ht_pcts):.1f}%, range {np.min(ht_pcts):.1f}-{np.max(ht_pcts):.1f}%")

# ============================================================
# TEST 1: HT density by kernel contact regime
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: HT DENSITY BY KERNEL CONTACT REGIME")
print("=" * 70)

sorted_by_kernel = sorted(folio_metrics, key=lambda f: f['kernel_pct'])
n = len(sorted_by_kernel)
t_size = n // 3

low_kernel = sorted_by_kernel[:t_size]
med_kernel = sorted_by_kernel[t_size:2*t_size]
high_kernel = sorted_by_kernel[2*t_size:]

low_k_ht = [f['ht_pct'] for f in low_kernel]
med_k_ht = [f['ht_pct'] for f in med_kernel]
high_k_ht = [f['ht_pct'] for f in high_kernel]

print(f"\nLow kernel tertile: kernel {np.mean([f['kernel_pct'] for f in low_kernel]):.1f}%, HT {np.mean(low_k_ht):.1f}%")
print(f"Medium kernel tertile: kernel {np.mean([f['kernel_pct'] for f in med_kernel]):.1f}%, HT {np.mean(med_k_ht):.1f}%")
print(f"High kernel tertile: kernel {np.mean([f['kernel_pct'] for f in high_kernel]):.1f}%, HT {np.mean(high_k_ht):.1f}%")

kw_k, kw_k_p = stats.kruskal(low_k_ht, med_k_ht, high_k_ht)
print(f"\nKruskal-Wallis: H = {kw_k:.2f}, p = {kw_k_p:.4f}")

rho_kernel_ht, p_kernel_ht = stats.spearmanr(kernel_pcts, ht_pcts)
print(f"Spearman (kernel vs HT): rho = {rho_kernel_ht:.3f}, p = {p_kernel_ht:.4f}")

# ============================================================
# TEST 2: HT density by escape rate regime
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: HT DENSITY BY ESCAPE RATE REGIME")
print("=" * 70)

sorted_by_escape = sorted(folio_metrics, key=lambda f: f['escape_pct'])

low_escape = sorted_by_escape[:t_size]
med_escape = sorted_by_escape[t_size:2*t_size]
high_escape = sorted_by_escape[2*t_size:]

low_e_ht = [f['ht_pct'] for f in low_escape]
med_e_ht = [f['ht_pct'] for f in med_escape]
high_e_ht = [f['ht_pct'] for f in high_escape]

print(f"\nLow escape tertile: escape {np.mean([f['escape_pct'] for f in low_escape]):.1f}%, HT {np.mean(low_e_ht):.1f}%")
print(f"Medium escape tertile: escape {np.mean([f['escape_pct'] for f in med_escape]):.1f}%, HT {np.mean(med_e_ht):.1f}%")
print(f"High escape tertile: escape {np.mean([f['escape_pct'] for f in high_escape]):.1f}%, HT {np.mean(high_e_ht):.1f}%")

kw_e, kw_e_p = stats.kruskal(low_e_ht, med_e_ht, high_e_ht)
print(f"\nKruskal-Wallis: H = {kw_e:.2f}, p = {kw_e_p:.4f}")

rho_escape_ht, p_escape_ht = stats.spearmanr(escape_pcts, ht_pcts)
print(f"Spearman (escape vs HT): rho = {rho_escape_ht:.3f}, p = {p_escape_ht:.4f}")

# ============================================================
# TEST 3: Kernel x Escape interaction on HT
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: KERNEL x ESCAPE INTERACTION")
print("=" * 70)

# Split into 2x2: high/low kernel x high/low escape
kernel_median = np.median(kernel_pcts)
escape_median = np.median(escape_pcts)

quadrants = {
    'low_k_low_e': [],
    'low_k_high_e': [],
    'high_k_low_e': [],
    'high_k_high_e': [],
}

for f in folio_metrics:
    k_label = 'high_k' if f['kernel_pct'] >= kernel_median else 'low_k'
    e_label = 'high_e' if f['escape_pct'] >= escape_median else 'low_e'
    quadrants[f'{k_label}_{e_label}'].append(f)

print(f"\nQuadrant HT densities:")
for q, folios in quadrants.items():
    if folios:
        mean_ht = np.mean([f['ht_pct'] for f in folios])
        print(f"  {q}: n={len(folios)}, mean HT={mean_ht:.1f}%")

# Test for interaction
if all(len(quadrants[q]) >= 5 for q in quadrants):
    # Compare (high_k - low_k) at low_e vs at high_e
    low_k_low_e_ht = np.mean([f['ht_pct'] for f in quadrants['low_k_low_e']])
    high_k_low_e_ht = np.mean([f['ht_pct'] for f in quadrants['high_k_low_e']])
    low_k_high_e_ht = np.mean([f['ht_pct'] for f in quadrants['low_k_high_e']])
    high_k_high_e_ht = np.mean([f['ht_pct'] for f in quadrants['high_k_high_e']])

    kernel_effect_at_low_e = high_k_low_e_ht - low_k_low_e_ht
    kernel_effect_at_high_e = high_k_high_e_ht - low_k_high_e_ht

    print(f"\nKernel effect at low escape: {kernel_effect_at_low_e:+.1f}pp")
    print(f"Kernel effect at high escape: {kernel_effect_at_high_e:+.1f}pp")
    print(f"Interaction (difference of differences): {kernel_effect_at_high_e - kernel_effect_at_low_e:+.1f}pp")

# ============================================================
# TEST 4: Line-1 vs Body HT by regime
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: LINE-1 VS BODY HT BY KERNEL REGIME")
print("=" * 70)

# Does line-1 HT elevation differ by kernel regime?
line1_elevations = line1_ht_pcts - body_ht_pcts

low_k_elevation = [f['line1_ht_pct'] - f['body_ht_pct'] for f in low_kernel]
high_k_elevation = [f['line1_ht_pct'] - f['body_ht_pct'] for f in high_kernel]

print(f"\nLow kernel: mean line-1 elevation = {np.mean(low_k_elevation):+.1f}pp")
print(f"High kernel: mean line-1 elevation = {np.mean(high_k_elevation):+.1f}pp")

mw_stat, mw_p = stats.mannwhitneyu(low_k_elevation, high_k_elevation, alternative='two-sided')
print(f"Mann-Whitney: U = {mw_stat:.0f}, p = {mw_p:.4f}")

# Save results
output = {
    'kernel_ht_correlation': {
        'spearman_rho': float(rho_kernel_ht),
        'spearman_p': float(p_kernel_ht),
        'kruskal_wallis_H': float(kw_k),
        'kruskal_wallis_p': float(kw_k_p),
    },
    'escape_ht_correlation': {
        'spearman_rho': float(rho_escape_ht),
        'spearman_p': float(p_escape_ht),
        'kruskal_wallis_H': float(kw_e),
        'kruskal_wallis_p': float(kw_e_p),
    },
    'quadrant_analysis': {
        q: {'n': len(folios), 'mean_ht': float(np.mean([f['ht_pct'] for f in folios])) if folios else None}
        for q, folios in quadrants.items()
    },
    'line1_elevation_by_kernel': {
        'low_kernel_mean': float(np.mean(low_k_elevation)),
        'high_kernel_mean': float(np.mean(high_k_elevation)),
        'mann_whitney_p': float(mw_p),
    },
}

output_path = PROJECT_ROOT / 'phases' / 'PP_HT_AZC_INTERACTION' / 'results' / 't3_regime_ht_patterns.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=True)
print(f"\nResults saved to: {output_path}")

print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

print(f"""
KERNEL CONTACT vs HT:
  Correlation: rho = {rho_kernel_ht:.3f}, p = {p_kernel_ht:.4f}
  {'SIGNIFICANT' if p_kernel_ht < 0.05 else 'not significant'}
  {'High kernel -> more HT' if rho_kernel_ht > 0 and p_kernel_ht < 0.05 else 'High kernel -> less HT' if rho_kernel_ht < 0 and p_kernel_ht < 0.05 else 'No relationship'}

ESCAPE RATE vs HT:
  Correlation: rho = {rho_escape_ht:.3f}, p = {p_escape_ht:.4f}
  {'SIGNIFICANT' if p_escape_ht < 0.05 else 'not significant'}
  {'High escape -> more HT' if rho_escape_ht > 0 and p_escape_ht < 0.05 else 'High escape -> less HT' if rho_escape_ht < 0 and p_escape_ht < 0.05 else 'No relationship'}

LINE-1 ELEVATION BY KERNEL REGIME:
  Low kernel: {np.mean(low_k_elevation):+.1f}pp elevation
  High kernel: {np.mean(high_k_elevation):+.1f}pp elevation
  Mann-Whitney p = {mw_p:.4f} {'(SIGNIFICANT)' if mw_p < 0.05 else '(not significant)'}
""")
