"""
AZC FOLIO SURVEY

Analyze placement structure for all AZC diagram folios.
"""

import os
from collections import defaultdict, Counter

os.chdir('C:/git/voynich')

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

def analyze_folio(target_folio):
    """Analyze a single folio's placement structure."""
    by_placement = defaultdict(list)

    for line in lines[1:]:
        parts = line.strip().split('\t')
        if len(parts) >= len(header):
            row = {header[i]: parts[i].strip('"') for i in range(len(header))}
            if row.get('transcriber', '').strip() == 'H' and row.get('folio') == target_folio:
                p = row.get('placement', '')
                w = row.get('word', '')
                ln = row.get('line_number', '')
                by_placement[p].append((ln, w))

    return by_placement

# Folios to analyze
folios = ['f73r', 'f73v']

for folio in folios:
    print(f"\n{'='*60}")
    print(f"{folio}")
    print(f"{'='*60}")

    data = analyze_folio(folio)
    total = sum(len(v) for v in data.values())

    print(f"Total tokens: {total}")
    print(f"Placements: {sorted(data.keys())}")

    for p in sorted(data.keys()):
        tokens = data[p]
        lines_used = set(ln for ln, w in tokens)

        # Determine pattern
        if len(lines_used) == len(tokens):
            pattern = "SCATTERED (1 token/line)"
        elif len(lines_used) == 1:
            pattern = "CONTINUOUS (all same line)"
        else:
            pattern = f"{len(lines_used)} lines, {len(tokens)} tokens"

        print(f"\n[{p}] {len(tokens)} tokens - {pattern}")

        # Group by line
        by_line = defaultdict(list)
        for ln, w in tokens:
            by_line[ln].append(w)

        for ln in sorted(by_line.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            words = by_line[ln]
            if len(words) <= 10:
                print(f"  Line {ln}: {' '.join(words)}")
            else:
                print(f"  Line {ln}: {' '.join(words[:5])} ... ({len(words)} total)")
