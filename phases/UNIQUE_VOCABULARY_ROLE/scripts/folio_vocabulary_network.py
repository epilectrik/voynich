"""
FOLIO VOCABULARY NETWORK

Tests the structural architecture of vocabulary sharing across B folios.
4 sections: section-controlled adjacency, similarity network/clustering,
vocabulary gradient, removal impact.

Phase: UNIQUE_VOCABULARY_ROLE
"""

import os
import sys
import json
import numpy as np
from collections import defaultdict, Counter
from scipy.stats import spearmanr
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# Load shared data
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = ctm['token_to_class']
class_to_role = ctm['class_to_role']
ROLE_MAP = {
    'ENERGY_OPERATOR': 'EN',
    'AUXILIARY': 'AX',
    'FREQUENT_OPERATOR': 'FQ',
    'CORE_CONTROL': 'CC',
    'FLOW_OPERATOR': 'FL'
}

with open('phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json') as f:
    regime_data = json.load(f)

folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

tx = Transcript()
morph = Morphology()

# ============================================================
# BUILD BASE DATA
# ============================================================

folio_middles = defaultdict(set)
folio_tokens = defaultdict(list)
folio_section = {}

for token in tx.currier_b():
    word = token.word
    if not word or not word.strip():
        continue
    m = morph.extract(word)
    if not m.middle:
        continue

    folio_middles[token.folio].add(m.middle)
    folio_section[token.folio] = token.section

    if word in token_to_class:
        cls = str(token_to_class[word])
        role = ROLE_MAP.get(class_to_role.get(cls, ''), 'UN')
    else:
        role = 'UN'

    folio_tokens[token.folio].append({
        'word': word,
        'middle': m.middle,
        'role': role
    })

# Unique/shared MIDDLE classification
middle_folio_count = defaultdict(int)
for folio, middles in folio_middles.items():
    for mid in middles:
        middle_folio_count[mid] += 1

unique_middles = set(mid for mid, cnt in middle_folio_count.items() if cnt == 1)
shared_middles = set(mid for mid, cnt in middle_folio_count.items() if cnt >= 2)

# Folio ordering (manuscript order from transcript iteration)
folio_order = []
seen = set()
for token in tx.currier_b():
    if token.folio not in seen:
        seen.add(token.folio)
        folio_order.append(token.folio)

folios = folio_order
n_folios = len(folios)

print("=" * 70)
print("FOLIO VOCABULARY NETWORK")
print("=" * 70)
print(f"B folios: {n_folios}")
print(f"Total distinct MIDDLEs: {len(middle_folio_count)}")
print(f"Unique MIDDLEs: {len(unique_middles)}")
print(f"Shared MIDDLEs: {len(shared_middles)}")

# ============================================================
# SECTION 1: SECTION-CONTROLLED ADJACENCY EFFECT
# ============================================================

print("\n" + "=" * 70)
print("SECTION 1: SECTION-CONTROLLED ADJACENCY EFFECT")
print("Does C533's 1.30x adjacency ratio survive section control?")
print("=" * 70)

# Build Jaccard matrix
jaccard_matrix = np.zeros((n_folios, n_folios))
for i in range(n_folios):
    for j in range(n_folios):
        if i == j:
            jaccard_matrix[i, j] = 1.0
        else:
            m1 = folio_middles[folios[i]]
            m2 = folio_middles[folios[j]]
            inter = len(m1 & m2)
            union = len(m1 | m2)
            jaccard_matrix[i, j] = inter / union if union > 0 else 0

# Classify pairs
adjacent_jaccards = []
same_section_nonadj_jaccards = []
diff_section_nonadj_jaccards = []
adjacent_same_section = []
adjacent_diff_section = []

for i in range(n_folios - 1):
    j = i + 1
    jac = jaccard_matrix[i, j]
    sec_i = folio_section.get(folios[i], '')
    sec_j = folio_section.get(folios[j], '')

    adjacent_jaccards.append(jac)
    if sec_i == sec_j:
        adjacent_same_section.append(jac)
    else:
        adjacent_diff_section.append(jac)

for i in range(n_folios):
    for j in range(i + 2, n_folios):  # skip adjacent
        jac = jaccard_matrix[i, j]
        sec_i = folio_section.get(folios[i], '')
        sec_j = folio_section.get(folios[j], '')
        if sec_i == sec_j:
            same_section_nonadj_jaccards.append(jac)
        else:
            diff_section_nonadj_jaccards.append(jac)

print(f"\nAdjacent folio Jaccard:")
print(f"  All adjacent: {np.mean(adjacent_jaccards):.4f} (n={len(adjacent_jaccards)})")
print(f"  Adjacent same-section: {np.mean(adjacent_same_section):.4f} (n={len(adjacent_same_section)})")
if adjacent_diff_section:
    print(f"  Adjacent diff-section: {np.mean(adjacent_diff_section):.4f} (n={len(adjacent_diff_section)})")

print(f"\nNon-adjacent folio Jaccard:")
print(f"  Same-section non-adjacent: {np.mean(same_section_nonadj_jaccards):.4f} (n={len(same_section_nonadj_jaccards)})")
print(f"  Diff-section non-adjacent: {np.mean(diff_section_nonadj_jaccards):.4f} (n={len(diff_section_nonadj_jaccards)})")

# Key ratio: adjacent same-section vs same-section non-adjacent
if same_section_nonadj_jaccards:
    adj_ratio = np.mean(adjacent_same_section) / np.mean(same_section_nonadj_jaccards) if np.mean(same_section_nonadj_jaccards) > 0 else float('inf')
    print(f"\nSection-controlled adjacency ratio: {adj_ratio:.3f}x")
    print(f"(Adjacent same-section / Same-section non-adjacent)")
    if adj_ratio > 1.05:
        print("  -> Genuine adjacency effect BEYOND section")
    else:
        print("  -> Section FULLY explains adjacency effect")

# Overall comparison
overall_nonadj = [j for j in same_section_nonadj_jaccards + diff_section_nonadj_jaccards]
overall_ratio = np.mean(adjacent_jaccards) / np.mean(overall_nonadj) if np.mean(overall_nonadj) > 0 else float('inf')
print(f"\nRaw adjacency ratio (all): {overall_ratio:.3f}x")
print(f"(C533 reported 1.30x for class overlap, not MIDDLE Jaccard)")

# ============================================================
# SECTION 2: FOLIO SIMILARITY NETWORK
# ============================================================

print("\n" + "=" * 70)
print("SECTION 2: FOLIO SIMILARITY NETWORK")
print("Cluster folios by vocabulary similarity")
print("=" * 70)

# Convert Jaccard to distance
dist_matrix = 1.0 - jaccard_matrix
np.fill_diagonal(dist_matrix, 0)

# Condensed distance matrix for hierarchical clustering
condensed = squareform(dist_matrix)

# Ward linkage
Z = linkage(condensed, method='ward')

# Silhouette scores for k=2..10
from sklearn.metrics import silhouette_score, adjusted_rand_score

best_k = 2
best_sil = -1
sil_scores = {}

for k in range(2, 11):
    labels = fcluster(Z, t=k, criterion='maxclust')
    if len(set(labels)) >= 2:
        sil = silhouette_score(dist_matrix, labels, metric='precomputed')
        sil_scores[k] = round(sil, 4)
        if sil > best_sil:
            best_sil = sil
            best_k = k

print(f"\nSilhouette scores:")
for k, s in sorted(sil_scores.items()):
    marker = " <-- best" if k == best_k else ""
    print(f"  k={k}: {s:.4f}{marker}")

# Best clustering
best_labels = fcluster(Z, t=best_k, criterion='maxclust')

# ARI with section
section_labels = [folio_section.get(f, 'X') for f in folios]
unique_sections = sorted(set(section_labels))
section_numeric = [unique_sections.index(s) for s in section_labels]
ari_section = adjusted_rand_score(section_numeric, best_labels)

# ARI with REGIME
regime_labels = [folio_to_regime.get(f, 'X') for f in folios]
unique_regimes = sorted(set(regime_labels))
regime_numeric = [unique_regimes.index(r) for r in regime_labels]
ari_regime = adjusted_rand_score(regime_numeric, best_labels)

print(f"\nBest clustering: k={best_k}, silhouette={best_sil:.4f}")
print(f"ARI with section: {ari_section:.4f}")
print(f"ARI with REGIME: {ari_regime:.4f}")

# Cluster composition
print(f"\nCluster composition (k={best_k}):")
for c in range(1, best_k + 1):
    cluster_folios = [folios[i] for i in range(n_folios) if best_labels[i] == c]
    cluster_sections = Counter(folio_section.get(f, 'X') for f in cluster_folios)
    cluster_regimes = Counter(folio_to_regime.get(f, 'X') for f in cluster_folios)
    print(f"\n  Cluster {c} ({len(cluster_folios)} folios):")
    print(f"    Sections: {dict(cluster_sections)}")
    print(f"    REGIMEs: {dict(cluster_regimes)}")

# Most isolated and most central folios
mean_similarity = []
for i in range(n_folios):
    others = [jaccard_matrix[i, j] for j in range(n_folios) if i != j]
    mean_similarity.append(np.mean(others))

most_isolated_idx = np.argmin(mean_similarity)
most_central_idx = np.argmax(mean_similarity)

print(f"\nMost isolated folio: {folios[most_isolated_idx]} (mean Jaccard={mean_similarity[most_isolated_idx]:.4f})")
print(f"  Section: {folio_section.get(folios[most_isolated_idx], '?')}")
print(f"  REGIME: {folio_to_regime.get(folios[most_isolated_idx], '?')}")
print(f"  Unique MIDDLEs: {len(folio_middles[folios[most_isolated_idx]] & unique_middles)}")

print(f"\nMost central folio: {folios[most_central_idx]} (mean Jaccard={mean_similarity[most_central_idx]:.4f})")
print(f"  Section: {folio_section.get(folios[most_central_idx], '?')}")
print(f"  REGIME: {folio_to_regime.get(folios[most_central_idx], '?')}")
print(f"  Unique MIDDLEs: {len(folio_middles[folios[most_central_idx]] & unique_middles)}")

# ============================================================
# SECTION 3: VOCABULARY GRADIENT
# ============================================================

print("\n" + "=" * 70)
print("SECTION 3: VOCABULARY GRADIENT")
print("Does unique vocabulary density vary with manuscript position?")
print("=" * 70)

folio_unique_counts = [len(folio_middles[f] & unique_middles) for f in folios]
folio_token_counts = [len(folio_tokens[f]) for f in folios]
folio_unique_dens = [uc / tc if tc > 0 else 0 for uc, tc in zip(folio_unique_counts, folio_token_counts)]
positions = list(range(n_folios))

rho_count, p_count = spearmanr(positions, folio_unique_counts)
rho_dens, p_dens = spearmanr(positions, folio_unique_dens)

print(f"\nUnique count vs manuscript position: rho={rho_count:.3f}, p={p_count:.6f}")
print(f"Unique density vs manuscript position: rho={rho_dens:.3f}, p={p_dens:.6f}")

# Per-section unique density
print(f"\nPer-section unique MIDDLE density:")
for sec in sorted(set(folio_section.values())):
    sec_folios = [f for f in folios if folio_section.get(f) == sec]
    sec_dens = [folio_unique_dens[folios.index(f)] for f in sec_folios]
    print(f"  {sec}: mean={100*np.mean(sec_dens):.2f}%, std={100*np.std(sec_dens):.2f}%, n={len(sec_dens)}")

# Per-REGIME unique density
print(f"\nPer-REGIME unique MIDDLE density:")
for reg in sorted(set(folio_to_regime.values())):
    reg_folios = [f for f in folios if folio_to_regime.get(f) == reg]
    reg_dens = [folio_unique_dens[folios.index(f)] for f in reg_folios]
    print(f"  {reg}: mean={100*np.mean(reg_dens):.2f}%, std={100*np.std(reg_dens):.2f}%, n={len(reg_dens)}")

# ============================================================
# SECTION 4: VOCABULARY REMOVAL IMPACT
# ============================================================

print("\n" + "=" * 70)
print("SECTION 4: VOCABULARY REMOVAL IMPACT")
print("What happens if unique MIDDLEs are removed from each folio?")
print("=" * 70)

survival_rates = []
role_shifts = []
roles = ['EN', 'AX', 'FQ', 'FL', 'CC', 'UN']

for f in folios:
    tokens = folio_tokens[f]
    total = len(tokens)
    if total == 0:
        continue

    # With unique MIDDLEs
    all_role_dist = Counter(t['role'] for t in tokens)
    # Without unique MIDDLEs
    shared_tokens = [t for t in tokens if t['middle'] not in unique_middles]
    shared_total = len(shared_tokens)
    shared_role_dist = Counter(t['role'] for t in shared_tokens)

    survival = shared_total / total if total > 0 else 1
    survival_rates.append(survival)

    # Role shift: max absolute change in role proportion
    max_shift = 0
    for role in roles:
        orig_prop = all_role_dist[role] / total if total else 0
        new_prop = shared_role_dist[role] / shared_total if shared_total else 0
        shift = abs(orig_prop - new_prop)
        if shift > max_shift:
            max_shift = shift
    role_shifts.append(max_shift)

print(f"\nToken survival after removing unique MIDDLEs:")
print(f"  Mean: {100*np.mean(survival_rates):.1f}%")
print(f"  Min: {100*np.min(survival_rates):.1f}%")
print(f"  Max: {100*np.max(survival_rates):.1f}%")
print(f"  Folios retaining >95%: {sum(1 for s in survival_rates if s > 0.95)}/{n_folios}")

print(f"\nMax role proportion shift per folio:")
print(f"  Mean: {100*np.mean(role_shifts):.2f} pp")
print(f"  Max: {100*np.max(role_shifts):.2f} pp")
print(f"  Folios with shift >5 pp: {sum(1 for s in role_shifts if s > 0.05)}/{n_folios}")

# Do ALL folios retain all 5 ICC roles after removal?
roles_lost = 0
for f in folios:
    shared_tokens = [t for t in folio_tokens[f] if t['middle'] not in unique_middles]
    roles_present = set(t['role'] for t in shared_tokens)
    classified_roles = roles_present - {'UN'}
    if len(classified_roles) < 5:
        roles_lost += 1

print(f"\nFolios losing ICC role coverage after removal: {roles_lost}/{n_folios}")

# Aggregate role impact
print(f"\nAggregate role distribution shift:")
all_total = sum(len(folio_tokens[f]) for f in folios)
shared_total_global = sum(1 for f in folios for t in folio_tokens[f] if t['middle'] not in unique_middles)
print(f"  Total tokens: {all_total} -> {shared_total_global} ({100*shared_total_global/all_total:.1f}%)")

all_role_global = Counter()
shared_role_global = Counter()
for f in folios:
    for t in folio_tokens[f]:
        all_role_global[t['role']] += 1
        if t['middle'] not in unique_middles:
            shared_role_global[t['role']] += 1

print(f"\n{'Role':<6} {'With unique':>12} {'Without':>12} {'Shift (pp)':>12}")
for role in roles:
    orig = 100 * all_role_global[role] / all_total
    new = 100 * shared_role_global[role] / shared_total_global if shared_total_global else 0
    shift = new - orig
    print(f"{role:<6} {orig:>11.1f}% {new:>11.1f}% {shift:>+11.2f}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'adjacency': {
        'all_adjacent_mean': round(np.mean(adjacent_jaccards), 4),
        'adjacent_same_section_mean': round(np.mean(adjacent_same_section), 4),
        'adjacent_diff_section_mean': round(np.mean(adjacent_diff_section), 4) if adjacent_diff_section else None,
        'same_section_nonadj_mean': round(np.mean(same_section_nonadj_jaccards), 4),
        'diff_section_nonadj_mean': round(np.mean(diff_section_nonadj_jaccards), 4),
        'section_controlled_ratio': round(adj_ratio, 3),
        'raw_ratio': round(overall_ratio, 3)
    },
    'clustering': {
        'best_k': best_k,
        'best_silhouette': round(best_sil, 4),
        'ari_section': round(ari_section, 4),
        'ari_regime': round(ari_regime, 4),
        'silhouette_scores': sil_scores
    },
    'gradient': {
        'count_vs_position_rho': round(rho_count, 3),
        'count_vs_position_p': round(p_count, 6),
        'density_vs_position_rho': round(rho_dens, 3),
        'density_vs_position_p': round(p_dens, 6)
    },
    'removal_impact': {
        'mean_survival_pct': round(100 * np.mean(survival_rates), 1),
        'min_survival_pct': round(100 * np.min(survival_rates), 1),
        'folios_above_95pct': sum(1 for s in survival_rates if s > 0.95),
        'mean_max_role_shift_pp': round(100 * np.mean(role_shifts), 2),
        'max_role_shift_pp': round(100 * np.max(role_shifts), 2),
        'folios_losing_role_coverage': roles_lost
    },
    'network': {
        'most_isolated': folios[most_isolated_idx],
        'most_isolated_similarity': round(mean_similarity[most_isolated_idx], 4),
        'most_central': folios[most_central_idx],
        'most_central_similarity': round(mean_similarity[most_central_idx], 4),
        'mean_pairwise_jaccard': round(np.mean(jaccard_matrix[np.triu_indices(n_folios, k=1)]), 4)
    }
}

with open('phases/UNIQUE_VOCABULARY_ROLE/results/folio_vocabulary_network.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Results saved to phases/UNIQUE_VOCABULARY_ROLE/results/folio_vocabulary_network.json")
print("=" * 70)
