"""
Phase 4: Equivalence Class Collapse Test
Tier 4 SPECULATIVE

Expert hypothesis: REGIME_2/3 folios are "reusable operational templates"
that cut across many materials. Collapsing them by structural similarity
should reveal the true mastery horizon count.

Test: If REGIME_2 collapses to ~3 classes and REGIME_3 to ~7 classes,
this matches Puff's sparse middle distribution.
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics
import math

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

def load_regime_folios():
    """Load B folios grouped by regime."""
    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        data = json.load(f)

    by_regime = defaultdict(list)

    for folio_name, folio_data in data.get('profiles', {}).items():
        if isinstance(folio_data, dict) and folio_data.get('system') == 'B':
            b_metrics = folio_data.get('b_metrics', {})
            if b_metrics and b_metrics.get('regime'):
                folio_entry = {
                    'folio': folio_name,
                    'regime': b_metrics['regime'],
                    'cei': b_metrics.get('cei_total', 0),
                    'hazard': b_metrics.get('hazard_density', 0),
                    'escape': b_metrics.get('escape_density', 0),
                    'link': b_metrics.get('link_density', 0),
                    'near_miss': b_metrics.get('near_miss_count', 0),
                    'recovery': b_metrics.get('recovery_ops_count', 0),
                    'intervention': b_metrics.get('intervention_frequency', 0),
                }
                by_regime[b_metrics['regime']].append(folio_entry)

    return by_regime


def euclidean_distance(f1, f2, features):
    """Compute Euclidean distance between two folios on given features."""
    total = 0
    for feat in features:
        diff = f1.get(feat, 0) - f2.get(feat, 0)
        total += diff * diff
    return math.sqrt(total)


def normalize_features(folios, features):
    """Z-score normalize features for fair distance computation."""
    # Compute means and stds
    stats = {}
    for feat in features:
        values = [f[feat] for f in folios]
        mean = statistics.mean(values) if values else 0
        std = statistics.stdev(values) if len(values) > 1 else 1
        stats[feat] = {'mean': mean, 'std': std if std > 0 else 1}

    # Normalize
    normalized = []
    for f in folios:
        norm_f = {'folio': f['folio'], 'regime': f['regime']}
        for feat in features:
            norm_f[feat] = (f[feat] - stats[feat]['mean']) / stats[feat]['std']
        normalized.append(norm_f)

    return normalized, stats


def hierarchical_clustering(folios, features, linkage='average'):
    """
    Simple hierarchical clustering without scipy.
    Returns dendrogram as list of merge steps.
    """
    n = len(folios)
    if n == 0:
        return [], []

    # Initialize: each folio is its own cluster
    clusters = [[i] for i in range(n)]
    cluster_ids = list(range(n))
    active = set(range(n))

    # Distance matrix
    dist = {}
    for i in range(n):
        for j in range(i + 1, n):
            d = euclidean_distance(folios[i], folios[j], features)
            dist[(i, j)] = d
            dist[(j, i)] = d

    merges = []  # (distance, cluster1_id, cluster2_id, new_cluster_members)
    next_cluster_id = n

    while len(active) > 1:
        # Find closest pair of active clusters
        min_dist = float('inf')
        merge_pair = None

        active_list = sorted(active)
        for i, c1 in enumerate(active_list):
            for c2 in active_list[i + 1:]:
                # Average linkage: mean distance between all pairs
                members1 = clusters[c1]
                members2 = clusters[c2]
                total_dist = 0
                count = 0
                for m1 in members1:
                    for m2 in members2:
                        key = (min(m1, m2), max(m1, m2))
                        total_dist += dist.get(key, 0)
                        count += 1
                avg_dist = total_dist / count if count > 0 else 0

                if avg_dist < min_dist:
                    min_dist = avg_dist
                    merge_pair = (c1, c2)

        if merge_pair is None:
            break

        c1, c2 = merge_pair

        # Merge clusters
        new_members = clusters[c1] + clusters[c2]
        clusters.append(new_members)
        cluster_ids.append(next_cluster_id)

        merges.append({
            'distance': min_dist,
            'merged': (c1, c2),
            'new_cluster': next_cluster_id,
            'members': [folios[m]['folio'] for m in new_members],
            'size': len(new_members)
        })

        active.remove(c1)
        active.remove(c2)
        active.add(len(clusters) - 1)
        next_cluster_id += 1

    return merges, clusters


def find_natural_clusters(merges, target_count=None):
    """
    Find natural cluster count by looking for large distance gaps.
    If target_count specified, cut at that level.
    """
    if not merges:
        return []

    # Get distances at each merge step
    distances = [m['distance'] for m in merges]

    # Find gaps
    gaps = []
    for i in range(1, len(distances)):
        gap = distances[i] - distances[i - 1]
        gaps.append({
            'after_merge': i,
            'n_clusters': len(distances) - i + 1,
            'gap': gap,
            'distance': distances[i]
        })

    # Sort by gap size to find natural cuts
    gaps.sort(key=lambda x: -x['gap'])

    return gaps


def cut_dendrogram(folios, merges, n_clusters):
    """Cut dendrogram to get exactly n_clusters."""
    n = len(folios)
    if n_clusters >= n:
        return [[f['folio']] for f in folios]

    # Start with each folio as its own cluster
    assignments = {f['folio']: i for i, f in enumerate(folios)}

    # Apply merges until we have n_clusters
    n_current = n
    for merge in merges:
        if n_current <= n_clusters:
            break

        # Get folios in merged clusters
        members = merge['members']

        # Assign all to new cluster id
        new_id = min(assignments[m] for m in members)
        for m in members:
            assignments[m] = new_id

        n_current = len(set(assignments.values()))

    # Group by cluster
    clusters = defaultdict(list)
    for folio, cluster_id in assignments.items():
        clusters[cluster_id].append(folio)

    return list(clusters.values())


def analyze_regime(regime_name, folios, puff_target):
    """Analyze one regime's clustering structure."""
    print(f"\n{'='*60}")
    print(f"{regime_name}: {len(folios)} folios (Puff target: {puff_target})")
    print("=" * 60)

    if len(folios) < 2:
        print("Too few folios for clustering")
        return None

    # Features for clustering
    features = ['cei', 'hazard', 'escape', 'link', 'intervention']

    # Normalize
    norm_folios, stats = normalize_features(folios, features)

    print("\n--- Feature Statistics ---")
    for feat in features:
        values = [f[feat] for f in folios]
        print(f"  {feat}: mean={statistics.mean(values):.3f}, "
              f"std={statistics.stdev(values) if len(values) > 1 else 0:.3f}")

    # Cluster
    print("\n--- Hierarchical Clustering ---")
    merges, clusters = hierarchical_clustering(norm_folios, features)

    if not merges:
        print("No merges possible")
        return None

    # Find natural cuts
    gaps = find_natural_clusters(merges)

    print("\n--- Top Natural Cuts (by gap size) ---")
    for g in gaps[:5]:
        print(f"  {g['n_clusters']} clusters: gap={g['gap']:.3f}, "
              f"at distance={g['distance']:.3f}")

    # Check if target is a natural cut
    target_gaps = [g for g in gaps if g['n_clusters'] == puff_target]
    if target_gaps:
        print(f"\n*** Puff target ({puff_target}) IS a natural cut! ***")
        print(f"    Gap rank: {gaps.index(target_gaps[0]) + 1} of {len(gaps)}")
    else:
        print(f"\n--- Puff target ({puff_target}) not in top natural cuts ---")

    # Cut at target
    print(f"\n--- Cutting to {puff_target} Clusters ---")
    cluster_members = cut_dendrogram(folios, merges, puff_target)

    result_clusters = []
    for i, members in enumerate(cluster_members):
        member_data = [f for f in folios if f['folio'] in members]
        if member_data:
            avg_cei = statistics.mean([m['cei'] for m in member_data])
            avg_escape = statistics.mean([m['escape'] for m in member_data])
            print(f"  Cluster {i + 1} ({len(members)} folios): "
                  f"CEI={avg_cei:.3f}, escape={avg_escape:.3f}")
            print(f"    Members: {', '.join(sorted(members))}")

            result_clusters.append({
                'cluster_id': i + 1,
                'size': len(members),
                'members': sorted(members),
                'avg_cei': avg_cei,
                'avg_escape': avg_escape,
            })

    return {
        'regime': regime_name,
        'n_folios': len(folios),
        'puff_target': puff_target,
        'n_clusters_at_target': len(cluster_members),
        'target_is_natural': bool(target_gaps),
        'target_gap_rank': gaps.index(target_gaps[0]) + 1 if target_gaps else None,
        'top_natural_cuts': [g['n_clusters'] for g in gaps[:3]],
        'clusters': result_clusters,
        'merge_distances': [m['distance'] for m in merges],
    }


def main():
    print("=" * 60)
    print("PHASE 4: EQUIVALENCE CLASS COLLAPSE TEST")
    print("Testing expert hypothesis: REGIME_2/3 are reusable templates")
    print("=" * 60)

    # Load data
    by_regime = load_regime_folios()

    print("\n--- Regime Distribution ---")
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        print(f"  {regime}: {len(by_regime[regime])} folios")

    # Puff targets (from corrected mapping)
    puff_targets = {
        'REGIME_1': 38,  # Can't really collapse - flowers are distinct
        'REGIME_2': 3,   # Expert predicts 11 -> ~3
        'REGIME_3': 7,   # Expert predicts 16 -> ~7
        'REGIME_4': 37,  # Precision herbs - distinct
    }

    results = {}

    # Focus on REGIME_2 and REGIME_3 (the mismatched ones)
    for regime in ['REGIME_2', 'REGIME_3']:
        result = analyze_regime(
            regime,
            by_regime[regime],
            puff_targets[regime]
        )
        if result:
            results[regime] = result

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: EQUIVALENCE CLASS COLLAPSE")
    print("=" * 60)

    print("\n--- Distribution Comparison ---")
    print(f"{'Regime':<12} {'Puff':<8} {'Voynich':<8} {'Collapsed':<10} {'Match?':<8}")
    print("-" * 50)

    all_match = True
    for regime in ['REGIME_2', 'REGIME_3']:
        puff = puff_targets[regime]
        voynich = len(by_regime[regime])
        collapsed = results[regime]['n_clusters_at_target'] if regime in results else voynich
        is_natural = results[regime]['target_is_natural'] if regime in results else False
        match_status = "YES" if is_natural else "FORCED"
        if not is_natural:
            all_match = False
        print(f"{regime:<12} {puff:<8} {voynich:<8} {collapsed:<10} {match_status:<8}")

    # Overall assessment
    print("\n--- Expert Hypothesis Assessment ---")

    r2_natural = results.get('REGIME_2', {}).get('target_is_natural', False)
    r3_natural = results.get('REGIME_3', {}).get('target_is_natural', False)

    if r2_natural and r3_natural:
        print("STRONG SUPPORT: Both targets are natural cuts")
        verdict = "PASS"
    elif r2_natural or r3_natural:
        print("PARTIAL SUPPORT: One target is natural cut")
        verdict = "PARTIAL"
    else:
        print("WEAK SUPPORT: Neither target is natural cut")
        # Check if targets are close to natural cuts
        r2_tops = results.get('REGIME_2', {}).get('top_natural_cuts', [])
        r3_tops = results.get('REGIME_3', {}).get('top_natural_cuts', [])

        r2_close = puff_targets['REGIME_2'] in r2_tops or \
                   any(abs(t - puff_targets['REGIME_2']) <= 1 for t in r2_tops)
        r3_close = puff_targets['REGIME_3'] in r3_tops or \
                   any(abs(t - puff_targets['REGIME_3']) <= 1 for t in r3_tops)

        if r2_close and r3_close:
            print("But targets are NEAR natural cuts - moderate support")
            verdict = "PARTIAL"
        else:
            verdict = "FAIL"

    print(f"\nVERDICT: {verdict}")

    # What the natural structure suggests
    print("\n--- What Natural Clustering Reveals ---")
    for regime in ['REGIME_2', 'REGIME_3']:
        if regime in results:
            tops = results[regime]['top_natural_cuts']
            print(f"  {regime} naturally clusters to: {tops}")

    # Save results
    output = {
        "tier": 4,
        "status": "HYPOTHETICAL",
        "test": "EQUIVALENCE_CLASS_COLLAPSE",
        "date": "2026-01-14",
        "hypothesis": "REGIME_2/3 folios are reusable operational templates",
        "expert_prediction": "Collapsing should yield Puff's sparse middle counts",
        "puff_targets": puff_targets,
        "voynich_raw": {r: len(by_regime[r]) for r in by_regime},
        "results": results,
        "verdict": verdict,
    }

    with open(RESULTS_DIR / "regime_equivalence_classes.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/regime_equivalence_classes.json")


if __name__ == "__main__":
    main()
