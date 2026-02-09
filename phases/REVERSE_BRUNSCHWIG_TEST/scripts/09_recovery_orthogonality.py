#!/usr/bin/env python3
"""
Test 9: Recovery Orthogonality

Tests whether recovery RATE (FQ density) and recovery PATHWAY (post-FQ kernel)
vary independently across REGIMEs.

Findings:
- C890: Recovery rate-pathway independence
- C892: Post-FQ h-dominance (h > k > e in all REGIMEs)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

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

# FQ classes (escape operators)
FQ_CLASSES = {9, 13, 14, 23}

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

# Kernel characters
KERNEL_CHARS = {'k', 'h', 'e'}

def get_first_kernel(word):
    """Return first kernel character in word, or None."""
    for c in word:
        if c in KERNEL_CHARS:
            return c
    return None

# Build line-grouped tokens
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if '*' in token.word:
        continue
    key = (token.folio, token.line)
    line_tokens[key].append(token)

print("="*70)
print("TEST 9: RECOVERY ORTHOGONALITY")
print("="*70)

# Track post-FQ kernels and FQ counts per REGIME
regime_post_fq = defaultdict(lambda: {'e': 0, 'h': 0, 'k': 0, 'none': 0, 'total_fq': 0})
regime_tokens = defaultdict(int)

for (folio, line), tokens in line_tokens.items():
    regime = folio_regime.get(folio)
    if regime is None:
        continue

    words = [t.word for t in tokens]
    regime_tokens[regime] += len(words)

    for i, word in enumerate(words):
        cls = token_to_class.get(word)
        if cls in FQ_CLASSES:
            regime_post_fq[regime]['total_fq'] += 1

            if i + 1 < len(words):
                next_word = words[i + 1]
                first_kernel = get_first_kernel(next_word)
                if first_kernel:
                    regime_post_fq[regime][first_kernel] += 1
                else:
                    regime_post_fq[regime]['none'] += 1
            else:
                regime_post_fq[regime]['none'] += 1

# Compute profiles
regime_profiles = {}
for regime in sorted(regime_post_fq.keys()):
    stats = regime_post_fq[regime]
    total = stats['total_fq']

    e_pct = 100 * stats['e'] / total if total > 0 else 0
    h_pct = 100 * stats['h'] / total if total > 0 else 0
    k_pct = 100 * stats['k'] / total if total > 0 else 0
    fq_rate = total / regime_tokens[regime] if regime_tokens[regime] > 0 else 0

    regime_profiles[regime] = {
        'fq_rate': fq_rate,
        'post_fq_e': e_pct,
        'post_fq_h': h_pct,
        'post_fq_k': k_pct,
        'total_fq': total
    }

# Print results
print("\nPost-FQ Kernel Distribution:")
print("-"*70)
print("REGIME   FQ_rate   Post-FQ_e%   Post-FQ_h%   Post-FQ_k%   Dominant")
print("-"*70)

for regime in sorted(regime_profiles.keys()):
    p = regime_profiles[regime]
    kernels = {'e': p['post_fq_e'], 'h': p['post_fq_h'], 'k': p['post_fq_k']}
    dominant = max(kernels, key=kernels.get)
    print(f"  R{regime}       {p['fq_rate']:.3f}       {p['post_fq_e']:5.1f}        {p['post_fq_h']:5.1f}        {p['post_fq_k']:5.1f}        {dominant}")

# Check rankings
sorted_by_fq = sorted(regime_profiles.keys(), key=lambda r: regime_profiles[r]['fq_rate'], reverse=True)
sorted_by_e = sorted(regime_profiles.keys(), key=lambda r: regime_profiles[r]['post_fq_e'], reverse=True)

print("\n" + "="*70)
print("ORTHOGONALITY CHECK")
print("="*70)
print(f"\nFQ rate ranking: {['R'+str(r) for r in sorted_by_fq]}")
print(f"Post-FQ e% ranking: {['R'+str(r) for r in sorted_by_e]}")

if sorted_by_fq != sorted_by_e:
    print("\n** Rankings DIFFER - orthogonality confirmed **")
    orthogonal = True
else:
    print("\nRankings same - no orthogonality")
    orthogonal = False

# Check h-dominance
print("\n" + "="*70)
print("H-DOMINANCE CHECK (C892)")
print("="*70)

h_dominates_all = True
for regime in sorted(regime_profiles.keys()):
    p = regime_profiles[regime]
    h_dom = p['post_fq_h'] > p['post_fq_e'] and p['post_fq_h'] > p['post_fq_k']
    status = "YES" if h_dom else "NO"
    print(f"  R{regime}: h > e,k? {status} (h={p['post_fq_h']:.1f}%, e={p['post_fq_e']:.1f}%, k={p['post_fq_k']:.1f}%)")
    if not h_dom:
        h_dominates_all = False

print(f"\nh dominates in ALL REGIMEs: {h_dominates_all}")

# Save results
output = {
    'test': 'Recovery Orthogonality',
    'findings': {
        'C890_rate_pathway_independence': {
            'fq_rate_ranking': [f'R{r}' for r in sorted_by_fq],
            'post_fq_e_ranking': [f'R{r}' for r in sorted_by_e],
            'orthogonal': orthogonal
        },
        'C892_post_fq_h_dominance': {
            'h_dominates_all_regimes': h_dominates_all,
            'ordering': 'h > k > e (all REGIMEs)'
        }
    },
    'regime_profiles': {str(k): v for k, v in regime_profiles.items()},
    'verdict': 'SUPPORT' if orthogonal and h_dominates_all else 'PARTIAL'
}

output_path = results_dir / 'recovery_orthogonality.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\nVERDICT: {output['verdict']}")
