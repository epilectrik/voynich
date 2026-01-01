"""Analyze if Voynich uses syllabic encoding."""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')
all_words = [w.text for w in corpus.words if w.text]

print("=" * 70)
print("SYLLABIC ANALYSIS")
print("=" * 70)

# The EVA transcription uses digraphs like 'ch', 'sh', 'cth'
# These might represent SINGLE GLYPHS in the original

# Common "gallows" characters in EVA: k, t, p, f (tall letters)
# Common "bench" characters: ch, sh, cth (combinations)
# Common vowel-like: a, o, e, i, y

# Define potential syllable units
GALLOWS = ['k', 't', 'p', 'f']
BENCH = ['ch', 'sh', 'cth', 'ckh', 'cph', 'cfh']
LOOPS = ['d', 's', 'r', 'l', 'n', 'm']
MIDDLE = ['a', 'o', 'e', 'i', 'y', 'ai', 'ee', 'ii', 'eo', 'oe']

print("\n### Analyzing 'ch' as a single unit")
print("-" * 50)

# If 'ch' is a single glyph, we can tokenize differently
def tokenize(word):
    """Convert EVA word to glyph tokens."""
    tokens = []
    i = 0
    while i < len(word):
        # Try 3-char combos first
        if i + 2 < len(word) and word[i:i+3] in ['cth', 'ckh', 'cph', 'cfh', 'sch', 'pch', 'tch', 'fch', 'kch']:
            tokens.append(word[i:i+3])
            i += 3
        # Try 2-char combos
        elif i + 1 < len(word) and word[i:i+2] in ['ch', 'sh', 'ai', 'ee', 'ii', 'eo', 'oe', 'or', 'ar', 'ol', 'ok', 'ot', 'qo', 'dy', 'ey', 'in', 'an']:
            tokens.append(word[i:i+2])
            i += 2
        else:
            tokens.append(word[i])
            i += 1
    return tokens

# Tokenize all words
token_counts = Counter()
token_positions = defaultdict(Counter)  # Where does each token appear?

for word in all_words:
    tokens = tokenize(word)
    for i, token in enumerate(tokens):
        token_counts[token] += 1
        pos = 'start' if i == 0 else ('end' if i == len(tokens)-1 else 'mid')
        token_positions[token][pos] += 1

print("\nMost common GLYPH tokens:")
for token, count in token_counts.most_common(30):
    # Show position distribution
    total = sum(token_positions[token].values())
    start_pct = 100 * token_positions[token]['start'] / total
    mid_pct = 100 * token_positions[token]['mid'] / total
    end_pct = 100 * token_positions[token]['end'] / total

    dominant = ''
    if start_pct > 60:
        dominant = '<- START'
    elif end_pct > 60:
        dominant = '<- END'
    elif mid_pct > 60:
        dominant = '<- MIDDLE'

    print(f"  {token:4}: {count:5}x  (S:{start_pct:4.0f}% M:{mid_pct:4.0f}% E:{end_pct:4.0f}%) {dominant}")

# Analyze word structure in terms of tokens
print("\n\n### Word structure patterns (in glyph tokens)")
print("-" * 50)

structure_counts = Counter()
for word in set(all_words):
    tokens = tokenize(word)
    if len(tokens) <= 6:
        structure = '-'.join(['G' if t in ['k','t','p','f'] else
                             'B' if t in ['ch','sh','cth','ckh','cph','cfh'] else
                             'L' if t in ['d','s','r','l','n','m'] else
                             'V' if t in ['a','o','e','i','y','ai','ee','ii','eo','oe'] else
                             'Q' if t in ['qo'] else
                             'X' for t in tokens])
        structure_counts[structure] += 1

print("Most common structures (G=gallows, B=bench, L=loop, V=vowel, Q=qo):")
for struct, count in structure_counts.most_common(20):
    print(f"  {struct:20}: {count}x")

# Look for "word" = "syllable + syllable" pattern
print("\n\n### Can words be split into repeated syllables?")
print("-" * 50)

# Check if words are made of repeated units
repeated = []
for word in set(all_words):
    if len(word) >= 4 and len(word) % 2 == 0:
        half = len(word) // 2
        if word[:half] == word[half:]:
            repeated.append(word)

print(f"Words that are X+X (doubled syllable): {len(repeated)}")
for w in sorted(repeated, key=lambda x: -all_words.count(x))[:15]:
    count = all_words.count(w)
    print(f"  {w} ({w[:len(w)//2]}+{w[len(w)//2:]}): {count}x")
