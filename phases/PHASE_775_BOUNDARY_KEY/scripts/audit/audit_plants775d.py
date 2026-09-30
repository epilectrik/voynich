"""PHASE_775 lock audit, part d (controls only; B's token lines are never scored).

  MIDMODE   no-message habit3 with line- (or paragraph-) level clustering of MIDDLEs: B's MIDDLE types are split into
            4 random groups; each unit (line or paragraph) draws one group and habit3's successor probabilities are
            multiplied by w for tokens whose MIDDLE is in that group. The prefix and first glyph still follow habit3's
            context-conditioned choice, so the same MIDDLE is spelled with context-dependent beginnings (B's junction
            coupling) while MIDDLEs cluster by line -- the non-cipher route "junction spelling rule + line-level
            MIDDLE homogeneity (C1212/C1563 + C1214)" to a positive key gain, if there is one.

Usage: python audit_plants775d.py [workers<=4]
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_plants775 as A  # noqa: E402

OUT = A.OUT


class Tilt:
    def __init__(self, base, group_of, w):
        self.b, self.g, self.w = base, group_of, w
        self.cache = {}

    def draw(self, prev, grp, rng):
        key, counter = self.b.table(prev)
        ck = (key, grp)
        if ck not in self.cache:
            keys = list(counter)
            p = np.array([counter[k] * (self.w if self.g.get(k) == grp else 1.0) for k in keys], dtype=float)
            self.cache[ck] = (keys, np.cumsum(p / p.sum()))
        keys, cum = self.cache[ck]
        return keys[min(int(np.searchsorted(cum, rng.random())), len(keys) - 1)]


def specs():
    S = []
    for mode in ('line', 'para'):
        for w in (2.0, 4.0, 8.0):
            for s in range(2):
                S.append(('MIDMODE', mode, w, 776400 + 10 * s + int(w) + 100 * (mode == 'para')))
    return S


def run_one(spec):
    A._setup()
    import gen775 as GK
    from scripts.voynich import Morphology
    HR = GK.G.HR
    kind, mode, w, seed = spec
    t0 = time.time()
    sk = HR.b_skeleton()
    lt = GK.b_line_types(sk)
    rng = np.random.default_rng(seed)
    base = A.H3(sk['lines'], HR.token_class, HR.GLYPH_RE)
    morph = Morphology()
    mid = {t: (morph.extract(t).middle or t) for t in base.uni}
    mtypes = sorted(set(mid.values()))
    mg = {m: int(g) for m, g in zip(mtypes, rng.integers(4, size=len(mtypes)))}
    group_of = {t: mg[m] for t, m in mid.items()}
    T = Tilt(base, group_of, w)
    unit = A.units_of(sk, lt, mode)
    pick = {u: int(rng.integers(4)) for u in set(unit)}
    lines = []
    for li, ln in enumerate(sk['lines']):
        g = pick[unit[li]]
        prev, cur = None, []
        for x in ln:
            if x is None:
                cur.append(None)
                prev = None
                continue
            t = T.draw(prev, g, rng)
            cur.append(t)
            prev = t
        lines.append(cur)
    assert lines != sk['lines'], 'refusing to score B'
    # line homogeneity of MIDDLEs (plant property): mean within-line share of the line's modal MIDDLE group
    share = []
    for ln in lines:
        gs = [group_of[t] for t in ln if t is not None]
        if len(gs) >= 4:
            share.append(max(np.bincount(gs, minlength=4)) / len(gs))
    res = A.score(lines, GK.ef_groups(sk), seed)
    name = '|'.join(str(x) for x in spec)
    return name, {'spec': [str(x) for x in spec], 'modal_group_share': float(np.mean(share)), 'res': res,
                  'runtime_s': time.time() - t0}


def main():
    workers = min(4, int(sys.argv[1]) if len(sys.argv) > 1 else 4)
    A._setup()
    TH = json.load(open(A.PH.parent / 'results' / 'thresholds775.json', encoding='utf-8'))
    fn = OUT / 'audit_plants775d.json'
    logf = open(OUT / 'audit_plants775d_log.txt', 'w', encoding='utf-8')

    def log(m):
        print(m, flush=True)
        logf.write(m + '\n')
        logf.flush()
    log(f'tau_K1 {TH["tau_K1"]:.5f}  tau_K2 {TH["tau_K2"]:.5f}  R {A.R}')
    out = {}
    T0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in specs()}
        for f in as_completed(futs):
            try:
                name, r = f.result()
            except Exception as e:  # noqa: BLE001
                log(f'FAILED {futs[f]}: {e!r}')
                continue
            out[name] = r
            a, b = r['res']['lag1'], r['res']['lag2']
            log(f'[{time.time() - T0:6.0f}s] {name:30s} modal share {r["modal_group_share"]:.3f} | lag1 dS0 '
                f'{a["dS_K0"]:+.4f} G1 {a["G_K1"]:+.4f} p {a["p_K1"]:.3f} G2 {a["G_K2"]:+.4f} p {a["p_K2"]:.3f} | '
                f'lag2 dS0 {b["dS_K0"]:+.4f} G1 {b["G_K1"]:+.4f} G2 {b["G_K2"]:+.4f}')
            json.dump(out, open(fn, 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
