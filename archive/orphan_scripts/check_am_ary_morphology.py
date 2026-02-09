#!/usr/bin/env python3
"""Check morphological structure of -am/-y tokens."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Morphology

morph = Morphology()

tokens = ['am', 'dam', 'otam', 'oly', 'oldy', 'daly', 'ldy', 'ary']

print('Token      Prefix     Middle     Suffix     Notes')
print('-' * 65)

# FL MIDDLEs from C777
fl_middles = {'i', 'ii', 'in', 'r', 'ar', 'al', 'l', 'ol', 'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'}

for t in tokens:
    try:
        m = morph.extract(t)
        prefix = m.prefix or '-'
        middle = m.middle or '-'
        suffix = m.suffix or '-'

        notes = []
        if middle in fl_middles:
            notes.append(f'MIDDLE "{middle}" is FL!')

        print(f'{t:<10} {prefix:<10} {middle:<10} {suffix:<10} {" ".join(notes)}')
    except Exception as e:
        print(f'{t:<10} ERROR: {e}')
