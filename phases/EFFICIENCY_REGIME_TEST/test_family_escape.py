#!/usr/bin/env python3
"""
Efficiency Regime Test 3: Family-Level Escape Transfer (CONFIRMATORY)

Question: Does family-level (not just folio-level) escape profile transfer to B?

Note: This is mostly confirmatory given F-AZC-016, but provides sanity check.

Method:
1. Group AZC folios by family (Zodiac vs A/C)
2. Calculate mean escape rate for vocabulary from each family
3. Track those tokens into B programs
4. Measure: does family-level escape profile persist?

Prediction:
- Zodiac-sourced tokens should show lower escape in B
- A/C-sourced tokens should show higher escape in B

Falsification:
- No family-level effect -> efficiency-regime structure not preserved in B
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
PROFILES_FILE = BASE_PATH / "results" / "unified_folio_profiles.json"
OUTPUT_FILE = BASE_PATH / "results" / "efficiency_regime_family_escape.json"

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


def load_token_azc_family() -> Dict[str, Dict]:
    """
    Map each token to its AZC family source (exclusive AC, exclusive Zodiac, or shared).
    """
    token_family = defaultdict(lambda: {'ac': 0, 'zodiac': 0, 'folios': set()})

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

            token_family[word]['folios'].add(folio)

            if folio in AC_FOLIOS:
                token_family[word]['ac'] += 1
            elif folio in ZODIAC_FOLIOS:
                token_family[word]['zodiac'] += 1

    # Classify tokens
    result = {}
    for token, data in token_family.items():
        if data['ac'] > 0 and data['zodiac'] == 0:
            family = 'AC_EXCLUSIVE'
        elif data['zodiac'] > 0 and data['ac'] == 0:
            family = 'ZODIAC_EXCLUSIVE'
        elif data['ac'] > 0 and data['zodiac'] > 0:
            family = 'SHARED'
        else:
            family = 'UNKNOWN'

        result[token] = {
            'family': family,
            'ac_count': data['ac'],
            'zodiac_count': data['zodiac'],
            'n_folios': len(data['folios'])
        }

    return result


def load_b_program_escape_rates() -> Dict[str, float]:
    """Load escape density for each B folio."""
    with open(PROFILES_FILE, 'r') as f:
        data = json.load(f)

    b_escape = {}
    for folio, profile in data['profiles'].items():
        if profile.get('system') == 'B' and profile.get('b_metrics'):
            escape = profile['b_metrics'].get('escape_density', 0)
            b_escape[folio] = escape

    return b_escape


def analyze_token_escape_by_family(token_family: Dict, b_escape: Dict) -> Dict:
    """
    Analyze escape rates in B for tokens by their AZC family source.
    """
    # Load B tokens and track their escape
    family_escape = {
        'AC_EXCLUSIVE': [],
        'ZODIAC_EXCLUSIVE': [],
        'SHARED': []
    }

    # Track tokens per family that appear in B
    family_b_presence = {
        'AC_EXCLUSIVE': 0,
        'ZODIAC_EXCLUSIVE': 0,
        'SHARED': 0
    }

    # Load B folio data
    folio_family_composition = defaultdict(lambda: {
        'ac': 0, 'zodiac': 0, 'shared': 0, 'no_azc': 0
    })

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language != 'B':
                continue

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            if folio not in b_escape:
                continue

            # Check token's AZC family
            if word in token_family:
                family = token_family[word]['family']
                if family == 'AC_EXCLUSIVE':
                    folio_family_composition[folio]['ac'] += 1
                    family_b_presence['AC_EXCLUSIVE'] += 1
                elif family == 'ZODIAC_EXCLUSIVE':
                    folio_family_composition[folio]['zodiac'] += 1
                    family_b_presence['ZODIAC_EXCLUSIVE'] += 1
                elif family == 'SHARED':
                    folio_family_composition[folio]['shared'] += 1
                    family_b_presence['SHARED'] += 1
            else:
                folio_family_composition[folio]['no_azc'] += 1

    # For each B folio, compute family composition and correlate with escape
    folio_data = []
    for folio, escape in b_escape.items():
        comp = folio_family_composition.get(folio, {'ac': 0, 'zodiac': 0, 'shared': 0, 'no_azc': 0})
        total = comp['ac'] + comp['zodiac'] + comp['shared']

        if total > 0:
            ac_frac = comp['ac'] / total
            zodiac_frac = comp['zodiac'] / total
        else:
            ac_frac = 0
            zodiac_frac = 0

        folio_data.append({
            'folio': folio,
            'escape': escape,
            'ac_fraction': ac_frac,
            'zodiac_fraction': zodiac_frac,
            'total_azc_tokens': total
        })

    # Compute correlation: AC fraction vs escape
    if len(folio_data) > 5:
        escapes = [d['escape'] for d in folio_data]
        ac_fracs = [d['ac_fraction'] for d in folio_data]
        zodiac_fracs = [d['zodiac_fraction'] for d in folio_data]

        n = len(folio_data)
        mean_esc = statistics.mean(escapes)
        mean_ac = statistics.mean(ac_fracs)
        mean_zod = statistics.mean(zodiac_fracs)

        # Correlation: escape vs ac_fraction
        cov_esc_ac = sum((e - mean_esc) * (a - mean_ac) for e, a in zip(escapes, ac_fracs)) / n
        var_esc = sum((e - mean_esc) ** 2 for e in escapes) / n
        var_ac = sum((a - mean_ac) ** 2 for a in ac_fracs) / n

        if var_esc > 0 and var_ac > 0:
            corr_esc_ac = cov_esc_ac / (var_esc ** 0.5 * var_ac ** 0.5)
        else:
            corr_esc_ac = 0

        # Correlation: escape vs zodiac_fraction
        cov_esc_zod = sum((e - mean_esc) * (z - mean_zod) for e, z in zip(escapes, zodiac_fracs)) / n
        var_zod = sum((z - mean_zod) ** 2 for z in zodiac_fracs) / n

        if var_esc > 0 and var_zod > 0:
            corr_esc_zod = cov_esc_zod / (var_esc ** 0.5 * var_zod ** 0.5)
        else:
            corr_esc_zod = 0
    else:
        corr_esc_ac = 0
        corr_esc_zod = 0

    return {
        'family_b_presence': family_b_presence,
        'n_folios': len(folio_data),
        'correlation_escape_vs_ac': round(corr_esc_ac, 3),
        'correlation_escape_vs_zodiac': round(corr_esc_zod, 3),
        'folio_samples': folio_data[:10]  # Sample
    }


def main():
    print("=" * 70)
    print("EFFICIENCY REGIME TEST 3: FAMILY-LEVEL ESCAPE TRANSFER")
    print("=" * 70)
    print("\nPriority: 3 (Confirmatory - sanity check given F-AZC-016)")
    print()

    # Load token -> AZC family mapping
    print("1. Loading token -> AZC family mapping...")
    token_family = load_token_azc_family()
    print(f"   Mapped {len(token_family)} tokens to AZC families")

    # Count by family
    family_counts = Counter(v['family'] for v in token_family.values())
    for family, count in sorted(family_counts.items()):
        print(f"   {family}: {count}")

    # Load B folio escape rates
    print("\n2. Loading B folio escape rates...")
    b_escape = load_b_program_escape_rates()
    print(f"   Found {len(b_escape)} B folios with escape data")

    # Analyze
    print("\n3. Analyzing escape by family source...")
    results = analyze_token_escape_by_family(token_family, b_escape)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\nTokens from each family appearing in B:")
    for family, count in results['family_b_presence'].items():
        print(f"   {family}: {count}")

    print(f"\nCorrelation analysis (N={results['n_folios']} B folios):")
    print(f"   Escape vs A/C fraction: r = {results['correlation_escape_vs_ac']}")
    print(f"   Escape vs Zodiac fraction: r = {results['correlation_escape_vs_zodiac']}")

    # Interpretation
    print("\n" + "=" * 70)
    print("TEST VERDICT")
    print("=" * 70)

    corr_ac = results['correlation_escape_vs_ac']
    corr_zod = results['correlation_escape_vs_zodiac']

    # Prediction: A/C -> higher escape (positive), Zodiac -> lower escape (negative)
    if corr_ac > 0.2 and corr_zod < -0.1:
        verdict = 'TEST_3_PASSED'
        interpretation = 'A/C tokens correlate with higher escape, Zodiac with lower'
    elif corr_ac > 0.1:
        verdict = 'TEST_3_PARTIAL'
        interpretation = 'A/C tokens show weak positive escape correlation'
    elif abs(corr_ac) < 0.1 and abs(corr_zod) < 0.1:
        verdict = 'TEST_3_FAILED'
        interpretation = 'No family-level escape effect detected'
    else:
        verdict = 'INCONCLUSIVE'
        interpretation = 'Mixed or unexpected pattern'

    print(f"\n>>> {verdict} <<<")
    print(f"    {interpretation}")

    # Save results
    output = {
        'test_id': 'EFFICIENCY_REGIME_TEST_3',
        'question': 'Does family-level escape profile transfer to B?',
        'prediction': 'A/C tokens -> higher escape, Zodiac tokens -> lower escape',
        'token_family_counts': dict(family_counts),
        'analysis': results,
        'verdict': {
            'overall': verdict,
            'interpretation': interpretation
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    main()
