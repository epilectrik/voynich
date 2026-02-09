#!/usr/bin/env python3
"""
Test 16: Q-placement Token Analysis

Where do the Rosettes Q-placement tokens appear elsewhere in the corpus?
Are they unique to Rosettes or shared with A, B, AZC?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Collect Q tokens from Rosettes
rosettes_q_tokens = []

# Collect all tokens by category
tokens_by_category = {
    'currier_a': [],
    'currier_b_non_ros': [],
    'azc': [],
    'azc_s_placement': [],  # S-series in AZC
    'azc_c_placement': [],  # C-series in AZC
    'azc_r_placement': [],  # R-series in AZC
}

# Track where each token appears
token_locations = defaultdict(lambda: defaultdict(list))  # token -> category -> [folios]

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

            if not token.strip() or '*' in token:
                continue

            if folio in ROSETTES:
                if placement == 'Q':
                    rosettes_q_tokens.append(token)
                    token_locations[token]['rosettes_q'].append(folio)
            elif currier == 'A':
                tokens_by_category['currier_a'].append(token)
                token_locations[token]['currier_a'].append(folio)
            elif currier == 'B':
                tokens_by_category['currier_b_non_ros'].append(token)
                token_locations[token]['currier_b'].append(folio)
            elif currier == 'NA':  # AZC
                tokens_by_category['azc'].append(token)
                token_locations[token]['azc'].append(folio)

                # Track by placement type
                if placement.startswith('S'):
                    tokens_by_category['azc_s_placement'].append(token)
                    token_locations[token]['azc_s'].append(folio)
                elif placement.startswith('C'):
                    tokens_by_category['azc_c_placement'].append(token)
                    token_locations[token]['azc_c'].append(folio)
                elif placement.startswith('R'):
                    tokens_by_category['azc_r_placement'].append(token)
                    token_locations[token]['azc_r'].append(folio)

print("=" * 70)
print("TEST 16: Q-PLACEMENT TOKEN ANALYSIS")
print("=" * 70)
print()

# Get unique Q tokens
q_unique = set(rosettes_q_tokens)
q_counts = Counter(rosettes_q_tokens)

print("1. ROSETTES Q-PLACEMENT TOKENS")
print("-" * 50)
print(f"Total Q tokens: {len(rosettes_q_tokens)}")
print(f"Unique Q tokens: {len(q_unique)}")
print()

print("All Q tokens with counts:")
for token, count in q_counts.most_common():
    print(f"  {token}: {count}")
print()

# 2. Where do Q tokens appear?
print("2. Q TOKEN APPEARANCES ELSEWHERE")
print("-" * 50)

# Build sets for comparison
a_set = set(tokens_by_category['currier_a'])
b_set = set(tokens_by_category['currier_b_non_ros'])
azc_set = set(tokens_by_category['azc'])
azc_s_set = set(tokens_by_category['azc_s_placement'])
azc_c_set = set(tokens_by_category['azc_c_placement'])
azc_r_set = set(tokens_by_category['azc_r_placement'])

q_in_a = q_unique & a_set
q_in_b = q_unique & b_set
q_in_azc = q_unique & azc_set
q_in_azc_s = q_unique & azc_s_set
q_in_azc_c = q_unique & azc_c_set
q_in_azc_r = q_unique & azc_r_set
q_unique_only = q_unique - a_set - b_set - azc_set

print(f"Q tokens in Currier A: {len(q_in_a)} ({len(q_in_a)/len(q_unique)*100:.1f}%)")
print(f"Q tokens in Currier B: {len(q_in_b)} ({len(q_in_b)/len(q_unique)*100:.1f}%)")
print(f"Q tokens in AZC: {len(q_in_azc)} ({len(q_in_azc)/len(q_unique)*100:.1f}%)")
print(f"  - in AZC S-placement: {len(q_in_azc_s)}")
print(f"  - in AZC C-placement: {len(q_in_azc_c)}")
print(f"  - in AZC R-placement: {len(q_in_azc_r)}")
print(f"Q tokens UNIQUE to Rosettes: {len(q_unique_only)} ({len(q_unique_only)/len(q_unique)*100:.1f}%)")
print()

# 3. Detailed breakdown for each Q token
print("3. DETAILED Q TOKEN ANALYSIS")
print("-" * 50)
print()

print(f"{'Token':<15} {'Ros Q':<8} {'A':<6} {'B':<6} {'AZC':<6} {'AZC-S':<6} {'AZC-C':<6} {'AZC-R':<6}")
print("-" * 65)

for token in sorted(q_unique, key=lambda t: -q_counts[t]):
    ros_count = q_counts[token]
    a_count = len(token_locations[token]['currier_a'])
    b_count = len(token_locations[token]['currier_b'])
    azc_count = len(token_locations[token]['azc'])
    azc_s_count = len(token_locations[token]['azc_s'])
    azc_c_count = len(token_locations[token]['azc_c'])
    azc_r_count = len(token_locations[token]['azc_r'])

    print(f"{token:<15} {ros_count:<8} {a_count:<6} {b_count:<6} {azc_count:<6} {azc_s_count:<6} {azc_c_count:<6} {azc_r_count:<6}")

print()

# 4. Q tokens that appear in AZC S-placement
print("4. Q TOKENS SHARED WITH AZC S-PLACEMENT")
print("-" * 50)

if q_in_azc_s:
    print("These Q tokens also appear in AZC spoke positions:")
    for token in sorted(q_in_azc_s):
        azc_s_folios = set(token_locations[token]['azc_s'])
        print(f"  {token}: AZC-S folios = {sorted(azc_s_folios)}")
else:
    print("No Q tokens appear in AZC S-placement positions.")
print()

# 5. Q tokens unique to Rosettes
print("5. Q TOKENS UNIQUE TO ROSETTES")
print("-" * 50)

if q_unique_only:
    print("These Q tokens appear ONLY in Rosettes Q-placement:")
    for token in sorted(q_unique_only):
        print(f"  {token}")
else:
    print("All Q tokens appear somewhere else in the corpus.")
print()

# 6. Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
ROSETTES Q-PLACEMENT VOCABULARY:

Total unique tokens: {len(q_unique)}

Distribution:
- Found in Currier A: {len(q_in_a)} tokens ({len(q_in_a)/len(q_unique)*100:.1f}%)
- Found in Currier B: {len(q_in_b)} tokens ({len(q_in_b)/len(q_unique)*100:.1f}%)
- Found in AZC: {len(q_in_azc)} tokens ({len(q_in_azc)/len(q_unique)*100:.1f}%)
- UNIQUE to Rosettes: {len(q_unique_only)} tokens ({len(q_unique_only)/len(q_unique)*100:.1f}%)

AZC placement overlap:
- Shared with AZC S-placement (spokes): {len(q_in_azc_s)} tokens
- Shared with AZC C-placement (circles): {len(q_in_azc_c)} tokens
- Shared with AZC R-placement (rings): {len(q_in_azc_r)} tokens
""")

if len(q_in_azc_s) > len(q_unique) * 0.3:
    print("CONCLUSION: Q-placement tokens significantly overlap with AZC spoke vocabulary.")
    print("The Rosettes Q-positions appear to function like AZC S-positions.")
elif len(q_in_b) > len(q_unique) * 0.7:
    print("CONCLUSION: Q-placement tokens are primarily Currier B vocabulary.")
    print("These are B words in label positions, not AZC-style labels.")
else:
    print("CONCLUSION: Q-placement tokens show mixed provenance.")
