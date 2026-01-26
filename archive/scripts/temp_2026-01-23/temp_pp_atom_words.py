#!/usr/bin/env python3
"""Check what words contain the key PP atoms 'e' and 'ol'."""

import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle(token):
    if not token or not isinstance(token, str):
        return None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

# Load words with 'e' and 'ol' as MIDDLE
words_with_e = []
words_with_ol = []

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        word = row.get('word', '').strip()
        language = row.get('language', '').strip()
        if not word or '*' in word:
            continue

        middle = extract_middle(word)
        if middle == 'e':
            words_with_e.append((word, language))
        elif middle == 'ol':
            words_with_ol.append((word, language))

print("="*70)
print("WORDS WITH MIDDLE = 'e'")
print("="*70)

e_words = Counter(w for w, lang in words_with_e)
e_by_lang = defaultdict(list)
for w, lang in words_with_e:
    e_by_lang[lang].append(w)

print(f"\nTotal occurrences: {len(words_with_e)}")
print(f"Unique words: {len(e_words)}")
print(f"By language: A={len(e_by_lang['A'])}, B={len(e_by_lang['B'])}")

print(f"\nMost common 'e' words:")
for word, count in e_words.most_common(15):
    print(f"  {word}: {count}")

print("\n" + "="*70)
print("WORDS WITH MIDDLE = 'ol'")
print("="*70)

ol_words = Counter(w for w, lang in words_with_ol)
ol_by_lang = defaultdict(list)
for w, lang in words_with_ol:
    ol_by_lang[lang].append(w)

print(f"\nTotal occurrences: {len(words_with_ol)}")
print(f"Unique words: {len(ol_words)}")
print(f"By language: A={len(ol_by_lang['A'])}, B={len(ol_by_lang['B'])}")

print(f"\nMost common 'ol' words:")
for word, count in ol_words.most_common(15):
    print(f"  {word}: {count}")

# What's the difference?
print("\n" + "="*70)
print("COMPARISON")
print("="*70)

print(f"\n'e' MIDDLE:")
print(f"  In A: {len(e_by_lang['A'])} tokens")
print(f"  In B: {len(e_by_lang['B'])} tokens")
print(f"  A/B ratio: {len(e_by_lang['A'])/len(e_by_lang['B']):.2f}" if e_by_lang['B'] else "")

print(f"\n'ol' MIDDLE:")
print(f"  In A: {len(ol_by_lang['A'])} tokens")
print(f"  In B: {len(ol_by_lang['B'])} tokens")
print(f"  A/B ratio: {len(ol_by_lang['A'])/len(ol_by_lang['B']):.2f}" if ol_by_lang['B'] else "")

# Check if these appear with different prefixes
print("\n" + "="*70)
print("PREFIX PATTERNS")
print("="*70)

def get_prefix(word):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if word.startswith(p):
            return p
    return None

e_prefixes = Counter(get_prefix(w) for w, _ in words_with_e)
ol_prefixes = Counter(get_prefix(w) for w, _ in words_with_ol)

print(f"\nPrefixes for 'e' MIDDLE:")
for p, c in e_prefixes.most_common(10):
    print(f"  {p}: {c} ({100*c/len(words_with_e):.1f}%)")

print(f"\nPrefixes for 'ol' MIDDLE:")
for p, c in ol_prefixes.most_common(10):
    print(f"  {p}: {c} ({100*c/len(words_with_ol):.1f}%)")
