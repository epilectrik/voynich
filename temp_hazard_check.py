"""Check if forbidden transition analysis is affected."""
import pandas as pd
from collections import Counter

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# The 17 forbidden transitions from BCSC
# These are kernel-level transitions, so we need to extract kernel characters
# h->k is the canonical example

def get_transitions_by_line(df_subset):
    """Get token transitions properly grouped by line."""
    transitions = []
    for (folio, line_num), group in df_subset.groupby(['folio', 'line_number']):
        words = group['word'].dropna().tolist()
        for i in range(len(words)-1):
            transitions.append((str(words[i]), str(words[i+1])))
    return transitions

# Currier B
b_h = df[(df['language'] == 'B') & (df['transcriber'] == 'H')]
b_all = df[df['language'] == 'B']

trans_h = get_transitions_by_line(b_h)
trans_all = get_transitions_by_line(b_all)

print("TRANSITION ANALYSIS CHECK")
print("=" * 70)
print(f"\nTotal transitions (grouped by line):")
print(f"  All transcribers: {len(trans_all)}")
print(f"  H-only: {len(trans_h)}")

# Check specific structural transitions
# Look for h->k at token level (tokens containing 'h' followed by tokens containing 'k')
def contains_char(word, char):
    return char in str(word).lower()

def count_char_transitions(transitions, from_char, to_char):
    count = 0
    for w1, w2 in transitions:
        if contains_char(w1, from_char) and contains_char(w2, to_char):
            count += 1
    return count

print("\n" + "-" * 70)
print("Character-level transitions (in tokens):")

# h->k (supposedly forbidden)
hk_all = count_char_transitions(trans_all, 'h', 'k')
hk_h = count_char_transitions(trans_h, 'h', 'k')
print(f"  h->k: ALL={hk_all}, H={hk_h}")

# k->h (supposedly allowed)
kh_all = count_char_transitions(trans_all, 'k', 'h')
kh_h = count_char_transitions(trans_h, 'k', 'h')
print(f"  k->h: ALL={kh_all}, H={kh_h}")

# Check the C357 claim: 0 violations in 2,338 cross-line bigrams
# This refers to grammar transitions across line breaks
print("\n" + "=" * 70)
print("C357: Cross-line bigrams")
print("=" * 70)

def get_cross_line_bigrams(df_subset):
    """Get bigrams that span line boundaries within a folio."""
    cross_bigrams = []
    for folio, folio_group in df_subset.groupby('folio'):
        lines = sorted(folio_group['line_number'].unique())
        for i in range(len(lines)-1):
            line1 = folio_group[folio_group['line_number'] == lines[i]]
            line2 = folio_group[folio_group['line_number'] == lines[i+1]]
            if len(line1) > 0 and len(line2) > 0:
                last_word = line1['word'].iloc[-1]
                first_word = line2['word'].iloc[0]
                if pd.notna(last_word) and pd.notna(first_word):
                    cross_bigrams.append((str(last_word), str(first_word)))
    return cross_bigrams

cross_h = get_cross_line_bigrams(b_h)
cross_all = get_cross_line_bigrams(b_all)

print(f"\nCross-line bigrams:")
print(f"  All transcribers: {len(cross_all)}")
print(f"  H-only: {len(cross_h)}")
print(f"  C357 claims: 2,338")
