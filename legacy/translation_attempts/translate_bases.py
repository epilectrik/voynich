"""Translate using base forms - stripping grammatical suffixes."""
import json
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# Define grammatical suffixes to strip (in order of length)
SUFFIXES = ['aiin', 'oiin', 'eiin', 'ain', 'iin', 'dy', 'ey', 'hy', 'ky', 'ly', 'ty', 'ry', 'y']

def get_base(word):
    """Strip grammatical suffix from word."""
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) > len(suffix):
            return word[:-len(suffix)], suffix
    return word, ''

# Define base translations (core vocabulary)
# These are the meaningful roots
BASE_DICT = {
    # Plants/herbs
    'ched': 'herba',      # herb
    'shed': 'herba',      # herb variant
    'dain': 'flos',       # flower
    'dal': 'folium',      # leaf

    # Liquids/preparations
    'ol': 'oleum',        # oil
    'she': 'succus',      # juice
    'sho': 'succus',      # juice variant
    'cth': 'aqua',        # water
    'shol': 'liquor',     # liquid

    # Actions - cooking/preparation
    'qoke': 'coquere',    # to cook
    'qok': 'coquere',     # to cook
    'cho': 'calor',       # heat
    'che': 'calor',       # heat variant
    'chol': 'calere',     # to be hot

    # Body/health
    'ok': 'oculus',       # eye
    'oke': 'oculus',      # eye
    'sho': 'sanare',      # to heal
    'shod': 'sanare',     # to heal
    'chor': 'curare',     # to cure

    # Elements
    'ar': 'aer',          # air
    'tar': 'terra',       # earth
    'sol': 'sol',         # sun

    # Quantities/properties
    'ot': 'totus',        # whole/all
    'ote': 'totus',       # whole variant
    'd': 'de',            # from/of
    'dar': 'dare',        # to give
    'or': 'aurum',        # gold/precious
    'al': 'alius',        # other
    's': 'sic',           # thus

    # Common elements
    'ch': 'cum',          # with
    'k': 'et',            # and
    'qo': 'quo',          # which/where
    'sh': 'sub',          # under
    'l': 'ille',          # that
}

# Suffix meanings
SUFFIX_MEANINGS = {
    'aiin': '-arium (container/place)',
    'oiin': '-orium (place of)',
    'ain': '-atio (action)',
    'iin': '-ium (thing)',
    'dy': '-tus (past part.)',
    'ey': '-ens (pres. part.)',
    'hy': '-osus (full of)',
    'ky': '-icus (adj.)',
    'ly': '-alis (adj.)',
    'ty': '-tas (quality)',
    'ry': '-arius (agent)',
    'y': '-us/-um (basic)',
}

# Load corpus and translate f1r
corpus = load_corpus('data/transcriptions')
f1r_words = [w.text for w in corpus.words if w.folio == 'f1r' and w.text]

print("=" * 70)
print("BASE-FORM TRANSLATION - Folio f1r")
print("=" * 70)
print("\nLegend: VOYNICH -> [base + suffix] -> LATIN meaning")
print("-" * 70)

translated = []
for i, word in enumerate(f1r_words):
    base, suffix = get_base(word)

    if base in BASE_DICT:
        latin = BASE_DICT[base]
        suffix_note = SUFFIX_MEANINGS.get(suffix, '')
        translated.append(f"{latin}")
        #print(f"{word:12} -> [{base:6}+{suffix:4}] -> {latin:12} {suffix_note}")
    else:
        translated.append(f"[{word}]")
        #print(f"{word:12} -> [{base:6}+{suffix:4}] -> ???")

# Group into lines of 6 words
print("\nTRANSLATED TEXT:")
print("=" * 70)
for i in range(0, len(translated), 6):
    line_num = i // 6 + 1
    chunk = translated[i:i+6]
    voy_chunk = f1r_words[i:i+6]

    print(f"\nLine {line_num}:")
    print(f"  VOY: {' '.join(voy_chunk)}")
    print(f"  LAT: {' '.join(chunk)}")

# Show coverage
known = sum(1 for t in translated if not t.startswith('['))
print(f"\n{'=' * 70}")
print(f"Coverage: {known}/{len(translated)} ({100*known/len(translated):.1f}%)")
print(f"Base dictionary: {len(BASE_DICT)} entries")
