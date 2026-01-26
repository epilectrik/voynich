"""
L-COMPOUND BOUNDARY ANALYSIS

Tests whether L-compound operators form symmetric line-initial markers
to complement LATE prefixes at line-final positions.

From C298/C501: L-compound MIDDLEs (lk, lch, lsh, etc.) are B-specific operators.
From C539: LATE prefixes (al, ar, or) are line-final markers.

Questions:
1. What is the mean line position of L-compound tokens?
2. Do L-compounds show the same B-exclusive + PP-MIDDLE pattern?
3. Do L-compounds and LATE prefixes co-occur in lines?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("L-COMPOUND BOUNDARY ANALYSIS")
print("=" * 70)

# =============================================================================
# STEP 1: Identify L-compound tokens
# =============================================================================
print("\n[Step 1] Identifying L-compound tokens...")

# L-compound pattern: MIDDLE starts with 'l' followed by consonant
def is_l_compound(middle):
    if not middle or len(middle) < 2:
        return False
    if middle[0] != 'l':
        return False
    # Second char should be consonant (not a, e, i, o, y)
    return middle[1] not in 'aeioy'

b_tokens = []
l_compound_tokens = []
late_tokens = []

LATE_PREFIXES = {'al', 'ar', 'or'}

for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        entry = {
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        }
        b_tokens.append(entry)

        if is_l_compound(entry['middle']):
            l_compound_tokens.append(entry)

        if entry['prefix'] in LATE_PREFIXES:
            late_tokens.append(entry)

print(f"  Total B tokens: {len(b_tokens)}")
print(f"  L-compound tokens: {len(l_compound_tokens)} ({len(l_compound_tokens)/len(b_tokens)*100:.2f}%)")
print(f"  LATE tokens: {len(late_tokens)} ({len(late_tokens)/len(b_tokens)*100:.2f}%)")

# List L-compound MIDDLEs
l_middles = Counter(t['middle'] for t in l_compound_tokens)
print(f"\n  L-compound MIDDLEs ({len(l_middles)} types):")
for mid, count in l_middles.most_common(15):
    print(f"    {mid}: {count}")

# =============================================================================
# STEP 2: Position analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Position analysis")
print("=" * 70)

# Build line sequences
folio_line_tokens = defaultdict(list)
for tok in b_tokens:
    key = (tok['folio'], tok['line'])
    folio_line_tokens[key].append(tok)

# Compute positions
l_compound_positions = []
late_positions = []
all_positions = []

for key, tokens in folio_line_tokens.items():
    n = len(tokens)
    if n < 2:
        continue
    for i, tok in enumerate(tokens):
        rel_pos = i / (n - 1)
        all_positions.append(rel_pos)

        if is_l_compound(tok['middle']):
            l_compound_positions.append(rel_pos)

        if tok['prefix'] in LATE_PREFIXES:
            late_positions.append(rel_pos)

print(f"\n  L-compound mean position: {np.mean(l_compound_positions):.3f} (n={len(l_compound_positions)})")
print(f"  LATE mean position: {np.mean(late_positions):.3f} (n={len(late_positions)})")
print(f"  Overall mean position: {np.mean(all_positions):.3f}")

# Line-initial enrichment for L-compounds
l_at_start = sum(1 for p in l_compound_positions if p == 0)
baseline_start = len(all_positions) / len(folio_line_tokens)  # ~1 token per line at pos 0

print(f"\n  L-compound at line-initial (pos=0): {l_at_start}/{len(l_compound_positions)} ({l_at_start/len(l_compound_positions)*100:.1f}%)")
print(f"  LATE at line-final (pos=1): {sum(1 for p in late_positions if p == 1)}/{len(late_positions)} ({sum(1 for p in late_positions if p == 1)/len(late_positions)*100:.1f}%)")

# =============================================================================
# STEP 3: Provenance analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Provenance analysis (B-exclusive vs PP)")
print("=" * 70)

# Get A vocabulary
a_words = set()
a_middles = set()

for token in tx.currier_a():
    if token.word:
        m = morph.extract(token.word)
        a_words.add(token.word)
        if m.middle:
            a_middles.add(m.middle)

# L-compound provenance
l_words = set(t['word'] for t in l_compound_tokens)
l_middles_set = set(t['middle'] for t in l_compound_tokens if t['middle'])

l_words_shared = l_words & a_words
l_words_b_exclusive = l_words - a_words
l_middles_shared = l_middles_set & a_middles
l_middles_b_exclusive = l_middles_set - a_middles

print(f"\n  L-compound TOKENS:")
print(f"    Total unique: {len(l_words)}")
print(f"    B-exclusive: {len(l_words_b_exclusive)} ({len(l_words_b_exclusive)/len(l_words)*100:.1f}%)")
print(f"    Shared with A: {len(l_words_shared)} ({len(l_words_shared)/len(l_words)*100:.1f}%)")

print(f"\n  L-compound MIDDLEs:")
print(f"    Total unique: {len(l_middles_set)}")
print(f"    B-exclusive: {len(l_middles_b_exclusive)} ({len(l_middles_b_exclusive)/len(l_middles_set)*100:.1f}%)")
print(f"    Shared with A (PP): {len(l_middles_shared)} ({len(l_middles_shared)/len(l_middles_set)*100:.1f}%)")

# Compare to LATE
print(f"\n  Comparison to LATE prefixes:")
print(f"    LATE: 85.4% B-exclusive tokens, 76.2% PP MIDDLEs")
print(f"    L-compound: {len(l_words_b_exclusive)/len(l_words)*100:.1f}% B-exclusive tokens, {len(l_middles_shared)/len(l_middles_set)*100:.1f}% PP MIDDLEs")

# =============================================================================
# STEP 4: Co-occurrence analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Co-occurrence analysis")
print("=" * 70)

# Count lines with L-compound, LATE, both, neither
lines_with_l = set()
lines_with_late = set()

for tok in l_compound_tokens:
    lines_with_l.add((tok['folio'], tok['line']))

for tok in late_tokens:
    lines_with_late.add((tok['folio'], tok['line']))

all_lines = set(folio_line_tokens.keys())
lines_with_both = lines_with_l & lines_with_late
lines_with_either = lines_with_l | lines_with_late
lines_with_neither = all_lines - lines_with_either

print(f"\n  Total lines (2+ tokens): {len(all_lines)}")
print(f"  Lines with L-compound: {len(lines_with_l)} ({len(lines_with_l)/len(all_lines)*100:.1f}%)")
print(f"  Lines with LATE: {len(lines_with_late)} ({len(lines_with_late)/len(all_lines)*100:.1f}%)")
print(f"  Lines with BOTH: {len(lines_with_both)} ({len(lines_with_both)/len(all_lines)*100:.1f}%)")
print(f"  Lines with NEITHER: {len(lines_with_neither)} ({len(lines_with_neither)/len(all_lines)*100:.1f}%)")

# Expected co-occurrence under independence
p_l = len(lines_with_l) / len(all_lines)
p_late = len(lines_with_late) / len(all_lines)
expected_both = p_l * p_late * len(all_lines)

print(f"\n  Expected co-occurrence (independence): {expected_both:.1f}")
print(f"  Observed co-occurrence: {len(lines_with_both)}")
print(f"  Ratio (obs/exp): {len(lines_with_both)/expected_both:.2f}x")

# =============================================================================
# STEP 5: Bracket structure test
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Bracket structure test")
print("=" * 70)

# In lines with both, check if L-compound comes before LATE
bracket_correct = 0
bracket_reversed = 0

for key in lines_with_both:
    tokens = folio_line_tokens[key]

    # Find positions of L-compound and LATE tokens
    l_positions = []
    late_positions_in_line = []

    for i, tok in enumerate(tokens):
        if is_l_compound(tok['middle']):
            l_positions.append(i)
        if tok['prefix'] in LATE_PREFIXES:
            late_positions_in_line.append(i)

    # Check if any L-compound comes before any LATE
    min_l = min(l_positions) if l_positions else float('inf')
    max_late = max(late_positions_in_line) if late_positions_in_line else float('-inf')

    if min_l < max_late:
        bracket_correct += 1
    else:
        bracket_reversed += 1

print(f"\n  Lines with both L-compound and LATE: {len(lines_with_both)}")
print(f"  Bracket order [L...LATE]: {bracket_correct} ({bracket_correct/len(lines_with_both)*100:.1f}%)")
print(f"  Reversed order [LATE...L]: {bracket_reversed} ({bracket_reversed/len(lines_with_both)*100:.1f}%)")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
FINDINGS:

1. POSITION:
   - L-compound mean position: {np.mean(l_compound_positions):.3f} (vs LATE: {np.mean(late_positions):.3f})
   - L-compounds are {'EARLY' if np.mean(l_compound_positions) < 0.4 else 'NOT early'} in lines
   - LATE prefixes are {'LATE' if np.mean(late_positions) > 0.6 else 'NOT late'} in lines

2. PROVENANCE:
   - L-compound: {len(l_words_b_exclusive)/len(l_words)*100:.1f}% B-exclusive tokens
   - LATE: 85.4% B-exclusive tokens
   - {'SIMILAR' if abs(len(l_words_b_exclusive)/len(l_words)*100 - 85.4) < 15 else 'DIFFERENT'} pattern

3. CO-OCCURRENCE:
   - Observed/Expected: {len(lines_with_both)/expected_both:.2f}x
   - {'ENRICHED' if len(lines_with_both)/expected_both > 1.2 else 'DEPLETED' if len(lines_with_both)/expected_both < 0.8 else 'INDEPENDENT'}

4. BRACKET STRUCTURE:
   - [L...LATE] order: {bracket_correct/len(lines_with_both)*100:.1f}%
   - {'CONSISTENT' if bracket_correct/len(lines_with_both) > 0.7 else 'INCONSISTENT'} bracketing
""")

if (np.mean(l_compound_positions) < 0.4 and
    len(lines_with_both)/expected_both > 1.0 and
    bracket_correct/len(lines_with_both) > 0.6):
    print("CONCLUSION: L-compounds and LATE prefixes form SYMMETRIC BOUNDARY MARKERS")
else:
    print("CONCLUSION: Pattern is more complex than simple symmetric bracketing")
