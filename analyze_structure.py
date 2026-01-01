"""Analyze text structure for hidden patterns."""
import json
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# Group words by line
lines = defaultdict(list)
for w in corpus.words:
    key = (w.folio, w.line)
    lines[key].append(w.text)

print("=" * 70)
print("STRUCTURAL ANALYSIS - Looking for Hidden Patterns")
print("=" * 70)

# 1. Word position analysis
print("\n1. WORD POSITION PATTERNS")
print("-" * 50)
position_words = defaultdict(Counter)
for key, words in lines.items():
    for i, word in enumerate(words):
        if i < 6:  # First 6 positions
            position_words[i][word] += 1

for pos in range(6):
    print(f"\nPosition {pos+1} (first word, second word, etc.):")
    top = position_words[pos].most_common(10)
    for word, count in top:
        print(f"  {word}: {count}x")

# 2. Line length distribution
print("\n\n2. LINE LENGTH DISTRIBUTION")
print("-" * 50)
lengths = Counter(len(words) for words in lines.values())
for length, count in sorted(lengths.items()):
    print(f"  {length} words: {count} lines")

# 3. First-last word patterns
print("\n\n3. FIRST vs LAST WORD PATTERNS")
print("-" * 50)
first_words = Counter()
last_words = Counter()
for words in lines.values():
    if words:
        first_words[words[0]] += 1
        last_words[words[-1]] += 1

print("Most common FIRST words:")
for word, count in first_words.most_common(15):
    print(f"  {word}: {count}x")

print("\nMost common LAST words:")
for word, count in last_words.most_common(15):
    print(f"  {word}: {count}x")

# 4. Bigram analysis - what follows what?
print("\n\n4. BIGRAM PATTERNS (word pairs)")
print("-" * 50)
bigrams = Counter()
for words in lines.values():
    for i in range(len(words) - 1):
        bigrams[(words[i], words[i+1])] += 1

print("Most common word pairs:")
for (w1, w2), count in bigrams.most_common(20):
    print(f"  '{w1}' -> '{w2}': {count}x")

# 5. Check for repeated phrases
print("\n\n5. REPEATED PHRASES (3+ words)")
print("-" * 50)
trigrams = Counter()
for words in lines.values():
    for i in range(len(words) - 2):
        trigrams[tuple(words[i:i+3])] += 1

print("Most common 3-word phrases:")
for phrase, count in trigrams.most_common(15):
    if count > 2:
        print(f"  '{' '.join(phrase)}': {count}x")

# 6. Word repetition within lines
print("\n\n6. WORD REPETITION WITHIN LINES")
print("-" * 50)
repetition_count = 0
for key, words in lines.items():
    unique = len(set(words))
    total = len(words)
    if total > unique and total > 3:
        repetition_count += 1

print(f"Lines with repeated words: {repetition_count}/{len(lines)} ({100*repetition_count/len(lines):.1f}%)")

# Example lines with repetition
print("\nExamples of lines with word repetition:")
count = 0
for key, words in lines.items():
    word_counts = Counter(words)
    repeated = [w for w, c in word_counts.items() if c > 1 and w]
    if repeated and len(words) > 3:
        print(f"  {key}: {' '.join(words)}")
        print(f"    Repeated: {repeated}")
        count += 1
        if count >= 5:
            break
