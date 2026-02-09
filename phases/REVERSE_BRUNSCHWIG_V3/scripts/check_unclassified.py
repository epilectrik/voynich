#!/usr/bin/env python3
"""Check what MIDDLEs are unclassified."""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

KNOWN = {'tch','pch','lch','ksh','sch','cth','k','t','e','ch','sh','h','ke','kch','te','the','kc','okch'}

tx = Transcript()
morph = Morphology()

folio = sys.argv[1] if len(sys.argv) > 1 else 'f107r'

other_middles = []
for tok in tx.currier_b():
    if tok.folio == folio:
        m = morph.extract(tok.word)
        if m.middle and m.middle not in KNOWN:
            other_middles.append(m.middle)

c = Counter(other_middles)
print(f'Top 20 unclassified MIDDLEs in {folio}:')
for mid, count in c.most_common(20):
    # Check if it contains known patterns
    contains = [k for k in KNOWN if k in mid and len(k) >= 2]
    note = f" (contains: {','.join(contains)})" if contains else ""
    print(f'  {mid}: {count}{note}')

print(f'\nTotal unique unclassified: {len(c)}')
print(f'Total unclassified tokens: {len(other_middles)}')
