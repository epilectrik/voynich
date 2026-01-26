"""
UNIQUE MIDDLE STRUCTURE

What do the 858 unique MIDDLEs (appearing in only 1 folio) look like?
Is there structure to them?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np

tx = Transcript()
morph = Morphology()

# Build per-folio MIDDLE data
folio_middles = defaultdict(Counter)
all_middles = Counter()

for token in tx.currier_b():
    folio = token.folio
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            folio_middles[folio][m.middle] += 1
            all_middles[m.middle] += 1

# Count folio appearances
middle_folio_count = defaultdict(int)
middle_to_folio = defaultdict(set)
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1
        middle_to_folio[m].add(folio)

# Get unique MIDDLEs (appear in exactly 1 folio)
unique_middles = [(m, list(middle_to_folio[m])[0])
                  for m, count in middle_folio_count.items() if count == 1]

print(f"{'='*70}")
print(f"UNIQUE MIDDLE ANALYSIS")
print(f"{'='*70}")
print(f"\nTotal unique MIDDLEs: {len(unique_middles)}")

# Length distribution
unique_lengths = [len(m) for m, f in unique_middles]
core_middles = [m for m, count in middle_folio_count.items() if count >= 41]
core_lengths = [len(m) for m in core_middles]

print(f"\n--- LENGTH DISTRIBUTION ---")
print(f"Unique MIDDLEs: mean={np.mean(unique_lengths):.1f}, range={min(unique_lengths)}-{max(unique_lengths)}")
print(f"Core MIDDLEs: mean={np.mean(core_lengths):.1f}, range={min(core_lengths)}-{max(core_lengths)}")

# Unique MIDDLEs are LONGER
print(f"\n=> Unique MIDDLEs are {np.mean(unique_lengths)/np.mean(core_lengths):.2f}x longer than core")

# Character composition
def char_freq(middles):
    chars = Counter()
    for m in middles:
        for c in m:
            chars[c] += 1
    total = sum(chars.values())
    return {c: count/total for c, count in chars.items()}

unique_chars = char_freq([m for m, f in unique_middles])
core_chars = char_freq(core_middles)

print(f"\n--- CHARACTER COMPOSITION ---")
print(f"{'Char':<6} {'Unique %':<12} {'Core %':<12} {'Ratio':<10}")
all_chars = set(unique_chars.keys()) | set(core_chars.keys())
for c in sorted(all_chars, key=lambda x: unique_chars.get(x, 0), reverse=True):
    u = unique_chars.get(c, 0) * 100
    co = core_chars.get(c, 0) * 100
    ratio = u / co if co > 0 else float('inf')
    print(f"{c!r:<6} {u:>8.1f}%    {co:>8.1f}%    {ratio:>8.2f}x")

# Kernel character content
print(f"\n--- KERNEL CHARACTER CONTENT ---")
unique_with_k = sum(1 for m, f in unique_middles if 'k' in m)
unique_with_h = sum(1 for m, f in unique_middles if 'h' in m)
unique_with_e = sum(1 for m, f in unique_middles if 'e' in m)

core_with_k = sum(1 for m in core_middles if 'k' in m)
core_with_h = sum(1 for m in core_middles if 'h' in m)
core_with_e = sum(1 for m in core_middles if 'e' in m)

print(f"  Contains 'k': Unique={100*unique_with_k/len(unique_middles):.1f}%, Core={100*core_with_k/len(core_middles):.1f}%")
print(f"  Contains 'h': Unique={100*unique_with_h/len(unique_middles):.1f}%, Core={100*core_with_h/len(core_middles):.1f}%")
print(f"  Contains 'e': Unique={100*unique_with_e/len(unique_middles):.1f}%, Core={100*core_with_e/len(core_middles):.1f}%")

# Sample unique MIDDLEs
print(f"\n--- SAMPLE UNIQUE MIDDLEs (by length) ---")

# Group by length
by_length = defaultdict(list)
for m, f in unique_middles:
    by_length[len(m)].append((m, f))

for length in sorted(by_length.keys())[:8]:
    samples = by_length[length][:5]
    print(f"\nLength {length}: {len(by_length[length])} total")
    for m, f in samples:
        print(f"  '{m}' in {f}")

# Are unique MIDDLEs extensions of core MIDDLEs?
print(f"\n{'='*70}")
print("UNIQUE MIDDLEs AS EXTENSIONS")
print(f"{'='*70}")

# Check if unique MIDDLEs contain core MIDDLEs as substrings
core_set = set(core_middles)
extensions = 0
for m, f in unique_middles:
    for core in core_set:
        if core in m and core != m:
            extensions += 1
            break

print(f"\nUnique MIDDLEs containing a core MIDDLE: {extensions}/{len(unique_middles)} ({100*extensions/len(unique_middles):.1f}%)")

# Examples of extensions
print(f"\nExamples of unique MIDDLEs that extend core MIDDLEs:")
count = 0
for m, f in unique_middles:
    for core in sorted(core_set, key=len, reverse=True):
        if core in m and core != m and len(core) >= 2:
            print(f"  '{m}' contains '{core}' (folio {f})")
            count += 1
            break
    if count >= 10:
        break

# Unique vs Core structure summary
print(f"\n{'='*70}")
print("INTERPRETATION")
print(f"{'='*70}")

print(f"""
UNIQUE MIDDLEs (858 types, appearing in only 1 folio):

1. LONGER than core MIDDLEs:
   - Unique: {np.mean(unique_lengths):.1f} chars average
   - Core: {np.mean(core_lengths):.1f} chars average
   - Ratio: {np.mean(unique_lengths)/np.mean(core_lengths):.2f}x longer

2. LESS kernel content:
   - Unique with 'e': {100*unique_with_e/len(unique_middles):.0f}%
   - Core with 'e': {100*core_with_e/len(core_middles):.0f}%

3. Many are EXTENSIONS of core MIDDLEs:
   - {100*extensions/len(unique_middles):.0f}% contain a core MIDDLE as substring

SPECULATION:
- Core MIDDLEs = universal apparatus states (kernel, basic operations)
- Unique MIDDLEs = core + folio-specific elaboration

Example: Core 'ed' -> Unique 'oked', 'edal', 'kched' etc.

The unique MIDDLEs appear to be:
- Compound patterns built on core vocabulary
- Folio-specific "flavors" of common situations
- Rare edge cases that combine multiple control elements
""")
