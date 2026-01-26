#!/usr/bin/env python3
"""
Check: What MIDDLEs are we extracting from closure tokens?

Are these meaningful MIDDLEs or just suffix-stripping artifacts?
"""

import csv
from collections import Counter

SUFFIXES = ['daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
            'chedy', 'shedy', 'tedy', 'kedy', 'cheey', 'sheey', 'chey', 'shey',
            'chol', 'shol', 'chor', 'shor', 'eedy', 'edy', 'eey',
            'iin', 'ain', 'oin', 'ein', 'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
            'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
            'in', 'an', 'on', 'en', 'y', 'l', 'r', 'm', 'n', 's']
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)
SUFFIXES_SET = set(SUFFIXES)

# Tokens that are exactly suffixes
SUFFIX_TOKENS = ['s', 'dy', 'ol', 'or', 'aiin', 'y', 'ar', 'r', 'al', 'am', 'ky',
                 'oiin', 'om', 'l', 'ain', 'ey', 'an', 'in', 'ody', 'oly', 'ory',
                 'eey', 'edy', 'air', 'm', 'n', 'ty', 'ry', 'ly', 'shy', 'chy']

def extract_middle(token):
    """Extract middle after stripping suffix (no prefix check)."""
    working = token
    suffix = None
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            suffix = s
            working = working[:-len(s)]
            break
    return working if working else None, suffix

print("="*70)
print("WHAT MIDDLES COME FROM CLOSURE TOKENS?")
print("="*70)

# Check common suffix-like tokens
test_tokens = ['dy', 'ol', 'or', 'aiin', 'y', 'ar', 's', 'al', 'am', 'ody', 'oly',
               'ain', 'oiin', 'odaiin', 'okaiin', 'otaiin']

print("\nExtraction of common closure-like tokens:")
print(f"{'Token':<12} {'Middle':<10} {'Suffix':<10} {'Notes'}")
print("-" * 50)

for token in test_tokens:
    middle, suffix = extract_middle(token)

    # Is the token itself a suffix?
    is_suffix = token in SUFFIXES_SET
    # Is the middle also a suffix?
    middle_is_suffix = middle in SUFFIXES_SET if middle else False

    notes = []
    if is_suffix:
        notes.append("TOKEN=SUFFIX")
    if middle_is_suffix:
        notes.append("MIDDLE=SUFFIX")
    if middle and len(middle) == 1:
        notes.append("SINGLE-CHAR")

    print(f"{token:<12} {str(middle):<10} {str(suffix):<10} {', '.join(notes)}")

# ============================================================
# Check: Do these single-char "middles" appear in real vocabulary?
# ============================================================
print("\n" + "="*70)
print("DO SINGLE-CHAR MIDDLES APPEAR WITH PREFIXES?")
print("="*70)

# If 'd' is a real MIDDLE, we should see it with prefixes like 'ch+d+y' = 'chdy'
# Let's check if these single-char middles appear in prefixed contexts

ARTICULATORS = ['y', 'k', 'l', 'p', 'd', 'f', 'r', 's', 't']
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

def has_prefix(token):
    for p in PREFIXES:
        if token.startswith(p) and len(token) > len(p):
            return p
    for art in ARTICULATORS:
        if token.startswith(art) and len(token) > len(art):
            after_art = token[len(art):]
            for p in PREFIXES:
                if after_art.startswith(p) and len(after_art) > len(p):
                    return art + '+' + p
    return None

def full_extract(token):
    prefix = has_prefix(token)
    if prefix and '+' in prefix:
        # Articulator + prefix
        parts = prefix.split('+')
        remainder = token[len(parts[0]) + len(parts[1]):]
    elif prefix:
        remainder = token[len(prefix):]
    else:
        remainder = token

    middle, suffix = extract_middle(remainder) if remainder else (None, None)
    return prefix, middle, suffix

# Collect middles by prefix status
middles_with_prefix = Counter()
middles_without_prefix = Counter()

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

        prefix, middle, suffix = full_extract(word)
        if middle:
            if prefix:
                middles_with_prefix[middle] += 1
            else:
                middles_without_prefix[middle] += 1

# Check single-char middles
single_char_middles = set(m for m in (set(middles_with_prefix.keys()) | set(middles_without_prefix.keys())) if len(m) == 1)

print(f"\nSingle-char MIDDLEs found: {len(single_char_middles)}")
print(f"  {sorted(single_char_middles)}")

print(f"\nSingle-char MIDDLE usage:")
print(f"{'Middle':<8} {'With PREFIX':<15} {'Without PREFIX':<15} {'Ratio'}")
print("-" * 50)

for m in sorted(single_char_middles):
    with_p = middles_with_prefix[m]
    without_p = middles_without_prefix[m]
    total = with_p + without_p
    if total > 0:
        ratio = with_p / without_p if without_p > 0 else float('inf')
        print(f"{m:<8} {with_p:<15} {without_p:<15} {ratio:.2f}")

# ============================================================
# KEY INSIGHT
# ============================================================
print("\n" + "="*70)
print("KEY INSIGHT")
print("="*70)

# Count how many middles are ONLY from prefix-less tokens
only_prefixless = set(middles_without_prefix.keys()) - set(middles_with_prefix.keys())
only_prefixed = set(middles_with_prefix.keys()) - set(middles_without_prefix.keys())
shared = set(middles_with_prefix.keys()) & set(middles_without_prefix.keys())

print(f"""
MIDDLEs that appear ONLY without prefix: {len(only_prefixless)}
MIDDLEs that appear ONLY with prefix: {len(only_prefixed)}
MIDDLEs that appear in BOTH contexts: {len(shared)}

If closure tokens produce unique MIDDLEs not seen with prefixes,
those are likely extraction artifacts, not real vocabulary.
""")

# Show examples of prefix-less only middles
print("MIDDLEs appearing ONLY in prefix-less tokens (first 20):")
for m in sorted(only_prefixless)[:20]:
    cnt = middles_without_prefix[m]
    print(f"  '{m}': {cnt} tokens")
