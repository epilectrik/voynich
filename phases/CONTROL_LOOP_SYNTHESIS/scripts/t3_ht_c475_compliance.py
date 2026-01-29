"""
T3: HT C475 Compliance Test

Do HT tokens obey MIDDLE incompatibility rules (C475)?
- If HT violates C475, it's truly outside the grammar
- If HT complies, it's constrained by the same rules

C475: Certain MIDDLE pairs never co-occur in adjacent tokens
"""

import json
import sys
sys.path.insert(0, 'C:/git/voynich')

from collections import Counter, defaultdict
from scripts.voynich import Transcript, Morphology
from scipy import stats
import numpy as np

# Load class mapping
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_data = json.load(f)

token_to_role = class_data['token_to_role']

def is_ht(word):
    return token_to_role.get(word.replace('*', ''), 'HT') == 'HT'

# Load morphology
morph = Morphology()

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())

lines = defaultdict(list)
for t in b_tokens:
    lines[(t.folio, t.line)].append(t)

print(f"Total B tokens: {len(b_tokens)}")

# First, identify forbidden MIDDLE pairs from classified tokens
# (pairs that never occur in adjacent classified tokens)
classified_pairs = Counter()
total_classified_transitions = 0

for key, tokens in lines.items():
    for i in range(len(tokens) - 1):
        w1 = tokens[i].word.replace('*', '')
        w2 = tokens[i+1].word.replace('*', '')
        if not w1.strip() or not w2.strip():
            continue

        # Both must be classified (non-HT)
        if not is_ht(w1) and not is_ht(w2):
            m1 = morph.extract(w1)
            m2 = morph.extract(w2)
            if m1.middle and m2.middle:
                pair = (m1.middle, m2.middle)
                classified_pairs[pair] += 1
                total_classified_transitions += 1

print(f"Total classified MIDDLE transitions: {total_classified_transitions}")
print(f"Unique MIDDLE pairs in classified: {len(classified_pairs)}")

# Get all MIDDLEs that appear in classified tokens
classified_middles = set()
for (m1, m2), count in classified_pairs.items():
    classified_middles.add(m1)
    classified_middles.add(m2)

print(f"Unique MIDDLEs in classified vocabulary: {len(classified_middles)}")

# Theoretical maximum pairs
max_pairs = len(classified_middles) ** 2
coverage = len(classified_pairs) / max_pairs if max_pairs > 0 else 0
print(f"Pair coverage: {len(classified_pairs)}/{max_pairs} = {coverage*100:.1f}%")

# Now check HT transitions
ht_pairs = Counter()
ht_violations = 0
ht_compliant = 0
total_ht_transitions = 0

# Also track HT-to-classified and classified-to-HT
ht_to_class_pairs = Counter()
class_to_ht_pairs = Counter()

for key, tokens in lines.items():
    for i in range(len(tokens) - 1):
        w1 = tokens[i].word.replace('*', '')
        w2 = tokens[i+1].word.replace('*', '')
        if not w1.strip() or not w2.strip():
            continue

        m1 = morph.extract(w1)
        m2 = morph.extract(w2)
        if not m1.middle or not m2.middle:
            continue

        is_ht1 = is_ht(w1)
        is_ht2 = is_ht(w2)
        pair = (m1.middle, m2.middle)

        # HT-HT transitions
        if is_ht1 and is_ht2:
            ht_pairs[pair] += 1
            total_ht_transitions += 1
            # Check if this pair ever occurs in classified
            if pair in classified_pairs:
                ht_compliant += 1
            else:
                # Novel pair - but is it because the MIDDLEs are HT-exclusive?
                if m1.middle in classified_middles and m2.middle in classified_middles:
                    ht_violations += 1  # Both MIDDLEs exist in classified, but pair doesn't

        # HT-to-classified
        elif is_ht1 and not is_ht2:
            ht_to_class_pairs[pair] += 1

        # Classified-to-HT
        elif not is_ht1 and is_ht2:
            class_to_ht_pairs[pair] += 1

print(f"\n{'='*60}")
print(f"HT C475 COMPLIANCE ANALYSIS")
print(f"{'='*60}")

print(f"\n--- HT-HT TRANSITIONS ---")
print(f"Total HT-HT MIDDLE transitions: {total_ht_transitions}")
print(f"Unique HT-HT pairs: {len(ht_pairs)}")

if total_ht_transitions > 0:
    print(f"\nCompliance with classified pairs:")
    print(f"  Pairs also seen in classified: {ht_compliant} ({100*ht_compliant/total_ht_transitions:.1f}%)")
    print(f"  Novel pairs (potential violations): {total_ht_transitions - ht_compliant} ({100*(total_ht_transitions-ht_compliant)/total_ht_transitions:.1f}%)")
    print(f"  True violations (both MIDDLEs exist in classified): {ht_violations} ({100*ht_violations/total_ht_transitions:.2f}%)")

# Check if novel HT pairs use HT-exclusive MIDDLEs
ht_middles = set()
for (m1, m2) in ht_pairs.keys():
    ht_middles.add(m1)
    ht_middles.add(m2)

ht_exclusive_middles = ht_middles - classified_middles
shared_middles = ht_middles & classified_middles

print(f"\n--- HT MIDDLE VOCABULARY ---")
print(f"Total MIDDLEs in HT-HT transitions: {len(ht_middles)}")
print(f"HT-exclusive MIDDLEs: {len(ht_exclusive_middles)} ({100*len(ht_exclusive_middles)/len(ht_middles):.1f}%)")
print(f"Shared with classified: {len(shared_middles)} ({100*len(shared_middles)/len(ht_middles):.1f}%)")

# Show some HT-exclusive MIDDLEs
if ht_exclusive_middles:
    print(f"\nSample HT-exclusive MIDDLEs: {list(ht_exclusive_middles)[:10]}")

# Analyze violation patterns
print(f"\n--- VIOLATION ANALYSIS ---")
if ht_violations > 0:
    violation_pairs = []
    for pair, count in ht_pairs.items():
        m1, m2 = pair
        if m1 in classified_middles and m2 in classified_middles and pair not in classified_pairs:
            violation_pairs.append((pair, count))

    violation_pairs.sort(key=lambda x: -x[1])
    print(f"Top 10 violation pairs (MIDDLEs exist in classified, but pair never seen):")
    for (m1, m2), count in violation_pairs[:10]:
        print(f"  {m1} -> {m2}: {count}")

# Boundary analysis: HT↔Classified transitions
print(f"\n--- HT<->CLASSIFIED BOUNDARY TRANSITIONS ---")
print(f"HT->Classified transitions: {sum(ht_to_class_pairs.values())}")
print(f"Classified->HT transitions: {sum(class_to_ht_pairs.values())}")

# Summary
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")

if total_ht_transitions > 0:
    violation_rate = ht_violations / total_ht_transitions
    if violation_rate < 0.02:
        print(f"HT COMPLIES with C475 (violation rate: {violation_rate*100:.2f}%)")
        print(f"  HT tokens follow the same MIDDLE incompatibility rules")
        print(f"  HT is constrained by grammar, not random padding")
    elif violation_rate < 0.10:
        print(f"HT MOSTLY COMPLIES with C475 (violation rate: {violation_rate*100:.2f}%)")
        print(f"  Minor deviations may be edge cases")
    else:
        print(f"HT VIOLATES C475 (violation rate: {violation_rate*100:.2f}%)")
        print(f"  HT operates outside normal MIDDLE constraints")

compliance_pct = 100 * ht_compliant / total_ht_transitions if total_ht_transitions > 0 else 0
print(f"\nOverall: {compliance_pct:.1f}% of HT-HT pairs are also seen in classified tokens")
