"""
ZERO SURVIVAL A RECORDS ANALYSIS

Some A records have 0 surviving B tokens.
What makes them special? Are they "dead" records?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("ZERO SURVIVAL A RECORDS ANALYSIS")
print("A records that cannot produce ANY B tokens")
print("=" * 70)

# Build B token morphology
b_tokens = {}
for token in tx.currier_b():
    word = token.word
    if word and word not in b_tokens:
        m = morph.extract(word)
        b_tokens[word] = {
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
        }

b_middles = set(info['middle'] for info in b_tokens.values() if info['middle'])
b_prefixes = set(info['prefix'] for info in b_tokens.values() if info['prefix'])
b_suffixes = set(info['suffix'] for info in b_tokens.values() if info['suffix'])

# Build A records with morphology
a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

record_morphology = {}
record_tokens = {}
for (folio, line), tokens in a_records.items():
    prefixes = set()
    middles = set()
    suffixes = set()
    words = []
    for t in tokens:
        m = morph.extract(t.word)
        words.append(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)
    record_morphology[(folio, line)] = (prefixes, middles, suffixes)
    record_tokens[(folio, line)] = words

# TOKEN-LEVEL SURVIVAL
def get_surviving_tokens(prefixes, middles, suffixes):
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    surviving = set()
    for word, info in b_tokens.items():
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
            surviving.add(word)

    return surviving

# Find records with 0 surviving tokens
zero_survival = []
low_survival = []  # 1-5 tokens

for a_key, (prefixes, middles, suffixes) in record_morphology.items():
    surviving = get_surviving_tokens(prefixes, middles, suffixes)
    if len(surviving) == 0:
        zero_survival.append(a_key)
    elif len(surviving) <= 5:
        low_survival.append((a_key, len(surviving)))

print(f"\nTotal A records: {len(record_morphology)}")
print(f"Records with 0 surviving tokens: {len(zero_survival)} ({100*len(zero_survival)/len(record_morphology):.2f}%)")
print(f"Records with 1-5 surviving tokens: {len(low_survival)} ({100*len(low_survival)/len(record_morphology):.2f}%)")

# Analyze zero-survival records
print("\n" + "=" * 70)
print("ZERO SURVIVAL RECORDS (0 B tokens possible)")
print("=" * 70)

for a_key in zero_survival[:20]:  # First 20
    prefixes, middles, suffixes = record_morphology[a_key]
    tokens = record_tokens[a_key]

    # Check why no survival
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    print(f"\n{a_key}:")
    print(f"  A tokens: {tokens}")
    print(f"  A MIDDLEs: {middles}")
    print(f"  PP MIDDLEs (in B): {pp_middles}")
    print(f"  A PREFIXes: {prefixes}")
    print(f"  PP PREFIXes (in B): {pp_prefixes}")
    print(f"  A SUFFIXes: {suffixes}")
    print(f"  PP SUFFIXes (in B): {pp_suffixes}")

# Why do these records have 0 survival?
print("\n" + "=" * 70)
print("WHY ZERO SURVIVAL?")
print("=" * 70)

# Categorize the failure modes
no_pp_middle = 0
no_pp_prefix = 0
no_pp_suffix = 0
no_bare_middle = 0

for a_key in zero_survival:
    prefixes, middles, suffixes = record_morphology[a_key]
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    if not pp_middles:
        no_pp_middle += 1
    if prefixes and not pp_prefixes:
        no_pp_prefix += 1
    if suffixes and not pp_suffixes:
        no_pp_suffix += 1

    # Check if any BARE tokens are possible
    # BARE tokens have no PREFIX, so just need matching MIDDLE
    bare_possible = False
    for word, info in b_tokens.items():
        if info['prefix'] is None and info['suffix'] is None:
            if info['middle'] is None or info['middle'] in pp_middles:
                bare_possible = True
                break
    if not bare_possible:
        no_bare_middle += 1

print(f"\nOf {len(zero_survival)} zero-survival records:")
print(f"  No PP MIDDLEs (nothing survives): {no_pp_middle} ({100*no_pp_middle/len(zero_survival):.1f}%)")
print(f"  No PP PREFIXes (PREFIX class inaccessible): {no_pp_prefix} ({100*no_pp_prefix/len(zero_survival):.1f}%)")
print(f"  No BARE tokens possible: {no_bare_middle} ({100*no_bare_middle/len(zero_survival):.1f}%)")

# What MIDDLEs do zero-survival records use?
print("\n" + "=" * 70)
print("MIDDLEs IN ZERO-SURVIVAL RECORDS")
print("=" * 70)

zero_middles = Counter()
for a_key in zero_survival:
    prefixes, middles, suffixes = record_morphology[a_key]
    for m in middles:
        zero_middles[m] += 1

print("\nMost common MIDDLEs in zero-survival records:")
for mid, count in zero_middles.most_common(15):
    in_b = "IN B" if mid in b_middles else "NOT IN B"
    print(f"  '{mid}': {count} records - {in_b}")

# Are these A-only MIDDLEs?
a_only_middles = set(m for m, c in zero_middles.items() if m not in b_middles)
print(f"\nA-only MIDDLEs (not in any B token): {len(a_only_middles)}")
print(f"Examples: {list(a_only_middles)[:10]}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
ZERO SURVIVAL RECORDS: {len(zero_survival)} ({100*len(zero_survival)/len(record_morphology):.2f}%)

These are A records that cannot produce ANY B tokens.
Primary cause: {no_pp_middle} records have NO MIDDLEs that exist in B vocabulary.

These records have A-only MIDDLEs that don't participate in PP.

INTERPRETATION:
- These records are "outside" the A->B pipeline
- They may represent A-internal operations (never intended to reach B)
- Or they may be errors/anomalies in the data
- Or the morphological extraction is missing something

Either way, ~{100*len(zero_survival)/len(record_morphology):.1f}% of A records are "dead ends"
that cannot contribute to B execution.
""")
