"""Quick look at f57v token structure - are there compound MIDDLEs?"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("f57v TOKEN STRUCTURE")
print("="*70)

# Get all tokens from f57v
f57v_tokens = []
for token in tx.all():
    if token.folio == 'f57v':
        w = token.word.strip()
        if w and '*' not in w:
            m = morph.extract(w)
            f57v_tokens.append({
                'word': w,
                'middle': m.middle,
                'placement': token.placement,
                'line': token.line,
                'length': len(w)
            })

print(f"\nTotal tokens on f57v: {len(f57v_tokens)}")

# Length distribution
lengths = [t['length'] for t in f57v_tokens]
print(f"\nToken length distribution:")
print(f"  Mean: {sum(lengths)/len(lengths):.2f}")
print(f"  Max: {max(lengths)}")
print(f"  Min: {min(lengths)}")

# Count by length
length_counts = Counter(lengths)
print("\nBy length:")
for l in sorted(length_counts.keys()):
    print(f"  Length {l}: {length_counts[l]} tokens")

# Long tokens (6+ chars)
long_tokens = [t for t in f57v_tokens if t['length'] >= 6]
print(f"\nLong tokens (6+ chars): {len(long_tokens)}")
for t in sorted(long_tokens, key=lambda x: -x['length'])[:20]:
    print(f"  '{t['word']}' (len={t['length']}, MIDDLE='{t['middle']}', placement={t['placement']})")

# By placement
print("\n" + "="*70)
print("BY PLACEMENT")
print("="*70)

by_placement = defaultdict(list)
for t in f57v_tokens:
    by_placement[t['placement']].append(t)

for placement in sorted(by_placement.keys()):
    tokens = by_placement[placement]
    mean_len = sum(t['length'] for t in tokens) / len(tokens)
    max_len = max(t['length'] for t in tokens)
    print(f"\n{placement}: {len(tokens)} tokens, mean length {mean_len:.2f}, max {max_len}")

    # Show longest in this placement
    long_here = sorted(tokens, key=lambda x: -x['length'])[:5]
    for t in long_here:
        print(f"    '{t['word']}' (len={t['length']})")

# MIDDLE length distribution
print("\n" + "="*70)
print("MIDDLE LENGTH DISTRIBUTION")
print("="*70)

middle_lengths = [len(t['middle']) for t in f57v_tokens if t['middle']]
if middle_lengths:
    print(f"Mean MIDDLE length: {sum(middle_lengths)/len(middle_lengths):.2f}")
    print(f"Max MIDDLE length: {max(middle_lengths)}")

    # Long MIDDLEs
    long_middles = [(t['word'], t['middle']) for t in f57v_tokens if t['middle'] and len(t['middle']) >= 4]
    print(f"\nLong MIDDLEs (4+ chars): {len(long_middles)}")
    for word, mid in sorted(long_middles, key=lambda x: -len(x[1]))[:15]:
        print(f"  '{word}' -> MIDDLE '{mid}' (len={len(mid)})")

# Compare to B average
print("\n" + "="*70)
print("COMPARISON TO CURRIER B AVERAGE")
print("="*70)

b_lengths = []
b_middle_lengths = []
for token in tx.currier_b():
    w = token.word.strip()
    if w and '*' not in w:
        b_lengths.append(len(w))
        m = morph.extract(w)
        if m.middle:
            b_middle_lengths.append(len(m.middle))

print(f"\nCurrier B average token length: {sum(b_lengths)/len(b_lengths):.2f}")
print(f"f57v average token length: {sum(lengths)/len(lengths):.2f}")
print(f"\nCurrier B average MIDDLE length: {sum(b_middle_lengths)/len(b_middle_lengths):.2f}")
print(f"f57v average MIDDLE length: {sum(middle_lengths)/len(middle_lengths):.2f}")
