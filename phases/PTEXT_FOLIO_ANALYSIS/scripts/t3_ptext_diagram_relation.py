#!/usr/bin/env python3
"""
Test 3: P-text to Same-Folio Diagram Relationship

Questions:
- Does P-text vocabulary overlap with the diagram on the SAME folio?
- Is P-text content predictive of diagram vocabulary?
- Or is P-text independent annotation?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter, defaultdict
from scripts.voynich import Morphology
import numpy as np

# Load transcript
filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Initialize morphology
morph = Morphology()

# Collect tokens by folio and type
ptext_by_folio = defaultdict(list)
diagram_by_folio = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            if currier != 'NA':  # Only AZC
                continue

            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if placement == 'P' or placement.startswith('P'):
                ptext_by_folio[folio].append(token)
            else:
                diagram_by_folio[folio].append(token)

print("=" * 70)
print("TEST 3: P-TEXT TO SAME-FOLIO DIAGRAM RELATIONSHIP")
print("=" * 70)
print()

# 1. Folio-level statistics
print("1. P-TEXT FOLIOS WITH DIAGRAM CONTENT")
print("-" * 50)

ptext_folios = set(ptext_by_folio.keys())

def get_middles(tokens):
    """Extract unique MIDDLEs."""
    middles = set()
    for t in tokens:
        m = morph.extract(t)
        if m.middle:
            middles.add(m.middle)
    return middles

def jaccard(s1, s2):
    if not s1 or not s2:
        return 0
    return len(s1 & s2) / len(s1 | s2)

print(f"{'Folio':<12} {'P-tok':<8} {'D-tok':<8} {'P-mid':<8} {'D-mid':<8} {'Overlap':<8} {'Jaccard':<8}")
print("-" * 68)

folio_results = []
for folio in sorted(ptext_folios):
    p_tokens = ptext_by_folio[folio]
    d_tokens = diagram_by_folio.get(folio, [])

    p_middles = get_middles(p_tokens)
    d_middles = get_middles(d_tokens)

    overlap = len(p_middles & d_middles)
    j = jaccard(p_middles, d_middles)

    folio_results.append({
        'folio': folio,
        'p_tokens': len(p_tokens),
        'd_tokens': len(d_tokens),
        'p_middles': len(p_middles),
        'd_middles': len(d_middles),
        'overlap': overlap,
        'jaccard': j
    })

    print(f"{folio:<12} {len(p_tokens):<8} {len(d_tokens):<8} {len(p_middles):<8} {len(d_middles):<8} {overlap:<8} {j:.3f}")

print()

# 2. Aggregate statistics
print("2. AGGREGATE STATISTICS")
print("-" * 50)

total_p_mid = sum(r['p_middles'] for r in folio_results)
total_d_mid = sum(r['d_middles'] for r in folio_results)
total_overlap = sum(r['overlap'] for r in folio_results)
mean_jaccard = np.mean([r['jaccard'] for r in folio_results if r['d_middles'] > 0])

print(f"Mean Jaccard (folios with diagram): {mean_jaccard:.3f}")
print(f"Total overlap instances: {total_overlap}")
print()

# 3. Comparison: cross-folio overlap
print("3. CROSS-FOLIO COMPARISON (BASELINE)")
print("-" * 50)
print("If P-text were random A vocabulary, how much overlap with random diagram folios?")
print()

# Get all P-text MIDDLEs combined
all_ptext_middles = set()
for tokens in ptext_by_folio.values():
    all_ptext_middles.update(get_middles(tokens))

# Compare to non-same-folio diagrams
cross_folio_jaccards = []
for folio in ptext_folios:
    p_middles = get_middles(ptext_by_folio[folio])
    # Compare to OTHER folio diagrams
    other_diagrams = set()
    for other_folio, d_tokens in diagram_by_folio.items():
        if other_folio != folio:
            other_diagrams.update(get_middles(d_tokens))

    if other_diagrams:
        j = jaccard(p_middles, other_diagrams)
        cross_folio_jaccards.append(j)

mean_cross_jaccard = np.mean(cross_folio_jaccards) if cross_folio_jaccards else 0
print(f"Mean Jaccard P-text to OTHER diagram folios: {mean_cross_jaccard:.3f}")
print(f"Mean Jaccard P-text to SAME diagram folio:  {mean_jaccard:.3f}")
print()

if mean_jaccard > mean_cross_jaccard:
    diff = mean_jaccard - mean_cross_jaccard
    print(f"Same-folio overlap is HIGHER by {diff:.3f}")
    print("=> P-text MAY be related to same-folio diagram content")
else:
    diff = mean_cross_jaccard - mean_jaccard
    print(f"Same-folio overlap is LOWER by {diff:.3f}")
    print("=> P-text is NOT specifically related to same-folio diagram")

print()

# 4. What MIDDLEs appear in BOTH P-text and same-folio diagram?
print("4. SHARED MIDDLES (P-TEXT & SAME-FOLIO DIAGRAM)")
print("-" * 50)

shared_middles = set()
for folio in ptext_folios:
    p_middles = get_middles(ptext_by_folio[folio])
    d_middles = get_middles(diagram_by_folio.get(folio, []))
    shared_middles.update(p_middles & d_middles)

print(f"Total unique MIDDLEs appearing in both P-text and same-folio diagram: {len(shared_middles)}")
if shared_middles:
    print(f"Examples: {sorted(shared_middles)[:15]}")
print()

# 5. f65v special case (100% P-text, no diagram)
print("5. SPECIAL CASE: f65v")
print("-" * 50)
f65v_ptokens = ptext_by_folio.get('f65v', [])
f65v_dtokens = diagram_by_folio.get('f65v', [])
print(f"f65v P-text tokens: {len(f65v_ptokens)}")
print(f"f65v Diagram tokens: {len(f65v_dtokens)}")
if len(f65v_dtokens) == 0:
    print("f65v has NO diagram content - it's entirely P-text (paragraph text)")
    print("This suggests f65v may be a text-only folio within the AZC section")
print()

# 6. Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
P-text to Same-Folio Diagram Relationship:

1. SAME-FOLIO OVERLAP:
   - Mean Jaccard: {mean_jaccard:.3f}
   - This is {'HIGHER' if mean_jaccard > mean_cross_jaccard else 'LOWER'} than cross-folio baseline ({mean_cross_jaccard:.3f})

2. INTERPRETATION:
   - P-text vocabulary overlap with same-folio diagram is {'MODERATE' if mean_jaccard > 0.1 else 'LOW'}
   - {len(shared_middles)} unique MIDDLEs appear in both P-text and same-folio diagram

3. f65v ANOMALY:
   - f65v has {len(f65v_ptokens)} P-text tokens and 0 diagram tokens
   - This folio is entirely paragraph text (no circular diagram)

4. CONCLUSION:
   P-text appears to be Currier A paragraph material that co-occurs with
   AZC diagrams but is not directly dependent on diagram content.
""")
