"""
AZC PLACEMENT ANALYSIS

What are the non-R/C/S placements in AZC? (P, Y, X, O, I, B, Z, etc.)
Should they be included in AZC analyses?
"""

import os
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Get H-only AZC
azc_rows = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if (row.get('transcriber', '').strip() == 'H' and
            row.get('language', '') == 'NA'):
            azc_rows.append(row)

print(f"Total H-only AZC: {len(azc_rows)}")

# Categorize by placement type
ring = [r for r in azc_rows if r.get('placement', '').startswith('R')]
circle = [r for r in azc_rows if r.get('placement', '').startswith('C')]
star = [r for r in azc_rows if r.get('placement', '').startswith('S')]
label = [r for r in azc_rows if r.get('placement', '').startswith('L')]
other = [r for r in azc_rows if not r.get('placement', '').startswith(('R', 'C', 'S', 'L'))]

print(f"\n[1] Placement breakdown:")
print(f"    RING (R*): {len(ring)} ({100*len(ring)/len(azc_rows):.1f}%)")
print(f"    CIRCLE (C*): {len(circle)} ({100*len(circle)/len(azc_rows):.1f}%)")
print(f"    STAR (S*): {len(star)} ({100*len(star)/len(azc_rows):.1f}%)")
print(f"    LABEL (L*): {len(label)} ({100*len(label)/len(azc_rows):.1f}%)")
print(f"    OTHER: {len(other)} ({100*len(other)/len(azc_rows):.1f}%)")

# Detail OTHER placements
print("\n[2] OTHER placement detail:")
other_pl = Counter(r.get('placement', '') for r in other)
for pl, count in sorted(other_pl.items(), key=lambda x: -x[1]):
    # Get folios for this placement
    folios = set(r['folio'] for r in other if r.get('placement', '') == pl)
    print(f"    '{pl}': {count} tokens in folios {sorted(folios)[:5]}{'...' if len(folios) > 5 else ''}")

# What is 'P' placement? (398 tokens - the biggest OTHER)
print("\n[3] 'P' placement analysis:")
p_rows = [r for r in other if r.get('placement', '') == 'P']
p_folios = Counter(r['folio'] for r in p_rows)
print(f"    Folios with P placement:")
for folio, count in sorted(p_folios.items()):
    print(f"      {folio}: {count}")

# Sample P words
p_words = [r['word'] for r in p_rows]
print(f"    Sample words: {p_words[:20]}")

# Vocabulary overlap analysis
print("\n[4] Vocabulary overlap:")
rcs_vocab = set(r['word'] for r in ring + circle + star)
other_vocab = set(r['word'] for r in other)
shared = rcs_vocab & other_vocab
other_only = other_vocab - rcs_vocab

print(f"    R/C/S vocabulary: {len(rcs_vocab)}")
print(f"    OTHER vocabulary: {len(other_vocab)}")
print(f"    Shared: {len(shared)} ({100*len(shared)/len(other_vocab):.1f}% of OTHER)")
print(f"    OTHER-only: {len(other_only)}")

# Check if OTHER tokens use same morphology
print("\n[5] Morphological similarity:")
def get_prefix(word):
    prefixes = ['qok', 'qo', 'ok', 'ot', 'ch', 'sh', 'ck', 'ct', 'cth', 'da', 'sa', 'ol']
    for p in sorted(prefixes, key=len, reverse=True):
        if word.startswith(p):
            return p
    return 'other'

rcs_prefixes = Counter(get_prefix(r['word']) for r in ring + circle + star)
other_prefixes = Counter(get_prefix(r['word']) for r in other)

print("    PREFIX distribution:")
print(f"    {'PREFIX':<10} {'R/C/S %':<12} {'OTHER %':<12}")
all_prefixes = set(rcs_prefixes.keys()) | set(other_prefixes.keys())
for pfx in sorted(all_prefixes, key=lambda x: rcs_prefixes.get(x, 0) + other_prefixes.get(x, 0), reverse=True)[:10]:
    rcs_pct = 100 * rcs_prefixes.get(pfx, 0) / len(ring + circle + star) if (ring + circle + star) else 0
    other_pct = 100 * other_prefixes.get(pfx, 0) / len(other) if other else 0
    print(f"    {pfx:<10} {rcs_pct:<12.1f} {other_pct:<12.1f}")

print("\n[6] Recommendation:")
if len(other_only) < 50 and len(shared) > len(other_only):
    print("    OTHER placements use mostly shared vocabulary")
    print("    -> INCLUDE in AZC analyses (same linguistic system)")
else:
    print("    OTHER placements have distinct vocabulary")
    print("    -> INVESTIGATE before including")
