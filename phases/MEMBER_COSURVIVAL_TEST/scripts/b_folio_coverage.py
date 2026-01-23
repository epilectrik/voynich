"""Check how much of each B folio's vocabulary survives under A contexts."""
import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Load member survivors (strict interpretation)
with open(PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'member_survivors.json') as f:
    survivors = json.load(f)

# Load B folio tokens
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_b = df[df['language'] == 'B'].copy()

# Get unique tokens per B folio
b_folio_tokens = {}
for folio, group in df_b.groupby('folio'):
    b_folio_tokens[folio] = set(group['word'].dropna().astype(str))

print(f"B folios: {len(b_folio_tokens)}")
print(f"A records tested: {len(survivors['records'])}")

# For a sample A record, check overlap with each B folio
sample = survivors['records'][0]
legal_tokens = set(sample['surviving_tokens'])
print(f"\nSample A record: {sample['a_record']}")
print(f"Legal B tokens: {len(legal_tokens)}")

# Check each B folio
overlaps = []
for b_folio, b_tokens in b_folio_tokens.items():
    overlap = len(b_tokens & legal_tokens)
    total = len(b_tokens)
    pct = overlap / total * 100 if total > 0 else 0
    overlaps.append((b_folio, overlap, total, pct))

overlaps.sort(key=lambda x: x[3])
print(f"\nB folio coverage under this A record:")
print(f"Lowest 5:")
for f, o, t, p in overlaps[:5]:
    print(f"  {f}: {o}/{t} tokens legal ({p:.1f}%)")
print(f"Highest 5:")
for f, o, t, p in overlaps[-5:]:
    print(f"  {f}: {o}/{t} tokens legal ({p:.1f}%)")
print(f"\nMean coverage: {sum(x[3] for x in overlaps)/len(overlaps):.1f}%")

# Now check across ALL A records - what's the range?
print("\n" + "=" * 60)
print("COVERAGE DISTRIBUTION ACROSS ALL A RECORDS")
print("=" * 60)

all_coverages = []
for rec in survivors['records']:
    legal = set(rec['surviving_tokens'])
    for b_folio, b_tokens in b_folio_tokens.items():
        overlap = len(b_tokens & legal)
        total = len(b_tokens)
        pct = overlap / total * 100 if total > 0 else 0
        all_coverages.append(pct)

print(f"Total (A record, B folio) pairs: {len(all_coverages)}")
print(f"Min coverage: {min(all_coverages):.1f}%")
print(f"Max coverage: {max(all_coverages):.1f}%")
print(f"Mean coverage: {sum(all_coverages)/len(all_coverages):.1f}%")

# How many pairs have <10% coverage?
low = sum(1 for c in all_coverages if c < 10)
print(f"\nPairs with <10% coverage: {low} ({low/len(all_coverages)*100:.1f}%)")
