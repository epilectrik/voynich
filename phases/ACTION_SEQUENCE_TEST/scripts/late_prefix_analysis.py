"""
LATE PREFIX MORPHOLOGY ANALYSIS

The LATE prefixes (al, ar, or) are 100% "OTHER" in CCM classification.
They don't fit major prefix families (ch-, sh-, qo-, ok-, da-, ol-, ct-).

Questions:
1. What tokens have these prefixes?
2. What MIDDLEs do they combine with?
3. What SUFFIXes do they combine with?
4. Are they structurally different from other prefixes?
5. Do they correlate with any specific context?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
import json

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("LATE PREFIX MORPHOLOGY ANALYSIS: al, ar, or")
print("=" * 70)

# =============================================================================
# STEP 1: Collect all tokens with LATE prefixes
# =============================================================================
print("\n[Step 1] Collecting tokens with LATE prefixes...")

LATE_PREFIXES = {'al', 'ar', 'or'}

late_tokens = []
all_b_tokens = []

for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        entry = {
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        }
        all_b_tokens.append(entry)
        if entry['prefix'] in LATE_PREFIXES:
            late_tokens.append(entry)

print(f"  Total B tokens: {len(all_b_tokens)}")
print(f"  LATE prefix tokens: {len(late_tokens)} ({len(late_tokens)/len(all_b_tokens)*100:.2f}%)")

# =============================================================================
# STEP 2: Token inventory by LATE prefix
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Token inventory by LATE prefix")
print("=" * 70)

for prefix in sorted(LATE_PREFIXES):
    tokens_with_prefix = [t for t in late_tokens if t['prefix'] == prefix]
    print(f"\n  PREFIX '{prefix}' ({len(tokens_with_prefix)} tokens):")

    # Unique words
    words = Counter(t['word'] for t in tokens_with_prefix)
    print(f"    Unique words: {len(words)}")
    print(f"    Top 10 words:")
    for word, count in words.most_common(10):
        print(f"      {word}: {count}")

# =============================================================================
# STEP 3: MIDDLE combinations
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: MIDDLE combinations with LATE prefixes")
print("=" * 70)

# Get all MIDDLEs used with LATE prefixes
late_middles = Counter(t['middle'] for t in late_tokens if t['middle'])

# Get all MIDDLEs in B corpus
all_middles = Counter(t['middle'] for t in all_b_tokens if t['middle'])

print(f"\n  Unique MIDDLEs with LATE prefixes: {len(late_middles)}")
print(f"  Total unique MIDDLEs in B: {len(all_middles)}")

print("\n  MIDDLEs used with LATE prefixes (sorted by frequency):")
for middle, count in late_middles.most_common(20):
    # Compare to baseline
    baseline = all_middles.get(middle, 0)
    enrichment = (count / len(late_tokens)) / (baseline / len(all_b_tokens)) if baseline else float('inf')
    print(f"    {middle}: {count} (enrichment: {enrichment:.2f}x)")

# =============================================================================
# STEP 4: SUFFIX combinations
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: SUFFIX combinations with LATE prefixes")
print("=" * 70)

# Get SUFFIXes by LATE prefix
for prefix in sorted(LATE_PREFIXES):
    tokens_with_prefix = [t for t in late_tokens if t['prefix'] == prefix]
    suffixes = Counter(t['suffix'] for t in tokens_with_prefix)
    print(f"\n  PREFIX '{prefix}' SUFFIX distribution:")
    total = len(tokens_with_prefix)
    for suffix, count in suffixes.most_common():
        pct = count / total * 100
        print(f"    '{suffix or '(none)'}': {count} ({pct:.1f}%)")

# Compare to overall SUFFIX distribution
print("\n  Overall B SUFFIX distribution (for comparison):")
all_suffixes = Counter(t['suffix'] for t in all_b_tokens)
total_b = len(all_b_tokens)
for suffix, count in all_suffixes.most_common(10):
    pct = count / total_b * 100
    print(f"    '{suffix or '(none)'}': {count} ({pct:.1f}%)")

# =============================================================================
# STEP 5: Morphological structure analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: Morphological structure analysis")
print("=" * 70)

# What's special about al, ar, or?
# They all end in a vowel-like pattern: a+l, a+r, o+r

print("\n  Structural analysis of LATE prefixes:")
print("    al = a + l (vowel + liquid)")
print("    ar = a + r (vowel + liquid)")
print("    or = o + r (vowel + liquid)")
print("\n  Pattern: [VOWEL] + [LIQUID CONSONANT]")

# Check if there are other V+L prefixes
all_prefixes = set(t['prefix'] for t in all_b_tokens if t['prefix'])
vl_pattern_prefixes = [p for p in all_prefixes if len(p) == 2 and p[0] in 'aeioy' and p[1] in 'lr']
print(f"\n  All V+L pattern prefixes in B: {sorted(vl_pattern_prefixes)}")

# Check position of each
print("\n  Position analysis for V+L prefixes:")
folio_line_tokens = defaultdict(list)
for tok in all_b_tokens:
    key = (tok['folio'], tok['line'])
    folio_line_tokens[key].append(tok)

for prefix in sorted(vl_pattern_prefixes):
    positions = []
    for key, tokens in folio_line_tokens.items():
        n = len(tokens)
        if n < 2:
            continue
        for i, tok in enumerate(tokens):
            if tok['prefix'] == prefix:
                positions.append(i / (n - 1))
    if positions:
        mean_pos = np.mean(positions)
        print(f"    {prefix}: mean position {mean_pos:.3f} (n={len(positions)})")

# =============================================================================
# STEP 6: Compare to ENERGY_OPERATOR prefixes
# =============================================================================
print("\n" + "=" * 70)
print("STEP 6: Structural comparison to ENERGY_OPERATOR prefixes")
print("=" * 70)

ENERGY_PREFIXES = {'ch', 'sh', 'qo', 'tch', 'pch', 'dch', 'lsh'}

print("\n  ENERGY_OPERATOR prefix structure:")
for p in sorted(ENERGY_PREFIXES):
    print(f"    {p}")

print("\n  LATE prefix structure:")
for p in sorted(LATE_PREFIXES):
    print(f"    {p}")

print("""
  Structural difference:
  - ENERGY: Consonant-initial (ch, sh, qo) or Consonant+ch compound (tch, pch, dch)
  - LATE: Vowel-initial with liquid ending (al, ar, or)

  This is a FUNDAMENTAL morphological distinction:
  - ENERGY prefixes are consonantal (onset-heavy)
  - LATE prefixes are vocalic (nucleus-heavy)
""")

# =============================================================================
# STEP 7: Context analysis - what comes before/after LATE tokens?
# =============================================================================
print("\n" + "=" * 70)
print("STEP 7: Context analysis - adjacent tokens")
print("=" * 70)

# Build line sequences
line_sequences = defaultdict(list)
for tok in all_b_tokens:
    key = (tok['folio'], tok['line'])
    line_sequences[key].append(tok)

# Find what precedes and follows LATE tokens
preceding_prefixes = Counter()
following_prefixes = Counter()

for key, tokens in line_sequences.items():
    for i, tok in enumerate(tokens):
        if tok['prefix'] in LATE_PREFIXES:
            if i > 0:
                preceding_prefixes[tokens[i-1]['prefix'] or '(none)'] += 1
            if i < len(tokens) - 1:
                following_prefixes[tokens[i+1]['prefix'] or '(none)'] += 1

print("\n  Prefixes PRECEDING LATE tokens:")
total_prec = sum(preceding_prefixes.values())
for prefix, count in preceding_prefixes.most_common(10):
    pct = count / total_prec * 100
    print(f"    {prefix}: {count} ({pct:.1f}%)")

print("\n  Prefixes FOLLOWING LATE tokens:")
total_foll = sum(following_prefixes.values())
for prefix, count in following_prefixes.most_common(10):
    pct = count / total_foll * 100
    print(f"    {prefix}: {count} ({pct:.1f}%)")

# =============================================================================
# STEP 8: Line-final analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 8: Line-final position analysis")
print("=" * 70)

# How often are LATE tokens at actual line end?
late_at_end = 0
late_total = 0

for key, tokens in line_sequences.items():
    for i, tok in enumerate(tokens):
        if tok['prefix'] in LATE_PREFIXES:
            late_total += 1
            if i == len(tokens) - 1:
                late_at_end += 1

print(f"\n  LATE tokens at absolute line end: {late_at_end}/{late_total} ({late_at_end/late_total*100:.1f}%)")

# Compare to baseline
any_at_end = 0
any_total = 0
for key, tokens in line_sequences.items():
    for i, tok in enumerate(tokens):
        any_total += 1
        if i == len(tokens) - 1:
            any_at_end += 1

baseline_end_rate = any_at_end / any_total * 100
print(f"  Baseline (any token at line end): {baseline_end_rate:.1f}%")
print(f"  LATE enrichment at line-end: {(late_at_end/late_total*100)/baseline_end_rate:.2f}x")

# =============================================================================
# STEP 9: Folio distribution
# =============================================================================
print("\n" + "=" * 70)
print("STEP 9: Folio distribution of LATE prefixes")
print("=" * 70)

folio_late_counts = Counter(t['folio'] for t in late_tokens)
folio_total_counts = Counter(t['folio'] for t in all_b_tokens)

# Compute LATE rate per folio
folio_late_rates = []
for folio in folio_total_counts:
    total = folio_total_counts[folio]
    late = folio_late_counts.get(folio, 0)
    if total >= 50:
        rate = late / total * 100
        folio_late_rates.append((folio, rate, late, total))

folio_late_rates.sort(key=lambda x: x[1], reverse=True)

print("\n  Folios with highest LATE prefix rate:")
for folio, rate, late, total in folio_late_rates[:10]:
    print(f"    {folio}: {rate:.2f}% ({late}/{total})")

print("\n  Folios with lowest LATE prefix rate:")
for folio, rate, late, total in folio_late_rates[-10:]:
    print(f"    {folio}: {rate:.2f}% ({late}/{total})")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
LATE PREFIX MORPHOLOGY FINDINGS:

1. STRUCTURAL PATTERN: [VOWEL] + [LIQUID]
   - al, ar, or all follow V+L pattern
   - This is morphologically opposite to ENERGY prefixes (consonant-initial)
   - Suggests different grammatical function, not just different meaning

2. MIDDLE COMBINATIONS:
   - Need to check if LATE prefixes have restricted MIDDLE partners
   - Or if they combine freely like other prefixes

3. SUFFIX PATTERNS:
   - Check if LATE prefixes favor certain suffixes
   - This would indicate functional specialization

4. LINE POSITION:
   - LATE prefixes cluster toward line end
   - Are they actually LINE-FINAL markers?

5. CONTEXT:
   - What precedes/follows LATE tokens?
   - Is there a predictable transition pattern?

INTERPRETATION:

If LATE prefixes are:
- Morphologically distinct (V+L vs consonantal)
- Position-restricted (line-end)
- Functionally specialized (limited MIDDLE/SUFFIX combos)

Then they may represent a SEPARATE GRAMMATICAL CLASS:
- Not "prefixes" in the same sense as ch-, sh-, qo-
- Possibly "output markers" or "completion signals"
- The V+L pattern may be phonologically motivated (easier articulation at phrase boundary)
""")
