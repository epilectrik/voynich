"""Render Voynich translation into readable English."""
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# ============================================================================
# TRANSLATION TABLE (Latin -> English)
# ============================================================================

LATIN_TO_ENGLISH = {
    # CATEGORY prefixes
    'TEMPUS': 'time',
    'CAELUM': 'sky',
    'AER': 'air',
    'STELLA': 'star',
    'CYCLUS': 'cycle',
    'MUNDUS': 'world',
    'AURUM': 'gold/sun',
    'CORPUS': 'body',
    'HUMOR': 'fluid',
    'SALUS': 'health',
    'AQUA': 'water',
    'FOLIUM': 'leaf',
    'FOLIA': 'leaves',
    'HERBA': 'herb/plant',
    'SUCCUS': 'juice',
    'LIQUOR': 'liquid',
    'OPUS': 'work',
    'MIXTURA': 'mixture',
    'SEMEN': 'seed',

    # ACTION/PROPERTY middles
    'coquere': 'cook',
    'bullire': 'boil',
    'calere': 'heat',
    'urere': 'burn',
    'miscere': 'mix',
    'oleum': 'oil',
    'prodesse': 'benefit',
    'viridis': 'green',
    'intus': 'inside',
    'fluere': 'flow',
    'aer': 'air',
    'astrum': 'star',
    'orbis': 'whole/round',
    'lavare': 'wash',
    'corporis': 'of-body',
    'tangere': 'touch',
    'tenere': 'hold',
    'esse': '',  # being/essence - often silent
    'madidus': 'wet',
    'siccus': 'dry',
    'unus': 'one',
    'multi': 'many',
    'vas': 'vessel',
    'continere': 'contain',
    'dare': 'give',
    'de': 'from',
    're': 'back',

    # KNOWN WORDS
    'PRODEST': 'benefits',
    'CALIDUS': 'hot',
    'VALDE-CALIDUS': 'very-hot',
    'PLANTA': 'plant',
    'SAPA': 'sap',
    'ET': 'and',
    'HIC': 'this',
    'IN': 'in',
    'EX': 'from',
    'OLEUM': 'oil',

    # SUFFIXES (grammatical - rendered as context)
    '-um': '',
    '-arium': '-place',
    '-atio': '-action',
    '-ium': '',
    '-im': '',
    '-tus': '[done]',
    '-ens': '[doing]',
    '-osus': '-full',
    '-icus': '-like',
    '-alis': '-type',
    '-itas': '-ness',
    '-arius': '-maker',
    '-aris': '-of',
    '-or': '-er',
    '-olum': '-small',
}

def render_latin_to_english(latin_str):
    """Convert Latin translation to readable English."""
    # Handle known words in parentheses
    if '(' in latin_str:
        # Extract English from parentheses
        import re
        match = re.search(r'\(([^)]+)\)', latin_str)
        if match:
            return match.group(1)

    # Handle unknown elements in brackets
    if '[' in latin_str:
        latin_str = latin_str.replace('[', '?').replace(']', '?')

    # Split on hyphens and translate each part
    parts = latin_str.split('-')
    english_parts = []

    for part in parts:
        if part in LATIN_TO_ENGLISH:
            eng = LATIN_TO_ENGLISH[part]
            if eng:  # Skip empty translations
                english_parts.append(eng)
        else:
            # Keep unknown parts
            english_parts.append(part.lower())

    return '-'.join(english_parts) if english_parts else latin_str


# ============================================================================
# FULL TRANSLATION SYSTEM (copied from comprehensive_decoder.py)
# ============================================================================

PREFIX = {
    'ot': ('TEMPUS', 'time'), 'ok': ('CAELUM', 'sky'), 'ar': ('AER', 'air'),
    'al': ('STELLA', 'star'), 'yk': ('CYCLUS', 'cycle'), 'yt': ('MUNDUS', 'world'),
    'or': ('AURUM', 'gold/sun'), 'qo': ('CORPUS', 'body'), 'ol': ('HUMOR', 'fluid'),
    'so': ('SALUS', 'health'), 'ct': ('AQUA', 'water'), 'cth': ('AQUA', 'water'),
    'da': ('FOLIUM', 'leaf'), 'ch': ('HERBA', 'plant'), 'sh': ('SUCCUS', 'juice'),
    'lk': ('LIQUOR', 'liquid'), 'op': ('OPUS', 'work'), 'pc': ('MIXTURA', 'mixture'),
    'sa': ('SEMEN', 'seed'),
}

MIDDLE = {
    'ke': ('coquere', 'cook'), 'kee': ('bullire', 'boil'), 'ka': ('calere', 'heat'),
    'kai': ('urere', 'burn'), 'ko': ('miscere', 'mix'), 'ol': ('oleum', 'oil'),
    'or': ('prodesse', 'benefit'), 'i': ('viridis', 'green'), 'in': ('intus', 'inside'),
    'eo': ('fluere', 'flow'), 'ar': ('aer', 'air'), 'al': ('astrum', 'star'),
    'o': ('orbis', 'whole'), 'l': ('lavare', 'wash'), 'k': ('corporis', 'body'),
    't': ('tangere', 'touch'), 'te': ('tenere', 'hold'), 'e': ('esse', 'being'),
    'ee': ('madidus', 'wet'), 'ed': ('siccus', 'dry'), 'a': ('unus', 'one'),
    'ii': ('multi', 'many'), 'y': ('esse', 'being'), 'ch': ('vas', 'vessel'),
    'ck': ('continere', 'contain'), 'od': ('dare', 'give'), 'd': ('de', 'from'),
    'r': ('re', 'back'),
}

SUFFIX = {
    'y': ('-um', 'noun'), 'aiin': ('-arium', 'place'), 'ain': ('-atio', 'action'),
    'iin': ('-ium', 'thing'), 'in': ('-im', 'acc'), 'dy': ('-tus', 'done'),
    'ey': ('-ens', 'doing'), 'hy': ('-osus', 'full'), 'ky': ('-icus', 'like'),
    'ly': ('-alis', 'type'), 'ty': ('-itas', 'quality'), 'ry': ('-arius', 'maker'),
    'ar': ('-aris', 'of'), 'or': ('-or', 'doer'), 'al': ('-alis', 'adj'),
    'ol': ('-olum', 'small'),
}

KNOWN_WORDS = {
    'daiin': ('FOLIA', 'leaves'), 'dain': ('FOLIUM', 'leaf'),
    'chedy': ('HERBA', 'herb'), 'shedy': ('HERBA', 'herb'),
    'ol': ('OLEUM', 'oil'), 'chol': ('CALIDUS', 'hot'),
    'chor': ('PRODEST', 'benefits'), 'cthy': ('AQUA', 'water'),
    'sho': ('SAPA', 'sap'), 'shy': ('SUCCUS', 'juice'),
    'chy': ('PLANTA', 'plant'), 'shol': ('LIQUOR', 'liquid'),
    'shor': ('EXTRACTUM', 'extract'),
    'y': ('ET', 'and'), 's': ('HIC', 'this'),
    'or': ('AURUM', 'gold'), 'ar': ('AER', 'air'),
    'al': ('DE', 'of'), 'dar': ('IN', 'in'), 'dal': ('EX', 'from'),
    'qol': ('HUMOR', 'fluid'), 'qokal': ('CALOR', 'heat'),
    'qokedy': ('CORPORIS', 'body-state'), 'qokeedy': ('PRAEPARATIO', 'preparation'),
    'qokain': ('COCTIO', 'cooking'),
    'otaiin': ('TEMPUS', 'time'),
}

PHRASES = {
    ('or', 'aiin'): ('AURUM-LOCUS', 'gold-place'),
    ('chol', 'daiin'): ('CALIDA-FOLIA', 'hot-leaves'),
    ('s', 'aiin'): ('HIC-LOCUS', 'this-place'),
    ('ar', 'aiin'): ('AERIS-LOCUS', 'air-place'),
    ('ar', 'al'): ('AERIS', 'of-air'),
    ('chol', 'chol'): ('VALDE-CALIDUS', 'very-hot'),
    ('ol', 'chedy'): ('OLEUM-HERBAE', 'herb-oil'),
    ('ol', 'shedy'): ('OLEUM-HERBAE', 'herb-oil'),
    ('daiin', 'daiin'): ('FOLIA-MULTA', 'many-leaves'),
}


def parse_word(word):
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


def translate_to_english(word):
    """Translate Voynich word directly to English."""
    if word in KNOWN_WORDS:
        return KNOWN_WORDS[word][1]  # Return English

    prefix, middle, suffix = parse_word(word)
    parts = []

    if prefix and prefix in PREFIX:
        parts.append(PREFIX[prefix][1])  # English meaning

    if middle and middle in MIDDLE:
        parts.append(MIDDLE[middle][1])
    elif middle:
        parts.append(f'?{middle}?')

    if suffix and suffix in SUFFIX:
        eng = SUFFIX[suffix][1]
        if eng and eng not in ['noun', 'thing', 'acc']:
            parts.append(f'[{eng}]')

    return '-'.join(parts) if parts else f'?{word}?'


def translate_with_phrases_english(words):
    result = []
    i = 0
    while i < len(words):
        if i + 1 < len(words):
            pair = (words[i], words[i+1])
            if pair in PHRASES:
                result.append(PHRASES[pair][1])  # English
                i += 2
                continue
        result.append(translate_to_english(words[i]))
        i += 1
    return result


# ============================================================================
# MAIN
# ============================================================================

corpus = load_corpus('data/transcriptions')
f1r_words = [w.text for w in corpus.words if w.folio == 'f1r' and w.text]

print("=" * 90)
print("VOYNICH MANUSCRIPT - ENGLISH TRANSLATION ATTEMPT")
print("Folio f1r (First page - Botanical/Herbal section)")
print("=" * 90)
print()
print("LEGEND:")
print("  ?xxx? = Unknown element")
print("  [done] = Past action (e.g., 'cooked', 'heated')")
print("  [doing] = Present action (e.g., 'cooking', 'heating')")
print("  -place = Location/container")
print()
print("-" * 90)

for line_start in range(0, len(f1r_words), 7):
    line_num = line_start // 7 + 1
    chunk = f1r_words[line_start:line_start+7]
    if not chunk:
        break

    eng = translate_with_phrases_english(chunk)

    print(f"LINE {line_num:2}: {' '.join(chunk)}")
    print(f"         {' '.join(eng)}")
    print()

print("=" * 90)
print("COHERENT FRAGMENTS (where we have high confidence)")
print("=" * 90)
print()

# Find lines with mostly known words
for line_start in range(0, len(f1r_words), 7):
    chunk = f1r_words[line_start:line_start+7]
    eng = translate_with_phrases_english(chunk)

    unknown_count = sum(1 for e in eng if '?' in e)
    if unknown_count <= 2:  # Mostly known
        line_num = line_start // 7 + 1
        print(f"Line {line_num}: {' '.join(eng)}")
        print(f"         (Voynich: {' '.join(chunk)})")
        print()

print("=" * 90)
print("INTERPRETATION OF BEST LINES")
print("=" * 90)
print()

# Line 17 example
print("LINE 17: 'chor shey kol chol chol kor chal'")
print("  -> 'benefits juice ?kol? very-hot body-[doer] plant-star'")
print("  INTERPRETATION: 'The juice benefits [when] very hot, [by] body [action], star-plant'")
print("  POSSIBLE: Instructions about heating the juice of a star-shaped plant")
print()

# Line 10 example
print("LINE 10: 'dain chor kos daiin shos cfhol shody'")
print("  -> 'leaf benefits ?kos? leaves juice-?os? ?cfh?-small juice-whole-[done]'")
print("  INTERPRETATION: 'The leaf benefits... leaves... juice... whole juice [prepared]'")
print("  POSSIBLE: Description of extracting and preparing juice from leaves")
print()

# Line 6 example
print("LINE 6: 'daiin otaiin or okan dair y chear'")
print("  -> 'leaves time gold sky-?an? leaf-?ir? and plant-being-[of]'")
print("  INTERPRETATION: 'Leaves [at] time [of] gold/sun, sky... and plant...'")
print("  POSSIBLE: Timing instructions - harvest leaves when sun is in a certain position")
