"""
Phase: ENTITY_MATCHING_CORRECTED - Skip Alignment Test
Tier 3 SPECULATIVE

Tests whether allowing gaps/skips in the Puff-Voynich alignment produces
significantly better matching than strict 1:1 correspondence.

Uses dynamic programming (similar to sequence alignment) with gap penalties
to find optimal alignment between Puff chapters and Voynich folios.
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics
from scipy import stats
import numpy as np

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# Curriculum-corrected mapping
CATEGORY_TO_DEGREE = {
    'FLOWER': 1, 'TREE_FLOWER': 1, 'LEGUME_FLOWER': 1,
    'HERB': 2, 'FERN': 2, 'SUCCULENT': 2, 'VEGETABLE': 2,
    'VINE': 2, 'TREE_LEAF': 2, 'PARASITE': 2,
    'ROOT': 3, 'BULB': 3, 'FRUIT': 3, 'BERRY': 3, 'SHRUB': 3,
    'FUNGUS': 4, 'ANIMAL': 4, 'OIL': 4, 'SPIRIT': 4,
}

DEGREE_TO_REGIME = {
    1: 'REGIME_2',  # EARLY
    2: 'REGIME_1',  # MIDDLE
    3: 'REGIME_3',  # LATE
    4: 'REGIME_4',  # SPECIAL
}

def load_data():
    """Load Puff chapters and Voynich folios in proposed order"""
    with open(RESULTS_DIR / "puff_83_chapters.json") as f:
        puff_data = json.load(f)
    puff_chapters = puff_data['chapters']

    # Load proposed order
    order_data = []
    with open(RESULTS_DIR / "proposed_folio_order.txt") as f:
        for line in f:
            line = line.strip()
            if '|' in line and line[0].isdigit():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    order_data.append({
                        'position': int(parts[0]),
                        'folio': parts[1],
                        'regime': parts[2],
                        'hazard': float(parts[4]) if parts[4] else 0,
                        'cei': float(parts[5]) if len(parts) > 5 and parts[5] else 0,
                    })

    return puff_chapters, order_data

def get_puff_degree(chapter):
    """Get Brunschwig degree for a Puff chapter"""
    category = chapter.get('category', 'HERB')
    is_dangerous = chapter.get('dangerous', False)
    degree = CATEGORY_TO_DEGREE.get(category, 2)
    if is_dangerous:
        degree = max(degree, 3)
    return degree

def match_score(puff_chapter, voynich_folio):
    """Calculate match score between a Puff chapter and Voynich folio"""
    degree = get_puff_degree(puff_chapter)
    expected_regime = DEGREE_TO_REGIME.get(degree, 'REGIME_1')
    actual_regime = voynich_folio['regime']

    # Base score from regime match
    if actual_regime == expected_regime:
        score = 10
    else:
        # Partial credit for adjacent
        regime_order = ['REGIME_2', 'REGIME_1', 'REGIME_3', 'REGIME_4']
        if expected_regime in regime_order and actual_regime in regime_order:
            exp_idx = regime_order.index(expected_regime)
            act_idx = regime_order.index(actual_regime)
            if abs(exp_idx - act_idx) == 1:
                score = 5
            else:
                score = 2
        else:
            score = 2

    return score

def needleman_wunsch(puff_chapters, voynich_folios, gap_penalty=-2):
    """
    Needleman-Wunsch global alignment algorithm.
    Returns alignment score and the aligned sequences with gaps.
    """
    n = len(puff_chapters)
    m = len(voynich_folios)

    # Initialize scoring matrix
    score_matrix = np.zeros((n + 1, m + 1))
    traceback = np.zeros((n + 1, m + 1), dtype=int)  # 0=diag, 1=up, 2=left

    # Initialize first row and column with gap penalties
    for i in range(1, n + 1):
        score_matrix[i, 0] = i * gap_penalty
        traceback[i, 0] = 1  # up
    for j in range(1, m + 1):
        score_matrix[0, j] = j * gap_penalty
        traceback[0, j] = 2  # left

    # Fill the matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = score_matrix[i-1, j-1] + match_score(puff_chapters[i-1], voynich_folios[j-1])
            delete = score_matrix[i-1, j] + gap_penalty  # gap in voynich
            insert = score_matrix[i, j-1] + gap_penalty  # gap in puff

            score_matrix[i, j] = max(match, delete, insert)

            if score_matrix[i, j] == match:
                traceback[i, j] = 0
            elif score_matrix[i, j] == delete:
                traceback[i, j] = 1
            else:
                traceback[i, j] = 2

    # Traceback to get alignment
    aligned_puff = []
    aligned_voynich = []
    i, j = n, m

    while i > 0 or j > 0:
        if i > 0 and j > 0 and traceback[i, j] == 0:
            aligned_puff.append(puff_chapters[i-1])
            aligned_voynich.append(voynich_folios[j-1])
            i -= 1
            j -= 1
        elif i > 0 and traceback[i, j] == 1:
            aligned_puff.append(puff_chapters[i-1])
            aligned_voynich.append(None)  # gap
            i -= 1
        else:
            aligned_puff.append(None)  # gap
            aligned_voynich.append(voynich_folios[j-1])
            j -= 1

    aligned_puff.reverse()
    aligned_voynich.reverse()

    return score_matrix[n, m], aligned_puff, aligned_voynich

def analyze_alignment(aligned_puff, aligned_voynich):
    """Analyze the alignment to find gaps and matches"""
    puff_gaps = 0
    voynich_gaps = 0
    matches = 0
    exact_regime_matches = 0
    adjacent_matches = 0

    alignment_details = []

    for i, (p, v) in enumerate(zip(aligned_puff, aligned_voynich)):
        if p is None:
            puff_gaps += 1
            alignment_details.append({
                'position': i + 1,
                'puff': None,
                'voynich': v['folio'] if v else None,
                'type': 'PUFF_GAP'
            })
        elif v is None:
            voynich_gaps += 1
            alignment_details.append({
                'position': i + 1,
                'puff': p.get('chapter'),
                'voynich': None,
                'type': 'VOYNICH_GAP'
            })
        else:
            matches += 1
            degree = get_puff_degree(p)
            expected = DEGREE_TO_REGIME.get(degree, 'REGIME_1')
            actual = v['regime']

            if expected == actual:
                exact_regime_matches += 1
                match_type = 'EXACT'
            else:
                regime_order = ['REGIME_2', 'REGIME_1', 'REGIME_3', 'REGIME_4']
                if expected in regime_order and actual in regime_order:
                    if abs(regime_order.index(expected) - regime_order.index(actual)) == 1:
                        adjacent_matches += 1
                        match_type = 'ADJACENT'
                    else:
                        match_type = 'DISTANT'
                else:
                    match_type = 'DISTANT'

            alignment_details.append({
                'position': i + 1,
                'puff': p.get('chapter'),
                'puff_german': p.get('german', '')[:20],
                'puff_degree': degree,
                'voynich': v['folio'],
                'voynich_regime': actual,
                'expected_regime': expected,
                'type': match_type
            })

    return {
        'total_positions': len(aligned_puff),
        'matches': matches,
        'puff_gaps': puff_gaps,
        'voynich_gaps': voynich_gaps,
        'exact_regime_matches': exact_regime_matches,
        'adjacent_matches': adjacent_matches,
        'exact_rate': exact_regime_matches / matches if matches > 0 else 0,
        'details': alignment_details
    }

def strict_alignment_score(puff_chapters, voynich_folios):
    """Calculate score for strict 1:1 alignment (no gaps)"""
    n = min(len(puff_chapters), len(voynich_folios))
    total_score = 0
    exact_matches = 0
    adjacent_matches = 0

    for i in range(n):
        score = match_score(puff_chapters[i], voynich_folios[i])
        total_score += score

        degree = get_puff_degree(puff_chapters[i])
        expected = DEGREE_TO_REGIME.get(degree, 'REGIME_1')
        actual = voynich_folios[i]['regime']

        if expected == actual:
            exact_matches += 1
        else:
            regime_order = ['REGIME_2', 'REGIME_1', 'REGIME_3', 'REGIME_4']
            if expected in regime_order and actual in regime_order:
                if abs(regime_order.index(expected) - regime_order.index(actual)) == 1:
                    adjacent_matches += 1

    return {
        'total_score': total_score,
        'matches': n,
        'exact_regime_matches': exact_matches,
        'adjacent_matches': adjacent_matches,
        'exact_rate': exact_matches / n if n > 0 else 0,
    }

def test_gap_penalties(puff_chapters, voynich_folios):
    """Test different gap penalties to find optimal"""
    results = []
    for gap_penalty in [-1, -2, -3, -4, -5, -6, -8, -10]:
        score, aligned_p, aligned_v = needleman_wunsch(puff_chapters, voynich_folios, gap_penalty)
        analysis = analyze_alignment(aligned_p, aligned_v)
        results.append({
            'gap_penalty': gap_penalty,
            'score': score,
            'puff_gaps': analysis['puff_gaps'],
            'voynich_gaps': analysis['voynich_gaps'],
            'exact_rate': analysis['exact_rate'],
            'matches': analysis['matches'],
        })
    return results

def main():
    print("=" * 70)
    print("SKIP ALIGNMENT TEST")
    print("[TIER 3 SPECULATIVE]")
    print("=" * 70)
    print("\nTests whether allowing gaps improves Puff-Voynich alignment")
    print()

    # Load data
    print("--- Loading Data ---")
    puff_chapters, voynich_folios = load_data()
    print(f"Puff chapters: {len(puff_chapters)}")
    print(f"Voynich folios (proposed order): {len(voynich_folios)}")

    # Strict 1:1 alignment (baseline)
    print("\n--- Strict 1:1 Alignment (Baseline) ---")
    strict = strict_alignment_score(puff_chapters, voynich_folios)
    print(f"Total score: {strict['total_score']}")
    print(f"Matches: {strict['matches']}")
    print(f"Exact regime matches: {strict['exact_regime_matches']} ({100*strict['exact_rate']:.1f}%)")
    print(f"Adjacent matches: {strict['adjacent_matches']}")

    # Test different gap penalties
    print("\n--- Gap Penalty Optimization ---")
    gap_results = test_gap_penalties(puff_chapters, voynich_folios)

    print(f"\n  Gap Penalty | Score   | Puff Gaps | Voynich Gaps | Exact Rate | Matches")
    print(f"  ------------|---------|-----------|--------------|------------|--------")
    for r in gap_results:
        print(f"  {r['gap_penalty']:11d} | {r['score']:7.0f} | {r['puff_gaps']:9d} | {r['voynich_gaps']:12d} | {100*r['exact_rate']:9.1f}% | {r['matches']}")

    # Find best gap penalty
    best = max(gap_results, key=lambda x: x['exact_rate'])
    print(f"\n  Best gap penalty: {best['gap_penalty']} (exact rate: {100*best['exact_rate']:.1f}%)")

    # Run optimal alignment
    print("\n--- Optimal Skip Alignment ---")
    opt_score, aligned_puff, aligned_voynich = needleman_wunsch(
        puff_chapters, voynich_folios, gap_penalty=best['gap_penalty']
    )
    opt_analysis = analyze_alignment(aligned_puff, aligned_voynich)

    print(f"Total score: {opt_score:.0f}")
    print(f"Alignment length: {opt_analysis['total_positions']}")
    print(f"Matched pairs: {opt_analysis['matches']}")
    print(f"Puff gaps (skipped chapters): {opt_analysis['puff_gaps']}")
    print(f"Voynich gaps (skipped folios): {opt_analysis['voynich_gaps']}")
    print(f"Exact regime matches: {opt_analysis['exact_regime_matches']} ({100*opt_analysis['exact_rate']:.1f}%)")
    print(f"Adjacent matches: {opt_analysis['adjacent_matches']}")

    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON: STRICT vs SKIP ALIGNMENT")
    print("=" * 70)

    improvement = opt_analysis['exact_rate'] - strict['exact_rate']
    print(f"\n  Metric              | Strict 1:1 | Skip Align | Change")
    print(f"  --------------------|------------|------------|-------")
    print(f"  Exact regime rate   | {100*strict['exact_rate']:9.1f}% | {100*opt_analysis['exact_rate']:9.1f}% | {100*improvement:+.1f}%")
    print(f"  Total matches       | {strict['matches']:10d} | {opt_analysis['matches']:10d} | {opt_analysis['matches'] - strict['matches']:+d}")

    # Identify skipped items
    print("\n--- Skipped Puff Chapters ---")
    skipped_puff = [d for d in opt_analysis['details'] if d['type'] == 'VOYNICH_GAP']
    if skipped_puff:
        for s in skipped_puff[:10]:
            print(f"  Ch.{s['puff']} skipped (no Voynich match)")
        if len(skipped_puff) > 10:
            print(f"  ... and {len(skipped_puff) - 10} more")
    else:
        print("  None")

    print("\n--- Skipped Voynich Folios ---")
    skipped_voynich = [d for d in opt_analysis['details'] if d['type'] == 'PUFF_GAP']
    if skipped_voynich:
        for s in skipped_voynich[:10]:
            print(f"  {s['voynich']} skipped (no Puff match)")
        if len(skipped_voynich) > 10:
            print(f"  ... and {len(skipped_voynich) - 10} more")
    else:
        print("  None")

    # Show sample alignment
    print("\n--- Sample Alignment (first 15) ---")
    for d in opt_analysis['details'][:15]:
        if d['type'] == 'PUFF_GAP':
            print(f"  {d['position']:3d}. --- gap ---          | {d['voynich']}")
        elif d['type'] == 'VOYNICH_GAP':
            print(f"  {d['position']:3d}. Ch.{d['puff']:<3}              | --- gap ---")
        else:
            match_str = "=" if d['type'] == 'EXACT' else "~" if d['type'] == 'ADJACENT' else "x"
            print(f"  {d['position']:3d}. Ch.{d['puff']:<3} D{d['puff_degree']} ({d['expected_regime']}) {match_str} {d['voynich']} ({d['voynich_regime']})")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    if improvement > 0.10:
        verdict = "SKIP ALIGNMENT SIGNIFICANTLY BETTER"
        interpretation = "Gaps improve alignment, suggesting partial transmission"
    elif improvement > 0.05:
        verdict = "SKIP ALIGNMENT MODERATELY BETTER"
        interpretation = "Some benefit from gaps, possible partial transmission"
    elif improvement > 0:
        verdict = "SKIP ALIGNMENT SLIGHTLY BETTER"
        interpretation = "Minimal improvement, mostly 1:1 correspondence"
    else:
        verdict = "NO IMPROVEMENT FROM GAPS"
        interpretation = "Strict 1:1 alignment is optimal or better"

    print(f"\n  {verdict}")
    print(f"  Improvement: {100*improvement:+.1f}% exact match rate")
    print(f"  Interpretation: {interpretation}")

    # Save results
    output = {
        "phase": "ENTITY_MATCHING_CORRECTED",
        "test": "SKIP_ALIGNMENT",
        "tier": 3,
        "status": "SPECULATIVE",
        "date": "2026-01-14",
        "data_counts": {
            "puff_chapters": len(puff_chapters),
            "voynich_folios": len(voynich_folios),
        },
        "strict_alignment": strict,
        "gap_penalty_search": gap_results,
        "optimal_alignment": {
            "gap_penalty": best['gap_penalty'],
            "score": opt_score,
            "total_positions": opt_analysis['total_positions'],
            "matches": opt_analysis['matches'],
            "puff_gaps": opt_analysis['puff_gaps'],
            "voynich_gaps": opt_analysis['voynich_gaps'],
            "exact_regime_matches": opt_analysis['exact_regime_matches'],
            "adjacent_matches": opt_analysis['adjacent_matches'],
            "exact_rate": opt_analysis['exact_rate'],
        },
        "comparison": {
            "strict_exact_rate": strict['exact_rate'],
            "skip_exact_rate": opt_analysis['exact_rate'],
            "improvement": improvement,
        },
        "skipped_puff_chapters": [d['puff'] for d in skipped_puff],
        "skipped_voynich_folios": [d['voynich'] for d in skipped_voynich],
        "verdict": verdict,
        "interpretation": interpretation,
        "sample_alignment": opt_analysis['details'][:30],
    }

    output_path = RESULTS_DIR / "skip_alignment_test.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return verdict

if __name__ == "__main__":
    main()
