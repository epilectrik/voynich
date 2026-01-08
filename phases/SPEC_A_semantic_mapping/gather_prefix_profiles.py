"""
SPEC-A: Gather detailed profiles of each PREFIX family for speculative semantic mapping.

Tier 4 (SPECULATIVE) - No constraints derived, exploratory only.
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

def get_middle(token, prefix, suffix):
    """Extract middle portion between prefix and suffix."""
    if not prefix:
        return None
    start = len(prefix)
    end = len(token) - len(suffix) if suffix else len(token)
    if end > start:
        return token[start:end]
    return None

# Load all Currier A tokens with metadata
tokens_data = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                if word:
                    tokens_data.append({
                        'token': word,
                        'folio': folio,
                        'section': section,
                        'prefix': get_core_prefix(word),
                        'suffix': get_suffix(word)
                    })

# Add middle extraction
for t in tokens_data:
    t['middle'] = get_middle(t['token'], t['prefix'], t['suffix'])

print("=" * 80)
print("SPEC-A: PREFIX FAMILY PROFILES")
print("=" * 80)
print("\nTier 4 (SPECULATIVE) - Exploratory semantic mapping\n")

# 1. Basic counts
print("### 1. PREFIX FREQUENCY AND SECTION DISTRIBUTION")
print("-" * 60)

prefix_section = {p: Counter() for p in CORE_PREFIXES}
prefix_total = Counter()

for t in tokens_data:
    if t['prefix']:
        prefix_section[t['prefix']][t['section']] += 1
        prefix_total[t['prefix']] += 1

print(f"\n{'PREFIX':<8} {'Total':>8} {'H%':>8} {'P%':>8} {'T%':>8} {'Primary':>10}")
print("-" * 55)

for p in CORE_PREFIXES:
    total = prefix_total[p]
    if total > 0:
        h_pct = 100 * prefix_section[p].get('H', 0) / total
        p_pct = 100 * prefix_section[p].get('P', 0) / total
        t_pct = 100 * prefix_section[p].get('T', 0) / total
        primary = max(['H', 'P', 'T'], key=lambda s: prefix_section[p].get(s, 0))
        print(f"{p:<8} {total:>8} {h_pct:>7.1f}% {p_pct:>7.1f}% {t_pct:>7.1f}% {primary:>10}")

# 2. Suffix associations
print("\n\n### 2. PREFIX x SUFFIX ASSOCIATIONS")
print("-" * 60)

prefix_suffix = {p: Counter() for p in CORE_PREFIXES}
for t in tokens_data:
    if t['prefix'] and t['suffix']:
        prefix_suffix[t['prefix']][t['suffix']] += 1

for p in CORE_PREFIXES:
    if prefix_total[p] > 100:
        print(f"\n{p.upper()} family - top suffixes:")
        total_with_suffix = sum(prefix_suffix[p].values())
        for suf, count in prefix_suffix[p].most_common(5):
            pct = 100 * count / total_with_suffix if total_with_suffix else 0
            print(f"  -{suf}: {count} ({pct:.1f}%)")

# 3. Middle diversity
print("\n\n### 3. MIDDLE DIVERSITY BY PREFIX")
print("-" * 60)

prefix_middles = {p: Counter() for p in CORE_PREFIXES}
for t in tokens_data:
    if t['prefix'] and t['middle']:
        prefix_middles[t['prefix']][t['middle']] += 1

print(f"\n{'PREFIX':<8} {'Unique Middles':>15} {'Top Middle':>15} {'Top %':>10}")
print("-" * 55)

for p in CORE_PREFIXES:
    middles = prefix_middles[p]
    if middles:
        unique = len(middles)
        top_mid, top_count = middles.most_common(1)[0] if middles else ('', 0)
        total = sum(middles.values())
        top_pct = 100 * top_count / total if total else 0
        print(f"{p:<8} {unique:>15} {top_mid:>15} {top_pct:>9.1f}%")

# 4. Token examples
print("\n\n### 4. REPRESENTATIVE TOKENS BY PREFIX")
print("-" * 60)

prefix_tokens = {p: Counter() for p in CORE_PREFIXES}
for t in tokens_data:
    if t['prefix']:
        prefix_tokens[t['prefix']][t['token']] += 1

for p in CORE_PREFIXES:
    tokens = prefix_tokens[p]
    if tokens:
        print(f"\n{p.upper()} family - most common tokens:")
        for tok, count in tokens.most_common(8):
            print(f"  {tok}: {count}")

# 5. Co-occurrence in mixed entries (which prefixes appear together?)
print("\n\n### 5. PREFIX CO-OCCURRENCE (in mixed entries)")
print("-" * 60)

# Group by entry
entries = defaultdict(lambda: {'tokens': [], 'section': ''})
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 11:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                line_num = parts[11].strip('"').strip()
                if word:
                    key = f"{folio}_{line_num}"
                    entries[key]['tokens'].append(word)
                    entries[key]['section'] = section

# Find prefix pairs
pair_counts = Counter()
for entry_id, data in entries.items():
    prefixes = set()
    for t in data['tokens']:
        p = get_core_prefix(t)
        if p:
            prefixes.add(p)
    if len(prefixes) >= 2:
        for p1 in prefixes:
            for p2 in prefixes:
                if p1 < p2:
                    pair_counts[(p1, p2)] += 1

print("\nMost common PREFIX pairs in mixed entries:")
for pair, count in pair_counts.most_common(15):
    print(f"  {pair[0]} + {pair[1]}: {count}")

# 6. Section-specific patterns
print("\n\n### 6. SECTION-SPECIFIC PREFIX DOMINANCE")
print("-" * 60)

for section in ['H', 'P', 'T']:
    section_tokens = [t for t in tokens_data if t['section'] == section and t['prefix']]
    if section_tokens:
        prefix_counts = Counter(t['prefix'] for t in section_tokens)
        total = sum(prefix_counts.values())
        print(f"\nSection {section} ({total} prefix tokens):")
        for p, count in prefix_counts.most_common():
            pct = 100 * count / total
            print(f"  {p}: {count} ({pct:.1f}%)")

print("\n\n" + "=" * 80)
print("SYNTHESIS: STRUCTURAL SIGNATURES FOR SEMANTIC MAPPING")
print("=" * 80)

print("""
Based on the above data, each PREFIX has a distinct structural profile:

STRUCTURAL SIGNATURES:
""")

# Generate signatures
for p in CORE_PREFIXES:
    total = prefix_total[p]
    if total > 100:
        # Section concentration
        h_pct = 100 * prefix_section[p].get('H', 0) / total
        p_pct = 100 * prefix_section[p].get('P', 0) / total
        t_pct = 100 * prefix_section[p].get('T', 0) / total
        primary = max(['H', 'P', 'T'], key=lambda s: prefix_section[p].get(s, 0))

        # Top suffix
        top_suf = prefix_suffix[p].most_common(1)[0][0] if prefix_suffix[p] else 'none'

        # Middle diversity
        mid_diversity = len(prefix_middles[p])

        # Top token
        top_tok = prefix_tokens[p].most_common(1)[0][0] if prefix_tokens[p] else ''

        print(f"{p.upper()}:")
        print(f"  Section: {primary} ({max(h_pct, p_pct, t_pct):.0f}%)")
        print(f"  Top suffix: -{top_suf}")
        print(f"  Middle diversity: {mid_diversity} forms")
        print(f"  Exemplar: {top_tok}")
        print()
