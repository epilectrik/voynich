"""Check prefix distribution in Currier B."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[(df['transcriber'] == 'H') & (df['language'] == 'B')]

prefixes = ['ok', 'ot', 'ch', 'sh', 'da', 'qo', 'ol']

print("PREFIX counts in Currier B:")
print(f"Total B tokens: {len(df)}")
print()
for p in prefixes:
    count = df['word'].str.startswith(p, na=False).sum()
    pct = count / len(df) * 100
    print(f"  {p}: {count} ({pct:.1f}%)")
