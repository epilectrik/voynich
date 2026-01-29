#!/usr/bin/env python3
"""
PP_POOL_CLASSIFICATION Phase — Script 2: PP Pool Validation

Tests 5-7: B-side behavioral profiles, cross-validation against
co-occurrence pools, effective pool census.

Constraints produced: C659 (pool behavioral coherence)
"""

import json
import sys
import math
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.spatial.distance import squareform, jensenshannon
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.stats import chi2_contingency, fisher_exact
from sklearn.metrics import silhouette_score, adjusted_rand_score

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
MIN_FREQ = 10          # minimum B-side bigrams for behavioral clustering
MAX_K_BEHAV = 15       # maximum clusters for behavioral clustering
SIL_THRESHOLD = 0.25


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, set):
            return sorted(list(obj))
        return super().default(obj)


# ---------------------------------------------------------------------------
# Section 1: Load & Prepare
# ---------------------------------------------------------------------------
print("=" * 70)
print("PP POOL VALIDATION")
print("=" * 70)

# Load PP set (404)
with open(PROJECT_ROOT / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v2_backup.json') as f:
    mid_classes = json.load(f)
pp_set = set(mid_classes['a_shared_middles'])

# Load role data
with open(PROJECT_ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json') as f:
    role_data = json.load(f)
azc_med_set = set(role_data['azc_split']['azc_mediated'])
b_native_set = set(role_data['azc_split']['b_native'])
pp_role_map = role_data['pp_role_map']

# Load material class
with open(PROJECT_ROOT / 'phases/PP_CLASSIFICATION/results/pp_classification.json') as f:
    pp_class_data = json.load(f)
pp_classification = pp_class_data['pp_classification']

# Load class mapping
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)
token_to_class = class_map.get('token_to_class', {})
all_classes = sorted(set(token_to_class.values()))
n_classes = len(all_classes)
class_to_idx = {c: i for i, c in enumerate(all_classes)}

# Load Script 1 results
with open(RESULTS_DIR / 'pp_cooccurrence_clustering.json') as f:
    script1_results = json.load(f)

# Extract primary clustering
primary_method = script1_results['hierarchical_clustering']['primary_method']
primary_clustering = script1_results['hierarchical_clustering']['linkage_results'].get(primary_method, {})
cooccurrence_assignments = primary_clustering.get('cluster_assignments', {})
cooccurrence_k = primary_clustering.get('optimal_k', 0)

print(f"PP MIDDLEs: {len(pp_set)}")
print(f"Co-occurrence pools loaded: k={cooccurrence_k}, n={len(cooccurrence_assignments)}")
print(f"B instruction classes: {n_classes}")

# Lane prediction (C649)
def lane_prediction(middle):
    if not middle:
        return 'neutral'
    c = middle[0]
    if c in ('k', 't', 'p'):
        return 'QO'
    elif c in ('e', 'o'):
        return 'CHSH'
    return 'neutral'

# Build B-side behavioral profiles
print("\nBuilding B-side behavioral profiles...")
tx = Transcript()
morph = Morphology()

# Build B lines
b_lines = defaultdict(list)
for token in tx.currier_b():
    if token.word.strip() and '*' not in token.word:
        b_lines[(token.folio, token.line)].append(token.word)

# Build successor profiles: for each PP MIDDLE, count successor class transitions
pp_successor_counts = defaultdict(Counter)  # mid -> Counter of successor classes
pp_bigram_totals = defaultdict(int)

for (folio, line), words in b_lines.items():
    for i in range(len(words) - 1):
        src_mid = morph.extract(words[i]).middle
        tgt_cls = token_to_class.get(words[i + 1])
        if src_mid and src_mid in pp_set and tgt_cls is not None:
            pp_successor_counts[src_mid][tgt_cls] += 1
            pp_bigram_totals[src_mid] += 1

# Build B-side frequency (total tokens, not bigrams) for census
pp_b_freq = Counter()
for (folio, line), words in b_lines.items():
    for w in words:
        mid = morph.extract(w).middle
        if mid and mid in pp_set:
            pp_b_freq[mid] += 1

# Filter to eligible PP (>= MIN_FREQ bigrams)
eligible_pp = sorted([mid for mid, total in pp_bigram_totals.items() if total >= MIN_FREQ])
print(f"PP with >={MIN_FREQ} B-side bigrams: {len(eligible_pp)}")

# Build normalized successor profiles (probability distributions)
pp_profiles = {}
for mid in eligible_pp:
    profile = np.zeros(n_classes)
    for cls, count in pp_successor_counts[mid].items():
        if cls in class_to_idx:
            profile[class_to_idx[cls]] = count
    total = profile.sum()
    if total > 0:
        profile = profile / total
    pp_profiles[mid] = profile


# ---------------------------------------------------------------------------
# Section 2: Test 5 — B-Side Behavioral Clustering
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TEST 5: B-Side Behavioral Clustering")
print("=" * 70)

behavioral_results = {}

if len(eligible_pp) < 30:
    print(f"GUARD: Only {len(eligible_pp)} eligible PP (< 30), descriptive only")
    behavioral_results['guard'] = True
    behavioral_results['n_eligible'] = len(eligible_pp)

    # Descriptive stats only
    if len(eligible_pp) >= 2:
        pairwise_jsd = []
        for i in range(len(eligible_pp)):
            for j in range(i + 1, len(eligible_pp)):
                d = jensenshannon(pp_profiles[eligible_pp[i]], pp_profiles[eligible_pp[j]])
                pairwise_jsd.append(d)
        behavioral_results['descriptive'] = {
            'mean_jsd': float(np.mean(pairwise_jsd)),
            'median_jsd': float(np.median(pairwise_jsd)),
            'n_pairs': len(pairwise_jsd),
        }
        print(f"  Mean pairwise JSD: {np.mean(pairwise_jsd):.4f}")
else:
    n_e = len(eligible_pp)
    print(f"Eligible PP for behavioral clustering: {n_e}")

    # Build JSD distance matrix
    jsd_matrix = np.zeros((n_e, n_e))
    for i in range(n_e):
        for j in range(i + 1, n_e):
            d = jensenshannon(pp_profiles[eligible_pp[i]], pp_profiles[eligible_pp[j]])
            if np.isnan(d):
                d = 1.0  # max distance for degenerate cases
            jsd_matrix[i, j] = d
            jsd_matrix[j, i] = d

    # Overall JSD stats
    upper_jsd = jsd_matrix[np.triu_indices(n_e, k=1)]
    print(f"Pairwise JSD: mean={np.mean(upper_jsd):.4f}, median={np.median(upper_jsd):.4f}")

    # Hierarchical clustering
    jsd_condensed = squareform(jsd_matrix)
    Z_b = linkage(jsd_condensed, method='average')

    behav_sil_scores = {}
    for k in range(2, min(MAX_K_BEHAV + 1, n_e)):
        labels_b = fcluster(Z_b, t=k, criterion='maxclust')
        n_actual = len(set(labels_b))
        if n_actual < 2:
            continue
        try:
            sil = silhouette_score(jsd_matrix, labels_b, metric='precomputed')
            behav_sil_scores[k] = float(sil)
        except Exception:
            pass

    if behav_sil_scores:
        qualifying = {k: s for k, s in behav_sil_scores.items() if s >= SIL_THRESHOLD}
        if qualifying:
            behav_opt_k = max(qualifying.keys())
            behav_opt_sil = qualifying[behav_opt_k]
        else:
            behav_opt_k = max(behav_sil_scores, key=behav_sil_scores.get)
            behav_opt_sil = behav_sil_scores[behav_opt_k]

        labels_opt = fcluster(Z_b, t=behav_opt_k, criterion='maxclust')
        behav_assignments = {eligible_pp[i]: int(labels_opt[i]) for i in range(n_e)}
        behav_cluster_sizes = Counter(labels_opt)

        print(f"\nSilhouette scores: {', '.join(f'k={k}: {s:.3f}' for k, s in sorted(behav_sil_scores.items())[:10])}")
        print(f"Qualifying (>={SIL_THRESHOLD}): {len(qualifying) if qualifying else 0}")
        print(f"Selected k={behav_opt_k} (sil={behav_opt_sil:.4f})")
        print(f"Cluster sizes: {dict(sorted(behav_cluster_sizes.items()))}")

        # Within/between JSD
        within_jsd = []
        between_jsd = []
        for i in range(n_e):
            for j in range(i + 1, n_e):
                d = jsd_matrix[i, j]
                if labels_opt[i] == labels_opt[j]:
                    within_jsd.append(d)
                else:
                    between_jsd.append(d)

        # Morphological prediction: initial character → cluster
        init_chars = [eligible_pp[i][0] if eligible_pp[i] else '?' for i in range(n_e)]
        init_labels = [lane_prediction(eligible_pp[i]) for i in range(n_e)]
        try:
            ari_morph = float(adjusted_rand_score(labels_opt, init_labels))
        except Exception:
            ari_morph = None
        print(f"ARI (behavioral cluster, lane character): {ari_morph:.4f}" if ari_morph is not None else "ARI: N/A")

        behavioral_results = {
            'n_eligible': n_e,
            'guard': False,
            'jsd_stats': {
                'mean': float(np.mean(upper_jsd)),
                'median': float(np.median(upper_jsd)),
            },
            'optimal_k': behav_opt_k,
            'optimal_silhouette': behav_opt_sil,
            'meets_threshold': behav_opt_sil >= SIL_THRESHOLD,
            'silhouette_scores': behav_sil_scores,
            'cluster_sizes': {int(k): int(v) for k, v in behav_cluster_sizes.items()},
            'cluster_assignments': behav_assignments,
            'within_jsd_mean': float(np.mean(within_jsd)) if within_jsd else None,
            'between_jsd_mean': float(np.mean(between_jsd)) if between_jsd else None,
            'morphological_prediction': {
                'ari_lane_character': ari_morph,
            },
        }
    else:
        print("No valid behavioral silhouette scores")
        behavioral_results = {
            'n_eligible': n_e,
            'guard': False,
            'error': 'no_valid_silhouette',
        }


# ---------------------------------------------------------------------------
# Section 3: Test 6 — Cross-Validation
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TEST 6: Cross-Validation (Co-Occurrence vs Behavioral)")
print("=" * 70)

cross_validation_results = {}

behav_assignments_final = behavioral_results.get('cluster_assignments', {})

# Find overlap: PP in both co-occurrence and behavioral clustering
overlap_pp = sorted(set(cooccurrence_assignments.keys()) & set(behav_assignments_final.keys()))
print(f"Overlap set: {len(overlap_pp)} PP MIDDLEs")

if len(overlap_pp) < 20:
    print(f"GUARD: Overlap < 20, descriptive only")
    cross_validation_results = {
        'guard': True,
        'overlap_n': len(overlap_pp),
        'note': 'insufficient_overlap'
    }
else:
    cooc_labels = [cooccurrence_assignments[mid] for mid in overlap_pp]
    behav_labels = [behav_assignments_final[mid] for mid in overlap_pp]

    # ARI
    ari = float(adjusted_rand_score(cooc_labels, behav_labels))
    print(f"ARI (co-occurrence, behavioral): {ari:.4f}")

    # Contingency table
    cooc_cats = sorted(set(cooc_labels))
    behav_cats = sorted(set(behav_labels))
    contingency = np.zeros((len(cooc_cats), len(behav_cats)), dtype=int)
    for cl, bl in zip(cooc_labels, behav_labels):
        i = cooc_cats.index(cl)
        j = behav_cats.index(bl)
        contingency[i, j] += 1

    # Chi-squared or Fisher's exact
    try:
        if contingency.shape == (2, 2):
            _, p_val = fisher_exact(contingency)
            test_result = {'test': 'fisher_exact', 'p': float(p_val)}
        else:
            chi2, p_val, dof, expected = chi2_contingency(contingency)
            test_result = {
                'test': 'chi2',
                'chi2': float(chi2),
                'p': float(p_val),
                'dof': int(dof),
                'min_expected': float(expected.min()),
            }
    except Exception as e:
        test_result = {'test': 'error', 'error': str(e)}

    print(f"Test: {test_result}")

    # Pool → behavioral cluster mapping
    pool_to_behavior = {}
    for pool in cooc_cats:
        pool_idx = cooc_cats.index(pool)
        row = contingency[pool_idx]
        dominant = behav_cats[np.argmax(row)]
        pool_to_behavior[pool] = {
            'dominant_behavioral': dominant,
            'distribution': {behav_cats[j]: int(row[j]) for j in range(len(behav_cats))},
        }

    # Behavioral cluster → pool mapping
    behavior_to_pool = {}
    for bc in behav_cats:
        bc_idx = behav_cats.index(bc)
        col = contingency[:, bc_idx]
        dominant = cooc_cats[np.argmax(col)]
        behavior_to_pool[bc] = {
            'dominant_pool': dominant,
            'distribution': {cooc_cats[i]: int(col[i]) for i in range(len(cooc_cats))},
        }

    cross_validation_results = {
        'guard': False,
        'overlap_n': len(overlap_pp),
        'ari': ari,
        'contingency_table': contingency.tolist(),
        'cooccurrence_pools': [int(x) if isinstance(x, (int, np.integer)) else x for x in cooc_cats],
        'behavioral_clusters': [int(x) if isinstance(x, (int, np.integer)) else x for x in behav_cats],
        'chi2_test': test_result,
        'pool_to_behavior': {str(k): v for k, v in pool_to_behavior.items()},
        'behavior_to_pool': {str(k): v for k, v in behavior_to_pool.items()},
        'interpretation': (
            'significant_agreement' if ari > 0.3 else
            'weak_agreement' if ari > 0.1 else
            'independent'
        ),
    }

    print(f"\nInterpretation: {cross_validation_results['interpretation']}")


# ---------------------------------------------------------------------------
# Section 4: Test 7 — Effective Pool Census
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TEST 7: Effective Pool Census")
print("=" * 70)

pool_census_results = {}

if not cooccurrence_assignments:
    print("No co-occurrence pools available, skipping census")
    pool_census_results = {'error': 'no_pools'}
else:
    # All PP in co-occurrence assignments
    assigned_pp = sorted(cooccurrence_assignments.keys())
    n_assigned = len(assigned_pp)
    pools = sorted(set(cooccurrence_assignments.values()))
    n_pools = len(pools)
    compression_ratio = len(pp_set) / n_pools if n_pools > 0 else float('inf')

    print(f"Pools: {n_pools}")
    print(f"Assigned PP: {n_assigned} / {len(pp_set)}")
    print(f"Compression ratio: {compression_ratio:.1f}x")

    # Build per-pool profiles
    pool_profiles = {}
    for pool in pools:
        members = sorted([mid for mid in assigned_pp if cooccurrence_assignments[mid] == pool])
        n_members = len(members)

        # Material class distribution
        mat_dist = Counter(pp_classification.get(mid, {}).get('material_class', 'UNKNOWN') for mid in members)

        # Pathway distribution
        path_dist = Counter()
        for mid in members:
            if mid in azc_med_set:
                path_dist['AZC-Med'] += 1
            elif mid in b_native_set:
                path_dist['B-Native'] += 1
            else:
                path_dist['UNKNOWN'] += 1

        # Lane character distribution
        lane_dist = Counter(lane_prediction(mid) for mid in members)

        # Role distribution (mean role vector)
        role_vectors = []
        role_entropies = []
        for mid in members:
            if mid in pp_role_map:
                rv = pp_role_map[mid].get('role_vector', {})
                role_vectors.append([
                    rv.get('AUXILIARY', 0), rv.get('CORE_CONTROL', 0),
                    rv.get('ENERGY_OPERATOR', 0), rv.get('FLOW_OPERATOR', 0),
                    rv.get('FREQUENT_OPERATOR', 0)
                ])
                role_entropies.append(pp_role_map[mid].get('role_entropy', 0))

        mean_role_vector = np.mean(role_vectors, axis=0).tolist() if role_vectors else [0]*5
        mean_role_entropy = float(np.mean(role_entropies)) if role_entropies else 0.0

        # B-side frequency
        b_freqs = [pp_b_freq.get(mid, 0) for mid in members]
        mean_b_freq = float(np.mean(b_freqs))

        # Top members by B frequency
        member_freqs = [(mid, pp_b_freq.get(mid, 0)) for mid in members]
        member_freqs.sort(key=lambda x: -x[1])
        top_members = [{'middle': mid, 'b_freq': freq} for mid, freq in member_freqs[:5]]

        # Dominant behavioral cluster (from Test 6)
        dominant_behav = None
        if not cross_validation_results.get('guard', True):
            pool_map = cross_validation_results.get('pool_to_behavior', {})
            pool_key = str(pool)
            if pool_key in pool_map:
                dominant_behav = pool_map[pool_key].get('dominant_behavioral')

        pool_profiles[int(pool)] = {
            'n_members': n_members,
            'material_class': dict(mat_dist),
            'pathway': dict(path_dist),
            'lane_character': dict(lane_dist),
            'mean_role_vector': {
                'AUXILIARY': mean_role_vector[0],
                'CORE_CONTROL': mean_role_vector[1],
                'ENERGY_OPERATOR': mean_role_vector[2],
                'FLOW_OPERATOR': mean_role_vector[3],
                'FREQUENT_OPERATOR': mean_role_vector[4],
            },
            'mean_role_entropy': mean_role_entropy,
            'mean_b_frequency': mean_b_freq,
            'top_members': top_members,
            'dominant_behavioral_cluster': dominant_behav,
            'members': members,
        }

    # Print census table
    print(f"\n{'Pool':>6} {'Size':>6} {'ANIMAL':>7} {'HERB':>6} {'MIXED':>6} {'NEUT':>6} {'AZC':>5} {'B-Nat':>6} {'QO':>4} {'CHSH':>5} {'RoleH':>6} {'B-freq':>7}")
    print("-" * 85)
    for pool in pools:
        p = pool_profiles[int(pool)]
        print(f"{pool:>6} {p['n_members']:>6} "
              f"{p['material_class'].get('ANIMAL',0):>7} "
              f"{p['material_class'].get('HERB',0):>6} "
              f"{p['material_class'].get('MIXED',0):>6} "
              f"{p['material_class'].get('NEUTRAL',0):>6} "
              f"{p['pathway'].get('AZC-Med',0):>5} "
              f"{p['pathway'].get('B-Native',0):>6} "
              f"{p['lane_character'].get('QO',0):>4} "
              f"{p['lane_character'].get('CHSH',0):>5} "
              f"{p['mean_role_entropy']:>6.3f} "
              f"{p['mean_b_frequency']:>7.1f}")

    # Variance explained: role vector eta-squared
    # Between-pool variance / total variance for each role dimension
    role_names = ['AUXILIARY', 'CORE_CONTROL', 'ENERGY_OPERATOR', 'FLOW_OPERATOR', 'FREQUENT_OPERATOR']
    eta_squared = {}
    for dim_idx, role_name in enumerate(role_names):
        all_values = []
        pool_means = []
        pool_ns = []
        for pool in pools:
            members = [mid for mid in assigned_pp if cooccurrence_assignments[mid] == pool]
            values = []
            for mid in members:
                if mid in pp_role_map:
                    rv = pp_role_map[mid].get('role_vector', {})
                    values.append(rv.get(role_name, 0))
            if values:
                all_values.extend(values)
                pool_means.append(np.mean(values))
                pool_ns.append(len(values))

        if all_values:
            grand_mean = np.mean(all_values)
            ss_total = np.sum((np.array(all_values) - grand_mean) ** 2)
            ss_between = sum(n_i * (mu - grand_mean) ** 2
                            for mu, n_i in zip(pool_means, pool_ns))
            eta2 = ss_between / ss_total if ss_total > 0 else 0
            eta_squared[role_name] = float(eta2)
        else:
            eta_squared[role_name] = 0.0

    print(f"\nVariance explained (eta-squared) by pool membership:")
    for role, eta2 in eta_squared.items():
        print(f"  {role}: {eta2:.4f}")

    # Assign excluded PP to nearest pool by building A-record sets
    # Build PP→record index from transcript (needed for excluded assignment)
    pp_records_v = defaultdict(set)
    record_pp_sets_v = {}
    for token in tx.currier_a():
        key = (token.folio, token.line)
        m_tok = morph.extract(token.word)
        if m_tok.middle and m_tok.middle in pp_set:
            record_pp_sets_v.setdefault(key, set()).add(m_tok.middle)
            pp_records_v[m_tok.middle].add(key)

    excluded_assignments = {}
    filtered_pp_list = sorted(cooccurrence_assignments.keys())
    excluded_in_records = [mid for mid in pp_set
                           if mid not in cooccurrence_assignments
                           and mid in pp_records_v and len(pp_records_v[mid]) > 0]

    if excluded_in_records:
        for ex_mid in excluded_in_records:
            ex_recs = pp_records_v[ex_mid]
            pool_jaccards = defaultdict(list)
            for assigned_mid in filtered_pp_list:
                a_recs = pp_records_v[assigned_mid]
                inter = len(ex_recs & a_recs)
                union = len(ex_recs | a_recs)
                if union > 0:
                    jac = inter / union
                    pool = cooccurrence_assignments[assigned_mid]
                    pool_jaccards[pool].append(jac)

            if pool_jaccards:
                pool_mean_jac = {p: np.mean(jacs) for p, jacs in pool_jaccards.items()}
                best_pool = max(pool_mean_jac, key=pool_mean_jac.get)
                best_jac = pool_mean_jac[best_pool]
                excluded_assignments[ex_mid] = {
                    'assigned_pool': int(best_pool) if isinstance(best_pool, (int, np.integer)) else best_pool,
                    'mean_jaccard': float(best_jac),
                }

    n_no_records = len([mid for mid in pp_set if mid not in pp_records_v or len(pp_records_v.get(mid, set())) == 0])
    print(f"\nExcluded PP assigned to nearest pool: {len(excluded_assignments)}")
    print(f"PP with no A records: {n_no_records}")

    pool_census_results = {
        'n_pools': n_pools,
        'compression_ratio': compression_ratio,
        'n_assigned_primary': n_assigned,
        'n_excluded_assigned': len(excluded_assignments),
        'n_no_records': n_no_records,
        'pool_profiles': pool_profiles,
        'variance_explained': {
            'role_eta_squared': eta_squared,
            'mean_role_eta_squared': float(np.mean(list(eta_squared.values()))),
        },
        'excluded_assignments': excluded_assignments,
    }


# ---------------------------------------------------------------------------
# Section 5: Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("SUMMARY SCORECARD")
print("=" * 70)

behav_k = behavioral_results.get('optimal_k', 'N/A')
behav_sil = behavioral_results.get('optimal_silhouette', 'N/A')
behav_guard = behavioral_results.get('guard', False)
cv_ari = cross_validation_results.get('ari', 'N/A')
cv_guard = cross_validation_results.get('guard', True)

print(f"Co-occurrence pools: k={cooccurrence_k}")
print(f"Behavioral clusters: k={behav_k} {'(GUARD)' if behav_guard else ''}")
if isinstance(behav_sil, float):
    print(f"Behavioral silhouette: {behav_sil:.4f} (threshold: {SIL_THRESHOLD})")
print(f"Cross-validation ARI: {cv_ari:.4f}" if isinstance(cv_ari, float) else f"Cross-validation: {cv_ari}")
if isinstance(cv_ari, float):
    interp = cross_validation_results.get('interpretation', 'N/A')
    print(f"Interpretation: {interp}")
print(f"Pool census: {pool_census_results.get('n_pools', 0)} pools, "
      f"{pool_census_results.get('compression_ratio', 0):.1f}x compression")

# Determine overall verdict
if behav_guard:
    behav_verdict = 'INSUFFICIENT_DATA'
elif behavioral_results.get('meets_threshold', False):
    behav_verdict = 'BEHAVIORAL_CLUSTERS_FOUND'
else:
    behav_verdict = 'BEHAVIORAL_CONTINUOUS'

if cv_guard:
    cv_verdict = 'INSUFFICIENT_OVERLAP'
elif isinstance(cv_ari, float) and cv_ari > 0.3:
    cv_verdict = 'COHERENT'
elif isinstance(cv_ari, float) and cv_ari > 0.1:
    cv_verdict = 'WEAK_COHERENCE'
else:
    cv_verdict = 'INDEPENDENT'

print(f"\nBehavioral verdict: {behav_verdict}")
print(f"Cross-validation verdict: {cv_verdict}")

# Save results
output = {
    'metadata': {
        'phase': 'PP_POOL_CLASSIFICATION',
        'script': 'pp_pool_validation.py',
        'min_freq': MIN_FREQ,
        'max_k_behavioral': MAX_K_BEHAV,
        'silhouette_threshold': SIL_THRESHOLD,
    },
    'behavioral_clustering': behavioral_results,
    'cross_validation': cross_validation_results,
    'pool_census': pool_census_results,
    'verdicts': {
        'behavioral': behav_verdict,
        'cross_validation': cv_verdict,
    },
}

with open(RESULTS_DIR / 'pp_pool_validation.json', 'w') as f:
    json.dump(output, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {RESULTS_DIR / 'pp_pool_validation.json'}")
