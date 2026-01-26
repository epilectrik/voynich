#!/usr/bin/env python3
"""
Analyze the 'y-' initial class in PREFIX-FORBIDDEN RI MIDDLEs.

Questions:
1. What is the full inventory of y- MIDDLEs?
2. Do they show internal sub-structure?
3. How do they compare to non-y- PREFIX-FORBIDDEN?
4. Token frequency - are they common or rare?
5. Do they cluster by folio/section?
"""

import csv
import json
from collections import Counter, defaultdict

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

def has_prefix(token):
    for p in PREFIXES:
        if token.startswith(p) and len(token) > len(p):
            return True
    return False

# Classify MIDDLEs
appears_with_prefix = set()
appears_without_prefix = set()

# Also track token occurrences
middle_tokens = defaultdict(list)  # middle -> list of (folio, word)

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        if not word or '*' in word:
            continue

        for m in ri_middles:
            if m in word:
                if has_prefix(word):
                    appears_with_prefix.add(m)
                else:
                    appears_without_prefix.add(m)
                    middle_tokens[m].append((folio, word))

prefix_forbidden = appears_without_prefix - appears_with_prefix

# Separate y- and non-y- PREFIX-FORBIDDEN
y_initial = {m for m in prefix_forbidden if m.startswith('y')}
non_y_initial = prefix_forbidden - y_initial

print("="*70)
print("Y-INITIAL CLASS ANALYSIS")
print("="*70)

print(f"\nPREFIX-FORBIDDEN total: {len(prefix_forbidden)}")
print(f"  y-initial: {len(y_initial)} ({100*len(y_initial)/len(prefix_forbidden):.1f}%)")
print(f"  non-y-initial: {len(non_y_initial)} ({100*len(non_y_initial)/len(prefix_forbidden):.1f}%)")

# ============================================================
# 1. FULL INVENTORY OF Y- MIDDLES
# ============================================================
print("\n" + "="*70)
print("1. Y-INITIAL MIDDLE INVENTORY")
print("="*70)

# Group by second character
y_by_second = defaultdict(list)
for m in sorted(y_initial):
    if len(m) > 1:
        y_by_second[m[1]].append(m)
    else:
        y_by_second['(single)'].append(m)

print(f"\nGrouped by second character:")
for char in sorted(y_by_second.keys(), key=lambda x: -len(y_by_second[x])):
    middles = y_by_second[char]
    print(f"\n  y{char}- ({len(middles)} MIDDLEs):")
    for m in sorted(middles)[:10]:
        token_count = len(middle_tokens.get(m, []))
        print(f"    {m} ({token_count} tokens)")
    if len(middles) > 10:
        print(f"    ... and {len(middles) - 10} more")

# ============================================================
# 2. INTERNAL STRUCTURE OF Y- CLASS
# ============================================================
print("\n" + "="*70)
print("2. Y-INITIAL INTERNAL STRUCTURE")
print("="*70)

# Common patterns after y-
def get_suffix_after_y(m):
    return m[1:] if len(m) > 1 else ''

y_suffixes = Counter(get_suffix_after_y(m) for m in y_initial)

print(f"\nWhat follows 'y' (top 15):")
for suf, cnt in y_suffixes.most_common(15):
    print(f"  y-{suf}: {cnt}")

# Check for known morpheme patterns
print("\nChecking for known morpheme patterns after y-:")

# Does the part after y- look like a PREFIX?
y_with_prefix_pattern = []
for m in y_initial:
    rest = m[1:]
    for p in PREFIXES:
        if rest.startswith(p):
            y_with_prefix_pattern.append((m, p, rest[len(p):]))
            break

print(f"\n  y- followed by PREFIX-like string: {len(y_with_prefix_pattern)}")
for m, p, remainder in sorted(y_with_prefix_pattern)[:15]:
    print(f"    {m} = y + [{p}] + {remainder}")

# ============================================================
# 3. COMPARE Y- TO NON-Y- PREFIX-FORBIDDEN
# ============================================================
print("\n" + "="*70)
print("3. Y-INITIAL vs NON-Y-INITIAL COMPARISON")
print("="*70)

# Length comparison
y_lengths = [len(m) for m in y_initial]
non_y_lengths = [len(m) for m in non_y_initial]

avg_y = sum(y_lengths) / len(y_lengths) if y_lengths else 0
avg_non_y = sum(non_y_lengths) / len(non_y_lengths) if non_y_lengths else 0

print(f"\nAverage length:")
print(f"  y-initial: {avg_y:.2f} chars")
print(f"  non-y-initial: {avg_non_y:.2f} chars")

# Ending character comparison
y_endings = Counter(m[-1] for m in y_initial if m)
non_y_endings = Counter(m[-1] for m in non_y_initial if m)

print(f"\nEnding characters (top 5):")
print(f"  y-initial: {y_endings.most_common(5)}")
print(f"  non-y-initial: {non_y_endings.most_common(5)}")

# Bigram comparison (excluding initial y)
def get_bigrams(s):
    return [s[i:i+2] for i in range(len(s)-1)]

y_bigrams = Counter()
non_y_bigrams = Counter()

for m in y_initial:
    # Get bigrams after the initial y
    y_bigrams.update(get_bigrams(m[1:]))
for m in non_y_initial:
    non_y_bigrams.update(get_bigrams(m))

print(f"\nInternal bigrams (y-initial, after the y):")
for bg, cnt in y_bigrams.most_common(10):
    print(f"  '{bg}': {cnt}")

print(f"\nInternal bigrams (non-y-initial):")
for bg, cnt in non_y_bigrams.most_common(10):
    print(f"  '{bg}': {cnt}")

# ============================================================
# 4. TOKEN FREQUENCY
# ============================================================
print("\n" + "="*70)
print("4. TOKEN FREQUENCY")
print("="*70)

# Count tokens per MIDDLE
y_token_counts = [len(middle_tokens.get(m, [])) for m in y_initial]
non_y_token_counts = [len(middle_tokens.get(m, [])) for m in non_y_initial]

total_y_tokens = sum(y_token_counts)
total_non_y_tokens = sum(non_y_token_counts)

avg_y_tokens = total_y_tokens / len(y_initial) if y_initial else 0
avg_non_y_tokens = total_non_y_tokens / len(non_y_initial) if non_y_initial else 0

print(f"\nToken statistics:")
print(f"  y-initial: {total_y_tokens} total tokens, {avg_y_tokens:.1f} avg per MIDDLE")
print(f"  non-y-initial: {total_non_y_tokens} total tokens, {avg_non_y_tokens:.1f} avg per MIDDLE")

# Most frequent y- MIDDLEs
print(f"\nMost frequent y-initial MIDDLEs:")
y_freq = [(m, len(middle_tokens.get(m, []))) for m in y_initial]
for m, cnt in sorted(y_freq, key=lambda x: -x[1])[:15]:
    print(f"  {m}: {cnt} tokens")

# ============================================================
# 5. FOLIO/SECTION DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("5. FOLIO DISTRIBUTION")
print("="*70)

# Where do y-initial tokens appear?
y_folios = Counter()
non_y_folios = Counter()

for m in y_initial:
    for folio, word in middle_tokens.get(m, []):
        y_folios[folio] += 1

for m in non_y_initial:
    for folio, word in middle_tokens.get(m, []):
        non_y_folios[folio] += 1

print(f"\ny-initial tokens appear in {len(y_folios)} folios")
print(f"non-y-initial tokens appear in {len(non_y_folios)} folios")

print(f"\nTop folios for y-initial:")
for folio, cnt in y_folios.most_common(10):
    print(f"  {folio}: {cnt} tokens")

# Check if any folios are y-heavy
print(f"\nFolios where y-initial is >30% of PREFIX-FORBIDDEN tokens:")
for folio in sorted(set(y_folios.keys()) | set(non_y_folios.keys())):
    y_cnt = y_folios.get(folio, 0)
    non_y_cnt = non_y_folios.get(folio, 0)
    total = y_cnt + non_y_cnt
    if total > 5 and y_cnt / total > 0.3:
        pct = 100 * y_cnt / total
        print(f"  {folio}: {y_cnt}/{total} = {pct:.1f}%")

# ============================================================
# 6. SEMANTIC HYPOTHESIS: Y- AS MARKER
# ============================================================
print("\n" + "="*70)
print("6. Y- AS MORPHOLOGICAL MARKER")
print("="*70)

# If y- is a marker, we'd expect:
# 1. What follows y- to match known morphemes
# 2. Some y-X to have non-y-X counterparts

# Check for y-X / X pairs
print("\nChecking for y-X / non-y-X pairs in PREFIX-FORBIDDEN:")
pairs_found = []
for m in y_initial:
    rest = m[1:]
    if rest in non_y_initial:
        pairs_found.append((m, rest))

print(f"  Pairs found: {len(pairs_found)}")
for y_form, base_form in sorted(pairs_found)[:20]:
    y_tokens = len(middle_tokens.get(y_form, []))
    base_tokens = len(middle_tokens.get(base_form, []))
    print(f"    {y_form} ({y_tokens} tok) <-> {base_form} ({base_tokens} tok)")

# Check if y-X appears where X appears with PREFIX
print("\nChecking if y-X corresponds to PREFIX+X:")
# Get PREFIX-REQUIRED middles
prefix_required = appears_with_prefix - appears_without_prefix

y_to_prefixed = []
for m in y_initial:
    rest = m[1:]
    if rest in prefix_required:
        y_to_prefixed.append((m, rest))

print(f"  y-X where X is PREFIX-REQUIRED: {len(y_to_prefixed)}")
for y_form, base_form in sorted(y_to_prefixed)[:15]:
    y_tokens = len(middle_tokens.get(y_form, []))
    print(f"    {y_form} ({y_tokens} tok) ~ PREFIX+{base_form}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Y-INITIAL CLASS PROFILE:
  - {len(y_initial)} MIDDLEs (25.2% of PREFIX-FORBIDDEN)
  - Average length: {avg_y:.2f} chars
  - Total tokens: {total_y_tokens}
  - Appears in {len(y_folios)} folios

STRUCTURAL OBSERVATIONS:
  - y- followed by PREFIX-like string: {len(y_with_prefix_pattern)} cases
  - y-X / non-y-X pairs in PREFIX-FORBIDDEN: {len(pairs_found)}
  - y-X where X is PREFIX-REQUIRED: {len(y_to_prefixed)}

DOMINANT SUBGROUPS:
""")

for char in sorted(y_by_second.keys(), key=lambda x: -len(y_by_second[x]))[:5]:
    print(f"  y{char}-: {len(y_by_second[char])} MIDDLEs")
