"""PHASE_774: summarise the pre-lock calibration (controls only).

For each representation x statistic: X and p for every control, grouped as design positives (by family and
plaintext), held-out positives, twins and no-message generators; the separation margin
min(design positive X) / max(negative X) per family.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).parent.parent / 'results'
d = json.load(open(OUT / (sys.argv[1] if len(sys.argv) > 1 else 'prelock_calib.json'), encoding='utf-8'))

STATS = [(rep, f'{st}{n}') for rep in ('TOK', 'MID', 'MIDn1') for n in (4, 5, 6)
         for st in ('RPT', 'RPTx')]


def X(v, rep, st):
    return v['reps'][rep][st]['X']


neg = [v for v in d.values() if v['kind'] == 'NEG']
twin = [v for v in d.values() if v['kind'] == 'TWIN']
pos = [v for v in d.values() if v['kind'] == 'POS']
print(f'{len(pos)} positives, {len(twin)} twins, {len(neg)} negatives')
fams = sorted({v['family'] for v in pos})
for rep, st in STATS:
    nx = [X(v, rep, st) for v in neg]
    tx = [X(v, rep, st) for v in twin]
    line = f'{rep:5s} {st:6s} | NEG max {max(nx):6.2f} (obs max {max(v["reps"][rep][st]["obs"] for v in neg):4d}) ' \
           f'| TWIN max {max(tx):6.2f} |'
    for fam in fams:
        dx = sorted((X(v, rep, st), v['plaintext']) for v in pos if v['family'] == fam and v['group'] == 'design')
        hx = sorted((X(v, rep, st), v['plaintext']) for v in pos if v['family'] == fam and v['group'] == 'heldout')
        if dx:
            line += f' {fam}: des min {dx[0][0]:.2f}({dx[0][1]})'
        if hx:
            line += f' ho min {hx[0][0]:.2f}({hx[0][1]})'
        line += ' ;'
    print(line)

print()
print('Per control (X at TOK5, MID5, MID6, MIDn1 6; obs/null in brackets):')
for name in sorted(d, key=lambda k: (d[k]['kind'], d[k]['family'], str(d[k]['plaintext']))):
    v = d[name]
    cells = []
    for rep, st in (('TOK', 'RPT5'), ('TOK', 'RPT6'), ('MID', 'RPT5'), ('MID', 'RPT6'), ('MIDn1', 'RPT6')):
        x = v['reps'][rep][st]
        cells.append(f'{rep}{st[-1]} {x["X"]:6.2f} [{x["obs"]}/{x["null_mean"]:.1f} p{x["p"]:.3f}]')
    print(f'{v["kind"]:4s} {v["group"]:7s} {v["family"]:9s} {str(v["plaintext"]):15s} {v["seed"]:5d} | '
          + ' | '.join(cells))
