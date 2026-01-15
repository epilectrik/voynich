#!/usr/bin/env python3
"""
SIMPLE RECIPE IN COMPLEX FOLIO TEST

Critical test: Can the simplest Brunschwig recipe (first degree balneum marie)
fit in the most complex Voynich folio?

If YES: Curriculum complexity model confirmed
        (complex folios have MORE options, not DIFFERENT requirements)

If NO:  Intensity model was correct
        (complex folios require aggressive operations)
"""

from collections import Counter

# ============================================================
# LOAD REGIME DATA
# ============================================================

# Load folio profiles
folio_data = {}
with open('results/proposed_folio_order.txt', encoding='utf-8') as f:
    for line in f:
        parts = line.split('|')
        if len(parts) >= 3:
            folio = parts[1].strip()
            regime = parts[2].strip()
            if folio.startswith('f') and regime.startswith('REGIME'):
                folio_data[folio] = {'regime': regime}

# Load CEI values
import json
try:
    with open('results/unified_folio_profiles.json', 'r') as f:
        profiles = json.load(f)
    for folio, data in profiles.items():
        if folio in folio_data:
            folio_data[folio]['cei'] = data.get('cei', 0)
            folio_data[folio]['hazard'] = data.get('hazard_rate', 0)
            folio_data[folio]['escape'] = data.get('escape_rate', 0)
except:
    pass

# ============================================================
# REGIME CONSTRAINT PROFILES
# ============================================================

REGIME_PROFILES = {
    'REGIME_2': {
        'cei': 0.367,
        'description': 'Introductory complexity',
        'max_k_steps': 2,
        'max_h_steps': 1,
        'requires_link': True,
        'allows_high_impact': False,
    },
    'REGIME_1': {
        'cei': 0.510,
        'description': 'Core training complexity',
        'max_k_steps': 4,
        'max_h_steps': 2,
        'requires_link': True,
        'allows_high_impact': True,
    },
    'REGIME_4': {
        'cei': 0.584,
        'description': 'Precision training complexity',
        'max_k_steps': 3,
        'max_h_steps': 2,
        'requires_link': True,
        'allows_high_impact': False,
        'min_link_ratio': 0.25,
    },
    'REGIME_3': {
        'cei': 0.717,
        'description': 'Advanced training complexity',
        'max_k_steps': 6,
        'max_h_steps': 3,
        'requires_link': True,
        'allows_high_impact': True,
        'min_e_steps': 2,
    }
}

# ============================================================
# SIMPLEST BRUNSCHWIG RECIPE
# ============================================================

SIMPLE_BALNEUM_MARIE = {
    'name': 'First Degree Balneum Marie (Rose Water)',
    'description': 'Simplest possible distillation - gentle water bath',
    'brunschwig_degree': 1,
    'procedure': [
        ('AUX', 'Prepare flower petals'),
        ('FLOW', 'Load cucurbit'),
        ('AUX', 'Setup water bath'),
        ('k', 'Apply gentle heat'),
        ('LINK', 'Monitor temperature'),
        ('h', 'Vapor rises'),
        ('FLOW', 'Collect distillate'),
        ('LINK', 'Watch completion'),
        ('e', 'Cool system'),
    ]
}

# ============================================================
# COMPATIBILITY CHECK
# ============================================================

def check_compatibility(procedure_data, regime_name):
    """Check if a procedure fits within a REGIME's constraints."""
    regime = REGIME_PROFILES[regime_name]
    procedure = procedure_data['procedure']

    violations = []

    sequence = [step[0] for step in procedure]
    counts = Counter(sequence)

    k_count = counts.get('k', 0)
    h_count = counts.get('h', 0)
    e_count = counts.get('e', 0)
    link_count = counts.get('LINK', 0)
    high_count = counts.get('HIGH', 0)
    total = len(sequence)

    # Check limits
    max_k = regime.get('max_k_steps', 10)
    if k_count > max_k:
        violations.append(f"Too many k ops: {k_count} > {max_k}")

    max_h = regime.get('max_h_steps', 10)
    if h_count > max_h:
        violations.append(f"Too many h ops: {h_count} > {max_h}")

    if regime.get('requires_link', False) and link_count == 0:
        violations.append("Missing LINK phases")

    min_link_ratio = regime.get('min_link_ratio', 0)
    if min_link_ratio > 0:
        actual_ratio = link_count / total if total > 0 else 0
        if actual_ratio < min_link_ratio:
            violations.append(f"Insufficient monitoring: {actual_ratio:.2f} < {min_link_ratio}")

    if high_count > 0 and not regime.get('allows_high_impact', True):
        violations.append(f"HIGH_IMPACT not allowed: {high_count} found")

    min_e = regime.get('min_e_steps', 0)
    if e_count < min_e:
        violations.append(f"Insufficient e ops: {e_count} < {min_e}")

    # Check h -> k forbidden
    for i in range(len(sequence) - 1):
        if sequence[i] == 'h' and sequence[i+1] == 'k':
            violations.append(f"Forbidden h->k at step {i+1}")

    return {
        'fits': len(violations) == 0,
        'violations': violations,
        'stats': {
            'k': k_count, 'h': h_count, 'e': e_count,
            'LINK': link_count, 'HIGH': high_count, 'total': total
        }
    }

# ============================================================
# MAIN TEST
# ============================================================

def main():
    print("=" * 70)
    print("SIMPLE RECIPE IN COMPLEX FOLIO TEST")
    print("=" * 70)
    print()
    print("Question: Can the SIMPLEST Brunschwig recipe fit in the MOST COMPLEX folio?")
    print()
    print("If YES -> Complexity model: folios add OPTIONS, not REQUIREMENTS")
    print("If NO  -> Intensity model: complex folios need aggressive operations")
    print()

    # Show the simple recipe
    print("-" * 70)
    print("SIMPLEST RECIPE: First Degree Balneum Marie")
    print("-" * 70)
    recipe = SIMPLE_BALNEUM_MARIE
    print(f"Name: {recipe['name']}")
    print(f"Description: {recipe['description']}")
    print(f"Brunschwig degree: {recipe['brunschwig_degree']}")
    print()
    print("Procedure:")
    for step in recipe['procedure']:
        print(f"  {step[0]:6s} - {step[1]}")

    sequence = [s[0] for s in recipe['procedure']]
    counts = Counter(sequence)
    print()
    print(f"Stats: k={counts.get('k',0)}, h={counts.get('h',0)}, e={counts.get('e',0)}, "
          f"LINK={counts.get('LINK',0)}, HIGH={counts.get('HIGH',0)}")
    print()

    # Find most complex folio
    print("-" * 70)
    print("MOST COMPLEX FOLIO")
    print("-" * 70)

    regime3_folios = [(f, d) for f, d in folio_data.items() if d.get('regime') == 'REGIME_3']

    if regime3_folios:
        # Sort by CEI if available
        regime3_folios.sort(key=lambda x: x[1].get('cei', 0), reverse=True)
        most_complex = regime3_folios[0]
        print(f"Folio: {most_complex[0]}")
        print(f"REGIME: {most_complex[1]['regime']}")
        if 'cei' in most_complex[1]:
            print(f"CEI: {most_complex[1]['cei']:.3f}")
    else:
        print("No REGIME_3 folios found")

    print()
    print("REGIME_3 constraints:")
    r3 = REGIME_PROFILES['REGIME_3']
    print(f"  max_k_steps: {r3['max_k_steps']}")
    print(f"  max_h_steps: {r3['max_h_steps']}")
    print(f"  allows_high_impact: {r3['allows_high_impact']}")
    print(f"  min_e_steps: {r3.get('min_e_steps', 0)}")
    print()

    # THE TEST
    print("=" * 70)
    print("THE TEST: Simple Recipe vs Complex Folio (REGIME_3)")
    print("=" * 70)
    print()

    result = check_compatibility(recipe, 'REGIME_3')

    print(f"Recipe stats: k={result['stats']['k']}, h={result['stats']['h']}, "
          f"e={result['stats']['e']}, LINK={result['stats']['LINK']}")
    print()
    print(f"REGIME_3 limits: max_k=6, max_h=3, min_e=2, HIGH allowed")
    print()

    if result['fits']:
        print("RESULT: *** FITS ***")
        print()
        print("The simplest Brunschwig recipe FITS in the most complex folio!")
    else:
        print("RESULT: *** VIOLATES ***")
        print()
        print("Violations:")
        for v in result['violations']:
            print(f"  - {v}")

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if result['fits']:
        print("COMPLEXITY MODEL CONFIRMED")
        print()
        print("The simple recipe fits because REGIME_3 constraints are UPPER BOUNDS:")
        print(f"  - max_k=6 allows k={result['stats']['k']} (simple uses less)")
        print(f"  - max_h=3 allows h={result['stats']['h']} (simple uses less)")
        print(f"  - HIGH allowed but not required (simple doesn't use it)")
        print()
        print("The only potential issue: min_e_steps=2")
        print(f"  - Recipe has e={result['stats']['e']}")

        if result['stats']['e'] >= 2:
            print("  - PASSES: Simple recipe has enough stability steps")
        else:
            print("  - Would need to add one more cooling step for full compliance")
        print()
        print("CONCLUSION:")
        print("  Complex folios = MORE OPTIONS, not DIFFERENT REQUIREMENTS")
        print("  An apprentice learning on a complex folio can still do simple procedures")
        print("  The curriculum adds complexity gradually without invalidating basics")
    else:
        print("INTENSITY MODEL SUPPORTED")
        print()
        print("The simple recipe violates complex folio constraints.")
        print("This would mean complex folios REQUIRE certain operations,")
        print("not just ALLOW more options.")

    # Test all REGIMEs for completeness
    print()
    print("=" * 70)
    print("FULL REGIME COMPATIBILITY CHECK")
    print("=" * 70)
    print()
    print(f"{'REGIME':<12} {'Fits?':<8} {'Notes'}")
    print("-" * 50)

    for regime in ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']:
        result = check_compatibility(recipe, regime)
        status = "YES" if result['fits'] else "NO"
        notes = ", ".join(result['violations'][:2]) if result['violations'] else "Clean fit"
        print(f"{regime:<12} {status:<8} {notes}")

    print()
    print("-" * 70)
    print()

    # Count how many regimes the simple recipe fits
    fits_count = sum(1 for r in ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']
                     if check_compatibility(recipe, r)['fits'])

    print(f"Simple recipe fits {fits_count}/4 REGIMEs")
    print()

    if fits_count >= 3:
        print("STRONG SUPPORT for complexity model:")
        print("  Simple procedures are valid at multiple curriculum stages")
    elif fits_count == 2:
        print("PARTIAL SUPPORT:")
        print("  Simple procedures work at some stages but not others")
    else:
        print("WEAK SUPPORT:")
        print("  Simple procedures are heavily constrained by REGIME")

if __name__ == '__main__':
    main()
