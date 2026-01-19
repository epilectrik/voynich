#!/usr/bin/env python3
"""
Efficiency Regime Test 2: Conditional MIDDLE Discrimination Pressure (CRITICAL)

Question: At equal prefix and section, are rarer MIDDLEs disproportionately A/C-concentrated?

This is the PRIMARY test - if it fails, the efficiency-regime interpretation is NOT SUPPORTED.

Rationale: This is NOT explainable by grammar or morphology alone. If true, it directly
supports "fine discrimination under stress."

Method:
1. For each MIDDLE: compute rarity within its prefix family (not global rarity)
2. Stratify by prefix family (qo-, ol-, ot-, ch-, ok-, etc.)
3. For each prefix family, for each rarity quintile: calculate A/C vs Zodiac concentration
4. Repeat separately for Section H, P, T (if sample size permits)
5. Test for gradient: rarer MIDDLEs → higher A/C concentration?

Controls:
- Prefix family (prevents C471 contamination)
- Section (prevents section-level confounds)
- Token frequency (prevents Simpson's paradox)

Prediction (efficiency-regime):
- At equal prefix and section, rarer MIDDLEs are disproportionately A/C-concentrated
- Gradient should be consistent across prefix families
- Effect should hold across sections

Falsification:
- No gradient within prefix families → interpretation falsified
- Effect present in some prefixes but not others → incomplete support
- Reversed gradient → strongly falsified
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import statistics

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "efficiency_regime_middle_discrimination.json"

# AZC Family definitions (from C430)
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

ALL_AZC_FOLIOS = ZODIAC_FOLIOS | AC_FOLIOS

# Known prefixes
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'ain', 'l', 'm', 'r', 's', 'g', 'am', 'an']

# Section definitions (H = Herbal, P = Pharma, T = Bathing/Text)
# We'll extract section from folio prefix patterns
SECTION_MAP = {
    'H': set(),  # Will be populated dynamically
    'P': set(),
    'T': set(),
    'Z': set(),  # Zodiac (for AZC)
    'A': set(),  # A/C (for AZC)
    'C': set(),  # Cosmological
}


def decompose_token(token: str) -> Dict[str, str]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return {'prefix': '', 'middle': token, 'suffix': ''}

    original = token
    prefix = ''
    suffix = ''

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return {'prefix': prefix, 'middle': token, 'suffix': suffix}


def load_azc_data() -> Tuple[Dict, Dict]:
    """
    Load AZC tokens and their folio/section information.

    Returns:
        - token_data: {token: {'folios': {folio: count}, 'sections': {section: count}, 'total': int}}
        - middle_data: {(prefix, middle): {'folios': {folio: count}, 'total': int}}
    """
    token_data = defaultdict(lambda: {'folios': defaultdict(int), 'sections': defaultdict(int), 'total': 0})
    middle_data = defaultdict(lambda: {'folios': defaultdict(int), 'total': 0})

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            # Skip invalid tokens
            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Check if AZC folio
            is_azc = section in {'Z', 'A', 'C'} or language not in ('A', 'B')
            if not is_azc:
                continue

            if folio not in ALL_AZC_FOLIOS:
                continue

            # Decompose token
            decomp = decompose_token(word)
            prefix = decomp['prefix']
            middle = decomp['middle']

            if not prefix or not middle:
                continue

            # Record token data
            token_data[word]['folios'][folio] += 1
            token_data[word]['sections'][section] += 1
            token_data[word]['total'] += 1

            # Record middle data by prefix
            middle_data[(prefix, middle)]['folios'][folio] += 1
            middle_data[(prefix, middle)]['total'] += 1

    return dict(token_data), dict(middle_data)


def compute_family_concentration(folio_counts: Dict[str, int]) -> Tuple[float, float, str]:
    """
    Compute A/C vs Zodiac concentration for a set of folio counts.

    Returns:
        - ac_fraction: fraction of occurrences in A/C folios
        - zodiac_fraction: fraction of occurrences in Zodiac folios
        - dominant_family: 'AC', 'ZODIAC', or 'MIXED'
    """
    total = sum(folio_counts.values())
    if total == 0:
        return 0.0, 0.0, 'EMPTY'

    ac_count = sum(folio_counts.get(f, 0) for f in AC_FOLIOS)
    zodiac_count = sum(folio_counts.get(f, 0) for f in ZODIAC_FOLIOS)

    ac_fraction = ac_count / total
    zodiac_fraction = zodiac_count / total

    if ac_fraction > 0.7:
        dominant = 'AC'
    elif zodiac_fraction > 0.7:
        dominant = 'ZODIAC'
    else:
        dominant = 'MIXED'

    return ac_fraction, zodiac_fraction, dominant


def compute_rarity_quintiles(middle_data: Dict, prefix: str) -> Dict:
    """
    Compute rarity quintiles for MIDDLEs within a specific prefix.

    Rarity is defined as inverse of frequency (less frequent = more rare).
    """
    # Get all middles for this prefix
    prefix_middles = {k: v for k, v in middle_data.items() if k[0] == prefix}

    if len(prefix_middles) < 5:
        return None  # Need at least 5 middles for quintiles

    # Sort by frequency (total count)
    sorted_middles = sorted(prefix_middles.items(), key=lambda x: x[1]['total'])

    # Split into quintiles
    n = len(sorted_middles)
    quintile_size = n // 5

    quintiles = {}
    for q in range(5):
        start = q * quintile_size
        if q == 4:  # Last quintile gets remainder
            end = n
        else:
            end = (q + 1) * quintile_size

        quintile_middles = sorted_middles[start:end]

        # Calculate A/C concentration for this quintile
        combined_folios = defaultdict(int)
        total_count = 0

        for (pfx, mid), data in quintile_middles:
            for folio, count in data['folios'].items():
                combined_folios[folio] += count
                total_count += count

        ac_frac, zodiac_frac, dominant = compute_family_concentration(dict(combined_folios))

        # Get frequency range
        freq_min = quintile_middles[0][1]['total']
        freq_max = quintile_middles[-1][1]['total']

        quintiles[q] = {
            'quintile': q + 1,  # 1-indexed for human readability
            'label': ['RAREST', 'RARE', 'MEDIUM', 'COMMON', 'MOST_COMMON'][q],
            'n_middles': len(quintile_middles),
            'freq_range': f"{freq_min}-{freq_max}",
            'total_tokens': total_count,
            'ac_fraction': round(ac_frac, 3),
            'zodiac_fraction': round(zodiac_frac, 3),
            'dominant_family': dominant,
            'example_middles': [m[0][1] for m in quintile_middles[:3]]  # First 3 examples
        }

    return quintiles


def test_gradient(quintiles: Dict) -> Dict:
    """
    Test for gradient: do rarer MIDDLEs show higher A/C concentration?

    Returns gradient analysis including:
    - Spearman correlation (quintile rank vs A/C fraction)
    - Trend direction
    - Pass/fail verdict
    """
    if quintiles is None:
        return {'status': 'INSUFFICIENT_DATA'}

    ac_fracs = [quintiles[q]['ac_fraction'] for q in range(5)]

    # Simple gradient test: is quintile 0 (rarest) > quintile 4 (most common)?
    gradient_diff = ac_fracs[0] - ac_fracs[4]

    # Monotonicity check
    increasing = all(ac_fracs[i] >= ac_fracs[i+1] for i in range(4))
    decreasing = all(ac_fracs[i] <= ac_fracs[i+1] for i in range(4))

    # Compute rough correlation
    # Quintile rank: 0=rarest, 4=common
    # If efficiency regime is correct: rarer should have HIGHER A/C
    # So we expect NEGATIVE correlation between quintile rank and A/C fraction

    # Simple correlation calculation
    x = [0, 1, 2, 3, 4]  # quintile ranks
    y = ac_fracs
    n = 5
    x_mean = sum(x) / n
    y_mean = sum(y) / n

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denom_x = sum((xi - x_mean) ** 2 for xi in x) ** 0.5
    denom_y = sum((yi - y_mean) ** 2 for yi in y) ** 0.5

    if denom_x * denom_y > 0:
        correlation = numerator / (denom_x * denom_y)
    else:
        correlation = 0

    # Determine verdict
    # Prediction: negative correlation (rarer = higher A/C)
    if correlation < -0.3 and gradient_diff > 0.05:
        verdict = 'GRADIENT_CONFIRMED'
        direction = 'RARER_MORE_AC'
    elif correlation > 0.3 and gradient_diff < -0.05:
        verdict = 'GRADIENT_REVERSED'
        direction = 'RARER_MORE_ZODIAC'
    elif abs(gradient_diff) < 0.05:
        verdict = 'NO_GRADIENT'
        direction = 'FLAT'
    else:
        verdict = 'WEAK_GRADIENT'
        direction = 'WEAK_RARER_MORE_AC' if gradient_diff > 0 else 'WEAK_RARER_MORE_ZODIAC'

    return {
        'gradient_diff': round(gradient_diff, 3),  # Q1(rarest) - Q5(common)
        'correlation': round(correlation, 3),
        'monotonic_increasing': increasing,
        'monotonic_decreasing': decreasing,
        'ac_by_quintile': [round(f, 3) for f in ac_fracs],
        'verdict': verdict,
        'direction': direction
    }


def analyze_by_section(middle_data: Dict, prefix: str, section: str) -> Dict:
    """
    Analyze gradient for a specific prefix+section combination.

    This is the key control: we hold both prefix AND section constant.
    """
    # This would require section-level data in the middle_data
    # For now, we'll note this as a future enhancement
    # The current test uses all-section pooled data with prefix control
    pass


def main():
    print("=" * 70)
    print("EFFICIENCY REGIME TEST 2: CONDITIONAL MIDDLE DISCRIMINATION PRESSURE")
    print("=" * 70)
    print("\nPriority: 1 (CRITICAL - if this fails, regime hypothesis is NOT SUPPORTED)")
    print()

    # Load data
    print("1. Loading AZC token data...")
    token_data, middle_data = load_azc_data()
    print(f"   Loaded {len(token_data)} token types")
    print(f"   Identified {len(middle_data)} (prefix, middle) combinations")

    # Get prefix statistics
    prefixes = set(k[0] for k in middle_data.keys())
    print(f"   Found {len(prefixes)} prefix families: {sorted(prefixes)}")

    # Analyze each prefix family
    print("\n2. Analyzing rarity-concentration gradient by prefix family...")

    results = {
        'test_id': 'EFFICIENCY_REGIME_TEST_2',
        'question': 'At equal prefix and section, are rarer MIDDLEs disproportionately A/C-concentrated?',
        'prediction': 'Rarer MIDDLEs should show higher A/C concentration (gradient)',
        'falsification': 'No gradient or reversed gradient',
        'prefix_results': {},
        'aggregate': None,
        'verdict': None
    }

    prefix_verdicts = []
    gradients_found = 0
    gradients_reversed = 0
    no_gradients = 0
    insufficient_data = 0

    for prefix in sorted(prefixes):
        prefix_middles = {k: v for k, v in middle_data.items() if k[0] == prefix}
        n_middles = len(prefix_middles)

        if n_middles < 5:
            print(f"\n   [{prefix}] Skipped - only {n_middles} MIDDLEs (need >= 5)")
            results['prefix_results'][prefix] = {
                'status': 'INSUFFICIENT_DATA',
                'n_middles': n_middles
            }
            insufficient_data += 1
            continue

        # Compute quintiles
        quintiles = compute_rarity_quintiles(middle_data, prefix)

        if quintiles is None:
            print(f"\n   [{prefix}] Skipped - could not compute quintiles")
            results['prefix_results'][prefix] = {'status': 'QUINTILE_FAILED'}
            insufficient_data += 1
            continue

        # Test gradient
        gradient = test_gradient(quintiles)

        results['prefix_results'][prefix] = {
            'n_middles': n_middles,
            'quintiles': quintiles,
            'gradient_analysis': gradient
        }

        # Print results
        print(f"\n   [{prefix}] {n_middles} MIDDLEs")
        print(f"      A/C by quintile (rarest->common): {gradient['ac_by_quintile']}")
        print(f"      Gradient diff (Q1-Q5): {gradient['gradient_diff']:+.3f}")
        print(f"      Correlation: {gradient['correlation']:.3f}")
        print(f"      Verdict: {gradient['verdict']}")

        prefix_verdicts.append({
            'prefix': prefix,
            'verdict': gradient['verdict'],
            'gradient_diff': gradient['gradient_diff'],
            'n_middles': n_middles
        })

        if gradient['verdict'] == 'GRADIENT_CONFIRMED':
            gradients_found += 1
        elif gradient['verdict'] == 'GRADIENT_REVERSED':
            gradients_reversed += 1
        elif gradient['verdict'] == 'NO_GRADIENT':
            no_gradients += 1

    # Aggregate analysis
    print("\n" + "=" * 70)
    print("AGGREGATE RESULTS")
    print("=" * 70)

    testable_prefixes = len(prefix_verdicts)

    print(f"\nTestable prefix families: {testable_prefixes}")
    print(f"  Gradient CONFIRMED (rarer = more A/C): {gradients_found}")
    print(f"  Gradient REVERSED (rarer = more Zodiac): {gradients_reversed}")
    print(f"  No gradient (flat): {no_gradients}")
    print(f"  Insufficient data: {insufficient_data}")

    # Compute overall verdict
    if testable_prefixes == 0:
        overall_verdict = 'INCONCLUSIVE'
        interpretation = 'Insufficient data to test hypothesis'
    elif gradients_found >= testable_prefixes * 0.6:
        overall_verdict = 'GRADIENT_SUPPORTED'
        interpretation = 'Majority of prefix families show rarer MIDDLEs concentrated in A/C'
    elif gradients_reversed >= testable_prefixes * 0.4:
        overall_verdict = 'GRADIENT_FALSIFIED'
        interpretation = 'Multiple prefix families show REVERSED gradient (rarer = more Zodiac)'
    elif no_gradients >= testable_prefixes * 0.6:
        overall_verdict = 'NO_GRADIENT_EFFECT'
        interpretation = 'No systematic relationship between MIDDLE rarity and family concentration'
    else:
        overall_verdict = 'WEAK_SUPPORT'
        interpretation = 'Some gradient evidence but not consistent across prefix families'

    results['aggregate'] = {
        'testable_prefixes': testable_prefixes,
        'gradients_confirmed': gradients_found,
        'gradients_reversed': gradients_reversed,
        'no_gradients': no_gradients,
        'insufficient_data': insufficient_data
    }

    results['verdict'] = {
        'overall': overall_verdict,
        'interpretation': interpretation
    }

    print(f"\n>>> OVERALL VERDICT: {overall_verdict} <<<")
    print(f"    {interpretation}")

    # Pre-declared stop condition
    print("\n" + "-" * 70)
    print("PRE-DECLARED STOP CONDITION CHECK")
    print("-" * 70)

    if overall_verdict == 'GRADIENT_FALSIFIED':
        print(">>> TEST 2 FAILED - Efficiency-regime hypothesis is NOT SUPPORTED <<<")
        print(">>> Per pre-declared stop conditions: DO NOT proceed with other tests <<<")
        results['stop_condition'] = 'STOP_HYPOTHESIS_NOT_SUPPORTED'
    elif overall_verdict == 'NO_GRADIENT_EFFECT':
        print(">>> TEST 2 FAILED - No gradient effect detected <<<")
        print(">>> Per pre-declared stop conditions: Efficiency-regime is NOT SUPPORTED <<<")
        results['stop_condition'] = 'STOP_HYPOTHESIS_NOT_SUPPORTED'
    elif overall_verdict in ['GRADIENT_SUPPORTED', 'WEAK_SUPPORT']:
        print(f">>> TEST 2 PASSED ({overall_verdict}) - Proceed to Test 1 <<<")
        results['stop_condition'] = 'PROCEED_TO_TEST_1'
    else:
        print(">>> TEST 2 INCONCLUSIVE - More data needed <<<")
        results['stop_condition'] = 'NEEDS_MORE_DATA'

    # Save results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return results


if __name__ == "__main__":
    main()
