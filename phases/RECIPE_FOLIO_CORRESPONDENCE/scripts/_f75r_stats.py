"""Quick stats for f75r folio notes."""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript
from collections import Counter

tx = Transcript()
tokens = [t for t in tx.currier_b() if t.folio == 'f75r' and not t.is_label]
lines = sorted(set(t.line for t in tokens), key=lambda x: int(x) if x.isdigit() else 0)

print(f'Tokens: {len(tokens)}')
print(f'Lines: {len(lines)} ({lines[0]}-{lines[-1]})')
print(f'Unique types: {len(set(t.word for t in tokens))}')

# Section info
print(f'Section: {tokens[0].section if tokens else "?"}')

# Paragraph count via line gaps
para_count = 1
for i in range(1, len(lines)):
    prev = int(lines[i-1]) if lines[i-1].isdigit() else 0
    curr = int(lines[i]) if lines[i].isdigit() else 0
    if curr - prev > 1:
        para_count += 1
print(f'Paragraphs (gap): {para_count}')

# Paragraph count from transcript field
# Check if tokens have paragraph info
sample = tokens[0]
print(f'Token fields: {[a for a in dir(sample) if not a.startswith("_")]}')
