"""
CLASS_COMPATIBILITY_ANALYSIS - Test 5
SUFFIX Incompatibility Investigation

Question: Why do certain SUFFIX class pairs never co-occur?
- Is it A-SUFFIX absence (like PREFIX)?
- Is it MIDDLE incompatibility?
- Is there a deeper pattern?
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
print("SUFFIX INCOMPATIBILITY INVESTIGATION")
print("=" * 70)

# Build data
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

# ========================================
# STEP 1: Identify SUFFIX classes and their requirements
# ========================================
print("\n" + "=" * 70)
print("STEP 1: SUFFIX CLASS INVENTORY")
print("=" * 70)

# Get all SUFFIX classes and their B tokens
suffix_classes = {}
for word, (pref, mid, suf, cls) in b_tokens.items():
    if cls.startswith('S_'):
        if cls not in suffix_classes:
            suffix_classes[cls] = {'tokens': [], 'middles': set(), 'suffix': cls[2:]}
        suffix_classes[cls]['tokens'].append(word)
        suffix_classes[cls]['middles'].add(mid)

print(f"\nSUFFIX classes: {len(suffix_classes)}")
for cls in sorted(suffix_classes.keys()):
    info = suffix_classes[cls]
    print(f"  {cls}: {len(info['tokens'])} tokens, {len(info['middles'])} MIDDLEs, suffix='{info['suffix']}'")

# ========================================
# STEP 2: Find mutually exclusive SUFFIX pairs
# ========================================
print("\n" + "=" * 70)
print("STEP 2: MUTUALLY EXCLUSIVE SUFFIX PAIRS")
print("=" * 70)

# Class occurrence
class_occurrence = defaultdict(int)
for classes in record_classes.values():
    for c in classes:
        class_occurrence[c] += 1

# Co-occurrence
cooccur = defaultdict(int)
for classes in record_classes.values():
    for c1, c2 in combinations(sorted(classes), 2):
        cooccur[(c1, c2)] += 1

# Find SUFFIX pairs that never co-occur
suffix_class_list = sorted([c for c in suffix_classes.keys() if class_occurrence[c] >= 10])
print(f"\nSUFFIX classes with >=10 occurrences: {len(suffix_class_list)}")

exclusive_suffix_pairs = []
for c1, c2 in combinations(suffix_class_list, 2):
    if cooccur[(c1, c2)] == 0:
        exclusive_suffix_pairs.append((c1, c2, class_occurrence[c1], class_occurrence[c2]))

print(f"Mutually exclusive SUFFIX pairs: {len(exclusive_suffix_pairs)}")

# ========================================
# STEP 3: Investigate each exclusive pair
# ========================================
print("\n" + "=" * 70)
print("STEP 3: INVESTIGATING EACH EXCLUSIVE PAIR")
print("=" * 70)

# A-SUFFIX co-occurrence
a_suffix_cooccur = defaultdict(int)
for r in all_records:
    sufs = record_morphology[r][2]
    for s1, s2 in combinations(sorted(sufs), 2):
        a_suffix_cooccur[(s1, s2)] += 1

# A-SUFFIX occurrence
a_suffix_occur = defaultdict(int)
for r in all_records:
    for s in record_morphology[r][2]:
        a_suffix_occur[s] += 1

print("\nFor each exclusive pair, check:")
print("  1. Do the A-SUFFIXes ever co-occur?")
print("  2. Do their MIDDLEs overlap?")
print("  3. What's blocking co-occurrence?")
print("-" * 70)

for c1, c2, o1, o2 in sorted(exclusive_suffix_pairs, key=lambda x: -(x[2]+x[3]))[:20]:
    s1 = suffix_classes[c1]['suffix']
    s2 = suffix_classes[c2]['suffix']

    # Check A-SUFFIX co-occurrence
    a_suf_cooccur = a_suffix_cooccur.get((min(s1,s2), max(s1,s2)), 0)
    a_suf1_occur = a_suffix_occur[s1]
    a_suf2_occur = a_suffix_occur[s2]

    # Check MIDDLE overlap
    mid1 = suffix_classes[c1]['middles']
    mid2 = suffix_classes[c2]['middles']
    mid_overlap = mid1 & mid2

    print(f"\n{c1} ({o1}) vs {c2} ({o2}):")
    print(f"  A-SUFFIX '{s1}' occurs: {a_suf1_occur}")
    print(f"  A-SUFFIX '{s2}' occurs: {a_suf2_occur}")
    print(f"  A-SUFFIXes co-occur: {a_suf_cooccur} records")
    print(f"  MIDDLE overlap: {len(mid_overlap)} shared MIDDLEs")

    if a_suf_cooccur == 0:
        print(f"  -> EXPLANATION: A-SUFFIXes never co-occur in same record")
    elif len(mid_overlap) == 0:
        print(f"  -> EXPLANATION: No shared MIDDLEs (different MIDDLE vocabularies)")
    else:
        # More complex - need to check why
        print(f"  -> NEEDS INVESTIGATION: A-SUFFIXes co-occur but classes don't")

        # Find records where both A-SUFFIXes appear
        both_suffix_records = [r for r in all_records
                              if s1 in record_morphology[r][2] and s2 in record_morphology[r][2]]
        print(f"     Records with both A-SUFFIXes: {len(both_suffix_records)}")

        if both_suffix_records:
            # Check what's missing
            for r in both_suffix_records[:3]:
                pref, mid, suf = record_morphology[r]
                pp_mid = mid & b_middles

                # Can we get c1?
                c1_possible = False
                c2_possible = False
                for word, (p, m, s, c) in b_tokens.items():
                    if c == c1 and m in pp_mid and (p is None or p in (pref & b_prefixes)):
                        c1_possible = True
                    if c == c2 and m in pp_mid and (p is None or p in (pref & b_prefixes)):
                        c2_possible = True

                print(f"     Record {r}: c1_possible={c1_possible}, c2_possible={c2_possible}")

# ========================================
# STEP 4: Categorize explanations
# ========================================
print("\n" + "=" * 70)
print("STEP 4: CATEGORIZING EXPLANATIONS")
print("=" * 70)

explanation_counts = {
    'a_suffix_never_cooccur': 0,
    'no_middle_overlap': 0,
    'complex': 0
}

for c1, c2, o1, o2 in exclusive_suffix_pairs:
    s1 = suffix_classes[c1]['suffix']
    s2 = suffix_classes[c2]['suffix']

    a_suf_cooccur = a_suffix_cooccur.get((min(s1,s2), max(s1,s2)), 0)
    mid_overlap = suffix_classes[c1]['middles'] & suffix_classes[c2]['middles']

    if a_suf_cooccur == 0:
        explanation_counts['a_suffix_never_cooccur'] += 1
    elif len(mid_overlap) == 0:
        explanation_counts['no_middle_overlap'] += 1
    else:
        explanation_counts['complex'] += 1

print(f"\nExplanation breakdown for {len(exclusive_suffix_pairs)} exclusive SUFFIX pairs:")
print(f"  A-SUFFIXes never co-occur: {explanation_counts['a_suffix_never_cooccur']}")
print(f"  No MIDDLE overlap: {explanation_counts['no_middle_overlap']}")
print(f"  Complex (needs investigation): {explanation_counts['complex']}")

# ========================================
# STEP 5: Deep dive on complex cases
# ========================================
if explanation_counts['complex'] > 0:
    print("\n" + "=" * 70)
    print("STEP 5: COMPLEX CASES - DEEP INVESTIGATION")
    print("=" * 70)

    for c1, c2, o1, o2 in exclusive_suffix_pairs:
        s1 = suffix_classes[c1]['suffix']
        s2 = suffix_classes[c2]['suffix']

        a_suf_cooccur = a_suffix_cooccur.get((min(s1,s2), max(s1,s2)), 0)
        mid_overlap = suffix_classes[c1]['middles'] & suffix_classes[c2]['middles']

        if a_suf_cooccur > 0 and len(mid_overlap) > 0:
            print(f"\n=== COMPLEX CASE: {c1} vs {c2} ===")
            print(f"  Class occurrences: {o1}, {o2}")
            print(f"  A-SUFFIX co-occurrence: {a_suf_cooccur}")
            print(f"  Shared MIDDLEs: {mid_overlap}")

            # Find the specific tokens
            c1_tokens = [(w, b_tokens[w]) for w in suffix_classes[c1]['tokens']]
            c2_tokens = [(w, b_tokens[w]) for w in suffix_classes[c2]['tokens']]

            print(f"\n  {c1} tokens ({len(c1_tokens)}):")
            for w, (p, m, s, c) in c1_tokens[:5]:
                print(f"    {w}: PREFIX={p}, MIDDLE={m}, SUFFIX={s}")

            print(f"\n  {c2} tokens ({len(c2_tokens)}):")
            for w, (p, m, s, c) in c2_tokens[:5]:
                print(f"    {w}: PREFIX={p}, MIDDLE={m}, SUFFIX={s}")

            # Check records with both A-SUFFIXes
            both_suffix_records = [r for r in all_records
                                  if s1 in record_morphology[r][2] and s2 in record_morphology[r][2]]

            print(f"\n  Records with both A-SUFFIXes ({len(both_suffix_records)}):")
            for r in both_suffix_records[:5]:
                pref, mid, suf = record_morphology[r]
                pp_mid = mid & b_middles
                pp_pref = pref & b_prefixes

                # Check which tokens from each class are possible
                c1_tokens_possible = []
                c2_tokens_possible = []

                for w, (p, m, s, c) in b_tokens.items():
                    if m in pp_mid:
                        pref_ok = (p is None or p in pp_pref)
                        suf_ok = (s is None or s in suf)
                        if pref_ok and suf_ok:
                            if c == c1:
                                c1_tokens_possible.append((w, p, m, s))
                            elif c == c2:
                                c2_tokens_possible.append((w, p, m, s))

                print(f"\n    Record {r}:")
                print(f"      A-PREFIXes: {pref}")
                print(f"      A-MIDDLEs (PP): {len(pp_mid)}")
                print(f"      A-SUFFIXes: {suf}")
                print(f"      {c1} tokens possible: {len(c1_tokens_possible)}")
                print(f"      {c2} tokens possible: {len(c2_tokens_possible)}")

                if c1_tokens_possible:
                    print(f"        c1 example: {c1_tokens_possible[0]}")
                if c2_tokens_possible:
                    print(f"        c2 example: {c2_tokens_possible[0]}")

# ========================================
# STEP 6: Check if SUFFIX classes require specific PREFIXes
# ========================================
print("\n" + "=" * 70)
print("STEP 6: DO SUFFIX CLASSES REQUIRE SPECIFIC PREFIXES?")
print("=" * 70)

# For each SUFFIX class, what PREFIXes do its tokens have?
print("\nSUFFIX class tokens - do they have PREFIXes?")
for cls in sorted(suffix_class_list):
    tokens = suffix_classes[cls]['tokens']
    prefixed = [w for w in tokens if b_tokens[w][0] is not None]
    unprefixed = [w for w in tokens if b_tokens[w][0] is None]

    prefixes_used = set(b_tokens[w][0] for w in prefixed)

    print(f"\n{cls}:")
    print(f"  Total tokens: {len(tokens)}")
    print(f"  With PREFIX: {len(prefixed)} ({100*len(prefixed)/len(tokens):.0f}%)")
    print(f"  Without PREFIX: {len(unprefixed)} ({100*len(unprefixed)/len(tokens):.0f}%)")
    if prefixes_used:
        print(f"  PREFIXes used: {prefixes_used}")

# ========================================
# SUMMARY
# ========================================
print("\n" + "=" * 70)
print("SUMMARY: SUFFIX INCOMPATIBILITY EXPLAINED")
print("=" * 70)

print(f"""
Of {len(exclusive_suffix_pairs)} mutually exclusive SUFFIX pairs:

  {explanation_counts['a_suffix_never_cooccur']} ({100*explanation_counts['a_suffix_never_cooccur']/len(exclusive_suffix_pairs):.0f}%): A-SUFFIXes never co-occur
     -> Same mechanism as PREFIX: if A record never has both SUFFIXes, classes can't co-occur

  {explanation_counts['no_middle_overlap']} ({100*explanation_counts['no_middle_overlap']/len(exclusive_suffix_pairs):.0f}%): No MIDDLE overlap
     -> Different MIDDLE vocabularies for different SUFFIX classes

  {explanation_counts['complex']} ({100*explanation_counts['complex']/len(exclusive_suffix_pairs):.0f}%): Complex cases
     -> Need further investigation

KEY INSIGHT:
SUFFIX class incompatibility is explained by the SAME mechanisms as PREFIX:
1. A-SUFFIX sparsity (SUFFIXes don't co-occur in A records)
2. MIDDLE vocabulary separation (different SUFFIXes attach to different MIDDLEs)
""")
