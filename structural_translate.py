"""Structural translation using PREFIX = CATEGORY system."""
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# PREFIX meanings based on section analysis
PREFIX_MEANINGS = {
    # ZODIAC prefixes - celestial/time
    'ot': ('TIME', 'tempus'),      # time, season, period
    'al': ('STAR', 'stella'),       # star, zodiac sign
    'ar': ('ARIES', 'aries'),       # ram, Aries, spring
    'ok': ('SKY', 'caelum'),        # sky, heaven, celestial
    'yk': ('CYCLE', 'cyclus'),      # cycle, return, repetition

    # BIOLOGICAL prefixes - body
    'ol': ('OIL/FLUID', 'oleum'),   # oil, bodily fluid
    'qo': ('BODY', 'corpus'),       # body, physical
    'so': ('HEALTH', 'salus'),      # health, wellbeing

    # HERBAL prefixes - plants
    'ct': ('WATER', 'aqua'),        # water, liquid
    'cth': ('WATER', 'aqua'),       # water variant
    'da': ('LEAF', 'folium'),       # leaf, foliage
    'ch': ('PLANT', 'herba'),       # herb, plant

    # RECIPES prefixes - procedures
    'lk': ('LIQUID', 'liquor'),     # liquid, solution
    'sh': ('JUICE', 'succus'),      # juice, sap

    # COSMOLOGICAL
    'yt': ('COSMIC', 'mundus'),     # world, cosmic
    'or': ('GOLD', 'aurum'),        # gold, precious

    # Other common
    'sa': ('SEED', 'semen'),        # seed
    'op': ('WORK', 'opus'),         # work, preparation
    'pc': ('CHEST', 'pectus'),      # chest, breast
}

# SUFFIX meanings (grammatical)
SUFFIX_MEANINGS = {
    'aiin': ('PLACE', '-arium'),    # place/container
    'ain': ('ACTION', '-atio'),     # action/process
    'iin': ('THING', '-ium'),       # thing/substance
    'in': ('IN', '-in/-im'),        # in/into
    'dy': ('STATE', '-tus'),        # state/condition
    'ey': ('DOING', '-ens'),        # present participle
    'hy': ('FULL', '-osus'),        # full of
    'ky': ('TYPE', '-icus'),        # relating to
    'ly': ('WAY', '-alis'),         # in manner of
    'ty': ('QUALITY', '-tas'),      # quality
    'ry': ('AGENT', '-arius'),      # one who does
    'y': ('NOUN', '-us/-um'),       # basic noun ending
    'ar': ('OF', '-aris'),          # of/relating to
    'or': ('DOER', '-or'),          # one who does
    'al': ('ADJ', '-alis'),         # adjective
    'ol': ('DIM', '-olum'),         # small/diminutive
}

# MIDDLE elements (the actual content - more speculative)
MIDDLE_MEANINGS = {
    'ke': 'cook/prepare',
    'ka': 'heat/warm',
    'kee': 'boil',
    'kai': 'burning',
    'ed': 'dry',
    'ee': 'liquid',
    'e': 'essence',
    'o': 'whole',
    'a': 'one',
    'ai': 'life/vital',
    'eo': 'flow',
    'ii': 'intense',
    'ch': 'vessel',
    'ck': 'contain',
    'od': 'give',
    'ta': 'take',
    'te': 'hold',
    'ko': 'mix',
}

def parse_word(word):
    """Parse word into PREFIX + MIDDLE + SUFFIX."""
    if not word or len(word) < 2:
        return None, word, None

    # Find prefix (try longer first)
    prefix = None
    rest = word
    for p in sorted(PREFIX_MEANINGS.keys(), key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            rest = word[len(p):]
            break

    # Find suffix (try longer first)
    suffix = None
    middle = rest
    for s in sorted(SUFFIX_MEANINGS.keys(), key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    return prefix, middle, suffix

def translate_word(word):
    """Translate a single word structurally."""
    prefix, middle, suffix = parse_word(word)

    parts = []

    if prefix and prefix in PREFIX_MEANINGS:
        cat, latin = PREFIX_MEANINGS[prefix]
        parts.append(f"{cat}")
    else:
        parts.append(f"[{prefix or '?'}]")

    if middle:
        if middle in MIDDLE_MEANINGS:
            parts.append(MIDDLE_MEANINGS[middle])
        else:
            parts.append(f"({middle})")

    if suffix and suffix in SUFFIX_MEANINGS:
        gram, latin = SUFFIX_MEANINGS[suffix]
        parts.append(f"-{gram}")

    return ' '.join(parts)

# Load and translate f1r
corpus = load_corpus('data/transcriptions')
f1r_words = [w.text for w in corpus.words if w.folio == 'f1r' and w.text]

print("=" * 80)
print("STRUCTURAL TRANSLATION - Folio f1r")
print("=" * 80)
print()
print("Format: PREFIX[category] + MIDDLE(content) + SUFFIX[-grammar]")
print()

# Group into lines of 6
for i in range(0, min(len(f1r_words), 60), 6):  # First 10 lines
    line_num = i // 6 + 1
    chunk = f1r_words[i:i+6]

    print(f"Line {line_num}:")
    print(f"  VOY: {' '.join(chunk)}")

    translations = [translate_word(w) for w in chunk]
    print(f"  ENG: {' | '.join(translations)}")
    print()

# Show the parsing for detailed view
print("=" * 80)
print("DETAILED WORD PARSING (first 20 words)")
print("=" * 80)
print()
print(f"{'WORD':<15} {'PREFIX':<8} {'MIDDLE':<10} {'SUFFIX':<8} {'TRANSLATION':<30}")
print("-" * 80)

for word in f1r_words[:20]:
    prefix, middle, suffix = parse_word(word)

    p_meaning = PREFIX_MEANINGS.get(prefix, ('?', '?'))[0] if prefix else '-'
    s_meaning = SUFFIX_MEANINGS.get(suffix, ('?', '?'))[0] if suffix else '-'
    m_meaning = MIDDLE_MEANINGS.get(middle, middle)

    trans = translate_word(word)
    print(f"{word:<15} {prefix or '-':<8} {middle:<10} {suffix or '-':<8} {trans:<30}")
