#!/usr/bin/env python3
"""Quick test: does '38%' mean 'tokens within a LINK proximity zone'?"""

import os
import sys

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript
from collections import defaultdict

tx = Transcript()

# Group B tokens by (folio, line), preserving order
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t.word)

print("LINK Proximity Zone Test")
print("=" * 50)
print("Does 38% = proportion of tokens within distance d of a LINK token?\n")

for d in [0, 1, 2, 3, 4]:
    in_zone = 0
    total_tokens = 0
    for key, words in line_tokens.items():
        n = len(words)
        total_tokens += n
        link_positions = set(i for i, w in enumerate(words) if 'ol' in w)
        zone = set()
        for pos in link_positions:
            for offset in range(-d, d + 1):
                if 0 <= pos + offset < n:
                    zone.add(pos + offset)
        in_zone += len(zone)
    pct = in_zone / total_tokens * 100
    match = " *** MATCH ***" if abs(pct - 38) < 3 else ""
    print(f"  Distance {d}: {in_zone}/{total_tokens} = {pct:.1f}%{match}")

print("\nDone.")
