"""
ADJACENT B FOLIO EXPLORATION

Speculative exploration: What changes between adjacent B folios?
Is there a subtle gradient or systematic drift?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("ADJACENT B FOLIO EXPLORATION")
print("What changes between adjacent folios?")
print("=" * 70)

# Build per-folio profiles
folio_profiles = {}
folio_order = []

for token in tx.currier_b():
    folio = token.folio
    if folio not in folio_profiles:
        folio_profiles[folio] = {
            'tokens': [],
            'middles': Counter(),
            'prefixes': Counter(),
            'suffixes': Counter(),
            'kernel_chars': Counter(),  # k, h, e within tokens
            'token_lengths': [],
        }
        folio_order.append(folio)

    word = token.word
    if word:
        m = morph.extract(word)
        folio_profiles[folio]['tokens'].append(word)
        if m.middle:
            folio_profiles[folio]['middles'][m.middle] += 1
        if m.prefix:
            folio_profiles[folio]['prefixes'][m.prefix] += 1
        if m.suffix:
            folio_profiles[folio]['suffixes'][m.suffix] += 1

        # Track kernel chars
        for char in ['k', 'h', 'e']:
            if char in word:
                folio_profiles[folio]['kernel_chars'][char] += 1

        folio_profiles[folio]['token_lengths'].append(len(word))

print(f"B folios: {len(folio_order)}")

# Compute derived metrics per folio
for folio, profile in folio_profiles.items():
    n_tokens = len(profile['tokens'])
    profile['n_tokens'] = n_tokens
    profile['mean_length'] = np.mean(profile['token_lengths']) if profile['token_lengths'] else 0

    # Kernel ratios
    total_kernel = sum(profile['kernel_chars'].values())
    if total_kernel > 0:
        profile['k_ratio'] = profile['kernel_chars']['k'] / total_kernel
        profile['h_ratio'] = profile['kernel_chars']['h'] / total_kernel
        profile['e_ratio'] = profile['kernel_chars']['e'] / total_kernel
    else:
        profile['k_ratio'] = profile['h_ratio'] = profile['e_ratio'] = 0

    # Unique MIDDLE count
    profile['n_unique_middles'] = len(profile['middles'])

    # Top PREFIX
    if profile['prefixes']:
        profile['top_prefix'] = profile['prefixes'].most_common(1)[0][0]
        profile['top_prefix_share'] = profile['prefixes'].most_common(1)[0][1] / n_tokens
    else:
        profile['top_prefix'] = None
        profile['top_prefix_share'] = 0

# ANALYSIS 1: How do adjacent folios differ in kernel balance?
print("\n" + "=" * 70)
print("KERNEL BALANCE DRIFT (k/h/e ratios)")
print("=" * 70)

k_ratios = [folio_profiles[f]['k_ratio'] for f in folio_order]
h_ratios = [folio_profiles[f]['h_ratio'] for f in folio_order]
e_ratios = [folio_profiles[f]['e_ratio'] for f in folio_order]

# Check for gradient across folio order
positions = np.arange(len(folio_order))
k_corr = np.corrcoef(positions, k_ratios)[0,1]
h_corr = np.corrcoef(positions, h_ratios)[0,1]
e_corr = np.corrcoef(positions, e_ratios)[0,1]

print(f"\nKernel ratio correlation with folio position:")
print(f"  k-ratio: r = {k_corr:.3f}")
print(f"  h-ratio: r = {h_corr:.3f}")
print(f"  e-ratio: r = {e_corr:.3f}")

# Adjacent differences
k_diffs = [k_ratios[i+1] - k_ratios[i] for i in range(len(k_ratios)-1)]
h_diffs = [h_ratios[i+1] - h_ratios[i] for i in range(len(h_ratios)-1)]
e_diffs = [e_ratios[i+1] - e_ratios[i] for i in range(len(e_ratios)-1)]

print(f"\nAdjacent folio kernel ratio changes:")
print(f"  k-ratio: mean={np.mean(k_diffs):.4f}, std={np.std(k_diffs):.4f}")
print(f"  h-ratio: mean={np.mean(h_diffs):.4f}, std={np.std(h_diffs):.4f}")
print(f"  e-ratio: mean={np.mean(e_diffs):.4f}, std={np.std(e_diffs):.4f}")

# ANALYSIS 2: MIDDLE vocabulary overlap between adjacent folios
print("\n" + "=" * 70)
print("MIDDLE VOCABULARY OVERLAP")
print("=" * 70)

def jaccard(set1, set2):
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

adjacent_jaccard = []
nonadjacent_jaccard = []

for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    m1 = set(folio_profiles[f1]['middles'].keys())
    m2 = set(folio_profiles[f2]['middles'].keys())
    adjacent_jaccard.append(jaccard(m1, m2))

# Sample non-adjacent pairs
import random
random.seed(42)
for _ in range(len(adjacent_jaccard)):
    i, j = random.sample(range(len(folio_order)), 2)
    if abs(i - j) > 1:  # Non-adjacent
        f1, f2 = folio_order[i], folio_order[j]
        m1 = set(folio_profiles[f1]['middles'].keys())
        m2 = set(folio_profiles[f2]['middles'].keys())
        nonadjacent_jaccard.append(jaccard(m1, m2))

print(f"\nMIDDLE vocabulary Jaccard similarity:")
print(f"  Adjacent folios: {np.mean(adjacent_jaccard):.3f} +/- {np.std(adjacent_jaccard):.3f}")
print(f"  Non-adjacent folios: {np.mean(nonadjacent_jaccard):.3f} +/- {np.std(nonadjacent_jaccard):.3f}")
print(f"  Ratio: {np.mean(adjacent_jaccard)/np.mean(nonadjacent_jaccard):.2f}x")

# ANALYSIS 3: Token length gradient
print("\n" + "=" * 70)
print("TOKEN LENGTH GRADIENT")
print("=" * 70)

mean_lengths = [folio_profiles[f]['mean_length'] for f in folio_order]
length_corr = np.corrcoef(positions, mean_lengths)[0,1]
print(f"\nMean token length correlation with position: r = {length_corr:.3f}")

# Adjacent changes
length_diffs = [mean_lengths[i+1] - mean_lengths[i] for i in range(len(mean_lengths)-1)]
print(f"Adjacent length change: mean={np.mean(length_diffs):.4f}, std={np.std(length_diffs):.4f}")

# ANALYSIS 4: Unique MIDDLE count gradient (vocabulary diversity)
print("\n" + "=" * 70)
print("VOCABULARY DIVERSITY GRADIENT")
print("=" * 70)

n_middles = [folio_profiles[f]['n_unique_middles'] for f in folio_order]
middles_corr = np.corrcoef(positions, n_middles)[0,1]
print(f"\nUnique MIDDLE count correlation with position: r = {middles_corr:.3f}")

# ANALYSIS 5: PREFIX distribution shift
print("\n" + "=" * 70)
print("PREFIX DISTRIBUTION")
print("=" * 70)

# Track which PREFIXes dominate each folio
prefix_sequence = [folio_profiles[f]['top_prefix'] for f in folio_order]
print(f"\nTop PREFIX by folio position (first 20):")
for i, (folio, prefix) in enumerate(zip(folio_order[:20], prefix_sequence[:20])):
    share = folio_profiles[folio]['top_prefix_share']
    print(f"  {i+1}. {folio}: '{prefix}' ({100*share:.1f}%)")

# Check if adjacent folios tend to share top PREFIX
same_prefix_adjacent = sum(1 for i in range(len(prefix_sequence)-1)
                          if prefix_sequence[i] == prefix_sequence[i+1] and prefix_sequence[i] is not None)
print(f"\nAdjacent folios with same top PREFIX: {same_prefix_adjacent}/{len(prefix_sequence)-1} ({100*same_prefix_adjacent/(len(prefix_sequence)-1):.1f}%)")

# ANALYSIS 6: Is there a "new MIDDLE introduction" pattern?
print("\n" + "=" * 70)
print("NEW MIDDLE INTRODUCTION PATTERN")
print("=" * 70)

all_middles_so_far = set()
new_middles_per_folio = []

for folio in folio_order:
    folio_middles = set(folio_profiles[folio]['middles'].keys())
    new_middles = folio_middles - all_middles_so_far
    new_middles_per_folio.append(len(new_middles))
    all_middles_so_far |= folio_middles

print(f"\nNew MIDDLEs introduced per folio:")
print(f"  Mean: {np.mean(new_middles_per_folio):.1f}")
print(f"  First 10 folios: {new_middles_per_folio[:10]}")
print(f"  Last 10 folios: {new_middles_per_folio[-10:]}")

# Is there a declining pattern (early folios introduce more)?
new_middle_corr = np.corrcoef(positions, new_middles_per_folio)[0,1]
print(f"\nNew MIDDLE count correlation with position: r = {new_middle_corr:.3f}")

# ANALYSIS 7: Cumulative vocabulary coverage
print("\n" + "=" * 70)
print("CUMULATIVE VOCABULARY COVERAGE")
print("=" * 70)

cumulative_coverage = []
all_b_middles = set()
for folio in folio_order:
    all_b_middles |= set(folio_profiles[folio]['middles'].keys())

running_middles = set()
for folio in folio_order:
    running_middles |= set(folio_profiles[folio]['middles'].keys())
    coverage = len(running_middles) / len(all_b_middles)
    cumulative_coverage.append(coverage)

print(f"\nCumulative MIDDLE coverage by position:")
print(f"  After 10 folios: {100*cumulative_coverage[9]:.1f}%")
print(f"  After 20 folios: {100*cumulative_coverage[19]:.1f}%")
print(f"  After 40 folios: {100*cumulative_coverage[39]:.1f}%")
print(f"  After 60 folios: {100*cumulative_coverage[59]:.1f}%")
print(f"  After all {len(folio_order)} folios: {100*cumulative_coverage[-1]:.1f}%")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: ADJACENT FOLIO DIFFERENTIATION")
print("=" * 70)

print(f"""
1. KERNEL BALANCE: Weak positional gradient
   - k-ratio: r = {k_corr:.3f}
   - h-ratio: r = {h_corr:.3f}
   - e-ratio: r = {e_corr:.3f}

2. MIDDLE VOCABULARY: Adjacent folios share {np.mean(adjacent_jaccard)/np.mean(nonadjacent_jaccard):.2f}x more
   - Adjacent Jaccard: {np.mean(adjacent_jaccard):.3f}
   - Non-adjacent Jaccard: {np.mean(nonadjacent_jaccard):.3f}

3. TOKEN LENGTH: Gradient with position r = {length_corr:.3f}

4. VOCABULARY DIVERSITY: Unique MIDDLEs r = {middles_corr:.3f}

5. NEW MIDDLE INTRODUCTION: Gradient r = {new_middle_corr:.3f}
   - Early folios introduce more new MIDDLEs
   - {cumulative_coverage[9]*100:.0f}% vocabulary in first 10 folios
""")
