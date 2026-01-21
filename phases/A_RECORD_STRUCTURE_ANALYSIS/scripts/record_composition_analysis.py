#!/usr/bin/env python3
"""
Analyze Currier A record composition by token type.

Token types:
- RI: Registry-Internal (A-exclusive)
- AZC-Med: AZC-Mediated (true pipeline)
- BN: B-Native Overlap (B vocabulary with A incidence)
"""

import pandas as pd
import statistics
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load transcript
df = pd.read_csv(DATA_PATH, sep='\t')
df = df[df['transcriber'] == 'H']  # PRIMARY track only

# Morphology parsing
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

AZC_FOLIOS = ['f67r1', 'f67r2', 'f67v1', 'f67v2', 'f68r1', 'f68r2', 'f68r3',
              'f68v1', 'f68v2', 'f68v3', 'f69r1', 'f69r2', 'f69v1', 'f69v2',
              'f70r1', 'f70r2', 'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1',
              'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v']

def extract_middle(token):
    """Extract MIDDLE from token."""
    if pd.isna(token):
        return None
    token = str(token)
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None
    remainder = token[len(prefix):]
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break
    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
    if middle == '':
        middle = '_EMPTY_'
    return middle

# Extract MIDDLEs by corpus segment
df['middle'] = df['word'].apply(extract_middle)

df_a = df[df['language'] == 'A']
df_b = df[df['language'] == 'B']
df_azc = df[df['folio'].isin(AZC_FOLIOS)]

a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
azc_middles = set(df_azc['middle'].dropna().unique())

# Classify
ri_middles = a_middles - b_middles
shared_middles = a_middles & b_middles
azc_mediated = shared_middles & azc_middles
b_native = shared_middles - azc_middles

print("=" * 70)
print("CURRIER A RECORD COMPOSITION ANALYSIS")
print("=" * 70)
print()

print("=== MIDDLE CLASSIFICATION ===")
print(f"RI (A-exclusive): {len(ri_middles)}")
print(f"AZC-Mediated (pipeline): {len(azc_mediated)}")
print(f"B-Native Overlap: {len(b_native)}")
print()

# Group by folio and line to get records
records = []
for (folio, line_num), group in df_a.groupby(['folio', 'line_number']):
    middles = group['middle'].tolist()
    total = len(middles)

    ri_count = sum(1 for m in middles if m in ri_middles)
    azc_count = sum(1 for m in middles if m in azc_mediated)
    bn_count = sum(1 for m in middles if m in b_native)
    unknown = sum(1 for m in middles if m is None or (m not in ri_middles and m not in azc_mediated and m not in b_native))

    records.append({
        'folio': folio,
        'line': line_num,
        'total': total,
        'ri': ri_count,
        'azc': azc_count,
        'bn': bn_count,
        'unknown': unknown,
        'ri_pct': ri_count / total * 100 if total > 0 else 0,
        'azc_pct': azc_count / total * 100 if total > 0 else 0,
        'bn_pct': bn_count / total * 100 if total > 0 else 0,
    })

totals = [r['total'] for r in records]
ri_counts = [r['ri'] for r in records]
azc_counts = [r['azc'] for r in records]
bn_counts = [r['bn'] for r in records]

print("=== RECORD SIZE STATISTICS ===")
print(f"Total records: {len(records)}")
print(f"Mean tokens per record: {statistics.mean(totals):.1f}")
print(f"Median tokens: {statistics.median(totals):.0f}")
print(f"Min: {min(totals)}, Max: {max(totals)}")
print(f"Std dev: {statistics.stdev(totals):.1f}")
print()

print("=== TOKEN COUNT PER RECORD (by type) ===")
print(f"RI tokens: mean={statistics.mean(ri_counts):.2f}, median={statistics.median(ri_counts):.0f}, max={max(ri_counts)}")
print(f"AZC-Med tokens: mean={statistics.mean(azc_counts):.2f}, median={statistics.median(azc_counts):.0f}, max={max(azc_counts)}")
print(f"B-Native tokens: mean={statistics.mean(bn_counts):.2f}, median={statistics.median(bn_counts):.0f}, max={max(bn_counts)}")
print()

ri_pcts = [r['ri_pct'] for r in records]
azc_pcts = [r['azc_pct'] for r in records]
bn_pcts = [r['bn_pct'] for r in records]

print("=== PERCENTAGE COMPOSITION (per record) ===")
print(f"RI %: mean={statistics.mean(ri_pcts):.1f}%, median={statistics.median(ri_pcts):.0f}%")
print(f"AZC-Med %: mean={statistics.mean(azc_pcts):.1f}%, median={statistics.median(azc_pcts):.0f}%")
print(f"B-Native %: mean={statistics.mean(bn_pcts):.1f}%, median={statistics.median(bn_pcts):.0f}%")
print()

has_ri = sum(1 for r in records if r['ri'] > 0)
has_azc = sum(1 for r in records if r['azc'] > 0)
has_bn = sum(1 for r in records if r['bn'] > 0)

print("=== TOKEN TYPE PRESENCE ===")
print(f"Records with ANY RI: {has_ri} ({has_ri/len(records)*100:.1f}%)")
print(f"Records with ANY AZC-Med: {has_azc} ({has_azc/len(records)*100:.1f}%)")
print(f"Records with ANY B-Native: {has_bn} ({has_bn/len(records)*100:.1f}%)")
print()

combos = Counter()
for r in records:
    key = (r['ri'] > 0, r['azc'] > 0, r['bn'] > 0)
    combos[key] += 1

print("=== COMPOSITION COMBINATIONS ===")
print("(has_RI, has_AZC-Med, has_BN) -> count")
for (ri, azc, bn), count in sorted(combos.items(), key=lambda x: -x[1]):
    pct = count / len(records) * 100
    label = f"{'RI' if ri else '--':>2} {'AZC' if azc else '---':>3} {'BN' if bn else '--':>2}"
    print(f"  {label}: {count:4d} ({pct:5.1f}%)")
print()

print("=== COMPOSITION BY RECORD SIZE ===")
size_bins = [(1, 1), (2, 3), (4, 6), (7, 10), (11, 20), (21, 50), (51, 200)]
for lo, hi in size_bins:
    subset = [r for r in records if lo <= r['total'] <= hi]
    if subset:
        mean_ri = statistics.mean([r['ri_pct'] for r in subset])
        mean_azc = statistics.mean([r['azc_pct'] for r in subset])
        mean_bn = statistics.mean([r['bn_pct'] for r in subset])
        print(f"Size {lo:2d}-{hi:3d} ({len(subset):4d} records): RI={mean_ri:4.1f}%  AZC={mean_azc:4.1f}%  BN={mean_bn:4.1f}%")
print()

pure_ri = [r for r in records if r['ri'] == r['total'] and r['total'] > 0]
pure_azc = [r for r in records if r['azc'] == r['total'] and r['total'] > 0]
pure_bn = [r for r in records if r['bn'] == r['total'] and r['total'] > 0]
no_ri = [r for r in records if r['ri'] == 0]

print("=== PURE TYPE RECORDS ===")
print(f"Pure RI (100% RI): {len(pure_ri)} records")
print(f"Pure AZC-Med (100%): {len(pure_azc)} records")
print(f"Pure B-Native (100%): {len(pure_bn)} records")
print(f"No RI at all: {len(no_ri)} ({len(no_ri)/len(records)*100:.1f}%)")
print()

print("=== MINIMUM VIABLE RECORDS ===")
single = [r for r in records if r['total'] == 1]
print(f"Single-token records: {len(single)}")
if single:
    sri = sum(1 for r in single if r['ri'] == 1)
    sazc = sum(1 for r in single if r['azc'] == 1)
    sbn = sum(1 for r in single if r['bn'] == 1)
    sunk = sum(1 for r in single if r['unknown'] == 1)
    print(f"  Pure RI: {sri}")
    print(f"  Pure AZC-Med: {sazc}")
    print(f"  Pure B-Native: {sbn}")
    print(f"  Unknown/no-prefix: {sunk}")
