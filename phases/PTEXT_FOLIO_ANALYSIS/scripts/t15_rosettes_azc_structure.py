#!/usr/bin/env python3
"""
Test 15: Rosettes AZC-like Structure Analysis

Do the Rosettes have AZC-like structural organization?
- Spokes with single tokens (S-positions)
- Labels on connections
- Ring/Circle positions

Compare placement patterns to actual AZC folios.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Morphology

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Collect placement data
rosettes_by_placement = defaultdict(list)
rosettes_by_folio_line_placement = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
azc_by_placement = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()
            line_num = parts[11].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if folio in ROSETTES:
                rosettes_by_placement[placement].append(token)
                rosettes_by_folio_line_placement[folio][line_num][placement].append(token)
            elif currier == 'NA':  # AZC
                azc_by_placement[placement].append(token)

print("=" * 70)
print("TEST 15: ROSETTES AZC-LIKE STRUCTURE ANALYSIS")
print("=" * 70)
print()

# 1. Placement type distribution
print("1. PLACEMENT TYPE DISTRIBUTION")
print("-" * 50)

print("\nROSETTES placements:")
ros_total = sum(len(tokens) for tokens in rosettes_by_placement.values())
for placement in sorted(rosettes_by_placement.keys(), key=lambda x: -len(rosettes_by_placement[x])):
    count = len(rosettes_by_placement[placement])
    pct = count / ros_total * 100
    print(f"  {placement:<8}: {count:>4} tokens ({pct:>5.1f}%)")

print("\nAZC placements:")
azc_total = sum(len(tokens) for tokens in azc_by_placement.values())
for placement in sorted(azc_by_placement.keys(), key=lambda x: -len(azc_by_placement[x]))[:15]:
    count = len(azc_by_placement[placement])
    pct = count / azc_total * 100
    print(f"  {placement:<8}: {count:>4} tokens ({pct:>5.1f}%)")

print()

# 2. Identify AZC-like placements in Rosettes
print("2. AZC-LIKE PLACEMENTS IN ROSETTES")
print("-" * 50)

# AZC typical placements: C (circle), R (ring), S (spoke), L (label)
azc_types = {
    'C': 'Circle/Center',
    'R': 'Ring',
    'S': 'Spoke',
    'L': 'Label',
    'P': 'Paragraph',
    'T': 'Text',
    'Q': 'Unknown Q',
}

rosettes_azc_like = 0
rosettes_paragraph = 0

for placement, tokens in rosettes_by_placement.items():
    first_char = placement[0] if placement else '?'
    if first_char in ['C', 'R', 'S', 'L']:
        rosettes_azc_like += len(tokens)
    elif first_char == 'P':
        rosettes_paragraph += len(tokens)

print(f"AZC-like placements (C, R, S, L): {rosettes_azc_like} ({rosettes_azc_like/ros_total*100:.1f}%)")
print(f"Paragraph placements (P): {rosettes_paragraph} ({rosettes_paragraph/ros_total*100:.1f}%)")
print()

# 3. Single-token positions (label-like)
print("3. SINGLE-TOKEN POSITIONS (LABEL-LIKE)")
print("-" * 50)

# Count how many lines have only 1 token per placement
single_token_positions = 0
multi_token_positions = 0

for folio in rosettes_by_folio_line_placement:
    for line_num in rosettes_by_folio_line_placement[folio]:
        for placement, tokens in rosettes_by_folio_line_placement[folio][line_num].items():
            if len(tokens) == 1:
                single_token_positions += 1
            else:
                multi_token_positions += 1

total_positions = single_token_positions + multi_token_positions
print(f"Single-token positions: {single_token_positions} ({single_token_positions/total_positions*100:.1f}%)")
print(f"Multi-token positions: {multi_token_positions} ({multi_token_positions/total_positions*100:.1f}%)")
print()

# 4. Analyze C-placement tokens (Circle/Center - likely diagram labels)
print("4. C-PLACEMENT ANALYSIS (DIAGRAM LABELS?)")
print("-" * 50)

c_tokens = []
for placement, tokens in rosettes_by_placement.items():
    if placement.startswith('C'):
        c_tokens.extend(tokens)

if c_tokens:
    print(f"Total C-placement tokens: {len(c_tokens)}")

    # Token length distribution
    c_lengths = [len(t) for t in c_tokens]
    print(f"Mean token length: {sum(c_lengths)/len(c_lengths):.2f}")

    # Unique tokens
    c_unique = set(c_tokens)
    print(f"Unique tokens: {len(c_unique)} (TTR: {len(c_unique)/len(c_tokens):.3f})")

    # Most common
    c_counts = Counter(c_tokens)
    print(f"\nMost common C-placement tokens:")
    for token, count in c_counts.most_common(10):
        print(f"  {token}: {count}")
print()

# 5. Analyze Q-placement (unknown - connections?)
print("5. Q-PLACEMENT ANALYSIS (CONNECTIONS?)")
print("-" * 50)

q_tokens = rosettes_by_placement.get('Q', [])
if q_tokens:
    print(f"Total Q-placement tokens: {len(q_tokens)}")

    q_lengths = [len(t) for t in q_tokens]
    print(f"Mean token length: {sum(q_lengths)/len(q_lengths):.2f}")

    q_unique = set(q_tokens)
    print(f"Unique tokens: {len(q_unique)} (TTR: {len(q_unique)/len(q_tokens):.3f})")

    q_counts = Counter(q_tokens)
    print(f"\nMost common Q-placement tokens:")
    for token, count in q_counts.most_common(10):
        print(f"  {token}: {count}")
print()

# 6. T-placement (connection text?)
print("6. T-PLACEMENT ANALYSIS")
print("-" * 50)

t_tokens = rosettes_by_placement.get('T', [])
if t_tokens:
    print(f"Total T-placement tokens: {len(t_tokens)}")
    print(f"Tokens: {t_tokens[:20]}")
print()

# 7. Compare token length by placement type
print("7. TOKEN LENGTH BY PLACEMENT TYPE")
print("-" * 50)

print(f"{'Placement':<10} {'Count':<8} {'Mean Len':<10} {'Unique':<8} {'TTR':<8}")
print("-" * 44)

for placement in sorted(rosettes_by_placement.keys(), key=lambda x: -len(rosettes_by_placement[x])):
    tokens = rosettes_by_placement[placement]
    if len(tokens) >= 5:  # Only show placements with 5+ tokens
        mean_len = sum(len(t) for t in tokens) / len(tokens)
        unique = len(set(tokens))
        ttr = unique / len(tokens)
        print(f"{placement:<10} {len(tokens):<8} {mean_len:<10.2f} {unique:<8} {ttr:<8.3f}")

print()

# 8. Per-folio breakdown
print("8. PER-FOLIO STRUCTURE")
print("-" * 50)

for folio in sorted(rosettes_by_folio_line_placement.keys()):
    lines = rosettes_by_folio_line_placement[folio]

    # Count placements
    folio_placements = Counter()
    for line_num in lines:
        for placement in lines[line_num]:
            folio_placements[placement] += len(lines[line_num][placement])

    print(f"\n{folio}:")
    for placement, count in folio_placements.most_common():
        print(f"  {placement}: {count}")

print()

# Verdict
print("=" * 70)
print("STRUCTURE VERDICT")
print("=" * 70)

azc_like_pct = rosettes_azc_like / ros_total * 100
single_token_pct = single_token_positions / total_positions * 100

print(f"""
ROSETTES STRUCTURAL ANALYSIS:

1. Placement distribution:
   - Paragraph (P*): {rosettes_paragraph} tokens ({rosettes_paragraph/ros_total*100:.1f}%)
   - AZC-like (C, R, S, L): {rosettes_azc_like} tokens ({azc_like_pct:.1f}%)

2. Position granularity:
   - Single-token positions: {single_token_positions} ({single_token_pct:.1f}%)
   - Multi-token positions: {multi_token_positions} ({100-single_token_pct:.1f}%)

3. C-placement (likely diagram labels): {len(c_tokens)} tokens
   Q-placement (possibly connections): {len(q_tokens)} tokens
""")

if azc_like_pct > 20:
    print("CONCLUSION: Rosettes have HYBRID structure:")
    print("  - Currier B vocabulary (linguistic)")
    print("  - AZC-like layout (structural)")
    print("  - Mix of paragraph text and diagram labels")
else:
    print("CONCLUSION: Rosettes are primarily paragraph-structured B text")
    print("with minimal AZC-like diagram labeling.")
