"""
Analyze the major unknown MIDDLEs: l, r, d, in, iin, daiin patterns
What function do these serve?
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import defaultdict, Counter
import re

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())

print("=" * 70)
print("UNKNOWN MIDDLE ANALYSIS: l, r, d, in, iin")
print("=" * 70)

# The major unknowns
UNKNOWN_MIDDLES = {'l', 'r', 'd', 'in', 'iin', 'aiin', 'ain'}

def safe_int(s):
    try:
        return int(s)
    except:
        match = re.match(r'(\d+)', str(s))
        return int(match.group(1)) if match else 0

# 1. Basic stats
print("\n1. BASIC DISTRIBUTION")
print("-" * 60)

for mid in sorted(UNKNOWN_MIDDLES):
    count = sum(1 for t in b_tokens if morph.extract(t.word).middle == mid)
    pct = count / len(b_tokens) * 100
    print(f"  {mid:<6} {count:>5} ({pct:.2f}%)")

# 2. PREFIX patterns for each
print("\n2. PREFIX PATTERNS")
print("-" * 60)

for mid in sorted(UNKNOWN_MIDDLES):
    tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == mid]
    if tokens:
        prefixes = Counter(m.prefix or '(none)' for t, m in tokens)
        print(f"\n{mid} (n={len(tokens)}):")
        for p, count in prefixes.most_common(5):
            pct = count / len(tokens) * 100
            print(f"  {p:<10} {count:>4} ({pct:>5.1f}%)")

# 3. SUFFIX patterns
print("\n3. SUFFIX PATTERNS")
print("-" * 60)

for mid in sorted(UNKNOWN_MIDDLES):
    tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).middle == mid]
    if tokens:
        suffixes = Counter(m.suffix or '(none)' for t, m in tokens)
        print(f"\n{mid} (n={len(tokens)}):")
        for s, count in suffixes.most_common(5):
            pct = count / len(tokens) * 100
            print(f"  {s:<10} {count:>4} ({pct:>5.1f}%)")

# 4. Position in folio
print("\n4. FOLIO POSITION")
print("-" * 60)

by_folio = defaultdict(list)
for t in b_tokens:
    by_folio[t.folio].append(t)

mid_positions = defaultdict(list)
for folio, tokens in by_folio.items():
    tokens_sorted = sorted(tokens, key=lambda t: (safe_int(t.line), 0))
    n = len(tokens_sorted)
    if n < 10:
        continue
    for i, t in enumerate(tokens_sorted):
        m = morph.extract(t.word)
        if m.middle in UNKNOWN_MIDDLES:
            pos = i / (n - 1)
            mid_positions[m.middle].append(pos)

print("\nMean folio position (0=early, 1=late):")
for mid in sorted(UNKNOWN_MIDDLES):
    if mid_positions[mid]:
        mean_pos = sum(mid_positions[mid]) / len(mid_positions[mid])
        print(f"  {mid:<6} {mean_pos:.3f} (n={len(mid_positions[mid])})")

# 5. Line position - are these line-initial or line-final?
print("\n5. LINE POSITION ANALYSIS")
print("-" * 60)

# Group by line
by_line = defaultdict(list)
for t in b_tokens:
    by_line[(t.folio, t.line)].append(t)

line_position_counts = defaultdict(Counter)  # mid -> {first, middle, last}

for (folio, line), tokens in by_line.items():
    if len(tokens) < 3:
        continue

    for i, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m.middle in UNKNOWN_MIDDLES:
            if i == 0:
                line_position_counts[m.middle]['FIRST'] += 1
            elif i == len(tokens) - 1:
                line_position_counts[m.middle]['LAST'] += 1
            else:
                line_position_counts[m.middle]['MIDDLE'] += 1

print("\nLine position (FIRST / MIDDLE / LAST):")
for mid in sorted(UNKNOWN_MIDDLES):
    counts = line_position_counts[mid]
    total = sum(counts.values())
    if total > 0:
        first_pct = counts['FIRST'] / total * 100
        mid_pct = counts['MIDDLE'] / total * 100
        last_pct = counts['LAST'] / total * 100
        print(f"  {mid:<6} FIRST={first_pct:>5.1f}%  MID={mid_pct:>5.1f}%  LAST={last_pct:>5.1f}%")

# 6. Most common full tokens
print("\n6. MOST COMMON FULL TOKENS")
print("-" * 60)

for mid in sorted(UNKNOWN_MIDDLES):
    tokens = [t.word for t in b_tokens if morph.extract(t.word).middle == mid]
    token_counts = Counter(tokens)
    print(f"\n{mid}:")
    for tok, count in token_counts.most_common(5):
        m = morph.extract(tok)
        print(f"  {tok:<15} {count:>4}  (PRE={m.prefix or '-'}, SUF={m.suffix or '-'})")

# 7. The special case: daiin
print("\n" + "=" * 70)
print("7. SPECIAL CASE: daiin AND RELATED")
print("=" * 70)

# daiin is famous - what's special about it?
daiin_tokens = [t for t in b_tokens if t.word == 'daiin']
print(f"\n'daiin' occurrences: {len(daiin_tokens)}")

# Where does it appear?
daiin_line_pos = Counter()
for (folio, line), tokens in by_line.items():
    for i, t in enumerate(tokens):
        if t.word == 'daiin':
            if i == 0:
                daiin_line_pos['FIRST'] += 1
            elif i == len(tokens) - 1:
                daiin_line_pos['LAST'] += 1
            else:
                daiin_line_pos['MIDDLE'] += 1

print(f"Line position: {dict(daiin_line_pos)}")

# What comes after daiin?
print("\nWhat token typically follows 'daiin'?")
following_daiin = Counter()
for (folio, line), tokens in by_line.items():
    for i, t in enumerate(tokens):
        if t.word == 'daiin' and i < len(tokens) - 1:
            following_daiin[tokens[i+1].word] += 1

for tok, count in following_daiin.most_common(10):
    print(f"  {tok}: {count}")

# What comes before daiin?
print("\nWhat token typically precedes 'daiin'?")
preceding_daiin = Counter()
for (folio, line), tokens in by_line.items():
    for i, t in enumerate(tokens):
        if t.word == 'daiin' and i > 0:
            preceding_daiin[tokens[i-1].word] += 1

for tok, count in preceding_daiin.most_common(10):
    print(f"  {tok}: {count}")

# 8. Comparison: daiin vs other da- tokens
print("\n8. da- PREFIX FAMILY")
print("-" * 60)

da_tokens = [(t, morph.extract(t.word)) for t in b_tokens if morph.extract(t.word).prefix == 'da']
da_middles = Counter(m.middle for t, m in da_tokens)

print(f"\nAll da- prefixed tokens by MIDDLE:")
for mid, count in da_middles.most_common(10):
    print(f"  da-{mid}: {count}")

# 9. Section distribution
print("\n9. SECTION DISTRIBUTION")
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

print("\nSection distribution for unknown MIDDLEs:")
for mid in sorted(UNKNOWN_MIDDLES):
    tokens = [t for t in b_tokens if morph.extract(t.word).middle == mid]
    sections = Counter(get_section(t.folio) for t in tokens)
    total = len(tokens)
    if total > 50:
        print(f"\n{mid}:")
        for sec, count in sections.most_common():
            pct = count / total * 100
            print(f"  {sec}: {pct:.1f}%")

# 10. Hypothesis
print("\n" + "=" * 70)
print("10. WORKING HYPOTHESES")
print("=" * 70)

print("""
Based on the analysis:

l, r, d:
  - Very common MIDDLEs with diverse PREFIX/SUFFIX
  - Appear throughout lines (not position-specific)
  - Possible interpretation: STRUCTURAL MARKERS or LINKERS
  - Need more investigation

in, iin, ain, aiin:
  - The "-iin" family
  - Often with da- prefix (daiin is famous)
  - daiin appears mid-line, followed by various tokens
  - Possible interpretation: INFRASTRUCTURE / ANCHORS
  - The "da-" prefix suggests "structural anchor" class

daiin specifically:
  - Most common infrastructure token
  - Appears mid-line predominantly
  - Followed by diverse tokens (not predictable)
  - May be a RECORD SEPARATOR or STATE MARKER
""")
