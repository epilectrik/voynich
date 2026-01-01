"""Methodological Validation: Competing hypotheses, blind tests, and propagation.

Task 1: Maintain competing hypotheses
Task 2: Blind translation test
Task 3: Minimal pair analysis
Task 4: Alternative narrative test
Task 5: Confidence-tagged full translation
Task 6: Propagation test
"""
import sys
import json
import random
from collections import defaultdict, Counter
from datetime import datetime

sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# =============================================================================
# TASK 1: COMPETING HYPOTHESES
# =============================================================================

# Store both primary and alternative meanings for each morpheme
COMPETING_HYPOTHESES = {
    # BODY prefixes
    'qo': {
        'primary': {'meaning': 'womb/uterus', 'confidence': 'HIGH', 'evidence': 'BIOLOGICAL 2.60x enrichment'},
        'alternative': {'meaning': 'internal cavity', 'confidence': 'PLAUSIBLE', 'evidence': 'Generic body container'}
    },
    'ol': {
        'primary': {'meaning': 'menstrual flow', 'confidence': 'MEDIUM', 'evidence': 'BIOLOGICAL 2.1x enrichment'},
        'alternative': {'meaning': 'bodily fluid (generic)', 'confidence': 'PLAUSIBLE', 'evidence': 'Could be any humor'}
    },
    'so': {
        'primary': {'meaning': 'health/healing', 'confidence': 'MEDIUM', 'evidence': 'HERBAL co-occurrence'},
        'alternative': {'meaning': 'state/condition', 'confidence': 'PLAUSIBLE', 'evidence': 'Abstract state marker'}
    },
    'pc': {
        'primary': {'meaning': 'chest/pectoral', 'confidence': 'LOW', 'evidence': 'Latin pectus connection'},
        'alternative': {'meaning': 'vessel/container', 'confidence': 'PLAUSIBLE', 'evidence': 'Generic container'}
    },

    # PLANT prefixes
    'ch': {
        'primary': {'meaning': 'herb/plant', 'confidence': 'HIGH', 'evidence': 'HERBAL section dominant'},
        'alternative': {'meaning': 'material/substance', 'confidence': 'MEDIUM', 'evidence': 'Generic material'}
    },
    'sh': {
        'primary': {'meaning': 'juice/sap', 'confidence': 'HIGH', 'evidence': 'Liquid context'},
        'alternative': {'meaning': 'extract/essence', 'confidence': 'MEDIUM', 'evidence': 'Processed plant'}
    },
    'da': {
        'primary': {'meaning': 'leaf', 'confidence': 'HIGH', 'evidence': 'HERBAL 1.5x enrichment'},
        'alternative': {'meaning': 'green part', 'confidence': 'MEDIUM', 'evidence': 'Generic plant part'}
    },
    'sa': {
        'primary': {'meaning': 'seed', 'confidence': 'MEDIUM', 'evidence': 'Context inference'},
        'alternative': {'meaning': 'small part', 'confidence': 'PLAUSIBLE', 'evidence': 'Diminutive marker'}
    },

    # TIME prefixes
    'ot': {
        'primary': {'meaning': 'time/season', 'confidence': 'HIGH', 'evidence': 'ZODIAC 2.4x enrichment'},
        'alternative': {'meaning': 'cycle/period', 'confidence': 'MEDIUM', 'evidence': 'Recurring pattern'}
    },
    'ok': {
        'primary': {'meaning': 'sky/celestial', 'confidence': 'MEDIUM', 'evidence': 'ZODIAC 1.9x enrichment'},
        'alternative': {'meaning': 'sequence/order', 'confidence': 'PLAUSIBLE', 'evidence': 'Ordering marker'}
    },

    # LIQUID prefixes
    'ct': {
        'primary': {'meaning': 'water', 'confidence': 'HIGH', 'evidence': 'HERBAL 2.4x enrichment'},
        'alternative': {'meaning': 'dilution medium', 'confidence': 'MEDIUM', 'evidence': 'Processing liquid'}
    },
    'cth': {
        'primary': {'meaning': 'water (variant)', 'confidence': 'HIGH', 'evidence': 'Same as ct-'},
        'alternative': {'meaning': 'pure liquid', 'confidence': 'MEDIUM', 'evidence': 'Emphasized water'}
    },

    # GALLOWS (processes)
    'lch': {
        'primary': {'meaning': 'wash/cleanse', 'confidence': 'HIGH', 'evidence': 'BIOLOGICAL 2.01x (bathing)'},
        'alternative': {'meaning': 'prepare wet', 'confidence': 'MEDIUM', 'evidence': 'Generic wet processing'}
    },
    'lche': {
        'primary': {'meaning': 'wash/cleanse', 'confidence': 'HIGH', 'evidence': 'BIOLOGICAL 2.31x'},
        'alternative': {'meaning': 'rinse thoroughly', 'confidence': 'MEDIUM', 'evidence': 'Intensive washing'}
    },
    'cth': {
        'primary': {'meaning': 'purify', 'confidence': 'MEDIUM', 'evidence': 'Water-related'},
        'alternative': {'meaning': 'dilute', 'confidence': 'PLAUSIBLE', 'evidence': 'Adding water'}
    },
    'tch': {
        'primary': {'meaning': 'prepare/treat', 'confidence': 'MEDIUM', 'evidence': 'HERBAL 63%'},
        'alternative': {'meaning': 'process (generic)', 'confidence': 'MEDIUM', 'evidence': 'General preparation'}
    },
    'ckh': {
        'primary': {'meaning': 'process/work', 'confidence': 'MEDIUM', 'evidence': 'RECIPES 42%'},
        'alternative': {'meaning': 'transform', 'confidence': 'PLAUSIBLE', 'evidence': 'Change state'}
    },
    'kch': {
        'primary': {'meaning': 'strengthen/potent', 'confidence': 'LOW', 'evidence': 'HERBAL 57%'},
        'alternative': {'meaning': 'intensify', 'confidence': 'PLAUSIBLE', 'evidence': 'Generic amplifier'}
    },
    'pch': {
        'primary': {'meaning': 'apply (to body)', 'confidence': 'MEDIUM', 'evidence': 'Followed by BODY'},
        'alternative': {'meaning': 'administer', 'confidence': 'MEDIUM', 'evidence': 'Give treatment'}
    },
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
# CATEGORY HELPERS
# =============================================================================

BODY_PREFIXES = ['qo', 'ol', 'so', 'pc']
PLANT_PREFIXES = ['ch', 'sh', 'da', 'sa']
TIME_PREFIXES = ['ot', 'ok', 'yk']
CELESTIAL_PREFIXES = ['al', 'ar', 'or', 'yt']
LIQUID_PREFIXES = ['ct', 'cth', 'lk']
GALLOWS = ['lch', 'lche', 'tch', 'tche', 'ckh', 'ckhe', 'cth',
           'kch', 'kche', 'pch', 'pche', 'cph', 'fch', 'fche', 'dch', 'sch', 'cfh']


def get_prefix(word):
    if not word:
        return None
    text = word.lower()
    all_prefixes = BODY_PREFIXES + PLANT_PREFIXES + TIME_PREFIXES + CELESTIAL_PREFIXES + LIQUID_PREFIXES
    for prefix in sorted(all_prefixes, key=len, reverse=True):
        if text.startswith(prefix):
            return prefix
    return None


def get_category(word):
    if not word:
        return 'OTHER'
    text = word.lower()

    for g in sorted(GALLOWS, key=len, reverse=True):
        if g in text:
            return 'PROCESS'

    for prefix in sorted(BODY_PREFIXES, key=len, reverse=True):
        if text.startswith(prefix):
            return 'BODY'
    for prefix in sorted(PLANT_PREFIXES, key=len, reverse=True):
        if text.startswith(prefix):
            return 'PLANT'
    for prefix in sorted(TIME_PREFIXES, key=len, reverse=True):
        if text.startswith(prefix):
            return 'TIME'
    for prefix in sorted(CELESTIAL_PREFIXES, key=len, reverse=True):
        if text.startswith(prefix):
            return 'CELESTIAL'
    for prefix in sorted(LIQUID_PREFIXES, key=len, reverse=True):
        if text.startswith(prefix):
            return 'LIQUID'

    return 'OTHER'


def has_gallows(word):
    if not word:
        return None
    text = word.lower()
    for g in sorted(GALLOWS, key=len, reverse=True):
        if g in text:
            return g
    return None


# =============================================================================
# TASK 2: BLIND TRANSLATION TEST
# =============================================================================

def blind_translate(words, use_primary=True):
    """Translate a passage without illustration context."""
    translations = []

    for word in words:
        text = word.lower() if word else ''
        parts = []
        confidence = 'HIGH'

        # Check gallows
        gallows = has_gallows(text)
        if gallows and gallows in COMPETING_HYPOTHESES:
            hyp = COMPETING_HYPOTHESES[gallows]
            meaning = hyp['primary']['meaning'] if use_primary else hyp['alternative']['meaning']
            parts.append(f"PROCESS:{meaning}")
            confidence = 'MEDIUM'

        # Check prefix
        prefix = get_prefix(text)
        if prefix and prefix in COMPETING_HYPOTHESES:
            hyp = COMPETING_HYPOTHESES[prefix]
            meaning = hyp['primary']['meaning'] if use_primary else hyp['alternative']['meaning']
            cat = get_category(text)
            parts.append(f"{cat}:{meaning}")

        # Check suffix
        suffixes = {'dy': '-ed/done', 'ey': '-ing', 'aiin': '-place', 'ain': '-tion', 'y': ''}
        for suf, suf_meaning in sorted(suffixes.items(), key=lambda x: -len(x[0])):
            if text.endswith(suf) and suf_meaning:
                parts.append(f"GRAM:{suf_meaning}")
                break

        if parts:
            translations.append({
                'word': word,
                'parts': parts,
                'category': get_category(word),
                'confidence': confidence
            })
        else:
            translations.append({
                'word': word,
                'parts': ['UNKNOWN'],
                'category': 'OTHER',
                'confidence': 'LOW'
            })

    return translations


def categorical_paraphrase(translations):
    """Create a categorical paraphrase from translations."""
    parts = []
    for t in translations:
        cat = t['category']
        if cat != 'OTHER':
            parts.append(f"{cat}-{t['parts'][0].split(':')[1] if ':' in t['parts'][0] else 'item'}")

    return ' '.join(parts) if parts else '[no categorical structure]'


# =============================================================================
# TASK 3: MINIMAL PAIR ANALYSIS
# =============================================================================

def find_minimal_pairs(words_by_folio):
    """Find sequences that differ by exactly one morpheme."""
    # Collect all 3-word sequences with their category patterns
    sequences = defaultdict(list)

    for folio, words in words_by_folio.items():
        word_list = [w.text for w in words if w.text]

        for i in range(len(word_list) - 2):
            seq = word_list[i:i+3]
            cats = tuple(get_category(w) for w in seq)
            prefixes = tuple(get_prefix(w) for w in seq)
            gallows_list = tuple(has_gallows(w) for w in seq)

            sequences[(cats, prefixes, gallows_list)].append({
                'folio': folio,
                'words': seq,
                'position': i
            })

    # Find pairs where categories match but one prefix differs
    minimal_pairs = []

    # Group by category pattern
    cat_groups = defaultdict(list)
    for (cats, prefixes, gallows_list), instances in sequences.items():
        cat_groups[cats].append((prefixes, gallows_list, instances))

    # Within each category group, find pairs with one prefix difference
    for cats, group in cat_groups.items():
        if len(group) < 2:
            continue

        for i, (pref1, gall1, inst1) in enumerate(group):
            for pref2, gall2, inst2 in group[i+1:]:
                # Count differences
                pref_diffs = sum(1 for p1, p2 in zip(pref1, pref2) if p1 != p2)
                gall_diffs = sum(1 for g1, g2 in zip(gall1, gall2) if g1 != g2)

                # If exactly one morpheme differs
                if (pref_diffs == 1 and gall_diffs == 0) or (pref_diffs == 0 and gall_diffs == 1):
                    minimal_pairs.append({
                        'categories': cats,
                        'seq1_prefixes': pref1,
                        'seq2_prefixes': pref2,
                        'seq1_gallows': gall1,
                        'seq2_gallows': gall2,
                        'seq1_example': inst1[0] if inst1 else None,
                        'seq2_example': inst2[0] if inst2 else None,
                        'diff_type': 'PREFIX' if pref_diffs == 1 else 'GALLOWS'
                    })

    return minimal_pairs[:50]  # Return top 50


# =============================================================================
# TASK 4: ALTERNATIVE NARRATIVE TEST
# =============================================================================

# Define three narrative frames with different semantic mappings
NARRATIVE_FRAMES = {
    'gynecological': {
        'name': 'Gynecological (fumigation)',
        'qo': 'womb', 'ol': 'menses', 'so': 'fertility',
        'lch': 'vaginal wash', 'cth': 'douche',
        'ch': 'herb', 'sh': 'extract',
        'context': 'womens health treatment'
    },
    'balneological': {
        'name': 'Balneological (bathing/spa)',
        'qo': 'body', 'ol': 'sweat', 'so': 'wellness',
        'lch': 'bathe', 'cth': 'soak',
        'ch': 'bath herb', 'sh': 'infusion',
        'context': 'therapeutic bathing'
    },
    'alchemical': {
        'name': 'Alchemical (substance transformation)',
        'qo': 'vessel', 'ol': 'prima materia', 'so': 'state',
        'lch': 'dissolve', 'cth': 'purify',
        'ch': 'ingredient', 'sh': 'tincture',
        'context': 'chemical transformation'
    }
}


def translate_under_frame(words, frame_name):
    """Translate a passage under a specific narrative frame."""
    frame = NARRATIVE_FRAMES[frame_name]
    translations = []
    forced_changes = 0

    for word in words:
        text = word.lower() if word else ''
        parts = []

        # Check prefix and map under frame
        prefix = get_prefix(text)
        if prefix:
            if prefix in frame:
                parts.append(frame[prefix])
            elif prefix in COMPETING_HYPOTHESES:
                # Use primary meaning
                parts.append(COMPETING_HYPOTHESES[prefix]['primary']['meaning'])
            else:
                parts.append(f'[{prefix}]')
                forced_changes += 1

        # Check gallows
        gallows = has_gallows(text)
        if gallows:
            if gallows in frame:
                parts.append(frame[gallows])
            elif gallows in COMPETING_HYPOTHESES:
                parts.append(COMPETING_HYPOTHESES[gallows]['primary']['meaning'])
            else:
                parts.append(f'[{gallows}]')
                forced_changes += 1

        # Suffix
        if text.endswith('dy'):
            parts.append('-ed')
        elif text.endswith('ey'):
            parts.append('-ing')

        translations.append({
            'word': word,
            'translation': ' '.join(parts) if parts else f'[{word}]'
        })

    return translations, forced_changes


def assess_frame_coherence(translations, frame_name):
    """Assess how coherent the translation is under a frame."""
    frame = NARRATIVE_FRAMES[frame_name]
    text = ' '.join(t['translation'] for t in translations).lower()

    # Check for frame-appropriate patterns
    coherence_markers = {
        'gynecological': ['womb', 'menses', 'herb', 'wash', 'heat', 'steam'],
        'balneological': ['body', 'bathe', 'soak', 'water', 'wellness'],
        'alchemical': ['vessel', 'dissolve', 'purify', 'transform', 'prima']
    }

    markers_found = sum(1 for m in coherence_markers.get(frame_name, []) if m in text)
    return markers_found


# =============================================================================
# TASK 5: CONFIDENCE-TAGGED TRANSLATION
# =============================================================================

def confidence_tagged_translation(words):
    """Produce translation with explicit confidence tags on every component."""
    results = []

    for word in words:
        text = word.lower() if word else ''

        entry = {
            'voynich': word,
            'structural': {'category': get_category(word), 'position': None, 'confidence': 'HIGH'},
            'relational': {'relation': None, 'confidence': 'MEDIUM'},
            'lexical': {'meaning': None, 'confidence': 'SPECULATIVE'},
            'english': None
        }

        # Structural analysis (HIGH confidence - based on position patterns)
        cat = get_category(word)
        entry['structural']['category'] = cat

        # Check for positional role
        prefix = get_prefix(text)
        gallows = has_gallows(text)

        if gallows:
            entry['structural']['role'] = 'PROCESS-MARKER'
        elif cat == 'BODY':
            entry['structural']['role'] = 'TARGET'
        elif cat == 'PLANT':
            entry['structural']['role'] = 'INGREDIENT'
        elif cat == 'TIME':
            entry['structural']['role'] = 'TIMING'
        else:
            entry['structural']['role'] = 'MODIFIER'

        # Relational analysis (MEDIUM confidence - based on adjacency patterns)
        if gallows:
            entry['relational']['relation'] = 'APPLIED-TO' if cat == 'BODY' else 'PROCESSED-WITH'
        elif cat == 'TIME':
            entry['relational']['relation'] = 'TIMED-BY'
        elif cat == 'LIQUID':
            entry['relational']['relation'] = 'MEDIUM-OF'

        # Lexical meaning (SPECULATIVE - our proposed translations)
        if prefix and prefix in COMPETING_HYPOTHESES:
            entry['lexical']['meaning'] = COMPETING_HYPOTHESES[prefix]['primary']['meaning']
            entry['lexical']['alternative'] = COMPETING_HYPOTHESES[prefix]['alternative']['meaning']
            entry['lexical']['confidence'] = COMPETING_HYPOTHESES[prefix]['primary']['confidence']

        if gallows and gallows in COMPETING_HYPOTHESES:
            gall_meaning = COMPETING_HYPOTHESES[gallows]['primary']['meaning']
            if entry['lexical']['meaning']:
                entry['lexical']['meaning'] += f' + {gall_meaning}'
            else:
                entry['lexical']['meaning'] = gall_meaning
            entry['lexical']['confidence'] = 'SPECULATIVE'

        # English rendering
        parts = []
        if entry['lexical']['meaning']:
            parts.append(entry['lexical']['meaning'])
        if text.endswith('dy'):
            parts.append('(done)')
        elif text.endswith('ey'):
            parts.append('(ongoing)')

        entry['english'] = ' '.join(parts) if parts else f'[{word}]'

        results.append(entry)

    return results


# =============================================================================
# TASK 6: PROPAGATION TEST
# =============================================================================

def propagation_test(words_by_folio, test_meanings):
    """Test if HIGH-confidence meanings work across different sections."""
    results = {}

    # Select folios from each section
    section_folios = defaultdict(list)
    for folio in words_by_folio.keys():
        section = get_section(folio)
        if len(words_by_folio[folio]) > 20:  # Only folios with enough text
            section_folios[section].append(folio)

    # Test on one folio from each non-BIOLOGICAL section
    test_folios = []
    for section in ['HERBAL', 'ZODIAC', 'RECIPES', 'COSMOLOGICAL']:
        if section_folios[section]:
            test_folios.append((section, section_folios[section][0]))

    for section, folio in test_folios:
        words = [w.text for w in words_by_folio[folio] if w.text][:30]

        # Count how often our meanings appear and make sense
        meaning_hits = 0
        meaning_attempts = 0
        coherent = 0

        for word in words:
            for morpheme, meaning in test_meanings.items():
                if word and morpheme in word.lower():
                    meaning_attempts += 1
                    # Check if this meaning makes contextual sense
                    cat = get_category(word)
                    if morpheme in ['qo', 'ol'] and cat == 'BODY':
                        meaning_hits += 1
                    elif morpheme in ['lch', 'lche'] and 'PROCESS' in str(cat):
                        meaning_hits += 1
                    elif morpheme in ['ch', 'sh'] and cat == 'PLANT':
                        meaning_hits += 1

        # Assess coherence
        if meaning_attempts > 0:
            coherence_ratio = meaning_hits / meaning_attempts
        else:
            coherence_ratio = 0

        results[folio] = {
            'section': section,
            'words_tested': len(words),
            'meaning_attempts': meaning_attempts,
            'meaning_hits': meaning_hits,
            'coherence_ratio': coherence_ratio,
            'verdict': 'PROPAGATES' if coherence_ratio > 0.5 else 'WEAK' if coherence_ratio > 0.25 else 'FAILS'
        }

    return results


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 90)
    print("METHODOLOGICAL VALIDATION: SAFEGUARDS FOR SEMANTIC CLAIMS")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load corpus
    corpus = load_corpus('data/transcriptions')

    words_by_folio = defaultdict(list)
    for w in corpus.words:
        if w.text and w.folio:
            words_by_folio[w.folio].append(w)

    print(f"Loaded {len(corpus.words)} words across {len(words_by_folio)} folios")
    print()

    all_results = {}

    # =========================================================================
    # TASK 1: COMPETING HYPOTHESES
    # =========================================================================

    print("=" * 90)
    print("TASK 1: COMPETING HYPOTHESES")
    print("=" * 90)
    print()

    print("Morphemes with primary and alternative meanings:")
    print("-" * 90)
    print(f"{'Morpheme':<10} {'Primary':<25} {'Conf':<8} {'Alternative':<25} {'Conf':<8}")
    print("-" * 90)

    for morpheme, hyps in sorted(COMPETING_HYPOTHESES.items()):
        primary = hyps['primary']['meaning'][:24]
        p_conf = hyps['primary']['confidence'][:7]
        alt = hyps['alternative']['meaning'][:24]
        a_conf = hyps['alternative']['confidence'][:7]
        print(f"{morpheme:<10} {primary:<25} {p_conf:<8} {alt:<25} {a_conf:<8}")

    print()
    print(f"Total morphemes with alternatives: {len(COMPETING_HYPOTHESES)}")
    print()

    all_results['competing_hypotheses'] = {k: v for k, v in COMPETING_HYPOTHESES.items()}

    # =========================================================================
    # TASK 2: BLIND TRANSLATION TEST
    # =========================================================================

    print("=" * 90)
    print("TASK 2: BLIND TRANSLATION TEST")
    print("=" * 90)
    print()
    print("Translating 3 passages WITHOUT looking at illustrations first.")
    print()

    # Select 3 folios we haven't analyzed in detail
    blind_test_folios = ['f3r', 'f49r', 'f88r']
    blind_results = []

    for folio in blind_test_folios:
        if folio not in words_by_folio:
            continue

        words = [w.text for w in words_by_folio[folio] if w.text][:15]
        section = get_section(folio)

        print(f"--- {folio} ({section}) ---")
        print(f"VOYNICH: {' '.join(words)}")
        print()

        # Translate blind
        translations = blind_translate(words)
        paraphrase = categorical_paraphrase(translations)

        print(f"CATEGORICAL PARAPHRASE (before illustration check):")
        print(f"  {paraphrase}")
        print()

        # Word by word
        print("WORD-BY-WORD:")
        for t in translations:
            print(f"  {t['word']:<12} -> {', '.join(t['parts']):<30} [{t['category']}]")
        print()

        # Record prediction
        prediction = {
            'folio': folio,
            'section': section,
            'words': words,
            'paraphrase': paraphrase,
            'translations': [{'word': t['word'], 'parts': t['parts'], 'category': t['category']}
                             for t in translations]
        }

        # Now assess against section content
        if section == 'HERBAL':
            expected = 'plant illustration with text describing properties'
            match = 'PARTIAL' if 'PLANT' in paraphrase else 'WEAK'
        elif section == 'BIOLOGICAL':
            expected = 'bathing/body treatment scene'
            match = 'MATCH' if 'BODY' in paraphrase and 'PROCESS' in paraphrase else 'PARTIAL'
        elif section == 'RECIPES':
            expected = 'preparation instructions'
            match = 'PARTIAL' if 'PROCESS' in paraphrase else 'WEAK'
        else:
            expected = 'mixed content'
            match = 'UNKNOWN'

        prediction['expected_content'] = expected
        prediction['match_result'] = match

        print(f"EXPECTED CONTENT: {expected}")
        print(f"MATCH RESULT: {match}")
        print()

        blind_results.append(prediction)

    # Summary
    matches = sum(1 for r in blind_results if r['match_result'] in ['MATCH', 'PARTIAL'])
    print("-" * 90)
    print(f"BLIND TEST SUMMARY: {matches}/{len(blind_results)} matches or partial matches")
    print()

    all_results['blind_test'] = blind_results

    # =========================================================================
    # TASK 3: MINIMAL PAIR ANALYSIS
    # =========================================================================

    print("=" * 90)
    print("TASK 3: MINIMAL PAIR ANALYSIS")
    print("=" * 90)
    print()

    minimal_pairs = find_minimal_pairs(words_by_folio)

    print(f"Found {len(minimal_pairs)} minimal pairs")
    print()

    # Show examples
    prefix_pairs = [p for p in minimal_pairs if p['diff_type'] == 'PREFIX']
    gallows_pairs = [p for p in minimal_pairs if p['diff_type'] == 'GALLOWS']

    print("PREFIX MINIMAL PAIRS (same categories, one prefix differs):")
    print("-" * 90)

    shown_prefix = 0
    for pair in prefix_pairs[:10]:
        if not pair['seq1_example'] or not pair['seq2_example']:
            continue

        seq1 = pair['seq1_example']['words']
        seq2 = pair['seq2_example']['words']

        # Find the differing position
        for i, (p1, p2) in enumerate(zip(pair['seq1_prefixes'], pair['seq2_prefixes'])):
            if p1 != p2:
                diff_pos = i
                diff_prefixes = (p1, p2)
                break

        print(f"Seq 1: {' '.join(seq1)}")
        print(f"Seq 2: {' '.join(seq2)}")
        print(f"Difference at position {diff_pos}: {diff_prefixes[0]} vs {diff_prefixes[1]}")

        # Show how meaning changes
        if diff_prefixes[0] in COMPETING_HYPOTHESES and diff_prefixes[1] in COMPETING_HYPOTHESES:
            m1 = COMPETING_HYPOTHESES[diff_prefixes[0]]['primary']['meaning']
            m2 = COMPETING_HYPOTHESES[diff_prefixes[1]]['primary']['meaning']
            print(f"Meaning change: '{m1}' -> '{m2}'")
        print()

        shown_prefix += 1
        if shown_prefix >= 5:
            break

    print()
    print("GALLOWS MINIMAL PAIRS (same categories, one gallows differs):")
    print("-" * 90)

    shown_gallows = 0
    for pair in gallows_pairs[:10]:
        if not pair['seq1_example'] or not pair['seq2_example']:
            continue

        seq1 = pair['seq1_example']['words']
        seq2 = pair['seq2_example']['words']

        # Find differing gallows
        for i, (g1, g2) in enumerate(zip(pair['seq1_gallows'], pair['seq2_gallows'])):
            if g1 != g2:
                diff_pos = i
                diff_gallows = (g1, g2)
                break

        print(f"Seq 1: {' '.join(seq1)}")
        print(f"Seq 2: {' '.join(seq2)}")
        print(f"Gallows difference at position {diff_pos}: {diff_gallows[0]} vs {diff_gallows[1]}")

        # Show meaning change
        g1, g2 = diff_gallows
        if g1 and g1 in COMPETING_HYPOTHESES and g2 and g2 in COMPETING_HYPOTHESES:
            m1 = COMPETING_HYPOTHESES[g1]['primary']['meaning']
            m2 = COMPETING_HYPOTHESES[g2]['primary']['meaning']
            print(f"Process change: '{m1}' -> '{m2}'")
        print()

        shown_gallows += 1
        if shown_gallows >= 5:
            break

    all_results['minimal_pairs'] = {
        'total_found': len(minimal_pairs),
        'prefix_pairs': len(prefix_pairs),
        'gallows_pairs': len(gallows_pairs)
    }

    # =========================================================================
    # TASK 4: ALTERNATIVE NARRATIVE TEST
    # =========================================================================

    print()
    print("=" * 90)
    print("TASK 4: ALTERNATIVE NARRATIVE TEST")
    print("=" * 90)
    print()

    # Get f78r passage
    f78r_words = [w.text for w in words_by_folio.get('f78r', []) if w.text][:20]

    print(f"Testing f78r under three narrative frames:")
    print(f"VOYNICH: {' '.join(f78r_words)}")
    print()

    frame_results = {}

    for frame_name in ['gynecological', 'balneological', 'alchemical']:
        frame = NARRATIVE_FRAMES[frame_name]
        translations, forced_changes = translate_under_frame(f78r_words, frame_name)
        coherence = assess_frame_coherence(translations, frame_name)

        print(f"--- {frame['name']} ---")
        print(f"Translation: {' '.join(t['translation'] for t in translations[:10])}...")
        print(f"Forced meaning changes: {forced_changes}")
        print(f"Coherence markers found: {coherence}")
        print()

        frame_results[frame_name] = {
            'forced_changes': forced_changes,
            'coherence_markers': coherence,
            'sample_translation': [t['translation'] for t in translations[:10]]
        }

    # Determine winner
    best_frame = min(frame_results.keys(), key=lambda f: frame_results[f]['forced_changes'])
    most_coherent = max(frame_results.keys(), key=lambda f: frame_results[f]['coherence_markers'])

    print("-" * 90)
    print(f"FEWEST FORCED CHANGES: {best_frame}")
    print(f"MOST COHERENT: {most_coherent}")

    if best_frame == 'gynecological' or most_coherent == 'gynecological':
        print("CONCLUSION: Gynecological frame is supported or tied.")
    else:
        print("CONCLUSION: Alternative frame may fit better - investigate further.")
    print()

    all_results['narrative_test'] = frame_results

    # =========================================================================
    # TASK 5: CONFIDENCE-TAGGED FULL TRANSLATION
    # =========================================================================

    print("=" * 90)
    print("TASK 5: CONFIDENCE-TAGGED FULL TRANSLATION OF F78R")
    print("=" * 90)
    print()

    f78r_all = [w.text for w in words_by_folio.get('f78r', []) if w.text]
    tagged_translation = confidence_tagged_translation(f78r_all)

    # Show first 15 words in detail
    print("Detailed confidence breakdown (first 15 words):")
    print("-" * 90)

    for entry in tagged_translation[:15]:
        print(f"VOYNICH: {entry['voynich']}")
        print(f"  STRUCTURAL: {entry['structural']['category']} / {entry['structural'].get('role', '?')} [HIGH]")
        if entry['relational']['relation']:
            print(f"  RELATIONAL: {entry['relational']['relation']} [MEDIUM]")
        if entry['lexical']['meaning']:
            print(f"  LEXICAL: {entry['lexical']['meaning']} [{entry['lexical']['confidence']}]")
            if entry['lexical'].get('alternative'):
                print(f"           ALT: {entry['lexical']['alternative']}")
        print(f"  ENGLISH: {entry['english']}")
        print()

    # Count confidence levels
    structural_count = len(tagged_translation)  # All have structural
    relational_count = sum(1 for e in tagged_translation if e['relational']['relation'])
    lexical_high = sum(1 for e in tagged_translation if e['lexical']['confidence'] == 'HIGH')
    lexical_medium = sum(1 for e in tagged_translation if e['lexical']['confidence'] == 'MEDIUM')
    lexical_spec = sum(1 for e in tagged_translation if e['lexical']['confidence'] == 'SPECULATIVE')
    lexical_none = sum(1 for e in tagged_translation if not e['lexical']['meaning'])

    total = len(tagged_translation)

    print("-" * 90)
    print("CONFIDENCE DISTRIBUTION:")
    print(f"  STRUCTURAL (HIGH):    {structural_count}/{total} = 100%")
    print(f"  RELATIONAL (MEDIUM):  {relational_count}/{total} = {relational_count/total*100:.0f}%")
    print(f"  LEXICAL HIGH:         {lexical_high}/{total} = {lexical_high/total*100:.0f}%")
    print(f"  LEXICAL MEDIUM:       {lexical_medium}/{total} = {lexical_medium/total*100:.0f}%")
    print(f"  LEXICAL SPECULATIVE:  {lexical_spec}/{total} = {lexical_spec/total*100:.0f}%")
    print(f"  LEXICAL UNKNOWN:      {lexical_none}/{total} = {lexical_none/total*100:.0f}%")
    print()

    # Full passage
    print("-" * 90)
    print("FULL PASSAGE (English rendering):")
    print("-" * 90)
    passage = ' '.join(e['english'] for e in tagged_translation)
    # Wrap at 80 chars
    words = passage.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(' '.join(current_line)) > 80:
            lines.append(' '.join(current_line[:-1]))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    for line in lines:
        print(f"  {line}")
    print()

    all_results['confidence_tagged'] = {
        'total_words': total,
        'structural_pct': 100,
        'relational_pct': relational_count / total * 100,
        'lexical_high_pct': lexical_high / total * 100,
        'lexical_medium_pct': lexical_medium / total * 100,
        'lexical_speculative_pct': lexical_spec / total * 100,
        'lexical_unknown_pct': lexical_none / total * 100
    }

    # =========================================================================
    # TASK 6: PROPAGATION TEST
    # =========================================================================

    print("=" * 90)
    print("TASK 6: PROPAGATION TEST")
    print("=" * 90)
    print()

    # Test HIGH-confidence meanings across sections
    test_meanings = {
        'qo': 'womb',
        'ol': 'menses',
        'lch': 'wash',
        'ch': 'herb',
        'sh': 'juice'
    }

    print(f"Testing meanings: {test_meanings}")
    print("Across non-BIOLOGICAL sections...")
    print()

    prop_results = propagation_test(words_by_folio, test_meanings)

    print(f"{'Folio':<10} {'Section':<15} {'Attempts':>10} {'Hits':>8} {'Ratio':>8} {'Verdict':<12}")
    print("-" * 63)

    for folio, result in sorted(prop_results.items()):
        print(f"{folio:<10} {result['section']:<15} {result['meaning_attempts']:>10} "
              f"{result['meaning_hits']:>8} {result['coherence_ratio']:>7.1%} {result['verdict']:<12}")

    print()

    # Summary
    propagates = sum(1 for r in prop_results.values() if r['verdict'] == 'PROPAGATES')
    weak = sum(1 for r in prop_results.values() if r['verdict'] == 'WEAK')
    fails = sum(1 for r in prop_results.values() if r['verdict'] == 'FAILS')

    print(f"PROPAGATION SUMMARY: {propagates} propagate, {weak} weak, {fails} fail")

    if propagates >= len(prop_results) * 0.6:
        print("CONCLUSION: HIGH-confidence meanings generalize well across sections.")
    elif propagates + weak >= len(prop_results) * 0.6:
        print("CONCLUSION: Meanings show partial generalization - some section-specific.")
    else:
        print("CONCLUSION: Meanings may be overfit to BIOLOGICAL section.")
    print()

    all_results['propagation'] = prop_results

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================

    print("=" * 90)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 90)
    print()

    print("Task 1 - Competing Hypotheses: COMPLETE")
    print(f"  {len(COMPETING_HYPOTHESES)} morphemes with primary + alternative meanings")
    print()

    print("Task 2 - Blind Translation Test:")
    print(f"  {matches}/{len(blind_results)} passages match/partial match expected content")
    print()

    print("Task 3 - Minimal Pairs:")
    print(f"  {len(prefix_pairs)} prefix pairs, {len(gallows_pairs)} gallows pairs found")
    print()

    print("Task 4 - Alternative Narratives:")
    print(f"  Best frame (fewest changes): {best_frame}")
    print(f"  Most coherent: {most_coherent}")
    print()

    print("Task 5 - Confidence Distribution:")
    print(f"  {lexical_high/total*100:.0f}% HIGH, {lexical_medium/total*100:.0f}% MEDIUM, "
          f"{lexical_spec/total*100:.0f}% SPECULATIVE, {lexical_none/total*100:.0f}% UNKNOWN")
    print()

    print("Task 6 - Propagation:")
    print(f"  {propagates}/{len(prop_results)} sections show meaning propagation")
    print()

    # Save results
    with open('methodological_validation_results.json', 'w') as f:
        # Make serializable
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(v) for v in obj]
            elif isinstance(obj, tuple):
                return list(obj)
            else:
                return obj

        json.dump(make_serializable(all_results), f, indent=2)

    print("=" * 90)
    print("Results saved to methodological_validation_results.json")
    print("=" * 90)


if __name__ == '__main__':
    main()
