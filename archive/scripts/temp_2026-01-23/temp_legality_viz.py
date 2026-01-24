"""Visualize AZC legality filtering on a B folio."""
import pandas as pd
import json
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_middle(token):
    if pd.isna(token): return None
    token = str(token)
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else '_EMPTY_'

# Split by system
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()
df_azc = df[df['language'].isna()].copy()  # AZC tokens

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)
df_azc['middle'] = df_azc['word'].apply(extract_middle)

# Get MIDDLEs by AZC folio
azc_folios = df_azc['folio'].unique()
azc_middles_by_folio = {f: set(df_azc[df_azc['folio'] == f]['middle'].dropna())
                         for f in azc_folios}

# Get A entries (line-level)
a_entries = df_a.groupby(['folio', 'line_number']).agg({
    'word': list,
    'middle': lambda x: set(x.dropna())
}).reset_index()

print("=" * 70)
print("AZC LEGALITY VISUALIZATION")
print("=" * 70)

# Pick a B folio
b_folio = 'f76r'  # One of the higher-coverage folios
b_tokens = df_b[df_b['folio'] == b_folio].copy()
b_tokens['middle'] = b_tokens['word'].apply(extract_middle)

print(f"\nB Folio: {b_folio}")
print(f"Total tokens: {len(b_tokens)}")
print(f"Unique tokens: {b_tokens['word'].nunique()}")
print(f"Unique MIDDLEs: {b_tokens['middle'].nunique()}")

# Get all MIDDLEs in this B folio
b_middles = set(b_tokens['middle'].dropna())

# Pick an AZC folio to use as filter
azc_folio = 'f72r1'  # Example zodiac folio
legal_middles = azc_middles_by_folio.get(azc_folio, set())

print(f"\nAZC Folio: {azc_folio}")
print(f"Legal MIDDLEs in this AZC context: {len(legal_middles)}")

# Check which B tokens would be legal/illegal
b_tokens['legal'] = b_tokens['middle'].apply(lambda m: m in legal_middles if m else False)

legal_count = b_tokens['legal'].sum()
illegal_count = len(b_tokens) - legal_count

print(f"\n--- LEGALITY FILTER RESULT ---")
print(f"Legal tokens (MIDDLE in AZC): {legal_count} ({legal_count/len(b_tokens)*100:.1f}%)")
print(f"Illegal tokens (MIDDLE not in AZC): {illegal_count} ({illegal_count/len(b_tokens)*100:.1f}%)")

# Show first few lines with legality marked
print(f"\n--- FIRST 5 LINES OF {b_folio} WITH LEGALITY ---")
print("(tokens in [brackets] are ILLEGAL in this AZC context)")
print()

for line_num in sorted(b_tokens['line_number'].unique())[:5]:
    line_tokens = b_tokens[b_tokens['line_number'] == line_num]
    tokens_display = []
    for _, row in line_tokens.iterrows():
        if row['legal']:
            tokens_display.append(row['word'])
        else:
            tokens_display.append(f"[{row['word']}]")
    print(f"Line {line_num}: {' '.join(tokens_display)}")

# Now show what happens with a DIFFERENT AZC folio
print("\n" + "=" * 70)
print("COMPARE: Different AZC context")
print("=" * 70)

azc_folio2 = 'f72r3'  # Different zodiac folio
legal_middles2 = azc_middles_by_folio.get(azc_folio2, set())

print(f"\nAZC Folio: {azc_folio2}")
print(f"Legal MIDDLEs in this AZC context: {len(legal_middles2)}")

b_tokens['legal2'] = b_tokens['middle'].apply(lambda m: m in legal_middles2 if m else False)

legal_count2 = b_tokens['legal2'].sum()
print(f"Legal tokens: {legal_count2} ({legal_count2/len(b_tokens)*100:.1f}%)")

# Show same lines with different legality
print(f"\n--- SAME LINES, DIFFERENT AZC CONTEXT ---")
print()

for line_num in sorted(b_tokens['line_number'].unique())[:5]:
    line_tokens = b_tokens[b_tokens['line_number'] == line_num]
    tokens_display = []
    for _, row in line_tokens.iterrows():
        if row['legal2']:
            tokens_display.append(row['word'])
        else:
            tokens_display.append(f"[{row['word']}]")
    print(f"Line {line_num}: {' '.join(tokens_display)}")

# Show tokens that are legal in one but not the other
print("\n" + "=" * 70)
print("DIFFERENTIAL LEGALITY")
print("=" * 70)

only_in_first = legal_middles - legal_middles2
only_in_second = legal_middles2 - legal_middles
in_both = legal_middles & legal_middles2

print(f"\nMIDDLEs legal ONLY in {azc_folio}: {len(only_in_first)}")
print(f"MIDDLEs legal ONLY in {azc_folio2}: {len(only_in_second)}")
print(f"MIDDLEs legal in BOTH: {len(in_both)}")

# Show which B tokens flip legality between contexts
flipped = b_tokens[b_tokens['legal'] != b_tokens['legal2']]['word'].unique()
print(f"\nB tokens that FLIP legality between contexts: {len(flipped)}")
if len(flipped) > 0:
    print(f"Examples: {list(flipped)[:10]}")
