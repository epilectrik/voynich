"""
CLASS CO-OCCURRENCE ANALYSIS

Research Question Q3: Class Co-occurrence
- Which classes co-occur within lines?
- Are there class "sequences" that repeat?
- Which class pairs are enriched/depleted?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript
from collections import defaultdict, Counter
import numpy as np
import json
from itertools import combinations

tx = Transcript()

print("=" * 70)
print("CLASS CO-OCCURRENCE ANALYSIS")
print("=" * 70)

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']
class_to_tokens = class_map['class_to_tokens']

# =============================================================================
# STEP 1: Collect class sequences per line
# =============================================================================
print("\n[Step 1] Collecting class sequences per line...")

# Group tokens by folio/line
line_class_sequences = []  # list of (folio, line, [class sequence])

current_line = None
current_seq = []

for token in tx.currier_b():
    if token.word and token.word in token_to_class:
        line_key = (token.folio, token.line)
        if line_key != current_line:
            if current_seq and len(current_seq) >= 2:
                line_class_sequences.append((current_line[0], current_line[1], current_seq))
            current_line = line_key
            current_seq = []
        current_seq.append(token_to_class[token.word])

# Don't forget last line
if current_seq and len(current_seq) >= 2:
    line_class_sequences.append((current_line[0], current_line[1], current_seq))

print(f"  Collected {len(line_class_sequences)} lines with 2+ classified tokens")

# =============================================================================
# STEP 2: Co-occurrence matrix (within same line)
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Co-occurrence Matrix")
print("=" * 70)

# Count co-occurrences
pair_counts = Counter()  # (class1, class2) -> count where class1 < class2
class_line_counts = Counter()  # class -> number of lines containing it

for folio, line, seq in line_class_sequences:
    unique_classes = set(seq)
    for cls in unique_classes:
        class_line_counts[cls] += 1
    for c1, c2 in combinations(sorted(unique_classes), 2):
        pair_counts[(c1, c2)] += 1

total_lines = len(line_class_sequences)

# Calculate expected co-occurrence and enrichment
print("\n  Calculating enrichment scores...")

enriched_pairs = []
depleted_pairs = []

for (c1, c2), observed in pair_counts.items():
    if observed < 10:
        continue

    # Expected count under independence
    p1 = class_line_counts[c1] / total_lines
    p2 = class_line_counts[c2] / total_lines
    expected = p1 * p2 * total_lines

    if expected < 5:
        continue

    enrichment = observed / expected

    role1 = class_to_role.get(str(c1), 'UNK')
    role2 = class_to_role.get(str(c2), 'UNK')

    if enrichment > 1.5:
        enriched_pairs.append((c1, c2, observed, expected, enrichment, role1, role2))
    elif enrichment < 0.5:
        depleted_pairs.append((c1, c2, observed, expected, enrichment, role1, role2))

enriched_pairs.sort(key=lambda x: x[4], reverse=True)
depleted_pairs.sort(key=lambda x: x[4])

print("\n  ENRICHED pairs (>1.5x expected):")
for c1, c2, obs, exp, enr, r1, r2 in enriched_pairs[:15]:
    t1 = class_to_tokens.get(str(c1), [])[:2]
    t2 = class_to_tokens.get(str(c2), [])[:2]
    print(f"    Class {c1:2d}+{c2:2d} ({r1[:4]}+{r2[:4]}): {enr:.2f}x (obs={obs}, exp={exp:.0f}) - {t1} + {t2}")

print("\n  DEPLETED pairs (<0.5x expected):")
for c1, c2, obs, exp, enr, r1, r2 in depleted_pairs[:15]:
    t1 = class_to_tokens.get(str(c1), [])[:2]
    t2 = class_to_tokens.get(str(c2), [])[:2]
    print(f"    Class {c1:2d}+{c2:2d} ({r1[:4]}+{r2[:4]}): {enr:.2f}x (obs={obs}, exp={exp:.0f}) - {t1} + {t2}")

# =============================================================================
# STEP 3: Adjacent pair analysis (bigrams)
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Adjacent Class Pairs (Bigrams)")
print("=" * 70)

bigram_counts = Counter()
class_counts = Counter()

for folio, line, seq in line_class_sequences:
    for cls in seq:
        class_counts[cls] += 1
    for i in range(len(seq) - 1):
        bigram_counts[(seq[i], seq[i+1])] += 1

total_bigrams = sum(bigram_counts.values())

# Calculate enriched bigrams
print("\n  Most enriched adjacent pairs:")
enriched_bigrams = []

for (c1, c2), observed in bigram_counts.items():
    if observed < 10:
        continue

    # Expected under independence
    p1 = class_counts[c1] / sum(class_counts.values())
    p2 = class_counts[c2] / sum(class_counts.values())
    expected = p1 * p2 * total_bigrams

    if expected < 5:
        continue

    enrichment = observed / expected

    if enrichment > 1.5:
        role1 = class_to_role.get(str(c1), 'UNK')
        role2 = class_to_role.get(str(c2), 'UNK')
        enriched_bigrams.append((c1, c2, observed, expected, enrichment, role1, role2))

enriched_bigrams.sort(key=lambda x: x[4], reverse=True)

for c1, c2, obs, exp, enr, r1, r2 in enriched_bigrams[:20]:
    t1 = class_to_tokens.get(str(c1), [])[:2]
    t2 = class_to_tokens.get(str(c2), [])[:2]
    print(f"    {c1:2d} -> {c2:2d} ({r1[:4]}->{r2[:4]}): {enr:.2f}x (n={obs}) - {t1} -> {t2}")

# =============================================================================
# STEP 4: Role-level co-occurrence patterns
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: Role-Level Co-occurrence")
print("=" * 70)

role_pair_counts = Counter()
role_line_counts = Counter()

for folio, line, seq in line_class_sequences:
    roles = [class_to_role.get(str(c), 'UNK') for c in seq]
    unique_roles = set(roles)
    for r in unique_roles:
        role_line_counts[r] += 1
    for r1, r2 in combinations(sorted(unique_roles), 2):
        role_pair_counts[(r1, r2)] += 1

print("\n  Role pair frequencies:")
for (r1, r2), count in role_pair_counts.most_common(20):
    p1 = role_line_counts[r1] / total_lines
    p2 = role_line_counts[r2] / total_lines
    expected = p1 * p2 * total_lines
    enrichment = count / expected if expected > 0 else 0
    print(f"    {r1:20s} + {r2:20s}: {count:4d} lines ({enrichment:.2f}x)")

# =============================================================================
# STEP 5: Repeated class sequences (motifs)
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Repeated Class Sequences (Motifs)")
print("=" * 70)

# Find repeated trigrams
trigram_counts = Counter()
for folio, line, seq in line_class_sequences:
    for i in range(len(seq) - 2):
        trigram = (seq[i], seq[i+1], seq[i+2])
        trigram_counts[trigram] += 1

print("\n  Most common class trigrams:")
for trigram, count in trigram_counts.most_common(20):
    if count < 5:
        break
    roles = [class_to_role.get(str(c), 'UNK')[:4] for c in trigram]
    tokens = [class_to_tokens.get(str(c), ['?'])[0] for c in trigram]
    print(f"    {trigram}: {count} occurrences ({'-'.join(roles)}) - {' -> '.join(tokens)}")

# Find repeated 4-grams
quadgram_counts = Counter()
for folio, line, seq in line_class_sequences:
    for i in range(len(seq) - 3):
        quadgram = (seq[i], seq[i+1], seq[i+2], seq[i+3])
        quadgram_counts[quadgram] += 1

print("\n  Most common class 4-grams:")
for quadgram, count in quadgram_counts.most_common(10):
    if count < 3:
        break
    roles = [class_to_role.get(str(c), 'UNK')[:4] for c in quadgram]
    tokens = [class_to_tokens.get(str(c), ['?'])[0] for c in quadgram]
    print(f"    {quadgram}: {count} occurrences ({'-'.join(roles)})")
    print(f"       {' -> '.join(tokens)}")

# =============================================================================
# STEP 6: Class self-repetition analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Class Self-Repetition")
print("=" * 70)

self_repeat_rates = {}
for cls in range(1, 50):
    if class_counts[cls] < 20:
        continue

    self_repeats = bigram_counts[(cls, cls)]
    total = class_counts[cls] - class_line_counts[cls]  # Subtract line boundaries
    if total > 0:
        rate = self_repeats / class_counts[cls]
        self_repeat_rates[cls] = rate

sorted_self = sorted(self_repeat_rates.items(), key=lambda x: x[1], reverse=True)

print("\n  Highest self-repetition rates (same class appears consecutively):")
for cls, rate in sorted_self[:15]:
    role = class_to_role.get(str(cls), 'UNK')
    tokens = class_to_tokens.get(str(cls), [])[:3]
    print(f"    Class {cls:2d} ({role[:4]}): {rate:.1%} self-repeat - {tokens}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
import os
os.makedirs('results', exist_ok=True)

results = {
    'enriched_pairs': [
        {'class1': c1, 'class2': c2, 'observed': obs, 'expected': exp, 'enrichment': enr}
        for c1, c2, obs, exp, enr, _, _ in enriched_pairs[:30]
    ],
    'depleted_pairs': [
        {'class1': c1, 'class2': c2, 'observed': obs, 'expected': exp, 'enrichment': enr}
        for c1, c2, obs, exp, enr, _, _ in depleted_pairs[:30]
    ],
    'enriched_bigrams': [
        {'class1': c1, 'class2': c2, 'observed': obs, 'enrichment': enr}
        for c1, c2, obs, _, enr, _, _ in enriched_bigrams[:30]
    ],
    'common_trigrams': [
        {'sequence': list(tri), 'count': count}
        for tri, count in trigram_counts.most_common(30) if count >= 5
    ],
    'self_repeat_rates': {str(k): v for k, v in self_repeat_rates.items()},
}

with open('results/class_cooccurrence.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Saved results to results/class_cooccurrence.json")
print("=" * 70)
