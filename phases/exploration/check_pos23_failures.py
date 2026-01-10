#!/usr/bin/env python
"""Check what's causing position 2-3 failures."""
import sys
import re
from collections import Counter
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from core.transcription import TranscriptionLoader
from ui.folio_viewer import get_token_primary_system

loader = TranscriptionLoader()
loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

a_folios = [f'{i}{side}' for i in range(1, 26) for side in ['r', 'v']]

print('=== Position 2 Failures ===')
print()

pos2_failures = []
for folio_id in a_folios:
    folio = loader.get_folio(folio_id)
    if not folio or not folio.lines:
        continue

    first_line = folio.lines[0]
    tokens = re.split(r'[\.\s]+', first_line.text)
    tokens = [t for t in tokens if t]

    if len(tokens) >= 2:
        token = tokens[1]
        classification = get_token_primary_system(token, 'A')
        is_pass = classification in ('A', 'A_UNDERSPECIFIED', 'A-UNCERTAIN')

        if not is_pass:
            pos2_failures.append({
                'folio': folio_id,
                'token': token,
                'classification': classification,
                'prefix_2': token[:2].lower() if len(token) >= 2 else token.lower(),
            })

print(f'Total position 2 failures: {len(pos2_failures)}')
print()

# Show each failure
for f in pos2_failures:
    print(f"  {f['folio']:6} {f['token']:15} -> {f['classification']}")

# Group by classification
print()
print('By classification:')
class_counts = Counter(f['classification'] for f in pos2_failures)
for cls, count in class_counts.most_common():
    print(f'  {cls}: {count}')

# Group by prefix
print()
print('By prefix:')
prefix_counts = Counter(f['prefix_2'] for f in pos2_failures)
for prefix, count in prefix_counts.most_common():
    examples = [f['token'] for f in pos2_failures if f['prefix_2'] == prefix]
    print(f'  {prefix}: {count} - {examples}')

print()
print('=== Position 3 Failures ===')
print()

pos3_failures = []
for folio_id in a_folios:
    folio = loader.get_folio(folio_id)
    if not folio or not folio.lines:
        continue

    first_line = folio.lines[0]
    tokens = re.split(r'[\.\s]+', first_line.text)
    tokens = [t for t in tokens if t]

    if len(tokens) >= 3:
        token = tokens[2]
        classification = get_token_primary_system(token, 'A')
        is_pass = classification in ('A', 'A_UNDERSPECIFIED', 'A-UNCERTAIN')

        if not is_pass:
            pos3_failures.append({
                'folio': folio_id,
                'token': token,
                'classification': classification,
                'prefix_2': token[:2].lower() if len(token) >= 2 else token.lower(),
            })

print(f'Total position 3 failures: {len(pos3_failures)}')
print()

# Group by classification
print('By classification:')
class_counts = Counter(f['classification'] for f in pos3_failures)
for cls, count in class_counts.most_common():
    print(f'  {cls}: {count}')

# Group by prefix
print()
print('By prefix:')
prefix_counts = Counter(f['prefix_2'] for f in pos3_failures)
for prefix, count in prefix_counts.most_common():
    examples = [f['token'] for f in pos3_failures if f['prefix_2'] == prefix][:3]
    print(f'  {prefix}: {count} - {examples}')
