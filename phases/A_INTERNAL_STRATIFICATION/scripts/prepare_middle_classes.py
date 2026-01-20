#!/usr/bin/env python3
"""
Prepare MIDDLE class data for A-Internal Stratification phase.

Establishes:
1. A-exclusive MIDDLEs (appear in A, never in B)
2. A/B-shared MIDDLEs (appear in both A and B)

Outputs comprehensive data structure for all subsequent tests.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
OUTPUT_PATH = Path(__file__).parent.parent / 'results' / 'middle_classes.json'

# Standard PREFIX list (8 marker classes from C235)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

# Extended prefixes (compound forms)
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]

ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]


def extract_middle(token):
    """Extract (prefix, middle, suffix) from token."""
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
        suffix = ''

    if middle == '':
        middle = '_EMPTY_'

    return prefix, middle, suffix


def get_section(folio):
    """Determine section (H, P, T) from folio name."""
    if not folio:
        return 'UNKNOWN'
    f = folio.lower()
    # Herbal section
    if any(f.startswith(x) for x in ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9']):
        if f < 'f26':
            return 'H'  # Herbal A (first part)
    # Pharma section
    if any(f.startswith(x) for x in ['f88', 'f89', 'f90', 'f99', 'f100', 'f101', 'f102', 'f103']):
        return 'P'
    # Text section
    if any(f.startswith(x) for x in ['f103', 'f104', 'f105', 'f106', 'f107', 'f108', 'f111', 'f112', 'f113', 'f114', 'f115', 'f116']):
        return 'T'
    # Default to H for Currier A folios
    return 'H'


def load_all_data():
    """Load comprehensive token data with all metadata."""
    import csv

    a_data = []  # Each token with full metadata
    b_middles = set()  # Just MIDDLEs for B (for classification)
    azc_data = []  # AZC tokens

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            # H-only filter
            transcriber = row.get('transcriber', '')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip().lower()
            folio = row.get('folio', '')
            line_num = row.get('line_number', '')
            lang = row.get('language', '')

            if not word or '*' in word:
                continue

            prefix, middle, suffix = extract_middle(word)

            if lang == 'A' and middle is not None:
                a_data.append({
                    'token': word,
                    'folio': folio,
                    'line': line_num,
                    'prefix': prefix,
                    'middle': middle,
                    'suffix': suffix,
                    'section': get_section(folio),
                })
            elif lang == 'B' and middle is not None:
                b_middles.add(middle)

            # Also collect AZC data (Zodiac folios)
            # AZC folios are the zodiac section: f70-f73, plus f67-f69
            azc_folios = ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73']
            if any(folio.lower().startswith(af) for af in azc_folios):
                if middle is not None:
                    azc_data.append({
                        'token': word,
                        'folio': folio,
                        'middle': middle,
                    })

    return a_data, b_middles, azc_data


def main():
    print("=" * 70)
    print("PREPARING MIDDLE CLASS DATA")
    print("=" * 70)
    print()

    print("Loading data...")
    a_data, b_middles, azc_data = load_all_data()
    print(f"  Currier A tokens (parsed): {len(a_data):,}")
    print(f"  Currier B unique MIDDLEs: {len(b_middles):,}")
    print(f"  AZC tokens: {len(azc_data):,}")
    print()

    # Get all A MIDDLEs
    a_middles = set(t['middle'] for t in a_data)
    azc_middles = set(t['middle'] for t in azc_data)

    # Classify
    a_exclusive = a_middles - b_middles
    a_shared = a_middles & b_middles

    print("=" * 70)
    print("MIDDLE CLASSIFICATION")
    print("=" * 70)
    print(f"  Total A MIDDLEs: {len(a_middles)}")
    print(f"  A-exclusive (never in B): {len(a_exclusive)} ({100*len(a_exclusive)/len(a_middles):.1f}%)")
    print(f"  A/B-shared: {len(a_shared)} ({100*len(a_shared)/len(a_middles):.1f}%)")
    print()

    # Calculate frequencies
    a_middle_freq = Counter(t['middle'] for t in a_data)

    # Token counts by class
    exclusive_token_count = sum(1 for t in a_data if t['middle'] in a_exclusive)
    shared_token_count = sum(1 for t in a_data if t['middle'] in a_shared)

    print(f"  A-exclusive token instances: {exclusive_token_count:,} ({100*exclusive_token_count/len(a_data):.1f}%)")
    print(f"  A/B-shared token instances: {shared_token_count:,} ({100*shared_token_count/len(a_data):.1f}%)")
    print()

    # AZC presence
    a_exclusive_in_azc = a_exclusive & azc_middles
    a_shared_in_azc = a_shared & azc_middles

    print(f"  A-exclusive MIDDLEs appearing in AZC: {len(a_exclusive_in_azc)} ({100*len(a_exclusive_in_azc)/len(a_exclusive):.1f}%)")
    print(f"  A/B-shared MIDDLEs appearing in AZC: {len(a_shared_in_azc)} ({100*len(a_shared_in_azc)/len(a_shared):.1f}%)")
    print()

    # Build entry-level data (group by folio+line)
    entries = defaultdict(list)
    for t in a_data:
        key = (t['folio'], t['line'])
        entries[key].append(t)

    # Classify entries
    entry_stats = []
    for (folio, line), tokens in entries.items():
        middles = [t['middle'] for t in tokens]
        exclusive_count = sum(1 for m in middles if m in a_exclusive)
        shared_count = sum(1 for m in middles if m in a_shared)

        if exclusive_count > 0 and shared_count == 0:
            composition = 'PURE_EXCLUSIVE'
        elif shared_count > 0 and exclusive_count == 0:
            composition = 'PURE_SHARED'
        else:
            composition = 'MIXED'

        entry_stats.append({
            'folio': folio,
            'line': line,
            'section': tokens[0]['section'],
            'n_tokens': len(tokens),
            'n_exclusive': exclusive_count,
            'n_shared': shared_count,
            'composition': composition,
            'tokens': tokens,
        })

    print(f"  Total entries: {len(entry_stats)}")
    comp_counts = Counter(e['composition'] for e in entry_stats)
    for comp, count in comp_counts.most_common():
        print(f"    {comp}: {count} ({100*count/len(entry_stats):.1f}%)")
    print()

    # Prepare output
    output = {
        'summary': {
            'a_total_middles': len(a_middles),
            'a_exclusive_count': len(a_exclusive),
            'a_shared_count': len(a_shared),
            'a_exclusive_pct': 100 * len(a_exclusive) / len(a_middles),
            'a_exclusive_token_instances': exclusive_token_count,
            'a_shared_token_instances': shared_token_count,
            'total_entries': len(entry_stats),
            'entry_composition': dict(comp_counts),
        },
        'a_exclusive_middles': sorted(list(a_exclusive)),
        'a_shared_middles': sorted(list(a_shared)),
        'a_exclusive_in_azc': sorted(list(a_exclusive_in_azc)),
        'a_shared_in_azc': sorted(list(a_shared_in_azc)),
        'middle_frequencies': {m: a_middle_freq[m] for m in a_middles},
        'azc_middles': sorted(list(azc_middles)),
    }

    # Save output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Saved to {OUTPUT_PATH}")

    # Also save entry data separately (larger file)
    entry_output_path = OUTPUT_PATH.parent / 'entry_data.json'
    with open(entry_output_path, 'w') as f:
        json.dump(entry_stats, f, indent=2)
    print(f"Saved entry data to {entry_output_path}")

    # Save token data
    token_output_path = OUTPUT_PATH.parent / 'token_data.json'
    # Add class to each token
    for t in a_data:
        t['middle_class'] = 'exclusive' if t['middle'] in a_exclusive else 'shared'
    with open(token_output_path, 'w') as f:
        json.dump(a_data, f, indent=2)
    print(f"Saved token data to {token_output_path}")

    return output


if __name__ == '__main__':
    main()
