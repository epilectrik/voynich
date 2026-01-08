"""
Deep analysis of B_SUFFIX_ONLY tokens

These have recognized grammar suffixes (-aiin, -dy, -hy, etc.)
but NO recognized grammar prefix. What are their prefixes?
"""

from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# B Grammar prefixes (known)
B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']

# B Grammar suffixes
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y',
                       'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']

# HT prefixes (for comparison)
HT_PREFIXES = ['yk', 'yp', 'yt', 'yc', 'yd', 'ys', 'op', 'oc', 'oe', 'of',
               'pc', 'tc', 'dc', 'kc', 'sc', 'fc', 'sa', 'so', 'ka', 'ke',
               'ko', 'ta', 'te', 'to', 'po', 'do', 'lo', 'ro']

def get_suffix(tok):
    """Return the matching suffix, longest first."""
    for s in sorted(B_GRAMMAR_SUFFIXES, key=len, reverse=True):
        if tok.endswith(s):
            return s
    return None

def has_b_prefix(tok):
    return any(tok.startswith(p) for p in B_GRAMMAR_PREFIXES)

def has_ht_prefix(tok):
    return any(tok.startswith(p) for p in HT_PREFIXES)

# Collect B_SUFFIX_ONLY tokens
suffix_only_tokens = []
suffix_only_by_section = defaultdict(list)
suffix_only_by_lang = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            section = parts[3].strip('"').strip() if len(parts) > 3 else ''
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''

            if not word or word.startswith('*'):
                continue

            suffix = get_suffix(word)
            if suffix and not has_b_prefix(word) and not has_ht_prefix(word):
                suffix_only_tokens.append({
                    'word': word,
                    'suffix': suffix,
                    'prefix': word[:-len(suffix)] if len(word) > len(suffix) else '',
                    'lang': lang,
                    'section': section,
                    'folio': folio
                })
                suffix_only_by_section[section].append(word)
                suffix_only_by_lang[lang].append(word)

print("=" * 80)
print("B_SUFFIX_ONLY DEEP ANALYSIS")
print("=" * 80)

print(f"\nTotal tokens: {len(suffix_only_tokens)}")
print(f"Unique types: {len(set(e['word'] for e in suffix_only_tokens))}")

# Analyze the prefixes (what comes before the suffix)
prefix_counter = Counter(e['prefix'] for e in suffix_only_tokens)
suffix_counter = Counter(e['suffix'] for e in suffix_only_tokens)

print(f"\n### SUFFIX DISTRIBUTION")
print(f"{'Suffix':<12} {'Count':>8} {'%':>8}")
print("-" * 30)
for suffix, count in suffix_counter.most_common():
    pct = 100 * count / len(suffix_only_tokens)
    print(f"{suffix:<12} {count:>8} {pct:>7.1f}%")

print(f"\n### PREFIX DISTRIBUTION (what comes BEFORE the suffix)")
print(f"{'Prefix':<15} {'Count':>8} {'%':>8} {'Example tokens':<40}")
print("-" * 75)

# Group by prefix, show examples
prefix_examples = defaultdict(list)
for e in suffix_only_tokens:
    if len(prefix_examples[e['prefix']]) < 5:
        prefix_examples[e['prefix']].append(e['word'])

for prefix, count in prefix_counter.most_common(50):
    pct = 100 * count / len(suffix_only_tokens)
    examples = ', '.join(prefix_examples[prefix][:3])
    print(f"{prefix if prefix else '(empty)':<15} {count:>8} {pct:>7.1f}% {examples:<40}")

# Analyze 2-char prefix patterns
print(f"\n### 2-CHAR PREFIX PATTERNS")
prefix_2char = Counter()
for e in suffix_only_tokens:
    p = e['prefix']
    if len(p) >= 2:
        prefix_2char[p[:2]] += 1
    elif len(p) == 1:
        prefix_2char[p] += 1

print(f"{'2-char':<10} {'Count':>8} {'%':>8}")
print("-" * 30)
for p2, count in prefix_2char.most_common(30):
    pct = 100 * count / len(suffix_only_tokens)
    print(f"{p2:<10} {count:>8} {pct:>7.1f}%")

# Check for NEW prefix candidates (high frequency, not in existing lists)
print(f"\n### POTENTIAL NEW PREFIX CANDIDATES")
print("(2-char patterns NOT in B_GRAMMAR or HT prefix lists)")
print("-" * 50)

all_known = set(B_GRAMMAR_PREFIXES) | set(HT_PREFIXES)
for p2, count in prefix_2char.most_common(30):
    if p2 not in all_known and len(p2) == 2:
        pct = 100 * count / len(suffix_only_tokens)
        # Get examples
        examples = [e['word'] for e in suffix_only_tokens if e['prefix'].startswith(p2)][:5]
        print(f"{p2:<10} {count:>8} ({pct:.1f}%)  Examples: {', '.join(examples)}")

# By section
print(f"\n### BY SECTION")
for section in sorted(suffix_only_by_section.keys()):
    tokens = suffix_only_by_section[section]
    print(f"  {section if section else '(none)'}: {len(tokens)} tokens")

# By language
print(f"\n### BY CURRIER LANGUAGE")
for lang in ['A', 'B', '']:
    tokens = suffix_only_by_lang.get(lang, [])
    print(f"  {lang if lang else '(none)'}: {len(tokens)} tokens ({100*len(tokens)/len(suffix_only_tokens):.1f}%)")

# Check if these might be HT variants with grammar suffixes
print(f"\n### COMPOSITIONAL ANALYSIS")
print("Are these HT-like tokens using grammar suffixes?")

# Look for patterns like: y + X + suffix, or consonant clusters + suffix
initial_char = Counter(e['word'][0] if e['word'] else '' for e in suffix_only_tokens)
print(f"\n{'Initial char':<12} {'Count':>8} {'%':>8}")
print("-" * 30)
for char, count in initial_char.most_common(15):
    pct = 100 * count / len(suffix_only_tokens)
    print(f"{char:<12} {count:>8} {pct:>7.1f}%")

# Specific pattern analysis
patterns = {
    'r_initial': [],
    'od_initial': [],
    'ckh_initial': [],
    'dsh_initial': [],
    'cph_initial': [],
    'l_initial': [],
    'a_initial': [],
    'other': []
}

for e in suffix_only_tokens:
    w = e['word']
    if w.startswith('r'):
        patterns['r_initial'].append(w)
    elif w.startswith('od'):
        patterns['od_initial'].append(w)
    elif w.startswith('ckh'):
        patterns['ckh_initial'].append(w)
    elif w.startswith('dsh'):
        patterns['dsh_initial'].append(w)
    elif w.startswith('cph'):
        patterns['cph_initial'].append(w)
    elif w.startswith('l') and not any(w.startswith(p) for p in ['lch', 'lk', 'ls']):
        patterns['l_initial'].append(w)
    elif w.startswith('a'):
        patterns['a_initial'].append(w)
    else:
        patterns['other'].append(w)

print(f"\n### MAJOR PREFIX FAMILIES")
for pattern, tokens in sorted(patterns.items(), key=lambda x: -len(x[1])):
    if len(tokens) > 50:
        types = set(tokens)
        examples = list(types)[:10]
        print(f"\n{pattern}: {len(tokens)} occurrences, {len(types)} types")
        print(f"  Examples: {', '.join(examples)}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
B_SUFFIX_ONLY tokens have grammar suffixes but unrecognized prefixes.

Key findings:
- Total: {len(suffix_only_tokens)} tokens
- Dominant suffixes: {', '.join([f"{s}({c})" for s, c in suffix_counter.most_common(5)])}

Candidate NEW prefix families:
""")

# Final candidate list
candidates = []
for p2, count in prefix_2char.most_common():
    if p2 not in all_known and len(p2) == 2 and count >= 100:
        candidates.append((p2, count))

for p2, count in candidates:
    print(f"  {p2}: {count} occurrences - consider adding to grammar prefix list")

print("\n" + "=" * 80)
