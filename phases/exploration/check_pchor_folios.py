#!/usr/bin/env python
"""Check what's special about the two folios with same first token (pchor)."""
import sys
import re
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from core.transcription import TranscriptionLoader

loader = TranscriptionLoader()
loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

folios_of_interest = ['19r', '21r']
# Also check adjacent folios for context
all_folios = ['18v', '19r', '19v', '20r', '20v', '21r', '21v', '22r']

print('=== Folios with same first token: pchor ===')
print()

for folio_id in all_folios:
    folio = loader.get_folio(folio_id)
    if not folio or not folio.lines:
        print(f'{folio_id}: [NO DATA]')
        continue

    marker = '***' if folio_id in folios_of_interest else '   '

    # Get first line
    first_line = folio.lines[0].text if folio.lines else ''
    tokens = re.split(r'[\.\s]+', first_line)
    tokens = [t for t in tokens if t]

    print(f'{marker} {folio_id}:')
    print(f'    First line: {first_line[:80]}...' if len(first_line) > 80 else f'    First line: {first_line}')
    print(f'    Token count: {len(tokens)}')
    print(f'    Line count: {len(folio.lines)}')
    print()

# Check full content similarity
print('=== Content Comparison ===')
print()

folio_19r = loader.get_folio('19r')
folio_21r = loader.get_folio('21r')

if folio_19r and folio_21r:
    # Get all tokens
    tokens_19r = []
    for line in folio_19r.lines:
        tokens_19r.extend([t for t in re.split(r'[\.\s]+', line.text) if t])

    tokens_21r = []
    for line in folio_21r.lines:
        tokens_21r.extend([t for t in re.split(r'[\.\s]+', line.text) if t])

    print(f'19r total tokens: {len(tokens_19r)}')
    print(f'21r total tokens: {len(tokens_21r)}')

    # Vocabulary overlap
    vocab_19r = set(tokens_19r)
    vocab_21r = set(tokens_21r)
    shared = vocab_19r & vocab_21r

    print(f'19r unique vocab: {len(vocab_19r)}')
    print(f'21r unique vocab: {len(vocab_21r)}')
    print(f'Shared vocabulary: {len(shared)}')

    jaccard = len(shared) / len(vocab_19r | vocab_21r)
    print(f'Jaccard similarity: {jaccard:.3f}')

    # Compare to random pair
    folio_5r = loader.get_folio('5r')
    if folio_5r:
        tokens_5r = []
        for line in folio_5r.lines:
            tokens_5r.extend([t for t in re.split(r'[\.\s]+', line.text) if t])
        vocab_5r = set(tokens_5r)

        shared_19_5 = vocab_19r & vocab_5r
        jaccard_19_5 = len(shared_19_5) / len(vocab_19r | vocab_5r)
        print(f'Jaccard 19r vs 5r (control): {jaccard_19_5:.3f}')

# Check if they're exactly 2 folios apart (same position in quire?)
print()
print('=== Structural Position ===')
print('19r: Quire 3, position 3r (f17-24)')
print('21r: Quire 3, position 5r')
print('Distance: 2 folios apart (4 pages)')

# Check what's between them
print()
print('=== What is between 19r and 21r? ===')
for fid in ['19v', '20r', '20v']:
    folio = loader.get_folio(fid)
    if folio and folio.lines:
        first_tokens = re.split(r'[\.\s]+', folio.lines[0].text)
        first_tokens = [t for t in first_tokens if t]
        print(f'{fid}: starts with "{first_tokens[0] if first_tokens else "?"}"')
