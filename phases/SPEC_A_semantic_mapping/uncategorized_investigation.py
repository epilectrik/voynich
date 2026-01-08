"""
Investigate the ~40,000 "uncategorized" tokens (33.4% of corpus).

Questions:
1. Are they in Currier A or B?
2. What ARE they?
3. Why aren't they categorized?
"""

from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Known prefixes from our compositional analysis
KNOWN_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Load all tokens with metadata
all_tokens = []
by_language = defaultdict(list)
by_section = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            section = parts[3].strip('"').strip() if len(parts) > 3 else ''

            if word:
                all_tokens.append({'word': word, 'lang': lang, 'section': section})
                by_language[lang].append(word)
                by_section[section].append(word)

print("=" * 70)
print("UNCATEGORIZED TOKEN INVESTIGATION")
print("=" * 70)

# Total counts
print(f"\n### TOTAL CORPUS")
print(f"Total tokens: {len(all_tokens)}")
print(f"Currier A tokens: {len(by_language['A'])}")
print(f"Currier B tokens: {len(by_language['B'])}")
print(f"Other/unlabeled: {len(all_tokens) - len(by_language['A']) - len(by_language['B'])}")

# What tokens DON'T have a known prefix?
def has_known_prefix(tok):
    for p in KNOWN_PREFIXES:
        if tok.startswith(p):
            return True
    return False

# Categorize tokens
a_with_prefix = [t for t in by_language['A'] if has_known_prefix(t)]
a_without_prefix = [t for t in by_language['A'] if not has_known_prefix(t)]
b_with_prefix = [t for t in by_language['B'] if has_known_prefix(t)]
b_without_prefix = [t for t in by_language['B'] if not has_known_prefix(t)]

print(f"\n### PREFIX COVERAGE")
print(f"A with known prefix: {len(a_with_prefix)} ({100*len(a_with_prefix)/len(by_language['A']):.1f}%)")
print(f"A WITHOUT known prefix: {len(a_without_prefix)} ({100*len(a_without_prefix)/len(by_language['A']):.1f}%)")
print(f"B with known prefix: {len(b_with_prefix)} ({100*len(b_with_prefix)/len(by_language['B']):.1f}%)")
print(f"B WITHOUT known prefix: {len(b_without_prefix)} ({100*len(b_without_prefix)/len(by_language['B']):.1f}%)")

total_without_prefix = len(a_without_prefix) + len(b_without_prefix)
print(f"\nTOTAL without known prefix: {total_without_prefix} ({100*total_without_prefix/len(all_tokens):.1f}%)")

# What ARE the non-prefix tokens?
print(f"\n### WHAT ARE THE NON-PREFIX TOKENS?")
print("-" * 70)

all_non_prefix = a_without_prefix + b_without_prefix
non_prefix_freq = Counter(all_non_prefix)

print(f"\nTop 50 tokens WITHOUT known prefix:")
print(f"{'Token':<15} {'Total':>8} {'A':>8} {'B':>8}")
print("-" * 45)

a_non_prefix_freq = Counter(a_without_prefix)
b_non_prefix_freq = Counter(b_without_prefix)

for tok, count in non_prefix_freq.most_common(50):
    a_count = a_non_prefix_freq.get(tok, 0)
    b_count = b_non_prefix_freq.get(tok, 0)
    print(f"{tok:<15} {count:>8} {a_count:>8} {b_count:>8}")

# Analyze what these tokens START with
print(f"\n### WHAT DO NON-PREFIX TOKENS START WITH?")
print("-" * 70)

start_chars = Counter()
start_digraphs = Counter()
for tok in all_non_prefix:
    if tok:
        start_chars[tok[0]] += 1
        if len(tok) >= 2:
            start_digraphs[tok[:2]] += 1

print(f"\nFirst character distribution:")
for char, count in start_chars.most_common(15):
    print(f"  {char}: {count} ({100*count/len(all_non_prefix):.1f}%)")

print(f"\nFirst digraph distribution:")
for digraph, count in start_digraphs.most_common(20):
    print(f"  {digraph}: {count} ({100*count/len(all_non_prefix):.1f}%)")

# Are these short tokens?
print(f"\n### TOKEN LENGTH DISTRIBUTION")
print("-" * 70)

prefix_lens = [len(t) for t in a_with_prefix + b_with_prefix]
non_prefix_lens = [len(t) for t in all_non_prefix]

print(f"\nWith prefix: avg {sum(prefix_lens)/len(prefix_lens):.1f} chars")
print(f"Without prefix: avg {sum(non_prefix_lens)/len(non_prefix_lens):.1f} chars")

len_dist = Counter(non_prefix_lens)
print(f"\nNon-prefix token length distribution:")
for length in sorted(len_dist.keys())[:10]:
    count = len_dist[length]
    print(f"  {length} chars: {count} ({100*count/len(non_prefix_lens):.1f}%)")

# Single-character tokens
single_char = [t for t in all_non_prefix if len(t) == 1]
print(f"\n### SINGLE CHARACTER TOKENS")
print(f"Count: {len(single_char)} ({100*len(single_char)/len(all_non_prefix):.1f}% of non-prefix)")
print(f"Distribution: {Counter(single_char).most_common(15)}")

# Check if these are the "grammar" tokens from B
print(f"\n### ARE THESE THE B GRAMMAR TOKENS?")
print("-" * 70)

# Known B grammar/operator patterns
grammar_patterns = ['aiin', 'ain', 'ar', 'or', 'al', 'ol', 'y', 'dy', 'r', 's', 'l', 'o', 'd', 'k', 'e', 'h', 't', 'c']

grammar_tokens = [t for t in all_non_prefix if t in grammar_patterns or len(t) <= 2]
print(f"Short/grammar tokens (len<=2 or known patterns): {len(grammar_tokens)}")
print(f"As % of non-prefix: {100*len(grammar_tokens)/len(all_non_prefix):.1f}%")

# By language
a_grammar = [t for t in a_without_prefix if t in grammar_patterns or len(t) <= 2]
b_grammar = [t for t in b_without_prefix if t in grammar_patterns or len(t) <= 2]
print(f"\nIn A: {len(a_grammar)} ({100*len(a_grammar)/len(a_without_prefix) if a_without_prefix else 0:.1f}%)")
print(f"In B: {len(b_grammar)} ({100*len(b_grammar)/len(b_without_prefix) if b_without_prefix else 0:.1f}%)")

# What's left after removing short tokens?
long_non_prefix = [t for t in all_non_prefix if len(t) > 2 and t not in grammar_patterns]
print(f"\n### LONGER NON-PREFIX TOKENS (len > 2, not grammar)")
print(f"Count: {len(long_non_prefix)}")

long_freq = Counter(long_non_prefix)
print(f"\nTop 30:")
for tok, count in long_freq.most_common(30):
    print(f"  {tok}: {count}")

# Check what these start with
print(f"\n### WHAT DO LONGER NON-PREFIX TOKENS START WITH?")
long_starts = Counter()
for tok in long_non_prefix:
    if len(tok) >= 2:
        long_starts[tok[:2]] += 1

for digraph, count in long_starts.most_common(20):
    print(f"  {digraph}: {count}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
