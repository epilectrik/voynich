#!/usr/bin/env python
"""Compare content after pchor on both folios."""
import sys
import re
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from core.transcription import TranscriptionLoader

loader = TranscriptionLoader()
loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

print('=== First Lines After pchor ===')
print()

folio_19r = loader.get_folio('19r')
folio_21r = loader.get_folio('21r')

line_19r = folio_19r.lines[0].text
line_21r = folio_21r.lines[0].text

print(f'19r: {line_19r}')
print(f'21r: {line_21r}')

# Get tokens after pchor
tokens_19r = re.split(r'[\.\s]+', line_19r)
tokens_19r = [t for t in tokens_19r if t][1:]  # Skip pchor

tokens_21r = re.split(r'[\.\s]+', line_21r)
tokens_21r = [t for t in tokens_21r if t][1:]  # Skip pchor

print()
print(f'19r after pchor: {tokens_19r}')
print(f'21r after pchor: {tokens_21r}')

# Check for shared tokens
shared = set(tokens_19r) & set(tokens_21r)
print(f'Shared tokens in first line: {shared if shared else "NONE"}')

# Compare all lines
print()
print('=== Full Folio Comparison ===')
print()

all_19r = []
for line in folio_19r.lines:
    all_19r.extend([t for t in re.split(r'[\.\s]+', line.text) if t])

all_21r = []
for line in folio_21r.lines:
    all_21r.extend([t for t in re.split(r'[\.\s]+', line.text) if t])

# Find shared vocabulary
shared_all = set(all_19r) & set(all_21r)
print(f'Shared vocabulary: {len(shared_all)} tokens')
print(f'Shared tokens: {sorted(shared_all)}')

# Check if pchor appears elsewhere in either folio
print()
print('=== pchor occurrences ===')
pchor_19r = all_19r.count('pchor')
pchor_21r = all_21r.count('pchor')
print(f'19r: pchor appears {pchor_19r}x')
print(f'21r: pchor appears {pchor_21r}x')

# Check other pch- tokens
print()
print('=== Other pch- tokens ===')
pch_19r = [t for t in all_19r if t.startswith('pch')]
pch_21r = [t for t in all_21r if t.startswith('pch')]
print(f'19r pch- tokens: {pch_19r}')
print(f'21r pch- tokens: {pch_21r}')
