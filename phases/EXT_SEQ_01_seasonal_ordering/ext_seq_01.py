"""
EXT-SEQ-01: Illustration Seasonal Ordering Analysis (Plant Classes Only)

Tests whether plant illustration ordering exhibits non-random seasonal sequence
at the broad plant-class level.

TIER 3 ONLY - External alignment, no interpretation.
"""

import random
import numpy as np
from scipy import stats as scipy_stats
from collections import Counter

# PIAA Plant Class Assignments (from plant_class_assignments.md)
# Format: folio -> (primary_class, secondary_class, key_features)
PIAA_DATA = {
    'f2r':  ('ALH', 'MH', 'palmate divided leaves, prominent root, flowering head'),
    'f3v':  ('AF', 'MH', 'lobed leaves, large dark blue spherical flower'),
    'f5r':  ('AF', 'AQ', 'large rounded/heart-shaped leaves, bulbous base'),
    'f5v':  ('AF', 'ALH', 'bushy with ivy-like leaves, small red/pink flowers'),
    'f9r':  ('ALH', None, 'feathery divided leaves, central spike, red root'),
    'f9v':  ('AF', None, 'palmate leaves with striking blue/violet flowers'),
    'f11r': ('AS', 'ALH', 'shrubby with dense small leaves, multiple stems'),
    'f11v': ('AS', 'RT', 'tree-like form, dense oval leaves'),
    'f17r': ('AF', 'MH', 'large oval leaves, tall blue/purple flower spike'),
    'f18r': ('MH', 'FP', 'fern-like/palm fronds, blue flower'),
    'f19r': ('ALH', None, 'very fine feathery leaves'),
    'f21r': ('AF', 'MH', 'rounded basal leaves, tall flowering spike'),
    'f22r': ('AF', 'ALH', 'divided leaves, small blue flowers, spreading habit'),
    'f22v': ('AF', 'MH', 'bushy with scalloped leaves, prominent blue flower'),
    'f24v': ('ALH', 'MH', 'deeply palmate/divided leaves'),
    'f25r': ('ALH', 'MH', 'rounded ivy-like leaves, branching stem'),
    'f29v': ('AF', 'MH', 'serrated leaves, curling flower spikes'),
    'f30v': ('RT', 'ALH', 'conifer/juniper type + broad-leaved herb'),
    'f32v': ('ALH', 'MH', 'stellate/radial leaf arrangement, seed pods'),
    'f35v': ('ALH', None, 'stellate/palmate leaves on stem'),
    'f36r': ('AF', 'MH', 'oval leaves, clustered flower heads'),
    'f37v': ('AS', 'RT', 'tree-like with diamond-shaped leaves'),
    'f38r': ('AF', None, 'iris-type with connected rhizomes, blue flower'),
    'f38v': ('ALH', None, 'oval leaves along central stem'),
    'f42r': ('AF', 'MH', 'multiple connected plants with flower heads, extensive roots'),
    'f45v': ('MH', 'AF', 'deeply serrated/spiny leaves, round flower heads'),
    'f47v': ('ALH', None, 'scattered leaf study page, ivy-like leaves'),
    'f49v': ('AF', None, 'large basal leaves, dramatic blue feathery flower'),
    'f51v': ('MH', None, 'spiny/serrated leaves on stem'),
    'f56r': ('AF', 'ALH', 'bushy palmate leaves, small blue flowers'),
}

# Folio order (as bound in manuscript)
FOLIO_ORDER = [
    'f2r', 'f3v', 'f5r', 'f5v', 'f9r', 'f9v', 'f11r', 'f11v',
    'f17r', 'f18r', 'f19r', 'f21r', 'f22r', 'f22v', 'f24v', 'f25r',
    'f29v', 'f30v', 'f32v', 'f35v', 'f36r', 'f37v', 'f38r', 'f38v',
    'f42r', 'f45v', 'f47v', 'f49v', 'f51v', 'f56r'
]

# Seasonal bin assignments at CLASS level (coarse, heuristic)
# Based on typical harvest/availability patterns in medieval Europe
CLASS_SEASONAL_BINS = {
    'AF':  'SUMMER',     # Aromatic Flowers - peak flowering summer
    'ALH': 'SUMMER',     # Aromatic Leaf Herbs - leafy growth spring-summer
    'AS':  'AUTUMN',     # Aromatic Shrubs - woody, harvest after growth
    'RT':  'AUTUMN',     # Resinous - sap/resin collection late season
    'MH':  'AMBIGUOUS',  # Medicinal Herbs - varies widely
    'FP':  'AMBIGUOUS',  # Food Plants - varies
    'AQ':  'SUMMER',     # Aquatic - growing season
    'DP':  'AUTUMN',     # Dye Plants - typically harvest late
    'TP':  'AMBIGUOUS',  # Toxic/Industrial - varies
}

# Ordinal seasonal scores for drift analysis
SEASON_ORDINAL = {
    'SPRING': 1,
    'SUMMER': 2,
    'AUTUMN': 3,
    'WINTER': 4,
    'AMBIGUOUS': 2.5  # Middle value
}

# Seasonal adjacency (neighbors)
SEASON_NEIGHBORS = {
    'SPRING': {'SPRING', 'SUMMER', 'AMBIGUOUS'},
    'SUMMER': {'SPRING', 'SUMMER', 'AUTUMN', 'AMBIGUOUS'},
    'AUTUMN': {'SUMMER', 'AUTUMN', 'WINTER', 'AMBIGUOUS'},
    'WINTER': {'AUTUMN', 'WINTER', 'SPRING', 'AMBIGUOUS'},
    'AMBIGUOUS': {'SPRING', 'SUMMER', 'AUTUMN', 'WINTER', 'AMBIGUOUS'}
}


def get_seasonal_bin(folio):
    """Get seasonal bin for a folio based on primary class."""
    if folio not in PIAA_DATA:
        return 'AMBIGUOUS'
    primary_class = PIAA_DATA[folio][0]
    return CLASS_SEASONAL_BINS.get(primary_class, 'AMBIGUOUS')


def get_seasonal_score(folio):
    """Get ordinal seasonal score for drift analysis."""
    season = get_seasonal_bin(folio)
    return SEASON_ORDINAL.get(season, 2.5)


def adjacency_same_or_neighbor(seq):
    """Count adjacent pairs in same or neighboring seasonal bin."""
    count = 0
    for i in range(len(seq) - 1):
        s1 = get_seasonal_bin(seq[i])
        s2 = get_seasonal_bin(seq[i+1])
        if s2 in SEASON_NEIGHBORS.get(s1, set()):
            count += 1
    return count / (len(seq) - 1) if len(seq) > 1 else 0


def monotonic_drift(seq):
    """Compute Spearman correlation between position and seasonal score."""
    positions = list(range(len(seq)))
    scores = [get_seasonal_score(f) for f in seq]
    if len(set(scores)) < 2:
        return 0, 1.0  # No variation
    rho, p = scipy_stats.spearmanr(positions, scores)
    return rho, p


def find_clusters(seq):
    """Find contiguous clusters of same seasonal bin."""
    if not seq:
        return []
    clusters = []
    current_bin = get_seasonal_bin(seq[0])
    current_size = 1
    for i in range(1, len(seq)):
        bin_i = get_seasonal_bin(seq[i])
        if bin_i == current_bin:
            current_size += 1
        else:
            clusters.append((current_bin, current_size))
            current_bin = bin_i
            current_size = 1
    clusters.append((current_bin, current_size))
    return clusters


def cluster_stats(seq):
    """Compute cluster statistics."""
    clusters = find_clusters(seq)
    sizes = [c[1] for c in clusters]
    if not sizes:
        return 0, 0, 0
    return len(clusters), np.mean(sizes), max(sizes)


def run_permutation_test(observed_stat, stat_func, seq, n_perms=10000):
    """Run permutation test comparing observed to shuffled."""
    null_stats = []
    for _ in range(n_perms):
        shuffled = seq.copy()
        random.shuffle(shuffled)
        null_stats.append(stat_func(shuffled))

    null_stats = np.array(null_stats)
    # Two-tailed p-value
    if observed_stat >= np.mean(null_stats):
        p = np.mean(null_stats >= observed_stat)
    else:
        p = np.mean(null_stats <= observed_stat)
    p = min(p * 2, 1.0)  # Two-tailed

    effect_size = (observed_stat - np.mean(null_stats)) / np.std(null_stats) if np.std(null_stats) > 0 else 0

    return p, np.mean(null_stats), np.std(null_stats), effect_size


def main():
    print("="*60)
    print("EXT-SEQ-01: Illustration Seasonal Ordering Analysis")
    print("="*60)
    print("\nTier 3 - External Alignment Only")
    print("No species identification, no meaning assignment\n")

    random.seed(42)
    np.random.seed(42)

    # Section 1: Method Summary
    print("="*60)
    print("SECTION 1: METHOD SUMMARY")
    print("="*60)

    print("\nData Used:")
    print(f"  - {len(FOLIO_ORDER)} botanical folios in manuscript order")
    print("  - PIAA plant-class annotations (primary class)")

    print("\nSeasonal Bin Definitions (Coarse, Heuristic):")
    for cls, season in sorted(CLASS_SEASONAL_BINS.items()):
        print(f"  {cls}: {season}")

    print("\nNull Models:")
    print("  1. Fully random order (10,000 permutations)")
    print("  2. Class-frequency preserving shuffle")

    # Class distribution
    print("\nObserved Class Distribution:")
    classes = [PIAA_DATA[f][0] for f in FOLIO_ORDER]
    class_counts = Counter(classes)
    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        season = CLASS_SEASONAL_BINS.get(cls, 'AMBIGUOUS')
        print(f"  {cls}: {count} ({season})")

    # Seasonal distribution
    print("\nSeasonal Bin Distribution:")
    seasons = [get_seasonal_bin(f) for f in FOLIO_ORDER]
    season_counts = Counter(seasons)
    for season, count in sorted(season_counts.items(), key=lambda x: -x[1]):
        print(f"  {season}: {count} ({count/len(FOLIO_ORDER)*100:.1f}%)")

    # Section 2: Results
    print("\n" + "="*60)
    print("SECTION 2: RESULTS")
    print("="*60)

    # A. Adjacency Bias Test
    print("\n--- A. ADJACENCY BIAS TEST ---")
    print("Measures probability adjacent folios are in same/neighboring seasonal bin\n")

    obs_adjacency = adjacency_same_or_neighbor(FOLIO_ORDER)
    p_adj, null_mean_adj, null_std_adj, d_adj = run_permutation_test(
        obs_adjacency, adjacency_same_or_neighbor, FOLIO_ORDER, 10000
    )

    print(f"  Observed adjacency rate: {obs_adjacency:.3f}")
    print(f"  Null mean (shuffled):    {null_mean_adj:.3f}")
    print(f"  Null std:                {null_std_adj:.3f}")
    print(f"  Effect size (Cohen's d): {d_adj:.3f}")
    print(f"  p-value (two-tailed):    {p_adj:.4f}")

    if p_adj < 0.05:
        adj_verdict = "SIGNIFICANT" if abs(d_adj) > 0.5 else "WEAK SIGNAL"
    else:
        adj_verdict = "NOT SIGNIFICANT"
    print(f"  Verdict: {adj_verdict}")

    # B. Monotonic Drift Test
    print("\n--- B. MONOTONIC DRIFT TEST ---")
    print("Tests for increasing/decreasing seasonal trend through manuscript\n")

    obs_rho, obs_p_rho = monotonic_drift(FOLIO_ORDER)

    # Permutation test for rho
    def drift_stat(seq):
        r, _ = monotonic_drift(seq)
        return r

    p_drift, null_mean_rho, null_std_rho, d_rho = run_permutation_test(
        obs_rho, drift_stat, FOLIO_ORDER, 10000
    )

    print(f"  Observed Spearman rho:   {obs_rho:.3f}")
    print(f"  Parametric p-value:      {obs_p_rho:.4f}")
    print(f"  Null mean (shuffled):    {null_mean_rho:.3f}")
    print(f"  Effect size (Cohen's d): {d_rho:.3f}")
    print(f"  Permutation p-value:     {p_drift:.4f}")

    if p_drift < 0.05 and abs(obs_rho) > 0.2:
        drift_verdict = "WEAK DRIFT DETECTED" if abs(obs_rho) < 0.4 else "MODERATE DRIFT"
    else:
        drift_verdict = "NO DRIFT DETECTED"
    print(f"  Verdict: {drift_verdict}")

    # C. Clustering Strength
    print("\n--- C. CLUSTERING STRENGTH ---")
    print("Measures contiguous same-season cluster sizes\n")

    obs_n_clusters, obs_mean_size, obs_max_size = cluster_stats(FOLIO_ORDER)

    def max_cluster_stat(seq):
        _, _, mx = cluster_stats(seq)
        return mx

    p_cluster, null_mean_max, null_std_max, d_cluster = run_permutation_test(
        obs_max_size, max_cluster_stat, FOLIO_ORDER, 10000
    )

    print(f"  Number of clusters:      {obs_n_clusters}")
    print(f"  Mean cluster size:       {obs_mean_size:.2f}")
    print(f"  Max cluster size:        {obs_max_size}")
    print(f"  Null mean max size:      {null_mean_max:.2f}")
    print(f"  Effect size (Cohen's d): {d_cluster:.3f}")
    print(f"  p-value (max cluster):   {p_cluster:.4f}")

    if p_cluster < 0.05 and d_cluster > 0.5:
        cluster_verdict = "SIGNIFICANT CLUSTERING"
    elif p_cluster < 0.1:
        cluster_verdict = "WEAK CLUSTERING"
    else:
        cluster_verdict = "NO CLUSTERING"
    print(f"  Verdict: {cluster_verdict}")

    # Show actual clusters
    print("\n  Observed clusters:")
    clusters = find_clusters(FOLIO_ORDER)
    for i, (season, size) in enumerate(clusters):
        print(f"    Cluster {i+1}: {season} (size={size})")

    # D. Summary Statistics Table
    print("\n--- D. SUMMARY STATISTICS ---")
    print(f"\n{'Test':<25} {'Observed':>10} {'Null Mean':>10} {'p-value':>10} {'Effect d':>10}")
    print("-" * 67)
    print(f"{'Adjacency Rate':<25} {obs_adjacency:>10.3f} {null_mean_adj:>10.3f} {p_adj:>10.4f} {d_adj:>10.3f}")
    print(f"{'Monotonic Drift (rho)':<25} {obs_rho:>10.3f} {null_mean_rho:>10.3f} {p_drift:>10.4f} {d_rho:>10.3f}")
    print(f"{'Max Cluster Size':<25} {obs_max_size:>10.1f} {null_mean_max:>10.2f} {p_cluster:>10.4f} {d_cluster:>10.3f}")

    # Section 3: Outcome Classification
    print("\n" + "="*60)
    print("SECTION 3: OUTCOME CLASSIFICATION")
    print("="*60)

    # Count significant results
    sig_count = sum([
        p_adj < 0.05,
        p_drift < 0.05,
        p_cluster < 0.05
    ])

    strong_effects = sum([
        abs(d_adj) > 0.8,
        abs(d_rho) > 0.8,
        abs(d_cluster) > 0.8
    ])

    print(f"\n  Tests with p < 0.05: {sig_count}/3")
    print(f"  Tests with |d| > 0.8: {strong_effects}/3")

    if sig_count == 0:
        outcome = "NO_ORDERING_SIGNAL"
        outcome_text = "Plant illustration ordering does not differ from random"
    elif sig_count >= 2 or strong_effects >= 1:
        if any([abs(d_adj) > 1.5, abs(d_rho) > 0.5, obs_max_size > 8]):
            outcome = "ANOMALOUS_STRONG_ORDERING"
            outcome_text = "Unexpectedly strong ordering - requires review"
        else:
            outcome = "MODERATE_CLUSTERING"
            outcome_text = "Moderate non-random clustering consistent with weak organization"
    else:
        outcome = "WEAK_SEASONAL_DRIFT"
        outcome_text = "Weak signal consistent with seasonal or organizational drift"

    print(f"\n  OUTCOME: {outcome}")
    print(f"  {outcome_text}")

    # Section 4: Interpretation Boundary
    print("\n" + "="*60)
    print("SECTION 4: INTERPRETATION BOUNDARY")
    print("="*60)
    print("""
This analysis tests only whether plant illustration ordering differs
from random with respect to coarse seasonal plausibility.

It does NOT imply:
- instruction
- meaning
- ingredient lists
- correspondence with executable text
- harvest guides or recipes

Any detected pattern may reflect:
- scribal/organizational convenience
- material availability during production
- copying order from an exemplar
- coincidence within statistical bounds

TIER ASSIGNMENT: Tier 3 (External Alignment Only)
""")

    print("="*60)
    print("EXT-SEQ-01 COMPLETE")
    print("="*60)

    return outcome


if __name__ == "__main__":
    main()
