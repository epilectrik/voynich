import pandas as pd
DATA_PATH = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
df_b = df[df['language'] == 'B']

# Look for tokens starting with ta, op, pc, do (non-y-initial HT)
prefixes = ['ta', 'op', 'pc', 'do']
for prefix in prefixes:
    matches = df_b[df_b['word'].str.startswith(prefix, na=False)]['word'].value_counts().head(10)
    print(f'\nTokens starting with {prefix}:')
    for tok, count in matches.items():
        print(f'  {tok}: {count}')

# Also check what percentages these are
print("\n\n=== Summary ===")
total = len(df_b)
for prefix in prefixes:
    count = df_b['word'].str.startswith(prefix, na=False).sum()
    print(f"{prefix}: {count} tokens ({count/total*100:.2f}%)")

# Check y-initial tokens with these patterns inside
print("\n\n=== y-initial tokens with ta/op/pc/do after y ===")
for pattern in ['yta', 'yop', 'ypc', 'ydo']:
    matches = df_b[df_b['word'].str.startswith(pattern, na=False)]['word'].value_counts().head(5)
    total_pat = df_b['word'].str.startswith(pattern, na=False).sum()
    print(f"\n{pattern}: {total_pat} tokens")
    for tok, count in matches.items():
        print(f"  {tok}: {count}")
