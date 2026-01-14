#!/usr/bin/env python3
"""
Test 5A: Memory Decay Optimality

Pre-Registered Question:
"Is A-registry ordering optimal under realistic memory decay?"

EPISTEMIC SAFEGUARD:
This test remains Tier 3/4 exploratory. Results do NOT enable semantic decoding
or Tier 2 promotion without independent corroboration.
"""

import csv
import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "memory_optimality.json"

# Prefixes and suffixes for decomposition
PREFIXES = ['ch', 'sh', 'qo', 'ok', 'ot', 'ct', 'da', 'ol', 'ar', 'or', 'al', 'sa']
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]


def decompose_token(token):
    """Extract prefix, middle, suffix from token."""
    if not token or len(token) < 2:
        return None, None, None

    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    prefix = None
    rest = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    if not middle:
        middle = None

    return prefix, middle, suffix


def load_a_registry_order():
    """Load Currier A entries in manuscript order."""
    entries = []
    seen_folios = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            lang = row['language'].strip('"')
            if lang != 'A':
                continue

            folio = row['folio'].strip('"')
            token = row['word'].strip('"').lower()
            line = int(row.get('line', 0) or 0)
            position = int(row.get('word_in_line', 0) or 0)

            prefix, middle, suffix = decompose_token(token)
            if middle:
                entries.append({
                    'folio': folio,
                    'line': line,
                    'position': position,
                    'middle': middle,
                    'token': token
                })

            if folio not in seen_folios:
                seen_folios.append(folio)

    return entries, seen_folios


def simulate_memory_decay(entries, decay_rate=0.1, window_size=100):
    """
    Simulate memory decay for MIDDLE tokens.

    Memory model: Each MIDDLE has an activation level.
    - Seeing a MIDDLE resets activation to 1.0
    - Each subsequent token decays activation by decay_rate.
    - If activation falls below threshold before reuse, count as "forgotten".

    Returns total forgetting cost under given ordering.
    """
    activation = {}  # middle -> (last_seen_index, current_activation)
    forgetting_cost = 0
    recall_cost = 0

    for i, entry in enumerate(entries):
        middle = entry['middle']

        if middle in activation:
            last_idx, _ = activation[middle]
            gap = i - last_idx

            # Decay model: exponential decay
            decay = np.exp(-decay_rate * gap / window_size)

            if decay < 0.5:  # Threshold for "forgotten"
                forgetting_cost += 1
                recall_cost += (1 - decay)  # Higher cost for more decayed

        # Reset activation
        activation[middle] = (i, 1.0)

    return forgetting_cost, recall_cost


def compute_ordering_metrics(entries, middles_freq):
    """Compute memory metrics for a given ordering."""
    # Forgetting events
    forgetting_cost, recall_cost = simulate_memory_decay(entries)

    # Re-introduction distance (how far between first and second use)
    first_use = {}
    second_use = {}

    for i, entry in enumerate(entries):
        middle = entry['middle']
        if middle not in first_use:
            first_use[middle] = i
        elif middle not in second_use:
            second_use[middle] = i

    reintro_distances = []
    for middle in second_use:
        dist = second_use[middle] - first_use[middle]
        reintro_distances.append(dist)

    mean_reintro = np.mean(reintro_distances) if reintro_distances else 0

    # Clustering score (how clustered are uses of each MIDDLE)
    middle_positions = defaultdict(list)
    for i, entry in enumerate(entries):
        middle_positions[entry['middle']].append(i)

    clustering_scores = []
    for middle, positions in middle_positions.items():
        if len(positions) >= 2:
            gaps = np.diff(positions)
            # Lower variance = more clustered
            clustering_scores.append(np.std(gaps))

    mean_clustering = np.mean(clustering_scores) if clustering_scores else 0

    return {
        'forgetting_events': forgetting_cost,
        'recall_cost': float(recall_cost),
        'mean_reintro_distance': float(mean_reintro),
        'mean_clustering_variance': float(mean_clustering)
    }


def generate_alternative_orderings(entries, middles_freq, n_random=100):
    """Generate alternative orderings for comparison."""
    orderings = {}

    # Original manuscript order
    orderings['manuscript'] = entries.copy()

    # Frequency-sorted (most frequent first)
    freq_sorted = sorted(entries, key=lambda e: -middles_freq.get(e['middle'], 0))
    orderings['frequency_sorted'] = freq_sorted

    # Reverse frequency (rare first)
    rare_first = sorted(entries, key=lambda e: middles_freq.get(e['middle'], 0))
    orderings['rare_first'] = rare_first

    # Alphabetical by MIDDLE (arbitrary baseline)
    alpha_sorted = sorted(entries, key=lambda e: e['middle'])
    orderings['alphabetical'] = alpha_sorted

    # Clustered by MIDDLE (group all uses together)
    by_middle = defaultdict(list)
    for e in entries:
        by_middle[e['middle']].append(e)
    clustered = []
    for middle in sorted(by_middle.keys()):
        clustered.extend(by_middle[middle])
    orderings['fully_clustered'] = clustered

    # Random orderings
    random_metrics = []
    for i in range(n_random):
        np.random.seed(i)
        random_order = entries.copy()
        np.random.shuffle(random_order)
        metrics = compute_ordering_metrics(random_order, middles_freq)
        random_metrics.append(metrics)

    return orderings, random_metrics


def main():
    print("=" * 60)
    print("Test 5A: Memory Decay Optimality")
    print("Tier 3/4 Exploratory")
    print("=" * 60)
    print()

    # Load A registry in manuscript order
    print("Loading Currier A registry...")
    entries, folios = load_a_registry_order()
    print(f"  Total entries with MIDDLEs: {len(entries)}")
    print(f"  Unique folios: {len(folios)}")
    print()

    # Compute MIDDLE frequencies
    middles_freq = Counter(e['middle'] for e in entries)
    print(f"  Unique MIDDLEs: {len(middles_freq)}")
    print(f"  Most common: {middles_freq.most_common(5)}")
    print()

    # Generate alternative orderings
    print("Generating alternative orderings...")
    orderings, random_metrics = generate_alternative_orderings(entries, middles_freq)
    print(f"  Orderings: {list(orderings.keys())}")
    print(f"  Random samples: {len(random_metrics)}")
    print()

    # Compute metrics for each ordering
    print("Computing memory metrics...")
    print("-" * 60)

    results = {}
    for name, order in orderings.items():
        metrics = compute_ordering_metrics(order, middles_freq)
        results[name] = metrics
        print(f"  {name}:")
        print(f"    Forgetting events: {metrics['forgetting_events']}")
        print(f"    Recall cost: {metrics['recall_cost']:.2f}")
        print(f"    Mean reintro distance: {metrics['mean_reintro_distance']:.1f}")
        print(f"    Clustering variance: {metrics['mean_clustering_variance']:.1f}")
        print()

    # Random baseline statistics
    random_forgetting = [m['forgetting_events'] for m in random_metrics]
    random_recall = [m['recall_cost'] for m in random_metrics]

    print("Random baseline statistics:")
    print(f"  Forgetting: mean={np.mean(random_forgetting):.1f}, std={np.std(random_forgetting):.1f}")
    print(f"  Recall cost: mean={np.mean(random_recall):.1f}, std={np.std(random_recall):.1f}")
    print()

    # Compare manuscript to alternatives
    print("=" * 60)
    print("Optimality Analysis")
    print("=" * 60)

    ms_forgetting = results['manuscript']['forgetting_events']
    ms_recall = results['manuscript']['recall_cost']

    # Z-score vs random
    z_forgetting = (ms_forgetting - np.mean(random_forgetting)) / np.std(random_forgetting)
    z_recall = (ms_recall - np.mean(random_recall)) / np.std(random_recall)

    # Percentile vs random
    pct_forgetting = stats.percentileofscore(random_forgetting, ms_forgetting)
    pct_recall = stats.percentileofscore(random_recall, ms_recall)

    print(f"\nManuscript vs Random:")
    print(f"  Forgetting z-score: {z_forgetting:.2f} (percentile: {pct_forgetting:.1f}%)")
    print(f"  Recall cost z-score: {z_recall:.2f} (percentile: {pct_recall:.1f}%)")

    # Rank among alternatives
    all_orderings = list(results.keys())
    forgetting_rank = sorted(all_orderings, key=lambda x: results[x]['forgetting_events'])
    recall_rank = sorted(all_orderings, key=lambda x: results[x]['recall_cost'])

    print(f"\nRank by forgetting (best=1): {forgetting_rank.index('manuscript') + 1}/{len(forgetting_rank)}")
    print(f"Rank by recall cost (best=1): {recall_rank.index('manuscript') + 1}/{len(recall_rank)}")

    # Best alternative
    best_forgetting = forgetting_rank[0]
    best_recall = recall_rank[0]
    print(f"\nBest by forgetting: {best_forgetting} ({results[best_forgetting]['forgetting_events']})")
    print(f"Best by recall: {best_recall} ({results[best_recall]['recall_cost']:.2f})")

    # Verdict
    print("\n" + "=" * 60)

    # Criteria:
    # - OPTIMAL: manuscript is best or within 10% of best
    # - NEAR_OPTIMAL: manuscript better than random (z < -1)
    # - SUBOPTIMAL: manuscript worse than or equal to random
    # - ANTI_OPTIMAL: manuscript worse than most alternatives

    ms_rank_forgetting = forgetting_rank.index('manuscript') + 1
    ms_rank_recall = recall_rank.index('manuscript') + 1
    n_orderings = len(forgetting_rank)

    if ms_rank_forgetting == 1 or ms_rank_recall == 1:
        verdict = "OPTIMAL"
        print("VERDICT: MANUSCRIPT ORDERING IS OPTIMAL")
        print("  Manuscript order minimizes memory cost.")
    elif z_forgetting < -1 or z_recall < -1:
        verdict = "NEAR_OPTIMAL"
        print("VERDICT: MANUSCRIPT ORDERING IS NEAR-OPTIMAL")
        print(f"  Better than random (z={min(z_forgetting, z_recall):.2f}).")
        print(f"  Rank: {ms_rank_forgetting}/{n_orderings} by forgetting, {ms_rank_recall}/{n_orderings} by recall.")
    elif z_forgetting > 1 or z_recall > 1:
        verdict = "SUBOPTIMAL"
        print("VERDICT: MANUSCRIPT ORDERING IS SUBOPTIMAL")
        print(f"  Worse than random (z={max(z_forgetting, z_recall):.2f}).")
        print("  Ordering may serve non-memory purposes.")
    else:
        verdict = "RANDOM_EQUIVALENT"
        print("VERDICT: MANUSCRIPT ORDERING IS RANDOM-EQUIVALENT")
        print("  No significant optimization detected.")
    print("=" * 60)

    # Save results
    output = {
        "test": "5A_MEMORY_OPTIMALITY",
        "tier": "3-4",
        "question": "Is A-registry ordering optimal under realistic memory decay?",
        "data": {
            "total_entries": len(entries),
            "unique_middles": len(middles_freq),
            "unique_folios": len(folios)
        },
        "ordering_metrics": {k: {kk: float(vv) if isinstance(vv, (int, float, np.floating, np.integer)) else vv
                                 for kk, vv in v.items()}
                            for k, v in results.items()},
        "random_baseline": {
            "n_samples": len(random_metrics),
            "forgetting_mean": float(np.mean(random_forgetting)),
            "forgetting_std": float(np.std(random_forgetting)),
            "recall_mean": float(np.mean(random_recall)),
            "recall_std": float(np.std(random_recall))
        },
        "manuscript_analysis": {
            "forgetting_z": float(z_forgetting),
            "recall_z": float(z_recall),
            "forgetting_percentile": float(pct_forgetting),
            "recall_percentile": float(pct_recall),
            "rank_forgetting": ms_rank_forgetting,
            "rank_recall": ms_rank_recall,
            "n_orderings": n_orderings
        },
        "verdict": verdict
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
