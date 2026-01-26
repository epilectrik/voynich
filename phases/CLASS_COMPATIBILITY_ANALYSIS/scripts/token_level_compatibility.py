"""
TOKEN-LEVEL A-B COMPATIBILITY TEST

Question: For a single A record, which specific B tokens can it produce?
- Does every A record have compatible tokens in EVERY B folio?
- Or are some A records completely incompatible with some B folios?

This goes deeper than class-level to actual token survival.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("TOKEN-LEVEL A-B COMPATIBILITY TEST")
print("Can every A record produce tokens for every B folio?")
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

print(f"\nB vocabulary: {len(b_tokens)} unique tokens")
print(f"B MIDDLEs: {len(b_middles)}, PREFIXes: {len(b_prefixes)}, SUFFIXes: {len(b_suffixes)}")

# Build B folio -> token mapping
b_folio_tokens = defaultdict(set)
for token in tx.currier_b():
    word = token.word
    if word:
        b_folio_tokens[token.folio].add(word)

print(f"B folios: {len(b_folio_tokens)}")

# Build A records with morphology
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

print(f"A records: {len(record_morphology)}")

# TOKEN-LEVEL SURVIVAL: For an A record, which specific B tokens survive?
def get_surviving_tokens(prefixes, middles, suffixes):
    """Return set of B tokens that survive this A record's filtering."""
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    surviving = set()
    for word, info in b_tokens.items():
        # MIDDLE check
        if info['middle'] is None:
            middle_ok = True
        else:
            middle_ok = info['middle'] in pp_middles

        # PREFIX check
        if info['prefix'] is None:
            prefix_ok = True
        else:
            prefix_ok = info['prefix'] in pp_prefixes

        # SUFFIX check
        if info['suffix'] is None:
            suffix_ok = True
        else:
            suffix_ok = info['suffix'] in pp_suffixes

        if middle_ok and prefix_ok and suffix_ok:
            surviving.add(word)

    return surviving

# For each A record, compute surviving tokens and check B folio coverage
print("\n" + "=" * 70)
print("COMPUTING TOKEN-LEVEL SURVIVAL")
print("=" * 70)

a_record_keys = list(record_morphology.keys())
b_folio_list = list(b_folio_tokens.keys())

# Track: for each A record, how many B folios have at least 1 compatible token?
a_record_b_coverage = []
a_record_token_counts = []
zero_coverage_pairs = []

for a_key in a_record_keys:
    prefixes, middles, suffixes = record_morphology[a_key]
    surviving = get_surviving_tokens(prefixes, middles, suffixes)
    a_record_token_counts.append(len(surviving))

    # How many B folios have at least one surviving token?
    b_folios_with_tokens = 0
    for b_folio in b_folio_list:
        overlap = surviving & b_folio_tokens[b_folio]
        if overlap:
            b_folios_with_tokens += 1
        else:
            zero_coverage_pairs.append((a_key, b_folio))

    a_record_b_coverage.append(b_folios_with_tokens)

print(f"\nPer A record:")
print(f"  Mean surviving tokens: {np.mean(a_record_token_counts):.1f}")
print(f"  Min surviving tokens: {np.min(a_record_token_counts)}")
print(f"  Max surviving tokens: {np.max(a_record_token_counts)}")

print(f"\nB folio coverage per A record:")
print(f"  Mean B folios reachable: {np.mean(a_record_b_coverage):.1f} / {len(b_folio_list)}")
print(f"  Min B folios reachable: {np.min(a_record_b_coverage)}")
print(f"  Max B folios reachable: {np.max(a_record_b_coverage)}")

# Key question: Are there any A records that can't reach ALL B folios?
full_coverage = sum(1 for x in a_record_b_coverage if x == len(b_folio_list))
print(f"\nA records with FULL B folio coverage: {full_coverage} / {len(a_record_keys)} ({100*full_coverage/len(a_record_keys):.1f}%)")

partial_coverage = sum(1 for x in a_record_b_coverage if x < len(b_folio_list))
print(f"A records with PARTIAL B folio coverage: {partial_coverage} / {len(a_record_keys)} ({100*partial_coverage/len(a_record_keys):.1f}%)")

# Analyze zero-coverage pairs
print("\n" + "=" * 70)
print("ZERO-COVERAGE PAIRS (A record has NO compatible tokens in B folio)")
print("=" * 70)

print(f"\nTotal zero-coverage pairs: {len(zero_coverage_pairs)}")
print(f"Out of {len(a_record_keys)} x {len(b_folio_list)} = {len(a_record_keys) * len(b_folio_list)} total pairs")
print(f"Zero-coverage rate: {100 * len(zero_coverage_pairs) / (len(a_record_keys) * len(b_folio_list)):.2f}%")

if zero_coverage_pairs:
    # Which A records have the most zero-coverage B folios?
    a_zero_counts = Counter(a_key for a_key, _ in zero_coverage_pairs)
    print("\nA records with most zero-coverage B folios:")
    for a_key, count in a_zero_counts.most_common(10):
        pct = 100 * count / len(b_folio_list)
        prefixes, middles, suffixes = record_morphology[a_key]
        surviving = get_surviving_tokens(prefixes, middles, suffixes)
        print(f"  {a_key}: {count} B folios unreachable ({pct:.1f}%), {len(surviving)} surviving tokens")
        print(f"    PREFIXes: {prefixes}")
        print(f"    MIDDLEs: {len(middles)}")

    # Which B folios are most often unreachable?
    b_zero_counts = Counter(b_folio for _, b_folio in zero_coverage_pairs)
    print("\nB folios most often unreachable:")
    for b_folio, count in b_zero_counts.most_common(10):
        pct = 100 * count / len(a_record_keys)
        folio_tokens = b_folio_tokens[b_folio]
        print(f"  {b_folio}: unreachable by {count} A records ({pct:.1f}%), {len(folio_tokens)} unique tokens")

# Detailed analysis of a sample zero-coverage pair
if zero_coverage_pairs:
    print("\n" + "=" * 70)
    print("SAMPLE ZERO-COVERAGE PAIR ANALYSIS")
    print("=" * 70)

    a_key, b_folio = zero_coverage_pairs[0]
    prefixes, middles, suffixes = record_morphology[a_key]
    surviving = get_surviving_tokens(prefixes, middles, suffixes)
    b_tokens_in_folio = b_folio_tokens[b_folio]

    print(f"\nA record: {a_key}")
    print(f"  A PREFIXes: {prefixes}")
    print(f"  A MIDDLEs: {middles}")
    print(f"  A SUFFIXes: {suffixes}")
    print(f"  Surviving B tokens: {len(surviving)}")

    print(f"\nB folio: {b_folio}")
    print(f"  Unique tokens in folio: {len(b_tokens_in_folio)}")

    # Why no overlap?
    print("\nWhy no overlap?")
    # Check a sample of B folio tokens
    sample_b = list(b_tokens_in_folio)[:10]
    for word in sample_b:
        info = b_tokens[word]
        reasons = []
        if info['middle'] and info['middle'] not in (middles & b_middles):
            reasons.append(f"MIDDLE '{info['middle']}' not in PP")
        if info['prefix'] and info['prefix'] not in (prefixes & b_prefixes):
            reasons.append(f"PREFIX '{info['prefix']}' not in PP")
        if info['suffix'] and info['suffix'] not in (suffixes & b_suffixes):
            reasons.append(f"SUFFIX '{info['suffix']}' not in PP")
        print(f"  {word}: {', '.join(reasons) if reasons else 'SHOULD SURVIVE?'}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if full_coverage == len(a_record_keys):
    print("""
RESULT: EVERY A record can produce at least one token for EVERY B folio.
This means A->B compatibility is UNIVERSAL at the token level.
No A record is completely cut off from any B folio.
""")
elif full_coverage > len(a_record_keys) * 0.9:
    print(f"""
RESULT: {100*full_coverage/len(a_record_keys):.1f}% of A records have FULL B folio coverage.
Most A records can reach all B folios, but some have gaps.
Zero-coverage rate: {100 * len(zero_coverage_pairs) / (len(a_record_keys) * len(b_folio_list)):.2f}%
""")
else:
    print(f"""
RESULT: Only {100*full_coverage/len(a_record_keys):.1f}% of A records have FULL B folio coverage.
Many A records have B folios they cannot reach at all.
Zero-coverage rate: {100 * len(zero_coverage_pairs) / (len(a_record_keys) * len(b_folio_list)):.2f}%

This suggests A records are NOT universally compatible with all B folios.
Some A records may be "specialized" for certain B folio subsets.
""")
