#!/usr/bin/env python3
"""Analyze how RI fits with the PP procedural compatibility model."""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token or not isinstance(token, str):
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

# Load PP/RI classification
with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])
ri_middles = set(data['a_exclusive_middles'])

print("="*70)
print("PP vs RI: BASIC COMPARISON")
print("="*70)
print(f"\nPP MIDDLEs (shared A+B): {len(pp_middles)}")
print(f"RI MIDDLEs (A-only): {len(ri_middles)}")

# Check length distribution
pp_lengths = [len(m) for m in pp_middles]
ri_lengths = [len(m) for m in ri_middles]

import statistics
print(f"\nMIDDLE length:")
print(f"  PP: mean={statistics.mean(pp_lengths):.2f}, median={statistics.median(pp_lengths)}")
print(f"  RI: mean={statistics.mean(ri_lengths):.2f}, median={statistics.median(ri_lengths)}")

# Check if RI MIDDLEs contain PP atoms
print("\n" + "="*70)
print("DO RI MIDDLEs CONTAIN PP ATOMS?")
print("="*70)

ri_contains_pp = 0
ri_pp_atoms_found = Counter()

for ri in ri_middles:
    found_pp = False
    for pp in pp_middles:
        if pp in ri and len(pp) >= 2:  # PP atom is substring of RI
            ri_pp_atoms_found[pp] += 1
            found_pp = True
    if found_pp:
        ri_contains_pp += 1

print(f"\nRI MIDDLEs containing at least one PP atom: {ri_contains_pp}/{len(ri_middles)} ({100*ri_contains_pp/len(ri_middles):.1f}%)")

print(f"\nMost common PP atoms found in RI MIDDLEs:")
for pp, count in ri_pp_atoms_found.most_common(15):
    print(f"  {pp}: found in {count} RI MIDDLEs")

# Check 'e' and 'ol' specifically
print("\n" + "="*70)
print("'e' AND 'ol' IN RI MIDDLEs")
print("="*70)

ri_with_e = [ri for ri in ri_middles if 'e' in ri]
ri_with_ol = [ri for ri in ri_middles if 'ol' in ri]

print(f"\nRI MIDDLEs containing 'e': {len(ri_with_e)} ({100*len(ri_with_e)/len(ri_middles):.1f}%)")
print(f"RI MIDDLEs containing 'ol': {len(ri_with_ol)} ({100*len(ri_with_ol)/len(ri_middles):.1f}%)")

print(f"\nExamples of RI with 'e': {sorted(ri_with_e)[:10]}")
print(f"Examples of RI with 'ol': {sorted(ri_with_ol)[:10]}")

# Key question: Does RI ADD discrimination ON TOP OF PP compatibility?
print("\n" + "="*70)
print("RI AS ELABORATION OF PP")
print("="*70)

# Check if RI = PP + something
ri_as_pp_plus = 0
examples = []

for ri in ri_middles:
    for pp in sorted(pp_middles, key=len, reverse=True):  # Check longest first
        if ri.startswith(pp) and len(ri) > len(pp):
            ri_as_pp_plus += 1
            examples.append((ri, pp, ri[len(pp):]))
            break
        elif ri.endswith(pp) and len(ri) > len(pp):
            ri_as_pp_plus += 1
            examples.append((ri, pp, ri[:-len(pp)]))
            break

print(f"\nRI MIDDLEs that are PP + extension: {ri_as_pp_plus}/{len(ri_middles)} ({100*ri_as_pp_plus/len(ri_middles):.1f}%)")

print(f"\nExamples (RI = PP + extension):")
for ri, pp, ext in examples[:15]:
    print(f"  {ri} = {pp} + '{ext}'")

# The key insight: What does RI ADD?
print("\n" + "="*70)
print("WHAT DOES RI ADD TO PP?")
print("="*70)

# Count the extensions
extensions = Counter(ext for _, _, ext in examples)
print(f"\nMost common RI extensions (what RI adds to PP):")
for ext, count in extensions.most_common(15):
    print(f"  '{ext}': {count}")

# Check if specific extensions correlate with specific PP bases
print(f"\nExtensions by PP base:")
pp_extensions = defaultdict(list)
for ri, pp, ext in examples:
    pp_extensions[pp].append(ext)

for pp in ['e', 'ol', 'or', 'ch', 'ar']:
    if pp in pp_extensions:
        ext_counts = Counter(pp_extensions[pp])
        print(f"\n  PP '{pp}' + extensions:")
        for ext, count in ext_counts.most_common(5):
            print(f"    + '{ext}': {count} -> {pp}{ext}")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print("""
If PP = procedural compatibility (what you can DO):
  - 'e' = standard procedural compatibility
  - 'ol' = precision handling required

Then RI = PP + discriminator:
  - RI elaborates on PP to specify WHICH material
  - The PP atom tells you the procedural class
  - The extension tells you the specific identity

Example:
  PP 'ol' = "needs precision handling"
  RI 'olar' = 'ol' + 'ar' = "needs precision handling" + "specific type ar"
  RI 'olch' = 'ol' + 'ch' = "needs precision handling" + "specific type ch"

This means:
  - PP answers: "What PROCEDURES is this compatible with?"
  - RI answers: "WHICH specific material (within that procedural class)?"
""")
