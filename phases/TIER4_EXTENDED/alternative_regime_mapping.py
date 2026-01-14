"""
Alternative Regime Mapping Test
Test if REGIME_4 means "constrained/precision" rather than "forbidden/dangerous"

Hypothesis: The 4 regimes represent PROCESSING MODES, not danger levels:
- REGIME_1: Forgiving (high escape) - broad tolerance, flowers/aromatics
- REGIME_2: Standard (baseline) - routine processing
- REGIME_3: Intensive (high CEI) - complex, multi-step, roots/resins
- REGIME_4: Constrained (low escape) - precision required, narrow tolerance

Under this model:
- REGIME_4 is NOT "dangerous materials"
- REGIME_4 is "precision operations" - things that need exact conditions
- Many herbs might need REGIME_4 (careful dosing, specific timing)
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# ALTERNATIVE MAPPING
# Based on processing requirements, not danger level
CATEGORY_TO_PROCESSING_MODE = {
    # MODE 1: Forgiving - volatile materials that tolerate variation
    'FLOWER': 'FORGIVING',
    'TREE_FLOWER': 'FORGIVING',
    'LEGUME_FLOWER': 'FORGIVING',

    # MODE 2: Standard - routine processing
    'VEGETABLE': 'STANDARD',
    'FRUIT': 'STANDARD',
    'BERRY': 'STANDARD',

    # MODE 3: Intensive - need sustained heat/complex processing
    'ROOT': 'INTENSIVE',
    'BULB': 'INTENSIVE',
    'SHRUB': 'INTENSIVE',

    # MODE 4: Precision - require exact conditions
    'HERB': 'PRECISION',  # Most herbs need careful handling
    'FERN': 'PRECISION',
    'SUCCULENT': 'PRECISION',
    'VINE': 'PRECISION',
    'TREE_LEAF': 'PRECISION',
    'PARASITE': 'PRECISION',
    'FUNGUS': 'PRECISION',
    'ANIMAL': 'PRECISION',
    'OIL': 'PRECISION',
    'SPIRIT': 'PRECISION',
}

# Aromatics get special treatment - they're forgiving despite being herbs
def get_processing_mode(chapter):
    category = chapter.get('category', 'HERB')
    is_aromatic = chapter.get('aromatic', False)

    if is_aromatic:
        return 'FORGIVING'  # Aromatics are volatile, tolerate gentle handling

    return CATEGORY_TO_PROCESSING_MODE.get(category, 'PRECISION')

MODE_TO_REGIME = {
    'FORGIVING': 'REGIME_1',
    'STANDARD': 'REGIME_2',
    'INTENSIVE': 'REGIME_3',
    'PRECISION': 'REGIME_4',
}

def main():
    print("=" * 60)
    print("ALTERNATIVE REGIME MAPPING TEST")
    print("[Testing: REGIME_4 = PRECISION, not FORBIDDEN]")
    print("=" * 60)

    # Load data
    with open(RESULTS_DIR / "puff_83_chapters.json") as f:
        puff = json.load(f)

    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        profiles = json.load(f)

    # Get Puff distribution under alternative mapping
    puff_modes = Counter()
    for ch in puff['chapters']:
        mode = get_processing_mode(ch)
        puff_modes[mode] += 1

    print("\n--- Puff Distribution (Alternative Mapping) ---")
    for mode in ['FORGIVING', 'STANDARD', 'INTENSIVE', 'PRECISION']:
        regime = MODE_TO_REGIME[mode]
        print(f"  {mode} -> {regime}: {puff_modes[mode]} chapters")

    # Get Voynich regime distribution
    regime_counts = Counter()
    for folio_name, folio_data in profiles.get('profiles', {}).items():
        if isinstance(folio_data, dict) and folio_data.get('system') == 'B':
            b_metrics = folio_data.get('b_metrics', {})
            if b_metrics:
                regime_counts[b_metrics.get('regime')] += 1

    print("\n--- Voynich Regime Distribution ---")
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        print(f"  {regime}: {regime_counts[regime]} folios")

    # Compare
    print("\n--- Comparison ---")
    print(f"{'Mode':<12} {'Puff':<8} {'Regime':<12} {'Voynich':<8} {'Ratio':<8}")
    print("-" * 50)

    total_ratio_diff = 0
    for mode in ['FORGIVING', 'STANDARD', 'INTENSIVE', 'PRECISION']:
        regime = MODE_TO_REGIME[mode]
        puff_count = puff_modes[mode]
        voynich_count = regime_counts[regime]
        ratio = puff_count / voynich_count if voynich_count > 0 else float('inf')
        print(f"{mode:<12} {puff_count:<8} {regime:<12} {voynich_count:<8} {ratio:.2f}")
        total_ratio_diff += abs(1 - ratio)

    print("\n--- Analysis ---")

    # Check if distribution is better than original mapping
    # Original: HERB->REGIME_2 (45 vs 11 = 4.09 ratio)
    # Alternative: HERB->REGIME_4 (where we have 25 folios)

    non_aromatic_herbs = len([ch for ch in puff['chapters']
                             if ch.get('category') == 'HERB' and not ch.get('aromatic')])
    aromatic_herbs = len([ch for ch in puff['chapters']
                         if ch.get('category') == 'HERB' and ch.get('aromatic')])

    print(f"Non-aromatic HERBs (-> PRECISION/R4): {non_aromatic_herbs}")
    print(f"Aromatic HERBs (-> FORGIVING/R1): {aromatic_herbs}")
    print(f"REGIME_4 folios available: {regime_counts['REGIME_4']}")

    # Calculate expected vs actual for PRECISION mode
    precision_chapters = puff_modes['PRECISION']
    regime_4_folios = regime_counts['REGIME_4']

    print(f"\nPRECISION chapters: {precision_chapters}")
    print(f"REGIME_4 folios: {regime_4_folios}")
    print(f"Ratio: {precision_chapters / regime_4_folios:.2f}" if regime_4_folios > 0 else "N/A")

    # Check FORGIVING mode
    forgiving_chapters = puff_modes['FORGIVING']
    regime_1_folios = regime_counts['REGIME_1']

    print(f"\nFORGIVING chapters: {forgiving_chapters}")
    print(f"REGIME_1 folios: {regime_1_folios}")
    print(f"Ratio: {forgiving_chapters / regime_1_folios:.2f}" if regime_1_folios > 0 else "N/A")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    original_herb_ratio = 45 / 11  # Original HERB->REGIME_2
    new_precision_ratio = precision_chapters / regime_4_folios if regime_4_folios > 0 else float('inf')

    print(f"Original mapping (HERB->REGIME_2): ratio = {original_herb_ratio:.2f}")
    print(f"Alternative mapping (HERB->REGIME_4): ratio = {new_precision_ratio:.2f}")

    if new_precision_ratio < original_herb_ratio:
        print("\nALTERNATIVE MAPPING IS BETTER")
        improvement = (original_herb_ratio - new_precision_ratio) / original_herb_ratio * 100
        print(f"Improvement: {improvement:.1f}% closer to 1:1")
    else:
        print("\nALTERNATIVE MAPPING IS NOT BETTER")

    # Save results
    output = {
        "hypothesis": "REGIME_4 means PRECISION, not FORBIDDEN",
        "alternative_mapping": {
            "FORGIVING": "REGIME_1 (volatile, tolerates variation)",
            "STANDARD": "REGIME_2 (routine processing)",
            "INTENSIVE": "REGIME_3 (complex, sustained heat)",
            "PRECISION": "REGIME_4 (exact conditions required)",
        },
        "puff_distribution": dict(puff_modes),
        "voynich_distribution": dict(regime_counts),
        "original_herb_ratio": original_herb_ratio,
        "alternative_herb_ratio": new_precision_ratio,
        "improvement": improvement if new_precision_ratio < original_herb_ratio else 0,
    }

    with open(RESULTS_DIR / "alternative_regime_mapping.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to results/alternative_regime_mapping.json")

if __name__ == "__main__":
    main()
