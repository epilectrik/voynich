#!/usr/bin/env python3
"""
Fresh Look at B Program Structure: Procedural Patterns

Question: Does B look like a procedure (sequential steps) or a state machine (reactive)?

We're looking for:
1. Sequential ordering within lines (do A, then B, then C)
2. Sequential ordering across lines (step 1, step 2, step 3)
3. Phase markers (beginning, middle, end tokens)
4. Repeated procedural chunks (like recipe steps)
5. Action vs monitoring distinction in classes
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats

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

print("=" * 70)
print("FRESH LOOK: PROCEDURAL STRUCTURE IN B PROGRAMS")
print("=" * 70)
print(f"\nB corpus: {len(df)} tokens across {df['folio'].nunique()} folios")

# =============================================================================
# TEST 1: Positional Class Distribution (Beginning/Middle/End of Lines)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: POSITIONAL CLASS DISTRIBUTION")
print("=" * 70)
print("\nDo certain classes dominate line-initial, line-medial, or line-final?")
print("(This would suggest procedural phases: 'start with X, do Y, end with Z')")

# Get position data
position_data = []
for (folio, line_num), group in df.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()
    n = len(tokens)
    if n < 3:
        continue

    for i, tok in enumerate(tokens):
        cls = token_to_class.get(tok)
        if cls is None:
            continue

        if i == 0:
            pos = 'INITIAL'
        elif i == n - 1:
            pos = 'FINAL'
        else:
            pos = 'MEDIAL'

        position_data.append({
            'class': cls,
            'position': pos,
            'folio': folio
        })

pos_df = pd.DataFrame(position_data)

# Chi-square test for position independence
contingency = pd.crosstab(pos_df['class'], pos_df['position'])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square test (class x position): chi2={chi2:.1f}, p={p:.2e}")

# Find classes with strongest positional preferences
print("\nClasses with strongest INITIAL preference (procedural 'starters'):")
initial_rates = contingency['INITIAL'] / contingency.sum(axis=1)
initial_rates = initial_rates.sort_values(ascending=False)
for cls in initial_rates.head(10).index:
    rate = initial_rates[cls]
    count = contingency.loc[cls, 'INITIAL']
    total = contingency.loc[cls].sum()
    if total >= 50:  # Minimum frequency
        print(f"  Class {cls}: {rate*100:.1f}% initial (n={total})")

print("\nClasses with strongest FINAL preference (procedural 'terminators'):")
final_rates = contingency['FINAL'] / contingency.sum(axis=1)
final_rates = final_rates.sort_values(ascending=False)
for cls in final_rates.head(10).index:
    rate = final_rates[cls]
    count = contingency.loc[cls, 'FINAL']
    total = contingency.loc[cls].sum()
    if total >= 50:
        print(f"  Class {cls}: {rate*100:.1f}% final (n={total})")

print("\nClasses with strongest MEDIAL preference (procedural 'actions'):")
medial_rates = contingency['MEDIAL'] / contingency.sum(axis=1)
medial_rates = medial_rates.sort_values(ascending=False)
for cls in medial_rates.head(10).index:
    rate = medial_rates[cls]
    total = contingency.loc[cls].sum()
    if total >= 50:
        print(f"  Class {cls}: {rate*100:.1f}% medial (n={total})")

# =============================================================================
# TEST 2: Line-Level Class Sequences (Do lines follow patterns?)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: LINE-LEVEL CLASS SEQUENCES")
print("=" * 70)
print("\nDo lines follow recurring class patterns (like recipe steps)?")

# Extract class sequences for each line
line_sequences = []
for (folio, line_num), group in df.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()
    classes = [token_to_class.get(t) for t in tokens]
    classes = [c for c in classes if c is not None]
    if len(classes) >= 3:
        line_sequences.append(tuple(classes))

print(f"\nLines with 3+ classified tokens: {len(line_sequences)}")

# Find most common class patterns (first 3 classes)
pattern_3 = Counter(seq[:3] for seq in line_sequences if len(seq) >= 3)
print(f"\nMost common 3-class opening patterns:")
for pattern, count in pattern_3.most_common(10):
    pct = 100 * count / len(line_sequences)
    print(f"  {pattern}: {count} ({pct:.1f}%)")

# Find most common full patterns (for short lines)
short_lines = [seq for seq in line_sequences if len(seq) <= 5]
pattern_full = Counter(short_lines)
print(f"\nMost common complete patterns (lines with <=5 classes):")
for pattern, count in pattern_full.most_common(10):
    if count >= 5:
        pct = 100 * count / len(short_lines)
        print(f"  {pattern}: {count} ({pct:.1f}%)")

# =============================================================================
# TEST 3: Cross-Line Progression (Do lines within folio show sequence?)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: CROSS-LINE PROGRESSION WITHIN FOLIOS")
print("=" * 70)
print("\nDo consecutive lines show class progression (step 1 -> step 2)?")

# For each folio, look at line-to-line class transitions
folio_progressions = []
for folio, folio_group in df.groupby('folio'):
    lines = sorted(folio_group['line_number'].unique())
    if len(lines) < 3:
        continue

    line_first_classes = []
    for line_num in lines:
        line_data = folio_group[folio_group['line_number'] == line_num]
        tokens = line_data['word'].tolist()
        classes = [token_to_class.get(t) for t in tokens if token_to_class.get(t)]
        if classes:
            line_first_classes.append(classes[0])  # First class of line

    if len(line_first_classes) >= 3:
        folio_progressions.append((folio, line_first_classes))

# Count line-initial class transitions
line_transitions = Counter()
for folio, classes in folio_progressions:
    for i in range(len(classes) - 1):
        line_transitions[(classes[i], classes[i+1])] += 1

print(f"\nMost common line-to-line initial class transitions:")
for (c1, c2), count in line_transitions.most_common(15):
    print(f"  Line starts {c1} -> Next line starts {c2}: {count}")

# Check for sequential patterns (same class continuing vs changing)
same_class = sum(count for (c1, c2), count in line_transitions.items() if c1 == c2)
diff_class = sum(count for (c1, c2), count in line_transitions.items() if c1 != c2)
total = same_class + diff_class
print(f"\nLine-to-line class continuity:")
print(f"  Same class continues: {same_class} ({100*same_class/total:.1f}%)")
print(f"  Class changes: {diff_class} ({100*diff_class/total:.1f}%)")

# =============================================================================
# TEST 4: Bigram Asymmetry (Is there forward directionality?)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: BIGRAM ASYMMETRY (PROCEDURAL DIRECTIONALITY)")
print("=" * 70)
print("\nIn procedures, A->B might be common but B->A rare (can't undo steps)")

# Get class bigrams
class_bigrams = Counter()
reverse_bigrams = Counter()

for (folio, line_num), group in df.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()
    classes = [token_to_class.get(t) for t in tokens]
    classes = [c for c in classes if c is not None]

    for i in range(len(classes) - 1):
        c1, c2 = classes[i], classes[i+1]
        class_bigrams[(c1, c2)] += 1

# Check asymmetry
asymmetric_pairs = []
for (c1, c2), count in class_bigrams.items():
    reverse_count = class_bigrams.get((c2, c1), 0)
    if count >= 10 and c1 != c2:
        ratio = count / max(reverse_count, 1)
        asymmetric_pairs.append((c1, c2, count, reverse_count, ratio))

asymmetric_pairs.sort(key=lambda x: -x[4])

print(f"\nMost asymmetric class bigrams (A->B common, B->A rare):")
for c1, c2, fwd, rev, ratio in asymmetric_pairs[:15]:
    print(f"  {c1}->{c2}: {fwd} times, reverse: {rev} times (ratio: {ratio:.1f}x)")

# Overall asymmetry measure
total_asymmetry = 0
total_pairs = 0
for (c1, c2), count in class_bigrams.items():
    if c1 < c2:  # Only count each pair once
        reverse_count = class_bigrams.get((c2, c1), 0)
        if count + reverse_count >= 10:
            asymmetry = abs(count - reverse_count) / (count + reverse_count)
            total_asymmetry += asymmetry
            total_pairs += 1

mean_asymmetry = total_asymmetry / total_pairs if total_pairs > 0 else 0
print(f"\nMean bigram asymmetry: {mean_asymmetry:.3f}")
print("  (0 = perfectly symmetric, 1 = completely one-directional)")

# =============================================================================
# TEST 5: Repeated Chunks (Procedural Steps?)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 5: REPEATED CLASS CHUNKS ACROSS FOLIOS")
print("=" * 70)
print("\nDo the same class sequences appear across multiple folios?")
print("(Would suggest shared procedural steps)")

# Find 4-grams that appear in multiple folios
chunk_folios = defaultdict(set)
for (folio, line_num), group in df.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()
    classes = [token_to_class.get(t) for t in tokens]
    classes = [c for c in classes if c is not None]

    for i in range(len(classes) - 3):
        chunk = tuple(classes[i:i+4])
        chunk_folios[chunk].add(folio)

# Filter to chunks appearing in 3+ folios
shared_chunks = [(chunk, folios) for chunk, folios in chunk_folios.items()
                 if len(folios) >= 3]
shared_chunks.sort(key=lambda x: -len(x[1]))

print(f"\n4-class chunks appearing in 3+ folios:")
for chunk, folios in shared_chunks[:15]:
    print(f"  {chunk}: {len(folios)} folios")

# =============================================================================
# TEST 6: Class Role Categories
# =============================================================================
print("\n" + "=" * 70)
print("TEST 6: INFERRING CLASS ROLES FROM BEHAVIOR")
print("=" * 70)

# Categorize classes by their positional and transitional behavior
class_profiles = {}
for cls in contingency.index:
    total = contingency.loc[cls].sum()
    if total < 30:
        continue

    init_rate = contingency.loc[cls, 'INITIAL'] / total
    final_rate = contingency.loc[cls, 'FINAL'] / total
    medial_rate = contingency.loc[cls, 'MEDIAL'] / total

    # Categorize
    if init_rate > 0.4:
        role = "INITIATOR"
    elif final_rate > 0.4:
        role = "TERMINATOR"
    elif medial_rate > 0.7:
        role = "OPERATOR"
    else:
        role = "FLEXIBLE"

    class_profiles[cls] = {
        'role': role,
        'init': init_rate,
        'final': final_rate,
        'medial': medial_rate,
        'total': total
    }

# Summarize
role_counts = Counter(p['role'] for p in class_profiles.values())
print(f"\nClass role distribution:")
for role, count in role_counts.most_common():
    print(f"  {role}: {count} classes")

print("\nINITIATOR classes (>40% line-initial - 'start with'):")
for cls, p in sorted(class_profiles.items(), key=lambda x: -x[1]['init']):
    if p['role'] == 'INITIATOR':
        print(f"  Class {cls}: {p['init']*100:.0f}% initial (n={p['total']})")

print("\nTERMINATOR classes (>40% line-final - 'end with'):")
for cls, p in sorted(class_profiles.items(), key=lambda x: -x[1]['final']):
    if p['role'] == 'TERMINATOR':
        print(f"  Class {cls}: {p['final']*100:.0f}% final (n={p['total']})")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: PROCEDURAL VS REACTIVE EVIDENCE")
print("=" * 70)

print("""
PROCEDURAL evidence (sequential steps):
- Strong positional class preferences (INITIATOR/OPERATOR/TERMINATOR roles)
- Recurring class patterns across lines
- Asymmetric bigrams (forward direction preferred)
- Shared chunks across folios (common procedures)

REACTIVE evidence (state machine):
- High class flexibility (FLEXIBLE role dominant)
- Symmetric bigrams (any order works)
- Unique patterns per folio (context-specific responses)
- Position-independent class distributions

Key question: Is B more like a cookbook (do A, then B, then C)
or a thermostat (if hot->cool, if cold->heat, loop)?
""")
