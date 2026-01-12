#!/usr/bin/env python3
"""
Efficiency Regime Test 4: Universal MIDDLE Negative Control (CRITICAL)

Question: Do Universal MIDDLEs (C462) show AZC family bias?

Rationale: Universal MIDDLEs work across ALL material classes and should therefore
work across ALL regimes. If they skew toward A/C, the regime story weakens dramatically.

Method:
1. Identify Universal MIDDLEs (those appearing in all 4 material classes)
2. Calculate their A/C vs Zodiac distribution in AZC folios
3. Compare to exclusive MIDDLEs

Prediction (efficiency-regime):
- Universal MIDDLEs should show NO family bias (near 50/50)
- Exclusive MIDDLEs should show strong family bias

Falsification:
- Universal MIDDLEs also skew A/C -> regime story fundamentally weakened
- No difference between universal and exclusive -> regime irrelevant to MIDDLE behavior
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import statistics

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "efficiency_regime_negative_control.json"

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

# Material class mapping (from C462)
PREFIX_TO_CLASS = {
    'ch': 'M-A', 'qo': 'M-A',
    'sh': 'M-B', 'ok': 'M-B',
    'da': 'M-C', 'ot': 'M-C',
    'ol': 'M-D', 'ct': 'M-D',
}

MATERIAL_CLASSES = {'M-A', 'M-B', 'M-C', 'M-D'}

# Known morphological patterns
KNOWN_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
KNOWN_SUFFIXES = ['y', 'dy', 'chy', 'shy', 'ain', 'aiin', 'in', 'n', 's', 'l', 'r', 'm']


def decompose_token(token: str) -> Dict[str, str]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return {'prefix': '', 'middle': token, 'suffix': ''}

    token = token.lower()
    prefix = ''
    suffix = ''

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    if not prefix:
        return {'prefix': '', 'middle': token, 'suffix': ''}

    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return {'prefix': prefix, 'middle': token, 'suffix': suffix}


def load_currier_a_data() -> Tuple[Dict, Dict]:
    """
    Load Currier A data to identify Universal vs Exclusive MIDDLEs.

    Returns:
        - middle_classes: {middle: set of material classes it appears in}
        - middle_tokens: {middle: list of tokens}
    """
    middle_classes = defaultdict(set)
    middle_tokens = defaultdict(list)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            language = row.get('language', '').strip()

            if language != 'A':
                continue

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            decomp = decompose_token(word)
            prefix = decomp['prefix']
            middle = decomp['middle']

            if not prefix or not middle:
                continue

            material_class = PREFIX_TO_CLASS.get(prefix)
            if material_class:
                middle_classes[middle].add(material_class)
                middle_tokens[middle].append(word)

    return dict(middle_classes), dict(middle_tokens)


def classify_middles(middle_classes: Dict) -> Tuple[Set, Set, Set]:
    """
    Classify MIDDLEs into Universal, Bridging, and Exclusive.

    Universal: appears in all 4 material classes
    Bridging: appears in 2-3 material classes
    Exclusive: appears in only 1 material class
    """
    universal = set()
    bridging = set()
    exclusive = set()

    for middle, classes in middle_classes.items():
        n_classes = len(classes)
        if n_classes == 4:
            universal.add(middle)
        elif n_classes >= 2:
            bridging.add(middle)
        else:
            exclusive.add(middle)

    return universal, bridging, exclusive


def compute_azc_family_distribution(middles: Set, middle_tokens: Dict) -> Dict:
    """
    Compute A/C vs Zodiac distribution for a set of MIDDLEs in AZC folios.
    """
    ac_count = 0
    zodiac_count = 0
    total_count = 0

    middle_family_dist = {}

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Check if AZC folio
            is_azc = section in {'Z', 'A', 'C'} or language not in ('A', 'B')
            if not is_azc or folio not in ALL_AZC_FOLIOS:
                continue

            decomp = decompose_token(word)
            middle = decomp['middle']

            if not middle or middle not in middles:
                continue

            total_count += 1

            if folio in AC_FOLIOS:
                ac_count += 1
                if middle not in middle_family_dist:
                    middle_family_dist[middle] = {'ac': 0, 'zodiac': 0}
                middle_family_dist[middle]['ac'] += 1
            elif folio in ZODIAC_FOLIOS:
                zodiac_count += 1
                if middle not in middle_family_dist:
                    middle_family_dist[middle] = {'ac': 0, 'zodiac': 0}
                middle_family_dist[middle]['zodiac'] += 1

    if total_count > 0:
        ac_fraction = ac_count / total_count
        zodiac_fraction = zodiac_count / total_count
    else:
        ac_fraction = 0
        zodiac_fraction = 0

    # Compute individual MIDDLE biases
    biases = []
    for middle, dist in middle_family_dist.items():
        m_total = dist['ac'] + dist['zodiac']
        if m_total >= 3:  # Minimum sample
            bias = dist['ac'] / m_total
            biases.append(bias)

    mean_bias = statistics.mean(biases) if biases else 0.5
    std_bias = statistics.stdev(biases) if len(biases) > 1 else 0

    return {
        'n_middles': len(middles),
        'n_middles_in_azc': len(middle_family_dist),
        'total_tokens': total_count,
        'ac_count': ac_count,
        'zodiac_count': zodiac_count,
        'ac_fraction': round(ac_fraction, 3),
        'zodiac_fraction': round(zodiac_fraction, 3),
        'mean_middle_ac_bias': round(mean_bias, 3),
        'std_middle_ac_bias': round(std_bias, 3),
        'per_middle': {m: d for m, d in list(middle_family_dist.items())[:10]}  # Sample
    }


def main():
    print("=" * 70)
    print("EFFICIENCY REGIME TEST 4: UNIVERSAL MIDDLE NEGATIVE CONTROL")
    print("=" * 70)
    print("\nPriority: 4 (Critical falsification guard)")
    print()

    # Load Currier A data to classify MIDDLEs
    print("1. Loading Currier A data to classify MIDDLEs...")
    middle_classes, middle_tokens = load_currier_a_data()
    print(f"   Found {len(middle_classes)} unique MIDDLEs")

    # Classify MIDDLEs
    print("\n2. Classifying MIDDLEs by material class coverage...")
    universal, bridging, exclusive = classify_middles(middle_classes)
    print(f"   Universal (4 classes): {len(universal)}")
    print(f"   Bridging (2-3 classes): {len(bridging)}")
    print(f"   Exclusive (1 class): {len(exclusive)}")

    # Compute AZC family distribution for each category
    print("\n3. Computing AZC family distribution...")

    print("\n   --- Universal MIDDLEs ---")
    universal_dist = compute_azc_family_distribution(universal, middle_tokens)
    print(f"   N in AZC: {universal_dist['n_middles_in_azc']}")
    print(f"   Total tokens: {universal_dist['total_tokens']}")
    print(f"   A/C fraction: {universal_dist['ac_fraction']}")
    print(f"   Zodiac fraction: {universal_dist['zodiac_fraction']}")
    print(f"   Mean per-MIDDLE A/C bias: {universal_dist['mean_middle_ac_bias']}")

    print("\n   --- Exclusive MIDDLEs ---")
    exclusive_dist = compute_azc_family_distribution(exclusive, middle_tokens)
    print(f"   N in AZC: {exclusive_dist['n_middles_in_azc']}")
    print(f"   Total tokens: {exclusive_dist['total_tokens']}")
    print(f"   A/C fraction: {exclusive_dist['ac_fraction']}")
    print(f"   Zodiac fraction: {exclusive_dist['zodiac_fraction']}")
    print(f"   Mean per-MIDDLE A/C bias: {exclusive_dist['mean_middle_ac_bias']}")

    print("\n   --- Bridging MIDDLEs (for comparison) ---")
    bridging_dist = compute_azc_family_distribution(bridging, middle_tokens)
    print(f"   N in AZC: {bridging_dist['n_middles_in_azc']}")
    print(f"   A/C fraction: {bridging_dist['ac_fraction']}")
    print(f"   Mean per-MIDDLE A/C bias: {bridging_dist['mean_middle_ac_bias']}")

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Key metric: difference in A/C bias between universal and exclusive
    universal_bias = universal_dist['mean_middle_ac_bias']
    exclusive_bias = exclusive_dist['mean_middle_ac_bias']
    bias_difference = exclusive_bias - universal_bias

    print(f"\nUniversal A/C bias: {universal_bias:.3f}")
    print(f"Exclusive A/C bias: {exclusive_bias:.3f}")
    print(f"Difference (exclusive - universal): {bias_difference:+.3f}")

    # Check predictions
    universal_is_balanced = abs(universal_bias - 0.5) < 0.1  # Within 10% of 50/50
    exclusive_is_biased = abs(exclusive_bias - 0.5) > 0.1  # More than 10% from 50/50
    hierarchy_preserved = bias_difference > 0.05  # Exclusive more A/C than Universal

    print(f"\nUniversal is balanced (within 10% of 50/50): {universal_is_balanced}")
    print(f"Exclusive is biased (>10% from 50/50): {exclusive_is_biased}")
    print(f"Hierarchy preserved (exclusive > universal): {hierarchy_preserved}")

    # Determine verdict
    print("\n" + "=" * 70)
    print("TEST VERDICT")
    print("=" * 70)

    if universal_is_balanced and exclusive_is_biased and hierarchy_preserved:
        verdict = 'NEGATIVE_CONTROL_PASSED'
        interpretation = 'Universal MIDDLEs are regime-neutral; Exclusive MIDDLEs show regime bias'
    elif not universal_is_balanced and universal_bias > 0.6:
        verdict = 'NEGATIVE_CONTROL_FAILED'
        interpretation = 'Universal MIDDLEs also skew A/C - regime story weakened'
    elif not exclusive_is_biased:
        verdict = 'NO_REGIME_EFFECT'
        interpretation = 'Neither category shows family bias - regime irrelevant to MIDDLE behavior'
    elif universal_bias > exclusive_bias:
        verdict = 'HIERARCHY_REVERSED'
        interpretation = 'Universal MIDDLEs MORE A/C-biased than exclusive - unexpected'
    else:
        verdict = 'INCONCLUSIVE'
        interpretation = 'Mixed results - partial regime effect'

    print(f"\n>>> {verdict} <<<")
    print(f"    {interpretation}")

    # Save results
    results = {
        'test_id': 'EFFICIENCY_REGIME_TEST_4',
        'question': 'Do Universal MIDDLEs (C462) show AZC family bias?',
        'prediction': 'Universal MIDDLEs should show no family bias (near 50/50)',
        'classification': {
            'universal': len(universal),
            'bridging': len(bridging),
            'exclusive': len(exclusive)
        },
        'distributions': {
            'universal': universal_dist,
            'bridging': bridging_dist,
            'exclusive': exclusive_dist
        },
        'analysis': {
            'universal_ac_bias': universal_bias,
            'exclusive_ac_bias': exclusive_bias,
            'bias_difference': round(bias_difference, 3),
            'universal_is_balanced': universal_is_balanced,
            'exclusive_is_biased': exclusive_is_biased,
            'hierarchy_preserved': hierarchy_preserved
        },
        'verdict': {
            'overall': verdict,
            'interpretation': interpretation
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return results


if __name__ == "__main__":
    main()
