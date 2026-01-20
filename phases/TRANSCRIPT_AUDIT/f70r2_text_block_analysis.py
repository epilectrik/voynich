"""
F70R2 TEXT BLOCK ANALYSIS

The user observed a separate text block on f70r2 (far right) that's NOT part of
the circular diagrams. Is it:
1. Similar to AZC diagram text (R/C/S)?
2. Similar to Currier A?
3. Something unique?

This analyzes the P-placement text on f70r2 specifically.
"""

import os
from collections import Counter

os.chdir('C:/git/voynich')

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Parse all H-only rows
all_rows = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if row.get('transcriber', '').strip() == 'H':
            all_rows.append(row)

# Get different text populations
f70r2_p = [r for r in all_rows if r.get('folio') == 'f70r2' and r.get('placement') == 'P']
f70r2_rcs = [r for r in all_rows if r.get('folio') == 'f70r2' and
             (r.get('placement', '').startswith('R') or
              r.get('placement', '').startswith('C') or
              r.get('placement', '').startswith('S'))]

# All AZC R/C/S text
all_azc_rcs = [r for r in all_rows if r.get('language') == 'NA' and
               (r.get('placement', '').startswith('R') or
                r.get('placement', '').startswith('C') or
                r.get('placement', '').startswith('S'))]

# Currier A
currier_a = [r for r in all_rows if r.get('language') == 'A']

print("=" * 70)
print("F70R2 TEXT BLOCK ANALYSIS")
print("Comparing the separate P-text block to AZC diagrams and Currier A")
print("=" * 70)

print(f"\n[1] Token counts:")
print(f"    f70r2 P-text: {len(f70r2_p)} tokens")
print(f"    f70r2 R/C/S: {len(f70r2_rcs)} tokens")
print(f"    All AZC R/C/S: {len(all_azc_rcs)} tokens")
print(f"    Currier A: {len(currier_a)} tokens")

# Show actual P-text content
print(f"\n[2] f70r2 P-text content (all {len(f70r2_p)} tokens):")
p_words = [r['word'] for r in f70r2_p]
print(f"    {p_words}")

# Vocabulary analysis
print(f"\n[3] Vocabulary comparison:")
f70r2_p_vocab = set(r['word'] for r in f70r2_p)
f70r2_rcs_vocab = set(r['word'] for r in f70r2_rcs)
all_azc_rcs_vocab = set(r['word'] for r in all_azc_rcs)
currier_a_vocab = set(r['word'] for r in currier_a)

print(f"    f70r2 P-text vocabulary: {len(f70r2_p_vocab)} types")
print(f"    f70r2 R/C/S vocabulary: {len(f70r2_rcs_vocab)} types")

# Overlap with different systems
p_in_f70r2_rcs = f70r2_p_vocab & f70r2_rcs_vocab
p_in_all_azc = f70r2_p_vocab & all_azc_rcs_vocab
p_in_currier_a = f70r2_p_vocab & currier_a_vocab
p_unique = f70r2_p_vocab - all_azc_rcs_vocab - currier_a_vocab

print(f"\n[4] P-text vocabulary overlap:")
print(f"    In f70r2 R/C/S: {len(p_in_f70r2_rcs)}/{len(f70r2_p_vocab)} ({100*len(p_in_f70r2_rcs)/len(f70r2_p_vocab):.1f}%)")
print(f"    In ALL AZC R/C/S: {len(p_in_all_azc)}/{len(f70r2_p_vocab)} ({100*len(p_in_all_azc)/len(f70r2_p_vocab):.1f}%)")
print(f"    In Currier A: {len(p_in_currier_a)}/{len(f70r2_p_vocab)} ({100*len(p_in_currier_a)/len(f70r2_p_vocab):.1f}%)")
print(f"    UNIQUE (not in AZC R/C/S or A): {len(p_unique)}/{len(f70r2_p_vocab)} ({100*len(p_unique)/len(f70r2_p_vocab):.1f}%)")

if p_unique:
    print(f"    Unique words: {sorted(p_unique)}")

# Morphological profile
print(f"\n[5] Morphological profile (PREFIX distribution):")

def get_prefix(word):
    prefixes = ['qok', 'qo', 'ok', 'ot', 'ch', 'sh', 'ck', 'ct', 'cth', 'da', 'sa', 'ol', 'al']
    for p in sorted(prefixes, key=len, reverse=True):
        if word.startswith(p):
            return p
    return 'other'

f70r2_p_pfx = Counter(get_prefix(r['word']) for r in f70r2_p)
all_azc_pfx = Counter(get_prefix(r['word']) for r in all_azc_rcs)
currier_a_pfx = Counter(get_prefix(r['word']) for r in currier_a)

print(f"    {'PREFIX':<10} {'f70r2 P%':<12} {'AZC R/C/S%':<12} {'Currier A%':<12}")
print(f"    {'-'*48}")

all_pfx = set(f70r2_p_pfx.keys()) | set(all_azc_pfx.keys()) | set(currier_a_pfx.keys())
for pfx in sorted(all_pfx, key=lambda x: f70r2_p_pfx.get(x, 0), reverse=True):
    p_pct = 100 * f70r2_p_pfx.get(pfx, 0) / len(f70r2_p) if f70r2_p else 0
    azc_pct = 100 * all_azc_pfx.get(pfx, 0) / len(all_azc_rcs) if all_azc_rcs else 0
    a_pct = 100 * currier_a_pfx.get(pfx, 0) / len(currier_a) if currier_a else 0
    if p_pct > 0 or azc_pct > 5 or a_pct > 5:
        print(f"    {pfx:<10} {p_pct:<12.1f} {azc_pct:<12.1f} {a_pct:<12.1f}")

# Token length distribution
print(f"\n[6] Token length distribution:")
f70r2_p_lens = [len(r['word']) for r in f70r2_p]
all_azc_lens = [len(r['word']) for r in all_azc_rcs]
currier_a_lens = [len(r['word']) for r in currier_a]

import numpy as np
print(f"    f70r2 P-text: mean={np.mean(f70r2_p_lens):.2f}, median={np.median(f70r2_p_lens):.1f}")
print(f"    AZC R/C/S:    mean={np.mean(all_azc_lens):.2f}, median={np.median(all_azc_lens):.1f}")
print(f"    Currier A:    mean={np.mean(currier_a_lens):.2f}, median={np.median(currier_a_lens):.1f}")

# Line structure
print(f"\n[7] Line structure (tokens per line):")
f70r2_p_by_line = {}
for r in f70r2_p:
    ln = r.get('line_number', '')
    if ln not in f70r2_p_by_line:
        f70r2_p_by_line[ln] = []
    f70r2_p_by_line[ln].append(r['word'])

print(f"    Lines in f70r2 P-text: {len(f70r2_p_by_line)}")
for ln in sorted(f70r2_p_by_line.keys()):
    tokens = f70r2_p_by_line[ln]
    print(f"      Line {ln}: {len(tokens)} tokens - {' '.join(tokens)}")

# Verdict
print(f"\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

a_overlap = len(p_in_currier_a) / len(f70r2_p_vocab) if f70r2_p_vocab else 0
azc_overlap = len(p_in_all_azc) / len(f70r2_p_vocab) if f70r2_p_vocab else 0

if a_overlap > 0.7:
    print("\n    -> f70r2 P-text is MORE SIMILAR TO CURRIER A")
    print(f"       (A overlap: {100*a_overlap:.1f}%, AZC overlap: {100*azc_overlap:.1f}%)")
elif azc_overlap > 0.7:
    print("\n    -> f70r2 P-text is SIMILAR TO AZC DIAGRAM TEXT")
    print(f"       (AZC overlap: {100*azc_overlap:.1f}%, A overlap: {100*a_overlap:.1f}%)")
elif a_overlap > azc_overlap:
    print("\n    -> f70r2 P-text LEANS TOWARD CURRIER A")
    print(f"       (A overlap: {100*a_overlap:.1f}%, AZC overlap: {100*azc_overlap:.1f}%)")
else:
    print("\n    -> f70r2 P-text has MIXED CHARACTER")
    print(f"       (A overlap: {100*a_overlap:.1f}%, AZC overlap: {100*azc_overlap:.1f}%)")
