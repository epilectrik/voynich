"""
Script 3: Effective Vocabulary Census

Aggregates clustering results across all 49 classes to determine:
1. Effective vocabulary size (sum of optimal_k)
2. Role-level decomposition
3. Size-heterogeneity correlation
4. Hazard vs non-hazard comparison

Expected constraint: C633 (Effective Vocabulary Census)
Depends on: Script 1 results (intra_class_clustering.json)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
import math
import numpy as np
from collections import Counter, defaultdict
from scipy import stats

# --- Data Loading ---
CLUSTERING_FILE = Path(__file__).parent.parent / 'results' / 'intra_class_clustering.json'
CLASS_MAP_FILE = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
RESULTS_DIR = Path(__file__).parent.parent / 'results'

with open(CLUSTERING_FILE) as f:
    clustering = json.load(f)

with open(CLASS_MAP_FILE) as f:
    class_data = json.load(f)

class_to_role = {int(k): v for k, v in class_data['class_to_role'].items()}
class_to_tokens = {int(k): v for k, v in class_data['class_to_tokens'].items()}

per_class = clustering['per_class']
summary = clustering['summary']
token_freqs = clustering.get('token_frequencies', {})

# Hazard classes
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

# ============================================================
# Section 1: Effective Vocabulary Size
# ============================================================

print("=" * 60)
print("SECTION 1: Effective Vocabulary Size")
print("=" * 60)

total_classes = len(per_class)
effective_vocab = sum(v['optimal_k'] for v in per_class.values())
total_token_types = len(class_data['token_to_class'])
n_heterogeneous = sum(1 for v in per_class.values() if v['optimal_k'] > 1)
n_uniform = total_classes - n_heterogeneous

compression_ratio = total_token_types / effective_vocab
expansion_ratio = effective_vocab / total_classes

print(f"Total cosurvival classes: {total_classes}")
print(f"Total classified token types: {total_token_types}")
print(f"Effective vocabulary size: {effective_vocab}")
print(f"Compression ratio (types/effective): {compression_ratio:.1f}x")
print(f"Expansion ratio (effective/classes): {expansion_ratio:.2f}x")
print(f"Heterogeneous classes: {n_heterogeneous} ({100*n_heterogeneous/total_classes:.1f}%)")
print(f"Uniform classes: {n_uniform} ({100*n_uniform/total_classes:.1f}%)")
print(f"\nInterpretation: The 49-class system captures {100/compression_ratio:.1f}% of "
      f"total type diversity as functional sub-types.")

# k distribution
k_dist = Counter(v['optimal_k'] for v in per_class.values())
print(f"\nk distribution:")
for k in sorted(k_dist.keys()):
    print(f"  k={k}: {k_dist[k]} classes ({100*k_dist[k]/total_classes:.1f}%)")

# ============================================================
# Section 2: Role-Level Decomposition
# ============================================================

print("\n" + "=" * 60)
print("SECTION 2: Role-Level Decomposition")
print("=" * 60)

role_data = defaultdict(lambda: {
    'classes': [], 'total_k': 0, 'heterogeneous': 0,
    'total_tokens': 0, 'total_eligible': 0
})

for cls_id_str, cdata in per_class.items():
    cls_id = int(cls_id_str)
    role = cdata['role']
    role_data[role]['classes'].append(cls_id)
    role_data[role]['total_k'] += cdata['optimal_k']
    role_data[role]['total_tokens'] += cdata['n_tokens']
    role_data[role]['total_eligible'] += cdata['n_eligible']
    if cdata['optimal_k'] > 1:
        role_data[role]['heterogeneous'] += 1

print(f"{'Role':>20s} {'Classes':>7s} {'EffVocab':>8s} {'Het':>4s} {'MeanK':>6s} "
      f"{'MaxK':>4s} {'Tokens':>7s} {'Eligible':>8s}")
print(f"{'----':>20s} {'-------':>7s} {'--------':>8s} {'---':>4s} {'-----':>6s} "
      f"{'----':>4s} {'------':>7s} {'--------':>8s}")

role_summary = {}
for role in sorted(role_data.keys()):
    rd = role_data[role]
    n_classes = len(rd['classes'])
    mean_k = rd['total_k'] / n_classes if n_classes > 0 else 0
    max_k = max(per_class[str(c)]['optimal_k'] for c in rd['classes'])
    print(f"{role:>20s} {n_classes:7d} {rd['total_k']:8d} {rd['heterogeneous']:4d} "
          f"{mean_k:6.2f} {max_k:4d} {rd['total_tokens']:7d} {rd['total_eligible']:8d}")
    role_summary[role] = {
        'n_classes': n_classes,
        'effective_vocab': rd['total_k'],
        'n_heterogeneous': rd['heterogeneous'],
        'mean_k': round(mean_k, 3),
        'max_k': max_k,
        'total_tokens': rd['total_tokens'],
        'total_eligible': rd['total_eligible'],
        'class_ids': sorted(rd['classes'])
    }

# ============================================================
# Section 3: Size-Heterogeneity Correlation
# ============================================================

print("\n" + "=" * 60)
print("SECTION 3: Size-Heterogeneity Correlation")
print("=" * 60)

# Collect class_size (n_tokens) and optimal_k
sizes = []
ks = []
eligible_counts = []
mean_jsds = []
total_class_freqs = []

for cls_id_str, cdata in per_class.items():
    cls_id = int(cls_id_str)
    sizes.append(cdata['n_tokens'])
    ks.append(cdata['optimal_k'])
    eligible_counts.append(cdata['n_eligible'])
    mean_jsds.append(cdata['mean_jsd'] if cdata['mean_jsd'] is not None else 0)
    # Compute total class frequency
    members = class_to_tokens.get(cls_id, [])
    total_freq = sum(token_freqs.get(t, 0) for t in members)
    total_class_freqs.append(total_freq)

sizes = np.array(sizes)
ks = np.array(ks)
eligible_counts = np.array(eligible_counts)
mean_jsds = np.array(mean_jsds)
total_class_freqs = np.array(total_class_freqs)

# Spearman correlations
rho_size_k, p_size_k = stats.spearmanr(sizes, ks)
rho_freq_k, p_freq_k = stats.spearmanr(total_class_freqs, ks)
rho_eligible_k, p_eligible_k = stats.spearmanr(eligible_counts, ks)
rho_jsd_k, p_jsd_k = stats.spearmanr(mean_jsds, ks)
rho_size_jsd, p_size_jsd = stats.spearmanr(sizes, mean_jsds)

print(f"Spearman correlations:")
print(f"  n_tokens vs optimal_k:     rho={rho_size_k:.3f}, p={p_size_k:.4f}")
print(f"  total_freq vs optimal_k:   rho={rho_freq_k:.3f}, p={p_freq_k:.4f}")
print(f"  n_eligible vs optimal_k:   rho={rho_eligible_k:.3f}, p={p_eligible_k:.4f}")
print(f"  mean_jsd vs optimal_k:     rho={rho_jsd_k:.3f}, p={p_jsd_k:.4f}")
print(f"  n_tokens vs mean_jsd:      rho={rho_size_jsd:.3f}, p={p_size_jsd:.4f}")

# Outliers: large classes with k=1
print(f"\nLargest classes with k=1 (surprisingly uniform):")
large_uniform = []
for cls_id_str, cdata in per_class.items():
    if cdata['optimal_k'] == 1 and cdata['n_tokens'] >= 10:
        large_uniform.append((int(cls_id_str), cdata))
large_uniform.sort(key=lambda x: -x[1]['n_tokens'])
for cls_id, cdata in large_uniform[:10]:
    jsd_str = f"{cdata['mean_jsd']:.3f}" if cdata['mean_jsd'] is not None else "N/A"
    sil_str = f"{cdata['silhouette_score']:.3f}" if cdata['silhouette_score'] is not None else "N/A"
    print(f"  Class {cls_id:2d} ({cdata['role']:20s}): {cdata['n_tokens']:2d} tokens, "
          f"{cdata['n_eligible']:2d} eligible, mean_jsd={jsd_str}, best_sil={sil_str}")

# Small classes with k=2
print(f"\nSmallest classes with k>1 (surprisingly diverse):")
small_het = []
for cls_id_str, cdata in per_class.items():
    if cdata['optimal_k'] > 1:
        small_het.append((int(cls_id_str), cdata))
small_het.sort(key=lambda x: x[1]['n_tokens'])
for cls_id, cdata in small_het:
    jsd_str = f"{cdata['mean_jsd']:.3f}" if cdata['mean_jsd'] is not None else "N/A"
    print(f"  Class {cls_id:2d} ({cdata['role']:20s}): {cdata['n_tokens']:2d} tokens, "
          f"{cdata['n_eligible']:2d} eligible, mean_jsd={jsd_str}")

# ============================================================
# Section 4: Hazard vs Non-Hazard Comparison
# ============================================================

print("\n" + "=" * 60)
print("SECTION 4: Hazard vs Non-Hazard Comparison")
print("=" * 60)

hazard_stats = {'classes': [], 'ks': [], 'jsds': [], 'sizes': [], 'eligible': []}
nonhazard_stats = {'classes': [], 'ks': [], 'jsds': [], 'sizes': [], 'eligible': []}

for cls_id_str, cdata in per_class.items():
    cls_id = int(cls_id_str)
    target = hazard_stats if cls_id in HAZARD_CLASSES else nonhazard_stats
    target['classes'].append(cls_id)
    target['ks'].append(cdata['optimal_k'])
    target['jsds'].append(cdata['mean_jsd'] if cdata['mean_jsd'] is not None else 0)
    target['sizes'].append(cdata['n_tokens'])
    target['eligible'].append(cdata['n_eligible'])

# Summary
print(f"{'Metric':>25s} {'Hazard':>10s} {'Non-Hazard':>10s} {'p-value':>10s}")
print(f"{'------':>25s} {'------':>10s} {'----------':>10s} {'-------':>10s}")

hz_ks = np.array(hazard_stats['ks'])
nh_ks = np.array(nonhazard_stats['ks'])
_, p_k = stats.mannwhitneyu(hz_ks, nh_ks, alternative='two-sided') if len(hz_ks) > 1 and len(nh_ks) > 1 else (None, 1.0)
print(f"{'mean k':>25s} {np.mean(hz_ks):10.2f} {np.mean(nh_ks):10.2f} {p_k:10.4f}")

hz_jsds = np.array(hazard_stats['jsds'])
nh_jsds = np.array(nonhazard_stats['jsds'])
# Filter out zeros (classes with no JSD)
hz_jsds_valid = hz_jsds[hz_jsds > 0]
nh_jsds_valid = nh_jsds[nh_jsds > 0]
if len(hz_jsds_valid) > 1 and len(nh_jsds_valid) > 1:
    _, p_jsd = stats.mannwhitneyu(hz_jsds_valid, nh_jsds_valid, alternative='two-sided')
else:
    p_jsd = 1.0
print(f"{'mean JSD':>25s} {np.mean(hz_jsds_valid):10.3f} {np.mean(nh_jsds_valid):10.3f} {p_jsd:10.4f}")

hz_sizes = np.array(hazard_stats['sizes'])
nh_sizes = np.array(nonhazard_stats['sizes'])
_, p_size = stats.mannwhitneyu(hz_sizes, nh_sizes, alternative='two-sided')
print(f"{'mean class size':>25s} {np.mean(hz_sizes):10.1f} {np.mean(nh_sizes):10.1f} {p_size:10.4f}")

hz_elig = np.array(hazard_stats['eligible'])
nh_elig = np.array(nonhazard_stats['eligible'])
_, p_elig = stats.mannwhitneyu(hz_elig, nh_elig, alternative='two-sided')
print(f"{'mean eligible':>25s} {np.mean(hz_elig):10.1f} {np.mean(nh_elig):10.1f} {p_elig:10.4f}")

# Het rates
hz_het = sum(1 for k in hazard_stats['ks'] if k > 1)
nh_het = sum(1 for k in nonhazard_stats['ks'] if k > 1)
hz_n = len(hazard_stats['ks'])
nh_n = len(nonhazard_stats['ks'])
# Fisher's exact: heterogeneous/uniform x hazard/nonhazard
table = np.array([[hz_het, hz_n - hz_het],
                  [nh_het, nh_n - nh_het]])
_, p_fisher = stats.fisher_exact(table)
print(f"{'het rate':>25s} {hz_het}/{hz_n} ({100*hz_het/hz_n:.0f}%)    "
      f"{nh_het}/{nh_n} ({100*nh_het/nh_n:.0f}%)    p={p_fisher:.4f}")

print(f"\nHazard class details:")
for cls_id in sorted(HAZARD_CLASSES):
    cdata = per_class[str(cls_id)]
    jsd_str = f"{cdata['mean_jsd']:.3f}" if cdata['mean_jsd'] is not None else "N/A"
    members = class_to_tokens.get(cls_id, [])
    print(f"  Class {cls_id:2d} ({cdata['role']:20s}): k={cdata['optimal_k']}, "
          f"n={cdata['n_tokens']}, eligible={cdata['n_eligible']}, "
          f"jsd={jsd_str}, members={members}")

# ============================================================
# Overall Verdict
# ============================================================

print("\n" + "=" * 60)
print("OVERALL VERDICT")
print("=" * 60)

print(f"""
The 49 cosurvival classes produce an effective vocabulary of {effective_vocab} functional sub-types.

Key findings:
1. VOCABULARY SIZE: {effective_vocab} effective sub-types from {total_token_types} classified types
   across {total_classes} classes. The class system captures {100/compression_ratio:.1f}% of type
   diversity as functional sub-types.

2. UNIFORMITY DOMINANCE: {n_uniform}/{total_classes} classes ({100*n_uniform/total_classes:.0f}%)
   are functionally uniform despite high within-class JS divergence (mean {np.mean(mean_jsds[mean_jsds>0]):.3f}).
   The divergence is continuous, not clustered.

3. ROLE PATTERN: FLOW_OPERATOR shows highest diversity (mean k={role_summary.get('FLOW_OPERATOR', {}).get('mean_k', 0):.2f}),
   CORE_CONTROL and FREQUENT_OPERATOR are fully uniform (mean k=1.00).

4. HAZARD EFFECT: Hazard classes have HIGHER heterogeneity rate ({hz_het}/{hz_n})
   vs non-hazard ({nh_het}/{nh_n}), driven by FL_HAZ classes 7 and 30.
   Fisher p={p_fisher:.4f}. This is the opposite of the "uniformity enforcement" hypothesis.

5. SIZE INDEPENDENCE: Class size does not predict sub-type count
   (rho={rho_size_k:.3f}, p={p_size_k:.4f}). Large classes are NOT more diverse.
""")

# ============================================================
# Save Results
# ============================================================

output = {
    'metadata': {
        'phase': 'INTRA_CLASS_DIVERSITY',
        'script': 'effective_vocabulary_census.py',
        'hazard_classes': sorted(HAZARD_CLASSES)
    },
    'effective_vocabulary': {
        'total_classes': total_classes,
        'total_token_types': total_token_types,
        'effective_vocab_size': effective_vocab,
        'compression_ratio': round(compression_ratio, 2),
        'expansion_ratio': round(expansion_ratio, 3),
        'n_heterogeneous': n_heterogeneous,
        'n_uniform': n_uniform,
        'k_distribution': {str(k): v for k, v in sorted(k_dist.items())}
    },
    'role_decomposition': role_summary,
    'correlations': {
        'size_vs_k': {'rho': round(float(rho_size_k), 4), 'p': round(float(p_size_k), 4)},
        'freq_vs_k': {'rho': round(float(rho_freq_k), 4), 'p': round(float(p_freq_k), 4)},
        'eligible_vs_k': {'rho': round(float(rho_eligible_k), 4), 'p': round(float(p_eligible_k), 4)},
        'jsd_vs_k': {'rho': round(float(rho_jsd_k), 4), 'p': round(float(p_jsd_k), 4)},
        'size_vs_jsd': {'rho': round(float(rho_size_jsd), 4), 'p': round(float(p_size_jsd), 4)}
    },
    'hazard_comparison': {
        'hazard': {
            'n_classes': hz_n,
            'n_heterogeneous': hz_het,
            'het_rate': round(hz_het / hz_n, 3) if hz_n > 0 else 0,
            'mean_k': round(float(np.mean(hz_ks)), 3),
            'mean_jsd': round(float(np.mean(hz_jsds_valid)), 3) if len(hz_jsds_valid) > 0 else None,
            'mean_size': round(float(np.mean(hz_sizes)), 1)
        },
        'non_hazard': {
            'n_classes': nh_n,
            'n_heterogeneous': nh_het,
            'het_rate': round(nh_het / nh_n, 3) if nh_n > 0 else 0,
            'mean_k': round(float(np.mean(nh_ks)), 3),
            'mean_jsd': round(float(np.mean(nh_jsds_valid)), 3) if len(nh_jsds_valid) > 0 else None,
            'mean_size': round(float(np.mean(nh_sizes)), 1)
        },
        'tests': {
            'k_mannwhitney_p': round(float(p_k), 4),
            'jsd_mannwhitney_p': round(float(p_jsd), 4),
            'het_rate_fisher_p': round(float(p_fisher), 4)
        }
    },
    'outliers': {
        'large_uniform': [
            {'class_id': cls_id, 'n_tokens': cdata['n_tokens'],
             'n_eligible': cdata['n_eligible'], 'role': cdata['role'],
             'mean_jsd': cdata['mean_jsd']}
            for cls_id, cdata in large_uniform[:10]
        ],
        'heterogeneous': [
            {'class_id': cls_id, 'n_tokens': cdata['n_tokens'],
             'n_eligible': cdata['n_eligible'], 'role': cdata['role'],
             'optimal_k': cdata['optimal_k'], 'mean_jsd': cdata['mean_jsd']}
            for cls_id, cdata in small_het
        ]
    }
}

out_file = RESULTS_DIR / 'effective_vocabulary_census.json'
with open(out_file, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {out_file}")
print("DONE")
