#!/usr/bin/env python3
"""Examine the 5 multi-token A-exclusive entries."""

import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / 'results'

with open(RESULTS_DIR / 'middle_classes.json') as f:
    middle_classes = json.load(f)

with open(RESULTS_DIR / 'entry_data.json') as f:
    entries = json.load(f)

a_exclusive = set(middle_classes['a_exclusive_middles'])

print("=" * 70)
print("MULTI-TOKEN A-EXCLUSIVE ENTRIES (all 5)")
print("=" * 70)
print()

for e in entries:
    middle = e['tokens'][0]['middle']
    if middle in a_exclusive and e['n_tokens'] > 1:
        tokens = [t['token'] for t in e['tokens']]
        print(f"Folio: {e['folio']}, Line: {e['line']}")
        print(f"  Tokens: {' '.join(tokens)}")
        print(f"  Token count: {e['n_tokens']}")
        print(f"  MIDDLE: {middle}")
        print(f"  PREFIX: {e['tokens'][0]['prefix']}")
        print(f"  SUFFIX: {e['tokens'][0]['suffix']}")
        print()
