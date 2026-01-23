"""Test strict interpretation: only A-record MIDDLEs are legal."""
import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

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

df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_a['middle'] = df_a['word'].apply(extract_middle)

with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

token_to_middle = class_map['token_to_middle']
b_tokens = set(class_map['token_to_class'].keys())

print("=" * 70)
print("STRICT INTERPRETATION: Only A-record MIDDLEs are legal")
print("=" * 70)

# Test multiple A records
results = []
for (folio, line), group in list(df_a.groupby(['folio', 'line_number']))[:100]:
    a_middles = set(group['middle'].dropna())
    if not a_middles:
        continue

    # STRICT: Only MIDDLEs in the A record are legal
    legal_middles = a_middles

    survivors = 0
    for token in b_tokens:
        token_middle = token_to_middle.get(token)
        if token_middle is None:  # atomic
            survivors += 1
        elif token_middle in legal_middles:
            survivors += 1

    results.append({
        'record': f"{folio}:{line}",
        'a_middles': len(a_middles),
        'survivors': survivors,
        'rate': survivors / len(b_tokens) * 100
    })

print(f"\nTested {len(results)} A records")
print(f"\nSurvivor statistics (STRICT - only A-record MIDDLEs legal):")
survivors = [r['survivors'] for r in results]
print(f"  Min: {min(survivors)}")
print(f"  Max: {max(survivors)}")
print(f"  Mean: {sum(survivors)/len(survivors):.1f}")

print(f"\nSample results:")
for r in results[:10]:
    print(f"  {r['record']}: {r['a_middles']} MIDDLEs -> {r['survivors']} survivors ({r['rate']:.1f}%)")

# Compare with original (union) approach
print("\n" + "=" * 70)
print("COMPARISON: What if only ~20-30 tokens should survive?")
print("=" * 70)
print(f"If only A-record MIDDLEs are legal:")
print(f"  Average survivors: {sum(survivors)/len(survivors):.1f} / 480")
print(f"  This is {sum(survivors)/len(survivors)/480*100:.1f}% of B vocabulary")
