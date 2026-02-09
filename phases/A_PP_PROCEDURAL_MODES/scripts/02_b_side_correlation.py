#!/usr/bin/env python3
"""
Test 2: B-Side Execution Correlation

Question: Do A procedural modes predict B execution characteristics?

If procedural modes have operational meaning, corresponding B folios
should show different execution patterns.
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

# Load class map
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}

# Key classes
FQ_CLASSES = {9, 13, 14, 23}  # Escape/recovery
LINK_CLASS = 29  # Monitoring
EN_CLASSES = {32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49}

# Role taxonomy
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
print("TEST 2: B-SIDE EXECUTION CORRELATION")
print("="*70)

# =========================================================================
# Build A folio PP profiles and clusters (Section H)
# =========================================================================
print("\n[1] Building A folio PP profiles...")

a_folio_data = defaultdict(lambda: {'role_counts': Counter(), 'total': 0})
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
                        a_folio_data[current_folio]['total'] += 1
                except:
                    pass
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
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

# Build feature matrix and cluster
roles = ['CORE', 'ESCAPE', 'AUXILIARY', 'LINK', 'CROSS-REF', 'CLOSURE', 'GALLOWS-CH', 'INPUT']
a_folios = []
feature_matrix = []

for folio, data in a_folio_data.items():
    if data['total'] >= 20:
        a_folios.append(folio)
        vec = [data['role_counts'].get(r, 0) / data['total'] for r in roles]
        feature_matrix.append(vec)

X = np.array(feature_matrix)
linkage = hierarchy.linkage(X, method='ward')
a_clusters = hierarchy.fcluster(linkage, t=3, criterion='maxclust')

a_folio_cluster = {folio: int(c) for folio, c in zip(a_folios, a_clusters)}

print(f"  A folios clustered: {len(a_folios)}")
for c in [1, 2, 3]:
    n = sum(1 for v in a_folio_cluster.values() if v == c)
    print(f"    Cluster {c}: {n} folios")

# =========================================================================
# Build B folio characteristics (Section H)
# =========================================================================
print("\n[2] Building B folio characteristics...")

b_folio_data = defaultdict(list)
b_folio_sections = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    b_folio_data[token.folio].append(token.word)
    if token.folio not in b_folio_sections:
        b_folio_sections[token.folio] = token.section

# Compute B characteristics for Section H folios
b_characteristics = {}

for folio, tokens in b_folio_data.items():
    if b_folio_sections.get(folio) != 'H':
        continue
    if len(tokens) < 50:
        continue

    n = len(tokens)

    # FQ rate
    fq_count = sum(1 for t in tokens if token_to_class.get(t) in FQ_CLASSES)
    fq_rate = fq_count / n

    # LINK rate
    link_count = sum(1 for t in tokens if token_to_class.get(t) == LINK_CLASS)
    link_rate = link_count / n

    # EN rate
    en_count = sum(1 for t in tokens if token_to_class.get(t) in EN_CLASSES)
    en_rate = en_count / n

    # Kernel ratios
    k_chars = sum(t.count('k') for t in tokens)
    h_chars = sum(t.count('h') for t in tokens)
    e_chars = sum(t.count('e') for t in tokens)
    total_kernel = k_chars + h_chars + e_chars

    b_characteristics[folio] = {
        'fq_rate': fq_rate,
        'link_rate': link_rate,
        'en_rate': en_rate,
        'link_fq_ratio': link_rate / fq_rate if fq_rate > 0 else 0,
        'k_ratio': k_chars / total_kernel if total_kernel > 0 else 0,
        'h_ratio': h_chars / total_kernel if total_kernel > 0 else 0,
        'e_ratio': e_chars / total_kernel if total_kernel > 0 else 0,
        'n_tokens': n,
    }

print(f"  B folios with characteristics: {len(b_characteristics)}")

# =========================================================================
# Match A clusters to B characteristics
# =========================================================================
print("\n[3] Matching A clusters to B folios...")

# For each A cluster, get characteristics of B folios in same section
# Since we're in Section H, all B folios are relevant

cluster_b_chars = {1: [], 2: [], 3: []}

# Map A folios to their clusters, then associate with all B folios
for cluster in [1, 2, 3]:
    a_folios_in_cluster = [f for f, c in a_folio_cluster.items() if c == cluster]

    # Get all B characteristics for this section (aggregate approach)
    for b_folio, chars in b_characteristics.items():
        cluster_b_chars[cluster].append(chars)

# Alternative: direct folio matching where possible
# Check if any A folios have same-numbered B folios
direct_matches = {1: [], 2: [], 3: []}
for a_folio, cluster in a_folio_cluster.items():
    # Check for corresponding B folio (same folio number in B)
    if a_folio in b_characteristics:
        direct_matches[cluster].append(b_characteristics[a_folio])

print("\nDirect folio matches (A folio has corresponding B folio):")
for c in [1, 2, 3]:
    print(f"  Cluster {c}: {len(direct_matches[c])} direct matches")

# =========================================================================
# Analysis: Compare B characteristics by A cluster
# =========================================================================
print("\n" + "="*70)
print("B-SIDE CHARACTERISTICS BY A CLUSTER (Direct Matches)")
print("="*70)

if any(len(direct_matches[c]) >= 3 for c in [1, 2, 3]):
    metrics = ['fq_rate', 'link_rate', 'en_rate', 'k_ratio', 'h_ratio', 'e_ratio']

    print(f"\n{'Metric':<15}", end="")
    for c in [1, 2, 3]:
        print(f"{'Cluster '+str(c):>15}", end="")
    print()
    print("-"*60)

    for metric in metrics:
        print(f"{metric:<15}", end="")
        for c in [1, 2, 3]:
            if direct_matches[c]:
                mean_val = np.mean([d[metric] for d in direct_matches[c]])
                print(f"{100*mean_val:>14.1f}%", end="")
            else:
                print(f"{'N/A':>15}", end="")
        print()

    # Kruskal-Wallis test for each metric
    print("\n" + "="*70)
    print("STATISTICAL TESTS (Kruskal-Wallis)")
    print("="*70)

    test_results = {}
    for metric in metrics:
        groups = []
        for c in [1, 2, 3]:
            if len(direct_matches[c]) >= 3:
                groups.append([d[metric] for d in direct_matches[c]])

        if len(groups) >= 2:
            try:
                h_stat, p_val = stats.kruskal(*groups)
                sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
                print(f"\n{metric}:")
                print(f"  H={h_stat:.2f}, p={p_val:.4f} {sig}")
                test_results[metric] = {'H': h_stat, 'p': p_val}

                if p_val < 0.05:
                    # Post-hoc pairwise comparisons
                    for i in range(len(groups)):
                        for j in range(i+1, len(groups)):
                            u_stat, p_pair = stats.mannwhitneyu(groups[i], groups[j], alternative='two-sided')
                            if p_pair < 0.05:
                                print(f"    Cluster {i+1} vs {j+1}: U={u_stat:.0f}, p={p_pair:.4f}")
            except Exception as e:
                print(f"\n{metric}: Test failed ({e})")
                test_results[metric] = {'error': str(e)}
else:
    print("\nInsufficient direct matches for statistical analysis")
    test_results = {}

# =========================================================================
# Alternative: A folio PP profile correlates with section-wide B patterns
# =========================================================================
print("\n" + "="*70)
print("ALTERNATIVE: A PP PROFILE vs B CHARACTERISTICS CORRELATION")
print("="*70)

# For each A folio, compute correlation between its PP profile and section B stats
# This tests if A folios with different PP profiles are associated with different B patterns

# Get section-wide B averages
section_b_avg = {
    'fq_rate': np.mean([d['fq_rate'] for d in b_characteristics.values()]),
    'link_rate': np.mean([d['link_rate'] for d in b_characteristics.values()]),
    'en_rate': np.mean([d['en_rate'] for d in b_characteristics.values()]),
}

print(f"\nSection H B averages:")
for metric, val in section_b_avg.items():
    print(f"  {metric}: {100*val:.1f}%")

# Compare cluster PP profiles to B patterns
print("\nCluster PP profiles vs B execution patterns:")

cluster_profiles = {}
for c in [1, 2, 3]:
    cluster_folios = [f for f, cl in a_folio_cluster.items() if cl == c]
    if cluster_folios:
        agg_roles = Counter()
        total = 0
        for f in cluster_folios:
            agg_roles.update(a_folio_data[f]['role_counts'])
            total += a_folio_data[f]['total']

        profile = {r: agg_roles.get(r, 0) / total for r in roles}
        cluster_profiles[c] = profile

        print(f"\n  Cluster {c}:")
        print(f"    ESCAPE: {100*profile['ESCAPE']:.1f}% (predicts higher FQ?)")
        print(f"    LINK: {100*profile['LINK']:.1f}% (predicts higher LINK?)")
        print(f"    CORE: {100*profile['CORE']:.1f}% (predicts higher EN?)")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: B-SIDE CORRELATION")
print("="*70)

# Count significant results
n_significant = sum(1 for r in test_results.values() if isinstance(r, dict) and r.get('p', 1) < 0.05)

if n_significant >= 2:
    verdict = "CONFIRMED"
    explanation = f"{n_significant} B-side metrics differ significantly by A cluster"
elif n_significant == 1:
    verdict = "SUPPORT"
    explanation = "Weak evidence of B-side correlation"
else:
    verdict = "NOT SUPPORTED"
    explanation = "A clusters do not predict B execution patterns"

print(f"""
Direct matches available: {sum(len(direct_matches[c]) for c in [1, 2, 3])}
Significant B-side differences: {n_significant}

VERDICT: {verdict}
  {explanation}

INTERPRETATION:
  If A procedural modes have operational meaning, we'd expect:
  - HIGH ESCAPE A clusters -> higher FQ rate in B
  - HIGH LINK A clusters -> higher LINK rate in B
  - HIGH CORE A clusters -> higher EN rate in B
""")

# Save results
output = {
    'n_a_folios': len(a_folios),
    'n_b_folios': len(b_characteristics),
    'direct_matches_per_cluster': {str(c): len(direct_matches[c]) for c in [1, 2, 3]},
    'test_results': test_results,
    'cluster_profiles': cluster_profiles,
    'section_b_avg': section_b_avg,
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'b_side_correlation.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\nResults saved to {output_path}")
