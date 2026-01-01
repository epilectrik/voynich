"""Search for additional encoding layers in the Voynich text."""
import json
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# Get words grouped by folio
folio_words = defaultdict(list)
for w in corpus.words:
    folio_words[w.folio].append(w.text)

print("=" * 70)
print("SEARCHING FOR ENCODING LAYERS")
print("=" * 70)

# TEST 1: Check if word endings correlate with position
print("\n\n### TEST 1: Do word endings correlate with line position?")
print("-" * 50)
print("If certain endings appear at specific positions, they might be grammar markers")

# Get f1r as test case
f1r_words = folio_words.get('f1r', [])

# Analyze endings by rough position (beginning, middle, end of text blocks)
endings = defaultdict(Counter)
for i, word in enumerate(f1r_words):
    if word:
        pos = "start" if i % 6 == 0 else ("end" if i % 6 == 5 else "middle")
        ending = word[-2:] if len(word) >= 2 else word
        endings[pos][ending] += 1

for pos in ["start", "middle", "end"]:
    print(f"\n{pos.upper()} position endings:")
    for ending, count in endings[pos].most_common(8):
        print(f"  -{ending}: {count}x")

# TEST 2: Word length patterns
print("\n\n### TEST 2: Word length distribution")
print("-" * 50)
print("Unusual length patterns might indicate encoding")

lengths = Counter(len(w) for w in corpus.words if w)
total = sum(lengths.values())
print("Length distribution:")
for length in sorted(lengths.keys()):
    count = lengths[length]
    pct = 100 * count / total
    bar = "#" * int(pct)
    print(f"  {length:2d} chars: {count:5d} ({pct:5.1f}%) {bar}")

# TEST 3: Character frequency by position within word
print("\n\n### TEST 3: Character position analysis")
print("-" * 50)
print("If certain chars only appear in certain positions, they may be markers")

char_positions = defaultdict(Counter)
for word in corpus.words:
    if word.text and len(word.text) >= 3:
        char_positions['first'][word.text[0]] += 1
        char_positions['second'][word.text[1]] += 1
        char_positions['last'][word.text[-1]] += 1
        char_positions['second_last'][word.text[-2]] += 1

print("\nCharacters that appear >80% in ONE position (likely structural):")
all_chars = set()
for pos in char_positions:
    all_chars.update(char_positions[pos].keys())

for char in sorted(all_chars):
    total_char = sum(char_positions[pos][char] for pos in char_positions)
    if total_char > 100:  # Only look at common chars
        for pos in char_positions:
            pct = 100 * char_positions[pos][char] / total_char
            if pct > 70:
                print(f"  '{char}' appears {pct:.0f}% in {pos} position ({total_char} total)")

# TEST 4: Repeated adjacent words
print("\n\n### TEST 4: Adjacent word repetition")
print("-" * 50)
print("Repeated words might be emphasis, or a coding pattern")

repetitions = []
for folio, words in folio_words.items():
    for i in range(len(words) - 1):
        if words[i] == words[i+1] and words[i]:
            repetitions.append((folio, words[i]))

rep_words = Counter(w for f, w in repetitions)
print(f"Total adjacent repetitions: {len(repetitions)}")
print("Most repeated adjacent words:")
for word, count in rep_words.most_common(15):
    print(f"  '{word}': {count}x")

# TEST 5: Word frequency vs position correlation
print("\n\n### TEST 5: High-frequency words - are they function words?")
print("-" * 50)
print("In natural language, most common words are function words (the, and, of)")

word_freq = Counter(w.text for w in corpus.words if w.text)
print("Top 20 most frequent words:")
for word, count in word_freq.most_common(20):
    # Check if they appear more at certain positions
    print(f"  {word}: {count}x")

# TEST 6: Look for "sentence" patterns
print("\n\n### TEST 6: Potential sentence markers")
print("-" * 50)
print("Looking for words that might mark phrase boundaries")

# Words that often appear after rare words (potential sentence starts)
rare_words = set(w for w, c in word_freq.items() if c < 5)
after_rare = Counter()
words_list = [w.text for w in corpus.words]
for i in range(len(words_list) - 1):
    if words_list[i] in rare_words and words_list[i+1]:
        after_rare[words_list[i+1]] += 1

print("Words that frequently follow rare words (potential restarts):")
for word, count in after_rare.most_common(10):
    total = word_freq[word]
    pct = 100 * count / total if total else 0
    print(f"  {word}: {count}x after rare words ({pct:.0f}% of its occurrences)")

# TEST 7: Check for null/filler pattern
print("\n\n### TEST 7: Potential NULL/FILLER words")
print("-" * 50)
print("Words that appear everywhere equally might be meaningless filler")

# Calculate how evenly distributed each common word is across folios
print("Words with most even distribution (potential fillers):")
common_words = [w for w, c in word_freq.most_common(50)]
for word in common_words[:20]:
    folios_with_word = sum(1 for f, words in folio_words.items() if word in words)
    total_folios = len(folio_words)
    pct = 100 * folios_with_word / total_folios
    if pct > 80:
        print(f"  {word}: appears in {pct:.0f}% of folios - POSSIBLE FILLER")
