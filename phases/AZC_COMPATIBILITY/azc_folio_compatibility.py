#!/usr/bin/env python3
"""
AZC Folio Compatibility Structure Probe

Determines which AZC folios are mutually exclusive vs compatible by analyzing
their vocabulary co-occurrence patterns in B programs.

Key insight: Vocabulary being disjoint (C437) does NOT mean folios are exclusive.
Two folios with zero shared tokens can still be compatible if their tokens
co-occur in the same B programs.

Method:
1. Build token -> AZC folio mapping
2. For each B program, compute which AZC folios are "activated"
3. Build pairwise Jaccard matrix on B-program co-occurrence
4. Cluster and test hypotheses

Hypotheses:
- H1: Family clustering (within-family > cross-family compatibility)
- H2: Phase-based structure (different-phase > same-phase compatibility)
- H3: Hub-and-spoke architecture (some folios are hubs with high centrality)
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import statistics

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "azc_folio_compatibility.json"

# AZC Family definitions (from C430)
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

ALL_AZC_FOLIOS = ZODIAC_FOLIOS | AC_FOLIOS


def build_token_to_azc_mapping() -> Dict[str, Set[str]]:
    """Build mapping of token -> set of AZC folios it appears in."""
    token_to_folios = defaultdict(set)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Only track tokens in AZC folios
            if folio in ALL_AZC_FOLIOS:
                token_to_folios[word].add(folio)

    return dict(token_to_folios)


def build_b_program_activations(token_to_azc: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    For each B program (folio), compute which AZC folios are "activated"
    (i.e., which AZC folios contributed vocabulary to that B program).
    """
    b_activations = defaultdict(set)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Only B programs
            if language != 'B':
                continue

            # Get which AZC folios this token appears in
            azc_folios = token_to_azc.get(word, set())
            b_activations[folio].update(azc_folios)

    return dict(b_activations)


def compute_jaccard(set1: Set[str], set2: Set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def compute_compatibility_matrix(b_activations: Dict[str, Set[str]]) -> Dict[Tuple[str, str], float]:
    """
    Compute pairwise Jaccard similarity between AZC folios based on
    their co-occurrence in B programs.
    """
    # For each AZC folio, get set of B programs where it's activated
    azc_to_b_programs = defaultdict(set)

    for b_folio, azc_folios in b_activations.items():
        for azc_folio in azc_folios:
            azc_to_b_programs[azc_folio].add(b_folio)

    # Compute pairwise Jaccard
    matrix = {}
    azc_folios = sorted(ALL_AZC_FOLIOS)

    for i, folio_i in enumerate(azc_folios):
        for folio_j in azc_folios[i:]:
            b_i = azc_to_b_programs.get(folio_i, set())
            b_j = azc_to_b_programs.get(folio_j, set())
            jaccard = compute_jaccard(b_i, b_j)
            matrix[(folio_i, folio_j)] = jaccard
            matrix[(folio_j, folio_i)] = jaccard

    return matrix, azc_to_b_programs


def simple_clustering(matrix: Dict[Tuple[str, str], float], threshold: float = 0.5) -> List[Set[str]]:
    """Simple single-linkage clustering based on compatibility threshold."""
    folios = sorted(ALL_AZC_FOLIOS)
    folio_to_cluster = {f: i for i, f in enumerate(folios)}
    clusters = [{f} for f in folios]

    for folio_i in folios:
        for folio_j in folios:
            if folio_i >= folio_j:
                continue
            jaccard = matrix.get((folio_i, folio_j), 0)
            if jaccard >= threshold:
                c1 = folio_to_cluster[folio_i]
                c2 = folio_to_cluster[folio_j]
                if c1 != c2:
                    # Merge smaller into larger
                    if len(clusters[c1]) < len(clusters[c2]):
                        c1, c2 = c2, c1
                    for f in clusters[c2]:
                        folio_to_cluster[f] = c1
                        clusters[c1].add(f)
                    clusters[c2] = set()

    return [c for c in clusters if len(c) > 0]


def test_h1_family_clustering(matrix: Dict[Tuple[str, str], float]) -> Dict:
    """
    H1: Family-Level Clustering
    Test if within-family compatibility > cross-family compatibility.
    """
    within_zodiac = []
    within_ac = []
    cross_family = []

    for (folio_i, folio_j), jaccard in matrix.items():
        if folio_i == folio_j:
            continue  # Skip diagonal

        i_zodiac = folio_i in ZODIAC_FOLIOS
        j_zodiac = folio_j in ZODIAC_FOLIOS

        if i_zodiac and j_zodiac:
            within_zodiac.append(jaccard)
        elif not i_zodiac and not j_zodiac:
            within_ac.append(jaccard)
        else:
            cross_family.append(jaccard)

    # Compute statistics
    mean_within_zodiac = statistics.mean(within_zodiac) if within_zodiac else 0
    mean_within_ac = statistics.mean(within_ac) if within_ac else 0
    mean_cross = statistics.mean(cross_family) if cross_family else 0

    # Combined within-family mean
    all_within = within_zodiac + within_ac
    mean_within = statistics.mean(all_within) if all_within else 0

    # Verdict
    if mean_within > mean_cross * 1.1:  # 10% higher
        verdict = "SUPPORTED"
    elif mean_within < mean_cross * 0.9:  # 10% lower
        verdict = "REJECTED"
    else:
        verdict = "INCONCLUSIVE"

    return {
        'within_zodiac_mean': round(mean_within_zodiac, 4),
        'within_zodiac_n': len(within_zodiac),
        'within_ac_mean': round(mean_within_ac, 4),
        'within_ac_n': len(within_ac),
        'cross_family_mean': round(mean_cross, 4),
        'cross_family_n': len(cross_family),
        'mean_within': round(mean_within, 4),
        'verdict': verdict,
        'interpretation': f"Within-family: {mean_within:.4f}, Cross-family: {mean_cross:.4f}"
    }


def test_h3_hub_spoke(matrix: Dict[Tuple[str, str], float],
                       azc_to_b_programs: Dict[str, Set[str]]) -> Dict:
    """
    H3: Hub-and-Spoke Architecture
    Test if some folios are "hubs" (compatible with many others).
    """
    # Compute degree centrality (sum of Jaccard scores)
    centrality = defaultdict(float)

    for (folio_i, folio_j), jaccard in matrix.items():
        if folio_i != folio_j:
            centrality[folio_i] += jaccard

    # Normalize by number of possible connections
    n_folios = len(ALL_AZC_FOLIOS)
    for folio in centrality:
        centrality[folio] /= (n_folios - 1)

    # Sort by centrality
    sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

    # Identify hubs (top 20%) and spokes (bottom 20%)
    n_top = max(1, len(sorted_centrality) // 5)
    hubs = sorted_centrality[:n_top]
    spokes = sorted_centrality[-n_top:]

    # Check hub properties
    hub_vocab_sizes = [len(azc_to_b_programs.get(f, set())) for f, _ in hubs]
    spoke_vocab_sizes = [len(azc_to_b_programs.get(f, set())) for f, _ in spokes]

    mean_hub_reach = statistics.mean(hub_vocab_sizes) if hub_vocab_sizes else 0
    mean_spoke_reach = statistics.mean(spoke_vocab_sizes) if spoke_vocab_sizes else 0

    # Verdict: Is there significant variance in centrality?
    centrality_values = list(centrality.values())
    if centrality_values:
        cv = statistics.stdev(centrality_values) / statistics.mean(centrality_values) if statistics.mean(centrality_values) > 0 else 0
    else:
        cv = 0

    if cv > 0.3:  # Substantial variation
        verdict = "SUPPORTED"
    elif cv < 0.1:  # Very uniform
        verdict = "REJECTED"
    else:
        verdict = "INCONCLUSIVE"

    return {
        'hub_folios': [(f, round(c, 4)) for f, c in hubs],
        'spoke_folios': [(f, round(c, 4)) for f, c in spokes],
        'mean_hub_centrality': round(hubs[0][1], 4) if hubs else 0,
        'mean_spoke_centrality': round(spokes[-1][1], 4) if spokes else 0,
        'centrality_cv': round(cv, 4),
        'mean_hub_b_reach': round(mean_hub_reach, 1),
        'mean_spoke_b_reach': round(mean_spoke_reach, 1),
        'verdict': verdict,
        'interpretation': f"Centrality CV = {cv:.4f} ({'high variance = hub structure' if cv > 0.2 else 'uniform'})"
    }


def find_exclusive_pairs(matrix: Dict[Tuple[str, str], float],
                          threshold: float = 0.1) -> List[Tuple[str, str, float]]:
    """Find folio pairs with very low compatibility (potentially exclusive)."""
    exclusive = []
    seen = set()

    for (folio_i, folio_j), jaccard in matrix.items():
        if folio_i == folio_j:
            continue
        pair = tuple(sorted([folio_i, folio_j]))
        if pair in seen:
            continue
        seen.add(pair)

        if jaccard < threshold:
            exclusive.append((folio_i, folio_j, jaccard))

    return sorted(exclusive, key=lambda x: x[2])


def find_highly_compatible(matrix: Dict[Tuple[str, str], float],
                            threshold: float = 0.8) -> List[Tuple[str, str, float]]:
    """Find folio pairs with very high compatibility."""
    compatible = []
    seen = set()

    for (folio_i, folio_j), jaccard in matrix.items():
        if folio_i == folio_j:
            continue
        pair = tuple(sorted([folio_i, folio_j]))
        if pair in seen:
            continue
        seen.add(pair)

        if jaccard > threshold:
            compatible.append((folio_i, folio_j, jaccard))

    return sorted(compatible, key=lambda x: x[2], reverse=True)


def main():
    print("=" * 70)
    print("AZC FOLIO COMPATIBILITY STRUCTURE PROBE")
    print("=" * 70)
    print("\nQuestion: Which AZC folios are mutually exclusive vs compatible?")
    print()

    # Step 1: Build token -> AZC mapping
    print("1. Building token -> AZC folio mapping...")
    token_to_azc = build_token_to_azc_mapping()
    print(f"   Mapped {len(token_to_azc)} tokens to AZC folios")

    # Step 2: Build B program activations
    print("\n2. Computing B program -> AZC activations...")
    b_activations = build_b_program_activations(token_to_azc)
    print(f"   Found {len(b_activations)} B programs with AZC vocabulary")

    # Statistics on activations
    activation_counts = [len(v) for v in b_activations.values()]
    mean_activated = statistics.mean(activation_counts) if activation_counts else 0
    print(f"   Mean AZC folios activated per B program: {mean_activated:.1f}")

    # Step 3: Compute compatibility matrix
    print("\n3. Computing pairwise compatibility matrix...")
    matrix, azc_to_b_programs = compute_compatibility_matrix(b_activations)

    # Get all unique Jaccard values (excluding diagonal)
    jaccard_values = [v for (i, j), v in matrix.items() if i != j]
    mean_jaccard = statistics.mean(jaccard_values) if jaccard_values else 0
    std_jaccard = statistics.stdev(jaccard_values) if len(jaccard_values) > 1 else 0

    print(f"   Mean pairwise Jaccard: {mean_jaccard:.4f} +/- {std_jaccard:.4f}")

    # Step 4: Test hypotheses
    print("\n" + "=" * 70)
    print("HYPOTHESIS TESTING")
    print("=" * 70)

    # H1: Family clustering
    print("\n### H1: Family-Level Clustering ###")
    h1_results = test_h1_family_clustering(matrix)
    print(f"   Within-Zodiac mean: {h1_results['within_zodiac_mean']:.4f} (n={h1_results['within_zodiac_n']})")
    print(f"   Within-A/C mean: {h1_results['within_ac_mean']:.4f} (n={h1_results['within_ac_n']})")
    print(f"   Cross-family mean: {h1_results['cross_family_mean']:.4f} (n={h1_results['cross_family_n']})")
    print(f"   >>> Verdict: {h1_results['verdict']} <<<")

    # H3: Hub-and-spoke
    print("\n### H3: Hub-and-Spoke Architecture ###")
    h3_results = test_h3_hub_spoke(matrix, azc_to_b_programs)
    print(f"   Top hubs: {h3_results['hub_folios'][:3]}")
    print(f"   Bottom spokes: {h3_results['spoke_folios'][-3:]}")
    print(f"   Centrality CV: {h3_results['centrality_cv']:.4f}")
    print(f"   >>> Verdict: {h3_results['verdict']} <<<")

    # Step 5: Find exclusive and highly compatible pairs
    print("\n" + "=" * 70)
    print("COMPATIBILITY EXTREMES")
    print("=" * 70)

    exclusive_pairs = find_exclusive_pairs(matrix, threshold=0.3)
    highly_compatible = find_highly_compatible(matrix, threshold=0.9)

    print(f"\n### Potentially Exclusive Pairs (Jaccard < 0.3): {len(exclusive_pairs)} ###")
    for folio_i, folio_j, jaccard in exclusive_pairs[:10]:
        i_family = "Zod" if folio_i in ZODIAC_FOLIOS else "A/C"
        j_family = "Zod" if folio_j in ZODIAC_FOLIOS else "A/C"
        print(f"   {folio_i} ({i_family}) <-> {folio_j} ({j_family}): {jaccard:.4f}")

    print(f"\n### Highly Compatible Pairs (Jaccard > 0.9): {len(highly_compatible)} ###")
    for folio_i, folio_j, jaccard in highly_compatible[:10]:
        i_family = "Zod" if folio_i in ZODIAC_FOLIOS else "A/C"
        j_family = "Zod" if folio_j in ZODIAC_FOLIOS else "A/C"
        print(f"   {folio_i} ({i_family}) <-> {folio_j} ({j_family}): {jaccard:.4f}")

    # Step 6: Clustering
    print("\n" + "=" * 70)
    print("CLUSTERING ANALYSIS")
    print("=" * 70)

    for threshold in [0.7, 0.8, 0.9]:
        clusters = simple_clustering(matrix, threshold=threshold)
        non_singleton = [c for c in clusters if len(c) >= 2]
        print(f"\n   Threshold {threshold}: {len(non_singleton)} clusters (size >= 2)")
        for i, cluster in enumerate(sorted(non_singleton, key=len, reverse=True)[:3]):
            zodiac_in = len(cluster & ZODIAC_FOLIOS)
            ac_in = len(cluster & AC_FOLIOS)
            print(f"      Cluster {i+1} (n={len(cluster)}): {zodiac_in} Zodiac, {ac_in} A/C")

    # Step 7: Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Determine overall verdict
    n_exclusive = len(exclusive_pairs)
    n_compatible = len(highly_compatible)

    if n_exclusive > len(ALL_AZC_FOLIOS) * 2:
        exclusivity_verdict = "STRONG_EXCLUSIVITY"
    elif n_exclusive > len(ALL_AZC_FOLIOS):
        exclusivity_verdict = "MODERATE_EXCLUSIVITY"
    elif n_exclusive == 0:
        exclusivity_verdict = "NO_EXCLUSIVITY"
    else:
        exclusivity_verdict = "WEAK_EXCLUSIVITY"

    print(f"\n   Exclusivity: {exclusivity_verdict}")
    print(f"   H1 (Family clustering): {h1_results['verdict']}")
    print(f"   H3 (Hub-spoke): {h3_results['verdict']}")

    # Save results
    output = {
        'probe_id': 'AZC_FOLIO_COMPATIBILITY',
        'question': 'Which AZC folios are mutually exclusive vs compatible?',
        'method': 'B-program co-occurrence Jaccard similarity',
        'data': {
            'n_tokens_mapped': len(token_to_azc),
            'n_b_programs': len(b_activations),
            'mean_azc_per_b': round(mean_activated, 2),
            'n_azc_folios': len(ALL_AZC_FOLIOS)
        },
        'matrix_stats': {
            'mean_jaccard': round(mean_jaccard, 4),
            'std_jaccard': round(std_jaccard, 4)
        },
        'hypotheses': {
            'H1_family_clustering': h1_results,
            'H3_hub_spoke': h3_results
        },
        'exclusive_pairs': [(i, j, round(v, 4)) for i, j, v in exclusive_pairs],
        'highly_compatible': [(i, j, round(v, 4)) for i, j, v in highly_compatible],
        'verdict': {
            'exclusivity': exclusivity_verdict,
            'interpretation': f"Mean Jaccard {mean_jaccard:.4f} with {len(exclusive_pairs)} low-compatibility pairs"
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    main()
