"""Check folio format in Currier A data."""

from pathlib import Path

filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

folios = set()
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                if folio:
                    folios.add(folio)

print('Sample Currier A folios:')
for f in sorted(folios)[:40]:
    print(f'  {f}')
print(f'\nTotal: {len(folios)} folios')

# Check if any match our morphology folios
morphology_folios = ['f26r', 'f26v', 'f31r', 'f34r', 'f39r', 'f41v', 'f43r', 'f55v',
                     'f33r', 'f39v', 'f40r', 'f40v', 'f46v', 'f50r', 'f50v',
                     'f33v', 'f41r', 'f46r', 'f48r', 'f48v', 'f55r']

print('\nMorphology folios in data:')
for mf in morphology_folios:
    if mf in folios:
        print(f'  {mf} - FOUND')
    else:
        print(f'  {mf} - NOT FOUND')
