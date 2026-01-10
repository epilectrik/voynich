#!/usr/bin/env python
"""Check how common pchor is in the corpus."""
import sys
import re
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from core.transcription import TranscriptionLoader

loader = TranscriptionLoader()
loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Count pchor across all A folios
a_folios = [f'{i}{side}' for i in range(1, 26) for side in ['r', 'v']]

pchor_count = 0
pchor_locations = []
total_tokens = 0

for folio_id in a_folios:
    folio = loader.get_folio(folio_id)
    if not folio or not folio.lines:
        continue

    for line_num, line in enumerate(folio.lines):
        tokens = [t for t in re.split(r'[\.\s]+', line.text) if t]
        total_tokens += len(tokens)
        for i, token in enumerate(tokens):
            if token.lower() == 'pchor':
                pchor_count += 1
                position = 'FIRST' if line_num == 0 and i == 0 else f'L{line_num+1}:T{i+1}'
                pchor_locations.append((folio_id, position))

print(f'=== pchor Frequency ===')
print(f'Total occurrences: {pchor_count}')
print(f'Total tokens in A folios: {total_tokens}')
print(f'Frequency: {100*pchor_count/total_tokens:.4f}%')
print()
print('Locations:')
for folio, pos in pchor_locations:
    print(f'  {folio}: {pos}')

# Compare to other common tokens
print()
print('=== Comparison to similar tokens ===')

# Count all pch* tokens
pch_tokens = {}
for folio_id in a_folios:
    folio = loader.get_folio(folio_id)
    if not folio:
        continue
    for line in folio.lines:
        tokens = [t.lower() for t in re.split(r'[\.\s]+', line.text) if t]
        for token in tokens:
            if token.startswith('pch'):
                pch_tokens[token] = pch_tokens.get(token, 0) + 1

print('All pch* tokens (by frequency):')
for token, count in sorted(pch_tokens.items(), key=lambda x: -x[1])[:15]:
    print(f'  {token}: {count}')
