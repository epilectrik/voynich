"""
Exhaustive Residue Audit: Find ALL unaccounted-for tokens

Classifications:
1. B_GRAMMAR - in 49-class grammar vocabulary
2. HT_COMPOSITIONAL - fits HT_PREFIX + MIDDLE + SUFFIX
3. HT_NON_COMPOSITIONAL - recognized HT prefix but doesn't decompose cleanly
4. A_MARKER - has Currier A marker prefix
5. AZC_UNIQUE - in AZC sections, unique vocabulary
6. SINGLE_CHAR - single character tokens
7. UNCLASSIFIED - fits NONE of the above
"""

from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# B Grammar - 49 class core vocabulary (approximate - high frequency tokens)
B_GRAMMAR_CORE = {
    'daiin', 'aiin', 'chedy', 'chey', 'ol', 'dy', 'qokaiin', 'qokedy',
    'qokeey', 'qokey', 'shedy', 'sheedy', 'shey', 'chol', 'chor',
    'okaiin', 'okedy', 'okeey', 'okey', 'dar', 'dal', 'ar', 'or', 'al',
    'otedy', 'oteey', 'otey', 'qol', 'sho', 'cho', 'dol', 'chy', 'shy',
    'cheol', 'sheol', 'okeol', 'qokeol', 'cheor', 'sheor', 'cthy',
    'cthor', 'cthol', 'cthey', 'lchedy', 'lchey', 'lkeedy', 'lkey',
    'okain', 'otain', 'chain', 'shain', 'kaiin', 'taiin', 'saiin',
    's', 'y', 'r', 'l', 'o', 'd', 'k', 'e', 'h', 't', 'c', 'a', 'n', 'i',
    'qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'ct',
}

# Expand with common variants
B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y',
                       'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']

# HT Prefixes (disjoint from A/B)
HT_PREFIXES = ['yk', 'yp', 'yt', 'yc', 'yd', 'ys',  # y-initial
               'op', 'oc', 'oe', 'of',              # o-initial (not ok/ot/ol)
               'pc', 'tc', 'dc', 'kc', 'sc', 'fc',  # Xc patterns
               'sa', 'so', 'ka', 'ke', 'ko',        # consonant + vowel
               'ta', 'te', 'to', 'po', 'do', 'lo', 'ro']

HT_SUFFIXES = ['dy', 'ey', 'hy', 'ry', 'ly', 'ty', 'sy', 'ky', 'ny', 'my',
               'in', 'ir', 'im', 'il', 'ar', 'or', 'er', 'al', 'ol', 'el',
               'am', 'om', 'an', 'on', 'as', 'os', 'es']

# A Marker prefixes
A_MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# AZC sections
AZC_SECTIONS = ['A', 'Z', 'C']

def classify_token(tok, lang, section):
    """Classify a single token."""
    t = tok.lower().strip()

    # Single character
    if len(t) == 1:
        return 'SINGLE_CHAR'

    # Empty or invalid
    if not t or t.startswith('*'):
        return 'INVALID'

    # Check B grammar core
    if t in B_GRAMMAR_CORE:
        return 'B_GRAMMAR_CORE'

    # Check B grammar by prefix+suffix pattern
    has_b_prefix = any(t.startswith(p) for p in B_GRAMMAR_PREFIXES)
    has_b_suffix = any(t.endswith(s) for s in B_GRAMMAR_SUFFIXES)
    if has_b_prefix and has_b_suffix:
        return 'B_GRAMMAR_EXTENDED'

    # Check HT compositional
    has_ht_prefix = any(t.startswith(p) for p in HT_PREFIXES)
    has_ht_suffix = any(t.endswith(s) for s in HT_SUFFIXES)

    if has_ht_prefix:
        if has_ht_suffix:
            return 'HT_COMPOSITIONAL'
        else:
            return 'HT_PREFIX_ONLY'

    # Check A marker (only in A sections)
    if lang == 'A':
        has_a_marker = any(t.startswith(p) for p in A_MARKER_PREFIXES)
        if has_a_marker:
            return 'A_MARKER'

    # AZC unique
    if section in AZC_SECTIONS:
        return 'AZC_UNCLASSIFIED'

    # B grammar prefix only (no recognized suffix)
    if has_b_prefix:
        return 'B_PREFIX_ONLY'

    # B grammar suffix only (no recognized prefix)
    if has_b_suffix:
        return 'B_SUFFIX_ONLY'

    return 'UNCLASSIFIED'

# Load and classify all tokens
classifications = Counter()
unclassified_tokens = Counter()
ht_prefix_only = Counter()
b_prefix_only = Counter()
b_suffix_only = Counter()

by_section = defaultdict(Counter)
by_lang = defaultdict(Counter)

total = 0

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            section = parts[3].strip('"').strip() if len(parts) > 3 else ''

            if not word or word.startswith('*'):
                continue

            total += 1
            cls = classify_token(word, lang, section)
            classifications[cls] += 1
            by_section[section][cls] += 1
            by_lang[lang][cls] += 1

            if cls == 'UNCLASSIFIED':
                unclassified_tokens[word] += 1
            elif cls == 'HT_PREFIX_ONLY':
                ht_prefix_only[word] += 1
            elif cls == 'B_PREFIX_ONLY':
                b_prefix_only[word] += 1
            elif cls == 'B_SUFFIX_ONLY':
                b_suffix_only[word] += 1

print("=" * 80)
print("EXHAUSTIVE RESIDUE AUDIT")
print("=" * 80)

print(f"\nTotal tokens: {total}")
print(f"\n### CLASSIFICATION BREAKDOWN")
print(f"{'Class':<25} {'Count':>10} {'%':>8}")
print("-" * 45)

for cls, count in sorted(classifications.items(), key=lambda x: -x[1]):
    pct = 100 * count / total
    print(f"{cls:<25} {count:>10} {pct:>7.2f}%")

# Truly unclassified
print(f"\n### TRULY UNCLASSIFIED TOKENS ({len(unclassified_tokens)} types)")
print(f"{'Token':<20} {'Freq':>8}")
print("-" * 30)
for tok, freq in unclassified_tokens.most_common(50):
    print(f"{tok:<20} {freq:>8}")

# HT prefix only (no suffix)
print(f"\n### HT PREFIX ONLY - No recognized suffix ({len(ht_prefix_only)} types)")
print(f"{'Token':<20} {'Freq':>8}")
print("-" * 30)
for tok, freq in ht_prefix_only.most_common(30):
    print(f"{tok:<20} {freq:>8}")

# B prefix only
print(f"\n### B PREFIX ONLY - No recognized suffix ({len(b_prefix_only)} types)")
print(f"{'Token':<20} {'Freq':>8}")
print("-" * 30)
for tok, freq in b_prefix_only.most_common(30):
    print(f"{tok:<20} {freq:>8}")

# B suffix only
print(f"\n### B SUFFIX ONLY - No recognized prefix ({len(b_suffix_only)} types)")
print(f"{'Token':<20} {'Freq':>8}")
print("-" * 30)
for tok, freq in b_suffix_only.most_common(30):
    print(f"{tok:<20} {freq:>8}")

# By language
print(f"\n### BY CURRIER LANGUAGE")
for lang in ['A', 'B', '']:
    if lang in by_lang:
        lang_total = sum(by_lang[lang].values())
        print(f"\n{lang if lang else 'UNASSIGNED'} (n={lang_total}):")
        for cls, count in sorted(by_lang[lang].items(), key=lambda x: -x[1])[:10]:
            pct = 100 * count / lang_total
            print(f"  {cls:<25} {count:>8} ({pct:.1f}%)")

# Summary
print("\n" + "=" * 80)
print("SUMMARY: WHERE TOKENS ARE HIDING")
print("=" * 80)

unclassified_pct = 100 * classifications.get('UNCLASSIFIED', 0) / total
ht_prefix_only_pct = 100 * classifications.get('HT_PREFIX_ONLY', 0) / total
b_prefix_only_pct = 100 * classifications.get('B_PREFIX_ONLY', 0) / total
b_suffix_only_pct = 100 * classifications.get('B_SUFFIX_ONLY', 0) / total
azc_unclass_pct = 100 * classifications.get('AZC_UNCLASSIFIED', 0) / total

print(f"""
FULLY CLASSIFIED:
  B_GRAMMAR_CORE:      {100 * classifications.get('B_GRAMMAR_CORE', 0) / total:.1f}%
  B_GRAMMAR_EXTENDED:  {100 * classifications.get('B_GRAMMAR_EXTENDED', 0) / total:.1f}%
  HT_COMPOSITIONAL:    {100 * classifications.get('HT_COMPOSITIONAL', 0) / total:.1f}%
  A_MARKER:            {100 * classifications.get('A_MARKER', 0) / total:.1f}%
  SINGLE_CHAR:         {100 * classifications.get('SINGLE_CHAR', 0) / total:.1f}%

PARTIALLY CLASSIFIED (have prefix OR suffix, not both):
  HT_PREFIX_ONLY:      {ht_prefix_only_pct:.1f}% ({len(ht_prefix_only)} types)
  B_PREFIX_ONLY:       {b_prefix_only_pct:.1f}% ({len(b_prefix_only)} types)
  B_SUFFIX_ONLY:       {b_suffix_only_pct:.1f}% ({len(b_suffix_only)} types)

UNCLASSIFIED:
  AZC_UNCLASSIFIED:    {azc_unclass_pct:.1f}%
  TRUE ORPHANS:        {unclassified_pct:.1f}% ({len(unclassified_tokens)} types)
""")

print("=" * 80)
