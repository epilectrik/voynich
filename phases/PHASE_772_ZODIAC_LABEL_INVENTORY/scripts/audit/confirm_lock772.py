#!/usr/bin/env python3
"""PHASE_772 lock confirmation pass (lean-expert). Runs in about 1-2 minutes.

No R / W / duplicate / recurrence statistic of the real labels is computed. The real labels are used only for
structural counts (label counts, ring and arc sizes, clock ties, glyph-unit lengths) and for the sign sizes.

  A. Structural checks on the ZL labels (counts only).
  B. H-track loader: labels per page (counts only), so the never-exercised H path cannot crash the locked run.
  C. Base pool provenance: tokens vs types, and no zodiac page contributes.
  D. Unit tests of zod772.verdict on synthetic inputs, with the binding thresholds from results/cal772.json.
     The case 'W high at N1 + low at N2' must give UNRESOLVED (fails until PALETTE requires W not low at N2).
  E. Exact replay of the first R-threshold blocks of cal772.py (lam 0, 0.5, 1, 2; same seed and RNG stream),
     compared with results/cal772.json.
"""
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import zod772 as Z  # noqa: E402

CAL = json.loads((HERE.parent / 'results' / 'cal772.json').read_text())
THR = {lam: CAL['R_thresholds'][lam]['N2'] for lam in CAL['R_thresholds']}
t0 = time.time()
fails = []


def check(name, ok, detail=''):
    print(f"  [{'OK ' if ok else 'FAIL'}] {name} {detail}", flush=True)
    if not ok:
        fails.append(name)


# ------------------------------------------------------------------------------------------------ A. structure
print('A. structural checks (counts only)')
lab = Z.load_labels()
alll = Z.load_labels(include_unreadable=True)
check('readable labels = 290', len(lab) == 290, len(lab))
check('unreadable labels = 8', len(alll) - len(lab) == 8, len(alll) - len(lab))
kinds = Counter()
cur = None
for raw in open(Z.ZL, encoding='utf-8', errors='replace'):
    m = re.match(r'^<(f\w+)>', raw)
    if m and not re.match(r'^<f\w+\.', raw):
        cur = m.group(1) if m.group(1) in Z.SIGN else None
        continue
    if cur is None:
        continue
    m = re.match(r'^<(f\w+)\.(\w+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
    if m and m.group(1) == cur and m.group(4).startswith('L') and re.match(r'<!(\d\d):(\d\d)>', m.group(5)):
        kinds[m.group(4)] += 1
print('  label locus types with a clock position:', dict(kinds))
r0 = Counter(r['folio'] for r in alll if r['ring'] == 0)
r0r = Counter(r['folio'] for r in lab if r['ring'] == 0)
print('  ring-0 labels per page (all / readable):', dict(r0), dict(r0r))
check('ring 0 only on the three top-row pages', set(r0) <= Z.TOP_ROW_PAGES, sorted(r0))
check('13 readable ring-0 labels', sum(r0r.values()) == 13, sum(r0r.values()))
arcs = Counter((r['folio'], r['ring']) for r in alll)
small = {k: v for k, v in arcs.items() if v < 4}
print(f'  arcs (page, ring): {len(arcs)}; with >= 4 labels: {sum(v >= 4 for v in arcs.values())}; '
      f'fragments < 4: {small}')
ties = sum(n - len({r['clock'] for r in alll if (r['folio'], r['ring']) == k}) for k, n in arcs.items())
print('  clock ties within an arc (all labels):', ties)
ln2 = Counter(len(Z.units(Z.n2(r['form']))) for r in lab)
print('  N2 glyph-unit lengths:', dict(sorted(ln2.items())))
check('no readable label is a single N2 unit (first-unit strip gives no empty form)', ln2.get(1, 0) == 0,
      f'{ln2.get(1, 0)} single-unit labels')

# ----------------------------------------------------------------------------------------------- B. H track
print('B. H-track loader (counts only)')
h = Z.load_labels_h()
hp = Counter(r['folio'] for r in h)
zp = Counter(r['folio'] for r in lab)
print('  H labels per page:', dict(sorted(hp.items())))
print('  ZL labels per page:', dict(sorted(zp.items())))
check('H loader returns labels on all 12 pages', set(hp) == set(Z.SIGN), f'{len(h)} labels')
nw = Counter(len(r['words']) for r in h)
print('  H words per label:', dict(sorted(nw.items())))
check('H labels are label-sized (<= 4 words)', max(nw) <= 4, max(nw) if nw else None)

# -------------------------------------------------------------------------------------------- C. base pool
print('C. base pool')
pool = Z.currier_a_words()
print(f'  pool: {len(pool)} tokens, {len(set(pool))} types (draws are token-frequency weighted)')
lang, zod_hits = None, 0
for raw in open(Z.ZL, encoding='utf-8', errors='replace'):
    m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
    if m:
        L = re.search(r'\$L=(\w)', m.group(2))
        lang = L.group(1) if L else None
        page = m.group(1)
        continue
    m = re.match(r'^<(f\w+)\.(\w+),([@+=*&~])(\w+)>', raw)
    if m and lang == 'A' and m.group(4).startswith('P') and m.group(1) in Z.SIGN:
        zod_hits += 1
check('no zodiac page contributes to the pool', zod_hits == 0, zod_hits)

# ---------------------------------------------------------------------------------------- D. verdict logic
print('D. verdict logic (synthetic inputs, binding thresholds)')
q = {lam: THR[str(lam)]['q01'] for lam in Z.LAM_GRID}
q05_3 = THR['3.0']['q05']


def st(pl, ph):
    return {'p_low': pl, 'p_high': ph}


NS, LO, HI = st(0.5, 0.5), st(0.001, 0.999), st(0.999, 0.001)
cases = [
    ('both low, R >= q05(3)', (LO, LO, q05_3, q05_3), ('INVENTORY', None)),
    ('both low, R just below q05(3)', (LO, LO, q05_3 - 1 / 290, 0.1), ('UNRESOLVED', 2.0)),
    ('low N1 only, R tiny', (LO, NS, 0.1, 0.1), ('UNRESOLVED', 8.0)),
    ('low N2 only, R tiny', (NS, LO, 0.1, 0.1), ('UNRESOLVED', 8.0)),
    ('low N2 only + high N1 gives UNRESOLVED (needs the PALETTE edit)', (HI, LO, 0.1, 0.1), ('UNRESOLVED', 8.0)),
    ('neither low, R tiny', (NS, NS, 0.1, 0.1), ('NO INVENTORY (bounded, lam* = 8.0)', 8.0)),
    ('neither low, high N1, R tiny', (HI, NS, 0.1, 0.1), ('NO INVENTORY (bounded, lam* = 8.0) + PALETTE', 8.0)),
    ('R between q01(1) and q01(0.5)', (NS, NS, (q[1.0] + q[0.5]) / 2, 0.1), ('UNRESOLVED', 0.5)),
    ('R = q01(1) exactly (strict)', (NS, NS, q[1.0], 0.1), ('UNRESOLVED', 0.5)),
    ('R just below q01(1)', (NS, NS, q[1.0] - 1 / 290, 0.1), ('NO INVENTORY (bounded, lam* = 1.0)', 1.0)),
    ('R low but R_words high (AND rule)', (NS, NS, 0.1, 0.99), ('UNRESOLVED', 0.0)),
    ('R = 1 (lam 0 fails)', (NS, NS, 1.0, 1.0), ('UNRESOLVED', None)),
    ('R_words limits lam*', (NS, NS, 0.1, (q[3.0] + q[5.0]) / 2), ('NO INVENTORY (bounded, lam* = 3.0)', 3.0)),
]
for name, args, want in cases:
    got = Z.verdict(*args, THR)
    if want is None:
        print(f'  [NOTE] {name}: {got}')
    else:
        check(name, got == want, got)
# prefix rule with a non-monotone synthetic threshold table
thr_nm = {str(l): {'q01': v, 'q05': 0.99} for l, v in zip(Z.LAM_GRID, (1.0, 0.9, 0.5, 0.95, 0.95, 0.95, 0.95))}
check('prefix rule stops at the first failure', Z.verdict(NS, NS, 0.7, 0.7, thr_nm) == ('UNRESOLVED', 0.5),
      Z.verdict(NS, NS, 0.7, 0.7, thr_nm))
check('thresholds unrounded floats', all(isinstance(v['q01'], float) for v in THR.values()))
rng0 = np.random.default_rng(0)
nan_st = Z.w_test(['a', 'b', 'c', 'd'], [1, 1, 2, 2], rng0, 50)
check('W undefined gives p = 1 both ways', nan_st['p_low'] == 1.0 and nan_st['p_high'] == 1.0)

# ---------------------------------------------------------------------------------- E. calibration replay
print('E. replay of cal772.py R thresholds (lam 0, 0.5, 1, 2)')
rng = np.random.default_rng(7721)
pool = Z.currier_a_words()
sizes = Counter(r['sign'] for r in Z.load_labels())
check('sizes match cal772.json', dict(sizes) == CAL['sizes'] and len(pool) == CAL['pool_size'])
for lam in (0.0, 0.5, 1.0, 2.0):
    R = {k: [] for k in Z.NORMS}
    vis = []
    for _ in range(2000):
        forms, signs, v = Z.simulate(sizes, pool, rng, lam)
        vis.extend(v)
        for k, f in Z.NORMS.items():
            R[k].append(Z.dup_stats([f(w) for w in forms], signs)['R'])
    thr = {k: {'q01': float(np.quantile(v, 0.01)), 'q05': float(np.quantile(v, 0.05))} for k, v in R.items()}
    same = thr == CAL['R_thresholds'][str(lam)] and float(np.mean(vis)) == CAL['visible_change_share_N2'][str(lam)]
    check(f'lam {lam} thresholds and visible share reproduce exactly', same, f'({time.time() - t0:.0f} s)')

print(f'done {time.time() - t0:.0f} s; failures: {fails}')
