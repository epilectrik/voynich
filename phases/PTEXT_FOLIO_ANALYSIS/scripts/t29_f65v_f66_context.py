#!/usr/bin/env python3
"""
Test 29: f65v/f66v Context Analysis

f65v and f66v are the only P-text only folios in AZC.
They're consecutive versos with f66r (86% diagram) between them.

What's the relationship?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter, defaultdict
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("TEST 29: f65v/f66v CONTEXT ANALYSIS")
print("=" * 70)
print()

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Get all tokens for f65v, f66r, f66v
target_folios = ['f65v', 'f66r', 'f66v']
folio_tokens = defaultdict(list)
folio_middles = defaultdict(set)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if folio in target_folios:
                folio_tokens[folio].append({'token': token, 'placement': placement})
                m = morph.extract(token)
                if m and m.middle:
                    folio_middles[folio].add(m.middle)

# 1. Physical layout
print("1. PHYSICAL LAYOUT")
print("-" * 50)
print("""
When you open the manuscript at this point:

  LEFT SIDE (verso)     |    RIGHT SIDE (recto)
  ---------------------|-----------------------
  f65v (P-text only)   |    f66r (86% diagram)
                       |
  [Close, turn page]   |
                       |
  f66r (86% diagram)   |    f66v (P-text only)

So f66r is the CENTRAL DIAGRAM with text pages on either side.
""")

# 2. Token comparison
print("2. TOKEN COUNTS")
print("-" * 50)

for folio in target_folios:
    tokens = folio_tokens[folio]
    placements = Counter(t['placement'] for t in tokens)

    p_count = sum(c for p, c in placements.items() if p.startswith('P'))
    c_count = sum(c for p, c in placements.items() if p.startswith('C'))
    r_count = sum(c for p, c in placements.items() if p.startswith('R'))
    s_count = sum(c for p, c in placements.items() if p.startswith('S'))

    print(f"{folio}: {len(tokens)} tokens")
    print(f"  P (paragraph): {p_count}")
    print(f"  C (circle): {c_count}")
    print(f"  R (ring): {r_count}")
    print(f"  S (star/spoke): {s_count}")
    print()

# 3. Vocabulary overlap
print("3. VOCABULARY OVERLAP")
print("-" * 50)

f65v_mids = folio_middles['f65v']
f66r_mids = folio_middles['f66r']
f66v_mids = folio_middles['f66v']

print(f"f65v unique MIDDLEs: {len(f65v_mids)}")
print(f"f66r unique MIDDLEs: {len(f66r_mids)}")
print(f"f66v unique MIDDLEs: {len(f66v_mids)}")
print()

# f65v <-> f66r
shared_65v_66r = f65v_mids & f66r_mids
jaccard_65v_66r = len(shared_65v_66r) / len(f65v_mids | f66r_mids) if (f65v_mids | f66r_mids) else 0
print(f"f65v <-> f66r overlap: {len(shared_65v_66r)} shared, Jaccard={jaccard_65v_66r:.3f}")

# f66r <-> f66v
shared_66r_66v = f66r_mids & f66v_mids
jaccard_66r_66v = len(shared_66r_66v) / len(f66r_mids | f66v_mids) if (f66r_mids | f66v_mids) else 0
print(f"f66r <-> f66v overlap: {len(shared_66r_66v)} shared, Jaccard={jaccard_66r_66v:.3f}")

# f65v <-> f66v (both P-text)
shared_65v_66v = f65v_mids & f66v_mids
jaccard_65v_66v = len(shared_65v_66v) / len(f65v_mids | f66v_mids) if (f65v_mids | f66v_mids) else 0
print(f"f65v <-> f66v overlap: {len(shared_65v_66v)} shared, Jaccard={jaccard_65v_66v:.3f}")

print()

# 4. What does f66r diagram contain?
print("4. f66r DIAGRAM CONTENT")
print("-" * 50)

f66r_placements = Counter(t['placement'] for t in folio_tokens['f66r'])
print("f66r placement breakdown:")
for placement, count in f66r_placements.most_common():
    print(f"  {placement}: {count}")

print()

# Check what positions dominate
c_total = sum(c for p, c in f66r_placements.items() if p.startswith('C'))
r_total = sum(c for p, c in f66r_placements.items() if p.startswith('R'))
s_total = sum(c for p, c in f66r_placements.items() if p.startswith('S'))

print(f"Diagram type: C={c_total}, R={r_total}, S={s_total}")
if c_total > r_total and c_total > s_total:
    print("-> f66r is primarily CIRCLE text (cosmological circles)")
elif r_total > c_total and r_total > s_total:
    print("-> f66r is primarily RING text (zodiac-style)")
else:
    print("-> f66r has mixed diagram positions")

print()

# 5. Do f65v/f66v relate to f66r diagram?
print("5. DO TEXT PAGES RELATE TO DIAGRAM?")
print("-" * 50)

# Check if P-text MIDDLEs appear in f66r
f65v_in_66r = f65v_mids & f66r_mids
f66v_in_66r = f66v_mids & f66r_mids

pct_65v = len(f65v_in_66r) / len(f65v_mids) * 100 if f65v_mids else 0
pct_66v = len(f66v_in_66r) / len(f66v_mids) * 100 if f66v_mids else 0

print(f"f65v MIDDLEs appearing in f66r: {len(f65v_in_66r)}/{len(f65v_mids)} ({pct_65v:.1f}%)")
print(f"f66v MIDDLEs appearing in f66r: {len(f66v_in_66r)}/{len(f66v_mids)} ({pct_66v:.1f}%)")

print()

# Compare to baseline (random AZC diagram)
# Get all AZC diagram MIDDLEs
all_azc_diagram_mids = set()
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            # AZC diagram positions (not P)
            if folio.startswith(('f57', 'f65', 'f66', 'f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73')):
                if placement.startswith(('C', 'R', 'S')):
                    m = morph.extract(token)
                    if m and m.middle:
                        all_azc_diagram_mids.add(m.middle)

f65v_in_all_azc = f65v_mids & all_azc_diagram_mids
f66v_in_all_azc = f66v_mids & all_azc_diagram_mids

pct_65v_all = len(f65v_in_all_azc) / len(f65v_mids) * 100 if f65v_mids else 0
pct_66v_all = len(f66v_in_all_azc) / len(f66v_mids) * 100 if f66v_mids else 0

print(f"f65v MIDDLEs in ANY AZC diagram: {len(f65v_in_all_azc)}/{len(f65v_mids)} ({pct_65v_all:.1f}%)")
print(f"f66v MIDDLEs in ANY AZC diagram: {len(f66v_in_all_azc)}/{len(f66v_mids)} ({pct_66v_all:.1f}%)")

print()

# 6. Content samples
print("6. SAMPLE CONTENT")
print("-" * 50)

print("f65v (first 3 lines):")
f65v_lines = defaultdict(list)
for t in folio_tokens['f65v']:
    # Group by presumed line (we don't have line numbers here, use sequence)
    pass

# Just show first 20 tokens
print("  " + " ".join(t['token'] for t in folio_tokens['f65v'][:20]) + "...")

print()
print("f66v (first 3 lines):")
print("  " + " ".join(t['token'] for t in folio_tokens['f66v'][:20]) + "...")

print()

# 7. Synthesis
print("=" * 70)
print("SYNTHESIS: f65v AND f66v")
print("=" * 70)

print(f"""
PHYSICAL ARRANGEMENT:
  f65v (P-text) | f66r (diagram) | f66v (P-text)

  The diagram f66r is flanked by two text pages.

VOCABULARY RELATIONSHIP:
  f65v <-> f66r: Jaccard {jaccard_65v_66r:.3f}
  f66r <-> f66v: Jaccard {jaccard_66r_66v:.3f}
  f65v <-> f66v: Jaccard {jaccard_65v_66v:.3f}

INTERPRETATION:
""")

if pct_65v > 50 and pct_66v > 50:
    print("""
HIGH OVERLAP: Text pages share vocabulary with central diagram.
-> f65v and f66v are likely ANNOTATIONS for f66r
-> They describe or explain the f66r diagram content
""")
elif pct_65v > 20 or pct_66v > 20:
    print("""
MODERATE OVERLAP: Some shared vocabulary with diagram.
-> Text pages may be RELATED to diagram content
-> But not direct annotations; possibly material specifications
""")
else:
    print("""
LOW OVERLAP: Text pages don't share much vocabulary with diagram.
-> f65v and f66v may be INDEPENDENT content
-> Possibly misplaced Currier A pages
-> Or procedural text unrelated to diagram labels
""")

print(f"""
ANOMALY EXPLANATION:

f65v and f66v are Currier A text (0.941 cosine to A) that happen to be
physically located within the cosmological section. They're not
diagram labels but paragraph text - possibly:

1. Material specifications for cosmological procedures
2. Explanatory annotations for the f66r diagram
3. Registry entries that relate to astronomical timing
4. Or simply misbound pages from the herbal section
""")
