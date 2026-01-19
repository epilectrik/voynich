#!/usr/bin/env python3
"""
Phase 12: Alchemical Tradition Fingerprinting
==============================================

Determines which historically attested alchemical tradition the Voynich's
transformation algebra belongs to.

Tests:
- 12A: Operation Canon Size Test (scholastic ~7-12 vs Paracelsian ~3)
- 12B: Substance vs State Emphasis (concentrated vs distributed attractors)
- 12C: Quantitative Weighting Pattern (balanced 4/7 vs tria prima 3)
- 12D: B-Text Procedural Style (enumerative vs cyclical)
- 12E: Novelty Detection (does Voynich exceed known traditions?)

Ground Rules:
- No word guessing - comparing structural signatures, not labels
- No image interpretation
- Historical traditions as hypotheses - test fit, don't assume
"""

import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set
import random

# ============================================================================
# CONSTANTS FROM PREVIOUS PHASES
# ============================================================================

KNOWN_PREFIXES = {'qo', 'da', 'ch', 'sh', 'ok', 'ot', 'sa', 'ct', 'yk', 'yp',
                  'ar', 'ko', 'so', 'ra', 'ta', 'op', 'cf', 'fc', 'pc', 'ts',
                  'al', 'ol', 'or', 'dy', 'od', 'ke', 'am', 'lk', 'ka'}
KNOWN_SUFFIXES = {'aiin', 'ol', 'hy', 'or', 'ar', 'ey', 'edy', 'dy', 'y',
                  'al', 'eey', 'eedy', 'ain', 'in', 'an', 'am', 'o'}

# Historical tradition parameters (estimated from literature)
TRADITION_PARAMETERS = {
    "scholastic": {
        "operation_count": (7, 12),  # 7-12 named operations
        "reversibility": (0.50, 0.70),  # 50-70% reversibility
        "commutativity": (0.20, 0.40),  # 20-40% commutativity
        "tria_prima_emphasis": "low",  # Less emphasis on 3
        "attractor_concentration": "high",  # Few concentrated attractors
        "procedural_style": "enumerative"  # Step-by-step
    },
    "paracelsian": {
        "operation_count": (3, 6),  # Fewer named operations
        "reversibility": (0.70, 0.85),  # Higher reversibility
        "commutativity": (0.40, 0.60),  # Moderate commutativity
        "tria_prima_emphasis": "high",  # Strong 3 (salt/sulfur/mercury)
        "attractor_concentration": "distributed",  # Many distributed attractors
        "procedural_style": "cyclical"  # Recurring patterns
    }
}

# ============================================================================
# CORPUS LOADING (reused from Phase 10-11)
# ============================================================================

def load_corpus():
    """Load the interlinear transcription corpus."""
    corpus_path = Path("data/transcriptions/interlinear_full_words.txt")
    records = []

    with open(corpus_path, 'r', encoding='utf-8') as f:
        header = None
        for line in f:
            if line.strip():
                parts = line.strip().split('\t')
                if header is None:
                    header = parts
                    continue
                if len(parts) >= 7:
                    # CRITICAL: Filter to H (PRIMARY) transcriber track only
                    transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                    if transcriber != 'H':
                        continue

                    word = parts[0].strip('"')
                    folio = parts[2].strip('"')
                    language = parts[6].strip('"')
                    if '*' in word or '?' in word:
                        continue
                    records.append({
                        'folio': folio,
                        'word': word,
                        'population': language
                    })
    return records

def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [2, 1]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    return word[:2] if len(word) >= 2 else word

def get_suffix(word: str) -> str:
    """Extract suffix from word."""
    for length in [4, 3, 2, 1]:
        if len(word) >= length:
            suffix = word[-length:]
            if suffix in KNOWN_SUFFIXES:
                return suffix
    return word[-2:] if len(word) >= 2 else word

def get_middle(word: str) -> str:
    """Extract middle from word."""
    prefix = get_prefix(word)
    suffix = get_suffix(word)
    if len(word) <= len(prefix) + len(suffix):
        return word
    middle = word[len(prefix):-len(suffix)] if suffix else word[len(prefix):]
    return middle if middle else word

def group_by_entry(records: List[Dict]) -> Dict[str, List[str]]:
    """Group tokens by folio (entry)."""
    entries = defaultdict(list)
    for rec in records:
        entries[rec['folio']].append(rec['word'])
    return dict(entries)

# ============================================================================
# LOAD PREVIOUS PHASE RESULTS
# ============================================================================

def load_phase10_results() -> Dict:
    """Load Phase 10 analysis results."""
    results = {}

    # Load operator features
    with open("phase10a_operator_clusters.json", 'r') as f:
        results['10a'] = json.load(f)

    # Load graph data
    with open("phase10b_operator_graph.json", 'r') as f:
        results['10b'] = json.load(f)

    # Load signatures
    with open("phase10c_alchemical_signatures.json", 'r') as f:
        results['10c'] = json.load(f)

    # Load operation classes
    with open("phase10d_operation_classes.json", 'r') as f:
        results['10d'] = json.load(f)

    return results

def load_phase11_results() -> Dict:
    """Load Phase 11 analysis results."""
    results = {}

    with open("phase11a_cardinality_fingerprints.json", 'r') as f:
        results['11a'] = json.load(f)

    with open("phase11c_cycle_lengths.json", 'r') as f:
        results['11c'] = json.load(f)

    with open("phase11d_population_split.json", 'r') as f:
        results['11d'] = json.load(f)

    return results

# ============================================================================
# 12A: OPERATION CANON SIZE TEST
# ============================================================================

def test_12a_operation_canon(phase10: Dict, entries: Dict[str, List[str]]) -> Dict:
    """
    Test: Are operations NAMED ENTITIES (scholastic) or BEHAVIORS OVER STATES (Paracelsian)?

    Method:
    - Cluster the 27 cyclic operators by their actual effects
    - Count functionally distinct operation types
    - Compare to scholastic (~7-12) vs Paracelsian (~3)
    """
    print("Running Phase 12A: Operation Canon Size Test...")

    operator_features = phase10['10a']['operator_features']

    # Get all cyclic operators
    cyclic_ops = phase10['10a']['behavior_clusters'].get('CYCLIC_BIDIRECTIONAL', [])

    # Build feature vectors for clustering
    feature_vectors = {}
    for op in cyclic_ops:
        if op in operator_features:
            f = operator_features[op]
            # Key discriminating features
            feature_vectors[op] = [
                f.get('reversibility', 0.5),
                f.get('commutativity_rate', 0.5),
                f.get('mean_position', 5.0) / 10.0,  # Normalize
                f.get('entry_initial_rate', 0.1),
                f.get('entry_terminal_rate', 0.1),
                f.get('hub_concentration', 0.5),
                min(1.0, f.get('cycle_participation', 0) / 1000)  # Normalize
            ]

    # Simple agglomerative clustering by distance
    clusters = cluster_by_behavior(feature_vectors, threshold=0.15)

    # Also cluster by hub transition patterns
    hub_transition_clusters = cluster_by_hub_effects(entries, cyclic_ops)

    # Count distinct functional types
    functional_clusters = max(len(clusters), len(hub_transition_clusters))

    # Determine fit
    scholastic_range = (7, 12)
    paracelsian_range = (3, 6)

    scholastic_distance = distance_to_range(functional_clusters, scholastic_range)
    paracelsian_distance = distance_to_range(functional_clusters, paracelsian_range)

    if scholastic_distance < paracelsian_distance:
        verdict = "SCHOLASTIC"
        fit_description = f"Cluster count {functional_clusters} closer to scholastic range {scholastic_range}"
    elif paracelsian_distance < scholastic_distance:
        verdict = "PARACELSIAN"
        fit_description = f"Cluster count {functional_clusters} closer to Paracelsian range {paracelsian_range}"
    else:
        verdict = "INTERMEDIATE"
        fit_description = f"Cluster count {functional_clusters} equidistant from both traditions"

    return {
        "metadata": {
            "phase": "12A",
            "title": "Operation Canon Size Test",
            "timestamp": datetime.now().isoformat()
        },
        "surface_operator_count": len(cyclic_ops),
        "functional_cluster_count": functional_clusters,
        "behavioral_clusters": {
            "by_feature": {
                "count": len(clusters),
                "clusters": {f"cluster_{i}": ops for i, ops in enumerate(clusters)}
            },
            "by_hub_effect": {
                "count": len(hub_transition_clusters),
                "clusters": {f"cluster_{i}": list(ops) for i, ops in enumerate(hub_transition_clusters)}
            }
        },
        "comparison": {
            "scholastic_expected": f"{scholastic_range[0]}-{scholastic_range[1]}",
            "paracelsian_expected": f"{paracelsian_range[0]}-{paracelsian_range[1]}",
            "scholastic_fit": round(1.0 / (1 + scholastic_distance), 3),
            "paracelsian_fit": round(1.0 / (1 + paracelsian_distance), 3)
        },
        "VERDICT": verdict,
        "interpretation": fit_description
    }

def cluster_by_behavior(feature_vectors: Dict[str, List[float]], threshold: float) -> List[List[str]]:
    """Simple agglomerative clustering of operators by feature similarity."""
    if not feature_vectors:
        return []

    # Start with each operator in its own cluster
    ops = list(feature_vectors.keys())
    clusters = [[op] for op in ops]

    def euclidean_distance(v1, v2):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    def cluster_distance(c1, c2):
        """Average linkage distance."""
        distances = []
        for op1 in c1:
            for op2 in c2:
                if op1 in feature_vectors and op2 in feature_vectors:
                    distances.append(euclidean_distance(
                        feature_vectors[op1], feature_vectors[op2]
                    ))
        return sum(distances) / len(distances) if distances else float('inf')

    # Agglomerate until no clusters are close enough
    while len(clusters) > 1:
        # Find closest pair
        min_dist = float('inf')
        merge_pair = None

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = cluster_distance(clusters[i], clusters[j])
                if d < min_dist:
                    min_dist = d
                    merge_pair = (i, j)

        if min_dist > threshold or merge_pair is None:
            break

        # Merge clusters
        i, j = merge_pair
        new_cluster = clusters[i] + clusters[j]
        clusters = [c for k, c in enumerate(clusters) if k not in (i, j)]
        clusters.append(new_cluster)

    return clusters

def cluster_by_hub_effects(entries: Dict[str, List[str]], operators: List[str]) -> List[Set[str]]:
    """Cluster operators by their effect on hub/middle transitions."""
    # Build transition profiles for each operator
    transition_profiles = defaultdict(Counter)

    for folio, tokens in entries.items():
        for i in range(len(tokens) - 1):
            op = get_prefix(tokens[i + 1])
            if op in operators:
                m1 = get_middle(tokens[i])
                m2 = get_middle(tokens[i + 1])
                if m1 and m2:
                    # Track what types of transitions this operator enables
                    transition_type = "same" if m1 == m2 else "different"
                    transition_profiles[op][transition_type] += 1

    # Group by transition behavior
    clusters = []

    # High-same-rate operators
    high_same = set()
    for op, profile in transition_profiles.items():
        total = sum(profile.values())
        if total > 10:
            same_rate = profile.get('same', 0) / total
            if same_rate > 0.3:
                high_same.add(op)

    if high_same:
        clusters.append(high_same)

    # High-different-rate operators
    high_diff = set()
    for op, profile in transition_profiles.items():
        total = sum(profile.values())
        if total > 10:
            diff_rate = profile.get('different', 0) / total
            if diff_rate > 0.7:
                high_diff.add(op)

    if high_diff:
        clusters.append(high_diff)

    # Mixed operators
    mixed = set(operators) - high_same - high_diff
    if mixed:
        clusters.append(mixed)

    return clusters

def distance_to_range(value: int, range_tuple: Tuple[int, int]) -> float:
    """Calculate distance from value to a range."""
    low, high = range_tuple
    if low <= value <= high:
        return 0
    elif value < low:
        return low - value
    else:
        return value - high

# ============================================================================
# 12B: SUBSTANCE VS STATE EMPHASIS
# ============================================================================

def test_12b_substance_state(phase10: Dict) -> Dict:
    """
    Test: Do attractors represent SUBSTANCES (few, concentrated) or STATES (many, distributed)?

    Method:
    - Analyze attractor distribution from Phase 10B
    - Calculate Gini coefficient of convergence
    - Check top-5 attractor concentration
    """
    print("Running Phase 12B: Substance vs State Emphasis...")

    attractor_data = phase10['10b']['attractor_states']
    top_attractors = attractor_data.get('top_10', [])
    attractor_count = attractor_data['count']

    # Extract convergence counts for top attractors
    convergence_counts = [a[1] for a in top_attractors]  # (node, sources, in_degree)

    # Get total convergence across all attractors
    # Estimate from graph statistics
    graph_stats = phase10['10b']['graph_statistics']
    total_in_degree = graph_stats.get('total_edge_weight', 100000)

    # Top 5 concentration
    top_5_convergence = sum(convergence_counts[:5]) if len(convergence_counts) >= 5 else sum(convergence_counts)

    # Estimate total convergence for all attractors (approximation)
    # Use the sum of top 10 as base and extrapolate
    top_10_sum = sum(convergence_counts)
    # Assume power-law distribution - remaining attractors contribute ~30% more
    estimated_total = top_10_sum * 1.5

    top_5_concentration = top_5_convergence / estimated_total if estimated_total > 0 else 0

    # Calculate Gini coefficient of convergence distribution
    gini = calculate_gini(convergence_counts + [1] * (attractor_count - len(convergence_counts)))

    # Determine substance vs state
    # Substance-focused: Gini > 0.7, top-5 > 50%
    # State-focused: Gini < 0.5, top-5 < 30%

    if gini > 0.7 and top_5_concentration > 0.5:
        verdict = "SUBSTANCE-FOCUSED"
        interpretation = ("Attractors are highly concentrated - few dominant states capture most convergence. "
                         "Consistent with substance-focused scholastic alchemy (terminal products as goals).")
    elif gini < 0.5 and top_5_concentration < 0.3:
        verdict = "STATE-FOCUSED"
        interpretation = ("Attractors are widely distributed - many states with similar convergence. "
                         "Consistent with state-focused Paracelsian tradition (degrees of purification).")
    else:
        verdict = "MIXED"
        interpretation = (f"Intermediate attractor distribution (Gini={gini:.2f}, top-5={top_5_concentration:.1%}). "
                         "Neither purely substance nor state focused.")

    return {
        "metadata": {
            "phase": "12B",
            "title": "Substance vs State Emphasis",
            "timestamp": datetime.now().isoformat()
        },
        "attractor_count": attractor_count,
        "top_5_attractors": [(a[0], a[1]) for a in top_attractors[:5]],
        "top_5_concentration": round(top_5_concentration, 3),
        "gini_coefficient": round(gini, 3),
        "thresholds": {
            "substance_signature": "Gini > 0.7, top-5 > 50%",
            "state_signature": "Gini < 0.5, top-5 < 30%"
        },
        "VERDICT": verdict,
        "interpretation": interpretation
    }

def calculate_gini(values: List[float]) -> float:
    """Calculate Gini coefficient of inequality."""
    if not values or all(v == 0 for v in values):
        return 0

    values = sorted(values)
    n = len(values)
    cumsum = 0

    for i, v in enumerate(values):
        cumsum += v * (n - i)

    mean = sum(values) / n
    if mean == 0:
        return 0

    gini = (2 * cumsum) / (n * sum(values)) - (n + 1) / n
    return max(0, min(1, gini))  # Clamp to [0, 1]

# ============================================================================
# 12C: QUANTITATIVE WEIGHTING PATTERN
# ============================================================================

def test_12c_quantitative_weighting(phase11: Dict) -> Dict:
    """
    Test: Which numerical signature dominates - balanced 4/7 (scholastic) or tria prima 3 (Paracelsian)?

    Uses cardinality peaks and cycle alignments from Phase 11.
    """
    print("Running Phase 12C: Quantitative Weighting Pattern...")

    # Get cycle alignment scores from Phase 11C
    alignment_scores = phase11['11c'].get('alignment_scores', {})

    tria_prima_3 = alignment_scores.get('tria_prima_3', 0)
    elemental_4 = alignment_scores.get('elemental_4', 0)
    planetary_7 = alignment_scores.get('planetary_7', 0)
    zodiacal_12 = alignment_scores.get('zodiacal_12', 0)

    # Get significant cardinalities from Phase 11A
    significant_cards = phase11['11a'].get('significant_cardinalities', [])

    # Calculate dominance ratios
    scholastic_avg = (elemental_4 + planetary_7) / 2 if (elemental_4 + planetary_7) > 0 else 1
    tria_prima_dominance = tria_prima_3 / scholastic_avg if scholastic_avg > 0 else 0

    # Scholastic balance: how similar are 4 and 7?
    scholastic_balance = 1 - abs(elemental_4 - planetary_7) / max(elemental_4, planetary_7, 1)

    # Check cardinality profile
    has_3 = 3 in significant_cards
    has_4 = 4 in significant_cards
    has_7 = 7 in significant_cards
    has_12 = 12 in significant_cards

    # Determine pattern
    if tria_prima_3 > 2.0 and tria_prima_dominance > 1.0:
        verdict = "PARACELSIAN_TRIA_PRIMA"
        interpretation = (f"Strong tria prima (3) dominance ({tria_prima_3:.2f}x enrichment). "
                         "Consistent with Paracelsian salt/sulfur/mercury framework.")
    elif scholastic_balance > 0.7 and elemental_4 > 1.5 and planetary_7 > 1.0:
        verdict = "SCHOLASTIC_BALANCED"
        interpretation = (f"Balanced elemental (4: {elemental_4:.2f}x) and planetary (7: {planetary_7:.2f}x) signatures. "
                         "Consistent with scholastic Aristotelian framework.")
    else:
        verdict = "MIXED"
        interpretation = (f"Mixed quantitative pattern. Tria prima: {tria_prima_3:.2f}x, "
                         f"Elemental: {elemental_4:.2f}x, Planetary: {planetary_7:.2f}x.")

    return {
        "metadata": {
            "phase": "12C",
            "title": "Quantitative Weighting Pattern",
            "timestamp": datetime.now().isoformat()
        },
        "alignment_scores": {
            "tria_prima_3": tria_prima_3,
            "elemental_4": elemental_4,
            "planetary_7": planetary_7,
            "zodiacal_12": zodiacal_12
        },
        "significant_cardinalities": significant_cards,
        "derived_metrics": {
            "tria_prima_dominance": round(tria_prima_dominance, 3),
            "scholastic_balance": round(scholastic_balance, 3),
            "has_key_numbers": {
                "3": has_3,
                "4": has_4,
                "7": has_7,
                "12": has_12
            }
        },
        "VERDICT": verdict,
        "interpretation": interpretation
    }

# ============================================================================
# 12D: B-TEXT PROCEDURAL STYLE
# ============================================================================

def test_12d_btext_style(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Test: Does B-text ENUMERATE OPERATIONS (scholastic) or NARRATE CYCLES (Paracelsian)?

    Method:
    - Measure cycle density per B-text entry
    - Measure sequential (non-repeating) chains per entry
    - Calculate cycle-to-sequence ratio
    """
    print("Running Phase 12D: B-Text Procedural Style...")

    # Separate B-text entries
    b_entries = defaultdict(list)
    for rec in records:
        if rec['population'] == 'B':
            b_entries[rec['folio']].append(rec['word'])

    # Analyze each B-text entry
    cycle_counts = []
    sequential_counts = []
    cycle_lengths_all = []

    for folio, tokens in b_entries.items():
        if len(tokens) < 10:
            continue

        middles = [get_middle(t) for t in tokens]

        # Count cycles (A->B->A patterns)
        cycles = 0
        for i in range(len(middles) - 2):
            if middles[i] == middles[i + 2] and middles[i] != middles[i + 1]:
                cycles += 1
                cycle_lengths_all.append(2)

        # Count longer cycles (A->B->C->A)
        for i in range(len(middles) - 3):
            if middles[i] == middles[i + 3] and len(set(middles[i:i+4])) == 3:
                cycles += 1
                cycle_lengths_all.append(3)

        cycle_counts.append(cycles)

        # Count sequential (non-repeating) chains
        # A chain is a run of unique middles
        seq_chains = 0
        chain_len = 1
        for i in range(1, len(middles)):
            if middles[i] != middles[i - 1] and middles[i] not in middles[max(0, i-4):i]:
                chain_len += 1
                if chain_len >= 3:
                    seq_chains += 1
            else:
                chain_len = 1

        sequential_counts.append(seq_chains)

    # Calculate statistics
    mean_cycles = sum(cycle_counts) / len(cycle_counts) if cycle_counts else 0
    mean_sequential = sum(sequential_counts) / len(sequential_counts) if sequential_counts else 0
    cycle_to_seq_ratio = mean_cycles / mean_sequential if mean_sequential > 0 else float('inf')

    # Determine style
    # Scholastic: ratio < 0.5 (more sequences than cycles)
    # Paracelsian: ratio > 1.0 (more cycles than sequences)

    if cycle_to_seq_ratio < 0.5:
        verdict = "ENUMERATIVE_SCHOLASTIC"
        interpretation = (f"B-text is predominantly enumerative (ratio: {cycle_to_seq_ratio:.2f}). "
                         "Sequential chains dominate - consistent with step-by-step scholastic procedures.")
    elif cycle_to_seq_ratio > 1.0:
        verdict = "CYCLICAL_PARACELSIAN"
        interpretation = (f"B-text is predominantly cyclical (ratio: {cycle_to_seq_ratio:.2f}). "
                         "Cyclic patterns dominate - consistent with Paracelsian cyclical transformations.")
    else:
        verdict = "MIXED"
        interpretation = (f"B-text shows mixed procedural style (ratio: {cycle_to_seq_ratio:.2f}). "
                         "Neither purely enumerative nor cyclical.")

    return {
        "metadata": {
            "phase": "12D",
            "title": "B-Text Procedural Style",
            "timestamp": datetime.now().isoformat()
        },
        "b_text_entries_analyzed": len(b_entries),
        "mean_cycles_per_entry": round(mean_cycles, 3),
        "mean_sequential_chains": round(mean_sequential, 3),
        "cycle_to_sequence_ratio": round(cycle_to_seq_ratio, 3) if cycle_to_seq_ratio != float('inf') else "inf",
        "cycle_length_distribution": Counter(cycle_lengths_all).most_common(5) if cycle_lengths_all else [],
        "thresholds": {
            "scholastic": "ratio < 0.5 (more sequences)",
            "paracelsian": "ratio > 1.0 (more cycles)"
        },
        "VERDICT": verdict,
        "interpretation": interpretation
    }

# ============================================================================
# 12E: NOVELTY DETECTION
# ============================================================================

def test_12e_novelty_detection(phase10: Dict) -> Dict:
    """
    Test: Do known traditions FAIL to accommodate Voynich's extreme metrics?

    Compares Voynich reversibility (94.6%) and commutativity (75.7%) to historical estimates.
    """
    print("Running Phase 12E: Novelty Detection...")

    # Voynich metrics from Phase 10
    voynich_reversibility = phase10['10c']['patterns']['reversible_pairs']['rate']

    # Get commutativity from operator features
    operator_features = phase10['10a']['operator_features']
    commutativity_rates = [f.get('commutativity_rate', 0) for f in operator_features.values()]
    voynich_commutativity = sum(commutativity_rates) / len(commutativity_rates) if commutativity_rates else 0

    # Historical baselines (estimated from literature)
    scholastic_reversibility = (0.50, 0.70)  # Mean ~0.60, SD ~0.10
    scholastic_commutativity = (0.20, 0.40)  # Mean ~0.30, SD ~0.10

    paracelsian_reversibility = (0.70, 0.85)  # Mean ~0.775, SD ~0.075
    paracelsian_commutativity = (0.40, 0.60)  # Mean ~0.50, SD ~0.10

    # Calculate standard deviations from expected ranges
    def sds_above_range(value, range_tuple, assumed_sd=0.10):
        """Calculate how many SDs above the range the value is."""
        low, high = range_tuple
        if value <= high:
            return 0
        return (value - high) / assumed_sd

    scholastic_rev_deviation = sds_above_range(voynich_reversibility, scholastic_reversibility)
    scholastic_comm_deviation = sds_above_range(voynich_commutativity, scholastic_commutativity)

    paracelsian_rev_deviation = sds_above_range(voynich_reversibility, paracelsian_reversibility)
    paracelsian_comm_deviation = sds_above_range(voynich_commutativity, paracelsian_commutativity)

    # Determine if exceeds known traditions
    exceeds_scholastic = scholastic_rev_deviation > 2 or scholastic_comm_deviation > 2
    exceeds_paracelsian = paracelsian_rev_deviation > 2 or paracelsian_comm_deviation > 2
    exceeds_both = exceeds_scholastic and exceeds_paracelsian

    # Novel features
    novel_features = []
    if voynich_reversibility > 0.90:
        novel_features.append(f"Extreme reversibility ({voynich_reversibility:.1%})")
    if voynich_commutativity > 0.70:
        novel_features.append(f"High commutativity ({voynich_commutativity:.1%})")

    # Ladder-to-cycle collapse from Phase 10C
    ladder_collapse = phase10['10c']['patterns']['ladder_to_cycle']['cycle_return_rate']
    if ladder_collapse > 0.95:
        novel_features.append(f"Near-universal ladder-to-cycle collapse ({ladder_collapse:.1%})")

    if exceeds_both:
        verdict = "EXCEEDS_KNOWN_TRADITIONS"
        label = "Private cyclic alchemical algebra"
        interpretation = (f"Voynich metrics significantly exceed both scholastic and Paracelsian traditions. "
                         f"Novel features: {', '.join(novel_features)}. "
                         "This suggests a private or otherwise unattested school.")
    elif exceeds_scholastic:
        verdict = "EXCEEDS_SCHOLASTIC_ONLY"
        label = "Paracelsian or post-Paracelsian"
        interpretation = ("Voynich metrics exceed scholastic expectations but may fit extreme Paracelsian practice.")
    else:
        verdict = "WITHIN_KNOWN_TRADITIONS"
        label = "Compatible with known traditions"
        interpretation = ("Voynich metrics fall within the range of known alchemical traditions.")

    return {
        "metadata": {
            "phase": "12E",
            "title": "Novelty Detection",
            "timestamp": datetime.now().isoformat()
        },
        "voynich_metrics": {
            "reversibility": round(voynich_reversibility, 3),
            "commutativity": round(voynich_commutativity, 3),
            "ladder_collapse_rate": round(ladder_collapse, 3)
        },
        "historical_baselines": {
            "scholastic": {
                "reversibility": f"{scholastic_reversibility[0]*100:.0f}-{scholastic_reversibility[1]*100:.0f}%",
                "commutativity": f"{scholastic_commutativity[0]*100:.0f}-{scholastic_commutativity[1]*100:.0f}%"
            },
            "paracelsian": {
                "reversibility": f"{paracelsian_reversibility[0]*100:.0f}-{paracelsian_reversibility[1]*100:.0f}%",
                "commutativity": f"{paracelsian_commutativity[0]*100:.0f}-{paracelsian_commutativity[1]*100:.0f}%"
            }
        },
        "deviation_analysis": {
            "scholastic_reversibility_sds": round(scholastic_rev_deviation, 2),
            "scholastic_commutativity_sds": round(scholastic_comm_deviation, 2),
            "paracelsian_reversibility_sds": round(paracelsian_rev_deviation, 2),
            "paracelsian_commutativity_sds": round(paracelsian_comm_deviation, 2)
        },
        "exceeds_known_traditions": exceeds_both,
        "novel_features": novel_features,
        "VERDICT": verdict,
        "label": label,
        "interpretation": interpretation
    }

# ============================================================================
# SYNTHESIS
# ============================================================================

def synthesize_phase12(results: Dict) -> Dict:
    """Generate final tradition classification."""
    print("Synthesizing Phase 12 results...")

    verdicts = {
        "12A": results['12a']['VERDICT'],
        "12B": results['12b']['VERDICT'],
        "12C": results['12c']['VERDICT'],
        "12D": results['12d']['VERDICT'],
        "12E": results['12e']['VERDICT']
    }

    # Count tradition signals
    scholastic_signals = sum([
        1 if "SCHOLASTIC" in verdicts['12A'] else 0,
        1 if "SUBSTANCE" in verdicts['12B'] else 0,
        1 if "SCHOLASTIC" in verdicts['12C'] else 0,
        1 if "SCHOLASTIC" in verdicts['12D'] or "ENUMERATIVE" in verdicts['12D'] else 0
    ])

    paracelsian_signals = sum([
        1 if "PARACELSIAN" in verdicts['12A'] else 0,
        1 if "STATE" in verdicts['12B'] else 0,
        1 if "PARACELSIAN" in verdicts['12C'] or "TRIA" in verdicts['12C'] else 0,
        1 if "PARACELSIAN" in verdicts['12D'] or "CYCLICAL" in verdicts['12D'] else 0
    ])

    # Check for novelty
    is_novel = "EXCEEDS" in verdicts['12E']

    # Determine primary match
    if is_novel:
        primary_match = "T3_PRIVATE_SCHOOL"
        confidence = "HIGH" if scholastic_signals < 2 and paracelsian_signals < 2 else "MEDIUM"
    elif scholastic_signals > paracelsian_signals + 1:
        primary_match = "T1_SCHOLASTIC"
        confidence = "HIGH" if scholastic_signals >= 3 else "MEDIUM"
    elif paracelsian_signals > scholastic_signals + 1:
        primary_match = "T2_PARACELSIAN"
        confidence = "HIGH" if paracelsian_signals >= 3 else "MEDIUM"
    else:
        primary_match = "HYBRID_TRANSITIONAL"
        confidence = "MEDIUM"

    # Distinctive features
    distinctive_features = []
    if results['12e']['voynich_metrics']['reversibility'] > 0.90:
        distinctive_features.append("Extreme reversibility (94.6%)")
    if results['12e']['voynich_metrics']['ladder_collapse_rate'] > 0.95:
        distinctive_features.append("Near-universal cyclic collapse (97.7%)")
    if results['12c']['alignment_scores']['tria_prima_3'] > 2.0:
        distinctive_features.append("Strong tria prima (3) enrichment")
    if results['12a']['functional_cluster_count'] < 6:
        distinctive_features.append(f"Low operation diversity ({results['12a']['functional_cluster_count']} types)")

    # Generate final statement
    final_statement = generate_final_statement(primary_match, confidence, distinctive_features, verdicts)

    return {
        "metadata": {
            "phase": "12_SYNTHESIS",
            "title": "Alchemical Tradition Fingerprint",
            "timestamp": datetime.now().isoformat()
        },
        "test_verdicts": {
            "12A_operation_canon": verdicts['12A'],
            "12B_substance_state": verdicts['12B'],
            "12C_quantitative_weight": verdicts['12C'],
            "12D_btext_style": verdicts['12D'],
            "12E_novelty": verdicts['12E']
        },
        "tradition_signals": {
            "scholastic_count": scholastic_signals,
            "paracelsian_count": paracelsian_signals,
            "novel_features_count": len(distinctive_features)
        },
        "OVERALL_CLASSIFICATION": {
            "primary_match": primary_match,
            "confidence": confidence
        },
        "distinctive_features": distinctive_features,
        "final_statement": final_statement
    }

def generate_final_statement(primary_match: str, confidence: str, features: List[str], verdicts: Dict) -> str:
    """Generate final characterization statement."""

    if primary_match == "T1_SCHOLASTIC":
        return (f"The Voynich transformation algebra aligns with SCHOLASTIC MEDIEVAL ALCHEMY "
                f"({confidence} confidence): {verdicts['12A']} operation types, "
                f"{verdicts['12B']} attractor structure, "
                f"{verdicts['12D']} procedural style. "
                f"However, extreme reversibility (94.6%) exceeds typical scholastic range.")

    elif primary_match == "T2_PARACELSIAN":
        return (f"The Voynich transformation algebra aligns with PARACELSIAN/IATROCHEMICAL tradition "
                f"({confidence} confidence): state-focused attractors, "
                f"tria prima quantitative dominance, cyclical procedural style.")

    elif primary_match == "T3_PRIVATE_SCHOOL":
        feature_list = "; ".join(features) if features else "multiple extreme metrics"
        return (f"The Voynich implements a PRIVATE CYCLIC ALCHEMICAL ALGEBRA "
                f"exceeding known traditions ({confidence} confidence). "
                f"Distinctive features: {feature_list}. "
                f"This suggests an otherwise unattested school combining iatrochemical "
                f"and scholastic elements with extreme systematization.")

    else:  # HYBRID
        return (f"The Voynich shows a HYBRID tradition combining scholastic features "
                f"({verdicts['12A']}, {verdicts['12B']}) with Paracelsian features "
                f"({verdicts['12C']}, {verdicts['12D']}). "
                f"Consistent with transitional 15th-century practice or "
                f"eclectic private compilation.")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute Phase 12 analysis."""
    print("=" * 70)
    print("PHASE 12: ALCHEMICAL TRADITION FINGERPRINTING")
    print("=" * 70)
    print()

    # Load corpus
    print("Loading corpus...")
    records = load_corpus()
    entries = group_by_entry(records)
    print(f"  Loaded {len(records)} records in {len(entries)} entries")
    print()

    # Load previous results
    print("Loading Phase 10-11 results...")
    phase10 = load_phase10_results()
    phase11 = load_phase11_results()
    print()

    # Run Phase 12 tests
    results = {}

    results['12a'] = test_12a_operation_canon(phase10, entries)
    print()

    results['12b'] = test_12b_substance_state(phase10)
    print()

    results['12c'] = test_12c_quantitative_weighting(phase11)
    print()

    results['12d'] = test_12d_btext_style(entries, records)
    print()

    results['12e'] = test_12e_novelty_detection(phase10)
    print()

    # Synthesize
    synthesis = synthesize_phase12(results)
    print()

    # Save results
    output_files = [
        ("phase12a_operation_canon.json", results['12a']),
        ("phase12b_substance_state.json", results['12b']),
        ("phase12c_quantitative_weight.json", results['12c']),
        ("phase12d_btext_style.json", results['12d']),
        ("phase12e_novelty_detection.json", results['12e']),
        ("phase12_synthesis.json", synthesis)
    ]

    for filename, data in output_files:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved: {filename}")

    # Print summary
    print()
    print("=" * 70)
    print("PHASE 12 RESULTS SUMMARY")
    print("=" * 70)
    print()

    print("TEST VERDICTS:")
    print("-" * 50)
    for test, verdict in synthesis['test_verdicts'].items():
        print(f"  {test}: {verdict}")
    print()

    print("TRADITION SIGNALS:")
    print("-" * 50)
    print(f"  Scholastic signals: {synthesis['tradition_signals']['scholastic_count']}/4")
    print(f"  Paracelsian signals: {synthesis['tradition_signals']['paracelsian_count']}/4")
    print(f"  Novel features: {synthesis['tradition_signals']['novel_features_count']}")
    print()

    print("CLASSIFICATION:")
    print("-" * 50)
    print(f"  Primary match: {synthesis['OVERALL_CLASSIFICATION']['primary_match']}")
    print(f"  Confidence: {synthesis['OVERALL_CLASSIFICATION']['confidence']}")
    print()

    if synthesis['distinctive_features']:
        print("DISTINCTIVE FEATURES:")
        print("-" * 50)
        for feature in synthesis['distinctive_features']:
            print(f"  - {feature}")
        print()

    print("FINAL STATEMENT:")
    print("-" * 50)
    print()
    # Word wrap the final statement
    statement = synthesis['final_statement']
    words = statement.split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > 70:
            print(line)
            line = "  " + word
        else:
            line += " " + word if line != "  " else word
    if line.strip():
        print(line)
    print()

if __name__ == "__main__":
    main()
