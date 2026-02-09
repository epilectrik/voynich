"""
20_ab_pairing_specificity.py

TEST: Do viable A-B pairings cluster, or are they random?

If A records are "material lists" for specific B procedures:
  - Viable A-B pairings should be above chance
  - Best-match A records for a B folio should share vocabulary
  - There should be structure in the A-B viability matrix

If A records are generic registry entries:
  - Any A record works about as well as any other
  - Best matches would be random
  - No clustering

Method:
1. Compute vocabulary overlap for all A-B folio pairs
2. For each B folio, identify "best match" A folios
3. Check if best matches cluster or are random
4. Compare to null model
"""

import sys
from pathlib import Path
from collections import defaultdict
import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

print("="*70)
print("A-B PAIRING SPECIFICITY TEST")
print("="*70)
print("Question: Are viable A-B pairings specific or random?")

tx = Transcript()
morph = Morphology()

# =============================================================
# STEP 1: Build vocabulary sets by folio
# =============================================================
print("\nSTEP 1: Building vocabulary sets...")

a_folio_vocab = defaultdict(set)  # A folio -> set of MIDDLEs
b_folio_vocab = defaultdict(set)  # B folio -> set of MIDDLEs

for t in tx.currier_a():
    try:
        m = morph.extract(t.word)
        if m.middle:
            a_folio_vocab[t.folio].add(m.middle)
    except:
        pass

for t in tx.currier_b():
    try:
        m = morph.extract(t.word)
        if m.middle:
            b_folio_vocab[t.folio].add(m.middle)
    except:
        pass

a_folios = sorted(a_folio_vocab.keys())
b_folios = sorted(b_folio_vocab.keys())

print(f"A folios: {len(a_folios)}")
print(f"B folios: {len(b_folios)}")

# =============================================================
# STEP 2: Compute A-B overlap matrix
# =============================================================
print("\nSTEP 2: Computing A-B vocabulary overlap matrix...")

def jaccard(set1, set2):
    if not set1 or not set2:
        return 0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

def overlap_fraction(a_set, b_set):
    """What fraction of B's vocabulary is covered by A?"""
    if not b_set:
        return 0
    return len(a_set & b_set) / len(b_set)

# Compute overlap for all pairs
overlap_matrix = {}
for a_folio in a_folios:
    for b_folio in b_folios:
        a_vocab = a_folio_vocab[a_folio]
        b_vocab = b_folio_vocab[b_folio]
        overlap_matrix[(a_folio, b_folio)] = {
            'jaccard': jaccard(a_vocab, b_vocab),
            'b_coverage': overlap_fraction(a_vocab, b_vocab),
            'shared': len(a_vocab & b_vocab)
        }

print(f"Computed {len(overlap_matrix)} A-B pairs")

# =============================================================
# STEP 3: For each B folio, find best-match A folios
# =============================================================
print("\nSTEP 3: Finding best-match A folios for each B...")

b_best_matches = {}
for b_folio in b_folios:
    # Rank A folios by coverage of B vocabulary
    a_scores = [(a_folio, overlap_matrix[(a_folio, b_folio)]['b_coverage'])
                for a_folio in a_folios]
    a_scores.sort(key=lambda x: -x[1])

    best_a = a_scores[0][0]
    best_score = a_scores[0][1]
    top_5 = [a for a, s in a_scores[:5]]

    b_best_matches[b_folio] = {
        'best_a': best_a,
        'best_score': best_score,
        'top_5': top_5,
        'top_5_scores': [s for a, s in a_scores[:5]]
    }

# Summary stats
best_scores = [b_best_matches[b]['best_score'] for b in b_folios]
print(f"\nBest-match coverage stats:")
print(f"  Mean: {sum(best_scores)/len(best_scores):.3f}")
print(f"  Min: {min(best_scores):.3f}")
print(f"  Max: {max(best_scores):.3f}")

# =============================================================
# STEP 4: Check if best matches cluster
# =============================================================
print("\n" + "="*70)
print("STEP 4: Do best-match A folios cluster?")
print("="*70)

# Count how often each A folio is a best match
a_best_counts = defaultdict(int)
for b_folio in b_folios:
    best_a = b_best_matches[b_folio]['best_a']
    a_best_counts[best_a] += 1

# If random: each A folio would be best match ~82/114 = 0.72 times on average
# If clustered: some A folios would be best match for many B folios

print("\nA folios that are best-match for multiple B folios:")
sorted_counts = sorted(a_best_counts.items(), key=lambda x: -x[1])
for a_folio, count in sorted_counts[:10]:
    print(f"  {a_folio}: best for {count} B folios")

top_a = sorted_counts[0][0]
top_count = sorted_counts[0][1]
print(f"\nMost common best-match: {top_a} (matches {top_count} B folios)")

# Expected under random: ~1-2 matches per A folio (Poisson)
# If one A matches 10+, that's clustering

# =============================================================
# STEP 5: Compare to null model
# =============================================================
print("\n" + "="*70)
print("STEP 5: Null model comparison")
print("="*70)

# Shuffle A-B assignments and see if best-match clustering is above chance
n_permutations = 1000
null_max_counts = []

for _ in range(n_permutations):
    # Randomly assign A folios to B folios
    shuffled_best = random.choices(a_folios, k=len(b_folios))
    counts = defaultdict(int)
    for a in shuffled_best:
        counts[a] += 1
    null_max_counts.append(max(counts.values()))

mean_null_max = sum(null_max_counts) / len(null_max_counts)
p_value = sum(1 for x in null_max_counts if x >= top_count) / len(null_max_counts)

print(f"\nReal max count: {top_count}")
print(f"Null mean max: {mean_null_max:.2f}")
print(f"p-value (real >= null): {p_value:.4f}")

if p_value < 0.05:
    print("  --> SIGNIFICANT CLUSTERING: Best matches are more concentrated than random")
else:
    print("  --> NOT SIGNIFICANT: Clustering is within random expectation")

# =============================================================
# STEP 6: Check if top-5 A matches share vocabulary
# =============================================================
print("\n" + "="*70)
print("STEP 6: Do top A matches share vocabulary with each other?")
print("="*70)

# For each B folio, check if the top-5 A matches share vocabulary
top5_self_jaccard = []
for b_folio in b_folios:
    top_5 = b_best_matches[b_folio]['top_5']
    # Compute pairwise Jaccard among top 5
    pair_jaccards = []
    for i in range(len(top_5)):
        for j in range(i+1, len(top_5)):
            j_score = jaccard(a_folio_vocab[top_5[i]], a_folio_vocab[top_5[j]])
            pair_jaccards.append(j_score)
    if pair_jaccards:
        top5_self_jaccard.append(sum(pair_jaccards) / len(pair_jaccards))

mean_top5_jaccard = sum(top5_self_jaccard) / len(top5_self_jaccard)

# Compare to random: pick 5 random A folios and compute their pairwise Jaccard
null_jaccards = []
for _ in range(1000):
    random_5 = random.sample(a_folios, 5)
    pair_jaccards = []
    for i in range(len(random_5)):
        for j in range(i+1, len(random_5)):
            j_score = jaccard(a_folio_vocab[random_5[i]], a_folio_vocab[random_5[j]])
            pair_jaccards.append(j_score)
    null_jaccards.append(sum(pair_jaccards) / len(pair_jaccards))

mean_null_jaccard = sum(null_jaccards) / len(null_jaccards)
p_top5 = sum(1 for x in null_jaccards if x >= mean_top5_jaccard) / len(null_jaccards)

print(f"\nTop-5 A matches for each B - mean pairwise Jaccard: {mean_top5_jaccard:.4f}")
print(f"Random 5 A folios - mean pairwise Jaccard: {mean_null_jaccard:.4f}")
print(f"p-value: {p_top5:.4f}")

if mean_top5_jaccard > mean_null_jaccard and p_top5 < 0.05:
    print("  --> TOP MATCHES SHARE VOCABULARY: They cluster in vocabulary space")
elif mean_top5_jaccard < mean_null_jaccard and p_top5 < 0.05:
    print("  --> TOP MATCHES ARE DIVERSE: They cover different vocabulary")
else:
    print("  --> NO SIGNIFICANT PATTERN")

# =============================================================
# STEP 7: Viability analysis
# =============================================================
print("\n" + "="*70)
print("STEP 7: Viability threshold analysis")
print("="*70)

# What fraction of A-B pairs exceed various coverage thresholds?
thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
for thresh in thresholds:
    viable = sum(1 for (a, b), v in overlap_matrix.items() if v['b_coverage'] >= thresh)
    total = len(overlap_matrix)
    pct = 100 * viable / total
    print(f"  Coverage >= {thresh:.0%}: {viable}/{total} pairs ({pct:.1f}%)")

# =============================================================
# STEP 8: Summary
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
FINDINGS:

1. BEST-MATCH CONCENTRATION:
   - Most common best-match A folio: {top_a}
   - It's best for {top_count} B folios
   - Null expectation: ~{mean_null_max:.1f}
   - p-value: {p_value:.4f}
   - {'CLUSTERED' if p_value < 0.05 else 'RANDOM'}

2. TOP-5 VOCABULARY SHARING:
   - Top-5 A matches share vocabulary at: {mean_top5_jaccard:.4f} (Jaccard)
   - Random 5 A folios share at: {mean_null_jaccard:.4f}
   - {'CLUSTERED' if mean_top5_jaccard > mean_null_jaccard else 'DIVERSE'}

3. VIABILITY:
   - Only {sum(1 for (a,b),v in overlap_matrix.items() if v['b_coverage'] >= 0.3)}/{len(overlap_matrix)} pairs have >=30% coverage
   - This is {100*sum(1 for (a,b),v in overlap_matrix.items() if v['b_coverage'] >= 0.3)/len(overlap_matrix):.1f}% of all pairs

INTERPRETATION:
""")

if p_value < 0.05:
    print("Best-match A folios are MORE CONCENTRATED than random.")
    print("This supports SPECIFICITY: certain A folios work with certain B folios.")
else:
    print("Best-match distribution is within random expectation.")
    print("This could mean A records are GENERIC (any works about equally).")

if mean_top5_jaccard < mean_null_jaccard:
    print("\nTop A matches are DIVERSE - they cover different vocabulary.")
    print("This suggests B folios need BROAD coverage, not specific A records.")
elif mean_top5_jaccard > mean_null_jaccard and p_top5 < 0.05:
    print("\nTop A matches SHARE vocabulary - they cluster together.")
    print("This suggests B folios have SPECIFIC vocabulary needs.")
