"""Check AZC token counts more carefully."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

print("Section distribution:")
for section in sorted(df['section'].dropna().unique()):
    all_count = len(df[df['section'] == section])
    h_count = len(df[(df['section'] == section) & (df['transcriber'] == 'H')])
    print(f"  {section}: all={all_count}, H-only={h_count}")

print("\nLanguage distribution:")
for lang in sorted(df['language'].dropna().unique()):
    all_count = len(df[df['language'] == lang])
    h_count = len(df[(df['language'] == lang) & (df['transcriber'] == 'H')])
    print(f"  {lang}: all={all_count}, H-only={h_count}")

# AZC is defined as language=NaN (not A, not B)
print("\nAZC (language=NaN):")
azc_all = df[df['language'].isna()]
azc_h = df[(df['language'].isna()) & (df['transcriber'] == 'H')]
print(f"  All transcribers: {len(azc_all)} tokens")
print(f"  H-only: {len(azc_h)} tokens")
print(f"  Unique types (all): {len(azc_all['word'].dropna().unique())}")
print(f"  Unique types (H): {len(azc_h['word'].dropna().unique())}")

# What percentage of H corpus is AZC?
h_total = len(df[df['transcriber'] == 'H'])
print(f"\nH-only total: {h_total}")
print(f"H-only AZC: {len(azc_h)} ({100*len(azc_h)/h_total:.1f}%)")

# What percentage of all corpus is AZC?
all_total = len(df)
print(f"\nAll-transcriber total: {all_total}")
print(f"All-transcriber AZC: {len(azc_all)} ({100*len(azc_all)/all_total:.1f}%)")
