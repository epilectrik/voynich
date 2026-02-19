"""Dump all f85v2 region tokens in sequence order for visual matching."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import RosettesAnalyzer

ra = RosettesAnalyzer()

REGIONS = ['B1', 'B2', 'B3', 'C2', 'D1', 'M1', 'M2', 'M3',
           'N1', 'N2', 'U1', 'U2', 'U3', 'V1', 'V2', 'W1']

for region in REGIONS:
    toks = ra.get_tokens('f85v2', region)
    if not toks:
        continue
    words = [t.word.strip() for t in toks if t.word.strip() and '*' not in t.word]
    # Also show line structure
    lines = {}
    for t in toks:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        line_key = t.line
        if line_key not in lines:
            lines[line_key] = []
        lines[line_key].append(w)

    print(f'\n{"=" * 60}')
    print(f'REGION {region} ({len(words)} tokens, {len(lines)} lines)')
    print(f'{"=" * 60}')
    for line_key in sorted(lines.keys()):
        print(f'  Line {line_key}: {" ".join(lines[line_key])}')
