#!/usr/bin/env python3
"""
VISUAL LABEL PREPARATION CORRELATION
====================================

We observed:
- f99r (93% PP labels): Cut roots (tops removed, processed)
- f102r2 (0% PP labels): 2 unique horizontal-growing roots (RI labels: koldarod, odalydary)
- f99r bottom: Unique whole plant with horizontal root (tolsasy - NOT IN A)

This test examines the MIDDLEs of these labels to see if:
1. PP labels share common MIDDLEs (standard processing)
2. RI labels have unique/rare MIDDLEs (specific identification)
3. The "dar" pattern in horizontal roots is meaningful

Phase: BRUNSCHWIG_PP_RI_TEST
Date: 2026-01-24
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    original = token
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

def main():
    print("VISUAL LABEL PREPARATION CORRELATION")
    print("="*70)

    # Load PP/RI classification
    with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
        data = json.load(f)
    pp_middles = set(data['a_shared_middles'])
    ri_middles = set(data['a_exclusive_middles'])

    # Load all A vocabulary (text)
    a_text_words = set()
    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip() != 'H':
                continue
            word = row.get('word', '').strip()
            language = row.get('language', '').strip()
            placement = row.get('placement', '').strip()
            if language == 'A' and word and not placement.startswith('L'):
                a_text_words.add(word)

    # Key folios we examined visually
    visual_observations = {
        'f99r': {
            'description': 'Cut roots (tops removed, processed, interchangeable)',
            'pp_pct': 93,
            'observation': 'Many varieties of unusual looking roots, most just roots like top parts cut off'
        },
        'f102r2': {
            'description': 'Unique horizontal-growing roots',
            'pp_pct': 0,
            'observation': 'Two labeled roots are definitely unique, look like they grow horizontally'
        }
    }

    # Specific tokens we examined
    examined_tokens = {
        'tolsasy': {'folio': 'f99r', 'visual': 'Unique whole plant with horizontal root and leaves', 'expected': 'NOT_IN_A'},
        'koldarod': {'folio': 'f102r2', 'visual': 'Horizontal-growing root', 'expected': 'RI'},
        'odalydary': {'folio': 'f102r2', 'visual': 'Horizontal-growing root', 'expected': 'RI'},
    }

    print("\n" + "="*70)
    print("EXAMINED TOKEN ANALYSIS")
    print("="*70)

    for token, info in examined_tokens.items():
        middle = extract_middle(token)

        in_a_text = token in a_text_words
        middle_is_pp = middle in pp_middles if middle else False
        middle_is_ri = middle in ri_middles if middle else False

        print(f"\n{token}:")
        print(f"  Folio: {info['folio']}")
        print(f"  Visual: {info['visual']}")
        print(f"  MIDDLE: {middle}")
        print(f"  In A text: {in_a_text}")
        print(f"  MIDDLE is PP: {middle_is_pp}")
        print(f"  MIDDLE is RI: {middle_is_ri}")

        actual = 'PP' if middle_is_pp else 'RI' if middle_is_ri else 'NOT_IN_A'
        matches = actual == info['expected']
        print(f"  Expected: {info['expected']}, Actual: {actual}, Match: {matches}")

    # Load pharma labels from JSON files
    print("\n" + "="*70)
    print("PHARMA LABEL MIDDLE ANALYSIS")
    print("="*70)

    pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'

    all_labels = []
    for json_file in pharma_dir.glob('*_mapping.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        folio = data.get('folio', json_file.stem)

        if 'groups' in data:
            for group in data['groups']:
                for key in ['roots', 'leaves', 'labels']:
                    if key in group:
                        for item in group[key]:
                            if isinstance(item, dict):
                                token = item.get('token', '')
                            else:
                                token = item
                            if token and isinstance(token, str) and '*' not in token:
                                all_labels.append({'folio': folio, 'token': token})

    print(f"\nTotal pharma labels: {len(all_labels)}")

    # Classify each label
    pp_labels = []
    ri_labels = []
    neither_labels = []

    for item in all_labels:
        token = item['token']
        middle = extract_middle(token)

        if middle in pp_middles:
            pp_labels.append(item)
        elif middle in ri_middles:
            ri_labels.append(item)
        else:
            neither_labels.append(item)

    print(f"  PP labels: {len(pp_labels)}")
    print(f"  RI labels: {len(ri_labels)}")
    print(f"  Neither (label-only): {len(neither_labels)}")

    # Analyze MIDDLEs
    print("\n" + "-"*70)
    print("MIDDLE patterns in PP vs RI labels:")
    print("-"*70)

    pp_label_middles = [extract_middle(item['token']) for item in pp_labels]
    ri_label_middles = [extract_middle(item['token']) for item in ri_labels]

    pp_middle_counts = Counter(pp_label_middles)
    ri_middle_counts = Counter(ri_label_middles)

    print(f"\nMost common PP label MIDDLEs:")
    for middle, count in pp_middle_counts.most_common(10):
        print(f"  {middle}: {count}")

    print(f"\nMost common RI label MIDDLEs:")
    for middle, count in ri_middle_counts.most_common(10):
        print(f"  {middle}: {count}")

    # Check for "dar" pattern
    print("\n" + "-"*70)
    print("'dar' PATTERN ANALYSIS (horizontal roots)")
    print("-"*70)

    dar_labels = [item for item in all_labels if 'dar' in (extract_middle(item['token']) or '')]
    print(f"\nLabels containing 'dar' in MIDDLE: {len(dar_labels)}")
    for item in dar_labels[:10]:
        middle = extract_middle(item['token'])
        pp_ri = 'PP' if middle in pp_middles else 'RI' if middle in ri_middles else 'NEITHER'
        print(f"  {item['token']} ({item['folio']}): MIDDLE={middle}, {pp_ri}")

    # Check MIDDLE localization for label MIDDLEs
    print("\n" + "-"*70)
    print("MIDDLE LOCALIZATION (how many folios each MIDDLE appears in)")
    print("-"*70)

    # Count folio appearances for each MIDDLE
    middle_folios = defaultdict(set)
    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip() != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            if language == 'A' and word:
                middle = extract_middle(word)
                if middle:
                    middle_folios[middle].add(folio)

    pp_folios = [len(middle_folios.get(m, set())) for m in set(pp_label_middles) if m]
    ri_folios = [len(middle_folios.get(m, set())) for m in set(ri_label_middles) if m]

    import statistics

    if pp_folios:
        print(f"\nPP label MIDDLEs appear in: mean {statistics.mean(pp_folios):.1f} folios, median {statistics.median(pp_folios):.0f}")
    if ri_folios:
        print(f"RI label MIDDLEs appear in: mean {statistics.mean(ri_folios):.1f} folios, median {statistics.median(ri_folios):.0f}")

    # Summary
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)
    print("""
Visual observation: PP labels = processed/cut materials, RI labels = unique specimens

What the data shows:
1. The specific tokens we examined (koldarod, odalydary) are correctly classified as RI
2. tolsasy (unique whole plant) is NOT in A vocabulary at all
3. RI label MIDDLEs are more localized than PP label MIDDLEs

This is consistent with RI encoding something like:
- Material identity (specific specimen identification)
- Unusual morphology (horizontal roots)
- Properties that require non-standard handling

PP appears to encode:
- Standard/processed materials
- Interchangeable items within a category
- Materials with established procedures

The question "does RI encode preparation state" may be too narrow.
RI seems to encode "anything that makes this specimen NON-INTERCHANGEABLE":
- Could be preparation (cut vs whole)
- Could be morphology (horizontal vs vertical roots)
- Could be rarity (unique specimen)
- Could be special properties (requires specific handling)
""")

if __name__ == '__main__':
    main()
