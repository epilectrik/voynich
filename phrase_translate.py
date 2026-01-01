"""Phrase-based translation using discovered patterns."""
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# PHRASE dictionary - multi-word units
PHRASES = {
    # Common confirmed pairs
    ('or', 'aiin'): 'precious-essence',
    ('chol', 'daiin'): 'cooked-leaves',
    ('s', 'aiin'): 'this-essence',
    ('ar', 'aiin'): 'air-essence',
    ('ar', 'al'): 'of-the-air',
    ('ol', 'shedy'): 'oil-of-herb',
    ('ol', 'chedy'): 'oil-of-herb',
    ('ol', 'daiin'): 'oil-leaves',
    ('shey', 'qokain'): 'juice-preparation',
    ('chedy', 'qokain'): 'herb-preparation',
    ('shedy', 'qokedy'): 'herb-body-medicine',
    ('chol', 'chol'): 'very-hot',
    ('daiin', 'daiin'): 'many-leaves',
}

# Single word translations - refined based on context
WORDS = {
    # HERBAL-SPECIFIC (high confidence)
    'cthy': 'water',
    'chor': 'remedy',
    'sho': 'sap',
    'chy': 'plant',
    'shy': 'juice',
    'shor': 'extract',
    'shol': 'liquid',
    'chol': 'heat/cook',
    'daiin': 'leaves',
    'dain': 'leaf',

    # Common words
    'ol': 'oil',
    'or': 'gold/precious',
    'ar': 'air',
    'aiin': 'essence/thing',
    's': 'this/thus',
    'y': 'and',
    'dar': 'give/put',
    'dal': 'from-leaf',
    'al': 'of-the',
    'dy': '[state]',

    # BODY/PREPARATION
    'qokeedy': 'prepare-body',
    'qokedy': 'body-medicine',
    'qokain': 'preparation',
    'qokaiin': 'preparation-place',
    'qol': 'body-oil',
    'qokal': 'body-heat',

    # PLANT terms
    'chedy': 'herb',
    'shedy': 'herb',
    'cheol': 'hot-oil',
    'sheol': 'juice-oil',

    # WATER terms
    'cthar': 'water',
    'cthol': 'watery',

    # Zodiac/time
    'otaiin': 'of-time',
    'otedy': 'time-state',
    'otar': 'of-star',
}

def translate_text(words):
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
        word = words[i]
        if word in WORDS:
            result.append(WORDS[word])
        else:
            result.append(f'[{word}]')
        i += 1

    return result

# Load and translate f1r
corpus = load_corpus('data/transcriptions')
f1r_words = [w.text for w in corpus.words if w.folio == 'f1r' and w.text]

print("=" * 80)
print("PHRASE-BASED TRANSLATION - Folio f1r")
print("=" * 80)
print()

# Group into lines
for line_num in range(1, 13):
    start = (line_num - 1) * 6
    end = start + 6
    if start >= len(f1r_words):
        break

    chunk = f1r_words[start:end]
    trans = translate_text(chunk)

    print(f"Line {line_num}:")
    print(f"  VOY: {' '.join(chunk)}")
    print(f"  ENG: {' '.join(trans)}")
    print()

# Show translation statistics
print("=" * 80)
print("TRANSLATION COVERAGE")
print("=" * 80)

total = len(f1r_words)
trans = translate_text(f1r_words)
known = sum(1 for t in trans if not t.startswith('['))
print(f"Words translated: {known}/{len(trans)} ({100*known/len(trans):.1f}%)")

# Show unknown words
unknown = [t[1:-1] for t in trans if t.startswith('[')]
from collections import Counter
unk_freq = Counter(unknown)
print(f"\nMost common UNKNOWN words:")
for word, count in unk_freq.most_common(15):
    print(f"  {word}: {count}x")
