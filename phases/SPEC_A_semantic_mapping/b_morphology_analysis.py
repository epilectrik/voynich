"""
Currier B Compositional Morphology Analysis

Question: Does B have the same PREFIX+MIDDLE+SUFFIX structure as A?

If B has different morphology, it confirms A/B serve fundamentally different functions.
If B has the SAME morphology, it suggests deeper integration than currently understood.
"""

from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# A's known prefixes for comparison
A_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# A's known suffixes
A_SUFFIXES = ['-y', '-l', '-iin', '-r', '-m', '-ol', '-eol', '-ain', '-aiin']

# Load B tokens
b_tokens = []

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            word = parts[0].strip('"').strip().lower()
            if word and lang == 'B':
                b_tokens.append(word)

print("=" * 70)
print("CURRIER B COMPOSITIONAL MORPHOLOGY ANALYSIS")
print("=" * 70)

# Basic stats
b_vocab = Counter(b_tokens)
print(f"\n### BASIC STATISTICS")
print(f"Total B tokens: {len(b_tokens)}")
print(f"Unique B tokens: {len(b_vocab)}")
print(f"TTR: {len(b_vocab)/len(b_tokens):.3f}")

# Top tokens
print(f"\n### TOP 30 B TOKENS")
print(f"{'Token':<15} {'Count':>8} {'%':>8}")
print("-" * 35)
for tok, count in b_vocab.most_common(30):
    print(f"{tok:<15} {count:>8} {100*count/len(b_tokens):>7.2f}%")

# Test PREFIX structure
print(f"\n\n### PREFIX ANALYSIS")
print("=" * 70)
print("Testing if B tokens start with A's known prefixes...")

prefix_counts = Counter()
no_prefix = []

for tok in b_vocab:
    found = False
    for p in A_PREFIXES:
        if tok.startswith(p):
            prefix_counts[p] += b_vocab[tok]
            found = True
            break
    if not found:
        no_prefix.append(tok)

total_with_prefix = sum(prefix_counts.values())
print(f"\nTokens with A-style prefix: {total_with_prefix} ({100*total_with_prefix/len(b_tokens):.1f}%)")
print(f"Tokens WITHOUT A-style prefix: {len(b_tokens) - total_with_prefix} ({100*(len(b_tokens)-total_with_prefix)/len(b_tokens):.1f}%)")

print(f"\n{'Prefix':<10} {'Count':>10} {'%':>10}")
print("-" * 35)
for p in A_PREFIXES:
    count = prefix_counts.get(p, 0)
    print(f"{p:<10} {count:>10} {100*count/len(b_tokens):>9.1f}%")

# What are the no-prefix tokens?
print(f"\n### TOKENS WITHOUT A-STYLE PREFIX")
print("-" * 70)
no_prefix_freq = Counter()
for tok in no_prefix:
    no_prefix_freq[tok] = b_vocab[tok]

print(f"Unique tokens without prefix: {len(no_prefix)}")
print(f"\nTop 30 non-prefixed tokens:")
for tok, count in no_prefix_freq.most_common(30):
    print(f"  {tok}: {count}")

# Check what these tokens START with
print(f"\n### WHAT DO NON-PREFIXED TOKENS START WITH?")
print("-" * 70)
start_chars = Counter()
start_digraphs = Counter()
for tok in no_prefix:
    if tok:
        start_chars[tok[0]] += b_vocab[tok]
        if len(tok) >= 2:
            start_digraphs[tok[:2]] += b_vocab[tok]

print(f"\nFirst character distribution:")
for char, count in start_chars.most_common(15):
    print(f"  {char}: {count} ({100*count/sum(start_chars.values()):.1f}%)")

print(f"\nFirst digraph distribution:")
for digraph, count in start_digraphs.most_common(15):
    print(f"  {digraph}: {count} ({100*count/sum(start_digraphs.values()):.1f}%)")

# Test SUFFIX structure
print(f"\n\n### SUFFIX ANALYSIS")
print("=" * 70)

suffix_patterns = ['-y', '-dy', '-ey', '-chy', '-shy',
                   '-l', '-ol', '-al', '-eol',
                   '-iin', '-aiin', '-oiin',
                   '-r', '-or', '-ar', '-er',
                   '-m', '-am', '-om',
                   '-n', '-ain', '-in']

suffix_counts = Counter()
for tok in b_vocab:
    for suf in suffix_patterns:
        if tok.endswith(suf[1:]):  # Remove leading dash
            suffix_counts[suf] += b_vocab[tok]
            break

print(f"\n{'Suffix':<10} {'Count':>10} {'%':>10}")
print("-" * 35)
for suf in sorted(suffix_counts.keys(), key=lambda x: -suffix_counts[x])[:15]:
    count = suffix_counts[suf]
    print(f"{suf:<10} {count:>10} {100*count/len(b_tokens):>9.1f}%")

# What do tokens END with?
print(f"\n### TERMINAL CHARACTER ANALYSIS")
print("-" * 70)
end_chars = Counter()
end_digraphs = Counter()
for tok in b_vocab:
    if tok:
        end_chars[tok[-1]] += b_vocab[tok]
        if len(tok) >= 2:
            end_digraphs[tok[-2:]] += b_vocab[tok]

print(f"\nLast character distribution:")
for char, count in end_chars.most_common(15):
    print(f"  {char}: {count} ({100*count/len(b_tokens):.1f}%)")

print(f"\nLast digraph distribution:")
for digraph, count in end_digraphs.most_common(15):
    print(f"  {digraph}: {count} ({100*count/len(b_tokens):.1f}%)")

# Compare to A's morphology
print(f"\n\n### COMPARISON TO CURRIER A")
print("=" * 70)

# Load A tokens for comparison
a_tokens = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            word = parts[0].strip('"').strip().lower()
            if word and lang == 'A':
                a_tokens.append(word)

a_vocab = Counter(a_tokens)

# Prefix coverage comparison
a_prefix_count = 0
for tok in a_vocab:
    for p in A_PREFIXES:
        if tok.startswith(p):
            a_prefix_count += a_vocab[tok]
            break

print(f"\nPREFIX COVERAGE:")
print(f"  A: {100*a_prefix_count/len(a_tokens):.1f}% of tokens have A-style prefix")
print(f"  B: {100*total_with_prefix/len(b_tokens):.1f}% of tokens have A-style prefix")

# Vocabulary overlap
a_vocab_set = set(a_vocab.keys())
b_vocab_set = set(b_vocab.keys())
overlap = a_vocab_set & b_vocab_set

print(f"\nVOCABULARY OVERLAP:")
print(f"  A unique tokens: {len(a_vocab_set)}")
print(f"  B unique tokens: {len(b_vocab_set)}")
print(f"  Shared tokens: {len(overlap)} ({100*len(overlap)/len(a_vocab_set | b_vocab_set):.1f}% Jaccard)")

# What's in the overlap?
print(f"\n### SHARED VOCABULARY (top 30 by B frequency)")
overlap_by_b_freq = [(tok, b_vocab[tok], a_vocab[tok]) for tok in overlap]
overlap_by_b_freq.sort(key=lambda x: -x[1])

print(f"{'Token':<15} {'B count':>10} {'A count':>10} {'B/A ratio':>12}")
print("-" * 50)
for tok, b_count, a_count in overlap_by_b_freq[:30]:
    ratio = b_count / a_count if a_count > 0 else float('inf')
    print(f"{tok:<15} {b_count:>10} {a_count:>10} {ratio:>11.2f}x")

# Look for B-specific prefixes
print(f"\n\n### B-SPECIFIC PREFIX CANDIDATES")
print("=" * 70)

# Find common starting patterns in B that are rare in A
b_starts = Counter()
for tok in b_vocab:
    if len(tok) >= 2:
        b_starts[tok[:2]] += b_vocab[tok]

a_starts = Counter()
for tok in a_vocab:
    if len(tok) >= 2:
        a_starts[tok[:2]] += a_vocab[tok]

print(f"\nDigraphs that START B tokens more than A tokens:")
print(f"{'Digraph':<10} {'B count':>10} {'A count':>10} {'B/A ratio':>12}")
print("-" * 45)
for digraph, b_count in b_starts.most_common(30):
    a_count = a_starts.get(digraph, 0)
    if b_count > 100:  # Only significant ones
        ratio = b_count / a_count if a_count > 0 else float('inf')
        if ratio > 2:  # B-favored
            print(f"{digraph:<10} {b_count:>10} {a_count:>10} {ratio:>11.2f}x")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
