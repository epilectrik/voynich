"""
Human Track Token Morphology Analysis

Analyze whether the ~11,649 HT types have their own compositional structure
similar to Currier A markers (PREFIX + MIDDLE + SUFFIX).
"""

from collections import Counter, defaultdict
from pathlib import Path
import re

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Grammar tokens (the 479 operational types)
# Based on canonical grammar - tokens that ARE in the grammar
GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct']
GRAMMAR_SUFFIXES = ['aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'al', 'edy', 'y']

# Known high-frequency grammar tokens
GRAMMAR_CORE = {
    'qokaiin', 'chey', 'cheey', 'chedy', 'okaiin', 'dar', 'okal', 'saiin',
    'qokal', 'daiin', 'dol', 'ckhey', 'chol', 'dy', 'cheky', 'tedy', 'ol',
    'aiin', 'checkhy', 'otain', 'shey', 'shol', 'shedy', 'shy', 'shor',
    'qo', 'qok', 'ok', 'al', 'or', 'ar', 'dal', 'qokedy', 'okey', 'okeey',
    'okedy', 'chee', 'cheol', 'ched', 'chor', 'char', 'sho', 'she',
    'qokeey', 'qokain', 'okain', 'sheey', 'sheo', 'otar',
    'oteey', 'otedy', 'okeedy', 'taiin', 'cthaiin', 'cthol', 'cthor', 'cthy',
    'kcheol', 'kchey', 'kcheedy', 'pchedy', 'pchey', 'fchedy', 'fchey',
    's', 'y', 'r', 'l', 'o', 'd', 'k', 'e', 'h', 't', 'c',
    'cheor', 'shar', 'otol', 'otar', 'cthey', 'shol', 'okol',
    'qokchey', 'qokeedy', 'qokain', 'chkal', 'chal', 'shal',
}

def is_grammar_token(tok):
    """Check if token is in the operational grammar."""
    t = tok.lower()
    if t in GRAMMAR_CORE:
        return True
    # Standard grammar prefix
    for p in GRAMMAR_PREFIXES:
        if t.startswith(p) and len(t) > len(p):
            return True
    # L-compounds (B-specific operators)
    if t.startswith('l') and len(t) > 1 and t[1] in 'cks':
        return True
    return False

# Load all tokens
all_tokens = []
by_section = defaultdict(list)
by_language = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            section = parts[3].strip('"').strip() if len(parts) > 3 else ''
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''

            if word and not word.startswith('*'):
                entry = {'word': word, 'lang': lang, 'section': section, 'folio': folio}
                all_tokens.append(entry)
                by_section[section].append(word)
                by_language[lang].append(word)

# Separate grammar vs HT tokens
grammar_tokens = []
ht_tokens = []

for entry in all_tokens:
    if is_grammar_token(entry['word']):
        grammar_tokens.append(entry)
    else:
        ht_tokens.append(entry)

print("=" * 80)
print("HUMAN TRACK TOKEN MORPHOLOGY ANALYSIS")
print("=" * 80)

print(f"\n### CORPUS SPLIT")
print(f"Total tokens: {len(all_tokens)}")
print(f"Grammar tokens: {len(grammar_tokens)} ({100*len(grammar_tokens)/len(all_tokens):.1f}%)")
print(f"HT tokens: {len(ht_tokens)} ({100*len(ht_tokens)/len(all_tokens):.1f}%)")

# Get unique HT types
ht_words = [e['word'] for e in ht_tokens]
ht_types = set(ht_words)
ht_freq = Counter(ht_words)

print(f"\nUnique HT types: {len(ht_types)}")

# ============================================================================
# MORPHOLOGICAL ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("PART 1: MORPHOLOGICAL DECOMPOSITION")
print("=" * 80)

# Common prefixes in HT tokens
prefixes_2 = Counter()
prefixes_3 = Counter()
for w in ht_types:
    if len(w) >= 2:
        prefixes_2[w[:2]] += 1
    if len(w) >= 3:
        prefixes_3[w[:3]] += 1

print(f"\n### TOP 20 HT PREFIXES (2-char)")
for prefix, count in prefixes_2.most_common(20):
    pct = 100 * count / len(ht_types)
    print(f"  {prefix}: {count} types ({pct:.1f}%)")

print(f"\n### TOP 20 HT PREFIXES (3-char)")
for prefix, count in prefixes_3.most_common(20):
    pct = 100 * count / len(ht_types)
    print(f"  {prefix}: {count} types ({pct:.1f}%)")

# Common suffixes in HT tokens
suffixes_2 = Counter()
suffixes_3 = Counter()
suffixes_4 = Counter()
for w in ht_types:
    if len(w) >= 2:
        suffixes_2[w[-2:]] += 1
    if len(w) >= 3:
        suffixes_3[w[-3:]] += 1
    if len(w) >= 4:
        suffixes_4[w[-4:]] += 1

print(f"\n### TOP 20 HT SUFFIXES (2-char)")
for suffix, count in suffixes_2.most_common(20):
    pct = 100 * count / len(ht_types)
    print(f"  {suffix}: {count} types ({pct:.1f}%)")

print(f"\n### TOP 20 HT SUFFIXES (3-char)")
for suffix, count in suffixes_3.most_common(20):
    pct = 100 * count / len(ht_types)
    print(f"  {suffix}: {count} types ({pct:.1f}%)")

print(f"\n### TOP 20 HT SUFFIXES (4-char)")
for suffix, count in suffixes_4.most_common(20):
    pct = 100 * count / len(ht_types)
    print(f"  {suffix}: {count} types ({pct:.1f}%)")

# ============================================================================
# IDENTIFY HT-SPECIFIC MORPHEMES
# ============================================================================

print("\n" + "=" * 80)
print("PART 2: HT-SPECIFIC MORPHEME IDENTIFICATION")
print("=" * 80)

# What prefixes are ENRICHED in HT vs grammar?
grammar_words = [e['word'] for e in grammar_tokens]
grammar_types = set(grammar_words)

grammar_prefixes_2 = Counter()
for w in grammar_types:
    if len(w) >= 2:
        grammar_prefixes_2[w[:2]] += 1

print(f"\n### PREFIX ENRICHMENT (HT vs Grammar)")
print(f"{'Prefix':<8} {'HT Types':>10} {'Grammar':>10} {'HT %':>8} {'Gram %':>8} {'Ratio':>8}")
print("-" * 60)

all_prefixes = set(prefixes_2.keys()) | set(grammar_prefixes_2.keys())
enrichment = []
for p in all_prefixes:
    ht_c = prefixes_2.get(p, 0)
    gr_c = grammar_prefixes_2.get(p, 0)
    ht_pct = 100 * ht_c / len(ht_types) if ht_types else 0
    gr_pct = 100 * gr_c / len(grammar_types) if grammar_types else 0
    ratio = (ht_pct / gr_pct) if gr_pct > 0 else float('inf')
    if ht_c >= 50 or gr_c >= 10:  # Only significant ones
        enrichment.append((p, ht_c, gr_c, ht_pct, gr_pct, ratio))

enrichment.sort(key=lambda x: -x[5])  # Sort by ratio descending
for p, ht_c, gr_c, ht_pct, gr_pct, ratio in enrichment[:20]:
    ratio_str = f"{ratio:.2f}x" if ratio < 100 else "HT-only"
    print(f"{p:<8} {ht_c:>10} {gr_c:>10} {ht_pct:>7.1f}% {gr_pct:>7.1f}% {ratio_str:>8}")

# ============================================================================
# COMPOSITIONAL STRUCTURE TEST
# ============================================================================

print("\n" + "=" * 80)
print("PART 3: COMPOSITIONAL STRUCTURE TEST")
print("=" * 80)

# Define candidate HT morphemes based on frequency
HT_PREFIXES = ['yp', 'op', 'yk', 'yt', 'tp', 'pc', 'tc', 'dc', 'kc', 'ep', 'yc', 'yd', 'sa', 'so', 'ta', 'te', 'ka', 'ke']
HT_SUFFIXES = ['dy', 'ey', 'hy', 'ry', 'ly', 'ty', 'sy', 'ky', 'py', 'ny', 'my', 'cy']

def decompose_ht(token):
    """Try to decompose HT token into prefix + middle + suffix."""
    t = token.lower()

    prefix = None
    suffix = None

    # Check for HT prefix (2-char)
    for p in HT_PREFIXES:
        if t.startswith(p):
            prefix = p
            break

    # Check for HT suffix (2-char)
    for s in HT_SUFFIXES:
        if t.endswith(s):
            suffix = s
            break

    # Extract middle
    start = len(prefix) if prefix else 0
    end = len(t) - len(suffix) if suffix else len(t)
    middle = t[start:end] if end > start else ''

    return prefix, middle, suffix

# Decompose all HT tokens
decomposed = []
has_prefix = 0
has_suffix = 0
has_both = 0
has_neither = 0

for w in ht_types:
    prefix, middle, suffix = decompose_ht(w)
    decomposed.append((w, prefix, middle, suffix))

    if prefix and suffix:
        has_both += 1
    elif prefix:
        has_prefix += 1
    elif suffix:
        has_suffix += 1
    else:
        has_neither += 1

print(f"\n### DECOMPOSITION RESULTS")
print(f"Total HT types: {len(ht_types)}")
print(f"Has both prefix + suffix: {has_both} ({100*has_both/len(ht_types):.1f}%)")
print(f"Has prefix only: {has_prefix} ({100*has_prefix/len(ht_types):.1f}%)")
print(f"Has suffix only: {has_suffix} ({100*has_suffix/len(ht_types):.1f}%)")
print(f"Has neither: {has_neither} ({100*has_neither/len(ht_types):.1f}%)")

# Middle component analysis
middles = Counter()
for w, prefix, middle, suffix in decomposed:
    if middle:
        middles[middle] += 1

print(f"\n### TOP 30 MIDDLE COMPONENTS")
for mid, count in middles.most_common(30):
    print(f"  '{mid}': {count}")

# ============================================================================
# SECTION-SPECIFIC PATTERNS
# ============================================================================

print("\n" + "=" * 80)
print("PART 4: SECTION-SPECIFIC HT PATTERNS")
print("=" * 80)

# HT tokens by section
ht_by_section = defaultdict(list)
for entry in ht_tokens:
    ht_by_section[entry['section']].append(entry['word'])

for section in ['H', 'S', 'B', 'P', 'C', 'Z', 'A', 'T']:
    tokens = ht_by_section.get(section, [])
    if not tokens:
        continue

    types = set(tokens)
    freq = Counter(tokens)

    print(f"\n### SECTION {section}")
    print(f"HT tokens: {len(tokens)}, unique types: {len(types)}")

    # Section-specific prefixes
    sec_prefixes = Counter()
    for w in types:
        if len(w) >= 2:
            sec_prefixes[w[:2]] += 1

    print(f"Top prefixes: ", end="")
    top_p = sec_prefixes.most_common(5)
    print(", ".join([f"{p}({c})" for p, c in top_p]))

    # Section-specific suffixes
    sec_suffixes = Counter()
    for w in types:
        if len(w) >= 2:
            sec_suffixes[w[-2:]] += 1

    print(f"Top suffixes: ", end="")
    top_s = sec_suffixes.most_common(5)
    print(", ".join([f"{s}({c})" for s, c in top_s]))

    # Top tokens
    print(f"Top 10 tokens: ", end="")
    top_t = freq.most_common(10)
    print(", ".join([f"{t}({c})" for t, c in top_t]))

# ============================================================================
# HIGH-FREQUENCY HT TOKEN ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("PART 5: HIGH-FREQUENCY HT TOKENS (freq >= 50)")
print("=" * 80)

high_freq_ht = [(w, c) for w, c in ht_freq.items() if c >= 50]
high_freq_ht.sort(key=lambda x: -x[1])

print(f"\nFound {len(high_freq_ht)} high-frequency HT tokens")
print(f"\n{'Token':<15} {'Count':>8} {'Decomposition':<30}")
print("-" * 60)

for w, count in high_freq_ht[:50]:
    prefix, middle, suffix = decompose_ht(w)
    decomp = f"[{prefix or '-'}] + [{middle or '-'}] + [{suffix or '-'}]"
    print(f"{w:<15} {count:>8} {decomp:<30}")

# ============================================================================
# PATTERN FAMILIES
# ============================================================================

print("\n" + "=" * 80)
print("PART 6: PATTERN FAMILIES IN HT")
print("=" * 80)

# Group by prefix
by_prefix = defaultdict(list)
for w in ht_types:
    if len(w) >= 2:
        by_prefix[w[:2]].append(w)

# Find family structures
print(f"\n### LARGEST PREFIX FAMILIES")
for prefix in sorted(by_prefix.keys(), key=lambda x: -len(by_prefix[x]))[:10]:
    members = by_prefix[prefix]
    print(f"\n{prefix}- family: {len(members)} types")

    # Suffix distribution within family
    family_suffixes = Counter()
    for w in members:
        if len(w) >= 2:
            family_suffixes[w[-2:]] += 1

    print(f"  Suffixes: ", end="")
    for s, c in family_suffixes.most_common(5):
        print(f"{s}({c}) ", end="")
    print()

    # Sample members
    print(f"  Sample: {', '.join(sorted(members)[:10])}")

# ============================================================================
# COMPARISON WITH CURRIER A STRUCTURE
# ============================================================================

print("\n" + "=" * 80)
print("PART 7: COMPARISON WITH CURRIER A MORPHOLOGY")
print("=" * 80)

# Currier A prefixes (from CAS-MORPH)
A_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Check overlap
print(f"\n### PREFIX OVERLAP")
print(f"Currier A prefixes: {A_PREFIXES}")
print(f"\nHT tokens starting with A-prefixes:")
for ap in A_PREFIXES:
    ht_with_prefix = [w for w in ht_types if w.startswith(ap)]
    print(f"  {ap}-: {len(ht_with_prefix)} HT types")

# HT-exclusive prefixes (not in grammar, not in A)
print(f"\n### HT-EXCLUSIVE PREFIXES (high frequency, not A-prefixes)")
for prefix, count in prefixes_2.most_common(30):
    if prefix not in A_PREFIXES and count >= 100:
        # Check if it's enriched in HT
        gr_c = grammar_prefixes_2.get(prefix, 0)
        ratio = (count / len(ht_types)) / (gr_c / len(grammar_types)) if gr_c > 0 else float('inf')
        if ratio > 2:
            print(f"  {prefix}: {count} types, {ratio:.1f}x enriched vs grammar")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
