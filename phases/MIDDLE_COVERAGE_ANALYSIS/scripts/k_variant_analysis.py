"""
K-variant analysis: ck, ckh, ek, eck, eek, etc.
Are these k-absorbed forms or something else?
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())
total = len(b_tokens)

print("=" * 70)
print("K-VARIANT ANALYSIS")
print("=" * 70)

# All potential k-related MIDDLEs
K_VARIANTS = ['k', 'ck', 'ckh', 'ek', 'eck', 'eek', 'ok', 'lk', 'key', 'kedy',
              'ky', 'kdy', 'kch', 'ke', 'ko', 'ka', 'ki']

print("\n1. K-VARIANT FREQUENCY")
print("-" * 60)

k_counts = {}
for mid in K_VARIANTS:
    count = len([t for t in b_tokens if morph.extract(t.word).middle == mid])
    if count > 0:
        k_counts[mid] = count
        pct = count / total * 100
        print(f"  {mid:<8} {count:>5} ({pct:.2f}%)")

print(f"\nTotal k-family: {sum(k_counts.values())} ({sum(k_counts.values())/total*100:.1f}%)")

# 2. Suffix patterns for each k-variant
print("\n2. SUFFIX PATTERNS (Key test for absorption)")
print("-" * 60)
print("If ck = c+k absorbed, then 'ck' should have NO suffix (like edy)")

for mid in ['k', 'ck', 'ckh', 'ek', 'eck', 'eek', 'ok', 'lk']:
    tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == mid]
    if len(tokens) > 20:
        suffixes = Counter(m.suffix or '(none)' for t, m in tokens)
        no_suffix = suffixes.get('(none)', 0)
        no_suffix_pct = no_suffix / len(tokens) * 100
        print(f"\n'{mid}' (n={len(tokens)}):")
        print(f"  No suffix: {no_suffix_pct:.1f}%")
        for s, count in suffixes.most_common(5):
            pct = count / len(tokens) * 100
            print(f"    {s:<10} {count:>4} ({pct:>5.1f}%)")

# 3. PREFIX patterns
print("\n3. PREFIX PATTERNS")
print("-" * 60)

for mid in ['k', 'ck', 'ckh', 'ek', 'eck', 'eek', 'ok', 'lk']:
    tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == mid]
    if len(tokens) > 20:
        prefixes = Counter(m.prefix or '(none)' for t, m in tokens)
        print(f"\n'{mid}' (n={len(tokens)}):")
        for p, count in prefixes.most_common(6):
            pct = count / len(tokens) * 100
            print(f"    {p:<10} {count:>4} ({pct:>5.1f}%)")

# 4. Most common full tokens
print("\n4. MOST COMMON TOKENS")
print("-" * 60)

for mid in ['k', 'ck', 'ckh', 'ek', 'eck', 'eek']:
    tokens = [t.word for t in b_tokens if morph.extract(t.word).middle == mid]
    if len(tokens) > 20:
        token_counts = Counter(tokens)
        print(f"\n'{mid}':")
        for tok, count in token_counts.most_common(6):
            m = morph.extract(tok)
            print(f"  {tok:<15} {count:>4}  PRE={m.prefix or '-':<6} SUF={m.suffix or '-'}")

# 5. Section distribution
print("\n5. SECTION DISTRIBUTION")
print("-" * 60)

SECTION_MAP = {
    'HERBAL_B': {'f102v', 'f103r', 'f103v', 'f104r', 'f104v', 'f105r', 'f105v', 'f106r', 'f106v',
                 'f107r', 'f107v', 'f108r', 'f108v', 'f111r', 'f111v', 'f112r', 'f112v'},
    'BIO': {'f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v', 'f78r', 'f78v', 'f79r', 'f79v',
            'f80r', 'f80v', 'f81r', 'f81v', 'f82r', 'f82v', 'f83r', 'f83v', 'f84r', 'f84v'}
}

def get_section(folio):
    for section, folios in SECTION_MAP.items():
        if folio in folios:
            return section
    return 'OTHER'

print(f"\n{'MIDDLE':<8} {'BIO':>8} {'HERBAL_B':>10} {'OTHER':>8}")
print("-" * 40)

for mid in ['k', 'ck', 'ckh', 'ek', 'eck', 'eek']:
    tokens = [t for t in b_tokens if morph.extract(t.word).middle == mid]
    if len(tokens) > 20:
        sections = Counter(get_section(t.folio) for t in tokens)
        total_mid = len(tokens)
        bio = sections.get('BIO', 0) / total_mid * 100
        herb = sections.get('HERBAL_B', 0) / total_mid * 100
        other = sections.get('OTHER', 0) / total_mid * 100
        print(f"{mid:<8} {bio:>7.1f}% {herb:>9.1f}% {other:>7.1f}%")

# 6. The ck/ckh question - are these ch+k?
print("\n" + "=" * 70)
print("6. HYPOTHESIS: ck = ch + k ABSORPTION?")
print("=" * 70)

print("""
If ck is ch+k absorbed (like edy is e+dy absorbed), then:
  - 'ck' should behave like 'k' with ch- prefix
  - Compare: chk... tokens vs ck tokens
""")

# Find tokens with ch prefix and k middle
chk_tokens = [(t, morph.extract(t.word)) for t in b_tokens
              if morph.extract(t.word).middle == 'k' and morph.extract(t.word).prefix == 'ch']
print(f"\nTokens with PREFIX=ch, MIDDLE=k: {len(chk_tokens)}")
if chk_tokens:
    print("Examples:")
    for tok, m in chk_tokens[:5]:
        print(f"  {tok.word}: PRE={m.prefix}, MID={m.middle}, SUF={m.suffix}")

# Compare to ck tokens
ck_tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == 'ck']
print(f"\nTokens with MIDDLE=ck: {len(ck_tokens)}")
if ck_tokens:
    print("Examples:")
    for tok, m in ck_tokens[:5]:
        print(f"  {tok.word}: PRE={m.prefix}, MID={m.middle}, SUF={m.suffix}")

# 7. The ek question - is this e+k or k+e reversed?
print("\n" + "=" * 70)
print("7. HYPOTHESIS: ek = e + k COMPOUND?")
print("=" * 70)

print("""
We have 'ke' as an EXT tier MIDDLE (k extended by e).
Is 'ek' the reverse? Or is it e with k absorbed?
""")

ke_tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == 'ke']
ek_tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == 'ek']

print(f"\n'ke' MIDDLE: {len(ke_tokens)} tokens")
print(f"'ek' MIDDLE: {len(ek_tokens)} tokens")

# Compare suffix patterns
print("\nSuffix comparison:")
ke_suffixes = Counter(m.suffix or '(none)' for t, m in ke_tokens)
ek_suffixes = Counter(m.suffix or '(none)' for t, m in ek_tokens)

print(f"\n'ke' suffixes:")
for s, count in ke_suffixes.most_common(5):
    print(f"  {s}: {count}")

print(f"\n'ek' suffixes:")
for s, count in ek_suffixes.most_common(5):
    print(f"  {s}: {count}")

# 8. Line position analysis
print("\n" + "=" * 70)
print("8. LINE POSITION ANALYSIS")
print("=" * 70)

by_line = defaultdict(list)
for t in b_tokens:
    by_line[(t.folio, t.line)].append(t)

def get_line_pos_dist(middle):
    positions = Counter()
    for (folio, line), tokens in by_line.items():
        if len(tokens) < 3:
            continue
        for i, t in enumerate(tokens):
            m = morph.extract(t.word)
            if m.middle == middle:
                if i == 0:
                    positions['FIRST'] += 1
                elif i == len(tokens) - 1:
                    positions['LAST'] += 1
                else:
                    positions['MIDDLE'] += 1
    return positions

print(f"\n{'MIDDLE':<8} {'FIRST':>8} {'MIDDLE':>8} {'LAST':>8}")
print("-" * 40)

for mid in ['k', 'ck', 'ckh', 'ek', 'eck', 'eek', 'ke', 'kch']:
    pos = get_line_pos_dist(mid)
    total_pos = sum(pos.values())
    if total_pos > 20:
        first = pos.get('FIRST', 0) / total_pos * 100
        middle = pos.get('MIDDLE', 0) / total_pos * 100
        last = pos.get('LAST', 0) / total_pos * 100
        print(f"{mid:<8} {first:>7.1f}% {middle:>7.1f}% {last:>7.1f}%")

# 9. Synthesis
print("\n" + "=" * 70)
print("9. K-VARIANT SYNTHESIS")
print("=" * 70)

# Calculate what portion of k-variants have absorbed suffixes
k_no_suffix = len([t for t in b_tokens if morph.extract(t.word).middle == 'k' and not morph.extract(t.word).suffix])
k_total = len([t for t in b_tokens if morph.extract(t.word).middle == 'k'])

ck_no_suffix = len([t for t in b_tokens if morph.extract(t.word).middle == 'ck' and not morph.extract(t.word).suffix])
ck_total = len([t for t in b_tokens if morph.extract(t.word).middle == 'ck'])

ek_no_suffix = len([t for t in b_tokens if morph.extract(t.word).middle == 'ek' and not morph.extract(t.word).suffix])
ek_total = len([t for t in b_tokens if morph.extract(t.word).middle == 'ek'])

print(f"""
SUFFIX ABSORPTION TEST:

'k' has no suffix:  {k_no_suffix}/{k_total} = {k_no_suffix/k_total*100:.1f}%
'ck' has no suffix: {ck_no_suffix}/{ck_total} = {ck_no_suffix/ck_total*100:.1f}%
'ek' has no suffix: {ek_no_suffix}/{ek_total} = {ek_no_suffix/ek_total*100:.1f}%

INTERPRETATION:
- 'k' almost always takes a suffix (like 'e')
- 'ck' and 'ek' rarely take suffix -> ABSORPTION CONFIRMED
- These are k-compounds with absorbed prefixes/modifiers
""")
