#!/usr/bin/env python3
"""
Test: Do different A records activate different TOKEN SUBSETS within the same classes?

The user's insight: Processing vs distillation control could use the SAME classes
but DIFFERENT tokens within those classes. The distinction is at member/token level,
not class level.

For example:
- Class 34 might have "adjust heat" tokens AND "grind material" tokens
- Both are OPERATOR class, appear in medial position
- Class profile looks identical
- But WHICH TOKENS are activated differs

Test: Do A records cluster by token composition, not just class composition?
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

df_b = df[df['language'] == 'B'].copy()

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)
token_to_class = data['token_to_class']
class_to_tokens = data['class_to_tokens']

# Load survivor data
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivor_data = json.load(f)

# Get all B tokens
all_b_tokens = sorted(set(df_b['word'].dropna()) & set(token_to_class.keys()))
token_to_idx = {t: i for i, t in enumerate(all_b_tokens)}

print("=" * 70)
print("TOKEN-LEVEL PROCESS TYPE TEST")
print("=" * 70)
print(f"\nTotal classified B tokens: {len(all_b_tokens)}")

# Extract MIDDLE
def get_middle(token):
    if pd.isna(token) or len(str(token)) < 2:
        return None
    token = str(token)
    return token[1:-1] if len(token) > 2 else (token[1] if len(token) == 2 else None)

# =============================================================================
# Build A record -> surviving TOKEN profiles
# =============================================================================
print("\nBuilding A record -> surviving token profiles...")

# For each A record, which specific TOKENS survive (not just classes)?
a_record_tokens = {}

for record in survivor_data['records']:
    record_id = record['a_record']
    a_middles = set(record.get('a_middles', []))

    if len(a_middles) < 2:
        continue

    # Find B tokens whose MIDDLE is in the A record's MIDDLE set
    surviving_tokens = set()
    for token in all_b_tokens:
        mid = get_middle(token)
        if mid and mid in a_middles:
            surviving_tokens.add(token)

    if len(surviving_tokens) >= 10:
        a_record_tokens[record_id] = surviving_tokens

print(f"A records with 10+ surviving tokens: {len(a_record_tokens)}")

# =============================================================================
# TEST 1: Token-Level Jaccard Distance
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: TOKEN-LEVEL PROFILE DISTANCES")
print("=" * 70)

# Sample for computational feasibility
record_ids = list(a_record_tokens.keys())[:300]

# Compute pairwise Jaccard at TOKEN level
token_distances = []
for i in range(len(record_ids)):
    for j in range(i+1, len(record_ids)):
        tokens_i = a_record_tokens[record_ids[i]]
        tokens_j = a_record_tokens[record_ids[j]]
        intersection = len(tokens_i & tokens_j)
        union = len(tokens_i | tokens_j)
        jaccard = 1 - (intersection / union) if union > 0 else 1
        token_distances.append(jaccard)

print(f"\nToken-level Jaccard distances (n={len(token_distances)} pairs):")
print(f"  Mean: {np.mean(token_distances):.3f}")
print(f"  Std: {np.std(token_distances):.3f}")
print(f"  Min: {np.min(token_distances):.3f}")
print(f"  Max: {np.max(token_distances):.3f}")

# Compare to class-level (from previous test)
print(f"\nComparison:")
print(f"  Class-level mean Jaccard: 0.391")
print(f"  Token-level mean Jaccard: {np.mean(token_distances):.3f}")
print(f"  Difference: {np.mean(token_distances) - 0.391:.3f}")

# =============================================================================
# TEST 2: Within-Class Token Divergence
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: WITHIN-CLASS TOKEN SELECTION DIVERGENCE")
print("=" * 70)
print("\nFor records that activate the SAME classes, do they activate DIFFERENT tokens?")

# Find pairs of A records with identical class profiles
class_profiles = {}
for record_id in record_ids:
    tokens = a_record_tokens[record_id]
    classes = frozenset(token_to_class[t] for t in tokens if t in token_to_class)
    class_profiles[record_id] = classes

# Group by class profile
profile_to_records = defaultdict(list)
for record_id, classes in class_profiles.items():
    profile_to_records[classes].append(record_id)

same_class_groups = [(profile, recs) for profile, recs in profile_to_records.items() if len(recs) >= 2]
print(f"\nGroups of A records with IDENTICAL class profiles: {len(same_class_groups)}")

# For same-class pairs, what's the token-level divergence?
same_class_token_divergences = []
for profile, recs in same_class_groups:
    for i in range(len(recs)):
        for j in range(i+1, len(recs)):
            tokens_i = a_record_tokens[recs[i]]
            tokens_j = a_record_tokens[recs[j]]
            intersection = len(tokens_i & tokens_j)
            union = len(tokens_i | tokens_j)
            jaccard_dist = 1 - (intersection / union) if union > 0 else 1
            same_class_token_divergences.append(jaccard_dist)

if same_class_token_divergences:
    print(f"\nToken divergence for SAME-CLASS-PROFILE pairs:")
    print(f"  N pairs: {len(same_class_token_divergences)}")
    print(f"  Mean Jaccard distance: {np.mean(same_class_token_divergences):.3f}")
    print(f"  Std: {np.std(same_class_token_divergences):.3f}")
    print(f"  Range: [{np.min(same_class_token_divergences):.3f}, {np.max(same_class_token_divergences):.3f}]")

    if np.mean(same_class_token_divergences) > 0.1:
        print("\n  -> SIGNIFICANT: Same classes but different tokens!")
        print("     This supports process-type distinction at token level.")
    else:
        print("\n  -> MINIMAL: Same classes = same tokens")
        print("     Token selection is determined by class selection.")

# =============================================================================
# TEST 3: Token Clustering Within Specific Classes
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: DO TOKENS WITHIN A CLASS CLUSTER BY A-RECORD?")
print("=" * 70)

# For a specific high-frequency class, check if its tokens cluster
# based on which A records activate them

# Pick class 34 (high frequency OPERATOR)
test_class = 34
class_tokens = [t for t in all_b_tokens if token_to_class.get(t) == test_class]
print(f"\nAnalyzing class {test_class}: {len(class_tokens)} tokens")

# For each token, which A records activate it?
token_to_a_records = defaultdict(set)
for record_id in record_ids:
    surviving = a_record_tokens[record_id]
    for token in surviving:
        if token_to_class.get(token) == test_class:
            token_to_a_records[token].add(record_id)

# Filter to tokens that appear in at least 5 A records
active_tokens = {t: recs for t, recs in token_to_a_records.items() if len(recs) >= 5}
print(f"Tokens active in 5+ A records: {len(active_tokens)}")

if len(active_tokens) >= 10:
    # Compute token-token similarity by A-record overlap
    token_list = list(active_tokens.keys())
    token_sims = []

    for i in range(len(token_list)):
        for j in range(i+1, len(token_list)):
            recs_i = active_tokens[token_list[i]]
            recs_j = active_tokens[token_list[j]]
            intersection = len(recs_i & recs_j)
            union = len(recs_i | recs_j)
            sim = intersection / union if union > 0 else 0
            token_sims.append(sim)

    print(f"\nToken-token A-record overlap (Jaccard similarity):")
    print(f"  Mean: {np.mean(token_sims):.3f}")
    print(f"  Std: {np.std(token_sims):.3f}")

    # Check for bimodality (would suggest token clusters)
    if np.std(token_sims) > 0.15:
        print("  -> HIGH VARIANCE: Tokens may cluster into groups")
    else:
        print("  -> LOW VARIANCE: Tokens activated fairly uniformly")

# =============================================================================
# TEST 4: MIDDLE-Based Token Partitioning
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: DO DIFFERENT A-RECORD MIDDLEs ACTIVATE DIFFERENT B TOKENS?")
print("=" * 70)

# Group A records by their MIDDLE composition similarity
# Then check if similar-MIDDLE A records activate similar tokens

# Build MIDDLE profiles for each A record
a_middle_profiles = {}
for record in survivor_data['records'][:300]:
    record_id = record['a_record']
    a_middles = frozenset(record.get('a_middles', []))
    if len(a_middles) >= 2 and record_id in a_record_tokens:
        a_middle_profiles[record_id] = a_middles

# Compute MIDDLE-level vs token-level correlation
middle_dists = []
token_dists_paired = []

record_list = list(a_middle_profiles.keys())[:200]
for i in range(len(record_list)):
    for j in range(i+1, min(i+50, len(record_list))):  # Sample for speed
        mid_i = a_middle_profiles[record_list[i]]
        mid_j = a_middle_profiles[record_list[j]]
        mid_intersection = len(mid_i & mid_j)
        mid_union = len(mid_i | mid_j)
        mid_dist = 1 - (mid_intersection / mid_union) if mid_union > 0 else 1

        tok_i = a_record_tokens[record_list[i]]
        tok_j = a_record_tokens[record_list[j]]
        tok_intersection = len(tok_i & tok_j)
        tok_union = len(tok_i | tok_j)
        tok_dist = 1 - (tok_intersection / tok_union) if tok_union > 0 else 1

        middle_dists.append(mid_dist)
        token_dists_paired.append(tok_dist)

corr, p = stats.spearmanr(middle_dists, token_dists_paired)
print(f"\nCorrelation between A-MIDDLE distance and B-token distance:")
print(f"  rho = {corr:.3f}, p = {p:.2e}")

if corr > 0.8:
    print("  -> VERY HIGH: Token selection is fully determined by MIDDLE selection")
    print("     No independent token-level process types")
elif corr > 0.5:
    print("  -> MODERATE: MIDDLEs predict tokens but some independent variation")
else:
    print("  -> LOW: Token selection has independence from MIDDLE selection")
    print("     Possible process-type distinction at token level")

# =============================================================================
# TEST 5: Token Mutual Exclusion
# =============================================================================
print("\n" + "=" * 70)
print("TEST 5: TOKEN-LEVEL MUTUAL EXCLUSION")
print("=" * 70)
print("\nAre there token pairs that NEVER co-occur across A records?")

# For tokens within the same class, check if any are mutually exclusive
mutual_exclusion_count = 0
tested_pairs = 0

for cls in range(1, 50):
    cls_tokens = [t for t in all_b_tokens if token_to_class.get(t) == cls]
    if len(cls_tokens) < 5:
        continue

    # Get A-record activation for each token
    token_activations = {}
    for tok in cls_tokens:
        activating_records = set()
        for record_id in record_ids:
            if tok in a_record_tokens.get(record_id, set()):
                activating_records.add(record_id)
        if len(activating_records) >= 3:
            token_activations[tok] = activating_records

    # Check for mutual exclusion
    tok_list = list(token_activations.keys())
    for i in range(len(tok_list)):
        for j in range(i+1, len(tok_list)):
            tested_pairs += 1
            recs_i = token_activations[tok_list[i]]
            recs_j = token_activations[tok_list[j]]
            if len(recs_i & recs_j) == 0:
                mutual_exclusion_count += 1

print(f"\nWithin-class token pairs tested: {tested_pairs}")
print(f"Mutually exclusive pairs (never co-activated): {mutual_exclusion_count}")
print(f"Mutual exclusion rate: {100*mutual_exclusion_count/tested_pairs:.2f}%" if tested_pairs > 0 else "N/A")

if mutual_exclusion_count > tested_pairs * 0.05:
    print("\n  -> SIGNIFICANT MUTUAL EXCLUSION")
    print("     Different A records activate different tokens within same class")
    print("     Supports process-type distinction at token level")
else:
    print("\n  -> MINIMAL MUTUAL EXCLUSION")
    print("     Tokens within classes are co-activated broadly")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: TOKEN-LEVEL PROCESS TYPE EVIDENCE")
print("=" * 70)

print(f"""
KEY METRICS:
- Token-level Jaccard distance: {np.mean(token_distances):.3f} (vs 0.391 at class level)
- Same-class token divergence: {np.mean(same_class_token_divergences):.3f if same_class_token_divergences else 'N/A'}
- MIDDLE-to-token correlation: rho={corr:.3f}
- Token mutual exclusion rate: {100*mutual_exclusion_count/tested_pairs:.1f}%

INTERPRETATION:
""")

if np.mean(same_class_token_divergences) > 0.15 if same_class_token_divergences else False:
    print("EVIDENCE FOR TOKEN-LEVEL PROCESS TYPES:")
    print("- Same classes but different token selections")
    print("- A records may distinguish 'processing' vs 'control' at token level")
else:
    print("EVIDENCE AGAINST TOKEN-LEVEL PROCESS TYPES:")
    print("- Token selection determined by class/MIDDLE selection")
    print("- No independent token-level distinction")
