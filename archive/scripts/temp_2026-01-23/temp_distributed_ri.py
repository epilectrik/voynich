#!/usr/bin/env python3
"""
What are the highly distributed RI? They appear across many folios,
suggesting they're not specific materials but something else.
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Load PP/RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])
ri_middles = set(data['a_exclusive_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token or not isinstance(token, str):
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

# The distributed RI
distributed_ri = ['odaiin', 'ho', 'ols', 'eom', 'chol']

print("="*70)
print("DISTRIBUTED RI ANALYSIS")
print("="*70)

# Get all words containing these RI as MIDDLE
ri_words = defaultdict(list)

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue

        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        if not word or '*' in word:
            continue

        middle = extract_middle(word)
        if middle in distributed_ri:
            ri_words[middle].append({'word': word, 'folio': folio})

for ri in distributed_ri:
    words = ri_words.get(ri, [])
    print(f"\n{ri.upper()} ({len(words)} occurrences):")

    # Show word forms
    word_forms = Counter(w['word'] for w in words)
    print(f"  Word forms:")
    for wf, count in word_forms.most_common(10):
        print(f"    {wf}: {count}")

    # Show folio distribution
    folio_dist = Counter(w['folio'] for w in words)
    print(f"  Appears on {len(folio_dist)} folios")
    print(f"  Top folios: {folio_dist.most_common(5)}")

# Check if these contain PP atoms
print("\n" + "="*70)
print("DO DISTRIBUTED RI CONTAIN PP ATOMS?")
print("="*70)

for ri in distributed_ri:
    contained_pp = []
    for pp in pp_middles:
        if pp in ri and len(pp) >= 2:
            contained_pp.append(pp)
    print(f"  {ri}: contains PP atoms {contained_pp}")

# Check what the localized RI look like in comparison
print("\n" + "="*70)
print("COMPARISON: LOCALIZED RI STRUCTURE")
print("="*70)

# Get some examples of localized RI
ri_to_folios = defaultdict(set)

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

        middle = extract_middle(word)
        if middle and middle in ri_middles:
            ri_to_folios[middle].add(folio)

localized = [ri for ri, folios in ri_to_folios.items() if len(folios) == 1]

print(f"\nLocalized RI (1 folio only): {len(localized)}")
print("Examples:")
for ri in sorted(localized)[:15]:
    contained_pp = [pp for pp in pp_middles if pp in ri and len(pp) >= 2]
    print(f"  {ri}: contains PP {contained_pp}")

# Hypothesis
print("\n" + "="*70)
print("HYPOTHESIS")
print("="*70)
print("""
Two types of RI observed:

1. LOCALIZED RI (123 items, 71%):
   - Appear on 1-2 folios
   - Likely encode SPECIFIC MATERIALS
   - Structure: PP_atom + specific_extension

2. DISTRIBUTED RI (5 items, appearing on 10+ folios):
   - odaiin (43 folios), ho (25), ols (12), eom (11), chol (11)
   - Too widespread to be specific materials
   - May encode:
     a) CATEGORY or CLASS markers
     b) PROCESSING/PREPARATION state
     c) Common MODIFIER that applies to many materials
     d) Structural/grammatical element

These distributed RI might be:
   "dried" - applies to many plants
   "root" - a part type across many plants
   "spring harvest" - a timing across many plants
""")
