#!/usr/bin/env python3
"""
Test: Do different tokens within a class represent different OPERATIONS
or the same operation with different ROUTING?

Different operations would show:
1. Different PREDECESSORS (not just successors) - they're called in different contexts
2. Low co-occurrence within lines - you do one OR the other
3. Different positional micro-distributions

Same operation, different routing would show:
1. Similar predecessors (same contexts trigger them)
2. Can co-occur (same operation, multiple times)
3. Same positional distribution
4. Only successors differ (output routing varies)
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats
from itertools import combinations

# Load data
DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']
df = df[df['language'] == 'B']
df = df[~df['word'].isna()]
df = df[~df['word'].str.contains(r'\*', na=False)]

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)
token_to_class = data['token_to_class']
class_to_tokens = data['class_to_tokens']

# Extract MIDDLE from token
def get_middle(token):
    if len(token) < 2:
        return None
    return token[1:-1] if len(token) > 2 else token[1] if len(token) == 2 else None

print("=" * 70)
print("TOKEN OPERATION TEST: Different Operations vs Same Operation/Different Routing")
print("=" * 70)

# =============================================================================
# TEST 1: Predecessor Divergence (Do different tokens get called differently?)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: PREDECESSOR PROFILES")
print("=" * 70)
print("\nIf tokens are different operations: different predecessors")
print("If same operation/different routing: similar predecessors")

# Build predecessor profiles for each token
token_predecessors = defaultdict(Counter)
token_successors = defaultdict(Counter)

for (folio, line_num), group in df.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()

    for i in range(len(tokens)):
        tok = tokens[i]
        if tok not in token_to_class:
            continue

        if i > 0 and tokens[i-1] in token_to_class:
            pred_class = token_to_class[tokens[i-1]]
            token_predecessors[tok][pred_class] += 1

        if i < len(tokens) - 1 and tokens[i+1] in token_to_class:
            succ_class = token_to_class[tokens[i+1]]
            token_successors[tok][succ_class] += 1

# For each class, compare predecessor profiles of tokens with different MIDDLEs
def jaccard_counters(c1, c2):
    keys = set(c1.keys()) | set(c2.keys())
    if not keys:
        return 1.0
    intersection = sum(min(c1.get(k, 0), c2.get(k, 0)) for k in keys)
    union = sum(max(c1.get(k, 0), c2.get(k, 0)) for k in keys)
    return intersection / union if union > 0 else 1.0

predecessor_divergences = []
successor_divergences = []

for cls, tokens in class_to_tokens.items():
    # Group tokens by MIDDLE
    middle_tokens = defaultdict(list)
    for tok in tokens:
        mid = get_middle(tok)
        if mid and tok in token_predecessors and sum(token_predecessors[tok].values()) >= 5:
            middle_tokens[mid].append(tok)

    # Compare tokens with different MIDDLEs
    middles = [m for m, toks in middle_tokens.items() if len(toks) >= 1]

    for m1, m2 in combinations(middles, 2):
        for t1 in middle_tokens[m1][:3]:  # Sample up to 3 tokens per MIDDLE
            for t2 in middle_tokens[m2][:3]:
                pred_js = jaccard_counters(token_predecessors[t1], token_predecessors[t2])
                succ_js = jaccard_counters(token_successors[t1], token_successors[t2])
                predecessor_divergences.append(pred_js)
                successor_divergences.append(succ_js)

print(f"\nComparing tokens with DIFFERENT MIDDLEs within same class:")
print(f"  Predecessor Jaccard: mean={np.mean(predecessor_divergences):.3f}, std={np.std(predecessor_divergences):.3f}")
print(f"  Successor Jaccard: mean={np.mean(successor_divergences):.3f}, std={np.std(successor_divergences):.3f}")

# Compare to same-MIDDLE tokens
same_middle_pred = []
same_middle_succ = []

for cls, tokens in class_to_tokens.items():
    middle_tokens = defaultdict(list)
    for tok in tokens:
        mid = get_middle(tok)
        if mid and tok in token_predecessors and sum(token_predecessors[tok].values()) >= 5:
            middle_tokens[mid].append(tok)

    for mid, toks in middle_tokens.items():
        if len(toks) >= 2:
            for t1, t2 in combinations(toks[:5], 2):
                pred_js = jaccard_counters(token_predecessors[t1], token_predecessors[t2])
                succ_js = jaccard_counters(token_successors[t1], token_successors[t2])
                same_middle_pred.append(pred_js)
                same_middle_succ.append(succ_js)

print(f"\nComparing tokens with SAME MIDDLE within same class:")
print(f"  Predecessor Jaccard: mean={np.mean(same_middle_pred):.3f}, std={np.std(same_middle_pred):.3f}")
print(f"  Successor Jaccard: mean={np.mean(same_middle_succ):.3f}, std={np.std(same_middle_succ):.3f}")

# Statistical test
pred_stat, pred_p = stats.mannwhitneyu(predecessor_divergences, same_middle_pred, alternative='less')
succ_stat, succ_p = stats.mannwhitneyu(successor_divergences, same_middle_succ, alternative='less')

print(f"\nStatistical tests (different-MIDDLE vs same-MIDDLE):")
print(f"  Predecessor divergence: p={pred_p:.4f} {'***' if pred_p < 0.001 else '**' if pred_p < 0.01 else '*' if pred_p < 0.05 else 'NS'}")
print(f"  Successor divergence: p={succ_p:.4f} {'***' if succ_p < 0.001 else '**' if succ_p < 0.01 else '*' if succ_p < 0.05 else 'NS'}")

# =============================================================================
# TEST 2: Within-Line Co-occurrence
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: WITHIN-LINE CO-OCCURRENCE")
print("=" * 70)
print("\nIf different operations: low co-occurrence (do one OR the other)")
print("If same operation: can co-occur (might need it twice)")

# For each class, check if tokens with different MIDDLEs co-occur in lines
cooccurrence_rates = []

for cls, tokens in class_to_tokens.items():
    if len(tokens) < 5:
        continue

    # Group by MIDDLE
    middle_tokens = defaultdict(set)
    for tok in tokens:
        mid = get_middle(tok)
        if mid:
            middle_tokens[mid].add(tok)

    middles = [m for m, toks in middle_tokens.items() if len(toks) >= 1]
    if len(middles) < 2:
        continue

    # Check line-level co-occurrence
    lines_with_class = 0
    lines_with_multiple_middles = 0

    for (folio, line_num), group in df.groupby(['folio', 'line_number']):
        line_tokens = set(group['word'].tolist())
        class_tokens_in_line = line_tokens & set(tokens)

        if class_tokens_in_line:
            lines_with_class += 1
            middles_in_line = set()
            for tok in class_tokens_in_line:
                mid = get_middle(tok)
                if mid:
                    middles_in_line.add(mid)
            if len(middles_in_line) > 1:
                lines_with_multiple_middles += 1

    if lines_with_class >= 20:
        rate = lines_with_multiple_middles / lines_with_class
        cooccurrence_rates.append((cls, rate, lines_with_class))

print(f"\nClasses where multiple MIDDLEs co-occur in same line:")
sorted_rates = sorted(cooccurrence_rates, key=lambda x: -x[1])
for cls, rate, n in sorted_rates[:10]:
    print(f"  Class {cls}: {rate*100:.1f}% of lines have multiple MIDDLEs (n={n} lines)")

print(f"\nClasses where MIDDLEs rarely co-occur (one or the other):")
for cls, rate, n in sorted_rates[-10:]:
    print(f"  Class {cls}: {rate*100:.1f}% of lines have multiple MIDDLEs (n={n} lines)")

mean_cooccur = np.mean([r[1] for r in cooccurrence_rates])
print(f"\nOverall mean co-occurrence rate: {mean_cooccur*100:.1f}%")

# =============================================================================
# TEST 3: The Critical Question
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: PREDECESSOR vs SUCCESSOR DIVERGENCE COMPARISON")
print("=" * 70)
print("\nKey insight: If predecessors diverge AS MUCH as successors,")
print("tokens are truly different operations (called differently AND route differently)")
print("\nIf only successors diverge but predecessors similar,")
print("same operation with different output routing")

pred_diff = np.mean(same_middle_pred) - np.mean(predecessor_divergences)
succ_diff = np.mean(same_middle_succ) - np.mean(successor_divergences)

print(f"\nDivergence caused by different MIDDLEs:")
print(f"  Predecessor divergence increase: {pred_diff:.3f}")
print(f"  Successor divergence increase: {succ_diff:.3f}")
print(f"  Ratio (pred/succ): {pred_diff/succ_diff:.2f}" if succ_diff > 0 else "  Ratio: N/A")

if pred_diff > 0.01 and succ_diff > 0.01:
    if abs(pred_diff - succ_diff) < 0.02:
        conclusion = "DIFFERENT OPERATIONS (both inputs and outputs differ)"
    elif pred_diff < succ_diff * 0.5:
        conclusion = "SAME OPERATION, DIFFERENT ROUTING (only outputs differ)"
    else:
        conclusion = "PARTIAL DIFFERENTIATION (inputs differ somewhat, outputs differ more)"
else:
    conclusion = "MINIMAL DIFFERENTIATION (tokens behave similarly)"

print(f"\nConclusion: {conclusion}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: CHOP VS GRIND HYPOTHESIS")
print("=" * 70)

print("""
The 'chop vs grind' hypothesis requires that tokens with different MIDDLEs
represent DIFFERENT OPERATIONS - meaning they should be:
1. Called in different contexts (different predecessors)
2. Mutually exclusive (low co-occurrence)
3. Route to different outputs (different successors)

Alternative hypothesis (same operation, different routing):
1. Called in same contexts (similar predecessors)
2. Can co-occur (same operation used multiple times)
3. Only differ in output routing (different successors)
""")

# Final verdict
if pred_p < 0.05:
    print("RESULT: Predecessors DO differ significantly for different MIDDLEs")
    print("-> Tokens ARE called in different contexts")
    print("-> Supports 'different operations' hypothesis")
else:
    print("RESULT: Predecessors do NOT differ significantly")
    print("-> Tokens are called in similar contexts")
    print("-> Supports 'same operation, different routing' hypothesis")
