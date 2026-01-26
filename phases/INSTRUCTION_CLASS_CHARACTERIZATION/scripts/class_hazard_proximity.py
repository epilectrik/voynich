"""
CLASS HAZARD PROXIMITY ANALYSIS

Research Question Q5: Class Hazard Proximity
- Which classes appear adjacent to forbidden transitions?
- Do classes differ in hazard exposure?
- Are certain classes "gateway" vs "terminal"?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript
from collections import defaultdict, Counter
import json

tx = Transcript()

print("=" * 70)
print("CLASS HAZARD PROXIMITY ANALYSIS")
print("=" * 70)

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']
class_to_tokens = class_map['class_to_tokens']

# =============================================================================
# DEFINE THE 17 FORBIDDEN TRANSITIONS
# =============================================================================
# From forbidden_transition_scenarios.md

FORBIDDEN_TRANSITIONS = [
    # PHASE_ORDERING (7)
    ('shey', 'aiin'),
    ('shey', 'al'),
    ('shey', 'c'),      # Note: 'c' is not in our vocabulary
    ('dy', 'aiin'),
    ('dy', 'chey'),
    ('chey', 'chedy'),
    ('chey', 'shedy'),
    # COMPOSITION_JUMP (4)
    ('chedy', 'ee'),    # Note: 'ee' may not be in our vocabulary
    ('c', 'ee'),        # Note: these may be MIDDLE references
    ('shedy', 'aiin'),
    ('shedy', 'o'),
    # CONTAINMENT_TIMING (4)
    ('chol', 'r'),
    ('l', 'chol'),
    ('or', 'dal'),
    ('he', 'or'),       # Note: 'he' may not be in vocabulary
    # RATE_MISMATCH (1)
    ('ar', 'dal'),
    # ENERGY_OVERSHOOT (1)
    ('he', 't'),        # Note: 'he', 't' may not be in vocabulary
]

HAZARD_CLASS = {
    ('shey', 'aiin'): 'PHASE_ORDERING',
    ('shey', 'al'): 'PHASE_ORDERING',
    ('shey', 'c'): 'PHASE_ORDERING',
    ('dy', 'aiin'): 'PHASE_ORDERING',
    ('dy', 'chey'): 'PHASE_ORDERING',
    ('chey', 'chedy'): 'PHASE_ORDERING',
    ('chey', 'shedy'): 'PHASE_ORDERING',
    ('chedy', 'ee'): 'COMPOSITION_JUMP',
    ('c', 'ee'): 'COMPOSITION_JUMP',
    ('shedy', 'aiin'): 'COMPOSITION_JUMP',
    ('shedy', 'o'): 'COMPOSITION_JUMP',
    ('chol', 'r'): 'CONTAINMENT_TIMING',
    ('l', 'chol'): 'CONTAINMENT_TIMING',
    ('or', 'dal'): 'CONTAINMENT_TIMING',
    ('he', 'or'): 'CONTAINMENT_TIMING',
    ('ar', 'dal'): 'RATE_MISMATCH',
    ('he', 't'): 'ENERGY_OVERSHOOT',
}

# Create set for both directions (transitions are bidirectional)
forbidden_set = set()
for a, b in FORBIDDEN_TRANSITIONS:
    forbidden_set.add((a, b))
    forbidden_set.add((b, a))

print(f"\n[Setup] {len(FORBIDDEN_TRANSITIONS)} forbidden transitions defined")
print(f"  Bidirectional set: {len(forbidden_set)} pairs")

# =============================================================================
# STEP 1: Map tokens to their hazard involvement
# =============================================================================
print("\n[Step 1] Mapping tokens to hazard involvement...")

# Tokens that appear in forbidden transitions
hazard_tokens = set()
for a, b in FORBIDDEN_TRANSITIONS:
    hazard_tokens.add(a)
    hazard_tokens.add(b)

print(f"  Tokens in forbidden transitions: {sorted(hazard_tokens)}")

# Map to classes
hazard_classes = set()
for token in hazard_tokens:
    if token in token_to_class:
        hazard_classes.add(token_to_class[token])

print(f"  Classes directly involved: {sorted(hazard_classes)}")

# =============================================================================
# STEP 2: Count forbidden transitions by class pair
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Forbidden Transitions by Class")
print("=" * 70)

# Map token pairs to class pairs
class_pair_forbidden = Counter()  # (class1, class2) -> count of forbidden pairs

for a, b in FORBIDDEN_TRANSITIONS:
    if a in token_to_class and b in token_to_class:
        cls_a = token_to_class[a]
        cls_b = token_to_class[b]
        # Store with smaller class first for consistency
        pair = (min(cls_a, cls_b), max(cls_a, cls_b))
        class_pair_forbidden[pair] += 1

print("\n  Class pairs with forbidden transitions:")
for (c1, c2), count in class_pair_forbidden.most_common():
    role1 = class_to_role.get(str(c1), 'UNK')
    role2 = class_to_role.get(str(c2), 'UNK')
    t1 = class_to_tokens.get(str(c1), [])[:2]
    t2 = class_to_tokens.get(str(c2), [])[:2]
    print(f"    Class {c1:2d}+{c2:2d} ({role1[:4]}+{role2[:4]}): {count} forbidden - {t1} <-> {t2}")

# =============================================================================
# STEP 3: Analyze class hazard exposure in corpus
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Class Hazard Exposure in Corpus")
print("=" * 70)

# Collect bigrams and track hazard adjacency
bigram_counts = Counter()
hazard_adjacent = Counter()  # class -> count of times it appears next to a hazard token
class_total = Counter()

# Build sequences from transcript
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if token.word:
        key = (token.folio, token.line)
        line_tokens[key].append(token.word)

# Analyze bigrams
for (folio, line), words in line_tokens.items():
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]

        # Count if this is a forbidden transition
        if (w1, w2) in forbidden_set:
            if w1 in token_to_class:
                hazard_adjacent[token_to_class[w1]] += 1
            if w2 in token_to_class:
                hazard_adjacent[token_to_class[w2]] += 1

        # Track totals
        if w1 in token_to_class:
            class_total[token_to_class[w1]] += 1

# Calculate hazard exposure rates
class_hazard_rates = {}
for cls in range(1, 50):
    if class_total[cls] >= 20:
        rate = hazard_adjacent[cls] / class_total[cls] if class_total[cls] > 0 else 0
        class_hazard_rates[cls] = {
            'hazard_count': hazard_adjacent[cls],
            'total': class_total[cls],
            'rate': rate
        }

sorted_by_rate = sorted(class_hazard_rates.items(), key=lambda x: x[1]['rate'], reverse=True)

print("\n  Classes with highest hazard exposure (bigram proximity):")
for cls, stats in sorted_by_rate[:15]:
    if stats['hazard_count'] > 0:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): {stats['rate']:.2%} "
              f"({stats['hazard_count']}/{stats['total']}) - {tokens}")

print("\n  Classes with ZERO hazard exposure:")
zero_hazard = [cls for cls, stats in class_hazard_rates.items() if stats['hazard_count'] == 0]
print(f"    {len(zero_hazard)} classes: {sorted(zero_hazard)}")

# =============================================================================
# STEP 4: Gateway vs Terminal analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Gateway vs Terminal Classes")
print("=" * 70)

# A class is a "gateway" if it often PRECEDES hazard tokens
# A class is "terminal" if it often FOLLOWS hazard tokens

gateway_counts = Counter()  # class -> count of times it precedes hazard token
terminal_counts = Counter()  # class -> count of times it follows hazard token

for (folio, line), words in line_tokens.items():
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]

        if (w1, w2) in forbidden_set:
            # w1 is the "gateway" (leads into forbidden)
            # w2 is the "terminal" (follows forbidden)
            if w1 in token_to_class:
                gateway_counts[token_to_class[w1]] += 1
            if w2 in token_to_class:
                terminal_counts[token_to_class[w2]] += 1

# Calculate gateway/terminal balance
class_gateway_terminal = {}
for cls in range(1, 50):
    gw = gateway_counts[cls]
    term = terminal_counts[cls]
    total = gw + term
    if total >= 5:
        class_gateway_terminal[cls] = {
            'gateway': gw,
            'terminal': term,
            'balance': (gw - term) / total if total > 0 else 0,  # positive = gateway-biased
            'total': total
        }

# Sort by balance
sorted_by_balance = sorted(class_gateway_terminal.items(), key=lambda x: x[1]['balance'], reverse=True)

print("\n  GATEWAY-biased classes (tend to precede hazards):")
for cls, stats in sorted_by_balance[:10]:
    if stats['balance'] > 0:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): {stats['balance']:+.2f} "
              f"(gw={stats['gateway']}, term={stats['terminal']}) - {tokens}")

print("\n  TERMINAL-biased classes (tend to follow hazards):")
for cls, stats in reversed(sorted_by_balance[-10:]):
    if stats['balance'] < 0:
        role = class_to_role.get(str(cls), 'UNK')
        tokens = class_to_tokens.get(str(cls), [])[:3]
        print(f"    Class {cls:2d} ({role[:4]}): {stats['balance']:+.2f} "
              f"(gw={stats['gateway']}, term={stats['terminal']}) - {tokens}")

# =============================================================================
# STEP 5: Hazard class analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Hazard Class Analysis")
print("=" * 70)

# Count which instruction classes are involved in which hazard classes
class_hazard_class_involvement = defaultdict(Counter)  # instruction class -> {hazard_class -> count}

for a, b in FORBIDDEN_TRANSITIONS:
    hazard = HAZARD_CLASS.get((a, b), 'UNKNOWN')
    if a in token_to_class:
        class_hazard_class_involvement[token_to_class[a]][hazard] += 1
    if b in token_to_class:
        class_hazard_class_involvement[token_to_class[b]][hazard] += 1

print("\n  Instruction class involvement by hazard type:")
for cls in sorted(class_hazard_class_involvement.keys()):
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:2]
    hazards = class_hazard_class_involvement[cls]
    hazard_str = ", ".join(f"{h}:{c}" for h, c in hazards.most_common())
    print(f"    Class {cls:2d} ({role[:4]}): {hazard_str} - {tokens}")

# =============================================================================
# STEP 6: Role-level hazard summary
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Role-Level Hazard Summary")
print("=" * 70)

role_hazard_exposure = defaultdict(lambda: {'count': 0, 'total': 0})

for cls, stats in class_hazard_rates.items():
    role = class_to_role.get(str(cls), 'UNKNOWN')
    role_hazard_exposure[role]['count'] += stats['hazard_count']
    role_hazard_exposure[role]['total'] += stats['total']

print("\n  Hazard exposure by role:")
for role in sorted(role_hazard_exposure.keys()):
    stats = role_hazard_exposure[role]
    rate = stats['count'] / stats['total'] if stats['total'] > 0 else 0
    print(f"    {role:20s}: {rate:.3%} ({stats['count']}/{stats['total']})")

# =============================================================================
# STEP 7: Distance from hazard analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 7: Class Distance from Hazards")
print("=" * 70)

# For each class occurrence, measure distance to nearest hazard token
class_distance_sums = Counter()
class_distance_counts = Counter()

for (folio, line), words in line_tokens.items():
    # Find positions of hazard-involved tokens
    hazard_positions = []
    for i, w in enumerate(words):
        if w in hazard_tokens:
            hazard_positions.append(i)

    if not hazard_positions:
        continue

    # For each classified token, find distance to nearest hazard
    for i, w in enumerate(words):
        if w in token_to_class:
            cls = token_to_class[w]
            min_dist = min(abs(i - hp) for hp in hazard_positions)
            class_distance_sums[cls] += min_dist
            class_distance_counts[cls] += 1

# Calculate average distances
class_avg_distances = {}
for cls in range(1, 50):
    if class_distance_counts[cls] >= 20:
        avg_dist = class_distance_sums[cls] / class_distance_counts[cls]
        class_avg_distances[cls] = avg_dist

sorted_by_distance = sorted(class_avg_distances.items(), key=lambda x: x[1])

print("\n  CLOSEST to hazards (lowest average distance):")
for cls, dist in sorted_by_distance[:10]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): avg_dist={dist:.2f} - {tokens}")

print("\n  FURTHEST from hazards (highest average distance):")
for cls, dist in sorted_by_distance[-10:]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): avg_dist={dist:.2f} - {tokens}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
import os
os.makedirs('results', exist_ok=True)

results = {
    'forbidden_class_pairs': [
        {'class1': c1, 'class2': c2, 'count': count}
        for (c1, c2), count in class_pair_forbidden.most_common()
    ],
    'class_hazard_rates': {str(k): v for k, v in class_hazard_rates.items()},
    'class_gateway_terminal': {str(k): v for k, v in class_gateway_terminal.items()},
    'class_avg_distances': {str(k): v for k, v in class_avg_distances.items()},
    'hazard_involved_classes': sorted(list(hazard_classes)),
}

with open('results/class_hazard_proximity.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Saved results to results/class_hazard_proximity.json")
print("=" * 70)
