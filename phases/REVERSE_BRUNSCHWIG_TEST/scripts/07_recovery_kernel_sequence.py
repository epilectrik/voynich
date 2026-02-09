#!/usr/bin/env python3
"""
Test: Does e→h→k kernel ordering dominate in RECOVERY contexts?

Hypothesis: Brunschwig's "verify→align→heat" (e→h→k) appears specifically
after escape (FQ) events, not throughout lines. In closed-loop control,
recovery should follow the stabilization protocol.

Method:
1. Find all FQ tokens in B
2. Extract kernel sequence in the tokens FOLLOWING FQ (same line)
3. Compare e→h→k rate in post-FQ context vs baseline (13.6%)
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# Load class map for FQ identification
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_map = json.load(f)

# The JSON has nested structure - use token_to_class directly
token_to_class = {token: int(cls) for token, cls in class_map['token_to_class'].items()}

# FQ classes (from C587)
FQ_CLASSES = {9, 13, 14, 23}

# Load transcript
tx = Transcript()

# Build line-grouped tokens for B
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if '*' in token.word:
        continue
    key = (token.folio, token.line)
    line_tokens[key].append(token)

print("="*70)
print("RECOVERY KERNEL SEQUENCE TEST")
print("="*70)
print(f"Total lines: {len(line_tokens)}")

# Functions
def get_kernels(word):
    """Extract kernel characters (e, h, k) in order from a word."""
    kernels = []
    for char in str(word):
        if char in 'ehk':
            kernels.append(char)
    return kernels

def get_ordering(kernels):
    """Get the ordering pattern from a list of kernel chars."""
    unique = []
    for k in kernels:
        if k not in unique:
            unique.append(k)
    return '->'.join(unique)

# Process lines
results = {
    'post_fq_sequences': [],
    'non_post_fq_sequences': [],
    'post_fq_orderings': Counter(),
    'non_post_fq_orderings': Counter(),
}

lines_with_fq = 0
lines_without_fq = 0

for (folio, line), tokens in line_tokens.items():
    words = [t.word for t in tokens]
    classes = [token_to_class.get(t.word) for t in tokens]

    # Find FQ positions
    fq_positions = [i for i, c in enumerate(classes) if c in FQ_CLASSES]

    if not fq_positions:
        lines_without_fq += 1
        # No FQ in this line - all tokens are non-post-FQ context
        all_kernels = []
        for word in words:
            all_kernels.extend(get_kernels(word))
        if len(set(all_kernels)) >= 2:  # At least 2 different kernels
            ordering = get_ordering(all_kernels)
            results['non_post_fq_orderings'][ordering] += 1
            results['non_post_fq_sequences'].append(all_kernels)
    else:
        lines_with_fq += 1
        # Line has FQ - split into pre-FQ and post-FQ
        last_fq = max(fq_positions)

        # Post-FQ tokens (everything after last FQ)
        post_fq_words = words[last_fq + 1:]
        if post_fq_words:
            post_kernels = []
            for word in post_fq_words:
                post_kernels.extend(get_kernels(word))
            if len(set(post_kernels)) >= 2:
                ordering = get_ordering(post_kernels)
                results['post_fq_orderings'][ordering] += 1
                results['post_fq_sequences'].append(post_kernels)

        # Pre-FQ tokens (everything before first FQ) - control
        first_fq = min(fq_positions)
        pre_fq_words = words[:first_fq]
        if pre_fq_words:
            pre_kernels = []
            for word in pre_fq_words:
                pre_kernels.extend(get_kernels(word))
            if len(set(pre_kernels)) >= 2:
                ordering = get_ordering(pre_kernels)
                results['non_post_fq_orderings'][ordering] += 1
                results['non_post_fq_sequences'].append(pre_kernels)

print(f"Lines with FQ: {lines_with_fq}")
print(f"Lines without FQ: {lines_without_fq}")

# Calculate e→h→k rates
def ehk_rate(orderings):
    """Calculate rate of e→h→k orderings among lines with all three kernels."""
    # For orderings with all three kernels
    all_three = ['e->h->k', 'e->k->h', 'h->e->k', 'h->k->e', 'k->e->h', 'k->h->e']
    total_all_three = sum(orderings.get(o, 0) for o in all_three)
    ehk_count = orderings.get('e->h->k', 0)
    return ehk_count, total_all_three

post_fq_ehk, post_fq_total = ehk_rate(results['post_fq_orderings'])
non_post_fq_ehk, non_post_fq_total = ehk_rate(results['non_post_fq_orderings'])

post_fq_rate = post_fq_ehk / post_fq_total if post_fq_total > 0 else 0
non_post_fq_rate = non_post_fq_ehk / non_post_fq_total if non_post_fq_total > 0 else 0

print(f"\nPost-FQ: {post_fq_ehk}/{post_fq_total} = {post_fq_rate:.1%} e->h->k")
print(f"Non-post-FQ: {non_post_fq_ehk}/{non_post_fq_total} = {non_post_fq_rate:.1%} e->h->k")

# Statistical test
contingency = [
    [post_fq_ehk, post_fq_total - post_fq_ehk],
    [non_post_fq_ehk, non_post_fq_total - non_post_fq_ehk]
]

# Use Fisher's exact for small counts
if post_fq_total < 30 or non_post_fq_total < 30:
    _, p_value = stats.fisher_exact(contingency)
    test_type = 'fisher'
else:
    chi2, p_value, _, _ = stats.chi2_contingency([contingency[0], contingency[1]])
    test_type = 'chi2'

# Also check e-first rate (does e appear before h and before k?)
def e_first_rate(sequences):
    """Rate at which e appears before h and before k."""
    e_before_h = 0
    e_before_k = 0
    h_present = 0
    k_present = 0

    for seq in sequences:
        if 'e' in seq and 'h' in seq:
            h_present += 1
            if seq.index('e') < seq.index('h'):
                e_before_h += 1
        if 'e' in seq and 'k' in seq:
            k_present += 1
            if seq.index('e') < seq.index('k'):
                e_before_k += 1

    return {
        'e_before_h': e_before_h / h_present if h_present > 0 else 0,
        'e_before_k': e_before_k / k_present if k_present > 0 else 0,
        'e_before_h_count': e_before_h,
        'e_before_k_count': e_before_k,
        'h_present': h_present,
        'k_present': k_present
    }

post_fq_e_first = e_first_rate(results['post_fq_sequences'])
non_post_fq_e_first = e_first_rate(results['non_post_fq_sequences'])

print(f"\nE-before-H rate: post-FQ {post_fq_e_first['e_before_h']:.1%} vs non-post-FQ {non_post_fq_e_first['e_before_h']:.1%}")
print(f"E-before-K rate: post-FQ {post_fq_e_first['e_before_k']:.1%} vs non-post-FQ {non_post_fq_e_first['e_before_k']:.1%}")

# Determine verdict
if p_value < 0.05 and post_fq_rate > non_post_fq_rate:
    verdict = 'SUPPORT - e->h->k enriched in recovery contexts'
elif p_value < 0.05 and post_fq_rate < non_post_fq_rate:
    verdict = 'CONTRADICT - e->h->k depleted in recovery contexts'
else:
    verdict = 'NEUTRAL - no significant difference'

print(f"\np-value: {p_value:.6f}")
print(f"VERDICT: {verdict}")

# Output
output = {
    'hypothesis': 'e->h->k ordering enriched in post-FQ (recovery) contexts',
    'baseline_ehk_rate': 0.136,  # From REVERSE_BRUNSCHWIG
    'post_fq': {
        'total_sequences': len(results['post_fq_sequences']),
        'sequences_with_all_three': post_fq_total,
        'ehk_count': post_fq_ehk,
        'ehk_rate': round(post_fq_rate, 4),
        'orderings': dict(results['post_fq_orderings'].most_common(10)),
        'e_before_h_rate': round(post_fq_e_first['e_before_h'], 4),
        'e_before_k_rate': round(post_fq_e_first['e_before_k'], 4),
    },
    'non_post_fq': {
        'total_sequences': len(results['non_post_fq_sequences']),
        'sequences_with_all_three': non_post_fq_total,
        'ehk_count': non_post_fq_ehk,
        'ehk_rate': round(non_post_fq_rate, 4),
        'orderings': dict(results['non_post_fq_orderings'].most_common(10)),
        'e_before_h_rate': round(non_post_fq_e_first['e_before_h'], 4),
        'e_before_k_rate': round(non_post_fq_e_first['e_before_k'], 4),
    },
    'comparison': {
        'ehk_rate_ratio': round(post_fq_rate / non_post_fq_rate, 3) if non_post_fq_rate > 0 else None,
        'test_type': test_type,
        'p_value': round(float(p_value), 6),
        'significant': bool(p_value < 0.05),
    },
    'e_first_comparison': {
        'post_fq_e_before_h': round(post_fq_e_first['e_before_h'], 4),
        'non_post_fq_e_before_h': round(non_post_fq_e_first['e_before_h'], 4),
        'post_fq_e_before_k': round(post_fq_e_first['e_before_k'], 4),
        'non_post_fq_e_before_k': round(non_post_fq_e_first['e_before_k'], 4),
    },
    'verdict': verdict
}

# Save results
output_path = results_dir / 'recovery_kernel_sequence.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
