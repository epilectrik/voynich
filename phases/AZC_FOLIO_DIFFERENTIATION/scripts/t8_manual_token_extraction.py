"""
T8: Manual Token Extraction for Visual Inspection

Extract AZC tokens in readable format for manual pattern analysis.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Get AZC tokens grouped by folio and line
folios = {}
for token in tx.azc():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    key = token.folio
    if key not in folios:
        folios[key] = {}

    line_key = (token.line, getattr(token, 'placement', ''))
    if line_key not in folios[key]:
        folios[key][line_key] = []
    folios[key][line_key].append(w)

print(f"Total AZC folios: {len(folios)}")
print(f"Folios: {sorted(folios.keys())}")

# Print all AZC folios in detail
for folio in sorted(folios.keys()):
    print(f"\n{'='*70}")
    print(f"FOLIO: {folio}")
    print(f"{'='*70}")

    # Group by placement first
    by_placement = {}
    for (line, placement), tokens in folios[folio].items():
        if placement not in by_placement:
            by_placement[placement] = []
        by_placement[placement].append((line, tokens))

    for placement in sorted(by_placement.keys()):
        print(f"\n  [{placement}]")
        for line, tokens in sorted(by_placement[placement]):
            token_str = ' '.join(tokens)
            print(f"    L{line:02}: {token_str}")
