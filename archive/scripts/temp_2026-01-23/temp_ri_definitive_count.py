#!/usr/bin/env python3
"""
DEFINITIVE RI MIDDLE COUNT TEST

Goal: Establish the TRUE count of unique RI MIDDLEs in Currier A with
fully documented, verifiable methodology.

Key questions to answer:
1. What counts as a MIDDLE?
2. Is PREFIX optional or required?
3. How do we handle SUFFIX?
4. What makes something A-exclusive (RI)?

Validation checks:
- PREFIX presence should match C509.a (~58.5% for RI, ~85.4% for PP)
- Results should be reproducible and transparent
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('.')

# ============================================================
# STEP 1: DEFINE THE MORPHOLOGICAL COMPONENTS
# ============================================================

# From C235 and prepare_middle_classes.py - the recognized PREFIX set
# These are the structural markers that can precede a MIDDLE
CORE_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

EXTENDED_PREFIXES = [
    # Compound ch-forms
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
    # Compound k-forms
    'lk', 'yk',
    # Compound sh-forms
    'lsh',
    # Gallows + vowel (common patterns)
    'ke', 'te', 'se', 'de', 'pe',
    'ko', 'to', 'so', 'do', 'po',
    'ka', 'ta', 'sa',
    # Bench forms
    'al', 'ar', 'or',
]

ALL_PREFIXES = sorted(set(CORE_PREFIXES + EXTENDED_PREFIXES), key=len, reverse=True)

# Suffixes - from the original script, simplified and deduplicated
# These are the grammatical endings that follow MIDDLEs
SUFFIXES = [
    # Long compound suffixes
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'tedy', 'kedy',
    'cheey', 'sheey', 'chey', 'shey',
    'chol', 'shol', 'chor', 'shor',
    'eedy', 'edy', 'eey',
    # Medium suffixes
    'iin', 'ain', 'oin', 'ein',
    'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'in', 'an', 'on', 'en',
    # Short suffixes (single char) - be careful with these
    'y', 'l', 'r', 'm', 'n', 's',
]
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

print("="*70)
print("DEFINITIVE RI MIDDLE COUNT TEST")
print("="*70)
print(f"\nMorphological inventory:")
print(f"  Core PREFIXES: {len(CORE_PREFIXES)} - {CORE_PREFIXES}")
print(f"  Extended PREFIXES: {len(EXTENDED_PREFIXES)}")
print(f"  Total PREFIXES: {len(ALL_PREFIXES)}")
print(f"  SUFFIXES: {len(SUFFIXES)}")

# ============================================================
# STEP 2: DEFINE EXTRACTION FUNCTIONS
# ============================================================

def extract_components(token):
    """
    Extract (prefix, middle, suffix) from a token.

    Rules:
    - PREFIX is OPTIONAL (try to match, but don't require)
    - SUFFIX is stripped if present (to get MIDDLE core)
    - MIDDLE is what remains after stripping both

    Returns: dict with all components and metadata
    """
    if not token or len(token) == 0:
        return None

    original = token
    working = token
    prefix = None
    suffix = None

    # Try to strip PREFIX (optional - longest match first)
    for p in ALL_PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            prefix = p
            working = working[len(p):]
            break

    # Try to strip SUFFIX (longest match first, must leave something)
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            suffix = s
            working = working[:-len(s)]
            break

    middle = working if len(working) > 0 else None

    if middle is None:
        return None

    return {
        'original': original,
        'prefix': prefix,
        'middle': middle,
        'suffix': suffix,
        'had_prefix': prefix is not None,
        'had_suffix': suffix is not None,
        'middle_len': len(middle),
    }

# ============================================================
# STEP 3: LOAD AND PROCESS ALL TOKENS
# ============================================================

print("\n" + "="*70)
print("LOADING TRANSCRIPT DATA")
print("="*70)

a_tokens = []  # All parsed A tokens
b_tokens = []  # All parsed B tokens
skipped = {'no_middle': 0, 'asterisk': 0, 'bracket': 0, 'empty': 0}

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        # H-track only
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue

        word = row.get('word', '').strip()
        language = row.get('language', '').strip()
        folio = row.get('folio', '').strip()
        line = row.get('line_number', '').strip()

        # Skip invalid tokens
        if not word:
            skipped['empty'] += 1
            continue
        if '*' in word:
            skipped['asterisk'] += 1
            continue
        if word.startswith('[') or word.startswith('<'):
            skipped['bracket'] += 1
            continue

        # Parse the token
        parsed = extract_components(word)
        if parsed is None:
            skipped['no_middle'] += 1
            continue

        parsed['folio'] = folio
        parsed['line'] = line
        parsed['language'] = language

        if language == 'A':
            a_tokens.append(parsed)
        elif language == 'B':
            b_tokens.append(parsed)

print(f"\nTokens loaded:")
print(f"  Currier A: {len(a_tokens):,}")
print(f"  Currier B: {len(b_tokens):,}")
print(f"  Skipped: {skipped}")

# ============================================================
# STEP 4: COMPUTE UNIQUE MIDDLES AND CLASSIFY
# ============================================================

print("\n" + "="*70)
print("COMPUTING UNIQUE MIDDLES")
print("="*70)

# Get unique MIDDLEs per language
a_middles = set(t['middle'] for t in a_tokens)
b_middles = set(t['middle'] for t in b_tokens)

# Classify
ri_middles = a_middles - b_middles  # A-exclusive
pp_middles = a_middles & b_middles  # Shared A&B

print(f"\nUnique MIDDLE cores:")
print(f"  Total A MIDDLEs: {len(a_middles)}")
print(f"  Total B MIDDLEs: {len(b_middles)}")
print(f"  RI (A-exclusive): {len(ri_middles)}")
print(f"  PP (shared A&B): {len(pp_middles)}")
print(f"  RI percentage: {100*len(ri_middles)/len(a_middles):.1f}%")

# ============================================================
# STEP 5: VALIDATE AGAINST C509.a (PREFIX RATES)
# ============================================================

print("\n" + "="*70)
print("VALIDATION: PREFIX PRESENCE (should match C509.a)")
print("="*70)
print("C509.a says: RI ~58.5% PREFIX, PP ~85.4% PREFIX")

# Get tokens by MIDDLE class
ri_tokens = [t for t in a_tokens if t['middle'] in ri_middles]
pp_tokens = [t for t in a_tokens if t['middle'] in pp_middles]

ri_with_prefix = sum(1 for t in ri_tokens if t['had_prefix'])
pp_with_prefix = sum(1 for t in pp_tokens if t['had_prefix'])

ri_prefix_rate = 100 * ri_with_prefix / len(ri_tokens) if ri_tokens else 0
pp_prefix_rate = 100 * pp_with_prefix / len(pp_tokens) if pp_tokens else 0

print(f"\nObserved PREFIX rates:")
print(f"  RI: {ri_prefix_rate:.1f}% (C509.a: 58.5%) - {'MATCH' if abs(ri_prefix_rate - 58.5) < 10 else 'MISMATCH'}")
print(f"  PP: {pp_prefix_rate:.1f}% (C509.a: 85.4%) - {'MATCH' if abs(pp_prefix_rate - 85.4) < 10 else 'MISMATCH'}")

# ============================================================
# STEP 6: VALIDATE AGAINST C509.a (MIDDLE LENGTH)
# ============================================================

print("\n" + "="*70)
print("VALIDATION: MIDDLE LENGTH (should match C509.a)")
print("="*70)
print("C509.a says: RI mean 3.96 chars, PP mean 1.46 chars")

ri_middle_lengths = [len(m) for m in ri_middles]
pp_middle_lengths = [len(m) for m in pp_middles]

ri_mean_len = sum(ri_middle_lengths) / len(ri_middle_lengths) if ri_middle_lengths else 0
pp_mean_len = sum(pp_middle_lengths) / len(pp_middle_lengths) if pp_middle_lengths else 0

print(f"\nObserved MIDDLE lengths (type-level):")
print(f"  RI mean: {ri_mean_len:.2f} chars (C509.a: 3.96) - {'MATCH' if abs(ri_mean_len - 3.96) < 1 else 'MISMATCH'}")
print(f"  PP mean: {pp_mean_len:.2f} chars (C509.a: 1.46) - {'MATCH' if abs(pp_mean_len - 1.46) < 1 else 'MISMATCH'}")

# ============================================================
# STEP 7: LENGTH DISTRIBUTION ANALYSIS
# ============================================================

print("\n" + "="*70)
print("MIDDLE LENGTH DISTRIBUTION")
print("="*70)

ri_len_dist = Counter(len(m) for m in ri_middles)
pp_len_dist = Counter(len(m) for m in pp_middles)

print("\nRI MIDDLE length distribution:")
for length in sorted(ri_len_dist.keys()):
    count = ri_len_dist[length]
    pct = 100 * count / len(ri_middles)
    bar = '#' * int(pct / 2)
    print(f"  len={length}: {count:4d} ({pct:5.1f}%) {bar}")

print("\nPP MIDDLE length distribution:")
for length in sorted(pp_len_dist.keys()):
    count = pp_len_dist[length]
    pct = 100 * count / len(pp_middles)
    bar = '#' * int(pct / 2)
    print(f"  len={length}: {count:4d} ({pct:5.1f}%) {bar}")

# ============================================================
# STEP 8: CHECK FOR SUSPICIOUS PATTERNS
# ============================================================

print("\n" + "="*70)
print("SANITY CHECKS")
print("="*70)

# Check for 1-char MIDDLEs (might be extraction artifacts)
ri_1char = [m for m in ri_middles if len(m) == 1]
pp_1char = [m for m in pp_middles if len(m) == 1]

print(f"\n1-character MIDDLEs (potential artifacts):")
print(f"  RI: {len(ri_1char)} - {sorted(ri_1char)}")
print(f"  PP: {len(pp_1char)} - {sorted(pp_1char)}")

# Check for very long MIDDLEs (might be unstripped tokens)
ri_long = [m for m in ri_middles if len(m) >= 8]
pp_long = [m for m in pp_middles if len(m) >= 8]

print(f"\n8+ character MIDDLEs (check for unstripped tokens):")
print(f"  RI: {len(ri_long)} examples: {sorted(ri_long)[:10]}")
print(f"  PP: {len(pp_long)} examples: {sorted(pp_long)[:10]}")

# ============================================================
# STEP 9: SUFFIX PRESENCE ANALYSIS
# ============================================================

print("\n" + "="*70)
print("SUFFIX PRESENCE ANALYSIS")
print("="*70)
print("C498 says RI is 'suffix-less 3x enriched'")

ri_with_suffix = sum(1 for t in ri_tokens if t['had_suffix'])
pp_with_suffix = sum(1 for t in pp_tokens if t['had_suffix'])

ri_suffix_rate = 100 * ri_with_suffix / len(ri_tokens) if ri_tokens else 0
pp_suffix_rate = 100 * pp_with_suffix / len(pp_tokens) if pp_tokens else 0

print(f"\nSUFFIX presence (token-level):")
print(f"  RI: {ri_suffix_rate:.1f}% have suffix")
print(f"  PP: {pp_suffix_rate:.1f}% have suffix")
print(f"  PP/RI ratio: {pp_suffix_rate/ri_suffix_rate:.1f}x" if ri_suffix_rate > 0 else "  (RI has 0%)")

# ============================================================
# STEP 10: FOLIO LOCALIZATION CHECK
# ============================================================

print("\n" + "="*70)
print("FOLIO LOCALIZATION (C498: RI is folio-localized)")
print("="*70)

# Count folios per MIDDLE
ri_folio_counts = defaultdict(set)
pp_folio_counts = defaultdict(set)

for t in a_tokens:
    if t['middle'] in ri_middles:
        ri_folio_counts[t['middle']].add(t['folio'])
    else:
        pp_folio_counts[t['middle']].add(t['folio'])

ri_avg_folios = sum(len(f) for f in ri_folio_counts.values()) / len(ri_folio_counts) if ri_folio_counts else 0
pp_avg_folios = sum(len(f) for f in pp_folio_counts.values()) / len(pp_folio_counts) if pp_folio_counts else 0

print(f"\nAverage folios per MIDDLE:")
print(f"  RI: {ri_avg_folios:.2f} folios (C498 says 1.34)")
print(f"  PP: {pp_avg_folios:.2f} folios (C498 says 7.96)")

ri_single_folio = sum(1 for f in ri_folio_counts.values() if len(f) == 1)
pp_single_folio = sum(1 for f in pp_folio_counts.values() if len(f) == 1)

print(f"\nSingle-folio MIDDLEs:")
print(f"  RI: {ri_single_folio}/{len(ri_middles)} ({100*ri_single_folio/len(ri_middles):.1f}%)")
print(f"  PP: {pp_single_folio}/{len(pp_middles)} ({100*pp_single_folio/len(pp_middles):.1f}%)")

# ============================================================
# STEP 11: FINAL SUMMARY
# ============================================================

print("\n" + "="*70)
print("DEFINITIVE RESULTS")
print("="*70)

print(f"""
METHODOLOGY:
  - PREFIX: Optional (try to strip, but include tokens without)
  - SUFFIX: Stripped to get MIDDLE core
  - RI definition: A-exclusive (appears in A, never in B)
  - PP definition: Shared between A and B

COUNTS:
  - Total A MIDDLEs: {len(a_middles)}
  - RI MIDDLEs: {len(ri_middles)} ({100*len(ri_middles)/len(a_middles):.1f}% of A)
  - PP MIDDLEs: {len(pp_middles)} ({100*len(pp_middles)/len(a_middles):.1f}% of A)

VALIDATION AGAINST C509.a:
  - RI PREFIX rate: {ri_prefix_rate:.1f}% (expected ~58.5%) {'OK' if abs(ri_prefix_rate - 58.5) < 10 else 'CHECK'}
  - PP PREFIX rate: {pp_prefix_rate:.1f}% (expected ~85.4%) {'OK' if abs(pp_prefix_rate - 85.4) < 10 else 'CHECK'}
  - RI MIDDLE length: {ri_mean_len:.2f} chars (expected ~3.96) {'OK' if abs(ri_mean_len - 3.96) < 1 else 'CHECK'}
  - PP MIDDLE length: {pp_mean_len:.2f} chars (expected ~1.46) {'OK' if abs(pp_mean_len - 1.46) < 1 else 'CHECK'}

COMPARISON WITH OLD CONSTRAINTS:
  - Old C498 said: 349 RI MIDDLEs
  - We found: {len(ri_middles)} RI MIDDLEs
  - Difference: {len(ri_middles) - 349:+d} ({100*(len(ri_middles)-349)/349:+.1f}%)
""")

# ============================================================
# STEP 12: SAVE RESULTS
# ============================================================

output = {
    'methodology': {
        'prefix_handling': 'optional (stripped if present)',
        'suffix_handling': 'stripped to get MIDDLE core',
        'ri_definition': 'A-exclusive (in A, not in B)',
        'pp_definition': 'shared between A and B',
        'prefix_list_size': len(ALL_PREFIXES),
        'suffix_list_size': len(SUFFIXES),
    },
    'counts': {
        'total_a_middles': len(a_middles),
        'total_b_middles': len(b_middles),
        'ri_middles': len(ri_middles),
        'pp_middles': len(pp_middles),
    },
    'validation': {
        'ri_prefix_rate': round(ri_prefix_rate, 1),
        'pp_prefix_rate': round(pp_prefix_rate, 1),
        'ri_mean_length': round(ri_mean_len, 2),
        'pp_mean_length': round(pp_mean_len, 2),
        'ri_avg_folios': round(ri_avg_folios, 2),
        'pp_avg_folios': round(pp_avg_folios, 2),
    },
    'ri_middles': sorted(ri_middles),
    'pp_middles': sorted(pp_middles),
}

with open(PROJECT_ROOT / 'temp_ri_definitive_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Results saved to temp_ri_definitive_results.json")
