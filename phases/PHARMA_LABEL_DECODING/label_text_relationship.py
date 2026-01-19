"""
CURRIER-A-LABEL-TEXT-RELATIONSHIP Analysis

Analyzes how Currier A labels relate to Currier A text:
1. Morphological comparison (same PREFIX+MIDDLE+SUFFIX structure?)
2. MIDDLE overlap (label-exclusive MIDDLEs?)
3. Jar vs root differentiation
4. Section distribution
5. Folio co-occurrence
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
F99R_PATH = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING' / 'f99r_jar_root_mapping.json'
OUTPUT_PATH = PROJECT_ROOT / 'results' / 'label_text_relationship.json'

# Morphology parsing (from MIDDLE_AB analysis)
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


def parse_morphology(token):
    """Parse token into (prefix, middle, suffix). Returns (None, None, None) if unparseable."""
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


def load_data():
    """Load H-only Currier A data, separated by placement type."""
    labels = []  # placement starts with 'L'
    text = []    # placement starts with 'P'

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            transcriber = parts[12].strip('"')
            if transcriber != 'H':
                continue

            language = parts[6].strip('"')
            if language != 'A':
                continue

            word = parts[0].strip('"').lower()
            if not word or '*' in word:
                continue

            placement = parts[10].strip('"')
            section = parts[3].strip('"')
            folio = parts[2].strip('"')

            row_data = {
                'word': word,
                'placement': placement,
                'section': section,
                'folio': folio
            }

            if placement.startswith('L'):
                labels.append(row_data)
            elif placement.startswith('P'):
                text.append(row_data)

    return labels, text


def test1_morphological_comparison(labels, text):
    """Compare morphology parse success rates."""
    print("\n" + "=" * 60)
    print("TEST 1: MORPHOLOGICAL COMPARISON")
    print("=" * 60)

    label_types = set(r['word'] for r in labels)
    text_types = set(r['word'] for r in text)

    # Parse labels
    label_parsed = 0
    label_prefixes = Counter()
    label_suffixes = Counter()
    for word in label_types:
        prefix, middle, suffix = parse_morphology(word)
        if prefix:
            label_parsed += 1
            label_prefixes[prefix] += 1
            label_suffixes[suffix] += 1

    # Parse text
    text_parsed = 0
    text_prefixes = Counter()
    text_suffixes = Counter()
    for word in text_types:
        prefix, middle, suffix = parse_morphology(word)
        if prefix:
            text_parsed += 1
            text_prefixes[prefix] += 1
            text_suffixes[suffix] += 1

    label_rate = label_parsed / len(label_types) if label_types else 0
    text_rate = text_parsed / len(text_types) if text_types else 0

    print(f"\nLabel types: {len(label_types)}")
    print(f"  Parsed: {label_parsed} ({label_rate:.1%})")
    print(f"  Top prefixes: {label_prefixes.most_common(5)}")
    print(f"  Top suffixes: {label_suffixes.most_common(5)}")

    print(f"\nText types: {len(text_types)}")
    print(f"  Parsed: {text_parsed} ({text_rate:.1%})")
    print(f"  Top prefixes: {text_prefixes.most_common(5)}")
    print(f"  Top suffixes: {text_suffixes.most_common(5)}")

    return {
        'label_types': len(label_types),
        'label_parsed': label_parsed,
        'label_parse_rate': label_rate,
        'label_top_prefixes': label_prefixes.most_common(10),
        'label_top_suffixes': label_suffixes.most_common(10),
        'text_types': len(text_types),
        'text_parsed': text_parsed,
        'text_parse_rate': text_rate,
        'text_top_prefixes': text_prefixes.most_common(10),
        'text_top_suffixes': text_suffixes.most_common(10),
    }


def test2_middle_overlap(labels, text):
    """Analyze MIDDLE overlap between labels and text."""
    print("\n" + "=" * 60)
    print("TEST 2: MIDDLE OVERLAP")
    print("=" * 60)

    label_types = set(r['word'] for r in labels)
    text_types = set(r['word'] for r in text)

    # Extract MIDDLEs
    label_middles = set()
    text_middles = set()

    for word in label_types:
        prefix, middle, suffix = parse_morphology(word)
        if middle:
            label_middles.add(middle)

    for word in text_types:
        prefix, middle, suffix = parse_morphology(word)
        if middle:
            text_middles.add(middle)

    shared = label_middles & text_middles
    label_only = label_middles - text_middles
    text_only = text_middles - label_middles

    print(f"\nLabel MIDDLEs: {len(label_middles)}")
    print(f"Text MIDDLEs: {len(text_middles)}")
    print(f"Shared: {len(shared)} ({100*len(shared)/len(label_middles):.1f}% of label MIDDLEs)")
    print(f"Label-only: {len(label_only)}")
    print(f"Text-only: {len(text_only)}")

    print(f"\nLabel-only MIDDLEs (potential material identifiers):")
    for m in sorted(label_only)[:20]:
        print(f"  {m}")

    return {
        'label_middles': len(label_middles),
        'text_middles': len(text_middles),
        'shared': len(shared),
        'label_only': len(label_only),
        'text_only': len(text_only),
        'label_only_list': sorted(label_only),
        'shared_list': sorted(shared)[:30],
    }


def test3_jar_root_differentiation():
    """Compare jar labels vs root labels using f99r mapping."""
    print("\n" + "=" * 60)
    print("TEST 3: JAR vs ROOT DIFFERENTIATION")
    print("=" * 60)

    if not F99R_PATH.exists():
        print("  f99r mapping not found")
        return {'error': 'f99r mapping not found'}

    with open(F99R_PATH) as f:
        mapping = json.load(f)

    jars = []
    roots = []

    for group in mapping['groups']:
        jars.append(group['jar'])
        for root in group['roots']:
            if isinstance(root, dict):
                roots.append(root['token'])
            else:
                roots.append(root)

    # Analyze jars
    jar_lengths = [len(j) for j in jars]
    jar_prefixes = Counter()
    jar_suffixes = Counter()
    jar_parsed = 0
    for jar in jars:
        prefix, middle, suffix = parse_morphology(jar)
        if prefix:
            jar_parsed += 1
            jar_prefixes[prefix] += 1
            jar_suffixes[suffix] += 1

    # Analyze roots
    root_lengths = [len(r) for r in roots]
    root_prefixes = Counter()
    root_suffixes = Counter()
    root_parsed = 0
    for root in roots:
        prefix, middle, suffix = parse_morphology(root)
        if prefix:
            root_parsed += 1
            root_prefixes[prefix] += 1
            root_suffixes[suffix] += 1

    avg_jar_len = sum(jar_lengths) / len(jars)
    avg_root_len = sum(root_lengths) / len(roots)

    print(f"\nJars (n={len(jars)}):")
    print(f"  Examples: {jars}")
    print(f"  Avg length: {avg_jar_len:.1f}")
    print(f"  Parse rate: {jar_parsed}/{len(jars)}")
    print(f"  Prefixes: {dict(jar_prefixes)}")
    print(f"  Suffixes: {dict(jar_suffixes)}")

    print(f"\nRoots (n={len(roots)}):")
    print(f"  Examples: {roots[:10]}...")
    print(f"  Avg length: {avg_root_len:.1f}")
    print(f"  Parse rate: {root_parsed}/{len(roots)}")
    print(f"  Prefixes: {dict(root_prefixes)}")
    print(f"  Suffixes: {dict(root_suffixes)}")

    print(f"\nKey finding: Jars are {avg_jar_len/avg_root_len:.1f}x longer than roots")

    return {
        'jars': jars,
        'roots': roots,
        'jar_count': len(jars),
        'root_count': len(roots),
        'avg_jar_length': avg_jar_len,
        'avg_root_length': avg_root_len,
        'length_ratio': avg_jar_len / avg_root_len,
        'jar_prefixes': dict(jar_prefixes),
        'root_prefixes': dict(root_prefixes),
        'jar_suffixes': dict(jar_suffixes),
        'root_suffixes': dict(root_suffixes),
    }


def test4_section_distribution(labels, text):
    """Analyze section distribution of labels vs text."""
    print("\n" + "=" * 60)
    print("TEST 4: SECTION DISTRIBUTION")
    print("=" * 60)

    label_sections = Counter(r['section'] for r in labels)
    text_sections = Counter(r['section'] for r in text)

    total_labels = len(labels)
    total_text = len(text)

    print("\nLabel distribution by section:")
    for section, count in label_sections.most_common():
        pct = 100 * count / total_labels
        print(f"  {section}: {count} ({pct:.1f}%)")

    print("\nText distribution by section:")
    for section, count in text_sections.most_common():
        pct = 100 * count / total_text
        print(f"  {section}: {count} ({pct:.1f}%)")

    # Calculate enrichment
    print("\nLabel enrichment by section (vs text baseline):")
    for section in label_sections:
        label_pct = label_sections[section] / total_labels
        text_pct = text_sections.get(section, 0) / total_text if total_text else 0
        if text_pct > 0:
            enrichment = label_pct / text_pct
            print(f"  {section}: {enrichment:.1f}x")

    return {
        'label_sections': dict(label_sections),
        'text_sections': dict(text_sections),
        'total_labels': total_labels,
        'total_text': total_text,
    }


def test5_folio_cooccurrence(labels, text):
    """Analyze if labels appear in same-folio text."""
    print("\n" + "=" * 60)
    print("TEST 5: FOLIO CO-OCCURRENCE")
    print("=" * 60)

    # Get folios with labels
    label_folios = set(r['folio'] for r in labels)
    text_folios = set(r['folio'] for r in text)

    # Get label vocabulary per folio
    label_vocab_by_folio = defaultdict(set)
    for r in labels:
        label_vocab_by_folio[r['folio']].add(r['word'])

    # Get text vocabulary per folio
    text_vocab_by_folio = defaultdict(set)
    for r in text:
        text_vocab_by_folio[r['folio']].add(r['word'])

    print(f"\nFolios with labels: {len(label_folios)}")
    print(f"Folios with text: {len(text_folios)}")
    print(f"Overlap: {len(label_folios & text_folios)}")

    # Check if label tokens appear in same-folio text
    same_folio_matches = 0
    other_folio_matches = 0
    no_matches = 0

    all_text_vocab = set(r['word'] for r in text)

    match_details = []
    for folio, label_words in label_vocab_by_folio.items():
        folio_text_vocab = text_vocab_by_folio.get(folio, set())
        other_text_vocab = all_text_vocab - folio_text_vocab

        for word in label_words:
            in_same_folio = word in folio_text_vocab
            in_other_folio = word in other_text_vocab

            if in_same_folio:
                same_folio_matches += 1
                match_details.append((folio, word, 'same_folio'))
            elif in_other_folio:
                other_folio_matches += 1
                match_details.append((folio, word, 'other_folio'))
            else:
                no_matches += 1
                match_details.append((folio, word, 'label_only'))

    total = same_folio_matches + other_folio_matches + no_matches
    print(f"\nLabel token co-occurrence:")
    print(f"  Same-folio match: {same_folio_matches} ({100*same_folio_matches/total:.1f}%)")
    print(f"  Other-folio match: {other_folio_matches} ({100*other_folio_matches/total:.1f}%)")
    print(f"  Label-only: {no_matches} ({100*no_matches/total:.1f}%)")

    print(f"\nSame-folio matches (first 10):")
    for folio, word, match_type in match_details[:10]:
        if match_type == 'same_folio':
            print(f"  {folio}: {word}")

    return {
        'label_folios': len(label_folios),
        'text_folios': len(text_folios),
        'overlap_folios': len(label_folios & text_folios),
        'same_folio_matches': same_folio_matches,
        'other_folio_matches': other_folio_matches,
        'label_only': no_matches,
        'label_folio_list': sorted(label_folios),
    }


def main():
    print("CURRIER-A-LABEL-TEXT-RELATIONSHIP ANALYSIS")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    labels, text = load_data()
    print(f"  Labels: {len(labels)} tokens")
    print(f"  Text: {len(text)} tokens")

    # Run tests
    results = {
        'counts': {
            'label_tokens': len(labels),
            'text_tokens': len(text),
            'label_types': len(set(r['word'] for r in labels)),
            'text_types': len(set(r['word'] for r in text)),
        }
    }

    results['test1_morphology'] = test1_morphological_comparison(labels, text)
    results['test2_middle_overlap'] = test2_middle_overlap(labels, text)
    results['test3_jar_root'] = test3_jar_root_differentiation()
    results['test4_sections'] = test4_section_distribution(labels, text)
    results['test5_cooccurrence'] = test5_folio_cooccurrence(labels, text)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    t1 = results['test1_morphology']
    t2 = results['test2_middle_overlap']
    t3 = results['test3_jar_root']
    t5 = results['test5_cooccurrence']

    print(f"\n1. MORPHOLOGY: Labels parse at {t1['label_parse_rate']:.0%} vs text at {t1['text_parse_rate']:.0%}")
    print(f"   -> Labels follow {'SAME' if abs(t1['label_parse_rate'] - t1['text_parse_rate']) < 0.1 else 'DIFFERENT'} morphology rules")

    print(f"\n2. MIDDLES: {t2['label_only']} label-only MIDDLEs (potential material identifiers)")
    print(f"   -> {100*t2['shared']/t2['label_middles']:.0f}% of label MIDDLEs also in text")

    if 'length_ratio' in t3:
        print(f"\n3. JAR vs ROOT: Jars are {t3['length_ratio']:.1f}x longer than roots")

    print(f"\n4. SECTIONS: Labels concentrate in specific sections (see above)")

    print(f"\n5. CO-OCCURRENCE: {t5['same_folio_matches']}/{t5['same_folio_matches']+t5['other_folio_matches']+t5['label_only']} labels appear in same-folio text")

    # Save results
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n\nResults saved to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
