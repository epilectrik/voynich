"""
T2: Map p/f variant positions in R2 sequence.

Question: Do p/f positions have regular spacing that supports "angular coordinate" hypothesis?
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# The clean R2 sequence (from C763)
seq = "o d r x k k p t r y c o l c y r t l k k x r d p r o c l d r x k k f t r y c o y r t f k x r d l m n".split()

print("="*70)
print("T2: p/f POSITION MAPPING IN f57v R2")
print("="*70)

print(f"\nSequence length: {len(seq)} characters")
print(f"Full sequence: {' '.join(seq)}")

# Find p and f positions
p_positions = [i for i, c in enumerate(seq) if c == 'p']
f_positions = [i for i, c in enumerate(seq) if c == 'f']

print(f"\n'p' appears at positions: {p_positions}")
print(f"'f' appears at positions: {f_positions}")

# Calculate spacing
all_gallows_positions = sorted(p_positions + f_positions)
print(f"\nAll p/f positions (sorted): {all_gallows_positions}")

if len(all_gallows_positions) > 1:
    spacings = [all_gallows_positions[i+1] - all_gallows_positions[i]
                for i in range(len(all_gallows_positions)-1)]
    print(f"Spacings between p/f: {spacings}")
    print(f"Mean spacing: {sum(spacings)/len(spacings):.1f}")

# Analyze context around p and f
print("\n" + "="*70)
print("CONTEXT AROUND p/f POSITIONS")
print("="*70)

for pos in p_positions:
    start = max(0, pos-5)
    end = min(len(seq), pos+6)
    context = seq[start:end]
    marker_pos = pos - start
    context_str = ' '.join(context)
    print(f"\n'p' at position {pos}:")
    print(f"  Context: {context_str}")
    print(f"  Pattern: {' '.join(context[:marker_pos])} [p] {' '.join(context[marker_pos+1:])}")

for pos in f_positions:
    start = max(0, pos-5)
    end = min(len(seq), pos+6)
    context = seq[start:end]
    marker_pos = pos - start
    context_str = ' '.join(context)
    print(f"\n'f' at position {pos}:")
    print(f"  Context: {context_str}")
    print(f"  Pattern: {' '.join(context[:marker_pos])} [f] {' '.join(context[marker_pos+1:])}")

# Check if p and f appear in same structural position
print("\n" + "="*70)
print("STRUCTURAL POSITION ANALYSIS")
print("="*70)

# Look at what comes before and after p vs f
p_before = [seq[p-3:p] if p >= 3 else seq[:p] for p in p_positions]
p_after = [seq[p+1:p+4] if p+4 <= len(seq) else seq[p+1:] for p in p_positions]
f_before = [seq[f-3:f] if f >= 3 else seq[:f] for f in f_positions]
f_after = [seq[f+1:f+4] if f+4 <= len(seq) else seq[f+1:] for f in f_positions]

print("\nPreceding 3 chars before 'p':", [' '.join(b) for b in p_before])
print("Following 3 chars after 'p':", [' '.join(a) for a in p_after])
print("\nPreceding 3 chars before 'f':", [' '.join(b) for b in f_before])
print("Following 3 chars after 'f':", [' '.join(a) for a in f_after])

# Check if same preceding pattern
same_structure = False
if p_before and f_before:
    # Both p positions have 'x k k' before them
    p_pattern = [' '.join(b) for b in p_before]
    f_pattern = [' '.join(b) for b in f_before]
    print(f"\nAll p preceded by: {p_pattern}")
    print(f"All f preceded by: {f_pattern}")

    if any('x k k' in p for p in p_pattern) and any('x k k' in f for f in f_pattern):
        print("\n*** BOTH p AND f ARE PRECEDED BY 'x k k' ***")
        same_structure = True

# Angular position hypothesis
print("\n" + "="*70)
print("ANGULAR POSITION HYPOTHESIS")
print("="*70)

# If this is a ring with 50 positions, p/f might mark angular sectors
ring_positions = len(seq)
print(f"\nTotal ring positions: {ring_positions}")

# Calculate what fraction of the ring each p/f marks
for i, pos in enumerate(p_positions):
    angle = 360 * pos / ring_positions
    print(f"'p' at position {pos} = {angle:.0f} degrees")

for i, pos in enumerate(f_positions):
    angle = 360 * pos / ring_positions
    print(f"'f' at position {pos} = {angle:.0f} degrees")

# Check if p and f mark opposing/regular positions
if p_positions and f_positions:
    # First p vs first f
    p1, f1 = p_positions[0], f_positions[0]
    diff = f1 - p1
    print(f"\nDistance from first 'p' to first 'f': {diff} positions")
    print(f"Angular separation: {360 * diff / ring_positions:.0f} degrees")

# Save results
results = {
    'sequence_length': len(seq),
    'p_positions': p_positions,
    'f_positions': f_positions,
    'all_gallows_positions': all_gallows_positions,
    'spacings': spacings if len(all_gallows_positions) > 1 else [],
    'same_preceding_pattern': same_structure,
    'verdict': 'SYSTEMATIC_VARIATION' if same_structure else 'UNCLEAR'
}

output_path = PROJECT_ROOT / 'phases' / 'F57V_COORDINATE_RING' / 'results' / 't2_pf_positions.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to: {output_path}")
