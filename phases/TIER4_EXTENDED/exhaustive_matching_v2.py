"""
Phase 3 v2: Exhaustive Entity Matching with CORRECTED Regime Mapping
Tier 4 SPECULATIVE

Key insight: REGIME_4 = PRECISION OPERATIONS (not forbidden/dangerous)
- REGIME_1: Forgiving (high escape) - tolerant of variation
- REGIME_2: Simple (low CEI) - baseline procedures
- REGIME_3: Complex (high CEI) - multi-step operations
- REGIME_4: Constrained (low escape) - precision required
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
import random
import statistics

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# CORRECTED MAPPING based on structural analysis
def categorize_puff_chapter(chapter):
    """
    Map Puff chapter to expected Voynich regime based on PROCESSING NEEDS
    not material danger level
    """
    category = chapter.get('category', 'HERB')
    is_aromatic = chapter.get('aromatic', False)
    is_dangerous = chapter.get('dangerous', False)

    # Aromatics are volatile - tolerate gentle handling
    if is_aromatic:
        return 'REGIME_1'  # Forgiving

    # Map by processing needs
    if category in ['FLOWER', 'TREE_FLOWER', 'LEGUME_FLOWER']:
        return 'REGIME_1'  # Forgiving - volatile, gentle processing

    if category in ['FRUIT', 'BERRY', 'VEGETABLE']:
        return 'REGIME_2'  # Simple - basic extraction

    if category in ['ROOT', 'BULB', 'SHRUB']:
        return 'REGIME_3'  # Complex - need sustained heat, multi-step

    # Most other materials need precision
    # HERBs (non-aromatic), FERN, SUCCULENT, FUNGUS, etc.
    return 'REGIME_4'  # Constrained - precision required

# Expected metric ranges by regime (from structural analysis)
REGIME_EXPECTATIONS = {
    'REGIME_1': {'cei_range': (0.40, 0.60), 'escape_range': (0.15, 0.25), 'hazard_range': (0.55, 0.70)},
    'REGIME_2': {'cei_range': (0.30, 0.45), 'escape_range': (0.08, 0.15), 'hazard_range': (0.40, 0.55)},
    'REGIME_3': {'cei_range': (0.60, 0.80), 'escape_range': (0.12, 0.22), 'hazard_range': (0.55, 0.75)},
    'REGIME_4': {'cei_range': (0.45, 0.70), 'escape_range': (0.05, 0.15), 'hazard_range': (0.45, 0.65)},
}

def load_data():
    with open(RESULTS_DIR / "puff_83_chapters.json") as f:
        puff = json.load(f)

    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        profiles = json.load(f)

    # Extract B folios
    b_folios = []
    for folio_name, folio_data in profiles.get('profiles', {}).items():
        if isinstance(folio_data, dict) and folio_data.get('system') == 'B':
            b_metrics = folio_data.get('b_metrics', {})
            if b_metrics:
                b_folios.append({
                    'folio': folio_name,
                    'regime': b_metrics.get('regime'),
                    'cei': b_metrics.get('cei_total', 0),
                    'hazard': b_metrics.get('hazard_density', 0),
                    'escape': b_metrics.get('escape_density', 0),
                })

    return puff['chapters'], b_folios

def calculate_match_score(puff_chapter, voynich_folio):
    expected_regime = categorize_puff_chapter(puff_chapter)
    actual_regime = voynich_folio['regime']

    score = 0

    # Regime match (50 points)
    if actual_regime == expected_regime:
        score += 50
    elif actual_regime and expected_regime:
        regime_num = {'REGIME_1': 1, 'REGIME_2': 2, 'REGIME_3': 3, 'REGIME_4': 4}
        if abs(regime_num.get(actual_regime, 0) - regime_num.get(expected_regime, 0)) == 1:
            score += 25

    # Metric matches
    expected = REGIME_EXPECTATIONS.get(expected_regime, REGIME_EXPECTATIONS['REGIME_4'])

    # CEI match (20 points)
    cei_low, cei_high = expected['cei_range']
    if cei_low <= voynich_folio['cei'] <= cei_high:
        score += 20
    else:
        dist = min(abs(voynich_folio['cei'] - cei_low), abs(voynich_folio['cei'] - cei_high))
        score += max(0, 20 - dist * 50)

    # Escape match (15 points)
    esc_low, esc_high = expected['escape_range']
    if esc_low <= voynich_folio['escape'] <= esc_high:
        score += 15
    else:
        dist = min(abs(voynich_folio['escape'] - esc_low), abs(voynich_folio['escape'] - esc_high))
        score += max(0, 15 - dist * 100)

    # Hazard match (15 points)
    haz_low, haz_high = expected['hazard_range']
    if haz_low <= voynich_folio['hazard'] <= haz_high:
        score += 15
    else:
        dist = min(abs(voynich_folio['hazard'] - haz_low), abs(voynich_folio['hazard'] - haz_high))
        score += max(0, 15 - dist * 50)

    return min(score, 100), expected_regime

def greedy_assignment(puff_chapters, voynich_folios):
    # Compute all scores
    all_pairs = []
    for i, puff_ch in enumerate(puff_chapters):
        for j, voynich_f in enumerate(voynich_folios):
            score, expected = calculate_match_score(puff_ch, voynich_f)
            all_pairs.append((i, j, score, expected))

    # Sort by score
    all_pairs.sort(key=lambda x: -x[2])

    # Greedy 1:1 assignment
    assigned_puff = set()
    assigned_voynich = set()
    assignments = []

    for puff_idx, voynich_idx, score, expected in all_pairs:
        if puff_idx not in assigned_puff and voynich_idx not in assigned_voynich:
            assignments.append({
                'puff_chapter': puff_chapters[puff_idx].get('chapter'),
                'puff_german': puff_chapters[puff_idx].get('german'),
                'puff_category': puff_chapters[puff_idx].get('category'),
                'expected_regime': expected,
                'voynich_folio': voynich_folios[voynich_idx]['folio'],
                'actual_regime': voynich_folios[voynich_idx]['regime'],
                'score': score,
            })
            assigned_puff.add(puff_idx)
            assigned_voynich.add(voynich_idx)

    return assignments

def permutation_test(puff_chapters, voynich_folios, actual_assignments, n_perms=1000):
    actual_total = sum(a['score'] for a in actual_assignments)

    random_totals = []
    for _ in range(n_perms):
        shuffled_puff = puff_chapters.copy()
        random.shuffle(shuffled_puff)
        random_assignments = greedy_assignment(shuffled_puff, voynich_folios)
        random_totals.append(sum(a['score'] for a in random_assignments))

    p_value = (sum(1 for r in random_totals if r >= actual_total) + 1) / (n_perms + 1)
    z_score = (actual_total - statistics.mean(random_totals)) / statistics.stdev(random_totals) if statistics.stdev(random_totals) > 0 else 0

    return {
        'actual_total': actual_total,
        'random_mean': statistics.mean(random_totals),
        'random_std': statistics.stdev(random_totals),
        'p_value': p_value,
        'z_score': z_score,
    }

def main():
    print("=" * 60)
    print("PHASE 3 v2: CORRECTED REGIME MAPPING")
    print("[REGIME_4 = PRECISION, not FORBIDDEN]")
    print("=" * 60)

    puff_chapters, voynich_folios = load_data()

    print(f"\nPuff chapters: {len(puff_chapters)}")
    print(f"Voynich B folios: {len(voynich_folios)}")

    # Distribution check
    puff_expected = Counter()
    for ch in puff_chapters:
        puff_expected[categorize_puff_chapter(ch)] += 1

    voynich_actual = Counter(f['regime'] for f in voynich_folios)

    print("\n--- Distribution Comparison (CORRECTED MAPPING) ---")
    print(f"{'Regime':<12} {'Puff':<8} {'Voynich':<8} {'Ratio':<8}")
    print("-" * 40)
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        p = puff_expected[regime]
        v = voynich_actual[regime]
        ratio = p / v if v > 0 else float('inf')
        print(f"{regime:<12} {p:<8} {v:<8} {ratio:.2f}")

    # Run matching
    print("\n--- Running Greedy Assignment ---")
    assignments = greedy_assignment(puff_chapters, voynich_folios)

    scores = [a['score'] for a in assignments]
    print(f"Assignments: {len(assignments)}")
    print(f"Mean score: {statistics.mean(scores):.1f}")
    print(f"Median score: {statistics.median(scores):.1f}")

    strong = sum(1 for s in scores if s >= 60)
    moderate = sum(1 for s in scores if s >= 40)
    print(f"Strong (>=60): {strong} ({100*strong/len(scores):.1f}%)")
    print(f"Moderate (>=40): {moderate} ({100*moderate/len(scores):.1f}%)")

    # Permutation test
    print("\n--- Permutation Test (1000 shuffles) ---")
    perm = permutation_test(puff_chapters, voynich_folios, assignments, 1000)
    print(f"Actual total: {perm['actual_total']:.1f}")
    print(f"Random mean: {perm['random_mean']:.1f} +/- {perm['random_std']:.1f}")
    print(f"Z-score: {perm['z_score']:.2f}")
    print(f"P-value: {perm['p_value']:.4f}")

    # Regime match rates
    print("\n--- Regime Match Rates ---")
    by_expected = defaultdict(list)
    for a in assignments:
        by_expected[a['expected_regime']].append(a)

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        if by_expected[regime]:
            exact = sum(1 for a in by_expected[regime] if a['actual_regime'] == regime)
            total = len(by_expected[regime])
            print(f"  {regime}: {exact}/{total} ({100*exact/total:.1f}%)")

    # Results
    print("\n" + "=" * 60)
    test_a = perm['p_value'] < 0.05
    print(f"Test A (better than random): {'PASS' if test_a else 'FAIL'} (p={perm['p_value']:.4f})")

    regime_match_rates = {}
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        if by_expected[regime]:
            exact = sum(1 for a in by_expected[regime] if a['actual_regime'] == regime)
            regime_match_rates[regime] = exact / len(by_expected[regime])

    test_b = sum(1 for r in regime_match_rates.values() if r > 0.5) >= 2
    print(f"Test B (regime patterns): {'PASS' if test_b else 'FAIL'}")

    test_c = moderate / len(scores) > 0.6
    print(f"Test C (match quality): {'PASS' if test_c else 'FAIL'} ({100*moderate/len(scores):.0f}%)")

    passed = sum([test_a, test_b, test_c])
    overall = "PASS" if passed >= 2 else ("PARTIAL" if passed == 1 else "FAIL")
    print(f"\nOVERALL: {overall} ({passed}/3)")
    print("=" * 60)

    # Top matches
    print("\n--- Top 10 Matches ---")
    sorted_a = sorted(assignments, key=lambda x: -x['score'])
    for a in sorted_a[:10]:
        match_status = "EXACT" if a['expected_regime'] == a['actual_regime'] else "MISMATCH"
        print(f"  Ch.{a['puff_chapter']} ({a['puff_german'][:15]}) -> {a['voynich_folio']} "
              f"[{a['expected_regime'][:3]}->{a['actual_regime'][:3]}] {match_status} score={a['score']:.0f}")

    # Save
    output = {
        "tier": 4,
        "status": "HYPOTHETICAL",
        "test": "EXHAUSTIVE_MATCHING_V2",
        "mapping": "CORRECTED (REGIME_4=PRECISION)",
        "date": "2026-01-14",
        "distribution": {
            "puff_expected": dict(puff_expected),
            "voynich_actual": dict(voynich_actual),
        },
        "scores": {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "strong": strong,
            "moderate": moderate,
        },
        "permutation": perm,
        "regime_match_rates": regime_match_rates,
        "tests": {
            "test_a": test_a,
            "test_b": test_b,
            "test_c": test_c,
        },
        "overall": overall,
        "top_20_matches": sorted_a[:20],
    }

    with open(RESULTS_DIR / "puff_voynich_matching_v2.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/puff_voynich_matching_v2.json")

if __name__ == "__main__":
    main()
