#!/usr/bin/env python3
"""
Test 3: Monitoring Orthogonality (LINK vs Kernel Contact)

Tests whether monitoring intensity (LINK) and kernel engagement
(kernel contact rate) are independent dimensions.
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

# Load class map
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_map = json.load(f)

token_to_class = {token: int(cls) for token, cls in class_map['token_to_class'].items()}
token_to_role = class_map.get('token_to_role', {})

# Key classes
LINK_CLASS = 29
FQ_CLASSES = {9, 13, 14, 23}
KERNEL_CHARS = {'k', 'h', 'e'}

# Build token sets
link_tokens = set(t for t, c in token_to_class.items() if c == LINK_CLASS)
fq_tokens = set(t for t, c in token_to_class.items() if c in FQ_CLASSES)

def has_kernel(word):
    return any(c in KERNEL_CHARS for c in word)

# Load REGIME mapping
with open(Path(__file__).parent.parent.parent.parent / 'results' / 'regime_folio_mapping.json') as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    regime_num = int(regime.replace('REGIME_', ''))
    for folio in folios:
        folio_regime[folio] = regime_num

# Load transcript
tx = Transcript()

print("="*70)
print("TEST 3: MONITORING ORTHOGONALITY")
print("="*70)

# Compute per-folio metrics
folio_stats = defaultdict(lambda: {'total': 0, 'link': 0, 'fq': 0, 'kernel_contact': 0})

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio = token.folio
    word = token.word

    folio_stats[folio]['total'] += 1

    if word in link_tokens:
        folio_stats[folio]['link'] += 1
    if word in fq_tokens:
        folio_stats[folio]['fq'] += 1
    if has_kernel(word):
        folio_stats[folio]['kernel_contact'] += 1

# Build data arrays
folio_data = []
for folio in sorted(folio_stats.keys()):
    s = folio_stats[folio]
    if s['total'] < 50:
        continue

    link_rate = s['link'] / s['total']
    fq_rate = s['fq'] / s['total']
    kernel_rate = s['kernel_contact'] / s['total']

    folio_data.append({
        'folio': folio,
        'regime': folio_regime.get(folio),
        'link_rate': link_rate,
        'fq_rate': fq_rate,
        'kernel_rate': kernel_rate,
        'total': s['total']
    })

print(f"\nFolios analyzed: {len(folio_data)}")

# Extract arrays
link_rates = np.array([d['link_rate'] for d in folio_data])
fq_rates = np.array([d['fq_rate'] for d in folio_data])
kernel_rates = np.array([d['kernel_rate'] for d in folio_data])

# Pairwise correlations
print(f"\n{'='*70}")
print("PAIRWISE CORRELATIONS")
print("='*70")

correlations = {}

# LINK vs Kernel
r_link_kernel, p_link_kernel = scipy_stats.spearmanr(link_rates, kernel_rates)
correlations['LINK_vs_Kernel'] = {'rho': float(r_link_kernel), 'p': float(p_link_kernel)}
print(f"\nLINK vs Kernel Contact: rho={r_link_kernel:.3f}, p={p_link_kernel:.4f}")

# LINK vs FQ
r_link_fq, p_link_fq = scipy_stats.spearmanr(link_rates, fq_rates)
correlations['LINK_vs_FQ'] = {'rho': float(r_link_fq), 'p': float(p_link_fq)}
print(f"LINK vs FQ (escape): rho={r_link_fq:.3f}, p={p_link_fq:.4f}")

# Kernel vs FQ
r_kernel_fq, p_kernel_fq = scipy_stats.spearmanr(kernel_rates, fq_rates)
correlations['Kernel_vs_FQ'] = {'rho': float(r_kernel_fq), 'p': float(p_kernel_fq)}
print(f"Kernel vs FQ (escape): rho={r_kernel_fq:.3f}, p={p_kernel_fq:.4f}")

# Interpretation
print(f"\n{'='*70}")
print("INTERPRETATION")
print("="*70)

orthogonal_pairs = []
for name, stats in correlations.items():
    if abs(stats['rho']) < 0.3:
        orthogonal_pairs.append(name)
        print(f"  {name}: ORTHOGONAL (|rho| < 0.3)")
    elif stats['rho'] > 0.3:
        print(f"  {name}: ALIGNED (rho > 0.3)")
    else:
        print(f"  {name}: INVERSE (rho < -0.3)")

# By REGIME
print(f"\n{'='*70}")
print("BY REGIME")
print("="*70)

for regime in sorted(set(d['regime'] for d in folio_data if d['regime'])):
    regime_folios = [d for d in folio_data if d['regime'] == regime]
    mean_link = np.mean([d['link_rate'] for d in regime_folios])
    mean_fq = np.mean([d['fq_rate'] for d in regime_folios])
    mean_kernel = np.mean([d['kernel_rate'] for d in regime_folios])
    print(f"  R{regime}: LINK={mean_link:.3f}, FQ={mean_fq:.3f}, Kernel={mean_kernel:.3f}")

# Verdict
if len(orthogonal_pairs) >= 1:
    verdict = "SUPPORT"
    print(f"\n** Orthogonality found: {orthogonal_pairs} **")
else:
    verdict = "NOT SUPPORTED"
    print(f"\nNo orthogonal pairs found")

# Save results
output = {
    'test': 'Monitoring Orthogonality',
    'n_folios': len(folio_data),
    'correlations': correlations,
    'orthogonal_pairs': orthogonal_pairs,
    'verdict': verdict,
    'summary': {
        'mean_link': float(np.mean(link_rates)),
        'mean_fq': float(np.mean(fq_rates)),
        'mean_kernel': float(np.mean(kernel_rates))
    }
}

output_path = results_dir / 'monitoring_orthogonality.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\nVERDICT: {verdict}")
