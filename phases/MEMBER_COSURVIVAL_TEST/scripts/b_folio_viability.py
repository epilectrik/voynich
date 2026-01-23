"""Analyze B folio viability: what's the atomic core vs context-dependent content?"""
import json
import pandas as pd
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Load class-token map to get atomic tokens
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

token_to_middle = class_map['token_to_middle']

# Atomic tokens = MIDDLE is None
atomic_tokens = set(t for t, m in token_to_middle.items() if m is None)
print(f"Atomic tokens (always legal): {len(atomic_tokens)}")
print(f"  {sorted(atomic_tokens)}")

# Load B folio tokens
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_b = df[df['language'] == 'B'].copy()

print(f"\nTotal B tokens: {len(df_b)}")

# Analyze each B folio
print("\n" + "=" * 70)
print("B FOLIO ATOMIC CORE ANALYSIS")
print("=" * 70)

results = []
for folio, group in df_b.groupby('folio'):
    tokens = group['word'].dropna().astype(str).tolist()
    total = len(tokens)

    # Count atomic vs decomposable
    atomic_count = sum(1 for t in tokens if t in atomic_tokens)
    decomposable_count = total - atomic_count

    # Unique tokens
    unique_tokens = set(tokens)
    unique_atomic = len(unique_tokens & atomic_tokens)
    unique_decomposable = len(unique_tokens) - unique_atomic

    atomic_pct = atomic_count / total * 100 if total > 0 else 0

    results.append({
        'folio': folio,
        'total_tokens': total,
        'atomic_tokens': atomic_count,
        'atomic_pct': atomic_pct,
        'unique_total': len(unique_tokens),
        'unique_atomic': unique_atomic,
        'unique_decomposable': unique_decomposable
    })

# Sort by atomic percentage
results.sort(key=lambda x: x['atomic_pct'])

print("\nFolios with LOWEST atomic content (most context-dependent):")
for r in results[:10]:
    print(f"  {r['folio']}: {r['atomic_pct']:.1f}% atomic ({r['atomic_tokens']}/{r['total_tokens']} tokens)")

print("\nFolios with HIGHEST atomic content (most always-legal):")
for r in results[-10:]:
    print(f"  {r['folio']}: {r['atomic_pct']:.1f}% atomic ({r['atomic_tokens']}/{r['total_tokens']} tokens)")

# Summary stats
atomic_pcts = [r['atomic_pct'] for r in results]
print(f"\n" + "-" * 70)
print("SUMMARY")
print("-" * 70)
print(f"Mean atomic %: {sum(atomic_pcts)/len(atomic_pcts):.1f}%")
print(f"Min atomic %: {min(atomic_pcts):.1f}%")
print(f"Max atomic %: {max(atomic_pcts):.1f}%")

# How many folios have <5% atomic content?
low_atomic = sum(1 for p in atomic_pcts if p < 5)
print(f"\nFolios with <5% atomic: {low_atomic} ({low_atomic/len(results)*100:.1f}%)")

# Key question: what's the minimum viable folio?
print("\n" + "=" * 70)
print("VIABILITY ANALYSIS")
print("=" * 70)
print("If stripped to atomic core only, a folio has:")

for r in results[:5]:
    print(f"  {r['folio']}: {r['unique_atomic']} unique atomic tokens out of {r['unique_total']} total")
    print(f"    -> {r['atomic_tokens']} token occurrences would remain")

# Load member survivors to see variance
with open(PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'member_survivors.json') as f:
    survivors = json.load(f)

# For the lowest-atomic folio, what's the coverage range across A records?
lowest_folio = results[0]['folio']
lowest_folio_tokens = set(df_b[df_b['folio'] == lowest_folio]['word'].dropna().astype(str))

coverages = []
for rec in survivors['records']:
    legal = set(rec['surviving_tokens'])
    overlap = len(lowest_folio_tokens & legal)
    pct = overlap / len(lowest_folio_tokens) * 100
    coverages.append(pct)

print(f"\n{lowest_folio} coverage across all A records:")
print(f"  Min: {min(coverages):.1f}%")
print(f"  Max: {max(coverages):.1f}%")
print(f"  Mean: {sum(coverages)/len(coverages):.1f}%")
print(f"  Atomic floor: {results[0]['atomic_pct']:.1f}%")
