"""
T6: LINK-Kernel Contact Analysis

Analyze how LINK relates to kernel operators (k, h, e):
1. Does LINK cluster near kernel tokens?
2. What transitions occur between LINK and kernel?
3. Is there asymmetry in LINK-kernel relationships?
"""

import json
import sys
sys.path.insert(0, 'C:/git/voynich')

from collections import Counter, defaultdict
from scripts.voynich import Transcript, Morphology
from scipy import stats
import numpy as np

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_data = json.load(f)

token_to_role = class_data['token_to_role']

def is_link(word):
    """LINK = token contains 'ol' substring (C609)"""
    return 'ol' in word.replace('*', '')

# C085 kernel primitives: k, h, e are the core (C089)
def has_kernel(word):
    """Check if word contains kernel primitives k, h, or e"""
    word = word.replace('*', '').lower()
    return 'k' in word or 'h' in word or 'e' in word

def get_kernel_type(word):
    """Return which kernel primitive is present"""
    word = word.replace('*', '').lower()
    kernels = []
    if 'k' in word:
        kernels.append('k')
    if 'h' in word:
        kernels.append('h')
    if 'e' in word:
        kernels.append('e')
    return kernels if kernels else None

# Load morphology
morph = Morphology()

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

# Group by folio and line
lines = defaultdict(list)
for t in b_tokens:
    key = (t.folio, t.line)
    lines[key].append(t)

print(f"Total B tokens: {len(b_tokens)}")

# Count overlaps
link_with_kernel = Counter()
link_without_kernel = 0
nonlink_with_kernel = Counter()
nonlink_without_kernel = 0

for t in b_tokens:
    word = t.word.replace('*', '')
    if not word.strip():
        continue

    is_l = is_link(word)
    kernels = get_kernel_type(word)

    if is_l:
        if kernels:
            for k in kernels:
                link_with_kernel[k] += 1
        else:
            link_without_kernel += 1
    else:
        if kernels:
            for k in kernels:
                nonlink_with_kernel[k] += 1
        else:
            nonlink_without_kernel += 1

print(f"\n{'='*60}")
print(f"LINK-KERNEL OVERLAP")
print(f"{'='*60}")

total_link = sum(link_with_kernel.values()) + link_without_kernel
total_nonlink = sum(nonlink_with_kernel.values()) + nonlink_without_kernel

print(f"\nKernel content in LINK tokens:")
for k in ['k', 'h', 'e']:
    count = link_with_kernel[k]
    pct = 100 * count / total_link
    print(f"  Contains '{k}': {count} ({pct:.1f}%)")

print(f"\nKernel content in non-LINK tokens:")
for k in ['k', 'h', 'e']:
    count = nonlink_with_kernel[k]
    pct = 100 * count / total_nonlink
    print(f"  Contains '{k}': {count} ({pct:.1f}%)")

# Enrichment
print(f"\n--- KERNEL ENRICHMENT IN LINK ---")
for k in ['k', 'h', 'e']:
    link_rate = link_with_kernel[k] / total_link
    nonlink_rate = nonlink_with_kernel[k] / total_nonlink
    enrich = link_rate / nonlink_rate if nonlink_rate > 0 else 0
    print(f"  '{k}' enrichment: {enrich:.2f}x")

# Distance analysis: LINK to kernel tokens
print(f"\n{'='*60}")
print(f"LINK-KERNEL DISTANCE ANALYSIS")
print(f"{'='*60}")

link_to_kernel_distances = []
nonlink_to_kernel_distances = []

for key, tokens in lines.items():
    # Find kernel positions (tokens containing k, h, or e but NOT link)
    kernel_positions = []
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if word.strip() and has_kernel(word) and not is_link(word):
            kernel_positions.append(i)

    if not kernel_positions:
        continue

    # Calculate distances
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        min_dist = min(abs(i - kp) for kp in kernel_positions)

        if is_link(word):
            link_to_kernel_distances.append(min_dist)
        else:
            nonlink_to_kernel_distances.append(min_dist)

if link_to_kernel_distances and nonlink_to_kernel_distances:
    print(f"Mean distance to kernel tokens:")
    print(f"  LINK tokens: {np.mean(link_to_kernel_distances):.2f}")
    print(f"  Non-LINK tokens: {np.mean(nonlink_to_kernel_distances):.2f}")

    u_stat, p_mw = stats.mannwhitneyu(link_to_kernel_distances, nonlink_to_kernel_distances, alternative='two-sided')
    print(f"\nMann-Whitney U: p={p_mw:.4f}")

# Transition analysis: what comes before/after LINK?
print(f"\n{'='*60}")
print(f"LINK-KERNEL TRANSITIONS")
print(f"{'='*60}")

# Pre-LINK kernel content
pre_link_k = 0
pre_link_h = 0
pre_link_e = 0
pre_link_total = 0

# Post-LINK kernel content
post_link_k = 0
post_link_h = 0
post_link_e = 0
post_link_total = 0

# Pre-kernel LINK rate
pre_kernel_link = Counter()
pre_kernel_total = Counter()

# Post-kernel LINK rate
post_kernel_link = Counter()
post_kernel_total = Counter()

for key, tokens in lines.items():
    for i, t in enumerate(tokens):
        word = t.word.replace('*', '')
        if not word.strip():
            continue

        is_l = is_link(word)
        kernels = get_kernel_type(word)

        if is_l:
            # Check what precedes LINK
            if i > 0:
                prev_word = tokens[i-1].word.replace('*', '')
                if prev_word.strip():
                    pre_link_total += 1
                    prev_kernels = get_kernel_type(prev_word)
                    if prev_kernels:
                        if 'k' in prev_kernels:
                            pre_link_k += 1
                        if 'h' in prev_kernels:
                            pre_link_h += 1
                        if 'e' in prev_kernels:
                            pre_link_e += 1

            # Check what follows LINK
            if i < len(tokens) - 1:
                next_word = tokens[i+1].word.replace('*', '')
                if next_word.strip():
                    post_link_total += 1
                    next_kernels = get_kernel_type(next_word)
                    if next_kernels:
                        if 'k' in next_kernels:
                            post_link_k += 1
                        if 'h' in next_kernels:
                            post_link_h += 1
                        if 'e' in next_kernels:
                            post_link_e += 1

        # Check LINK rate after kernel
        if kernels:
            for k in kernels:
                if i < len(tokens) - 1:
                    next_word = tokens[i+1].word.replace('*', '')
                    if next_word.strip():
                        post_kernel_total[k] += 1
                        if is_link(next_word):
                            post_kernel_link[k] += 1

                if i > 0:
                    prev_word = tokens[i-1].word.replace('*', '')
                    if prev_word.strip():
                        pre_kernel_total[k] += 1
                        if is_link(prev_word):
                            pre_kernel_link[k] += 1

print(f"\nWhat precedes LINK tokens?")
print(f"  Contains 'k': {pre_link_k}/{pre_link_total} = {100*pre_link_k/pre_link_total:.1f}%")
print(f"  Contains 'h': {pre_link_h}/{pre_link_total} = {100*pre_link_h/pre_link_total:.1f}%")
print(f"  Contains 'e': {pre_link_e}/{pre_link_total} = {100*pre_link_e/pre_link_total:.1f}%")

print(f"\nWhat follows LINK tokens?")
print(f"  Contains 'k': {post_link_k}/{post_link_total} = {100*post_link_k/post_link_total:.1f}%")
print(f"  Contains 'h': {post_link_h}/{post_link_total} = {100*post_link_h/post_link_total:.1f}%")
print(f"  Contains 'e': {post_link_e}/{post_link_total} = {100*post_link_e/post_link_total:.1f}%")

# Baseline rates
baseline_link = 13.2  # LINK rate
print(f"\nLINK rate after kernel tokens (baseline: {baseline_link:.1f}%):")
for k in ['k', 'h', 'e']:
    if post_kernel_total[k] > 0:
        rate = 100 * post_kernel_link[k] / post_kernel_total[k]
        enrich = rate / baseline_link
        print(f"  After '{k}': {rate:.1f}% ({enrich:.2f}x)")

print(f"\nLINK rate before kernel tokens (baseline: {baseline_link:.1f}%):")
for k in ['k', 'h', 'e']:
    if pre_kernel_total[k] > 0:
        rate = 100 * pre_kernel_link[k] / pre_kernel_total[k]
        enrich = rate / baseline_link
        print(f"  Before '{k}': {rate:.1f}% ({enrich:.2f}x)")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")

if link_to_kernel_distances and nonlink_to_kernel_distances:
    mean_link_dist = np.mean(link_to_kernel_distances)
    mean_nonlink_dist = np.mean(nonlink_to_kernel_distances)
    if p_mw < 0.05:
        if mean_link_dist < mean_nonlink_dist:
            print(f"LINK is CLOSER to kernel tokens than non-LINK")
        else:
            print(f"LINK is FARTHER from kernel tokens than non-LINK")
    else:
        print(f"LINK distance to kernel is NOT different from baseline")

# Check for asymmetry
print(f"\nAsymmetry analysis:")
print(f"  'k' follows LINK at {100*post_link_k/post_link_total:.1f}% vs precedes at {100*pre_link_k/pre_link_total:.1f}%")
print(f"  'h' follows LINK at {100*post_link_h/post_link_total:.1f}% vs precedes at {100*pre_link_h/pre_link_total:.1f}%")
print(f"  'e' follows LINK at {100*post_link_e/post_link_total:.1f}% vs precedes at {100*pre_link_e/pre_link_total:.1f}%")
