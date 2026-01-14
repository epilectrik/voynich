"""Analyze unique contribution per AZC folio."""
import csv
from collections import defaultdict

# Build token -> AZC folio mapping
token_to_folios = defaultdict(set)
azc_sections = {'Z', 'A', 'C'}

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip()
        folio = row.get('folio', '').strip()
        section = row.get('section', '').strip()
        language = row.get('language', '').strip()

        if not word or word.startswith('[') or word.startswith('<') or '*' in word:
            continue

        is_azc = section in azc_sections or language not in ('A', 'B')
        if is_azc:
            token_to_folios[word].add(folio)

# Count unique tokens per folio (appear in ONLY that folio)
folio_unique = defaultdict(set)
folio_total = defaultdict(set)

for token, folios in token_to_folios.items():
    for f in folios:
        folio_total[f].add(token)
    if len(folios) == 1:
        folio_unique[list(folios)[0]].add(token)

# Report
print('AZC Folio Unique Contributions')
print('='*60)
print(f'{"Folio":<12} {"Total Types":<12} {"Unique Types":<12} {"% Unique":<10}')
print('-'*60)

folios_sorted = sorted(folio_total.keys())
total_unique = 0
total_all = 0

for folio in folios_sorted:
    total = len(folio_total[folio])
    unique = len(folio_unique[folio])
    pct = (unique/total*100) if total > 0 else 0
    total_unique += unique
    total_all += total
    print(f'{folio:<12} {total:<12} {unique:<12} {pct:<.1f}%')

print('-'*60)
print(f'Total unique types across AZC: {total_unique}')
print(f'Total AZC folios: {len(folio_total)}')
print()

# Show examples of unique tokens from a few folios
print('\nExample unique tokens by folio:')
print('='*60)
for folio in ['f70v1', 'f72r1', 'f86v3', 'f67r1']:
    if folio in folio_unique and folio_unique[folio]:
        examples = list(folio_unique[folio])[:5]
        print(f'{folio}: {", ".join(examples)}')
