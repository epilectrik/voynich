#!/usr/bin/env python3
"""
Test 12: Rosettes Deep Analysis

The Rosettes (f85/f86) have extremely high P-text rates (68-100%).
This is completely different from other AZC folios (17-21% P-text).

Questions:
1. What placements are used on Rosettes? (Ring, Circle, Paragraph?)
2. Is the vocabulary similar to regular Currier A or AZC?
3. Do they have line/paragraph structure like A text?
4. Are they actually Currier A pages misclassified as AZC?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
from scripts.voynich import Morphology

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

# Rosettes folios
ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Collect data
rosettes_tokens = []
rosettes_by_placement = defaultdict(list)
rosettes_by_line = defaultdict(lambda: defaultdict(list))

other_azc_tokens = []
currier_a_tokens = []

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
                rosettes_tokens.append(token)
                rosettes_by_placement[placement].append(token)
                rosettes_by_line[folio][line_num].append(token)
            elif currier == 'NA':
                other_azc_tokens.append(token)
            elif currier == 'A':
                currier_a_tokens.append(token)

print("=" * 70)
print("TEST 12: ROSETTES DEEP ANALYSIS")
print("=" * 70)
print()

# 1. Placement distribution
print("1. ROSETTES PLACEMENT DISTRIBUTION")
print("-" * 50)

total = len(rosettes_tokens)
print(f"Total Rosettes tokens: {total}")
print()

for placement in sorted(rosettes_by_placement.keys(), key=lambda x: -len(rosettes_by_placement[x])):
    count = len(rosettes_by_placement[placement])
    pct = count / total * 100
    print(f"  {placement:<6}: {count:>4} tokens ({pct:.1f}%)")

print()

# 2. Line structure
print("2. ROSETTES LINE STRUCTURE")
print("-" * 50)

for folio in sorted(rosettes_by_line.keys()):
    lines = rosettes_by_line[folio]
    n_lines = len(lines)
    tokens_per_line = [len(tokens) for tokens in lines.values()]
    mean_tokens = sum(tokens_per_line) / n_lines if n_lines > 0 else 0

    print(f"\n{folio}: {n_lines} lines, {sum(tokens_per_line)} tokens")
    print(f"  Mean tokens/line: {mean_tokens:.1f}")
    print(f"  Lines: {sorted(lines.keys())[:10]}{'...' if n_lines > 10 else ''}")

print()

# 3. MIDDLE vocabulary comparison
print("3. MIDDLE VOCABULARY COMPARISON")
print("-" * 50)

def get_middles(tokens):
    middles = []
    for t in tokens:
        m = morph.extract(t)
        if m.middle:
            middles.append(m.middle)
    return middles

rosettes_middles = set(get_middles(rosettes_tokens))
other_azc_middles = set(get_middles(other_azc_tokens))
currier_a_middles = set(get_middles(currier_a_tokens))

print(f"Unique Rosettes MIDDLEs: {len(rosettes_middles)}")
print(f"Unique other-AZC MIDDLEs: {len(other_azc_middles)}")
print(f"Unique Currier A MIDDLEs: {len(currier_a_middles)}")
print()

# Overlaps
ros_in_azc = rosettes_middles & other_azc_middles
ros_in_a = rosettes_middles & currier_a_middles
ros_only = rosettes_middles - other_azc_middles - currier_a_middles

print(f"Rosettes MIDDLEs in other-AZC: {len(ros_in_azc)} ({len(ros_in_azc)/len(rosettes_middles)*100:.1f}%)")
print(f"Rosettes MIDDLEs in Currier A: {len(ros_in_a)} ({len(ros_in_a)/len(rosettes_middles)*100:.1f}%)")
print(f"Rosettes-only MIDDLEs: {len(ros_only)} ({len(ros_only)/len(rosettes_middles)*100:.1f}%)")
print()

if ros_only:
    print(f"Rosettes-unique MIDDLEs: {sorted(ros_only)[:20]}")
print()

# 4. PREFIX profile
print("4. PREFIX PROFILE")
print("-" * 50)

def prefix_profile(tokens):
    prefixes = []
    for t in tokens:
        m = morph.extract(t)
        prefixes.append(m.prefix if m.prefix else 'NONE')
    return Counter(prefixes)

ros_prefixes = prefix_profile(rosettes_tokens)
azc_prefixes = prefix_profile(other_azc_tokens)
a_prefixes = prefix_profile(currier_a_tokens)

# Normalize
ros_total = sum(ros_prefixes.values())
azc_total = sum(azc_prefixes.values())
a_total = sum(a_prefixes.values())

print(f"{'PREFIX':<10} {'Rosettes':<12} {'Other-AZC':<12} {'Currier A':<12}")
print("-" * 46)

all_prefixes = set(ros_prefixes.keys()) | set(azc_prefixes.keys()) | set(a_prefixes.keys())
for prefix in sorted(all_prefixes, key=lambda p: -ros_prefixes.get(p, 0))[:15]:
    ros_pct = ros_prefixes.get(prefix, 0) / ros_total * 100 if ros_total else 0
    azc_pct = azc_prefixes.get(prefix, 0) / azc_total * 100 if azc_total else 0
    a_pct = a_prefixes.get(prefix, 0) / a_total * 100 if a_total else 0
    print(f"{prefix:<10} {ros_pct:<12.1f}% {azc_pct:<12.1f}% {a_pct:<12.1f}%")

print()

# 5. Calculate cosine similarity
print("5. PREFIX COSINE SIMILARITY")
print("-" * 50)

import numpy as np

def cosine_sim(profile1, profile2, total1, total2):
    all_keys = set(profile1.keys()) | set(profile2.keys())
    vec1 = np.array([profile1.get(k, 0)/total1 for k in all_keys]) if total1 else np.zeros(len(all_keys))
    vec2 = np.array([profile2.get(k, 0)/total2 for k in all_keys]) if total2 else np.zeros(len(all_keys))

    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

sim_ros_a = cosine_sim(ros_prefixes, a_prefixes, ros_total, a_total)
sim_ros_azc = cosine_sim(ros_prefixes, azc_prefixes, ros_total, azc_total)
sim_a_azc = cosine_sim(a_prefixes, azc_prefixes, a_total, azc_total)

print(f"Rosettes to Currier A: {sim_ros_a:.3f}")
print(f"Rosettes to other-AZC: {sim_ros_azc:.3f}")
print(f"Currier A to other-AZC: {sim_a_azc:.3f}")
print()

# 6. Morphological completeness
print("6. MORPHOLOGICAL COMPLETENESS")
print("-" * 50)

def morph_profile(tokens):
    has_prefix = 0
    has_suffix = 0
    has_articulator = 0

    for t in tokens:
        m = morph.extract(t)
        if m.prefix:
            has_prefix += 1
        if m.suffix:
            has_suffix += 1
        if m.articulator:
            has_articulator += 1

    n = len(tokens)
    return {
        'has_prefix': has_prefix / n if n else 0,
        'has_suffix': has_suffix / n if n else 0,
        'has_articulator': has_articulator / n if n else 0
    }

ros_morph = morph_profile(rosettes_tokens)
azc_morph = morph_profile(other_azc_tokens)
a_morph = morph_profile(currier_a_tokens)

print(f"{'Metric':<20} {'Rosettes':<12} {'Other-AZC':<12} {'Currier A':<12}")
print("-" * 56)
print(f"{'Has PREFIX':<20} {ros_morph['has_prefix']*100:<12.1f}% {azc_morph['has_prefix']*100:<12.1f}% {a_morph['has_prefix']*100:<12.1f}%")
print(f"{'Has SUFFIX':<20} {ros_morph['has_suffix']*100:<12.1f}% {azc_morph['has_suffix']*100:<12.1f}% {a_morph['has_suffix']*100:<12.1f}%")
print(f"{'Has ARTICULATOR':<20} {ros_morph['has_articulator']*100:<12.1f}% {azc_morph['has_articulator']*100:<12.1f}% {a_morph['has_articulator']*100:<12.1f}%")

print()

# 7. Token length
print("7. TOKEN LENGTH")
print("-" * 50)

ros_lens = [len(t) for t in rosettes_tokens]
azc_lens = [len(t) for t in other_azc_tokens]
a_lens = [len(t) for t in currier_a_tokens]

print(f"Rosettes mean length: {np.mean(ros_lens):.2f}")
print(f"Other-AZC mean length: {np.mean(azc_lens):.2f}")
print(f"Currier A mean length: {np.mean(a_lens):.2f}")

print()

# Verdict
print("=" * 70)
print("VERDICT")
print("=" * 70)

print(f"""
ROSETTES CLASSIFICATION:

1. PREFIX similarity to Currier A: {sim_ros_a:.3f}
   PREFIX similarity to other-AZC: {sim_ros_azc:.3f}
   => Rosettes are {"A-LIKE" if sim_ros_a > sim_ros_azc else "AZC-LIKE"} in PREFIX profile

2. MIDDLE overlap with Currier A: {len(ros_in_a)/len(rosettes_middles)*100:.1f}%
   MIDDLE overlap with other-AZC: {len(ros_in_azc)/len(rosettes_middles)*100:.1f}%
   => Rosettes vocabulary is {"A-LIKE" if len(ros_in_a) > len(ros_in_azc) else "AZC-LIKE"}

3. Morphological completeness:
   - PREFIX rate: Rosettes {ros_morph['has_prefix']*100:.1f}% vs A {a_morph['has_prefix']*100:.1f}% vs AZC {azc_morph['has_prefix']*100:.1f}%
   - SUFFIX rate: Rosettes {ros_morph['has_suffix']*100:.1f}% vs A {a_morph['has_suffix']*100:.1f}% vs AZC {azc_morph['has_suffix']*100:.1f}%

4. Token length: Rosettes {np.mean(ros_lens):.2f} vs A {np.mean(a_lens):.2f} vs AZC {np.mean(azc_lens):.2f}
""")

# Final classification
if sim_ros_a > 0.95:
    print("CONCLUSION: Rosettes are linguistically CURRIER A text on large foldouts.")
    print("They should NOT be classified as AZC diagram text.")
elif sim_ros_a > sim_ros_azc:
    print("CONCLUSION: Rosettes are A-LIKE but may represent a distinct category.")
else:
    print("CONCLUSION: Rosettes show mixed A/AZC characteristics.")
