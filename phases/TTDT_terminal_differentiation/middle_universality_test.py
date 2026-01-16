#!/usr/bin/env python3
"""
MIDDLE Universality Test

Question: Within each B folio's ~100 MIDDLEs, how many are:
- Unique (only this folio)
- Rare (2-5 folios)
- Common (6-20 folios)
- Universal (20+ folios)

This tests whether B folios contain:
- Universal product types (shared MIDDLEs)
- Material-specific variants (unique MIDDLEs)
"""

import json
import csv
import statistics
from pathlib import Path
from collections import defaultdict, Counter

BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
RESULTS_PATH = BASE_PATH / "results"
OUTPUT_FILE = RESULTS_PATH / "middle_universality.json"

# Morphological parsing
PREFIXES = ['qo', 'ch', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'lk', 'lch', 'yk', 'yt', 'ke', 'sa', 'so', 'al', 'op', 'lo']
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]


def decompose_token(token):
    """Extract MIDDLE from token."""
    if not token or len(token) < 2:
        return None
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None

    rest = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            rest = token[len(p):]
            break

    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            middle = rest[:-len(s)]
            break

    return middle if middle else None


def load_b_folios():
    """Load B folio tokens."""
    with open(RESULTS_PATH / "unified_folio_profiles.json") as f:
        profiles = json.load(f)
    b_folios = set(f for f, p in profiles["profiles"].items() if p.get("system") == "B")

    folio_tokens = defaultdict(list)
    with open(DATA_FILE, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            folio = row['folio']
            word = row['word'].strip('"')
            lang = row['language']
            if lang == 'B' and folio in b_folios:
                folio_tokens[folio].append(word)

    return folio_tokens, b_folios


def main():
    print("=" * 70)
    print("MIDDLE UNIVERSALITY TEST")
    print("=" * 70)

    folio_tokens, b_folios = load_b_folios()
    print(f"\nB folios: {len(folio_tokens)}")

    # Step 1: Extract MIDDLEs per folio
    folio_middles = {}
    for folio, tokens in folio_tokens.items():
        middles = set()
        for token in tokens:
            middle = decompose_token(token)
            if middle:
                middles.add(middle)
        folio_middles[folio] = middles

    # Step 2: Count how many folios each MIDDLE appears in
    middle_folio_count = Counter()
    for folio, middles in folio_middles.items():
        for middle in middles:
            middle_folio_count[middle] += 1

    # Step 3: Classify MIDDLEs by universality
    def classify_middle(count):
        if count == 1:
            return 'UNIQUE'
        elif count <= 5:
            return 'RARE'
        elif count <= 20:
            return 'COMMON'
        else:
            return 'UNIVERSAL'

    middle_class = {m: classify_middle(c) for m, c in middle_folio_count.items()}

    # Global distribution
    class_counts = Counter(middle_class.values())
    print("\n" + "-" * 70)
    print("GLOBAL MIDDLE DISTRIBUTION")
    print("-" * 70)
    print(f"\n  Total unique MIDDLEs: {len(middle_folio_count)}")
    print(f"\n  By universality class:")
    for cls in ['UNIQUE', 'RARE', 'COMMON', 'UNIVERSAL']:
        count = class_counts[cls]
        pct = 100 * count / len(middle_folio_count)
        print(f"    {cls:10s}: {count:4d} ({pct:5.1f}%)")

    # Step 4: Analyze composition of each folio
    folio_composition = {}
    for folio, middles in folio_middles.items():
        composition = Counter()
        for middle in middles:
            composition[middle_class[middle]] += 1

        total = len(middles)
        folio_composition[folio] = {
            'total': total,
            'UNIQUE': composition['UNIQUE'],
            'RARE': composition['RARE'],
            'COMMON': composition['COMMON'],
            'UNIVERSAL': composition['UNIVERSAL'],
            'pct_unique': 100 * composition['UNIQUE'] / total if total > 0 else 0,
            'pct_universal': 100 * composition['UNIVERSAL'] / total if total > 0 else 0,
        }

    # Summary statistics
    print("\n" + "-" * 70)
    print("PER-FOLIO COMPOSITION")
    print("-" * 70)

    unique_pcts = [v['pct_unique'] for v in folio_composition.values()]
    universal_pcts = [v['pct_universal'] for v in folio_composition.values()]
    unique_counts = [v['UNIQUE'] for v in folio_composition.values()]
    universal_counts = [v['UNIVERSAL'] for v in folio_composition.values()]

    print(f"\n  UNIQUE MIDDLEs per folio (material-specific):")
    print(f"    Count: {min(unique_counts)}-{max(unique_counts)} (mean: {statistics.mean(unique_counts):.1f})")
    print(f"    Percent: {min(unique_pcts):.1f}%-{max(unique_pcts):.1f}% (mean: {statistics.mean(unique_pcts):.1f}%)")

    print(f"\n  UNIVERSAL MIDDLEs per folio (shared product types):")
    print(f"    Count: {min(universal_counts)}-{max(universal_counts)} (mean: {statistics.mean(universal_counts):.1f})")
    print(f"    Percent: {min(universal_pcts):.1f}%-{max(universal_pcts):.1f}% (mean: {statistics.mean(universal_pcts):.1f}%)")

    # Show example folios
    print("\n" + "-" * 70)
    print("EXAMPLE FOLIOS")
    print("-" * 70)

    # Sort by unique percentage
    sorted_folios = sorted(folio_composition.items(), key=lambda x: -x[1]['pct_unique'])

    print("\n  Highest material-specificity (most UNIQUE):")
    for folio, comp in sorted_folios[:3]:
        print(f"    {folio}: {comp['total']} MIDDLEs = {comp['UNIQUE']} unique ({comp['pct_unique']:.1f}%) + {comp['UNIVERSAL']} universal ({comp['pct_universal']:.1f}%)")

    print("\n  Lowest material-specificity (most UNIVERSAL):")
    for folio, comp in sorted_folios[-3:]:
        print(f"    {folio}: {comp['total']} MIDDLEs = {comp['UNIQUE']} unique ({comp['pct_unique']:.1f}%) + {comp['UNIVERSAL']} universal ({comp['pct_universal']:.1f}%)")

    # Step 5: What are the universal MIDDLEs?
    print("\n" + "-" * 70)
    print("TOP UNIVERSAL MIDDLEs (appear in 20+ folios)")
    print("-" * 70)

    universal_middles = [(m, c) for m, c in middle_folio_count.items() if c > 20]
    universal_middles.sort(key=lambda x: -x[1])

    print(f"\n  Total universal MIDDLEs: {len(universal_middles)}")
    print(f"\n  Top 15:")
    for middle, count in universal_middles[:15]:
        print(f"    '{middle}': {count} folios")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    avg_unique_pct = statistics.mean(unique_pcts)
    avg_universal_pct = statistics.mean(universal_pcts)

    print(f"\n  Average folio composition:")
    print(f"    {avg_unique_pct:.1f}% UNIQUE (material-specific variants)")
    print(f"    {avg_universal_pct:.1f}% UNIVERSAL (shared product types)")
    print(f"    {100 - avg_unique_pct - avg_universal_pct:.1f}% RARE/COMMON (partially shared)")

    print(f"\n  Model supported:")
    if avg_unique_pct > 30:
        print(f"    YES - Each folio has significant material-specific content")
        print(f"    ~{statistics.mean(unique_counts):.0f} unique MIDDLEs = material-specific products")
        print(f"    ~{statistics.mean(universal_counts):.0f} universal MIDDLEs = common product types")
    else:
        print(f"    NO - Folios are mostly shared, not material-specific")

    # Save results
    results = {
        'test': 'MIDDLE_UNIVERSALITY',
        'question': 'How many MIDDLEs are unique vs universal per B folio?',
        'global_distribution': {
            'total_middles': len(middle_folio_count),
            'UNIQUE': class_counts['UNIQUE'],
            'RARE': class_counts['RARE'],
            'COMMON': class_counts['COMMON'],
            'UNIVERSAL': class_counts['UNIVERSAL']
        },
        'per_folio_stats': {
            'unique_count': {
                'min': min(unique_counts),
                'max': max(unique_counts),
                'mean': statistics.mean(unique_counts),
                'median': statistics.median(unique_counts)
            },
            'unique_pct': {
                'min': min(unique_pcts),
                'max': max(unique_pcts),
                'mean': statistics.mean(unique_pcts)
            },
            'universal_count': {
                'min': min(universal_counts),
                'max': max(universal_counts),
                'mean': statistics.mean(universal_counts),
                'median': statistics.median(universal_counts)
            },
            'universal_pct': {
                'min': min(universal_pcts),
                'max': max(universal_pcts),
                'mean': statistics.mean(universal_pcts)
            }
        },
        'top_universal_middles': universal_middles[:20],
        'folio_details': {
            folio: comp for folio, comp in sorted_folios[:20]
        },
        'interpretation': {
            'avg_unique_pct': avg_unique_pct,
            'avg_universal_pct': avg_universal_pct,
            'model_supported': avg_unique_pct > 30
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUTPUT_FILE}")

    return results


if __name__ == '__main__':
    main()
