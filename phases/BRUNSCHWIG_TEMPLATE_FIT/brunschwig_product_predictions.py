#!/usr/bin/env python3
"""
BRUNSCHWIG PRODUCT -> A SIGNATURE PREDICTIONS

Test specific Brunschwig products against predicted A signatures.

Products organized by Brunschwig's degree system:
- First degree (balneum marie): Gentle flowers -> WATER_GENTLE
- Second degree (moderate): Standard herbs -> WATER_STANDARD
- Third degree (seething): Roots, oils -> OIL_RESIN
- Fourth degree (dry): Resins -> OIL_RESIN
- Precision variants: Any degree with exact timing -> PRECISION
"""

import json
from collections import Counter

# ============================================================
# BRUNSCHWIG PRODUCT CATALOG
# ============================================================

BRUNSCHWIG_PRODUCTS = {
    # FIRST DEGREE - Gentle flowers (balneum marie)
    'rose_water': {
        'german': 'Rosenwasser',
        'degree': 1,
        'method': 'balneum marie',
        'material': 'flower petals',
        'expected_type': 'WATER_GENTLE',
        'brunschwig_notes': 'First degree, gentle heat, aromatic'
    },
    'lavender_water': {
        'german': 'Lavendelwasser',
        'degree': 1,
        'method': 'balneum marie',
        'material': 'flowers',
        'expected_type': 'WATER_GENTLE',
        'brunschwig_notes': 'First degree, delicate aromatics'
    },
    'violet_water': {
        'german': 'Veilchenwasser',
        'degree': 1,
        'method': 'balneum marie',
        'material': 'flowers',
        'expected_type': 'WATER_GENTLE',
        'brunschwig_notes': 'First degree, very gentle'
    },

    # SECOND DEGREE - Standard herbs
    'horehound_water': {
        'german': 'Andornwasser',
        'degree': 2,
        'method': 'moderate heat',
        'material': 'whole herb',
        'expected_type': 'WATER_STANDARD',
        'brunschwig_notes': 'Second degree, 16 uses documented'
    },
    'mint_water': {
        'german': 'Minzwasser',
        'degree': 2,
        'method': 'moderate heat',
        'material': 'leaves',
        'expected_type': 'WATER_STANDARD',
        'brunschwig_notes': 'Second degree, common herb'
    },
    'sage_water': {
        'german': 'Salbeiwasser',
        'degree': 2,
        'method': 'moderate heat',
        'material': 'leaves',
        'expected_type': 'WATER_STANDARD',
        'brunschwig_notes': 'Second degree, medicinal herb'
    },
    'melissa_water': {
        'german': 'Melissenwasser',
        'degree': 2,
        'method': 'moderate heat',
        'material': 'herb',
        'expected_type': 'WATER_STANDARD',
        'brunschwig_notes': 'Second degree, lemon balm'
    },

    # THIRD DEGREE - Intensive extraction (oils)
    'juniper_oil': {
        'german': 'Wacholderöl',
        'degree': 3,
        'method': 'seething',
        'material': 'berries/wood',
        'expected_type': 'OIL_RESIN',
        'brunschwig_notes': 'Third degree, essential oil extraction'
    },
    'rosemary_oil': {
        'german': 'Rosmarinöl',
        'degree': 3,
        'method': 'seething',
        'material': 'herb',
        'expected_type': 'OIL_RESIN',
        'brunschwig_notes': 'Third degree, aromatic oil'
    },
    'turpentine': {
        'german': 'Terpentin',
        'degree': 3,
        'method': 'seething',
        'material': 'pine resin',
        'expected_type': 'OIL_RESIN',
        'brunschwig_notes': 'Third degree, resinous extraction'
    },

    # FOURTH DEGREE - Dry distillation (forbidden but documented)
    'amber_oil': {
        'german': 'Bernsteinöl',
        'degree': 4,
        'method': 'dry distillation',
        'material': 'fossil resin',
        'expected_type': 'OIL_RESIN',
        'brunschwig_notes': 'Fourth degree, destructive distillation'
    },
    'hartshorn': {
        'german': 'Hirschhorn',
        'degree': 4,
        'method': 'dry distillation',
        'material': 'animal horn',
        'expected_type': 'OIL_RESIN',
        'brunschwig_notes': 'Fourth degree, documented but dangerous'
    },

    # PRECISION VARIANTS - Exact timing required
    'neroli_water': {
        'german': 'Neroliwasser',
        'degree': 1,
        'method': 'precision balneum',
        'material': 'orange flowers',
        'expected_type': 'PRECISION',
        'brunschwig_notes': 'First degree but volatile, needs exact timing'
    },
    'fraction_separation': {
        'german': 'Fraktionierung',
        'degree': 2,
        'method': 'precision moderate',
        'material': 'mixed herbs',
        'expected_type': 'PRECISION',
        'brunschwig_notes': 'Separating close-boiling fractions'
    },
    'heat_sensitive': {
        'german': 'Hitzeempfindlich',
        'degree': 1,
        'method': 'precision gentle',
        'material': 'delicate compounds',
        'expected_type': 'PRECISION',
        'brunschwig_notes': 'Must not overshoot temperature'
    }
}

# ============================================================
# LOAD ACTUAL A SIGNATURES
# ============================================================

# Load from our previous analysis
with open('results/exclusive_middle_backprop.json', 'r') as f:
    backprop_data = json.load(f)

ACTUAL_PROFILES = backprop_data['product_prefix_profiles']

# ============================================================
# PREDICTED SIGNATURES
# ============================================================

# Based on our analysis, these are the distinguishing features
PREDICTED_SIGNATURES = {
    'WATER_GENTLE': {
        'description': 'Gentle aromatic waters (first degree)',
        'key_features': {
            'ch': 'DEPLETED (14.6% vs 23.9% standard)',
            'ok': 'ENRICHED (9.6% vs 5.9% standard)',
            'y': 'SLIGHTLY ENRICHED (7.5%)'
        },
        'interpretation': 'Less phase operations, more gentle handling'
    },
    'WATER_STANDARD': {
        'description': 'Standard herbal waters (second degree)',
        'key_features': {
            'ch': 'BASELINE (23.9%)',
            'd': 'BASELINE (17.6%)',
            'qo': 'BASELINE (10.9%)'
        },
        'interpretation': 'Default procedural profile'
    },
    'OIL_RESIN': {
        'description': 'Oils and resins (third/fourth degree)',
        'key_features': {
            'd': 'ENRICHED (22.5% vs 17.6% standard)',
            'ch': 'SLIGHTLY DEPLETED (20.8%)',
            'y': 'DEPLETED (6.7%)'
        },
        'interpretation': 'More energy operations, aggressive extraction'
    },
    'PRECISION': {
        'description': 'Precision procedures (any degree, exact timing)',
        'key_features': {
            'ch': 'ENRICHED (24.3%)',
            'd': 'DEPLETED (16.7% vs 22.5% oil)',
            'sh': 'ENRICHED (11.5%)'
        },
        'interpretation': 'Phase-controlled, monitoring-heavy'
    }
}

# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():
    print("=" * 75)
    print("BRUNSCHWIG PRODUCT -> A SIGNATURE PREDICTIONS")
    print("=" * 75)
    print()

    # Show predicted signatures
    print("PREDICTED A SIGNATURES BY PRODUCT TYPE:")
    print("-" * 75)
    print()

    for ptype, sig in PREDICTED_SIGNATURES.items():
        print(f"{ptype}: {sig['description']}")
        print(f"  Interpretation: {sig['interpretation']}")
        for prefix, desc in sig['key_features'].items():
            print(f"    {prefix}: {desc}")
        print()

    # Show actual profiles
    print("=" * 75)
    print("ACTUAL A PREFIX PROFILES (from exclusive MIDDLE analysis)")
    print("=" * 75)
    print()

    prefixes_of_interest = ['qo', 'ch', 'y', 'sh', 'd', 'ok', 'ot', 'ol', 'or']

    print(f"{'Product Type':<18}", end="")
    for p in prefixes_of_interest:
        print(f"{p:>7}", end="")
    print()
    print("-" * 75)

    for ptype in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
        if ptype in ACTUAL_PROFILES:
            prof = ACTUAL_PROFILES[ptype]
            print(f"{ptype:<18}", end="")
            for p in prefixes_of_interest:
                val = 100 * prof.get(p, 0)
                print(f"{val:>6.1f}%", end="")
            print()
    print()

    # Test specific products
    print("=" * 75)
    print("BRUNSCHWIG PRODUCT PREDICTIONS")
    print("=" * 75)
    print()

    # Group products by expected type
    by_type = {}
    for name, prod in BRUNSCHWIG_PRODUCTS.items():
        etype = prod['expected_type']
        if etype not in by_type:
            by_type[etype] = []
        by_type[etype].append((name, prod))

    for expected_type in ['WATER_GENTLE', 'WATER_STANDARD', 'OIL_RESIN', 'PRECISION']:
        if expected_type not in by_type:
            continue

        print(f"\n{expected_type}:")
        print("-" * 50)

        sig = PREDICTED_SIGNATURES[expected_type]
        print(f"  Predicted signature: {sig['interpretation']}")

        actual = ACTUAL_PROFILES.get(expected_type, {})
        print(f"  Actual key values:", end="")
        for prefix in ['ch', 'd', 'ok', 'y']:
            val = 100 * actual.get(prefix, 0)
            print(f" {prefix}={val:.1f}%", end="")
        print()
        print()

        print("  Products in this category:")
        for name, prod in by_type[expected_type]:
            print(f"    - {prod['german']} ({name})")
            print(f"      Degree: {prod['degree']}, Method: {prod['method']}")
            print(f"      Material: {prod['material']}")
            print()

    # Specific product predictions
    print("=" * 75)
    print("SPECIFIC PRODUCT -> A REGISTER PREDICTIONS")
    print("=" * 75)
    print()

    test_products = [
        ('rose_water', 'Rose water - classic gentle aromatic'),
        ('turpentine', 'Turpentine - aggressive resin extraction'),
        ('horehound_water', 'Horehound - standard medicinal water'),
        ('neroli_water', 'Neroli - precision volatile aromatic')
    ]

    for prod_name, description in test_products:
        prod = BRUNSCHWIG_PRODUCTS[prod_name]
        expected = prod['expected_type']
        actual_prof = ACTUAL_PROFILES.get(expected, {})

        print(f"{description}")
        print(f"  Brunschwig: {prod['german']}, {prod['method']}")
        print(f"  Expected type: {expected}")
        print()
        print(f"  PREDICTED A register should show:")

        sig = PREDICTED_SIGNATURES[expected]
        for prefix, desc in sig['key_features'].items():
            actual_val = 100 * actual_prof.get(prefix, 0)
            print(f"    {prefix}-prefix: {desc}")
            print(f"      (actual: {actual_val:.1f}%)")
        print()
        print("-" * 50)
        print()

    # Summary table
    print("=" * 75)
    print("SUMMARY: BRUNSCHWIG -> VOYNICH A REGISTER MAPPING")
    print("=" * 75)
    print()

    print(f"{'Brunschwig Product':<25} {'Degree':<8} {'-> A Signature':<20} {'Key PREFIX':<15}")
    print("-" * 75)

    for name, prod in sorted(BRUNSCHWIG_PRODUCTS.items(), key=lambda x: x[1]['degree']):
        expected = prod['expected_type']

        # Get most distinctive prefix for this type
        if expected == 'WATER_GENTLE':
            key_prefix = "ok+ ch-"
        elif expected == 'WATER_STANDARD':
            key_prefix = "ch baseline"
        elif expected == 'OIL_RESIN':
            key_prefix = "d+ y-"
        elif expected == 'PRECISION':
            key_prefix = "ch+ d-"
        else:
            key_prefix = "?"

        print(f"{prod['german']:<25} {prod['degree']:<8} {expected:<20} {key_prefix:<15}")

    print()
    print("-" * 75)
    print()
    print("INTERPRETATION:")
    print()
    print("If you have a Brunschwig recipe, you can predict what A register")
    print("pattern it would 'light up' in the Voynich:")
    print()
    print("  1. Identify the degree (1-4) and method (balneum, moderate, seething, dry)")
    print("  2. Map to product type (WATER_GENTLE, WATER_STANDARD, OIL_RESIN, PRECISION)")
    print("  3. Look for A records with the corresponding PREFIX signature")
    print("  4. Those A records should contain MIDDLEs exclusive to that product type")
    print()
    print("This completes the backward chain:")
    print("  Brunschwig recipe -> Product type -> REGIME -> B folio -> A register")

if __name__ == '__main__':
    main()
