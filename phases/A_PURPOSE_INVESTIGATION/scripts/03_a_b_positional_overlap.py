"""
03_a_b_positional_overlap.py - Test if A vocabulary = B MIDDLE position vocabulary

Hypothesis: A logs material-specific vocabulary, not universal operations.
- B EARLY/LATE positions have universal operations (not in A)
- B MIDDLE positions have context-specific vocabulary (logged in A)

Test: Does A vocabulary concentrate in B's MIDDLE positions?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np

tx = Transcript()
morph = Morphology()

# Get all tokens
a_tokens = list(tx.currier_a())
b_tokens = list(tx.currier_b())

print(f"Currier A tokens: {len(a_tokens)}")
print(f"Currier B tokens: {len(b_tokens)}")

# Build A vocabulary (all MIDDLEs)
a_middles = set()
for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        a_middles.add(m.middle)

print(f"A unique MIDDLEs: {len(a_middles)}")

# ============================================================
# Build B vocabulary by position zone
# ============================================================
print("\n" + "="*70)
print("B VOCABULARY BY WITHIN-LINE POSITION")
print("="*70)

# Group B tokens by line to compute positions
b_lines = defaultdict(list)
for t in b_tokens:
    key = (t.folio, t.line)
    b_lines[key].append(t)

# Compute position for each B token and categorize
b_early_middles = set()    # position < 0.33
b_middle_middles = set()   # position 0.33 - 0.67
b_late_middles = set()     # position >= 0.67

b_early_tokens = []
b_middle_tokens = []
b_late_tokens = []

for key, tokens in b_lines.items():
    n = len(tokens)
    for i, t in enumerate(tokens):
        m = morph.extract(t.word)
        if not m or not m.middle:
            continue

        # Compute normalized position
        if n == 1:
            pos = 0.5
        else:
            pos = i / (n - 1)

        mid = m.middle

        if pos < 0.33:
            b_early_middles.add(mid)
            b_early_tokens.append(mid)
        elif pos < 0.67:
            b_middle_middles.add(mid)
            b_middle_tokens.append(mid)
        else:
            b_late_middles.add(mid)
            b_late_tokens.append(mid)

print(f"\nB vocabulary by position zone (unique MIDDLEs):")
print(f"  EARLY (<0.33):  {len(b_early_middles)}")
print(f"  MIDDLE (0.33-0.67): {len(b_middle_middles)}")
print(f"  LATE (>=0.67):  {len(b_late_middles)}")

print(f"\nB tokens by position zone:")
print(f"  EARLY:  {len(b_early_tokens)}")
print(f"  MIDDLE: {len(b_middle_tokens)}")
print(f"  LATE:   {len(b_late_tokens)}")

# ============================================================
# Compute A overlap with each B position zone
# ============================================================
print("\n" + "="*70)
print("A VOCABULARY OVERLAP WITH B POSITION ZONES")
print("="*70)

a_in_b_early = a_middles & b_early_middles
a_in_b_middle = a_middles & b_middle_middles
a_in_b_late = a_middles & b_late_middles

print(f"\nA MIDDLEs appearing in B zones:")
print(f"  A in B_EARLY:  {len(a_in_b_early)} ({100*len(a_in_b_early)/len(a_middles):.1f}% of A)")
print(f"  A in B_MIDDLE: {len(a_in_b_middle)} ({100*len(a_in_b_middle)/len(a_middles):.1f}% of A)")
print(f"  A in B_LATE:   {len(a_in_b_late)} ({100*len(a_in_b_late)/len(a_middles):.1f}% of A)")

# What fraction of each B zone is covered by A?
print(f"\nB zone coverage by A:")
print(f"  B_EARLY covered by A:  {len(a_in_b_early)}/{len(b_early_middles)} ({100*len(a_in_b_early)/len(b_early_middles):.1f}%)")
print(f"  B_MIDDLE covered by A: {len(a_in_b_middle)}/{len(b_middle_middles)} ({100*len(a_in_b_middle)/len(b_middle_middles):.1f}%)")
print(f"  B_LATE covered by A:   {len(a_in_b_late)}/{len(b_late_middles)} ({100*len(a_in_b_late)/len(b_late_middles):.1f}%)")

# ============================================================
# Exclusive vocabulary analysis
# ============================================================
print("\n" + "="*70)
print("EXCLUSIVE VOCABULARY ANALYSIS")
print("="*70)

# B vocabulary that ONLY appears in one zone
b_early_only = b_early_middles - b_middle_middles - b_late_middles
b_middle_only = b_middle_middles - b_early_middles - b_late_middles
b_late_only = b_late_middles - b_early_middles - b_middle_middles

print(f"\nB zone-exclusive vocabulary:")
print(f"  EARLY-only:  {len(b_early_only)} MIDDLEs")
print(f"  MIDDLE-only: {len(b_middle_only)} MIDDLEs")
print(f"  LATE-only:   {len(b_late_only)} MIDDLEs")

# How much of zone-exclusive B is in A?
a_in_early_only = a_middles & b_early_only
a_in_middle_only = a_middles & b_middle_only
a_in_late_only = a_middles & b_late_only

print(f"\nA coverage of zone-exclusive B vocabulary:")
print(f"  A in EARLY-only:  {len(a_in_early_only)}/{len(b_early_only)} ({100*len(a_in_early_only)/len(b_early_only):.1f}%)" if b_early_only else "  A in EARLY-only:  N/A")
print(f"  A in MIDDLE-only: {len(a_in_middle_only)}/{len(b_middle_only)} ({100*len(a_in_middle_only)/len(b_middle_only):.1f}%)" if b_middle_only else "  A in MIDDLE-only: N/A")
print(f"  A in LATE-only:   {len(a_in_late_only)}/{len(b_late_only)} ({100*len(a_in_late_only)/len(b_late_only):.1f}%)" if b_late_only else "  A in LATE-only:   N/A")

# ============================================================
# Token frequency analysis
# ============================================================
print("\n" + "="*70)
print("TOKEN FREQUENCY BY POSITION AND A-MEMBERSHIP")
print("="*70)

# For B tokens, what fraction come from A vocabulary?
early_from_a = sum(1 for m in b_early_tokens if m in a_middles)
middle_from_a = sum(1 for m in b_middle_tokens if m in a_middles)
late_from_a = sum(1 for m in b_late_tokens if m in a_middles)

print(f"\nB tokens using A vocabulary (by position):")
print(f"  EARLY:  {early_from_a}/{len(b_early_tokens)} ({100*early_from_a/len(b_early_tokens):.1f}%)")
print(f"  MIDDLE: {middle_from_a}/{len(b_middle_tokens)} ({100*middle_from_a/len(b_middle_tokens):.1f}%)")
print(f"  LATE:   {late_from_a}/{len(b_late_tokens)} ({100*late_from_a/len(b_late_tokens):.1f}%)")

# ============================================================
# Top vocabulary comparison
# ============================================================
print("\n" + "="*70)
print("TOP B VOCABULARY BY ZONE (in A or not)")
print("="*70)

early_counter = Counter(b_early_tokens)
middle_counter = Counter(b_middle_tokens)
late_counter = Counter(b_late_tokens)

print("\nTop 10 B EARLY MIDDLEs:")
for mid, count in early_counter.most_common(10):
    in_a = "in A" if mid in a_middles else "NOT in A"
    print(f"  {mid:<12} {count:>5} ({in_a})")

print("\nTop 10 B MIDDLE MIDDLEs:")
for mid, count in middle_counter.most_common(10):
    in_a = "in A" if mid in a_middles else "NOT in A"
    print(f"  {mid:<12} {count:>5} ({in_a})")

print("\nTop 10 B LATE MIDDLEs:")
for mid, count in late_counter.most_common(10):
    in_a = "in A" if mid in a_middles else "NOT in A"
    print(f"  {mid:<12} {count:>5} ({in_a})")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

early_coverage = len(a_in_b_early)/len(b_early_middles)
middle_coverage = len(a_in_b_middle)/len(b_middle_middles)
late_coverage = len(a_in_b_late)/len(b_late_middles)

early_token_rate = early_from_a/len(b_early_tokens)
middle_token_rate = middle_from_a/len(b_middle_tokens)
late_token_rate = late_from_a/len(b_late_tokens)

print(f"""
B zone coverage by A vocabulary:
  EARLY:  {early_coverage:.1%} (types), {early_token_rate:.1%} (tokens)
  MIDDLE: {middle_coverage:.1%} (types), {middle_token_rate:.1%} (tokens)
  LATE:   {late_coverage:.1%} (types), {late_token_rate:.1%} (tokens)

Interpretation:
""")

if middle_coverage > early_coverage and middle_coverage > late_coverage:
    print("  A vocabulary concentrates in B MIDDLE positions")
    print("  -> A logs material/context vocabulary, not universal operations")
    verdict = "SUPPORTS"
elif middle_token_rate > early_token_rate and middle_token_rate > late_token_rate:
    print("  A vocabulary usage concentrates in B MIDDLE positions")
    print("  -> A logs material/context vocabulary")
    verdict = "SUPPORTS"
else:
    print("  No clear positional concentration")
    verdict = "INCONCLUSIVE"

# Save results
output = {
    'a_middles_count': len(a_middles),
    'b_zone_vocab': {
        'early': len(b_early_middles),
        'middle': len(b_middle_middles),
        'late': len(b_late_middles)
    },
    'a_coverage_of_b_zones': {
        'early': float(early_coverage),
        'middle': float(middle_coverage),
        'late': float(late_coverage)
    },
    'a_token_rates_in_b_zones': {
        'early': float(early_token_rate),
        'middle': float(middle_token_rate),
        'late': float(late_token_rate)
    },
    'verdict': verdict
}

with open('C:/git/voynich/phases/A_PURPOSE_INVESTIGATION/results/a_b_positional_overlap.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to a_b_positional_overlap.json")
