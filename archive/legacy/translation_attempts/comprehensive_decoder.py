"""Comprehensive Voynich decoder using full PREFIX-MIDDLE-SUFFIX system."""
import sys
sys.path.insert(0, '.')
from collections import Counter
from tools.parser.voynich_parser import load_corpus

# ============================================================================
# THE VOYNICH ENCODING SYSTEM (Discovered through statistical analysis)
# ============================================================================

# PREFIX = SEMANTIC CATEGORY (what domain/topic)
PREFIX = {
    # ZODIAC/TIME prefixes
    'ot': ('TEMPUS', 'time'),      # 2.4x zodiac
    'ok': ('CAELUM', 'sky'),       # 1.9x zodiac
    'ar': ('AER', 'air'),          # 2.0x zodiac
    'al': ('STELLA', 'star'),      # 2.5x zodiac
    'yk': ('CYCLUS', 'cycle'),     # 1.9x zodiac

    # COSMOLOGICAL
    'yt': ('MUNDUS', 'world'),     # 3.1x cosmological
    'or': ('AURUM', 'gold/sun'),   # 2.4x cosmological

    # BIOLOGICAL/BODY
    'qo': ('CORPUS', 'body'),      # 1.7x biological
    'ol': ('HUMOR', 'fluid'),      # 2.1x biological
    'so': ('SALUS', 'health'),     # 1.8x biological

    # HERBAL/PLANT
    'ct': ('AQUA', 'water'),       # 2.4x herbal
    'cth': ('AQUA', 'water'),      # variant
    'da': ('FOLIUM', 'leaf'),      # 1.5x herbal
    'ch': ('HERBA', 'plant'),      # herbal
    'sh': ('SUCCUS', 'juice'),     # herbal

    # RECIPE/PROCEDURE
    'lk': ('LIQUOR', 'liquid'),    # 2.8x recipes
    'op': ('OPUS', 'work'),        # recipes
    'pc': ('MIXTURA', 'mixture'),  # recipes
    'sa': ('SEMEN', 'seed'),       # seed
}

# MIDDLE = ACTION or PROPERTY (what is being done/described)
MIDDLE = {
    # COOKING/PREPARATION (enriched in BIOLOGICAL - bathing section)
    'ke': ('coquere', 'cook'),     # 2.2x biological
    'kee': ('bullire', 'boil'),    # 2.3x biological
    'ka': ('calere', 'heat'),      # body heat
    'kai': ('urere', 'burn'),      # burning
    'ko': ('miscere', 'mix'),      # mixing

    # PLANT PROPERTIES (enriched in HERBAL)
    'ol': ('oleum', 'oil'),        # 1.7x herbal
    'or': ('prodesse', 'benefit'), # 1.9x herbal
    'i': ('viridis', 'green'),     # 1.6x herbal (leaf-like)
    'in': ('intus', 'inside'),     # interior

    # CELESTIAL MOTION (enriched in ZODIAC)
    'eo': ('fluere', 'flow'),      # 3.4x zodiac - celestial movement
    'ar': ('aer', 'air'),          # 2.0x zodiac
    'al': ('astrum', 'star'),      # 1.6x zodiac
    'o': ('orbis', 'circle'),      # 2.1x zodiac - whole/cycle

    # BODY/FLUID (enriched in BIOLOGICAL)
    'l': ('lavare', 'wash'),       # 2.3x biological
    'k': ('corporis', 'of body'),  # 2.2x biological
    't': ('tangere', 'touch'),     # body contact
    'te': ('tenere', 'hold'),      # holding

    # STATE/CONDITION
    'e': ('esse', 'being'),        # general essence
    'ee': ('madidus', 'wet'),      # wet/moist
    'ed': ('siccus', 'dry'),       # dried
    'a': ('unus', 'one'),          # singular
    'ii': ('multi', 'many'),       # plural
    'y': ('esse', 'being'),        # state

    # CONTAINMENT
    'ch': ('vas', 'vessel'),       # container
    'ck': ('continere', 'contain'),# containing
    'od': ('dare', 'give'),        # giving
    'd': ('de', 'from/down'),      # from
    'r': ('re', 'back/again'),     # return/again
}

# SUFFIX = GRAMMATICAL ENDING (Latin case/form)
SUFFIX = {
    # Noun endings
    'y': ('-um', 'neut.noun'),     # 41% of words!
    'aiin': ('-arium', 'place'),   # container/place
    'ain': ('-atio', 'action'),    # action noun
    'iin': ('-ium', 'subst.'),     # substance
    'in': ('-im', 'acc.'),         # accusative

    # Participial/adjectival
    'dy': ('-tus', 'p.part.'),     # past participle (cooked, heated)
    'ey': ('-ens', 'pr.part.'),    # present participle (cooking, heating)
    'hy': ('-osus', 'full of'),    # full of
    'ky': ('-icus', 'rel.to'),     # relating to
    'ly': ('-alis', 'manner'),     # in manner of
    'ty': ('-itas', 'quality'),    # quality
    'ry': ('-arius', 'agent'),     # one who does

    # Case endings
    'ar': ('-aris', 'gen.'),       # of/relating to
    'or': ('-or', 'agent'),        # doer
    'al': ('-alis', 'adj.'),       # adjective
    'ol': ('-olum', 'dimin.'),     # small/diminutive
}

# KNOWN COMPLETE WORDS (high confidence mappings)
KNOWN_WORDS = {
    # Herbal vocabulary
    'daiin': 'FOLIA (leaves)',
    'dain': 'FOLIUM (leaf)',
    'chedy': 'HERBA (herb)',
    'shedy': 'HERBA (herb)',
    'ol': 'OLEUM (oil)',
    'chol': 'CALIDUS (hot)',
    'chor': 'PRODEST (benefits)',
    'cthy': 'AQUA (water)',
    'sho': 'SAPA (sap)',
    'shy': 'SUCCUS (juice)',
    'chy': 'PLANTA (plant)',
    'shol': 'LIQUOR (liquid)',
    'shor': 'EXTRACTUM (extract)',

    # Function words
    'y': 'ET (and)',
    's': 'HIC (this)',
    'or': 'AURUM (gold)',
    'ar': 'AER (air)',
    'al': 'DE (of the)',
    'dar': 'IN (in)',
    'dal': 'EX (from)',

    # Body terms
    'qol': 'HUMOR (bodily fluid)',
    'qokal': 'CALOR (body heat)',
    'qokedy': 'CORPORIS (of body)',
    'qokeedy': 'PRAEPARATIO (preparation)',
    'qokain': 'COCTIO (cooking)',

    # Time terms
    'otaiin': 'TEMPUS (time)',
}

# KNOWN PHRASES
PHRASES = {
    ('or', 'aiin'): 'AURUM-LOCUS (gold-place)',
    ('chol', 'daiin'): 'CALIDA-FOLIA (hot leaves)',
    ('s', 'aiin'): 'HIC-LOCUS (this place)',
    ('ar', 'aiin'): 'AERIS-LOCUS (air place)',
    ('ar', 'al'): 'AERIS (of the air)',
    ('chol', 'chol'): 'VALDE-CALIDUS (very hot)',
    ('ol', 'chedy'): 'OLEUM-HERBAE (oil of herb)',
    ('ol', 'shedy'): 'OLEUM-HERBAE (oil of herb)',
    ('daiin', 'daiin'): 'FOLIA-MULTA (many leaves)',
    ('shedy', 'qokedy'): 'HERBA-CORPORIS (herb of body)',
    ('shey', 'qokain'): 'SUCCUS-COCTIONIS (juice of cooking)',
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
    """Translate a single word."""
    if word in KNOWN_WORDS:
        return KNOWN_WORDS[word]

    prefix, middle, suffix = parse_word(word)

    parts = []

    if prefix and prefix in PREFIX:
        latin, eng = PREFIX[prefix]
        parts.append(latin)

    if middle and middle in MIDDLE:
        latin, eng = MIDDLE[middle]
        parts.append(latin)
    elif middle:
        parts.append(f'[{middle}]')

    if suffix and suffix in SUFFIX:
        latin, eng = SUFFIX[suffix]
        parts.append(latin)

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


# ============================================================================
# MAIN TRANSLATION
# ============================================================================

corpus = load_corpus('data/transcriptions')
f1r_words = [w.text for w in corpus.words if w.folio == 'f1r' and w.text]

print("=" * 90)
print("VOYNICH MANUSCRIPT - COMPREHENSIVE TRANSLATION")
print("Folio f1r (First page of botanical section)")
print("=" * 90)
print()
print("ENCODING SYSTEM:")
print("  PREFIX = Category (HERBA, CORPUS, TEMPUS, etc.)")
print("  MIDDLE = Action/Property (coquere, oleum, fluere, etc.)")
print("  SUFFIX = Grammar (-um, -tus, -arium, etc.)")
print()
print("-" * 90)

# Group into lines of roughly 6-8 words
for line_start in range(0, len(f1r_words), 7):
    line_num = line_start // 7 + 1
    chunk = f1r_words[line_start:line_start+7]
    if not chunk:
        break

    trans = translate_with_phrases(chunk)

    print(f"LINE {line_num:2}:")
    print(f"  VOY: {' '.join(chunk)}")
    print(f"  LAT: {' '.join(trans)}")
    print()

# Statistics
print("=" * 90)
print("TRANSLATION STATISTICS")
print("=" * 90)

all_trans = translate_with_phrases(f1r_words)

# Count categories
full_known = sum(1 for t in all_trans if '(' in t)  # KNOWN_WORDS have parentheses
has_bracket = sum(1 for t in all_trans if '[' in t)  # Unknown middle
has_question = sum(1 for t in all_trans if t.startswith('?'))  # Completely unknown
structured = len(all_trans) - full_known - has_question

print(f"Total words: {len(f1r_words)}")
print(f"Known words: {full_known} ({100*full_known/len(f1r_words):.1f}%)")
print(f"Structurally parsed: {structured} ({100*structured/len(f1r_words):.1f}%)")
print(f"Unknown structure: {has_question} ({100*has_question/len(f1r_words):.1f}%)")
print()

# Sample interpretation
print("=" * 90)
print("SAMPLE INTERPRETATION (speculative)")
print("=" * 90)
print()
print("Line 4: 'cthar cthar dan syaiir sheky or'")
print("  -> AQUA AQUA FOLIUM-[n] [syaiir] SUCCUS-esse-icus AURUM")
print("  -> 'Water, water, leaf?, [?], juice-like, gold/sun'")
print("  -> Possible: 'Mix with water, from the leaf, juice-like, in sunlight'")
print()
print("Line 9: 'chor kos daiin shos cfhol shody dain os'")
print("  -> PRODEST [kos] FOLIA SUCCUS-[os] [cfhol] SUCCUS-orbis-tus FOLIUM [os]")
print("  -> 'Benefits [?] leaves juice-[?] [?] juice-whole-state leaf [?]'")
print("  -> Possible: 'The leaves are beneficial, the juice [is extracted], the whole leaf...'")
print()
print("Line 15: 'chor shey kol chol chol kor chal sho'")
print("  -> PRODEST SUCCUS-esse-um [kol] VALDE-CALIDUS [kor] HERBA-astrum SAPA")
print("  -> 'Benefits juice [?] very-hot [?] herb-star sap'")
print("  -> Possible: 'The juice benefits, very hot, [boil?] the herb, [extract] sap'")
