#!/usr/bin/env python
"""Analyze patterns among first tokens of A folios."""
import sys
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from ui.folio_viewer import get_token_primary_system
from core.transcription import TranscriptionLoader
import re
from collections import Counter

loader = TranscriptionLoader()
loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Expand to more A folios
a_folios = [f'{i}{side}' for i in range(1, 26) for side in ['r', 'v']]

first_tokens = []
failed_tokens = []
passed_tokens = []

for folio_id in a_folios:
    folio = loader.get_folio(folio_id)
    if not folio or not folio.lines:
        continue

    first_line = folio.lines[0]
    tokens = re.split(r'[\.\s]+', first_line.text)
    tokens = [t for t in tokens if t]

    if not tokens:
        continue

    first_token = tokens[0]
    classification = get_token_primary_system(first_token, 'A')

    first_tokens.append((folio_id, first_token, classification))

    if classification not in ('A', 'A_UNDERSPECIFIED', 'A-UNCERTAIN'):
        failed_tokens.append(first_token)
    else:
        passed_tokens.append(first_token)

print('=== First Token Pattern Analysis ===\n')

# Prefix analysis (2-char)
print('FAILED tokens - 2-char prefix frequency:')
prefix2_failed = Counter(t[:2].lower() for t in failed_tokens if len(t) >= 2)
for prefix, count in prefix2_failed.most_common(10):
    pct = 100 * count / len(failed_tokens)
    examples = [t for t in failed_tokens if t.lower().startswith(prefix)][:3]
    print(f'  {prefix}: {count} ({pct:.0f}%) - {", ".join(examples)}')

print(f'\nPASSED tokens - 2-char prefix frequency:')
prefix2_passed = Counter(t[:2].lower() for t in passed_tokens if len(t) >= 2)
for prefix, count in prefix2_passed.most_common(10):
    pct = 100 * count / len(passed_tokens)
    examples = [t for t in passed_tokens if t.lower().startswith(prefix)][:3]
    print(f'  {prefix}: {count} ({pct:.0f}%) - {", ".join(examples)}')

# Suffix analysis
print(f'\nFAILED tokens - suffix patterns:')
suffix2_failed = Counter(t[-2:].lower() for t in failed_tokens if len(t) >= 2)
for suffix, count in suffix2_failed.most_common(5):
    pct = 100 * count / len(failed_tokens)
    print(f'  -{suffix}: {count} ({pct:.0f}%)')

# Length analysis
print(f'\nLength distribution:')
print(f'  Failed avg: {sum(len(t) for t in failed_tokens)/len(failed_tokens):.1f} chars')
print(f'  Passed avg: {sum(len(t) for t in passed_tokens)/len(passed_tokens):.1f} chars')

# Check for ko- specifically
print(f'\n=== "ko-" prefix analysis ===')
ko_tokens = [t for t in failed_tokens if t.lower().startswith('ko')]
print(f'ko- tokens: {len(ko_tokens)} ({100*len(ko_tokens)/len(failed_tokens):.0f}% of failed)')
for t in ko_tokens:
    print(f'  {t}')

# Check if failed tokens share patterns with each other
print(f'\n=== Cross-pattern check ===')
print(f'Total first tokens: {len(first_tokens)}')
print(f'Failed: {len(failed_tokens)} ({100*len(failed_tokens)/len(first_tokens):.0f}%)')
print(f'Passed: {len(passed_tokens)} ({100*len(passed_tokens)/len(first_tokens):.0f}%)')

# Check for k+vowel pattern
k_vowel = [t for t in failed_tokens if len(t) >= 2 and t[0].lower() == 'k' and t[1].lower() in 'aeiou']
print(f'\nk+vowel pattern: {len(k_vowel)} tokens')
for t in k_vowel:
    print(f'  {t}')

# Check for C+vowel pattern (consonant + vowel start)
c_vowel = [t for t in failed_tokens if len(t) >= 2 and t[0].lower() in 'bcdfghjklmnpqrstvwxz' and t[1].lower() in 'aeiouyw']
print(f'\nC+vowel/y pattern: {len(c_vowel)} tokens ({100*len(c_vowel)/len(failed_tokens):.0f}% of failed)')
