import csv
from collections import Counter

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

def extract_middle_core(token):
    if not token:
        return None
    working = token
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if working.startswith(p):
            working = working[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if working.endswith(s) and len(working) > len(s):
            working = working[:-len(s)]
            break
    return working if working else None

a_middles = set()
b_middles = set()

with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        word = row.get('word', '').strip()
        language = row.get('language', '').strip()
        if not word or '*' in word or word.startswith('[') or word.startswith('<'):
            continue
        middle = extract_middle_core(word)
        if middle and len(middle) > 0:
            if language == 'A':
                a_middles.add(middle)
            elif language == 'B':
                b_middles.add(middle)

ri = a_middles - b_middles
pp = a_middles & b_middles

# Check length distribution
ri_lengths = Counter(len(m) for m in ri)
pp_lengths = Counter(len(m) for m in pp)

print('RI MIDDLE length distribution:')
for length in sorted(ri_lengths.keys()):
    print(f'  len={length}: {ri_lengths[length]}')

print(f'\nPP MIDDLE length distribution:')
for length in sorted(pp_lengths.keys())[:10]:
    print(f'  len={length}: {pp_lengths[length]}')

print(f'\nTotal RI: {len(ri)}')
print(f'RI with len>=2: {sum(1 for m in ri if len(m) >= 2)}')

print(f'\nTotal PP: {len(pp)}')
print(f'PP with len>=2: {sum(1 for m in pp if len(m) >= 2)}')

# Show some 1-char middles
one_char_ri = sorted([m for m in ri if len(m) == 1])
one_char_pp = sorted([m for m in pp if len(m) == 1])
print(f'\n1-char RI: {one_char_ri}')
print(f'1-char PP: {one_char_pp}')

# What are the constraint numbers?
print(f'\nConstraint reference (C498):')
print(f'  Expected PP: ~90')
print(f'  Expected RI: ~173 (from earlier check)')
