import sys
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

tx = Transcript()

# Check line numbering for a few B tokens
print("Sample B tokens:")
for i, token in enumerate(tx.currier_b()):
    if i < 30:
        print(f"  {token.folio} line={token.line}: '{token.word}'")

# Check line distribution
lines = Counter()
for token in tx.currier_b():
    lines[token.line] += 1

print(f"\nLine distribution (first 15):")
for line, count in sorted(lines.items())[:15]:
    print(f"  Line {line}: {count} tokens")

# Check what's on line 1
print("\nLine 1 tokens by folio (first 5 folios):")
line1_by_folio = {}
for token in tx.currier_b():
    if token.line == 1:
        if token.folio not in line1_by_folio:
            line1_by_folio[token.folio] = []
        line1_by_folio[token.folio].append(token.word)

for folio in list(line1_by_folio.keys())[:5]:
    print(f"  {folio}: {line1_by_folio[folio]}")
