#!/usr/bin/env python3
"""
Verify: Is the zero-overlap structural or meaningful?

The zero Jaccard could be because tokens with different MIDDLEs are
by definition different tokens. Let's check:

1. Can multiple MIDDLEs ever activate the same token? (No, by construction)
2. Can the same MIDDLE appear in multiple tokens of the same class?
3. What's the actual relationship: MIDDLE → token → class?
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')

# Load class-token map
map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(map_path, 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
token_to_middle = class_map['token_to_middle']
class_to_tokens = class_map['class_to_tokens']

print("="*70)
print("VERIFYING TOKEN-MIDDLE RELATIONSHIP STRUCTURE")
print("="*70)

# Question 1: Is MIDDLE → token 1:1 or 1:many?
middle_to_tokens = defaultdict(list)
for token, middle in token_to_middle.items():
    if middle:
        middle_to_tokens[middle].append(token)

one_to_one = sum(1 for m, ts in middle_to_tokens.items() if len(ts) == 1)
one_to_many = sum(1 for m, ts in middle_to_tokens.items() if len(ts) > 1)

print(f"\n1. MIDDLE → token relationship:")
print(f"   MIDDLEs with exactly 1 token: {one_to_one}")
print(f"   MIDDLEs with multiple tokens: {one_to_many}")

if one_to_many > 0:
    print(f"\n   Examples of 1:many MIDDLEs:")
    for middle, tokens in list(middle_to_tokens.items())[:10]:
        if len(tokens) > 1:
            classes = [token_to_class.get(t, '?') for t in tokens]
            print(f"     MIDDLE '{middle}': {len(tokens)} tokens → classes {set(classes)}")
            for t in tokens[:5]:
                print(f"       - {t} (class {token_to_class.get(t, '?')})")

# Question 2: Do tokens within the same class share a MIDDLE?
print(f"\n2. Within-class MIDDLE sharing:")

class_middle_sharing = {}
for cls, tokens in class_to_tokens.items():
    middles_in_class = [token_to_middle.get(t) for t in tokens]
    unique_middles = len(set(middles_in_class))
    total_tokens = len(tokens)
    class_middle_sharing[cls] = (unique_middles, total_tokens)

# Find classes where multiple tokens share a MIDDLE
shared_middle_classes = []
for cls, tokens in class_to_tokens.items():
    middle_counts = Counter(token_to_middle.get(t) for t in tokens)
    shared = [(m, c) for m, c in middle_counts.items() if c > 1 and m]
    if shared:
        shared_middle_classes.append((cls, shared, len(tokens)))

print(f"   Classes with tokens sharing the same MIDDLE: {len(shared_middle_classes)}")

for cls, shared, n_tokens in shared_middle_classes[:10]:
    print(f"\n   Class {cls} ({n_tokens} tokens):")
    for middle, count in shared:
        matching = [t for t in class_to_tokens[cls] if token_to_middle.get(t) == middle]
        print(f"     MIDDLE '{middle}' → {count} tokens: {matching}")

# Question 3: The fundamental structure
print(f"\n3. FUNDAMENTAL STRUCTURE:")
print(f"   Total tokens: {len(token_to_class)}")
print(f"   Total classes: {len(class_to_tokens)}")
print(f"   Unique MIDDLEs in tokens: {len(middle_to_tokens)}")

# The key insight: Is class determined by MIDDLE, or can same MIDDLE appear in multiple classes?
middle_to_classes = defaultdict(set)
for token, middle in token_to_middle.items():
    if middle:
        cls = token_to_class.get(token)
        if cls:
            middle_to_classes[middle].add(cls)

single_class_middles = sum(1 for m, cs in middle_to_classes.items() if len(cs) == 1)
multi_class_middles = sum(1 for m, cs in middle_to_classes.items() if len(cs) > 1)

print(f"\n   MIDDLEs mapping to single class: {single_class_middles}")
print(f"   MIDDLEs mapping to multiple classes: {multi_class_middles}")

if multi_class_middles > 0:
    print(f"\n   Examples of MIDDLEs spanning multiple classes:")
    for middle, classes in list(middle_to_classes.items()):
        if len(classes) > 1:
            tokens_per_class = {}
            for t in middle_to_tokens[middle]:
                cls = token_to_class.get(t)
                if cls not in tokens_per_class:
                    tokens_per_class[cls] = []
                tokens_per_class[cls].append(t)
            print(f"     MIDDLE '{middle}' → {len(classes)} classes:")
            for cls, toks in tokens_per_class.items():
                print(f"       Class {cls}: {toks[:3]}{'...' if len(toks)>3 else ''}")

# Conclusion
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if multi_class_middles > 0:
    print("""
The same MIDDLE can appear in tokens belonging to DIFFERENT classes.
This means:
  - MIDDLE does NOT determine class (class is a separate dimension)
  - MIDDLE determines which specific tokens are legal
  - Class groups tokens by FUNCTION, not by MIDDLE

Therefore: Different RI entries (A MIDDLEs) activate different tokens
even within the same class because the MIDDLE is part of the token identity,
and tokens with different MIDDLEs are distinct even if functionally similar.

This is TOKEN-LEVEL SPECIFICITY: RI doesn't just select a class,
it selects specific tokens within classes based on MIDDLE matching.
""")
else:
    print("""
Each MIDDLE maps to exactly one class.
This means MIDDLE → class is deterministic.
Token-level discrimination is a direct consequence of MIDDLE identity.
""")
