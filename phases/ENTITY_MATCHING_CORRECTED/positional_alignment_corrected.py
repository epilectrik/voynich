"""
Phase: ENTITY_MATCHING_CORRECTED - Positional Alignment Test
Tier 3 SPECULATIVE

Tests whether Brunschwig degree correlates with curriculum position in proposed order.

Key hypothesis: Higher Brunschwig degree (more intensive processing) should
correlate with LATER curriculum position (higher complexity/hazard).

This replaces T1 from tier4_semantic_assignment.md which used current (wrong) folio order.
"""

import json
from pathlib import Path
from collections import defaultdict
from scipy import stats
import statistics

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# Category -> Brunschwig Degree (same as entity matching)
CATEGORY_TO_DEGREE = {
    'FLOWER': 1, 'TREE_FLOWER': 1, 'LEGUME_FLOWER': 1,
    'HERB': 2, 'FERN': 2, 'SUCCULENT': 2, 'VEGETABLE': 2,
    'VINE': 2, 'TREE_LEAF': 2, 'PARASITE': 2,
    'ROOT': 3, 'BULB': 3, 'FRUIT': 3, 'BERRY': 3, 'SHRUB': 3,
    'FUNGUS': 4, 'ANIMAL': 4, 'OIL': 4, 'SPIRIT': 4,
}

# Expected curriculum position ranges for each degree
DEGREE_POSITION_EXPECTATIONS = {
    1: {'name': 'EARLY', 'range': (1, 27), 'description': 'Gentle (balneum)'},
    2: {'name': 'MIDDLE', 'range': (28, 55), 'description': 'Standard (warm)'},
    3: {'name': 'LATE', 'range': (56, 83), 'description': 'Intensive (seething)'},
    4: {'name': 'SPECIAL', 'range': None, 'description': 'Forbidden/anomalous'},
}

def load_data():
    """Load Puff chapters and proposed order"""
    with open(RESULTS_DIR / "puff_83_chapters.json") as f:
        puff_data = json.load(f)
    puff_chapters = puff_data['chapters']

    # Load proposed order with regime info
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

def assign_degrees(puff_chapters):
    """Assign Brunschwig degree to each Puff chapter"""
    results = []
    for ch in puff_chapters:
        category = ch.get('category', 'HERB')
        is_dangerous = ch.get('dangerous', False)

        degree = CATEGORY_TO_DEGREE.get(category, 2)
        if is_dangerous:
            degree = max(degree, 3)

        results.append({
            'chapter': ch.get('chapter'),
            'german': ch.get('german'),
            'category': category,
            'degree': degree,
            'dangerous': is_dangerous,
        })
    return results

def create_positional_mapping(puff_with_degrees, order_data):
    """Map Puff chapters to folio positions (1:1 in order)"""
    n = min(len(puff_with_degrees), len(order_data))

    mappings = []
    for i in range(n):
        puff = puff_with_degrees[i]
        folio = order_data[i]

        mappings.append({
            'puff_chapter': puff['chapter'],
            'puff_degree': puff['degree'],
            'puff_category': puff['category'],
            'folio': folio['folio'],
            'position': folio['position'],
            'regime': folio['regime'],
            'hazard': folio['hazard'],
            'cei': folio['cei'],
        })

    return mappings

def test_degree_position_correlation(mappings):
    """Test if degree correlates with curriculum position"""
    # Extract degree and position for correlation
    degrees = [m['puff_degree'] for m in mappings]
    positions = [m['position'] for m in mappings]
    hazards = [m['hazard'] for m in mappings]
    ceis = [m['cei'] for m in mappings]

    # Spearman correlation (rank-based, handles ordinal degree)
    rho_position, p_position = stats.spearmanr(degrees, positions)
    rho_hazard, p_hazard = stats.spearmanr(degrees, hazards)
    rho_cei, p_cei = stats.spearmanr(degrees, ceis)

    return {
        'degree_vs_position': {'rho': rho_position, 'p': p_position},
        'degree_vs_hazard': {'rho': rho_hazard, 'p': p_hazard},
        'degree_vs_cei': {'rho': rho_cei, 'p': p_cei},
    }

def analyze_by_degree(mappings):
    """Analyze position statistics by degree"""
    by_degree = defaultdict(list)
    for m in mappings:
        by_degree[m['puff_degree']].append(m)

    results = {}
    for degree in [1, 2, 3, 4]:
        if degree in by_degree:
            items = by_degree[degree]
            positions = [m['position'] for m in items]
            hazards = [m['hazard'] for m in items]
            ceis = [m['cei'] for m in items]

            expected = DEGREE_POSITION_EXPECTATIONS[degree]
            if expected['range']:
                low, high = expected['range']
                in_range = sum(1 for p in positions if low <= p <= high)
            else:
                in_range = None

            results[degree] = {
                'n': len(items),
                'expected_phase': expected['name'],
                'expected_range': expected['range'],
                'mean_position': statistics.mean(positions),
                'std_position': statistics.stdev(positions) if len(positions) > 1 else 0,
                'min_position': min(positions),
                'max_position': max(positions),
                'mean_hazard': statistics.mean(hazards),
                'mean_cei': statistics.mean(ceis),
                'in_expected_range': in_range,
                'range_match_rate': in_range / len(items) if in_range is not None else None,
            }

    return results

def test_position_escalation(degree_stats):
    """Test if positions escalate with degree (1 < 2 < 3)"""
    # Get mean positions for degrees 1, 2, 3
    pos_1 = degree_stats.get(1, {}).get('mean_position')
    pos_2 = degree_stats.get(2, {}).get('mean_position')
    pos_3 = degree_stats.get(3, {}).get('mean_position')

    if pos_1 is not None and pos_2 is not None and pos_3 is not None:
        escalates = pos_1 < pos_2 < pos_3
        partial_escalation = (pos_1 < pos_3) or (pos_2 < pos_3)
        diff_1_to_2 = pos_2 - pos_1
        diff_2_to_3 = pos_3 - pos_2
        total_escalation = pos_3 - pos_1

        return {
            'positions': [pos_1, pos_2, pos_3],
            'strict_escalation': escalates,
            'partial_escalation': partial_escalation,
            'diff_1_to_2': diff_1_to_2,
            'diff_2_to_3': diff_2_to_3,
            'total_escalation': total_escalation,
        }
    return None

def main():
    print("=" * 70)
    print("POSITIONAL ALIGNMENT TEST (CORRECTED)")
    print("[TIER 3 SPECULATIVE]")
    print("=" * 70)
    print("\nTests whether Brunschwig degree correlates with curriculum position")
    print("in the PROPOSED folio order (not current misbinding).")
    print()

    # Load data
    print("--- Loading Data ---")
    puff_chapters, order_data = load_data()
    print(f"Puff chapters: {len(puff_chapters)}")
    print(f"Proposed order folios: {len(order_data)}")

    # Assign degrees
    puff_with_degrees = assign_degrees(puff_chapters)

    # Count by degree
    degree_counts = defaultdict(int)
    for p in puff_with_degrees:
        degree_counts[p['degree']] += 1
    print(f"Puff by degree: {dict(degree_counts)}")

    # Create 1:1 positional mapping
    print("\n--- Creating Positional Mapping ---")
    mappings = create_positional_mapping(puff_with_degrees, order_data)
    print(f"Mappings created: {len(mappings)}")

    # Test correlations
    print("\n--- Correlation Analysis ---")
    correlations = test_degree_position_correlation(mappings)

    print(f"\nDegree vs Position: rho = {correlations['degree_vs_position']['rho']:.3f}, p = {correlations['degree_vs_position']['p']:.4f}")
    print(f"Degree vs Hazard:   rho = {correlations['degree_vs_hazard']['rho']:.3f}, p = {correlations['degree_vs_hazard']['p']:.4f}")
    print(f"Degree vs CEI:      rho = {correlations['degree_vs_cei']['rho']:.3f}, p = {correlations['degree_vs_cei']['p']:.4f}")

    # Analyze by degree
    print("\n--- Position Statistics by Degree ---")
    degree_stats = analyze_by_degree(mappings)

    for degree in [1, 2, 3, 4]:
        if degree in degree_stats:
            d = degree_stats[degree]
            exp = DEGREE_POSITION_EXPECTATIONS[degree]
            range_str = f"{exp['range'][0]}-{exp['range'][1]}" if exp['range'] else "N/A"
            match_rate = f"{100*d['range_match_rate']:.0f}%" if d['range_match_rate'] is not None else "N/A"

            print(f"\n  Degree {degree} ({exp['description']}):")
            print(f"    N = {d['n']}")
            print(f"    Expected range: {exp['name']} ({range_str})")
            print(f"    Actual positions: {d['mean_position']:.1f} +/- {d['std_position']:.1f}")
            print(f"    Range: {d['min_position']} - {d['max_position']}")
            print(f"    In expected range: {d['in_expected_range']}/{d['n']} ({match_rate})")
            print(f"    Mean hazard: {d['mean_hazard']:.3f}")
            print(f"    Mean CEI: {d['mean_cei']:.3f}")

    # Test escalation
    print("\n--- Escalation Test ---")
    escalation = test_position_escalation(degree_stats)

    if escalation:
        print(f"\n  Mean positions: D1={escalation['positions'][0]:.1f}, D2={escalation['positions'][1]:.1f}, D3={escalation['positions'][2]:.1f}")
        print(f"  Strict escalation (D1 < D2 < D3): {escalation['strict_escalation']}")
        print(f"  D1 -> D2: {escalation['diff_1_to_2']:+.1f} positions")
        print(f"  D2 -> D3: {escalation['diff_2_to_3']:+.1f} positions")
        print(f"  Total (D1 -> D3): {escalation['total_escalation']:+.1f} positions")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    pos_significant = correlations['degree_vs_position']['p'] < 0.05
    pos_positive = correlations['degree_vs_position']['rho'] > 0
    strong_d3 = degree_stats.get(3, {}).get('mean_position', 0) > 60

    tests_passed = []
    if pos_significant and pos_positive:
        tests_passed.append("Significant positive correlation")
    if escalation and escalation['strict_escalation']:
        tests_passed.append("Strict degree escalation")
    elif escalation and escalation['diff_2_to_3'] > 20:
        tests_passed.append("Strong D2->D3 escalation")
    if strong_d3:
        tests_passed.append("Degree 3 in LATE positions")

    if len(tests_passed) >= 2:
        verdict = "SUPPORTS CURRICULUM HYPOTHESIS"
    elif len(tests_passed) == 1:
        verdict = "PARTIAL SUPPORT"
    else:
        verdict = "DOES NOT SUPPORT"

    print(f"\n  {verdict}")
    for t in tests_passed:
        print(f"    - {t}")

    # Save results
    output = {
        "phase": "ENTITY_MATCHING_CORRECTED",
        "test": "POSITIONAL_ALIGNMENT",
        "tier": 3,
        "status": "SPECULATIVE",
        "date": "2026-01-14",
        "note": "Replaces T1 from tier4_semantic_assignment.md with corrected folio order",
        "data_counts": {
            "puff_chapters": len(puff_chapters),
            "order_folios": len(order_data),
            "mappings": len(mappings),
            "puff_by_degree": dict(degree_counts),
        },
        "correlations": correlations,
        "degree_statistics": degree_stats,
        "escalation_test": escalation,
        "verdict": verdict,
        "tests_passed": tests_passed,
        "interpretation": (
            f"Degree-position correlation: rho={correlations['degree_vs_position']['rho']:.3f} "
            f"(p={correlations['degree_vs_position']['p']:.4f}). "
            f"{'Significant positive' if pos_significant and pos_positive else 'Not significant'}. "
            f"Degree 3 mean position = {degree_stats.get(3, {}).get('mean_position', 0):.1f} "
            f"({'in LATE range' if strong_d3 else 'not in LATE range'})."
        )
    }

    output_path = RESULTS_DIR / "positional_alignment_corrected.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")

    # Show sample mappings
    print("\n--- Sample Mappings (first 10) ---")
    for m in mappings[:10]:
        exp = DEGREE_POSITION_EXPECTATIONS[m['puff_degree']]
        print(f"  Ch.{m['puff_chapter']} D{m['puff_degree']} ({exp['name']}) -> {m['folio']} pos={m['position']} ({m['regime']})")

    print("\n--- Degree 3 mappings (should be LATE) ---")
    d3_mappings = [m for m in mappings if m['puff_degree'] == 3]
    for m in d3_mappings[:10]:
        in_range = "OK" if m['position'] >= 56 else "EARLY"
        print(f"  Ch.{m['puff_chapter']} -> {m['folio']} pos={m['position']} ({m['regime']}) [{in_range}]")

    return verdict

if __name__ == "__main__":
    main()
