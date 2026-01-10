#!/usr/bin/env python
"""Investigate the 25% of first tokens that PASS classification."""
import sys
import json
import re
sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from core.transcription import TranscriptionLoader
from ui.folio_viewer import get_token_primary_system

with open('C:/git/voynich/phases/exploration/first_token_data.json', 'r') as f:
    data = json.load(f)

records = data['records']
passing = [r for r in records if r['is_pass']]
failing = [r for r in records if not r['is_pass']]

print('=== PASSING First Tokens (25%) ===')
print()
print(f"{'Folio':<8} {'Token':<15} {'Classification':<20} {'Prefix'}")
print('-' * 55)
for r in passing:
    print(f"{r['folio_id']:<8} {r['token']:<15} {r['classification']:<20} {r['prefix_2char']}")

print()
print('=== Folio Sequence with Pass/Fail ===')
print()
for r in records:
    marker = 'PASS' if r['is_pass'] else '    '
    print(f"{r['folio_id']:6} {marker} {r['token']}")

# Check if passing folios are adjacent (continuations?)
print()
print('=== Are PASSING folios adjacent? ===')
pass_indices = [i for i, r in enumerate(records) if r['is_pass']]
print(f'Pass positions in sequence: {pass_indices}')

# Check gaps between passing folios
if len(pass_indices) > 1:
    gaps = [pass_indices[i+1] - pass_indices[i] for i in range(len(pass_indices)-1)]
    print(f'Gaps between passing folios: {gaps}')
    adjacent_pairs = sum(1 for g in gaps if g == 1)
    print(f'Adjacent passing pairs: {adjacent_pairs}')

# Check if passing folios share content with previous folio
print()
print('=== Do PASSING folios continue from previous? ===')

loader = TranscriptionLoader()
loader.load_interlinear('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

for r in passing:
    folio_id = r['folio_id']
    # Get previous folio
    num = int(folio_id[:-1])
    side = folio_id[-1]

    if side == 'v':
        prev_id = f'{num}r'
    else:
        prev_id = f'{num-1}v' if num > 1 else None

    if prev_id:
        # Check vocabulary overlap
        curr_folio = loader.get_folio(folio_id)
        prev_folio = loader.get_folio(prev_id)

        if curr_folio and prev_folio:
            curr_tokens = set()
            for line in curr_folio.lines:
                curr_tokens.update([t.lower() for t in re.split(r'[\.\s]+', line.text) if t])

            prev_tokens = set()
            for line in prev_folio.lines:
                prev_tokens.update([t.lower() for t in re.split(r'[\.\s]+', line.text) if t])

            shared = len(curr_tokens & prev_tokens)
            jaccard = len(curr_tokens & prev_tokens) / len(curr_tokens | prev_tokens) if (curr_tokens | prev_tokens) else 0

            # Get previous folio's last line last token
            prev_last_line = prev_folio.lines[-1].text if prev_folio.lines else ''
            prev_last_tokens = [t for t in re.split(r'[\.\s]+', prev_last_line) if t]
            prev_last_token = prev_last_tokens[-1] if prev_last_tokens else '?'

            print(f'{prev_id} -> {folio_id}: J={jaccard:.3f}, prev_last="{prev_last_token}", curr_first="{r["token"]}"')

# Compare prefix patterns
print()
print('=== Prefix Pattern Comparison ===')
print()
print('PASSING prefixes:')
from collections import Counter
pass_prefixes = Counter(r['prefix_2char'] for r in passing)
for p, c in pass_prefixes.most_common():
    print(f'  {p}: {c}')

print()
print('FAILING prefixes (top 10):')
fail_prefixes = Counter(r['prefix_2char'] for r in failing)
for p, c in fail_prefixes.most_common(10):
    print(f'  {p}: {c}')

# Key difference
print()
print('=== Key Difference ===')
pass_set = set(pass_prefixes.keys())
fail_set = set(fail_prefixes.keys())
print(f'Prefixes ONLY in passing: {pass_set - fail_set}')
print(f'Prefixes ONLY in failing: {fail_set - pass_set}')
print(f'Prefixes in BOTH: {pass_set & fail_set}')
