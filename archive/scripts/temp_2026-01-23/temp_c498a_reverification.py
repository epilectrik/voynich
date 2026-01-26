#!/usr/bin/env python3
"""
C498.a BIFURCATION RE-VERIFICATION

With corrected 412 shared MIDDLEs (from v2 extraction), re-verify:
- AZC-Mediated: MIDDLEs in A & AZC & B (true pipeline participation)
- B-Native Overlap: MIDDLEs in A & B but NOT in AZC

Original (from 268 shared):
- AZC-Mediated: 154 (25.0% of A vocabulary)
- B-Native Overlap: 114 (18.5% of A vocabulary)
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('.')

# Load corrected middle_classes.json
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)

print(f"Loaded middle_classes.json version: {data.get('version', 'unknown')}")
print(f"  RI MIDDLEs: {len(data['a_exclusive_middles'])}")
print(f"  Shared MIDDLEs: {len(data['a_shared_middles'])}")

shared_middles = set(data['a_shared_middles'])
ri_middles = set(data['a_exclusive_middles'])

# ============================================================
# EXTRACTION FUNCTION (same as v2)
# ============================================================

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def extract_middle(token):
    if not token:
        return None
    working = token
    for p in PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            working = working[len(p):]
            break
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break
    return working if working else None

# ============================================================
# COLLECT MIDDLES BY SYSTEM
# ============================================================

a_middles = set()
b_middles = set()
azc_middles = set()

# Also track folio counts for AZC-Mediated breakdown
azc_folio_counts = defaultdict(set)  # middle -> set of AZC folios
b_folio_counts = defaultdict(set)    # middle -> set of B folios

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue

        word = row.get('word', '').strip()
        lang = row.get('language', '').strip()
        folio = row.get('folio', '').strip()

        if not word or '*' in word:
            continue

        middle = extract_middle(word)
        if not middle:
            continue

        if lang == 'A':
            a_middles.add(middle)
        elif lang == 'B':
            b_middles.add(middle)
            b_folio_counts[middle].add(folio)
        elif lang == 'NA':  # AZC
            azc_middles.add(middle)
            azc_folio_counts[middle].add(folio)

print(f"\n" + "="*70)
print("MIDDLE SETS BY SYSTEM")
print("="*70)
print(f"  A MIDDLEs: {len(a_middles)}")
print(f"  B MIDDLEs: {len(b_middles)}")
print(f"  AZC MIDDLEs: {len(azc_middles)}")

# ============================================================
# VERIFY SHARED MIDDLES
# ============================================================

# Shared should be A & B
computed_shared = a_middles & b_middles
print(f"\n  Computed A & B: {len(computed_shared)}")
print(f"  From middle_classes.json: {len(shared_middles)}")

if computed_shared != shared_middles:
    diff1 = computed_shared - shared_middles
    diff2 = shared_middles - computed_shared
    print(f"  MISMATCH! In computed but not in file: {len(diff1)}")
    print(f"  MISMATCH! In file but not computed: {len(diff2)}")
else:
    print(f"  MATCH confirmed")

# ============================================================
# C498.a BIFURCATION
# ============================================================

print(f"\n" + "="*70)
print("C498.a BIFURCATION (CORRECTED)")
print("="*70)

# AZC-Mediated: A & AZC & B
azc_mediated = shared_middles & azc_middles
print(f"\n  AZC-Mediated (A & AZC & B): {len(azc_mediated)}")

# B-Native Overlap: (A & B) - AZC = shared but NOT in AZC
b_native_overlap = shared_middles - azc_middles
print(f"  B-Native Overlap (A & B, NOT in AZC): {len(b_native_overlap)}")

# Sanity check
assert len(azc_mediated) + len(b_native_overlap) == len(shared_middles), "Partition check failed!"
print(f"\n  Partition check: {len(azc_mediated)} + {len(b_native_overlap)} = {len(shared_middles)} OK")

# Percentages of total A vocabulary
total_a = len(a_middles)
print(f"\n  As % of A vocabulary ({total_a} total):")
print(f"    AZC-Mediated: {100*len(azc_mediated)/total_a:.1f}%")
print(f"    B-Native Overlap: {100*len(b_native_overlap)/total_a:.1f}%")
print(f"    RI (A-exclusive): {100*len(ri_middles)/total_a:.1f}%")

# ============================================================
# AZC-MEDIATED BREAKDOWN BY AZC FOLIO BREADTH
# ============================================================

print(f"\n" + "="*70)
print("AZC-MEDIATED BREAKDOWN BY AZC FOLIO BREADTH")
print("="*70)

universal = []    # 10+ AZC folios
moderate = []     # 3-9 AZC folios
restricted = []   # 1-2 AZC folios

for middle in azc_mediated:
    n_azc_folios = len(azc_folio_counts[middle])
    n_b_folios = len(b_folio_counts[middle])

    if n_azc_folios >= 10:
        universal.append((middle, n_azc_folios, n_b_folios))
    elif n_azc_folios >= 3:
        moderate.append((middle, n_azc_folios, n_b_folios))
    else:
        restricted.append((middle, n_azc_folios, n_b_folios))

print(f"\n  Universal (10+ AZC folios): {len(universal)}")
if universal:
    avg_b = sum(x[2] for x in universal) / len(universal)
    print(f"    Avg B folios: {avg_b:.1f}")

print(f"\n  Moderate (3-9 AZC folios): {len(moderate)}")
if moderate:
    avg_b = sum(x[2] for x in moderate) / len(moderate)
    print(f"    Avg B folios: {avg_b:.1f}")

print(f"\n  Restricted (1-2 AZC folios): {len(restricted)}")
if restricted:
    avg_b = sum(x[2] for x in restricted) / len(restricted)
    print(f"    Avg B folios: {avg_b:.1f}")

# ============================================================
# B-NATIVE OVERLAP CHARACTERISTICS
# ============================================================

print(f"\n" + "="*70)
print("B-NATIVE OVERLAP CHARACTERISTICS")
print("="*70)

# Check B-heaviness
b_heavy_count = 0
for middle in b_native_overlap:
    # Count A frequency vs B frequency
    # We need to get actual token counts
    pass

# For now just show the B folio spread
b_folios_for_bno = [len(b_folio_counts[m]) for m in b_native_overlap]
if b_folios_for_bno:
    avg_b_folios = sum(b_folios_for_bno) / len(b_folios_for_bno)
    print(f"\n  Avg B folios for B-Native Overlap: {avg_b_folios:.1f}")
    print(f"  Min B folios: {min(b_folios_for_bno)}")
    print(f"  Max B folios: {max(b_folios_for_bno)}")

# ============================================================
# COMPARISON WITH ORIGINAL
# ============================================================

print(f"\n" + "="*70)
print("COMPARISON WITH ORIGINAL C498.a")
print("="*70)

print(f"\n  Original (from 268 shared):")
print(f"    AZC-Mediated: 154 (25.0% of A)")
print(f"    B-Native Overlap: 114 (18.5% of A)")

print(f"\n  Corrected (from 412 shared):")
print(f"    AZC-Mediated: {len(azc_mediated)} ({100*len(azc_mediated)/total_a:.1f}% of A)")
print(f"    B-Native Overlap: {len(b_native_overlap)} ({100*len(b_native_overlap)/total_a:.1f}% of A)")

print(f"\n  Change:")
print(f"    AZC-Mediated: {len(azc_mediated) - 154:+d}")
print(f"    B-Native Overlap: {len(b_native_overlap) - 114:+d}")

# ============================================================
# SAMPLE MIDDLES
# ============================================================

print(f"\n" + "="*70)
print("SAMPLE MIDDLES")
print("="*70)

print(f"\n  Universal AZC-Mediated (first 10):")
for m, azc, b in sorted(universal, key=lambda x: -x[1])[:10]:
    print(f"    {m}: {azc} AZC folios, {b} B folios")

print(f"\n  B-Native Overlap (first 10 by B spread):")
bno_with_spread = [(m, len(b_folio_counts[m])) for m in b_native_overlap]
for m, b in sorted(bno_with_spread, key=lambda x: -x[1])[:10]:
    print(f"    {m}: {b} B folios, 0 AZC folios")

# ============================================================
# RI in AZC CHECK (interface noise)
# ============================================================

print(f"\n" + "="*70)
print("RI IN AZC (Interface Noise)")
print("="*70)

ri_in_azc = ri_middles & azc_middles
print(f"\n  RI MIDDLEs that also appear in AZC: {len(ri_in_azc)}")
print(f"  As % of RI: {100*len(ri_in_azc)/len(ri_middles):.1f}%")
print(f"  (Original C498 noted 8.9% - interface noise, not a distinct stratum)")

# ============================================================
# OUTPUT SUMMARY FOR CONSTRAINT UPDATE
# ============================================================

print(f"\n" + "="*70)
print("SUMMARY FOR CONSTRAINT UPDATE")
print("="*70)

print(f"""
C498.a REVISED VALUES (2026-01-24):

Shared MIDDLEs: 412 (from corrected extraction)
+-- AZC-Mediated: {len(azc_mediated)} ({100*len(azc_mediated)/total_a:.1f}% of A vocabulary)
|     True pipeline participation: A=>AZC=>B
|     +-- Universal (10+ AZC folios): {len(universal)}
|     +-- Moderate (3-9 AZC folios): {len(moderate)}
|     +-- Restricted (1-2 AZC folios): {len(restricted)}
|
+-- B-Native Overlap: {len(b_native_overlap)} ({100*len(b_native_overlap)/total_a:.1f}% of A vocabulary)
      Zero AZC presence, B execution vocabulary with incidental A appearance

RI (A-exclusive): {len(ri_middles)} ({100*len(ri_middles)/total_a:.1f}% of A vocabulary)
""")

# Save results
results = {
    'version': '2.0',
    'date': '2026-01-24',
    'total_a_middles': len(a_middles),
    'shared_middles': len(shared_middles),
    'ri_middles': len(ri_middles),
    'azc_mediated': {
        'count': len(azc_mediated),
        'percent_of_a': round(100*len(azc_mediated)/total_a, 1),
        'breakdown': {
            'universal_10plus': len(universal),
            'moderate_3to9': len(moderate),
            'restricted_1to2': len(restricted),
        },
        'middles': sorted(azc_mediated),
    },
    'b_native_overlap': {
        'count': len(b_native_overlap),
        'percent_of_a': round(100*len(b_native_overlap)/total_a, 1),
        'middles': sorted(b_native_overlap),
    },
    'ri_in_azc': {
        'count': len(ri_in_azc),
        'percent_of_ri': round(100*len(ri_in_azc)/len(ri_middles), 1),
        'note': 'Interface noise, not distinct stratum',
    },
}

with open(PROJECT_ROOT / 'temp_c498a_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to temp_c498a_results.json")
