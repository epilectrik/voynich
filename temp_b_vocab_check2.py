"""Check Currier B vocabulary size using language column."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# The language column contains Currier classification
print(f"Language values: {df['language'].unique()}")

# Get Currier B
b_all = df[df['language'] == 'B']
b_h = df[(df['language'] == 'B') & (df['transcriber'] == 'H')]

print(f"\nCurrier B vocabulary:")
print(f"  All transcribers: {len(b_all['word'].dropna().unique())} unique tokens")
print(f"  H-only: {len(b_h['word'].dropna().unique())} unique tokens")
print(f"  Ratio: {len(b_all['word'].dropna().unique()) / len(b_h['word'].dropna().unique()):.2f}x")

# Also check token counts
print(f"\nCurrier B token counts:")
print(f"  All transcribers: {len(b_all)}")
print(f"  H-only: {len(b_h)}")

# The constraint says 479 - let's see how close H is
print(f"\n479 in constraint vs {len(b_h['word'].dropna().unique())} in H-only")
