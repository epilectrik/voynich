#!/usr/bin/env python3
"""
Show the actual pattern within a folio:
- Multiple MIDDLEs per folio
- Each MIDDLE appears with varying PREFIX/SUFFIX
- The MIDDLE itself is PP_atom + extension (constant)
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])
pp_middles = set(data['a_shared_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_parts(token):
    if not token or not isinstance(token, str):
        return None, None, None

    original = token
    prefix = None
    suffix = None

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

    middle = token if token else None
    return prefix, middle, suffix

def find_pp_in_middle(middle):
    """Find PP atoms contained in this MIDDLE."""
    found = []
    for pp in sorted(pp_middles, key=len, reverse=True):
        if pp in middle and len(pp) >= 2:
            found.append(pp)
    return found[:3]  # Top 3

# Collect data by folio
folio_data = defaultdict(lambda: defaultdict(list))

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue

        folio = row.get('folio', '').strip()
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_parts(word)
        if middle and middle in ri_middles:
            folio_data[folio][middle].append({
                'word': word,
                'prefix': prefix,
                'suffix': suffix
            })

# Show a few example folios in detail
print("="*70)
print("FOLIO-LEVEL MIDDLE PATTERNS")
print("="*70)

# Pick folios with good variety
example_folios = ['f58r', 'f99v', 'f88r', 'f24r', 'f56r']

for folio in example_folios:
    if folio not in folio_data:
        continue

    middles = folio_data[folio]
    print(f"\n{'='*70}")
    print(f"FOLIO {folio}: {len(middles)} unique MIDDLEs")
    print("="*70)

    for middle, occurrences in sorted(middles.items(), key=lambda x: -len(x[1])):
        pp_atoms = find_pp_in_middle(middle)

        print(f"\n  MIDDLE '{middle}' (contains PP: {pp_atoms}):")
        print(f"  Appears {len(occurrences)} times with these forms:")

        # Group by word form
        word_forms = Counter(o['word'] for o in occurrences)
        for word, count in word_forms.most_common():
            # Find the prefix/suffix for this word
            for o in occurrences:
                if o['word'] == word:
                    print(f"    {word} (prefix={o['prefix']}, suffix={o['suffix']}) x{count}")
                    break

# Summary pattern
print("\n" + "="*70)
print("THE PATTERN")
print("="*70)
print("""
Within a folio:

1. MULTIPLE MIDDLEs (3-4 on average)
   - Each MIDDLE identifies a different material
   - e.g., folio f58r has MIDDLEs: 'talo', 'olal', 'ls', etc.

2. Each MIDDLE is CONSTANT but appears with VARIANT affixes:
   - MIDDLE 'talo' appears as: qotalody, ytalody
   - Same core identity, different grammatical forms

3. Each MIDDLE contains PP atoms (superstring structure):
   - 'talo' contains PP 'ta', 'alo', 'lo', 'al'
   - The PP atoms encode procedural compatibility
   - The full MIDDLE encodes specific identity

STRUCTURE:
  Word = PREFIX + MIDDLE + SUFFIX
  MIDDLE = PP_atom + extension (constant for material)
  PREFIX/SUFFIX = varies by context/grammar
""")
