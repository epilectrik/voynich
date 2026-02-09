#!/usr/bin/env python3
"""
Test 2: Folio-Level Post-FQ h-Dominance Verification

Confirms that h dominates post-FQ at folio level, not just REGIME aggregates.
C892 claims h (24-36%) > e (3-8%) in all REGIMEs.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np

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

# FQ classes
FQ_CLASSES = {9, 13, 14, 23}
KERNEL_CHARS = {'k', 'h', 'e'}

def get_first_kernel(word):
    for c in word:
        if c in KERNEL_CHARS:
            return c
    return None

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
print("TEST 2: FOLIO-LEVEL POST-FQ H-DOMINANCE")
print("="*70)

# Build line-grouped tokens
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if '*' in token.word:
        continue
    key = (token.folio, token.line)
    line_tokens[key].append(token)

# Compute post-FQ kernel distribution per folio
folio_post_fq = defaultdict(lambda: {'e': 0, 'h': 0, 'k': 0, 'total_fq': 0})

for (folio, line), tokens in line_tokens.items():
    words = [t.word for t in tokens]

    for i, word in enumerate(words):
        cls = token_to_class.get(word)
        if cls in FQ_CLASSES:
            folio_post_fq[folio]['total_fq'] += 1

            if i + 1 < len(words):
                next_word = words[i + 1]
                first_kernel = get_first_kernel(next_word)
                if first_kernel:
                    folio_post_fq[folio][first_kernel] += 1

# Analyze folios with sufficient FQ events
MIN_FQ = 10  # Minimum FQ events to include folio

folio_results = []
h_dominates_count = 0
e_dominates_count = 0
k_dominates_count = 0

for folio in sorted(folio_post_fq.keys()):
    stats = folio_post_fq[folio]
    if stats['total_fq'] < MIN_FQ:
        continue

    total_kernel = stats['e'] + stats['h'] + stats['k']
    if total_kernel == 0:
        continue

    e_pct = 100 * stats['e'] / total_kernel
    h_pct = 100 * stats['h'] / total_kernel
    k_pct = 100 * stats['k'] / total_kernel

    dominant = max(['e', 'h', 'k'], key=lambda x: stats[x])
    if dominant == 'h':
        h_dominates_count += 1
    elif dominant == 'e':
        e_dominates_count += 1
    else:
        k_dominates_count += 1

    folio_results.append({
        'folio': folio,
        'regime': folio_regime.get(folio),
        'total_fq': stats['total_fq'],
        'e_pct': e_pct,
        'h_pct': h_pct,
        'k_pct': k_pct,
        'dominant': dominant,
        'h_gt_e': stats['h'] > stats['e']
    })

print(f"\nFolios analyzed: {len(folio_results)} (with {MIN_FQ}+ FQ events)")

# Summary statistics
h_gt_e_count = sum(1 for r in folio_results if r['h_gt_e'])
h_gt_e_pct = 100 * h_gt_e_count / len(folio_results) if folio_results else 0

print(f"\n{'='*70}")
print("H-DOMINANCE STATISTICS")
print("="*70)
print(f"\nFolios where h > e: {h_gt_e_count}/{len(folio_results)} ({h_gt_e_pct:.1f}%)")
print(f"\nDominant kernel distribution:")
print(f"  h dominates: {h_dominates_count} folios ({100*h_dominates_count/len(folio_results):.1f}%)")
print(f"  k dominates: {k_dominates_count} folios ({100*k_dominates_count/len(folio_results):.1f}%)")
print(f"  e dominates: {e_dominates_count} folios ({100*e_dominates_count/len(folio_results):.1f}%)")

# Mean percentages
mean_h = np.mean([r['h_pct'] for r in folio_results])
mean_e = np.mean([r['e_pct'] for r in folio_results])
mean_k = np.mean([r['k_pct'] for r in folio_results])

print(f"\nMean post-FQ kernel percentages:")
print(f"  h: {mean_h:.1f}%")
print(f"  k: {mean_k:.1f}%")
print(f"  e: {mean_e:.1f}%")

# Breakdown by REGIME
print(f"\n{'='*70}")
print("BY REGIME")
print("="*70)

for regime in sorted(set(r['regime'] for r in folio_results if r['regime'])):
    regime_folios = [r for r in folio_results if r['regime'] == regime]
    h_gt_e = sum(1 for r in regime_folios if r['h_gt_e'])
    mean_h_r = np.mean([r['h_pct'] for r in regime_folios])
    mean_e_r = np.mean([r['e_pct'] for r in regime_folios])
    print(f"  R{regime}: {h_gt_e}/{len(regime_folios)} h>e, mean_h={mean_h_r:.1f}%, mean_e={mean_e_r:.1f}%")

# Verdict
if h_gt_e_pct >= 75:
    verdict = "CONFIRMED"
    print(f"\n** FOLIO-LEVEL CONFIRMS C892 (h>e in {h_gt_e_pct:.0f}% of folios) **")
elif h_gt_e_pct >= 60:
    verdict = "PARTIAL"
    print(f"\nPartial confirmation (h>e in {h_gt_e_pct:.0f}% of folios)")
else:
    verdict = "NOT CONFIRMED"
    print(f"\nFolio-level does not confirm C892")

# Save results
output = {
    'test': 'Folio-Level Post-FQ h-Dominance',
    'min_fq_threshold': MIN_FQ,
    'n_folios': len(folio_results),
    'h_gt_e_count': h_gt_e_count,
    'h_gt_e_pct': h_gt_e_pct,
    'dominant_distribution': {
        'h_dominates': h_dominates_count,
        'k_dominates': k_dominates_count,
        'e_dominates': e_dominates_count
    },
    'mean_percentages': {
        'h': float(mean_h),
        'k': float(mean_k),
        'e': float(mean_e)
    },
    'verdict': verdict,
    'folio_results': folio_results
}

output_path = results_dir / 'folio_post_fq_h.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\nVERDICT: {verdict}")
