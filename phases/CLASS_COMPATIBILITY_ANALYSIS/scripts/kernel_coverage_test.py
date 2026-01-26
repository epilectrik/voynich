"""
CLASS_COMPATIBILITY_ANALYSIS - Kernel Coverage Test

Question: Does every A record have access to at least one kernel class?

Kernel classes (CORE_CONTROL):
- Class 10: daiin
- Class 11: ol
- Class 12: k

Even if no single class is universal, the UNION might cover 100%.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import json

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("KERNEL COVERAGE TEST")
print("Does every A record have access to at least one kernel class?")
print("=" * 70)

# Load class assignments
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    raw_data = json.load(f)
    class_data = raw_data.get('token_to_class', raw_data)

print(f"\nLoaded {len(class_data)} token-to-class mappings")

# Get B tokens with morphology and class
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

# Build A records
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

# B vocabulary sets
b_middles = set(info['middle'] for info in b_tokens.values() if info['middle'])
b_prefixes = set(info['prefix'] for info in b_tokens.values() if info['prefix'])
b_suffixes = set(info['suffix'] for info in b_tokens.values() if info['suffix'])

print(f"A records: {len(record_morphology)}")

# Define kernel classes
KERNEL_CLASSES = {10, 11, 12}  # CORE_CONTROL
KERNEL_TOKENS = {
    10: ['daiin'],
    11: ['ol'],
    12: ['k']
}

print(f"\nKernel classes: {KERNEL_CLASSES}")
for cls, tokens in KERNEL_TOKENS.items():
    print(f"  Class {cls}: {tokens}")

# For each A record, determine which kernel classes survive
print("\n" + "=" * 70)
print("KERNEL CLASS SURVIVAL BY A RECORD")
print("=" * 70)

record_kernel_classes = {}
for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    kernel_surviving = set()
    for word, info in b_tokens.items():
        if info['class'] not in KERNEL_CLASSES:
            continue

        # MIDDLE filter
        if info['middle'] is None:
            middle_ok = True
        else:
            middle_ok = info['middle'] in pp_middles

        # PREFIX filter
        if info['prefix'] is None:
            prefix_ok = True
        else:
            prefix_ok = info['prefix'] in pp_prefixes

        # SUFFIX filter
        if info['suffix'] is None:
            suffix_ok = True
        else:
            suffix_ok = info['suffix'] in pp_suffixes

        if middle_ok and prefix_ok and suffix_ok:
            kernel_surviving.add(info['class'])

    record_kernel_classes[(folio, line)] = kernel_surviving

# Statistics
n_records = len(record_kernel_classes)

# Individual kernel class coverage
print("\nIndividual kernel class coverage:")
for cls in sorted(KERNEL_CLASSES):
    count = sum(1 for ks in record_kernel_classes.values() if cls in ks)
    pct = 100 * count / n_records
    print(f"  Class {cls}: {count}/{n_records} ({pct:.1f}%)")

# Union coverage (at least one kernel class)
has_any_kernel = sum(1 for ks in record_kernel_classes.values() if len(ks) > 0)
has_no_kernel = n_records - has_any_kernel

print(f"\n" + "=" * 70)
print("KEY RESULT: KERNEL UNION COVERAGE")
print("=" * 70)
print(f"\nRecords with AT LEAST ONE kernel class: {has_any_kernel}/{n_records} ({100*has_any_kernel/n_records:.1f}%)")
print(f"Records with NO kernel classes: {has_no_kernel}/{n_records} ({100*has_no_kernel/n_records:.1f}%)")

# Distribution of kernel class counts
kernel_count_dist = defaultdict(int)
for ks in record_kernel_classes.values():
    kernel_count_dist[len(ks)] += 1

print(f"\nDistribution of kernel class counts per record:")
for count in sorted(kernel_count_dist.keys()):
    n = kernel_count_dist[count]
    pct = 100 * n / n_records
    print(f"  {count} kernel classes: {n} records ({pct:.1f}%)")

# Examine records with no kernel
if has_no_kernel > 0:
    print(f"\n" + "=" * 70)
    print(f"EXAMINING {has_no_kernel} RECORDS WITH NO KERNEL CLASSES")
    print("=" * 70)

    no_kernel_records = [(r, record_morphology[r]) for r, ks in record_kernel_classes.items() if len(ks) == 0]

    print("\nSample records with no kernel access:")
    for (folio, line), (prefixes, middles, suffixes) in no_kernel_records[:10]:
        pp_mid = middles & b_middles
        print(f"\n  {folio}:{line}")
        print(f"    A-PREFIXes: {prefixes}")
        print(f"    A-MIDDLEs: {len(middles)} total, {len(pp_mid)} PP")
        print(f"    A-SUFFIXes: {suffixes}")

        # Check why each kernel class fails
        for cls in KERNEL_CLASSES:
            tokens = KERNEL_TOKENS[cls]
            for tok in tokens:
                info = b_tokens.get(tok)
                if info:
                    reasons = []
                    if info['middle'] and info['middle'] not in pp_mid:
                        reasons.append(f"MIDDLE '{info['middle']}' missing")
                    if info['prefix'] and info['prefix'] not in (prefixes & b_prefixes):
                        reasons.append(f"PREFIX '{info['prefix']}' missing")
                    if info['suffix'] and info['suffix'] not in (suffixes & b_suffixes):
                        reasons.append(f"SUFFIX '{info['suffix']}' missing")
                    if reasons:
                        print(f"    Class {cls} ({tok}): {', '.join(reasons)}")

# Also check other operator categories
print(f"\n" + "=" * 70)
print("CHECKING OTHER KEY OPERATOR CATEGORIES")
print("=" * 70)

# From class_to_role in the JSON
ROLE_CLASSES = {
    'CORE_CONTROL': {10, 11, 12},
    'FREQUENT_OPERATOR': {9, 13, 14, 23},
    'FLOW_OPERATOR': {7, 30, 38, 40},
    'ENERGY_OPERATOR': {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
}

for role, classes in ROLE_CLASSES.items():
    # Check union coverage for this role
    role_coverage = {}
    for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
        pp_middles = middles & b_middles
        pp_prefixes = prefixes & b_prefixes
        pp_suffixes = suffixes & b_suffixes

        role_surviving = set()
        for word, info in b_tokens.items():
            if info['class'] not in classes:
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
                role_surviving.add(info['class'])

        role_coverage[(folio, line)] = role_surviving

    has_any = sum(1 for rs in role_coverage.values() if len(rs) > 0)
    print(f"\n{role} ({len(classes)} classes):")
    print(f"  Records with at least one: {has_any}/{n_records} ({100*has_any/n_records:.1f}%)")

# Summary
print(f"\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if has_no_kernel == 0:
    print(f"""
ANSWER: YES - Every A record has access to at least one kernel class.

While no single kernel class is universal:
- Class 10 (daiin): {sum(1 for ks in record_kernel_classes.values() if 10 in ks)/n_records*100:.1f}%
- Class 11 (ol): {sum(1 for ks in record_kernel_classes.values() if 11 in ks)/n_records*100:.1f}%
- Class 12 (k): {sum(1 for ks in record_kernel_classes.values() if 12 in ks)/n_records*100:.1f}%

The UNION covers 100% of A records.
""")
else:
    print(f"""
ANSWER: NO - {has_no_kernel} A records ({100*has_no_kernel/n_records:.1f}%) have NO kernel class access.

This means some A records cannot execute any CORE_CONTROL instructions.
These records may be restricted to AUXILIARY, ENERGY, or FLOW operations only.
""")
