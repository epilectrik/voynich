"""Test whether Voynichese is combinatorially over-regular.

If the language is morpheme-combinatorial:
- Small set of prefixes
- Small set of middles
- Small set of suffixes
- Most words are mechanical products: prefix × middle × suffix

If real NL:
- Stems are arbitrary (no internal combinatorial structure)
- Word types are NOT predictable from a small morpheme set

Test: how many distinct PREFIX × MIDDLE × SUFFIX combinations explain how much of the running text?
What's the morpheme inventory size?
What's the irregularity rate (words that don't fit any clean morpheme pattern)?
"""
from collections import Counter
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Get all Currier B tokens with morpheme decomposition
prefixes = Counter()
middles = Counter()
suffixes = Counter()
articulators = Counter()
combos_full = Counter()  # (prefix, middle, suffix)
combos_pm = Counter()    # (prefix, middle)
all_tokens = []

for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w:
        continue
    try:
        m = morph.extract(w)
    except Exception:
        continue
    p = m.prefix or ''
    mid = m.middle or ''
    suf = m.suffix or ''
    art = m.articulator or ''
    prefixes[p] += 1
    middles[mid] += 1
    suffixes[suf] += 1
    articulators[art] += 1
    combos_full[(art, p, mid, suf)] += 1
    combos_pm[(p, mid)] += 1
    all_tokens.append(w)

print(f'Currier B: {len(all_tokens):,} tokens analyzed')
print()

print(f'=== MORPHEME INVENTORY ===')
print(f'Distinct ARTICULATORS: {len(articulators)}')
print(f'Distinct PREFIXES:     {len(prefixes)}')
print(f'Distinct MIDDLES:      {len(middles)}')
print(f'Distinct SUFFIXES:     {len(suffixes)}')
print()
print(f'Theoretical combinatorial space: {len(articulators)} x {len(prefixes)} x {len(middles)} x {len(suffixes)} = {len(articulators)*len(prefixes)*len(middles)*len(suffixes):,}')
print(f'Observed distinct combinations:  {len(combos_full):,}')
print(f'Distinct (prefix, middle) pairs: {len(combos_pm):,}')
print()

# How concentrated are these morphemes?
total = sum(prefixes.values())
print(f'=== PREFIX CONCENTRATION ===')
for p, c in prefixes.most_common(15):
    print(f'  {repr(p):>8}: {c:>5} ({100*c/total:.1f}%)')

print()
print(f'=== TOP 20 MIDDLES (count >= 50) ===')
for m, c in middles.most_common(20):
    print(f'  {repr(m):>10}: {c:>5} ({100*c/total:.1f}%)')

print()
print(f'=== SUFFIX CONCENTRATION ===')
for s, c in suffixes.most_common(15):
    print(f'  {repr(s):>8}: {c:>5} ({100*c/total:.1f}%)')

# how much of running text is covered by small middle inventory?
sorted_middles = middles.most_common()
cumul = 0
print()
print(f'=== MIDDLE COVERAGE ===')
for cutoff in (10, 25, 50, 100, 200, 500, 1000):
    if len(sorted_middles) >= cutoff:
        cov = sum(c for _, c in sorted_middles[:cutoff])
        print(f'  Top {cutoff:>4} middles cover {100*cov/total:.1f}% of all running tokens')

# combinatorial productivity: how full is the combinatorial space?
print()
print('=== COMBINATORIAL PRODUCTIVITY ===')
print(f'Top 30 (prefix, middle) cells:')
for (p, m), c in combos_pm.most_common(30):
    print(f'  ({repr(p):>5}, {repr(m):>8}): {c:>4}')

# Compare: how would NL look?
# In NL, you can take the TOP suffix and TOP stem; their product should NOT be a word usually.
# Voynichese: take top prefix qo + top middle and check if qo+middle is attested
top_prefix = prefixes.most_common(1)[0][0]
print()
print(f'=== PREDICTION TEST: top prefix "{top_prefix}" + top 30 middles ===')
existing = Counter()
for w in all_tokens:
    existing[w] += 1
attested = 0
total_top30 = 30
for mid, _ in middles.most_common(30):
    # try common suffixes
    for suf in ['', 'y', 'dy', 'r', 'l', 'in', 'ain', 'iin', 'ar', 'al']:
        candidate = (top_prefix or '') + mid + suf
        if candidate in existing:
            attested += 1
            break
print(f'  Of 30 top middles, {attested} have at least one attested ({top_prefix}+middle+suffix) form')

# Compare combinatorial fill rate
all_pm_possible = len(prefixes) * len(middles)
pm_attested = len(combos_pm)
print()
print(f'=== COMBINATORIAL FILL ===')
print(f'(prefix x middle) cells possible: {all_pm_possible:,}')
print(f'(prefix x middle) cells attested: {pm_attested:,} ({100*pm_attested/all_pm_possible:.2f}%)')
print(f'Top 10 prefixes x top 50 middles (top500 cells): how many attested?')
top_prefixes = [p for p, _ in prefixes.most_common(10)]
top_middles = [m for m, _ in middles.most_common(50)]
attested_top = 0
for p in top_prefixes:
    for m in top_middles:
        if (p, m) in combos_pm:
            attested_top += 1
print(f'  {attested_top} / 500 = {100*attested_top/500:.1f}%')
