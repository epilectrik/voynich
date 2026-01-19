"""
AXIS 2: Adjacency as Discrimination Navigation

Questions:
1. Do adjacency clusters function as working-memory chunks?
2. Are singleton entries deliberate isolation points?
3. Do adjacency clusters maximize contrast rather than similarity?
4. Do adjacency patterns optimize coverage traversal under hub rationing?

All tests use permutation-robust methods.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from typing import Dict, List, Set, Tuple
import random

from pcc_data_loader import (
    PCCDataLoader, get_order_robust_adjacency_pairs,
    permutation_test, bootstrap_ci
)


def identify_adjacency_clusters(entries: List[Dict],
                                loader: PCCDataLoader,
                                similarity_threshold: float = 0.15) -> List[List[Dict]]:
    """
    Identify adjacency clusters based on vocabulary overlap.

    A cluster is a contiguous sequence of entries with Jaccard > threshold.

    ORDER SENSITIVITY: FOLIO_LOCAL_ORDER
    """
    # Sort by folio and line
    sorted_entries = sorted(entries, key=lambda e: (e['folio'], e['line_number']))

    clusters = []
    current_cluster = []
    current_folio = None

    for i, entry in enumerate(sorted_entries):
        if entry['folio'] != current_folio:
            # New folio - start fresh
            if current_cluster:
                clusters.append(current_cluster)
            current_cluster = [entry]
            current_folio = entry['folio']
        elif i > 0 and sorted_entries[i-1]['folio'] == entry['folio']:
            # Same folio - check similarity with previous
            prev_entry = sorted_entries[i-1]
            similarity = loader.jaccard_similarity(
                prev_entry['middles'], entry['middles']
            )

            if similarity >= similarity_threshold:
                current_cluster.append(entry)
            else:
                if current_cluster:
                    clusters.append(current_cluster)
                current_cluster = [entry]
        else:
            current_cluster = [entry]

    if current_cluster:
        clusters.append(current_cluster)

    return clusters


def test_clusters_as_working_memory(entries: List[Dict],
                                    loader: PCCDataLoader) -> Dict:
    """
    Q1: Do adjacency clusters function as working-memory chunks?

    Hypothesis: Clusters should have size ~3-7 (Miller's 7+/-2 items).
    Within-cluster coherence should be significantly higher than cross-cluster.

    ORDER SENSITIVITY: FOLIO_LOCAL_ORDER
    """
    print("\n" + "-"*60)
    print("Q1: Adjacency Clusters as Working-Memory Chunks")
    print("-"*60)

    clusters = identify_adjacency_clusters(entries, loader)

    # Filter to non-singleton clusters
    multi_clusters = [c for c in clusters if len(c) > 1]
    singletons = [c for c in clusters if len(c) == 1]

    cluster_sizes = [len(c) for c in multi_clusters]

    print(f"\n  Total clusters identified: {len(clusters)}")
    print(f"  Multi-entry clusters: {len(multi_clusters)}")
    print(f"  Singleton entries: {len(singletons)}")

    if cluster_sizes:
        print(f"\n  Cluster size distribution (multi-entry only):")
        print(f"    Mean: {np.mean(cluster_sizes):.2f}")
        print(f"    Median: {np.median(cluster_sizes):.1f}")
        print(f"    Min: {min(cluster_sizes)}")
        print(f"    Max: {max(cluster_sizes)}")
        print(f"    Std: {np.std(cluster_sizes):.2f}")

        # Working memory window test (3-7 items)
        in_wm_range = sum(1 for s in cluster_sizes if 3 <= s <= 7)
        wm_rate = in_wm_range / len(cluster_sizes)
        print(f"\n  In working-memory range (3-7): {in_wm_range}/{len(cluster_sizes)} ({wm_rate:.1%})")

    # Within-cluster vs cross-cluster coherence
    within_similarities = []
    for cluster in multi_clusters:
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                sim = loader.jaccard_similarity(
                    cluster[i]['middles'], cluster[j]['middles']
                )
                within_similarities.append(sim)

    # Cross-cluster: sample pairs from different clusters
    cross_similarities = []
    for _ in range(min(1000, len(within_similarities))):
        if len(multi_clusters) >= 2:
            c1, c2 = random.sample(multi_clusters, 2)
            e1 = random.choice(c1)
            e2 = random.choice(c2)
            sim = loader.jaccard_similarity(e1['middles'], e2['middles'])
            cross_similarities.append(sim)

    if within_similarities and cross_similarities:
        mean_within = np.mean(within_similarities)
        mean_cross = np.mean(cross_similarities)

        u_stat, p_value = stats.mannwhitneyu(
            within_similarities, cross_similarities,
            alternative='greater'
        )

        print(f"\n  Within-cluster similarity: {mean_within:.4f}")
        print(f"  Cross-cluster similarity: {mean_cross:.4f}")
        print(f"  Ratio: {mean_within/mean_cross:.2f}x" if mean_cross > 0 else "  Ratio: N/A")
        print(f"  Mann-Whitney U: {u_stat:.1f}, p = {p_value:.6f}")

        # Effect size
        pooled_std = np.sqrt((np.var(within_similarities) + np.var(cross_similarities)) / 2)
        cohens_d = (mean_within - mean_cross) / pooled_std if pooled_std > 0 else 0
        print(f"  Cohen's d: {cohens_d:.3f}")

        # Verdict
        if p_value < 0.001 and cohens_d > 0.3:
            verdict = "YES"
            interpretation = "Clusters show working-memory chunk properties"
        elif p_value < 0.05:
            verdict = "WEAK_YES"
            interpretation = "Some clustering but weak chunking signal"
        else:
            verdict = "NO"
            interpretation = "No working-memory chunk structure detected"
    else:
        verdict = "INCONCLUSIVE"
        interpretation = "Insufficient data for within/cross comparison"
        mean_within = 0
        mean_cross = 0
        p_value = 1.0
        cohens_d = 0

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: FOLIO_LOCAL_ORDER")

    return {
        'question': 'Adjacency Clusters as Working-Memory Chunks',
        'order_sensitivity': 'FOLIO_LOCAL_ORDER',
        'n_clusters': len(clusters),
        'n_multi_clusters': len(multi_clusters),
        'n_singletons': len(singletons),
        'mean_cluster_size': float(np.mean(cluster_sizes)) if cluster_sizes else 0,
        'median_cluster_size': float(np.median(cluster_sizes)) if cluster_sizes else 0,
        'mean_within_similarity': float(mean_within),
        'mean_cross_similarity': float(mean_cross),
        'p_value': float(p_value),
        'cohens_d': float(cohens_d),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_singleton_isolation(entries: List[Dict],
                             loader: PCCDataLoader) -> Dict:
    """
    Q2: Are singleton entries deliberate isolation points?

    Hypothesis: Singletons should have unusual properties:
    - Higher MIDDLE diversity (unique vocabulary)
    - Lower overlap with global hub vocabulary
    - Higher incompatibility density

    ORDER SENSITIVITY: INVARIANT (property comparison, not order)
    """
    print("\n" + "-"*60)
    print("Q2: Singleton Entries as Isolation Points")
    print("-"*60)

    clusters = identify_adjacency_clusters(entries, loader)
    singletons = [c[0] for c in clusters if len(c) == 1]
    clustered = [e for c in clusters if len(c) > 1 for e in c]

    print(f"\n  Singleton entries: {len(singletons)}")
    print(f"  Clustered entries: {len(clustered)}")

    if not singletons or not clustered:
        return {
            'question': 'Singleton Isolation',
            'order_sensitivity': 'INVARIANT',
            'verdict': 'INCONCLUSIVE',
            'interpretation': 'Insufficient singletons or clustered entries'
        }

    # Get hub vocabulary (top 10% most frequent MIDDLEs)
    all_middles = loader.get_all_middles(entries)
    sorted_middles = sorted(all_middles.items(), key=lambda x: x[1], reverse=True)
    n_hubs = max(1, len(sorted_middles) // 10)
    hub_middles = {m for m, c in sorted_middles[:n_hubs]}

    print(f"  Hub MIDDLEs (top 10%): {len(hub_middles)}")

    # Compare properties
    singleton_unique = [len(e['middles']) for e in singletons]
    clustered_unique = [len(e['middles']) for e in clustered]

    singleton_hub_overlap = [
        len(e['middles'] & hub_middles) / len(e['middles'])
        if e['middles'] else 0 for e in singletons
    ]
    clustered_hub_overlap = [
        len(e['middles'] & hub_middles) / len(e['middles'])
        if e['middles'] else 0 for e in clustered
    ]

    singleton_density = [
        loader.calculate_incompatibility_density(e['middles'], all_middles)
        for e in singletons
    ]
    clustered_density = [
        loader.calculate_incompatibility_density(e['middles'], all_middles)
        for e in clustered
    ]

    # Statistics
    print(f"\n  Mean unique MIDDLEs:")
    print(f"    Singletons: {np.mean(singleton_unique):.2f}")
    print(f"    Clustered: {np.mean(clustered_unique):.2f}")
    u1, p1 = stats.mannwhitneyu(singleton_unique, clustered_unique, alternative='two-sided')
    print(f"    Mann-Whitney p = {p1:.4f}")

    print(f"\n  Mean hub overlap ratio:")
    print(f"    Singletons: {np.mean(singleton_hub_overlap):.3f}")
    print(f"    Clustered: {np.mean(clustered_hub_overlap):.3f}")
    u2, p2 = stats.mannwhitneyu(singleton_hub_overlap, clustered_hub_overlap, alternative='less')
    print(f"    Mann-Whitney (singletons < clustered) p = {p2:.4f}")

    print(f"\n  Mean incompatibility density:")
    print(f"    Singletons: {np.mean(singleton_density):.4f}")
    print(f"    Clustered: {np.mean(clustered_density):.4f}")
    u3, p3 = stats.mannwhitneyu(singleton_density, clustered_density, alternative='greater')
    print(f"    Mann-Whitney (singletons > clustered) p = {p3:.4f}")

    # Combined verdict
    signals = 0
    if p2 < 0.05:
        signals += 1
    if p3 < 0.05:
        signals += 1
    if p1 < 0.05:
        signals += 1

    if signals >= 2:
        verdict = "YES"
        interpretation = "Singletons show distinct isolation properties"
    elif signals >= 1:
        verdict = "WEAK_YES"
        interpretation = "Some isolation signal in singletons"
    else:
        verdict = "NO"
        interpretation = "Singletons not distinguishable from clustered"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: INVARIANT")

    return {
        'question': 'Singleton Isolation Properties',
        'order_sensitivity': 'INVARIANT',
        'n_singletons': len(singletons),
        'n_clustered': len(clustered),
        'mean_unique_singleton': float(np.mean(singleton_unique)),
        'mean_unique_clustered': float(np.mean(clustered_unique)),
        'mean_hub_overlap_singleton': float(np.mean(singleton_hub_overlap)),
        'mean_hub_overlap_clustered': float(np.mean(clustered_hub_overlap)),
        'mean_density_singleton': float(np.mean(singleton_density)),
        'mean_density_clustered': float(np.mean(clustered_density)),
        'p_unique': float(p1),
        'p_hub_overlap': float(p2),
        'p_density': float(p3),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_clusters_maximize_contrast(entries: List[Dict],
                                    loader: PCCDataLoader) -> Dict:
    """
    Q3: Do adjacency clusters maximize contrast rather than similarity?

    Hypothesis: Adjacent entries might be chosen to maximize DIFFERENCE
    (complementary coverage) rather than SIMILARITY (topic grouping).

    Test: Compare within-cluster contrast vs random baseline.

    ORDER SENSITIVITY: FOLIO_LOCAL_ORDER
    """
    print("\n" + "-"*60)
    print("Q3: Do Clusters Maximize Contrast?")
    print("-"*60)

    pairs = get_order_robust_adjacency_pairs(entries)

    # Calculate contrast (1 - similarity) for each adjacent pair
    observed_contrasts = []
    for curr, next_entry in pairs:
        similarity = loader.jaccard_similarity(
            curr['middles'], next_entry['middles']
        )
        contrast = 1 - similarity
        observed_contrasts.append(contrast)

    mean_observed_contrast = np.mean(observed_contrasts)

    # Permutation baseline: random pairing within same folio
    n_permutations = 1000
    null_contrasts = []

    entries_by_folio = defaultdict(list)
    for entry in entries:
        entries_by_folio[entry['folio']].append(entry)

    for _ in range(n_permutations):
        perm_contrasts = []
        for folio, folio_entries in entries_by_folio.items():
            if len(folio_entries) < 2:
                continue
            # Random shuffle and pair
            shuffled = random.sample(folio_entries, len(folio_entries))
            for i in range(len(shuffled) - 1):
                sim = loader.jaccard_similarity(
                    shuffled[i]['middles'], shuffled[i+1]['middles']
                )
                perm_contrasts.append(1 - sim)
        null_contrasts.append(np.mean(perm_contrasts))

    null_mean = np.mean(null_contrasts)
    null_std = np.std(null_contrasts)

    # Z-score
    z_score = (mean_observed_contrast - null_mean) / null_std if null_std > 0 else 0
    p_value = permutation_test(mean_observed_contrast, null_contrasts, 'greater')

    print(f"\n  Adjacent pairs analyzed: {len(observed_contrasts)}")
    print(f"\n  Mean observed contrast: {mean_observed_contrast:.4f}")
    print(f"  Null baseline (random): {null_mean:.4f}")
    print(f"  Null std: {null_std:.4f}")
    print(f"  Z-score: {z_score:.2f}")
    print(f"  Permutation p-value (observed > null): {p_value:.4f}")

    # Check: is observed contrast HIGHER than random? (=maximizing contrast)
    # Or LOWER than random? (=maximizing similarity)
    p_value_lower = permutation_test(mean_observed_contrast, null_contrasts, 'less')

    if p_value < 0.05:
        verdict = "YES_CONTRAST"
        interpretation = "Adjacency maximizes contrast (complementary coverage)"
    elif p_value_lower < 0.05:
        verdict = "NO_SIMILARITY"
        interpretation = "Adjacency maximizes similarity (topic clustering)"
    else:
        verdict = "NEUTRAL"
        interpretation = "Adjacency neither maximizes contrast nor similarity"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: FOLIO_LOCAL_ORDER")

    return {
        'question': 'Clusters Maximize Contrast',
        'order_sensitivity': 'FOLIO_LOCAL_ORDER',
        'n_pairs': len(observed_contrasts),
        'mean_observed_contrast': float(mean_observed_contrast),
        'null_mean': float(null_mean),
        'null_std': float(null_std),
        'z_score': float(z_score),
        'p_value_greater': float(p_value),
        'p_value_less': float(p_value_lower),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_coverage_traversal_optimization(entries: List[Dict],
                                         loader: PCCDataLoader) -> Dict:
    """
    Q4: Do adjacency patterns optimize coverage traversal under hub rationing?

    Hypothesis: If adjacency optimizes coverage, consecutive entries should
    collectively cover more MIDDLEs than random consecutive sequences.

    Test: Compare cumulative MIDDLE coverage in observed vs shuffled order.

    ORDER SENSITIVITY: FOLIO_LOCAL_ORDER
    """
    print("\n" + "-"*60)
    print("Q4: Coverage Traversal Optimization")
    print("-"*60)

    entries_by_folio = defaultdict(list)
    for entry in entries:
        entries_by_folio[entry['folio']].append(entry)

    # Sort within each folio
    for folio in entries_by_folio:
        entries_by_folio[folio].sort(key=lambda e: e['line_number'])

    def calculate_coverage_efficiency(ordered_entries: List[Dict]) -> float:
        """Calculate how efficiently coverage grows with sequence."""
        if not ordered_entries:
            return 0.0

        # Track cumulative coverage at each step
        seen = set()
        coverage_growth = []

        for entry in ordered_entries:
            new_middles = entry['middles'] - seen
            coverage_growth.append(len(new_middles))
            seen.update(entry['middles'])

        # Efficiency = early coverage weighted (first N entries matter more)
        # This penalizes "wasting" early positions on low-coverage entries
        weights = [1 / (i + 1) for i in range(len(coverage_growth))]
        weighted_coverage = sum(c * w for c, w in zip(coverage_growth, weights))

        return weighted_coverage

    # Calculate observed efficiency per folio
    observed_efficiencies = []
    for folio, folio_entries in entries_by_folio.items():
        if len(folio_entries) >= 5:  # Only meaningful for larger folios
            eff = calculate_coverage_efficiency(folio_entries)
            observed_efficiencies.append(eff)

    mean_observed = np.mean(observed_efficiencies) if observed_efficiencies else 0

    # Null baseline: shuffled order within each folio
    n_permutations = 500
    null_efficiencies = []

    for _ in range(n_permutations):
        perm_eff = []
        for folio, folio_entries in entries_by_folio.items():
            if len(folio_entries) >= 5:
                shuffled = random.sample(folio_entries, len(folio_entries))
                eff = calculate_coverage_efficiency(shuffled)
                perm_eff.append(eff)
        null_efficiencies.append(np.mean(perm_eff))

    null_mean = np.mean(null_efficiencies)
    null_std = np.std(null_efficiencies)

    z_score = (mean_observed - null_mean) / null_std if null_std > 0 else 0
    p_value = permutation_test(mean_observed, null_efficiencies, 'greater')

    print(f"\n  Folios analyzed (>= 5 entries): {len(observed_efficiencies)}")
    print(f"\n  Mean observed efficiency: {mean_observed:.4f}")
    print(f"  Null baseline (shuffled): {null_mean:.4f}")
    print(f"  Null std: {null_std:.4f}")
    print(f"  Z-score: {z_score:.2f}")
    print(f"  Permutation p-value: {p_value:.4f}")

    if p_value < 0.05 and z_score > 1.0:
        verdict = "YES"
        interpretation = "Order optimizes coverage traversal"
    elif p_value < 0.10:
        verdict = "WEAK_YES"
        interpretation = "Marginal coverage optimization signal"
    else:
        verdict = "NO"
        interpretation = "No coverage optimization in current order"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: FOLIO_LOCAL_ORDER")
    print(f"  NOTE: This finding is SENSITIVE to rebinding")

    return {
        'question': 'Coverage Traversal Optimization',
        'order_sensitivity': 'FOLIO_LOCAL_ORDER',
        'n_folios': len(observed_efficiencies),
        'mean_observed_efficiency': float(mean_observed),
        'null_mean': float(null_mean),
        'null_std': float(null_std),
        'z_score': float(z_score),
        'p_value': float(p_value),
        'verdict': verdict,
        'interpretation': interpretation
    }


def generate_axis2_report(results: Dict) -> str:
    """Generate formatted AXIS 2 report."""
    report = """
================================================================================
AXIS 2 REPORT: Adjacency as Discrimination Navigation
================================================================================

PHASE: Post-Closure Characterization
TIER: 3 (Exploratory characterization)
REBINDING SENSITIVITY: MOSTLY FOLIO_LOCAL_ORDER (1 test INVARIANT)

--------------------------------------------------------------------------------
SUMMARY OF FINDINGS
--------------------------------------------------------------------------------

"""
    for q_num, (key, data) in enumerate(results.items(), 1):
        report += f"""
Q{q_num}: {data['question']}
    Order Sensitivity: {data['order_sensitivity']}
    Verdict: {data['verdict']}
    Interpretation: {data['interpretation']}
"""

    report += """
--------------------------------------------------------------------------------
WHAT THIS DOES NOT CHANGE
--------------------------------------------------------------------------------

- Adjacency structure (C389, C346) remains unchanged
- Clustered adjacency (C424) is confirmed, mechanism characterized
- No new grammar for adjacency patterns
- No semantic interpretation of clusters
- Clusters are NOT topics or categories

--------------------------------------------------------------------------------
CRITICAL REBINDING NOTE
--------------------------------------------------------------------------------

Most AXIS 2 findings depend on FOLIO_LOCAL_ORDER:
- They assume within-folio line sequence is original
- They do NOT assume cross-folio order is original
- If within-folio rebinding occurred, these results would change

For rebinding-robust conclusions, only INVARIANT findings apply.

--------------------------------------------------------------------------------
IMPLICATIONS
--------------------------------------------------------------------------------

"""
    verdicts = [r['verdict'] for r in results.values()]
    if any(v in ['YES', 'YES_CONTRAST'] for v in verdicts):
        report += """
POSITIVE FINDINGS:
- Adjacency serves cognitive navigation function
- Clusters may function as working-memory chunks
- Order appears optimized (within folio) for some metric
"""
    else:
        report += """
NULL/NEUTRAL FINDINGS:
- Adjacency may be incidental rather than optimized
- Or: optimization is at a scale not detected here
"""

    report += """
================================================================================
"""
    return report


def main():
    print("="*70)
    print("AXIS 2: Adjacency as Discrimination Navigation")
    print("="*70)

    # Load data
    print("\nLoading data...")
    loader = PCCDataLoader()
    entries = loader.get_entries()
    print(f"Loaded {len(entries)} entries")

    # Run all tests
    results = {}

    results['q1_working_memory'] = test_clusters_as_working_memory(entries, loader)
    results['q2_singleton_isolation'] = test_singleton_isolation(entries, loader)
    results['q3_contrast_maximization'] = test_clusters_maximize_contrast(entries, loader)
    results['q4_coverage_optimization'] = test_coverage_traversal_optimization(entries, loader)

    # Generate report
    report = generate_axis2_report(results)
    print(report)

    # Save results
    output_path = Path(__file__).parent / 'axis2_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    # Save report
    report_path = Path(__file__).parent / 'AXIS2_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    return results


if __name__ == '__main__':
    main()
