"""Quick analysis of what falls into 'other' category."""
import csv
from collections import Counter
from pathlib import Path

# The 8 marker families from C240
MARKER_PREFIXES = {'ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct'}

CURRIER_A_FOLIOS = {
    '1r', '1v', '2r', '2v', '3r', '3v', '4r', '4v', '5r', '5v',
    '6r', '6v', '7r', '7v', '8r', '8v', '9r', '9v', '10r', '10v',
    '11r', '11v', '13r', '13v', '14r', '14v', '15r', '15v',
}

data_path = Path(__file__).parent.parent.parent / 'data/transcriptions/interlinear_full_words.txt'
other_tokens = Counter()
other_prefixes = Counter()

with open(data_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        transcriber = row.get('transcriber', '').strip().strip('"')
        if transcriber != 'H':
            continue
        folio = row.get('folio', '').strip('"').replace('f', '')
        if folio in CURRIER_A_FOLIOS:
            word = row.get('word', '').strip('"').lower()
            if word and not word.startswith('*') and len(word) >= 2:
                prefix = word[:2]
                if prefix not in MARKER_PREFIXES:
                    other_tokens[word] += 1
                    other_prefixes[prefix] += 1

print('="' * 30)
print('TOKENS FALLING INTO "OTHER" CATEGORY')
print('(First 2 chars not in: ch, sh, ok, ot, da, qo, ol, ct)')
print('=' * 60)

print('\nTop 20 "other" prefixes:')
for prefix, count in other_prefixes.most_common(20):
    print(f'  {prefix}: {count}')

print('\nTop 20 "other" tokens:')
for word, count in other_tokens.most_common(20):
    print(f'  {word}: {count}')

total_other = sum(other_tokens.values())
print(f'\nTotal "other" tokens: {total_other}')
