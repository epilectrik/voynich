"""Check if transcriber interleaving creates false repetition patterns."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# Check what folios exist
print(f"Sample folios: {df['folio'].dropna().unique()[:10]}")

# Try with '1r' instead of 'f1r'
sample = df[(df['folio'] == '1r') & (df['line_number'] == 3)].copy()
print(f"\nRows for 1r line 3: {len(sample)}")

if len(sample) == 0:
    # Check actual folio format
    f1r_rows = df[df['folio'].str.contains('1r', na=False)]
    print(f"Rows containing '1r': {len(f1r_rows)}")
    if len(f1r_rows) > 0:
        print(f"Sample folio values: {f1r_rows['folio'].unique()[:5]}")

# Let's just pick any line with multiple transcribers
print("\n" + "=" * 60)
print("Finding a line with multiple transcribers...")
print("=" * 60)

# Group by folio, line and count transcribers
grouped = df.groupby(['folio', 'line_number'])['transcriber'].nunique()
multi_trans = grouped[grouped > 1]
if len(multi_trans) > 0:
    folio, line = multi_trans.index[0]
    print(f"Using {folio} line {line}")

    sample = df[(df['folio'] == folio) & (df['line_number'] == line)].copy()

    print(f"\nRaw row order ({len(sample)} rows):")
    print("-" * 50)
    for i, (_, row) in enumerate(sample.head(30).iterrows()):
        print(f"  {i:2d}: {row['word']:<15} T={row['transcriber']}")

    print("\n" + "=" * 50)
    print("Checking for apparent consecutive repetitions:")
    words = sample['word'].tolist()
    found = False
    for i in range(len(words) - 1):
        if words[i] == words[i+1]:
            found = True
            t1 = sample.iloc[i]['transcriber']
            t2 = sample.iloc[i+1]['transcriber']
            print(f"  '{words[i]}' at rows {i},{i+1} (trans: {t1},{t2})")
    if not found:
        print("  None found in this sample")
