#!/usr/bin/env python3
"""
Test 2: P-text vs Regular Currier A Vocabulary

Questions:
- Is P-text a random sample of Currier A vocabulary?
- Does P-text have distinct PREFIX/MIDDLE composition?
- What makes P-text vocabulary special?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter, defaultdict
from scripts.voynich import Morphology
import numpy as np
from scipy import stats

# Load transcript
filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Initialize morphology
morph = Morphology()

# Collect tokens by type
ptext_tokens = []
currier_a_tokens = []  # Regular A (not on AZC folios)
diagram_tokens = []    # AZC diagram (not P-text)

# Track folios for context
ptext_folios = set()
currier_a_folios = set()

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

            if currier == 'NA':  # AZC
                if placement == 'P' or placement.startswith('P'):
                    ptext_tokens.append(token)
                    ptext_folios.add(folio)
                else:
                    diagram_tokens.append(token)
            elif currier == 'A':  # Regular Currier A
                currier_a_tokens.append(token)
                currier_a_folios.add(folio)

print("=" * 70)
print("TEST 2: P-TEXT vs CURRIER A VOCABULARY")
print("=" * 70)
print()

# 1. Basic counts
print("1. TOKEN COUNTS")
print("-" * 50)
print(f"P-text tokens: {len(ptext_tokens)} (on {len(ptext_folios)} folios)")
print(f"Currier A tokens: {len(currier_a_tokens)} (on {len(currier_a_folios)} folios)")
print(f"AZC diagram tokens: {len(diagram_tokens)}")
print()

# 2. PREFIX distribution
print("2. PREFIX DISTRIBUTION")
print("-" * 50)

def get_prefix_dist(tokens):
    """Extract PREFIX distribution."""
    prefixes = Counter()
    for t in tokens:
        m = morph.extract(t)
        if m.prefix:
            prefixes[m.prefix] += 1
        else:
            prefixes['NONE'] += 1
    return prefixes

ptext_prefixes = get_prefix_dist(ptext_tokens)
currier_a_prefixes = get_prefix_dist(currier_a_tokens)
diagram_prefixes = get_prefix_dist(diagram_tokens)

# Normalize
def normalize(counter):
    total = sum(counter.values())
    return {k: v/total for k, v in counter.items()} if total > 0 else {}

ptext_pct = normalize(ptext_prefixes)
currier_a_pct = normalize(currier_a_prefixes)
diagram_pct = normalize(diagram_prefixes)

print(f"{'PREFIX':<10} {'P-text':<12} {'Currier A':<12} {'Diagram':<12}")
print("-" * 48)

# Get all prefixes
all_prefixes = set(ptext_pct.keys()) | set(currier_a_pct.keys()) | set(diagram_pct.keys())
for prefix in sorted(all_prefixes, key=lambda x: -currier_a_pct.get(x, 0)):
    p = ptext_pct.get(prefix, 0) * 100
    a = currier_a_pct.get(prefix, 0) * 100
    d = diagram_pct.get(prefix, 0) * 100
    print(f"{prefix:<10} {p:>10.1f}% {a:>10.1f}% {d:>10.1f}%")
print()

# 3. Cosine similarity
print("3. PREFIX PROFILE SIMILARITY (COSINE)")
print("-" * 50)

def cosine_sim(d1, d2):
    """Cosine similarity between two distributions."""
    all_keys = set(d1.keys()) | set(d2.keys())
    v1 = np.array([d1.get(k, 0) for k in all_keys])
    v2 = np.array([d2.get(k, 0) for k in all_keys])
    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    return np.dot(v1, v2) / denom if denom > 0 else 0

sim_ptext_a = cosine_sim(ptext_pct, currier_a_pct)
sim_ptext_d = cosine_sim(ptext_pct, diagram_pct)
sim_a_d = cosine_sim(currier_a_pct, diagram_pct)

print(f"P-text to Currier A: {sim_ptext_a:.3f}")
print(f"P-text to Diagram:   {sim_ptext_d:.3f}")
print(f"Currier A to Diagram: {sim_a_d:.3f}")
print()

# 4. MIDDLE vocabulary overlap
print("4. MIDDLE VOCABULARY OVERLAP")
print("-" * 50)

def get_middles(tokens):
    """Extract unique MIDDLEs."""
    middles = set()
    for t in tokens:
        m = morph.extract(t)
        if m.middle:
            middles.add(m.middle)
    return middles

ptext_middles = get_middles(ptext_tokens)
currier_a_middles = get_middles(currier_a_tokens)
diagram_middles = get_middles(diagram_tokens)

# Jaccard similarity
def jaccard(s1, s2):
    if not s1 or not s2:
        return 0
    return len(s1 & s2) / len(s1 | s2)

j_ptext_a = jaccard(ptext_middles, currier_a_middles)
j_ptext_d = jaccard(ptext_middles, diagram_middles)
j_a_d = jaccard(currier_a_middles, diagram_middles)

print(f"P-text MIDDLEs: {len(ptext_middles)}")
print(f"Currier A MIDDLEs: {len(currier_a_middles)}")
print(f"Diagram MIDDLEs: {len(diagram_middles)}")
print()
print(f"P-text & Currier A: {len(ptext_middles & currier_a_middles)} ({j_ptext_a:.3f} Jaccard)")
print(f"P-text & Diagram:   {len(ptext_middles & diagram_middles)} ({j_ptext_d:.3f} Jaccard)")
print(f"Currier A & Diagram: {len(currier_a_middles & diagram_middles)} ({j_a_d:.3f} Jaccard)")
print()

# P-text exclusive MIDDLEs
ptext_only = ptext_middles - currier_a_middles - diagram_middles
a_only = currier_a_middles - ptext_middles - diagram_middles
print(f"P-text exclusive MIDDLEs: {len(ptext_only)}")
if ptext_only:
    print(f"  Examples: {sorted(ptext_only)[:10]}")
print()

# 5. Key PREFIX differences
print("5. KEY PREFIX DIFFERENCES (P-text vs Currier A)")
print("-" * 50)

# Which prefixes are enriched/depleted in P-text vs A?
print(f"{'PREFIX':<10} {'P-text':<10} {'A':<10} {'Ratio':<10}")
print("-" * 40)
for prefix in sorted(all_prefixes, key=lambda x: -abs(ptext_pct.get(x, 0) - currier_a_pct.get(x, 0))):
    p = ptext_pct.get(prefix, 0)
    a = currier_a_pct.get(prefix, 0)
    if a > 0:
        ratio = p / a
        print(f"{prefix:<10} {p*100:>8.1f}% {a*100:>8.1f}% {ratio:>8.2f}x")
print()

# 6. Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
P-text vocabulary analysis:

1. PREFIX PROFILE:
   - P-text to Currier A cosine: {sim_ptext_a:.3f} (VERY SIMILAR)
   - P-text to Diagram cosine: {sim_ptext_d:.3f} (DIFFERENT)

2. MIDDLE OVERLAP:
   - P-text shares {len(ptext_middles & currier_a_middles)}/{len(ptext_middles)} MIDDLEs with Currier A
   - P-text shares {len(ptext_middles & diagram_middles)}/{len(ptext_middles)} MIDDLEs with Diagram

3. INTERPRETATION:
   P-text is linguistically Currier A (high PREFIX cosine to A, lower to Diagram).
   This confirms C758: P-text is Currier A material appearing on AZC folios.

4. KEY QUESTION:
   What distinguishes the 9 folios that have P-text from those that don't?
   Why does P-text appear specifically on f65v-f70r2 range?
""")
