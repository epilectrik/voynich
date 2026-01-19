#!/usr/bin/env python3
"""
SCB-02: MIDDLE ZONE CLUSTERING

SECONDARY TEST for SEMANTIC_CEILING_BREACH phase.

Question: Do MIDDLE zone clusters correlate with modality domains?

This tests whether vocabulary-level patterns (MIDDLE zone affinity clusters)
correspond to semantic domains (modality classes). This respects C384
because we operate at vocabulary level, not entry level.

Pre-registered threshold: Cluster-modality correlation >0.3
"""

import json
from pathlib import Path
import numpy as np
from collections import Counter, defaultdict
from scipy import stats

def load_data():
    """Load MIDDLE clustering and modality data."""
    with open('results/middle_zone_survival.json', 'r', encoding='utf-8') as f:
        mzs_data = json.load(f)

    with open('results/brunschwig_reverse_activation.json', 'r', encoding='utf-8') as f:
        ra_data = json.load(f)

    with open('results/enhanced_sensory_extraction.json', 'r', encoding='utf-8') as f:
        enh_data = json.load(f)

    return mzs_data, ra_data, enh_data

def cosine_similarity(v1, v2):
    """Compute cosine similarity between two vectors."""
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return np.dot(v1, v2) / (norm1 * norm2)

def main():
    print("=" * 70)
    print("SCB-02: MIDDLE ZONE CLUSTERING")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    mzs_data, ra_data, enh_data = load_data()

    # Extract cluster info
    clusters = mzs_data['clustering']['clusters']
    print(f"Found {len(clusters)} MIDDLE zone clusters")
    print()

    # Display cluster profiles
    print("=" * 70)
    print("MIDDLE ZONE CLUSTER PROFILES")
    print("=" * 70)
    print()

    cluster_profiles = {}
    cluster_middles = {}

    for cluster_id, cluster_info in clusters.items():
        profile = cluster_info['mean_profile']
        cluster_profiles[cluster_id] = [profile['C'], profile['P'], profile['R'], profile['S']]
        cluster_middles[cluster_id] = cluster_info.get('example_middles', [])

        dom_zone = cluster_info['dominant_zone']
        n = cluster_info['size']

        print(f"Cluster {cluster_id} ({dom_zone}-dominant, n={n}):")
        print(f"  Profile: C={profile['C']:.3f}, P={profile['P']:.3f}, R={profile['R']:.3f}, S={profile['S']:.3f}")
        print(f"  Example MIDDLEs: {cluster_middles[cluster_id][:5]}")
        print()

    # Build recipe -> modality mapping
    enh_recipes = {r['recipe_id']: r for r in enh_data['recipe_level']['recipes']}
    ra_recipes = {r['recipe_id']: r for r in ra_data['recipes']}

    recipes_with_modality = []
    for recipe_id, enh in enh_recipes.items():
        modality = enh.get('dominant_modality')
        if modality is None:
            continue
        if recipe_id not in ra_recipes:
            continue

        ra = ra_recipes[recipe_id]
        zone_affinity = ra.get('zone_affinity', {})
        profile = [
            zone_affinity.get('C', 0),
            zone_affinity.get('P', 0),
            zone_affinity.get('R', 0),
            zone_affinity.get('S', 0)
        ]

        recipes_with_modality.append({
            'recipe_id': recipe_id,
            'modality': modality,
            'zone_profile': profile
        })

    print(f"Recipes with modality labels: {len(recipes_with_modality)}")
    print()

    # Assign each recipe to closest cluster
    print("=" * 70)
    print("RECIPE -> CLUSTER ASSIGNMENT")
    print("=" * 70)
    print()

    recipe_cluster_assignment = {}
    for recipe in recipes_with_modality:
        best_cluster = None
        best_sim = -1

        for cluster_id, cluster_profile in cluster_profiles.items():
            sim = cosine_similarity(recipe['zone_profile'], cluster_profile)
            if sim > best_sim:
                best_sim = sim
                best_cluster = cluster_id

        recipe_cluster_assignment[recipe['recipe_id']] = {
            'cluster': best_cluster,
            'similarity': best_sim,
            'modality': recipe['modality']
        }

    # Build cluster -> modality distribution
    cluster_modality_dist = defaultdict(lambda: defaultdict(int))
    for recipe_id, assignment in recipe_cluster_assignment.items():
        cluster_modality_dist[assignment['cluster']][assignment['modality']] += 1

    print("Cluster -> Modality distribution:")
    print()

    cluster_modality_matrix = {}
    for cluster_id in sorted(cluster_modality_dist.keys()):
        dist = dict(cluster_modality_dist[cluster_id])
        total = sum(dist.values())
        cluster_modality_matrix[cluster_id] = dist

        print(f"Cluster {cluster_id} (n={total}):")
        for mod in ['SOUND', 'TASTE', 'SIGHT', 'TOUCH']:
            count = dist.get(mod, 0)
            pct = count / total * 100 if total > 0 else 0
            bar = '#' * int(pct / 5)
            print(f"  {mod:<8}: {count:>3} ({pct:>5.1f}%) {bar}")
        print()

    # Statistical test: Chi-squared for cluster-modality independence
    print("=" * 70)
    print("STATISTICAL TESTS")
    print("=" * 70)
    print()

    # Build contingency table
    modalities = ['SOUND', 'TASTE', 'SIGHT', 'TOUCH']
    contingency = []
    for cluster_id in sorted(cluster_modality_matrix.keys()):
        row = [cluster_modality_matrix[cluster_id].get(mod, 0) for mod in modalities]
        contingency.append(row)

    contingency = np.array(contingency)
    print("Contingency table (Cluster x Modality):")
    print(f"{'':>12} | {'SOUND':>8} | {'TASTE':>8} | {'SIGHT':>8} | {'TOUCH':>8}")
    print("-" * 55)
    for i, cluster_id in enumerate(sorted(cluster_modality_matrix.keys())):
        row = contingency[i]
        print(f"{'Cluster ' + cluster_id:>12} | {row[0]:>8} | {row[1]:>8} | {row[2]:>8} | {row[3]:>8}")
    print()

    # Chi-squared test
    try:
        chi2, p_chi2, dof, expected = stats.chi2_contingency(contingency)
        print(f"Chi-squared test: chi2={chi2:.2f}, df={dof}, p={p_chi2:.4f}")

        if p_chi2 < 0.05:
            print("[SIGNIFICANT] Cluster and modality are NOT independent")
        else:
            print("[NOT SIGNIFICANT] Cannot reject independence")
    except Exception as e:
        print(f"Chi-squared test failed: {e}")
        chi2, p_chi2, dof = None, None, None
    print()

    # Cramer's V (effect size for chi-squared)
    if chi2 is not None:
        n_total = contingency.sum()
        min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
        cramers_v = np.sqrt(chi2 / (n_total * min_dim)) if min_dim > 0 and n_total > 0 else 0
        print(f"Cramer's V (effect size): {cramers_v:.3f}")

        if cramers_v > 0.3:
            print("[PASS] Effect size >0.3 (medium)")
        elif cramers_v > 0.1:
            print("[WEAK] Effect size 0.1-0.3 (small)")
        else:
            print("[FAIL] Effect size <0.1 (negligible)")
        print()
    else:
        cramers_v = None

    # Dominant modality per cluster
    print("=" * 70)
    print("CLUSTER CHARACTERIZATION")
    print("=" * 70)
    print()

    cluster_characterization = {}
    for cluster_id in sorted(cluster_modality_matrix.keys()):
        dist = cluster_modality_matrix[cluster_id]
        total = sum(dist.values())

        # Find dominant modality
        if total > 0:
            dom_mod = max(dist.keys(), key=lambda x: dist[x])
            dom_pct = dist[dom_mod] / total * 100
        else:
            dom_mod = 'NONE'
            dom_pct = 0

        # Get cluster's dominant zone
        dom_zone = clusters[cluster_id]['dominant_zone']

        cluster_characterization[cluster_id] = {
            'dominant_zone': dom_zone,
            'dominant_modality': dom_mod,
            'dominant_modality_pct': dom_pct,
            'n_recipes': total
        }

        print(f"Cluster {cluster_id}:")
        print(f"  Dominant zone: {dom_zone}")
        print(f"  Dominant modality: {dom_mod} ({dom_pct:.1f}%)")
        print(f"  Recipes assigned: {total}")
        print()

    # Check if zone-modality alignment matches expectations
    print("=" * 70)
    print("ZONE-MODALITY ALIGNMENT CHECK")
    print("=" * 70)
    print()

    # From ZONE_MODALITY_VALIDATION findings:
    # - SOUND associates with P-zone and R-zone
    # - SOUND avoids C-zone and S-zone

    expected_alignment = {
        'P': 'SOUND',  # P-zone -> SOUND expected
        'R': 'SOUND',  # R-zone -> SOUND expected
        'S': 'NOT_SOUND',  # S-zone -> not SOUND expected
        'C': 'NOT_SOUND'   # C-zone -> not SOUND expected
    }

    alignment_results = []
    for cluster_id, char in cluster_characterization.items():
        dom_zone = char['dominant_zone']
        dom_mod = char['dominant_modality']

        expected = expected_alignment.get(dom_zone, 'UNKNOWN')

        if expected == 'SOUND':
            aligned = dom_mod == 'SOUND'
        elif expected == 'NOT_SOUND':
            aligned = dom_mod != 'SOUND'
        else:
            aligned = None

        alignment_results.append({
            'cluster': cluster_id,
            'zone': dom_zone,
            'modality': dom_mod,
            'expected': expected,
            'aligned': aligned
        })

        status = "ALIGNED" if aligned else ("MISALIGNED" if aligned is False else "UNKNOWN")
        print(f"Cluster {cluster_id} ({dom_zone}-zone): {dom_mod} -> [{status}]")

    print()

    n_aligned = sum(1 for r in alignment_results if r['aligned'] is True)
    n_checked = sum(1 for r in alignment_results if r['aligned'] is not None)
    alignment_rate = n_aligned / n_checked if n_checked > 0 else 0

    print(f"Alignment rate: {n_aligned}/{n_checked} = {alignment_rate*100:.1f}%")
    print()

    # Final verdict
    print("=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print()

    if cramers_v is not None and cramers_v > 0.3 and p_chi2 is not None and p_chi2 < 0.05:
        verdict = "PASS"
        print(f"[{verdict}] MIDDLE zone clusters correlate with modality domains")
        print(f"  Cramer's V = {cramers_v:.3f} (>0.3)")
        print(f"  Chi-squared p = {p_chi2:.4f} (<0.05)")
    elif cramers_v is not None and cramers_v > 0.1:
        verdict = "WEAK"
        print(f"[{verdict}] Weak correlation detected")
    else:
        verdict = "FAIL"
        print(f"[{verdict}] No significant cluster-modality correlation")
    print()

    # Save results
    print("=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    print()

    results = {
        'phase': 'SEMANTIC_CEILING_BREACH',
        'test': 'scb_02_middle_zone_clustering',
        'question': 'Do MIDDLE zone clusters correlate with modality domains?',
        'cluster_profiles': {cid: list(profile) for cid, profile in cluster_profiles.items()},
        'cluster_modality_matrix': cluster_modality_matrix,
        'statistics': {
            'chi_squared': float(chi2) if chi2 is not None else None,
            'p_value': float(p_chi2) if p_chi2 is not None else None,
            'degrees_of_freedom': int(dof) if dof is not None else None,
            'cramers_v': float(cramers_v) if cramers_v is not None else None
        },
        'cluster_characterization': cluster_characterization,
        'alignment': {
            'results': alignment_results,
            'rate': alignment_rate
        },
        'verdict': verdict
    }

    output_path = Path('results/scb_middle_clusters.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Saved to {output_path}")
    print()

    return results

if __name__ == '__main__':
    main()
