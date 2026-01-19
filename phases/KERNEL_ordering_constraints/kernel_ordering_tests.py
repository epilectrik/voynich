#!/usr/bin/env python3
"""
DIRECTION G: KERNEL ORDERING CONSTRAINTS

Bounded, non-semantic analysis of kernel primitive ordering.

ALLOWED:
- Test for formal ordering constraints among {k, h, e}
- Measure bigram/trigram patterns
- Check position relative to LINK and hazards

NOT ALLOWED:
- Semantic interpretation
- Mapping to physical processes
- Reopening MONOSTATE or cycles

Tests:
G-1: Kernel Bigram Illegality Test
G-2: Kernel Trigram Collapse Test
G-3: Kernel Position-in-Instruction Analysis

STOP CONDITION: After these three tests, Direction G is CLOSED.
"""

import os
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency, fisher_exact

os.chdir('C:/git/voynich')

print("=" * 70)
print("DIRECTION G: KERNEL ORDERING CONSTRAINTS")
print("Bounded, non-semantic analysis")
print("=" * 70)

# ==========================================================================
# LOAD DATA
# ==========================================================================

print("\nLoading data...")

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # CRITICAL: Filter to H-only transcriber track
        if row.get('transcriber', '') != 'H':
            continue
        all_tokens.append(row)

b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']
all_b_words = [t.get('word', '') for t in b_tokens]

print(f"Currier B tokens: {len(all_b_words)}")

# ==========================================================================
# DEFINE KERNEL CONTACT
# ==========================================================================

# Kernel tokens are those ending in k, h, or e (the three primitives)
# This is the structural definition from the grammar

def get_kernel_class(word):
    """Classify token by kernel contact. Returns 'k', 'h', 'e', or None."""
    if not word:
        return None
    # Check suffix patterns for kernel contact
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'
    # 'e' kernel contact is trickier - only certain patterns
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy'):
        return 'e'
    return None

def is_link(word):
    """Check if token is LINK class (ol-containing)."""
    return 'ol' in word if word else False

# Classify all tokens
kernel_sequence = []
for word in all_b_words:
    k_class = get_kernel_class(word)
    kernel_sequence.append((word, k_class))

# Count kernel tokens
kernel_counts = Counter(k for _, k in kernel_sequence if k is not None)
print(f"\nKernel token counts:")
for k, c in kernel_counts.most_common():
    print(f"  {k}: {c} ({c/len(all_b_words)*100:.1f}%)")

total_kernel = sum(kernel_counts.values())
print(f"  Total kernel contact: {total_kernel} ({total_kernel/len(all_b_words)*100:.1f}%)")

# ==========================================================================
# G-1: KERNEL BIGRAM ILLEGALITY TEST
# ==========================================================================

print("\n" + "=" * 70)
print("G-1: KERNEL BIGRAM ILLEGALITY TEST")
print("Question: Are any ordered pairs among {k, h, e} systematically forbidden?")
print("=" * 70)

# Extract kernel-to-kernel bigrams
kernel_bigrams = Counter()
kernel_positions = []  # Track positions of kernel tokens

for i, (word, k_class) in enumerate(kernel_sequence):
    if k_class is not None:
        kernel_positions.append((i, k_class))

# Build bigrams from consecutive kernel tokens (allowing gaps)
# We look at the NEXT kernel token after each kernel token
for i in range(len(kernel_positions) - 1):
    pos1, k1 = kernel_positions[i]
    pos2, k2 = kernel_positions[i + 1]

    # Only count if within reasonable distance (not across folio boundaries)
    if pos2 - pos1 <= 20:  # Within 20 tokens
        kernel_bigrams[(k1, k2)] += 1

print("\nObserved kernel bigrams (next kernel token):")
total_bigrams = sum(kernel_bigrams.values())

# Expected under independence
k_marginal = Counter(k for _, k in kernel_positions)
total_k = sum(k_marginal.values())

print(f"\n{'Bigram':<10} {'Observed':<10} {'Expected':<10} {'Ratio':<10} {'Status'}")
print("-" * 55)

bigram_results = {}
for k1 in ['k', 'h', 'e']:
    for k2 in ['k', 'h', 'e']:
        observed = kernel_bigrams.get((k1, k2), 0)
        # Expected under independence
        p1 = k_marginal[k1] / total_k
        p2 = k_marginal[k2] / total_k
        expected = p1 * p2 * total_bigrams

        ratio = observed / expected if expected > 0 else 0

        if ratio < 0.5:
            status = "SUPPRESSED"
        elif ratio > 1.5:
            status = "ENRICHED"
        else:
            status = "NORMAL"

        bigram_results[(k1, k2)] = {
            'observed': observed,
            'expected': expected,
            'ratio': ratio,
            'status': status
        }

        print(f"{k1}->{k2}      {observed:<10} {expected:<10.1f} {ratio:<10.2f} {status}")

# Chi-square test for overall independence
observed_matrix = np.zeros((3, 3))
for i, k1 in enumerate(['k', 'h', 'e']):
    for j, k2 in enumerate(['k', 'h', 'e']):
        observed_matrix[i, j] = kernel_bigrams.get((k1, k2), 0)

if observed_matrix.sum() > 0:
    chi2, p, dof, expected_matrix = chi2_contingency(observed_matrix)
    print(f"\nChi-square test for independence:")
    print(f"  Chi2 = {chi2:.2f}, p = {p:.6f}")
    if p < 0.05:
        print("  RESULT: Kernel bigrams are NOT independent (ordering exists)")
    else:
        print("  RESULT: Kernel bigrams are approximately independent (no strong ordering)")

# Identify forbidden/suppressed pairs
suppressed = [(k1, k2) for (k1, k2), r in bigram_results.items() if r['status'] == 'SUPPRESSED']
enriched = [(k1, k2) for (k1, k2), r in bigram_results.items() if r['status'] == 'ENRICHED']

print(f"\nSuppressed bigrams (<0.5x expected): {suppressed if suppressed else 'None'}")
print(f"Enriched bigrams (>1.5x expected): {enriched if enriched else 'None'}")

# ==========================================================================
# G-2: KERNEL TRIGRAM COLLAPSE TEST
# ==========================================================================

print("\n" + "=" * 70)
print("G-2: KERNEL TRIGRAM COLLAPSE TEST")
print("Question: Do kernel trigrams collapse into fewer equivalence classes?")
print("=" * 70)

# Extract trigrams with >=2 kernel symbols
kernel_trigrams = Counter()

for i in range(len(kernel_positions) - 2):
    pos1, k1 = kernel_positions[i]
    pos2, k2 = kernel_positions[i + 1]
    pos3, k3 = kernel_positions[i + 2]

    # Only count if within reasonable distance
    if pos3 - pos1 <= 30:  # Within 30 tokens
        kernel_trigrams[(k1, k2, k3)] += 1

print(f"\nTotal kernel trigrams observed: {sum(kernel_trigrams.values())}")
print(f"Unique kernel trigram patterns: {len(kernel_trigrams)}")

# There are 27 possible trigrams (3^3)
# How many are actually observed?
possible_trigrams = 27
observed_patterns = len(kernel_trigrams)
collapse_ratio = observed_patterns / possible_trigrams

print(f"\nTrigram collapse analysis:")
print(f"  Possible patterns: {possible_trigrams}")
print(f"  Observed patterns: {observed_patterns}")
print(f"  Collapse ratio: {collapse_ratio:.2f}")

if collapse_ratio < 0.5:
    print("  RESULT: Strong trigram collapse (limited orderings dominate)")
elif collapse_ratio < 0.8:
    print("  RESULT: Moderate trigram collapse")
else:
    print("  RESULT: Weak/no trigram collapse")

# Show most common trigrams
print(f"\nMost common kernel trigrams:")
for trigram, count in kernel_trigrams.most_common(10):
    pct = count / sum(kernel_trigrams.values()) * 100
    print(f"  {trigram[0]}->{trigram[1]}->{trigram[2]}: {count} ({pct:.1f}%)")

# Entropy analysis
if kernel_trigrams:
    total_tri = sum(kernel_trigrams.values())
    probs = [c / total_tri for c in kernel_trigrams.values()]
    entropy = -sum(p * np.log2(p) for p in probs if p > 0)
    max_entropy = np.log2(possible_trigrams)  # If all equally likely

    print(f"\nEntropy analysis:")
    print(f"  Observed entropy: {entropy:.2f} bits")
    print(f"  Max entropy (uniform): {max_entropy:.2f} bits")
    print(f"  Entropy ratio: {entropy/max_entropy:.2f}")

# ==========================================================================
# G-3: KERNEL POSITION-IN-INSTRUCTION ANALYSIS
# ==========================================================================

print("\n" + "=" * 70)
print("G-3: KERNEL POSITION-IN-INSTRUCTION ANALYSIS")
print("Question: Do kernel tokens prefer specific grammatical positions?")
print("=" * 70)

# Load forbidden transitions (hazards)
# These are stored in control_signatures.json or canonical_grammar.json
with open('results/canonical_grammar.json', 'r') as f:
    grammar = json.load(f)

# Check for constraints/forbidden transitions
constraints = grammar.get('constraints', {})
print(f"\nGrammar constraints available: {list(constraints.keys())}")

# Measure kernel proximity to LINK
link_positions = [i for i, (word, _) in enumerate(kernel_sequence) if is_link(word)]
print(f"\nLINK tokens: {len(link_positions)}")

# For each kernel class, measure distance to nearest LINK
kernel_link_distances = {'k': [], 'h': [], 'e': []}
non_kernel_link_distances = []

for i, (word, k_class) in enumerate(kernel_sequence):
    if not link_positions:
        break
    # Find nearest LINK
    min_dist = min(abs(i - lp) for lp in link_positions)

    if k_class is not None:
        kernel_link_distances[k_class].append(min_dist)
    else:
        non_kernel_link_distances.append(min_dist)

print(f"\nMean distance to nearest LINK:")
for k in ['k', 'h', 'e']:
    if kernel_link_distances[k]:
        mean_dist = np.mean(kernel_link_distances[k])
        print(f"  {k}: {mean_dist:.2f} tokens")

if non_kernel_link_distances:
    non_k_mean = np.mean(non_kernel_link_distances)
    print(f"  non-kernel: {non_k_mean:.2f} tokens")

# Statistical test: do kernel tokens appear closer/farther from LINK?
from scipy.stats import mannwhitneyu

print(f"\nKernel vs non-kernel LINK proximity:")
all_kernel_dists = []
for k in ['k', 'h', 'e']:
    all_kernel_dists.extend(kernel_link_distances[k])

if all_kernel_dists and non_kernel_link_distances:
    stat, p = mannwhitneyu(all_kernel_dists, non_kernel_link_distances, alternative='two-sided')
    k_mean = np.mean(all_kernel_dists)
    nk_mean = np.mean(non_kernel_link_distances)
    print(f"  Kernel mean: {k_mean:.2f}")
    print(f"  Non-kernel mean: {nk_mean:.2f}")
    print(f"  Mann-Whitney p = {p:.6f}")

    if p < 0.05:
        if k_mean < nk_mean:
            print("  RESULT: Kernel tokens are CLOSER to LINK than non-kernel")
        else:
            print("  RESULT: Kernel tokens are FARTHER from LINK than non-kernel")
    else:
        print("  RESULT: No significant difference in LINK proximity")

# Check kernel position within local context (first/middle/last third of 10-token windows)
print(f"\nKernel position within local 10-token windows:")
position_counts = {'k': {'first': 0, 'middle': 0, 'last': 0},
                   'h': {'first': 0, 'middle': 0, 'last': 0},
                   'e': {'first': 0, 'middle': 0, 'last': 0}}

for i, (word, k_class) in enumerate(kernel_sequence):
    if k_class is None:
        continue

    # Position within a sliding 10-token window
    window_start = max(0, i - 5)
    window_pos = i - window_start  # 0-9 within window

    if window_pos < 3:
        position_counts[k_class]['first'] += 1
    elif window_pos < 7:
        position_counts[k_class]['middle'] += 1
    else:
        position_counts[k_class]['last'] += 1

print(f"\n{'Kernel':<8} {'First':<10} {'Middle':<10} {'Last':<10}")
print("-" * 40)
for k in ['k', 'h', 'e']:
    total = sum(position_counts[k].values())
    f_pct = position_counts[k]['first'] / total * 100 if total > 0 else 0
    m_pct = position_counts[k]['middle'] / total * 100 if total > 0 else 0
    l_pct = position_counts[k]['last'] / total * 100 if total > 0 else 0
    print(f"{k:<8} {f_pct:>6.1f}%    {m_pct:>6.1f}%    {l_pct:>6.1f}%")

# ==========================================================================
# SUMMARY AND VERDICT
# ==========================================================================

print("\n" + "=" * 70)
print("DIRECTION G: SUMMARY AND VERDICT")
print("=" * 70)

# Collect findings
findings = []

# G-1 findings
if suppressed:
    findings.append(f"G-1: Suppressed bigrams found: {suppressed}")
if enriched:
    findings.append(f"G-1: Enriched bigrams found: {enriched}")
if not suppressed and not enriched:
    findings.append("G-1: No strongly suppressed or enriched bigrams")

# G-2 findings
if collapse_ratio < 0.5:
    findings.append(f"G-2: Strong trigram collapse (ratio={collapse_ratio:.2f})")
elif collapse_ratio < 0.8:
    findings.append(f"G-2: Moderate trigram collapse (ratio={collapse_ratio:.2f})")
else:
    findings.append(f"G-2: Weak/no trigram collapse (ratio={collapse_ratio:.2f})")

# G-3 findings
if all_kernel_dists and non_kernel_link_distances and p < 0.05:
    if k_mean < nk_mean:
        findings.append("G-3: Kernel tokens closer to LINK than non-kernel")
    else:
        findings.append("G-3: Kernel tokens farther from LINK than non-kernel")
else:
    findings.append("G-3: No significant kernel-LINK proximity pattern")

print("\nFINDINGS:")
for f in findings:
    print(f"  - {f}")

# Determine if constraints should be added
add_constraints = False
constraint_text = []

if suppressed or enriched:
    add_constraints = True
    if suppressed:
        constraint_text.append(f"Kernel bigram suppression: {suppressed}")
    if enriched:
        constraint_text.append(f"Kernel bigram enrichment: {enriched}")

if collapse_ratio < 0.7:
    add_constraints = True
    constraint_text.append(f"Kernel trigram collapse ratio: {collapse_ratio:.2f}")

print(f"\nVERDICT:")
if add_constraints:
    print("  Kernel ordering constraints EXIST")
    print("  Recommend: Add 1-2 Tier 2 constraints")
    print(f"\n  Proposed constraints:")
    for c in constraint_text:
        print(f"    - {c}")
else:
    print("  No significant kernel ordering constraints found")
    print("  Recommend: Close Direction G as 'no further structure'")

print(f"\n" + "=" * 70)
print("DIRECTION G: CLOSED")
print("Kernel ordering investigation is now COMPLETE.")
print("=" * 70)

# Save results
results = {
    'bigram_results': {f"{k1}->{k2}": v for (k1, k2), v in bigram_results.items()},
    'trigram_collapse_ratio': collapse_ratio,
    'trigram_count': len(kernel_trigrams),
    'findings': findings,
    'add_constraints': add_constraints,
    'constraint_text': constraint_text
}

os.makedirs('phases/KERNEL_ordering_constraints', exist_ok=True)
with open('phases/KERNEL_ordering_constraints/kernel_ordering_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to phases/KERNEL_ordering_constraints/kernel_ordering_results.json")
