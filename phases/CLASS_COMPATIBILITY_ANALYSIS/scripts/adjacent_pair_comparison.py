"""
ADJACENT PAIR COMPARISON

Exactly how do two adjacent folios differ?
Pick some adjacent pairs and compare them in detail.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

# Build per-folio data
folio_data = {}
folio_order = []

for token in tx.currier_b():
    folio = token.folio
    if folio not in folio_data:
        folio_data[folio] = {
            'tokens': [],
            'words': [],
            'middles': Counter(),
            'prefixes': Counter(),
            'suffixes': Counter(),
        }
        folio_order.append(folio)

    word = token.word
    if word:
        folio_data[folio]['tokens'].append(token)
        folio_data[folio]['words'].append(word)
        m = morph.extract(word)
        if m.middle:
            folio_data[folio]['middles'][m.middle] += 1
        if m.prefix:
            folio_data[folio]['prefixes'][m.prefix] += 1
        if m.suffix:
            folio_data[folio]['suffixes'][m.suffix] += 1

def compare_folios(f1, f2):
    """Compare two folios in detail."""
    d1, d2 = folio_data[f1], folio_data[f2]

    print(f"\n{'='*70}")
    print(f"COMPARING: {f1} vs {f2}")
    print(f"{'='*70}")

    # Basic stats
    print(f"\nToken counts: {len(d1['words'])} vs {len(d2['words'])}")

    # MIDDLE comparison
    m1 = set(d1['middles'].keys())
    m2 = set(d2['middles'].keys())
    shared = m1 & m2
    only_f1 = m1 - m2
    only_f2 = m2 - m1

    print(f"\nMIDDLE vocabulary:")
    print(f"  {f1}: {len(m1)} unique")
    print(f"  {f2}: {len(m2)} unique")
    print(f"  Shared: {len(shared)} ({100*len(shared)/len(m1|m2):.1f}%)")
    print(f"  Only in {f1}: {len(only_f1)}")
    print(f"  Only in {f2}: {len(only_f2)}")

    # Jaccard
    jaccard = len(shared) / len(m1 | m2) if (m1 | m2) else 0
    print(f"  Jaccard: {jaccard:.3f}")

    # Top MIDDLEs comparison
    print(f"\nTop 10 MIDDLEs in each:")
    top1 = d1['middles'].most_common(10)
    top2 = d2['middles'].most_common(10)
    print(f"  {f1}: {[m for m,c in top1]}")
    print(f"  {f2}: {[m for m,c in top2]}")

    # How many of top 10 are shared?
    top1_set = set(m for m,c in top1)
    top2_set = set(m for m,c in top2)
    top_shared = top1_set & top2_set
    print(f"  Top-10 overlap: {len(top_shared)}/10")

    # PREFIX comparison
    p1 = set(d1['prefixes'].keys())
    p2 = set(d2['prefixes'].keys())

    print(f"\nPREFIX vocabulary:")
    print(f"  {f1}: {sorted(p1)}")
    print(f"  {f2}: {sorted(p2)}")
    print(f"  Shared: {sorted(p1 & p2)}")
    print(f"  Different: {sorted(p1 ^ p2)}")

    # SUFFIX comparison
    s1 = set(d1['suffixes'].keys())
    s2 = set(d2['suffixes'].keys())

    print(f"\nSUFFIX vocabulary:")
    print(f"  {f1}: {sorted(s1)}")
    print(f"  {f2}: {sorted(s2)}")
    print(f"  Shared: {sorted(s1 & s2)}")

    # Unique MIDDLEs (the differentiating content)
    print(f"\nMIDDLEs ONLY in {f1} (sample):")
    only_f1_list = list(only_f1)[:10]
    for m in only_f1_list:
        print(f"  '{m}' ({d1['middles'][m]} occurrences)")

    print(f"\nMIDDLEs ONLY in {f2} (sample):")
    only_f2_list = list(only_f2)[:10]
    for m in only_f2_list:
        print(f"  '{m}' ({d2['middles'][m]} occurrences)")

    # Token-level overlap (exact word matches)
    w1 = set(d1['words'])
    w2 = set(d2['words'])
    word_shared = w1 & w2
    word_jaccard = len(word_shared) / len(w1 | w2) if (w1 | w2) else 0

    print(f"\nExact TOKEN overlap:")
    print(f"  Shared tokens: {len(word_shared)} / {len(w1 | w2)} ({100*word_jaccard:.1f}%)")
    print(f"  Sample shared: {list(word_shared)[:10]}")

    return {
        'middle_jaccard': jaccard,
        'word_jaccard': word_jaccard,
        'shared_middles': len(shared),
        'unique_f1': len(only_f1),
        'unique_f2': len(only_f2),
    }

# Compare several adjacent pairs
print("ADJACENT FOLIO PAIR COMPARISONS")
print("="*70)

results = []
# Pick pairs spread across the manuscript
pairs_to_compare = [
    (folio_order[0], folio_order[1]),   # First pair
    (folio_order[10], folio_order[11]), # Early-middle
    (folio_order[40], folio_order[41]), # Middle
    (folio_order[70], folio_order[71]), # Late
]

for f1, f2 in pairs_to_compare:
    r = compare_folios(f1, f2)
    results.append(r)

# Summary statistics
print(f"\n{'='*70}")
print("SUMMARY: HOW ADJACENT FOLIOS DIFFER")
print(f"{'='*70}")

mean_middle_jaccard = np.mean([r['middle_jaccard'] for r in results])
mean_word_jaccard = np.mean([r['word_jaccard'] for r in results])
mean_unique = np.mean([r['unique_f1'] + r['unique_f2'] for r in results])

print(f"""
Across {len(results)} adjacent pairs:

MIDDLE vocabulary Jaccard: {mean_middle_jaccard:.3f}
  => ~{100*mean_middle_jaccard:.0f}% of MIDDLEs are shared

Exact TOKEN Jaccard: {mean_word_jaccard:.3f}
  => ~{100*mean_word_jaccard:.0f}% of exact tokens are shared

Mean unique MIDDLEs per pair: {mean_unique:.0f}
  => Each folio has ~{mean_unique/2:.0f} MIDDLEs the other lacks
""")

# Compute all adjacent pairs
print(f"\n{'='*70}")
print("ALL ADJACENT PAIRS: DISTRIBUTION")
print(f"{'='*70}")

all_middle_jaccard = []
all_word_jaccard = []

for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    d1, d2 = folio_data[f1], folio_data[f2]

    m1 = set(d1['middles'].keys())
    m2 = set(d2['middles'].keys())
    mj = len(m1 & m2) / len(m1 | m2) if (m1 | m2) else 0
    all_middle_jaccard.append(mj)

    w1 = set(d1['words'])
    w2 = set(d2['words'])
    wj = len(w1 & w2) / len(w1 | w2) if (w1 | w2) else 0
    all_word_jaccard.append(wj)

print(f"\nMIDDLE Jaccard across all {len(all_middle_jaccard)} adjacent pairs:")
print(f"  Mean: {np.mean(all_middle_jaccard):.3f}")
print(f"  Std: {np.std(all_middle_jaccard):.3f}")
print(f"  Range: {np.min(all_middle_jaccard):.3f} - {np.max(all_middle_jaccard):.3f}")

print(f"\nExact TOKEN Jaccard across all adjacent pairs:")
print(f"  Mean: {np.mean(all_word_jaccard):.3f}")
print(f"  Std: {np.std(all_word_jaccard):.3f}")
print(f"  Range: {np.min(all_word_jaccard):.3f} - {np.max(all_word_jaccard):.3f}")

# Find most similar and most different adjacent pairs
most_similar_idx = np.argmax(all_middle_jaccard)
most_different_idx = np.argmin(all_middle_jaccard)

print(f"\nMost SIMILAR adjacent pair:")
print(f"  {folio_order[most_similar_idx]} - {folio_order[most_similar_idx+1]}")
print(f"  MIDDLE Jaccard: {all_middle_jaccard[most_similar_idx]:.3f}")

print(f"\nMost DIFFERENT adjacent pair:")
print(f"  {folio_order[most_different_idx]} - {folio_order[most_different_idx+1]}")
print(f"  MIDDLE Jaccard: {all_middle_jaccard[most_different_idx]:.3f}")

print(f"\n{'='*70}")
print("INTERPRETATION")
print(f"{'='*70}")

print(f"""
Adjacent folios are NOT nearly identical:
- Only ~{100*np.mean(all_middle_jaccard):.0f}% MIDDLE vocabulary overlap
- Only ~{100*np.mean(all_word_jaccard):.0f}% exact token overlap

Each adjacent pair differs by:
- ~{100*(1-np.mean(all_middle_jaccard)):.0f}% of their MIDDLE vocabulary is unique to one or the other
- One folio has MIDDLEs the other lacks entirely

The similarity is RELATIVE:
- Adjacent: {np.mean(all_middle_jaccard):.3f} Jaccard
- Non-adjacent: ~0.276 Jaccard (from earlier analysis)
- Ratio: {np.mean(all_middle_jaccard)/0.276:.2f}x more similar

So adjacent folios are ~{np.mean(all_middle_jaccard)/0.276:.1f}x more similar than random pairs,
but still have substantial differences (~{100*(1-np.mean(all_middle_jaccard)):.0f}% unique vocabulary).
""")
