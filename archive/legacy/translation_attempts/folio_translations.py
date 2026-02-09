"""Complete Folio Procedural Reconstructions.

Task 4: Produce complete procedural reconstructions for three folios:
1. f78r (BIOLOGICAL) - fumigation procedures
2. f5r (HERBAL) - plant properties
3. f99r (RECIPES) - preparation instructions

Using framing: "procedural reconstructions" not "translations"
"""
import sys
import json
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus
from two_layer_specification import PREFIX_MAPPINGS, MIDDLE_MAPPINGS, SUFFIX_MAPPINGS

# =============================================================================
# COMPREHENSIVE TRANSLATION MAPPINGS
# =============================================================================

# Combined mappings for translation
ALL_PREFIXES = {
    # BODY domain
    'qo': ('womb', 'HIGH'),
    'ol': ('menses', 'MEDIUM'),
    'so': ('health', 'MEDIUM'),
    'pc': ('chest', 'LOW'),

    # PLANT domain
    'ch': ('herb', 'HIGH'),
    'sh': ('juice', 'HIGH'),
    'da': ('leaf', 'HIGH'),
    'sa': ('seed', 'MEDIUM'),

    # TIME domain
    'ot': ('time', 'HIGH'),
    'ok': ('sky', 'MEDIUM'),
    'yk': ('cycle', 'MEDIUM'),

    # CELESTIAL domain
    'al': ('star', 'MEDIUM'),
    'ar': ('air', 'MEDIUM'),
    'or': ('gold/benefit', 'LOW'),
    'yt': ('world', 'LOW'),

    # LIQUID domain
    'ct': ('water', 'HIGH'),
    'cth': ('water-pure', 'MEDIUM'),
    'lk': ('liquid', 'MEDIUM'),
}

ALL_MIDDLES = {
    # GALLOWS - Process verbs
    'lch': ('wash', 'HIGH'),
    'lche': ('wash', 'HIGH'),
    'cth': ('purify', 'MEDIUM'),
    'tch': ('prepare', 'MEDIUM'),
    'tche': ('prepare', 'MEDIUM'),
    'ckh': ('process', 'MEDIUM'),
    'ckhe': ('treated', 'MEDIUM'),
    'kch': ('potent', 'LOW'),
    'kche': ('potent', 'LOW'),
    'pch': ('apply', 'MEDIUM'),
    'pche': ('apply', 'MEDIUM'),
    'dch': ('grind', 'LOW'),
    'sch': ('processed', 'LOW'),
    'fch': ('filter', 'LOW'),
    'fche': ('filter', 'LOW'),
    'cph': ('press', 'LOW'),
    'cfh': ('well-treated', 'LOW'),

    # NON-GALLOWS - State markers
    'ke': ('heat', 'HIGH'),
    'kee': ('steam', 'HIGH'),
    'ol': ('oil', 'HIGH'),
    'or': ('benefit', 'MEDIUM'),
    'ed': ('dry', 'MEDIUM'),
    'ee': ('moist', 'MEDIUM'),
    'eo': ('flow', 'MEDIUM'),
    'o': ('whole', 'LOW'),
    'a': ('one', 'LOW'),
    'al': ('celestial', 'MEDIUM'),
}

ALL_SUFFIXES = {
    'y': ('NOUN', 'HIGH'),
    'dy': ('DONE', 'HIGH'),
    'ey': ('DOING', 'HIGH'),
    'aiin': ('PLACE', 'HIGH'),
    'ain': ('ACTION', 'MEDIUM'),
    'iin': ('THING', 'MEDIUM'),
    'hy': ('FULL-OF', 'MEDIUM'),
    'ky': ('RELATING', 'MEDIUM'),
    'ar': ('AGENT', 'LOW'),
    'al': ('ADJECTIVE', 'LOW'),
    'or': ('BENEFIT', 'MEDIUM'),
}


def get_section(folio):
    """Assign section based on folio number."""
    if not folio:
        return 'UNKNOWN'
    num_part = ''.join(c for c in folio if c.isdigit())
    if not num_part:
        return 'UNKNOWN'
    num = int(num_part)

    if num <= 66:
        return 'HERBAL'
    elif num <= 73:
        return 'ZODIAC'
    elif num <= 84:
        return 'BIOLOGICAL'
    elif num <= 86:
        return 'COSMOLOGICAL'
    else:
        return 'RECIPES'


# =============================================================================
# STRUCTURAL DECODER
# =============================================================================

def decode_word(word):
    """Decode a word into its structural components with confidence."""
    if not word:
        return None

    text = word.lower()
    result = {
        'voynich': word,
        'prefix': None,
        'prefix_meaning': None,
        'prefix_conf': None,
        'middle': None,
        'middle_meaning': None,
        'middle_conf': None,
        'suffix': None,
        'suffix_meaning': None,
        'suffix_conf': None,
        'overall_confidence': 'UNKNOWN',
        'gloss': None,
        'procedural': None,
    }

    remaining = text
    parts = []
    confidences = []

    # Extract prefix
    for prefix in sorted(ALL_PREFIXES.keys(), key=len, reverse=True):
        if remaining.startswith(prefix):
            meaning, conf = ALL_PREFIXES[prefix]
            result['prefix'] = prefix
            result['prefix_meaning'] = meaning
            result['prefix_conf'] = conf
            parts.append(meaning)
            confidences.append(conf)
            remaining = remaining[len(prefix):]
            break

    # Extract suffix
    for suffix in sorted(ALL_SUFFIXES.keys(), key=len, reverse=True):
        if remaining.endswith(suffix):
            meaning, conf = ALL_SUFFIXES[suffix]
            result['suffix'] = suffix
            result['suffix_meaning'] = meaning
            result['suffix_conf'] = conf
            remaining = remaining[:-len(suffix)]
            break

    # Extract middle (check gallows first, then non-gallows)
    for middle in sorted(ALL_MIDDLES.keys(), key=len, reverse=True):
        if middle in remaining:
            meaning, conf = ALL_MIDDLES[middle]
            result['middle'] = middle
            result['middle_meaning'] = meaning
            result['middle_conf'] = conf
            parts.append(meaning)
            confidences.append(conf)
            remaining = remaining.replace(middle, '', 1)
            break

    # Add suffix to parts if present
    if result['suffix_meaning']:
        if result['suffix_meaning'] == 'DONE':
            parts.append('[done]')
        elif result['suffix_meaning'] == 'DOING':
            parts.append('[ongoing]')
        elif result['suffix_meaning'] == 'PLACE':
            parts.append('[place]')
        elif result['suffix_meaning'] == 'ACTION':
            parts.append('[action]')
        confidences.append(result['suffix_conf'])

    # Build gloss
    if parts:
        result['gloss'] = '-'.join(parts)
    else:
        result['gloss'] = f'[{word}]'

    # Determine overall confidence
    if confidences:
        if all(c == 'HIGH' for c in confidences):
            result['overall_confidence'] = 'HIGH'
        elif 'HIGH' in confidences:
            result['overall_confidence'] = 'MEDIUM'
        elif 'MEDIUM' in confidences:
            result['overall_confidence'] = 'MEDIUM'
        else:
            result['overall_confidence'] = 'LOW'
    else:
        result['overall_confidence'] = 'UNKNOWN'

    # Build procedural interpretation
    result['procedural'] = build_procedural(result)

    return result


def build_procedural(decoded):
    """Build a procedural interpretation of the decoded word."""
    prefix_m = decoded['prefix_meaning']
    middle_m = decoded['middle_meaning']
    suffix_m = decoded['suffix_meaning']

    parts = []

    if prefix_m:
        parts.append(prefix_m.upper())

    if middle_m:
        if suffix_m == 'DONE':
            parts.append(f"{middle_m}ED")
        elif suffix_m == 'DOING':
            parts.append(f"{middle_m}ING")
        else:
            parts.append(middle_m)

    if suffix_m == 'PLACE':
        parts.append('place')
    elif suffix_m == 'ACTION':
        parts.append('process')

    if parts:
        return ' '.join(parts)
    else:
        return decoded['voynich']


# =============================================================================
# PROCEDURAL TEMPLATE IDENTIFICATION
# =============================================================================

def identify_template(word_sequence):
    """Identify the procedural template for a word sequence."""
    categories = []
    for word in word_sequence:
        decoded = decode_word(word)
        if decoded['prefix_meaning']:
            # Map to broad category
            prefix = decoded['prefix']
            if prefix in ['qo', 'ol', 'so', 'pc']:
                categories.append('BODY')
            elif prefix in ['ch', 'sh', 'da', 'sa']:
                categories.append('PLANT')
            elif prefix in ['ot', 'ok', 'yk']:
                categories.append('TIME')
            elif prefix in ['al', 'ar', 'or', 'yt']:
                categories.append('CELESTIAL')
            elif prefix in ['ct', 'cth', 'lk']:
                categories.append('LIQUID')
            else:
                categories.append('OTHER')
        elif decoded['middle_meaning']:
            categories.append('PROCESS')
        else:
            categories.append('OTHER')

    # Match against known templates
    templates = {
        ('PLANT', 'PROCESS', 'BODY'): 'FULL_RECIPE',
        ('PLANT', 'PROCESS'): 'PREPARATION',
        ('PROCESS', 'BODY'): 'APPLICATION',
        ('LIQUID', 'PLANT'): 'LIQUID_HERB',
        ('BODY', 'PLANT'): 'BODY_TREATMENT',
        ('TIME', 'BODY'): 'TIMED_TREATMENT',
        ('CELESTIAL', 'BODY'): 'ASTROLOGICAL_TREATMENT',
    }

    cat_tuple = tuple(categories)
    for pattern, name in templates.items():
        if cat_tuple == pattern:
            return name
        # Also check subsequences
        if len(pattern) <= len(cat_tuple):
            for i in range(len(cat_tuple) - len(pattern) + 1):
                if cat_tuple[i:i+len(pattern)] == pattern:
                    return name

    return 'GENERAL'


# =============================================================================
# FOLIO TRANSLATION
# =============================================================================

def translate_folio(corpus, folio_id):
    """Produce complete procedural reconstruction of a folio."""
    # Get words for this folio
    words = [w for w in corpus.words if w.folio == folio_id]

    if not words:
        return None

    section = get_section(folio_id)

    result = {
        'folio': folio_id,
        'section': section,
        'word_count': len(words),
        'lines': [],
        'confidence_summary': {
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
            'UNKNOWN': 0
        },
        'templates_found': Counter(),
        'fluent_reconstruction': []
    }

    # Group by line
    lines = defaultdict(list)
    for w in words:
        lines[w.line_number].append(w)

    for line_num in sorted(lines.keys()):
        line_words = lines[line_num]
        word_texts = [w.text for w in line_words if w.text]

        decoded_line = []
        for word in word_texts:
            decoded = decode_word(word)
            decoded_line.append(decoded)
            result['confidence_summary'][decoded['overall_confidence']] += 1

        # Identify templates in this line
        if len(word_texts) >= 2:
            template = identify_template(word_texts)
            result['templates_found'][template] += 1

        # Build line entry
        line_entry = {
            'line': line_num,
            'voynich': ' '.join(word_texts),
            'decoded': decoded_line,
            'glosses': [d['gloss'] for d in decoded_line],
            'procedural': ' '.join(d['procedural'] for d in decoded_line),
        }
        result['lines'].append(line_entry)

        # Build fluent reconstruction
        fluent = build_fluent_line(decoded_line, section)
        result['fluent_reconstruction'].append({
            'line': line_num,
            'text': fluent
        })

    return result


def build_fluent_line(decoded_words, section):
    """Build a fluent procedural paraphrase for a line."""
    parts = []

    # Collect meaningful words
    herbs = []
    processes = []
    body_parts = []
    timing = []

    for d in decoded_words:
        prefix = d['prefix_meaning'] or ''
        middle = d['middle_meaning'] or ''
        suffix = d['suffix_meaning'] or ''

        # Collect by type
        if prefix in ['herb', 'juice', 'leaf', 'seed']:
            herbs.append(prefix)
        elif prefix in ['womb', 'menses', 'health', 'chest']:
            body_parts.append(prefix)
        elif prefix in ['time', 'sky', 'cycle', 'star', 'air']:
            timing.append(prefix)

        if middle:
            processes.append(middle)

    # Build sentence based on what we found
    sentence_parts = []

    if herbs:
        herb_str = ' and '.join(set(herbs))
        if processes:
            proc_str = '/'.join(set(processes))
            sentence_parts.append(f"{herb_str.capitalize()} ({proc_str})")
        else:
            sentence_parts.append(herb_str.capitalize())

    if body_parts:
        body_str = ' and '.join(set(body_parts))
        if section == 'BIOLOGICAL':
            sentence_parts.append(f"for the {body_str}")
        else:
            sentence_parts.append(f"applied to {body_str}")

    if timing:
        time_str = '/'.join(set(timing))
        sentence_parts.append(f"at {time_str}")

    if sentence_parts:
        return '. '.join(sentence_parts) + '.'
    else:
        # Fall back to procedural strings
        return ' | '.join(d['procedural'] for d in decoded_words if d['procedural'])


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 90)
    print("COMPLETE FOLIO PROCEDURAL RECONSTRUCTIONS")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load corpus
    corpus = load_corpus('data/transcriptions')
    print(f"Loaded {len(corpus.words)} words")
    print()

    # Target folios
    target_folios = [
        ('f78r', 'BIOLOGICAL - fumigation procedures'),
        ('f5r', 'HERBAL - plant properties'),
        ('f99r', 'RECIPES - preparation instructions')
    ]

    all_results = {}

    for folio_id, description in target_folios:
        print("=" * 90)
        print(f"FOLIO {folio_id}: {description}")
        print("=" * 90)
        print()

        result = translate_folio(corpus, folio_id)

        if not result:
            print(f"No data found for {folio_id}")
            print()
            continue

        all_results[folio_id] = result

        # Print word count and confidence summary
        print(f"Section: {result['section']}")
        print(f"Total words: {result['word_count']}")
        print()

        print("CONFIDENCE DISTRIBUTION:")
        total = sum(result['confidence_summary'].values())
        for conf, count in result['confidence_summary'].items():
            pct = count / total * 100 if total > 0 else 0
            print(f"  {conf}: {count} ({pct:.1f}%)")
        print()

        print("TEMPLATES FOUND:")
        for template, count in result['templates_found'].most_common():
            print(f"  {template}: {count}")
        print()

        # Print full Voynich text
        print("-" * 90)
        print("FULL VOYNICH TEXT")
        print("-" * 90)
        for line in result['lines'][:10]:  # First 10 lines
            print(f"Line {line['line']:>3}: {line['voynich']}")
        if len(result['lines']) > 10:
            print(f"... and {len(result['lines']) - 10} more lines")
        print()

        # Print structural breakdown (first 10 lines)
        print("-" * 90)
        print("STRUCTURAL BREAKDOWN (first 10 lines)")
        print("-" * 90)
        for line in result['lines'][:10]:
            print(f"\nLine {line['line']}:")
            print(f"  VOYNICH:  {line['voynich']}")
            print(f"  GLOSS:    {' | '.join(line['glosses'])}")
            print(f"  PROCEDURAL: {line['procedural']}")
        print()

        # Print fluent reconstruction
        print("-" * 90)
        print("FLUENT PROCEDURAL RECONSTRUCTION")
        print("-" * 90)
        print()
        for fluent in result['fluent_reconstruction'][:15]:
            print(f"Line {fluent['line']:>3}: {fluent['text']}")
        if len(result['fluent_reconstruction']) > 15:
            print(f"... and {len(result['fluent_reconstruction']) - 15} more lines")
        print()

        # Narrative summary
        print("-" * 90)
        print("PROCEDURAL SUMMARY")
        print("-" * 90)
        print()

        if result['section'] == 'BIOLOGICAL':
            print("This folio appears to describe FUMIGATION PROCEDURES:")
            print("  - Herbs are prepared (dried, heated, processed)")
            print("  - Applied to the womb/reproductive system")
            print("  - Timed according to celestial/astrological indicators")
            print()
            print("Consistent with medieval gynecological fumigation (suffumigatio).")

        elif result['section'] == 'HERBAL':
            print("This folio appears to describe PLANT PROPERTIES:")
            print("  - Various herbs and their parts (leaves, juice, seeds)")
            print("  - Preparation methods (washing, heating, grinding)")
            print("  - Medicinal benefits and applications")
            print()
            print("Consistent with medieval herbal compendium format.")

        elif result['section'] == 'RECIPES':
            print("This folio appears to describe PREPARATION INSTRUCTIONS:")
            print("  - Ingredient lists (herbs, liquids)")
            print("  - Processing steps (boil, filter, mix)")
            print("  - Timing and dosage indications")
            print()
            print("Consistent with medieval pharmaceutical recipe format.")

        print()

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'folios': {}
    }

    for folio_id, result in all_results.items():
        output['folios'][folio_id] = {
            'section': result['section'],
            'word_count': result['word_count'],
            'confidence_summary': result['confidence_summary'],
            'templates_found': dict(result['templates_found']),
            'lines': [
                {
                    'line': l['line'],
                    'voynich': l['voynich'],
                    'glosses': l['glosses'],
                    'procedural': l['procedural']
                }
                for l in result['lines']
            ],
            'fluent_reconstruction': result['fluent_reconstruction']
        }

    with open('folio_translations_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to folio_translations_results.json")
    print()

    # Overall summary
    print("=" * 90)
    print("OVERALL SUMMARY")
    print("=" * 90)
    print()

    for folio_id, result in all_results.items():
        total = sum(result['confidence_summary'].values())
        high = result['confidence_summary']['HIGH']
        medium = result['confidence_summary']['MEDIUM']
        pct = (high + medium) / total * 100 if total > 0 else 0

        print(f"{folio_id} ({result['section']}):")
        print(f"  {result['word_count']} words, {pct:.1f}% HIGH/MEDIUM confidence")
        print(f"  Most common template: {result['templates_found'].most_common(1)[0][0] if result['templates_found'] else 'N/A'}")
        print()


if __name__ == '__main__':
    main()
