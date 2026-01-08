"""
TRUE ORPHANS Analysis - The 2% that fits nothing
"""

from collections import Counter
from pathlib import Path

filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y', 'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']
HT_PREFIXES = ['yk', 'yp', 'yt', 'yc', 'yd', 'ys', 'op', 'oc', 'oe', 'of', 'pc', 'tc', 'dc', 'kc', 'sc', 'fc', 'sa', 'so', 'ka', 'ke', 'ko', 'ta', 'te', 'to', 'po', 'do', 'lo', 'ro']
HT_SUFFIXES = ['dy', 'ey', 'hy', 'ry', 'ly', 'ty', 'sy', 'ky', 'ny', 'my', 'in', 'ir', 'im', 'il', 'ar', 'or', 'er', 'al', 'ol', 'el', 'am', 'om', 'an', 'on', 'as', 'os', 'es']

orphans = Counter()
orphan_contexts = {}
orphan_by_section = Counter()
orphan_by_lang = Counter()

with open(filepath, 'r', encoding='utf-8') as f:
    f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
            section = parts[3].strip('"').strip() if len(parts) > 3 else ''

            if not word or word.startswith('*') or len(word) == 1:
                continue

            has_b_prefix = any(word.startswith(p) for p in B_GRAMMAR_PREFIXES)
            has_b_suffix = any(word.endswith(s) for s in B_GRAMMAR_SUFFIXES)
            has_ht_prefix = any(word.startswith(p) for p in HT_PREFIXES)
            has_ht_suffix = any(word.endswith(s) for s in HT_SUFFIXES)

            if not has_b_prefix and not has_b_suffix and not has_ht_prefix and not has_ht_suffix:
                orphans[word] += 1
                orphan_by_section[section] += 1
                orphan_by_lang[lang] += 1
                if word not in orphan_contexts:
                    orphan_contexts[word] = (folio, section, lang)

print('=' * 70)
print('TRUE ORPHANS - No recognized prefix OR suffix')
print('=' * 70)
print(f'Total occurrences: {sum(orphans.values())}')
print(f'Unique types: {len(orphans)}')

print(f'\n### BY CURRIER LANGUAGE')
for lang, count in orphan_by_lang.most_common():
    print(f'  {lang if lang else "(none)"}: {count} ({100*count/sum(orphans.values()):.1f}%)')

print(f'\n### BY SECTION')
for section, count in orphan_by_section.most_common():
    print(f'  {section if section else "(none)"}: {count} ({100*count/sum(orphans.values()):.1f}%)')

# Categorize by pattern
patterns = {
    'ends_-m': [],
    'ends_-r': [],
    'ends_-s': [],
    'ends_-l': [],
    'ends_-n': [],
    'ends_-d': [],
    'has_ii': [],
    'has_ee': [],
    'consonant_cluster': [],
    'all_vowel': [],
    'other': []
}

for tok in orphans:
    if all(c in 'aeiou' for c in tok):
        patterns['all_vowel'].append(tok)
    elif all(c in 'bcdfghjklmnpqrstvwxyz' for c in tok):
        patterns['consonant_cluster'].append(tok)
    elif tok.endswith('m'):
        patterns['ends_-m'].append(tok)
    elif tok.endswith('r'):
        patterns['ends_-r'].append(tok)
    elif tok.endswith('s'):
        patterns['ends_-s'].append(tok)
    elif tok.endswith('l'):
        patterns['ends_-l'].append(tok)
    elif tok.endswith('n'):
        patterns['ends_-n'].append(tok)
    elif tok.endswith('d'):
        patterns['ends_-d'].append(tok)
    elif 'ii' in tok:
        patterns['has_ii'].append(tok)
    elif 'ee' in tok:
        patterns['has_ee'].append(tok)
    else:
        patterns['other'].append(tok)

print(f'\n### BY PATTERN')
for pattern, tokens in sorted(patterns.items(), key=lambda x: -len(x[1])):
    total_freq = sum(orphans[t] for t in tokens)
    print(f'\n{pattern}: {len(tokens)} types, {total_freq} occurrences')
    top_examples = sorted(tokens, key=lambda t: -orphans[t])[:10]
    print(f'  Top: {", ".join([f"{t}({orphans[t]})" for t in top_examples])}')

print(f'\n### TOP 50 ORPHANS')
print(f'{"Token":<15} {"Freq":>6} {"Len":>4} {"Folio":<10} {"Sect":<5} {"Lang":<5}')
print('-' * 50)

for tok, freq in orphans.most_common(50):
    folio, section, lang = orphan_contexts[tok]
    print(f'{tok:<15} {freq:>6} {len(tok):>4} {folio:<10} {section:<5} {lang:<5}')

# Check if these might be suffix-only forms we missed
print(f'\n### POTENTIAL MISSING SUFFIXES')
print('Tokens that might be standalone suffixes:')
suffix_candidates = [t for t in orphans if len(t) <= 4 and orphans[t] >= 10]
for tok in sorted(suffix_candidates, key=lambda t: -orphans[t])[:20]:
    print(f'  {tok}: {orphans[tok]} occurrences')

print('\n' + '=' * 70)
