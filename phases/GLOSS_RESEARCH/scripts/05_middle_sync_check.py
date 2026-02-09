"""Check sync between middle dictionary glosses and token dictionary glosses.

Finds cases where a token's hardcoded gloss disagrees with what
auto-composition would produce from the middle dictionary.
"""
import json, sys, re
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Morphology

morph = Morphology()
td = json.load(open('data/token_dictionary.json', encoding='utf-8'))
md = json.load(open('data/middle_dictionary.json', encoding='utf-8'))

middles = md['middles']
tokens = td['tokens']

# Step 1: What do the glossed middles currently say?
print(f"{'='*70}")
print(f"MIDDLE DICTIONARY GLOSSES (all {sum(1 for m in middles.values() if m.get('gloss'))} glossed)")
print(f"{'='*70}")

glossed_middles = {m: e['gloss'] for m, e in middles.items() if e.get('gloss')}
for mid in sorted(glossed_middles.keys(), key=lambda m: -middles[m].get('token_count', 0)):
    gloss = glossed_middles[mid]
    count = middles[mid].get('token_count', 0)
    print(f"  {mid:<14} = {gloss:<25} (n={count})")

# Step 2: For each glossed token, check if its middle's gloss appears in the token gloss
print(f"\n{'='*70}")
print(f"MISALIGNMENT CHECK: token gloss vs middle gloss")
print(f"{'='*70}")
print(f"Tokens where the middle has a gloss but it doesn't appear in the token gloss:\n")

misaligned = []
aligned = 0
no_middle_gloss = 0
star_ref = 0

for tok, entry in tokens.items():
    tok_gloss = entry.get('gloss')
    if not tok_gloss:
        continue

    # Skip *middle references - those are fine
    if '*' in tok_gloss:
        star_ref += 1
        continue

    m = morph.extract(tok)
    if not m.middle:
        continue

    mid_gloss = glossed_middles.get(m.middle)
    if not mid_gloss:
        no_middle_gloss += 1
        continue

    # Check if the middle gloss (or a close variant) appears in the token gloss
    # Normalize: lowercase, strip punctuation for matching
    tok_lower = tok_gloss.lower().replace('.', '').replace(',', '').replace(';', '').strip()
    mid_lower = mid_gloss.lower().strip()

    if mid_lower in tok_lower:
        aligned += 1
    else:
        misaligned.append((tok, tok_gloss, m.middle, mid_gloss, m.prefix, m.suffix))

print(f"  Aligned (middle gloss found in token gloss): {aligned}")
print(f"  Using * references: {star_ref}")
print(f"  Middle has no gloss: {no_middle_gloss}")
print(f"  MISALIGNED: {len(misaligned)}")

# Group misalignments by middle
by_middle = defaultdict(list)
for tok, tok_gloss, middle, mid_gloss, prefix, suffix in misaligned:
    by_middle[middle].append((tok, tok_gloss, prefix, suffix))

print(f"\n{'='*70}")
print(f"MISALIGNMENTS BY MIDDLE")
print(f"{'='*70}")

for middle in sorted(by_middle.keys(), key=lambda m: -len(by_middle[m])):
    items = by_middle[middle]
    mid_gloss = glossed_middles[middle]
    print(f"\n  MIDDLE '{middle}' = '{mid_gloss}' ({len(items)} misaligned tokens):")
    for tok, tok_gloss, prefix, suffix in sorted(items, key=lambda x: x[0])[:10]:
        print(f"    {tok:<20} gloss: {tok_gloss:<35} p={prefix or '-':<4} s={suffix or '-'}")
    if len(items) > 10:
        print(f"    ... and {len(items)-10} more")

# Step 3: Check vocabulary shift alignment
print(f"\n{'='*70}")
print(f"VOCABULARY SHIFT CHECK")
print(f"{'='*70}")
print(f"Are middle dictionary glosses using the new vocabulary?\n")

old_vocab = {
    'settle': 'cool', 'equilibrate': 'cool', 'deep settle': 'deep cool',
    'output': 'collect', 'operate': 'work', 'checkpoint': 'check',
    'monitor': 'check', 'watch': 'observe'
}

stale = []
for mid, entry in middles.items():
    gloss = entry.get('gloss', '')
    if not gloss:
        continue
    for old, new in old_vocab.items():
        if old in gloss.lower():
            stale.append((mid, gloss, old, new))

if stale:
    print(f"  STALE GLOSSES (using old vocabulary):")
    for mid, gloss, old, new in stale:
        print(f"    {mid:<14} '{gloss}' -- contains '{old}', should use '{new}'")
else:
    print(f"  All middle glosses use current vocabulary.")
