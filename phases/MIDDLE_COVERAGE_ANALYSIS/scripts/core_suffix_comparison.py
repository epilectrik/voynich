"""
Compare suffix attachment rates across all CORE MIDDLEs (k, t, e)
Why does only 'e' show suffix absorption?
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())

print("=" * 70)
print("CORE MIDDLE SUFFIX ATTACHMENT COMPARISON")
print("=" * 70)

CORE_MIDDLES = ['k', 't', 'e']

for mid in CORE_MIDDLES:
    tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == mid]
    if tokens:
        suffixes = Counter(m.suffix or '(none)' for t, m in tokens)
        total = len(tokens)
        no_suffix = suffixes.get('(none)', 0)
        has_suffix = total - no_suffix

        print(f"\n'{mid}' MIDDLE (n={total}):")
        print(f"  Has suffix: {has_suffix} ({has_suffix/total*100:.1f}%)")
        print(f"  No suffix:  {no_suffix} ({no_suffix/total*100:.1f}%)")
        print(f"\n  Top suffixes:")
        for s, count in suffixes.most_common(8):
            pct = count / total * 100
            print(f"    {s:<10} {count:>4} ({pct:>5.1f}%)")

# Check if k and t have absorbed variants we missed
print("\n" + "=" * 70)
print("CHECKING FOR k AND t ABSORBED VARIANTS")
print("=" * 70)

# All possible absorbed forms
K_ABSORBED = ['kdy', 'ky', 'key', 'kedy', 'keey', 'ko', 'kol', 'kar', 'kal']
T_ABSORBED = ['tdy', 'ty', 'tey', 'tedy', 'teey', 'to', 'tol', 'tar', 'tal']

print("\nPotential k-absorbed MIDDLEs:")
for mid in K_ABSORBED:
    count = len([t for t in b_tokens if morph.extract(t.word).middle == mid])
    if count > 0:
        print(f"  {mid}: {count}")

print("\nPotential t-absorbed MIDDLEs:")
for mid in T_ABSORBED:
    count = len([t for t in b_tokens if morph.extract(t.word).middle == mid])
    if count > 0:
        print(f"  {mid}: {count}")

# What about 'o' as a core?
print("\n" + "=" * 70)
print("CHECKING 'o' AS POTENTIAL CORE")
print("=" * 70)

O_ABSORBED = ['ody', 'oy', 'oey', 'oedy', 'oeey', 'ol', 'or', 'oal', 'oar']

o_tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == 'o']
print(f"\n'o' MIDDLE: {len(o_tokens)} tokens")

print("\nPotential o-absorbed MIDDLEs:")
for mid in O_ABSORBED:
    count = len([t for t in b_tokens if morph.extract(t.word).middle == mid])
    if count > 0:
        print(f"  {mid}: {count}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: WHY ONLY 'e' ABSORBS?")
print("=" * 70)

k_count = len([t for t in b_tokens if morph.extract(t.word).middle == 'k'])
t_count = len([t for t in b_tokens if morph.extract(t.word).middle == 't'])
e_count = len([t for t in b_tokens if morph.extract(t.word).middle == 'e'])

k_suffixed = len([t for t in b_tokens if morph.extract(t.word).middle == 'k' and morph.extract(t.word).suffix])
t_suffixed = len([t for t in b_tokens if morph.extract(t.word).middle == 't' and morph.extract(t.word).suffix])
e_suffixed = len([t for t in b_tokens if morph.extract(t.word).middle == 'e' and morph.extract(t.word).suffix])

print(f"""
CORE MIDDLE suffix attachment rates:
  k: {k_suffixed}/{k_count} = {k_suffixed/k_count*100:.1f}% have suffix
  t: {t_suffixed}/{t_count} = {t_suffixed/t_count*100:.1f}% have suffix
  e: {e_suffixed}/{e_count} = {e_suffixed/e_count*100:.1f}% have suffix

INTERPRETATION:
If 'e' REQUIRES a suffix 98% of the time, but k and t don't,
then 'e' may encode an INCOMPLETE operation that needs modification.

'e' = base process (incomplete without specification)
'k' = self-contained operation (optional modification)
't' = self-contained operation (optional modification)

The suffix absorption is a WRITING CONVENTION for the mandatory e+suffix pair.
""")
