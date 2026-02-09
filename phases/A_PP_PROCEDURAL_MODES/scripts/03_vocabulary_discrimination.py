#!/usr/bin/env python3
"""
Test 3: Vocabulary Discrimination Analysis

Question: How distinctive are cluster MIDDLE inventories?

Tests whether clusters have genuinely different vocabularies or
if the same MIDDLEs appear across all clusters.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats
from scipy.cluster import hierarchy

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

PREFIX_ROLES = {
    'ch': 'CORE', 'sh': 'CORE',
    'qo': 'ESCAPE', 'ok': 'AUXILIARY',
    'ol': 'LINK', 'or': 'LINK',
    'ct': 'CROSS-REF',
    'da': 'CLOSURE', 'do': 'CLOSURE',
}

def get_role(prefix):
    if prefix in PREFIX_ROLES:
        return PREFIX_ROLES[prefix]
    if prefix and len(prefix) >= 2 and prefix[-2:] == 'ch':
        return 'GALLOWS-CH'
    if prefix and prefix.endswith('o') and len(prefix) == 2:
        return 'INPUT'
    return 'UNCLASSIFIED'

print("="*70)
print("TEST 3: VOCABULARY DISCRIMINATION ANALYSIS")
print("="*70)

# Build A folio data with MIDDLE inventories
a_folio_data = defaultdict(lambda: {
    'role_counts': Counter(),
    'middle_counts': Counter(),
    'prefix_counts': Counter(),
    'total': 0
})

current_folio = None
current_para = []
current_line = None

for token in tx.currier_a():
    if '*' in token.word or token.section != 'H':
        continue

    if token.folio != current_folio:
        if current_para:
            tokens = [t.word for t in current_para]
            pp_tokens = tokens[3:-3] if len(tokens) > 6 else (tokens[3:] if len(tokens) > 3 else [])
            for tok in pp_tokens:
                try:
                    m = morph.extract(tok)
                    if m.prefix:
                        role = get_role(m.prefix)
                        a_folio_data[current_folio]['role_counts'][role] += 1
                        a_folio_data[current_folio]['prefix_counts'][m.prefix] += 1
                    if m.middle:
                        a_folio_data[current_folio]['middle_counts'][m.middle] += 1
                    a_folio_data[current_folio]['total'] += 1
                except:
                    pass
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            tokens = [t.word for t in current_para]
            pp_tokens = tokens[3:-3] if len(tokens) > 6 else (tokens[3:] if len(tokens) > 3 else [])
            for tok in pp_tokens:
                try:
                    m = morph.extract(tok)
                    if m.prefix:
                        role = get_role(m.prefix)
                        a_folio_data[current_folio]['role_counts'][role] += 1
                        a_folio_data[current_folio]['prefix_counts'][m.prefix] += 1
                    if m.middle:
                        a_folio_data[current_folio]['middle_counts'][m.middle] += 1
                    a_folio_data[current_folio]['total'] += 1
                except:
                    pass
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

# Final paragraph
if current_para:
    tokens = [t.word for t in current_para]
    pp_tokens = tokens[3:-3] if len(tokens) > 6 else (tokens[3:] if len(tokens) > 3 else [])
    for tok in pp_tokens:
        try:
            m = morph.extract(tok)
            if m.prefix:
                role = get_role(m.prefix)
                a_folio_data[current_folio]['role_counts'][role] += 1
                a_folio_data[current_folio]['prefix_counts'][m.prefix] += 1
            if m.middle:
                a_folio_data[current_folio]['middle_counts'][m.middle] += 1
            a_folio_data[current_folio]['total'] += 1
        except:
            pass

# Cluster folios
roles = ['CORE', 'ESCAPE', 'AUXILIARY', 'LINK', 'CROSS-REF', 'CLOSURE', 'GALLOWS-CH', 'INPUT']
folios = []
feature_matrix = []

for folio, data in a_folio_data.items():
    if data['total'] >= 20:
        folios.append(folio)
        vec = [data['role_counts'].get(r, 0) / data['total'] for r in roles]
        feature_matrix.append(vec)

X = np.array(feature_matrix)
linkage = hierarchy.linkage(X, method='ward')
clusters = hierarchy.fcluster(linkage, t=3, criterion='maxclust')
folio_cluster = {f: int(c) for f, c in zip(folios, clusters)}

print(f"\nFolios clustered: {len(folios)}")

# =========================================================================
# Aggregate MIDDLE inventories by cluster
# =========================================================================
print("\n" + "="*70)
print("1. CLUSTER MIDDLE INVENTORIES")
print("="*70)

cluster_middles = {1: Counter(), 2: Counter(), 3: Counter()}
cluster_totals = {1: 0, 2: 0, 3: 0}

for folio, cluster in folio_cluster.items():
    cluster_middles[cluster].update(a_folio_data[folio]['middle_counts'])
    cluster_totals[cluster] += sum(a_folio_data[folio]['middle_counts'].values())

for c in [1, 2, 3]:
    n_unique = len(cluster_middles[c])
    total = cluster_totals[c]
    print(f"\nCluster {c}:")
    print(f"  Unique MIDDLEs: {n_unique}")
    print(f"  Total MIDDLE tokens: {total}")
    print(f"  Top 5: {', '.join(m for m, _ in cluster_middles[c].most_common(5))}")

# =========================================================================
# Jaccard Similarity Between Clusters
# =========================================================================
print("\n" + "="*70)
print("2. JACCARD SIMILARITY (Vocabulary Overlap)")
print("="*70)

# Using MIDDLEs that appear at least 3 times (filter noise)
cluster_middle_sets = {}
for c in [1, 2, 3]:
    cluster_middle_sets[c] = set(m for m, count in cluster_middles[c].items() if count >= 3)

print(f"\nFiltered MIDDLEs (count >= 3):")
for c in [1, 2, 3]:
    print(f"  Cluster {c}: {len(cluster_middle_sets[c])}")

print(f"\nJaccard Similarity:")
jaccard_scores = {}
for i in [1, 2, 3]:
    for j in range(i+1, 4):
        intersection = cluster_middle_sets[i] & cluster_middle_sets[j]
        union = cluster_middle_sets[i] | cluster_middle_sets[j]
        jaccard = len(intersection) / len(union) if union else 0
        jaccard_scores[(i, j)] = jaccard
        print(f"  Cluster {i} vs {j}: {jaccard:.3f} ({len(intersection)} shared)")

avg_jaccard = np.mean(list(jaccard_scores.values()))
print(f"\nAverage Jaccard: {avg_jaccard:.3f}")

# =========================================================================
# Exclusive MIDDLEs
# =========================================================================
print("\n" + "="*70)
print("3. EXCLUSIVE MIDDLES (appear in only one cluster)")
print("="*70)

exclusive_middles = {}
for c in [1, 2, 3]:
    other_middles = set()
    for other_c in [1, 2, 3]:
        if other_c != c:
            other_middles.update(cluster_middle_sets[other_c])

    exclusive = cluster_middle_sets[c] - other_middles
    exclusive_middles[c] = exclusive

    print(f"\nCluster {c} exclusive MIDDLEs: {len(exclusive)}")
    if exclusive:
        # Sort by count
        exclusive_with_counts = [(m, cluster_middles[c][m]) for m in exclusive]
        exclusive_with_counts.sort(key=lambda x: -x[1])
        for m, count in exclusive_with_counts[:10]:
            print(f"  {m:<12} (n={count})")

# =========================================================================
# Enrichment Analysis
# =========================================================================
print("\n" + "="*70)
print("4. ENRICHMENT ANALYSIS (MIDDLEs enriched >2x in one cluster)")
print("="*70)

enriched_middles = {1: [], 2: [], 3: []}

# All MIDDLEs appearing in any cluster
all_middles = set()
for c in [1, 2, 3]:
    all_middles.update(cluster_middle_sets[c])

for middle in all_middles:
    rates = {}
    for c in [1, 2, 3]:
        count = cluster_middles[c].get(middle, 0)
        total = cluster_totals[c]
        rates[c] = count / total if total > 0 else 0

    # Find if any cluster is enriched
    for c in [1, 2, 3]:
        if rates[c] > 0:
            other_rates = [rates[oc] for oc in [1, 2, 3] if oc != c]
            max_other = max(other_rates) if other_rates else 0
            if max_other > 0:
                enrichment = rates[c] / max_other
                if enrichment > 2.0 and cluster_middles[c].get(middle, 0) >= 5:
                    enriched_middles[c].append((middle, enrichment, cluster_middles[c][middle]))

for c in [1, 2, 3]:
    enriched_middles[c].sort(key=lambda x: -x[1])
    print(f"\nCluster {c} enriched MIDDLEs (>2x, n>=5):")
    for m, ratio, count in enriched_middles[c][:10]:
        print(f"  {m:<12} {ratio:.1f}x (n={count})")

# =========================================================================
# Permutation Test
# =========================================================================
print("\n" + "="*70)
print("5. PERMUTATION TEST (Is discrimination significant?)")
print("="*70)

# Test: Are exclusive MIDDLE counts higher than expected by chance?
observed_exclusive = sum(len(exclusive_middles[c]) for c in [1, 2, 3])

n_permutations = 1000
permuted_exclusive = []

folio_list = list(folio_cluster.keys())
for _ in range(n_permutations):
    # Shuffle cluster assignments
    shuffled_clusters = np.random.permutation(clusters)
    shuffled_folio_cluster = {f: int(c) for f, c in zip(folio_list, shuffled_clusters)}

    # Recompute cluster middles
    perm_cluster_middles = {1: Counter(), 2: Counter(), 3: Counter()}
    for folio, cluster in shuffled_folio_cluster.items():
        perm_cluster_middles[cluster].update(a_folio_data[folio]['middle_counts'])

    # Compute exclusive
    perm_cluster_sets = {}
    for c in [1, 2, 3]:
        perm_cluster_sets[c] = set(m for m, count in perm_cluster_middles[c].items() if count >= 3)

    perm_exclusive_count = 0
    for c in [1, 2, 3]:
        other = set()
        for oc in [1, 2, 3]:
            if oc != c:
                other.update(perm_cluster_sets[oc])
        perm_exclusive_count += len(perm_cluster_sets[c] - other)

    permuted_exclusive.append(perm_exclusive_count)

# P-value
p_value = np.mean([p >= observed_exclusive for p in permuted_exclusive])

print(f"\nObserved exclusive MIDDLEs: {observed_exclusive}")
print(f"Permutation mean: {np.mean(permuted_exclusive):.1f}")
print(f"Permutation std: {np.std(permuted_exclusive):.1f}")
print(f"P-value (one-tailed): {p_value:.4f}")

if p_value < 0.05:
    print("** SIGNIFICANT: Clusters have more exclusive vocabulary than expected by chance **")
else:
    print("Not significant: Vocabulary discrimination may be due to chance")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: VOCABULARY DISCRIMINATION")
print("="*70)

total_exclusive = sum(len(exclusive_middles[c]) for c in [1, 2, 3])
total_enriched = sum(len(enriched_middles[c]) for c in [1, 2, 3])

print(f"""
Jaccard Similarity:
  Average: {avg_jaccard:.3f}
  Interpretation: {"LOW overlap (distinct clusters)" if avg_jaccard < 0.5 else "HIGH overlap (shared vocabulary)"}

Exclusive MIDDLEs:
  Total: {total_exclusive}
  Per cluster: {[len(exclusive_middles[c]) for c in [1, 2, 3]]}

Enriched MIDDLEs (>2x):
  Total: {total_enriched}
  Per cluster: {[len(enriched_middles[c]) for c in [1, 2, 3]]}

Permutation Test:
  P-value: {p_value:.4f}
""")

if p_value < 0.05 and avg_jaccard < 0.6:
    verdict = "CONFIRMED"
    explanation = "Clusters have significantly distinctive vocabularies"
elif p_value < 0.1 or total_exclusive > 30:
    verdict = "SUPPORT"
    explanation = "Some vocabulary discrimination, borderline significance"
else:
    verdict = "NOT SUPPORTED"
    explanation = "Clusters share most vocabulary"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'cluster_middle_counts': {str(c): len(cluster_middles[c]) for c in [1, 2, 3]},
    'cluster_totals': cluster_totals,
    'jaccard_scores': {f"{i}-{j}": v for (i, j), v in jaccard_scores.items()},
    'avg_jaccard': avg_jaccard,
    'exclusive_counts': {str(c): len(exclusive_middles[c]) for c in [1, 2, 3]},
    'exclusive_middles': {str(c): list(exclusive_middles[c])[:20] for c in [1, 2, 3]},
    'enriched_counts': {str(c): len(enriched_middles[c]) for c in [1, 2, 3]},
    'permutation_p_value': p_value,
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'vocabulary_discrimination.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\nResults saved to {output_path}")
