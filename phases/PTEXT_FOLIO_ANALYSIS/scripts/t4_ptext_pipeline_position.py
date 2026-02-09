#!/usr/bin/env python3
"""
Test 4: P-text Position in Pipeline

Questions:
- Do P-text MIDDLEs appear in Currier B execution?
- Does P-text vocabulary track with high-escape B behavior (C486)?
- Is P-text a registry subset that correlates with B recovery?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter, defaultdict
from scripts.voynich import Morphology, Transcript
import numpy as np
from scipy import stats

# Initialize
morph = Morphology()
tx = Transcript()

# Load P-text MIDDLEs
filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

ptext_tokens = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue
            currier = parts[6].strip('"').strip()
            placement = parts[10].strip('"').strip()
            token = parts[0].strip('"').strip().lower()

            if currier == 'NA' and (placement == 'P' or placement.startswith('P')):
                if token.strip() and '*' not in token:
                    ptext_tokens.append(token)

def get_middles(tokens):
    """Extract unique MIDDLEs."""
    middles = set()
    for t in tokens:
        m = morph.extract(t)
        if m.middle:
            middles.add(m.middle)
    return middles

ptext_middles = get_middles(ptext_tokens)

print("=" * 70)
print("TEST 4: P-TEXT POSITION IN PIPELINE")
print("=" * 70)
print()

# 1. P-text MIDDLEs in Currier B
print("1. P-TEXT MIDDLES IN CURRIER B")
print("-" * 50)

b_tokens = list(tx.currier_b())
b_middles = get_middles([t.word for t in b_tokens])

ptext_in_b = ptext_middles & b_middles
ptext_not_in_b = ptext_middles - b_middles

print(f"P-text MIDDLEs: {len(ptext_middles)}")
print(f"B MIDDLEs: {len(b_middles)}")
print(f"P-text MIDDLEs that appear in B: {len(ptext_in_b)} ({len(ptext_in_b)/len(ptext_middles):.1%})")
print(f"P-text MIDDLEs NOT in B: {len(ptext_not_in_b)} ({len(ptext_not_in_b)/len(ptext_middles):.1%})")
print()

if ptext_not_in_b:
    print(f"P-text exclusive (not in B): {sorted(ptext_not_in_b)[:15]}")
print()

# 2. Currier A comparison
print("2. CURRIER A COMPARISON")
print("-" * 50)

a_tokens = list(tx.currier_a())
a_middles = get_middles([t.word for t in a_tokens])

a_in_b = a_middles & b_middles
print(f"Currier A MIDDLEs: {len(a_middles)}")
print(f"A MIDDLEs that appear in B: {len(a_in_b)} ({len(a_in_b)/len(a_middles):.1%})")
print()

# Compare P-text to A overlap rate with B
p_to_b_rate = len(ptext_in_b) / len(ptext_middles)
a_to_b_rate = len(a_in_b) / len(a_middles)
print(f"P-text to B overlap rate: {p_to_b_rate:.1%}")
print(f"Full A to B overlap rate: {a_to_b_rate:.1%}")

if p_to_b_rate > a_to_b_rate:
    print(f"=> P-text has HIGHER B-overlap than average A ({p_to_b_rate - a_to_b_rate:+.1%})")
else:
    print(f"=> P-text has LOWER B-overlap than average A ({p_to_b_rate - a_to_b_rate:+.1%})")
print()

# 3. High-escape folio analysis (per C486)
print("3. HIGH-ESCAPE B FOLIO ANALYSIS (C486)")
print("-" * 50)
print("C486 claims P-zone vocabulary correlates with high-escape B behavior.")
print("Testing: Do high-escape B folios use more P-text MIDDLEs?")
print()

# Calculate escape rates per B folio
# Escape = when execution doesn't converge to stable state
# Proxy: unique MIDDLE diversity (higher = more variation = more escape)
folio_middles = defaultdict(set)
folio_tokens = defaultdict(list)

for t in b_tokens:
    m = morph.extract(t.word)
    if m.middle:
        folio_middles[t.folio].add(m.middle)
        folio_tokens[t.folio].append(t.word)

# Metric: proportion of folio's MIDDLEs that come from P-text
folio_ptext_ratio = {}
for folio, middles in folio_middles.items():
    ptext_overlap = middles & ptext_middles
    folio_ptext_ratio[folio] = len(ptext_overlap) / len(middles) if middles else 0

# Metric: type/token ratio as escape proxy (higher = more diverse = more escape)
folio_ttr = {}
for folio, tokens in folio_tokens.items():
    types = len(set(tokens))
    folio_ttr[folio] = types / len(tokens) if tokens else 0

# Correlation between P-text overlap and TTR
folios = sorted(set(folio_ptext_ratio.keys()) & set(folio_ttr.keys()))
x = [folio_ptext_ratio[f] for f in folios]
y = [folio_ttr[f] for f in folios]

if len(x) > 2:
    r, p = stats.pearsonr(x, y)
    print(f"Correlation (P-text ratio vs TTR): r={r:.3f}, p={p:.4f}")

    if p < 0.05:
        if r > 0:
            print("=> SIGNIFICANT POSITIVE: Folios using more P-text MIDDLEs have higher TTR")
        else:
            print("=> SIGNIFICANT NEGATIVE: Folios using more P-text MIDDLEs have lower TTR")
    else:
        print("=> NOT SIGNIFICANT: P-text usage doesn't predict B folio TTR")
print()

# 4. Top/bottom analysis
print("4. TOP vs BOTTOM B FOLIOS BY P-TEXT OVERLAP")
print("-" * 50)

sorted_folios = sorted(folio_ptext_ratio.items(), key=lambda x: -x[1])
top_5 = sorted_folios[:5]
bottom_5 = sorted_folios[-5:]

print("TOP 5 (highest P-text MIDDLE overlap):")
for folio, ratio in top_5:
    ttr = folio_ttr.get(folio, 0)
    print(f"  {folio}: {ratio:.1%} P-text overlap, TTR={ttr:.3f}")

print()
print("BOTTOM 5 (lowest P-text MIDDLE overlap):")
for folio, ratio in bottom_5:
    ttr = folio_ttr.get(folio, 0)
    print(f"  {folio}: {ratio:.1%} P-text overlap, TTR={ttr:.3f}")
print()

# 5. Key insight: which P-text MIDDLEs drive the correlation?
print("5. MOST COMMON P-TEXT MIDDLES IN CURRIER B")
print("-" * 50)

# Count P-text MIDDLEs across all B
ptext_in_b_counts = Counter()
for t in b_tokens:
    m = morph.extract(t.word)
    if m.middle and m.middle in ptext_middles:
        ptext_in_b_counts[m.middle] += 1

print("Top 15 P-text MIDDLEs in B (by frequency):")
for mid, count in ptext_in_b_counts.most_common(15):
    print(f"  {mid}: {count}")
print()

# 6. Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
P-text Pipeline Position Analysis:

1. P-TEXT TO B TRANSMISSION:
   - {len(ptext_in_b)}/{len(ptext_middles)} P-text MIDDLEs ({len(ptext_in_b)/len(ptext_middles):.1%}) appear in B
   - Compare: {len(a_in_b)/len(a_middles):.1%} of all A MIDDLEs appear in B
   - P-text has {'HIGHER' if p_to_b_rate > a_to_b_rate else 'LOWER'} B-transmission than average A

2. C486 CORRELATION (P-text vs high-escape B):
   - Correlation test: r={r:.3f}, p={p:.4f}
   - {'SUPPORTS' if p < 0.05 and r > 0 else 'DOES NOT SUPPORT'} C486 claim

3. INTERPRETATION:
   P-text vocabulary {'IS' if p_to_b_rate > a_to_b_rate else 'is NOT'} enriched in B execution
   compared to average Currier A vocabulary.

   This suggests P-text may {'represent a privileged subset of A vocabulary' if p_to_b_rate > a_to_b_rate else 'be no different from regular A in B transmission'}.
""")
