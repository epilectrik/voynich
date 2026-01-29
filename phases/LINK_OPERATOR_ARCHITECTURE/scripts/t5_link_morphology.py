"""
T5: LINK Morphological Profile

Analyze the MIDDLE composition of LINK tokens:
1. What MIDDLEs appear in LINK tokens?
2. Are they PP (pipeline-participating) or B-exclusive?
3. How does 'ol' relate to morphological structure?
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

# Load morphology
morph = Morphology()

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())
a_tokens = list(tx.currier_a())

# Get A MIDDLE set (PP vocabulary)
a_middles = set()
for t in a_tokens:
    word = t.word.replace('*', '')
    if word.strip():
        m = morph.extract(word)
        if m.middle:
            a_middles.add(m.middle)

print(f"Currier A unique MIDDLEs: {len(a_middles)}")

# Analyze LINK token morphology
link_middles = Counter()
nonlink_middles = Counter()
link_tokens_analyzed = 0
nonlink_tokens_analyzed = 0

link_pp_count = 0
link_non_pp_count = 0
nonlink_pp_count = 0
nonlink_non_pp_count = 0

# Where does 'ol' appear morphologically?
ol_in_middle = 0
ol_in_prefix = 0
ol_in_suffix = 0
ol_spans_boundary = 0
link_analyzed = 0

for t in b_tokens:
    word = t.word.replace('*', '')
    if not word.strip():
        continue

    m = morph.extract(word)
    if not m.middle:
        continue

    if is_link(word):
        link_tokens_analyzed += 1
        link_middles[m.middle] += 1
        if m.middle in a_middles:
            link_pp_count += 1
        else:
            link_non_pp_count += 1

        # Where is 'ol' in the morphology?
        link_analyzed += 1
        ol_idx = word.find('ol')
        if ol_idx >= 0:
            # Check if 'ol' is in middle
            prefix_len = len(m.prefix) if m.prefix else 0
            if m.articulator:
                prefix_len += len(m.articulator)

            middle_start = prefix_len
            middle_end = middle_start + len(m.middle)

            if ol_idx >= middle_start and ol_idx + 2 <= middle_end:
                ol_in_middle += 1
            elif ol_idx < middle_start:
                # In prefix (or articulator)
                if ol_idx + 2 <= middle_start:
                    ol_in_prefix += 1
                else:
                    ol_spans_boundary += 1
            elif ol_idx >= middle_end:
                ol_in_suffix += 1
            else:
                ol_spans_boundary += 1
    else:
        nonlink_tokens_analyzed += 1
        nonlink_middles[m.middle] += 1
        if m.middle in a_middles:
            nonlink_pp_count += 1
        else:
            nonlink_non_pp_count += 1

print(f"\n{'='*60}")
print(f"LINK MORPHOLOGICAL PROFILE")
print(f"{'='*60}")
print(f"LINK tokens with extractable MIDDLE: {link_tokens_analyzed}")
print(f"Non-LINK tokens with extractable MIDDLE: {nonlink_tokens_analyzed}")

# PP rates
link_pp_rate = 100 * link_pp_count / link_tokens_analyzed if link_tokens_analyzed > 0 else 0
nonlink_pp_rate = 100 * nonlink_pp_count / nonlink_tokens_analyzed if nonlink_tokens_analyzed > 0 else 0

print(f"\n--- PP (Pipeline-Participating) RATES ---")
print(f"LINK tokens PP: {link_pp_count}/{link_tokens_analyzed} = {link_pp_rate:.1f}%")
print(f"Non-LINK tokens PP: {nonlink_pp_count}/{nonlink_tokens_analyzed} = {nonlink_pp_rate:.1f}%")

# Chi-square test
chi2, p = stats.chi2_contingency([
    [link_pp_count, link_non_pp_count],
    [nonlink_pp_count, nonlink_non_pp_count]
])[:2]
print(f"Chi-square: chi2={chi2:.1f}, p={p:.2e}")

# Where does 'ol' appear?
print(f"\n--- 'OL' MORPHOLOGICAL POSITION ---")
print(f"In MIDDLE: {ol_in_middle}/{link_analyzed} = {100*ol_in_middle/link_analyzed:.1f}%")
print(f"In PREFIX/ARTICULATOR: {ol_in_prefix}/{link_analyzed} = {100*ol_in_prefix/link_analyzed:.1f}%")
print(f"In SUFFIX: {ol_in_suffix}/{link_analyzed} = {100*ol_in_suffix/link_analyzed:.1f}%")
print(f"Spans boundary: {ol_spans_boundary}/{link_analyzed} = {100*ol_spans_boundary/link_analyzed:.1f}%")

# Top MIDDLEs in LINK tokens
print(f"\n--- TOP 20 MIDDLEs IN LINK TOKENS ---")
print(f"{'MIDDLE':<15} {'Count':>8} {'PP?':>6}")
print(f"{'-'*15} {'-'*8} {'-'*6}")
for middle, count in link_middles.most_common(20):
    is_pp = 'PP' if middle in a_middles else 'RI'
    print(f"{middle:<15} {count:>8} {is_pp:>6}")

# Check if 'ol' is itself a MIDDLE
print(f"\n--- IS 'ol' A VALID MIDDLE? ---")
print(f"'ol' appears as MIDDLE: {link_middles.get('ol', 0)} times")
print(f"'ol' is in A vocabulary: {'YES' if 'ol' in a_middles else 'NO'}")

# MIDDLEs containing 'ol'
ol_middles = [m for m in link_middles.keys() if 'ol' in m]
print(f"\nMIDDLEs containing 'ol': {len(ol_middles)}")
print(f"Examples: {ol_middles[:10]}")

# Unique MIDDLEs
link_unique = set(link_middles.keys())
nonlink_unique = set(nonlink_middles.keys())
overlap = link_unique & nonlink_unique
link_only = link_unique - nonlink_unique
nonlink_only = nonlink_unique - link_unique

print(f"\n--- MIDDLE VOCABULARY ANALYSIS ---")
print(f"LINK unique MIDDLEs: {len(link_unique)}")
print(f"Non-LINK unique MIDDLEs: {len(nonlink_unique)}")
print(f"Overlap: {len(overlap)}")
print(f"LINK-only: {len(link_only)}")
print(f"Non-LINK-only: {len(nonlink_only)}")
print(f"Jaccard similarity: {len(overlap) / len(link_unique | nonlink_unique):.3f}")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
if link_pp_rate > nonlink_pp_rate + 5:
    print(f"LINK tokens are MORE PP-enriched than non-LINK ({link_pp_rate:.1f}% vs {nonlink_pp_rate:.1f}%)")
elif link_pp_rate < nonlink_pp_rate - 5:
    print(f"LINK tokens are LESS PP-enriched than non-LINK ({link_pp_rate:.1f}% vs {nonlink_pp_rate:.1f}%)")
else:
    print(f"LINK and non-LINK have SIMILAR PP rates ({link_pp_rate:.1f}% vs {nonlink_pp_rate:.1f}%)")

print(f"\n'ol' morphological position:")
dominant = max([
    ('MIDDLE', ol_in_middle),
    ('PREFIX', ol_in_prefix),
    ('SUFFIX', ol_in_suffix),
    ('BOUNDARY', ol_spans_boundary)
], key=lambda x: x[1])
print(f"  Dominant position: {dominant[0]} ({100*dominant[1]/link_analyzed:.1f}%)")
