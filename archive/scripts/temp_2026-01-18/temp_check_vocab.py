"""Quick check of A vs AZC vocabulary overlap."""

from collections import Counter

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    header = f.readline()

    a_tokens = []
    azc_tokens = []
    star_tokens = []

    for line in f:
        parts = line.strip().split('\t')
        if len(parts) < 13:
            continue

        word = parts[0].strip('"').strip()
        lang = parts[6].strip('"').strip()
        transcriber = parts[12].strip('"').strip()

        if transcriber != 'H':
            continue

        if lang == 'A':
            a_tokens.append(word)
            if '*' in word:
                star_tokens.append(word)
        elif lang == 'NA':
            azc_tokens.append(word)

print(f'Currier A tokens: {len(a_tokens)}')
print(f'AZC tokens: {len(azc_tokens)}')
print(f'A tokens with * : {len(star_tokens)} ({100*len(star_tokens)/len(a_tokens):.1f}%)')
if star_tokens:
    print(f'Star token examples: {star_tokens[:20]}')
else:
    print('No star tokens found')

# Check unique tokens
a_unique = set(a_tokens)
azc_unique = set(azc_tokens)
overlap = a_unique & azc_unique
print(f'\nA unique types: {len(a_unique)}')
print(f'AZC unique types: {len(azc_unique)}')
print(f'Overlap: {len(overlap)} ({100*len(overlap)/len(a_unique):.1f}% of A types)')
print(f'A-only: {len(a_unique - azc_unique)}')
