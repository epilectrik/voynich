"""Check placement codes and token metadata for all f85v2 regions."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import RosettesAnalyzer

ra = RosettesAnalyzer()

REGIONS = ['B1','B2','B3','C2','D1','M1','M2','M3',
           'N1','N2','U1','U2','U3','V1','V2','W1']

print("PLACEMENT AND LABEL FLAGS PER REGION")
print("=" * 60)
for region in REGIONS:
    toks = ra.get_tokens('f85v2', region)
    if not toks:
        continue
    placements = set()
    labels = set()
    sections = set()
    for t in toks:
        placements.add(t.placement)
        labels.add(t.is_label)
        sections.add(t.section)
    print(f'{region:3s}: placement={placements}, is_label={labels}, section={sections}')

# Now check: are there ANY other placement codes on f85v2 that we're missing?
print("\n\nALL PLACEMENT CODES ON f85v2")
print("=" * 60)
from scripts.voynich import Transcript
tx = Transcript()
f85v2_placements = {}
for t in tx.all(h_only=False):
    if t.folio == 'f85v2':
        p = t.placement
        if p not in f85v2_placements:
            f85v2_placements[p] = {'tokens': [], 'transcribers': set()}
        w = t.word.strip()
        if w and '*' not in w:
            f85v2_placements[p]['tokens'].append(w)
            f85v2_placements[p]['transcribers'].add(t.transcriber)

for p in sorted(f85v2_placements.keys()):
    data = f85v2_placements[p]
    words = data['tokens']
    tr = data['transcribers']
    print(f'  {p:5s}: {len(words)} tokens, transcribers={tr}')
    print(f'         {" ".join(words[:10])}{"..." if len(words) > 10 else ""}')

# Also check OTHER rosettes folios for comparison
print("\n\nOTHER ROSETTES FOLIOS - PLACEMENT CODES")
print("=" * 60)
for folio in ['f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']:
    folio_placements = {}
    for t in tx.all(h_only=False):
        if t.folio == folio:
            p = t.placement
            if p not in folio_placements:
                folio_placements[p] = 0
            w = t.word.strip()
            if w and '*' not in w:
                folio_placements[p] += 1
    if folio_placements:
        codes = ', '.join(f'{p}={n}' for p, n in sorted(folio_placements.items()))
        print(f'  {folio}: {codes}')
