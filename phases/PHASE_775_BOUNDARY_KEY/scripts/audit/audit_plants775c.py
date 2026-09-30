"""PHASE_775 lock audit, part c (controls only; B's token lines are never scored).

  TEMPPOS   no-message habit3 whose sampling temperature follows the within-line position (quintile 0..4): beta rises
            from lo to hi along the line ('up') or falls ('down') -- a line-position effect beyond the three EF zones
  FOLFIT    no-message habit3 fitted separately within each folio (B's adjacent pairs within the folio, declared class
            of exposure; thin tables back off to class/glyph and then the folio's own unigram), so every folio has its
            own concentrated vocabulary (the PHASE_774 folio-concentration concern)
  KCLUST    as part b (keyed cipher, true key K1, of a no-order hidden stream clustered by line), more plaintexts and
            seeds, and a paragraph-clustered version

Usage: python audit_plants775c.py [workers<=4]
"""
import json
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_plants775 as A  # noqa: E402

OUT = A.OUT


def gen_temppos(sk, base, lo, hi, rng):
    out = []
    for ln in sk['lines']:
        prev, cur = None, []
        n = len(ln)
        for p, w in enumerate(ln):
            if w is None:
                cur.append(None)
                prev = None
                continue
            q = min(4, int(5 * p / max(n, 1)))
            beta = lo + (hi - lo) * q / 4
            t = base.draw(prev, round(beta, 3), rng)
            cur.append(t)
            prev = t
        out.append(cur)
    return out


def kclust_stream(words, sk, unit, n_groups, rng):
    uc = Counter(words)
    types = sorted(uc)
    grp = {u: int(g) for u, g in zip(types, rng.integers(n_groups, size=len(types)))}
    pools = []
    for g in range(n_groups):
        us = [u for u in types if grp[u] == g]
        w = np.array([uc[u] for u in us], dtype=float)
        pools.append((us, np.cumsum(w / w.sum())))
    pick = {u: int(rng.integers(n_groups)) for u in set(unit)}
    stream = []
    for li, ln in enumerate(sk['lines']):
        us, cum = pools[pick[unit[li]]]
        for w in ln:
            if w is not None:
                stream.append(us[min(int(np.searchsorted(cum, rng.random())), len(us) - 1)])
    return stream


def specs():
    S = []
    for lo, hi in ((0.5, 2.0), (2.0, 0.5)):
        S.append(('TEMPPOS', (lo, hi), None, None, 776000 + int(10 * lo)))
    for s in range(2):
        S.append(('FOLFIT', None, None, None, 776100 + s))
    for pt in (('NT_it', 0), ('ITA_dante', 0), ('NT_la', 1), ('LAT_sismel', 0)):
        S.append(('KCLUST', 'line', 1, pt, 776201))
        S.append(('KCLUST', 'para', 1, pt, 776211))
    for s in range(3):
        S.append(('KCLUST', 'line', 1, ('NT_la', 0), 776301 + 10 * s))
    return S


def run_one(spec):
    A._setup()
    import gen775 as GK
    G = GK.G
    HR = G.HR
    kind, par, key, pt, seed = spec
    t0 = time.time()
    sk = HR.b_skeleton()
    lt = GK.b_line_types(sk)
    rng = np.random.default_rng(seed)
    info = {}
    if kind == 'TEMPPOS':
        base = A.H3(sk['lines'], HR.token_class, HR.GLYPH_RE)
        lines = gen_temppos(sk, base, par[0], par[1], rng)
    elif kind == 'FOLFIT':
        by = defaultdict(list)
        for i, f in enumerate(sk['folios']):
            by[f].append(i)
        lines = [None] * len(sk['lines'])
        for f, idx in by.items():
            T = A.H3([sk['lines'][i] for i in idx], HR.token_class, HR.GLYPH_RE)
            sub = {'lines': [sk['lines'][i] for i in idx]}
            gen = A.generate(sub, list(range(len(idx))), [T] * len(idx), [1.0] * len(idx), rng)
            for i, ln in zip(idx, gen):
                lines[i] = ln
    else:
        words = G.segment_stream(G.plaintext_words(pt[0]), sk, pt[1])
        stream = kclust_stream(words, sk, A.units_of(sk, lt, par), 4, rng)
        lines = GK.keyed_cipher(stream, sk, key, seed)
        info['O'] = GK.plaintext_order_index(stream, sk)
    assert lines != sk['lines'], 'refusing to score B'
    res = A.score(lines, GK.ef_groups(sk), seed)
    name = '|'.join(str(x) for x in spec)
    return name, {'spec': [str(x) for x in spec], **info, 'res': res, 'runtime_s': time.time() - t0}


def main():
    workers = min(4, int(sys.argv[1]) if len(sys.argv) > 1 else 4)
    A._setup()
    TH = json.load(open(A.PH.parent / 'results' / 'thresholds775.json', encoding='utf-8'))
    fn = OUT / 'audit_plants775c.json'
    logf = open(OUT / 'audit_plants775c_log.txt', 'w', encoding='utf-8')

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
            log(f'[{time.time() - T0:6.0f}s] {name:44s} O {r.get("O", float("nan")):.3f} | lag1 dS0 {a["dS_K0"]:+.4f} '
                f'G1 {a["G_K1"]:+.4f} p {a["p_K1"]:.3f} G2 {a["G_K2"]:+.4f} p {a["p_K2"]:.3f} | lag2 dS0 '
                f'{b["dS_K0"]:+.4f} G1 {b["G_K1"]:+.4f} G2 {b["G_K2"]:+.4f}')
            json.dump(out, open(fn, 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
