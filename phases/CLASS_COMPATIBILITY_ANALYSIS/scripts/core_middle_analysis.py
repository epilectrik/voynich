"""
CORE MIDDLE ANALYSIS

What are the 41 core MIDDLEs that appear in >50% of folios?
Are these the kernel/control vocabulary?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

# Build per-folio MIDDLE sets
folio_middles = defaultdict(set)
all_middles = Counter()

for token in tx.currier_b():
    folio = token.folio
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            folio_middles[folio].add(m.middle)
            all_middles[m.middle] += 1

n_folios = len(folio_middles)
print(f"B folios: {n_folios}")

# Count folio appearances
middle_folio_count = defaultdict(int)
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folio_count[m] += 1

# Core MIDDLEs (>50% of folios)
core_threshold = n_folios // 2
core_middles = [(m, count) for m, count in middle_folio_count.items() if count >= core_threshold]
core_middles.sort(key=lambda x: -x[1])

print(f"\n{'='*70}")
print(f"CORE MIDDLEs (appearing in >={core_threshold} folios)")
print(f"{'='*70}")

print(f"\n{len(core_middles)} core MIDDLEs:\n")
for m, count in core_middles:
    pct = 100 * count / n_folios
    # Check if this contains kernel chars
    has_k = 'k' in m
    has_h = 'h' in m
    has_e = 'e' in m
    kernel_note = []
    if has_k: kernel_note.append('k')
    if has_h: kernel_note.append('h')
    if has_e: kernel_note.append('e')
    kernel_str = f" [kernel: {','.join(kernel_note)}]" if kernel_note else ""
    print(f"  '{m}': {count}/{n_folios} folios ({pct:.0f}%){kernel_str}")

# Categorize core MIDDLEs
print(f"\n{'='*70}")
print("CORE MIDDLE CATEGORIES")
print(f"{'='*70}")

kernel_core = [m for m, _ in core_middles if 'k' in m or 'h' in m or 'e' in m]
non_kernel_core = [m for m, _ in core_middles if not ('k' in m or 'h' in m or 'e' in m)]

print(f"\nWith kernel chars (k/h/e): {len(kernel_core)}")
for m in kernel_core:
    print(f"  '{m}'")

print(f"\nWithout kernel chars: {len(non_kernel_core)}")
for m in non_kernel_core:
    print(f"  '{m}'")

# Token volume from core vs peripheral
print(f"\n{'='*70}")
print("TOKEN VOLUME: CORE vs PERIPHERAL")
print(f"{'='*70}")

core_set = set(m for m, _ in core_middles)
core_tokens = 0
peripheral_tokens = 0

for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            if m.middle in core_set:
                core_tokens += 1
            else:
                peripheral_tokens += 1

total = core_tokens + peripheral_tokens
print(f"\nCore MIDDLE tokens: {core_tokens} ({100*core_tokens/total:.1f}%)")
print(f"Peripheral MIDDLE tokens: {peripheral_tokens} ({100*peripheral_tokens/total:.1f}%)")

print(f"\n{'='*70}")
print("INTERPRETATION")
print(f"{'='*70}")

print(f"""
The 41 core MIDDLEs that appear in >50% of B folios:
- {len(kernel_core)} contain kernel chars (k/h/e) - these are control vocabulary
- {len(non_kernel_core)} do not contain kernel chars

Core MIDDLEs account for {100*core_tokens/total:.1f}% of B tokens.
Peripheral MIDDLEs (unique/rare) account for {100*peripheral_tokens/total:.1f}%.

SPECULATION:
- Core MIDDLEs = shared control operations (kernel, flow control)
- Peripheral MIDDLEs = folio-specific content (materials, parameters, procedures)

The 83 folios exist because they represent 83 different "procedures" that:
1. Share common control vocabulary (core)
2. Differ in their specific content (peripheral)

This is consistent with a recipe collection where:
- Same control grammar applies to all recipes
- Each recipe has its own materials/parameters encoded in peripheral MIDDLEs
""")
