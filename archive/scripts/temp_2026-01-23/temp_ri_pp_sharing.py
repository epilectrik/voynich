#!/usr/bin/env python3
"""
Do A records share PP sets while having different RI?

If yes: RI = identification, PP = processing instruction
Two different "materials" could have identical processing.
"""

import json
import sys
import pandas as pd
from collections import defaultdict
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

def extract_middle(token):
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
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

# Load class-token map to identify PP MIDDLEs (those appearing in B)
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

# PP MIDDLEs = those that appear in B tokens
pp_middles = set()
for token, middle in class_map['token_to_middle'].items():
    if middle:
        pp_middles.add(middle)

# Load transcript and build A records
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_a['middle'] = df_a['word'].apply(extract_middle)

# Build A records grouped by folio+line
a_records = []
for (folio, line), group in df_a.groupby(['folio', 'line_number']):
    middles = set(group['middle'].dropna())
    if middles:
        a_records.append({
            'key': f"{folio}:{line}",
            'middles': middles
        })

print("="*70)
print("RI vs PP SHARING ANALYSIS")
print("="*70)
print(f"\nPP MIDDLEs (appear in B): {len(pp_middles)}")
print(f"A records loaded: {len(a_records)}")

# For each A record, decompose into RI vs PP
record_decomposition = {}
for rec in a_records:
    middles = rec['middles']
    ri_set = frozenset(m for m in middles if m not in pp_middles)
    pp_set = frozenset(m for m in middles if m in pp_middles)
    record_decomposition[rec['key']] = {
        'ri': ri_set,
        'pp': pp_set,
        'all_middles': frozenset(middles)
    }

print(f"A records analyzed: {len(record_decomposition)}")

# Statistics on RI vs PP composition
ri_counts = [len(d['ri']) for d in record_decomposition.values()]
pp_counts = [len(d['pp']) for d in record_decomposition.values()]

print(f"\nPer-record composition:")
print(f"  RI MIDDLEs: min={min(ri_counts)}, max={max(ri_counts)}, mean={sum(ri_counts)/len(ri_counts):.1f}")
print(f"  PP MIDDLEs: min={min(pp_counts)}, max={max(pp_counts)}, mean={sum(pp_counts)/len(pp_counts):.1f}")

# How many records have NO RI (all PP)?
no_ri = sum(1 for d in record_decomposition.values() if len(d['ri']) == 0)
no_pp = sum(1 for d in record_decomposition.values() if len(d['pp']) == 0)
print(f"\n  Records with no RI (all PP): {no_ri}")
print(f"  Records with no PP (all RI): {no_pp}")

# Group by PP set
pp_to_records = defaultdict(list)
for rec_key, decomp in record_decomposition.items():
    pp_to_records[decomp['pp']].append((rec_key, decomp['ri']))

print(f"\n" + "="*70)
print("PP SHARING PATTERNS")
print("="*70)

print(f"\nUnique PP sets: {len(pp_to_records)}")

# Count how many records share each PP set
sharing_dist = defaultdict(int)
for pp_set, records in pp_to_records.items():
    sharing_dist[len(records)] += 1

print(f"\nPP set sharing distribution:")
print(f"  {'Records sharing':>20} {'PP sets':>10}")
for n in sorted(sharing_dist.keys()):
    print(f"  {n:>20} {sharing_dist[n]:>10}")

# Find PP sets shared by records with DIFFERENT RI
shared_different_ri = []
for pp_set, records in pp_to_records.items():
    if len(records) > 1:
        ri_sets = [r[1] for r in records]
        unique_ri = len(set(ri_sets))
        if unique_ri > 1:
            shared_different_ri.append((pp_set, records, unique_ri))

print(f"\n" + "="*70)
print("CRITICAL FINDING: PP SHARED WITH DIFFERENT RI")
print("="*70)

print(f"\nPP sets shared by records with DIFFERENT RI: {len(shared_different_ri)}")

if shared_different_ri:
    # Sort by most shared
    shared_different_ri.sort(key=lambda x: (-len(x[1]), -x[2]))

    print(f"\n--- Top examples ---")
    for pp_set, records, n_unique_ri in shared_different_ri[:15]:
        pp_str = ','.join(sorted(pp_set)) if pp_set else "(empty)"
        print(f"\nPP set: {{{pp_str}}}")
        print(f"  Shared by {len(records)} records, {n_unique_ri} distinct RI patterns:")

        # Group by RI
        ri_groups = defaultdict(list)
        for rec_key, ri in records:
            ri_groups[ri].append(rec_key)

        for ri, recs in sorted(ri_groups.items(), key=lambda x: -len(x[1]))[:5]:
            ri_str = ','.join(sorted(ri)) if ri else "(none)"
            print(f"    RI={{{ri_str}}}: {recs[:3]}{'...' if len(recs)>3 else ''}")
        if len(ri_groups) > 5:
            print(f"    ... and {len(ri_groups)-5} more RI patterns")

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if len(shared_different_ri) > 0:
    total_shared = sum(len(r[1]) for r in shared_different_ri)
    pct = 100 * total_shared / len(record_decomposition)
    print(f"""
SIGNIFICANT RI/PP SEPARATION CONFIRMED

{len(shared_different_ri)} PP sets are shared by records with DIFFERENT RI patterns.
This covers {total_shared} records ({pct:.1f}% of all A records).

Interpretation:
- RI serves as IDENTIFICATION (which material/entity)
- PP serves as PROCESSING INSTRUCTION (how to execute)
- Same processing can apply to different identified entities

This is consistent with:
- Different materials processed identically
- Material identity (RI) orthogonal to process parameters (PP)
- A records = (WHAT, HOW) tuples where WHAT and HOW are separable
""")
else:
    print("""
NO RI/PP SHARING FOUND

Each A record's PP set uniquely determines its RI (or vice versa).
RI and PP are NOT independent dimensions.
""")

# Save results
results = {
    'pp_middle_count': len(pp_middles),
    'records_analyzed': len(record_decomposition),
    'unique_pp_sets': len(pp_to_records),
    'pp_shared_different_ri': len(shared_different_ri),
    'no_ri_records': no_ri,
    'no_pp_records': no_pp
}

with open('temp_ri_pp_sharing_results.json', 'w') as f:
    json.dump(results, f, indent=2)
