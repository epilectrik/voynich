#!/usr/bin/env python3
"""
Analyze RI MIDDLE structure - what are they encoding?

Questions:
1. How unique are RI MIDDLEs? (singletons vs repeated)
2. Do they have internal patterns? (character sequences)
3. Are they folio-localized or distributed?
4. Any numeric/sequential patterns?
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
df_a['middle'] = df_a['word'].apply(extract_middle)

# Identify RI tokens
df_ri = df_a[df_a['middle'].apply(lambda m: m is not None and m not in pp_middles)].copy()

print("="*70)
print("RI MIDDLE STRUCTURE ANALYSIS")
print("="*70)

# 1. Uniqueness analysis
ri_middle_counts = df_ri['middle'].value_counts()
total_ri_middles = len(ri_middle_counts)
total_ri_tokens = len(df_ri)

print(f"\n--- UNIQUENESS ---")
print(f"Total RI tokens: {total_ri_tokens}")
print(f"Unique RI MIDDLEs: {total_ri_middles}")
print(f"Ratio: {total_ri_tokens/total_ri_middles:.2f} tokens per MIDDLE")

# Frequency distribution
singletons = sum(1 for c in ri_middle_counts if c == 1)
doubletons = sum(1 for c in ri_middle_counts if c == 2)
tripletons = sum(1 for c in ri_middle_counts if c == 3)
high_freq = sum(1 for c in ri_middle_counts if c >= 5)

print(f"\nFrequency distribution:")
print(f"  Singletons (appear once): {singletons} ({100*singletons/total_ri_middles:.1f}%)")
print(f"  Doubletons (appear twice): {doubletons} ({100*doubletons/total_ri_middles:.1f}%)")
print(f"  Tripletons (appear 3x): {tripletons} ({100*tripletons/total_ri_middles:.1f}%)")
print(f"  High frequency (5+): {high_freq} ({100*high_freq/total_ri_middles:.1f}%)")

# Most common RI MIDDLEs
print(f"\nMost common RI MIDDLEs:")
for middle, count in ri_middle_counts.head(20).items():
    print(f"  '{middle}': {count}")

# 2. Length analysis
ri_lengths = df_ri['middle'].apply(len)
print(f"\n--- LENGTH DISTRIBUTION ---")
print(f"Min: {ri_lengths.min()}, Max: {ri_lengths.max()}, Mean: {ri_lengths.mean():.2f}")

length_dist = ri_lengths.value_counts().sort_index()
print(f"\n{'Length':>8} {'Count':>10} {'%':>8}")
for length, count in length_dist.items():
    pct = 100 * count / total_ri_tokens
    bar = '#' * int(pct / 2)
    print(f"{length:>8} {count:>10} {pct:>7.1f}% {bar}")

# 3. Character composition
print(f"\n--- CHARACTER COMPOSITION ---")
all_chars = ''.join(df_ri['middle'].dropna())
char_counts = Counter(all_chars)
print(f"Total characters in RI MIDDLEs: {len(all_chars)}")
print(f"Unique characters: {len(char_counts)}")

print(f"\nCharacter frequency:")
for char, count in char_counts.most_common(15):
    pct = 100 * count / len(all_chars)
    print(f"  '{char}': {count} ({pct:.1f}%)")

# 4. Internal pattern analysis - do RI MIDDLEs have substructure?
print(f"\n--- INTERNAL PATTERNS ---")

# Common bigrams
bigrams = Counter()
for middle in df_ri['middle'].dropna():
    for i in range(len(middle) - 1):
        bigrams[middle[i:i+2]] += 1

print(f"Most common bigrams in RI MIDDLEs:")
for bg, count in bigrams.most_common(15):
    print(f"  '{bg}': {count}")

# Common prefixes within MIDDLE (first 2 chars)
middle_prefixes = Counter(m[:2] for m in df_ri['middle'].dropna() if len(m) >= 2)
print(f"\nMost common MIDDLE-internal prefixes (first 2 chars):")
for mp, count in middle_prefixes.most_common(10):
    print(f"  '{mp}': {count}")

# Common suffixes within MIDDLE (last 2 chars)
middle_suffixes = Counter(m[-2:] for m in df_ri['middle'].dropna() if len(m) >= 2)
print(f"\nMost common MIDDLE-internal suffixes (last 2 chars):")
for ms, count in middle_suffixes.most_common(10):
    print(f"  '{ms}': {count}")

# 5. Folio localization
print(f"\n--- FOLIO LOCALIZATION ---")

# For each RI MIDDLE, how many folios does it appear in?
middle_to_folios = defaultdict(set)
for _, row in df_ri.iterrows():
    if row['middle']:
        middle_to_folios[row['middle']].add(row['folio'])

folio_span_dist = Counter(len(folios) for folios in middle_to_folios.values())
print(f"RI MIDDLE folio span distribution:")
print(f"  {'Folios':>8} {'MIDDLEs':>10} {'%':>8}")
for span in sorted(folio_span_dist.keys())[:10]:
    count = folio_span_dist[span]
    pct = 100 * count / total_ri_middles
    print(f"  {span:>8} {count:>10} {pct:>7.1f}%")

single_folio = folio_span_dist[1]
print(f"\nRI MIDDLEs appearing in only 1 folio: {single_folio} ({100*single_folio/total_ri_middles:.1f}%)")

# 6. Check for sequential/counting patterns
print(f"\n--- SEQUENTIAL PATTERN CHECK ---")

# Do any RI MIDDLEs look like they could be counting?
# Check for patterns like: o, oo, ooo or ch, chch, chchch
# Or patterns with incrementing structure

# Look for repeated character patterns
repeated_patterns = []
for middle in ri_middle_counts.index:
    if len(middle) >= 2:
        # Check if it's a repeated unit
        for unit_len in range(1, len(middle)//2 + 1):
            unit = middle[:unit_len]
            if unit * (len(middle)//unit_len) == middle[:unit_len * (len(middle)//unit_len)]:
                if len(middle) // unit_len >= 2:
                    repeated_patterns.append((middle, unit, len(middle)//unit_len))
                    break

if repeated_patterns:
    print(f"RI MIDDLEs with repeated unit structure: {len(repeated_patterns)}")
    for middle, unit, reps in repeated_patterns[:15]:
        count = ri_middle_counts[middle]
        print(f"  '{middle}' = '{unit}' × {reps} (appears {count}x)")
else:
    print("No obvious repeated-unit patterns found")

# Check for numeric-like progressions (same prefix, varying suffix)
print(f"\n--- FAMILY PATTERNS (same start, different end) ---")
prefix_families = defaultdict(list)
for middle in ri_middle_counts.index:
    if len(middle) >= 3:
        prefix_families[middle[:2]].append(middle)

# Find families with multiple members
large_families = [(prefix, members) for prefix, members in prefix_families.items()
                  if len(members) >= 5]
large_families.sort(key=lambda x: -len(x[1]))

print(f"Families with 5+ members sharing first 2 chars:")
for prefix, members in large_families[:10]:
    print(f"\n  '{prefix}...' family ({len(members)} members):")
    for m in sorted(members, key=len)[:8]:
        count = ri_middle_counts[m]
        print(f"    '{m}' ({count}x)")
    if len(members) > 8:
        print(f"    ... and {len(members)-8} more")

# Summary interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if singletons / total_ri_middles > 0.7:
    print(f"""
HIGH SINGLETON RATE: {100*singletons/total_ri_middles:.1f}% of RI MIDDLEs appear only once.

This is consistent with:
- UNIQUE IDENTIFIERS (serial numbers, location codes)
- NOT a counting system (would expect repeated patterns)
- NOT a small vocabulary with combinatorial reuse
""")

if single_folio / total_ri_middles > 0.7:
    print(f"""
HIGH FOLIO LOCALIZATION: {100*single_folio/total_ri_middles:.1f}% appear in only 1 folio.

This suggests:
- RI MIDDLEs are FOLIO-SPECIFIC identifiers
- Not manuscript-wide cross-references
- Possibly: bin/location/batch markers local to each folio's context
""")

if large_families:
    print(f"""
FAMILY STRUCTURE DETECTED: {len(large_families)} prefix families with 5+ members.

This suggests:
- RI MIDDLEs have INTERNAL STRUCTURE (prefix + variant)
- Could encode: category + instance (e.g., "material-type" + "specific-variant")
- Not purely random unique IDs
""")
