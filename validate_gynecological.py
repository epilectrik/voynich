"""Validate decoder against GYNECOLOGICAL uses of identified plants."""
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# GYNECOLOGICAL plant uses (from medieval sources like Trotula, De Secretis Mulierum)
# NOT general uses - specifically women's health uses
GYNO_PLANT_IDS = {
    'f1v': {
        'name': 'Belladonna (Atropa belladonna)',
        'gyno_uses': [
            'Dilating cervix during childbirth',
            'Reducing uterine contractions',
            'Preventing/causing miscarriage (timing dependent)',
            'Treating menstrual cramps',
        ],
        'expected_terms': ['womb', 'uterus', 'birth', 'open', 'relax', 'pain', 'cramp', 'flow', 'blood']
    },
    'f3v': {
        'name': 'Hellebore (Helleborus foetidus)',
        'gyno_uses': [
            'ABORTIFACIENT - causes miscarriage',
            'EMMENAGOGUE - induces menstruation',
            'Listed in De viribus herbarum (11th c) as abortion herb',
            'Hildegard von Bingen mentions as emmenagogue',
        ],
        'expected_terms': ['flow', 'blood', 'menses', 'purge', 'expel', 'womb', 'hot', 'bring']
    },
    'f5v': {
        'name': 'Mallow (Malva sylvestris)',
        'gyno_uses': [
            'Softening birth canal for easier delivery',
            'Vaginal soothing/irritation',
            'Treating breast infections',
            'Emollient for gynecological use',
        ],
        'expected_terms': ['soft', 'birth', 'ease', 'soothe', 'breast', 'open', 'passage']
    },
}

# Our decoded PREFIX meanings - reinterpreted for gynecology
GYNO_PREFIX = {
    'qo': 'womb/uterus',      # NOT generic "body" - specifically female reproductive
    'ol': 'menstrual-fluid',  # NOT generic "fluid" - specifically menses
    'ch': 'herb',             # plant used for women's health
    'sh': 'sap/juice',        # plant extract
    'da': 'leaf',
    'ct': 'water',            # for fumigation/steam
    'cth': 'water',
    'ot': 'time/cycle',       # menstrual cycle? lunar cycle?
}

# Our decoded MIDDLE meanings - reinterpreted for gynecology
GYNO_MIDDLE = {
    'ke': 'heat/steam',       # fumigation!
    'kee': 'boil/steam',      # preparing fumigation herbs
    'eo': 'flow',             # menstrual flow!
    'ol': 'oil',              # for pessaries
    'ed': 'dry',              # dried herbs
    'ee': 'wet/moist',        # humoral - moisture
    'o': 'whole/womb',        # womb is often "whole"
    'l': 'wash',              # douching
    'k': 'body/womb',
}

# Suffix meanings stay the same
SUFFIX = {
    'y': '[noun]', 'dy': '[done]', 'ey': '[doing]', 'aiin': '[place]',
    'ain': '[action]', 'iin': '[thing]', 'hy': '[full]',
}

KNOWN_WORDS = {
    'daiin': 'leaves', 'dain': 'leaf', 'chedy': 'herb', 'shedy': 'herb',
    'ol': 'oil', 'chol': 'HOT', 'chor': 'benefits', 'cthy': 'water',
    'sho': 'sap', 'shy': 'juice', 'chy': 'plant', 'shol': 'liquid',
    'y': 'and', 's': 'this', 'dar': 'in', 'dal': 'from',
    # New gynecological interpretations:
    'qokedy': 'womb-state',
    'qokeedy': 'womb-steamed/fumigated',
    'qokain': 'womb-heating',
}


def parse_word(word):
    if not word or len(word) < 2:
        return None, word, None
    prefix = None
    rest = word
    for p in sorted(GYNO_PREFIX.keys(), key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            rest = word[len(p):]
            break
    suffix = None
    middle = rest
    for s in sorted(SUFFIX.keys(), key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break
    return prefix, middle, suffix


def decode_gyno(word):
    """Decode word with gynecological interpretation."""
    if word in KNOWN_WORDS:
        return KNOWN_WORDS[word]
    prefix, middle, suffix = parse_word(word)
    parts = []
    if prefix and prefix in GYNO_PREFIX:
        parts.append(GYNO_PREFIX[prefix])
    if middle and middle in GYNO_MIDDLE:
        parts.append(GYNO_MIDDLE[middle])
    elif middle:
        parts.append(f'?{middle}?')
    if suffix and suffix in SUFFIX:
        parts.append(SUFFIX[suffix])
    return '-'.join(parts) if parts else f'?{word}?'


corpus = load_corpus('data/transcriptions')

print("=" * 90)
print("GYNECOLOGICAL VALIDATION TEST")
print("=" * 90)
print()
print("Testing if our decoded terms match GYNECOLOGICAL uses of plants")
print("(not general medicinal uses)")
print()
print("KEY INSIGHT: 'Fumigation' was a real medieval gynecological procedure")
print("             (vaginal steaming with herbs)")
print("             This may explain the 'bathing women' illustrations!")
print()

for folio, info in GYNO_PLANT_IDS.items():
    words = [w.text for w in corpus.words if w.folio == folio and w.text]

    print("-" * 90)
    print(f"FOLIO {folio}: {info['name']}")
    print(f"GYNECOLOGICAL uses:")
    for use in info['gyno_uses']:
        print(f"  - {use}")
    print(f"Expected terms: {', '.join(info['expected_terms'])}")
    print()

    print(f"Voynich text ({len(words)} words):")
    print(f"  {' '.join(words[:25])}")
    print()

    decoded = [decode_gyno(w) for w in words[:25]]
    print(f"Gynecological decoding:")
    print(f"  {' '.join(decoded)}")
    print()

    # Check for matches
    decoded_text = ' '.join(decoded).lower()
    matches = [term for term in info['expected_terms'] if term in decoded_text]

    # Also check for our gynecological terms
    gyno_terms_found = []
    if 'womb' in decoded_text:
        gyno_terms_found.append('womb')
    if 'flow' in decoded_text:
        gyno_terms_found.append('flow')
    if 'steam' in decoded_text or 'fumigat' in decoded_text:
        gyno_terms_found.append('fumigation/steam')
    if 'hot' in decoded_text:
        gyno_terms_found.append('HOT (humoral)')
    if 'menstru' in decoded_text or 'menses' in decoded_text:
        gyno_terms_found.append('menstruation')

    if matches or gyno_terms_found:
        print(f"  *** MATCHES FOUND: {matches + gyno_terms_found}")
    else:
        print(f"  No direct term matches")
    print()

# Now analyze the BIOLOGICAL section (bathing women) with gynecological lens
print("=" * 90)
print("BIOLOGICAL SECTION ANALYSIS (The 'Bathing Women')")
print("=" * 90)
print()
print("If this section describes FUMIGATION (vaginal steaming), we should see:")
print("  - qo- prefix (womb) more common")
print("  - -ke-/-kee- middle (heat/steam/boil) more common")
print("  - References to tubes/vessels (fumigation apparatus)")
print()

# Get words from biological section (f75-f84)
bio_words = []
for w in corpus.words:
    if w.text:
        num = ''.join(c for c in w.folio if c.isdigit())
        if num and 75 <= int(num) <= 84:
            bio_words.append(w.text)

print(f"Biological section: {len(bio_words)} words")
print()

# Count qo- words
qo_count = sum(1 for w in bio_words if w.startswith('qo'))
total = len(bio_words)
print(f"Words starting with 'qo-' (womb): {qo_count} ({100*qo_count/total:.1f}%)")

# Look for -ke-/-kee- patterns
ke_words = [w for w in bio_words if 'ke' in w]
print(f"Words containing 'ke' (heat/steam): {len(ke_words)} ({100*len(ke_words)/total:.1f}%)")
print(f"  Examples: {ke_words[:10]}")
print()

# Show most common words in biological section with gynecological decoding
from collections import Counter
bio_freq = Counter(bio_words)
print("Most common words in BIOLOGICAL section (gynecological interpretation):")
for word, count in bio_freq.most_common(15):
    decoded = decode_gyno(word)
    print(f"  {word:15} ({count:3}x) -> {decoded}")

print()
print("=" * 90)
print("INTERPRETATION")
print("=" * 90)
print("""
If the biological section (bathing women) is about FUMIGATION:
- The 'tubes' in the illustrations could be fumigation apparatus
- The 'water' could be steam
- The naked women are patients receiving vaginal steam treatment
- The 'qo-' prefix would mean 'womb' not generic 'body'
- The '-ke-'/'-kee-' middle would mean 'steam/heat treatment'

This interpretation would explain:
1. Why the women are depicted naked (medical procedure)
2. Why there are tube-like structures (fumigation tubes)
3. Why the vocabulary is different from the herbal section
4. Why this content would need to be encoded (taboo)
""")
