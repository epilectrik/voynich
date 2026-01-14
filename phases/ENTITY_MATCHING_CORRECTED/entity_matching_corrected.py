"""
Phase: ENTITY_MATCHING_CORRECTED
Tier 3 SPECULATIVE - Re-run entity matching with curriculum-corrected mapping

CORRECTIONS FROM ORIGINAL (phases/TIER4_EXTENDED/exhaustive_entity_matching.py):
1. Degree-to-Regime mapping now based on CURRICULUM POSITION, not regime number
2. Uses PROPOSED folio order that recovers pedagogical structure
3. Compares results with and without corrections

Original mapping (WRONG):  {1: REGIME_1, 2: REGIME_2, 3: REGIME_3, 4: REGIME_4}
Corrected mapping:         {1: REGIME_2, 2: REGIME_1, 3: REGIME_3, 4: REGIME_4}

Why: Curriculum discovery showed REGIME_2=EARLY, REGIME_1=MIDDLE, REGIME_3=LATE
"""

import json
from pathlib import Path
from collections import defaultdict
import random
import statistics

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# ============================================================
# CORRECTED CURRICULUM-BASED MAPPING
# ============================================================

# Category -> Expected Brunschwig Degree (unchanged from original)
CATEGORY_TO_DEGREE = {
    # 1st degree (balneum) - gentle, volatile
    'FLOWER': 1,
    'TREE_FLOWER': 1,
    'LEGUME_FLOWER': 1,

    # 2nd degree (warm) - standard processing
    'HERB': 2,
    'FERN': 2,
    'SUCCULENT': 2,
    'VEGETABLE': 2,
    'VINE': 2,
    'TREE_LEAF': 2,
    'PARASITE': 2,

    # 3rd degree (seething) - intensive processing
    'ROOT': 3,
    'BULB': 3,
    'FRUIT': 3,
    'BERRY': 3,
    'SHRUB': 3,

    # 4th degree (forbidden/special) - dangerous or anomalous
    'FUNGUS': 4,
    'ANIMAL': 4,
    'OIL': 4,
    'SPIRIT': 4,
}

# CORRECTED: Degree -> Expected Voynich Regime based on CURRICULUM POSITION
# 1st degree (gentle/introductory) -> REGIME_2 (EARLY curriculum position)
# 2nd degree (standard/core) -> REGIME_1 (MIDDLE curriculum position)
# 3rd degree (intensive/advanced) -> REGIME_3 (LATE curriculum position)
# 4th degree (forbidden) -> REGIME_4 (excluded from normal curriculum)
DEGREE_TO_REGIME_CORRECTED = {
    1: 'REGIME_2',  # EARLY - gentle processing, low hazard
    2: 'REGIME_1',  # MIDDLE - standard processing, moderate hazard
    3: 'REGIME_3',  # LATE - intensive processing, high hazard
    4: 'REGIME_4',  # SPECIAL - precision-constrained
}

# ORIGINAL (for comparison): Based on regime NUMBER, not curriculum position
DEGREE_TO_REGIME_ORIGINAL = {
    1: 'REGIME_1',
    2: 'REGIME_2',
    3: 'REGIME_3',
    4: 'REGIME_4',
}

# Updated metric expectations based on curriculum analysis
DEGREE_EXPECTATIONS_CORRECTED = {
    1: {'cei_range': (0.30, 0.50), 'escape_range': (0.08, 0.18), 'hazard_range': (0.40, 0.55)},  # REGIME_2 metrics
    2: {'cei_range': (0.45, 0.60), 'escape_range': (0.10, 0.20), 'hazard_range': (0.55, 0.65)},  # REGIME_1 metrics
    3: {'cei_range': (0.60, 0.85), 'escape_range': (0.12, 0.22), 'hazard_range': (0.60, 0.75)},  # REGIME_3 metrics
    4: {'cei_range': (0.45, 0.70), 'escape_range': (0.05, 0.15), 'hazard_range': (0.50, 0.65)},  # REGIME_4 metrics
}

# ============================================================
# DATA LOADING
# ============================================================

def load_puff_chapters():
    """Load Puff chapter data with categories"""
    with open(RESULTS_DIR / "puff_83_chapters.json") as f:
        data = json.load(f)
    return data['chapters']

def load_voynich_folios():
    """Load Voynich B folio profiles"""
    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        data = json.load(f)

    b_folios = []
    profiles = data.get('profiles', data)
    for folio_name, folio_data in profiles.items():
        if isinstance(folio_data, dict) and folio_data.get('system') == 'B':
            b_metrics = folio_data.get('b_metrics', {})
            if b_metrics:
                b_folios.append({
                    'folio': folio_name,
                    'regime': b_metrics.get('regime'),
                    'cei': b_metrics.get('cei_total', 0),
                    'hazard': b_metrics.get('hazard_density', 0),
                    'escape': b_metrics.get('escape_density', 0),
                    'link': b_metrics.get('link_density', 0),
                    'intervention': b_metrics.get('intervention_frequency', 0),
                })
    return b_folios

def load_proposed_order():
    """Load proposed folio order from optimization"""
    order = []
    with open(RESULTS_DIR / "proposed_folio_order.txt") as f:
        for line in f:
            line = line.strip()
            if '|' in line and line[0].isdigit():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    pos = int(parts[0])
                    folio = parts[1]
                    order.append({'position': pos, 'folio': folio})
    return order

def reorder_folios(folios, proposed_order):
    """Reorder folios according to proposed curriculum order"""
    folio_map = {f['folio']: f for f in folios}
    reordered = []
    for item in proposed_order:
        folio_name = item['folio']
        if folio_name in folio_map:
            folio_data = folio_map[folio_name].copy()
            folio_data['curriculum_position'] = item['position']
            reordered.append(folio_data)
    return reordered

# ============================================================
# SIGNATURE BUILDING
# ============================================================

def build_puff_signature(chapter, use_corrected=True):
    """Build expected Voynich signature for a Puff chapter"""
    category = chapter.get('category', 'HERB')
    is_dangerous = chapter.get('dangerous', False)
    is_aromatic = chapter.get('aromatic', False)

    # Get base degree from category
    degree = CATEGORY_TO_DEGREE.get(category, 2)

    # Adjust for dangerous flag
    if is_dangerous:
        degree = max(degree, 3)

    # Get expected regime based on mapping choice
    if use_corrected:
        expected_regime = DEGREE_TO_REGIME_CORRECTED.get(degree, 'REGIME_1')
        expected = DEGREE_EXPECTATIONS_CORRECTED.get(degree, DEGREE_EXPECTATIONS_CORRECTED[2])
    else:
        expected_regime = DEGREE_TO_REGIME_ORIGINAL.get(degree, 'REGIME_2')
        # Use original expectations for comparison
        expected = {
            1: {'cei_range': (0.35, 0.55), 'escape_range': (0.15, 0.25), 'hazard_range': (0.50, 0.65)},
            2: {'cei_range': (0.30, 0.50), 'escape_range': (0.08, 0.15), 'hazard_range': (0.55, 0.65)},
            3: {'cei_range': (0.55, 0.80), 'escape_range': (0.12, 0.22), 'hazard_range': (0.55, 0.70)},
            4: {'cei_range': (0.45, 0.70), 'escape_range': (0.05, 0.15), 'hazard_range': (0.55, 0.70)},
        }.get(degree, {'cei_range': (0.30, 0.50), 'escape_range': (0.08, 0.15), 'hazard_range': (0.55, 0.65)})

    # Adjust for aromatic
    if is_aromatic and degree == 2:
        if use_corrected:
            expected = DEGREE_EXPECTATIONS_CORRECTED[1]
        degree = 1
        expected_regime = DEGREE_TO_REGIME_CORRECTED[1] if use_corrected else DEGREE_TO_REGIME_ORIGINAL[1]

    return {
        'chapter': chapter.get('chapter'),
        'german': chapter.get('german'),
        'category': category,
        'degree': degree,
        'expected_regime': expected_regime,
        'expected_cei': sum(expected['cei_range']) / 2,
        'expected_escape': sum(expected['escape_range']) / 2,
        'expected_hazard': sum(expected['hazard_range']) / 2,
        'cei_range': expected['cei_range'],
        'escape_range': expected['escape_range'],
        'hazard_range': expected['hazard_range'],
        'is_dangerous': is_dangerous,
        'is_aromatic': is_aromatic,
    }

# ============================================================
# MATCHING ALGORITHM
# ============================================================

def calculate_match_score(puff_sig, voynich_folio):
    """Calculate match score between Puff signature and Voynich folio"""
    score = 0
    max_score = 100

    # Regime match (40 points)
    expected_regime = puff_sig['expected_regime']
    actual_regime = voynich_folio['regime']

    if actual_regime == expected_regime:
        score += 40
    elif actual_regime and expected_regime:
        # Adjacent regime partial credit
        regime_num = {'REGIME_1': 1, 'REGIME_2': 2, 'REGIME_3': 3, 'REGIME_4': 4}
        expected_num = regime_num.get(expected_regime, 2)
        actual_num = regime_num.get(actual_regime, 2)
        if abs(expected_num - actual_num) == 1:
            score += 20

    # CEI match (20 points)
    cei_low, cei_high = puff_sig['cei_range']
    actual_cei = voynich_folio['cei']
    if cei_low <= actual_cei <= cei_high:
        score += 20
    else:
        if actual_cei < cei_low:
            dist = cei_low - actual_cei
        else:
            dist = actual_cei - cei_high
        score += max(0, 20 - dist * 50)

    # Escape density match (20 points)
    esc_low, esc_high = puff_sig['escape_range']
    actual_escape = voynich_folio['escape']
    if esc_low <= actual_escape <= esc_high:
        score += 20
    else:
        if actual_escape < esc_low:
            dist = esc_low - actual_escape
        else:
            dist = actual_escape - esc_high
        score += max(0, 20 - dist * 100)

    # Hazard density match (20 points)
    haz_low, haz_high = puff_sig['hazard_range']
    actual_hazard = voynich_folio['hazard']
    if haz_low <= actual_hazard <= haz_high:
        score += 20
    else:
        if actual_hazard < haz_low:
            dist = haz_low - actual_hazard
        else:
            dist = actual_hazard - haz_high
        score += max(0, 20 - dist * 50)

    return min(score, max_score)

def greedy_assignment(puff_signatures, voynich_folios):
    """Find greedy 1:1 assignment maximizing total score"""
    # Build match matrix
    n_puff = len(puff_signatures)
    n_voynich = len(voynich_folios)

    # Create list of all (puff_idx, voynich_idx, score) tuples
    all_pairs = []
    for i in range(n_puff):
        for j in range(n_voynich):
            score = calculate_match_score(puff_signatures[i], voynich_folios[j])
            all_pairs.append((i, j, score))

    # Sort by score descending
    all_pairs.sort(key=lambda x: -x[2])

    # Greedy assignment
    assigned_puff = set()
    assigned_voynich = set()
    assignments = []

    for puff_idx, voynich_idx, score in all_pairs:
        if puff_idx not in assigned_puff and voynich_idx not in assigned_voynich:
            assignments.append({
                'puff_chapter': puff_signatures[puff_idx]['chapter'],
                'puff_german': puff_signatures[puff_idx]['german'],
                'puff_category': puff_signatures[puff_idx]['category'],
                'puff_degree': puff_signatures[puff_idx]['degree'],
                'expected_regime': puff_signatures[puff_idx]['expected_regime'],
                'voynich_folio': voynich_folios[voynich_idx]['folio'],
                'actual_regime': voynich_folios[voynich_idx]['regime'],
                'curriculum_position': voynich_folios[voynich_idx].get('curriculum_position'),
                'score': score,
            })
            assigned_puff.add(puff_idx)
            assigned_voynich.add(voynich_idx)

    return assignments

def permutation_test(puff_signatures, voynich_folios, n_permutations=1000):
    """Test if actual assignment is better than random"""
    # Calculate actual greedy score
    assignments = greedy_assignment(puff_signatures, voynich_folios)
    actual_total = sum(a['score'] for a in assignments)

    # Permutation distribution
    random_totals = []
    for _ in range(n_permutations):
        shuffled_puff = puff_signatures.copy()
        random.shuffle(shuffled_puff)
        perm_assignments = greedy_assignment(shuffled_puff, voynich_folios)
        random_totals.append(sum(a['score'] for a in perm_assignments))

    # Calculate p-value
    better_count = sum(1 for r in random_totals if r >= actual_total)
    p_value = (better_count + 1) / (n_permutations + 1)

    return {
        'actual_total': actual_total,
        'random_mean': statistics.mean(random_totals),
        'random_std': statistics.stdev(random_totals) if len(random_totals) > 1 else 0,
        'p_value': p_value,
        'z_score': (actual_total - statistics.mean(random_totals)) / statistics.stdev(random_totals) if statistics.stdev(random_totals) > 0 else 0,
    }

# ============================================================
# PATTERN ANALYSIS
# ============================================================

def analyze_patterns(assignments):
    """Analyze category->regime and degree->position patterns"""
    # By expected regime
    by_expected = defaultdict(list)
    for a in assignments:
        by_expected[a['expected_regime']].append(a)

    regime_results = {}
    for regime, items in by_expected.items():
        matches = sum(1 for a in items if a['actual_regime'] == regime)
        regime_results[regime] = {
            'total': len(items),
            'exact_matches': matches,
            'match_rate': matches / len(items) if items else 0,
        }

    # By degree
    by_degree = defaultdict(list)
    for a in assignments:
        by_degree[a['puff_degree']].append(a)

    degree_results = {}
    for degree, items in by_degree.items():
        scores = [a['score'] for a in items]
        positions = [a['curriculum_position'] for a in items if a['curriculum_position']]
        degree_results[degree] = {
            'count': len(items),
            'mean_score': statistics.mean(scores) if scores else 0,
            'mean_position': statistics.mean(positions) if positions else 0,
        }

    # By category
    by_category = defaultdict(list)
    for a in assignments:
        by_category[a['puff_category']].append(a)

    category_results = {}
    for category, items in by_category.items():
        scores = [a['score'] for a in items]
        category_results[category] = {
            'count': len(items),
            'mean_score': statistics.mean(scores) if scores else 0,
        }

    return regime_results, degree_results, category_results

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("PHASE: ENTITY_MATCHING_CORRECTED")
    print("[TIER 3 SPECULATIVE]")
    print("=" * 70)
    print("\nCORRECTIONS APPLIED:")
    print("  1. Degree mapping: 1->REGIME_2, 2->REGIME_1, 3->REGIME_3 (curriculum-based)")
    print("  2. Folio order: Using proposed order from gradient optimization")
    print()

    # Load data
    print("--- Loading Data ---")
    puff_chapters = load_puff_chapters()
    voynich_folios = load_voynich_folios()
    proposed_order = load_proposed_order()

    print(f"Puff chapters: {len(puff_chapters)}")
    print(f"Voynich B folios: {len(voynich_folios)}")
    print(f"Proposed order positions: {len(proposed_order)}")

    # Reorder folios according to curriculum
    voynich_reordered = reorder_folios(voynich_folios, proposed_order)
    print(f"Folios with curriculum position: {len(voynich_reordered)}")

    # Build signatures with CORRECTED mapping
    print("\n--- Building Signatures (CORRECTED mapping) ---")
    puff_sigs_corrected = [build_puff_signature(ch, use_corrected=True) for ch in puff_chapters]

    # Count by degree
    degree_counts = defaultdict(int)
    for sig in puff_sigs_corrected:
        degree_counts[sig['degree']] += 1
    print(f"Puff by degree: {dict(degree_counts)}")

    # Show expected regime mapping
    print("\nCORRECTED degree->regime mapping:")
    for deg in [1, 2, 3, 4]:
        expected = DEGREE_TO_REGIME_CORRECTED[deg]
        count = degree_counts.get(deg, 0)
        print(f"  Degree {deg} ({count} herbs) -> {expected}")

    # Count Voynich by regime
    regime_counts = defaultdict(int)
    for f in voynich_reordered:
        regime_counts[f['regime']] += 1
    print(f"\nVoynich by regime: {dict(regime_counts)}")

    # Run CORRECTED matching
    print("\n" + "=" * 70)
    print("TEST 1: CORRECTED MAPPING + PROPOSED ORDER")
    print("=" * 70)

    assignments_corrected = greedy_assignment(puff_sigs_corrected, voynich_reordered)
    scores_corrected = [a['score'] for a in assignments_corrected]

    print(f"\nAssignments made: {len(assignments_corrected)}")
    print(f"Score range: {min(scores_corrected):.1f} - {max(scores_corrected):.1f}")
    print(f"Mean score: {statistics.mean(scores_corrected):.1f}")
    print(f"Median score: {statistics.median(scores_corrected):.1f}")

    strong_corrected = sum(1 for s in scores_corrected if s >= 60)
    moderate_corrected = sum(1 for s in scores_corrected if s >= 40)
    print(f"Strong matches (>=60): {strong_corrected} ({100*strong_corrected/len(scores_corrected):.1f}%)")
    print(f"Moderate matches (>=40): {moderate_corrected} ({100*moderate_corrected/len(scores_corrected):.1f}%)")

    # Permutation test
    print("\n--- Permutation Test (CORRECTED) ---")
    perm_corrected = permutation_test(puff_sigs_corrected, voynich_reordered, n_permutations=1000)
    print(f"Actual total score: {perm_corrected['actual_total']:.1f}")
    print(f"Random mean: {perm_corrected['random_mean']:.1f} +/- {perm_corrected['random_std']:.1f}")
    print(f"Z-score: {perm_corrected['z_score']:.2f}")
    print(f"P-value: {perm_corrected['p_value']:.4f}")

    # Pattern analysis
    regime_results, degree_results, category_results = analyze_patterns(assignments_corrected)

    print("\n--- Regime Match Rates (CORRECTED) ---")
    for regime in ['REGIME_2', 'REGIME_1', 'REGIME_3', 'REGIME_4']:
        if regime in regime_results:
            r = regime_results[regime]
            print(f"  {regime}: {r['exact_matches']}/{r['total']} ({100*r['match_rate']:.1f}%)")

    print("\n--- Degree -> Mean Position (curriculum order) ---")
    for deg in [1, 2, 3, 4]:
        if deg in degree_results:
            d = degree_results[deg]
            print(f"  Degree {deg}: mean position = {d['mean_position']:.1f}, mean score = {d['mean_score']:.1f}")

    # Run ORIGINAL mapping for comparison
    print("\n" + "=" * 70)
    print("TEST 2: ORIGINAL MAPPING (for comparison)")
    print("=" * 70)

    puff_sigs_original = [build_puff_signature(ch, use_corrected=False) for ch in puff_chapters]
    assignments_original = greedy_assignment(puff_sigs_original, voynich_reordered)
    scores_original = [a['score'] for a in assignments_original]

    print(f"\nMean score (original mapping): {statistics.mean(scores_original):.1f}")
    strong_original = sum(1 for s in scores_original if s >= 60)
    moderate_original = sum(1 for s in scores_original if s >= 40)
    print(f"Strong matches (>=60): {strong_original} ({100*strong_original/len(scores_original):.1f}%)")
    print(f"Moderate matches (>=40): {moderate_original} ({100*moderate_original/len(scores_original):.1f}%)")

    perm_original = permutation_test(puff_sigs_original, voynich_reordered, n_permutations=1000)
    print(f"P-value (original): {perm_original['p_value']:.4f}")

    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON: CORRECTED vs ORIGINAL")
    print("=" * 70)
    print(f"\n  Metric                | Original | Corrected | Improvement")
    print(f"  ----------------------|----------|-----------|------------")
    print(f"  Mean score            | {statistics.mean(scores_original):8.1f} | {statistics.mean(scores_corrected):9.1f} | {statistics.mean(scores_corrected) - statistics.mean(scores_original):+.1f}")
    print(f"  Strong matches (>=60) | {strong_original:8d} | {strong_corrected:9d} | {strong_corrected - strong_original:+d}")
    print(f"  Moderate matches      | {moderate_original:8d} | {moderate_corrected:9d} | {moderate_corrected - moderate_original:+d}")
    print(f"  Z-score               | {perm_original['z_score']:8.2f} | {perm_corrected['z_score']:9.2f} | {perm_corrected['z_score'] - perm_original['z_score']:+.2f}")
    print(f"  P-value               | {perm_original['p_value']:8.4f} | {perm_corrected['p_value']:9.4f} |")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    corrected_better = perm_corrected['z_score'] > perm_original['z_score']
    corrected_significant = perm_corrected['p_value'] < 0.05

    if corrected_better and corrected_significant:
        verdict = "CORRECTED MAPPING SIGNIFICANTLY BETTER"
    elif corrected_better:
        verdict = "CORRECTED MAPPING BETTER (not significant)"
    elif corrected_significant:
        verdict = "BOTH SIGNIFICANT (original better)"
    else:
        verdict = "NEITHER SIGNIFICANT"

    print(f"\n  {verdict}")

    # Save results
    output = {
        "phase": "ENTITY_MATCHING_CORRECTED",
        "tier": 3,
        "status": "SPECULATIVE",
        "date": "2026-01-14",
        "corrections_applied": [
            "Degree-to-regime mapping based on curriculum position",
            "Using proposed folio order from gradient optimization"
        ],
        "mapping_comparison": {
            "original": dict(DEGREE_TO_REGIME_ORIGINAL),
            "corrected": dict(DEGREE_TO_REGIME_CORRECTED),
        },
        "data_counts": {
            "puff_chapters": len(puff_chapters),
            "voynich_folios": len(voynich_reordered),
            "puff_by_degree": dict(degree_counts),
            "voynich_by_regime": dict(regime_counts),
        },
        "corrected_results": {
            "mean_score": statistics.mean(scores_corrected),
            "median_score": statistics.median(scores_corrected),
            "strong_matches": strong_corrected,
            "moderate_matches": moderate_corrected,
            "permutation_test": perm_corrected,
            "regime_match_rates": regime_results,
            "degree_positions": degree_results,
        },
        "original_results": {
            "mean_score": statistics.mean(scores_original),
            "strong_matches": strong_original,
            "moderate_matches": moderate_original,
            "permutation_test": perm_original,
        },
        "comparison": {
            "mean_score_improvement": statistics.mean(scores_corrected) - statistics.mean(scores_original),
            "strong_match_improvement": strong_corrected - strong_original,
            "z_score_improvement": perm_corrected['z_score'] - perm_original['z_score'],
            "corrected_better": corrected_better,
            "corrected_significant": corrected_significant,
        },
        "verdict": verdict,
        "top_assignments": assignments_corrected[:20],
        "interpretation": (
            f"Curriculum-corrected mapping {'shows' if corrected_significant else 'does not show'} significant improvement. "
            f"Z-score improved from {perm_original['z_score']:.2f} to {perm_corrected['z_score']:.2f}. "
            f"This {'supports' if corrected_better and corrected_significant else 'does not support'} the curriculum hypothesis."
        )
    }

    output_path = RESULTS_DIR / "entity_matching_corrected.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")

    # Show top matches
    print("\n--- Top 10 Matches (CORRECTED) ---")
    sorted_assignments = sorted(assignments_corrected, key=lambda x: -x['score'])
    for a in sorted_assignments[:10]:
        pos_str = f"pos={a['curriculum_position']}" if a['curriculum_position'] else ""
        print(f"  Ch.{a['puff_chapter']} ({a['puff_german'][:15]}) D{a['puff_degree']} -> {a['voynich_folio']} "
              f"[{a['expected_regime']} -> {a['actual_regime']}] score={a['score']} {pos_str}")

    return verdict

if __name__ == "__main__":
    main()
