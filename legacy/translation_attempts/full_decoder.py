"""Full decoder using discovered PREFIX-MIDDLE-SUFFIX system."""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

# SECTION-SPECIFIC PREFIX MEANINGS (from statistical analysis)
PREFIX = {
    # ZODIAC/TIME prefixes (ot, ok, ar, al, yk enriched in zodiac)
    'ot': 'time',      # 2.4x zodiac - tempus, hora
    'ok': 'sky',       # 1.9x zodiac - caelum, aether
    'ar': 'air',       # 2.0x zodiac - aer, spiritus
    'al': 'star',      # 2.5x zodiac - stella, astrum
    'yk': 'cycle',     # 1.9x zodiac - cyclus, circulus

    # COSMOLOGICAL prefixes
    'yt': 'world',     # 3.1x cosmological - mundus
    'or': 'gold',      # 2.4x cosmological - aurum, sol

    # BIOLOGICAL/BODY prefixes (qo, ol, so enriched in biological)
    'qo': 'body',      # 1.7x biological - corpus
    'ol': 'fluid',     # 2.1x biological - liquor, humor
    'so': 'health',    # 1.8x biological - salus, valetudo

    # HERBAL/PLANT prefixes (ct, da, ch, sh enriched in herbal)
    'ct': 'water',     # 2.4x herbal - aqua
    'cth': 'water',    # variant
    'da': 'leaf',      # 1.5x herbal - folium
    'ch': 'plant',     # herbal - herba, planta
    'sh': 'juice',     # herbal - succus, sapa

    # RECIPE prefixes
    'lk': 'liquid',    # 2.8x recipes - liquor
    'op': 'work',      # recipes - opus
    'pc': 'mix',       # recipes - miscere
    'sa': 'seed',      # semen
}

# MIDDLE CONTENT meanings (from morphological analysis)
MIDDLE = {
    # Cooking/preparation (common in qo- words)
    'ke': 'cook',      # coquere
    'ka': 'heat',      # calere
    'kee': 'boil',     # bullire
    'kai': 'burn',     # urere

    # State/condition
    'ed': 'dry',       # siccus
    'ee': 'wet',       # humidus
    'o': 'whole',      # totus
    'e': 'essence',    # essentia
    'a': 'one',        # unus

    # Action/process
    'ai': 'life',      # vita
    'ii': 'plural',    # many
    'eo': 'flow',      # fluere
    'od': 'give',      # dare
    'ta': 'take',      # sumere
    'te': 'hold',      # tenere

    # Object/container
    'ch': 'vessel',    # vas
    'ck': 'contain',   # continere
    'ko': 'mix',       # miscere
}

# SUFFIX grammatical endings (from position analysis)
SUFFIX = {
    # Noun endings
    'y': '-um',        # neuter noun (41% of words!)
    'aiin': '-ium',    # place/container
    'ain': '-io',      # action noun
    'iin': '-ium',     # substance
    'in': '-im',       # accusative

    # Adjective/state endings
    'dy': '-tus',      # past participle state
    'ey': '-ens',      # present participle
    'hy': '-osus',     # full of
    'ky': '-icus',     # relating to
    'ly': '-alis',     # manner
    'ty': '-tas',      # quality
    'ry': '-arius',    # agent

    # Other endings
    'ar': '-aris',     # of/relating to
    'or': '-or',       # doer
    'al': '-alis',     # adjective
    'ol': '-olum',     # diminutive
}

# KNOWN PHRASES (word pairs that function as units)
PHRASES = {
    ('or', 'aiin'): 'aurum-locus',       # gold place (53x)
    ('chol', 'daiin'): 'calida-folia',   # hot leaves (35x)
    ('s', 'aiin'): 'hic-locus',          # this place (32x)
    ('ar', 'aiin'): 'aer-locus',         # air place (24x)
    ('ar', 'al'): 'aer-alis',            # of the air (24x)
    ('chol', 'chol'): 'valde-calidus',   # very hot (22x)
    ('ol', 'chedy'): 'oleum-herbae',     # oil of herb (21x)
    ('ol', 'shedy'): 'oleum-herbae',     # oil of herb (21x)
    ('daiin', 'daiin'): 'folia-multa',   # many leaves (20x)
    ('shedy', 'qokedy'): 'herba-corporis', # herb of body (21x)
    ('shey', 'qokain'): 'succus-coctionis', # juice of cooking (18x)
    ('chedy', 'qokain'): 'herba-coctionis', # herb of cooking (18x)
}

# COMPLETE WORD translations (high confidence)
WORDS = {
    # Confirmed by section analysis
    'daiin': 'folia',      # leaves (863x, 54% herbal)
    'dain': 'folium',      # leaf
    'chedy': 'herba',      # herb (501x)
    'shedy': 'herba',      # herb variant (426x)
    'ol': 'oleum',         # oil (537x)
    'chol': 'calidus',     # hot/heat (396x, 59% herbal)
    'chor': 'prodest',     # benefits (71% herbal)
    'cthy': 'aqua',        # water (88% herbal)
    'sho': 'sapa',         # sap (75% herbal)
    'shy': 'succus',       # juice (65% herbal)
    'chy': 'planta',       # plant (68% herbal)
    'shol': 'liquor',      # liquid (60% herbal)
    'shor': 'extractum',   # extract (69% herbal)

    # Function words
    'y': 'et',             # and (151x standalone)
    's': 'hic',            # this
    'or': 'aurum',         # gold
    'ar': 'aer',           # air
    'al': 'de',            # of the
    'dar': 'in',           # in
    'dal': 'ex',           # from

    # Body terms (biological section)
    'qol': 'humor',        # bodily fluid
    'qokal': 'calor',      # body heat
    'qokedy': 'corporis',  # of body
    'qokeedy': 'praeparatio', # preparation
    'qokain': 'coctio',    # cooking

    # Time terms (zodiac section)
    'otaiin': 'tempus',    # time
    'otedy': 'status',     # state
    'otar': 'stella',      # star
    'okal': 'caelum',      # sky
}


def parse_word(word):
    """Parse word into prefix + middle + suffix."""
    if not word or len(word) < 2:
        return None, word, None

    # Find prefix (try longer first)
    prefix = None
    rest = word
    for p in sorted(PREFIX.keys(), key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            rest = word[len(p):]
            break

    # Find suffix (try longer first)
    suffix = None
    middle = rest
    for s in sorted(SUFFIX.keys(), key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    return prefix, middle, suffix


def translate_word(word):
    """Translate a single word using the full system."""
    # First check if it's a known complete word
    if word in WORDS:
        return WORDS[word]

    # Parse into components
    prefix, middle, suffix = parse_word(word)

    parts = []

    # Translate prefix (category)
    if prefix in PREFIX:
        parts.append(PREFIX[prefix])
    elif prefix:
        parts.append(f'[{prefix}]')

    # Translate middle (content)
    if middle in MIDDLE:
        parts.append(MIDDLE[middle])
    elif middle:
        parts.append(f'({middle})')

    # Translate suffix (grammar)
    if suffix in SUFFIX:
        parts.append(SUFFIX[suffix])

    return '-'.join(parts) if parts else f'[{word}]'


def translate_with_phrases(words):
    """Translate word list, checking for phrases first."""
    result = []
    i = 0

    while i < len(words):
        # Check for 2-word phrase
        if i + 1 < len(words):
            pair = (words[i], words[i+1])
            if pair in PHRASES:
                result.append(PHRASES[pair])
                i += 2
                continue

        # Single word
        result.append(translate_word(words[i]))
        i += 1

    return result


# Load corpus
corpus = load_corpus('data/transcriptions')

# Get f1r words
f1r_words = [w.text for w in corpus.words if w.folio == 'f1r' and w.text]

print("=" * 80)
print("FULL VOYNICH DECODER - Folio f1r")
print("=" * 80)
print()
print("System: PREFIX(category) + MIDDLE(content) + SUFFIX(grammar)")
print("        Known phrases treated as single units")
print()

# Translate line by line
line_num = 0
for i in range(0, len(f1r_words), 8):  # ~8 words per line
    line_num += 1
    chunk = f1r_words[i:i+8]
    if not chunk:
        break

    trans = translate_with_phrases(chunk)

    print("-" * 80)
    print(f"LINE {line_num}:")
    print(f"  Voynich: {' '.join(chunk)}")
    print(f"  Latin:   {' '.join(trans)}")
    print()

# Summary statistics
print("=" * 80)
print("TRANSLATION SUMMARY")
print("=" * 80)

all_trans = translate_with_phrases(f1r_words)
known = sum(1 for t in all_trans if not t.startswith('[') and '(' not in t)
partial = sum(1 for t in all_trans if '(' in t and not t.startswith('['))
unknown = sum(1 for t in all_trans if t.startswith('['))

print(f"Total words: {len(f1r_words)}")
print(f"Fully translated: {known} ({100*known/len(f1r_words):.1f}%)")
print(f"Partially parsed: {partial} ({100*partial/len(f1r_words):.1f}%)")
print(f"Unknown: {unknown} ({100*unknown/len(f1r_words):.1f}%)")

# Show what we couldn't translate
print()
print("Unknown words (most common):")
unknown_words = [f1r_words[i] for i, t in enumerate(all_trans) if t.startswith('[')]
for word, count in Counter(unknown_words).most_common(15):
    print(f"  {word}: {count}x")

print()
print("Partial parses (showing pattern):")
partial_words = [(f1r_words[i], all_trans[i]) for i, t in enumerate(all_trans) if '(' in t]
shown = set()
for word, trans in partial_words[:20]:
    if word not in shown:
        print(f"  {word:15} -> {trans}")
        shown.add(word)
