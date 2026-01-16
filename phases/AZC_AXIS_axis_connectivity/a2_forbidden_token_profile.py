#!/usr/bin/env python3
"""
A2-FOLLOW: FORBIDDEN TOKEN CHARACTERIZATION

The 18 frequent AZC-only tokens are globally forbidden with local exceptions.
Who ARE these tokens? What makes them restricted?

NOT semantic - STRUCTURAL characterization.
"""

import os
from collections import defaultdict, Counter

os.chdir('C:/git/voynich')

print("=" * 70)
print("A2-FOLLOW: FORBIDDEN TOKEN CHARACTERIZATION")
print("What makes these 18 tokens 'restricted operators'?")
print("=" * 70)

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip('\"') != 'H':
            continue
        all_tokens.append(row)

# Separate by language
azc_tokens = [t for t in all_tokens if t.get('language', '') in ['NA', '']]
a_tokens = [t for t in all_tokens if t.get('language', '') == 'A']
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']

# Get vocabularies
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in a_tokens)
b_words = set(t['word'] for t in b_tokens)
azc_only = azc_words - a_words - b_words

# AZC-only tokens
azc_only_tokens = [t for t in azc_tokens if t['word'] in azc_only]

# Identify the 18 frequent AZC-only tokens
token_totals = Counter(t['word'] for t in azc_only_tokens)
frequent_tokens = sorted([t for t, c in token_totals.items() if c >= 5],
                        key=lambda x: -token_totals[x])

print(f"\nThe 18 Restricted Operators (frequent AZC-only tokens):")
print(f"{'Token':<15} {'Count':<8} {'%AZC-only':<10}")
print("-" * 40)
total_azc_only = len(azc_only_tokens)
for token in frequent_tokens:
    count = token_totals[token]
    pct = count / total_azc_only * 100
    print(f"{token:<15} {count:<8} {pct:<10.2f}")

# =========================================================================
# TEST 1: Are they ALL AZC-unique, or do some appear in A/B?
# =========================================================================

print("\n" + "=" * 70)
print("TEST 1: VOCABULARY EXCLUSIVITY")
print("=" * 70)

for token in frequent_tokens:
    in_a = token in a_words
    in_b = token in b_words
    status = "AZC-ONLY"
    if in_a and in_b:
        status = "SHARED (A+B)"
    elif in_a:
        status = "SHARED (A)"
    elif in_b:
        status = "SHARED (B)"
    print(f"  {token:<15} {status}")

# By definition they're AZC-only (that's how we selected them)
# But let's verify
shared_count = sum(1 for t in frequent_tokens if t in a_words or t in b_words)
print(f"\nVerification: {shared_count}/18 shared with A or B")
print("(Should be 0 by construction)")

# =========================================================================
# TEST 2: Morphological Profile
# =========================================================================

print("\n" + "=" * 70)
print("TEST 2: MORPHOLOGICAL PROFILE")
print("=" * 70)

# Decompose tokens
def decompose_token(word):
    prefixes = ['ch', 'sh', 'qo', 'ok', 'ot', 'ct', 'da', 'ol', 'ar', 'or', 'al', 'op', 'sy']
    suffixes = ['aiin', 'ain', 'iin', 'in', 'an', 'dy', 'edy', 'y', 'ol', 'or', 'ar', 'al', 'ey', 'eey', 'oe', 'es', 'ees']

    prefix = ''
    suffix = ''
    middle = word

    for pf in sorted(prefixes, key=len, reverse=True):
        if word.startswith(pf):
            prefix = pf
            middle = word[len(pf):]
            break

    for sf in sorted(suffixes, key=len, reverse=True):
        if middle.endswith(sf) and len(middle) > len(sf):
            suffix = sf
            middle = middle[:-len(sf)]
            break

    return prefix, middle, suffix

print(f"\n{'Token':<15} {'Prefix':<8} {'Middle':<10} {'Suffix':<8} {'Length':<6}")
print("-" * 55)

prefix_counts = Counter()
suffix_counts = Counter()
middle_counts = Counter()
lengths = []

for token in frequent_tokens:
    prefix, middle, suffix = decompose_token(token)
    prefix_counts[prefix or '(none)'] += 1
    suffix_counts[suffix or '(none)'] += 1
    middle_counts[middle or '(none)'] += 1
    lengths.append(len(token))
    print(f"{token:<15} {prefix or '-':<8} {middle or '-':<10} {suffix or '-':<8} {len(token):<6}")

print(f"\nPrefix distribution: {dict(prefix_counts)}")
print(f"Suffix distribution: {dict(suffix_counts)}")
print(f"Mean length: {sum(lengths)/len(lengths):.1f}")

# =========================================================================
# TEST 3: Section Distribution
# =========================================================================

print("\n" + "=" * 70)
print("TEST 3: SECTION DISTRIBUTION")
print("=" * 70)

# Which AZC sections do these tokens appear in?
section_counts = defaultdict(Counter)
for t in azc_only_tokens:
    if t['word'] in frequent_tokens:
        section = t.get('section', 'UNK')
        section_counts[t['word']][section] += 1

print(f"\n{'Token':<15} {'Z':<6} {'A':<6} {'C':<6} {'Dominant':<10}")
print("-" * 50)

for token in frequent_tokens:
    counts = section_counts[token]
    z = counts.get('Z', 0)
    a = counts.get('A', 0)
    c = counts.get('C', 0)
    total = z + a + c

    if total > 0:
        dominant = max(['Z', 'A', 'C'], key=lambda s: counts.get(s, 0))
        dom_pct = counts.get(dominant, 0) / total * 100
        if dom_pct > 60:
            dominant = f"{dominant} ({dom_pct:.0f}%)"
        else:
            dominant = "MIXED"
    else:
        dominant = "?"

    print(f"{token:<15} {z:<6} {a:<6} {c:<6} {dominant:<10}")

# Calculate section exclusivity
section_exclusive = 0
for token in frequent_tokens:
    counts = section_counts[token]
    sections_present = sum(1 for s in ['Z', 'A', 'C'] if counts.get(s, 0) > 0)
    if sections_present == 1:
        section_exclusive += 1

print(f"\nSection-exclusive tokens: {section_exclusive}/18 ({section_exclusive/18*100:.0f}%)")

# =========================================================================
# TEST 4: Line Position Distribution
# =========================================================================

print("\n" + "=" * 70)
print("TEST 4: LINE POSITION DISTRIBUTION")
print("=" * 70)

# Group by line
by_line = defaultdict(list)
for t in azc_only_tokens:
    key = (t.get('folio', ''), t.get('line_number', ''))
    by_line[key].append(t)

# For each forbidden token, count line-initial/final/interior
position_profile = defaultdict(lambda: {'initial': 0, 'final': 0, 'interior': 0})

for key, tokens in by_line.items():
    for i, t in enumerate(tokens):
        if t['word'] in frequent_tokens:
            if i == 0:
                position_profile[t['word']]['initial'] += 1
            elif i == len(tokens) - 1:
                position_profile[t['word']]['final'] += 1
            else:
                position_profile[t['word']]['interior'] += 1

print(f"\n{'Token':<15} {'Initial%':<10} {'Final%':<10} {'Interior%':<10} {'Boundary%':<10}")
print("-" * 60)

for token in frequent_tokens:
    prof = position_profile[token]
    total = prof['initial'] + prof['final'] + prof['interior']
    if total > 0:
        init_pct = prof['initial'] / total * 100
        final_pct = prof['final'] / total * 100
        inter_pct = prof['interior'] / total * 100
        boundary_pct = (prof['initial'] + prof['final']) / total * 100
    else:
        init_pct = final_pct = inter_pct = boundary_pct = 0

    print(f"{token:<15} {init_pct:<10.1f} {final_pct:<10.1f} {inter_pct:<10.1f} {boundary_pct:<10.1f}")

# =========================================================================
# TEST 5: Placement Distribution (where they DO appear)
# =========================================================================

print("\n" + "=" * 70)
print("TEST 5: PLACEMENT DISTRIBUTION (WHERE ALLOWED)")
print("=" * 70)

# We know they're mostly forbidden. Where DO they appear?
placement_for_token = defaultdict(Counter)
for t in azc_only_tokens:
    if t['word'] in frequent_tokens:
        p = t.get('placement', 'UNK')
        placement_for_token[t['word']][p] += 1

print(f"\n{'Token':<15} {'Placements Where Present':<50}")
print("-" * 70)

for token in frequent_tokens:
    placements = placement_for_token[token]
    if placements:
        p_str = ", ".join(f"{p}({c})" for p, c in placements.most_common(5))
    else:
        p_str = "(none)"
    print(f"{token:<15} {p_str:<50}")

# Which placements allow the most restricted tokens?
placement_allows = Counter()
for token in frequent_tokens:
    for p in placement_for_token[token]:
        placement_allows[p] += 1

print(f"\nPlacements by number of restricted tokens allowed:")
for p, count in placement_allows.most_common():
    print(f"  {p}: {count}/18 allowed")

# =========================================================================
# TEST 6: Repetition Behavior
# =========================================================================

print("\n" + "=" * 70)
print("TEST 6: REPETITION BEHAVIOR")
print("=" * 70)

# Do these tokens ever repeat consecutively?
repeats = Counter()
for key, tokens in by_line.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['word'] == tokens[i+1]['word']:
            if tokens[i]['word'] in frequent_tokens:
                repeats[tokens[i]['word']] += 1

print(f"\n{'Token':<15} {'Consecutive Repeats':<20}")
print("-" * 40)

for token in frequent_tokens:
    rep_count = repeats.get(token, 0)
    print(f"{token:<15} {rep_count:<20}")

total_repeaters = sum(1 for t in frequent_tokens if repeats.get(t, 0) > 0)
print(f"\nTokens that ever repeat: {total_repeaters}/18 ({total_repeaters/18*100:.0f}%)")

# =========================================================================
# PROFILE SUMMARY
# =========================================================================

print("\n" + "=" * 70)
print("RESTRICTED OPERATOR PROFILE SUMMARY")
print("=" * 70)

print(f"""
THE 18 RESTRICTED OPERATORS:

1. VOCABULARY STATUS:
   - 100% AZC-only (by construction)
   - Never appear in Currier A or B
   - Unique to Astronomical/Zodiac/Cosmological sections

2. MORPHOLOGICAL SIGNATURE:
   - Dominant prefix: {prefix_counts.most_common(1)[0] if prefix_counts else 'none'}
   - Dominant suffix: {suffix_counts.most_common(1)[0] if suffix_counts else 'none'}
   - Mean length: {sum(lengths)/len(lengths):.1f} characters

3. SECTION DISTRIBUTION:
   - Section-exclusive: {section_exclusive}/18 ({section_exclusive/18*100:.0f}%)
   - Most appear in specific AZC section only

4. LINE POSITION:
   - Boundary enrichment varies by token
   - No uniform position preference

5. PLACEMENT (WHERE ALLOWED):
   - Most permissive: {placement_allows.most_common(1)[0] if placement_allows else 'none'}
   - These tokens cluster in exception zones

6. REPETITION:
   - {total_repeaters}/18 ever repeat consecutively
   - Low repetition = single-use operators?

STRUCTURAL CLASSIFICATION:
""")

# Determine classification
if section_exclusive >= 14:
    print("   SECTION-LOCKED RESTRICTED OPERATORS")
    print("   -> Each token belongs to ONE AZC section")
    print("   -> Restriction is section-boundary enforcement")
elif total_repeaters <= 4:
    print("   NON-REPEATING RESTRICTED OPERATORS")
    print("   -> Tokens that cannot iterate")
    print("   -> Single-shot actions or markers")
else:
    print("   GENERAL RESTRICTED OPERATORS")
    print("   -> No dominant pattern")
    print("   -> Restriction is purely positional")

print("\n" + "=" * 70)
print("A2-FOLLOW COMPLETE")
print("=" * 70)
