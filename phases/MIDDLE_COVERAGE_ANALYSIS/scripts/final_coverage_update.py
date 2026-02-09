"""
Final coverage update including:
- Three-tier operations (PREP, CORE, EXT)
- Vowel core absorption (e, o, a families)
- Primary infrastructure (daiin family)
- Secondary infrastructure (-hy consonant clusters)
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())
total = len(b_tokens)

print("=" * 70)
print("FINAL COVERAGE SUMMARY")
print("=" * 70)

# Categories
PREP_TIER = {'te', 'pch', 'lch', 'tch', 'ksh'}
CORE_TIER = {'k', 't', 'e'}
EXT_TIER = {'ke', 'kch'}

# Vowel absorption
E_ABSORBED = {'edy', 'ey', 'eey', 'ed', 'eo', 'eol', 'ee', 'eeo', 'eed', 'eod'}
O_ABSORBED = {'ol', 'or'}
A_ABSORBED = {'al', 'ar', 'ain', 'aiin', 'am'}
VOWEL_CORES = {'a', 'o'}

# Primary infrastructure (daiin family)
PRIMARY_INFRA = {'iin', 'in', 'l', 'r', 'd'}

# Secondary infrastructure (-hy consonant clusters)
# These are MIDDLEs that take -hy suffix
HY_MIDDLES = {'ck', 'ct', 'eck', 'ect', 'c', 'kc', 'tc', 'oct', 'ec', 'ock', 'kec', 'pc', 'cp', 'opc'}

def count_tokens(middle_set):
    return len([t for t in b_tokens if morph.extract(t.word).middle in middle_set])

def count_suffix(suffix):
    return len([t for t in b_tokens if morph.extract(t.word).suffix == suffix])

# Calculate counts
prep_count = count_tokens(PREP_TIER)
core_count = count_tokens(CORE_TIER)
ext_count = count_tokens(EXT_TIER)

e_abs = count_tokens(E_ABSORBED)
o_abs = count_tokens(O_ABSORBED)
a_abs = count_tokens(A_ABSORBED)
vowel_core = count_tokens(VOWEL_CORES)

primary_infra = count_tokens(PRIMARY_INFRA)

# -hy tokens (using suffix, not MIDDLE)
hy_count = count_suffix('hy')

print(f"\nTotal Currier B tokens: {total}")

print("\n" + "-" * 70)
print("OPERATIONAL TOKENS")
print("-" * 70)

print(f"""
PREP tier (te, pch, lch, tch, ksh):     {prep_count:>5} ({prep_count/total*100:>5.1f}%)
CORE tier (k, t, e):                    {core_count:>5} ({core_count/total*100:>5.1f}%)
EXT tier (ke, kch):                      {ext_count:>5} ({ext_count/total*100:>5.1f}%)

e-absorbed (edy, ey, eey, etc.):        {e_abs:>5} ({e_abs/total*100:>5.1f}%)
o-absorbed (ol, or):                    {o_abs:>5} ({o_abs/total*100:>5.1f}%)
a-absorbed (al, ar, ain, aiin, am):     {a_abs:>5} ({a_abs/total*100:>5.1f}%)
Vowel cores (a, o):                      {vowel_core:>5} ({vowel_core/total*100:>5.1f}%)
""")

operational = prep_count + core_count + ext_count + e_abs + o_abs + a_abs + vowel_core
print(f"OPERATIONAL SUBTOTAL:                   {operational:>5} ({operational/total*100:>5.1f}%)")

print("\n" + "-" * 70)
print("INFRASTRUCTURE TOKENS")
print("-" * 70)

print(f"""
Primary infra (iin, in, l, r, d):       {primary_infra:>5} ({primary_infra/total*100:>5.1f}%)
Secondary infra (-hy suffix):             {hy_count:>5} ({hy_count/total*100:>5.1f}%)
""")

infra_total = primary_infra + hy_count
print(f"INFRASTRUCTURE SUBTOTAL:                {infra_total:>5} ({infra_total/total*100:>5.1f}%)")

print("\n" + "-" * 70)
print("TOTAL COVERAGE")
print("-" * 70)

# Note: there might be overlap, so let's count precisely
all_explained = set()
for t in b_tokens:
    m = morph.extract(t.word)
    mid = m.middle
    suf = m.suffix

    # Check if explained
    if mid in PREP_TIER | CORE_TIER | EXT_TIER | E_ABSORBED | O_ABSORBED | A_ABSORBED | VOWEL_CORES | PRIMARY_INFRA:
        all_explained.add(id(t))
    elif suf == 'hy':
        all_explained.add(id(t))

precise_coverage = len(all_explained)
remaining = total - precise_coverage

print(f"""
TOTAL EXPLAINED (precise):              {precise_coverage:>5} ({precise_coverage/total*100:>5.1f}%)
REMAINING UNKNOWN:                      {remaining:>5} ({remaining/total*100:>5.1f}%)
""")

print("\n" + "=" * 70)
print("REMAINING UNKNOWNS")
print("=" * 70)

# What's still unknown?
unexplained = []
for t in b_tokens:
    if id(t) not in all_explained:
        m = morph.extract(t.word)
        unexplained.append(m.middle)

unexplained_counts = Counter(unexplained)
print(f"\nTop 25 unexplained MIDDLEs:")
for mid, count in unexplained_counts.most_common(25):
    pct = count / total * 100
    print(f"  {mid:<12} {count:>5} ({pct:>5.2f}%)")

print(f"\n\nTotal unique unexplained MIDDLEs: {len(unexplained_counts)}")
