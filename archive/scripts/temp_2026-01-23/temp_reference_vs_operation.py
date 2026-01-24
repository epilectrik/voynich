#!/usr/bin/env python3
"""
Test: Do some B tokens behave like static references vs active operations?

Static references might show:
1. Low repetition within folio (appear once as "declaration")
2. High transition rigidity (always followed by same successor)
3. Positional uniqueness (always in same spot)
4. Folio-specific rather than content-driven appearance

Active operations might show:
1. Variable repetition (used as needed)
2. Diverse transitions (context-dependent successors)
3. Positional flexibility
4. Content-driven appearance
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
class_to_tokens = data['class_to_tokens']

print("=" * 70)
print("REFERENCE VS OPERATION: CLASS BEHAVIOR ANALYSIS")
print("=" * 70)

# =============================================================================
# TEST 1: Within-Folio Repetition Rate
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: WITHIN-FOLIO REPETITION RATE")
print("=" * 70)
print("\nReferences: likely appear once per folio (declared once)")
print("Operations: likely repeat within folio (used multiple times)")

class_folio_counts = defaultdict(list)  # class -> [count_in_folio1, count_in_folio2, ...]

for folio, folio_group in df.groupby('folio'):
    class_counts = Counter()
    for tok in folio_group['word']:
        cls = token_to_class.get(tok)
        if cls:
            class_counts[cls] += 1

    for cls, count in class_counts.items():
        class_folio_counts[cls].append(count)

# Calculate mean and variance of within-folio counts
class_repetition = {}
for cls, counts in class_folio_counts.items():
    if len(counts) >= 10:  # Appears in at least 10 folios
        mean_count = np.mean(counts)
        var_count = np.var(counts)
        # Coefficient of variation (high = variable, low = consistent)
        cv = np.std(counts) / mean_count if mean_count > 0 else 0
        # What fraction of appearances are exactly 1?
        once_rate = sum(1 for c in counts if c == 1) / len(counts)
        class_repetition[cls] = {
            'mean': mean_count,
            'var': var_count,
            'cv': cv,
            'once_rate': once_rate,
            'n_folios': len(counts)
        }

# Find classes that tend to appear exactly once (reference-like)
print("\nClasses with HIGH 'appears once' rate (reference-like):")
sorted_by_once = sorted(class_repetition.items(), key=lambda x: -x[1]['once_rate'])
for cls, stats in sorted_by_once[:10]:
    print(f"  Class {cls}: {stats['once_rate']*100:.1f}% appear once, mean={stats['mean']:.1f}/folio (n={stats['n_folios']} folios)")

print("\nClasses with LOW 'appears once' rate (operation-like, repeats):")
sorted_by_once_rev = sorted(class_repetition.items(), key=lambda x: x[1]['once_rate'])
for cls, stats in sorted_by_once_rev[:10]:
    print(f"  Class {cls}: {stats['once_rate']*100:.1f}% appear once, mean={stats['mean']:.1f}/folio (n={stats['n_folios']} folios)")

# =============================================================================
# TEST 2: Transition Entropy (Successor Diversity)
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: TRANSITION ENTROPY (SUCCESSOR DIVERSITY)")
print("=" * 70)
print("\nReferences: might have rigid successors (always followed by same thing)")
print("Operations: might have diverse successors (context-dependent)")

# Count class-to-class transitions
class_successors = defaultdict(Counter)

for (folio, line_num), group in df.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()
    classes = [token_to_class.get(t) for t in tokens]

    for i in range(len(classes) - 1):
        if classes[i] and classes[i+1]:
            class_successors[classes[i]][classes[i+1]] += 1

# Calculate entropy for each class's successor distribution
def entropy(counter):
    total = sum(counter.values())
    if total == 0:
        return 0
    probs = [c / total for c in counter.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)

class_entropy = {}
for cls, successors in class_successors.items():
    total = sum(successors.values())
    if total >= 20:  # Minimum sample size
        ent = entropy(successors)
        n_successors = len(successors)
        max_ent = np.log2(n_successors) if n_successors > 1 else 0
        normalized_ent = ent / max_ent if max_ent > 0 else 0
        class_entropy[cls] = {
            'entropy': ent,
            'n_successors': n_successors,
            'normalized': normalized_ent,
            'total': total
        }

print("\nClasses with LOWEST transition entropy (rigid successors - reference-like):")
sorted_by_ent = sorted(class_entropy.items(), key=lambda x: x[1]['entropy'])
for cls, stats in sorted_by_ent[:10]:
    top_successor = class_successors[cls].most_common(1)[0]
    print(f"  Class {cls}: entropy={stats['entropy']:.2f}, {stats['n_successors']} unique successors, top={top_successor[0]} ({top_successor[1]}/{stats['total']})")

print("\nClasses with HIGHEST transition entropy (diverse successors - operation-like):")
sorted_by_ent_rev = sorted(class_entropy.items(), key=lambda x: -x[1]['entropy'])
for cls, stats in sorted_by_ent_rev[:10]:
    print(f"  Class {cls}: entropy={stats['entropy']:.2f}, {stats['n_successors']} unique successors (n={stats['total']})")

# =============================================================================
# TEST 3: Position Rigidity
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: POSITION RIGIDITY")
print("=" * 70)
print("\nReferences: might always appear in same position (like headers)")
print("Operations: might appear in various positions")

# Calculate position entropy for each class
class_positions = defaultdict(Counter)

for (folio, line_num), group in df.groupby(['folio', 'line_number']):
    tokens = group['word'].tolist()
    n = len(tokens)
    if n < 3:
        continue

    for i, tok in enumerate(tokens):
        cls = token_to_class.get(tok)
        if cls:
            # Categorize position
            if i == 0:
                pos = 'INITIAL'
            elif i == n - 1:
                pos = 'FINAL'
            else:
                # Further subdivide medial
                rel_pos = i / (n - 1)  # 0 to 1
                if rel_pos < 0.33:
                    pos = 'EARLY'
                elif rel_pos < 0.67:
                    pos = 'MIDDLE'
                else:
                    pos = 'LATE'
            class_positions[cls][pos] += 1

# Calculate position entropy
class_pos_entropy = {}
for cls, positions in class_positions.items():
    total = sum(positions.values())
    if total >= 30:
        ent = entropy(positions)
        n_positions = len(positions)
        max_ent = np.log2(5)  # 5 position categories
        class_pos_entropy[cls] = {
            'entropy': ent,
            'normalized': ent / max_ent,
            'total': total,
            'dominant': positions.most_common(1)[0]
        }

print("\nClasses with LOWEST position entropy (rigid position - reference-like):")
sorted_by_pos = sorted(class_pos_entropy.items(), key=lambda x: x[1]['entropy'])
for cls, stats in sorted_by_pos[:10]:
    dom_pos, dom_count = stats['dominant']
    pct = 100 * dom_count / stats['total']
    print(f"  Class {cls}: pos_entropy={stats['entropy']:.2f}, dominant={dom_pos} ({pct:.0f}%) (n={stats['total']})")

print("\nClasses with HIGHEST position entropy (flexible position - operation-like):")
sorted_by_pos_rev = sorted(class_pos_entropy.items(), key=lambda x: -x[1]['entropy'])
for cls, stats in sorted_by_pos_rev[:10]:
    print(f"  Class {cls}: pos_entropy={stats['entropy']:.2f} (n={stats['total']})")

# =============================================================================
# TEST 4: ATOMIC Classes (7, 11) - Special Case
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: ATOMIC CLASSES (7, 11) - SPECIAL ANALYSIS")
print("=" * 70)
print("\nThese have MIDDLE=None, always pass AZC filter. Are they references?")

for cls in [7, 11]:
    if cls in class_repetition:
        rep = class_repetition[cls]
        print(f"\nClass {cls}:")
        print(f"  Repetition: {rep['once_rate']*100:.1f}% appear once, mean={rep['mean']:.1f}/folio")
    if cls in class_entropy:
        ent = class_entropy[cls]
        print(f"  Transition entropy: {ent['entropy']:.2f} ({ent['n_successors']} unique successors)")
    if cls in class_pos_entropy:
        pos = class_pos_entropy[cls]
        dom_pos, dom_count = pos['dominant']
        pct = 100 * dom_count / pos['total']
        print(f"  Position: dominant={dom_pos} ({pct:.0f}%), entropy={pos['entropy']:.2f}")

# =============================================================================
# TEST 5: Correlation Analysis
# =============================================================================
print("\n" + "=" * 70)
print("TEST 5: REFERENCE-LIKE COMPOSITE SCORE")
print("=" * 70)
print("\nCombining: high once-rate + low transition entropy + low position entropy")

composite_scores = {}
for cls in set(class_repetition.keys()) & set(class_entropy.keys()) & set(class_pos_entropy.keys()):
    # Higher score = more reference-like
    once_score = class_repetition[cls]['once_rate']
    trans_score = 1 - class_entropy[cls]['normalized']  # Invert: low entropy = high score
    pos_score = 1 - class_pos_entropy[cls]['normalized']  # Invert: low entropy = high score

    composite = (once_score + trans_score + pos_score) / 3
    composite_scores[cls] = {
        'composite': composite,
        'once': once_score,
        'trans': trans_score,
        'pos': pos_score
    }

print("\nMost REFERENCE-LIKE classes (high composite score):")
sorted_composite = sorted(composite_scores.items(), key=lambda x: -x[1]['composite'])
for cls, scores in sorted_composite[:10]:
    print(f"  Class {cls}: composite={scores['composite']:.3f} (once={scores['once']:.2f}, trans={scores['trans']:.2f}, pos={scores['pos']:.2f})")

print("\nMost OPERATION-LIKE classes (low composite score):")
sorted_composite_rev = sorted(composite_scores.items(), key=lambda x: x[1]['composite'])
for cls, scores in sorted_composite_rev[:10]:
    print(f"  Class {cls}: composite={scores['composite']:.3f} (once={scores['once']:.2f}, trans={scores['trans']:.2f}, pos={scores['pos']:.2f})")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY: REFERENCE VS OPERATION SPECTRUM")
print("=" * 70)

# Count how many classes fall into each category
reference_like = sum(1 for s in composite_scores.values() if s['composite'] > 0.6)
operation_like = sum(1 for s in composite_scores.values() if s['composite'] < 0.4)
mixed = len(composite_scores) - reference_like - operation_like

print(f"\nClass distribution by behavior:")
print(f"  Reference-like (score > 0.6): {reference_like} classes")
print(f"  Operation-like (score < 0.4): {operation_like} classes")
print(f"  Mixed behavior (0.4-0.6): {mixed} classes")

print("""
Interpretation:
- Reference-like: Appear once, rigid successors, fixed position
  -> Could be setpoints, parameters, material identifiers
- Operation-like: Repeat freely, diverse successors, flexible position
  -> Likely active control operations
- Mixed: Some of both behaviors
  -> May serve dual roles depending on context
""")
