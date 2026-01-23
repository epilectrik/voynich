"""Verify the survivor logic with a specific example."""
import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

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
    if not token.strip(): return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None

# Load data
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

df_a = df[df['language'] == 'A'].copy()
df_azc = df[df['language'].isna()].copy()

df_a['middle'] = df_a['word'].apply(extract_middle)
df_azc['middle'] = df_azc['word'].apply(extract_middle)

# Pick a specific A record
example_folio = 'f1r'
example_line = '1'

a_tokens = df_a[(df_a['folio'] == example_folio) & (df_a['line_number'].astype(str) == example_line)]
print(f"=== A RECORD: {example_folio}:{example_line} ===")
print(f"Tokens: {a_tokens['word'].tolist()}")
a_middles = set(a_tokens['middle'].dropna())
print(f"MIDDLEs in this A record: {a_middles}")
print(f"Count: {len(a_middles)}")

# Find matching AZC folios
azc_middles_by_folio = {}
for folio, group in df_azc.groupby('folio'):
    azc_middles_by_folio[folio] = set(group['middle'].dropna())

print(f"\n=== AZC FOLIOS ===")
print(f"Total AZC folios: {len(azc_middles_by_folio)}")

matching_folios = []
for azc_folio, azc_mids in azc_middles_by_folio.items():
    overlap = a_middles & azc_mids
    if overlap:
        matching_folios.append((azc_folio, len(azc_mids), overlap))

print(f"AZC folios matching this A record: {len(matching_folios)}")
for f, size, overlap in matching_folios[:5]:
    print(f"  {f}: {size} MIDDLEs, overlap: {overlap}")

# Compute legal MIDDLEs (union of matched folios)
legal_middles = set()
for azc_folio, _, _ in matching_folios:
    legal_middles |= azc_middles_by_folio[azc_folio]

print(f"\n=== LEGAL MIDDLEs (union of matched AZC folios) ===")
print(f"Count: {len(legal_middles)}")

# Now check B tokens
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

token_to_middle = class_map['token_to_middle']
b_tokens = set(class_map['token_to_class'].keys())

print(f"\n=== B INSTRUCTION TOKENS ===")
print(f"Total B tokens: {len(b_tokens)}")

# Count survivors
atomic_survivors = []
middle_survivors = []
filtered_out = []

for token in sorted(b_tokens):
    token_middle = token_to_middle.get(token)
    if token_middle is None:
        atomic_survivors.append(token)
    elif token_middle in legal_middles:
        middle_survivors.append(token)
    else:
        filtered_out.append((token, token_middle))

print(f"\n=== SURVIVORS ===")
print(f"Atomic (MIDDLE=None, always survive): {len(atomic_survivors)}")
print(f"  Tokens: {atomic_survivors}")
print(f"Middle-based survivors: {len(middle_survivors)}")
print(f"FILTERED OUT: {len(filtered_out)}")

print(f"\n=== SUMMARY ===")
print(f"Survive: {len(atomic_survivors) + len(middle_survivors)} / {len(b_tokens)}")
print(f"Filtered: {len(filtered_out)} / {len(b_tokens)}")

if filtered_out:
    print(f"\nSample filtered tokens and their MIDDLEs:")
    for token, mid in filtered_out[:20]:
        print(f"  {token}: MIDDLE='{mid}'")

# Check: are the filtered MIDDLEs in the A record?
filtered_middles = set(mid for _, mid in filtered_out)
print(f"\n=== KEY QUESTION ===")
print(f"Filtered MIDDLEs that ARE in A record: {filtered_middles & a_middles}")
print(f"Filtered MIDDLEs NOT in A record: {filtered_middles - a_middles}")
