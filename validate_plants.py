"""Validate our decoder against known plant identifications."""
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# Known plant identifications (from Edith Sherwood)
PLANT_IDS = {
    'f1v': {
        'name': 'Deadly Nightshade / Belladonna',
        'scientific': 'Atropa belladonna',
        'properties': 'Extremely toxic, hallucinogenic, contains atropine. Used to dilate eyes, as sedative.',
        'expected_terms': ['poison', 'danger', 'eye', 'sleep', 'death', 'medicine', 'careful']
    },
    'f2r': {
        'name': 'Diffuse Knapweed',
        'scientific': 'Centaurea diffusa',
        'properties': 'Used for healing wounds in Middle Ages.',
        'expected_terms': ['wound', 'heal', 'blood', 'cut', 'medicine']
    },
    'f3v': {
        'name': 'Dungwort / Bears Foot / Hellebore',
        'scientific': 'Helleborus foetidus',
        'properties': 'Poisonous Western European shrub.',
        'expected_terms': ['poison', 'danger', 'root', 'careful']
    },
    'f5r': {
        'name': 'Wolfs Bane / Arnica',
        'scientific': 'Arnica montana',
        'properties': 'Used externally for sprains and bruises.',
        'expected_terms': ['external', 'bruise', 'pain', 'rub', 'apply', 'skin']
    },
    'f5v': {
        'name': 'Mallow',
        'scientific': 'Malva sylvestris',
        'properties': 'Used as sweetener, pink-red dye.',
        'expected_terms': ['sweet', 'flower', 'color', 'dye']
    }
}

# Our decoded PREFIX meanings
PREFIX = {
    'ot': 'time', 'ok': 'sky', 'ar': 'air', 'al': 'star', 'yk': 'cycle',
    'yt': 'world', 'or': 'gold/sun', 'qo': 'body', 'ol': 'fluid', 'so': 'health',
    'ct': 'water', 'cth': 'water', 'da': 'leaf', 'ch': 'plant', 'sh': 'juice',
    'lk': 'liquid', 'op': 'work', 'pc': 'mix', 'sa': 'seed',
}

MIDDLE = {
    'ke': 'cook', 'kee': 'boil', 'ka': 'heat', 'kai': 'burn', 'ko': 'mix',
    'ol': 'oil', 'or': 'benefit', 'i': 'green', 'in': 'inside',
    'eo': 'flow', 'ar': 'air', 'al': 'star', 'o': 'whole',
    'l': 'wash', 'k': 'body', 't': 'touch', 'te': 'hold',
    'e': 'being', 'ee': 'wet', 'ed': 'dry', 'a': 'one',
    'ii': 'many', 'y': 'being', 'ch': 'vessel', 'ck': 'contain',
    'od': 'give', 'd': 'from', 'r': 'back',
}

SUFFIX = {
    'y': 'noun', 'aiin': 'place', 'ain': 'action', 'iin': 'thing', 'in': 'acc',
    'dy': 'done', 'ey': 'doing', 'hy': 'full', 'ky': 'like',
    'ly': 'type', 'ty': 'quality', 'ry': 'maker',
    'ar': 'of', 'or': 'doer', 'al': 'adj', 'ol': 'small',
}

KNOWN_WORDS = {
    'daiin': 'leaves', 'dain': 'leaf', 'chedy': 'herb', 'shedy': 'herb',
    'ol': 'oil', 'chol': 'hot', 'chor': 'benefits', 'cthy': 'water',
    'sho': 'sap', 'shy': 'juice', 'chy': 'plant', 'shol': 'liquid',
    'y': 'and', 's': 'this', 'or': 'gold', 'ar': 'air',
    'dar': 'in', 'dal': 'from', 'qokedy': 'body-state',
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

def decode_word(word):
    if word in KNOWN_WORDS:
        return KNOWN_WORDS[word]
    prefix, middle, suffix = parse_word(word)
    parts = []
    if prefix and prefix in PREFIX:
        parts.append(PREFIX[prefix])
    if middle and middle in MIDDLE:
        parts.append(MIDDLE[middle])
    elif middle:
        parts.append(f'?{middle}?')
    if suffix and suffix in SUFFIX:
        parts.append(f'[{SUFFIX[suffix]}]')
    return '-'.join(parts) if parts else f'?{word}?'


corpus = load_corpus('data/transcriptions')

print("=" * 90)
print("VALIDATION: Testing Decoder Against Known Plant Identifications")
print("=" * 90)
print()
print("If our decoder is correct, the decoded text should relate to the plant's properties.")
print()

for folio, info in PLANT_IDS.items():
    words = [w.text for w in corpus.words if w.folio == folio and w.text]

    print("-" * 90)
    print(f"FOLIO {folio}: {info['name']} ({info['scientific']})")
    print(f"Known properties: {info['properties']}")
    print(f"Expected terms: {', '.join(info['expected_terms'])}")
    print()
    print(f"Voynich text ({len(words)} words):")
    print(f"  {' '.join(words[:20])}{'...' if len(words) > 20 else ''}")
    print()
    print("Decoded:")
    decoded = [decode_word(w) for w in words[:20]]
    print(f"  {' '.join(decoded)}")
    print()

    # Check for any matches with expected terms
    decoded_text = ' '.join(decoded).lower()
    matches = [term for term in info['expected_terms'] if term in decoded_text]
    if matches:
        print(f"  MATCHES FOUND: {matches}")
    else:
        print(f"  NO MATCHES with expected terms")
    print()

print("=" * 90)
print("ANALYSIS")
print("=" * 90)
print()
print("If we see matches between decoded terms and expected plant properties,")
print("that would be EXTERNAL VALIDATION of our decoding system.")
print()
print("If we see NO matches, our semantic assignments may be wrong,")
print("even if the structural analysis (PREFIX-MIDDLE-SUFFIX) is correct.")
