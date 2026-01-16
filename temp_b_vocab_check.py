"""Check Currier B vocabulary size: H-only vs all transcribers."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# Currier B folios (sections other than A, Z, C, H, S based on our earlier findings)
# Actually, let's use the currier column if it exists
print("Columns:", df.columns.tolist())

# Check if currier column exists
if 'currier' in df.columns:
    b_all = df[df['currier'] == 'B']
    b_h = df[(df['currier'] == 'B') & (df['transcriber'] == 'H')]

    print(f"\nCurrier B vocabulary:")
    print(f"  All transcribers: {len(b_all['word'].dropna().unique())} unique tokens")
    print(f"  H-only: {len(b_h['word'].dropna().unique())} unique tokens")
    print(f"  Ratio: {len(b_all['word'].dropna().unique()) / len(b_h['word'].dropna().unique()):.2f}x")
else:
    print("No 'currier' column found, checking by section...")
    # Try to infer B from section codes
    sections = df['section'].unique()
    print(f"Available sections: {sections}")
