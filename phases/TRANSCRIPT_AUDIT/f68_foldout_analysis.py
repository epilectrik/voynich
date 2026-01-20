"""
F68R1/F68R2/F68R3 FOLDOUT ANALYSIS

User observations:
- f68r1 & f68r2: Currier A-like paragraph ABOVE diagram
- f68r1 & f68r2: Diagrams are NOT rings - circular areas with scattered tokens
- f68r3: More typical - outer ring, spoke lines, internal ring, scattered between spokes
"""

import os
from collections import defaultdict

os.chdir('C:/git/voynich')

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

for folio in ['f68r1', 'f68r2', 'f68r3']:
    print(f"\n{'='*60}")
    print(f"{folio}")
    print(f"{'='*60}")

    by_placement = defaultdict(list)
    for line in lines[1:]:
        parts = line.strip().split('\t')
        if len(parts) >= len(header):
            row = {header[i]: parts[i].strip('"') for i in range(len(header))}
            if row.get('transcriber', '').strip() == 'H' and row.get('folio') == folio:
                p = row.get('placement', '')
                w = row.get('word', '')
                ln = row.get('line_number', '')
                by_placement[p].append((ln, w))

    for p in sorted(by_placement.keys()):
        tokens = by_placement[p]
        print(f"\n[{p}] - {len(tokens)} tokens:")
        # Group by line
        by_line = defaultdict(list)
        for ln, w in tokens:
            by_line[ln].append(w)
        for ln in sorted(by_line.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            words = by_line[ln]
            print(f"  Line {ln}: {' '.join(words)}")
