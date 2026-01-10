#!/usr/bin/env python
"""Check classification rates for positions 1, 2, 3 on each folio."""
import sys
import re
from collections import Counter
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from core.transcription import TranscriptionLoader
from ui.folio_viewer import get_token_primary_system

loader = TranscriptionLoader()
loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

a_folios = [f'{i}{side}' for i in range(1, 26) for side in ['r', 'v']]

# Collect data for positions 1, 2, 3
position_data = {1: [], 2: [], 3: []}

for folio_id in a_folios:
    folio = loader.get_folio(folio_id)
    if not folio or not folio.lines:
        continue

    first_line = folio.lines[0]
    tokens = re.split(r'[\.\s]+', first_line.text)
    tokens = [t for t in tokens if t]

    for pos in [1, 2, 3]:
        if len(tokens) >= pos:
            token = tokens[pos - 1]
            classification = get_token_primary_system(token, 'A')
            is_pass = classification in ('A', 'A_UNDERSPECIFIED', 'A-UNCERTAIN')
            prefix_2 = token[:2].lower() if len(token) >= 2 else token.lower()

            position_data[pos].append({
                'folio': folio_id,
                'token': token,
                'classification': classification,
                'is_pass': is_pass,
                'prefix_2': prefix_2,
            })

# Analyze each position
print('=== Classification by Position ===')
print()

c_vowel = {'ko', 'po', 'to', 'fo', 'ka', 'ta', 'pa', 'fa'}

for pos in [1, 2, 3]:
    data = position_data[pos]
    total = len(data)
    passed = sum(1 for d in data if d['is_pass'])
    failed = total - passed

    # C+vowel count
    cvowel_count = sum(1 for d in data if d['prefix_2'] in c_vowel)

    print(f'Position {pos}:')
    print(f'  Total: {total}')
    print(f'  Pass: {passed} ({100*passed/total:.1f}%)')
    print(f'  FAIL: {failed} ({100*failed/total:.1f}%)')
    print(f'  C+vowel: {cvowel_count} ({100*cvowel_count/total:.1f}%)')
    print()

# Show prefix distribution for each position
print('=== Prefix Distribution by Position ===')
print()

for pos in [1, 2, 3]:
    data = position_data[pos]
    prefix_counts = Counter(d['prefix_2'] for d in data)

    print(f'Position {pos} top prefixes:')
    for prefix, count in prefix_counts.most_common(8):
        pct = 100 * count / len(data)
        is_cvowel = '*' if prefix in c_vowel else ' '
        print(f'  {is_cvowel} {prefix}: {count} ({pct:.1f}%)')
    print()

# Check if there's a gradient
print('=== Gradient Check ===')
print()
print('Fail rate by position:')
for pos in [1, 2, 3]:
    data = position_data[pos]
    fail_rate = 100 * sum(1 for d in data if not d['is_pass']) / len(data)
    cvowel_rate = 100 * sum(1 for d in data if d['prefix_2'] in c_vowel) / len(data)
    print(f'  Position {pos}: {fail_rate:.1f}% fail, {cvowel_rate:.1f}% C+vowel')

# Show some examples of folios where positions 1,2,3 all fail
print()
print('=== Folios where positions 1,2,3 ALL fail ===')
for i in range(len(position_data[1])):
    if i < len(position_data[2]) and i < len(position_data[3]):
        if (not position_data[1][i]['is_pass'] and
            not position_data[2][i]['is_pass'] and
            not position_data[3][i]['is_pass']):
            folio = position_data[1][i]['folio']
            t1 = position_data[1][i]['token']
            t2 = position_data[2][i]['token']
            t3 = position_data[3][i]['token']
            print(f"  {folio}: {t1}, {t2}, {t3}")
