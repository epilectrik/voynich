"""
Phase 3: Exhaustive Puff-Voynich Entity Matching
Tier 4 SPECULATIVE - Test 1:1 correspondence between Puff chapters and Voynich B folios

Tests whether individual Puff chapters can be matched to individual Voynich B folios
using Brunschwig's procedural framework as a bridge.
"""

import json
from pathlib import Path
from collections import defaultdict
import random
import statistics

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# ============================================================
# BRUNSCHWIG DEGREE MAPPING
# ============================================================

# Category -> Expected Brunschwig Degree
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

# Degree -> Expected Voynich Regime
DEGREE_TO_REGIME = {
    1: 'REGIME_1',
    2: 'REGIME_2',
    3: 'REGIME_3',
    4: 'REGIME_4',
}

# Degree -> Expected metrics (approximate ranges)
DEGREE_EXPECTATIONS = {
    1: {'cei_range': (0.35, 0.55), 'escape_range': (0.15, 0.25), 'hazard_range': (0.50, 0.65)},
    2: {'cei_range': (0.30, 0.50), 'escape_range': (0.08, 0.15), 'hazard_range': (0.55, 0.65)},
    3: {'cei_range': (0.55, 0.80), 'escape_range': (0.12, 0.22), 'hazard_range': (0.55, 0.70)},
    4: {'cei_range': (0.45, 0.70), 'escape_range': (0.05, 0.15), 'hazard_range': (0.55, 0.70)},
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

    # Extract only B folios from 'profiles' key
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

# ============================================================
# SIGNATURE BUILDING
# ============================================================

def build_puff_signature(chapter):
    """Build expected Voynich signature for a Puff chapter"""
    category = chapter.get('category', 'HERB')
    is_dangerous = chapter.get('dangerous', False)
    is_aromatic = chapter.get('aromatic', False)

    # Get base degree from category
    degree = CATEGORY_TO_DEGREE.get(category, 2)

    # Adjust for dangerous flag
    if is_dangerous:
        degree = max(degree, 3)  # At least 3rd degree

    # Get expected metrics
    expected = DEGREE_EXPECTATIONS.get(degree, DEGREE_EXPECTATIONS[2])

    # Adjust for aromatic (higher volatility = degree 1 characteristics)
    if is_aromatic and degree == 2:
        expected = DEGREE_EXPECTATIONS[1]  # Treat aromatics like flowers

    return {
        'chapter': chapter.get('chapter'),
        'german': chapter.get('german'),
        'category': category,
        'degree': degree,
        'expected_regime': DEGREE_TO_REGIME.get(degree, 'REGIME_2'),
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
        # Partial credit for adjacent regimes
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
        # Partial credit based on distance
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

def compute_match_matrix(puff_signatures, voynich_folios):
    """Compute full match score matrix"""
    n_puff = len(puff_signatures)
    n_voynich = len(voynich_folios)

    matrix = []
    for puff_sig in puff_signatures:
        row = []
        for voynich_folio in voynich_folios:
            score = calculate_match_score(puff_sig, voynich_folio)
            row.append(score)
        matrix.append(row)

    return matrix

def greedy_assignment(matrix, puff_signatures, voynich_folios):
    """Find greedy 1:1 assignment maximizing total score"""
    n_puff = len(matrix)
    n_voynich = len(matrix[0]) if matrix else 0

    # Create list of all (puff_idx, voynich_idx, score) tuples
    all_pairs = []
    for i in range(n_puff):
        for j in range(n_voynich):
            all_pairs.append((i, j, matrix[i][j]))

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
                'expected_regime': puff_signatures[puff_idx]['expected_regime'],
                'voynich_folio': voynich_folios[voynich_idx]['folio'],
                'actual_regime': voynich_folios[voynich_idx]['regime'],
                'score': score,
            })
            assigned_puff.add(puff_idx)
            assigned_voynich.add(voynich_idx)

    return assignments

# ============================================================
# PERMUTATION TEST
# ============================================================

def permutation_test(matrix, n_permutations=1000):
    """Test if actual assignment is better than random"""
    n_puff = len(matrix)
    n_voynich = len(matrix[0]) if matrix else 0

    # Calculate actual score using greedy diagonal
    actual_scores = []
    for i in range(min(n_puff, n_voynich)):
        actual_scores.append(matrix[i][i] if i < n_voynich else 0)
    actual_total = sum(actual_scores)

    # More sophisticated: use the greedy assignment score
    assignments = []
    assigned_voynich = set()
    for i in range(n_puff):
        best_score = -1
        best_j = -1
        for j in range(n_voynich):
            if j not in assigned_voynich and matrix[i][j] > best_score:
                best_score = matrix[i][j]
                best_j = j
        if best_j >= 0:
            assigned_voynich.add(best_j)
            assignments.append(best_score)
    actual_greedy_total = sum(assignments)

    # Permutation distribution
    random_totals = []
    for _ in range(n_permutations):
        # Shuffle puff indices
        puff_order = list(range(n_puff))
        random.shuffle(puff_order)

        # Compute greedy assignment with shuffled puff
        assigned_voynich = set()
        perm_scores = []
        for i in puff_order:
            best_score = -1
            best_j = -1
            for j in range(n_voynich):
                if j not in assigned_voynich and matrix[i][j] > best_score:
                    best_score = matrix[i][j]
                    best_j = j
            if best_j >= 0:
                assigned_voynich.add(best_j)
                perm_scores.append(best_score)
        random_totals.append(sum(perm_scores))

    # Calculate p-value
    better_count = sum(1 for r in random_totals if r >= actual_greedy_total)
    p_value = (better_count + 1) / (n_permutations + 1)

    return {
        'actual_total': actual_greedy_total,
        'random_mean': statistics.mean(random_totals),
        'random_std': statistics.stdev(random_totals) if len(random_totals) > 1 else 0,
        'p_value': p_value,
        'z_score': (actual_greedy_total - statistics.mean(random_totals)) / statistics.stdev(random_totals) if statistics.stdev(random_totals) > 0 else 0,
    }

# ============================================================
# PATTERN ANALYSIS
# ============================================================

def analyze_patterns(assignments):
    """Analyze category->regime patterns"""
    # Group by expected regime
    by_expected = defaultdict(list)
    for a in assignments:
        by_expected[a['expected_regime']].append(a)

    # Calculate match rates
    pattern_results = {}
    for regime, items in by_expected.items():
        matches = sum(1 for a in items if a['actual_regime'] == regime)
        adjacent = sum(1 for a in items if a['actual_regime'] != regime and a['score'] >= 40)
        pattern_results[regime] = {
            'total': len(items),
            'exact_matches': matches,
            'match_rate': matches / len(items) if items else 0,
            'adjacent_matches': adjacent,
        }

    # Category-level analysis
    by_category = defaultdict(list)
    for a in assignments:
        by_category[a['puff_category']].append(a)

    category_results = {}
    for category, items in by_category.items():
        scores = [a['score'] for a in items]
        category_results[category] = {
            'count': len(items),
            'mean_score': statistics.mean(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
        }

    return pattern_results, category_results

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("PHASE 3: EXHAUSTIVE ENTITY MATCHING")
    print("[TIER 4 SPECULATIVE]")
    print("=" * 60)

    # Load data
    print("\n--- Loading Data ---")
    puff_chapters = load_puff_chapters()
    voynich_folios = load_voynich_folios()

    print(f"Puff chapters: {len(puff_chapters)}")
    print(f"Voynich B folios: {len(voynich_folios)}")

    # Build signatures
    print("\n--- Building Signatures ---")
    puff_signatures = [build_puff_signature(ch) for ch in puff_chapters]

    # Count by degree
    degree_counts = defaultdict(int)
    for sig in puff_signatures:
        degree_counts[sig['degree']] += 1
    print(f"Puff by degree: {dict(degree_counts)}")

    # Count Voynich by regime
    regime_counts = defaultdict(int)
    for f in voynich_folios:
        regime_counts[f['regime']] += 1
    print(f"Voynich by regime: {dict(regime_counts)}")

    # Compute match matrix
    print("\n--- Computing Match Matrix ---")
    matrix = compute_match_matrix(puff_signatures, voynich_folios)
    print(f"Matrix size: {len(matrix)} x {len(matrix[0]) if matrix else 0}")

    # Find optimal assignment
    print("\n--- Finding Optimal Assignment ---")
    assignments = greedy_assignment(matrix, puff_signatures, voynich_folios)
    print(f"Assignments made: {len(assignments)}")

    # Score distribution
    scores = [a['score'] for a in assignments]
    print(f"Score range: {min(scores):.1f} - {max(scores):.1f}")
    print(f"Mean score: {statistics.mean(scores):.1f}")
    print(f"Median score: {statistics.median(scores):.1f}")

    strong_matches = sum(1 for s in scores if s >= 60)
    moderate_matches = sum(1 for s in scores if s >= 40)
    print(f"Strong matches (>=60): {strong_matches} ({100*strong_matches/len(scores):.1f}%)")
    print(f"Moderate matches (>=40): {moderate_matches} ({100*moderate_matches/len(scores):.1f}%)")

    # Permutation test
    print("\n--- Permutation Test ---")
    perm_results = permutation_test(matrix, n_permutations=1000)
    print(f"Actual total score: {perm_results['actual_total']:.1f}")
    print(f"Random mean: {perm_results['random_mean']:.1f} +/- {perm_results['random_std']:.1f}")
    print(f"Z-score: {perm_results['z_score']:.2f}")
    print(f"P-value: {perm_results['p_value']:.4f}")

    # Pattern analysis
    print("\n--- Pattern Analysis ---")
    pattern_results, category_results = analyze_patterns(assignments)

    print("\nRegime match rates:")
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        if regime in pattern_results:
            r = pattern_results[regime]
            print(f"  {regime}: {r['exact_matches']}/{r['total']} ({100*r['match_rate']:.1f}%)")

    print("\nCategory scores:")
    for cat in sorted(category_results.keys()):
        c = category_results[cat]
        print(f"  {cat}: mean={c['mean_score']:.1f}, n={c['count']}")

    # Determine pass/fail
    print("\n" + "=" * 60)

    # Test A: Better than random?
    test_a = perm_results['p_value'] < 0.05
    print(f"Test A (better than random): {'PASS' if test_a else 'FAIL'} (p={perm_results['p_value']:.4f})")

    # Test B: Category->regime patterns?
    regime_1_rate = pattern_results.get('REGIME_1', {}).get('match_rate', 0)
    regime_3_rate = pattern_results.get('REGIME_3', {}).get('match_rate', 0)
    test_b = regime_1_rate > 0.5 or regime_3_rate > 0.5
    print(f"Test B (category patterns): {'PASS' if test_b else 'FAIL'} (R1={100*regime_1_rate:.0f}%, R3={100*regime_3_rate:.0f}%)")

    # Test C: Match quality?
    test_c = moderate_matches / len(scores) > 0.6 if scores else False
    print(f"Test C (match quality): {'PASS' if test_c else 'FAIL'} ({100*moderate_matches/len(scores):.0f}% >= 40)")

    # Overall
    passed = sum([test_a, test_b, test_c])
    overall = "PASS" if passed >= 2 else ("PARTIAL" if passed >= 1 else "FAIL")
    print(f"\nOVERALL: {overall} ({passed}/3 tests)")
    print("=" * 60)

    # Save results
    output = {
        "tier": 4,
        "status": "HYPOTHETICAL",
        "test": "EXHAUSTIVE_ENTITY_MATCHING",
        "date": "2026-01-14",
        "warning": "PURE SPECULATION - Model frozen",
        "counts": {
            "puff_chapters": len(puff_chapters),
            "voynich_folios": len(voynich_folios),
            "assignments": len(assignments),
        },
        "puff_by_degree": dict(degree_counts),
        "voynich_by_regime": dict(regime_counts),
        "score_distribution": {
            "min": min(scores),
            "max": max(scores),
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "strong_matches": strong_matches,
            "moderate_matches": moderate_matches,
        },
        "permutation_test": perm_results,
        "pattern_results": pattern_results,
        "category_results": category_results,
        "tests": {
            "test_a_better_than_random": test_a,
            "test_b_category_patterns": test_b,
            "test_c_match_quality": test_c,
        },
        "overall": overall,
        "assignments": assignments[:20],  # Top 20 for inspection
        "interpretation": (
            f"[TIER 4] Entity matching {'shows' if passed >= 2 else 'does not show'} significant correspondence. "
            f"P-value {perm_results['p_value']:.4f} ({'significant' if test_a else 'not significant'}). "
            f"{moderate_matches}/{len(scores)} matches scored >=40."
        )
    }

    with open(RESULTS_DIR / "puff_voynich_entity_matching.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/puff_voynich_entity_matching.json")

    # Show top matches
    print("\n--- Top 10 Matches ---")
    sorted_assignments = sorted(assignments, key=lambda x: -x['score'])
    for a in sorted_assignments[:10]:
        print(f"  Ch.{a['puff_chapter']} ({a['puff_german'][:20]}) -> {a['voynich_folio']} "
              f"[{a['expected_regime']} -> {a['actual_regime']}] score={a['score']}")

    print("\n--- Worst 10 Matches ---")
    for a in sorted_assignments[-10:]:
        print(f"  Ch.{a['puff_chapter']} ({a['puff_german'][:20]}) -> {a['voynich_folio']} "
              f"[{a['expected_regime']} -> {a['actual_regime']}] score={a['score']}")

    return overall

if __name__ == "__main__":
    main()
