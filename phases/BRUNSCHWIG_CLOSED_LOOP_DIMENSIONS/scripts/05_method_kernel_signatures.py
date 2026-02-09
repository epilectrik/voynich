#!/usr/bin/env python3
"""
Test 5: Method Signatures - Kernel Patterns by Distillation Method

Tests whether different fire degrees (as method proxies) have distinct
kernel patterns (k:h:e ratios).
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# Load REGIME mapping
with open(Path(__file__).parent.parent.parent.parent / 'results' / 'regime_folio_mapping.json') as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    regime_num = int(regime.replace('REGIME_', ''))
    for folio in folios:
        folio_regime[folio] = regime_num

# Fire degree mapping (from BRSC)
FIRE_DEGREE = {1: 2, 2: 1, 3: 3, 4: 4}  # REGIME -> fire degree

# Load transcript
tx = Transcript()

KERNEL_CHARS = {'k', 'h', 'e'}

def get_kernel_counts(word):
    counts = {'k': 0, 'h': 0, 'e': 0}
    for c in word:
        if c in counts:
            counts[c] += 1
    return counts

print("="*70)
print("TEST 5: METHOD-KERNEL SIGNATURES")
print("="*70)

# Compute kernel proportions per folio
folio_kernels = defaultdict(lambda: {'k': 0, 'h': 0, 'e': 0, 'total': 0})

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio = token.folio
    word = token.word

    counts = get_kernel_counts(word)
    for k, v in counts.items():
        folio_kernels[folio][k] += v
    folio_kernels[folio]['total'] += sum(counts.values())

# Build data by fire degree
fire_data = defaultdict(list)

for folio, kernels in folio_kernels.items():
    regime = folio_regime.get(folio)
    if regime is None:
        continue

    fire = FIRE_DEGREE.get(regime, 2)
    total = kernels['total']
    if total < 50:
        continue

    k_ratio = kernels['k'] / total
    h_ratio = kernels['h'] / total
    e_ratio = kernels['e'] / total

    fire_data[fire].append({
        'folio': folio,
        'regime': regime,
        'k_ratio': k_ratio,
        'h_ratio': h_ratio,
        'e_ratio': e_ratio,
        'total_kernels': total
    })

print(f"\nFolios by fire degree:")
for fire in sorted(fire_data.keys()):
    print(f"  Fire {fire}: {len(fire_data[fire])} folios")

# Compute mean kernel ratios by fire degree
print(f"\n{'='*70}")
print("KERNEL PROPORTIONS BY FIRE DEGREE")
print("="*70)

fire_profiles = {}
print(f"\nFire   k%       h%       e%       k:h:e")
print("-"*50)

for fire in sorted(fire_data.keys()):
    folios = fire_data[fire]
    mean_k = np.mean([f['k_ratio'] for f in folios])
    mean_h = np.mean([f['h_ratio'] for f in folios])
    mean_e = np.mean([f['e_ratio'] for f in folios])

    fire_profiles[fire] = {'k': mean_k, 'h': mean_h, 'e': mean_e}

    # Normalize to k:h:e ratio
    total = mean_k + mean_h + mean_e
    if total > 0:
        k_norm = mean_k / total
        h_norm = mean_h / total
        e_norm = mean_e / total
        ratio = f"{k_norm:.2f}:{h_norm:.2f}:{e_norm:.2f}"
    else:
        ratio = "N/A"

    print(f"  {fire}     {100*mean_k:.1f}%    {100*mean_h:.1f}%    {100*mean_e:.1f}%    {ratio}")

# Statistical test: Kruskal-Wallis for each kernel across fire degrees
print(f"\n{'='*70}")
print("KRUSKAL-WALLIS TEST (Kernel ~ Fire Degree)")
print("="*70)

kw_results = {}
for kernel in ['k', 'h', 'e']:
    groups = [
        [f[f'{kernel}_ratio'] for f in fire_data[fire]]
        for fire in sorted(fire_data.keys())
        if len(fire_data[fire]) >= 3
    ]

    if len(groups) >= 2 and all(len(g) >= 2 for g in groups):
        h_stat, p_val = scipy_stats.kruskal(*groups)
        kw_results[kernel] = {'H': float(h_stat), 'p': float(p_val)}
        sig = "**" if p_val < 0.05 else ""
        print(f"  {kernel}: H={h_stat:.2f}, p={p_val:.4f} {sig}")
    else:
        kw_results[kernel] = {'H': None, 'p': None}
        print(f"  {kernel}: insufficient groups")

# Interpretation
print(f"\n{'='*70}")
print("INTERPRETATION")
print("="*70)

significant = [k for k, v in kw_results.items() if v['p'] and v['p'] < 0.05]
if significant:
    print(f"\nKernel(s) varying significantly by fire degree: {significant}")

    # Direction analysis
    for kernel in significant:
        fire_1 = np.mean([f[f'{kernel}_ratio'] for f in fire_data.get(1, [])] or [0])
        fire_3 = np.mean([f[f'{kernel}_ratio'] for f in fire_data.get(3, [])] or [0])
        direction = "increases" if fire_3 > fire_1 else "decreases"
        print(f"  {kernel} {direction} with fire degree ({100*fire_1:.1f}% at fire 1 -> {100*fire_3:.1f}% at fire 3)")

    verdict = "SUPPORT"
else:
    print(f"\nNo kernels vary significantly by fire degree")
    verdict = "NOT SUPPORTED"

# Expected patterns check
print(f"\n{'='*70}")
print("EXPECTED PATTERNS CHECK")
print("="*70)
print("\nBrunschwig hypothesis:")
print("  - Gentle (fire 1): More h (monitoring), less k")
print("  - Intense (fire 3): More k (energy), less h")

if fire_profiles.get(1) and fire_profiles.get(3):
    f1, f3 = fire_profiles[1], fire_profiles[3]
    print(f"\nActual:")
    print(f"  Fire 1: k={100*f1['k']:.1f}%, h={100*f1['h']:.1f}%")
    print(f"  Fire 3: k={100*f3['k']:.1f}%, h={100*f3['h']:.1f}%")

    if f3['k'] > f1['k'] and f1['h'] > f3['h']:
        print(f"\n  ** Pattern MATCHES Brunschwig hypothesis **")
        pattern_match = True
    else:
        print(f"\n  Pattern does NOT match hypothesis")
        pattern_match = False
else:
    pattern_match = False

# Save results
output = {
    'test': 'Method-Kernel Signatures',
    'fire_degree_mapping': FIRE_DEGREE,
    'n_folios_by_fire': {str(k): len(v) for k, v in fire_data.items()},
    'fire_profiles': {str(k): v for k, v in fire_profiles.items()},
    'kruskal_wallis': kw_results,
    'significant_kernels': significant,
    'pattern_match': pattern_match,
    'verdict': verdict
}

output_path = results_dir / 'method_kernel_signatures.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\nVERDICT: {verdict}")
