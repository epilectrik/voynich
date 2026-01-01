"""Show a complete translated page."""
import sys
from pathlib import Path

project_root = Path('.')
sys.path.insert(0, str(project_root))

from analysis.crypto.translator import Translator

t = Translator()

folio = sys.argv[1] if len(sys.argv) > 1 else 'f1r'
translated = t.translate_folio(folio)
entries = t.dictionary.get('entries', {})

print('=' * 80)
print(f'FOLIO {folio} - COMPLETE TRANSLATION')
print(f'Words: {len(translated)}')
print('=' * 80)
print()
print('Format: Voynich -> Latin (English)')
print('-' * 80)
print()

# Group into lines of ~6 words for readability
line_num = 1
for i in range(0, len(translated), 6):
    chunk = translated[i:i+6]

    print(f'[Line {line_num}]')

    # Voynich
    voy = ' '.join(x['voynich'] for x in chunk)
    print(f'  VOY: {voy}')

    # Latin
    lat = ' '.join(x['latin'] for x in chunk)
    print(f'  LAT: {lat}')

    # English
    eng_parts = []
    for x in chunk:
        if x['voynich'] in entries:
            eng = entries[x['voynich']].get('english', x['latin'])
        else:
            eng = x['latin']
        eng_parts.append(eng)
    eng = ' '.join(eng_parts)
    print(f'  ENG: {eng}')
    print()

    line_num += 1
