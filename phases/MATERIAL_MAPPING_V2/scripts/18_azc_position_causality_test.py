"""
18_azc_position_causality_test.py

TEST: Does AZC position actually predict B behavior?

Method:
1. Find tokens that appear at different AZC positions (P, R1, R2, R3, S, C)
2. For tokens appearing at multiple positions, check if B behavior differs
3. Compare B escape rates for P-position vocabulary vs R/S-position vocabulary

This tests whether AZC position is CAUSAL or just CORRELATED with B behavior.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

print("="*70)
print("AZC POSITION CAUSALITY TEST")
print("="*70)
print("Question: Does AZC position CAUSE different B behavior,")
print("          or is the correlation due to vocabulary differences?")

tx = Transcript()
morph = Morphology()

# Step 1: Build vocabulary by AZC position
print("\n" + "="*70)
print("STEP 1: CATALOG AZC TOKENS BY POSITION")
print("="*70)

# Position classification based on placement codes
def classify_position(placement):
    """Classify AZC placement into position zones."""
    if not placement:
        return None
    p = placement.upper()
    if p.startswith('C'):
        return 'C'
    elif p.startswith('P'):
        return 'P'
    elif p.startswith('R1') or p == 'R1':
        return 'R1'
    elif p.startswith('R2') or p == 'R2':
        return 'R2'
    elif p.startswith('R3') or p == 'R3':
        return 'R3'
    elif p.startswith('S'):
        return 'S'
    elif 'R1' in p:
        return 'R1'
    elif 'R2' in p:
        return 'R2'
    elif 'R3' in p:
        return 'R3'
    return 'OTHER'

# Collect tokens by position
position_tokens = defaultdict(set)  # position -> set of words
token_positions = defaultdict(set)  # word -> set of positions

azc_count = 0
for t in tx.azc():
    azc_count += 1
    pos = classify_position(t.placement)
    if pos and pos != 'OTHER':
        position_tokens[pos].add(t.word)
        token_positions[t.word].add(pos)

print(f"\nTotal AZC tokens: {azc_count}")
print(f"\nTokens by position:")
for pos in ['C', 'P', 'R1', 'R2', 'R3', 'S']:
    print(f"  {pos}: {len(position_tokens[pos])} unique tokens")

# Step 2: Find tokens appearing at multiple positions
print("\n" + "="*70)
print("STEP 2: TOKENS AT MULTIPLE POSITIONS")
print("="*70)

multi_position = {w: pos for w, pos in token_positions.items() if len(pos) > 1}
print(f"\nTokens appearing at multiple positions: {len(multi_position)}")

# Categorize by position combinations
combo_counts = Counter(tuple(sorted(pos)) for pos in multi_position.values())
print(f"\nPosition combinations:")
for combo, count in combo_counts.most_common(10):
    print(f"  {'+'.join(combo)}: {count} tokens")

# Step 3: Define high-escape vs low-escape position groups
print("\n" + "="*70)
print("STEP 3: HIGH-ESCAPE VS LOW-ESCAPE POSITION GROUPS")
print("="*70)
print("Per C443: P=11-25%, R1=2%, R2=1.2%, R3=0%, S=0%")

high_escape_positions = {'P'}
low_escape_positions = {'R3', 'S'}
medium_positions = {'R1', 'R2', 'C'}

high_escape_vocab = position_tokens['P']
low_escape_vocab = position_tokens['R3'] | position_tokens['S']

# Tokens ONLY in high-escape positions
only_high = high_escape_vocab - low_escape_vocab
# Tokens ONLY in low-escape positions
only_low = low_escape_vocab - high_escape_vocab
# Tokens in BOTH
both = high_escape_vocab & low_escape_vocab

print(f"\nVocabulary groups:")
print(f"  Only high-escape (P only): {len(only_high)} tokens")
print(f"  Only low-escape (R3/S only): {len(only_low)} tokens")
print(f"  BOTH high and low positions: {len(both)} tokens")

# Step 4: Measure B behavior for each group
print("\n" + "="*70)
print("STEP 4: B BEHAVIOR BY AZC POSITION GROUP")
print("="*70)

# Collect B tokens
b_tokens = list(tx.currier_b())
print(f"\nTotal B tokens: {len(b_tokens)}")

# For each group, find matching B tokens and compute escape proxy
# Using 'q' as escape character (qo- prefix indicates escape)
def compute_escape_rate(token_set, b_tokens):
    """Compute escape proxy rate for tokens in set."""
    matches = [t for t in b_tokens if t.word in token_set]
    if not matches:
        return 0, 0, 0

    escape_count = 0
    for t in matches:
        # Check if word starts with escape-associated patterns
        if t.word.startswith('qo') or t.word.startswith('q') and not t.word.startswith('qk'):
            escape_count += 1

    return len(matches), escape_count, escape_count / len(matches) if matches else 0

# Better approach: use morphological analysis for escape detection
def compute_escape_rate_morph(token_set, b_tokens, morph):
    """Compute escape rate using morphological prefix analysis."""
    matches = [t for t in b_tokens if t.word in token_set]
    if not matches:
        return 0, 0, 0

    escape_prefixes = {'qo'}  # ESCAPE role per BCSC
    escape_count = 0

    for t in matches:
        try:
            m = morph.extract(t.word)
            if m.prefix in escape_prefixes:
                escape_count += 1
        except:
            pass

    return len(matches), escape_count, escape_count / len(matches) if matches else 0

print("\nEscape rate (qo- prefix) by AZC position group:")

n_high, esc_high, rate_high = compute_escape_rate_morph(only_high, b_tokens, morph)
n_low, esc_low, rate_low = compute_escape_rate_morph(only_low, b_tokens, morph)
n_both, esc_both, rate_both = compute_escape_rate_morph(both, b_tokens, morph)

print(f"\n  Only HIGH-escape positions (P):")
print(f"    B tokens: {n_high}, escape: {esc_high}, rate: {rate_high:.4f}")

print(f"\n  Only LOW-escape positions (R3/S):")
print(f"    B tokens: {n_low}, escape: {esc_low}, rate: {rate_low:.4f}")

print(f"\n  BOTH positions:")
print(f"    B tokens: {n_both}, escape: {esc_both}, rate: {rate_both:.4f}")

# Step 5: The critical test - tokens in BOTH positions
print("\n" + "="*70)
print("STEP 5: CRITICAL TEST - SAME TOKENS, DIFFERENT POSITIONS")
print("="*70)

if both:
    print(f"\n{len(both)} tokens appear in BOTH high-escape (P) AND low-escape (R3/S) positions.")
    print("If AZC position is causal, these tokens should show INTERMEDIATE B behavior.")
    print("If position is NOT causal, they should behave like one group or the other.")

    print(f"\nResult: escape rate = {rate_both:.4f}")
    print(f"  vs HIGH-only: {rate_high:.4f}")
    print(f"  vs LOW-only: {rate_low:.4f}")

    if rate_high > 0 and rate_low < rate_high:
        if rate_both > rate_low and rate_both < rate_high:
            print("\n  --> INTERMEDIATE: Consistent with position having some effect")
        elif abs(rate_both - rate_high) < abs(rate_both - rate_low):
            print("\n  --> CLOSER TO HIGH: Position may not be the driver")
        else:
            print("\n  --> CLOSER TO LOW: Position may not be the driver")
else:
    print("\nNo tokens appear in both high and low escape positions.")
    print("Cannot run critical same-token test.")

# Step 6: Alternative test - compare by MIDDLE, control for vocabulary
print("\n" + "="*70)
print("STEP 6: CONTROL FOR VOCABULARY - SAME MIDDLE, DIFFERENT POSITIONS")
print("="*70)

# Get MIDDLEs that appear at different positions
middle_positions = defaultdict(set)
for t in tx.azc():
    try:
        m = morph.extract(t.word)
        if m.middle:
            pos = classify_position(t.placement)
            if pos and pos != 'OTHER':
                middle_positions[m.middle].add(pos)
    except:
        pass

# MIDDLEs in both high and low
middles_in_high = set()
middles_in_low = set()
for mid, positions in middle_positions.items():
    if 'P' in positions:
        middles_in_high.add(mid)
    if 'R3' in positions or 'S' in positions:
        middles_in_low.add(mid)

middles_in_both = middles_in_high & middles_in_low
middles_only_high = middles_in_high - middles_in_low
middles_only_low = middles_in_low - middles_in_high

print(f"\nMIDDLEs by AZC position:")
print(f"  Only high-escape (P): {len(middles_only_high)}")
print(f"  Only low-escape (R3/S): {len(middles_only_low)}")
print(f"  BOTH: {len(middles_in_both)}")

# Compute B escape rate by MIDDLE group
def escape_rate_by_middles(middle_set, b_tokens, morph):
    matches = []
    escape_count = 0
    for t in b_tokens:
        try:
            m = morph.extract(t.word)
            if m.middle in middle_set:
                matches.append(t)
                if m.prefix == 'qo':
                    escape_count += 1
        except:
            pass
    n = len(matches)
    return n, escape_count, escape_count/n if n > 0 else 0

n_mh, esc_mh, rate_mh = escape_rate_by_middles(middles_only_high, b_tokens, morph)
n_ml, esc_ml, rate_ml = escape_rate_by_middles(middles_only_low, b_tokens, morph)
n_mb, esc_mb, rate_mb = escape_rate_by_middles(middles_in_both, b_tokens, morph)

print(f"\nB escape rate by MIDDLE group:")
print(f"  MIDDLEs only in HIGH positions: {n_mh} tokens, escape={rate_mh:.4f}")
print(f"  MIDDLEs only in LOW positions: {n_ml} tokens, escape={rate_ml:.4f}")
print(f"  MIDDLEs in BOTH positions: {n_mb} tokens, escape={rate_mb:.4f}")

# Step 7: Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
TEST RESULTS:

1. VOCABULARY SEPARATION:
   - {len(only_high)} tokens ONLY in high-escape AZC positions
   - {len(only_low)} tokens ONLY in low-escape AZC positions
   - {len(both)} tokens in BOTH (critical test group)

2. B ESCAPE RATES:
   - High-only vocabulary: {rate_high:.4f}
   - Low-only vocabulary: {rate_low:.4f}
   - Both vocabulary: {rate_both:.4f}

3. MIDDLE-LEVEL ANALYSIS:
   - High-only MIDDLEs: {rate_mh:.4f}
   - Low-only MIDDLEs: {rate_ml:.4f}
   - Both MIDDLEs: {rate_mb:.4f}

INTERPRETATION:
""")

# Interpret results
if rate_high > rate_low * 1.5:
    print("  Escape rates DO differ by AZC position group.")
    if len(both) > 10 and rate_both > rate_low and rate_both < rate_high:
        print("  Tokens in BOTH positions show intermediate behavior.")
        print("  --> CONSISTENT WITH POSITION HAVING CAUSAL EFFECT")
    elif len(both) > 10:
        print("  But tokens in BOTH positions don't show intermediate behavior.")
        print("  --> POSITION EFFECT MAY BE CONFOUNDED WITH VOCABULARY")
    else:
        print("  Too few tokens in both positions to test intermediate behavior.")
else:
    print("  Escape rates do NOT significantly differ by AZC position.")
    print("  --> NO EVIDENCE FOR POSITION CAUSALITY")
