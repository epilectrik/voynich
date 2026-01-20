"""
AZC TRANSCRIPT AUDIT

Question: Are we loading AZC folios correctly from the transcript?

Checks:
1. What are the unique language values?
2. Are there empty language values and what are they?
3. What placement types exist in AZC (language=NA)?
4. Are there multiple transcriber tracks for AZC folios?
5. What folios are classified as AZC?
6. Are there labels/notes mixed in with AZC text?
"""

import os
from collections import Counter, defaultdict
from pathlib import Path

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC TRANSCRIPT AUDIT")
print("Verifying correct loading of AZC (zodiac/astronomical) sections")
print("=" * 70)

# Load raw data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

print(f"\n[1] Header columns ({len(header)}):")
for i, h in enumerate(header):
    print(f"    {i}: {h}")

# Parse all rows
all_rows = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_rows.append(row)

print(f"\n[2] Total rows: {len(all_rows):,}")

# Check unique language values
print("\n[3] Unique language values:")
language_counts = Counter(row.get('language', 'MISSING') for row in all_rows)
for lang, count in sorted(language_counts.items(), key=lambda x: -x[1]):
    print(f"    '{lang}': {count:,}")

# Check what empty language means
empty_lang_rows = [row for row in all_rows if row.get('language', '') == '']
print(f"\n[4] Empty language rows: {len(empty_lang_rows)}")
if empty_lang_rows:
    # Sample some
    print("    Sample (first 5):")
    for row in empty_lang_rows[:5]:
        print(f"      word='{row.get('word', '')}' folio='{row.get('folio', '')}' "
              f"placement='{row.get('placement', '')}' transcriber='{row.get('transcriber', '')}'")

# Check transcriber distribution in AZC (language=NA)
print("\n[5] Transcriber distribution in AZC (language=NA):")
na_rows = [row for row in all_rows if row.get('language', '') == 'NA']
transcriber_counts = Counter(row.get('transcriber', 'MISSING') for row in na_rows)
for trans, count in sorted(transcriber_counts.items(), key=lambda x: -x[1]):
    print(f"    '{trans}': {count:,}")

# Filter to H only for AZC
h_azc_rows = [row for row in na_rows if row.get('transcriber', '').strip() == 'H']
print(f"\n[6] H-only AZC rows: {len(h_azc_rows):,}")

# Placement distribution in H-only AZC
print("\n[7] Placement types in H-only AZC:")
placement_counts = Counter(row.get('placement', 'MISSING') for row in h_azc_rows)
for pl, count in sorted(placement_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"    '{pl}': {count:,}")

# Check for labels in AZC
print("\n[8] Label check (placement starting with 'L'):")
label_rows = [row for row in h_azc_rows if row.get('placement', '').startswith('L')]
print(f"    Labels in H-only AZC: {len(label_rows)}")

# Ring/Circle/Star breakdown
ring_rows = [row for row in h_azc_rows if row.get('placement', '').startswith('R')]
circle_rows = [row for row in h_azc_rows if row.get('placement', '').startswith('C')]
star_rows = [row for row in h_azc_rows if row.get('placement', '').startswith('S')]
other_rows = [row for row in h_azc_rows
              if not row.get('placement', '').startswith(('R', 'C', 'S', 'L'))]

print("\n[9] AZC placement breakdown (H-only):")
print(f"    RING (R*): {len(ring_rows):,}")
print(f"    CIRCLE (C*): {len(circle_rows):,}")
print(f"    STAR (S*): {len(star_rows):,}")
print(f"    OTHER: {len(other_rows):,}")

if other_rows:
    print("\n    OTHER placements detail:")
    other_pl = Counter(row.get('placement', '') for row in other_rows)
    for pl, count in sorted(other_pl.items(), key=lambda x: -x[1]):
        print(f"      '{pl}': {count}")

# Unique folios in AZC
print("\n[10] Unique folios in H-only AZC:")
azc_folios = sorted(set(row.get('folio', '') for row in h_azc_rows))
print(f"    Count: {len(azc_folios)}")
print(f"    Folios: {', '.join(azc_folios[:20])}{'...' if len(azc_folios) > 20 else ''}")

# Check if any AZC folios also have A or B tokens
print("\n[11] AZC folio overlap with A/B:")
a_folios = set(row.get('folio', '') for row in all_rows
               if row.get('language', '') == 'A' and row.get('transcriber', '').strip() == 'H')
b_folios = set(row.get('folio', '') for row in all_rows
               if row.get('language', '') == 'B' and row.get('transcriber', '').strip() == 'H')
azc_folios_set = set(azc_folios)

azc_and_a = azc_folios_set & a_folios
azc_and_b = azc_folios_set & b_folios
azc_only = azc_folios_set - a_folios - b_folios

print(f"    AZC folios that also have A: {len(azc_and_a)}")
print(f"    AZC folios that also have B: {len(azc_and_b)}")
print(f"    AZC-only folios: {len(azc_only)}")

if azc_and_a:
    print(f"    Mixed A+AZC folios: {sorted(azc_and_a)[:10]}")
if azc_and_b:
    print(f"    Mixed B+AZC folios: {sorted(azc_and_b)[:10]}")

# Final token count verification
print("\n[12] Final verification (H-only):")
h_rows = [row for row in all_rows if row.get('transcriber', '').strip() == 'H']
h_a = len([r for r in h_rows if r.get('language', '') == 'A'])
h_b = len([r for r in h_rows if r.get('language', '') == 'B'])
h_na = len([r for r in h_rows if r.get('language', '') == 'NA'])
h_empty = len([r for r in h_rows if r.get('language', '') == ''])
h_other = len(h_rows) - h_a - h_b - h_na - h_empty

print(f"    Total H rows: {len(h_rows):,}")
print(f"    H + language=A: {h_a:,}")
print(f"    H + language=B: {h_b:,}")
print(f"    H + language=NA: {h_na:,}")
print(f"    H + language='': {h_empty:,}")
print(f"    H + other language: {h_other:,}")

# Investigate empty language in H track
if h_empty > 0:
    print("\n[13] WARNING: Empty language in H track")
    empty_h = [r for r in h_rows if r.get('language', '') == '']
    empty_placements = Counter(r.get('placement', '') for r in empty_h)
    empty_folios = Counter(r.get('folio', '') for r in empty_h)
    print(f"    Placements: {dict(empty_placements.most_common(10))}")
    print(f"    Folios: {dict(empty_folios.most_common(10))}")
    print("    Sample words:", [r.get('word', '') for r in empty_h[:10]])

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
