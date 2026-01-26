#!/usr/bin/env python3
"""
Test: Does RI PREFIX bifurcation correlate with H/P/T sections?

If PREFIX-REQUIRED vs PREFIX-FORBIDDEN populations align with sections,
the interpretation shifts from "substance class" to "section-specific morphology."
"""

import csv
import json
from collections import defaultdict, Counter

# Load RI MIDDLEs
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    data = json.load(f)
ri_middles = set(data['a_exclusive_middles'])

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)

def get_section(folio):
    """Determine section (H, P, T) from folio name."""
    if not folio:
        return 'UNKNOWN'
    f = folio.lower()
    # Pharma section
    if any(f.startswith(x) for x in ['f88', 'f89', 'f90', 'f99', 'f100', 'f101', 'f102', 'f103']):
        return 'P'
    # Text section
    if any(f.startswith(x) for x in ['f103', 'f104', 'f105', 'f106', 'f107', 'f108', 'f111', 'f112', 'f113', 'f114', 'f115', 'f116']):
        return 'T'
    # Default to H for Currier A folios
    return 'H'

def extract(token):
    if not token:
        return None, False
    working = token
    had_prefix = False
    for p in PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            working = working[len(p):]
            had_prefix = True
            break
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break
    return working if working else None, had_prefix

# First pass: classify MIDDLEs into prefix-required/forbidden/optional
appears_with_prefix = set()
appears_without_prefix = set()

# Also track by section
section_prefixed_middles = defaultdict(set)    # section -> MIDDLEs seen with prefix
section_unprefixed_middles = defaultdict(set)  # section -> MIDDLEs seen without prefix
section_token_counts = defaultdict(lambda: {'prefixed': 0, 'unprefixed': 0})

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

        section = get_section(folio)
        middle, had_prefix = extract(word)

        if middle and middle in ri_middles:
            if had_prefix:
                appears_with_prefix.add(middle)
                section_prefixed_middles[section].add(middle)
                section_token_counts[section]['prefixed'] += 1
            else:
                appears_without_prefix.add(middle)
                section_unprefixed_middles[section].add(middle)
                section_token_counts[section]['unprefixed'] += 1

# Classify MIDDLEs
only_prefixed = appears_with_prefix - appears_without_prefix      # PREFIX-REQUIRED
only_unprefixed = appears_without_prefix - appears_with_prefix    # PREFIX-FORBIDDEN
both = appears_with_prefix & appears_without_prefix               # PREFIX-OPTIONAL

print("="*70)
print("RI PREFIX BIFURCATION BY SECTION")
print("="*70)

print(f"\nOverall RI PREFIX classification:")
print(f"  PREFIX-REQUIRED: {len(only_prefixed)} MIDDLEs")
print(f"  PREFIX-FORBIDDEN: {len(only_unprefixed)} MIDDLEs")
print(f"  PREFIX-OPTIONAL: {len(both)} MIDDLEs")

# For each section, what's the breakdown?
print("\n" + "="*70)
print("SECTION-LEVEL TOKEN COUNTS")
print("="*70)

for section in ['H', 'P', 'T']:
    counts = section_token_counts[section]
    total = counts['prefixed'] + counts['unprefixed']
    if total > 0:
        pct_prefixed = 100 * counts['prefixed'] / total
        print(f"\nSection {section}:")
        print(f"  RI tokens with PREFIX: {counts['prefixed']} ({pct_prefixed:.1f}%)")
        print(f"  RI tokens without PREFIX: {counts['unprefixed']} ({100-pct_prefixed:.1f}%)")
        print(f"  Total RI tokens: {total}")

# For each section, how many of each MIDDLE class appear?
print("\n" + "="*70)
print("SECTION-LEVEL MIDDLE TYPE DISTRIBUTION")
print("="*70)

for section in ['H', 'P', 'T']:
    prefixed_in_section = section_prefixed_middles[section]
    unprefixed_in_section = section_unprefixed_middles[section]

    # How many PREFIX-REQUIRED appear in this section?
    req_in_section = only_prefixed & prefixed_in_section
    # How many PREFIX-FORBIDDEN appear in this section?
    forb_in_section = only_unprefixed & unprefixed_in_section
    # How many PREFIX-OPTIONAL appear?
    opt_in_section = both & (prefixed_in_section | unprefixed_in_section)

    total_types = len(req_in_section) + len(forb_in_section) + len(opt_in_section)

    if total_types > 0:
        print(f"\nSection {section} ({total_types} unique RI MIDDLEs):")
        print(f"  PREFIX-REQUIRED types: {len(req_in_section)} ({100*len(req_in_section)/total_types:.1f}%)")
        print(f"  PREFIX-FORBIDDEN types: {len(forb_in_section)} ({100*len(forb_in_section)/total_types:.1f}%)")
        print(f"  PREFIX-OPTIONAL types: {len(opt_in_section)} ({100*len(opt_in_section)/total_types:.1f}%)")

# Check if any MIDDLE class is section-exclusive
print("\n" + "="*70)
print("SECTION EXCLUSIVITY")
print("="*70)

# Which PREFIX-REQUIRED are section-exclusive?
req_sections = defaultdict(set)
for section in ['H', 'P', 'T']:
    for m in only_prefixed & section_prefixed_middles[section]:
        req_sections[m].add(section)

req_h_only = [m for m, secs in req_sections.items() if secs == {'H'}]
req_p_only = [m for m, secs in req_sections.items() if secs == {'P'}]
req_t_only = [m for m, secs in req_sections.items() if secs == {'T'}]
req_multi = [m for m, secs in req_sections.items() if len(secs) > 1]

print(f"\nPREFIX-REQUIRED MIDDLEs ({len(only_prefixed)} total):")
print(f"  H-only: {len(req_h_only)} ({100*len(req_h_only)/len(only_prefixed):.1f}%)")
print(f"  P-only: {len(req_p_only)} ({100*len(req_p_only)/len(only_prefixed):.1f}%)")
print(f"  T-only: {len(req_t_only)} ({100*len(req_t_only)/len(only_prefixed):.1f}%)")
print(f"  Multi-section: {len(req_multi)} ({100*len(req_multi)/len(only_prefixed):.1f}%)")

# Which PREFIX-FORBIDDEN are section-exclusive?
forb_sections = defaultdict(set)
for section in ['H', 'P', 'T']:
    for m in only_unprefixed & section_unprefixed_middles[section]:
        forb_sections[m].add(section)

forb_h_only = [m for m, secs in forb_sections.items() if secs == {'H'}]
forb_p_only = [m for m, secs in forb_sections.items() if secs == {'P'}]
forb_t_only = [m for m, secs in forb_sections.items() if secs == {'T'}]
forb_multi = [m for m, secs in forb_sections.items() if len(secs) > 1]

print(f"\nPREFIX-FORBIDDEN MIDDLEs ({len(only_unprefixed)} total):")
print(f"  H-only: {len(forb_h_only)} ({100*len(forb_h_only)/len(only_unprefixed):.1f}%)")
print(f"  P-only: {len(forb_p_only)} ({100*len(forb_p_only)/len(only_unprefixed):.1f}%)")
print(f"  T-only: {len(forb_t_only)} ({100*len(forb_t_only)/len(only_unprefixed):.1f}%)")
print(f"  Multi-section: {len(forb_multi)} ({100*len(forb_multi)/len(only_unprefixed):.1f}%)")

# Summary statistics
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Compare H-only rates
if len(only_prefixed) > 0 and len(only_unprefixed) > 0:
    req_h_rate = 100 * len(req_h_only) / len(only_prefixed)
    forb_h_rate = 100 * len(forb_h_only) / len(only_unprefixed)

    print(f"""
Section H dominance:
  PREFIX-REQUIRED H-only rate: {req_h_rate:.1f}%
  PREFIX-FORBIDDEN H-only rate: {forb_h_rate:.1f}%

If these rates are SIMILAR, the bifurcation is NOT section-driven.
If one is much higher, that population may be section-specific.
""")

# Check ratio within each section
print("Per-section PREFIX rate (token-level):")
for section in ['H', 'P', 'T']:
    counts = section_token_counts[section]
    total = counts['prefixed'] + counts['unprefixed']
    if total > 0:
        rate = 100 * counts['prefixed'] / total
        print(f"  Section {section}: {rate:.1f}% prefixed")

print("""
If all sections have ~similar PREFIX rates (~50-60%),
the bifurcation is SUBSTANCE-DRIVEN, not section-driven.

If one section has very different rate (e.g., 80% or 20%),
the bifurcation may be SECTION-SPECIFIC morphology.
""")
