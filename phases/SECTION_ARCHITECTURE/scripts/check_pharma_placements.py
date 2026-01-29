"""Check placement types for all PHARMA folios."""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

tx = Transcript()

# Check each PHARMA folio
for folio in ['f57r', 'f57v', 'f66r', 'f66v']:
    tokens = [t for t in tx.currier_b() if t.folio == folio]
    if tokens:
        placements = Counter(t.placement for t in tokens)
        print(f'{folio}: {len(tokens)} tokens')
        for p, c in placements.most_common():
            print(f'  {p}: {c}')
        print()
    else:
        print(f'{folio}: no Currier B tokens')
        print()
