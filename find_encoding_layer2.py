"""Search for additional encoding layers in the Voynich text."""
import json
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# Get all words as strings
all_words = [w.text for w in corpus.words if w.text]

# Get words grouped by folio
folio_words = defaultdict(list)
for w in corpus.words:
    if w.text:
        folio_words[w.folio].append(w.text)

print("=" * 70)
print("SEARCHING FOR ENCODING LAYERS")
print("=" * 70)

# TEST 1: Word length distribution
print("\n### TEST 1: Word length distribution")
print("-" * 50)

lengths = Counter(len(w) for w in all_words)
total = sum(lengths.values())
print("Length distribution:")
for length in sorted(lengths.keys())[:15]:
    count = lengths[length]
    pct = 100 * count / total
    bar = "#" * int(pct/2)
    print(f"  {length:2d} chars: {count:5d} ({pct:5.1f}%) {bar}")

# TEST 2: Character position analysis - KEY TEST
print("\n\n### TEST 2: Character position constraints")
print("-" * 50)
print("Characters restricted to certain positions = STRUCTURAL MARKERS")

char_positions = {'first': Counter(), 'middle': Counter(), 'last': Counter()}
for word in all_words:
    if len(word) >= 2:
        char_positions['first'][word[0]] += 1
        char_positions['last'][word[-1]] += 1
        for c in word[1:-1]:
            char_positions['middle'][c] += 1

print("\nPosition-restricted characters:")
all_chars = set()
for pos in char_positions:
    all_chars.update(char_positions[pos].keys())

restricted = []
for char in sorted(all_chars):
    counts = {pos: char_positions[pos][char] for pos in char_positions}
    total_char = sum(counts.values())
    if total_char > 200:
        max_pos = max(counts, key=counts.get)
        max_pct = 100 * counts[max_pos] / total_char
        if max_pct > 60:
            restricted.append((char, max_pos, max_pct, total_char))

for char, pos, pct, total in sorted(restricted, key=lambda x: -x[2]):
    print(f"  '{char}' -> {pct:.0f}% in {pos:6} position ({total:5d} occurrences)")

# TEST 3: The 'y' ending phenomenon
print("\n\n### TEST 3: The 'y' ending phenomenon")
print("-" * 50)

y_endings = sum(1 for w in all_words if w.endswith('y'))
print(f"Words ending in 'y': {y_endings}/{len(all_words)} ({100*y_endings/len(all_words):.1f}%)")
print("\nThis is ABNORMALLY HIGH for any natural language!")
print("'y' might be:")
print("  - A word-boundary marker (like a space)")
print("  - A grammatical suffix added systematically")
print("  - Part of the encoding, not the content")

# What comes before 'y'?
before_y = Counter()
for word in all_words:
    if word.endswith('y') and len(word) >= 2:
        before_y[word[-2]] += 1

print("\nCharacters before final 'y':")
for char, count in before_y.most_common(10):
    print(f"  -{char}y: {count}x")

# TEST 4: Bigram/sequence patterns
print("\n\n### TEST 4: Character sequences (bigrams)")
print("-" * 50)

bigrams = Counter()
for word in all_words:
    for i in range(len(word) - 1):
        bigrams[word[i:i+2]] += 1

print("Most common character pairs:")
for bg, count in bigrams.most_common(20):
    print(f"  '{bg}': {count}x")

# TEST 5: Word patterns - same structure, different content
print("\n\n### TEST 5: Word families (same pattern, different chars)")
print("-" * 50)

def get_pattern(word):
    """Convert word to pattern: vowels=V, consonants=C"""
    vowels = 'aeiou'
    return ''.join('V' if c in vowels else 'C' for c in word)

patterns = defaultdict(list)
for word in set(all_words):
    p = get_pattern(word)
    patterns[p].append(word)

print("Most common word patterns:")
pattern_counts = [(p, len(words)) for p, words in patterns.items()]
for pattern, count in sorted(pattern_counts, key=lambda x: -x[1])[:10]:
    examples = patterns[pattern][:5]
    print(f"  {pattern}: {count} words (e.g., {', '.join(examples)})")

# TEST 6: Repeated words analysis
print("\n\n### TEST 6: Word repetition patterns")
print("-" * 50)

# Find words that repeat immediately
immediate_repeats = Counter()
for words in folio_words.values():
    for i in range(len(words) - 1):
        if words[i] == words[i+1]:
            immediate_repeats[words[i]] += 1

print(f"Immediate word repetitions (word word): {sum(immediate_repeats.values())} total")
print("Most repeated:")
for word, count in immediate_repeats.most_common(10):
    print(f"  '{word} {word}': {count}x")

# TEST 7: Prefix analysis
print("\n\n### TEST 7: Prefix patterns")
print("-" * 50)

prefixes = Counter()
for word in all_words:
    if len(word) >= 3:
        prefixes[word[:2]] += 1

print("Most common 2-char prefixes:")
for prefix, count in prefixes.most_common(15):
    pct = 100 * count / len(all_words)
    print(f"  {prefix}-: {count}x ({pct:.1f}%)")

# TEST 8: Suffix analysis
print("\n\n### TEST 8: Suffix patterns")
print("-" * 50)

suffixes = Counter()
for word in all_words:
    if len(word) >= 3:
        suffixes[word[-2:]] += 1

print("Most common 2-char suffixes:")
for suffix, count in suffixes.most_common(15):
    pct = 100 * count / len(all_words)
    print(f"  -{suffix}: {count}x ({pct:.1f}%)")
