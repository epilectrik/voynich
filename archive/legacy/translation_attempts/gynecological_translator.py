"""Translate Voynich text using gynecological interpretation."""
import sys
sys.path.insert(0, '.')
from collections import Counter
from tools.parser.voynich_parser import load_corpus

# ============================================================================
# GYNECOLOGICAL TRANSLATION SYSTEM
# ============================================================================

# PREFIX = Body part / Domain (gynecological interpretation)
PREFIX = {
    # FEMALE REPRODUCTIVE
    'qo': 'womb',           # NOT generic body - specifically uterus/matrix
    'ol': 'menses',         # menstrual fluid, NOT generic humor
    'so': 'health',         # women's health

    # HERBAL (for gynecological remedies)
    'ch': 'herb',           # medicinal plant
    'sh': 'juice',          # plant extract/sap
    'da': 'leaf',           # folium
    'ct': 'water',          # aqua (for infusions)
    'cth': 'water',         # variant
    'sa': 'seed',           # semen (botanical)

    # PREPARATION
    'lk': 'liquid',         # prepared liquid/decoction
    'op': 'work',           # opus/procedure
    'pc': 'mixture',        # compound remedy

    # TIME/ASTROLOGY (for timing treatments)
    'ot': 'time',           # when to apply treatment
    'ok': 'sky',            # astrological timing
    'ar': 'air',            # element
    'al': 'star',           # stellar influence
    'yk': 'cycle',          # menstrual/lunar cycle
    'yt': 'world',          # mundus
    'or': 'gold/sun',       # solar timing
}

# MIDDLE = Action / Property (gynecological interpretation)
MIDDLE = {
    # FUMIGATION / HEAT TREATMENT
    'ke': 'heat',           # fumigation - applying heat to womb
    'kee': 'steam',         # vaginal steaming
    'ka': 'warm',           # calere - warming
    'kai': 'burn',          # urere - strong heat

    # FLOW / FLUIDS
    'eo': 'flow',           # menstrual flow
    'l': 'wash',            # lavare - cleansing
    'ol': 'oil',            # oleum - for pessaries

    # PREPARATION
    'ko': 'mix',            # miscere
    'ed': 'dry',            # siccus - dried herbs
    'ee': 'moist',          # madidus - wet preparation

    # PROPERTIES
    'or': 'benefit',        # prodesse - therapeutic benefit
    'i': 'green',           # viridis - fresh herb
    'in': 'inside',         # intus - internal application
    'o': 'whole',           # orbis - complete
    'a': 'one',             # unus - single dose
    'ii': 'many',           # multi - multiple doses

    # BODY
    'k': 'body',            # corpus
    't': 'touch',           # tangere - apply
    'te': 'hold',           # tenere - retain

    # CONTAINMENT
    'ch': 'vessel',         # vas - container/womb
    'ck': 'contain',        # continere
    'od': 'give',           # dare - administer
    'd': 'from',            # de - from/of
    'r': 'back',            # re - again/return

    # STATE
    'e': 'being',           # esse
    'y': 'state',           # condition
}

# SUFFIX = Grammar (Latin-derived)
SUFFIX = {
    'y': '',                # -um (neuter noun) - often silent in English
    'dy': '[done]',         # -tus past participle
    'ey': '[ing]',          # -ens present participle
    'aiin': '-place',       # -arium container/place
    'ain': '-tion',         # -atio action noun
    'iin': '-thing',        # -ium substance
    'in': '',               # accusative (often silent)
    'hy': '-ful',           # -osus full of
    'ky': '-like',          # -icus relating to
    'ly': '-type',          # -alis manner
    'ty': '-ness',          # -itas quality
    'ry': '-er',            # -arius agent
    'ar': '-of',            # genitive
    'or': '-er',            # -or agent/doer
    'al': '',               # adjective (context dependent)
    'ol': '-small',         # diminutive
}

# KNOWN COMPLETE WORDS
KNOWN_WORDS = {
    # High confidence
    'daiin': 'leaves',
    'dain': 'leaf',
    'chedy': 'herb',
    'shedy': 'herb',
    'ol': 'oil',
    'chol': 'HOT',          # Humoral term - induces menstruation!
    'chor': 'benefits',
    'cthy': 'water',
    'sho': 'sap',
    'shy': 'juice',
    'chy': 'plant',
    'shol': 'liquid',
    'shor': 'extract',

    # Function words
    'y': 'and',
    's': 'this',
    'or': 'gold',
    'ar': 'air',
    'al': 'of',
    'dar': 'in',
    'dal': 'from',

    # Gynecological terms
    'qol': 'womb-fluid',
    'qokal': 'womb-heat',
    'qokedy': 'fumigated',      # womb-heat-[done]
    'qokeedy': 'steam-treated', # womb-steam-[done]
    'qokain': 'fumigation',     # womb-heat-action
    'qokeey': 'steaming',       # womb-steam-[ing]
    'qokey': 'heat-treatment',
    'qokeed': 'steamed',

    # Time
    'otaiin': 'time',
    'otey': 'timing',
}

# PHRASE TRANSLATIONS
PHRASES = {
    ('chol', 'chol'): 'very-HOT',
    ('chol', 'daiin'): 'hot leaves',
    ('ol', 'chedy'): 'herb-oil',
    ('ol', 'shedy'): 'herb-oil',
    ('daiin', 'daiin'): 'many leaves',
    ('dar', 'qo'): 'in the womb',
    ('dal', 'qo'): 'from the womb',
    ('qokedy', 'shedy'): 'fumigated with herb',
    ('qokeedy', 'chedy'): 'steamed with herb',
}


def parse_word(word):
    """Parse word into prefix + middle + suffix."""
    if not word or len(word) < 2:
        return None, word, None

    prefix = None
    rest = word
    for p in sorted(PREFIX.keys(), key=len, reverse=True):
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


def translate_word(word):
    """Translate a single Voynich word."""
    if word in KNOWN_WORDS:
        return KNOWN_WORDS[word]

    prefix, middle, suffix = parse_word(word)
    parts = []

    if prefix and prefix in PREFIX:
        parts.append(PREFIX[prefix])

    if middle:
        if middle in MIDDLE:
            parts.append(MIDDLE[middle])
        else:
            parts.append(f'?{middle}?')

    if suffix and suffix in SUFFIX:
        suf = SUFFIX[suffix]
        if suf:  # Skip empty suffixes
            parts.append(suf)

    if parts:
        return '-'.join(parts)
    return f'?{word}?'


def translate_with_phrases(words):
    """Translate with phrase recognition."""
    result = []
    i = 0

    while i < len(words):
        if i + 1 < len(words):
            pair = (words[i], words[i+1])
            if pair in PHRASES:
                result.append(PHRASES[pair])
                i += 2
                continue

        result.append(translate_word(words[i]))
        i += 1

    return result


def analyze_translation_quality(translations):
    """Analyze how much we successfully translated."""
    total = len(translations)
    unknown = sum(1 for t in translations if '?' in t)
    known = total - unknown

    return {
        'total': total,
        'known': known,
        'unknown': unknown,
        'coverage': known / total * 100 if total > 0 else 0
    }


# ============================================================================
# MAIN
# ============================================================================

corpus = load_corpus('data/transcriptions')

print("=" * 90)
print("GYNECOLOGICAL TRANSLATION OF VOYNICH MANUSCRIPT")
print("=" * 90)
print()
print("Key interpretations:")
print("  qo- = womb/uterus (NOT generic 'body')")
print("  -ke-/-kee- = heat/steam treatment (fumigation)")
print("  ol- = menstrual fluid")
print("  chol = HOT (humoral term - induces menstruation)")
print()

# Translate the BIOLOGICAL section (bathing women = fumigation)
print("=" * 90)
print("BIOLOGICAL SECTION (f75-f84) - FUMIGATION PROCEDURES")
print("=" * 90)
print()

bio_folios = ['f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v', 'f78r', 'f78v']

for folio in bio_folios:
    words = [w.text for w in corpus.words if w.folio == folio and w.text]
    if not words:
        continue

    print(f"--- {folio} ---")

    # Translate in chunks of 8 words
    for i in range(0, min(24, len(words)), 8):
        chunk = words[i:i+8]
        trans = translate_with_phrases(chunk)

        print(f"VOY: {' '.join(chunk)}")
        print(f"ENG: {' '.join(trans)}")
        print()

    # Show quality stats
    all_trans = translate_with_phrases(words)
    quality = analyze_translation_quality(all_trans)
    print(f"Coverage: {quality['known']}/{quality['total']} ({quality['coverage']:.1f}%)")
    print()

# Translate herbal section with gynecological plants
print("=" * 90)
print("HERBAL SECTION - GYNECOLOGICAL PLANTS")
print("=" * 90)
print()

gyno_plants = {
    'f1v': 'Belladonna (cervix dilation, miscarriage)',
    'f3v': 'Hellebore (ABORTIFACIENT, emmenagogue)',
    'f5v': 'Mallow (softening birth canal)',
}

for folio, plant in gyno_plants.items():
    words = [w.text for w in corpus.words if w.folio == folio and w.text]
    if not words:
        continue

    print(f"--- {folio}: {plant} ---")

    # Translate first 32 words
    for i in range(0, min(32, len(words)), 8):
        chunk = words[i:i+8]
        trans = translate_with_phrases(chunk)

        print(f"VOY: {' '.join(chunk)}")
        print(f"ENG: {' '.join(trans)}")
        print()

    # Quality
    all_trans = translate_with_phrases(words[:32])
    quality = analyze_translation_quality(all_trans)
    print(f"Coverage: {quality['known']}/{quality['total']} ({quality['coverage']:.1f}%)")
    print()

# Summary of unknown elements
print("=" * 90)
print("UNKNOWN ELEMENTS TO DECODE")
print("=" * 90)
print()

# Collect all unknown middles
all_words = [w.text for w in corpus.words if w.text]
unknown_middles = Counter()

for word in all_words:
    prefix, middle, suffix = parse_word(word)
    if middle and middle not in MIDDLE and len(middle) > 0:
        unknown_middles[middle] += 1

print("Most frequent unknown MIDDLE elements:")
for middle, count in unknown_middles.most_common(20):
    print(f"  ?{middle}? ({count}x)")

print()
print("These unknown elements are what prevent full translation.")
print("Decoding them is the next major task.")
