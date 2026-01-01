"""Test if removing 'y' endings reveals hidden structure."""
import json
import sys
sys.path.insert(0, '.')
from collections import Counter
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')
all_words = [w.text for w in corpus.words if w.text]

print("=" * 70)
print("TESTING: Is 'y' a meaningless suffix/word marker?")
print("=" * 70)

# Strip 'y' from end of words
stripped = []
for word in all_words:
    if word.endswith('y') and len(word) > 1:
        stripped.append(word[:-1])
    else:
        stripped.append(word)

# Compare vocabularies
original_vocab = set(all_words)
stripped_vocab = set(stripped)

print(f"\nOriginal unique words: {len(original_vocab)}")
print(f"After stripping 'y': {len(stripped_vocab)}")
print(f"Reduction: {len(original_vocab) - len(stripped_vocab)} words ({100*(len(original_vocab) - len(stripped_vocab))/len(original_vocab):.1f}%)")

# Check: do -y words collapse into non-y words?
collapses = []
for word in original_vocab:
    if word.endswith('y') and word[:-1] in original_vocab:
        collapses.append((word, word[:-1]))

print(f"\nWords where X and Xy BOTH exist: {len(collapses)}")
print("Examples:")
for wy, w in sorted(collapses, key=lambda x: -all_words.count(x[0]))[:20]:
    count_y = all_words.count(wy)
    count_no = all_words.count(w)
    print(f"  {w} ({count_no}x) vs {wy} ({count_y}x)")

# Test: what are the most common words AFTER stripping y?
print("\n" + "=" * 70)
print("Most common words after stripping 'y':")
print("=" * 70)
stripped_freq = Counter(stripped)
for word, count in stripped_freq.most_common(30):
    # Show what original forms this came from
    sources = []
    if word in original_vocab:
        sources.append(f"{word}:{all_words.count(word)}")
    if word + 'y' in original_vocab:
        sources.append(f"{word}y:{all_words.count(word+'y')}")
    print(f"  {word}: {count}x  <- {', '.join(sources)}")

# Test the 'dy' pattern specifically
print("\n" + "=" * 70)
print("Testing '-dy' ending (17% of words)")
print("=" * 70)
dy_words = [w for w in all_words if w.endswith('dy')]
print(f"Words ending in -dy: {len(dy_words)}")

# Strip 'dy' and see what's left
stripped_dy = Counter()
for word in dy_words:
    base = word[:-2]  # Remove 'dy'
    stripped_dy[base] += 1

print("\nMost common bases after removing '-dy':")
for base, count in stripped_dy.most_common(20):
    full_word = base + 'dy'
    print(f"  {base} ({count}x) <- {full_word}")
