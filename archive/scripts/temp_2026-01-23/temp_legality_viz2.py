"""Visualize AZC legality filtering starting from a Currier A entry."""
import pandas as pd
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

# Build A entries (line-level records)
a_entries = []
for (folio, line), group in df_a.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()
    middles = set(group['middle'].dropna())
    a_entries.append({
        'folio': folio,
        'line': line,
        'tokens': tokens,
        'middles': middles,
        'token_count': len(tokens)
    })

# Get MIDDLEs by AZC folio
azc_middles_by_folio = {f: set(df_azc[df_azc['folio'] == f]['middle'].dropna())
                         for f in df_azc['folio'].unique()}

print("=" * 70)
print("CURRIER A ENTRY -> AZC -> B LEGALITY CHAIN")
print("=" * 70)

# Pick a specific A entry with multiple tokens
# Let's find an interesting one
multi_token_entries = [e for e in a_entries if e['token_count'] >= 3]
print(f"\nA entries with 3+ tokens: {len(multi_token_entries)}")

# Pick one
a_entry = multi_token_entries[50]  # Arbitrary choice

print(f"\n--- SELECTED A ENTRY ---")
print(f"Location: {a_entry['folio']}:{a_entry['line']}")
print(f"Tokens: {' '.join(a_entry['tokens'])}")
print(f"MIDDLEs: {a_entry['middles']}")

# Find which AZC folios contain these MIDDLEs
a_middles = a_entry['middles']
azc_matches = {}
for azc_folio, azc_mids in azc_middles_by_folio.items():
    overlap = a_middles & azc_mids
    if overlap:
        azc_matches[azc_folio] = overlap

print(f"\n--- AZC FOLIOS CONTAINING THESE MIDDLEs ---")
for azc_folio, overlap in sorted(azc_matches.items(), key=lambda x: -len(x[1]))[:5]:
    print(f"  {azc_folio}: {len(overlap)} MIDDLEs overlap - {overlap}")

# Pick the best-matching AZC folio
if azc_matches:
    best_azc = max(azc_matches.keys(), key=lambda x: len(azc_matches[x]))
    legal_middles = azc_middles_by_folio[best_azc]

    print(f"\n--- USING AZC FOLIO: {best_azc} ---")
    print(f"Total legal MIDDLEs in this context: {len(legal_middles)}")

    # Now filter a B folio
    b_folio = 'f76r'
    b_tokens = df_b[df_b['folio'] == b_folio].copy()

    b_tokens['legal'] = b_tokens['middle'].apply(lambda m: m in legal_middles if m else False)

    print(f"\n--- B FOLIO {b_folio} FILTERED BY A ENTRY ---")
    print(f"A entry: {a_entry['folio']}:{a_entry['line']} -> AZC {best_azc} -> B {b_folio}")
    print(f"Legal: {b_tokens['legal'].sum()}/{len(b_tokens)} ({b_tokens['legal'].sum()/len(b_tokens)*100:.1f}%)")

    print(f"\n--- FIRST 5 LINES (brackets = illegal) ---")
    for line_num in sorted(b_tokens['line_number'].unique())[:5]:
        line_tokens = b_tokens[b_tokens['line_number'] == line_num]
        tokens_display = []
        for _, row in line_tokens.iterrows():
            if row['legal']:
                tokens_display.append(row['word'])
            else:
                tokens_display.append(f"[{row['word']}]")
        print(f"Line {line_num}: {' '.join(tokens_display)}")

# Now pick a DIFFERENT A entry and show how legality changes
print("\n" + "=" * 70)
print("COMPARE: DIFFERENT A ENTRY")
print("=" * 70)

a_entry2 = multi_token_entries[100]  # Different entry

print(f"\n--- SELECTED A ENTRY #2 ---")
print(f"Location: {a_entry2['folio']}:{a_entry2['line']}")
print(f"Tokens: {' '.join(a_entry2['tokens'])}")
print(f"MIDDLEs: {a_entry2['middles']}")

a_middles2 = a_entry2['middles']
azc_matches2 = {}
for azc_folio, azc_mids in azc_middles_by_folio.items():
    overlap = a_middles2 & azc_mids
    if overlap:
        azc_matches2[azc_folio] = overlap

if azc_matches2:
    best_azc2 = max(azc_matches2.keys(), key=lambda x: len(azc_matches2[x]))
    legal_middles2 = azc_middles_by_folio[best_azc2]

    print(f"\n--- USING AZC FOLIO: {best_azc2} ---")

    b_tokens['legal2'] = b_tokens['middle'].apply(lambda m: m in legal_middles2 if m else False)

    print(f"\n--- SAME B FOLIO, DIFFERENT A ENTRY ---")
    print(f"A entry: {a_entry2['folio']}:{a_entry2['line']} -> AZC {best_azc2} -> B {b_folio}")
    print(f"Legal: {b_tokens['legal2'].sum()}/{len(b_tokens)} ({b_tokens['legal2'].sum()/len(b_tokens)*100:.1f}%)")

    print(f"\n--- FIRST 5 LINES (brackets = illegal) ---")
    for line_num in sorted(b_tokens['line_number'].unique())[:5]:
        line_tokens = b_tokens[b_tokens['line_number'] == line_num]
        tokens_display = []
        for _, row in line_tokens.iterrows():
            if row['legal2']:
                tokens_display.append(row['word'])
            else:
                tokens_display.append(f"[{row['word']}]")
        print(f"Line {line_num}: {' '.join(tokens_display)}")

    # Show what flipped
    flipped = b_tokens[b_tokens['legal'] != b_tokens['legal2']]['word'].unique()
    print(f"\nTokens that FLIPPED legality: {len(flipped)}")
    print(f"Examples: {list(flipped)[:15]}")
