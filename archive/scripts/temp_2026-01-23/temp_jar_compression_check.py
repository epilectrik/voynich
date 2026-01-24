#!/usr/bin/env python3
"""
Check if jar labels are compound/compressed forms.

Questions:
1. Are jar labels longer than typical tokens?
2. Do they decompose into known PP components?
3. Are there shorter tokens that could be "base forms"?
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).parent

def extract_middle(token):
    """Extract MIDDLE from token."""
    prefixes = ['qok', 'qot', 'cph', 'cth', 'pch', 'tch', 'ckh', 'qo', 'ch', 'sh',
                'ok', 'ot', 'op', 'ol', 'or', 'da', 'sa', 'so', 'ct', 'yk', 'do',
                'ar', 'po', 'oe', 'os', 'al', 'of', 'cp', 'ko', 'yd', 'sy']
    suffixes = ['aiin', 'oiin', 'iin', 'ain', 'dy', 'hy', 'ky', 'ly', 'my', 'ny',
                'ry', 'sy', 'ty', 'am', 'an', 'al', 'ar', 'ol', 'or', 'y', 's',
                'g', 'd', 'l', 'r', 'n', 'm']

    middle = str(token).strip()
    prefix_found = None
    suffix_found = None

    for p in sorted(prefixes, key=len, reverse=True):
        if middle.startswith(p) and len(middle) > len(p):
            prefix_found = p
            middle = middle[len(p):]
            break
    for s in sorted(suffixes, key=len, reverse=True):
        if middle.endswith(s) and len(middle) > len(s):
            suffix_found = s
            middle = middle[:-len(s)]
            break
    return prefix_found, middle, suffix_found

# Load transcript for comparison
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_text = df[~df['placement'].str.startswith('L', na=False)]

a_tokens = set(df_text[df_text['language'] == 'A']['word'].dropna().unique())
b_tokens = set(df_text[df_text['language'] == 'B']['word'].dropna().unique())
pp_tokens = a_tokens & b_tokens

# Get PP MIDDLEs for decomposition check
pp_middles = set()
for token in pp_tokens:
    _, mid, _ = extract_middle(token)
    if mid and len(mid) >= 2:
        pp_middles.add(mid)

print(f"PP MIDDLEs available for decomposition: {len(pp_middles)}")

# Jar labels
jar_labels = ['daramdal', 'dardsh', 'darolaly', 'ddardsh', 'dordod', 'keoraiiin',
              'okaradag', 'okaramy', 'okoldody', 'okolky', 'okrolda', 'oparal',
              'oralas', 'porshols', 'tsholdy', 'yteoldy']

print("\n" + "=" * 70)
print("JAR LABEL LENGTH ANALYSIS")
print("=" * 70)

# Compare lengths
a_lengths = [len(t) for t in a_tokens]
jar_lengths = [len(j) for j in jar_labels]

print(f"\nCurrier A token lengths: mean={sum(a_lengths)/len(a_lengths):.1f}, median={sorted(a_lengths)[len(a_lengths)//2]}")
print(f"Jar label lengths: mean={sum(jar_lengths)/len(jar_lengths):.1f}, median={sorted(jar_lengths)[len(jar_lengths)//2]}")
print(f"\nJar labels: {sorted(jar_labels, key=len)}")
print(f"Lengths: {sorted(jar_lengths)}")

print("\n" + "=" * 70)
print("JAR LABEL DECOMPOSITION")
print("=" * 70)

for jar in sorted(jar_labels, key=len):
    prefix, middle, suffix = extract_middle(jar)

    print(f"\n{jar} (len={len(jar)}):")
    print(f"  PREFIX: {prefix}")
    print(f"  MIDDLE: {middle} (len={len(middle) if middle else 0})")
    print(f"  SUFFIX: {suffix}")

    # Check if MIDDLE contains PP MIDDLEs as substrings
    if middle and len(middle) >= 2:
        contained_pp = []
        for pp in pp_middles:
            if len(pp) >= 2 and pp in middle:
                contained_pp.append(pp)

        # Sort by length descending to show longest matches first
        contained_pp = sorted(contained_pp, key=len, reverse=True)[:10]
        print(f"  PP atoms in MIDDLE: {contained_pp}")

print("\n" + "=" * 70)
print("CHECKING FOR SHORTER BASE FORMS IN VOCABULARY")
print("=" * 70)

all_tokens = a_tokens | b_tokens

for jar in sorted(jar_labels, key=len):
    # Look for tokens that are substrings of this jar label
    base_forms = []
    for token in all_tokens:
        if len(token) >= 3 and token in jar and token != jar:
            base_forms.append(token)

    # Also check if jar is prefix of other tokens
    extensions = []
    for token in all_tokens:
        if token.startswith(jar) and token != jar:
            extensions.append(token)

    if base_forms or extensions:
        print(f"\n{jar}:")
        if base_forms:
            base_forms = sorted(base_forms, key=len, reverse=True)[:8]
            print(f"  Shorter forms contained: {base_forms}")
        if extensions:
            print(f"  Extensions of this: {extensions[:5]}")

print("\n" + "=" * 70)
print("COMPRESSION ANALYSIS - OVERLAPPING PP ATOMS")
print("=" * 70)

def find_overlapping_pp(token, pp_set):
    """Find PP atoms that could share hinge letters in this token."""
    found = []
    for pp in pp_set:
        if pp in token and len(pp) >= 2:
            found.append(pp)

    # Check for overlaps (shared hinges)
    overlaps = []
    for i, pp1 in enumerate(found):
        for pp2 in found[i+1:]:
            # Check if end of pp1 = start of pp2 (or vice versa)
            for hinge_len in [1, 2]:
                if len(pp1) > hinge_len and len(pp2) > hinge_len:
                    if pp1[-hinge_len:] == pp2[:hinge_len]:
                        overlaps.append((pp1, pp2, pp1[-hinge_len:]))
                    if pp2[-hinge_len:] == pp1[:hinge_len]:
                        overlaps.append((pp2, pp1, pp2[-hinge_len:]))
    return found, overlaps

for jar in sorted(jar_labels, key=len, reverse=True)[:8]:
    _, middle, _ = extract_middle(jar)
    if middle:
        found, overlaps = find_overlapping_pp(middle, pp_middles)

        print(f"\n{jar} (MIDDLE='{middle}'):")
        print(f"  PP atoms found: {len(found)}")
        if overlaps:
            print(f"  Overlapping pairs (compression): {len(overlaps)}")
            for pp1, pp2, hinge in overlaps[:5]:
                print(f"    {pp1} + {pp2} via '{hinge}'")
