#!/usr/bin/env python3
"""
Test 7: P-text Transition Patterns

Question: Does P-text follow Currier A's bigram grammar or something different?

If P-text is "A vocabulary in A structure", transition patterns should match A.
If P-text is "A vocabulary in AZC structure", patterns should differ.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scripts.voynich import Morphology

# Load transcript
filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

# Collect tokens by category
ptext_tokens = []
azc_diagram_tokens = []
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
            line_num = parts[3].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if currier == 'NA':  # AZC
                if placement == 'P' or placement.startswith('P'):
                    ptext_tokens.append((folio, line_num, token))
                else:
                    azc_diagram_tokens.append((folio, line_num, token))
            elif currier == 'A':
                currier_a_tokens.append((folio, line_num, token))

print("=" * 70)
print("TEST 7: P-TEXT TRANSITION PATTERNS")
print("=" * 70)
print()

def get_prefix(token):
    m = morph.extract(token)
    return m.prefix if m.prefix else 'NONE'

def get_bigrams(token_list):
    """Get PREFIX bigrams within same folio-line."""
    bigrams = []
    prev_key = None
    prev_prefix = None

    for folio, line, token in token_list:
        key = (folio, line)
        prefix = get_prefix(token)

        if prev_key == key and prev_prefix:
            bigrams.append((prev_prefix, prefix))

        prev_key = key
        prev_prefix = prefix

    return bigrams

ptext_bigrams = get_bigrams(ptext_tokens)
azc_bigrams = get_bigrams(azc_diagram_tokens)
a_bigrams = get_bigrams(currier_a_tokens)

print("1. BIGRAM COUNTS")
print("-" * 50)
print(f"P-text bigrams: {len(ptext_bigrams)}")
print(f"AZC diagram bigrams: {len(azc_bigrams)}")
print(f"Currier A bigrams: {len(a_bigrams)}")
print()

# Get top bigrams for each
ptext_top = Counter(ptext_bigrams).most_common(15)
azc_top = Counter(azc_bigrams).most_common(15)
a_top = Counter(a_bigrams).most_common(15)

print("2. TOP BIGRAMS COMPARISON")
print("-" * 50)

print("\nP-text top 15 bigrams:")
for bg, count in ptext_top:
    pct = count / len(ptext_bigrams) * 100 if ptext_bigrams else 0
    print(f"  {bg[0]:>6} -> {bg[1]:<6}: {count:4d} ({pct:.1f}%)")

print("\nCurrier A top 15 bigrams:")
for bg, count in a_top[:10]:
    pct = count / len(a_bigrams) * 100 if a_bigrams else 0
    print(f"  {bg[0]:>6} -> {bg[1]:<6}: {count:4d} ({pct:.1f}%)")

print()

# 3. Bigram distribution similarity
print("3. BIGRAM DISTRIBUTION SIMILARITY")
print("-" * 50)

def bigram_profile(bigrams):
    """Get normalized bigram distribution."""
    counts = Counter(bigrams)
    total = sum(counts.values())
    if total == 0:
        return {}
    return {bg: c/total for bg, c in counts.items()}

def cosine_similarity(profile1, profile2):
    """Cosine similarity between two profiles."""
    all_keys = set(profile1.keys()) | set(profile2.keys())
    vec1 = np.array([profile1.get(k, 0) for k in all_keys])
    vec2 = np.array([profile2.get(k, 0) for k in all_keys])

    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

ptext_profile = bigram_profile(ptext_bigrams)
azc_profile = bigram_profile(azc_bigrams)
a_profile = bigram_profile(a_bigrams)

sim_ptext_a = cosine_similarity(ptext_profile, a_profile)
sim_ptext_azc = cosine_similarity(ptext_profile, azc_profile)
sim_a_azc = cosine_similarity(a_profile, azc_profile)

print(f"P-text to Currier A similarity: {sim_ptext_a:.3f}")
print(f"P-text to AZC diagram similarity: {sim_ptext_azc:.3f}")
print(f"Currier A to AZC diagram similarity: {sim_a_azc:.3f}")
print()

# 4. Unique bigrams analysis
print("4. UNIQUE BIGRAM PATTERNS")
print("-" * 50)

ptext_bg_set = set(ptext_bigrams)
azc_bg_set = set(azc_bigrams)
a_bg_set = set(a_bigrams)

ptext_only = ptext_bg_set - a_bg_set - azc_bg_set
shared_with_a = ptext_bg_set & a_bg_set
shared_with_azc = ptext_bg_set & azc_bg_set

print(f"Bigram types in P-text: {len(ptext_bg_set)}")
print(f"Shared with Currier A: {len(shared_with_a)} ({len(shared_with_a)/len(ptext_bg_set)*100:.1f}%)")
print(f"Shared with AZC diagram: {len(shared_with_azc)} ({len(shared_with_azc)/len(ptext_bg_set)*100:.1f}%)")
print(f"Unique to P-text: {len(ptext_only)} ({len(ptext_only)/len(ptext_bg_set)*100:.1f}%)")
print()

# 5. Self-transition analysis (characteristic of AZC)
print("5. SELF-TRANSITION RATE")
print("-" * 50)
print("(AZC diagram has elevated self-transitions per C309)")
print()

def self_transition_rate(bigrams):
    if not bigrams:
        return 0
    self_trans = sum(1 for a, b in bigrams if a == b)
    return self_trans / len(bigrams)

ptext_self = self_transition_rate(ptext_bigrams)
azc_self = self_transition_rate(azc_bigrams)
a_self = self_transition_rate(a_bigrams)

print(f"P-text self-transition rate: {ptext_self:.3f}")
print(f"AZC diagram self-transition rate: {azc_self:.3f}")
print(f"Currier A self-transition rate: {a_self:.3f}")
print()

# Verdict
print("=" * 70)
print("VERDICT")
print("=" * 70)

if sim_ptext_a > sim_ptext_azc:
    pattern_verdict = "A-LIKE"
    print(f"P-text bigram patterns are MORE SIMILAR to Currier A ({sim_ptext_a:.3f} vs {sim_ptext_azc:.3f})")
else:
    pattern_verdict = "AZC-LIKE"
    print(f"P-text bigram patterns are MORE SIMILAR to AZC diagram ({sim_ptext_azc:.3f} vs {sim_ptext_a:.3f})")

if abs(ptext_self - a_self) < abs(ptext_self - azc_self):
    self_verdict = "A-LIKE"
else:
    self_verdict = "AZC-LIKE"

print(f"P-text self-transition rate is {self_verdict} ({ptext_self:.3f})")
print()
print(f"Pattern verdict: {pattern_verdict}")
print(f"Self-transition verdict: {self_verdict}")
