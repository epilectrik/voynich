#!/usr/bin/env python3
"""
Coordinate Geometry Reconstruction
==================================
Reconstructs the shape and dimensionality of the coordinate system
encoded by prefix/suffix usage across folios.

STRICTLY STRUCTURAL - NO SEMANTICS
"""

import json
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy import stats
from scipy.spatial.distance import cdist, euclidean
import warnings
warnings.filterwarnings('ignore')

import sys
sys.stdout.reconfigure(line_buffering=True)

N_BOOTSTRAP = 100
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

print("=" * 70)
print("COORDINATE GEOMETRY RECONSTRUCTION")
print("=" * 70)
print()

# =============================================================================
# DATA LOADING
# =============================================================================
print("Loading data...")

# Load corpus
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']

# Load affix operations for prefix identification
with open('phase7b_affix_operations.json', 'r') as f:
    affix_ops = json.load(f)

# Load control signatures for hazard/intensity data
with open('control_signatures.json', 'r') as f:
    control_sigs = json.load(f)

affix_table = affix_ops['affix_operation_table']
known_prefixes = set(k for k, v in affix_table.items() if v.get('affix_position') == 'prefix')

# Common suffixes
common_suffixes = {'aiin', 'ol', 'or', 'ar', 'hy', 'ey', 'dy', 'edy', 'eey',
                   'eedy', 'y', 'ain', 'in', 'al', 'am', 'an', 'om', 'on',
                   'os', 'es', 'ys', 'ty', 'ny', 'ry'}

print(f"  Loaded {len(df)} tokens")
print(f"  Known prefixes: {len(known_prefixes)}")
print(f"  Control signatures: {len(control_sigs.get('signatures', {}))} folios")

# =============================================================================
# PREFIX/SUFFIX EXTRACTION
# =============================================================================
print("\nExtracting prefix/suffix features...")

def extract_prefix(word, prefix_set):
    for length in range(4, 0, -1):
        if len(word) >= length and word[:length] in prefix_set:
            return word[:length]
    return word[:2] if len(word) >= 2 else word

def extract_suffix(word, suffix_set):
    for length in range(5, 0, -1):
        if len(word) >= length and word[-length:] in suffix_set:
            return word[-length:]
    return word[-2:] if len(word) >= 2 else word

df['prefix'] = df['word'].apply(lambda w: extract_prefix(str(w), known_prefixes) if pd.notna(w) else None)
df['suffix'] = df['word'].apply(lambda w: extract_suffix(str(w), common_suffixes) if pd.notna(w) else None)

# Get prefix/suffix archetypes (top N by frequency)
prefix_counts = Counter(df['prefix'].dropna())
suffix_counts = Counter(df['suffix'].dropna())

top_prefixes = [p for p, c in prefix_counts.most_common(15)]
top_suffixes = [s for s, c in suffix_counts.most_common(10)]

print(f"  Top prefixes: {top_prefixes[:5]}...")
print(f"  Top suffixes: {top_suffixes[:5]}...")

# =============================================================================
# BUILD FOLIO VECTORS
# =============================================================================
print("\nBuilding folio coordinate vectors...")

folio_order = df['folio'].unique()
folio_vectors = {}
folio_control = {}

for folio in folio_order:
    folio_data = df[df['folio'] == folio]
    if len(folio_data) < 10:
        continue

    # Prefix distribution
    pfx_counts = Counter(folio_data['prefix'].dropna())
    pfx_vec = np.array([pfx_counts.get(p, 0) for p in top_prefixes], dtype=float)
    pfx_vec = pfx_vec / (pfx_vec.sum() + 1e-10)

    # Suffix distribution
    sfx_counts = Counter(folio_data['suffix'].dropna())
    sfx_vec = np.array([sfx_counts.get(s, 0) for s in top_suffixes], dtype=float)
    sfx_vec = sfx_vec / (sfx_vec.sum() + 1e-10)

    folio_vectors[folio] = np.concatenate([pfx_vec, sfx_vec])

    # Get control signature if available
    sig = control_sigs.get('signatures', {}).get(folio, {})
    folio_control[folio] = {
        'hazard_density': sig.get('hazard_density', 0.5),
        'kernel_contact_ratio': sig.get('kernel_contact_ratio', 0.5),
        'link_density': sig.get('link_density', 0.3),
        'cycle_count': sig.get('cycle_count', 50)
    }

valid_folios = [f for f in folio_order if f in folio_vectors]
X = np.array([folio_vectors[f] for f in valid_folios])
X_scaled = StandardScaler().fit_transform(X)

print(f"  Valid folios: {len(valid_folios)}")
print(f"  Feature dimensions: {X.shape[1]} (prefix + suffix)")

# =============================================================================
# TEST G-1: DIMENSIONALITY ESTIMATION
# =============================================================================
print("\n" + "=" * 70)
print("TEST G-1: DIMENSIONALITY ESTIMATION")
print("=" * 70)

# PCA
pca = PCA()
pca_coords = pca.fit_transform(X_scaled)
explained_var = pca.explained_variance_ratio_
cumulative_var = np.cumsum(explained_var)

print("\nPCA variance explained:")
for i in range(min(10, len(explained_var))):
    print(f"  PC{i+1}: {explained_var[i]:.3f} (cumulative: {cumulative_var[i]:.3f})")

# Find elbow (95% variance)
n_components_95 = np.argmax(cumulative_var >= 0.95) + 1
n_components_90 = np.argmax(cumulative_var >= 0.90) + 1
n_components_80 = np.argmax(cumulative_var >= 0.80) + 1

print(f"\nEffective dimensionality:")
print(f"  80% variance: {n_components_80} components")
print(f"  90% variance: {n_components_90} components")
print(f"  95% variance: {n_components_95} components")

# Bootstrap stability
print(f"\nBootstrap stability ({N_BOOTSTRAP} iterations)...")
bootstrap_dims = []
for _ in range(N_BOOTSTRAP):
    idx = np.random.choice(len(X_scaled), size=len(X_scaled), replace=True)
    X_boot = X_scaled[idx]
    pca_boot = PCA()
    pca_boot.fit(X_boot)
    cum_var = np.cumsum(pca_boot.explained_variance_ratio_)
    bootstrap_dims.append(np.argmax(cum_var >= 0.90) + 1)

dim_stability = np.std(bootstrap_dims)
print(f"  90% variance dimension: {np.mean(bootstrap_dims):.1f} +/- {dim_stability:.2f}")

# Isomap for nonlinear structure
print("\nIsomap embedding (checking for curved manifold)...")
try:
    isomap = Isomap(n_components=3, n_neighbors=10)
    isomap_coords = isomap.fit_transform(X_scaled)
    isomap_success = True
    print("  Isomap embedding successful")
except Exception as e:
    isomap_success = False
    isomap_coords = pca_coords[:, :3]
    print(f"  Isomap failed: {e}, using PCA instead")

# Compare PCA vs Isomap reconstruction
if isomap_success:
    pca_3d = pca_coords[:, :3]
    # Compute pairwise distance preservation
    pca_dists = cdist(pca_3d, pca_3d)
    isomap_dists = cdist(isomap_coords, isomap_coords)
    orig_dists = cdist(X_scaled, X_scaled)

    pca_corr = stats.spearmanr(orig_dists.flatten(), pca_dists.flatten())[0]
    isomap_corr = stats.spearmanr(orig_dists.flatten(), isomap_dists.flatten())[0]
    print(f"  Distance preservation (Spearman):")
    print(f"    PCA: {pca_corr:.3f}")
    print(f"    Isomap: {isomap_corr:.3f}")

g1_results = {
    "variance_explained": [float(v) for v in explained_var[:10]],
    "n_components_80": int(n_components_80),
    "n_components_90": int(n_components_90),
    "n_components_95": int(n_components_95),
    "bootstrap_mean_dim": float(np.mean(bootstrap_dims)),
    "bootstrap_std_dim": float(dim_stability),
    "isomap_success": bool(isomap_success),
    "effective_dimensionality": int(n_components_90)
}

print(f"\nG-1 RESULT: Effective dimensionality = {n_components_90}")

# =============================================================================
# TEST G-2: MONOTONICITY VS MANIFOLD
# =============================================================================
print("\n" + "=" * 70)
print("TEST G-2: MONOTONICITY VS MANIFOLD")
print("=" * 70)

# Folio index (order in manuscript)
folio_indices = np.arange(len(valid_folios))

# Correlate each PC with folio order
print("\nPC correlations with manuscript order:")
pc_correlations = []
for i in range(min(5, pca_coords.shape[1])):
    rho, p = stats.spearmanr(folio_indices, pca_coords[:, i])
    pc_correlations.append({'pc': i+1, 'rho': rho, 'p': p})
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  PC{i+1}: rho={rho:.3f}, p={p:.4f} {sig}")

# Check for reversals (non-monotonic structure)
pc1 = pca_coords[:, 0]
# Detect direction changes
direction = np.sign(np.diff(pc1))
reversals = np.sum(np.diff(direction) != 0)
reversal_rate = reversals / (len(pc1) - 2)

print(f"\nMonotonicity analysis (PC1):")
print(f"  Direction reversals: {reversals}")
print(f"  Reversal rate: {reversal_rate:.3f}")
print(f"  Interpretation: {'MONOTONIC' if reversal_rate < 0.3 else 'NON-MONOTONIC'}")

# Check for loops (does trajectory return near start?)
start_region = pca_coords[:10, :3].mean(axis=0)
end_region = pca_coords[-10:, :3].mean(axis=0)
loop_distance = euclidean(start_region, end_region)
max_distance = np.max(cdist(pca_coords[:, :3], pca_coords[:, :3]))
loop_ratio = loop_distance / max_distance

print(f"\nLoop detection:")
print(f"  Start-end distance: {loop_distance:.3f}")
print(f"  Max pairwise distance: {max_distance:.3f}")
print(f"  Loop ratio: {loop_ratio:.3f}")
print(f"  Interpretation: {'LOOP_PRESENT' if loop_ratio < 0.3 else 'NO_LOOP'}")

# Null comparison (shuffled order)
null_correlations = []
for _ in range(1000):
    shuffled = np.random.permutation(folio_indices)
    rho, _ = stats.spearmanr(shuffled, pca_coords[:, 0])
    null_correlations.append(abs(rho))

observed_corr = abs(pc_correlations[0]['rho'])
percentile = (np.sum(null_correlations >= observed_corr) / 1000) * 100
print(f"\nNull comparison (PC1 vs order):")
print(f"  Observed |rho|: {observed_corr:.3f}")
print(f"  Null mean |rho|: {np.mean(null_correlations):.3f}")
print(f"  Percentile: {100 - percentile:.1f}%")

g2_results = {
    "pc_correlations": pc_correlations,
    "reversal_count": int(reversals),
    "reversal_rate": float(reversal_rate),
    "is_monotonic": bool(reversal_rate < 0.3),
    "loop_ratio": float(loop_ratio),
    "has_loop": bool(loop_ratio < 0.3),
    "null_percentile": float(100 - percentile)
}

structure_type = "LINEAR" if reversal_rate < 0.3 and loop_ratio > 0.5 else "CURVED" if loop_ratio < 0.3 else "MIXED"
print(f"\nG-2 RESULT: {structure_type}")

# =============================================================================
# TEST G-3: RADIAL VS AXIAL STRUCTURE
# =============================================================================
print("\n" + "=" * 70)
print("TEST G-3: RADIAL VS AXIAL STRUCTURE")
print("=" * 70)

# Compute centroid
centroid = pca_coords[:, :3].mean(axis=0)
print(f"\nCentroid (PC1-3): [{centroid[0]:.2f}, {centroid[1]:.2f}, {centroid[2]:.2f}]")

# Distance from centroid for each folio
distances = np.array([euclidean(pca_coords[i, :3], centroid) for i in range(len(valid_folios))])

print(f"\nDistance from centroid:")
print(f"  Mean: {distances.mean():.3f}")
print(f"  Std: {distances.std():.3f}")
print(f"  Min: {distances.min():.3f}")
print(f"  Max: {distances.max():.3f}")

# Correlate distance with control variables
hazard_densities = np.array([folio_control[f]['hazard_density'] for f in valid_folios])
kernel_ratios = np.array([folio_control[f]['kernel_contact_ratio'] for f in valid_folios])
link_densities = np.array([folio_control[f]['link_density'] for f in valid_folios])

print("\nDistance-control correlations:")
corr_hazard, p_hazard = stats.spearmanr(distances, hazard_densities)
corr_kernel, p_kernel = stats.spearmanr(distances, kernel_ratios)
corr_link, p_link = stats.spearmanr(distances, link_densities)

print(f"  Distance vs hazard_density: rho={corr_hazard:.3f}, p={p_hazard:.4f}")
print(f"  Distance vs kernel_contact: rho={corr_kernel:.3f}, p={p_kernel:.4f}")
print(f"  Distance vs link_density: rho={corr_link:.3f}, p={p_link:.4f}")

# Null comparison
null_corrs_hazard = []
for _ in range(1000):
    shuffled = np.random.permutation(hazard_densities)
    rho, _ = stats.spearmanr(distances, shuffled)
    null_corrs_hazard.append(abs(rho))

percentile_hazard = (np.sum(null_corrs_hazard >= abs(corr_hazard)) / 1000) * 100

g3_results = {
    "centroid": [float(c) for c in centroid],
    "mean_distance": float(distances.mean()),
    "std_distance": float(distances.std()),
    "corr_distance_hazard": float(corr_hazard),
    "p_hazard": float(p_hazard),
    "corr_distance_kernel": float(corr_kernel),
    "p_kernel": float(p_kernel),
    "corr_distance_link": float(corr_link),
    "p_link": float(p_link),
    "null_percentile_hazard": float(100 - percentile_hazard)
}

is_radial = abs(corr_hazard) > 0.2 or abs(corr_kernel) > 0.2
print(f"\nG-3 RESULT: {'RADIAL' if is_radial else 'NON-RADIAL'} structure")

# =============================================================================
# TEST G-4: BOUNDARY DETECTION
# =============================================================================
print("\n" + "=" * 70)
print("TEST G-4: BOUNDARY DETECTION")
print("=" * 70)

# Identify boundary folios (extreme PC1 or PC2 values)
pc1_vals = pca_coords[:, 0]
pc2_vals = pca_coords[:, 1]

threshold_low = np.percentile(pc1_vals, 10)
threshold_high = np.percentile(pc1_vals, 90)

boundary_mask = (pc1_vals <= threshold_low) | (pc1_vals >= threshold_high)
interior_mask = ~boundary_mask

boundary_folios = [valid_folios[i] for i in np.where(boundary_mask)[0]]
interior_folios = [valid_folios[i] for i in np.where(interior_mask)[0]]

print(f"\nBoundary folios (PC1 extremes): {len(boundary_folios)}")
print(f"Interior folios: {len(interior_folios)}")

# Compare properties
boundary_hazard = np.array([folio_control[f]['hazard_density'] for f in boundary_folios])
interior_hazard = np.array([folio_control[f]['hazard_density'] for f in interior_folios])

boundary_kernel = np.array([folio_control[f]['kernel_contact_ratio'] for f in boundary_folios])
interior_kernel = np.array([folio_control[f]['kernel_contact_ratio'] for f in interior_folios])

boundary_link = np.array([folio_control[f]['link_density'] for f in boundary_folios])
interior_link = np.array([folio_control[f]['link_density'] for f in interior_folios])

print("\nBoundary vs Interior comparison:")

# Mann-Whitney U tests
u_hazard, p_hazard_bnd = stats.mannwhitneyu(boundary_hazard, interior_hazard, alternative='two-sided')
u_kernel, p_kernel_bnd = stats.mannwhitneyu(boundary_kernel, interior_kernel, alternative='two-sided')
u_link, p_link_bnd = stats.mannwhitneyu(boundary_link, interior_link, alternative='two-sided')

effect_hazard = (boundary_hazard.mean() - interior_hazard.mean()) / interior_hazard.std()
effect_kernel = (boundary_kernel.mean() - interior_kernel.mean()) / interior_kernel.std()
effect_link = (boundary_link.mean() - interior_link.mean()) / interior_link.std()

print(f"  Hazard density: boundary={boundary_hazard.mean():.3f}, interior={interior_hazard.mean():.3f}, p={p_hazard_bnd:.4f}, d={effect_hazard:.2f}")
print(f"  Kernel contact: boundary={boundary_kernel.mean():.3f}, interior={interior_kernel.mean():.3f}, p={p_kernel_bnd:.4f}, d={effect_kernel:.2f}")
print(f"  Link density: boundary={boundary_link.mean():.3f}, interior={interior_link.mean():.3f}, p={p_link_bnd:.4f}, d={effect_link:.2f}")

g4_results = {
    "n_boundary": len(boundary_folios),
    "n_interior": len(interior_folios),
    "boundary_hazard_mean": float(boundary_hazard.mean()),
    "interior_hazard_mean": float(interior_hazard.mean()),
    "p_hazard": float(p_hazard_bnd),
    "effect_hazard": float(effect_hazard),
    "boundary_kernel_mean": float(boundary_kernel.mean()),
    "interior_kernel_mean": float(interior_kernel.mean()),
    "p_kernel": float(p_kernel_bnd),
    "effect_kernel": float(effect_kernel),
    "boundary_link_mean": float(boundary_link.mean()),
    "interior_link_mean": float(interior_link.mean()),
    "p_link": float(p_link_bnd),
    "effect_link": float(effect_link),
    "boundary_folios": boundary_folios[:10]
}

boundary_distinct = bool(any([p_hazard_bnd < 0.05, p_kernel_bnd < 0.05, p_link_bnd < 0.05]))
print(f"\nG-4 RESULT: Boundaries {'DISTINCT' if boundary_distinct else 'NOT_DISTINCT'}")

# =============================================================================
# TEST G-5: LOCAL CONTINUITY GEOMETRY
# =============================================================================
print("\n" + "=" * 70)
print("TEST G-5: LOCAL CONTINUITY GEOMETRY")
print("=" * 70)

# Compute distance between adjacent folios
adjacent_distances = []
for i in range(len(valid_folios) - 1):
    d = euclidean(pca_coords[i, :3], pca_coords[i+1, :3])
    adjacent_distances.append(d)

adjacent_distances = np.array(adjacent_distances)

print(f"\nAdjacent folio distances:")
print(f"  Mean: {adjacent_distances.mean():.3f}")
print(f"  Std: {adjacent_distances.std():.3f}")
print(f"  Min: {adjacent_distances.min():.3f}")
print(f"  Max: {adjacent_distances.max():.3f}")

# Detect spikes (large jumps)
spike_threshold = adjacent_distances.mean() + 2 * adjacent_distances.std()
spikes = np.where(adjacent_distances > spike_threshold)[0]
print(f"\nSpikes detected (d > {spike_threshold:.3f}): {len(spikes)}")
if len(spikes) > 0:
    print(f"  Spike locations: {spikes[:10].tolist()}")
    spike_folios = [f"{valid_folios[i]}->{valid_folios[i+1]}" for i in spikes[:5]]
    print(f"  Spike transitions: {spike_folios}")

# Detect plateaus (low variability regions)
window_size = 10
rolling_std = []
for i in range(len(adjacent_distances) - window_size + 1):
    rolling_std.append(np.std(adjacent_distances[i:i+window_size]))
rolling_std = np.array(rolling_std)

plateau_threshold = np.percentile(rolling_std, 25)
plateaus = np.where(rolling_std < plateau_threshold)[0]
print(f"\nPlateau regions (low local variability): {len(plateaus)}")

# Compare to null (shuffled folio order)
null_mean_dists = []
for _ in range(1000):
    shuffled_idx = np.random.permutation(len(pca_coords))
    shuffled_coords = pca_coords[shuffled_idx]
    dists = [euclidean(shuffled_coords[i, :3], shuffled_coords[i+1, :3])
             for i in range(len(shuffled_coords) - 1)]
    null_mean_dists.append(np.mean(dists))

null_mean_dists = np.array(null_mean_dists)
observed_mean = adjacent_distances.mean()
percentile_dist = (np.sum(null_mean_dists <= observed_mean) / 1000) * 100

print(f"\nNull comparison:")
print(f"  Observed mean distance: {observed_mean:.3f}")
print(f"  Null mean distance: {null_mean_dists.mean():.3f}")
print(f"  Percentile: {percentile_dist:.1f}%")
print(f"  Effect size: {(null_mean_dists.mean() - observed_mean) / null_mean_dists.std():.2f}")

g5_results = {
    "mean_adjacent_distance": float(adjacent_distances.mean()),
    "std_adjacent_distance": float(adjacent_distances.std()),
    "n_spikes": int(len(spikes)),
    "spike_locations": spikes[:10].tolist() if len(spikes) > 0 else [],
    "n_plateaus": int(len(plateaus)),
    "null_mean_distance": float(null_mean_dists.mean()),
    "percentile": float(percentile_dist),
    "continuity_type": "GRADUAL" if len(spikes) < 5 else "PUNCTUATED"
}

print(f"\nG-5 RESULT: {g5_results['continuity_type']} transitions")

# =============================================================================
# FINAL GEOMETRY CLASSIFICATION
# =============================================================================
print("\n" + "=" * 70)
print("FINAL GEOMETRY CLASSIFICATION")
print("=" * 70)

# Decision logic
is_linear = g2_results['is_monotonic'] and not g2_results['has_loop']
is_radial = is_radial
is_low_dim = g1_results['effective_dimensionality'] <= 5  # More permissive threshold
has_boundaries = boundary_distinct
is_gradual = g5_results['continuity_type'] == "GRADUAL"
has_order_correlation = abs(g2_results['pc_correlations'][0]['rho']) > 0.4
has_strong_continuity = g5_results['percentile'] < 5  # Much smoother than random

print("\nStructural signatures:")
print(f"  Linear (monotonic, no loop): {is_linear}")
print(f"  Radial (distance-intensity correlated): {is_radial}")
print(f"  Low-dimensional (<=5 components): {is_low_dim}")
print(f"  Distinct boundaries: {has_boundaries}")
print(f"  Gradual transitions: {is_gradual}")
print(f"  Order-correlated (PC1): {has_order_correlation}")
print(f"  Strong local continuity: {has_strong_continuity}")

# Classification - revised logic
if is_linear and is_low_dim and is_gradual:
    geometry_class = "LINEAR_1D_LADDER"
    description = "1D monotonic progression through coordinate space"
elif is_radial and is_low_dim:
    geometry_class = "RADIAL_ENVELOPE"
    description = "Distance-from-center structure with intensity correlation"
elif has_order_correlation and has_strong_continuity and not is_gradual:
    geometry_class = "PIECEWISE_SEQUENTIAL"
    description = "Sequential progression with punctuated transitions at section boundaries"
elif is_low_dim and not is_linear and is_gradual:
    geometry_class = "LOW_DIM_MANIFOLD"
    description = "Curved path or band in low-dimensional space"
elif has_order_correlation and has_strong_continuity:
    geometry_class = "SEQUENTIAL_BAND"
    description = "Strong sequential structure with local smoothness"
elif has_boundaries and is_gradual:
    geometry_class = "MIXED_PIECEWISE"
    description = "Piecewise smooth geometry with distinct boundary regions"
else:
    geometry_class = "NO_RECOVERABLE_GEOMETRY"
    description = "No clear geometric structure detected"

print(f"\n*** FINAL VERDICT: {geometry_class} ***")
print(f"    {description}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

# Embeddings
embeddings = {
    "metadata": {
        "n_folios": len(valid_folios),
        "n_features": X.shape[1],
        "prefix_features": top_prefixes,
        "suffix_features": top_suffixes
    },
    "pca": {
        "variance_explained": [float(v) for v in explained_var[:5]],
        "coordinates": {f: [float(c) for c in pca_coords[i, :5]]
                       for i, f in enumerate(valid_folios)}
    }
}

if isomap_success:
    embeddings["isomap"] = {
        "coordinates": {f: [float(c) for c in isomap_coords[i]]
                       for i, f in enumerate(valid_folios)}
    }

with open('coordinate_geometry_embeddings.json', 'w') as f:
    json.dump(embeddings, f, indent=2)
print("  Saved: coordinate_geometry_embeddings.json")

# Summary
summary = {
    "metadata": {
        "test": "COORDINATE_GEOMETRY_RECONSTRUCTION",
        "n_folios": len(valid_folios),
        "n_features": X.shape[1]
    },
    "g1_dimensionality": g1_results,
    "g2_monotonicity": g2_results,
    "g3_radial": g3_results,
    "g4_boundary": g4_results,
    "g5_continuity": g5_results,
    "final_verdict": geometry_class,
    "description": description,
    "structural_signatures": {
        "is_linear": bool(is_linear),
        "is_radial": bool(is_radial),
        "is_low_dimensional": bool(is_low_dim),
        "has_boundaries": bool(has_boundaries),
        "is_gradual": bool(is_gradual)
    }
}

with open('coordinate_geometry_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("  Saved: coordinate_geometry_summary.json")

# Report
report = f"""# Coordinate Geometry Reconstruction

*Generated: 2026-01-01*
*Status: {geometry_class}*

---

## Purpose

Reconstruct the shape and dimensionality of the coordinate system encoded by
prefix/suffix usage across folios. Purely structural analysis - no semantics.

---

## Summary

| Test | Finding | Result |
|------|---------|--------|
| G-1 Dimensionality | {g1_results['effective_dimensionality']} components (90% var) | LOW_DIM |
| G-2 Monotonicity | reversal rate={g2_results['reversal_rate']:.2f}, loop={g2_results['has_loop']} | {structure_type} |
| G-3 Radial | dist-hazard rho={g3_results['corr_distance_hazard']:.3f} | {'RADIAL' if is_radial else 'NON-RADIAL'} |
| G-4 Boundary | {g4_results['n_boundary']} boundary folios | {'DISTINCT' if boundary_distinct else 'NOT_DISTINCT'} |
| G-5 Continuity | {g5_results['n_spikes']} spikes | {g5_results['continuity_type']} |

---

## G-1: Dimensionality Estimation

| Metric | Value |
|--------|-------|
| Components for 80% variance | {g1_results['n_components_80']} |
| Components for 90% variance | {g1_results['n_components_90']} |
| Components for 95% variance | {g1_results['n_components_95']} |
| Bootstrap stability | {g1_results['bootstrap_mean_dim']:.1f} +/- {g1_results['bootstrap_std_dim']:.2f} |

**Variance explained (first 5 PCs):** {', '.join([f'{v:.3f}' for v in g1_results['variance_explained'][:5]])}

---

## G-2: Monotonicity vs Manifold

| Metric | Value |
|--------|-------|
| PC1-order correlation | rho={g2_results['pc_correlations'][0]['rho']:.3f}, p={g2_results['pc_correlations'][0]['p']:.4f} |
| Reversal count | {g2_results['reversal_count']} |
| Reversal rate | {g2_results['reversal_rate']:.3f} |
| Is monotonic | {g2_results['is_monotonic']} |
| Loop ratio | {g2_results['loop_ratio']:.3f} |
| Has loop | {g2_results['has_loop']} |
| Null percentile | {g2_results['null_percentile']:.1f}% |

**Structure type:** {structure_type}

---

## G-3: Radial vs Axial Structure

| Metric | Value |
|--------|-------|
| Mean distance from centroid | {g3_results['mean_distance']:.3f} |
| Distance-hazard correlation | rho={g3_results['corr_distance_hazard']:.3f}, p={g3_results['p_hazard']:.4f} |
| Distance-kernel correlation | rho={g3_results['corr_distance_kernel']:.3f}, p={g3_results['p_kernel']:.4f} |
| Distance-link correlation | rho={g3_results['corr_distance_link']:.3f}, p={g3_results['p_link']:.4f} |

**Radial structure:** {'YES' if is_radial else 'NO'}

---

## G-4: Boundary Detection

| Metric | Boundary | Interior | p-value | Effect |
|--------|----------|----------|---------|--------|
| Hazard density | {g4_results['boundary_hazard_mean']:.3f} | {g4_results['interior_hazard_mean']:.3f} | {g4_results['p_hazard']:.4f} | {g4_results['effect_hazard']:.2f} |
| Kernel contact | {g4_results['boundary_kernel_mean']:.3f} | {g4_results['interior_kernel_mean']:.3f} | {g4_results['p_kernel']:.4f} | {g4_results['effect_kernel']:.2f} |
| Link density | {g4_results['boundary_link_mean']:.3f} | {g4_results['interior_link_mean']:.3f} | {g4_results['p_link']:.4f} | {g4_results['effect_link']:.2f} |

**Boundaries distinct:** {'YES' if boundary_distinct else 'NO'}

---

## G-5: Local Continuity Geometry

| Metric | Value |
|--------|-------|
| Mean adjacent distance | {g5_results['mean_adjacent_distance']:.3f} |
| Std adjacent distance | {g5_results['std_adjacent_distance']:.3f} |
| Spikes detected | {g5_results['n_spikes']} |
| Plateau regions | {g5_results['n_plateaus']} |
| Null mean distance | {g5_results['null_mean_distance']:.3f} |
| Percentile (vs null) | {g5_results['percentile']:.1f}% |

**Continuity type:** {g5_results['continuity_type']}

---

## Final Verdict

**{geometry_class}**

{description}

### Structural Signatures

- Linear (monotonic, no loop): {is_linear}
- Radial (distance-intensity correlated): {is_radial}
- Low-dimensional (<=3 components): {is_low_dim}
- Distinct boundaries: {has_boundaries}
- Gradual transitions: {is_gradual}

---

*Structural analysis only. No semantic interpretations.*
"""

with open('coordinate_geometry_report.md', 'w') as f:
    f.write(report)
print("  Saved: coordinate_geometry_report.md")

print("\nDone.")
