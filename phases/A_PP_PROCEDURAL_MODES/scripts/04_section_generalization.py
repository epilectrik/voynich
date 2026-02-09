#!/usr/bin/env python3
"""
Test 4: Section Generalization

Question: Do P and T sections show analogous procedural mode clustering?

If procedural modes are a universal organizational principle,
all sections should show similar clustering patterns.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats
from scipy.cluster import hierarchy
from sklearn.metrics import silhouette_score

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
print("TEST 4: SECTION GENERALIZATION")
print("="*70)

# Build A folio data for ALL sections
a_folio_data = defaultdict(lambda: {
    'role_counts': Counter(),
    'total': 0,
    'section': None
})

current_folio = None
current_para = []
current_line = None
current_section = None

for token in tx.currier_a():
    if '*' in token.word:
        continue

    if token.folio != current_folio:
        if current_para and current_section:
            tokens = [t.word for t in current_para]
            pp_tokens = tokens[3:-3] if len(tokens) > 6 else (tokens[3:] if len(tokens) > 3 else [])
            for tok in pp_tokens:
                try:
                    m = morph.extract(tok)
                    if m.prefix:
                        role = get_role(m.prefix)
                        a_folio_data[current_folio]['role_counts'][role] += 1
                        a_folio_data[current_folio]['total'] += 1
                except:
                    pass
            a_folio_data[current_folio]['section'] = current_section

        current_folio = token.folio
        current_section = token.section
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
                        a_folio_data[current_folio]['total'] += 1
                except:
                    pass
            a_folio_data[current_folio]['section'] = current_section
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

# Final paragraph
if current_para and current_section:
    tokens = [t.word for t in current_para]
    pp_tokens = tokens[3:-3] if len(tokens) > 6 else (tokens[3:] if len(tokens) > 3 else [])
    for tok in pp_tokens:
        try:
            m = morph.extract(tok)
            if m.prefix:
                role = get_role(m.prefix)
                a_folio_data[current_folio]['role_counts'][role] += 1
                a_folio_data[current_folio]['total'] += 1
        except:
            pass
    a_folio_data[current_folio]['section'] = current_section

# Group by section
section_folios = defaultdict(list)
for folio, data in a_folio_data.items():
    if data['total'] >= 20 and data['section']:
        section_folios[data['section']].append(folio)

print("\nFolios per section (with PP data):")
for section in sorted(section_folios.keys()):
    print(f"  {section}: {len(section_folios[section])}")

# =========================================================================
# Cluster each section independently
# =========================================================================
roles = ['CORE', 'ESCAPE', 'AUXILIARY', 'LINK', 'CROSS-REF', 'CLOSURE', 'GALLOWS-CH', 'INPUT']

section_results = {}

for section in ['H', 'P', 'T']:
    folios = section_folios.get(section, [])
    if len(folios) < 6:
        print(f"\n{section}: Insufficient folios ({len(folios)}) for clustering")
        section_results[section] = {'status': 'insufficient_data', 'n_folios': len(folios)}
        continue

    print(f"\n{'='*70}")
    print(f"SECTION {section} ({len(folios)} folios)")
    print("="*70)

    # Build feature matrix
    feature_matrix = []
    folio_labels = []
    for folio in folios:
        data = a_folio_data[folio]
        vec = [data['role_counts'].get(r, 0) / data['total'] for r in roles]
        feature_matrix.append(vec)
        folio_labels.append(folio)

    X = np.array(feature_matrix)

    # Try clustering with k=2,3
    best_k = 2
    best_score = -1

    for k in [2, 3]:
        if len(folios) < k + 2:
            continue

        linkage = hierarchy.linkage(X, method='ward')
        clusters = hierarchy.fcluster(linkage, t=k, criterion='maxclust')

        try:
            score = silhouette_score(X, clusters)
            print(f"\n  k={k}: Silhouette = {score:.3f}")

            if score > best_score:
                best_score = score
                best_k = k
        except:
            pass

    # Use best k for final clustering
    linkage = hierarchy.linkage(X, method='ward')
    clusters = hierarchy.fcluster(linkage, t=best_k, criterion='maxclust')

    # Analyze cluster profiles
    print(f"\n  Best k={best_k}, Silhouette={best_score:.3f}")

    cluster_profiles = {}
    for c in range(1, best_k + 1):
        mask = clusters == c
        cluster_folios = [f for f, m in zip(folio_labels, mask) if m]

        # Aggregate roles
        agg_roles = Counter()
        total = 0
        for f in cluster_folios:
            agg_roles.update(a_folio_data[f]['role_counts'])
            total += a_folio_data[f]['total']

        profile = {r: agg_roles.get(r, 0) / total if total > 0 else 0 for r in roles}
        cluster_profiles[c] = profile

        print(f"\n  Cluster {c} ({len(cluster_folios)} folios):")
        top_roles = sorted(profile.items(), key=lambda x: -x[1])[:3]
        for role, pct in top_roles:
            print(f"    {role}: {100*pct:.1f}%")

    section_results[section] = {
        'status': 'clustered',
        'n_folios': len(folios),
        'best_k': best_k,
        'silhouette': best_score,
        'cluster_profiles': cluster_profiles,
        'cluster_assignments': {f: int(c) for f, c in zip(folio_labels, clusters)},
    }

# =========================================================================
# Compare section cluster profiles
# =========================================================================
print("\n" + "="*70)
print("CROSS-SECTION COMPARISON")
print("="*70)

# Check if H cluster profiles have analogs in P/T
if 'H' in section_results and section_results['H']['status'] == 'clustered':
    h_profiles = section_results['H']['cluster_profiles']

    print("\nSection H cluster profiles (reference):")
    for c, profile in h_profiles.items():
        dominant = max(profile.items(), key=lambda x: x[1])
        print(f"  Cluster {c}: {dominant[0]} dominant ({100*dominant[1]:.1f}%)")

    # Compare to P if available
    if 'P' in section_results and section_results['P']['status'] == 'clustered':
        p_profiles = section_results['P']['cluster_profiles']

        print("\nSection P cluster profiles:")
        for c, profile in p_profiles.items():
            dominant = max(profile.items(), key=lambda x: x[1])
            print(f"  Cluster {c}: {dominant[0]} dominant ({100*dominant[1]:.1f}%)")

        # Check similarity
        print("\nProfile similarity (H vs P):")
        for h_c, h_prof in h_profiles.items():
            for p_c, p_prof in p_profiles.items():
                # Cosine similarity
                h_vec = np.array([h_prof.get(r, 0) for r in roles])
                p_vec = np.array([p_prof.get(r, 0) for r in roles])

                cos_sim = np.dot(h_vec, p_vec) / (np.linalg.norm(h_vec) * np.linalg.norm(p_vec))
                print(f"  H-{h_c} vs P-{p_c}: {cos_sim:.3f}")

# =========================================================================
# Universal vs Section-Specific
# =========================================================================
print("\n" + "="*70)
print("UNIVERSAL vs SECTION-SPECIFIC ANALYSIS")
print("="*70)

# Cluster ALL folios together, ignoring section
all_folios = []
all_features = []
all_sections = []

for folio, data in a_folio_data.items():
    if data['total'] >= 20 and data['section']:
        all_folios.append(folio)
        vec = [data['role_counts'].get(r, 0) / data['total'] for r in roles]
        all_features.append(vec)
        all_sections.append(data['section'])

X_all = np.array(all_features)

# Cluster all together
linkage_all = hierarchy.linkage(X_all, method='ward')
clusters_all = hierarchy.fcluster(linkage_all, t=3, criterion='maxclust')

# Check if clusters align with sections
print("\nCross-section clustering (k=3):")
for c in [1, 2, 3]:
    mask = clusters_all == c
    sections_in_cluster = [s for s, m in zip(all_sections, mask) if m]
    section_counts = Counter(sections_in_cluster)
    print(f"\n  Cluster {c} ({sum(mask)} folios):")
    for s, count in section_counts.most_common():
        print(f"    {s}: {count} ({100*count/sum(mask):.1f}%)")

# Chi-square: do clusters predict section?
contingency = []
for c in [1, 2, 3]:
    row = [sum(1 for s, cl in zip(all_sections, clusters_all) if cl == c and s == sec)
           for sec in ['H', 'P', 'T']]
    contingency.append(row)

chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square (cluster ~ section): chi2={chi2:.2f}, p={p_val:.4f}")

if p_val < 0.05:
    print("** Clusters are section-confounded (not universal) **")
else:
    print("Clusters are NOT section-confounded (may be universal)")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: SECTION GENERALIZATION")
print("="*70)

h_clusterable = 'H' in section_results and section_results['H']['status'] == 'clustered'
p_clusterable = 'P' in section_results and section_results['P']['status'] == 'clustered'

print(f"""
Section H clustering: {section_results.get('H', {}).get('status', 'N/A')}
  Silhouette: {section_results.get('H', {}).get('silhouette', 'N/A')}

Section P clustering: {section_results.get('P', {}).get('status', 'N/A')}
  Silhouette: {section_results.get('P', {}).get('silhouette', 'N/A')}

Section T clustering: {section_results.get('T', {}).get('status', 'N/A')}

Cross-section chi-square: p={p_val:.4f}
""")

if h_clusterable and p_clusterable and p_val > 0.05:
    verdict = "CONFIRMED"
    explanation = "Procedural modes generalize across sections"
elif h_clusterable:
    if p_val < 0.05:
        verdict = "PARTIAL"
        explanation = "H clusters exist but are section-specific"
    else:
        verdict = "SUPPORT"
        explanation = "H clusters exist; P data limited"
else:
    verdict = "NOT SUPPORTED"
    explanation = "Clustering does not replicate across sections"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'section_results': {k: {kk: vv for kk, vv in v.items() if kk != 'cluster_profiles'}
                        for k, v in section_results.items()},
    'chi_square_section_confound': {'chi2': chi2, 'p': p_val},
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'section_generalization.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\nResults saved to {output_path}")
