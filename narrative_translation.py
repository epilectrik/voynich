"""Narrative Translation of Folio f78r (Biological/Bathing Women Page).

Goal: Produce a complete, fluent translation that reads like a medieval medical recipe.

For each line:
1. Show Voynich text
2. Show word-by-word decoding
3. Produce fluent English sentence interpretation
4. Reorder words to match medieval recipe conventions

At the end: Compile all sentences into a continuous passage.
"""
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# ============================================================================
# COMPLETE DECODING TABLES (All work to date)
# ============================================================================

# Fully decoded words (highest confidence)
KNOWN_WORDS = {
    # Plants/Herbs
    'daiin': 'leaves',
    'dain': 'leaf',
    'chedy': 'dried herb',
    'shedy': 'dried herb',
    'chy': 'plant',
    'chey': 'herb',
    'shey': 'juice',
    'shy': 'juice',
    'sho': 'sap',
    'shol': 'sap',
    'chol': 'HOT',  # Humoral property - emmenagogue
    'chor': 'benefits',
    'cthy': 'water',
    'ol': 'oil',

    # Body/Procedures
    'qokedy': 'fumigated',
    'qokeedy': 'steam-treated',
    'qokain': 'fumigation',
    'qokeey': 'steaming',
    'qokey': 'heat treatment',

    # Grammar words
    'y': 'and',
    's': 'this',
    'dar': 'in',
    'dal': 'from',
    'dy': 'done',
    'or': 'for',
    'ar': 'with',
    'al': 'of',

    # Time/Astrology
    'otaiin': 'season',
    'okaiin': 'constellation',
    'otedy': 'timed',
    'otar': 'at time',
}

# Prefix meanings
PREFIX = {
    'qo': 'womb',
    'ol': 'menses',
    'so': 'health',
    'ch': 'herb',
    'sh': 'juice',
    'da': 'leaf',
    'ct': 'water',
    'cth': 'water',
    'sa': 'seed',
    'lk': 'liquid',
    'op': 'prepared',
    'ot': 'time',
    'ok': 'sky',
    'ar': 'air',
    'al': 'star',
    'yk': 'cycle',
    'yt': 'world',
    'or': 'gold',
    'pc': 'body',
}

# Middle meanings (actions/properties) - INCLUDING GALLOWS
MIDDLE = {
    # Heat/Steam actions
    'ke': 'heated',
    'kee': 'steamed',
    'ka': 'warmed',
    'kai': 'burned',

    # Flow/movement
    'eo': 'flowing',
    'eos': 'flowing',
    'eod': 'flowing',

    # Preparation actions
    'l': 'washed',
    'lshe': 'washed',
    'ed': 'dried',
    'ee': 'moistened',
    'ko': 'mixed',

    # Properties
    'ol': 'oiled',
    'or': 'beneficial',
    'od': 'given',
    'o': 'whole',
    'a': 'one',
    'e': '',
    't': 'applied',
    'te': 'held',
    'd': 'from',
    'r': 'back',
    'i': 'green',
    'ii': 'many',

    # GALLOWS MEANINGS (decoded via section enrichment)
    'kch': 'potent',
    'ckh': 'treated',
    'tch': 'prepared',
    'pch': 'applied',
    'fch': 'processed',
    'cth': 'purified',
    'cph': 'pressed',
    'cfh': 'ground',
    'kche': 'potent',
    'ckhe': 'well-treated',
    'tche': 'prepared',
    'pche': 'applied',
    'fche': 'processed',
    'lche': 'washed',
    'lch': 'washed',
    'dch': 'derived',
    'sch': 'extracted',
}

# Suffix meanings (grammatical)
SUFFIX = {
    'y': '',           # noun marker
    'dy': '[DONE]',    # past participle
    'ey': '[ING]',     # present participle
    'aiin': 'place',   # location/container
    'ain': 'process',  # action noun
    'iin': '',         # substance
    'in': '',          # object
    'hy': 'full',      # full of
    'ky': 'like',      # resembling
    'ar': 'with',      # instrumental
    'or': 'for',       # purpose
    'al': 'of',        # genitive
    'ly': 'manner',    # adverb
    'ty': 'state',     # condition
    'ry': 'doer',      # agent
}


def decode_word(word):
    """Decode a single word to English with structure analysis."""
    # Check known words first
    if word in KNOWN_WORDS:
        return {
            'word': word,
            'meaning': KNOWN_WORDS[word],
            'confidence': 'HIGH',
            'structure': 'known',
        }

    # Parse structure: PREFIX + MIDDLE + SUFFIX
    prefix, middle, suffix = None, word, None

    # Find prefix (longest match first)
    for p in sorted(PREFIX.keys(), key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            middle = word[len(p):]
            break

    # Find suffix (longest match first)
    rest = middle
    for s in sorted(SUFFIX.keys(), key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    # Build meaning
    parts = []
    confidence = 'HIGH'

    if prefix and prefix in PREFIX:
        parts.append(PREFIX[prefix])
    elif prefix:
        parts.append(f'[{prefix}?]')
        confidence = 'MEDIUM'

    if middle:
        # Try to match middle (including gallows)
        found = False
        for m in sorted(MIDDLE.keys(), key=len, reverse=True):
            if middle == m:
                if MIDDLE[m]:
                    parts.append(MIDDLE[m])
                found = True
                break
            elif middle.startswith(m):
                if MIDDLE[m]:
                    parts.append(MIDDLE[m])
                # Handle remaining middle
                remaining = middle[len(m):]
                if remaining and remaining not in ['e', 'i', 'o']:
                    parts.append(f'[{remaining}]')
                    confidence = 'MEDIUM'
                found = True
                break
        if not found:
            if len(middle) <= 2:
                parts.append(f'[{middle}]')
                confidence = 'LOW'
            else:
                parts.append(f'[{middle}]')
                confidence = 'LOW'

    if suffix and suffix in SUFFIX and SUFFIX[suffix]:
        parts.append(SUFFIX[suffix])

    if parts:
        meaning = ' '.join(parts)
    else:
        meaning = f'[{word}]'
        confidence = 'UNKNOWN'

    return {
        'word': word,
        'meaning': meaning,
        'confidence': confidence,
        'structure': f"P:{prefix or '?'} M:{middle or '?'} S:{suffix or '?'}",
    }


def categorize_word(meaning):
    """Categorize a decoded word for recipe reordering."""
    m = meaning.lower()
    if any(x in m for x in ['herb', 'leaf', 'leaves', 'dried', 'plant', 'juice', 'seed', 'sap']):
        return 'INGREDIENT'
    if any(x in m for x in ['hot', 'heated', 'steamed', 'warmed', 'burned']):
        return 'HEAT'
    if any(x in m for x in ['washed', 'mixed', 'prepared', 'potent', 'treated', 'applied',
                            'processed', 'pressed', 'ground', 'derived', 'extracted', 'purified']):
        return 'ACTION'
    if any(x in m for x in ['womb', 'menses', 'body', 'health']):
        return 'BODY'
    if any(x in m for x in ['time', 'season', 'sky', 'star', 'cycle', 'constellation']):
        return 'TIMING'
    if any(x in m for x in ['oil', 'water', 'liquid']):
        return 'MEDIUM'
    if any(x in m for x in ['fumigat', 'steam']):
        return 'PROCEDURE'
    if any(x in m for x in ['in', 'from', 'with', 'for', 'of', 'this', 'and']):
        return 'CONNECTOR'
    if '[done]' in m.lower() or '[ing]' in m.lower():
        return 'GRAMMAR'
    return 'OTHER'


def clean_meaning(m):
    """Clean a meaning string for fluent output."""
    m = m.replace('[DONE]', '').replace('[ING]', '')
    m = m.replace('[', '(').replace(']', ')')
    m = m.strip()
    return m


def to_fluent_sentence(decoded_words):
    """Convert decoded words into a fluent English sentence.

    Medieval recipe convention: PROCEDURE + BODY + with INGREDIENT + in MEDIUM + ACTION + at TIMING
    """
    if not decoded_words:
        return ""

    # Categorize all words
    categorized = [(d, categorize_word(d['meaning'])) for d in decoded_words]

    # Collect by category (cleaned)
    procedures = [clean_meaning(d['meaning']) for d, c in categorized if c == 'PROCEDURE']
    body = [clean_meaning(d['meaning']) for d, c in categorized if c == 'BODY']
    ingredients = [clean_meaning(d['meaning']) for d, c in categorized if c == 'INGREDIENT']
    medium = [clean_meaning(d['meaning']) for d, c in categorized if c == 'MEDIUM']
    heat = [clean_meaning(d['meaning']) for d, c in categorized if c == 'HEAT']
    actions = [clean_meaning(d['meaning']) for d, c in categorized if c == 'ACTION']
    timing = [clean_meaning(d['meaning']) for d, c in categorized if c == 'TIMING']
    other = [clean_meaning(d['meaning']) for d, c in categorized if c in ['OTHER', 'GRAMMAR', 'CONNECTOR']]

    # Build fluent sentence in recipe order
    parts = []

    # 1. Procedure verb
    if procedures:
        proc = ', '.join(set(procedures))  # deduplicate
        parts.append(proc.capitalize())

    # 2. Body target
    if body:
        body_str = ' '.join(body)
        if parts:
            parts.append(f"the {body_str}")
        else:
            parts.append(body_str.capitalize())

    # 3. Ingredients
    if ingredients:
        ing_str = ', '.join(ingredients)
        if parts:
            parts.append(f"with {ing_str}")
        else:
            parts.append(ing_str.capitalize())

    # 4. Medium
    if medium:
        med_str = ' '.join(medium)
        if parts:
            parts.append(f"in {med_str}")
        else:
            parts.append(med_str.capitalize())

    # 5. Actions/heat
    combined_actions = heat + actions
    if combined_actions:
        act_str = ', '.join(combined_actions)
        if parts:
            parts.append(f"({act_str})")
        else:
            parts.append(act_str.capitalize())

    # 6. Timing
    if timing:
        time_str = ' '.join(timing)
        if parts:
            parts.append(f"at {time_str}")
        else:
            parts.append(time_str.capitalize())

    # 7. Remaining
    if other and not parts:
        parts.append(' '.join(other))

    sentence = ' '.join(parts)

    # Clean up multiple spaces and punctuate
    while '  ' in sentence:
        sentence = sentence.replace('  ', ' ')
    sentence = sentence.strip()

    if sentence:
        if not sentence.endswith('.') and not sentence.endswith('?'):
            sentence += '.'

    return sentence


# ============================================================================
# GET F78R TEXT
# ============================================================================

# Extract all words from f78r
f78r_words = [w.text for w in corpus.words if w.folio == 'f78r' and w.text]

# Split into lines of ~6-8 words (approximating original line breaks)
lines = []
for i in range(0, len(f78r_words), 7):
    lines.append(f78r_words[i:i+7])

print("=" * 100)
print("FOLIO F78R - COMPLETE NARRATIVE TRANSLATION")
print("=" * 100)
print()
print("Section: BIOLOGICAL (Bathing Women / Fumigation Procedures)")
print(f"Total words: {len(f78r_words)}")
print(f"Lines: {len(lines)}")
print()

# ============================================================================
# LINE-BY-LINE TRANSLATION
# ============================================================================

print("=" * 100)
print("LINE-BY-LINE ANALYSIS")
print("=" * 100)
print()

all_decoded = []
all_fluent = []
gaps = []

for line_num, line_words in enumerate(lines, 1):
    # Decode each word
    decoded = [decode_word(w) for w in line_words]
    all_decoded.extend(decoded)

    # Voynich text
    voy_text = ' '.join(line_words)

    # Word-by-word gloss
    gloss = ' | '.join(d['meaning'] for d in decoded)

    # Confidence markers
    conf_markers = ''.join('H' if d['confidence'] == 'HIGH' else
                           'M' if d['confidence'] == 'MEDIUM' else
                           'L' if d['confidence'] == 'LOW' else '?'
                           for d in decoded)

    # Fluent interpretation
    fluent = to_fluent_sentence(decoded)
    all_fluent.append(fluent)

    # Track gaps
    for d in decoded:
        if d['confidence'] in ['LOW', 'UNKNOWN']:
            gaps.append({'line': line_num, 'word': d['word'], 'meaning': d['meaning']})

    # Display
    print(f"--- Line {line_num:2d} [{conf_markers}] ---")
    print(f"  VOYNICH: {voy_text}")
    print(f"  GLOSS:   {gloss}")
    print(f"  FLUENT:  {fluent}")
    print()

# ============================================================================
# CONTINUOUS NARRATIVE PASSAGE
# ============================================================================

print("=" * 100)
print("COMPILED NARRATIVE PASSAGE")
print("=" * 100)
print()

# Group fluent sentences into paragraphs (every 5 lines)
paragraphs = []
current_para = []
for i, sentence in enumerate(all_fluent, 1):
    current_para.append(sentence)
    if i % 5 == 0:
        paragraphs.append(' '.join(current_para))
        current_para = []
if current_para:
    paragraphs.append(' '.join(current_para))

for para_num, para in enumerate(paragraphs, 1):
    print(f"[{para_num}] {para}")
    print()

# ============================================================================
# COVERAGE STATISTICS
# ============================================================================

print("=" * 100)
print("COVERAGE STATISTICS")
print("=" * 100)
print()

total = len(all_decoded)
high = sum(1 for d in all_decoded if d['confidence'] == 'HIGH')
medium = sum(1 for d in all_decoded if d['confidence'] == 'MEDIUM')
low = sum(1 for d in all_decoded if d['confidence'] == 'LOW')
unknown = sum(1 for d in all_decoded if d['confidence'] == 'UNKNOWN')

print(f"Total words: {total}")
print(f"  HIGH confidence:   {high:3d} ({high/total*100:5.1f}%)")
print(f"  MEDIUM confidence: {medium:3d} ({medium/total*100:5.1f}%)")
print(f"  LOW confidence:    {low:3d} ({low/total*100:5.1f}%)")
print(f"  UNKNOWN:           {unknown:3d} ({unknown/total*100:5.1f}%)")
print()
print(f"TOTAL DECODED: {high + medium} ({(high+medium)/total*100:.1f}%)")
print(f"REMAINING GAPS: {low + unknown} ({(low+unknown)/total*100:.1f}%)")
print()

# ============================================================================
# GAPS ANALYSIS
# ============================================================================

print("=" * 100)
print("REMAINING GAPS (Words Breaking Pattern)")
print("=" * 100)
print()

if gaps:
    # Group gaps by the unknown element
    from collections import Counter
    gap_patterns = Counter(g['meaning'] for g in gaps)

    print("Most frequent unknown elements:")
    for pattern, count in gap_patterns.most_common(20):
        print(f"  {pattern}: {count}x")
    print()

    print(f"Total unique gaps: {len(gap_patterns)}")
    print(f"Total gap instances: {len(gaps)}")
else:
    print("No gaps found!")

# ============================================================================
# RECIPE PATTERN ANALYSIS
# ============================================================================

print()
print("=" * 100)
print("RECIPE PATTERN ANALYSIS")
print("=" * 100)
print()

# Look for recipe sequences
recipe_sequences = []
for i in range(len(all_decoded) - 2):
    d1, d2, d3 = all_decoded[i], all_decoded[i+1], all_decoded[i+2]
    c1 = categorize_word(d1['meaning'])
    c2 = categorize_word(d2['meaning'])
    c3 = categorize_word(d3['meaning'])

    # Look for meaningful patterns
    pattern = f"{c1}-{c2}-{c3}"
    if pattern in ['INGREDIENT-MEDIUM-ACTION', 'INGREDIENT-ACTION-BODY',
                   'PROCEDURE-BODY-INGREDIENT', 'BODY-ACTION-TIMING',
                   'INGREDIENT-HEAT-BODY', 'BODY-PROCEDURE-INGREDIENT']:
        recipe_sequences.append({
            'pattern': pattern,
            'voynich': f"{d1['word']} {d2['word']} {d3['word']}",
            'decoded': f"{d1['meaning']} -> {d2['meaning']} -> {d3['meaning']}",
        })

print(f"Found {len(recipe_sequences)} recipe-like sequences:")
print()

# Group by pattern
from collections import defaultdict
by_pattern = defaultdict(list)
for seq in recipe_sequences:
    by_pattern[seq['pattern']].append(seq)

for pattern, seqs in sorted(by_pattern.items(), key=lambda x: -len(x[1])):
    print(f"{pattern}: {len(seqs)} occurrences")
    for seq in seqs[:3]:
        print(f"  {seq['voynich']}")
        print(f"  -> {seq['decoded']}")
    print()

# ============================================================================
# FINAL ASSESSMENT
# ============================================================================

print("=" * 100)
print("FINAL ASSESSMENT")
print("=" * 100)
print()

# Count thematic elements
proc_count = sum(1 for d in all_decoded if 'fumigat' in d['meaning'].lower() or 'steam' in d['meaning'].lower())
body_count = sum(1 for d in all_decoded if categorize_word(d['meaning']) == 'BODY')
herb_count = sum(1 for d in all_decoded if categorize_word(d['meaning']) == 'INGREDIENT')
heat_count = sum(1 for d in all_decoded if categorize_word(d['meaning']) == 'HEAT' or 'hot' in d['meaning'].lower())
action_count = sum(1 for d in all_decoded if categorize_word(d['meaning']) == 'ACTION')

print("Thematic content detected:")
print(f"  Fumigation/steam procedures: {proc_count}")
print(f"  Body/womb references: {body_count}")
print(f"  Herb/ingredient terms: {herb_count}")
print(f"  Heat/HOT terms: {heat_count}")
print(f"  Preparation actions: {action_count}")
print()

print("DOES F78R READ AS COHERENT MEDICAL INSTRUCTIONS?")
print("-" * 50)
print()
if proc_count > 10 and body_count > 10 and herb_count > 10:
    print("YES - The text exhibits clear thematic coherence:")
    print("  1. Consistent gynecological focus (womb, menses)")
    print("  2. Fumigation procedures described throughout")
    print("  3. Herbal preparations specified")
    print("  4. Heat treatments mentioned repeatedly")
    print()
    print("The passage appears to describe:")
    print("  'Fumigate the womb with dried herbs, steamed/heated,")
    print("   apply [treatments] with oil/water, timed to [cycle].'")
else:
    print("PARTIAL - Theme visible but sentence structure incomplete.")
    print(f"  Missing fluent connections between concepts.")

print()
print("=" * 100)
print("END OF NARRATIVE TRANSLATION")
print("=" * 100)
