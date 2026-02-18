#!/usr/bin/env python3
"""Check all Rosettes folios across all transcribers."""
import sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript

tx = Transcript()

# Get ALL tokens (not just B, not just H) for f85/f86
rosette_data = defaultdict(lambda: defaultdict(list))
all_folios = set()

for tok in tx.all(h_only=False):
    if tok.folio and ('f85' in tok.folio or 'f86' in tok.folio):
        all_folios.add(tok.folio)
        rosette_data[tok.folio][tok.transcriber].append(tok)

print("All folios in f85-f86 range:")
for f in sorted(all_folios):
    transcribers = sorted(rosette_data[f].keys())
    for t in transcribers:
        toks = rosette_data[f][t]
        sections = set(tok.section for tok in toks)
        langs = set(tok.language for tok in toks)
        placements = Counter(tok.placement for tok in toks)
        n = len(toks)
        words = [tok.word for tok in toks[:5]]
        place_str = ', '.join(f'{p}:{c}' for p, c in placements.most_common(5))
        print(f"  {f:10} track={t} n={n:4} section={sections} lang={langs} placements=[{place_str}]")
        print(f"           first words: {words}")

# Which folios have H track?
print()
print("H-track coverage:")
for f in sorted(all_folios):
    if 'H' in rosette_data[f]:
        h_toks = rosette_data[f]['H']
        n_b = sum(1 for t in h_toks if t.language == 'B')
        n_a = sum(1 for t in h_toks if t.language == 'A')
        n_na = sum(1 for t in h_toks if t.language not in ('A', 'B'))
        print(f"  {f}: H-track {len(h_toks)} tokens (B={n_b}, A={n_a}, other={n_na})")
    else:
        print(f"  {f}: NO H-track data")

# Line counts per folio
print()
print("Lines per folio (H-track Currier B only):")
for f in sorted(all_folios):
    if 'H' in rosette_data[f]:
        b_toks = [t for t in rosette_data[f]['H'] if t.language == 'B']
        if b_toks:
            lines = set(t.line for t in b_toks)
            print(f"  {f}: {len(lines)} lines, {len(b_toks)} tokens")
