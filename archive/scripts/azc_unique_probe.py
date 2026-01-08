#!/usr/bin/env python3
"""
AZC Unique Vocabulary Probe

Investigates the 25.4% unique vocabulary (1,529 types) that appears
ONLY in AZC sections, not in Currier A or B.

Questions:
- Does it execute (B-like grammar patterns)?
- Does it index (A-like registry patterns)?
- Is it something else (labels, astronomical terms)?
"""

import json
import os
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')

# =============================================================================
# LOAD DATA
# =============================================================================

print("=" * 60)
print("AZC UNIQUE VOCABULARY PROBE")
print("=" * 60)

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Extract all tokens by Currier type
azc_tokens = []
a_tokens = []
b_tokens = []

for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        lang = row.get('language', '')
        word = row.get('word', '')
        if lang == 'NA' or lang == '':
            azc_tokens.append(row)
        elif lang == 'A':
            a_tokens.append(row)
        elif lang == 'B':
            b_tokens.append(row)

# Get vocabularies
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in a_tokens)
b_words = set(t['word'] for t in b_tokens)

# AZC-only vocabulary
azc_only = azc_words - a_words - b_words
azc_only_tokens = [t for t in azc_tokens if t['word'] in azc_only]

print(f"\nAZC-only vocabulary: {len(azc_only)} types")
print(f"AZC-only token occurrences: {len(azc_only_tokens)}")

# =============================================================================
# SECTION DISTRIBUTION
# =============================================================================

print("\n" + "=" * 60)
print("SECTION DISTRIBUTION")
print("=" * 60)

by_section = defaultdict(list)
for t in azc_only_tokens:
    by_section[t.get('section', 'UNK')].append(t['word'])

print("\nAZC-only by section:")
for sec, tokens in sorted(by_section.items(), key=lambda x: -len(x[1])):
    unique = len(set(tokens))
    print(f"  {sec}: {len(tokens)} tokens ({unique} types)")

# Section exclusivity
section_vocab = {sec: set(tokens) for sec, tokens in by_section.items()}
exclusive_count = 0
multi_section = 0
for word in azc_only:
    sections_with_word = [s for s, v in section_vocab.items() if word in v]
    if len(sections_with_word) == 1:
        exclusive_count += 1
    else:
        multi_section += 1

print(f"\nSection exclusivity:")
print(f"  Single-section types: {exclusive_count} ({exclusive_count/len(azc_only):.1%})")
print(f"  Multi-section types: {multi_section} ({multi_section/len(azc_only):.1%})")

# =============================================================================
# MORPHOLOGICAL ANALYSIS
# =============================================================================

print("\n" + "=" * 60)
print("MORPHOLOGICAL ANALYSIS")
print("=" * 60)

prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt', 'kch', 'ko', 'op', 'oe', 'oa', 'yp', 'ys']
suffixes = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eedy', 'y', 'ey', 'eey', 'ol', 'al', 'or', 'ar', 'chy', 'shy', 'hy', 'eol', 'eal', 'os', 'es', 'as']

prefix_counts = Counter()
suffix_counts = Counter()
no_prefix = []
no_suffix = []

for w in azc_only:
    found_p = False
    for p in sorted(prefixes, key=len, reverse=True):
        if w.startswith(p):
            prefix_counts[p] += 1
            found_p = True
            break
    if not found_p:
        prefix_counts['NONE'] += 1
        no_prefix.append(w)

    found_s = False
    for s in sorted(suffixes, key=len, reverse=True):
        if w.endswith(s):
            suffix_counts[s] += 1
            found_s = True
            break
    if not found_s:
        suffix_counts['NONE'] += 1
        no_suffix.append(w)

prefix_cov = 1 - prefix_counts['NONE']/len(azc_only)
suffix_cov = 1 - suffix_counts['NONE']/len(azc_only)

print(f"\nPrefix coverage: {prefix_cov:.1%}")
print(f"Suffix coverage: {suffix_cov:.1%}")
print(f"\nTop prefixes: {prefix_counts.most_common(10)}")
print(f"\nTop suffixes: {suffix_counts.most_common(10)}")

# =============================================================================
# NO-PREFIX ANALYSIS (Potential unique markers)
# =============================================================================

print("\n" + "=" * 60)
print("NO-PREFIX TOKENS (Potential unique markers)")
print("=" * 60)

print(f"\nTokens with NO standard prefix: {len(no_prefix)} types")

# Starting characters
start_chars = Counter(w[0] if w else '' for w in no_prefix)
print(f"\nStarting characters:")
for char, count in start_chars.most_common(15):
    print(f"  '{char}': {count} ({count/len(no_prefix):.1%})")

# Check for special characters (asterisks, etc.)
special = [w for w in no_prefix if '*' in w or '?' in w or '!' in w]
print(f"\nTokens with special characters: {len(special)}")
if special:
    print(f"  Examples: {special[:20]}")

# Short tokens (potential labels)
short_tokens = [w for w in no_prefix if len(w) <= 3]
print(f"\nShort tokens (<=3 chars): {len(short_tokens)}")
print(f"  Examples: {sorted(short_tokens)[:30]}")

# Sample of no-prefix tokens
print(f"\nSample no-prefix tokens:")
print(sorted(no_prefix, key=len)[:40])

# =============================================================================
# LINE POSITION ANALYSIS
# =============================================================================

print("\n" + "=" * 60)
print("LINE POSITION ANALYSIS")
print("=" * 60)

# Note: line_initial might be stored differently
# Let's check what columns we have
sample = azc_only_tokens[0] if azc_only_tokens else {}
print(f"Available columns: {list(sample.keys())}")

# Try to determine position from available data
line_positions = defaultdict(int)
for t in azc_only_tokens:
    # Check if there's position info
    li = t.get('line_initial', '')
    lf = t.get('line_final', '')
    if li == '1' or li == 1:
        line_positions['initial'] += 1
    if lf == '1' or lf == 1:
        line_positions['final'] += 1

total = len(azc_only_tokens)
print(f"\nLine position (from metadata):")
print(f"  Line-initial: {line_positions['initial']} ({line_positions['initial']/total:.1%})")
print(f"  Line-final: {line_positions['final']} ({line_positions['final']/total:.1%})")

# =============================================================================
# REPETITION ANALYSIS
# =============================================================================

print("\n" + "=" * 60)
print("REPETITION ANALYSIS")
print("=" * 60)

word_counts = Counter(t['word'] for t in azc_only_tokens)
hapax = sum(1 for c in word_counts.values() if c == 1)
low_freq = sum(1 for c in word_counts.values() if 2 <= c <= 5)
high_freq = sum(1 for c in word_counts.values() if c > 5)

print(f"\nFrequency distribution:")
print(f"  Hapax (1 occurrence): {hapax} types ({hapax/len(azc_only):.1%})")
print(f"  Low freq (2-5): {low_freq} types ({low_freq/len(azc_only):.1%})")
print(f"  High freq (>5): {high_freq} types ({high_freq/len(azc_only):.1%})")

print(f"\nMost common AZC-only tokens:")
for w, c in word_counts.most_common(25):
    print(f"  {w}: {c}")

# =============================================================================
# TRANSITION ANALYSIS (Does it execute?)
# =============================================================================

print("\n" + "=" * 60)
print("TRANSITION ANALYSIS (Does it execute?)")
print("=" * 60)

# Group by folio and line to analyze sequences
by_line = defaultdict(list)
for t in azc_only_tokens:
    key = (t.get('folio', ''), t.get('line_number', ''))
    by_line[key].append(t['word'])

# Check if AZC-only tokens appear in sequences or isolation
isolated = 0
in_sequence = 0
for key, words in by_line.items():
    if len(words) == 1:
        isolated += 1
    else:
        in_sequence += 1

print(f"\nAZC-only token clustering:")
print(f"  Lines with single AZC-only token: {isolated}")
print(f"  Lines with multiple AZC-only tokens: {in_sequence}")

# Adjacent pair analysis
adjacent_pairs = Counter()
for key, words in by_line.items():
    for i in range(len(words) - 1):
        pair = (words[i], words[i+1])
        adjacent_pairs[pair] += 1

print(f"\nAdjacent AZC-only pairs: {len(adjacent_pairs)}")
print(f"Most common pairs:")
for pair, count in adjacent_pairs.most_common(10):
    print(f"  {pair[0]} -> {pair[1]}: {count}")

# =============================================================================
# FOLIO CONCENTRATION
# =============================================================================

print("\n" + "=" * 60)
print("FOLIO CONCENTRATION")
print("=" * 60)

by_folio = defaultdict(list)
for t in azc_only_tokens:
    by_folio[t.get('folio', '')].append(t['word'])

print(f"\nAZC-only tokens by folio (top 15):")
for folio, tokens in sorted(by_folio.items(), key=lambda x: -len(x[1]))[:15]:
    unique = len(set(tokens))
    print(f"  {folio}: {len(tokens)} tokens ({unique} types)")

# =============================================================================
# VERDICT
# =============================================================================

print("\n" + "=" * 60)
print("PRELIMINARY VERDICT")
print("=" * 60)

verdicts = []

# Test 1: Morphological conformity
if prefix_cov < 0.40:
    verdicts.append("LOW prefix coverage suggests NON-STANDARD morphology")
else:
    verdicts.append("STANDARD prefix coverage suggests conformity with main system")

# Test 2: Hapax dominance
if hapax / len(azc_only) > 0.70:
    verdicts.append("HIGH hapax rate suggests LABELS or UNIQUE TERMS")
else:
    verdicts.append("Lower hapax rate suggests FUNCTIONAL vocabulary")

# Test 3: Section exclusivity
if exclusive_count / len(azc_only) > 0.70:
    verdicts.append("HIGH section exclusivity suggests SECTION-SPECIFIC markers")
else:
    verdicts.append("Lower exclusivity suggests CROSS-SECTION vocabulary")

# Test 4: Special characters
if len(special) > 50:
    verdicts.append("MANY special characters suggests DAMAGED/UNCERTAIN readings")
else:
    verdicts.append("Few special characters suggests CLEAN vocabulary")

print("\nFindings:")
for v in verdicts:
    print(f"  - {v}")

# Save results
results = {
    'azc_only_types': len(azc_only),
    'azc_only_tokens': len(azc_only_tokens),
    'prefix_coverage': prefix_cov,
    'suffix_coverage': suffix_cov,
    'hapax_rate': hapax / len(azc_only),
    'section_exclusive_rate': exclusive_count / len(azc_only),
    'special_char_count': len(special),
    'no_prefix_count': len(no_prefix),
    'top_tokens': word_counts.most_common(50),
    'section_distribution': {s: len(t) for s, t in by_section.items()},
}

with open('phases/AZC_astronomical_zodiac_cosmological/azc_unique_probe.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to: phases/AZC_astronomical_zodiac_cosmological/azc_unique_probe.json")
print("\n" + "=" * 60)
print("PROBE COMPLETE")
print("=" * 60)
