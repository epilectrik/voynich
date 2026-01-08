"""
Post-Recovery Unexplained Token Audit

After fixing damaged tokens, what remains truly unexplained?
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib import load_transcription

# All known morphological components
B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y', 'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']
HT_PREFIXES = ['yk', 'yp', 'yt', 'yc', 'yd', 'ys', 'op', 'oc', 'oe', 'of', 'pc', 'tc', 'dc', 'kc', 'sc', 'fc', 'sa', 'so', 'ka', 'ke', 'ko', 'ta', 'te', 'to', 'po', 'do', 'lo', 'ro']
HT_SUFFIXES = ['dy', 'ey', 'hy', 'ry', 'ly', 'ty', 'sy', 'ky', 'ny', 'my', 'in', 'ir', 'im', 'il', 'ar', 'or', 'er', 'al', 'ol', 'el', 'am', 'om', 'an', 'on', 'as', 'os', 'es']

# Extended/cluster prefixes we identified
CLUSTER_PREFIXES = ['ck', 'ckh', 'ds', 'dsh', 'cp', 'cph', 'ks', 'ksh', 'ts', 'tsh', 'ps', 'psh']

# Single-char tokens that are probably just initials/fragments
SINGLE_CHARS = set('abcdefghijklmnopqrstuvwxyz')

def classify_token_detailed(word):
    """Detailed classification of a token."""
    if not word:
        return 'EMPTY'

    if '*' in word:
        return 'DAMAGED'

    if len(word) == 1:
        return 'SINGLE_CHAR'

    # Check for B grammar components
    has_b_prefix = any(word.startswith(p) for p in B_GRAMMAR_PREFIXES)
    has_b_suffix = any(word.endswith(s) for s in B_GRAMMAR_SUFFIXES)
    has_cluster_prefix = any(word.startswith(p) for p in CLUSTER_PREFIXES)

    # Check for HT components
    has_ht_prefix = any(word.startswith(p) for p in HT_PREFIXES)
    has_ht_suffix = any(word.endswith(s) for s in HT_SUFFIXES)

    # Classify
    if has_b_prefix and has_b_suffix:
        return 'B_FULL'
    elif has_b_prefix:
        return 'B_PREFIX_ONLY'
    elif has_b_suffix and has_cluster_prefix:
        return 'CLUSTER_VARIANT'
    elif has_b_suffix:
        return 'B_SUFFIX_ONLY'
    elif has_ht_prefix and has_ht_suffix:
        return 'HT_FULL'
    elif has_ht_prefix:
        return 'HT_PREFIX_ONLY'
    elif has_ht_suffix:
        return 'HT_SUFFIX_ONLY'
    else:
        return 'TRUE_ORPHAN'

# Load with HIGH recovery
entries = load_transcription(apply_recovery=True, min_confidence='HIGH', include_metadata=True)

print("=" * 70)
print("POST-RECOVERY UNEXPLAINED TOKEN AUDIT")
print("=" * 70)

# Classify all tokens
classifications = defaultdict(list)
for e in entries:
    cat = classify_token_detailed(e['word'])
    classifications[cat].append(e)

# Summary
print("\n### CLASSIFICATION SUMMARY")
print(f"\n{'Category':<20} {'Tokens':>10} {'Types':>10} {'%':>8}")
print("-" * 50)

total = len(entries)
for cat in ['B_FULL', 'B_PREFIX_ONLY', 'B_SUFFIX_ONLY', 'CLUSTER_VARIANT',
            'HT_FULL', 'HT_PREFIX_ONLY', 'HT_SUFFIX_ONLY',
            'SINGLE_CHAR', 'DAMAGED', 'TRUE_ORPHAN']:
    tokens = classifications[cat]
    types = len(set(e['word'] for e in tokens))
    pct = 100 * len(tokens) / total
    print(f"{cat:<20} {len(tokens):>10} {types:>10} {pct:>7.1f}%")

# Focus on TRUE_ORPHAN
orphans = classifications['TRUE_ORPHAN']
print(f"\n" + "=" * 70)
print(f"TRUE ORPHANS: {len(orphans)} tokens, {len(set(e['word'] for e in orphans))} types")
print("=" * 70)

# Analyze orphan patterns
orphan_freq = Counter(e['word'] for e in orphans)
orphan_by_currier = Counter(e['currier'] for e in orphans)
orphan_by_section = Counter(e['section'] for e in orphans)

print(f"\n### BY CURRIER LANGUAGE")
for lang, count in orphan_by_currier.most_common():
    print(f"  {lang if lang else '(none)'}: {count} ({100*count/len(orphans):.1f}%)")

print(f"\n### BY SECTION")
for section, count in orphan_by_section.most_common(10):
    print(f"  {section if section else '(none)'}: {count} ({100*count/len(orphans):.1f}%)")

# Pattern analysis
print(f"\n### ORPHAN PATTERNS")

patterns = {
    'consonant_only': [],  # all consonants
    'vowel_only': [],      # all vowels
    'starts_with_vowel': [],
    'ends_with_consonant_cluster': [],
    'very_short': [],      # 2 chars
    'very_long': [],       # 10+ chars
    'has_doubled_char': [],
    'other': []
}

vowels = set('aeiou')
consonants = set('bcdfghjklmnpqrstvwxyz')

for tok in set(e['word'] for e in orphans):
    chars = set(tok)

    if chars <= consonants:
        patterns['consonant_only'].append(tok)
    elif chars <= vowels:
        patterns['vowel_only'].append(tok)
    elif len(tok) == 2:
        patterns['very_short'].append(tok)
    elif len(tok) >= 10:
        patterns['very_long'].append(tok)
    elif tok[0] in vowels:
        patterns['starts_with_vowel'].append(tok)
    elif any(tok[i] == tok[i+1] for i in range(len(tok)-1)):
        patterns['has_doubled_char'].append(tok)
    else:
        patterns['other'].append(tok)

print(f"\n{'Pattern':<30} {'Types':>8} {'Occurrences':>12}")
print("-" * 55)

for pattern, tokens in sorted(patterns.items(), key=lambda x: -len(x[1])):
    total_occ = sum(orphan_freq[t] for t in tokens)
    examples = sorted(tokens, key=lambda t: -orphan_freq[t])[:5]
    print(f"{pattern:<30} {len(tokens):>8} {total_occ:>12}")
    if examples:
        print(f"  Examples: {', '.join([f'{t}({orphan_freq[t]})' for t in examples])}")

# Top orphans
print(f"\n### TOP 50 TRUE ORPHANS")
print(f"{'Token':<20} {'Freq':>6} {'Len':>4} {'Pattern':<20}")
print("-" * 55)

for tok, freq in orphan_freq.most_common(50):
    # Determine pattern
    chars = set(tok)
    if chars <= consonants:
        pat = 'consonant_only'
    elif chars <= vowels:
        pat = 'vowel_only'
    elif tok[0] in vowels:
        pat = 'starts_vowel'
    elif len(tok) == 2:
        pat = 'very_short'
    else:
        pat = 'other'

    print(f"{tok:<20} {freq:>6} {len(tok):>4} {pat:<20}")

# Check if any orphans look like they should be grammar
print(f"\n### ORPHANS THAT LOOK GRAMMAR-LIKE")
print("(Have recognizable substrings but don't match prefix+suffix)")

grammar_like = []
for tok in set(e['word'] for e in orphans):
    # Check for partial matches
    has_partial_prefix = any(p in tok for p in B_GRAMMAR_PREFIXES)
    has_partial_suffix = any(s in tok for s in B_GRAMMAR_SUFFIXES)

    if has_partial_prefix or has_partial_suffix:
        grammar_like.append((tok, orphan_freq[tok]))

grammar_like.sort(key=lambda x: -x[1])
print(f"\nFound {len(grammar_like)} grammar-like orphans")
print(f"\nTop 20:")
for tok, freq in grammar_like[:20]:
    print(f"  {tok:<20} {freq:>6}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

explained = total - len(orphans) - len(classifications['DAMAGED']) - len(classifications['SINGLE_CHAR'])
print(f"""
Total tokens: {total}
  Explained (grammar + HT): {explained} ({100*explained/total:.1f}%)
  Single chars: {len(classifications['SINGLE_CHAR'])} ({100*len(classifications['SINGLE_CHAR'])/total:.2f}%)
  Still damaged: {len(classifications['DAMAGED'])} ({100*len(classifications['DAMAGED'])/total:.2f}%)
  TRUE ORPHANS: {len(orphans)} ({100*len(orphans)/total:.2f}%)

TRUE ORPHAN breakdown:
  Consonant clusters: {len(patterns['consonant_only'])} types
  Very short (2 char): {len(patterns['very_short'])} types
  Starts with vowel: {len(patterns['starts_with_vowel'])} types
  Other patterns: {len(patterns['other'])} types
""")
