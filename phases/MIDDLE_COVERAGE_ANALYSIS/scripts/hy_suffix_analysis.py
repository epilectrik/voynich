"""
Analyze the -hy suffix: What does it encode?
It appears almost exclusively with ck/eck variants.
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
print("-hy SUFFIX ANALYSIS")
print("=" * 70)

# 1. Basic frequency
hy_tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).suffix == 'hy']
print(f"\n1. BASIC STATS")
print("-" * 60)
print(f"Tokens with -hy suffix: {len(hy_tokens)} ({len(hy_tokens)/total*100:.2f}%)")

# 2. What MIDDLEs take -hy?
print("\n2. MIDDLEs THAT TAKE -hy")
print("-" * 60)

hy_middles = Counter(m.middle for t, m in hy_tokens)
print(f"\nTop MIDDLEs with -hy suffix:")
for mid, count in hy_middles.most_common(15):
    pct = count / len(hy_tokens) * 100
    print(f"  {mid:<12} {count:>4} ({pct:>5.1f}%)")

# 3. What PREFIXes appear with -hy?
print("\n3. PREFIXes WITH -hy SUFFIX")
print("-" * 60)

hy_prefixes = Counter(m.prefix or '(none)' for t, m in hy_tokens)
print(f"\nPREFIX distribution for -hy tokens:")
for pre, count in hy_prefixes.most_common(10):
    pct = count / len(hy_tokens) * 100
    print(f"  {pre:<12} {count:>4} ({pct:>5.1f}%)")

# 4. Most common full tokens with -hy
print("\n4. MOST COMMON -hy TOKENS")
print("-" * 60)

hy_token_counts = Counter(t.word for t, m in hy_tokens)
for tok, count in hy_token_counts.most_common(20):
    m = morph.extract(tok)
    print(f"  {tok:<15} {count:>4}  PRE={m.prefix or '-':<6} MID={m.middle:<6}")

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

hy_sections = Counter(get_section(t.folio) for t, m in hy_tokens)
print(f"\n-hy suffix section distribution:")
for sec, count in hy_sections.most_common():
    pct = count / len(hy_tokens) * 100
    print(f"  {sec:<12} {count:>4} ({pct:>5.1f}%)")

# 6. Line position
print("\n6. LINE POSITION")
print("-" * 60)

by_line = defaultdict(list)
for t in b_tokens:
    by_line[(t.folio, t.line)].append(t)

hy_positions = Counter()
for (folio, line), tokens in by_line.items():
    if len(tokens) < 3:
        continue
    for i, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m.suffix == 'hy':
            if i == 0:
                hy_positions['FIRST'] += 1
            elif i == len(tokens) - 1:
                hy_positions['LAST'] += 1
            else:
                hy_positions['MIDDLE'] += 1

total_pos = sum(hy_positions.values())
print(f"\n-hy line position:")
for pos, count in hy_positions.most_common():
    pct = count / total_pos * 100
    print(f"  {pos:<8} {count:>4} ({pct:>5.1f}%)")

# 7. Compare -hy to other -y suffixes
print("\n7. COMPARING -hy TO OTHER -y SUFFIXES")
print("-" * 60)

y_suffixes = ['y', 'dy', 'ey', 'hy', 'edy', 'eey']
print(f"\n{'Suffix':<8} {'Count':>6} {'% of B':>8}")
print("-" * 30)

for suf in y_suffixes:
    count = len([t for t in b_tokens if morph.extract(t.word).suffix == suf])
    pct = count / total * 100
    print(f"{suf:<8} {count:>6} {pct:>7.2f}%")

# 8. What comes AFTER -hy tokens?
print("\n8. WHAT FOLLOWS -hy TOKENS?")
print("-" * 60)

following_hy = Counter()
for (folio, line), tokens in by_line.items():
    for i, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m.suffix == 'hy' and i < len(tokens) - 1:
            following_hy[tokens[i+1].word] += 1

print(f"\nMost common tokens following -hy:")
for tok, count in following_hy.most_common(15):
    m = morph.extract(tok)
    print(f"  {tok:<15} {count:>3}  (MID={m.middle})")

# 9. What comes BEFORE -hy tokens?
print("\n9. WHAT PRECEDES -hy TOKENS?")
print("-" * 60)

preceding_hy = Counter()
for (folio, line), tokens in by_line.items():
    for i, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m.suffix == 'hy' and i > 0:
            preceding_hy[tokens[i-1].word] += 1

print(f"\nMost common tokens preceding -hy:")
for tok, count in preceding_hy.most_common(15):
    m = morph.extract(tok)
    print(f"  {tok:<15} {count:>3}  (MID={m.middle})")

# 10. The chckhy phenomenon
print("\n" + "=" * 70)
print("10. THE chckhy PHENOMENON")
print("=" * 70)

chckhy_tokens = [t for t in b_tokens if t.word == 'chckhy']
print(f"\n'chckhy' occurrences: {len(chckhy_tokens)}")

# Where does it appear in lines?
chckhy_positions = Counter()
for (folio, line), tokens in by_line.items():
    for i, t in enumerate(tokens):
        if t.word == 'chckhy':
            if i == 0:
                chckhy_positions['FIRST'] += 1
            elif i == len(tokens) - 1:
                chckhy_positions['LAST'] += 1
            else:
                rel_pos = i / (len(tokens) - 1)
                if rel_pos < 0.33:
                    chckhy_positions['EARLY'] += 1
                elif rel_pos < 0.67:
                    chckhy_positions['MID'] += 1
                else:
                    chckhy_positions['LATE'] += 1

print(f"\nLine position distribution:")
for pos, count in chckhy_positions.most_common():
    print(f"  {pos}: {count}")

# What follows chckhy?
following_chckhy = Counter()
for (folio, line), tokens in by_line.items():
    for i, t in enumerate(tokens):
        if t.word == 'chckhy' and i < len(tokens) - 1:
            following_chckhy[tokens[i+1].word] += 1

print(f"\nWhat follows 'chckhy':")
for tok, count in following_chckhy.most_common(10):
    print(f"  {tok}: {count}")

# 11. Synthesis
print("\n" + "=" * 70)
print("11. -hy SUFFIX SYNTHESIS")
print("=" * 70)

# Calculate concentration
ck_hy = len([t for t in b_tokens if morph.extract(t.word).middle == 'ck' and morph.extract(t.word).suffix == 'hy'])
eck_hy = len([t for t in b_tokens if morph.extract(t.word).middle == 'eck' and morph.extract(t.word).suffix == 'hy'])
ct_hy = len([t for t in b_tokens if morph.extract(t.word).middle == 'ct' and morph.extract(t.word).suffix == 'hy'])
total_hy = len(hy_tokens)

print(f"""
-hy SUFFIX PROFILE:

Total -hy tokens: {total_hy}

MIDDLE concentration:
  ck + hy:  {ck_hy} ({ck_hy/total_hy*100:.1f}% of all -hy)
  eck + hy: {eck_hy} ({eck_hy/total_hy*100:.1f}% of all -hy)
  ct + hy:  {ct_hy} ({ct_hy/total_hy*100:.1f}% of all -hy)
  Combined: {(ck_hy + eck_hy + ct_hy)/total_hy*100:.1f}%

PREFIX concentration:
  ch- + X + hy: {sum(1 for t,m in hy_tokens if m.prefix == 'ch')} ({sum(1 for t,m in hy_tokens if m.prefix == 'ch')/total_hy*100:.1f}%)
  sh- + X + hy: {sum(1 for t,m in hy_tokens if m.prefix == 'sh')} ({sum(1 for t,m in hy_tokens if m.prefix == 'sh')/total_hy*100:.1f}%)

INTERPRETATION:
The -hy suffix is NOT a general modifier.
It appears in a HIGHLY SPECIFIC context:
  ch-/sh- + ck/eck/ct + -hy

This is a FORMULAIC CONSTRUCTION, not compositional morphology.
""")
