#!/usr/bin/env python3
"""
Test: Do different RI entries (A MIDDLEs) predict different token subsets within classes?

Architecture (C502 strict interpretation):
- A records have MIDDLEs (RI entries)
- B tokens have MIDDLEs
- A MIDDLE makes B tokens with matching MIDDLE "legal"
- Those B tokens belong to instruction classes

Question: Within a given class, do different RI entries activate different tokens?
If YES → token-level discrimination is RI-specific
If NO → class membership is what matters, not specific RI
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd

PROJECT_ROOT = Path('.')

# Morphology extraction (from compute_survivor_sets.py)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    """Extract MIDDLE component from token."""
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None


# Load class-token map
map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(map_path, 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
token_to_middle = class_map['token_to_middle']
class_to_tokens = class_map['class_to_tokens']

print(f"Loaded class map: {len(token_to_class)} B tokens in {len(class_to_tokens)} classes")

# Build MIDDLE → B tokens mapping
middle_to_b_tokens = defaultdict(set)
for token, middle in token_to_middle.items():
    if middle:
        middle_to_b_tokens[middle].add(token)

print(f"Unique MIDDLEs in B instruction classes: {len(middle_to_b_tokens)}")

# Load transcript
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

# Get A MIDDLEs (RI entries)
df_a = df[df['language'] == 'A'].copy()
df_a['middle'] = df_a['word'].apply(extract_middle)

a_middles = df_a['middle'].dropna().unique()
print(f"\nUnique A MIDDLEs (RI entries): {len(a_middles)}")

# Find A MIDDLEs that also exist in B instruction tokens
shared_middles = [m for m in a_middles if m in middle_to_b_tokens]
print(f"A MIDDLEs that activate B instruction tokens: {len(shared_middles)}")

# For each shared MIDDLE, get:
# 1. The B tokens it activates
# 2. The classes those tokens belong to
print("\n" + "="*70)
print("TOKEN-LEVEL ANALYSIS: Within-class token selection by RI")
print("="*70)

# Build class → {middle → tokens} mapping
class_middle_tokens = defaultdict(lambda: defaultdict(set))

for middle in shared_middles:
    for token in middle_to_b_tokens[middle]:
        cls = token_to_class.get(token)
        if cls:
            class_middle_tokens[cls][middle].add(token)

# For each class, analyze how many MIDDLEs share it and whether they use same tokens
print(f"\nClasses with multiple activating MIDDLEs: ", end='')
multi_middle_classes = [c for c, middles in class_middle_tokens.items() if len(middles) >= 2]
print(len(multi_middle_classes))

# Detailed analysis
print("\n--- Token overlap analysis within classes ---")

class_metrics = []
for cls in sorted(multi_middle_classes, key=lambda c: -len(class_middle_tokens[c])):
    middles_dict = class_middle_tokens[cls]
    n_middles = len(middles_dict)

    # Get all tokens in this class activated by any shared MIDDLE
    all_tokens = set()
    for tokens in middles_dict.values():
        all_tokens.update(tokens)

    # Calculate pairwise Jaccard between MIDDLEs within this class
    middle_list = list(middles_dict.keys())
    jaccards = []
    for i in range(len(middle_list)):
        for j in range(i+1, len(middle_list)):
            set_i = middles_dict[middle_list[i]]
            set_j = middles_dict[middle_list[j]]
            if set_i and set_j:
                jacc = len(set_i & set_j) / len(set_i | set_j)
                jaccards.append(jacc)

    if jaccards:
        avg_jacc = sum(jaccards) / len(jaccards)
        class_metrics.append((cls, n_middles, len(all_tokens), avg_jacc, len(jaccards)))

# Sort by number of MIDDLEs (most data first)
class_metrics.sort(key=lambda x: -x[1])

print(f"\n{'Class':>6} {'#MID':>5} {'#Tok':>5} {'AvgJacc':>8} {'#Pairs':>7}")
print("-" * 40)
for cls, n_mid, n_tok, avg_jacc, n_pairs in class_metrics[:20]:
    print(f"{cls:>6} {n_mid:>5} {n_tok:>5} {avg_jacc:>8.3f} {n_pairs:>7}")

# Overall statistics
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if class_metrics:
    all_jaccards = [m[3] for m in class_metrics]
    overall_avg = sum(all_jaccards) / len(all_jaccards)

    print(f"\nClasses analyzed: {len(class_metrics)}")
    print(f"Overall avg within-class Jaccard: {overall_avg:.3f}")

    # Interpretation
    print(f"\nInterpretation:")
    if overall_avg > 0.7:
        print("  HIGH overlap (>0.7): Different RIs activate SAME tokens within classes")
        print("  → Token selection is CLASS-driven, not RI-specific")
        print("  → MIDDLE determines class membership, not token identity")
    elif overall_avg < 0.3:
        print("  LOW overlap (<0.3): Different RIs activate DIFFERENT tokens within classes")
        print("  → Token selection is RI-SPECIFIC")
        print("  → Same MIDDLE can map to different tokens depending on context")
    else:
        print(f"  MODERATE overlap ({overall_avg:.2f}): Mixed picture")
        print("  → Some within-class differentiation, but class is primary driver")

    # Find most discriminating classes (lowest Jaccard)
    print("\n--- Most RI-discriminating classes (lowest within-class overlap) ---")
    for cls, n_mid, n_tok, avg_jacc, n_pairs in sorted(class_metrics, key=lambda x: x[3])[:10]:
        print(f"  Class {cls}: Jaccard {avg_jacc:.3f} ({n_mid} MIDDLEs, {n_tok} tokens)")

    print("\n--- Least RI-discriminating classes (highest overlap) ---")
    for cls, n_mid, n_tok, avg_jacc, n_pairs in sorted(class_metrics, key=lambda x: -x[3])[:10]:
        print(f"  Class {cls}: Jaccard {avg_jacc:.3f} ({n_mid} MIDDLEs, {n_tok} tokens)")

# Deep dive: Show token breakdown for a few classes
print("\n" + "="*70)
print("DEEP DIVE: Token breakdown by MIDDLE for sample classes")
print("="*70)

for cls, n_mid, n_tok, avg_jacc, n_pairs in class_metrics[:5]:
    print(f"\n--- Class {cls} (Jaccard={avg_jacc:.3f}) ---")
    middles_dict = class_middle_tokens[cls]

    # Show first 5 MIDDLEs and their tokens
    for i, (middle, tokens) in enumerate(list(middles_dict.items())[:5]):
        tokens_str = ', '.join(sorted(tokens)[:5])
        if len(tokens) > 5:
            tokens_str += f'... (+{len(tokens)-5})'
        print(f"  MIDDLE '{middle}': {tokens_str}")

    # Check if any tokens are exclusive to specific MIDDLEs
    token_counts = Counter()
    for tokens in middles_dict.values():
        for t in tokens:
            token_counts[t] += 1

    exclusive = [t for t, c in token_counts.items() if c == 1]
    shared = [t for t, c in token_counts.items() if c > 1]
    print(f"  Exclusive tokens (1 MIDDLE only): {len(exclusive)}")
    print(f"  Shared tokens (2+ MIDDLEs): {len(shared)}")
