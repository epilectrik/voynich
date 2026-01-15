#!/usr/bin/env python3
"""
MATERIAL GRANULARITY TEST

Question: Do A registers specify individual materials or material CLASSES?

Test approach:
1. Count comparison: How many A registers vs how many Brunschwig materials per type?
2. Puff alignment: Do A register counts match Puff CLASS counts or CHAPTER counts?
3. MIDDLE sharing: Do MIDDLEs correlate with material PROPERTIES (class) or unique per material?

Predictions:
- CLASS-level: Fewer A registers than individual materials, MIDDLEs encode properties
- INDIVIDUAL-level: ~1:1 A registers to materials, MIDDLEs unique per register
"""

import json
from collections import defaultdict, Counter

# ============================================================
# BRUNSCHWIG MATERIAL INVENTORY (by product type)
# ============================================================

BRUNSCHWIG_MATERIALS = {
    'WATER_GENTLE': {
        'description': 'First degree gentle flower waters',
        'individual_materials': [
            'Rose', 'Lavender', 'Violet', 'Orange flower', 'Elder flower',
            'Chamomile', 'Lily', 'Jasmine', 'Borage flower', 'Betony flower'
        ],
        'material_classes': [
            'Delicate petals (Rose, Violet, Lily)',
            'Aromatic flowers (Lavender, Chamomile)',
            'Medicinal flowers (Elder, Borage, Betony)',
        ],
    },
    'WATER_STANDARD': {
        'description': 'Second degree standard herbal waters',
        'individual_materials': [
            'Mint', 'Sage', 'Rosemary', 'Thyme', 'Horehound', 'Melissa',
            'Hyssop', 'Fennel', 'Anise', 'Wormwood', 'Rue', 'Mugwort',
            'Plantain', 'Yarrow', 'Betony', 'Valerian', 'Vervain', 'Angelica',
            # ... Brunschwig has 50+ standard herbs
        ],
        'material_classes': [
            'Aromatic leaves (Mint, Sage, Rosemary)',
            'Medicinal herbs (Horehound, Hyssop)',
            'Bitter herbs (Wormwood, Rue)',
            'Seeds (Fennel, Anise)',
            'Roots (Valerian, Angelica)',
        ],
    },
    'OIL_RESIN': {
        'description': 'Third/fourth degree oils and resins',
        'individual_materials': [
            'Juniper', 'Pine', 'Turpentine', 'Amber', 'Myrrh', 'Frankincense',
            'Mastick', 'Benzoin', 'Storax', 'Camphor', 'Cedar', 'Cypress',
        ],
        'material_classes': [
            'Conifer resins (Pine, Juniper, Cedar)',
            'Exotic resins (Myrrh, Frankincense, Benzoin)',
            'Fossil resins (Amber)',
            'Wood oils (Cedar, Cypress)',
        ],
    },
    'PRECISION': {
        'description': 'Any degree requiring exact timing',
        'individual_materials': [
            'Neroli (orange flower oil)', 'Rose oil', 'Lavender oil',
            'Clove oil', 'Nutmeg oil', 'Cinnamon oil',
            # Precision is about METHOD, not specific materials
        ],
        'material_classes': [
            'Volatile florals (require exact temperature)',
            'Heat-sensitive aromatics',
            'Close-boiling fractions',
        ],
    },
}

# ============================================================
# PUFF MATERIAL ORGANIZATION
# ============================================================

PUFF_STRUCTURE = {
    'FLOWER': {
        'chapters': list(range(1, 12)),  # Chapters 1-11
        'description': 'Prestigious flowers',
        'maps_to': 'WATER_GENTLE',
    },
    'HERB': {
        'chapters': list(range(12, 55)),  # Chapters 12-54
        'description': 'Mixed herbs',
        'maps_to': 'WATER_STANDARD',
    },
    'ROOT': {
        'chapters': list(range(55, 65)),  # Chapters 55-64
        'description': 'Roots and bark',
        'maps_to': 'WATER_STANDARD',  # Or OIL_RESIN depending on processing
    },
    'RESIN_OIL': {
        'chapters': list(range(65, 75)),  # Chapters 65-74
        'description': 'Resins, oils',
        'maps_to': 'OIL_RESIN',
    },
    'ANOMALY': {
        'chapters': list(range(75, 86)),  # Chapters 75-85
        'description': 'Animal, fungi, externals',
        'maps_to': 'OIL_RESIN',  # Advanced processing
    },
}

# ============================================================
# LOAD A REGISTER COUNTS
# ============================================================

def load_a_register_counts():
    """Load A folio counts by product type."""
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)

    classifications = data['a_folio_classifications']

    counts = Counter(classifications.values())
    return dict(counts), classifications

# ============================================================
# ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("MATERIAL GRANULARITY TEST")
    print("=" * 70)
    print()
    print("Question: Do A registers specify INDIVIDUAL materials or CLASSES?")
    print()

    # Load A register counts
    a_counts, a_classifications = load_a_register_counts()

    # Test 1: Count comparison
    print("=" * 70)
    print("TEST 1: COUNT COMPARISON")
    print("=" * 70)
    print()

    print(f"{'Product Type':<20} {'A Regs':>8} {'Indiv':>8} {'Classes':>8} {'Ratio A/I':>10} {'Ratio A/C':>10}")
    print("-" * 70)

    ratios_individual = []
    ratios_class = []

    for ptype in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
        a_count = a_counts.get(ptype, 0)

        if ptype in BRUNSCHWIG_MATERIALS:
            indiv_count = len(BRUNSCHWIG_MATERIALS[ptype]['individual_materials'])
            class_count = len(BRUNSCHWIG_MATERIALS[ptype]['material_classes'])
        else:
            indiv_count = 0
            class_count = 0

        ratio_i = a_count / indiv_count if indiv_count > 0 else 0
        ratio_c = a_count / class_count if class_count > 0 else 0

        ratios_individual.append(ratio_i)
        ratios_class.append(ratio_c)

        print(f"{ptype:<20} {a_count:>8} {indiv_count:>8} {class_count:>8} {ratio_i:>10.2f} {ratio_c:>10.2f}")

    print()

    avg_ratio_individual = sum(ratios_individual) / len(ratios_individual)
    avg_ratio_class = sum(ratios_class) / len(ratios_class)

    print(f"Average A/Individual ratio: {avg_ratio_individual:.2f}")
    print(f"Average A/Class ratio: {avg_ratio_class:.2f}")
    print()

    if avg_ratio_individual < 0.5:
        print("FINDING: A registers << individual materials")
        print("         Suggests CLASS-level specification")
    elif avg_ratio_individual > 0.8:
        print("FINDING: A registers ~ individual materials")
        print("         Suggests INDIVIDUAL-level specification")
    else:
        print("FINDING: A registers between class and individual")
        print("         May be SUB-CLASS level (e.g., 'aromatic flowers')")

    print()

    # Test 2: Puff alignment
    print("=" * 70)
    print("TEST 2: PUFF ALIGNMENT")
    print("=" * 70)
    print()

    print("Puff organizes by CHAPTER (individual material) and CLASS (category)")
    print()

    print(f"{'Puff Class':<15} {'Chapters':>10} {'Maps to':>20} {'A Regs':>10}")
    print("-" * 60)

    for puff_class, info in PUFF_STRUCTURE.items():
        n_chapters = len(info['chapters'])
        maps_to = info['maps_to']
        a_count = a_counts.get(maps_to, 0)
        print(f"{puff_class:<15} {n_chapters:>10} {maps_to:>20} {a_count:>10}")

    print()

    # Compare granularity
    puff_class_count = len(PUFF_STRUCTURE)  # 5 major classes
    puff_chapter_count = 85  # Individual chapters

    total_a_regs = sum(a_counts.values())

    print(f"Total Puff classes: {puff_class_count}")
    print(f"Total Puff chapters: {puff_chapter_count}")
    print(f"Total A registers: {total_a_regs}")
    print()

    print(f"A registers / Puff classes: {total_a_regs / puff_class_count:.1f}")
    print(f"A registers / Puff chapters: {total_a_regs / puff_chapter_count:.2f}")
    print()

    if total_a_regs / puff_chapter_count > 0.8:
        print("FINDING: A register count ~ Puff chapter count")
        print("         Suggests INDIVIDUAL material specification")
    elif total_a_regs / puff_class_count > 10:
        print("FINDING: A registers >> Puff classes but << chapters")
        print("         Suggests SUB-CLASS level (finer than class, coarser than individual)")
    else:
        print("FINDING: A registers ~ Puff classes")
        print("         Suggests CLASS-level specification")

    print()

    # Test 3: WATER_GENTLE deep dive
    print("=" * 70)
    print("TEST 3: WATER_GENTLE DEEP DIVE")
    print("=" * 70)
    print()

    gentle_folios = [f for f, t in a_classifications.items() if t == 'WATER_GENTLE']
    gentle_count = len(gentle_folios)

    print(f"WATER_GENTLE A registers: {gentle_count}")
    print(f"Brunschwig gentle flowers (individual): {len(BRUNSCHWIG_MATERIALS['WATER_GENTLE']['individual_materials'])}")
    print(f"Brunschwig gentle flower CLASSES: {len(BRUNSCHWIG_MATERIALS['WATER_GENTLE']['material_classes'])}")
    print(f"Puff FLOWER chapters: {len(PUFF_STRUCTURE['FLOWER']['chapters'])}")
    print()

    # The classes
    print("Brunschwig gentle flower CLASSES:")
    for i, cls in enumerate(BRUNSCHWIG_MATERIALS['WATER_GENTLE']['material_classes']):
        print(f"  {i+1}. {cls}")
    print()

    print("WATER_GENTLE A registers:")
    for folio in sorted(gentle_folios):
        print(f"  {folio}")
    print()

    if gentle_count <= len(BRUNSCHWIG_MATERIALS['WATER_GENTLE']['material_classes']) + 2:
        print("FINDING: A register count ≈ material CLASS count")
        print()
        print("HYPOTHESIS: Each A register specifies a material CLASS:")
        for i, (folio, cls) in enumerate(zip(sorted(gentle_folios),
                                              BRUNSCHWIG_MATERIALS['WATER_GENTLE']['material_classes'])):
            print(f"  {folio} -> {cls}")
        if gentle_count > len(BRUNSCHWIG_MATERIALS['WATER_GENTLE']['material_classes']):
            remaining = sorted(gentle_folios)[len(BRUNSCHWIG_MATERIALS['WATER_GENTLE']['material_classes']):]
            for folio in remaining:
                print(f"  {folio} -> (additional class or variant)")
    else:
        print("FINDING: A register count > material CLASS count")
        print("         May be finer than class level")

    print()

    # Final verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    # Calculate best fit
    gentle_to_class = gentle_count / len(BRUNSCHWIG_MATERIALS['WATER_GENTLE']['material_classes'])
    gentle_to_indiv = gentle_count / len(BRUNSCHWIG_MATERIALS['WATER_GENTLE']['individual_materials'])
    gentle_to_puff = gentle_count / len(PUFF_STRUCTURE['FLOWER']['chapters'])

    print(f"WATER_GENTLE ratios:")
    print(f"  A/Classes: {gentle_to_class:.2f}")
    print(f"  A/Individual: {gentle_to_indiv:.2f}")
    print(f"  A/Puff chapters: {gentle_to_puff:.2f}")
    print()

    # Closest to 1.0 wins
    ratios = [
        (abs(gentle_to_class - 1.0), "CLASS-level (material categories)"),
        (abs(gentle_to_indiv - 1.0), "INDIVIDUAL-level (specific materials)"),
        (abs(gentle_to_puff - 1.0), "PUFF-aligned (chapter-level)"),
    ]

    best = min(ratios, key=lambda x: x[0])

    print(f"Best fit: {best[1]}")
    print(f"  (ratio closest to 1.0: {1.0 - best[0]:.2f})")
    print()

    if "CLASS" in best[1]:
        verdict = "CLASS-LEVEL"
        interpretation = "A registers specify material CLASSES, not individual species"
    elif "INDIVIDUAL" in best[1]:
        verdict = "INDIVIDUAL-LEVEL"
        interpretation = "A registers specify individual materials"
    else:
        verdict = "SUB-CLASS"
        interpretation = "A registers specify at a level between class and individual"

    print(f"Verdict: {verdict}")
    print(f"Interpretation: {interpretation}")
    print()

    # Save results
    output = {
        'test': 'MATERIAL_GRANULARITY',
        'a_register_counts': a_counts,
        'brunschwig_counts': {
            ptype: {
                'individual': len(info['individual_materials']),
                'classes': len(info['material_classes'])
            }
            for ptype, info in BRUNSCHWIG_MATERIALS.items()
        },
        'ratios': {
            'avg_a_to_individual': avg_ratio_individual,
            'avg_a_to_class': avg_ratio_class,
        },
        'verdict': verdict,
        'interpretation': interpretation
    }

    with open('results/material_granularity.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to results/material_granularity.json")

if __name__ == '__main__':
    main()
