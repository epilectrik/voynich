#!/usr/bin/env python3
"""
A PP Cluster Characterization

Follow-up to a_pp_processing_correlation.py finding:
Section H has 3 distinct A folio clusters by PP role composition.

Questions:
1. What vocabulary distinguishes these clusters?
2. Do clusters have different MIDDLE inventories (potential sensory terms)?
3. Do clusters differ in paragraph structure (WITH-RI vs WITHOUT-RI)?
4. Can we interpret cluster differences as material-handling categories?
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
sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

# Role taxonomy
PREFIX_ROLES = {
    'ch': 'CORE', 'sh': 'CORE',
    'qo': 'ESCAPE',
    'ok': 'AUXILIARY',
    'ol': 'LINK', 'or': 'LINK',
    'ct': 'CROSS-REF',
    'da': 'CLOSURE', 'do': 'CLOSURE',
    'kch': 'GALLOWS-CH', 'tch': 'GALLOWS-CH', 'pch': 'GALLOWS-CH',
    'fch': 'GALLOWS-CH', 'sch': 'GALLOWS-CH', 'dch': 'GALLOWS-CH',
    'po': 'INPUT', 'so': 'INPUT', 'to': 'INPUT', 'ko': 'INPUT',
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
print("A PP CLUSTER CHARACTERIZATION")
print("="*70)

# Build A paragraph data per folio (Section H only)
a_folio_data = defaultdict(lambda: {
    'paragraphs': [],
    'pp_tokens': [],
    'prefix_counts': Counter(),
    'middle_counts': Counter(),
    'role_counts': Counter(),
    'with_ri': 0,
    'without_ri': 0,
})

current_folio = None
current_para = []
current_line = None
current_section = None

for token in tx.currier_a():
    if '*' in token.word:
        continue
    if token.section != 'H':
        continue

    if token.folio != current_folio:
        if current_para and current_section == 'H':
            a_folio_data[current_folio]['paragraphs'].append([t.word for t in current_para])
        current_folio = token.folio
        current_section = token.section
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            if current_para:
                a_folio_data[current_folio]['paragraphs'].append([t.word for t in current_para])
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para and current_section == 'H':
    a_folio_data[current_folio]['paragraphs'].append([t.word for t in current_para])

# Process each folio
for folio, data in a_folio_data.items():
    for para in data['paragraphs']:
        # Check if WITH-RI or WITHOUT-RI
        if len(para) > 0:
            first_word = para[0]
            try:
                m = morph.extract(first_word)
                ri_prefixes = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh'}
                if m.prefix in ri_prefixes:
                    data['with_ri'] += 1
                else:
                    data['without_ri'] += 1
            except:
                data['without_ri'] += 1

        # Extract PP tokens (middle zone)
        if len(para) > 6:
            pp_tokens = para[3:-3]
        elif len(para) > 3:
            pp_tokens = para[3:]
        else:
            pp_tokens = []

        data['pp_tokens'].extend(pp_tokens)

        for token in pp_tokens:
            try:
                m = morph.extract(token)
                if m.prefix:
                    data['prefix_counts'][m.prefix] += 1
                    role = get_role(m.prefix)
                    data['role_counts'][role] += 1
                if m.middle:
                    data['middle_counts'][m.middle] += 1
            except:
                pass

# Filter to folios with sufficient data
folios = []
for folio, data in a_folio_data.items():
    total_pp = sum(data['role_counts'].values())
    if total_pp >= 20:
        data['total_pp'] = total_pp
        folios.append(folio)

print(f"\nSection H folios with PP data: {len(folios)}")

# Build feature matrix for clustering
roles = ['CORE', 'ESCAPE', 'AUXILIARY', 'LINK', 'CROSS-REF', 'CLOSURE', 'GALLOWS-CH', 'INPUT']

feature_matrix = []
folio_labels = []

for folio in folios:
    data = a_folio_data[folio]
    total = data['total_pp']
    feature_vec = [data['role_counts'].get(r, 0) / total for r in roles]
    feature_matrix.append(feature_vec)
    folio_labels.append(folio)

X = np.array(feature_matrix)

# Hierarchical clustering
linkage = hierarchy.linkage(X, method='ward')
clusters = hierarchy.fcluster(linkage, t=3, criterion='maxclust')

# =========================================================================
# Cluster Analysis
# =========================================================================
print("\n" + "="*70)
print("CLUSTER PROFILES")
print("="*70)

cluster_data = defaultdict(lambda: {
    'folios': [],
    'prefix_counts': Counter(),
    'middle_counts': Counter(),
    'role_counts': Counter(),
    'with_ri': 0,
    'without_ri': 0,
    'total_pp': 0,
})

for i, (folio, cluster) in enumerate(zip(folio_labels, clusters)):
    data = a_folio_data[folio]
    cd = cluster_data[cluster]

    cd['folios'].append(folio)
    cd['prefix_counts'].update(data['prefix_counts'])
    cd['middle_counts'].update(data['middle_counts'])
    cd['role_counts'].update(data['role_counts'])
    cd['with_ri'] += data['with_ri']
    cd['without_ri'] += data['without_ri']
    cd['total_pp'] += data['total_pp']

# Print cluster profiles
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    n_folios = len(cd['folios'])
    total_para = cd['with_ri'] + cd['without_ri']
    with_ri_pct = 100 * cd['with_ri'] / total_para if total_para > 0 else 0

    print(f"\n{'='*50}")
    print(f"CLUSTER {cluster_id} ({n_folios} folios)")
    print(f"{'='*50}")

    # Role distribution
    print(f"\nRole Distribution:")
    total = sum(cd['role_counts'].values())
    for role in roles:
        count = cd['role_counts'].get(role, 0)
        pct = 100 * count / total if total > 0 else 0
        bar = '#' * int(pct / 2)
        print(f"  {role:<12} {pct:>5.1f}% {bar}")

    # WITH-RI vs WITHOUT-RI
    print(f"\nParagraph Structure:")
    print(f"  WITH-RI: {cd['with_ri']} ({with_ri_pct:.1f}%)")
    print(f"  WITHOUT-RI: {cd['without_ri']} ({100-with_ri_pct:.1f}%)")

    # Top prefixes
    print(f"\nTop PREFIXes:")
    for prefix, count in cd['prefix_counts'].most_common(8):
        pct = 100 * count / cd['total_pp']
        role = get_role(prefix)
        print(f"  {prefix:<6} {pct:>5.1f}% ({role})")

    # Top MIDDLEs (potential sensory vocabulary)
    print(f"\nTop MIDDLEs (potential material-specific terms):")
    for middle, count in cd['middle_counts'].most_common(10):
        pct = 100 * count / cd['total_pp']
        print(f"  {middle:<10} {pct:>5.1f}%")

    # Folios
    print(f"\nFolios: {', '.join(sorted(cd['folios'])[:10])}...")

# =========================================================================
# Distinctive Vocabulary
# =========================================================================
print("\n" + "="*70)
print("DISTINCTIVE VOCABULARY BY CLUSTER")
print("="*70)

# Find MIDDLEs enriched in each cluster vs others
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    other_middles = Counter()
    other_total = 0

    for other_id in cluster_data:
        if other_id != cluster_id:
            other_middles.update(cluster_data[other_id]['middle_counts'])
            other_total += cluster_data[other_id]['total_pp']

    cluster_total = cd['total_pp']

    # Find enriched MIDDLEs
    enriched = []
    for middle in cd['middle_counts']:
        cluster_count = cd['middle_counts'][middle]
        other_count = other_middles.get(middle, 0)

        if cluster_count >= 5:
            cluster_rate = cluster_count / cluster_total
            other_rate = other_count / other_total if other_total > 0 else 0.0001

            if other_rate > 0:
                ratio = cluster_rate / other_rate
                if ratio > 2.0:
                    enriched.append((middle, ratio, cluster_count))

    enriched.sort(key=lambda x: -x[1])

    print(f"\nCluster {cluster_id} ENRICHED MIDDLEs (>2x vs others):")
    if enriched:
        for middle, ratio, count in enriched[:10]:
            print(f"  {middle:<12} {ratio:.1f}x (n={count})")
    else:
        print("  (none found)")

# =========================================================================
# Cluster-Exclusive Vocabulary
# =========================================================================
print("\n" + "="*70)
print("CLUSTER-EXCLUSIVE VOCABULARY")
print("="*70)

for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    cluster_middles = set(m for m, c in cd['middle_counts'].items() if c >= 3)

    other_middles = set()
    for other_id in cluster_data:
        if other_id != cluster_id:
            other_middles.update(m for m, c in cluster_data[other_id]['middle_counts'].items() if c >= 3)

    exclusive = cluster_middles - other_middles

    print(f"\nCluster {cluster_id} exclusive MIDDLEs (n>3): {len(exclusive)}")
    if exclusive:
        # Show top by count
        exclusive_counts = [(m, cd['middle_counts'][m]) for m in exclusive]
        exclusive_counts.sort(key=lambda x: -x[1])
        for middle, count in exclusive_counts[:10]:
            print(f"  {middle:<12} (n={count})")

# =========================================================================
# Statistical Comparison
# =========================================================================
print("\n" + "="*70)
print("STATISTICAL COMPARISON")
print("="*70)

# Test 1: WITH-RI ratio difference
print("\nWITH-RI ratio by cluster:")
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    total = cd['with_ri'] + cd['without_ri']
    rate = cd['with_ri'] / total if total > 0 else 0
    print(f"  Cluster {cluster_id}: {rate:.1%} WITH-RI")

# Chi-square test
contingency = []
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    contingency.append([cd['with_ri'], cd['without_ri']])

chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square test (WITH-RI ~ Cluster): chi2={chi2:.2f}, p={p:.4f}")
if p < 0.05:
    print("  ** Significant: Clusters differ in WITH-RI/WITHOUT-RI ratio **")

# Test 2: MIDDLE diversity
print("\nMIDDLE diversity by cluster:")
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    diversity = len(cd['middle_counts']) / cd['total_pp']
    print(f"  Cluster {cluster_id}: {diversity:.4f} (unique/total)")

# =========================================================================
# Interpretation
# =========================================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("""
CLUSTER CHARACTERIZATION:

If clusters represent different material-handling categories:
- Different role composition = different operational emphasis
- Different MIDDLE inventory = different procedural vocabulary
- Different WITH-RI ratio = different record structure

SENSORY CRITERIA HYPOTHESIS:

If A PP encodes sensory feedback criteria, we'd expect:
1. Clusters to have distinctive MIDDLE vocabularies (CHECK: exclusive MIDDLEs found)
2. Role composition to reflect monitoring needs (CHECK: LINK/CROSS-REF variation)
3. Clusters to map to material property categories

BRUNSCHWIG ALIGNMENT:

- HIGH CLOSURE cluster = Output-focused materials (distillates, products)
- HIGH ESCAPE cluster = Hazardous materials (volatile, unstable)
- HIGH CROSS-REF cluster = Related/indexed materials (plant families)
- BALANCED cluster = Standard processing materials
""")

# =========================================================================
# Detailed Cluster Comparison Table
# =========================================================================
print("\n" + "="*70)
print("CLUSTER COMPARISON TABLE")
print("="*70)

print(f"\n{'Metric':<25}", end="")
for cluster_id in sorted(cluster_data.keys()):
    print(f"{'Cluster '+str(cluster_id):>15}", end="")
print()
print("-"*70)

# Role percentages
for role in ['CORE', 'ESCAPE', 'CLOSURE', 'CROSS-REF', 'LINK', 'GALLOWS-CH']:
    print(f"{role:<25}", end="")
    for cluster_id in sorted(cluster_data.keys()):
        cd = cluster_data[cluster_id]
        total = sum(cd['role_counts'].values())
        pct = 100 * cd['role_counts'].get(role, 0) / total if total > 0 else 0
        print(f"{pct:>14.1f}%", end="")
    print()

print("-"*70)

# WITH-RI rate
print(f"{'WITH-RI rate':<25}", end="")
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    total = cd['with_ri'] + cd['without_ri']
    rate = 100 * cd['with_ri'] / total if total > 0 else 0
    print(f"{rate:>14.1f}%", end="")
print()

# MIDDLE diversity
print(f"{'MIDDLE diversity':<25}", end="")
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    div = len(cd['middle_counts']) / cd['total_pp']
    print(f"{div:>14.4f}", end="")
print()

# Unique MIDDLEs
print(f"{'Unique MIDDLEs':<25}", end="")
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    print(f"{len(cd['middle_counts']):>15}", end="")
print()

# Total PP
print(f"{'Total PP tokens':<25}", end="")
for cluster_id in sorted(cluster_data.keys()):
    cd = cluster_data[cluster_id]
    print(f"{cd['total_pp']:>15}", end="")
print()

# Save results
output = {
    'n_folios': len(folios),
    'n_clusters': len(cluster_data),
    'clusters': {},
}

for cluster_id, cd in cluster_data.items():
    output['clusters'][str(cluster_id)] = {
        'folios': cd['folios'],
        'n_folios': len(cd['folios']),
        'with_ri_rate': cd['with_ri'] / (cd['with_ri'] + cd['without_ri']) if (cd['with_ri'] + cd['without_ri']) > 0 else 0,
        'top_prefixes': cd['prefix_counts'].most_common(10),
        'top_middles': cd['middle_counts'].most_common(10),
        'role_dist': dict(cd['role_counts']),
    }

output_path = Path(__file__).parent.parent / 'results' / 'a_pp_cluster_characterization.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n\nResults saved to {output_path}")
