"""
PP CLASSIFICATION SYSTEM

Build Tier 4 properties for all PP MIDDLEs:
1. Material-association class (ANIMAL/HERB/NEUTRAL/MIXED)
2. Token variant profile (which B tokens each PP enables)
3. Co-occurrence clusters (which PPs appear together)
4. RI containment (which RI contain each PP - for projection)

This creates the foundation for understanding RI through PP composition.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("PP CLASSIFICATION SYSTEM")
print("=" * 70)

# =============================================================================
# STEP 1: IDENTIFY ALL PP MIDDLEs
# =============================================================================
print("\n[1] Identifying PP MIDDLEs...")

# PP = MIDDLEs that appear in both A and B (C498)
a_middles = set()
b_middles = set()

for token in tx.currier_a():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            a_middles.add(m.middle)

for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            b_middles.add(m.middle)

pp_middles = a_middles & b_middles
ri_middles = a_middles - b_middles

print(f"  PP MIDDLEs (A and B): {len(pp_middles)}")
print(f"  RI MIDDLEs (A only): {len(ri_middles)}")

# =============================================================================
# STEP 2: BUILD A RECORD PROFILES FOR MATERIAL CLASSIFICATION
# =============================================================================
print("\n[2] Building A record profiles...")

a_records = defaultdict(lambda: {
    'middles': [],
    'suffixes': [],
    'pp_middles': [],
})

for token in tx.currier_a():
    rid = f"{token.folio}:{token.line}"
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            a_records[rid]['middles'].append(m.middle)
            if m.middle in pp_middles:
                a_records[rid]['pp_middles'].append(m.middle)
        if m.suffix:
            a_records[rid]['suffixes'].append(m.suffix)

print(f"  Total A records: {len(a_records)}")

# =============================================================================
# STEP 3: CLASSIFY RECORDS BY MATERIAL SIGNATURE
# =============================================================================
print("\n[3] Classifying records by material signature...")

ANIMAL_SUFFIXES = {'ey', 'ol'}
HERB_SUFFIXES = {'y', 'dy'}

animal_records = set()
herb_records = set()
neutral_records = set()

for rid, data in a_records.items():
    suffixes = data['suffixes']
    animal_count = sum(1 for s in suffixes if s in ANIMAL_SUFFIXES)
    herb_count = sum(1 for s in suffixes if s in HERB_SUFFIXES)

    if animal_count >= 2 and animal_count > herb_count:
        animal_records.add(rid)
    elif herb_count >= 2 and herb_count > animal_count:
        herb_records.add(rid)
    else:
        neutral_records.add(rid)

print(f"  Animal-signature records: {len(animal_records)}")
print(f"  Herb-signature records: {len(herb_records)}")
print(f"  Neutral records: {len(neutral_records)}")

# =============================================================================
# STEP 4: COMPUTE PP MATERIAL-CLASS ENRICHMENT
# =============================================================================
print("\n[4] Computing PP material-class enrichment...")

# Count PP occurrences in each material class
pp_in_animal = Counter()
pp_in_herb = Counter()
pp_in_neutral = Counter()

for rid in animal_records:
    for pp in a_records[rid]['pp_middles']:
        pp_in_animal[pp] += 1

for rid in herb_records:
    for pp in a_records[rid]['pp_middles']:
        pp_in_herb[pp] += 1

for rid in neutral_records:
    for pp in a_records[rid]['pp_middles']:
        pp_in_neutral[pp] += 1

# Normalize by record count
n_animal = len(animal_records) or 1
n_herb = len(herb_records) or 1
n_neutral = len(neutral_records) or 1

pp_classification = {}

for pp in pp_middles:
    animal_rate = pp_in_animal.get(pp, 0) / n_animal
    herb_rate = pp_in_herb.get(pp, 0) / n_herb
    neutral_rate = pp_in_neutral.get(pp, 0) / n_neutral

    # Compute enrichment ratios
    baseline = (animal_rate + herb_rate + neutral_rate) / 3 or 0.001

    animal_enrichment = animal_rate / baseline if baseline > 0 else 0
    herb_enrichment = herb_rate / baseline if baseline > 0 else 0

    # Classify
    if animal_rate > 0 and herb_rate > 0:
        ratio = animal_rate / herb_rate if herb_rate > 0 else float('inf')
        if ratio > 2.0:
            material_class = 'ANIMAL'
        elif ratio < 0.5:
            material_class = 'HERB'
        else:
            material_class = 'MIXED'
    elif animal_rate > 0:
        material_class = 'ANIMAL'
    elif herb_rate > 0:
        material_class = 'HERB'
    else:
        material_class = 'NEUTRAL'

    pp_classification[pp] = {
        'animal_rate': animal_rate,
        'herb_rate': herb_rate,
        'neutral_rate': neutral_rate,
        'animal_enrichment': animal_enrichment,
        'herb_enrichment': herb_enrichment,
        'animal_herb_ratio': animal_rate / herb_rate if herb_rate > 0 else float('inf'),
        'material_class': material_class,
        'total_occurrences': pp_in_animal.get(pp, 0) + pp_in_herb.get(pp, 0) + pp_in_neutral.get(pp, 0),
    }

# Count by class
class_counts = Counter(p['material_class'] for p in pp_classification.values())
print(f"\n  Material class distribution:")
for cls, count in sorted(class_counts.items()):
    pct = 100 * count / len(pp_classification)
    print(f"    {cls}: {count} ({pct:.1f}%)")

# =============================================================================
# STEP 5: COMPUTE PP CO-OCCURRENCE MATRIX
# =============================================================================
print("\n[5] Computing PP co-occurrence...")

# Build co-occurrence matrix
pp_list = sorted(pp_middles)
pp_to_idx = {pp: i for i, pp in enumerate(pp_list)}
n_pp = len(pp_list)

cooccur = np.zeros((n_pp, n_pp))

for rid, data in a_records.items():
    pps = set(data['pp_middles'])
    for pp1 in pps:
        for pp2 in pps:
            if pp1 in pp_to_idx and pp2 in pp_to_idx:
                cooccur[pp_to_idx[pp1], pp_to_idx[pp2]] += 1

# Normalize to get conditional probabilities P(pp2 | pp1)
row_sums = cooccur.sum(axis=1, keepdims=True)
row_sums[row_sums == 0] = 1  # Avoid division by zero
cooccur_norm = cooccur / row_sums

print(f"  Co-occurrence matrix: {n_pp} x {n_pp}")

# Find top co-occurring pairs
cooccur_pairs = []
for i in range(n_pp):
    for j in range(i+1, n_pp):
        if cooccur[i, j] >= 5:  # Min 5 co-occurrences
            cooccur_pairs.append({
                'pp1': pp_list[i],
                'pp2': pp_list[j],
                'count': int(cooccur[i, j]),
                'p_pp2_given_pp1': cooccur_norm[i, j],
                'p_pp1_given_pp2': cooccur_norm[j, i],
            })

cooccur_pairs.sort(key=lambda x: -x['count'])
print(f"  Strong co-occurrence pairs (n>=5): {len(cooccur_pairs)}")

# =============================================================================
# STEP 6: CLUSTER PPs BY CO-OCCURRENCE PATTERN
# =============================================================================
print("\n[6] Clustering PPs by co-occurrence pattern...")

# Use co-occurrence profile as feature vector
# Filter to PPs with sufficient data
min_occurrences = 10
active_pps = [pp for pp in pp_list if pp_classification[pp]['total_occurrences'] >= min_occurrences]
active_idx = [pp_to_idx[pp] for pp in active_pps]

if len(active_pps) >= 10:
    # Extract co-occurrence submatrix
    cooccur_sub = cooccur_norm[np.ix_(active_idx, active_idx)]

    # Hierarchical clustering
    dist_matrix = pdist(cooccur_sub, metric='cosine')
    dist_matrix = np.nan_to_num(dist_matrix, nan=1.0)  # Handle NaN

    Z = linkage(dist_matrix, method='ward')

    # Cut into clusters
    n_clusters = min(8, len(active_pps) // 5)
    clusters = fcluster(Z, n_clusters, criterion='maxclust')

    # Assign clusters
    for i, pp in enumerate(active_pps):
        pp_classification[pp]['cluster'] = int(clusters[i])

    # Count cluster membership
    cluster_counts = Counter(clusters)
    print(f"  Clusters formed: {n_clusters}")
    for c, count in sorted(cluster_counts.items()):
        print(f"    Cluster {c}: {count} PPs")
else:
    print("  Insufficient data for clustering")

# =============================================================================
# STEP 7: COMPUTE PP TOKEN VARIANT PROFILES
# =============================================================================
print("\n[7] Computing PP token variant profiles...")

# For each PP, find which B tokens become legal when that PP is in the A record
# Build A record → B compatible tokens mapping

a_profiles = {}
for rid, data in a_records.items():
    a_profiles[rid] = {
        'middles': set(data['middles']),
        'pps': set(data['pp_middles']),
    }

# Build B token inventory
b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
        })

# For each PP, find records containing it and their compatible B tokens
pp_token_profiles = {}

for pp in pp_middles:
    records_with_pp = [rid for rid, data in a_records.items() if pp in data['pp_middles']]

    compatible_tokens = Counter()
    for rid in records_with_pp:
        middles = a_profiles[rid]['middles']
        for bt in b_tokens:
            if bt['middle'] in middles:
                compatible_tokens[bt['word']] += 1

    pp_token_profiles[pp] = {
        'n_records': len(records_with_pp),
        'n_compatible_tokens': len(compatible_tokens),
        'top_tokens': compatible_tokens.most_common(10),
    }

print(f"  Token profiles computed for {len(pp_token_profiles)} PPs")

# =============================================================================
# STEP 8: COMPUTE RI CONTAINMENT (PP → RI mapping)
# =============================================================================
print("\n[8] Computing RI containment...")

# For each PP, find which RI MIDDLEs contain it as a substring
pp_in_ri = defaultdict(list)

for ri in ri_middles:
    for pp in pp_middles:
        if pp in ri and len(pp) >= 2:  # PP must be substring of RI
            pp_in_ri[pp].append(ri)

# Add to classification
for pp in pp_middles:
    pp_classification[pp]['ri_containing'] = pp_in_ri.get(pp, [])
    pp_classification[pp]['n_ri_containing'] = len(pp_in_ri.get(pp, []))

# Stats
ri_counts = [len(v) for v in pp_in_ri.values()]
print(f"  PPs that appear in RI: {sum(1 for v in pp_in_ri.values() if v)}")
print(f"  Mean RI per PP: {np.mean(ri_counts):.1f}")
print(f"  Max RI per PP: {max(ri_counts) if ri_counts else 0}")

# =============================================================================
# STEP 9: BUILD FINAL CLASSIFICATION TABLE
# =============================================================================
print("\n" + "=" * 70)
print("PP CLASSIFICATION RESULTS")
print("=" * 70)

# Sort by material class strength
sorted_pps = sorted(pp_classification.items(),
                    key=lambda x: abs(np.log(x[1]['animal_herb_ratio'] + 0.01)),
                    reverse=True)

print("\nTop ANIMAL-associated PPs:")
print(f"{'PP':<12} {'A/H Ratio':<12} {'Occurrences':<12} {'RI Contains':<12}")
print("-" * 50)
animal_pps = [(pp, d) for pp, d in sorted_pps if d['material_class'] == 'ANIMAL']
for pp, d in animal_pps[:15]:
    ratio = d['animal_herb_ratio']
    ratio_str = f"{ratio:.1f}x" if ratio < 1000 else "inf"
    print(f"{pp:<12} {ratio_str:<12} {d['total_occurrences']:<12} {d['n_ri_containing']:<12}")

print("\nTop HERB-associated PPs:")
print(f"{'PP':<12} {'H/A Ratio':<12} {'Occurrences':<12} {'RI Contains':<12}")
print("-" * 50)
herb_pps = [(pp, d) for pp, d in sorted_pps if d['material_class'] == 'HERB']
for pp, d in herb_pps[:15]:
    ratio = 1 / d['animal_herb_ratio'] if d['animal_herb_ratio'] > 0 else float('inf')
    ratio_str = f"{ratio:.1f}x" if ratio < 1000 else "inf"
    print(f"{pp:<12} {ratio_str:<12} {d['total_occurrences']:<12} {d['n_ri_containing']:<12}")

print("\nMIXED PPs (appear in both, no strong preference):")
mixed_pps = [(pp, d) for pp, d in sorted_pps if d['material_class'] == 'MIXED']
print(f"  Count: {len(mixed_pps)}")
if mixed_pps:
    print(f"  Examples: {[pp for pp, _ in mixed_pps[:10]]}")

# =============================================================================
# STEP 10: SAVE RESULTS
# =============================================================================
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

results = {
    'metadata': {
        'n_pp': len(pp_middles),
        'n_ri': len(ri_middles),
        'n_animal_records': len(animal_records),
        'n_herb_records': len(herb_records),
    },
    'class_distribution': dict(class_counts),
    'pp_classification': {
        pp: {
            'material_class': d['material_class'],
            'animal_rate': d['animal_rate'],
            'herb_rate': d['herb_rate'],
            'animal_herb_ratio': d['animal_herb_ratio'] if d['animal_herb_ratio'] != float('inf') else 999,
            'total_occurrences': d['total_occurrences'],
            'cluster': d.get('cluster'),
            'n_ri_containing': d['n_ri_containing'],
            'ri_containing': d['ri_containing'][:10],  # Top 10 only
        }
        for pp, d in pp_classification.items()
    },
    'cooccurrence_pairs': cooccur_pairs[:50],  # Top 50
    'pp_token_profiles': {
        pp: {
            'n_records': d['n_records'],
            'n_compatible_tokens': d['n_compatible_tokens'],
        }
        for pp, d in pp_token_profiles.items()
    },
}

output_path = 'phases/PP_CLASSIFICATION/results/pp_classification.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {output_path}")

# Summary table for quick reference
print("\n" + "=" * 70)
print("SUMMARY: PP MATERIAL-CLASS DISTRIBUTION")
print("=" * 70)

print(f"""
Total PP MIDDLEs: {len(pp_middles)}

| Class   | Count | % of PP | Description |
|---------|-------|---------|-------------|
| ANIMAL  | {class_counts.get('ANIMAL', 0):<5} | {100*class_counts.get('ANIMAL', 0)/len(pp_middles):.1f}%   | >2x enriched in animal-suffix records |
| HERB    | {class_counts.get('HERB', 0):<5} | {100*class_counts.get('HERB', 0)/len(pp_middles):.1f}%   | >2x enriched in herb-suffix records |
| MIXED   | {class_counts.get('MIXED', 0):<5} | {100*class_counts.get('MIXED', 0)/len(pp_middles):.1f}%   | Present in both, no strong preference |
| NEUTRAL | {class_counts.get('NEUTRAL', 0):<5} | {100*class_counts.get('NEUTRAL', 0)/len(pp_middles):.1f}%   | Not enriched in either |

RI Projection Potential:
- {sum(1 for d in pp_classification.values() if d['n_ri_containing'] > 0)} PPs appear in at least one RI
- Mean RI per PP: {np.mean([d['n_ri_containing'] for d in pp_classification.values()]):.1f}
- This enables projecting PP properties onto RI through containment
""")
