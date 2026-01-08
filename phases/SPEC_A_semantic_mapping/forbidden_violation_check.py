"""
Sanity check: Why only 5 forbidden violations when running A through B grammar?

Expected: If A transitions are random w.r.t. B grammar, ~0.7% should hit forbidden pairs.
Observed: Only 5 violations.

Questions:
1. How many A transitions involve TWO B-vocabulary tokens?
2. What's the expected violation count under random model?
3. Is 5 surprisingly low, or expected given vocabulary overlap?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load the canonical grammar to get B vocabulary and forbidden transitions
grammar_path = project_root / 'results' / 'canonical_grammar.json'

# First, let's get B vocabulary
b_tokens = set()
a_tokens = set()

b_transitions = []
a_transitions = []

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    prev_token = None
    prev_lang = None

    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            word = parts[0].strip('"').strip().lower()

            if word:
                if lang == 'B':
                    b_tokens.add(word)
                    if prev_token and prev_lang == 'B':
                        b_transitions.append((prev_token, word))
                elif lang == 'A':
                    a_tokens.add(word)
                    if prev_token and prev_lang == 'A':
                        a_transitions.append((prev_token, word))

                prev_token = word
                prev_lang = lang

print("=" * 70)
print("FORBIDDEN VIOLATION SANITY CHECK")
print("=" * 70)

print(f"\n### VOCABULARY SIZES")
print(f"B vocabulary: {len(b_tokens)} unique tokens")
print(f"A vocabulary: {len(a_tokens)} unique tokens")

# Overlap
overlap = a_tokens & b_tokens
print(f"Overlap (in both A and B): {len(overlap)} tokens")
print(f"A-only tokens: {len(a_tokens - b_tokens)}")
print(f"B-only tokens: {len(b_tokens - a_tokens)}")

print(f"\n### TRANSITION COUNTS")
print(f"Total A transitions: {len(a_transitions)}")
print(f"Total B transitions: {len(b_transitions)}")

# How many A transitions have BOTH tokens in B vocabulary?
a_trans_both_in_b = [(t1, t2) for t1, t2 in a_transitions if t1 in b_tokens and t2 in b_tokens]
a_trans_first_in_b = [(t1, t2) for t1, t2 in a_transitions if t1 in b_tokens]
a_trans_second_in_b = [(t1, t2) for t1, t2 in a_transitions if t2 in b_tokens]

print(f"\nA transitions where BOTH tokens in B vocab: {len(a_trans_both_in_b)}")
print(f"A transitions where FIRST token in B vocab: {len(a_trans_first_in_b)}")
print(f"A transitions where SECOND token in B vocab: {len(a_trans_second_in_b)}")
print(f"A transitions where NEITHER in B vocab: {len(a_transitions) - len(a_trans_first_in_b) - len(a_trans_second_in_b) + len(a_trans_both_in_b)}")

# Expected violations
# B has 17 forbidden transitions. What fraction of B transition space is forbidden?
# We need to load the forbidden transitions

# Try to load from grammar file
try:
    with open(grammar_path, 'r') as f:
        grammar = json.load(f)

    # Check structure
    if 'forbidden_transitions' in grammar:
        forbidden = grammar['forbidden_transitions']
        print(f"\n### FORBIDDEN TRANSITIONS")
        print(f"Number of forbidden transition types: {len(forbidden)}")
    else:
        print("\nNo forbidden_transitions in grammar file")
        forbidden = []
except:
    print("\nCouldn't load grammar file")
    forbidden = []

# Calculate expected violations
# If B has N grammar classes, and 17 forbidden pairs out of N^2 possible
# Then forbidden rate = 17/N^2

# But we're dealing with TOKEN transitions, not CLASS transitions
# A token can appear in multiple classes, or no class

# Simpler approach: count actual forbidden transitions in B
b_forbidden_count = 0
b_trans_counter = Counter(b_transitions)

# We need the actual forbidden token pairs from B
# Let's empirically find transitions that NEVER occur in B but involve common tokens

# Actually, let's just calculate the overlap statistics

print(f"\n### EXPECTED vs OBSERVED")

# Percentage of A transitions where both tokens are in B vocab
pct_both_in_b = 100 * len(a_trans_both_in_b) / len(a_transitions) if a_transitions else 0
print(f"A transitions with both in B vocab: {pct_both_in_b:.1f}%")

# If 17 forbidden out of ~2400 possible class pairs = 0.7%
# Expected violations from random sampling
expected_random = len(a_trans_both_in_b) * 0.007
print(f"\nExpected violations (if 0.7% forbidden rate): {expected_random:.1f}")
print(f"Observed violations: 5")

if expected_random > 0:
    ratio = 5 / expected_random
    print(f"Observed/Expected ratio: {ratio:.2f}")

# Let's also check: what are the most common A transitions that involve B vocab?
print(f"\n### MOST COMMON A TRANSITIONS (both in B vocab)")
trans_counter = Counter(a_trans_both_in_b)
for trans, count in trans_counter.most_common(20):
    print(f"  {trans[0]} -> {trans[1]}: {count}")

# And the overlap vocabulary
print(f"\n### MOST COMMON OVERLAP TOKENS")
overlap_in_a = Counter()
for t in a_tokens:
    if t in overlap:
        # Count occurrences in A
        pass

# Count token frequencies in A for overlap tokens
a_token_freq = Counter()
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            word = parts[0].strip('"').strip().lower()
            if word and lang == 'A' and word in overlap:
                a_token_freq[word] += 1

print(f"\nTop overlap tokens by A frequency:")
for tok, freq in a_token_freq.most_common(15):
    print(f"  {tok}: {freq}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if pct_both_in_b < 5:
    print("""
LOW OVERLAP EXPLANATION:
Only {:.1f}% of A transitions involve two B-vocabulary tokens.
This means A largely operates in vocabulary space OUTSIDE B.
5 violations from {} "both-in-B" transitions = {:.1f}% violation rate.
This is {} the 0.7% expected rate.
""".format(pct_both_in_b, len(a_trans_both_in_b),
           100*5/len(a_trans_both_in_b) if a_trans_both_in_b else 0,
           "close to" if abs(5/len(a_trans_both_in_b) - 0.007) < 0.01 else "different from"))
else:
    print("""
MODERATE OVERLAP:
{:.1f}% of A transitions involve B vocabulary.
Expected ~{:.0f} violations, observed 5.
This suggests {} avoidance of B forbidden patterns.
""".format(pct_both_in_b, expected_random,
           "systematic" if 5 < expected_random * 0.5 else "no special"))
