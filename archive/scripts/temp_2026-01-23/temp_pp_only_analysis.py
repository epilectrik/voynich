#!/usr/bin/env python3
"""
Analyze PP-only A records (no RI MIDDLEs).

What are these 23.2% of records that have compatibility carriers
but no A-internal discriminators?
"""

import json
import pandas as pd
from collections import Counter, defaultdict

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']
df = df.rename(columns={'line_number': 'line'})

# Load class mapping and survivors
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

token_to_middle = class_map['token_to_middle']
records = survivors_data['records']

# Get B MIDDLEs
df_b = df[df['language'] == 'B']
b_middles = set()
for token in df_b['word'].unique():
    if token in token_to_middle:
        m = token_to_middle[token]
        if m:
            b_middles.add(m)

# Get all A MIDDLEs
all_a_middles = set()
for rec in records:
    all_a_middles.update(rec['a_middles'])

ri_middles = all_a_middles - b_middles
pp_middles = all_a_middles & b_middles

# Find PP-only records
pp_only_records = []
both_records = []

for rec in records:
    middles = set(rec['a_middles'])
    has_ri = bool(middles & ri_middles)
    has_pp = bool(middles & pp_middles)

    if has_pp and not has_ri:
        pp_only_records.append(rec)
    elif has_pp and has_ri:
        both_records.append(rec)

print(f"PP-only records: {len(pp_only_records)}")
print(f"Both PP+RI records: {len(both_records)}")

# ============================================================
# ANALYSIS 1: Record naming patterns
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 1: RECORD NAMING PATTERNS")
print("="*60)

# Check if PP-only records have special naming (like 'a', 'b' suffixes)
pp_only_names = [r['a_record'] for r in pp_only_records]
both_names = [r['a_record'] for r in both_records]

# Check for letter suffixes (like f100r:2a)
def has_letter_suffix(name):
    # Pattern: folio:line followed by letter
    parts = name.split(':')
    if len(parts) == 2:
        line_part = parts[1]
        return line_part and line_part[-1].isalpha()
    return False

pp_only_with_suffix = sum(1 for n in pp_only_names if has_letter_suffix(n))
both_with_suffix = sum(1 for n in both_names if has_letter_suffix(n))

print(f"\nPP-only with letter suffix: {pp_only_with_suffix}/{len(pp_only_names)} ({100*pp_only_with_suffix/len(pp_only_names):.1f}%)")
print(f"Both PP+RI with letter suffix: {both_with_suffix}/{len(both_names)} ({100*both_with_suffix/len(both_names):.1f}%)")

# ============================================================
# ANALYSIS 2: Token counts
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 2: TOKEN COUNTS")
print("="*60)

pp_only_token_counts = [len(r['a_middles']) for r in pp_only_records]
both_token_counts = [len(r['a_middles']) for r in both_records]

print(f"\nPP-only mean MIDDLE count: {sum(pp_only_token_counts)/len(pp_only_token_counts):.2f}")
print(f"Both PP+RI mean MIDDLE count: {sum(both_token_counts)/len(both_token_counts):.2f}")

# Distribution
print("\nPP-only MIDDLE count distribution:")
pp_dist = Counter(pp_only_token_counts)
for count in sorted(pp_dist.keys())[:8]:
    print(f"  {count} MIDDLEs: {pp_dist[count]} records")

# ============================================================
# ANALYSIS 3: Surviving class counts
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 3: SURVIVING CLASS COUNTS")
print("="*60)

pp_only_survival = [r['surviving_class_count'] for r in pp_only_records]
both_survival = [r['surviving_class_count'] for r in both_records]

print(f"\nPP-only mean surviving classes: {sum(pp_only_survival)/len(pp_only_survival):.1f}")
print(f"Both PP+RI mean surviving classes: {sum(both_survival)/len(both_survival):.1f}")

print(f"\nPP-only survival range: {min(pp_only_survival)} - {max(pp_only_survival)}")
print(f"Both PP+RI survival range: {min(both_survival)} - {max(both_survival)}")

# ============================================================
# ANALYSIS 4: Which PP MIDDLEs appear in PP-only records?
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 4: PP MIDDLE USAGE")
print("="*60)

pp_only_pp_middles = Counter()
both_pp_middles = Counter()

for rec in pp_only_records:
    for m in set(rec['a_middles']) & pp_middles:
        pp_only_pp_middles[m] += 1

for rec in both_records:
    for m in set(rec['a_middles']) & pp_middles:
        both_pp_middles[m] += 1

print("\nMost common PP MIDDLEs in PP-only records:")
for m, count in pp_only_pp_middles.most_common(15):
    pct = 100 * count / len(pp_only_records)
    print(f"  '{m}': {count} ({pct:.1f}%)")

# ============================================================
# ANALYSIS 5: Folio distribution
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 5: FOLIO DISTRIBUTION")
print("="*60)

pp_only_folios = Counter(r['a_record'].split(':')[0] for r in pp_only_records)
both_folios = Counter(r['a_record'].split(':')[0] for r in both_records)

print(f"\nPP-only records spread across {len(pp_only_folios)} folios")
print(f"Both PP+RI records spread across {len(both_folios)} folios")

print("\nFolios with highest PP-only concentration:")
for folio, count in pp_only_folios.most_common(10):
    total_in_folio = pp_only_folios[folio] + both_folios.get(folio, 0)
    pct = 100 * count / total_in_folio if total_in_folio > 0 else 0
    print(f"  {folio}: {count} PP-only / {total_in_folio} total ({pct:.1f}%)")

# ============================================================
# ANALYSIS 6: Example records
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 6: EXAMPLE PP-ONLY RECORDS")
print("="*60)

# Show a variety of PP-only records
print("\nSmall PP-only records (1-2 MIDDLEs):")
small = [r for r in pp_only_records if len(r['a_middles']) <= 2][:5]
for r in small:
    print(f"  {r['a_record']}: {r['a_middles']} -> {r['surviving_class_count']} classes")

print("\nLarge PP-only records (5+ MIDDLEs):")
large = [r for r in pp_only_records if len(r['a_middles']) >= 5][:5]
for r in large:
    print(f"  {r['a_record']}: {r['a_middles'][:5]}{'...' if len(r['a_middles']) > 5 else ''} -> {r['surviving_class_count']} classes")

# ============================================================
# ANALYSIS 7: Are PP-only records sub-entries?
# ============================================================
print("\n" + "="*60)
print("ANALYSIS 7: SUB-ENTRY ANALYSIS")
print("="*60)

# Check if PP-only records tend to follow RI+PP records on same folio:line base
def get_base_line(name):
    """Get folio:line without any suffix"""
    parts = name.split(':')
    if len(parts) == 2:
        folio = parts[0]
        line = ''.join(c for c in parts[1] if c.isdigit())
        return f"{folio}:{line}" if line else None
    return None

pp_only_bases = set(get_base_line(r['a_record']) for r in pp_only_records)
both_bases = set(get_base_line(r['a_record']) for r in both_records)

shared_bases = pp_only_bases & both_bases
print(f"\nPP-only records that share a base line with PP+RI records: {len(shared_bases)}")
print(f"This suggests PP-only may be sub-entries or annotations of main entries")

# Show examples of shared bases
print("\nExamples of shared base lines:")
count = 0
for base in list(shared_bases)[:5]:
    pp_only_at_base = [r for r in pp_only_records if get_base_line(r['a_record']) == base]
    both_at_base = [r for r in both_records if get_base_line(r['a_record']) == base]

    print(f"\n  Base: {base}")
    for r in both_at_base[:2]:
        ri = set(r['a_middles']) & ri_middles
        pp = set(r['a_middles']) & pp_middles
        print(f"    {r['a_record']} (PP+RI): RI={list(ri)[:3]}, PP={list(pp)[:3]}")
    for r in pp_only_at_base[:2]:
        pp = set(r['a_middles']) & pp_middles
        print(f"    {r['a_record']} (PP-only): PP={list(pp)}")
    count += 1

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"\nPP-only records: {len(pp_only_records)} ({100*len(pp_only_records)/len(records):.1f}%)")
print(f"Have letter suffix: {pp_only_with_suffix} ({100*pp_only_with_suffix/len(pp_only_records):.1f}%)")
print(f"Mean MIDDLE count: {sum(pp_only_token_counts)/len(pp_only_token_counts):.2f} (vs {sum(both_token_counts)/len(both_token_counts):.2f} for PP+RI)")
print(f"Mean surviving classes: {sum(pp_only_survival)/len(pp_only_survival):.1f} (vs {sum(both_survival)/len(both_survival):.1f} for PP+RI)")
