#!/usr/bin/env python3
"""
Test 13: Rosettes vs Regular Currier B

The Rosettes are classified as Currier B (not AZC).
How do they compare to regular B folios?
Are they structurally different B or misclassified A?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scripts.voynich import Morphology

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Collect data
rosettes_tokens = []
regular_b_tokens = []
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

            if not token.strip() or '*' in token:
                continue

            if folio in ROSETTES:
                rosettes_tokens.append(token)
            elif currier == 'B':
                regular_b_tokens.append(token)
            elif currier == 'A':
                currier_a_tokens.append(token)

print("=" * 70)
print("TEST 13: ROSETTES VS REGULAR CURRIER B")
print("=" * 70)
print()

# 1. Token counts
print("1. TOKEN COUNTS")
print("-" * 50)
print(f"Rosettes tokens: {len(rosettes_tokens)}")
print(f"Regular B tokens: {len(regular_b_tokens)}")
print(f"Currier A tokens: {len(currier_a_tokens)}")
print()

# 2. PREFIX profile
print("2. PREFIX PROFILE")
print("-" * 50)

def prefix_profile(tokens):
    prefixes = []
    for t in tokens:
        m = morph.extract(t)
        prefixes.append(m.prefix if m.prefix else 'NONE')
    return Counter(prefixes)

ros_prefixes = prefix_profile(rosettes_tokens)
b_prefixes = prefix_profile(regular_b_tokens)
a_prefixes = prefix_profile(currier_a_tokens)

ros_total = sum(ros_prefixes.values())
b_total = sum(b_prefixes.values())
a_total = sum(a_prefixes.values())

print(f"{'PREFIX':<10} {'Rosettes':<12} {'Regular B':<12} {'Currier A':<12}")
print("-" * 46)

all_prefixes = set(ros_prefixes.keys()) | set(b_prefixes.keys()) | set(a_prefixes.keys())
for prefix in sorted(all_prefixes, key=lambda p: -ros_prefixes.get(p, 0))[:15]:
    ros_pct = ros_prefixes.get(prefix, 0) / ros_total * 100 if ros_total else 0
    b_pct = b_prefixes.get(prefix, 0) / b_total * 100 if b_total else 0
    a_pct = a_prefixes.get(prefix, 0) / a_total * 100 if a_total else 0
    print(f"{prefix:<10} {ros_pct:<12.1f}% {b_pct:<12.1f}% {a_pct:<12.1f}%")

print()

# 3. PREFIX cosine similarity
print("3. PREFIX COSINE SIMILARITY")
print("-" * 50)

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
sim_ros_b = cosine_sim(ros_prefixes, b_prefixes, ros_total, b_total)
sim_a_b = cosine_sim(a_prefixes, b_prefixes, a_total, b_total)

print(f"Rosettes to Currier A: {sim_ros_a:.3f}")
print(f"Rosettes to Regular B: {sim_ros_b:.3f}")
print(f"Currier A to Regular B: {sim_a_b:.3f}")
print()

# 4. MIDDLE vocabulary
print("4. MIDDLE VOCABULARY OVERLAP")
print("-" * 50)

def get_middles(tokens):
    middles = []
    for t in tokens:
        m = morph.extract(t)
        if m.middle:
            middles.append(m.middle)
    return middles

ros_middles = set(get_middles(rosettes_tokens))
b_middles = set(get_middles(regular_b_tokens))
a_middles = set(get_middles(currier_a_tokens))

print(f"Unique Rosettes MIDDLEs: {len(ros_middles)}")
print(f"Unique Regular B MIDDLEs: {len(b_middles)}")
print(f"Unique Currier A MIDDLEs: {len(a_middles)}")
print()

ros_in_b = ros_middles & b_middles
ros_in_a = ros_middles & a_middles
ros_only = ros_middles - b_middles - a_middles

print(f"Rosettes MIDDLEs in Regular B: {len(ros_in_b)} ({len(ros_in_b)/len(ros_middles)*100:.1f}%)")
print(f"Rosettes MIDDLEs in Currier A: {len(ros_in_a)} ({len(ros_in_a)/len(ros_middles)*100:.1f}%)")
print(f"Rosettes-only MIDDLEs: {len(ros_only)} ({len(ros_only)/len(ros_middles)*100:.1f}%)")
print()

# 5. Key PREFIX differences
print("5. KEY PREFIX DIFFERENCES")
print("-" * 50)
print("PREFIXes where Rosettes differ most from Regular B:")
print()

diffs = []
for prefix in all_prefixes:
    ros_pct = ros_prefixes.get(prefix, 0) / ros_total * 100 if ros_total else 0
    b_pct = b_prefixes.get(prefix, 0) / b_total * 100 if b_total else 0
    diff = ros_pct - b_pct
    diffs.append((prefix, diff, ros_pct, b_pct))

diffs.sort(key=lambda x: abs(x[1]), reverse=True)

print(f"{'PREFIX':<10} {'Diff':<10} {'Rosettes':<12} {'Regular B':<12}")
print("-" * 44)
for prefix, diff, ros_pct, b_pct in diffs[:10]:
    sign = '+' if diff > 0 else ''
    print(f"{prefix:<10} {sign}{diff:<9.1f} {ros_pct:<12.1f}% {b_pct:<12.1f}%")

print()

# 6. Morphological signature
print("6. MORPHOLOGICAL SIGNATURE")
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
b_morph = morph_profile(regular_b_tokens)
a_morph = morph_profile(currier_a_tokens)

print(f"{'Metric':<20} {'Rosettes':<12} {'Regular B':<12} {'Currier A':<12}")
print("-" * 56)
print(f"{'Has PREFIX':<20} {ros_morph['has_prefix']*100:<12.1f}% {b_morph['has_prefix']*100:<12.1f}% {a_morph['has_prefix']*100:<12.1f}%")
print(f"{'Has SUFFIX':<20} {ros_morph['has_suffix']*100:<12.1f}% {b_morph['has_suffix']*100:<12.1f}% {a_morph['has_suffix']*100:<12.1f}%")
print(f"{'Has ARTICULATOR':<20} {ros_morph['has_articulator']*100:<12.1f}% {b_morph['has_articulator']*100:<12.1f}% {a_morph['has_articulator']*100:<12.1f}%")

print()

# Verdict
print("=" * 70)
print("VERDICT")
print("=" * 70)

closer_to_a = sim_ros_a > sim_ros_b
vocab_a_like = len(ros_in_a) > len(ros_in_b)

print(f"""
ROSETTES LINGUISTIC IDENTITY:

1. PREFIX profile:
   - Rosettes -> Currier A: {sim_ros_a:.3f}
   - Rosettes -> Regular B: {sim_ros_b:.3f}
   => Rosettes are {'A-LIKE' if closer_to_a else 'B-LIKE'} ({abs(sim_ros_a - sim_ros_b):.3f} difference)

2. MIDDLE vocabulary:
   - Overlap with A: {len(ros_in_a)/len(ros_middles)*100:.1f}%
   - Overlap with B: {len(ros_in_b)/len(ros_middles)*100:.1f}%
   => Rosettes vocabulary is {'A-LIKE' if vocab_a_like else 'B-LIKE'}

3. Key observations:
   - Rosettes use qo- PREFIX at {ros_prefixes.get('qo', 0)/ros_total*100:.1f}% (B uses {b_prefixes.get('qo', 0)/b_total*100:.1f}%, A uses {a_prefixes.get('qo', 0)/a_total*100:.1f}%)
   - Rosettes use ok- PREFIX at {ros_prefixes.get('ok', 0)/ros_total*100:.1f}% (B uses {b_prefixes.get('ok', 0)/b_total*100:.1f}%, A uses {a_prefixes.get('ok', 0)/a_total*100:.1f}%)
   - Rosettes use ch- PREFIX at {ros_prefixes.get('ch', 0)/ros_total*100:.1f}% (B uses {b_prefixes.get('ch', 0)/b_total*100:.1f}%, A uses {a_prefixes.get('ch', 0)/a_total*100:.1f}%)

""")

if closer_to_a and vocab_a_like:
    print("CONCLUSION: Rosettes are linguistically CURRIER A, despite being")
    print("classified as Currier B in the transcript.")
    print()
    print("This may indicate:")
    print("  1. Misclassification in the original Currier analysis")
    print("  2. A transitional section between A and B")
    print("  3. A distinct subcategory that shares A's vocabulary")
elif sim_ros_b > 0.95:
    print("CONCLUSION: Rosettes are standard Currier B text on foldout pages.")
else:
    print("CONCLUSION: Rosettes show mixed A/B characteristics.")
    print("They may represent a transitional or hybrid section.")
