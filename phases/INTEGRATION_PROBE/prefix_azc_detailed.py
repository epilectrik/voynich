#!/usr/bin/env python3
"""
Probe 1b: Detailed PREFIX -> AZC Folio Analysis

Following up on the signal: qo- and ct- concentrate in specific AZC folios.
Questions:
1. What AZC folio family (Zodiac vs A/C) do concentrated prefixes favor?
2. Do qo-concentrated folios share any characteristics?
3. Is there a PREFIX -> AZC family pattern?
"""

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List

DATA_FILE = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")

# PREFIX families
PREFIXES = ['ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct']

# AZC folio families (from C430)
# Family 0 (Zodiac): all 12 Z + f57v
ZODIAC_FOLIOS = {
    'f70r1', 'f70r2', 'f70v1', 'f70v2',  # Aries/Taurus
    'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',  # Zodiac
    'f73r', 'f73v',  # More zodiac
    'f57v'  # Associated with zodiac family
}

# Family 1 (A/C): 8 A + 6 C + 2 H + 1 S
# Everything else in AZC is A/C family


def load_data(filepath: Path) -> Dict:
    """Load token data with folio and section info."""
    token_data = defaultdict(lambda: {'folios': defaultdict(int), 'sections': set()})
    azc_folios = set()
    azc_sections = {'Z', 'A', 'C'}

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to H (PRIMARY) transcriber only
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            is_azc = section in azc_sections or language not in ('A', 'B')
            if is_azc:
                azc_folios.add(folio)
                token_data[word]['folios'][folio] += 1
                token_data[word]['sections'].add(section)

    return dict(token_data), azc_folios


def get_prefix(token: str) -> str:
    """Extract prefix from token."""
    for p in PREFIXES:
        if token.startswith(p):
            return p
    return 'OTHER'


def classify_folio_family(folio: str) -> str:
    """Classify folio as Zodiac or A/C family."""
    return 'ZODIAC' if folio in ZODIAC_FOLIOS else 'AC'


def analyze_prefix_family_affinity(token_data: Dict, azc_folios: Set[str]) -> Dict:
    """Analyze PREFIX -> AZC folio FAMILY affinity."""

    # Build PREFIX -> family distribution
    prefix_family = defaultdict(lambda: {'ZODIAC': 0, 'AC': 0})
    prefix_folio_detail = defaultdict(lambda: defaultdict(int))

    for token, data in token_data.items():
        prefix = get_prefix(token)
        if prefix == 'OTHER':
            continue

        for folio, count in data['folios'].items():
            family = classify_folio_family(folio)
            prefix_family[prefix][family] += count
            prefix_folio_detail[prefix][folio] += count

    # Calculate family ratios
    results = {}
    for prefix in PREFIXES:
        zodiac = prefix_family[prefix]['ZODIAC']
        ac = prefix_family[prefix]['AC']
        total = zodiac + ac

        if total == 0:
            continue

        # Get top folios by family
        folio_counts = prefix_folio_detail[prefix]
        zodiac_folios = [(f, c) for f, c in folio_counts.items() if classify_folio_family(f) == 'ZODIAC']
        ac_folios = [(f, c) for f, c in folio_counts.items() if classify_folio_family(f) == 'AC']

        zodiac_folios.sort(key=lambda x: -x[1])
        ac_folios.sort(key=lambda x: -x[1])

        results[prefix] = {
            'total': total,
            'zodiac_count': zodiac,
            'ac_count': ac,
            'zodiac_pct': round(zodiac / total * 100, 1),
            'ac_pct': round(ac / total * 100, 1),
            'zodiac_top_3': zodiac_folios[:3],
            'ac_top_3': ac_folios[:3]
        }

    return results


def analyze_f86_concentration(token_data: Dict) -> Dict:
    """Analyze why qo- concentrates in f86v* folios."""

    f86_folios = [f for f in ['f86v3', 'f86v4', 'f86v5', 'f86v6'] if True]
    qo_tokens = defaultdict(lambda: {'f86': 0, 'other': 0, 'folios': {}})

    for token, data in token_data.items():
        if not token.startswith('qo'):
            continue

        for folio, count in data['folios'].items():
            if folio.startswith('f86'):
                qo_tokens[token]['f86'] += count
            else:
                qo_tokens[token]['other'] += count
            qo_tokens[token]['folios'][folio] = count

    # Find qo- tokens that are f86-exclusive
    f86_exclusive = []
    f86_concentrated = []
    broadly_distributed = []

    for token, counts in qo_tokens.items():
        total = counts['f86'] + counts['other']
        f86_share = counts['f86'] / total if total > 0 else 0

        if f86_share == 1.0:
            f86_exclusive.append((token, counts['f86'], counts['folios']))
        elif f86_share > 0.7:
            f86_concentrated.append((token, counts['f86'], counts['other'], f86_share, counts['folios']))
        else:
            broadly_distributed.append((token, counts['f86'], counts['other'], f86_share))

    return {
        'f86_exclusive_count': len(f86_exclusive),
        'f86_exclusive_tokens': f86_exclusive[:10],
        'f86_concentrated_count': len(f86_concentrated),
        'f86_concentrated_tokens': f86_concentrated[:10],
        'broadly_distributed_count': len(broadly_distributed)
    }


def main():
    print("=" * 60)
    print("PROBE 1b: DETAILED PREFIX -> AZC ANALYSIS")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    token_data, azc_folios = load_data(DATA_FILE)
    print(f"Loaded {len(token_data)} tokens from {len(azc_folios)} AZC folios")

    # Count Zodiac vs A/C folios
    zodiac_count = len([f for f in azc_folios if f in ZODIAC_FOLIOS])
    ac_count = len(azc_folios) - zodiac_count
    print(f"Zodiac family: {zodiac_count} folios")
    print(f"A/C family: {ac_count} folios")

    # Analyze PREFIX -> Family affinity
    print("\n" + "=" * 60)
    print("PREFIX -> AZC FAMILY AFFINITY")
    print("=" * 60)

    family_results = analyze_prefix_family_affinity(token_data, azc_folios)

    for prefix in PREFIXES:
        if prefix not in family_results:
            continue
        r = family_results[prefix]
        print(f"\n{prefix.upper()}:")
        print(f"  Total: {r['total']:,}")
        print(f"  Zodiac: {r['zodiac_pct']}%  |  A/C: {r['ac_pct']}%")
        print(f"  Top Zodiac folios: {', '.join([f'{f}({c})' for f, c in r['zodiac_top_3']])}")
        print(f"  Top A/C folios: {', '.join([f'{f}({c})' for f, c in r['ac_top_3']])}")

    # Calculate expected ratio (by folio count)
    expected_zodiac = zodiac_count / len(azc_folios) * 100
    expected_ac = ac_count / len(azc_folios) * 100
    print(f"\nExpected by folio count: Zodiac {expected_zodiac:.1f}% | A/C {expected_ac:.1f}%")

    # Find deviations
    print("\n--- Deviations from Expected ---")
    for prefix in PREFIXES:
        if prefix not in family_results:
            continue
        r = family_results[prefix]
        z_dev = r['zodiac_pct'] - expected_zodiac
        if abs(z_dev) > 5:
            direction = "ZODIAC-enriched" if z_dev > 0 else "A/C-enriched"
            print(f"  {prefix.upper()}: {direction} ({z_dev:+.1f}pp)")

    # Analyze f86 concentration
    print("\n" + "=" * 60)
    print("QO- f86v CONCENTRATION ANALYSIS")
    print("=" * 60)

    f86_analysis = analyze_f86_concentration(token_data)

    print(f"\nqo- tokens exclusively in f86v*: {f86_analysis['f86_exclusive_count']}")
    print("Examples:")
    for token, count, folios in f86_analysis['f86_exclusive_tokens'][:5]:
        folio_str = ', '.join([f'{f}({c})' for f, c in sorted(folios.items(), key=lambda x: -x[1])])
        print(f"  {token}: {count} occurrences in {folio_str}")

    print(f"\nqo- tokens concentrated (>70%) in f86v*: {f86_analysis['f86_concentrated_count']}")
    print(f"qo- tokens broadly distributed: {f86_analysis['broadly_distributed_count']}")

    # Key insight
    print("\n" + "=" * 60)
    print("KEY INSIGHT")
    print("=" * 60)

    # Check qo family affinity
    if 'qo' in family_results:
        qo = family_results['qo']
        if qo['ac_pct'] > qo['zodiac_pct']:
            print(f"\nqo- is A/C-FAMILY CONCENTRATED ({qo['ac_pct']}% vs {qo['zodiac_pct']}% Zodiac)")
            print("This aligns with C430: A/C family has folio-specific scaffolds")
            print("qo- tokens appear in specific A/C folio constraint contexts")
        else:
            print(f"\nqo- is Zodiac-concentrated ({qo['zodiac_pct']}%)")

    # Check ct family affinity
    if 'ct' in family_results:
        ct = family_results['ct']
        if ct['zodiac_pct'] > ct['ac_pct']:
            print(f"\nct- is ZODIAC-CONCENTRATED ({ct['zodiac_pct']}% vs {ct['ac_pct']}% A/C)")
        else:
            print(f"\nct- is A/C-concentrated ({ct['ac_pct']}%)")


if __name__ == "__main__":
    main()
