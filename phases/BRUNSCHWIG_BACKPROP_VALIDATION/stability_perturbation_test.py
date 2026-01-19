#!/usr/bin/env python3
"""
STABILITY UNDER PERTURBATION TEST (Tier A-1)

Question: Do the observed sub-class clusters persist under controlled perturbations?

Method:
1. Randomly remove 5-10% of tail MIDDLEs
2. Randomly down-weight hubs
3. Recompute A-register clustering
4. Measure cluster survival rate and adjacency preservation

Why this matters:
- Confirms clusters are STRUCTURAL, not data artifacts
- Reinforces "regions in constraint space" framing
- Strengthens C481 (survivor-set uniqueness) defensively

Expected: High cluster survival (>80%) confirms structural basis.
"""

import csv
import json
import random
from collections import defaultdict, Counter
import math

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def load_data():
    """Load MIDDLE tokens per folio."""
    folio_middles = defaultdict(Counter)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only - CRITICAL for clean data
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio][middle] += 1

    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)

    return folio_middles, data['a_folio_classifications']

def compute_clusters(folio_middle_sets, folios, min_jaccard=0.10):
    """Compute clusters via greedy Jaccard matching."""
    # Pairwise Jaccard
    overlaps = []
    for i, f1 in enumerate(folios):
        for f2 in folios[i+1:]:
            s1 = folio_middle_sets.get(f1, set())
            s2 = folio_middle_sets.get(f2, set())
            if not s1 or not s2:
                continue
            intersection = len(s1 & s2)
            union = len(s1 | s2)
            jaccard = intersection / union if union > 0 else 0
            overlaps.append((f1, f2, jaccard))

    overlaps.sort(key=lambda x: -x[2])

    # Greedy clustering
    clusters = []
    remaining = set(folios)

    while remaining and overlaps:
        best = None
        for f1, f2, jacc in overlaps:
            if f1 in remaining and f2 in remaining and jacc >= min_jaccard:
                best = (f1, f2, jacc)
                break
        if best is None:
            break

        cluster = {best[0], best[1]}
        remaining.discard(best[0])
        remaining.discard(best[1])
        clusters.append(cluster)

    # Add singletons
    for f in remaining:
        clusters.append({f})

    return clusters, overlaps

def perturb_data(folio_middles, perturbation_type, strength=0.10):
    """Apply perturbation to MIDDLE data."""
    perturbed = {}

    # Get global MIDDLE frequencies
    global_counts = Counter()
    for fm in folio_middles.values():
        global_counts.update(fm)

    # Identify tails (bottom 30% by frequency) and hubs (top 10%)
    sorted_middles = sorted(global_counts.items(), key=lambda x: x[1])
    n = len(sorted_middles)

    tail_middles = set(m for m, c in sorted_middles[:int(n * 0.3)])
    hub_middles = set(m for m, c in sorted_middles[int(n * 0.9):])

    for folio, middle_counts in folio_middles.items():
        new_counts = Counter()

        for middle, count in middle_counts.items():
            if perturbation_type == 'tail_removal':
                # Remove tail MIDDLEs with probability = strength
                if middle in tail_middles and random.random() < strength:
                    continue  # Remove
                new_counts[middle] = count

            elif perturbation_type == 'hub_downweight':
                # Downweight hub MIDDLEs by reducing count
                if middle in hub_middles:
                    new_count = max(1, int(count * (1 - strength)))
                    new_counts[middle] = new_count
                else:
                    new_counts[middle] = count

            elif perturbation_type == 'random_removal':
                # Remove random MIDDLEs with probability = strength
                if random.random() < strength:
                    continue
                new_counts[middle] = count

        perturbed[folio] = new_counts

    return perturbed

def cluster_similarity(clusters1, clusters2):
    """Measure cluster survival and adjacency preservation."""
    # Extract pairs from each clustering
    def get_pairs(clusters):
        pairs = set()
        for cluster in clusters:
            for f1 in cluster:
                for f2 in cluster:
                    if f1 < f2:
                        pairs.add((f1, f2))
        return pairs

    pairs1 = get_pairs(clusters1)
    pairs2 = get_pairs(clusters2)

    if not pairs1 and not pairs2:
        return 1.0, 1.0  # Both empty

    # Jaccard of pairs
    intersection = len(pairs1 & pairs2)
    union = len(pairs1 | pairs2)
    pair_jaccard = intersection / union if union > 0 else 0

    # Count preserved multi-member clusters
    multi1 = [c for c in clusters1 if len(c) > 1]
    multi2 = [c for c in clusters2 if len(c) > 1]

    preserved = 0
    for c1 in multi1:
        for c2 in multi2:
            if c1 == c2:
                preserved += 1
                break

    survival_rate = preserved / len(multi1) if multi1 else 1.0

    return pair_jaccard, survival_rate

def main():
    print("=" * 70)
    print("STABILITY UNDER PERTURBATION TEST")
    print("=" * 70)
    print()
    print("Testing if sub-class clusters persist under controlled perturbations.")
    print("High survival confirms STRUCTURAL basis, not data artifacts.")
    print()

    # Set seed for reproducibility
    random.seed(42)

    # Load data
    folio_middles, classifications = load_data()

    # Get WATER_GENTLE folios (our test case with clear clusters)
    gentle_folios = sorted([f for f, t in classifications.items()
                            if t == 'WATER_GENTLE' and f in folio_middles])

    print(f"Testing on WATER_GENTLE: {gentle_folios}")
    print()

    # Baseline clustering
    baseline_sets = {f: set(folio_middles[f].keys()) for f in gentle_folios}
    baseline_clusters, baseline_overlaps = compute_clusters(baseline_sets, gentle_folios)

    print("BASELINE CLUSTERING:")
    for i, cluster in enumerate(baseline_clusters):
        if len(cluster) > 1:
            print(f"  Cluster {i+1}: {sorted(cluster)}")
    print()

    # Run perturbation experiments
    perturbation_tests = [
        ('tail_removal', 0.10, 'Remove 10% of tail MIDDLEs'),
        ('tail_removal', 0.20, 'Remove 20% of tail MIDDLEs'),
        ('hub_downweight', 0.30, 'Downweight hubs by 30%'),
        ('hub_downweight', 0.50, 'Downweight hubs by 50%'),
        ('random_removal', 0.10, 'Remove 10% random MIDDLEs'),
        ('random_removal', 0.20, 'Remove 20% random MIDDLEs'),
    ]

    n_trials = 10  # Multiple trials for random perturbations
    results = []

    print("=" * 70)
    print("PERTURBATION RESULTS")
    print("=" * 70)
    print()

    for ptype, strength, description in perturbation_tests:
        trial_pair_jaccards = []
        trial_survivals = []

        for trial in range(n_trials):
            # Perturb data
            perturbed = perturb_data(folio_middles, ptype, strength)

            # Compute perturbed clustering
            perturbed_sets = {f: set(perturbed.get(f, {}).keys()) for f in gentle_folios}
            perturbed_clusters, _ = compute_clusters(perturbed_sets, gentle_folios)

            # Measure similarity
            pair_jacc, survival = cluster_similarity(baseline_clusters, perturbed_clusters)
            trial_pair_jaccards.append(pair_jacc)
            trial_survivals.append(survival)

        avg_pair_jacc = sum(trial_pair_jaccards) / len(trial_pair_jaccards)
        avg_survival = sum(trial_survivals) / len(trial_survivals)

        print(f"{description}:")
        print(f"  Pair Jaccard: {avg_pair_jacc:.2f} (avg over {n_trials} trials)")
        print(f"  Cluster survival: {avg_survival:.0%}")

        status = "STABLE" if avg_survival >= 0.80 else "UNSTABLE"
        print(f"  Status: [{status}]")
        print()

        results.append({
            'perturbation': ptype,
            'strength': strength,
            'description': description,
            'avg_pair_jaccard': avg_pair_jacc,
            'avg_survival': avg_survival,
            'stable': avg_survival >= 0.80
        })

    # Now test on ALL product types
    print("=" * 70)
    print("FULL CORPUS TEST (all product types)")
    print("=" * 70)
    print()

    all_folios = sorted(folio_middles.keys())
    all_baseline_sets = {f: set(folio_middles[f].keys()) for f in all_folios}
    all_baseline_clusters, _ = compute_clusters(all_baseline_sets, all_folios)

    n_multi_baseline = len([c for c in all_baseline_clusters if len(c) > 1])
    print(f"Baseline: {n_multi_baseline} multi-member clusters across {len(all_folios)} folios")
    print()

    # Test most aggressive perturbation
    for ptype, strength, description in [('random_removal', 0.20, 'Remove 20% random MIDDLEs')]:
        trial_survivals = []

        for trial in range(n_trials):
            perturbed = perturb_data(folio_middles, ptype, strength)
            perturbed_sets = {f: set(perturbed.get(f, {}).keys()) for f in all_folios}
            perturbed_clusters, _ = compute_clusters(perturbed_sets, all_folios)

            _, survival = cluster_similarity(all_baseline_clusters, perturbed_clusters)
            trial_survivals.append(survival)

        avg_survival = sum(trial_survivals) / len(trial_survivals)
        print(f"{description}:")
        print(f"  Full corpus survival: {avg_survival:.0%}")
        status = "STABLE" if avg_survival >= 0.70 else "UNSTABLE"
        print(f"  Status: [{status}]")
    print()

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    stable_count = sum(1 for r in results if r['stable'])
    total = len(results)

    if stable_count == total:
        verdict = "STRONGLY STABLE"
        interpretation = "Clusters persist under all perturbation types. Structure is robust."
    elif stable_count >= total * 0.7:
        verdict = "MOSTLY STABLE"
        interpretation = "Clusters persist under most perturbations. Structure is defensible."
    elif stable_count >= total * 0.5:
        verdict = "PARTIALLY STABLE"
        interpretation = "Some fragility detected. Clusters may have data-dependent elements."
    else:
        verdict = "UNSTABLE"
        interpretation = "Clusters do not persist. May be data artifacts."

    print(f"Stable tests: {stable_count}/{total}")
    print(f"Verdict: {verdict}")
    print()
    print(f"Interpretation: {interpretation}")
    print()

    if verdict in ["STRONGLY STABLE", "MOSTLY STABLE"]:
        print("This confirms C481 (survivor-set uniqueness):")
        print("  Sub-class clusters represent STRUCTURAL regions in constraint space,")
        print("  not artifacts of specific vocabulary items.")

    # Save results
    output = {
        'test': 'STABILITY_PERTURBATION',
        'test_folios': gentle_folios,
        'n_trials': n_trials,
        'baseline_clusters': [sorted(c) for c in baseline_clusters if len(c) > 1],
        'perturbation_results': results,
        'stable_count': stable_count,
        'total_tests': total,
        'verdict': verdict,
        'interpretation': interpretation
    }

    with open('results/stability_perturbation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print(f"Results saved to results/stability_perturbation.json")

if __name__ == '__main__':
    main()
