"""
UNREACHABLE B FOLIO ANALYSIS

Why are some B folios (f41r, f26v, f57r) unreachable by 25% of A records?
What makes them morphologically distinct?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("UNREACHABLE B FOLIO ANALYSIS")
print("What makes some B folios hard to reach?")
print("=" * 70)

# Build B token morphology per folio
b_folio_morphology = defaultdict(lambda: {'middles': set(), 'prefixes': set(), 'suffixes': set()})
b_folio_tokens = defaultdict(set)

for token in tx.currier_b():
    word = token.word
    if word:
        folio = token.folio
        m = morph.extract(word)
        b_folio_tokens[folio].add(word)
        if m.middle:
            b_folio_morphology[folio]['middles'].add(m.middle)
        if m.prefix:
            b_folio_morphology[folio]['prefixes'].add(m.prefix)
        if m.suffix:
            b_folio_morphology[folio]['suffixes'].add(m.suffix)

# Hard-to-reach folios (from previous analysis)
hard_folios = ['f41r', 'f26v', 'f57r']
easy_folios = ['f33r', 'f33v', 'f31r']  # High compatibility from previous analysis

# Compare morphological profiles
print("\n--- HARD-TO-REACH FOLIOS (unreachable by ~25% of A records) ---")
for folio in hard_folios:
    info = b_folio_morphology[folio]
    tokens = b_folio_tokens[folio]
    print(f"\n{folio}:")
    print(f"  Unique tokens: {len(tokens)}")
    print(f"  Unique MIDDLEs: {len(info['middles'])}")
    print(f"  Unique PREFIXes: {len(info['prefixes'])}")
    print(f"  Unique SUFFIXes: {len(info['suffixes'])}")
    print(f"  PREFIXes: {sorted(info['prefixes'])}")

print("\n--- EASY-TO-REACH FOLIOS (for comparison) ---")
for folio in easy_folios:
    if folio in b_folio_morphology:
        info = b_folio_morphology[folio]
        tokens = b_folio_tokens[folio]
        print(f"\n{folio}:")
        print(f"  Unique tokens: {len(tokens)}")
        print(f"  Unique MIDDLEs: {len(info['middles'])}")
        print(f"  Unique PREFIXes: {len(info['prefixes'])}")
        print(f"  Unique SUFFIXes: {len(info['suffixes'])}")
        print(f"  PREFIXes: {sorted(info['prefixes'])}")

# Check BARE token presence (tokens with no PREFIX)
print("\n" + "=" * 70)
print("BARE TOKEN ANALYSIS (no PREFIX)")
print("=" * 70)

def count_bare_tokens(folio):
    bare = 0
    total = 0
    for word in b_folio_tokens[folio]:
        m = morph.extract(word)
        total += 1
        if not m.prefix:
            bare += 1
    return bare, total

print("\nHard-to-reach folios:")
for folio in hard_folios:
    bare, total = count_bare_tokens(folio)
    print(f"  {folio}: {bare}/{total} BARE tokens ({100*bare/total:.1f}%)")

print("\nEasy-to-reach folios:")
for folio in easy_folios:
    if folio in b_folio_tokens:
        bare, total = count_bare_tokens(folio)
        print(f"  {folio}: {bare}/{total} BARE tokens ({100*bare/total:.1f}%)")

# Check: what MIDDLEs are UNIQUE to hard folios?
print("\n" + "=" * 70)
print("MIDDLE UNIQUENESS ANALYSIS")
print("=" * 70)

# Get MIDDLEs that appear in most folios vs only hard folios
all_folio_middles = defaultdict(set)
for folio, info in b_folio_morphology.items():
    for mid in info['middles']:
        all_folio_middles[mid].add(folio)

# MIDDLEs common across all folios
common_middles = set(mid for mid, folios in all_folio_middles.items() if len(folios) > 70)
print(f"\nMIDDLEs appearing in >70 folios: {len(common_middles)}")

# MIDDLEs in hard folios
hard_folio_middles = set()
for folio in hard_folios:
    hard_folio_middles |= b_folio_morphology[folio]['middles']

# What fraction of hard folio MIDDLEs are common?
common_in_hard = hard_folio_middles & common_middles
print(f"\nHard folios use {len(hard_folio_middles)} unique MIDDLEs")
print(f"  Of which {len(common_in_hard)} are common (in >70 folios)")
print(f"  And {len(hard_folio_middles - common_middles)} are less common")

# Are hard folios dominated by rare MIDDLEs?
print("\n--- MIDDLE RARITY in hard folios ---")
for folio in hard_folios:
    folio_middles = b_folio_morphology[folio]['middles']
    rare = [m for m in folio_middles if len(all_folio_middles[m]) < 20]
    common = [m for m in folio_middles if len(all_folio_middles[m]) >= 70]
    print(f"{folio}:")
    print(f"  Rare MIDDLEs (<20 folios): {len(rare)}")
    print(f"  Common MIDDLEs (>=70 folios): {len(common)}")
    if rare:
        print(f"  Rare examples: {rare[:5]}")

# Summary: what makes a folio hard to reach?
print("\n" + "=" * 70)
print("SUMMARY: WHY SOME FOLIOS ARE HARD TO REACH")
print("=" * 70)

# Statistical summary
all_folios = list(b_folio_morphology.keys())
folio_stats = []
for folio in all_folios:
    bare, total = count_bare_tokens(folio)
    bare_pct = 100 * bare / total if total > 0 else 0
    n_middles = len(b_folio_morphology[folio]['middles'])
    n_prefixes = len(b_folio_morphology[folio]['prefixes'])
    folio_stats.append({
        'folio': folio,
        'bare_pct': bare_pct,
        'n_middles': n_middles,
        'n_prefixes': n_prefixes,
        'n_tokens': total
    })

# Correlation: do hard folios have fewer BARE tokens?
import numpy as np
bare_pcts = [s['bare_pct'] for s in folio_stats]
n_middles = [s['n_middles'] for s in folio_stats]

print(f"\nAcross all {len(all_folios)} B folios:")
print(f"  BARE token %: mean={np.mean(bare_pcts):.1f}%, std={np.std(bare_pcts):.1f}%")
print(f"  Range: {np.min(bare_pcts):.1f}% - {np.max(bare_pcts):.1f}%")

# Hard folio stats
hard_stats = [s for s in folio_stats if s['folio'] in hard_folios]
print(f"\nHard-to-reach folios ({hard_folios}):")
for s in hard_stats:
    print(f"  {s['folio']}: {s['bare_pct']:.1f}% BARE, {s['n_middles']} MIDDLEs, {s['n_prefixes']} PREFIXes")

# What predicts "hard to reach"?
print("""
HYPOTHESIS: Hard-to-reach folios have:
1. Fewer BARE tokens (require PREFIXes to access)
2. More rare MIDDLEs (not in most A records)
3. Less morphological diversity
""")
