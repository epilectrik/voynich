"""
SPEC-A Part 2: Suffix analysis for semantic mapping.

Tier 4 (SPECULATIVE)
"""

from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

CORE_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = ['daiin', 'aiin', 'ain', 'dy', 'edy', 'ody', 'or', 'eor', 'ar',
            'ol', 'eol', 'al', 'chy', 'hy', 'y', 'ey', 'am', 'om', 'in']

def get_core_prefix(token):
    for p in CORE_PREFIXES:
        if token.startswith(p):
            return p
    return None

def get_suffix(token):
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if token.endswith(s):
            return s
    return None

# Load data
tokens_data = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                if word:
                    tokens_data.append({
                        'token': word,
                        'section': section,
                        'prefix': get_core_prefix(word),
                        'suffix': get_suffix(word)
                    })

print("=" * 80)
print("SPEC-A: SUFFIX SEMANTIC PROFILES")
print("=" * 80)

# 1. Overall suffix frequency
print("\n### 1. SUFFIX FREQUENCY")
print("-" * 60)

suffix_counts = Counter(t['suffix'] for t in tokens_data if t['suffix'])
total_suffixed = sum(suffix_counts.values())

print(f"\n{'SUFFIX':<12} {'Count':>10} {'%':>10}")
print("-" * 35)
for suf, count in suffix_counts.most_common():
    pct = 100 * count / total_suffixed
    print(f"-{suf:<11} {count:>10} {pct:>9.1f}%")

# 2. Suffix by section
print("\n\n### 2. SUFFIX DISTRIBUTION BY SECTION")
print("-" * 60)

suffix_section = defaultdict(Counter)
for t in tokens_data:
    if t['suffix']:
        suffix_section[t['suffix']][t['section']] += 1

print(f"\n{'SUFFIX':<12} {'H%':>10} {'P%':>10} {'T%':>10} {'Primary':>10}")
print("-" * 55)

for suf, _ in suffix_counts.most_common(15):
    total = sum(suffix_section[suf].values())
    h_pct = 100 * suffix_section[suf].get('H', 0) / total
    p_pct = 100 * suffix_section[suf].get('P', 0) / total
    t_pct = 100 * suffix_section[suf].get('T', 0) / total
    primary = max(['H', 'P', 'T'], key=lambda s: suffix_section[suf].get(s, 0))
    print(f"-{suf:<11} {h_pct:>9.1f}% {p_pct:>9.1f}% {t_pct:>9.1f}% {primary:>10}")

# 3. Suffix families (group by ending pattern)
print("\n\n### 3. SUFFIX FAMILIES")
print("-" * 60)

families = {
    '-iin family': ['daiin', 'aiin', 'ain', 'in'],
    '-y family': ['dy', 'edy', 'ody', 'chy', 'hy', 'y', 'ey'],
    '-r family': ['or', 'eor', 'ar'],
    '-l family': ['ol', 'eol', 'al'],
    '-m family': ['am', 'om']
}

for family_name, members in families.items():
    family_total = sum(suffix_counts.get(m, 0) for m in members)
    family_pct = 100 * family_total / total_suffixed
    print(f"\n{family_name}: {family_total} ({family_pct:.1f}%)")
    for m in members:
        count = suffix_counts.get(m, 0)
        if count > 0:
            print(f"  -{m}: {count}")

# 4. Suffix-Prefix affinity matrix
print("\n\n### 4. SUFFIX-PREFIX AFFINITY")
print("-" * 60)
print("Which suffixes prefer which prefixes? (chi-square residuals)")

suffix_prefix = defaultdict(Counter)
for t in tokens_data:
    if t['suffix'] and t['prefix']:
        suffix_prefix[t['suffix']][t['prefix']] += 1

# Calculate expected vs observed for top suffixes
print(f"\n{'SUFFIX':<12}", end='')
for p in CORE_PREFIXES:
    print(f"{p:>8}", end='')
print()
print("-" * 80)

prefix_totals = Counter(t['prefix'] for t in tokens_data if t['prefix'])
total_prefixed = sum(prefix_totals.values())

for suf, _ in suffix_counts.most_common(10):
    suf_total = sum(suffix_prefix[suf].values())
    print(f"-{suf:<11}", end='')
    for p in CORE_PREFIXES:
        observed = suffix_prefix[suf].get(p, 0)
        # Expected under independence
        expected = (prefix_totals[p] / total_prefixed) * suf_total if total_prefixed else 0
        if expected > 0:
            residual = (observed - expected) / (expected ** 0.5)
            # Show + for positive affinity, - for negative
            if residual > 2:
                print(f"{'++':>8}", end='')
            elif residual > 1:
                print(f"{'+':>8}", end='')
            elif residual < -2:
                print(f"{'--':>8}", end='')
            elif residual < -1:
                print(f"{'-':>8}", end='')
            else:
                print(f"{'~':>8}", end='')
        else:
            print(f"{'?':>8}", end='')
    print()

print("\nLegend: ++ strong positive, + positive, ~ neutral, - negative, -- strong negative")

# 5. Semantic grouping hypothesis
print("\n\n### 5. SEMANTIC GROUPING HYPOTHESIS")
print("-" * 60)

print("""
Based on structural patterns, suffixes may encode:

-iin FAMILY (daiin, aiin, ain, in):
  - Concentrated in DA prefix (55% of DA tokens)
  - Possibly marks: QUANTITY/MEASURE or BASE FORM
  - 'daiin' appears to be a fundamental unit marker

-y FAMILY (y, ey, hy, chy, dy, edy, ody):
  - Most diverse family (7 variants)
  - -chy strongly H-concentrated (93%)
  - -hy strongly associated with CT prefix
  - Possibly marks: PROCESSING STATE or QUALITY GRADE

-l FAMILY (ol, eol, al):
  - -eol uniquely P-concentrated (56% in P)
  - -ol is most common suffix overall
  - Possibly marks: FORM/PREPARATION TYPE

-r FAMILY (or, eor, ar):
  - Relatively even distribution
  - Possibly marks: SOURCE/ORIGIN variant

-m FAMILY (am, om):
  - Smallest family
  - Possibly marks: SPECIAL CONDITION
""")

# 6. Middle patterns by suffix
print("\n\n### 6. COMMON TOKEN FORMS BY SUFFIX")
print("-" * 60)

suffix_tokens = defaultdict(Counter)
for t in tokens_data:
    if t['suffix']:
        suffix_tokens[t['suffix']][t['token']] += 1

for suf, _ in suffix_counts.most_common(8):
    print(f"\n-{suf} tokens:")
    for tok, count in suffix_tokens[suf].most_common(5):
        print(f"  {tok}: {count}")
