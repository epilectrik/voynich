"""
Raw f103r token extraction with atom decomposition.
No CategoryClassifier, no BFolioDecoder — just morphology and atom glosses.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

# Atom glosses (from C1195, C1388-C1392, and the expert context)
ATOM_GLOSSES = {
    'k': 'heat',
    'e': 'cool',
    'h': 'watch',
    'y': 'end',
    'i': 'iterate',
    'n': 'halt',  # bind/connect per some glosses
    'a': 'yield',
    'm': 'finalize',
    'd': 'mark',
    't': 'transfer',
    'l': 'state',
    'o': 'arrange',
    'c': 'adjust',
    'p': 'pause',
    'f': 'flag',
    's': 'sequence',
    'r': 'respond',
    'g': 'complete',
    'x': 'diagram',
}

def decompose_middle(middle):
    """Break a MIDDLE into its constituent atoms and gloss each."""
    if not middle:
        return []
    atoms = []
    for char in middle:
        gloss = ATOM_GLOSSES.get(char, f'?({char})')
        atoms.append((char, gloss))
    return atoms

tx = Transcript()
morph = Morphology()

# Get f103r tokens, sorted by line then position
tokens = [t for t in tx.currier_b() if t.folio == 'f103r']

# Group by line
from collections import defaultdict
lines = defaultdict(list)
for t in tokens:
    lines[t.line].append(t)

# Sort lines numerically
sorted_lines = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)

print("=" * 100)
print("RAW f103r TOKEN EXTRACTION WITH ATOM DECOMPOSITION")
print("=" * 100)
print()

for line_num in sorted_lines:
    line_tokens = lines[line_num]
    print(f"--- LINE {line_num} ({len(line_tokens)} tokens) ---")
    print()

    for i, t in enumerate(line_tokens):
        word = t.word
        m = morph.extract(word)

        prefix = m.prefix if m.prefix else '-'
        middle = m.middle if m.middle else '-'
        suffix = m.suffix if m.suffix else '-'
        articulator = m.articulator if m.articulator else ''

        atoms = decompose_middle(m.middle)
        atom_str = ' + '.join(f"{char}({gloss})" for char, gloss in atoms) if atoms else '-'

        art_str = f"[ART:{articulator}] " if articulator else ""

        print(f"  {i+1:2d}. {word:20s} {art_str}PFX:{prefix:6s} MID:{middle:10s} SFX:{suffix:6s} | {atom_str}")

    print()

print(f"\nTotal lines: {len(sorted_lines)}")
print(f"Total tokens: {len(tokens)}")
