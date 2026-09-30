"""PHASE_775 lock audit, part b (controls only; B's token lines are never scored).

  SKIP2     no-message second-order token habit: habit3, but with probability p the next token is drawn from B's
            successors of the token TWO back (a lag-2 identity dependence; B adjacent-pair tables only)
  KHAB      context-keyed cipher (true key K1 or K2) whose hidden stream is a habit3 corpus (a first-order no-message
            process over whole tokens): keying present, message absent
  KCLUST    context-keyed cipher of a no-order hidden stream with strong line-level clustering: plaintext word types
            are split into 4 random groups, each line draws one group and its units are sampled from the plaintext's
            unigram restricted to that group (no word order at all)

Same scorer as audit_plants775.py (lag-1 = key775.run exactly, plus lag-2 on the same EF samples).
Usage: python audit_plants775b.py [workers<=4]
"""
import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_plants775 as A  # noqa: E402

OUT = A.OUT


def gen_skip2(sk, base, p, rng):
    out = []
    for ln in sk['lines']:
        prev, prev2, cur = None, None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = prev2 = None
                continue
            src = prev2 if (prev2 is not None and rng.random() < p) else prev
            t = base.draw(src, 1.0, rng)
            cur.append(t)
            prev2, prev = prev, t
        out.append(cur)
    return out


def specs():
    S = []
    for p in (0.3, 0.6):
        for s in range(2):
            S.append(('SKIP2', p, None, None, 775700 + 10 * s + int(10 * p)))
    for key in (1, 2):
        for s in range(2):
            S.append(('KHAB', None, key, None, 775800 + 10 * s + key))
        for pt in (('NT_la', 0), ('LAT_rec', 0)):
            S.append(('KCLUST', 4, key, pt, 775900 + key))
    return S


def run_one(spec):
    A._setup()
    import gen775 as GK
    G = GK.G
    HR = G.HR
    kind, par, key, pt, seed = spec
    t0 = time.time()
    sk = HR.b_skeleton()
    rng = np.random.default_rng(seed)
    info = {}
    if kind == 'SKIP2':
        base = A.H3(sk['lines'], HR.token_class, HR.GLYPH_RE)
        lines = gen_skip2(sk, base, par, rng)
    elif kind == 'KHAB':
        hid = HR.habit3_lines(sk, seed + 5)
        stream = [w for ln in hid for w in ln if w is not None]
        assert len(stream) == HR.n_certain(sk)
        lines = GK.keyed_cipher(stream, sk, key, seed)
        info['O'] = GK.plaintext_order_index(stream, sk)
    else:
        words = G.segment_stream(G.plaintext_words(pt[0]), sk, pt[1])
        uc = Counter(words)
        types = sorted(uc)
        grp = {u: int(g) for u, g in zip(types, rng.integers(par, size=len(types)))}
        pools = []
        for g in range(par):
            us = [u for u in types if grp[u] == g]
            w = np.array([uc[u] for u in us], dtype=float)
            pools.append((us, np.cumsum(w / w.sum())))
        stream = []
        for ln in sk['lines']:
            us, cum = pools[int(rng.integers(par))]
            for w in ln:
                if w is not None:
                    stream.append(us[min(int(np.searchsorted(cum, rng.random())), len(us) - 1)])
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
    fn = OUT / 'audit_plants775b.json'
    logf = open(OUT / 'audit_plants775b_log.txt', 'w', encoding='utf-8')

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
            log(f'[{time.time() - T0:6.0f}s] {name:40s} O {r.get("O", float("nan")):.3f} | lag1 dS0 {a["dS_K0"]:+.4f} '
                f'G1 {a["G_K1"]:+.4f} p {a["p_K1"]:.3f} G2 {a["G_K2"]:+.4f} p {a["p_K2"]:.3f} | lag2 dS0 '
                f'{b["dS_K0"]:+.4f} G1 {b["G_K1"]:+.4f} G2 {b["G_K2"]:+.4f}')
            json.dump(out, open(fn, 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
