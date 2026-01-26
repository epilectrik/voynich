#!/usr/bin/env python3
"""
Check: How many "prefix-less" tokens are actually SUFFIX-ONLY closure tokens?

Per C509.a: 31% of RI tokens are SUFFIX-only (no PREFIX)
Per C498-CHAR-A-CLOSURE: These are closure tokens, not vocabulary items.
"""

import csv
from collections import Counter

ARTICULATORS = ['y', 'k', 'l', 'p', 'd', 'f', 'r', 's', 't']

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES_SET = set(SUFFIXES)

def find_prefix(token):
    for p in PREFIXES:
        if token.startswith(p) and len(token) > len(p):
            return p, token[len(p):]
    return None, token

def has_prefix(token):
    prefix, _ = find_prefix(token)
    if prefix:
        return True
    for art in ARTICULATORS:
        if token.startswith(art) and len(token) > len(art):
            after_art = token[len(art):]
            prefix, _ = find_prefix(after_art)
            if prefix:
                return True
    return False

def is_suffix_only(token):
    """Check if token is just a suffix (or concatenation of suffixes)."""
    # Direct suffix match
    if token in SUFFIXES_SET:
        return True
    # Check for suffix+suffix patterns like 'aiin' which is itself a suffix
    # or 'ody' = o + dy (both suffixes)
    return False

def classify_prefixless(token):
    """Classify a prefix-less token."""
    # Is it exactly a suffix?
    if token in SUFFIXES_SET:
        return 'SUFFIX_ONLY'

    # Is it a very short token that looks like suffix material?
    if len(token) <= 2 and all(c in 'aeioylrdsmn' for c in token):
        return 'SUFFIX_LIKE'

    # Does it start with a pattern that might be an unrecognized prefix?
    potential_prefixes = ['ck', 'cp', 'cf', 'op', 'oc', 'od', 'sy', 'py', 'fy']
    for pp in potential_prefixes:
        if token.startswith(pp) and len(token) > len(pp):
            return f'POTENTIAL_PREFIX_{pp}'

    # Otherwise it's genuine vocabulary
    return 'VOCABULARY'

# Collect data
prefixless_tokens = []

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        if not has_prefix(word):
            line_final = row.get('line_final', '').strip() == '1'
            prefixless_tokens.append({
                'word': word,
                'line_final': line_final,
                'category': classify_prefixless(word)
            })

print("="*70)
print("PREFIX-LESS TOKEN CLASSIFICATION")
print("="*70)

print(f"\nTotal prefix-less tokens: {len(prefixless_tokens)}")

# Count by category
categories = Counter(t['category'] for t in prefixless_tokens)
print(f"\nBy category:")
for cat, cnt in categories.most_common():
    pct = 100 * cnt / len(prefixless_tokens)
    print(f"  {cat}: {cnt} ({pct:.1f}%)")

# ============================================================
# SUFFIX-ONLY tokens
# ============================================================
print("\n" + "="*70)
print("SUFFIX-ONLY TOKENS (Closure Tokens)")
print("="*70)

suffix_only = [t for t in prefixless_tokens if t['category'] == 'SUFFIX_ONLY']
print(f"\nSUFFIX-ONLY count: {len(suffix_only)} ({100*len(suffix_only)/len(prefixless_tokens):.1f}%)")

suffix_only_words = Counter(t['word'] for t in suffix_only)
print(f"\nTop SUFFIX-ONLY tokens:")
for word, cnt in suffix_only_words.most_common(15):
    line_final_cnt = sum(1 for t in suffix_only if t['word'] == word and t['line_final'])
    lf_pct = 100 * line_final_cnt / cnt if cnt > 0 else 0
    print(f"  {word}: {cnt} ({lf_pct:.0f}% line-final)")

# ============================================================
# POTENTIAL UNRECOGNIZED PREFIXES
# ============================================================
print("\n" + "="*70)
print("POTENTIAL UNRECOGNIZED PREFIXES")
print("="*70)

potential_prefix_cats = [c for c in categories.keys() if c.startswith('POTENTIAL_PREFIX')]
for cat in sorted(potential_prefix_cats, key=lambda x: -categories[x]):
    tokens = [t for t in prefixless_tokens if t['category'] == cat]
    prefix = cat.replace('POTENTIAL_PREFIX_', '')
    print(f"\n{prefix}- pattern: {len(tokens)} tokens")

    words = Counter(t['word'] for t in tokens)
    for word, cnt in words.most_common(10):
        print(f"  {word}: {cnt}")

# ============================================================
# GENUINE VOCABULARY
# ============================================================
print("\n" + "="*70)
print("GENUINE PREFIX-LESS VOCABULARY")
print("="*70)

vocab = [t for t in prefixless_tokens if t['category'] == 'VOCABULARY']
print(f"\nGenuine vocabulary count: {len(vocab)} ({100*len(vocab)/len(prefixless_tokens):.1f}%)")

vocab_words = Counter(t['word'] for t in vocab)
print(f"\nUnique vocabulary types: {len(vocab_words)}")
print(f"\nTop genuine vocabulary:")
for word, cnt in vocab_words.most_common(20):
    print(f"  {word}: {cnt}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY: BREAKDOWN OF 'PREFIX-LESS' TOKENS")
print("="*70)

suffix_only_cnt = len(suffix_only)
potential_prefix_cnt = sum(categories[c] for c in potential_prefix_cats)
vocab_cnt = len(vocab)
suffix_like_cnt = categories.get('SUFFIX_LIKE', 0)

print(f"""
Total prefix-less tokens: {len(prefixless_tokens)}

  SUFFIX-ONLY (closure tokens): {suffix_only_cnt} ({100*suffix_only_cnt/len(prefixless_tokens):.1f}%)
    -> These are structural tokens, NOT vocabulary
    -> Should be EXCLUDED from MIDDLE extraction

  SUFFIX-LIKE (short, vowel-heavy): {suffix_like_cnt} ({100*suffix_like_cnt/len(prefixless_tokens):.1f}%)
    -> Probably also closure/structural

  POTENTIAL UNRECOGNIZED PREFIXES: {potential_prefix_cnt} ({100*potential_prefix_cnt/len(prefixless_tokens):.1f}%)
    -> ck-, cp-, cf-, op-, etc.
    -> Should probably ADD these to prefix list

  GENUINE VOCABULARY: {vocab_cnt} ({100*vocab_cnt/len(prefixless_tokens):.1f}%)
    -> Truly prefix-less vocabulary items
    -> Examples: fachys, complex multi-syllable tokens
""")
