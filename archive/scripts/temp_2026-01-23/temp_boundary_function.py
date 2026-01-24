#!/usr/bin/env python3
"""
What are boundary MIDDLEs actually doing?

They're PP-like in structure but A-exclusive in function.
Let's investigate their role:
1. What PP do they co-occur with in the same record?
2. What PREFIX patterns do they use?
3. What line positions do they appear in?
4. Are they markers/modifiers for something?
"""

import json
import sys
import pandas as pd
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Morphology
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_morphology(token):
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

# Load PP MIDDLEs
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

pp_middles = set()
for token, middle in class_map['token_to_middle'].items():
    if middle:
        pp_middles.add(middle)

# Load A tokens
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()

# Extract morphology
morph = df_a['word'].apply(extract_morphology)
df_a['prefix'] = morph.apply(lambda x: x[0])
df_a['middle'] = morph.apply(lambda x: x[1])
df_a['suffix'] = morph.apply(lambda x: x[2])

# Classify MIDDLEs
df_a['middle_type'] = df_a['middle'].apply(
    lambda m: 'PP' if m in pp_middles else ('RI' if m else None)
)

# Identify boundary MIDDLEs (short repeating RI)
ri_counts = df_a[df_a['middle_type'] == 'RI']['middle'].value_counts()
short_repeating = set(m for m, c in ri_counts.items() if c > 1 and len(m) <= 3)

df_a['is_boundary'] = df_a['middle'].isin(short_repeating)

print("="*70)
print("BOUNDARY MIDDLE FUNCTION ANALYSIS")
print("="*70)

top_boundary = ['sh', 'ko', 'to', 'yd', 'p', 'ro', 'ls', 'ld', 'yk', 'da']

# 1. What FULL TOKENS contain boundary MIDDLEs?
print(f"\n--- FULL TOKENS WITH BOUNDARY MIDDLEs ---")
for middle in top_boundary[:7]:
    tokens = df_a[df_a['middle'] == middle]['word'].value_counts()
    print(f"\n  MIDDLE '{middle}' appears in tokens:")
    for tok, count in tokens.head(8).items():
        row = df_a[df_a['word'] == tok].iloc[0]
        print(f"    {tok} ({count}x) - PREFIX={row['prefix']}, SUFFIX={row['suffix']}")

# 2. PREFIX patterns for boundary MIDDLEs
print(f"\n" + "="*70)
print("PREFIX PATTERNS FOR BOUNDARY MIDDLEs")
print("="*70)

boundary_tokens = df_a[df_a['is_boundary']]
boundary_prefixes = boundary_tokens['prefix'].value_counts(dropna=False)

print(f"\nPREFIX distribution for boundary MIDDLE tokens:")
print(f"{'PREFIX':>10} {'Count':>8} {'%':>8}")
print("-" * 30)
for prefix, count in boundary_prefixes.head(15).items():
    pct = count / len(boundary_tokens) * 100
    print(f"{str(prefix):>10} {count:>8} {pct:>7.1f}%")

# Compare to PP PREFIX distribution
pp_tokens = df_a[df_a['middle_type'] == 'PP']
pp_prefixes = pp_tokens['prefix'].value_counts(dropna=False)

print(f"\nFor comparison - PP token PREFIX distribution:")
print(f"{'PREFIX':>10} {'Count':>8} {'%':>8}")
print("-" * 30)
for prefix, count in pp_prefixes.head(10).items():
    pct = count / len(pp_tokens) * 100
    print(f"{str(prefix):>10} {count:>8} {pct:>7.1f}%")

# 3. Line position analysis
print(f"\n" + "="*70)
print("LINE POSITION ANALYSIS")
print("="*70)

# Get position within line for each token
def get_line_position(group):
    group = group.sort_values('placement')
    positions = list(range(len(group)))
    return pd.Series(positions, index=group.index)

df_a['line_pos'] = df_a.groupby(['folio', 'line_number']).apply(
    lambda g: pd.Series(range(len(g)), index=g.index)
).reset_index(level=[0,1], drop=True)

# Line lengths
line_lengths = df_a.groupby(['folio', 'line_number']).size()
df_a['line_length'] = df_a.apply(lambda r: line_lengths.get((r['folio'], r['line_number']), 1), axis=1)
df_a['rel_pos'] = df_a['line_pos'] / df_a['line_length']

# Position distribution for boundary vs PP vs singleton RI
singleton_ri = set(m for m, c in ri_counts.items() if c == 1)
df_a['ri_type'] = df_a.apply(
    lambda r: 'BOUNDARY' if r['middle'] in short_repeating else
              ('SINGLETON_RI' if r['middle'] in singleton_ri else
               ('PP' if r['middle'] in pp_middles else 'OTHER')),
    axis=1
)

print(f"\nMean relative position (0=start, 1=end):")
for ri_type in ['PP', 'BOUNDARY', 'SINGLETON_RI']:
    subset = df_a[df_a['ri_type'] == ri_type]
    if len(subset) > 0:
        mean_pos = subset['rel_pos'].mean()
        print(f"  {ri_type:15}: {mean_pos:.3f} (n={len(subset)})")

# Line-initial and line-final rates
print(f"\nLine-initial rate (position 0):")
for ri_type in ['PP', 'BOUNDARY', 'SINGLETON_RI']:
    subset = df_a[df_a['ri_type'] == ri_type]
    if len(subset) > 0:
        initial_rate = (subset['line_pos'] == 0).mean() * 100
        print(f"  {ri_type:15}: {initial_rate:.1f}%")

print(f"\nLine-final rate (last position):")
for ri_type in ['PP', 'BOUNDARY', 'SINGLETON_RI']:
    subset = df_a[df_a['ri_type'] == ri_type]
    if len(subset) > 0:
        final_rate = (subset['line_pos'] == subset['line_length'] - 1).mean() * 100
        print(f"  {ri_type:15}: {final_rate:.1f}%")

# 4. Co-occurrence with PP in same record
print(f"\n" + "="*70)
print("CO-OCCURRENCE: BOUNDARY + PP IN SAME RECORD")
print("="*70)

# Build records
records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna()),
    'is_boundary': 'any'
}).reset_index()

records['has_boundary'] = records['is_boundary']
records['pp_middles'] = records['middle'].apply(lambda ms: ms & pp_middles)
records['pp_count'] = records['pp_middles'].apply(len)

records_with_boundary = records[records['has_boundary']]
records_without_boundary = records[~records['has_boundary']]

print(f"\nRecords with boundary MIDDLEs: {len(records_with_boundary)}")
print(f"Records without boundary MIDDLEs: {len(records_without_boundary)}")

print(f"\nMean PP count per record:")
print(f"  With boundary: {records_with_boundary['pp_count'].mean():.2f}")
print(f"  Without boundary: {records_without_boundary['pp_count'].mean():.2f}")

# Which PP MIDDLEs co-occur most with boundary?
pp_cooccurrence = Counter()
for _, row in records_with_boundary.iterrows():
    for pp in row['pp_middles']:
        pp_cooccurrence[pp] += 1

print(f"\nPP MIDDLEs that most often co-occur with boundary MIDDLEs:")
for pp, count in pp_cooccurrence.most_common(15):
    pct = count / len(records_with_boundary) * 100
    print(f"  '{pp}': {count} records ({pct:.1f}%)")

# 5. Specific boundary MIDDLE analysis
print(f"\n" + "="*70)
print("SPECIFIC BOUNDARY MIDDLE PATTERNS")
print("="*70)

for middle in ['sh', 'ko', 'to', 'p']:
    tokens = df_a[df_a['middle'] == middle]
    print(f"\n'{middle}' ({len(tokens)} tokens):")

    # Prefixes used
    prefixes = tokens['prefix'].value_counts()
    prefix_str = ', '.join(f"{p}:{c}" for p, c in prefixes.head(5).items())
    print(f"  Prefixes: {prefix_str}")

    # Suffixes used
    suffixes = tokens['suffix'].value_counts()
    suffix_str = ', '.join(f"{s}:{c}" for s, c in suffixes.head(5).items())
    print(f"  Suffixes: {suffix_str}")

    # Position
    mean_pos = tokens['rel_pos'].mean()
    initial = (tokens['line_pos'] == 0).mean() * 100
    final = (tokens['line_pos'] == tokens['line_length'] - 1).mean() * 100
    print(f"  Position: mean={mean_pos:.2f}, initial={initial:.1f}%, final={final:.1f}%")

# 6. Are boundary MIDDLEs morphological variants of PP?
print(f"\n" + "="*70)
print("MORPHOLOGICAL RELATIONSHIP TO PP")
print("="*70)

print(f"\nChecking if boundary MIDDLEs are substrings/superstrings of PP:")
for boundary in sorted(short_repeating)[:20]:
    # Check if boundary is substring of any PP
    supersets = [pp for pp in pp_middles if boundary in pp and boundary != pp]
    # Check if any PP is substring of boundary
    subsets = [pp for pp in pp_middles if pp in boundary and pp != boundary]

    if supersets or subsets:
        print(f"  '{boundary}': subsets={subsets[:3]}, supersets={supersets[:3]}")

# Interpretation
print(f"\n" + "="*70)
print("INTERPRETATION")
print("="*70)

boundary_initial = (df_a[df_a['ri_type'] == 'BOUNDARY']['line_pos'] == 0).mean() * 100
pp_initial = (df_a[df_a['ri_type'] == 'PP']['line_pos'] == 0).mean() * 100

if boundary_initial > pp_initial * 1.5:
    print(f"""
BOUNDARY MIDDLEs are LINE-INITIAL MARKERS.

Initial rate: Boundary={boundary_initial:.1f}% vs PP={pp_initial:.1f}%

They may serve as:
- Record-type markers (what kind of entry follows)
- Section/category indicators
- "Header" elements for A records
""")
elif (df_a[df_a['ri_type'] == 'BOUNDARY']['line_pos'] == df_a[df_a['ri_type'] == 'BOUNDARY']['line_length'] - 1).mean() > 0.3:
    print("""
BOUNDARY MIDDLEs are LINE-FINAL MARKERS.

They may serve as:
- Closure markers (end of entry)
- Status indicators
- Cross-reference terminators
""")
else:
    print(f"""
BOUNDARY MIDDLEs have MIXED POSITION distribution.

They appear throughout A records, not concentrated at boundaries.
This suggests they're:
- Modifiers/qualifiers integrated into record content
- Category markers that can appear anywhere
- A-internal organizational vocabulary (not positional markers)
""")
