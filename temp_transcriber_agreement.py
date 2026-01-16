"""Check overall transcriber agreement rate."""
import pandas as pd
from collections import defaultdict

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# Get H transcriber tokens as baseline
h_tokens = df[df['transcriber'] == 'H']
print(f"Total H tokens: {len(h_tokens)}")
print(f"Total all tokens: {len(df)}")
print(f"Inflation factor: {len(df) / len(h_tokens):.2f}x")

# Check unique words
h_words = set(h_tokens['word'].dropna())
all_words = set(df['word'].dropna())
print(f"\nUnique words in H: {len(h_words)}")
print(f"Unique words in all: {len(all_words)}")
print(f"Words only in non-H: {len(all_words - h_words)}")

# Sample some words that appear in non-H but not H
only_non_h = list(all_words - h_words)[:20]
print(f"\nSample words only in non-H transcriptions:")
for w in only_non_h[:10]:
    print(f"  {w}")

# Check transcriber distribution
print(f"\nTokens by transcriber:")
for t in sorted(df['transcriber'].unique()):
    count = len(df[df['transcriber'] == t])
    print(f"  {t}: {count} ({100*count/len(df):.1f}%)")
