#!/usr/bin/env python
"""Check first tokens of Currier A folios."""
import sys
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from ui.folio_viewer import get_token_primary_system
from core.transcription import TranscriptionLoader
import re

loader = TranscriptionLoader()
loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Get A folios (early folios are typically A)
a_folios = ['1r', '1v', '2r', '2v', '3r', '3v', '4r', '4v', '5r', '5v',
            '6r', '6v', '7r', '7v', '8r', '8v', '9r', '9v', '10r', '10v']

print('=== First Tokens of Currier A Folios ===\n')
print(f'{"Folio":<8} {"First Token":<15} {"Classification":<25} {"Notes"}')
print('-' * 70)

failed_count = 0
total_count = 0

for folio_id in a_folios:
    folio = loader.get_folio(folio_id)
    if not folio or not folio.lines:
        continue

    # Get first token from first line
    first_line = folio.lines[0]
    tokens = re.split(r'[\.\s]+', first_line.text)
    tokens = [t for t in tokens if t]

    if not tokens:
        continue

    first_token = tokens[0]
    classification = get_token_primary_system(first_token, 'A')

    total_count += 1

    # Check if it failed A classification
    is_failed = classification not in ('A', 'A_UNDERSPECIFIED', 'A-UNCERTAIN')
    if is_failed:
        failed_count += 1
        note = '<-- FAILED'
    else:
        note = ''

    print(f'{folio_id:<8} {first_token:<15} {classification:<25} {note}')

print()
print(f'Failed: {failed_count}/{total_count} ({100*failed_count/total_count:.1f}%)')
