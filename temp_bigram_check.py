"""Check if bigram analyses were affected by transcriber interleaving."""
import pandas as pd
from collections import Counter

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

def get_bigrams_sequential(df_subset):
    """Get bigrams by reading rows sequentially (WRONG method)."""
    words = df_subset['word'].dropna().tolist()
    return [(words[i], words[i+1]) for i in range(len(words)-1)]

def get_bigrams_by_line(df_subset):
    """Get bigrams properly grouped by line (CORRECT method)."""
    bigrams = []
    for (folio, line_num), group in df_subset.groupby(['folio', 'line_number']):
        words = group['word'].dropna().tolist()
        for i in range(len(words)-1):
            bigrams.append((words[i], words[i+1]))
    return bigrams

# Currier B
b_all = df[df['language'] == 'B']
b_h = df[(df['language'] == 'B') & (df['transcriber'] == 'H')]

print("BIGRAM ANALYSIS CHECK")
print("=" * 70)

# Sequential method (wrong)
seq_all = get_bigrams_sequential(b_all)
seq_h = get_bigrams_sequential(b_h)

# Grouped method (correct)
grp_all = get_bigrams_by_line(b_all)
grp_h = get_bigrams_by_line(b_h)

print("\nSequential reading (WRONG - affected by transcriber order):")
print(f"  All transcribers: {len(seq_all)} bigrams")
print(f"  H-only: {len(seq_h)} bigrams")

print("\nGrouped by line (CORRECT):")
print(f"  All transcribers: {len(grp_all)} bigrams")
print(f"  H-only: {len(grp_h)} bigrams")

# Check for same-token bigrams (strong indicator of transcriber artifact)
def count_same_token_bigrams(bigrams):
    return sum(1 for a, b in bigrams if a == b)

print("\n" + "-" * 70)
print("Same-token bigrams (e.g., 'daiin'-'daiin'):")
print(f"  Sequential ALL: {count_same_token_bigrams(seq_all)}")
print(f"  Sequential H: {count_same_token_bigrams(seq_h)}")
print(f"  Grouped ALL: {count_same_token_bigrams(grp_all)}")
print(f"  Grouped H: {count_same_token_bigrams(grp_h)}")

# The 70.7% bigram reuse claim
print("\n" + "=" * 70)
print("C267 claims: 70.7% bigram reuse")
print("=" * 70)

def bigram_reuse_rate(bigrams):
    counts = Counter(bigrams)
    total = len(bigrams)
    reused = sum(c for c in counts.values() if c > 1)
    return 100 * reused / total if total > 0 else 0

# For Currier A (where C267 applies)
a_all = df[df['language'] == 'A']
a_h = df[(df['language'] == 'A') & (df['transcriber'] == 'H')]

grp_a_all = get_bigrams_by_line(a_all)
grp_a_h = get_bigrams_by_line(a_h)

print(f"\nCurrier A bigram reuse (grouped by line):")
print(f"  All transcribers: {bigram_reuse_rate(grp_a_all):.1f}%")
print(f"  H-only: {bigram_reuse_rate(grp_a_h):.1f}%")
