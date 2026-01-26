"""
INVESTIGATE ZERO SURVIVAL: Why do records with valid PP components still have 0 survival?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict

tx = Transcript()
morph = Morphology()

# Build B token morphology
b_tokens = {}
for token in tx.currier_b():
    word = token.word
    if word and word not in b_tokens:
        m = morph.extract(word)
        b_tokens[word] = {
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
        }

print("=" * 70)
print("INVESTIGATING f1r line 6: ydaraishy")
print("=" * 70)

# f1r line 6 has MIDDLE 'rais', PREFIX 'da', SUFFIX 'hy'
# All are in B. So why 0 survival?

# Check what B tokens have MIDDLE 'rais'
print("\nB tokens with MIDDLE 'rais':")
rais_tokens = [w for w, info in b_tokens.items() if info['middle'] == 'rais']
print(f"  Found: {len(rais_tokens)}")
for w in rais_tokens:
    info = b_tokens[w]
    print(f"  {w}: PREFIX={info['prefix']}, MIDDLE={info['middle']}, SUFFIX={info['suffix']}")

# Check what B tokens have PREFIX 'da'
print("\nB tokens with PREFIX 'da' (first 20):")
da_tokens = [w for w, info in b_tokens.items() if info['prefix'] == 'da']
print(f"  Found: {len(da_tokens)}")
for w in da_tokens[:20]:
    info = b_tokens[w]
    print(f"  {w}: MIDDLE={info['middle']}, SUFFIX={info['suffix']}")

# Check what B tokens have SUFFIX 'hy'
print("\nB tokens with SUFFIX 'hy' (first 20):")
hy_tokens = [w for w, info in b_tokens.items() if info['suffix'] == 'hy']
print(f"  Found: {len(hy_tokens)}")
for w in hy_tokens[:20]:
    info = b_tokens[w]
    print(f"  {w}: PREFIX={info['prefix']}, MIDDLE={info['middle']}")

# The key question: are there ANY B tokens that:
# - Have MIDDLE 'rais' AND any of: PREFIX in {da, None} AND SUFFIX in {hy, None}
print("\n" + "=" * 70)
print("CROSS-CHECK: B tokens compatible with f1r line 6")
print("=" * 70)

pp_middles = {'rais'}
pp_prefixes = {'da'}
pp_suffixes = {'hy'}

compatible = []
for word, info in b_tokens.items():
    # MIDDLE check
    if info['middle'] is None:
        middle_ok = True
    else:
        middle_ok = info['middle'] in pp_middles

    # PREFIX check (None = no PREFIX = always OK)
    if info['prefix'] is None:
        prefix_ok = True
    else:
        prefix_ok = info['prefix'] in pp_prefixes

    # SUFFIX check (None = no SUFFIX = always OK)
    if info['suffix'] is None:
        suffix_ok = True
    else:
        suffix_ok = info['suffix'] in pp_suffixes

    if middle_ok and prefix_ok and suffix_ok:
        compatible.append((word, info))

print(f"\nCompatible B tokens: {len(compatible)}")
for w, info in compatible:
    print(f"  {w}: PREFIX={info['prefix']}, MIDDLE={info['middle']}, SUFFIX={info['suffix']}")

# If 0 compatible, why?
if not compatible:
    print("\nWhy 0 compatible?")
    print("Need: MIDDLE in {rais, None}, PREFIX in {da, None}, SUFFIX in {hy, None}")

    # Check tokens with no MIDDLE (should all pass)
    no_middle = [w for w, info in b_tokens.items() if info['middle'] is None]
    print(f"\nTokens with no MIDDLE: {len(no_middle)}")
    for w in no_middle[:5]:
        info = b_tokens[w]
        print(f"  {w}: PREFIX={info['prefix']}, SUFFIX={info['suffix']}")
        # These need PREFIX in {da, None} AND SUFFIX in {hy, None}
        pok = info['prefix'] is None or info['prefix'] in pp_prefixes
        sok = info['suffix'] is None or info['suffix'] in pp_suffixes
        print(f"    PREFIX OK: {pok}, SUFFIX OK: {sok}")

# Check BARE tokens (no PREFIX) with MIDDLE 'rais'
print("\nBARE tokens (no PREFIX) with MIDDLE 'rais':")
bare_rais = [w for w, info in b_tokens.items() if info['prefix'] is None and info['middle'] == 'rais']
print(f"  Found: {len(bare_rais)}")
for w in bare_rais:
    info = b_tokens[w]
    print(f"  {w}: SUFFIX={info['suffix']}")

print("\n" + "=" * 70)
print("DIAGNOSIS")
print("=" * 70)

# The issue is likely that:
# - MIDDLE 'rais' requires specific PREFIX/SUFFIX combinations
# - The A record only has da/hy
# - But B tokens with MIDDLE 'rais' require different PREFIX/SUFFIX

print("\nB tokens with MIDDLE 'rais' have these PREFIX/SUFFIX combos:")
for w in rais_tokens:
    info = b_tokens[w]
    print(f"  PREFIX='{info['prefix']}', SUFFIX='{info['suffix']}'")
    print(f"    A has PREFIX 'da': {info['prefix'] in [None, 'da']}")
    print(f"    A has SUFFIX 'hy': {info['suffix'] in [None, 'hy']}")
