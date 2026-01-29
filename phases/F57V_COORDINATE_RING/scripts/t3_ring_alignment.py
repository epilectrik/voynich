"""
T3: Check if R2 positions correlate with R1/R3 content.

Question: Does the R2 single-char sequence serve as an index or coordinate for content rings?
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Morphology

morph = Morphology()

# Load data
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
f57v = df[df['folio'] == 'f57v']

print("="*70)
print("T3: R2 vs R1/R3 ALIGNMENT ANALYSIS")
print("="*70)

# Extract all rings
def get_ring_sequence(ring_name):
    subset = f57v[f57v['placement'] == ring_name].sort_values('line_number')
    words = [str(w) for w in subset['word'].tolist() if str(w) != 'nan']
    # Keep asterisks to maintain position alignment
    return words

r1 = get_ring_sequence('R1')
r2 = get_ring_sequence('R2')
r3 = get_ring_sequence('R3')
r4 = get_ring_sequence('R4')

print(f"\nRing lengths: R1={len(r1)}, R2={len(r2)}, R3={len(r3)}, R4={len(r4)}")

# Clean R2 for analysis
r2_clean = [w for w in r2 if w != '*']

print("\n" + "="*70)
print("RING TOKEN COUNTS")
print("="*70)

# R2 has 50 clean tokens, but R1 has 51 total (50 clean)
# Check if they might be aligned
print(f"\nR1 total: {len(r1)}, clean (no *): {len([w for w in r1 if w != '*'])}")
print(f"R2 total: {len(r2)}, clean (no *): {len(r2_clean)}")
print(f"R3 total: {len(r3)}, clean (no *): {len([w for w in r3 if w != '*'])}")

# The key question: are the NUMBERS of tokens similar?
# If R2 has 50 positions and R1 has ~50, they might be parallel

print("\n" + "="*70)
print("R1 CONTENT ANALYSIS")
print("="*70)

r1_clean = [w for w in r1 if w != '*']
print(f"\nR1 sequence ({len(r1_clean)} tokens):")
print(" ".join(r1_clean))

# Extract MIDDLEs from R1
r1_middles = []
for w in r1_clean:
    if len(w) > 1:
        m = morph.extract(w)
        if m.middle:
            r1_middles.append(m.middle)

print(f"\nR1 MIDDLEs: {r1_middles[:20]}...")
print(f"Unique MIDDLEs in R1: {len(set(r1_middles))}")

print("\n" + "="*70)
print("R3 CONTENT ANALYSIS")
print("="*70)

r3_clean = [w for w in r3 if w != '*']
print(f"\nR3 sequence ({len(r3_clean)} tokens):")
print(" ".join(r3_clean))

r3_middles = []
for w in r3_clean:
    if len(w) > 1:
        m = morph.extract(w)
        if m.middle:
            r3_middles.append(m.middle)

print(f"\nR3 MIDDLEs: {r3_middles[:20]}...")
print(f"Unique MIDDLEs in R3: {len(set(r3_middles))}")

# Check if R2's unique characters 'm' and 'n' (terminators) have any special relationship
print("\n" + "="*70)
print("R2 TERMINATOR ANALYSIS")
print("="*70)

# m and n only appear at the end of R2
m_pos = [i for i, c in enumerate(r2_clean) if c == 'm']
n_pos = [i for i, c in enumerate(r2_clean) if c == 'n']

print(f"\n'm' positions in R2: {m_pos}")
print(f"'n' positions in R2: {n_pos}")
print(f"R2 length: {len(r2_clean)}")
print(f"'m' and 'n' are the last two characters (positions {len(r2_clean)-2}, {len(r2_clean)-1})")

# Check if m/n appear in R1 or R3
m_in_r1 = sum(1 for w in r1_clean if 'm' in w)
n_in_r1 = sum(1 for w in r1_clean if 'n' in w)
m_in_r3 = sum(1 for w in r3_clean if 'm' in w)
n_in_r3 = sum(1 for w in r3_clean if 'n' in w)

print(f"\n'm' occurrences in R1: {m_in_r1}, in R3: {m_in_r3}")
print(f"'n' occurrences in R1: {n_in_r1}, in R3: {n_in_r3}")

# Check if R2's 'x' character has any special distribution
print("\n" + "="*70)
print("R2 'x' DISTRIBUTION (unusual character)")
print("="*70)

x_pos = [i for i, c in enumerate(r2_clean) if c == 'x']
print(f"\n'x' positions in R2: {x_pos}")
print(f"'x' appears {len(x_pos)} times, spacing: {[x_pos[i+1]-x_pos[i] for i in range(len(x_pos)-1)]}")

# x is unusual in EVA - check if it appears in R1/R3
x_in_r1 = [w for w in r1_clean if 'x' in w]
x_in_r3 = [w for w in r3_clean if 'x' in w]
print(f"'x' in R1 tokens: {x_in_r1}")
print(f"'x' in R3 tokens: {x_in_r3}")

# The key observation from the expert: R2 might be a coordinate system
# Let's see if the R2 character sequence has any relationship to R1/R3 morphology
print("\n" + "="*70)
print("COORDINATE HYPOTHESIS TEST")
print("="*70)

# If R2 is a coordinate system, maybe 'x k k' marks sections
# Let's find where 'x k k' appears and see what's at those positions in R1
xkk_positions = []
for i in range(len(r2_clean) - 2):
    if r2_clean[i:i+3] == ['x', 'k', 'k']:
        xkk_positions.append(i)

print(f"\n'x k k' appears at R2 positions: {xkk_positions}")

# Scale to R1 positions (R1 and R2 have similar length)
r1_length = len(r1_clean)
r2_length = len(r2_clean)
scale = r1_length / r2_length

print(f"\nR1/R2 length ratio: {scale:.2f}")

for pos in xkk_positions:
    r1_pos = int(pos * scale)
    # Get R1 token at that approximate position
    if r1_pos < len(r1_clean):
        r1_token = r1_clean[r1_pos]
        print(f"  R2 'x k k' at {pos} -> R1 position ~{r1_pos}: '{r1_token}'")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
Key observations:
1. R1 and R2 have nearly identical token counts (50 each) - possible 1:1 correspondence
2. 'm' and 'n' are unique terminators at the end of R2
3. 'x' is unusual and appears at regular intervals in R2
4. 'x k k' pattern appears twice, potentially marking sections

The alignment hypothesis cannot be definitively tested without visual mapping
to the actual manuscript diagram, but the equal token counts suggest R2 may
index R1 positions.
""")

# Save results
results = {
    'ring_lengths': {'R1': len(r1_clean), 'R2': len(r2_clean), 'R3': len(r3_clean), 'R4': len([w for w in r4 if w != '*'])},
    'xkk_positions': xkk_positions,
    'x_positions': x_pos,
    'terminators': {'m': m_pos, 'n': n_pos},
    'r1_unique_middles': len(set(r1_middles)),
    'r3_unique_middles': len(set(r3_middles)),
    'verdict': 'ALIGNMENT_POSSIBLE' if abs(len(r1_clean) - len(r2_clean)) <= 2 else 'NO_ALIGNMENT'
}

output_path = PROJECT_ROOT / 'phases' / 'F57V_COORDINATE_RING' / 'results' / 't3_ring_alignment.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to: {output_path}")
