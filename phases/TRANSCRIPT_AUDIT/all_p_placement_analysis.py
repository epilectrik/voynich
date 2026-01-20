"""
ALL P-PLACEMENT TEXT ANALYSIS

Is the Currier A similarity pattern consistent across all P-placement text?
"""

import os
from collections import Counter
import numpy as np

os.chdir('C:/git/voynich')

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_rows = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if row.get('transcriber', '').strip() == 'H':
            all_rows.append(row)

# Get populations
all_p = [r for r in all_rows if r.get('language') == 'NA' and r.get('placement') == 'P']
all_azc_rcs = [r for r in all_rows if r.get('language') == 'NA' and
               (r.get('placement', '').startswith('R') or
                r.get('placement', '').startswith('C') or
                r.get('placement', '').startswith('S'))]
currier_a = [r for r in all_rows if r.get('language') == 'A']
currier_b = [r for r in all_rows if r.get('language') == 'B']

print("=" * 70)
print("ALL P-PLACEMENT TEXT ANALYSIS")
print("=" * 70)

print(f"\n[1] Corpus sizes:")
print(f"    All P-placement: {len(all_p)} tokens")
print(f"    AZC R/C/S: {len(all_azc_rcs)} tokens")
print(f"    Currier A: {len(currier_a)} tokens")
print(f"    Currier B: {len(currier_b)} tokens")

# Vocabulary overlap
p_vocab = set(r['word'] for r in all_p)
azc_vocab = set(r['word'] for r in all_azc_rcs)
a_vocab = set(r['word'] for r in currier_a)
b_vocab = set(r['word'] for r in currier_b)

print(f"\n[2] P-text vocabulary overlap:")
print(f"    P vocabulary: {len(p_vocab)} types")
print(f"    In AZC R/C/S: {len(p_vocab & azc_vocab)} ({100*len(p_vocab & azc_vocab)/len(p_vocab):.1f}%)")
print(f"    In Currier A: {len(p_vocab & a_vocab)} ({100*len(p_vocab & a_vocab)/len(p_vocab):.1f}%)")
print(f"    In Currier B: {len(p_vocab & b_vocab)} ({100*len(p_vocab & b_vocab)/len(p_vocab):.1f}%)")

p_unique = p_vocab - azc_vocab - a_vocab - b_vocab
print(f"    UNIQUE (not in AZC/A/B): {len(p_unique)} ({100*len(p_unique)/len(p_vocab):.1f}%)")

# Per-folio breakdown
print(f"\n[3] Per-folio P-text analysis:")
p_by_folio = {}
for r in all_p:
    folio = r.get('folio', '')
    if folio not in p_by_folio:
        p_by_folio[folio] = []
    p_by_folio[folio].append(r)

print(f"    {'Folio':<10} {'Tokens':<8} {'A-overlap%':<12} {'AZC-overlap%':<12} {'B-overlap%':<12}")
print(f"    {'-'*55}")

for folio in sorted(p_by_folio.keys()):
    tokens = p_by_folio[folio]
    vocab = set(r['word'] for r in tokens)
    a_ovl = 100 * len(vocab & a_vocab) / len(vocab) if vocab else 0
    azc_ovl = 100 * len(vocab & azc_vocab) / len(vocab) if vocab else 0
    b_ovl = 100 * len(vocab & b_vocab) / len(vocab) if vocab else 0
    print(f"    {folio:<10} {len(tokens):<8} {a_ovl:<12.1f} {azc_ovl:<12.1f} {b_ovl:<12.1f}")

# PREFIX profile comparison
print(f"\n[4] PREFIX distribution comparison:")

def get_prefix(word):
    prefixes = ['qok', 'qo', 'ok', 'ot', 'ch', 'sh', 'ck', 'ct', 'cth', 'da', 'sa', 'ol', 'al']
    for p in sorted(prefixes, key=len, reverse=True):
        if word.startswith(p):
            return p
    return 'other'

p_pfx = Counter(get_prefix(r['word']) for r in all_p)
azc_pfx = Counter(get_prefix(r['word']) for r in all_azc_rcs)
a_pfx = Counter(get_prefix(r['word']) for r in currier_a)
b_pfx = Counter(get_prefix(r['word']) for r in currier_b)

print(f"    {'PREFIX':<10} {'P-text%':<10} {'AZC%':<10} {'A%':<10} {'B%':<10} {'P closest to':<15}")
print(f"    {'-'*65}")

for pfx in ['ch', 'sh', 'da', 'ok', 'ot', 'qo', 'qok', 'ol', 'al', 'other']:
    p_pct = 100 * p_pfx.get(pfx, 0) / len(all_p) if all_p else 0
    azc_pct = 100 * azc_pfx.get(pfx, 0) / len(all_azc_rcs) if all_azc_rcs else 0
    a_pct = 100 * a_pfx.get(pfx, 0) / len(currier_a) if currier_a else 0
    b_pct = 100 * b_pfx.get(pfx, 0) / len(currier_b) if currier_b else 0

    # Which is P closest to?
    diffs = {'AZC': abs(p_pct - azc_pct), 'A': abs(p_pct - a_pct), 'B': abs(p_pct - b_pct)}
    closest = min(diffs, key=diffs.get)

    print(f"    {pfx:<10} {p_pct:<10.1f} {azc_pct:<10.1f} {a_pct:<10.1f} {b_pct:<10.1f} {closest:<15}")

# Statistical test: Is P more similar to A or AZC?
print(f"\n[5] Statistical similarity assessment:")

# Calculate cosine similarity of PREFIX distributions
def cosine_sim(c1, c2, all_keys):
    v1 = np.array([c1.get(k, 0) for k in all_keys])
    v2 = np.array([c2.get(k, 0) for k in all_keys])
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

all_pfx_keys = set(p_pfx.keys()) | set(azc_pfx.keys()) | set(a_pfx.keys()) | set(b_pfx.keys())
sim_p_azc = cosine_sim(p_pfx, azc_pfx, all_pfx_keys)
sim_p_a = cosine_sim(p_pfx, a_pfx, all_pfx_keys)
sim_p_b = cosine_sim(p_pfx, b_pfx, all_pfx_keys)

print(f"    PREFIX cosine similarity:")
print(f"      P vs AZC R/C/S: {sim_p_azc:.4f}")
print(f"      P vs Currier A: {sim_p_a:.4f}")
print(f"      P vs Currier B: {sim_p_b:.4f}")

# Verdict
print(f"\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

if sim_p_a > sim_p_azc and sim_p_a > sim_p_b:
    print(f"\n    P-placement text is MOST SIMILAR TO CURRIER A")
    print(f"    Similarity: A={sim_p_a:.3f} > AZC={sim_p_azc:.3f} > B={sim_p_b:.3f}")
elif sim_p_azc > sim_p_a and sim_p_azc > sim_p_b:
    print(f"\n    P-placement text is MOST SIMILAR TO AZC R/C/S")
    print(f"    Similarity: AZC={sim_p_azc:.3f} > A={sim_p_a:.3f} > B={sim_p_b:.3f}")
else:
    print(f"\n    P-placement text is MOST SIMILAR TO CURRIER B")
    print(f"    Similarity: B={sim_p_b:.3f} > A={sim_p_a:.3f} > AZC={sim_p_azc:.3f}")

print(f"\n    IMPLICATION: P-text may be MISCLASSIFIED as AZC")
print(f"    Consider: These may be Currier A-like entries placed in AZC folios")
