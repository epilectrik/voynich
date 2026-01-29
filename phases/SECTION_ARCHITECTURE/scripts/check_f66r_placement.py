"""Check f66r placement types to determine if single-chars are labels."""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

tx = Transcript()

# Get all f66r tokens
f66r_tokens = [t for t in tx.currier_b() if t.folio == 'f66r']

print(f'f66r total tokens: {len(f66r_tokens)}')
print()

# Placement distribution
placement_counts = Counter(t.placement for t in f66r_tokens)
print('Placement types:')
for p, count in placement_counts.most_common():
    print(f"  {p}: {count}")
print()

# Single-char tokens
single_char = [t for t in f66r_tokens if len(t.word) == 1]
print(f'Single-char tokens: {len(single_char)}')

single_char_by_placement = {}
for t in single_char:
    if t.placement not in single_char_by_placement:
        single_char_by_placement[t.placement] = []
    single_char_by_placement[t.placement].append(t.word)

print('\nSingle-char by placement:')
for p, chars in single_char_by_placement.items():
    print(f"  {p}: {chars}")

# Check lines of single-char tokens
print('\nSingle-char token details:')
for t in single_char[:10]:
    print(f"  {t.word}: line={t.line}, placement={t.placement}")
