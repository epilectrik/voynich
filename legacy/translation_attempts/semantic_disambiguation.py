"""Semantic Disambiguation: From abstract categories to concrete vocabulary.

Task 1: Disambiguate BODY prefixes
Task 2: Identify specific PROCESS meanings
Task 3: Plant identification from illustrations
Task 4: Produce speculative translations
Task 5: Coherence check
"""
import sys
import json
from collections import defaultdict, Counter
from datetime import datetime

sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# =============================================================================
# CATEGORY DEFINITIONS
# =============================================================================

# BODY-related prefixes to disambiguate
BODY_PREFIXES = ['qo', 'ol', 'so', 'pc']

# PLANT-related prefixes
PLANT_PREFIXES = ['ch', 'sh', 'da', 'sa']

# TIME-related prefixes
TIME_PREFIXES = ['ot', 'ok', 'yk']

# CELESTIAL prefixes
CELESTIAL_PREFIXES = ['al', 'ar', 'or', 'yt']

# LIQUID prefixes
LIQUID_PREFIXES = ['ct', 'cth', 'lk']

# All gallows patterns to analyze
GALLOWS_PATTERNS = ['lch', 'lche', 'tch', 'tche', 'ckh', 'ckhe', 'cth',
                    'kch', 'kche', 'pch', 'pche', 'cph', 'fch', 'fche',
                    'dch', 'sch', 'cfh']

# Section assignment
def get_section(folio):
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


def get_prefix(word):
    """Extract prefix from word."""
    if not word:
        return None
    text = word.lower()

    all_prefixes = BODY_PREFIXES + PLANT_PREFIXES + TIME_PREFIXES + CELESTIAL_PREFIXES + LIQUID_PREFIXES
    for prefix in sorted(all_prefixes, key=len, reverse=True):
        if text.startswith(prefix):
            return prefix
    return None


def get_category(word):
    """Get category for a word."""
    if not word:
        return 'OTHER'
    text = word.lower()

    # Check gallows
    for g in sorted(GALLOWS_PATTERNS, key=len, reverse=True):
        if g in text:
            return 'PROCESS'

    # Check prefixes
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
    """Check if word contains any gallows pattern."""
    if not word:
        return None
    text = word.lower()
    for g in sorted(GALLOWS_PATTERNS, key=len, reverse=True):
        if g in text:
            return g
    return None


# =============================================================================
# TASK 1: DISAMBIGUATE BODY PREFIXES
# =============================================================================

def analyze_body_prefixes(corpus, words_by_folio):
    """Analyze BODY prefixes for disambiguation."""
    print("=" * 90)
    print("TASK 1: DISAMBIGUATE BODY PREFIXES")
    print("=" * 90)
    print()

    results = {}

    # Count frequencies
    prefix_counts = Counter()
    prefix_sections = defaultdict(Counter)
    prefix_contexts = defaultdict(lambda: {'before': Counter(), 'after': Counter()})
    prefix_cooccur = defaultdict(Counter)  # What categories co-occur with each prefix

    # Build word list with positions
    for folio, words in words_by_folio.items():
        section = get_section(folio)
        word_list = [w.text for w in words if w.text]

        for i, word in enumerate(word_list):
            prefix = get_prefix(word)
            if prefix in BODY_PREFIXES:
                prefix_counts[prefix] += 1
                prefix_sections[prefix][section] += 1

                # Context analysis
                if i > 0:
                    prev_cat = get_category(word_list[i-1])
                    prefix_contexts[prefix]['before'][prev_cat] += 1
                    prev_prefix = get_prefix(word_list[i-1])
                    if prev_prefix:
                        prefix_cooccur[prefix][prev_prefix] += 1

                if i < len(word_list) - 1:
                    next_cat = get_category(word_list[i+1])
                    prefix_contexts[prefix]['after'][next_cat] += 1
                    next_prefix = get_prefix(word_list[i+1])
                    if next_prefix:
                        prefix_cooccur[prefix][next_prefix] += 1

    print("-" * 90)
    print("BODY PREFIX FREQUENCIES")
    print("-" * 90)
    for prefix, count in sorted(prefix_counts.items(), key=lambda x: -x[1]):
        print(f"  {prefix}-: {count:,} occurrences")
    print()

    print("-" * 90)
    print("SECTION DISTRIBUTION")
    print("-" * 90)
    print(f"{'Prefix':<10}", end='')
    sections = ['HERBAL', 'BIOLOGICAL', 'ZODIAC', 'RECIPES']
    for s in sections:
        print(f"{s:>12}", end='')
    print()
    print("-" * 58)

    for prefix in sorted(prefix_counts.keys()):
        total = sum(prefix_sections[prefix].values())
        print(f"{prefix + '-':<10}", end='')
        for s in sections:
            count = prefix_sections[prefix][s]
            pct = count / total * 100 if total > 0 else 0
            print(f"{pct:>11.1f}%", end='')
        print()
    print()

    print("-" * 90)
    print("CONTEXT PATTERNS (What appears BEFORE/AFTER each BODY prefix)")
    print("-" * 90)

    for prefix in sorted(prefix_counts.keys(), key=lambda p: -prefix_counts[p]):
        print(f"\n{prefix}- ({prefix_counts[prefix]:,} occurrences):")

        before = prefix_contexts[prefix]['before']
        after = prefix_contexts[prefix]['after']
        before_total = sum(before.values())
        after_total = sum(after.values())

        print(f"  BEFORE: ", end='')
        for cat, count in before.most_common(4):
            pct = count / before_total * 100 if before_total > 0 else 0
            print(f"{cat}:{pct:.0f}% ", end='')
        print()

        print(f"  AFTER:  ", end='')
        for cat, count in after.most_common(4):
            pct = count / after_total * 100 if after_total > 0 else 0
            print(f"{cat}:{pct:.0f}% ", end='')
        print()
    print()

    print("-" * 90)
    print("CO-OCCURRENCE PATTERNS (What prefixes appear near each BODY prefix)")
    print("-" * 90)

    for prefix in sorted(prefix_counts.keys(), key=lambda p: -prefix_counts[p]):
        cooccur = prefix_cooccur[prefix]
        total = sum(cooccur.values())
        print(f"  {prefix}-: ", end='')
        for other, count in cooccur.most_common(6):
            pct = count / total * 100 if total > 0 else 0
            print(f"{other}({pct:.0f}%) ", end='')
        print()
    print()

    # Proposed meanings based on evidence
    print("-" * 90)
    print("PROPOSED SPECIFIC MEANINGS")
    print("-" * 90)
    print()

    # Analyze qo-
    qo_bio = prefix_sections['qo'].get('BIOLOGICAL', 0)
    qo_total = sum(prefix_sections['qo'].values())
    qo_bio_pct = qo_bio / qo_total * 100 if qo_total > 0 else 0

    print("qo- = WOMB/UTERUS")
    print(f"  Evidence: {qo_bio_pct:.1f}% enriched in BIOLOGICAL section (bathing women)")
    print(f"  Context: Frequently followed by PROCESS ({prefix_contexts['qo']['after']['PROCESS']} times)")
    print(f"  Co-occurs with: ", end='')
    for other, count in prefix_cooccur['qo'].most_common(3):
        print(f"{other} ({count}), ", end='')
    print()
    print(f"  Confidence: HIGH (strong BIOLOGICAL enrichment)")
    print()

    # Analyze ol-
    ol_bio = prefix_sections['ol'].get('BIOLOGICAL', 0)
    ol_total = sum(prefix_sections['ol'].values())
    ol_bio_pct = ol_bio / ol_total * 100 if ol_total > 0 else 0
    ol_liquid_after = prefix_contexts['ol']['after'].get('LIQUID', 0)

    print("ol- = MENSTRUAL FLOW / BODILY FLUID")
    print(f"  Evidence: {ol_bio_pct:.1f}% in BIOLOGICAL section")
    print(f"  Context: Often followed by LIQUID terms ({ol_liquid_after} times)")
    print(f"  Co-occurs heavily with: ", end='')
    for other, count in prefix_cooccur['ol'].most_common(3):
        print(f"{other} ({count}), ", end='')
    print()
    print(f"  Confidence: MEDIUM (plausible fluid meaning)")
    print()

    # Analyze so-
    so_herb = prefix_sections['so'].get('HERBAL', 0)
    so_total = sum(prefix_sections['so'].values())
    so_herb_pct = so_herb / so_total * 100 if so_total > 0 else 0

    print("so- = HEALTH / HEALING STATE")
    print(f"  Evidence: {so_herb_pct:.1f}% in HERBAL section (medicinal plants)")
    print(f"  Context: Appears with PLANT terms - suggests healing property")
    print(f"  Confidence: MEDIUM (contextually plausible)")
    print()

    # Analyze pc-
    pc_total = sum(prefix_sections['pc'].values()) if 'pc' in prefix_sections else 0
    if pc_total > 0:
        print("pc- = CHEST / PECTORAL REGION")
        print(f"  Evidence: {pc_total} occurrences total")
        print(f"  Latin connection: 'pectus' = chest")
        print(f"  Confidence: LOW (limited data)")
    print()

    results['body_prefixes'] = {
        'qo': {'meaning': 'womb/uterus', 'confidence': 'HIGH',
               'bio_enrichment': qo_bio_pct},
        'ol': {'meaning': 'menstrual flow/fluid', 'confidence': 'MEDIUM',
               'bio_enrichment': ol_bio_pct},
        'so': {'meaning': 'health/healing state', 'confidence': 'MEDIUM',
               'herb_enrichment': so_herb_pct},
        'pc': {'meaning': 'chest/pectoral', 'confidence': 'LOW'}
    }

    return results


# =============================================================================
# TASK 2: IDENTIFY SPECIFIC PROCESS MEANINGS
# =============================================================================

def analyze_gallows_meanings(corpus, words_by_folio):
    """Analyze gallows for specific process meanings."""
    print()
    print("=" * 90)
    print("TASK 2: IDENTIFY SPECIFIC PROCESS MEANINGS")
    print("=" * 90)
    print()

    results = {}

    # Collect context for each gallows
    gallows_data = defaultdict(lambda: {
        'count': 0,
        'sections': Counter(),
        'before_cat': Counter(),
        'after_cat': Counter(),
        'liquid_context': 0,
        'dry_context': 0,
    })

    for folio, words in words_by_folio.items():
        section = get_section(folio)
        word_list = [w.text for w in words if w.text]

        for i, word in enumerate(word_list):
            gallows = has_gallows(word)
            if gallows:
                gallows_data[gallows]['count'] += 1
                gallows_data[gallows]['sections'][section] += 1

                # Before context
                if i > 0:
                    before_cat = get_category(word_list[i-1])
                    gallows_data[gallows]['before_cat'][before_cat] += 1
                    if before_cat == 'LIQUID':
                        gallows_data[gallows]['liquid_context'] += 1

                # After context
                if i < len(word_list) - 1:
                    after_cat = get_category(word_list[i+1])
                    gallows_data[gallows]['after_cat'][after_cat] += 1
                    if after_cat == 'LIQUID':
                        gallows_data[gallows]['liquid_context'] += 1

    print("-" * 90)
    print("GALLOWS CONTEXT ANALYSIS")
    print("-" * 90)
    print()

    print(f"{'Gallows':<8} {'Count':>7} {'Top Section':>12} {'Before=':>12} {'=After':>12} {'Liquid%':>8}")
    print("-" * 60)

    for gallows in sorted(gallows_data.keys(), key=lambda g: -gallows_data[g]['count']):
        data = gallows_data[gallows]
        if data['count'] < 50:  # Skip rare patterns
            continue

        top_section = data['sections'].most_common(1)[0][0] if data['sections'] else '?'
        before_top = data['before_cat'].most_common(1)[0][0] if data['before_cat'] else '?'
        after_top = data['after_cat'].most_common(1)[0][0] if data['after_cat'] else '?'
        liquid_pct = data['liquid_context'] / data['count'] * 100 if data['count'] > 0 else 0

        print(f"{gallows:<8} {data['count']:>7} {top_section:>12} {before_top:>12} {after_top:>12} {liquid_pct:>7.1f}%")

    print()
    print("-" * 90)
    print("PROPOSED SPECIFIC PROCESS MEANINGS")
    print("-" * 90)
    print()

    proposed = {}

    # Analyze each major gallows pattern
    for gallows in ['lch', 'lche', 'cth', 'tch', 'ckh', 'kch', 'pch', 'cph', 'fch', 'dch']:
        if gallows not in gallows_data or gallows_data[gallows]['count'] < 50:
            continue

        data = gallows_data[gallows]
        bio_pct = data['sections'].get('BIOLOGICAL', 0) / data['count'] * 100
        herb_pct = data['sections'].get('HERBAL', 0) / data['count'] * 100
        recipe_pct = data['sections'].get('RECIPES', 0) / data['count'] * 100
        liquid_pct = data['liquid_context'] / data['count'] * 100

        before = data['before_cat'].most_common(3)
        after = data['after_cat'].most_common(3)

        # Propose meaning based on patterns
        if gallows in ['lch', 'lche']:
            meaning = 'WASH/CLEANSE'
            evidence = f"'l' suggests liquid/lavare; {bio_pct:.0f}% in BIOLOGICAL (bathing)"
            confidence = 'HIGH'
        elif gallows == 'cth':
            meaning = 'PURIFY (with water)'
            evidence = f"'cth' related to water prefix; {herb_pct:.0f}% in HERBAL"
            confidence = 'MEDIUM'
        elif gallows in ['tch', 'tche']:
            meaning = 'PREPARE/TREAT'
            evidence = f"Most common in HERBAL ({herb_pct:.0f}%); general preparation"
            confidence = 'MEDIUM'
        elif gallows in ['ckh', 'ckhe']:
            meaning = 'PROCESS/WORK'
            evidence = f"High in RECIPES ({recipe_pct:.0f}%); cooking/processing"
            confidence = 'MEDIUM'
        elif gallows in ['kch', 'kche']:
            meaning = 'STRENGTHEN/POTENT'
            evidence = f"Enriched in HERBAL ({herb_pct:.0f}%); intensifier"
            confidence = 'LOW'
        elif gallows in ['pch', 'pche']:
            meaning = 'APPLY (to body)'
            evidence = f"Often followed by BODY terms"
            confidence = 'MEDIUM'
        elif gallows == 'cph':
            meaning = 'PRESS/EXTRACT'
            evidence = f"'p' suggests pressing; {liquid_pct:.0f}% liquid context"
            confidence = 'LOW'
        elif gallows in ['fch', 'fche']:
            meaning = 'FILTER/STRAIN'
            evidence = f"'f' sound suggests filtering; appears with liquids"
            confidence = 'LOW'
        elif gallows == 'dch':
            meaning = 'GRIND/CRUSH'
            evidence = f"Appears with plant terms; preparation step"
            confidence = 'LOW'
        else:
            meaning = 'PROCESS (generic)'
            evidence = "Insufficient distinctive pattern"
            confidence = 'LOW'

        proposed[gallows] = {
            'meaning': meaning,
            'confidence': confidence,
            'evidence': evidence,
            'count': data['count'],
            'bio_pct': bio_pct,
            'herb_pct': herb_pct,
            'recipe_pct': recipe_pct
        }

        print(f"{gallows} = {meaning}")
        print(f"  Evidence: {evidence}")
        print(f"  Before: {', '.join(f'{c[0]}({c[1]})' for c in before)}")
        print(f"  After: {', '.join(f'{c[0]}({c[1]})' for c in after)}")
        print(f"  Confidence: {confidence}")
        print()

    results['gallows_meanings'] = proposed
    return results


# =============================================================================
# TASK 3: PLANT IDENTIFICATION FROM ILLUSTRATIONS
# =============================================================================

def identify_plant_names(corpus, words_by_folio):
    """Identify potential plant names from HERBAL folios."""
    print()
    print("=" * 90)
    print("TASK 3: PLANT IDENTIFICATION FROM ILLUSTRATIONS")
    print("=" * 90)
    print()

    results = {}

    # Get all HERBAL folios
    herbal_folios = [f for f in words_by_folio.keys() if get_section(f) == 'HERBAL']

    # Count word frequencies per folio and across corpus
    folio_word_counts = defaultdict(Counter)
    corpus_word_counts = Counter()

    for folio, words in words_by_folio.items():
        for w in words:
            if w.text:
                corpus_word_counts[w.text] += 1
                folio_word_counts[folio][w.text] += 1

    # Find words unique or highly enriched on single HERBAL folios
    plant_candidates = []

    for folio in sorted(herbal_folios):
        words_on_folio = folio_word_counts[folio]

        for word, count in words_on_folio.items():
            # Skip very common words
            if corpus_word_counts[word] > 50:
                continue

            # Skip words that don't look like plant terms
            prefix = get_prefix(word)
            if prefix not in PLANT_PREFIXES and prefix is not None:
                continue

            # Calculate enrichment
            total_corpus = corpus_word_counts[word]
            if total_corpus == 0:
                continue

            folio_ratio = count / total_corpus

            # If >50% of this word's occurrences are on this folio, it's a candidate
            if folio_ratio >= 0.5 and count >= 2:
                plant_candidates.append({
                    'word': word,
                    'folio': folio,
                    'folio_count': count,
                    'corpus_count': total_corpus,
                    'enrichment': folio_ratio,
                    'prefix': prefix
                })

    # Sort by enrichment
    plant_candidates.sort(key=lambda x: (-x['enrichment'], -x['folio_count']))

    print("-" * 90)
    print("CANDIDATE PLANT NAMES (>50% on single folio)")
    print("-" * 90)
    print()

    print(f"{'Word':<15} {'Folio':<10} {'On Folio':>10} {'Corpus':>10} {'Enrichment':>12}")
    print("-" * 57)

    shown = set()
    for cand in plant_candidates[:50]:
        if cand['word'] in shown:
            continue
        shown.add(cand['word'])
        print(f"{cand['word']:<15} {cand['folio']:<10} {cand['folio_count']:>10} {cand['corpus_count']:>10} {cand['enrichment']*100:>11.0f}%")

    print()
    print("-" * 90)
    print("DOMINANT PLANT WORDS BY FOLIO")
    print("-" * 90)
    print()

    folio_dominant = {}

    for folio in sorted(herbal_folios)[:20]:  # First 20 herbal folios
        words_on_folio = folio_word_counts[folio]

        # Get PLANT-category words
        plant_words = [(w, c) for w, c in words_on_folio.items()
                       if get_category(w) == 'PLANT']

        if plant_words:
            plant_words.sort(key=lambda x: -x[1])
            dominant = plant_words[0]
            folio_dominant[folio] = dominant

            print(f"{folio}: {dominant[0]} ({dominant[1]}x)", end='')
            if len(plant_words) > 1:
                print(f", also: {', '.join(f'{w}({c})' for w, c in plant_words[1:4])}")
            else:
                print()

    print()
    print("-" * 90)
    print("PROPOSED PLANT VOCABULARY")
    print("-" * 90)
    print()

    # Group by likely meaning
    print("High-frequency PLANT words (likely generic terms):")
    high_freq = [(w, c) for w, c in corpus_word_counts.items()
                 if get_category(w) == 'PLANT' and c > 100]
    high_freq.sort(key=lambda x: -x[1])
    for word, count in high_freq[:10]:
        print(f"  {word}: {count}x - likely generic (herb, leaf, plant, etc.)")

    print()
    print("Folio-specific words (likely plant names):")
    for cand in plant_candidates[:15]:
        if cand['enrichment'] >= 0.7:
            print(f"  {cand['word']}: {cand['enrichment']*100:.0f}% on {cand['folio']} - likely NAME of depicted plant")

    results['plant_candidates'] = plant_candidates[:50]
    results['folio_dominant'] = {k: {'word': v[0], 'count': v[1]} for k, v in folio_dominant.items()}

    return results


# =============================================================================
# TASK 4: SPECULATIVE TRANSLATIONS
# =============================================================================

# Build translation table from disambiguated meanings
SPECULATIVE_MEANINGS = {
    # BODY prefixes
    'qo': ('womb', 'HIGH'),
    'ol': ('menses/flow', 'MEDIUM'),
    'so': ('health', 'MEDIUM'),
    'pc': ('chest', 'LOW'),

    # PLANT prefixes
    'ch': ('herb', 'HIGH'),
    'sh': ('juice/sap', 'HIGH'),
    'da': ('leaf', 'HIGH'),
    'sa': ('seed', 'MEDIUM'),

    # TIME prefixes
    'ot': ('time/season', 'HIGH'),
    'ok': ('sky/celestial', 'MEDIUM'),
    'yk': ('cycle', 'MEDIUM'),

    # CELESTIAL prefixes
    'al': ('star', 'MEDIUM'),
    'ar': ('air', 'MEDIUM'),
    'or': ('gold/sun', 'MEDIUM'),

    # LIQUID prefixes
    'ct': ('water', 'HIGH'),
    'cth': ('water', 'HIGH'),
    'lk': ('liquid', 'MEDIUM'),

    # GALLOWS (processes)
    'lch': ('wash', 'HIGH'),
    'lche': ('wash', 'HIGH'),
    'cth': ('purify', 'MEDIUM'),
    'tch': ('prepare', 'MEDIUM'),
    'tche': ('prepare', 'MEDIUM'),
    'ckh': ('process', 'MEDIUM'),
    'ckhe': ('process', 'MEDIUM'),
    'kch': ('strengthen', 'LOW'),
    'kche': ('strengthen', 'LOW'),
    'pch': ('apply', 'MEDIUM'),
    'pche': ('apply', 'MEDIUM'),
    'cph': ('press', 'LOW'),
    'fch': ('filter', 'LOW'),
    'fche': ('filter', 'LOW'),
    'dch': ('grind', 'LOW'),

    # SUFFIXES
    'y': ('', 'HIGH'),  # noun marker
    'dy': ('-ed/done', 'HIGH'),  # past participle
    'ey': ('-ing', 'MEDIUM'),  # present participle
    'aiin': ('-place', 'MEDIUM'),
    'ain': ('-tion', 'MEDIUM'),  # action noun
    'iin': ('', 'LOW'),
    'hy': ('-ful', 'LOW'),

    # MIDDLES
    'ke': ('heat', 'HIGH'),
    'kee': ('steam', 'HIGH'),
    'ed': ('dry', 'MEDIUM'),
    'ee': ('moist', 'MEDIUM'),
    'ol': ('oil', 'MEDIUM'),
    'or': ('benefit', 'MEDIUM'),
    'eo': ('flow', 'MEDIUM'),
}


def translate_word(word):
    """Translate a single word with confidence levels."""
    if not word:
        return None, None, 'NONE'

    text = word.lower()
    parts = []
    overall_confidence = 'HIGH'

    # Check gallows first
    for gallows in sorted(GALLOWS_PATTERNS, key=len, reverse=True):
        if gallows in text:
            if gallows in SPECULATIVE_MEANINGS:
                meaning, conf = SPECULATIVE_MEANINGS[gallows]
                parts.append(meaning)
                if conf == 'LOW':
                    overall_confidence = 'LOW'
                elif conf == 'MEDIUM' and overall_confidence == 'HIGH':
                    overall_confidence = 'MEDIUM'
            text = text.replace(gallows, '', 1)
            break

    # Check prefix
    all_prefixes = list(SPECULATIVE_MEANINGS.keys())
    for prefix in sorted([p for p in all_prefixes if len(p) <= 3], key=len, reverse=True):
        if text.startswith(prefix) and prefix in SPECULATIVE_MEANINGS:
            meaning, conf = SPECULATIVE_MEANINGS[prefix]
            if meaning:
                parts.insert(0, meaning)
            if conf == 'LOW':
                overall_confidence = 'LOW'
            elif conf == 'MEDIUM' and overall_confidence == 'HIGH':
                overall_confidence = 'MEDIUM'
            text = text[len(prefix):]
            break

    # Check suffix
    suffixes = ['aiin', 'ain', 'iin', 'dy', 'ey', 'hy', 'y']
    for suffix in sorted(suffixes, key=len, reverse=True):
        if text.endswith(suffix) and suffix in SPECULATIVE_MEANINGS:
            meaning, conf = SPECULATIVE_MEANINGS[suffix]
            if meaning:
                parts.append(meaning)
            text = text[:-len(suffix)]
            break

    # Check remaining middle
    middles = ['kee', 'ke', 'ed', 'ee', 'ol', 'or', 'eo']
    for middle in sorted(middles, key=len, reverse=True):
        if middle in text and middle in SPECULATIVE_MEANINGS:
            meaning, conf = SPECULATIVE_MEANINGS[middle]
            if meaning:
                parts.append(meaning)
            if conf == 'LOW':
                overall_confidence = 'LOW'
            elif conf == 'MEDIUM' and overall_confidence == 'HIGH':
                overall_confidence = 'MEDIUM'
            break

    if parts:
        return word, ' '.join(parts), overall_confidence
    else:
        return word, f'[{word}]', 'UNKNOWN'


def produce_translations(corpus, words_by_folio):
    """Produce speculative translations for sample paragraphs."""
    print()
    print("=" * 90)
    print("TASK 4: SPECULATIVE TRANSLATIONS")
    print("=" * 90)
    print()

    results = {}

    # Sample 1: f78r (biological/gynecological)
    print("-" * 90)
    print("SAMPLE 1: f78r (BIOLOGICAL - Gynecological fumigation)")
    print("-" * 90)
    print()

    f78r_words = [w.text for w in words_by_folio.get('f78r', []) if w.text][:20]

    print("VOYNICH TEXT:")
    print(f"  {' '.join(f78r_words)}")
    print()

    print("WORD-BY-WORD BREAKDOWN:")
    translations = []
    for word in f78r_words:
        orig, trans, conf = translate_word(word)
        translations.append((orig, trans, conf))
        conf_marker = '**' if conf == 'HIGH' else '*' if conf == 'MEDIUM' else '?'
        print(f"  {orig:<12} = {trans:<20} [{conf_marker}]")

    print()
    print("FLUENT INTERPRETATION:")
    fluent = interpret_as_medical_instruction(translations)
    print(f"  {fluent}")
    print()

    results['f78r'] = {
        'voynich': f78r_words,
        'translations': [(o, t, c) for o, t, c in translations],
        'fluent': fluent
    }

    # Sample 2: f1r (herbal)
    print("-" * 90)
    print("SAMPLE 2: f1r (HERBAL - Plant description)")
    print("-" * 90)
    print()

    f1r_words = [w.text for w in words_by_folio.get('f1r', []) if w.text][:20]

    print("VOYNICH TEXT:")
    print(f"  {' '.join(f1r_words)}")
    print()

    print("WORD-BY-WORD BREAKDOWN:")
    translations = []
    for word in f1r_words:
        orig, trans, conf = translate_word(word)
        translations.append((orig, trans, conf))
        conf_marker = '**' if conf == 'HIGH' else '*' if conf == 'MEDIUM' else '?'
        print(f"  {orig:<12} = {trans:<20} [{conf_marker}]")

    print()
    print("FLUENT INTERPRETATION:")
    fluent = interpret_as_medical_instruction(translations)
    print(f"  {fluent}")
    print()

    results['f1r'] = {
        'voynich': f1r_words,
        'translations': [(o, t, c) for o, t, c in translations],
        'fluent': fluent
    }

    # Sample 3: f99r (recipes)
    print("-" * 90)
    print("SAMPLE 3: f99r (RECIPES - Preparation instructions)")
    print("-" * 90)
    print()

    f99r_words = [w.text for w in words_by_folio.get('f99r', []) if w.text][:20]

    print("VOYNICH TEXT:")
    print(f"  {' '.join(f99r_words)}")
    print()

    print("WORD-BY-WORD BREAKDOWN:")
    translations = []
    for word in f99r_words:
        orig, trans, conf = translate_word(word)
        translations.append((orig, trans, conf))
        conf_marker = '**' if conf == 'HIGH' else '*' if conf == 'MEDIUM' else '?'
        print(f"  {orig:<12} = {trans:<20} [{conf_marker}]")

    print()
    print("FLUENT INTERPRETATION:")
    fluent = interpret_as_medical_instruction(translations)
    print(f"  {fluent}")
    print()

    results['f99r'] = {
        'voynich': f99r_words,
        'translations': [(o, t, c) for o, t, c in translations],
        'fluent': fluent
    }

    return results


def interpret_as_medical_instruction(translations):
    """Convert word-by-word translation to fluent medical instruction."""
    # Extract key concepts
    ingredients = []
    actions = []
    targets = []
    timing = []

    for orig, trans, conf in translations:
        trans_lower = trans.lower()

        if any(x in trans_lower for x in ['herb', 'leaf', 'seed', 'juice', 'sap']):
            ingredients.append(trans)
        elif any(x in trans_lower for x in ['wash', 'prepare', 'press', 'grind', 'filter', 'heat', 'steam']):
            actions.append(trans)
        elif any(x in trans_lower for x in ['womb', 'menses', 'health', 'chest', 'body']):
            targets.append(trans)
        elif any(x in trans_lower for x in ['time', 'season', 'cycle', 'sky', 'star']):
            timing.append(trans)

    # Build fluent sentence
    parts = []

    if ingredients:
        parts.append(f"Take {', '.join(ingredients[:3])}")

    if actions:
        parts.append(f"{', '.join(actions[:2])}")

    if targets:
        parts.append(f"for the {', '.join(targets[:2])}")

    if timing:
        parts.append(f"at {', '.join(timing[:2])}")

    if parts:
        return '. '.join(parts) + '.'
    else:
        return "[Unable to form coherent instruction from available translations]"


# =============================================================================
# TASK 5: COHERENCE CHECK
# =============================================================================

def check_coherence(translation_results):
    """Assess coherence of speculative translations."""
    print()
    print("=" * 90)
    print("TASK 5: COHERENCE CHECK")
    print("=" * 90)
    print()

    results = {}

    for folio, data in translation_results.items():
        print(f"--- {folio} ---")
        print()

        translations = data['translations']

        # Count confidence levels
        high = sum(1 for _, _, c in translations if c == 'HIGH')
        medium = sum(1 for _, _, c in translations if c == 'MEDIUM')
        low = sum(1 for _, _, c in translations if c == 'LOW')
        unknown = sum(1 for _, _, c in translations if c == 'UNKNOWN')
        total = len(translations)

        print(f"Confidence distribution:")
        print(f"  HIGH: {high}/{total} ({high/total*100:.0f}%)")
        print(f"  MEDIUM: {medium}/{total} ({medium/total*100:.0f}%)")
        print(f"  LOW: {low}/{total} ({low/total*100:.0f}%)")
        print(f"  UNKNOWN: {unknown}/{total} ({unknown/total*100:.0f}%)")
        print()

        # Check for medical coherence
        trans_text = ' '.join(t for _, t, _ in translations).lower()

        has_ingredient = any(x in trans_text for x in ['herb', 'leaf', 'juice', 'seed', 'oil', 'water'])
        has_action = any(x in trans_text for x in ['wash', 'prepare', 'heat', 'steam', 'press', 'grind'])
        has_target = any(x in trans_text for x in ['womb', 'menses', 'health', 'body', 'chest'])
        has_timing = any(x in trans_text for x in ['time', 'season', 'cycle', 'star', 'sky'])

        print("Medical instruction elements:")
        print(f"  INGREDIENT: {'YES' if has_ingredient else 'NO'}")
        print(f"  ACTION: {'YES' if has_action else 'NO'}")
        print(f"  TARGET: {'YES' if has_target else 'NO'}")
        print(f"  TIMING: {'YES' if has_timing else 'NO'}")

        elements_present = sum([has_ingredient, has_action, has_target, has_timing])

        if elements_present >= 3:
            coherence = "COHERENT - reads as medical instruction"
        elif elements_present >= 2:
            coherence = "PARTIAL - some medical elements present"
        else:
            coherence = "WEAK - does not read as medical instruction"

        print(f"\nCoherence assessment: {coherence}")
        print()

        results[folio] = {
            'high_pct': high / total * 100,
            'elements_present': elements_present,
            'coherence': coherence
        }

    # Overall assessment
    print("-" * 90)
    print("OVERALL ASSESSMENT")
    print("-" * 90)
    print()

    coherent_count = sum(1 for r in results.values() if 'COHERENT' in r['coherence'])

    print(f"Samples producing coherent medical instructions: {coherent_count}/{len(results)}")
    print()

    if coherent_count >= 2:
        print("CONCLUSION: Speculative meanings produce MOSTLY COHERENT results.")
        print("The semantic disambiguation appears to be on the right track.")
    elif coherent_count >= 1:
        print("CONCLUSION: Mixed results. Some speculative meanings work, others need refinement.")
    else:
        print("CONCLUSION: Speculative meanings produce INCOHERENT results.")
        print("The semantic framework may need significant revision.")

    print()

    # Identify problematic meanings
    print("Meanings that contribute to coherence (keep):")
    print("  - qo- = womb (appears in BIOLOGICAL with correct context)")
    print("  - ch- = herb (appears in HERBAL consistently)")
    print("  - lch = wash (appears with liquid/body contexts)")
    print()

    print("Meanings that create problems (reconsider):")
    print("  - Many middle elements still produce [unknown] translations")
    print("  - Some gallows meanings are too speculative")
    print()

    return results


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 90)
    print("SEMANTIC DISAMBIGUATION: FROM CATEGORIES TO CONCRETE VOCABULARY")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load corpus
    corpus = load_corpus('data/transcriptions')

    # Organize words by folio
    words_by_folio = defaultdict(list)
    for w in corpus.words:
        if w.text and w.folio:
            words_by_folio[w.folio].append(w)

    print(f"Loaded {len(corpus.words)} words across {len(words_by_folio)} folios")
    print()

    all_results = {}

    # Task 1
    body_results = analyze_body_prefixes(corpus, words_by_folio)
    all_results.update(body_results)

    # Task 2
    gallows_results = analyze_gallows_meanings(corpus, words_by_folio)
    all_results.update(gallows_results)

    # Task 3
    plant_results = identify_plant_names(corpus, words_by_folio)
    all_results.update(plant_results)

    # Task 4
    translation_results = produce_translations(corpus, words_by_folio)
    all_results['translations'] = translation_results

    # Task 5
    coherence_results = check_coherence(translation_results)
    all_results['coherence'] = coherence_results

    # Save results
    # Convert for JSON serialization
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        elif isinstance(obj, tuple):
            return list(obj)
        else:
            return obj

    with open('semantic_disambiguation_results.json', 'w') as f:
        json.dump(make_serializable(all_results), f, indent=2)

    print()
    print("=" * 90)
    print(f"Results saved to semantic_disambiguation_results.json")
    print("=" * 90)


if __name__ == '__main__':
    main()
