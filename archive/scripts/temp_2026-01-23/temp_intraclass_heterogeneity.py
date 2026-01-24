#!/usr/bin/env python3
"""
Intra-Class Token Heterogeneity Test

Question: Do tokens within the same class behave differently?

Key insight from user: Positional compatibility ≠ functional equivalence.
"Chop" and "grind" can appear in same position but mean different things.

So:
- If tokens DIFFER behaviorally → definitely not just spelling variants
- If tokens are SIMILAR → ambiguous (could be variants OR different-but-compatible operations)

We test for DIFFERENCE, not sameness.
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats
from scipy.spatial.distance import jensenshannon
import warnings
warnings.filterwarnings('ignore')

# Load data
DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
df = df[df['transcriber'] == 'H']
df = df[df['language'] == 'B']  # B execution only
df = df[~df['word'].isna()]
df = df[~df['word'].str.contains(r'\*', na=False)]

# Load class-token mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    data = json.load(f)

token_to_class = data['token_to_class']
token_to_middle = data['token_to_middle']

# Build class structures
class_to_tokens = defaultdict(list)
class_to_middles = defaultdict(set)
for token, cls in token_to_class.items():
    class_to_tokens[cls].append(token)
    m = token_to_middle.get(token)
    if m:
        class_to_middles[cls].add(m)

print("=" * 70)
print("INTRA-CLASS TOKEN HETEROGENEITY TEST")
print("=" * 70)
print(f"\nB corpus tokens: {len(df)}")
print(f"Classes with multiple MIDDLEs: {sum(1 for c in class_to_middles if len(class_to_middles[c]) > 1)}")

# Build token usage statistics
token_stats = defaultdict(lambda: {
    'count': 0,
    'positions': [],  # position in line
    'successors': [],  # what follows
    'predecessors': [],  # what precedes
    'line_lengths': [],  # length of line it appears in
})

# Process by folio and line
for (folio, line_num), group in df.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()  # Already in order within line
    n = len(tokens)

    for i, tok in enumerate(tokens):
        if tok not in token_to_class:
            continue

        token_stats[tok]['count'] += 1
        token_stats[tok]['positions'].append(i / max(n-1, 1) if n > 1 else 0.5)  # normalized position
        token_stats[tok]['line_lengths'].append(n)

        if i > 0:
            token_stats[tok]['predecessors'].append(tokens[i-1])
        if i < n - 1:
            token_stats[tok]['successors'].append(tokens[i+1])

print(f"Tokens with usage data: {len(token_stats)}")

# =============================================================================
# TEST 1: Positional Distribution Divergence Within Classes
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: POSITIONAL DISTRIBUTION DIVERGENCE")
print("=" * 70)
print("\nDo tokens in the same class appear in different positions?")
print("(Remember: same position doesn't mean same function)")

# For each class with multiple tokens, compare positional distributions
positional_divergences = []
classes_with_divergence = []

for cls in sorted(class_to_tokens.keys()):
    tokens = [t for t in class_to_tokens[cls] if token_stats[t]['count'] >= 10]
    if len(tokens) < 2:
        continue

    # Get positional distributions
    pos_dists = {}
    for tok in tokens:
        positions = token_stats[tok]['positions']
        if len(positions) >= 10:
            # Bin into 5 position buckets
            hist, _ = np.histogram(positions, bins=5, range=(0, 1), density=True)
            hist = hist / hist.sum() if hist.sum() > 0 else hist
            pos_dists[tok] = hist

    if len(pos_dists) < 2:
        continue

    # Compare all pairs
    tokens_with_dists = list(pos_dists.keys())
    for i in range(len(tokens_with_dists)):
        for j in range(i+1, len(tokens_with_dists)):
            t1, t2 = tokens_with_dists[i], tokens_with_dists[j]
            js = jensenshannon(pos_dists[t1], pos_dists[t2])
            if not np.isnan(js):
                positional_divergences.append({
                    'class': cls,
                    'token1': t1,
                    'token2': t2,
                    'middle1': token_to_middle.get(t1),
                    'middle2': token_to_middle.get(t2),
                    'js_divergence': js,
                    'same_middle': token_to_middle.get(t1) == token_to_middle.get(t2)
                })

if positional_divergences:
    pos_df = pd.DataFrame(positional_divergences)

    print(f"\nToken pairs compared: {len(pos_df)}")
    print(f"Mean JS divergence: {pos_df['js_divergence'].mean():.4f}")
    print(f"Max JS divergence: {pos_df['js_divergence'].max():.4f}")

    # Compare same-MIDDLE vs different-MIDDLE pairs
    same_mid = pos_df[pos_df['same_middle']]
    diff_mid = pos_df[~pos_df['same_middle']]

    print(f"\nSame-MIDDLE pairs: {len(same_mid)}, mean JS = {same_mid['js_divergence'].mean():.4f}")
    print(f"Different-MIDDLE pairs: {len(diff_mid)}, mean JS = {diff_mid['js_divergence'].mean():.4f}")

    if len(same_mid) > 5 and len(diff_mid) > 5:
        stat, p = stats.mannwhitneyu(same_mid['js_divergence'], diff_mid['js_divergence'])
        print(f"Mann-Whitney U: p = {p:.4f}")

        if p < 0.05:
            print("-> Different-MIDDLE tokens have DIFFERENT positional profiles")
        else:
            print("-> No significant difference (could mean similar OR compatible-but-different)")

# =============================================================================
# TEST 2: Transition Pattern Divergence Within Classes
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: TRANSITION PATTERN DIVERGENCE")
print("=" * 70)
print("\nDo tokens in the same class have different successors?")

# For each class, compare successor distributions
transition_divergences = []

for cls in sorted(class_to_tokens.keys()):
    tokens = [t for t in class_to_tokens[cls] if len(token_stats[t]['successors']) >= 10]
    if len(tokens) < 2:
        continue

    # Get successor class distributions (not specific tokens)
    succ_dists = {}
    for tok in tokens:
        succs = token_stats[tok]['successors']
        succ_classes = [token_to_class.get(s, -1) for s in succs]
        counter = Counter(succ_classes)
        total = sum(counter.values())
        # Create distribution over all 49 classes + unknown
        dist = np.zeros(50)
        for c, count in counter.items():
            if c == -1:
                dist[49] = count / total
            else:
                dist[c-1] = count / total
        succ_dists[tok] = dist

    if len(succ_dists) < 2:
        continue

    # Compare all pairs
    tokens_with_dists = list(succ_dists.keys())
    for i in range(len(tokens_with_dists)):
        for j in range(i+1, len(tokens_with_dists)):
            t1, t2 = tokens_with_dists[i], tokens_with_dists[j]
            js = jensenshannon(succ_dists[t1], succ_dists[t2])
            if not np.isnan(js):
                transition_divergences.append({
                    'class': cls,
                    'token1': t1,
                    'token2': t2,
                    'middle1': token_to_middle.get(t1),
                    'middle2': token_to_middle.get(t2),
                    'js_divergence': js,
                    'same_middle': token_to_middle.get(t1) == token_to_middle.get(t2)
                })

if transition_divergences:
    trans_df = pd.DataFrame(transition_divergences)

    print(f"\nToken pairs compared: {len(trans_df)}")
    print(f"Mean JS divergence: {trans_df['js_divergence'].mean():.4f}")
    print(f"Max JS divergence: {trans_df['js_divergence'].max():.4f}")

    # Compare same-MIDDLE vs different-MIDDLE pairs
    same_mid = trans_df[trans_df['same_middle']]
    diff_mid = trans_df[~trans_df['same_middle']]

    print(f"\nSame-MIDDLE pairs: {len(same_mid)}, mean JS = {same_mid['js_divergence'].mean():.4f}")
    print(f"Different-MIDDLE pairs: {len(diff_mid)}, mean JS = {diff_mid['js_divergence'].mean():.4f}")

    if len(same_mid) > 5 and len(diff_mid) > 5:
        stat, p = stats.mannwhitneyu(same_mid['js_divergence'], diff_mid['js_divergence'])
        print(f"Mann-Whitney U: p = {p:.4f}")

        if p < 0.05:
            print("-> Different-MIDDLE tokens have DIFFERENT transition patterns")
        else:
            print("-> No significant difference")

# =============================================================================
# TEST 3: Specific Examples of Intra-Class Divergence
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: EXAMPLES OF MAXIMUM INTRA-CLASS DIVERGENCE")
print("=" * 70)

if transition_divergences:
    # Find most divergent pairs within same class
    trans_df_sorted = trans_df.sort_values('js_divergence', ascending=False)

    print("\nMost behaviorally divergent token pairs within same class:")
    print("-" * 60)

    seen_classes = set()
    for _, row in trans_df_sorted.iterrows():
        if row['class'] in seen_classes:
            continue
        seen_classes.add(row['class'])

        t1, t2 = row['token1'], row['token2']
        m1, m2 = row['middle1'], row['middle2']

        print(f"\nClass {row['class']}:")
        print(f"  {t1} (MIDDLE={m1}) vs {t2} (MIDDLE={m2})")
        print(f"  Transition JS divergence: {row['js_divergence']:.4f}")
        print(f"  Counts: {token_stats[t1]['count']} vs {token_stats[t2]['count']}")

        # Show top successors for each
        succ1 = Counter(token_stats[t1]['successors']).most_common(3)
        succ2 = Counter(token_stats[t2]['successors']).most_common(3)
        print(f"  Top successors of {t1}: {succ1}")
        print(f"  Top successors of {t2}: {succ2}")

        if len(seen_classes) >= 5:
            break

# =============================================================================
# TEST 4: MIDDLE-Level Aggregation
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: MIDDLE-LEVEL BEHAVIORAL DIVERGENCE")
print("=" * 70)
print("\nAggregating by MIDDLE within each class...")

# For each class, group tokens by MIDDLE and compare MIDDLE-level distributions
middle_divergences = []

for cls in sorted(class_to_tokens.keys()):
    middles_in_class = list(class_to_middles[cls])
    if len(middles_in_class) < 2:
        continue

    # Aggregate successors by MIDDLE
    middle_succs = defaultdict(list)
    for tok in class_to_tokens[cls]:
        m = token_to_middle.get(tok)
        if m and len(token_stats[tok]['successors']) > 0:
            middle_succs[m].extend(token_stats[tok]['successors'])

    # Filter to MIDDLEs with enough data
    valid_middles = [m for m in middle_succs if len(middle_succs[m]) >= 20]
    if len(valid_middles) < 2:
        continue

    # Build distributions
    middle_dists = {}
    for m in valid_middles:
        succs = middle_succs[m]
        succ_classes = [token_to_class.get(s, -1) for s in succs]
        counter = Counter(succ_classes)
        total = sum(counter.values())
        dist = np.zeros(50)
        for c, count in counter.items():
            if c == -1:
                dist[49] = count / total
            else:
                dist[c-1] = count / total
        middle_dists[m] = dist

    # Compare all MIDDLE pairs
    middles_list = list(middle_dists.keys())
    for i in range(len(middles_list)):
        for j in range(i+1, len(middles_list)):
            m1, m2 = middles_list[i], middles_list[j]
            js = jensenshannon(middle_dists[m1], middle_dists[m2])
            if not np.isnan(js):
                middle_divergences.append({
                    'class': cls,
                    'middle1': m1,
                    'middle2': m2,
                    'js_divergence': js,
                    'n1': len(middle_succs[m1]),
                    'n2': len(middle_succs[m2])
                })

if middle_divergences:
    mid_df = pd.DataFrame(middle_divergences)

    print(f"\nMIDDLE pairs compared: {len(mid_df)}")
    print(f"Mean JS divergence: {mid_df['js_divergence'].mean():.4f}")
    print(f"Median JS divergence: {mid_df['js_divergence'].median():.4f}")
    print(f"Max JS divergence: {mid_df['js_divergence'].max():.4f}")

    # Distribution
    print(f"\nDistribution of MIDDLE-level divergence:")
    for thresh in [0.1, 0.2, 0.3, 0.4, 0.5]:
        count = (mid_df['js_divergence'] > thresh).sum()
        pct = 100 * count / len(mid_df)
        print(f"  JS > {thresh}: {count} ({pct:.1f}%)")

    # Top divergent MIDDLE pairs
    print("\nMost divergent MIDDLE pairs within same class:")
    top_mid = mid_df.nlargest(5, 'js_divergence')
    for _, row in top_mid.iterrows():
        print(f"  Class {row['class']}: {row['middle1']} vs {row['middle2']} -> JS={row['js_divergence']:.3f} (n={row['n1']},{row['n2']})")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
Key findings:

1. POSITIONAL divergence: Do tokens in same class appear in different positions?
   - If yes: They have different positional preferences
   - But: Same position could still mean different operations

2. TRANSITION divergence: Do tokens in same class have different successors?
   - If yes: They lead to different grammatical continuations
   - This is stronger evidence of behavioral difference

3. MIDDLE-level divergence: Do different MIDDLEs within a class behave differently?
   - If yes: PP composition selecting different MIDDLEs = different behavior
   - This is the key test for whether PP composition matters

INTERPRETATION FRAMEWORK:
- High divergence -> tokens are NOT just spelling variants
- Low divergence -> AMBIGUOUS (could be variants OR compatible-but-different)
- The absence of measurable difference doesn't prove sameness
""")
