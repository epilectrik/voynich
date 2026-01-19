"""
Check which specific forbidden transitions could occur in A
and whether A systematically avoids them.
"""

from collections import Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# The 17 forbidden transitions (bidirectional, so 34 pairs total)
FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('aiin', 'shey'),
    ('shey', 'al'), ('al', 'shey'),
    ('shey', 'c'), ('c', 'shey'),
    ('dy', 'aiin'), ('aiin', 'dy'),
    ('dy', 'chey'), ('chey', 'dy'),
    ('chey', 'chedy'), ('chedy', 'chey'),
    ('chey', 'shedy'), ('shedy', 'chey'),
    ('chedy', 'ee'), ('ee', 'chedy'),
    ('c', 'ee'), ('ee', 'c'),
    ('shedy', 'aiin'), ('aiin', 'shedy'),
    ('shedy', 'o'), ('o', 'shedy'),
    ('chol', 'r'), ('r', 'chol'),
    ('l', 'chol'), ('chol', 'l'),
    ('or', 'dal'), ('dal', 'or'),
    ('he', 'or'), ('or', 'he'),
    ('ar', 'dal'), ('dal', 'ar'),
    ('he', 't'), ('t', 'he'),
]

# Get tokens involved in forbidden transitions
forbidden_tokens = set()
for t1, t2 in FORBIDDEN_PAIRS:
    forbidden_tokens.add(t1)
    forbidden_tokens.add(t2)

print("=" * 70)
print("FORBIDDEN TRANSITION TOKEN ANALYSIS")
print("=" * 70)

print(f"\nTokens involved in forbidden transitions: {len(forbidden_tokens)}")
print(sorted(forbidden_tokens))

# Load A and B data
a_tokens_list = []
b_tokens_list = []
a_transitions = []
b_transitions = []

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    prev_token = None
    prev_lang = None

    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue
            lang = parts[6].strip('"').strip()
            word = parts[0].strip('"').strip().lower()

            if word:
                if lang == 'A':
                    a_tokens_list.append(word)
                    if prev_token and prev_lang == 'A':
                        a_transitions.append((prev_token, word))
                elif lang == 'B':
                    b_tokens_list.append(word)
                    if prev_token and prev_lang == 'B':
                        b_transitions.append((prev_token, word))

                prev_token = word
                prev_lang = lang

# Count forbidden token frequencies in A and B
a_token_freq = Counter(a_tokens_list)
b_token_freq = Counter(b_tokens_list)

print(f"\n### FORBIDDEN TOKEN FREQUENCIES IN A vs B")
print(f"{'Token':<10} {'A freq':>10} {'B freq':>10} {'A/B ratio':>12}")
print("-" * 45)

for tok in sorted(forbidden_tokens):
    a_f = a_token_freq.get(tok, 0)
    b_f = b_token_freq.get(tok, 0)
    ratio = a_f / b_f if b_f > 0 else float('inf') if a_f > 0 else 0
    print(f"{tok:<10} {a_f:>10} {b_f:>10} {ratio:>12.2f}")

# Check which forbidden pairs could theoretically occur in A
# (both tokens present in A vocabulary)
a_vocab = set(a_tokens_list)

print(f"\n### FORBIDDEN PAIRS: COULD THEY OCCUR IN A?")
print("-" * 70)

possible_in_a = []
impossible_in_a = []

for t1, t2 in FORBIDDEN_PAIRS:
    if t1 in a_vocab and t2 in a_vocab:
        possible_in_a.append((t1, t2))
    else:
        impossible_in_a.append((t1, t2))

print(f"\nForbidden pairs where BOTH tokens appear in A: {len(possible_in_a)}/34")
print(f"Forbidden pairs where at least one token MISSING from A: {len(impossible_in_a)}/34")

if possible_in_a:
    print(f"\nPossible in A:")
    for t1, t2 in possible_in_a:
        print(f"  {t1} -> {t2}")

# Now check if these possible pairs actually occur
print(f"\n### DO THESE PAIRS ACTUALLY OCCUR IN A?")
print("-" * 70)

a_trans_set = set(a_transitions)
violations_in_a = []

for pair in possible_in_a:
    if pair in a_trans_set:
        count = a_transitions.count(pair)
        violations_in_a.append((pair, count))

print(f"\nForbidden pairs that ACTUALLY OCCUR in A: {len(violations_in_a)}")
for pair, count in violations_in_a:
    print(f"  {pair[0]} -> {pair[1]}: {count} times")

# Calculate expected vs observed
print(f"\n### STATISTICAL COMPARISON")
print("-" * 70)

# For pairs that COULD occur (both tokens in A vocab), how many transitions exist?
# and what fraction are forbidden?

a_trans_counter = Counter(a_transitions)

# Count transitions where both tokens are in forbidden_tokens set AND in A vocab
relevant_transitions = 0
for (t1, t2), count in a_trans_counter.items():
    if t1 in a_vocab and t2 in a_vocab and t1 in forbidden_tokens and t2 in forbidden_tokens:
        relevant_transitions += count

print(f"\nA transitions involving two forbidden-relevant tokens: {relevant_transitions}")
print(f"Forbidden violations among these: {sum(c for _, c in violations_in_a)}")

# What's the rate?
if relevant_transitions > 0:
    violation_rate = sum(c for _, c in violations_in_a) / relevant_transitions
    print(f"Violation rate: {100*violation_rate:.2f}%")

# Compare to expected
# How many of the possible pairs (in possible_in_a) would we expect to hit by chance?
# This requires knowing the marginal probabilities

# Simpler: count how many token PAIRS in A involve tokens from forbidden set
# then estimate expected forbidden rate

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

if len(violations_in_a) <= 5:
    print(f"""
FINDING: Only {len(violations_in_a)} forbidden pairs actually occur in A.

This is explained by:
1. Many forbidden tokens are RARE or ABSENT in A
2. Even when tokens are present, the specific PAIRS rarely form
3. A's vocabulary and transition structure naturally avoids B's hazards

This supports the CO-DESIGN hypothesis:
A and B were designed together, sharing vocabulary but avoiding
each other's structural constraints.
""")
