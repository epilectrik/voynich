"""
Quick test: Is there ANY operator role/class combination that covers 100% of A records?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import json

tx = Transcript()
morph = Morphology()

# Load class data
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    raw_data = json.load(f)
    class_data = raw_data.get('token_to_class', raw_data)
    class_to_role = raw_data.get('class_to_role', {})

# Build data
b_tokens = {}
for token in tx.currier_b():
    word = token.word
    if word not in b_tokens:
        m = morph.extract(word)
        b_tokens[word] = {
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'class': class_data.get(word)
        }

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

b_middles = set(info['middle'] for info in b_tokens.values() if info['middle'])
b_prefixes = set(info['prefix'] for info in b_tokens.values() if info['prefix'])
b_suffixes = set(info['suffix'] for info in b_tokens.values() if info['suffix'])

n_records = len(record_morphology)

# For each A record, compute ALL surviving classes
record_classes = {}
for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    surviving = set()
    for word, info in b_tokens.items():
        if info['class'] is None:
            continue

        if info['middle'] is None:
            middle_ok = True
        else:
            middle_ok = info['middle'] in pp_middles

        if info['prefix'] is None:
            prefix_ok = True
        else:
            prefix_ok = info['prefix'] in pp_prefixes

        if info['suffix'] is None:
            suffix_ok = True
        else:
            suffix_ok = info['suffix'] in pp_suffixes

        if middle_ok and prefix_ok and suffix_ok:
            surviving.add(info['class'])

    record_classes[(folio, line)] = surviving

print("=" * 70)
print("CHECKING FOR 100% COVERAGE")
print("=" * 70)

# Check each class
print("\nIndividual class coverage (top 20):")
class_coverage = {}
for cls in range(1, 50):
    count = sum(1 for cs in record_classes.values() if cls in cs)
    class_coverage[cls] = count

sorted_classes = sorted(class_coverage.items(), key=lambda x: -x[1])[:20]
for cls, count in sorted_classes:
    pct = 100 * count / n_records
    role = class_to_role.get(str(cls), "UNKNOWN")
    print(f"  Class {cls}: {count}/{n_records} ({pct:.1f}%) - {role}")

# Check role unions
print("\n" + "=" * 70)
print("ROLE UNION COVERAGE")
print("=" * 70)

roles = defaultdict(set)
for cls_str, role in class_to_role.items():
    roles[role].add(int(cls_str))

for role, classes in sorted(roles.items()):
    has_any = sum(1 for cs in record_classes.values() if len(cs & classes) > 0)
    pct = 100 * has_any / n_records
    print(f"\n{role} ({len(classes)} classes): {has_any}/{n_records} ({pct:.1f}%)")

# Check: ANY class at all?
print("\n" + "=" * 70)
print("RECORDS WITH ANY CLASS AT ALL")
print("=" * 70)

has_any_class = sum(1 for cs in record_classes.values() if len(cs) > 0)
has_no_class = n_records - has_any_class

print(f"\nRecords with at least 1 class: {has_any_class}/{n_records} ({100*has_any_class/n_records:.1f}%)")
print(f"Records with NO classes: {has_no_class}/{n_records} ({100*has_no_class/n_records:.1f}%)")

if has_no_class > 0:
    print("\n*** CRITICAL: Some A records have NO legal B classes at all! ***")
    no_class_records = [r for r, cs in record_classes.items() if len(cs) == 0]
    print(f"\nExamples:")
    for r in no_class_records[:5]:
        pref, mid, suf = record_morphology[r]
        pp_mid = mid & b_middles
        print(f"  {r}: {len(pref)} PREFIXes, {len(pp_mid)} PP MIDDLEs, {len(suf)} SUFFIXes")

# Check combined unions
print("\n" + "=" * 70)
print("COMBINED ROLE COVERAGE")
print("=" * 70)

# ENERGY + FREQUENT
ef_classes = roles['ENERGY_OPERATOR'] | roles['FREQUENT_OPERATOR']
has_ef = sum(1 for cs in record_classes.values() if len(cs & ef_classes) > 0)
print(f"\nENERGY + FREQUENT ({len(ef_classes)} classes): {has_ef}/{n_records} ({100*has_ef/n_records:.1f}%)")

# All non-AUXILIARY
non_aux = roles['CORE_CONTROL'] | roles['FREQUENT_OPERATOR'] | roles['FLOW_OPERATOR'] | roles['ENERGY_OPERATOR']
has_non_aux = sum(1 for cs in record_classes.values() if len(cs & non_aux) > 0)
print(f"All non-AUXILIARY ({len(non_aux)} classes): {has_non_aux}/{n_records} ({100*has_non_aux/n_records:.1f}%)")

# All roles
all_classes = set(range(1, 50))
has_any = sum(1 for cs in record_classes.values() if len(cs & all_classes) > 0)
print(f"ALL classes (49): {has_any}/{n_records} ({100*has_any/n_records:.1f}%)")
