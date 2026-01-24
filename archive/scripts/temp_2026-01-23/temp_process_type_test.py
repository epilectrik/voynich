#!/usr/bin/env python3
"""
Test: Do different A records activate qualitatively different B vocabulary?

If A records can select different "process types":
- A records would cluster into distinct groups by B vocabulary profile
- Different clusters would have different class compositions
- Some might emphasize kernel vs non-kernel, or different functional roles

If all A records activate similar B profiles:
- Continuous variation, not distinct clusters
- Similar class distributions across all A records
- Uniform kernel involvement
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

# Load data
DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']

# Split by language
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)
token_to_class = data['token_to_class']

# Load survivor data
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivor_data = json.load(f)

print("=" * 70)
print("PROCESS TYPE TEST: Do A Records Activate Different B Vocabulary Types?")
print("=" * 70)

# =============================================================================
# Build A record -> B class profile mapping
# =============================================================================
print("\nBuilding A record -> B class profiles...")

# Extract MIDDLE from token
def get_middle(token):
    if pd.isna(token) or len(str(token)) < 2:
        return None
    token = str(token)
    return token[1:-1] if len(token) > 2 else (token[1] if len(token) == 2 else None)

# Get all B tokens and their classes
b_tokens = set(df_b['word'].dropna())
b_token_to_class = {t: token_to_class.get(t) for t in b_tokens if token_to_class.get(t)}

# Build class profiles for each A record
a_record_profiles = {}

for record in survivor_data['records'][:500]:  # Sample for speed
    record_id = record['a_record']
    surviving_classes = set(record.get('surviving_classes', []))
    a_middles = record.get('a_middles', [])

    if len(surviving_classes) >= 5:  # Minimum viable program
        # Create class distribution vector
        class_vector = np.zeros(49)
        for cls in surviving_classes:
            if 1 <= cls <= 49:
                class_vector[cls-1] = 1

        a_record_profiles[record_id] = {
            'classes': surviving_classes,
            'vector': class_vector,
            'n_classes': len(surviving_classes),
            'a_middles': a_middles,
            'middle_count': len(a_middles)
        }

print(f"A records with viable B profiles: {len(a_record_profiles)}")

# =============================================================================
# TEST 1: Class Profile Clustering
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: DO A RECORDS CLUSTER BY B CLASS PROFILE?")
print("=" * 70)

# Build distance matrix
record_ids = list(a_record_profiles.keys())
vectors = np.array([a_record_profiles[r]['vector'] for r in record_ids])

# Compute pairwise Jaccard distances
distances = pdist(vectors, metric='jaccard')
dist_matrix = squareform(distances)

print(f"\nPairwise Jaccard distances:")
print(f"  Mean: {np.mean(distances):.3f}")
print(f"  Std: {np.std(distances):.3f}")
print(f"  Min: {np.min(distances):.3f}")
print(f"  Max: {np.max(distances):.3f}")

# Hierarchical clustering
Z = linkage(distances, method='ward')

# Try different cluster counts
print("\nClustering analysis:")
for n_clusters in [2, 3, 4, 5]:
    labels = fcluster(Z, n_clusters, criterion='maxclust')

    # Check cluster sizes
    cluster_sizes = Counter(labels)

    # Check within-cluster vs between-cluster distance
    within_dists = []
    between_dists = []

    for i in range(len(record_ids)):
        for j in range(i+1, len(record_ids)):
            if labels[i] == labels[j]:
                within_dists.append(dist_matrix[i,j])
            else:
                between_dists.append(dist_matrix[i,j])

    if within_dists and between_dists:
        silhouette_approx = (np.mean(between_dists) - np.mean(within_dists)) / max(np.mean(between_dists), np.mean(within_dists))
        print(f"  {n_clusters} clusters: sizes={dict(cluster_sizes)}, silhouette~{silhouette_approx:.3f}")

# =============================================================================
# TEST 2: Kernel Class Involvement
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: KERNEL INVOLVEMENT ACROSS A RECORDS")
print("=" * 70)
print("\nDo all A records activate kernel-adjacent classes equally?")

# Kernel-adjacent classes (from BCSC - classes that interact with k, h, e)
# Based on C089, C103-C105: kernel classes are special
# Let's identify which classes are "kernel-heavy" vs "kernel-light"

# Get class frequencies in B corpus
b_class_counts = Counter()
for tok in df_b['word'].dropna():
    cls = token_to_class.get(tok)
    if cls:
        b_class_counts[cls] += 1

# Top 10 most common classes (likely core/kernel-adjacent)
top_classes = [c for c, _ in b_class_counts.most_common(10)]
print(f"\nTop 10 B classes by frequency: {top_classes}")

# For each A record, calculate proportion of top classes vs tail classes
kernel_ratios = []
for record_id, profile in a_record_profiles.items():
    surviving = profile['classes']
    n_top = len(surviving & set(top_classes))
    ratio = n_top / len(surviving) if surviving else 0
    kernel_ratios.append(ratio)

print(f"\nTop-class involvement across A records:")
print(f"  Mean ratio: {np.mean(kernel_ratios):.3f}")
print(f"  Std: {np.std(kernel_ratios):.3f}")
print(f"  Min: {np.min(kernel_ratios):.3f}")
print(f"  Max: {np.max(kernel_ratios):.3f}")

# Is there bimodal distribution? (Would suggest process types)
from scipy.stats import normaltest
if len(kernel_ratios) >= 20:
    stat, p = normaltest(kernel_ratios)
    print(f"  Normality test: p={p:.4f} {'(non-normal - possible clustering)' if p < 0.05 else '(normal - continuous variation)'}")

# =============================================================================
# TEST 3: Class Co-occurrence Patterns
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: CLASS CO-OCCURRENCE STRUCTURE")
print("=" * 70)
print("\nDo certain classes always appear together (functional modules)?")

# Build class co-occurrence matrix from A record profiles
cooccur = np.zeros((49, 49))
class_counts = np.zeros(49)

for profile in a_record_profiles.values():
    classes = list(profile['classes'])
    for cls in classes:
        if 1 <= cls <= 49:
            class_counts[cls-1] += 1
    for i, c1 in enumerate(classes):
        for c2 in classes[i+1:]:
            if 1 <= c1 <= 49 and 1 <= c2 <= 49:
                cooccur[c1-1, c2-1] += 1
                cooccur[c2-1, c1-1] += 1

# Find class pairs that ALWAYS co-occur (would suggest modules)
always_together = []
for i in range(49):
    for j in range(i+1, 49):
        if class_counts[i] > 10 and class_counts[j] > 10:
            # If class i appears, how often does j appear too?
            if cooccur[i,j] == class_counts[i] or cooccur[i,j] == class_counts[j]:
                always_together.append((i+1, j+1, cooccur[i,j]))

print(f"\nClass pairs that ALWAYS co-occur: {len(always_together)}")
if always_together:
    for c1, c2, count in always_together[:10]:
        print(f"  Classes {c1} & {c2}: {int(count)} co-occurrences")

# Find class pairs that NEVER co-occur (would suggest mutual exclusion/different process types)
never_together = []
for i in range(49):
    for j in range(i+1, 49):
        if class_counts[i] > 20 and class_counts[j] > 20:
            if cooccur[i,j] == 0:
                never_together.append((i+1, j+1, class_counts[i], class_counts[j]))

print(f"\nClass pairs that NEVER co-occur (with n>20 each): {len(never_together)}")
if never_together:
    for c1, c2, n1, n2 in never_together[:10]:
        print(f"  Classes {c1} (n={int(n1)}) & {c2} (n={int(n2)}): never together")

# =============================================================================
# TEST 4: A Record Vocabulary -> B Class Profile Correlation
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: DO DIFFERENT A VOCABULARY TYPES PREDICT DIFFERENT B PROFILES?")
print("=" * 70)

# Group A records by their vocabulary characteristics
# Use PP count as a proxy for "capacity" dimension

# Get A record MIDDLE counts from survivor data
middle_to_profile = defaultdict(list)
for record_id, profile in a_record_profiles.items():
    middle_count = profile['middle_count']
    middle_to_profile[middle_count].append(profile)

print(f"\nA records grouped by MIDDLE count:")
for middle_count in sorted(middle_to_profile.keys()):
    profiles = middle_to_profile[middle_count]
    if len(profiles) >= 5:
        mean_classes = np.mean([p['n_classes'] for p in profiles])
        print(f"  MIDDLEs={middle_count}: {len(profiles)} records, mean surviving classes={mean_classes:.1f}")

# Check if MIDDLE count predicts class profile diversity
if len(middle_to_profile) >= 3:
    middle_counts = []
    n_classes = []
    for record_id, profile in a_record_profiles.items():
        middle_counts.append(profile['middle_count'])
        n_classes.append(profile['n_classes'])

    corr, p = stats.spearmanr(middle_counts, n_classes)
    print(f"\nMIDDLE count vs surviving B classes: rho={corr:.3f}, p={p:.4f}")

# =============================================================================
# TEST 5: Functional Role Distribution
# =============================================================================
print("\n" + "=" * 70)
print("TEST 5: FUNCTIONAL ROLE DISTRIBUTION ACROSS A RECORDS")
print("=" * 70)

# Define functional roles based on our earlier findings
# TERMINATOR classes (high line-final): 22, 40, 15, 38
# OPERATOR classes (high medial): 48, 35, 9, 34, 8
# High-frequency core: 33, 13, 34, 8, 31

TERMINATORS = {22, 40, 15, 38}
OPERATORS = {48, 35, 9, 34, 8}
CORE = {33, 13, 34, 8, 31}

role_distributions = []
for record_id, profile in a_record_profiles.items():
    surviving = profile['classes']
    n_term = len(surviving & TERMINATORS)
    n_oper = len(surviving & OPERATORS)
    n_core = len(surviving & CORE)
    total = len(surviving)

    role_distributions.append({
        'terminator_ratio': n_term / total if total > 0 else 0,
        'operator_ratio': n_oper / total if total > 0 else 0,
        'core_ratio': n_core / total if total > 0 else 0,
    })

term_ratios = [r['terminator_ratio'] for r in role_distributions]
oper_ratios = [r['operator_ratio'] for r in role_distributions]
core_ratios = [r['core_ratio'] for r in role_distributions]

print(f"\nFunctional role ratios across A records:")
print(f"  TERMINATOR ratio: mean={np.mean(term_ratios):.3f}, std={np.std(term_ratios):.3f}, range=[{np.min(term_ratios):.3f}, {np.max(term_ratios):.3f}]")
print(f"  OPERATOR ratio: mean={np.mean(oper_ratios):.3f}, std={np.std(oper_ratios):.3f}, range=[{np.min(oper_ratios):.3f}, {np.max(oper_ratios):.3f}]")
print(f"  CORE ratio: mean={np.mean(core_ratios):.3f}, std={np.std(core_ratios):.3f}, range=[{np.min(core_ratios):.3f}, {np.max(core_ratios):.3f}]")

# Check for bimodality in role ratios
print(f"\nRole ratio variance (low = all A records similar, high = process types differ):")
print(f"  TERMINATOR CV: {np.std(term_ratios)/np.mean(term_ratios):.3f}" if np.mean(term_ratios) > 0 else "  TERMINATOR: N/A")
print(f"  OPERATOR CV: {np.std(oper_ratios)/np.mean(oper_ratios):.3f}" if np.mean(oper_ratios) > 0 else "  OPERATOR: N/A")
print(f"  CORE CV: {np.std(core_ratios)/np.mean(core_ratios):.3f}" if np.mean(core_ratios) > 0 else "  CORE: N/A")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: PROCESS TYPE EVIDENCE")
print("=" * 70)

print("""
EVIDENCE FOR DIFFERENT PROCESS TYPES:
- Distinct clustering of A records by B profile
- Bimodal distribution of kernel involvement
- Class pairs that NEVER co-occur (mutual exclusion)
- High variance in functional role ratios

EVIDENCE FOR UNIFIED PROCESS:
- Continuous variation in class profiles
- Normal distribution of kernel involvement
- All classes can co-occur (no strict modules)
- Low variance in functional role ratios
""")

# Final verdict
mean_jaccard = np.mean(distances)
if mean_jaccard < 0.3:
    verdict = "STRONG EVIDENCE FOR UNIFIED: A records activate very similar B profiles"
elif mean_jaccard < 0.5:
    verdict = "MODERATE: Some variation but not distinct process types"
else:
    verdict = "POSSIBLE PROCESS TYPES: A records activate qualitatively different B profiles"

print(f"VERDICT: {verdict}")
print(f"(Mean Jaccard distance between A record B-profiles: {mean_jaccard:.3f})")
