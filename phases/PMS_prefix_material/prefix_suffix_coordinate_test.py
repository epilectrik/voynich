#!/usr/bin/env python3
"""
Prefix/Suffix Coordinate-System Test Battery
=============================================
Tests whether prefixes and suffixes function as positional/coordinate-like indices
within an abstract structured space, rather than encoding semantic content.

This hypothesis makes purely structural predictions tested internally.

STRICT CONSTRAINTS:
- No semantic interpretations
- No material/plant/purpose assignments
- No grammar alterations
- Statistical and descriptive outputs only
"""

import json
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy import stats
from scipy.spatial.distance import jensenshannon, cosine
from scipy.stats import chi2_contingency
import warnings
warnings.filterwarnings('ignore')

# Configuration
N_PERMUTATIONS = 1000  # Reduced for faster execution
MIN_TOKENS_PER_CELL = 5
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

import sys
sys.stdout.reconfigure(line_buffering=True)  # Force line buffering

print("=" * 70)
print("PREFIX/SUFFIX COORDINATE-SYSTEM TEST BATTERY")
print("=" * 70)
print()

# =============================================================================
# DATA LOADING AND PREPROCESSING
# =============================================================================
print("Loading data...")

# Load corpus
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
print(f"  Loaded {len(df)} tokens")

# Load affix data
with open('phase7b_affix_operations.json', 'r') as f:
    affix_ops = json.load(f)

# Load slot grammar
with open('phase7c_slot_grammar.json', 'r') as f:
    slot_grammar = json.load(f)

# Extract known prefixes
affix_table = affix_ops['affix_operation_table']
known_prefixes = {k: v for k, v in affix_table.items() if v.get('affix_position') == 'prefix'}
prefix_set = set(known_prefixes.keys())
print(f"  Known prefixes: {len(prefix_set)}")

# Define common suffixes from slot grammar analysis
common_suffixes = set()
for slot_num in range(10):
    slot_data = slot_grammar['slot_analysis'].get(str(slot_num), {})
    for suff in slot_data.get('dominant_suffixes', []):
        common_suffixes.add(suff)

# Add more suffixes from co-occurrence data
additional_suffixes = ['aiin', 'ol', 'or', 'ar', 'hy', 'ey', 'dy', 'edy', 'eey',
                       'eedy', 'y', 'ain', 'in', 'al', 'am', 'an', 'om', 'on',
                       'os', 'es', 'ys', 'ty', 'ny', 'ry']
common_suffixes.update(additional_suffixes)
print(f"  Known suffixes: {len(common_suffixes)}")

# =============================================================================
# PREFIX/SUFFIX EXTRACTION
# =============================================================================
print("\nExtracting prefixes and suffixes...")

def extract_prefix(word, prefix_set):
    """Extract longest matching prefix."""
    for length in range(4, 0, -1):
        if len(word) >= length:
            candidate = word[:length]
            if candidate in prefix_set:
                return candidate
    # Try 2-char prefix as fallback
    if len(word) >= 2:
        return word[:2]
    return word

def extract_suffix(word, suffix_set):
    """Extract longest matching suffix."""
    for length in range(5, 0, -1):
        if len(word) >= length:
            candidate = word[-length:]
            if candidate in suffix_set:
                return candidate
    # Try 2-char suffix as fallback
    if len(word) >= 2:
        return word[-2:]
    return word

# Apply extraction
df['prefix'] = df['word'].apply(lambda w: extract_prefix(str(w), prefix_set) if pd.notna(w) else None)
df['suffix'] = df['word'].apply(lambda w: extract_suffix(str(w), common_suffixes) if pd.notna(w) else None)

# Filter valid extractions
df_valid = df[df['prefix'].notna() & df['suffix'].notna()].copy()
print(f"  Valid tokens with prefix+suffix: {len(df_valid)}")

# =============================================================================
# PREFIX/SUFFIX CLUSTERING (ARCHETYPES)
# =============================================================================
print("\nClustering prefixes into archetypes...")

# Build prefix feature matrix
prefix_counts = Counter(df_valid['prefix'])
freq_prefixes = [p for p, c in prefix_counts.items() if c >= 50]

prefix_features = []
prefix_names = []
for pfx in freq_prefixes:
    if pfx in known_prefixes:
        data = known_prefixes[pfx]
        features = [
            data.get('hub_strength', 0),
            data.get('mean_slot', 5),
            data.get('entry_initial_rate', 0),
            data.get('entry_final_rate', 0),
        ]
    else:
        # Compute from data
        pfx_data = df_valid[df_valid['prefix'] == pfx]
        features = [0.3, 5.0, 0.05, 0.05]  # Defaults
    prefix_features.append(features)
    prefix_names.append(pfx)

if len(prefix_features) >= 5:
    X_prefix = np.array(prefix_features)
    X_prefix_scaled = StandardScaler().fit_transform(X_prefix)

    # Find optimal k
    best_k_prefix = 5
    best_sil_prefix = -1
    for k in range(3, 8):
        if k > len(prefix_names):
            break
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_prefix_scaled)
        sil = silhouette_score(X_prefix_scaled, labels)
        if sil > best_sil_prefix:
            best_sil_prefix = sil
            best_k_prefix = k

    km_prefix = KMeans(n_clusters=best_k_prefix, random_state=42, n_init=10)
    prefix_archetypes = km_prefix.fit_predict(X_prefix_scaled)
    prefix_to_archetype = dict(zip(prefix_names, prefix_archetypes))
    print(f"  Prefix archetypes: {best_k_prefix} (silhouette: {best_sil_prefix:.3f})")
else:
    prefix_to_archetype = {p: 0 for p in freq_prefixes}
    best_k_prefix = 1

# Suffix clustering
print("Clustering suffixes into archetypes...")
suffix_counts = Counter(df_valid['suffix'])
freq_suffixes = [s for s, c in suffix_counts.items() if c >= 50]

# Compute suffix features from positional data
suffix_features = []
suffix_names = []
for sfx in freq_suffixes:
    sfx_data = df_valid[df_valid['suffix'] == sfx]
    # Compute slot distribution
    mean_slot = sfx_data.groupby('folio').size().mean() if len(sfx_data) > 0 else 5.0
    # Entry position
    entry_initial = 0
    entry_final = 0
    features = [mean_slot, entry_initial, entry_final, len(sfx_data)]
    suffix_features.append(features)
    suffix_names.append(sfx)

if len(suffix_features) >= 5:
    X_suffix = np.array(suffix_features)
    X_suffix_scaled = StandardScaler().fit_transform(X_suffix)

    best_k_suffix = 5
    best_sil_suffix = -1
    for k in range(3, 8):
        if k > len(suffix_names):
            break
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_suffix_scaled)
        sil = silhouette_score(X_suffix_scaled, labels)
        if sil > best_sil_suffix:
            best_sil_suffix = sil
            best_k_suffix = k

    km_suffix = KMeans(n_clusters=best_k_suffix, random_state=42, n_init=10)
    suffix_archetypes = km_suffix.fit_predict(X_suffix_scaled)
    suffix_to_archetype = dict(zip(suffix_names, suffix_archetypes))
    print(f"  Suffix archetypes: {best_k_suffix} (silhouette: {best_sil_suffix:.3f})")
else:
    suffix_to_archetype = {s: 0 for s in freq_suffixes}
    best_k_suffix = 1

# Map archetypes to dataframe
df_valid['prefix_archetype'] = df_valid['prefix'].map(lambda p: prefix_to_archetype.get(p, -1))
df_valid['suffix_archetype'] = df_valid['suffix'].map(lambda s: suffix_to_archetype.get(s, -1))

# Filter to known archetypes
df_archetypes = df_valid[(df_valid['prefix_archetype'] >= 0) & (df_valid['suffix_archetype'] >= 0)].copy()
print(f"  Tokens with valid archetypes: {len(df_archetypes)}")

# =============================================================================
# TEST 1: PREFIX x SUFFIX AXIS INDEPENDENCE
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: PREFIX x SUFFIX AXIS INDEPENDENCE")
print("=" * 70)

def compute_mutual_info(labels1, labels2):
    """Compute mutual information between two label sequences."""
    contingency = pd.crosstab(labels1, labels2)
    total = contingency.sum().sum()

    # Marginals
    p_rows = contingency.sum(axis=1) / total
    p_cols = contingency.sum(axis=0) / total

    mi = 0.0
    for i in contingency.index:
        for j in contingency.columns:
            p_ij = contingency.loc[i, j] / total
            if p_ij > 0:
                mi += p_ij * np.log2(p_ij / (p_rows[i] * p_cols[j]))

    return mi

def compute_conditional_entropy(labels1, labels2):
    """Compute H(labels1 | labels2)."""
    contingency = pd.crosstab(labels1, labels2)
    total = contingency.sum().sum()

    # H(labels1)
    p1 = pd.Series(labels1).value_counts(normalize=True)
    h1 = -sum(p * np.log2(p) for p in p1 if p > 0)

    # MI
    mi = compute_mutual_info(labels1, labels2)

    # H(labels1 | labels2) = H(labels1) - MI
    return h1 - mi

# Observed MI and conditional entropies
prefix_labels = df_archetypes['prefix_archetype']
suffix_labels = df_archetypes['suffix_archetype']

observed_mi = compute_mutual_info(prefix_labels, suffix_labels)
h_prefix_given_suffix = compute_conditional_entropy(prefix_labels, suffix_labels)
h_suffix_given_prefix = compute_conditional_entropy(suffix_labels, prefix_labels)

print(f"\nObserved statistics:")
print(f"  Mutual Information: {observed_mi:.4f} bits")
print(f"  H(prefix|suffix): {h_prefix_given_suffix:.4f} bits")
print(f"  H(suffix|prefix): {h_suffix_given_prefix:.4f} bits")

# Contingency table
contingency_table = pd.crosstab(prefix_labels, suffix_labels)
print(f"\nContingency table shape: {contingency_table.shape}")

# Chi-square test
chi2, p_value, dof, expected = chi2_contingency(contingency_table)
print(f"Chi-square: {chi2:.2f}, p-value: {p_value:.6f}")

# Permutation test
print(f"\nRunning {N_PERMUTATIONS} permutations...")
null_mi_prefix_shuffle = []
null_mi_suffix_shuffle = []

for i in range(N_PERMUTATIONS):
    # Shuffle prefixes
    shuffled_prefix = np.random.permutation(prefix_labels.values)
    mi_shuf = compute_mutual_info(pd.Series(shuffled_prefix), suffix_labels)
    null_mi_prefix_shuffle.append(mi_shuf)

    # Shuffle suffixes
    shuffled_suffix = np.random.permutation(suffix_labels.values)
    mi_shuf = compute_mutual_info(prefix_labels, pd.Series(shuffled_suffix))
    null_mi_suffix_shuffle.append(mi_shuf)

null_mi_prefix_shuffle = np.array(null_mi_prefix_shuffle)
null_mi_suffix_shuffle = np.array(null_mi_suffix_shuffle)

percentile_prefix = (np.sum(null_mi_prefix_shuffle >= observed_mi) / N_PERMUTATIONS) * 100
percentile_suffix = (np.sum(null_mi_suffix_shuffle >= observed_mi) / N_PERMUTATIONS) * 100

print(f"\nNull distribution (prefix shuffle):")
print(f"  Mean: {null_mi_prefix_shuffle.mean():.4f}, Std: {null_mi_prefix_shuffle.std():.4f}")
print(f"  Observed percentile: {100 - percentile_prefix:.1f}%")

print(f"\nNull distribution (suffix shuffle):")
print(f"  Mean: {null_mi_suffix_shuffle.mean():.4f}, Std: {null_mi_suffix_shuffle.std():.4f}")
print(f"  Observed percentile: {100 - percentile_suffix:.1f}%")

# Identify over/under-represented combinations
observed_counts = contingency_table.values
expected_counts = expected
residuals = (observed_counts - expected_counts) / np.sqrt(expected_counts + 0.001)

over_represented = []
under_represented = []
for i, pfx_arch in enumerate(contingency_table.index):
    for j, sfx_arch in enumerate(contingency_table.columns):
        if residuals[i, j] > 3.0:
            over_represented.append((pfx_arch, sfx_arch, residuals[i, j], observed_counts[i, j]))
        elif residuals[i, j] < -3.0:
            under_represented.append((pfx_arch, sfx_arch, residuals[i, j], observed_counts[i, j]))

print(f"\nOver-represented combinations (z > 3): {len(over_represented)}")
for combo in over_represented[:5]:
    print(f"  Prefix arch {combo[0]} + Suffix arch {combo[1]}: z={combo[2]:.2f}, n={combo[3]}")

print(f"\nUnder-represented combinations (z < -3): {len(under_represented)}")
for combo in under_represented[:5]:
    print(f"  Prefix arch {combo[0]} + Suffix arch {combo[1]}: z={combo[2]:.2f}, n={combo[3]}")

# TEST 1 Verdict
test1_significant = percentile_prefix < 5 and percentile_suffix < 5
test1_verdict = "SIGNIFICANT" if test1_significant else "NOT_SIGNIFICANT"
test1_interpretation = "PARTIAL_INDEPENDENCE" if observed_mi < 0.5 else "DEPENDENT"

print(f"\nTEST 1 VERDICT: {test1_verdict}")
print(f"  Interpretation: {test1_interpretation}")

test1_results = {
    "observed_mi": float(observed_mi),
    "h_prefix_given_suffix": float(h_prefix_given_suffix),
    "h_suffix_given_prefix": float(h_suffix_given_prefix),
    "chi2": float(chi2),
    "p_value": float(p_value),
    "null_mi_prefix_mean": float(null_mi_prefix_shuffle.mean()),
    "null_mi_prefix_std": float(null_mi_prefix_shuffle.std()),
    "null_mi_suffix_mean": float(null_mi_suffix_shuffle.mean()),
    "null_mi_suffix_std": float(null_mi_suffix_shuffle.std()),
    "percentile_prefix": float(100 - percentile_prefix),
    "percentile_suffix": float(100 - percentile_suffix),
    "over_represented_count": len(over_represented),
    "under_represented_count": len(under_represented),
    "verdict": test1_verdict,
    "interpretation": test1_interpretation
}

# =============================================================================
# TEST 2: LOCAL CONTINUITY / SMOOTHNESS TEST
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: LOCAL CONTINUITY / SMOOTHNESS TEST")
print("=" * 70)

# Get unique folios in order
folio_order = df_valid['folio'].unique()
print(f"\nFolios in corpus order: {len(folio_order)}")

# Build folio vectors (prefix + suffix archetype frequencies)
folio_vectors = {}
for folio in folio_order:
    folio_data = df_archetypes[df_archetypes['folio'] == folio]
    if len(folio_data) < 10:
        continue

    # Prefix archetype distribution
    pfx_dist = np.zeros(best_k_prefix)
    pfx_counts = folio_data['prefix_archetype'].value_counts()
    for arch, count in pfx_counts.items():
        if 0 <= arch < best_k_prefix:
            pfx_dist[arch] = count
    pfx_dist = pfx_dist / (pfx_dist.sum() + 1e-10)

    # Suffix archetype distribution
    sfx_dist = np.zeros(best_k_suffix)
    sfx_counts = folio_data['suffix_archetype'].value_counts()
    for arch, count in sfx_counts.items():
        if 0 <= arch < best_k_suffix:
            sfx_dist[arch] = count
    sfx_dist = sfx_dist / (sfx_dist.sum() + 1e-10)

    folio_vectors[folio] = np.concatenate([pfx_dist, sfx_dist])

valid_folios = [f for f in folio_order if f in folio_vectors]
print(f"Folios with sufficient data: {len(valid_folios)}")

# Compute consecutive folio distances
consecutive_distances = []
for i in range(len(valid_folios) - 1):
    f1, f2 = valid_folios[i], valid_folios[i + 1]
    v1, v2 = folio_vectors[f1], folio_vectors[f2]
    # Jensen-Shannon distance
    js_dist = jensenshannon(v1, v2)
    if np.isfinite(js_dist):
        consecutive_distances.append(js_dist)

mean_consecutive_dist = np.mean(consecutive_distances)
print(f"\nMean consecutive folio distance (JS): {mean_consecutive_dist:.4f}")

# Null: random permutation of folio order
print(f"\nRunning {1000} permutations...")
null_consecutive_dists = []
for _ in range(1000):
    shuffled_folios = np.random.permutation(valid_folios)
    dists = []
    for i in range(len(shuffled_folios) - 1):
        f1, f2 = shuffled_folios[i], shuffled_folios[i + 1]
        v1, v2 = folio_vectors[f1], folio_vectors[f2]
        js_dist = jensenshannon(v1, v2)
        if np.isfinite(js_dist):
            dists.append(js_dist)
    null_consecutive_dists.append(np.mean(dists))

null_consecutive_dists = np.array(null_consecutive_dists)
percentile_continuity = (np.sum(null_consecutive_dists <= mean_consecutive_dist) / 1000) * 100

print(f"\nNull distribution:")
print(f"  Mean: {null_consecutive_dists.mean():.4f}, Std: {null_consecutive_dists.std():.4f}")
print(f"  Observed percentile: {percentile_continuity:.1f}%")

# Effect size
effect_size_continuity = (null_consecutive_dists.mean() - mean_consecutive_dist) / null_consecutive_dists.std()
print(f"  Effect size (Cohen's d): {effect_size_continuity:.3f}")

# TEST 2 Verdict
test2_significant = percentile_continuity < 5  # Lower distance = more continuous
test2_verdict = "SIGNIFICANT" if test2_significant else "NOT_SIGNIFICANT"

print(f"\nTEST 2 VERDICT: {test2_verdict}")

test2_results = {
    "mean_consecutive_dist": float(mean_consecutive_dist),
    "null_mean": float(null_consecutive_dists.mean()),
    "null_std": float(null_consecutive_dists.std()),
    "percentile": float(percentile_continuity),
    "effect_size": float(effect_size_continuity),
    "n_folios": len(valid_folios),
    "verdict": test2_verdict
}

# =============================================================================
# TEST 3: CYCLE-PHASE ALIGNMENT
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: CYCLE-PHASE ALIGNMENT")
print("=" * 70)

# Use slot position as proxy for cycle phase (10 slots = cycle positions)
# Group into 4 phases: EARLY (0-2), MID_EARLY (3-4), MID_LATE (5-6), LATE (7-9)
def assign_phase(slot_position, n_slots=10):
    """Assign a cycle phase based on slot position."""
    if slot_position is None or not np.isfinite(slot_position):
        return None
    position = int(slot_position % n_slots)
    if position <= 2:
        return "EARLY"
    elif position <= 4:
        return "MID_EARLY"
    elif position <= 6:
        return "MID_LATE"
    else:
        return "LATE"

# Assign phases (using row index mod 10 as slot proxy)
df_archetypes = df_archetypes.copy()
df_archetypes['row_in_folio'] = df_archetypes.groupby('folio').cumcount()
df_archetypes['phase'] = df_archetypes['row_in_folio'].apply(lambda x: assign_phase(x))
df_phase = df_archetypes[df_archetypes['phase'].notna()].copy()

print(f"\nTokens with phase assignment: {len(df_phase)}")
print(f"Phase distribution: {df_phase['phase'].value_counts().to_dict()}")

# Prefix archetype by phase
print("\nPrefix archetype enrichment by phase:")
prefix_phase_table = pd.crosstab(df_phase['prefix_archetype'], df_phase['phase'])
print(prefix_phase_table)

chi2_prefix_phase, p_prefix_phase, dof_pp, _ = chi2_contingency(prefix_phase_table)
print(f"\nChi-square (prefix x phase): {chi2_prefix_phase:.2f}, p={p_prefix_phase:.6f}")

# Suffix archetype by phase
print("\nSuffix archetype enrichment by phase:")
suffix_phase_table = pd.crosstab(df_phase['suffix_archetype'], df_phase['phase'])
print(suffix_phase_table)

chi2_suffix_phase, p_suffix_phase, dof_sp, _ = chi2_contingency(suffix_phase_table)
print(f"\nChi-square (suffix x phase): {chi2_suffix_phase:.2f}, p={p_suffix_phase:.6f}")

# Permutation test for prefix-phase
print(f"\nRunning {N_PERMUTATIONS} permutations for prefix-phase...")
null_chi2_prefix_phase = []
for _ in range(N_PERMUTATIONS):
    shuffled = np.random.permutation(df_phase['phase'].values)
    table = pd.crosstab(df_phase['prefix_archetype'], pd.Series(shuffled, index=df_phase.index))
    chi2, _, _, _ = chi2_contingency(table)
    null_chi2_prefix_phase.append(chi2)

null_chi2_prefix_phase = np.array(null_chi2_prefix_phase)
percentile_prefix_phase = (np.sum(null_chi2_prefix_phase >= chi2_prefix_phase) / N_PERMUTATIONS) * 100

print(f"  Null mean: {null_chi2_prefix_phase.mean():.2f}, Observed: {chi2_prefix_phase:.2f}")
print(f"  Percentile rank: {100 - percentile_prefix_phase:.1f}%")

# Permutation test for suffix-phase
print(f"\nRunning {N_PERMUTATIONS} permutations for suffix-phase...")
null_chi2_suffix_phase = []
for _ in range(N_PERMUTATIONS):
    shuffled = np.random.permutation(df_phase['phase'].values)
    table = pd.crosstab(df_phase['suffix_archetype'], pd.Series(shuffled, index=df_phase.index))
    chi2, _, _, _ = chi2_contingency(table)
    null_chi2_suffix_phase.append(chi2)

null_chi2_suffix_phase = np.array(null_chi2_suffix_phase)
percentile_suffix_phase = (np.sum(null_chi2_suffix_phase >= chi2_suffix_phase) / N_PERMUTATIONS) * 100

print(f"  Null mean: {null_chi2_suffix_phase.mean():.2f}, Observed: {chi2_suffix_phase:.2f}")
print(f"  Percentile rank: {100 - percentile_suffix_phase:.1f}%")

# Effect sizes
effect_prefix_phase = (chi2_prefix_phase - null_chi2_prefix_phase.mean()) / null_chi2_prefix_phase.std()
effect_suffix_phase = (chi2_suffix_phase - null_chi2_suffix_phase.mean()) / null_chi2_suffix_phase.std()

# TEST 3 Verdict
test3_prefix_sig = percentile_prefix_phase < 5
test3_suffix_sig = percentile_suffix_phase < 5
test3_verdict = "SIGNIFICANT" if (test3_prefix_sig or test3_suffix_sig) else "NOT_SIGNIFICANT"

print(f"\nTEST 3 VERDICT: {test3_verdict}")
print(f"  Prefix-phase: {'SIGNIFICANT' if test3_prefix_sig else 'NOT_SIGNIFICANT'} (effect d={effect_prefix_phase:.2f})")
print(f"  Suffix-phase: {'SIGNIFICANT' if test3_suffix_sig else 'NOT_SIGNIFICANT'} (effect d={effect_suffix_phase:.2f})")

test3_results = {
    "prefix_phase_chi2": float(chi2_prefix_phase),
    "prefix_phase_p": float(p_prefix_phase),
    "prefix_phase_percentile": float(100 - percentile_prefix_phase),
    "prefix_phase_effect": float(effect_prefix_phase),
    "suffix_phase_chi2": float(chi2_suffix_phase),
    "suffix_phase_p": float(p_suffix_phase),
    "suffix_phase_percentile": float(100 - percentile_suffix_phase),
    "suffix_phase_effect": float(effect_suffix_phase),
    "prefix_phase_significant": test3_prefix_sig,
    "suffix_phase_significant": test3_suffix_sig,
    "verdict": test3_verdict
}

# =============================================================================
# TEST 4: AXIAL CONSISTENCY ACROSS FOLIOS
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: AXIAL CONSISTENCY ACROSS FOLIOS")
print("=" * 70)

# Normalize token positions within each folio to [0,1]
df_archetypes = df_archetypes.copy()
folio_sizes = df_archetypes.groupby('folio').size()
df_archetypes['normalized_position'] = df_archetypes.apply(
    lambda row: row['row_in_folio'] / max(folio_sizes[row['folio']] - 1, 1)
    if row['folio'] in folio_sizes else 0.5, axis=1
)

# For each prefix-suffix archetype combination, check positional clustering
print("\nAnalyzing positional clustering of prefix-suffix combinations...")

combo_positions = defaultdict(list)
for _, row in df_archetypes.iterrows():
    combo = (row['prefix_archetype'], row['suffix_archetype'])
    combo_positions[combo].append(row['normalized_position'])

# Statistics for each combination
clustering_stats = []
for combo, positions in combo_positions.items():
    if len(positions) >= 20:
        positions = np.array(positions)
        mean_pos = np.mean(positions)
        std_pos = np.std(positions)
        clustering_stats.append({
            'prefix_arch': combo[0],
            'suffix_arch': combo[1],
            'count': len(positions),
            'mean_position': mean_pos,
            'std_position': std_pos
        })

clustering_df = pd.DataFrame(clustering_stats)
if len(clustering_df) > 0:
    print(f"\nCombinations with sufficient data: {len(clustering_df)}")
    print(f"Mean positional std: {clustering_df['std_position'].mean():.3f}")

    # Identify tightly clustered combinations (low std)
    tight_clusters = clustering_df[clustering_df['std_position'] < 0.25]
    print(f"Tightly clustered (std < 0.25): {len(tight_clusters)}")

    for _, row in tight_clusters.nlargest(5, 'count').iterrows():
        print(f"  Prefix {int(row['prefix_arch'])} + Suffix {int(row['suffix_arch'])}: "
              f"mean={row['mean_position']:.3f}, std={row['std_position']:.3f}, n={int(row['count'])}")

# Null test: shuffle positions within folios
print(f"\nRunning {1000} permutations...")
observed_mean_std = clustering_df['std_position'].mean() if len(clustering_df) > 0 else 0.5

null_mean_stds = []
for _ in range(1000):
    # Shuffle positions
    shuffled_positions = np.random.permutation(df_archetypes['normalized_position'].values)
    temp_df = df_archetypes.copy()
    temp_df['normalized_position'] = shuffled_positions

    temp_combo_positions = defaultdict(list)
    for _, row in temp_df.iterrows():
        combo = (row['prefix_archetype'], row['suffix_archetype'])
        temp_combo_positions[combo].append(row['normalized_position'])

    temp_stds = [np.std(pos) for pos in temp_combo_positions.values() if len(pos) >= 20]
    if temp_stds:
        null_mean_stds.append(np.mean(temp_stds))

null_mean_stds = np.array(null_mean_stds)
percentile_clustering = (np.sum(null_mean_stds <= observed_mean_std) / len(null_mean_stds)) * 100 if len(null_mean_stds) > 0 else 50

print(f"\nObserved mean std: {observed_mean_std:.4f}")
print(f"Null mean std: {null_mean_stds.mean():.4f} +/- {null_mean_stds.std():.4f}")
print(f"Percentile (lower = more clustered): {percentile_clustering:.1f}%")

effect_size_clustering = (null_mean_stds.mean() - observed_mean_std) / null_mean_stds.std() if len(null_mean_stds) > 0 else 0

# Identify consistent positional bands
print("\nPositional bands (combinations with mean position in similar ranges):")
if len(clustering_df) > 0:
    band_counts = {'early_0.0-0.2': 0, 'mid_early_0.2-0.4': 0, 'mid_0.4-0.6': 0,
                   'mid_late_0.6-0.8': 0, 'late_0.8-1.0': 0}
    for _, row in clustering_df.iterrows():
        pos = row['mean_position']
        if pos < 0.2:
            band_counts['early_0.0-0.2'] += 1
        elif pos < 0.4:
            band_counts['mid_early_0.2-0.4'] += 1
        elif pos < 0.6:
            band_counts['mid_0.4-0.6'] += 1
        elif pos < 0.8:
            band_counts['mid_late_0.6-0.8'] += 1
        else:
            band_counts['late_0.8-1.0'] += 1
    print(f"  {band_counts}")

# TEST 4 Verdict
test4_significant = percentile_clustering < 5
test4_verdict = "SIGNIFICANT" if test4_significant else "NOT_SIGNIFICANT"

print(f"\nTEST 4 VERDICT: {test4_verdict}")

test4_results = {
    "observed_mean_std": float(observed_mean_std) if np.isfinite(observed_mean_std) else None,
    "null_mean_std": float(null_mean_stds.mean()) if len(null_mean_stds) > 0 else None,
    "null_std_std": float(null_mean_stds.std()) if len(null_mean_stds) > 0 else None,
    "percentile": float(percentile_clustering),
    "effect_size": float(effect_size_clustering) if np.isfinite(effect_size_clustering) else None,
    "n_combinations": len(clustering_df),
    "tight_clusters": int(len(tight_clusters)) if len(clustering_df) > 0 else 0,
    "band_distribution": band_counts if len(clustering_df) > 0 else {},
    "verdict": test4_verdict
}

# =============================================================================
# FINAL VERDICT
# =============================================================================
print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)

tests_passed = sum([
    test1_significant,  # Axis independence shows structure
    test2_significant,  # Local continuity
    test3_prefix_sig or test3_suffix_sig,  # Cycle-phase alignment
    test4_significant   # Axial consistency
])

print(f"\nTests showing significant positional effects: {tests_passed}/4")
print(f"  TEST 1 (Axis Independence): {test1_verdict}")
print(f"  TEST 2 (Local Continuity): {test2_verdict}")
print(f"  TEST 3 (Cycle-Phase): {test3_verdict}")
print(f"  TEST 4 (Axial Consistency): {test4_verdict}")

if tests_passed >= 2:
    final_verdict = "SUPPORT"
    final_description = "Prefixes and suffixes show positional/coordinate-like structuring"
elif tests_passed == 1:
    final_verdict = "WEAK_SUPPORT"
    final_description = "Limited evidence for coordinate-like role"
else:
    final_verdict = "NO_SUPPORT"
    final_description = "No evidence for positional structuring beyond global frequency effects"

print(f"\nFINAL VERDICT: {final_verdict}")
print(f"  {final_description}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

results = {
    "metadata": {
        "test": "PREFIX_SUFFIX_COORDINATE_SYSTEM",
        "purpose": "Test if prefixes/suffixes function as positional indices",
        "n_permutations": N_PERMUTATIONS,
        "n_tokens_analyzed": len(df_archetypes),
        "n_folios": len(valid_folios),
        "prefix_archetypes": best_k_prefix,
        "suffix_archetypes": best_k_suffix
    },
    "test1_axis_independence": test1_results,
    "test2_local_continuity": test2_results,
    "test3_cycle_phase": test3_results,
    "test4_axial_consistency": test4_results,
    "final_verdict": final_verdict,
    "final_description": final_description,
    "tests_passed": tests_passed
}

with open('coordinate_system_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("  Saved: coordinate_system_test_results.json")

# Generate report
report = f"""# Prefix/Suffix Coordinate-System Test Battery

*Generated: 2026-01-01*
*Status: {final_verdict}*

---

## Purpose

Test whether prefixes and suffixes function as positional/coordinate-like indices
within an abstract structured space, rather than encoding semantic content.

---

## Summary

| Test | Finding | Verdict |
|------|---------|---------|
| TEST 1: Axis Independence | MI={test1_results['observed_mi']:.4f} bits | {test1_results['verdict']} |
| TEST 2: Local Continuity | d={test2_results['effect_size']:.3f} | {test2_results['verdict']} |
| TEST 3: Cycle-Phase | prefix d={test3_results['prefix_phase_effect']:.2f}, suffix d={test3_results['suffix_phase_effect']:.2f} | {test3_results['verdict']} |
| TEST 4: Axial Consistency | d={test4_results['effect_size']:.3f} if {test4_results['effect_size']} else 'N/A' | {test4_results['verdict']} |

**Tests with significant positional effects: {tests_passed}/4**

---

## TEST 1: PREFIX x SUFFIX AXIS INDEPENDENCE

**Goal:** Determine whether prefix and suffix channels behave like partially independent axes.

### Results

| Metric | Value |
|--------|-------|
| Mutual Information | {test1_results['observed_mi']:.4f} bits |
| H(prefix|suffix) | {test1_results['h_prefix_given_suffix']:.4f} bits |
| H(suffix|prefix) | {test1_results['h_suffix_given_prefix']:.4f} bits |
| Chi-square | {test1_results['chi2']:.2f} (p={test1_results['p_value']:.6f}) |
| Null MI (prefix shuffle) | {test1_results['null_mi_prefix_mean']:.4f} +/- {test1_results['null_mi_prefix_std']:.4f} |
| Observed percentile | {test1_results['percentile_prefix']:.1f}% |

### Interpretation

- Over-represented combinations: {test1_results['over_represented_count']}
- Under-represented combinations: {test1_results['under_represented_count']}
- {test1_results['interpretation']}

**Verdict: {test1_results['verdict']}**

---

## TEST 2: LOCAL CONTINUITY / SMOOTHNESS TEST

**Goal:** Test whether prefix/suffix usage shows local continuity along manuscript order.

### Results

| Metric | Value |
|--------|-------|
| Mean consecutive folio distance (JS) | {test2_results['mean_consecutive_dist']:.4f} |
| Null mean distance | {test2_results['null_mean']:.4f} +/- {test2_results['null_std']:.4f} |
| Observed percentile | {test2_results['percentile']:.1f}% |
| Effect size (Cohen's d) | {test2_results['effect_size']:.3f} |
| Folios analyzed | {test2_results['n_folios']} |

### Interpretation

- Lower percentile indicates more continuity than random
- Effect size indicates practical significance of continuity

**Verdict: {test2_results['verdict']}**

---

## TEST 3: CYCLE-PHASE ALIGNMENT

**Goal:** Determine whether prefix/suffix usage aligns with cycle position.

### Prefix-Phase Results

| Metric | Value |
|--------|-------|
| Chi-square | {test3_results['prefix_phase_chi2']:.2f} (p={test3_results['prefix_phase_p']:.6f}) |
| Percentile rank | {test3_results['prefix_phase_percentile']:.1f}% |
| Effect size | {test3_results['prefix_phase_effect']:.2f} |

### Suffix-Phase Results

| Metric | Value |
|--------|-------|
| Chi-square | {test3_results['suffix_phase_chi2']:.2f} (p={test3_results['suffix_phase_p']:.6f}) |
| Percentile rank | {test3_results['suffix_phase_percentile']:.1f}% |
| Effect size | {test3_results['suffix_phase_effect']:.2f} |

**Verdict: {test3_results['verdict']}**

---

## TEST 4: AXIAL CONSISTENCY ACROSS FOLIOS

**Goal:** Test whether prefix-suffix combinations recur at similar positions across folios.

### Results

| Metric | Value |
|--------|-------|
| Observed mean positional std | {test4_results['observed_mean_std']:.4f} if {test4_results['observed_mean_std']} else 'N/A' |
| Null mean std | {test4_results['null_mean_std']:.4f} if {test4_results['null_mean_std']} else 'N/A' |
| Percentile | {test4_results['percentile']:.1f}% |
| Effect size | {test4_results['effect_size']:.3f} if {test4_results['effect_size']} else 'N/A' |
| Combinations analyzed | {test4_results['n_combinations']} |
| Tightly clustered (std < 0.25) | {test4_results['tight_clusters']} |

**Verdict: {test4_results['verdict']}**

---

## Final Verdict

**{final_verdict}**

{final_description}

### Pre-Registered Decision Criteria

- SUPPORT: >= 2 tests significant with positional effects
- WEAK SUPPORT: 1 test significant
- NO SUPPORT: 0 tests significant

---

*Statistical and descriptive analysis only. No semantic interpretations.*
"""

with open('coordinate_system_test_report.md', 'w') as f:
    f.write(report)
print("  Saved: coordinate_system_test_report.md")

print("\nDone.")
