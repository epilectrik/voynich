"""Examine f66r's column structure."""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

tx = Transcript()
all_tokens = list(tx.all(h_only=True))

f66r = [t for t in all_tokens if t.folio == 'f66r']

print("=== F66R COLUMN STRUCTURE ===\n")

# Group by placement
by_placement = {}
for t in f66r:
    p = t.placement
    if p not in by_placement:
        by_placement[p] = []
    by_placement[p].append(t)

# L-placement (likely the "token column")
print("=== L-PLACEMENT (token column?) ===\n")
l_tokens = sorted(by_placement.get('L', []), key=lambda t: int(''.join(c for c in t.line if c.isdigit()) or '0'))
for t in l_tokens:
    print(f"  line {t.line:>3}: {t.word}")

print(f"\nTotal L-placement: {len(l_tokens)}")

# Check patterns
print("\n--- Pattern analysis ---")
l_words = [t.word for t in l_tokens]

# First characters
first_chars = [w[0] if w else '' for w in l_words]
print(f"First characters: {' '.join(first_chars)}")

# Last characters
last_chars = [w[-1] if w else '' for w in l_words]
print(f"Last characters: {' '.join(last_chars)}")

# Lengths
lengths = [len(w) for w in l_words]
print(f"Lengths: {lengths}")

# Check if they match the M-placement single chars
print("\n=== M-PLACEMENT (single char column) ===\n")
m_tokens = sorted(by_placement.get('M', []), key=lambda t: int(''.join(c for c in t.line if c.isdigit()) or '0'))
for t in m_tokens[:20]:
    print(f"  line {t.line:>3}: {t.word}")
print(f"... ({len(m_tokens)} total)")

# Side by side comparison
print("\n=== SIDE BY SIDE (L and M by line) ===\n")
l_by_line = {t.line: t.word for t in l_tokens}
m_by_line = {t.line: t.word for t in m_tokens}

all_lines = sorted(set(l_by_line.keys()) | set(m_by_line.keys()),
                   key=lambda x: int(''.join(c for c in x if c.isdigit()) or '0'))

print(f"{'Line':>5} {'L (token)':>15} {'M (single)':>10}")
print("-" * 35)
for line in all_lines[:40]:
    l_word = l_by_line.get(line, '')
    m_word = m_by_line.get(line, '')
    print(f"{line:>5} {l_word:>15} {m_word:>10}")
