"""Examine f76r - a Bio folio with R-placement."""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

tx = Transcript()
all_tokens = list(tx.all(h_only=True))

# Compare f76r and f66r
for folio in ['f76r', 'f66r', 'f75r']:  # f75r is a "normal" bio folio for comparison
    tokens = [t for t in all_tokens if t.folio == folio]

    print(f'=== {folio} ===')
    print(f'Total tokens: {len(tokens)}')

    placements = Counter(t.placement for t in tokens)
    print(f'Placements: {dict(placements)}')

    section = tokens[0].section if tokens else '?'
    lang = tokens[0].language if tokens else '?'
    print(f'Section: {section}, Language: {lang}')

    # Sample tokens
    print('Sample tokens:')
    for t in tokens[:10]:
        print(f'  {t.word:15} line={t.line:>3} placement={t.placement}')
    print()
