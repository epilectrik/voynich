#!/usr/bin/env python3
"""
Analyze the 31 A-exclusive MIDDLEs that appear in AZC but never reach B.

These are "AZC-terminal" - they pass through AZC but stop there.
Why don't they propagate to B?
"""

import json
import csv
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
RESULTS_PATH = Path(__file__).parent.parent / 'results'

# Load the middle classes data
with open(RESULTS_PATH / 'middle_classes.json') as f:
    data = json.load(f)

AZC_TERMINAL = set(data['a_exclusive_in_azc'])  # 31 MIDDLEs
A_EXCLUSIVE = set(data['a_exclusive_middles'])  # 349 MIDDLEs
A_SHARED = set(data['a_shared_middles'])  # 268 MIDDLEs

print("=" * 70)
print("ANALYZING AZC-TERMINAL MIDDLEs")
print("=" * 70)
print(f"\nAZC-terminal count: {len(AZC_TERMINAL)}")
print(f"A-exclusive NOT in AZC: {len(A_EXCLUSIVE - AZC_TERMINAL)}")
print()

# Standard PREFIX list
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
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


# AZC folios
AZC_FOLIOS = ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73', 'f57']

# Collect data on AZC-terminal MIDDLEs
azc_terminal_tokens = []  # Tokens in AZC with these MIDDLEs
azc_terminal_in_a = []    # Tokens in A with these MIDDLEs

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')

    for row in reader:
        if row.get('transcriber') != 'H':
            continue

        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')
        lang = row.get('language', '')
        placement = row.get('placement', '')

        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_middle(word)
        if middle is None:
            continue

        if middle in AZC_TERMINAL:
            # Check if in AZC folio
            is_azc = any(folio.lower().startswith(af) for af in AZC_FOLIOS)

            if is_azc:
                azc_terminal_tokens.append({
                    'token': word,
                    'folio': folio,
                    'middle': middle,
                    'prefix': prefix,
                    'suffix': suffix,
                    'placement': placement,
                    'lang': lang,
                })
            elif lang == 'A':
                azc_terminal_in_a.append({
                    'token': word,
                    'folio': folio,
                    'middle': middle,
                    'prefix': prefix,
                    'suffix': suffix,
                })

print("=" * 70)
print("AZC-TERMINAL MIDDLEs IN AZC FOLIOS")
print("=" * 70)
print(f"\nToken instances in AZC: {len(azc_terminal_tokens)}")
print(f"Token instances in A (non-AZC): {len(azc_terminal_in_a)}")
print()

# List them
print("The 31 AZC-terminal MIDDLEs:")
for m in sorted(AZC_TERMINAL):
    azc_count = sum(1 for t in azc_terminal_tokens if t['middle'] == m)
    a_count = sum(1 for t in azc_terminal_in_a if t['middle'] == m)
    freq = data['middle_frequencies'].get(m, 0)
    print(f"  {m:15} | A freq: {freq:3} | In AZC: {azc_count:2} | In A(non-AZC): {a_count:2}")

# Analyze placement codes in AZC
print()
print("=" * 70)
print("PLACEMENT DISTRIBUTION IN AZC")
print("=" * 70)

placement_counts = Counter(t['placement'] for t in azc_terminal_tokens)
print(f"\nPlacement codes for AZC-terminal tokens:")
for p, count in placement_counts.most_common():
    print(f"  {p:10}: {count} ({100*count/len(azc_terminal_tokens):.1f}%)")

# Compare with shared MIDDLEs in AZC
shared_in_azc_tokens = []
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')

    for row in reader:
        if row.get('transcriber') != 'H':
            continue

        word = row.get('word', '').strip().lower()
        folio = row.get('folio', '')
        placement = row.get('placement', '')

        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_middle(word)
        if middle is None:
            continue

        is_azc = any(folio.lower().startswith(af) for af in AZC_FOLIOS)
        if is_azc and middle in A_SHARED:
            shared_in_azc_tokens.append({
                'token': word,
                'middle': middle,
                'prefix': prefix,
                'suffix': suffix,
                'placement': placement,
            })

print()
print("Placement codes for A/B-shared MIDDLEs in AZC:")
shared_placement = Counter(t['placement'] for t in shared_in_azc_tokens)
for p, count in shared_placement.most_common():
    print(f"  {p:10}: {count} ({100*count/len(shared_in_azc_tokens):.1f}%)")

# Analyze PREFIX distribution
print()
print("=" * 70)
print("PREFIX DISTRIBUTION")
print("=" * 70)

terminal_prefixes = Counter(t['prefix'] for t in azc_terminal_tokens)
shared_prefixes = Counter(t['prefix'] for t in shared_in_azc_tokens)

print("\nAZC-terminal MIDDLEs:")
for p, count in terminal_prefixes.most_common(10):
    pct = 100 * count / len(azc_terminal_tokens) if azc_terminal_tokens else 0
    print(f"  {p:6}: {count:3} ({pct:.1f}%)")

print("\nA/B-shared MIDDLEs in AZC:")
for p, count in shared_prefixes.most_common(10):
    pct = 100 * count / len(shared_in_azc_tokens) if shared_in_azc_tokens else 0
    print(f"  {p:6}: {count:3} ({pct:.1f}%)")

# Analyze SUFFIX distribution
print()
print("=" * 70)
print("SUFFIX DISTRIBUTION")
print("=" * 70)

terminal_suffixes = Counter(t['suffix'] for t in azc_terminal_tokens)
shared_suffixes = Counter(t['suffix'] for t in shared_in_azc_tokens)

print("\nAZC-terminal MIDDLEs:")
for s, count in terminal_suffixes.most_common(10):
    suffix_label = s if s else '(none)'
    pct = 100 * count / len(azc_terminal_tokens) if azc_terminal_tokens else 0
    print(f"  {suffix_label:10}: {count:3} ({pct:.1f}%)")

print("\nA/B-shared MIDDLEs in AZC:")
for s, count in shared_suffixes.most_common(10):
    suffix_label = s if s else '(none)'
    pct = 100 * count / len(shared_in_azc_tokens) if shared_in_azc_tokens else 0
    print(f"  {suffix_label:10}: {count:3} ({pct:.1f}%)")

# Analyze folio distribution
print()
print("=" * 70)
print("FOLIO DISTRIBUTION IN AZC")
print("=" * 70)

terminal_folios = Counter(t['folio'] for t in azc_terminal_tokens)
print("\nAZC-terminal tokens by folio:")
for f, count in terminal_folios.most_common():
    print(f"  {f:10}: {count}")

# Language classification in AZC
print()
print("=" * 70)
print("LANGUAGE CLASSIFICATION IN AZC")
print("=" * 70)

terminal_langs = Counter(t['lang'] for t in azc_terminal_tokens)
print("\nAZC-terminal tokens by Currier language:")
for lang, count in terminal_langs.most_common():
    print(f"  {lang}: {count} ({100*count/len(azc_terminal_tokens):.1f}%)")

# Detailed token list
print()
print("=" * 70)
print("SAMPLE TOKENS")
print("=" * 70)
print("\nFirst 20 AZC-terminal tokens in AZC:")
for t in azc_terminal_tokens[:20]:
    print(f"  {t['token']:20} | folio: {t['folio']:8} | placement: {t['placement']:5} | lang: {t['lang']}")

# Save results
output = {
    'azc_terminal_middles': sorted(list(AZC_TERMINAL)),
    'azc_terminal_token_count': len(azc_terminal_tokens),
    'azc_terminal_a_count': len(azc_terminal_in_a),
    'placement_distribution': dict(placement_counts),
    'prefix_distribution': dict(terminal_prefixes),
    'suffix_distribution': dict(terminal_suffixes),
    'folio_distribution': dict(terminal_folios),
    'language_distribution': dict(terminal_langs),
    'tokens': azc_terminal_tokens,
}

with open(RESULTS_PATH / 'azc_terminal_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nSaved to {RESULTS_PATH / 'azc_terminal_analysis.json'}")
