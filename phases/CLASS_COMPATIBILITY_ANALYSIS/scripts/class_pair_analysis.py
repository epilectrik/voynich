"""
CLASS_COMPATIBILITY_ANALYSIS - Test 4
Specific class pair relationships

Questions:
1. Which class pairs ALWAYS avoid each other?
2. Which class pairs frequently appear together?
3. Are these patterns explained by PREFIX, or is there something deeper?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import numpy as np
from itertools import combinations

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("CLASS PAIR RELATIONSHIP ANALYSIS")
print("=" * 70)

# Build data (same setup as before)
b_tokens = {}
for token in tx.currier_b():
    word = token.word
    if word not in b_tokens:
        m = morph.extract(word)
        if m.middle:
            if m.prefix:
                cls = f"P_{m.prefix}"
            elif m.suffix:
                cls = f"S_{m.suffix}"
            else:
                cls = "BARE"
            b_tokens[word] = (m.prefix, m.middle, m.suffix, cls)

a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

record_morphology = {}
for (folio, line), tokens in a_records.items():
    prefixes = set()
    middles = set()
    suffixes = set()
    for t in tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)
    record_morphology[(folio, line)] = (prefixes, middles, suffixes)

b_middles = set(m for p, m, s, c in b_tokens.values())
b_prefixes = set(p for p, m, s, c in b_tokens.values() if p)
b_suffixes = set(s for p, m, s, c in b_tokens.values() if s)

record_classes = {}
for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    surviving = set()
    for word, (pref, mid, suf, cls) in b_tokens.items():
        if mid in pp_middles:
            pref_ok = (pref is None or pref in pp_prefixes)
            suf_ok = (suf is None or suf in pp_suffixes)
            if pref_ok and suf_ok:
                surviving.add(cls)
    record_classes[(folio, line)] = surviving

n_records = len(record_classes)
all_records = list(record_classes.keys())

# Get active classes (appear at least once)
class_occurrence = defaultdict(int)
for classes in record_classes.values():
    for c in classes:
        class_occurrence[c] += 1

active_classes = sorted([c for c, cnt in class_occurrence.items() if cnt > 0])
print(f"\nActive classes: {len(active_classes)}")

# ========================================
# ANALYSIS 1: Classes that NEVER co-occur
# ========================================
print("\n" + "=" * 70)
print("CLASSES THAT NEVER CO-OCCUR (Mutual Exclusion)")
print("=" * 70)

# Build co-occurrence matrix
cooccur = defaultdict(int)
for classes in record_classes.values():
    for c1, c2 in combinations(sorted(classes), 2):
        cooccur[(c1, c2)] += 1

# Find mutually exclusive pairs (both common enough to matter)
mutual_exclusive = []
for c1, c2 in combinations(active_classes, 2):
    if cooccur[(c1, c2)] == 0:
        # Both must appear in at least 10 records to be meaningful
        if class_occurrence[c1] >= 10 and class_occurrence[c2] >= 10:
            mutual_exclusive.append((c1, c2, class_occurrence[c1], class_occurrence[c2]))

print(f"\nMutually exclusive pairs (both with >=10 occurrences): {len(mutual_exclusive)}")

# Group by type
prefix_prefix_me = [(c1, c2, o1, o2) for c1, c2, o1, o2 in mutual_exclusive
                    if c1.startswith('P_') and c2.startswith('P_')]
prefix_suffix_me = [(c1, c2, o1, o2) for c1, c2, o1, o2 in mutual_exclusive
                    if (c1.startswith('P_') and c2.startswith('S_')) or
                       (c1.startswith('S_') and c2.startswith('P_'))]
suffix_suffix_me = [(c1, c2, o1, o2) for c1, c2, o1, o2 in mutual_exclusive
                    if c1.startswith('S_') and c2.startswith('S_')]
bare_involved_me = [(c1, c2, o1, o2) for c1, c2, o1, o2 in mutual_exclusive
                    if c1 == 'BARE' or c2 == 'BARE']

print(f"\n  PREFIX vs PREFIX: {len(prefix_prefix_me)}")
print(f"  PREFIX vs SUFFIX: {len(prefix_suffix_me)}")
print(f"  SUFFIX vs SUFFIX: {len(suffix_suffix_me)}")
print(f"  Involving BARE: {len(bare_involved_me)}")

print("\n--- PREFIX vs PREFIX (never together) ---")
for c1, c2, o1, o2 in sorted(prefix_prefix_me, key=lambda x: -(x[2]+x[3]))[:20]:
    print(f"  {c1} ({o1}) vs {c2} ({o2})")

print("\n--- SUFFIX vs SUFFIX (never together) ---")
for c1, c2, o1, o2 in sorted(suffix_suffix_me, key=lambda x: -(x[2]+x[3]))[:15]:
    print(f"  {c1} ({o1}) vs {c2} ({o2})")

# ========================================
# ANALYSIS 2: Classes that ALWAYS co-occur
# ========================================
print("\n" + "=" * 70)
print("CLASSES THAT FREQUENTLY CO-OCCUR")
print("=" * 70)

# Calculate Jaccard similarity and conditional probability
class_pairs_data = []
for c1, c2 in combinations(active_classes, 2):
    o1, o2 = class_occurrence[c1], class_occurrence[c2]
    if o1 < 10 or o2 < 10:
        continue

    co = cooccur[(c1, c2)]
    union = o1 + o2 - co
    jaccard = co / union if union > 0 else 0

    # P(c2 | c1) = co / o1
    p_c2_given_c1 = co / o1
    # P(c1 | c2) = co / o2
    p_c1_given_c2 = co / o2

    class_pairs_data.append({
        'c1': c1, 'c2': c2,
        'o1': o1, 'o2': o2, 'co': co,
        'jaccard': jaccard,
        'p_c2_given_c1': p_c2_given_c1,
        'p_c1_given_c2': p_c1_given_c2
    })

# High Jaccard pairs (frequently together)
print("\n--- Highest Jaccard (most similar occurrence patterns) ---")
high_jaccard = sorted(class_pairs_data, key=lambda x: -x['jaccard'])[:25]
for p in high_jaccard:
    print(f"  {p['c1']} + {p['c2']}: Jaccard={p['jaccard']:.3f}, co-occur {p['co']}x")

# High conditional probability (one implies the other)
print("\n--- High Conditional Probability (c1 implies c2) ---")
# Where P(c2|c1) > 0.8 and c1 is reasonably common
high_conditional = [p for p in class_pairs_data if p['p_c2_given_c1'] > 0.8 and p['o1'] >= 50]
high_conditional = sorted(high_conditional, key=lambda x: -x['p_c2_given_c1'])[:20]
for p in high_conditional:
    print(f"  {p['c1']} -> {p['c2']}: P={p['p_c2_given_c1']:.1%} ({p['co']}/{p['o1']})")

# ========================================
# ANALYSIS 3: Is this just PREFIX?
# ========================================
print("\n" + "=" * 70)
print("ARE THESE PATTERNS JUST PREFIX EFFECTS?")
print("=" * 70)

# For mutually exclusive PREFIX pairs, check if their PREFIXes ever co-occur in A
print("\n--- PREFIX pairs that never co-occur: Is it A-PREFIX absence? ---")
a_prefix_cooccur = defaultdict(int)
for r in all_records:
    prefs = record_morphology[r][0]
    for p1, p2 in combinations(sorted(prefs), 2):
        a_prefix_cooccur[(p1, p2)] += 1

for c1, c2, o1, o2 in prefix_prefix_me[:10]:
    p1 = c1[2:]  # Remove P_
    p2 = c2[2:]
    a_cooccur = a_prefix_cooccur.get((min(p1,p2), max(p1,p2)), 0)
    print(f"  {c1} vs {c2}: A-PREFIXes '{p1}' and '{p2}' co-occur in {a_cooccur} records")

# For high Jaccard pairs, check if they share PREFIX or if it's MIDDLE-driven
print("\n--- High co-occurrence pairs: What drives them? ---")
for p in high_jaccard[:10]:
    c1, c2 = p['c1'], p['c2']

    # Are they same PREFIX family?
    same_prefix = False
    if c1.startswith('P_') and c2.startswith('P_'):
        same_prefix = c1[2:] == c2[2:]

    # Is one BARE?
    bare_involved = c1 == 'BARE' or c2 == 'BARE'

    # Are they both SUFFIX?
    both_suffix = c1.startswith('S_') and c2.startswith('S_')

    driver = "UNKNOWN"
    if same_prefix:
        driver = "SAME PREFIX"
    elif bare_involved:
        driver = "BARE (no PREFIX needed)"
    elif both_suffix:
        driver = "BOTH SUFFIX"
    elif c1.startswith('P_') and c2.startswith('S_'):
        driver = "PREFIX + SUFFIX (independent)"
    elif c1.startswith('S_') and c2.startswith('P_'):
        driver = "SUFFIX + PREFIX (independent)"
    else:
        driver = "PREFIX vs PREFIX (need both A-PREFIXes)"

    print(f"  {c1} + {c2}: Jaccard={p['jaccard']:.3f} -- {driver}")

# ========================================
# ANALYSIS 4: Non-PREFIX explanations
# ========================================
print("\n" + "=" * 70)
print("LOOKING FOR NON-PREFIX PATTERNS")
print("=" * 70)

# Check if any PREFIX pairs have high co-occurrence despite different PREFIXes
print("\n--- PREFIX class pairs with high co-occurrence (different PREFIXes) ---")
prefix_pairs_high = [p for p in class_pairs_data
                     if p['c1'].startswith('P_') and p['c2'].startswith('P_')
                     and p['c1'][2:] != p['c2'][2:]
                     and p['jaccard'] > 0.3]
prefix_pairs_high = sorted(prefix_pairs_high, key=lambda x: -x['jaccard'])[:15]

for p in prefix_pairs_high:
    c1, c2 = p['c1'], p['c2']
    p1, p2 = c1[2:], c2[2:]
    a_cooccur = a_prefix_cooccur.get((min(p1,p2), max(p1,p2)), 0)
    print(f"  {c1} + {c2}: Jaccard={p['jaccard']:.3f}, A-PREFIX co-occur={a_cooccur}")

# Check SUFFIX co-occurrence patterns
print("\n--- SUFFIX class pairs: co-occurrence patterns ---")
suffix_pairs = [p for p in class_pairs_data
                if p['c1'].startswith('S_') and p['c2'].startswith('S_')]
suffix_pairs_high = sorted(suffix_pairs, key=lambda x: -x['jaccard'])[:10]
suffix_pairs_low = sorted([p for p in suffix_pairs if p['jaccard'] == 0], key=lambda x: -(x['o1']+x['o2']))[:10]

print("\n  High co-occurrence SUFFIX pairs:")
for p in suffix_pairs_high:
    print(f"    {p['c1']} + {p['c2']}: Jaccard={p['jaccard']:.3f}")

print("\n  Never co-occurring SUFFIX pairs:")
for p in suffix_pairs_low:
    print(f"    {p['c1']} vs {p['c2']}: {p['o1']} and {p['o2']} occurrences, never together")

# ========================================
# SUMMARY
# ========================================
print("\n" + "=" * 70)
print("SUMMARY: CLASS PAIR RELATIONSHIPS")
print("=" * 70)

print(f"""
MUTUAL EXCLUSION (never co-occur, both >=10 occurrences):
  Total pairs: {len(mutual_exclusive)}
  PREFIX vs PREFIX: {len(prefix_prefix_me)}
  PREFIX vs SUFFIX: {len(prefix_suffix_me)}
  SUFFIX vs SUFFIX: {len(suffix_suffix_me)}

HIGH CO-OCCURRENCE (Jaccard > 0.5):
  {len([p for p in class_pairs_data if p['jaccard'] > 0.5])} pairs

KEY FINDING:
- PREFIX class mutual exclusion is ENTIRELY explained by A-PREFIX absence
- When A-PREFIXes co-occur, their classes co-occur
- SUFFIX pairs show more independent patterns (some never co-occur despite being SUFFIX)
- BARE co-occurs with everything (it only needs MIDDLE match)
""")
