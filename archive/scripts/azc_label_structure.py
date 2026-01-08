#!/usr/bin/env python3
"""
AZC Label Structure Analysis

Deep probe into the 1,529 unique AZC labels to find structural patterns:
- Positional patterns (where do labels appear?)
- Morphological structure (how are labels built?)
- Co-occurrence patterns (what appears together?)
- Cross-folio patterns (any standard vocabulary?)
- Section-specific structure (do Z, A, C differ?)
"""

import json
import os
from collections import Counter, defaultdict
import math

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC LABEL STRUCTURE ANALYSIS")
print("=" * 70)

# =============================================================================
# LOAD DATA
# =============================================================================

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Extract tokens
azc_tokens = []
a_tokens = []
b_tokens = []

for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        lang = row.get('language', '')
        if lang == 'NA' or lang == '':
            azc_tokens.append(row)
        elif lang == 'A':
            a_tokens.append(row)
        elif lang == 'B':
            b_tokens.append(row)

# Get AZC-only vocabulary
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in a_tokens)
b_words = set(t['word'] for t in b_tokens)
azc_only = azc_words - a_words - b_words
azc_only_tokens = [t for t in azc_tokens if t['word'] in azc_only]

print(f"\nAZC-only labels: {len(azc_only)} types, {len(azc_only_tokens)} tokens")

# =============================================================================
# 1. POSITIONAL ANALYSIS - Where do labels appear on the page?
# =============================================================================

print("\n" + "=" * 70)
print("1. POSITIONAL ANALYSIS")
print("=" * 70)

# Analyze by line number within folio
by_folio_line = defaultdict(list)
for t in azc_only_tokens:
    folio = t.get('folio', '')
    line_num = t.get('line_number', '')
    by_folio_line[folio].append((line_num, t['word']))

# Get line distribution per folio
print("\nLine number distribution (sample folios):")
for folio in sorted(by_folio_line.keys())[:5]:
    lines_data = by_folio_line[folio]
    line_nums = [int(ln) for ln, w in lines_data if ln.isdigit()]
    if line_nums:
        print(f"  {folio}: lines {min(line_nums)}-{max(line_nums)}, "
              f"mean={sum(line_nums)/len(line_nums):.1f}, count={len(line_nums)}")

# Check placement column
placements = Counter(t.get('placement', '') for t in azc_only_tokens)
print(f"\nPlacement distribution:")
for p, c in placements.most_common(10):
    print(f"  '{p}': {c} ({c/len(azc_only_tokens):.1%})")

# =============================================================================
# 2. MORPHOLOGICAL DECOMPOSITION
# =============================================================================

print("\n" + "=" * 70)
print("2. MORPHOLOGICAL DECOMPOSITION")
print("=" * 70)

# Extended prefix list including potential label-specific prefixes
all_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt',
                'kch', 'ko', 'op', 'oe', 'oa', 'yp', 'ys', 'ar', 'or', 'al',
                'o', 'y', 's', 'd', 'a', 'c', 'k', 'q', 't']

all_suffixes = ['aiin', 'ain', 'iin', 'in', 'dy', 'edy', 'eedy', 'y', 'ey',
                'eey', 'ol', 'al', 'or', 'ar', 'chy', 'shy', 'hy', 'eol',
                'eal', 'os', 'es', 'as', 'am', 'an', 'r', 'l', 's']

# Decompose each label
decompositions = []
for word in azc_only:
    # Find longest matching prefix
    prefix = ''
    for p in sorted(all_prefixes, key=len, reverse=True):
        if word.startswith(p) and len(p) <= len(word) - 1:
            prefix = p
            break

    # Find longest matching suffix
    suffix = ''
    remainder = word[len(prefix):] if prefix else word
    for s in sorted(all_suffixes, key=len, reverse=True):
        if remainder.endswith(s) and len(s) <= len(remainder):
            suffix = s
            break

    # Middle is what's left
    if prefix and suffix:
        middle = word[len(prefix):-len(suffix)] if len(suffix) > 0 else word[len(prefix):]
    elif prefix:
        middle = word[len(prefix):]
        suffix = ''
    elif suffix:
        middle = word[:-len(suffix)]
        prefix = ''
    else:
        middle = word

    decompositions.append({
        'word': word,
        'prefix': prefix,
        'middle': middle,
        'suffix': suffix,
        'structure': f"{prefix or '_'}+{middle or '_'}+{suffix or '_'}"
    })

# Analyze decomposition patterns
prefix_dist = Counter(d['prefix'] for d in decompositions)
suffix_dist = Counter(d['suffix'] for d in decompositions)
middle_dist = Counter(d['middle'] for d in decompositions)

print(f"\nPrefix distribution (top 15):")
for p, c in prefix_dist.most_common(15):
    pct = c / len(decompositions) * 100
    print(f"  '{p or 'NONE'}': {c} ({pct:.1f}%)")

print(f"\nSuffix distribution (top 15):")
for s, c in suffix_dist.most_common(15):
    pct = c / len(decompositions) * 100
    print(f"  '{s or 'NONE'}': {c} ({pct:.1f}%)")

print(f"\nMiddle components (top 20):")
for m, c in middle_dist.most_common(20):
    if c > 1:  # Only show repeated middles
        print(f"  '{m}': {c}")

# =============================================================================
# 3. STRUCTURAL TEMPLATES
# =============================================================================

print("\n" + "=" * 70)
print("3. STRUCTURAL TEMPLATES")
print("=" * 70)

# Look for common structural patterns
structures = Counter(d['structure'] for d in decompositions)
print(f"\nMost common structures:")
for struct, count in structures.most_common(20):
    if count > 2:
        examples = [d['word'] for d in decompositions if d['structure'] == struct][:3]
        print(f"  {struct}: {count} (e.g., {', '.join(examples)})")

# Length distribution
lengths = Counter(len(w) for w in azc_only)
print(f"\nLength distribution:")
for length in sorted(lengths.keys()):
    count = lengths[length]
    bar = '#' * (count // 10)
    print(f"  {length:2d} chars: {count:4d} {bar}")

# =============================================================================
# 4. SECTION-SPECIFIC PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("4. SECTION-SPECIFIC PATTERNS")
print("=" * 70)

by_section = defaultdict(list)
for t in azc_only_tokens:
    by_section[t.get('section', '')].append(t['word'])

for section in ['Z', 'A', 'C']:
    if section not in by_section:
        continue

    words = by_section[section]
    unique_words = set(words)

    # Prefix distribution for this section
    sec_prefixes = Counter()
    for w in unique_words:
        for p in sorted(all_prefixes[:12], key=len, reverse=True):  # Main prefixes only
            if w.startswith(p):
                sec_prefixes[p] += 1
                break
        else:
            sec_prefixes['OTHER'] += 1

    print(f"\nSection {section} ({len(words)} tokens, {len(unique_words)} types):")
    print(f"  Top prefixes: {sec_prefixes.most_common(5)}")

    # Most common words in this section
    word_counts = Counter(words)
    print(f"  Most common: {word_counts.most_common(5)}")

# =============================================================================
# 5. CROSS-FOLIO PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("5. CROSS-FOLIO PATTERNS (Potential standard vocabulary)")
print("=" * 70)

# Which labels appear in multiple folios?
by_folio_vocab = defaultdict(set)
for t in azc_only_tokens:
    by_folio_vocab[t.get('folio', '')].add(t['word'])

word_to_folios = defaultdict(set)
for folio, vocab in by_folio_vocab.items():
    for word in vocab:
        word_to_folios[word].add(folio)

multi_folio = {w: folios for w, folios in word_to_folios.items() if len(folios) > 1}
print(f"\nLabels appearing in multiple folios: {len(multi_folio)} / {len(azc_only)}")

if multi_folio:
    print(f"\nLabels in 3+ folios (potential standard terms):")
    for word, folios in sorted(multi_folio.items(), key=lambda x: -len(x[1])):
        if len(folios) >= 3:
            print(f"  '{word}': {len(folios)} folios - {sorted(folios)[:5]}...")

# =============================================================================
# 6. ADJACENCY PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("6. ADJACENCY PATTERNS (What appears next to labels?)")
print("=" * 70)

# Get context for each AZC-only token
# Look at what comes before and after in the line
by_folio_line_all = defaultdict(list)
for t in azc_tokens:  # All AZC tokens, not just unique
    key = (t.get('folio', ''), t.get('line_number', ''))
    by_folio_line_all[key].append(t['word'])

# Find neighbors of AZC-only tokens
before_counts = Counter()
after_counts = Counter()

for key, line_words in by_folio_line_all.items():
    for i, word in enumerate(line_words):
        if word in azc_only:
            if i > 0:
                before_counts[line_words[i-1]] += 1
            if i < len(line_words) - 1:
                after_counts[line_words[i+1]] += 1

print(f"\nMost common tokens BEFORE labels:")
for w, c in before_counts.most_common(15):
    in_azc = "LABEL" if w in azc_only else "shared"
    print(f"  '{w}': {c} ({in_azc})")

print(f"\nMost common tokens AFTER labels:")
for w, c in after_counts.most_common(15):
    in_azc = "LABEL" if w in azc_only else "shared"
    print(f"  '{w}': {c} ({in_azc})")

# =============================================================================
# 7. REPETITION PATTERNS WITHIN FOLIOS
# =============================================================================

print("\n" + "=" * 70)
print("7. REPETITION PATTERNS WITHIN FOLIOS")
print("=" * 70)

# Do labels repeat within the same folio?
folio_repetitions = {}
for folio, vocab in by_folio_vocab.items():
    words_in_folio = [t['word'] for t in azc_only_tokens if t.get('folio') == folio]
    word_counts = Counter(words_in_folio)
    repeated = {w: c for w, c in word_counts.items() if c > 1}
    if repeated:
        folio_repetitions[folio] = repeated

print(f"\nFolios with repeated labels: {len(folio_repetitions)}")
for folio, reps in sorted(folio_repetitions.items(), key=lambda x: -sum(x[1].values()))[:10]:
    total_reps = sum(reps.values())
    print(f"  {folio}: {len(reps)} repeated types, {total_reps} total repetitions")
    for w, c in sorted(reps.items(), key=lambda x: -x[1])[:3]:
        print(f"    '{w}' x{c}")

# =============================================================================
# 8. SPECIAL PATTERN DETECTION
# =============================================================================

print("\n" + "=" * 70)
print("8. SPECIAL PATTERN DETECTION")
print("=" * 70)

# Look for systematic patterns
# Pattern 1: Labels ending in numbers or systematic suffixes
systematic_endings = defaultdict(list)
for word in azc_only:
    # Check last 2-3 characters
    if len(word) >= 3:
        ending = word[-3:]
        systematic_endings[ending].append(word)

print(f"\nCommon 3-char endings (potential systematic markers):")
for ending, words in sorted(systematic_endings.items(), key=lambda x: -len(x[1]))[:15]:
    if len(words) >= 5:
        print(f"  '-{ending}': {len(words)} labels (e.g., {words[:3]})")

# Pattern 2: Labels with internal repetition
internal_rep = []
for word in azc_only:
    if len(word) >= 4:
        # Check for doubled characters or patterns
        for i in range(len(word) - 1):
            if word[i] == word[i+1]:
                internal_rep.append(word)
                break

print(f"\nLabels with doubled characters: {len(internal_rep)}")
print(f"  Examples: {internal_rep[:15]}")

# Pattern 3: Very short labels (potential single-symbol markers)
very_short = [w for w in azc_only if len(w) <= 2]
print(f"\nVery short labels (1-2 chars): {len(very_short)}")
print(f"  All: {sorted(very_short)}")

# =============================================================================
# 9. ZODIAC-SPECIFIC ANALYSIS
# =============================================================================

print("\n" + "=" * 70)
print("9. ZODIAC SECTION DEEP DIVE")
print("=" * 70)

z_tokens = [t for t in azc_only_tokens if t.get('section') == 'Z']
z_words = set(t['word'] for t in z_tokens)

print(f"\nZodiac section: {len(z_tokens)} tokens, {len(z_words)} unique labels")

# Group by folio
z_by_folio = defaultdict(list)
for t in z_tokens:
    z_by_folio[t.get('folio', '')].append(t['word'])

print(f"\nZodiac folios:")
for folio, words in sorted(z_by_folio.items()):
    unique = len(set(words))
    print(f"  {folio}: {len(words)} tokens, {unique} types")

# Look for 12-element patterns (zodiac signs?)
# Check if any set of 12 labels appears consistently
print(f"\nLooking for potential zodiac markers...")
# Count labels that appear exactly once per folio
once_per_folio = []
for word in z_words:
    folios_with_word = [f for f, words in z_by_folio.items() if word in words]
    counts_per_folio = [z_by_folio[f].count(word) for f in folios_with_word]
    if all(c == 1 for c in counts_per_folio) and len(folios_with_word) >= 3:
        once_per_folio.append((word, len(folios_with_word)))

if once_per_folio:
    print(f"Labels appearing exactly once per folio in 3+ folios:")
    for word, count in sorted(once_per_folio, key=lambda x: -x[1])[:10]:
        print(f"  '{word}': in {count} folios")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("STRUCTURAL SUMMARY")
print("=" * 70)

summary = {
    'total_labels': len(azc_only),
    'total_tokens': len(azc_only_tokens),
    'multi_folio_labels': len(multi_folio),
    'very_short_labels': len(very_short),
    'internal_repetition': len(internal_rep),
    'folios_with_repetition': len(folio_repetitions),
    'top_prefixes': prefix_dist.most_common(5),
    'top_suffixes': suffix_dist.most_common(5),
}

print(f"""
Key Findings:
- Labels with standard morphology: {len([d for d in decompositions if d['prefix'] and d['suffix']])} / {len(azc_only)}
- Labels appearing in multiple folios: {len(multi_folio)} (potential standard terms)
- Folios with internal repetition: {len(folio_repetitions)}
- Very short labels (1-2 chars): {len(very_short)}
- Labels with doubled chars: {len(internal_rep)}
""")

# Save results
with open('phases/AZC_astronomical_zodiac_cosmological/azc_label_structure.json', 'w') as f:
    json.dump({
        'summary': summary,
        'multi_folio_labels': {w: list(f) for w, f in multi_folio.items()},
        'very_short': very_short,
        'section_distribution': {s: len(set(w)) for s, w in by_section.items()},
    }, f, indent=2)

print("\nResults saved to: phases/AZC_astronomical_zodiac_cosmological/azc_label_structure.json")
print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
