"""Analyze words in context to find patterns."""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# Get words grouped by folio
folio_words = defaultdict(list)
for w in corpus.words:
    if w.text:
        folio_words[w.folio].append(w.text)

all_words = [w.text for w in corpus.words if w.text]
word_freq = Counter(all_words)

print("=" * 80)
print("CONTEXTUAL WORD ANALYSIS")
print("=" * 80)

# 1. What words appear NEXT TO the most common words?
print("\n### What appears ADJACENT to high-frequency words?")
print("-" * 60)

top_words = ['daiin', 'chedy', 'shedy', 'qokeedy', 'ol', 'chol', 'ar', 'or', 'dar', 'aiin']

for target in top_words:
    before = Counter()
    after = Counter()

    for i, word in enumerate(all_words):
        if word == target:
            if i > 0:
                before[all_words[i-1]] += 1
            if i < len(all_words) - 1:
                after[all_words[i+1]] += 1

    print(f"\n'{target}' ({word_freq[target]}x):")
    print(f"  BEFORE: {', '.join(f'{w}({c})' for w,c in before.most_common(5))}")
    print(f"  AFTER:  {', '.join(f'{w}({c})' for w,c in after.most_common(5))}")

# 2. Find "phrases" - word pairs that always appear together
print("\n\n### Common word PAIRS (potential phrases)")
print("-" * 60)

pairs = Counter()
for i in range(len(all_words) - 1):
    pair = (all_words[i], all_words[i+1])
    pairs[pair] += 1

print("Most common word pairs:")
for (w1, w2), count in pairs.most_common(30):
    if count > 15:
        print(f"  '{w1} {w2}': {count}x")

# 3. Find words that almost always start "sentences" (after rare words)
print("\n\n### Potential sentence/clause starters")
print("-" * 60)

# Words that follow hapax or rare words
rare_set = set(w for w, c in word_freq.items() if c <= 2)
starters = Counter()
for i in range(len(all_words) - 1):
    if all_words[i] in rare_set:
        starters[all_words[i+1]] += 1

print("Words that frequently follow rare words (potential starters):")
for word, count in starters.most_common(15):
    freq = word_freq[word]
    pct = 100 * count / freq
    print(f"  {word}: {count}x after rare words ({pct:.0f}% of occurrences)")

# 4. Analyze the 'y' word specifically
print("\n\n### Analysis of standalone 'y'")
print("-" * 60)

y_before = Counter()
y_after = Counter()
for i, word in enumerate(all_words):
    if word == 'y':
        if i > 0:
            y_before[all_words[i-1]] += 1
        if i < len(all_words) - 1:
            y_after[all_words[i+1]] += 1

print(f"'y' appears {word_freq['y']} times as a standalone word")
print(f"  Before 'y': {', '.join(f'{w}({c})' for w,c in y_before.most_common(10))}")
print(f"  After 'y':  {', '.join(f'{w}({c})' for w,c in y_after.most_common(10))}")

# 5. Look for patterns in the HERBAL section specifically
print("\n\n### HERBAL section (f1-f66) - Plant descriptions")
print("-" * 60)

herbal_words = []
for folio, words in folio_words.items():
    n = ''.join(c for c in folio if c.isdigit())
    if n and int(n) <= 66:
        herbal_words.extend(words)

herbal_freq = Counter(herbal_words)
print(f"Total words in HERBAL: {len(herbal_words)}")
print(f"\nMost common in HERBAL section:")
for word, count in herbal_freq.most_common(20):
    overall = word_freq[word]
    pct_herbal = 100 * count / overall if overall else 0
    enriched = "*HERBAL-SPECIFIC*" if pct_herbal > 40 and count > 50 else ""
    print(f"  {word}: {count}x ({pct_herbal:.0f}% of total) {enriched}")

# 6. Look for repeated patterns that might be "templates"
print("\n\n### Repeated phrase patterns (templates)")
print("-" * 60)

# Look for 3-word sequences that repeat
trigrams = Counter()
for i in range(len(all_words) - 2):
    trigram = tuple(all_words[i:i+3])
    trigrams[trigram] += 1

print("Repeated 3-word phrases:")
for phrase, count in trigrams.most_common(20):
    if count >= 5:
        print(f"  '{' '.join(phrase)}': {count}x")
