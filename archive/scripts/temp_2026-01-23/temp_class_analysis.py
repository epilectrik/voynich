#!/usr/bin/env python3
"""Analyze class-token redundancy to understand PP composition effects."""

import json
from collections import defaultdict

# Load class-token mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)

# Invert token_to_class to get class_to_tokens
token_to_class = data['token_to_class']
class_to_tokens = defaultdict(list)
for token, cls in token_to_class.items():
    class_to_tokens[cls].append(token)

class_map = dict(class_to_tokens)

# Analyze class sizes
sizes = [(cls, len(tokens)) for cls, tokens in class_map.items()]
sizes.sort(key=lambda x: -x[1])

print("=" * 60)
print("CLASS-TOKEN REDUNDANCY ANALYSIS")
print("=" * 60)

print("\nTop 10 largest classes:")
for cls, size in sizes[:10]:
    print(f"  Class {cls}: {size} tokens")

print(f"\nTotal classes: {len(sizes)}")
print(f"Mean tokens/class: {sum(s for _,s in sizes)/len(sizes):.1f}")
print(f"Min: {min(s for _,s in sizes)}, Max: {max(s for _,s in sizes)}")

small = sum(1 for _,s in sizes if s <= 2)
print(f"Classes with <=2 tokens: {small} ({100*small/len(sizes):.1f}%)")

# Now check: how many unique MIDDLEs per class?
print("\n" + "=" * 60)
print("MIDDLE DIVERSITY PER CLASS")
print("=" * 60)

# We already have token list from class_map

# Extract MIDDLEs for each class
def extract_middle(token):
    """Extract MIDDLE from token (simplified)."""
    PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
                'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
                'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
    ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
    SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
                'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
                'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
                'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

    for p in ALL_PREFIXES:
        if token.startswith(p):
            remainder = token[len(p):]
            for s in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(s):
                    return remainder[:-len(s)] or None
            return remainder or None
    return None

class_middles = {}
for cls, tokens in class_map.items():
    middles = set()
    for tok in tokens:
        m = extract_middle(tok)
        if m:
            middles.add(m)
    class_middles[cls] = middles

# Report
print("\nMIDDLE diversity by class:")
diversity = [(cls, len(mids)) for cls, mids in class_middles.items()]
diversity.sort(key=lambda x: -x[1])

for cls, n_middles in diversity[:10]:
    n_tokens = len(class_map[cls])
    print(f"  Class {cls}: {n_middles} unique MIDDLEs across {n_tokens} tokens")

print(f"\nMean MIDDLEs/class: {sum(d for _,d in diversity)/len(diversity):.1f}")
single_middle = sum(1 for _,d in diversity if d <= 1)
print(f"Classes with <=1 MIDDLE: {single_middle} ({100*single_middle/len(diversity):.1f}%)")

# Key question: if PP composition changes, does token-level availability change?
print("\n" + "=" * 60)
print("KEY INSIGHT")
print("=" * 60)
print("""
PP composition DOES affect token-level availability:
- If PP = {'a', 'o'}, only tokens with MIDDLE 'a' or 'o' are legal
- If PP = {'e', 'ee'}, only tokens with MIDDLE 'e' or 'ee' are legal

But class-level survival is REDUNDANT:
- Classes survive if ANY member token has a legal MIDDLE
- Large classes (~50+ tokens) have many MIDDLEs, so most PP sets enable them
- Small classes (1-2 tokens) are more sensitive to specific PP composition

This explains why:
- PP COUNT matters for class survival (more PP = more classes enabled)
- PP COMPOSITION doesn't matter for class PATTERN (redundancy masks composition)
- PP COMPOSITION DOES matter for WHICH TOKENS within a class are available
""")
