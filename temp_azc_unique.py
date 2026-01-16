"""Check AZC-unique types (absent from both A and B)."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# All transcribers
a_types_all = set(df[df['language'] == 'A']['word'].dropna())
b_types_all = set(df[df['language'] == 'B']['word'].dropna())
azc_types_all = set(df[df['language'].isna()]['word'].dropna())
azc_unique_all = azc_types_all - a_types_all - b_types_all

# H-only
h = df[df['transcriber'] == 'H']
a_types_h = set(h[h['language'] == 'A']['word'].dropna())
b_types_h = set(h[h['language'] == 'B']['word'].dropna())
azc_types_h = set(h[h['language'].isna()]['word'].dropna())
azc_unique_h = azc_types_h - a_types_h - b_types_h

print("AZC-unique types (absent from A AND B):")
print(f"  All transcribers: {len(azc_unique_all)}")
print(f"  H-only: {len(azc_unique_h)}")
print(f"  C304 claims: 1,529")
print(f"  Match: {len(azc_unique_all) == 1529}")
