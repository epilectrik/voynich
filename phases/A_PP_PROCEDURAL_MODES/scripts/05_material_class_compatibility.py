#!/usr/bin/env python3
"""
Test 5: Material Class Compatibility (C642 Check)

Question: How do procedural modes relate to material class mixing?

C642 establishes that A records actively mix material classes (88.2% heterogeneous).
This test verifies that finding holds within procedural mode clusters.

If procedural modes are about procedure type (not material identity),
material mixing should persist across all clusters.
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

# Load CASC material class definitions
# From CASC: M-A (gallows-initial), M-B (ch/sh-initial), M-C (o-initial), M-D (other)
def get_material_class(prefix):
    """Classify token by material class based on PREFIX."""
    if not prefix:
        return 'M-D'
    if prefix[0] in GALLOWS:
        return 'M-A'
    if prefix in ['ch', 'sh'] or prefix.endswith('ch') or prefix.endswith('sh'):
        return 'M-B'
    if prefix.startswith('o') or prefix.endswith('o'):
        return 'M-C'
    return 'M-D'

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
print("TEST 5: MATERIAL CLASS COMPATIBILITY (C642 CHECK)")
print("="*70)

# Build A folio data with material classes
a_folio_data = defaultdict(lambda: {
    'role_counts': Counter(),
    'material_classes': Counter(),
    'total': 0,
    'paragraphs': []
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

            para_classes = []
            for tok in pp_tokens:
                try:
                    m = morph.extract(tok)
                    if m.prefix:
                        role = get_role(m.prefix)
                        a_folio_data[current_folio]['role_counts'][role] += 1
                        mat_class = get_material_class(m.prefix)
                        a_folio_data[current_folio]['material_classes'][mat_class] += 1
                        para_classes.append(mat_class)
                    a_folio_data[current_folio]['total'] += 1
                except:
                    pass

            if para_classes:
                a_folio_data[current_folio]['paragraphs'].append(para_classes)

        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            tokens = [t.word for t in current_para]
            pp_tokens = tokens[3:-3] if len(tokens) > 6 else (tokens[3:] if len(tokens) > 3 else [])

            para_classes = []
            for tok in pp_tokens:
                try:
                    m = morph.extract(tok)
                    if m.prefix:
                        role = get_role(m.prefix)
                        a_folio_data[current_folio]['role_counts'][role] += 1
                        mat_class = get_material_class(m.prefix)
                        a_folio_data[current_folio]['material_classes'][mat_class] += 1
                        para_classes.append(mat_class)
                    a_folio_data[current_folio]['total'] += 1
                except:
                    pass

            if para_classes:
                a_folio_data[current_folio]['paragraphs'].append(para_classes)

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

    para_classes = []
    for tok in pp_tokens:
        try:
            m = morph.extract(tok)
            if m.prefix:
                role = get_role(m.prefix)
                a_folio_data[current_folio]['role_counts'][role] += 1
                mat_class = get_material_class(m.prefix)
                a_folio_data[current_folio]['material_classes'][mat_class] += 1
                para_classes.append(mat_class)
            a_folio_data[current_folio]['total'] += 1
        except:
            pass

    if para_classes:
        a_folio_data[current_folio]['paragraphs'].append(para_classes)

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
# Compute heterogeneity by cluster
# =========================================================================
print("\n" + "="*70)
print("1. MATERIAL CLASS HETEROGENEITY BY CLUSTER")
print("="*70)

def compute_heterogeneity(paragraphs):
    """Compute what fraction of paragraphs use multiple material classes."""
    if not paragraphs:
        return 0, 0

    heterogeneous = 0
    homogeneous = 0

    for para_classes in paragraphs:
        unique_classes = set(para_classes)
        if len(unique_classes) > 1:
            heterogeneous += 1
        else:
            homogeneous += 1

    total = heterogeneous + homogeneous
    return heterogeneous / total if total > 0 else 0, total

cluster_heterogeneity = {}

for c in [1, 2, 3]:
    cluster_folios = [f for f, cl in folio_cluster.items() if cl == c]

    all_paras = []
    for f in cluster_folios:
        all_paras.extend(a_folio_data[f]['paragraphs'])

    het_rate, n_paras = compute_heterogeneity(all_paras)
    cluster_heterogeneity[c] = {'rate': het_rate, 'n_paragraphs': n_paras}

    print(f"\nCluster {c} ({len(cluster_folios)} folios, {n_paras} paragraphs):")
    print(f"  Heterogeneity rate: {100*het_rate:.1f}%")

# Compare to C642's finding (88.2% heterogeneous)
c642_rate = 0.882
print(f"\nC642 baseline: {100*c642_rate:.1f}% heterogeneous")

# =========================================================================
# Statistical test: Is heterogeneity different across clusters?
# =========================================================================
print("\n" + "="*70)
print("2. HETEROGENEITY VARIATION TEST")
print("="*70)

# Build contingency table
contingency = []
for c in [1, 2, 3]:
    cluster_folios = [f for f, cl in folio_cluster.items() if cl == c]
    all_paras = []
    for f in cluster_folios:
        all_paras.extend(a_folio_data[f]['paragraphs'])

    het_count = sum(1 for p in all_paras if len(set(p)) > 1)
    hom_count = len(all_paras) - het_count
    contingency.append([het_count, hom_count])

chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square (heterogeneity ~ cluster): chi2={chi2:.2f}, p={p_val:.4f}")

if p_val < 0.05:
    print("** Clusters differ in material mixing rate **")
    print("   This VIOLATES C642 expectation if procedural modes are material-independent")
else:
    print("Clusters do NOT differ significantly in material mixing")
    print("   This CONFIRMS C642 compatibility - procedural modes are orthogonal to material class")

# =========================================================================
# Material class distribution by cluster
# =========================================================================
print("\n" + "="*70)
print("3. MATERIAL CLASS DISTRIBUTION BY CLUSTER")
print("="*70)

print(f"\n{'Cluster':<10} {'M-A':<10} {'M-B':<10} {'M-C':<10} {'M-D':<10}")
print("-"*50)

cluster_mat_dist = {}
for c in [1, 2, 3]:
    cluster_folios = [f for f, cl in folio_cluster.items() if cl == c]

    agg_classes = Counter()
    for f in cluster_folios:
        agg_classes.update(a_folio_data[f]['material_classes'])

    total = sum(agg_classes.values())
    dist = {mat: agg_classes.get(mat, 0) / total if total > 0 else 0
            for mat in ['M-A', 'M-B', 'M-C', 'M-D']}
    cluster_mat_dist[c] = dist

    print(f"{c:<10}", end="")
    for mat in ['M-A', 'M-B', 'M-C', 'M-D']:
        print(f"{100*dist[mat]:<10.1f}", end="")
    print()

# Chi-square: do clusters have different material class distributions?
mat_contingency = []
for c in [1, 2, 3]:
    cluster_folios = [f for f, cl in folio_cluster.items() if cl == c]
    agg_classes = Counter()
    for f in cluster_folios:
        agg_classes.update(a_folio_data[f]['material_classes'])
    row = [agg_classes.get(mat, 0) for mat in ['M-A', 'M-B', 'M-C', 'M-D']]
    mat_contingency.append(row)

chi2_mat, p_val_mat, _, _ = stats.chi2_contingency(mat_contingency)
print(f"\nChi-square (material dist ~ cluster): chi2={chi2_mat:.2f}, p={p_val_mat:.4f}")

if p_val_mat < 0.05:
    print("** Clusters have different material class distributions **")
else:
    print("Material class distributions are similar across clusters")

# =========================================================================
# C642 Compatibility Summary
# =========================================================================
print("\n" + "="*70)
print("4. C642 COMPATIBILITY ASSESSMENT")
print("="*70)

all_het_rates = [cluster_heterogeneity[c]['rate'] for c in [1, 2, 3]]
min_het = min(all_het_rates)
max_het = max(all_het_rates)

print(f"""
C642 Key Finding: 88.2% of A records are HETEROGENEOUS (mix material classes)

Our Findings:
  Cluster 1 heterogeneity: {100*cluster_heterogeneity[1]['rate']:.1f}%
  Cluster 2 heterogeneity: {100*cluster_heterogeneity[2]['rate']:.1f}%
  Cluster 3 heterogeneity: {100*cluster_heterogeneity[3]['rate']:.1f}%

  Range: {100*min_het:.1f}% - {100*max_het:.1f}%
  Chi-square (cluster ~ het): p={p_val:.4f}
""")

# Check if all clusters maintain high heterogeneity
all_high_het = all(rate > 0.70 for rate in all_het_rates)
het_uniform = p_val > 0.05

if all_high_het and het_uniform:
    c642_verdict = "FULLY COMPATIBLE"
    c642_explanation = "All clusters maintain high heterogeneity; mixing is procedural-mode independent"
elif all_high_het:
    c642_verdict = "PARTIALLY COMPATIBLE"
    c642_explanation = "All clusters are heterogeneous but rates differ"
else:
    c642_verdict = "POTENTIALLY CONFLICTING"
    c642_explanation = "Some clusters show low heterogeneity"

print(f"C642 Compatibility: {c642_verdict}")
print(f"  {c642_explanation}")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: MATERIAL CLASS COMPATIBILITY")
print("="*70)

if c642_verdict == "FULLY COMPATIBLE":
    verdict = "CONFIRMED"
    explanation = "Procedural modes are orthogonal to material class (C642 compatible)"
elif c642_verdict == "PARTIALLY COMPATIBLE":
    verdict = "SUPPORT"
    explanation = "Procedural modes mostly orthogonal to material class"
else:
    verdict = "CONFLICT"
    explanation = "Procedural modes may be confounded with material class"

print(f"""
VERDICT: {verdict}
  {explanation}

INTERPRETATION:
  If CONFIRMED: Clusters represent PROCEDURE types, not MATERIAL types
  If CONFLICT: Clusters may conflate procedure with material identity

This test validates the expert's reframing:
  "procedural modes independent of specific material identity"
""")

# Save results
output = {
    'cluster_heterogeneity': cluster_heterogeneity,
    'chi_square_heterogeneity': {'chi2': chi2, 'p': p_val},
    'cluster_material_dist': cluster_mat_dist,
    'chi_square_material_dist': {'chi2': chi2_mat, 'p': p_val_mat},
    'c642_compatibility': c642_verdict,
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'material_class_compatibility.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\nResults saved to {output_path}")
