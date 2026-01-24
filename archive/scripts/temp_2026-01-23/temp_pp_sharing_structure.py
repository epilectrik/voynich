#!/usr/bin/env python3
"""
Analyze structural characteristics of records sharing PP but differing in RI.

Questions:
1. Do they share PREFIX patterns?
2. Do they share SUFFIX patterns?
3. Are they from similar folios/sections?
4. Is there any systematic structure in the RI dimension?
"""

import json
import sys
import pandas as pd
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_morphology(token):
    """Extract PREFIX, MIDDLE, SUFFIX from token."""
    if pd.isna(token):
        return None, None, None
    token = str(token)
    if not token.strip():
        return None, None, None

    prefix = None
    suffix = None
    remainder = token

    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            prefix = p
            remainder = remainder[len(p):]
            break

    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    middle = remainder if remainder else None
    return prefix, middle, suffix

# Load class-token map to identify PP MIDDLEs
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

pp_middles = set()
for token, middle in class_map['token_to_middle'].items():
    if middle:
        pp_middles.add(middle)

# Load transcript and build A records with full morphology
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()

# Extract full morphology for each token
morphologies = df_a['word'].apply(lambda w: extract_morphology(w))
df_a['prefix'] = morphologies.apply(lambda x: x[0])
df_a['middle'] = morphologies.apply(lambda x: x[1])
df_a['suffix'] = morphologies.apply(lambda x: x[2])

# Build A records with all morphology info
a_records = []
for (folio, line), group in df_a.groupby(['folio', 'line_number']):
    middles = set(group['middle'].dropna())
    prefixes = set(group['prefix'].dropna())
    suffixes = set(group['suffix'].dropna())
    tokens = list(group['word'].dropna())

    if middles:
        ri_set = frozenset(m for m in middles if m not in pp_middles)
        pp_set = frozenset(m for m in middles if m in pp_middles)

        a_records.append({
            'key': f"{folio}:{line}",
            'folio': folio,
            'middles': middles,
            'ri': ri_set,
            'pp': pp_set,
            'prefixes': prefixes,
            'suffixes': suffixes,
            'tokens': tokens
        })

# Group by PP set
pp_to_records = defaultdict(list)
for rec in a_records:
    pp_to_records[rec['pp']].append(rec)

# Find PP sets shared by records with different RI
shared_groups = []
for pp_set, records in pp_to_records.items():
    if len(records) > 1:
        ri_sets = [r['ri'] for r in records]
        unique_ri = len(set(ri_sets))
        if unique_ri > 1:
            shared_groups.append((pp_set, records))

print("="*70)
print("STRUCTURAL ANALYSIS OF PP-SHARING RECORD GROUPS")
print("="*70)
print(f"\nPP sets shared by records with different RI: {len(shared_groups)}")

# Analyze PREFIX patterns within groups
print("\n" + "="*70)
print("PREFIX ANALYSIS")
print("="*70)

prefix_coherence = []
for pp_set, records in shared_groups:
    # Get all prefixes used across records in this group
    all_prefixes = [p for r in records for p in r['prefixes']]
    prefix_counts = Counter(all_prefixes)

    # How concentrated is the prefix distribution?
    if len(prefix_counts) > 0:
        most_common = prefix_counts.most_common(1)[0]
        concentration = most_common[1] / len(all_prefixes) if all_prefixes else 0
        prefix_coherence.append({
            'pp': pp_set,
            'n_records': len(records),
            'dominant_prefix': most_common[0],
            'concentration': concentration,
            'unique_prefixes': len(prefix_counts),
            'prefix_dist': dict(prefix_counts)
        })

# Sort by concentration
prefix_coherence.sort(key=lambda x: -x['concentration'])

print(f"\nPREFIX concentration in PP-sharing groups:")
print(f"{'PP Set':30} {'Records':>8} {'Dominant':>10} {'Conc.':>8} {'Unique':>8}")
print("-" * 70)

high_coherence = 0
for pc in prefix_coherence[:20]:
    pp_str = ','.join(sorted(pc['pp'])) if pc['pp'] else '(empty)'
    if len(pp_str) > 28:
        pp_str = pp_str[:25] + '...'
    print(f"{pp_str:30} {pc['n_records']:>8} {pc['dominant_prefix'] or 'None':>10} {pc['concentration']:>7.1%} {pc['unique_prefixes']:>8}")
    if pc['concentration'] > 0.5:
        high_coherence += 1

print(f"\nGroups with >50% PREFIX concentration: {high_coherence}/{len(prefix_coherence)}")

# Analyze SUFFIX patterns within groups
print("\n" + "="*70)
print("SUFFIX ANALYSIS")
print("="*70)

suffix_coherence = []
for pp_set, records in shared_groups:
    all_suffixes = [s for r in records for s in r['suffixes']]
    suffix_counts = Counter(all_suffixes)

    if len(suffix_counts) > 0:
        most_common = suffix_counts.most_common(1)[0]
        concentration = most_common[1] / len(all_suffixes) if all_suffixes else 0
        suffix_coherence.append({
            'pp': pp_set,
            'n_records': len(records),
            'dominant_suffix': most_common[0],
            'concentration': concentration,
            'unique_suffixes': len(suffix_counts),
            'suffix_dist': dict(suffix_counts)
        })

suffix_coherence.sort(key=lambda x: -x['concentration'])

print(f"\nSUFFIX concentration in PP-sharing groups:")
print(f"{'PP Set':30} {'Records':>8} {'Dominant':>10} {'Conc.':>8} {'Unique':>8}")
print("-" * 70)

high_suffix_coherence = 0
for sc in suffix_coherence[:20]:
    pp_str = ','.join(sorted(sc['pp'])) if sc['pp'] else '(empty)'
    if len(pp_str) > 28:
        pp_str = pp_str[:25] + '...'
    print(f"{pp_str:30} {sc['n_records']:>8} {sc['dominant_suffix'] or 'None':>10} {sc['concentration']:>7.1%} {sc['unique_suffixes']:>8}")
    if sc['concentration'] > 0.5:
        high_suffix_coherence += 1

print(f"\nGroups with >50% SUFFIX concentration: {high_suffix_coherence}/{len(suffix_coherence)}")

# Analyze FOLIO patterns within groups
print("\n" + "="*70)
print("FOLIO LOCALITY ANALYSIS")
print("="*70)

folio_coherence = []
for pp_set, records in shared_groups:
    folios = [r['folio'] for r in records]
    folio_counts = Counter(folios)

    # Get unique folios
    unique_folios = len(folio_counts)
    # Are records from same folio?
    max_same_folio = folio_counts.most_common(1)[0][1] if folio_counts else 0
    same_folio_pct = max_same_folio / len(records) if records else 0

    folio_coherence.append({
        'pp': pp_set,
        'n_records': len(records),
        'unique_folios': unique_folios,
        'max_same_folio': max_same_folio,
        'same_folio_pct': same_folio_pct,
        'folios': list(folio_counts.keys())[:5]
    })

# Sort by folio locality
folio_coherence.sort(key=lambda x: -x['same_folio_pct'])

print(f"\nFOLIO locality in PP-sharing groups:")
print(f"{'PP Set':30} {'Records':>8} {'Folios':>8} {'Same%':>8} {'Examples'}")
print("-" * 70)

same_folio_groups = 0
for fc in folio_coherence[:20]:
    pp_str = ','.join(sorted(fc['pp'])) if fc['pp'] else '(empty)'
    if len(pp_str) > 28:
        pp_str = pp_str[:25] + '...'
    folio_str = ','.join(fc['folios'][:3])
    print(f"{pp_str:30} {fc['n_records']:>8} {fc['unique_folios']:>8} {fc['same_folio_pct']:>7.1%} {folio_str}")
    if fc['same_folio_pct'] > 0.5:
        same_folio_groups += 1

print(f"\nGroups with >50% same-folio: {same_folio_groups}/{len(folio_coherence)}")

# Deep dive: The empty PP group (pure RI records)
print("\n" + "="*70)
print("DEEP DIVE: EMPTY PP GROUP (Pure RI Records)")
print("="*70)

empty_pp_records = pp_to_records[frozenset()]
if empty_pp_records:
    print(f"\nRecords with empty PP (pure RI): {len(empty_pp_records)}")

    # What prefixes do they use?
    all_prefixes = Counter()
    all_suffixes = Counter()
    all_ri = Counter()

    for r in empty_pp_records:
        all_prefixes.update(r['prefixes'])
        all_suffixes.update(r['suffixes'])
        all_ri.update(r['ri'])

    print(f"\nPREFIX distribution:")
    for p, c in all_prefixes.most_common(10):
        print(f"  {p}: {c}")

    print(f"\nSUFFIX distribution:")
    for s, c in all_suffixes.most_common(10):
        print(f"  {s}: {c}")

    print(f"\nRI MIDDLE distribution (top 15):")
    for m, c in all_ri.most_common(15):
        print(f"  {m}: {c}")

    print(f"\nFolios represented: {len(set(r['folio'] for r in empty_pp_records))}")
    print(f"Sample records:")
    for r in empty_pp_records[:10]:
        print(f"  {r['key']}: RI={set(r['ri'])}, PREFIX={r['prefixes']}, tokens={r['tokens'][:3]}")

# Statistical summary
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)

avg_prefix_conc = sum(pc['concentration'] for pc in prefix_coherence) / len(prefix_coherence) if prefix_coherence else 0
avg_suffix_conc = sum(sc['concentration'] for sc in suffix_coherence) / len(suffix_coherence) if suffix_coherence else 0
avg_folio_loc = sum(fc['same_folio_pct'] for fc in folio_coherence) / len(folio_coherence) if folio_coherence else 0

print(f"""
Average PREFIX concentration: {avg_prefix_conc:.1%}
Average SUFFIX concentration: {avg_suffix_conc:.1%}
Average folio locality: {avg_folio_loc:.1%}

Groups with >50% PREFIX coherence: {high_coherence}/{len(prefix_coherence)} ({100*high_coherence/len(prefix_coherence):.1f}%)
Groups with >50% SUFFIX coherence: {high_suffix_coherence}/{len(suffix_coherence)} ({100*high_suffix_coherence/len(suffix_coherence):.1f}%)
Groups with >50% folio locality: {same_folio_groups}/{len(folio_coherence)} ({100*same_folio_groups/len(folio_coherence):.1f}%)
""")

# Interpretation
print("="*70)
print("INTERPRETATION")
print("="*70)

if avg_prefix_conc > 0.5 or high_coherence > len(prefix_coherence) * 0.3:
    print("""
PREFIX COHERENCE DETECTED in PP-sharing groups.
Records sharing the same PP tend to use similar PREFIXES.
This suggests PREFIX may encode a dimension correlated with PP (capacity).
""")
elif avg_suffix_conc > 0.5 or high_suffix_coherence > len(suffix_coherence) * 0.3:
    print("""
SUFFIX COHERENCE DETECTED in PP-sharing groups.
Records sharing the same PP tend to use similar SUFFIXES.
This suggests SUFFIX may encode a dimension correlated with PP.
""")
elif avg_folio_loc > 0.5 or same_folio_groups > len(folio_coherence) * 0.3:
    print("""
FOLIO LOCALITY DETECTED in PP-sharing groups.
Records sharing the same PP tend to be from the same folio.
This suggests PP is folio-local (manuscript organization effect).
""")
else:
    print("""
NO STRONG STRUCTURAL PATTERN DETECTED.

Records sharing the same PP show:
- Diverse PREFIXES (no systematic grouping)
- Diverse SUFFIXES (no systematic grouping)
- Dispersed across folios (not localized)

This suggests RI (discrimination coordinates) is orthogonal to
morphological structure. The RI dimension provides discrimination
without systematic PREFIX/SUFFIX/FOLIO correlation.
""")
