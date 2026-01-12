#!/usr/bin/env python3
"""
Probe 3: AZC Folio Unique Contribution Characterization

Question: What makes each AZC folio's constraint contribution unique?

Method:
1. For each AZC folio, extract vocabulary appearing ONLY in that folio
2. Decompose into PREFIX/MIDDLE/SUFFIX components
3. Look for patterns: does folio X have coherent morphological profile?

Prediction: Each folio's exclusive vocabulary should be morphologically coherent
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional

DATA_FILE = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
OUTPUT_FILE = Path("C:/git/voynich/results/integration_probe_azc_unique.json")

PREFIXES = ['ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct']
SUFFIXES = ['dy', 'ol', 'or', 'ar', 'al', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'ey', 'eey', 'chy', 'shy']

# AZC folio families
ZODIAC_FOLIOS = {
    'f70r1', 'f70r2', 'f70v1', 'f70v2',
    'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v', 'f57v'
}

AZC_SECTIONS = {'Z', 'A', 'C'}


def parse_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Parse token into PREFIX, MIDDLE, SUFFIX."""
    prefix = None
    for p in PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    suffix = None
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
        suffix = ''

    return prefix, middle if middle else '_EMPTY_', suffix


def load_azc_data(filepath: Path) -> Tuple[Dict, Set]:
    """Load AZC token data with folio mapping."""
    token_folios = defaultdict(set)
    azc_folios = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            is_azc = section in AZC_SECTIONS or language not in ('A', 'B')
            if is_azc:
                azc_folios.add(folio)
                token_folios[word].add(folio)

    return dict(token_folios), azc_folios


def get_folio_exclusive_vocab(token_folios: Dict) -> Dict[str, List[str]]:
    """Get tokens that appear in exactly one AZC folio."""
    folio_exclusive = defaultdict(list)

    for token, folios in token_folios.items():
        if len(folios) == 1:
            folio = list(folios)[0]
            folio_exclusive[folio].append(token)

    return dict(folio_exclusive)


def analyze_folio_morphology(tokens: List[str]) -> Dict:
    """Analyze morphological composition of a folio's exclusive vocabulary."""
    prefix_counts = Counter()
    middle_counts = Counter()
    suffix_counts = Counter()
    parseable = 0

    for token in tokens:
        prefix, middle, suffix = parse_token(token)
        if prefix:
            parseable += 1
            prefix_counts[prefix] += 1
            if middle:
                middle_counts[middle] += 1
            if suffix:
                suffix_counts[suffix] += 1

    # Calculate concentration metrics
    if parseable == 0:
        return {'parseable': 0, 'total': len(tokens)}

    # Dominant PREFIX
    top_prefix = prefix_counts.most_common(1)[0] if prefix_counts else (None, 0)
    prefix_concentration = top_prefix[1] / parseable if parseable > 0 else 0

    # Number of unique MIDDLEs
    n_middles = len(middle_counts)

    # Most common MIDDLEs
    top_middles = middle_counts.most_common(5)

    return {
        'total': len(tokens),
        'parseable': parseable,
        'prefix_counts': dict(prefix_counts),
        'dominant_prefix': top_prefix[0],
        'dominant_prefix_share': round(prefix_concentration * 100, 1),
        'n_unique_middles': n_middles,
        'top_middles': top_middles,
        'suffix_counts': dict(suffix_counts)
    }


def main():
    print("=" * 60)
    print("PROBE 3: AZC FOLIO UNIQUE CONTRIBUTION CHARACTERIZATION")
    print("=" * 60)

    # Load data
    print("\n1. Loading AZC token data...")
    token_folios, azc_folios = load_azc_data(DATA_FILE)
    print(f"   Loaded {len(token_folios)} tokens from {len(azc_folios)} AZC folios")

    # Get folio-exclusive vocabulary
    print("\n2. Extracting folio-exclusive vocabulary...")
    folio_exclusive = get_folio_exclusive_vocab(token_folios)

    total_exclusive = sum(len(v) for v in folio_exclusive.values())
    print(f"   Folio-exclusive tokens: {total_exclusive} ({total_exclusive/len(token_folios)*100:.1f}%)")

    # Analyze each folio
    print("\n3. Analyzing morphological composition...")
    results = {}

    for folio in sorted(azc_folios):
        tokens = folio_exclusive.get(folio, [])
        family = 'ZODIAC' if folio in ZODIAC_FOLIOS else 'AC'
        analysis = analyze_folio_morphology(tokens)
        analysis['family'] = family
        results[folio] = analysis

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print("\n--- Folio-Exclusive Token Counts ---")
    for folio in sorted(results.keys(), key=lambda f: -results[f]['total']):
        r = results[folio]
        if r['total'] == 0:
            continue
        prefix_str = r.get('dominant_prefix', '-')
        share = r.get('dominant_prefix_share', 0)
        family = r['family']
        n_middles = r.get('n_unique_middles', 0)
        print(f"  {folio} [{family}]: {r['total']:3d} tokens, "
              f"dominant: {prefix_str}- ({share}%), "
              f"{n_middles} unique MIDDLEs")

    # Aggregate by folio family
    print("\n--- Aggregate by Family ---")
    zodiac_exclusive = sum(r['total'] for f, r in results.items() if r['family'] == 'ZODIAC')
    ac_exclusive = sum(r['total'] for f, r in results.items() if r['family'] == 'AC')
    print(f"  ZODIAC exclusive tokens: {zodiac_exclusive}")
    print(f"  A/C exclusive tokens: {ac_exclusive}")

    # Analyze prefix concentration by family
    print("\n--- PREFIX Concentration by Family ---")

    zodiac_prefix_counts = Counter()
    ac_prefix_counts = Counter()

    for folio, r in results.items():
        if 'prefix_counts' not in r:
            continue
        if r['family'] == 'ZODIAC':
            zodiac_prefix_counts.update(r['prefix_counts'])
        else:
            ac_prefix_counts.update(r['prefix_counts'])

    print("\nZODIAC family exclusive token PREFIXes:")
    z_total = sum(zodiac_prefix_counts.values())
    for prefix, count in zodiac_prefix_counts.most_common():
        print(f"  {prefix}: {count} ({count/z_total*100:.1f}%)")

    print("\nA/C family exclusive token PREFIXes:")
    ac_total = sum(ac_prefix_counts.values())
    for prefix, count in ac_prefix_counts.most_common():
        print(f"  {prefix}: {count} ({count/ac_total*100:.1f}%)")

    # Look for morphological coherence
    print("\n--- Morphological Coherence Check ---")

    coherent_folios = []
    incoherent_folios = []

    for folio, r in results.items():
        if r['total'] < 5:
            continue
        if r.get('dominant_prefix_share', 0) >= 50:
            coherent_folios.append((folio, r['dominant_prefix'], r['dominant_prefix_share'], r['total']))
        else:
            incoherent_folios.append((folio, r['total'], dict(r.get('prefix_counts', {}))))

    print(f"\nFolios with coherent exclusive vocabulary (>50% single PREFIX):")
    for folio, prefix, share, total in sorted(coherent_folios, key=lambda x: -x[2])[:15]:
        print(f"  {folio}: {prefix}- ({share}% of {total} tokens)")

    print(f"\nFolios with diverse exclusive vocabulary (<50% single PREFIX):")
    for folio, total, counts in incoherent_folios[:10]:
        top_2 = Counter(counts).most_common(2)
        top_str = ', '.join([f"{p}({c})" for p, c in top_2])
        print(f"  {folio}: {total} tokens, top: {top_str}")

    # Final interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    coherence_rate = len(coherent_folios) / (len(coherent_folios) + len(incoherent_folios)) * 100 if (len(coherent_folios) + len(incoherent_folios)) > 0 else 0

    print(f"\nMorphological coherence rate: {coherence_rate:.1f}%")
    print(f"({len(coherent_folios)} coherent, {len(incoherent_folios)} diverse)")

    if coherence_rate > 60:
        print("\n>>> AZC folios have COHERENT exclusive vocabulary <<<")
        print("Each folio contributes a PREFIX-specific vocabulary subset")
        verdict = "COHERENT"
    elif coherence_rate > 40:
        print("\n>>> AZC folios show MIXED morphological patterns <<<")
        verdict = "MIXED"
    else:
        print("\n>>> AZC folios have DIVERSE exclusive vocabulary <<<")
        print("Folio identity is not strongly PREFIX-determined")
        verdict = "DIVERSE"

    # Save results
    output = {
        'probe': 'AZC_UNIQUE_MORPHOLOGY',
        'total_exclusive': total_exclusive,
        'exclusive_pct': round(total_exclusive / len(token_folios) * 100, 1),
        'coherent_folios': len(coherent_folios),
        'incoherent_folios': len(incoherent_folios),
        'coherence_rate': round(coherence_rate, 1),
        'zodiac_prefix_distribution': dict(zodiac_prefix_counts),
        'ac_prefix_distribution': dict(ac_prefix_counts),
        'verdict': verdict
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
