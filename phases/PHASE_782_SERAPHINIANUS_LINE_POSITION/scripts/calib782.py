#!/usr/bin/env python3
"""PHASE_782 calibration and certification (pre-registration v2), on B and within-line-shuffled CS only.

  python calib782.py run      C1-C5, the split artifact, the Brunschwig anchor -> results/calib782.json
                              (replicates -> results/calib782_reps.jsonl, resumable)
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core782 as C  # noqa: E402

RES = C.PH / 'results'
SEED = 782_000_000
R_PERM = 500
B_BOOT = 2000
N_REAL = 20
N_REP = 200
WORKERS = 6
NOISE = {'clean': (0.0, 0.0, 0.0), 'matched': (0.18, 0.02, 0.02), 'heavy': (0.30, 0.05, 0.05)}
TRUNC = (0.05, 0.10, 0.20)
W = {}
# Configuration (E6 permitted revisions; chosen on controls only): chunk length L (K = 2L), primary units raw or top-8.
CFG_L = int(os.environ.get('PHASE782_L', '40'))
CFG_TOPK = int(os.environ.get('PHASE782_TOPK', '0')) or None
SUFFIX = '' if (CFG_L == 40 and not CFG_TOPK) else f'_L{CFG_L}' + (f'_top{CFG_TOPK}' if CFG_TOPK else '')
CHUNK_KW = {'L': CFG_L, 'K': 2 * CFG_L, **({'topk': CFG_TOPK} if CFG_TOPK else {})}


def CSET(lines, rng, **kw):
    """ChunkSet with the configured L, K and units; a two-character request under top-k uses k-1 per-chunk symbols."""
    merged = {**CHUNK_KW, **kw}
    if kw.get('interior'):
        merged['K'] = CFG_L
    if merged.get('first_n') == 2:
        tk = merged.pop('topk', None)
        merged['topk_per_chunk'] = (tk - 1) if tk else 24
    return C.ChunkSet(lines, rng, **merged)


def log(msg):
    print(msg, flush=True)
    with open(RES / f'calib_log782{SUFFIX}.txt', 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')


def stable_rng(tag, rep=0):
    s = sum((i + 1) * ord(c) for i, c in enumerate(tag)) % 997
    return np.random.default_rng(SEED + 100_000 * s + rep)


def _init():
    os.environ['OMP_NUM_THREADS'] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    W['B'] = C.load_b()
    W['margB'] = C.unit_marginals(W['B'])
    W['frag'] = C.cs_marginals()['fragment_strokes']


# ------------------------------------------------------------------------------------------------ B pieces
def b_excess(lines, rng, **kw):
    return CSET(lines, rng, **kw).excess(R_PERM, rng)


def b_realisations(setting, shuffled_first=False, n=N_REAL, **kw):
    q, s, m = NOISE[setting]
    out = []
    for r in range(n):
        rng = stable_rng(f'B-{setting}-{"sh" if shuffled_first else "real"}-{kw}', r)
        lines = W['B']
        if shuffled_first:
            lines = C.shuffle_lines(lines, rng)
        if q or s or m:
            lines = C.degrade(lines, q, s, m, rng, W['margB'])
        out.append(b_excess(lines, rng, **kw))
    return out


def tilts():
    """B's I/M/F first-unit log-ratios by frequency rank, mapped onto CS non-fragment first characters by rank."""
    B = W['B']
    cnt = {0: Counter(), 1: Counter(), 2: Counter()}
    for L in B:
        if not C.eligible(L):
            continue
        n = len(L.toks)
        for i, t in enumerate(L.toks):
            if t is None:
                continue
            cnt[0 if i == 0 else 2 if i == n - 1 else 1][t[0]] += 1
    allc = cnt[0] + cnt[1] + cnt[2]
    mg = C.cs_marginals()
    frag = set(mg['fragment_strokes'])
    cs_lines = C._load_cs_raw()            # marginal only: first characters pooled over all positions
    cs_first = Counter(t[0] for L in cs_lines for t in L.toks if t is not None and t[0] not in frag)
    b_rank = [u for u, _ in allc.most_common()]
    c_rank = [u for u, _ in cs_first.most_common()]
    k = min(len(b_rank), len(c_rank))
    tot = {z: sum(cnt[z].values()) for z in cnt}
    out = {}
    for z in (0, 2):
        w = {}
        for i in range(k):
            u = b_rank[i]
            r = np.log(((cnt[z][u] + 0.5) / tot[z]) / ((cnt[1][u] + 0.5) / tot[1]))
            w[c_rank[i]] = (float(cs_first[c_rank[i]]), float(r))      # (CS base weight, B log-ratio)
        out[z] = w
    return out[0], out[2], {'mapping': list(zip(c_rank[:k], b_rank[:k]))}


def tilted(w, lam):
    return {c: b * float(np.exp(lam * r)) for c, (b, r) in w.items()}


# ------------------------------------------------------------------------------------------------ replicate tasks
def task(args):
    kind, setting, rep = args
    t0 = time.time()
    rng = stable_rng(f'{kind}-{setting}', rep)
    cs = C.load_cs(rng=rng)                                   # within-line shuffled (pre-lock guard)
    out = {'kind': kind, 'setting': setting, 'rep': rep}
    if kind == 'c5':
        if setting == 'none':
            pl = cs
        elif setting.startswith('trunc'):
            pl = C.plant_truncation(cs, float(setting[5:]), rng)
        else:
            pl = C.plant_splits(cs, 0.05, rng)
        g = CSET(C.guard(pl, W['frag']), rng).excess(R_PERM, rng)
        u = CSET(pl, rng).excess(R_PERM, rng)
        out.update({'guarded_median': float(np.median(g)), 'unguarded_median': float(np.median(u))})
    elif kind == 'c4b':
        p, lam = W['plant_p'], W['plant_lam']
        tI, tF = W['tilt_I'], W['tilt_F']
        pl = C.plant_edges(cs, p, tI, tF, rng)
        raw = CSET(pl, rng).excess(R_PERM, rng)
        gd = CSET(C.guard(pl, W['frag']), rng).excess(R_PERM, rng)
        a = C.auc_block(W['b_clean'], raw, rng, B=B_BOOT)
        b = C.auc_block(W['b_clean'], gd, rng, B=B_BOOT)
        out.update({'raw_median': float(np.median(raw)), 'guarded_median': float(np.median(gd)),
                    'auc_raw': a, 'auc_guarded': b, 'reached': bool(a['hi'] <= 0.65 and b['hi'] <= 0.65)})
    out['sec'] = round(time.time() - t0, 1)
    return out


def _init_c4b(p, lam, tI, tF, b_clean):
    _init()
    W.update({'plant_p': p, 'plant_lam': lam, 'tilt_I': tI, 'tilt_F': tF, 'b_clean': b_clean})


def run_pool(tasks, name, initializer=_init, initargs=()):
    path = RES / name
    done = {}
    if path.exists():
        for ln in open(path, encoding='utf-8'):
            d = json.loads(ln)
            done[(d['kind'], d['setting'], d['rep'])] = d
    todo = [t for t in tasks if t not in done]
    log(f'{name}: {len(done)} done, {len(todo)} to run')
    t0 = time.time()
    if todo:
        with Pool(WORKERS, initializer=initializer, initargs=initargs) as pool, open(path, 'a', encoding='utf-8') as fh:
            for k, r in enumerate(pool.imap_unordered(task, todo, chunksize=2)):
                fh.write(json.dumps(r) + '\n')
                fh.flush()
                done[(r['kind'], r['setting'], r['rep'])] = r
                if (k + 1) % 50 == 0:
                    log(f'  {name}: {k + 1}/{len(todo)} ({time.time() - t0:.0f}s)')
    return [done[t] for t in tasks]


# ------------------------------------------------------------------------------------------------ stages
def calibrate_p(tI, tF, target, rng):
    """Smallest plant probability whose planted (raw, shuffled-CS) median excess reaches the B clean median, by
    bisection on 6 replicates per point; if p = 1 falls short, the tilt is sharpened (log-ratios times lam)."""
    def med(p, I, F, n=6):
        vals = []
        for r in range(n):
            rr = stable_rng(f'calp-{p:.4f}', r)
            cs = C.load_cs(rng=rr)
            vals.append(np.median(CSET(C.plant_edges(cs, p, I, F, rr), rr).excess(200, rr)))
        return float(np.median(vals))
    lam = 1.0
    I, F = tilted(tI, lam), tilted(tF, lam)
    while med(1.0, I, F) < target and lam < 16:
        lam *= 2
        I, F = tilted(tI, lam), tilted(tF, lam)
    lo, hi = 0.0, 1.0
    for _ in range(10):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if med(mid, I, F) < target else (lo, mid)
    return hi, lam, I, F


def run():
    RES.mkdir(exist_ok=True)
    t0 = time.time()
    _init()
    out = {'pre_registration': 'v2', 'config': CHUNK_KW, 'R_perm': R_PERM, 'B_boot': B_BOOT, 'n_real': N_REAL}
    mg = C.cs_marginals()
    out['cs_marginals'] = {'fragment_strokes': ''.join(mg['fragment_strokes']),
                           'fragment_initial_share': mg['fragment_initial_tokens'] / mg['n_tokens'],
                           'one_char_share': mg['one_char_tokens'] / mg['n_tokens']}
    raw = C._load_cs_raw()
    out['cs_lines'] = {'lines': len(raw), 'para_first_analogue': sum(L.first for L in raw),
                       'block_first': sum(L.flags['block_first'] for L in raw),
                       'after_short': sum(L.flags['after_short'] for L in raw),
                       'wide_block_lines': sum(L.flags['wide_block'] for L in raw),
                       'long_lines': sum(L.flags['long_line'] for L in raw),
                       'block_code_23_lines': sum(L.flags['block_code_23'] for L in raw)}
    # B clean, shuffled, degraded
    rng = stable_rng('B-clean')
    cb = CSET(W['B'], rng)
    b_clean = cb.excess(R_PERM, rng)
    out['b_chunks'] = {'n': len(b_clean), 'leftover_lines': cb.n_leftover_lines, 'groups': Counter(cb.chunk_group)}
    rng = stable_rng('B-shuffled')
    b_sh = b_excess(C.shuffle_lines(W['B'], rng), rng)
    reals = {s: b_realisations(s) for s in ('matched', 'heavy')}
    split_art = {s: float(np.median(np.concatenate(b_realisations(s, shuffled_first=True, n=10)))) for s in ('matched', 'heavy')}
    out['b_median_excess'] = {'clean': float(np.median(b_clean)), 'shuffled': float(np.median(b_sh)),
                              **{s: float(np.median(np.concatenate(v))) for s, v in reals.items()}}
    out['split_artifact_median_excess'] = split_art
    log(f"B median excess {out['b_median_excess']}; split artifact (shuffled then degraded) {split_art}")
    # C1
    blocks = [list(range(i, min(i + 3, len(b_clean)))) for i in range(0, len(b_clean), 3)]
    h1 = np.concatenate([b_clean[b] for b in blocks[0::2]])
    h2 = np.concatenate([b_clean[b] for b in blocks[1::2]])
    c1 = C.auc_block(h1, h2, stable_rng('C1'), B=B_BOOT)
    out['C1'] = {**c1, 'pass': bool(c1['lo'] <= 0.5 <= c1['hi'])}
    # C2
    c2 = C.auc(b_clean, b_sh)
    out['C2'] = {'auc': c2, 'pass': bool(c2 >= 0.95)}
    # C3
    c3 = C.auc_block(reals['heavy'], b_sh, stable_rng('C3'), B=B_BOOT)
    out['C3'] = {**c3, 'pass': bool(c3['lo'] >= 0.80)}
    log(f"C1 {out['C1']}\nC2 {out['C2']}\nC3 {out['C3']}")
    # C4a: several shuffles of CS, conditions (a) raw and (b) two characters
    c4a = []
    for k in range(5):
        r = stable_rng('C4a', k)
        cs = C.load_cs(rng=r)
        ea = CSET(cs, r).excess(R_PERM, r)
        eb = CSET(cs, r, first_n=2).excess(R_PERM, r)
        a = C.auc_block(reals['heavy'], ea, r, B=B_BOOT)
        b = C.auc_block(reals['heavy'], eb, r, B=B_BOOT)
        c4a.append({'shuffle': k, 'a': a, 'b': b, 'cs_median_raw': float(np.median(ea)), 'cs_median_two': float(np.median(eb)),
                    'pass': bool(a['lo'] >= 0.80 and b['lo'] >= 0.80)})
    out['C4a'] = {'shuffles': c4a, 'pass': all(x['pass'] for x in c4a)}
    log(f"C4a pass {out['C4a']['pass']}: " + '; '.join(f"a lo {x['a']['lo']:.3f} b lo {x['b']['lo']:.3f}" for x in c4a))
    # Brunschwig anchor (descriptive)
    r = stable_rng('BR')
    br = CSET(C.load_brunschwig(), r, within_groups=False).excess(R_PERM, r)
    out['brunschwig_anchor'] = {'n_chunks': len(br), 'median_excess': float(np.median(br)),
                                'auc_B_clean_vs_BR': C.auc_block(b_clean, br, r, B=B_BOOT)}
    log(f"Brunschwig anchor: {out['brunschwig_anchor']}")
    json.dump(out, open(RES / f'calib782{SUFFIX}.json', 'w', encoding='utf-8'), indent=1, default=float)
    # C5 guard
    settings = ['none'] + [f'trunc{t}' for t in TRUNC] + ['split0.05']
    rows = run_pool([('c5', s, i) for s in settings for i in range(N_REP)], f'calib782_reps{SUFFIX}.jsonl')
    base = np.array([x['guarded_median'] for x in rows if x['setting'] == 'none'])
    lo, hi = np.percentile(base, [5, 95])
    c5 = {'unplanted_central90': [float(lo), float(hi)], 'B_clean_median': out['b_median_excess']['clean'], 'settings': {}}
    for s in settings[1:]:
        g = np.median([x['guarded_median'] for x in rows if x['setting'] == s])
        u = np.median([x['unguarded_median'] for x in rows if x['setting'] == s])
        c5['settings'][s] = {'guarded_median': float(g), 'unguarded_median': float(u),
                             'unguarded_over_B_clean': float(u / out['b_median_excess']['clean']),
                             'pass': bool(lo <= g <= hi)}
    c5['unplanted_unguarded_median'] = float(np.median([x['unguarded_median'] for x in rows if x['setting'] == 'none']))
    c5['pass'] = all(v['pass'] for v in c5['settings'].values())
    out['C5'] = c5
    log(f"C5 pass {c5['pass']}: {c5}")
    json.dump(out, open(RES / f'calib782{SUFFIX}.json', 'w', encoding='utf-8'), indent=1, default=float)
    # C4b plants
    tI, tF, info = tilts()
    p, lam, I, F = calibrate_p(tI, tF, out['b_median_excess']['clean'], stable_rng('calp'))
    out['C4b_plant'] = {'p': p, 'lam': lam, **info}
    log(f'C4b plant: p {p:.3f}, lam {lam}')
    rows = run_pool([('c4b', 'plant', i) for i in range(N_REP)], f'calib782_c4b{SUFFIX}.jsonl', initializer=_init_c4b,
                    initargs=(p, 1.0, I, F, b_clean))
    fire = float(np.mean([x['reached'] for x in rows]))
    out['C4b'] = {'reached_rate': fire, 'pass': bool(fire >= 0.80),
                  'planted_raw_median': float(np.median([x['raw_median'] for x in rows])),
                  'planted_guarded_median': float(np.median([x['guarded_median'] for x in rows]))}
    log(f"C4b {out['C4b']}")
    out['runtime_s'] = round(time.time() - t0, 1)
    json.dump(out, open(RES / f'calib782{SUFFIX}.json', 'w', encoding='utf-8'), indent=1, default=float)
    log('calibration done')


if __name__ == '__main__':
    {'run': run}[sys.argv[1]]()
