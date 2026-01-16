"""Check if top 480 tokens are the same between H-only and all-transcriber."""
import pandas as pd
from collections import Counter

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# Get Currier B
b_all = df[df['language'] == 'B']['word'].dropna()
b_h = df[(df['language'] == 'B') & (df['transcriber'] == 'H')]['word'].dropna()

# Top 480 by frequency
top480_all = set([t for t, _ in Counter(b_all).most_common(480)])
top480_h = set([t for t, _ in Counter(b_h).most_common(480)])

print(f"Top 480 tokens:")
print(f"  All transcribers: {len(top480_all)} unique")
print(f"  H-only: {len(top480_h)} unique")

# Overlap
overlap = top480_all & top480_h
print(f"\nOverlap: {len(overlap)} tokens ({100*len(overlap)/480:.1f}%)")

# Tokens in all but not H
only_all = top480_all - top480_h
print(f"\nTokens in top480-all but NOT top480-H: {len(only_all)}")
if only_all:
    print(f"  Examples: {list(only_all)[:10]}")

# Tokens in H but not all
only_h = top480_h - top480_all
print(f"\nTokens in top480-H but NOT top480-all: {len(only_h)}")
if only_h:
    print(f"  Examples: {list(only_h)[:10]}")
