#!/usr/bin/env python3
"""PHASE_780 pre-lock calibration (controls only; the Voynich text-picture alignment at k = 0 is never evaluated).

  python calib780.py setup     gates, anchors, generator parameters (bisections on pictures alone / text alone),
                               fidelity gates of the K1 generators, Brunschwig degradation -> results/calib_setup780.json
  python calib780.py k1        drift generators (V-A1): Zmax per replicate -> results/k1_780.jsonl
  python calib780.py k2        anchored writing sessions: Zmax per replicate -> results/k2_780.jsonl
  python calib780.py k3        plants on real texts with real pictures under a random shift (planted replicates only)
  python calib780.py k4        Brunschwig: own z* (K1 i-ii) and genre power with ablation rows
  python calib780.py summary   z*, MDE80, genre power -> results/calib780.json
Heavy stages run on WORKERS processes at Idle priority and append one JSON line per replicate (resumable)."""
from __future__ import annotations

import json
import math
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import binom

PH = Path('C:/git/voynich/phases/PHASE_780_HERBAL_PICTURE_TEXT')
sys.path.insert(0, str(PH / 'scripts'))
import core780 as K  # noqa: E402

DATA, RES, CODE_DIR = PH / 'data', PH / 'results', K.CODE_DIR
WORKERS = 6
N_K1, N_K1_BIND, N_K2, N_K2X2, N_K3, N_K4, N_K4Z = 500, 2000, 500, 200, 200, 200, 500
K3_GRID = (0.5, 1.0, 2.0, 4.0)
SEED = {'k1': 780_100_000, 'k2': 780_200_000, 'k3': 780_300_000, 'k4': 780_400_000, 'k4z': 780_500_000, 'setup': 780_600_000}
POOL_EXCL = 10            # donors more than this many positions away (pos units) and not on the target's leaf/bifolium
W = {}


def log(msg, f='calib_log780.txt'):
    print(msg, flush=True)
    with open(RES / f, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')


# ================================================================================================ data
def load_codes(corpus):
    key = json.load(open(DATA / 'key_code.json', encoding='utf-8'))
    out = {'A': {}, 'B': {}}
    for cset in 'AB':
        for p in sorted((DATA / 'codes').glob(f'codes_{cset}_{corpus}_*.json')):
            for code, feats in json.load(open(p, encoding='utf-8')).items():
                code = Path(code).stem
                if code in key and key[code]['corpus'] == corpus:
                    ident = key[code]['id']
                    out[cset][ident if corpus == 'V' else int(ident)] = feats
    return out


def v_data(arm='V-A1'):
    pages_all = json.load(open(DATA / 'pages_v.json', encoding='utf-8'))
    prep = json.load(open(DATA / 'prepare_summary.json', encoding='utf-8'))
    excl = set(prep['V_excluded_no_main_plant'])
    pages = sorted([p for p in pages_all if p['arm'] == arm and not p['excluded'] and p['folio'] not in excl],
                   key=lambda p: p['pos'])
    folios = [p['folio'] for p in pages]
    toks = K.voynich_texts(folios)
    feats = json.load(open(DATA / 'page_features_v.json', encoding='utf-8'))
    geom = json.load(open(DATA / 'geometry.json', encoding='utf-8'))
    codes = load_codes('V')
    codes = {s: {f: codes[s][f] for f in folios if f in codes[s]} for s in codes}
    g = K.gate('V', folios, codes['A'], codes['B'])
    X, names = K.v_covariates(pages, feats, [len(t) for t in toks])
    leaf = np.array([p['leaf'] for p in pages])
    special = {87: 90, 90: 87, 93: 96, 96: 93}
    conj = np.array([special.get(l, K.conjugate(l, (l - 1) // 8 * 8 + 1)) for l in leaf])
    return {'pages': pages, 'ids': folios, 'toks': toks, 'feats': feats, 'X': X, 'Xnames': names,
            'blocks': K.v_blocks(pages), 'T': K.text_similarity(toks, 'V'), 'codes': codes, 'gate': g,
            'heights': [geom[f]['drawing_height'] for f in folios], 'pos': np.array([p['pos'] for p in pages]),
            'leaf': leaf, 'conj': conj, 'group': [p['quire'] for p in pages]}


def br_data():
    entries = sorted(json.load(open(DATA / 'entries_br.json', encoding='utf-8')), key=lambda e: e['head_line'])
    codes = load_codes('BR')
    noplant = {i for i in codes['A'] if str(codes['A'][i].get('main_plant', 'yes')).lower() == 'no'
               and str(codes['B'].get(i, {}).get('main_plant', 'yes')).lower() == 'no'}
    entries = [e for e in entries if e['idx'] not in noplant]          # amendment 9: non-plant woodcuts
    for r, e in enumerate(entries):
        e['rank'] = r
    ids = [e['idx'] for e in entries]
    codes = {s: {i: codes[s][i] for i in ids if i in codes[s]} for s in codes}
    g = K.gate('BR', ids, codes['A'], codes['B'])
    return {'entries': entries, 'ids': ids, 'toks': K.br_texts(entries), 'codes': codes, 'gate': g,
            'heights': [e['woodcut_height'] for e in entries], 'pos': np.array([e['rank'] for e in entries]) * 2,
            'leaf': np.array([-1] * len(entries)), 'conj': np.array([-2] * len(entries)),
            'group': [e['chapter'] or '?' for e in entries]}


# ================================================================================================ picture records
def organ_feats(g, corpus):
    org = {o: [f for f in fs if f in g['entered_content']] for o, fs in K.ORGANS.items()}
    org = {o: fs for o, fs in org.items() if fs}
    st = [f for f in g['entered_style']]
    if st:
        org['style'] = st
    return org


def records(codes, ids, org):
    return [{o: tuple(str(codes.get(i, {}).get(f, 'unclear')).strip().lower() for f in fs) for o, fs in org.items()} for i in ids]


def to_codes(recs, ids, org):
    out = {}
    for i, r in zip(ids, recs):
        d = {}
        for o, fs in org.items():
            for f, v in zip(fs, r[o]):
                d[f] = v
        out[i] = d
    return out


def disagreement(codes, ids, feats):
    d, margB = {}, {}
    for f in feats:
        a = [str(codes['A'].get(i, {}).get(f, 'unclear')).lower() for i in ids]
        b = [str(codes['B'].get(i, {}).get(f, 'unclear')).lower() for i in ids]
        d[f] = float(np.mean([x != y for x, y in zip(a, b)]))
        margB[f] = Counter(b)
    return d, margB


def perturb_B(codesA, d, margB, rng):
    out = {}
    for i, rec in codesA.items():
        r = dict(rec)
        for f, p in d.items():
            if rng.random() < p:
                vals, w = zip(*margB[f].items())
                r[f] = vals[int(rng.choice(len(vals), p=np.array(w, float) / sum(w)))]
        out[i] = r
    return out


def donor_pools(D, same_group=False):
    n = len(D['ids'])
    pools = []
    for i in range(n):
        ok = [j for j in range(n) if j != i and D['leaf'][j] != D['leaf'][i] and D['leaf'][j] != D['conj'][i]
              and (abs(int(D['pos'][j]) - int(D['pos'][i])) > POOL_EXCL or same_group)]
        if same_group:
            ok = [j for j in ok if D['group'][j] == D['group'][i] and abs(int(D['pos'][j]) - int(D['pos'][i])) > 2]
        if not ok:
            ok = [j for j in range(n) if abs(int(D['pos'][j]) - int(D['pos'][i])) > POOL_EXCL] or [j for j in range(n) if j != i]
        pools.append(ok)
    return pools


def stay_probs(recs, org, groups=None):
    """Stay probability per organ so that the stationary chain's lag-1 tuple agreement matches the real one."""
    rho = {}
    for o in org:
        seq = [r[o] for r in recs]
        pairs = [(seq[k], seq[k + 1]) for k in range(len(seq) - 1) if groups is None or groups[k] == groups[k + 1]]
        a = np.mean([x == y for x, y in pairs]) if pairs else 0.0
        c = Counter(seq)
        pc = sum((v / len(seq)) ** 2 for v in c.values())
        rho[o] = float(np.clip((a - pc) / (1 - pc), 0.0, 0.95)) if pc < 1 else 0.0
    return rho


def gen_markov(D, P, rng, quire=False):
    recs, H = P['recs'], D['heights']
    n = len(recs)
    pools = P['pools_q'] if quire else P['pools']
    rho = P['rho_q'] if quire else P['rho']
    out, hs = [], []
    for i in range(n):
        d = pools[i][int(rng.integers(len(pools[i])))]
        start = i == 0 or (quire and D['group'][i] != D['group'][i - 1])
        r = {}
        for o in recs[0]:
            r[o] = out[i - 1][o] if (not start and rng.random() < rho[o]) else recs[d][o]
        stay_h = (not start) and rng.random() < rho.get('style', 0.0)
        out.append(r)
        hs.append(hs[i - 1] if stay_h else H[d])
    return out, hs


def smooth(x, width):
    n = len(x)
    k = np.arange(n)
    Wm = np.exp(-0.5 * ((k[:, None] - k[None, :]) / max(width, 1e-9)) ** 2)
    y = Wm @ x / Wm.sum(1)
    sd = y.std()
    return (y - y.mean()) / sd if sd > 0 else y * 0


def gen_tilted(D, P, rng, score, scale):
    """Organ tuples drawn independently per organ with P(t | i) ~ marginal(t) exp(scale * a_t * score_i)."""
    recs = P['recs']
    n = len(recs)
    out = [dict() for _ in range(n)]
    for o in recs[0]:
        c = Counter(r[o] for r in recs)
        tup, w = zip(*c.items())
        base = np.log(np.array(w, float) / sum(w))
        a = rng.standard_normal(len(tup))
        sc = score if score.ndim == 1 else score
        logits = base[None, :] + scale * sc[:, None] * a[None, :]
        pr = np.exp(logits - logits.max(1, keepdims=True))
        pr /= pr.sum(1, keepdims=True)
        for i in range(n):
            out[i][o] = tup[int(rng.choice(len(tup), p=pr[i]))]
    hs = [D['heights'][j] for j in rng.permutation(n)]
    return out, hs


def gen_trend(D, P, rng, scale):
    n = len(P['recs'])
    score = smooth(np.cumsum(rng.standard_normal(n)), 16)
    return gen_tilted(D, P, rng, score, scale)


def gen_shared(D, P, rng, scale, width):
    score = smooth(P['text_score'], width)
    return gen_tilted(D, P, rng, score, scale)


def lag1_mean(recs):
    return float(np.mean([np.mean([recs[k][o] == recs[k + 1][o] for k in range(len(recs) - 1)]) for o in recs[0]]))


def bisect_scale(D, P, gen, target, rng, lo=0.0, hi=12.0, steps=12, reps=20):
    for _ in range(steps):
        mid = (lo + hi) / 2
        v = np.mean([lag1_mean(gen(D, P, rng, mid)[0]) for _ in range(reps)])
        if v < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ================================================================================================ fidelity (pictures only)
def fidelity_stats(codesA, ids, groups, feats, spec=K.CONTENT):
    out = {}
    for f in feats:
        ftype, levels = spec[f]
        v = [K.norm_value(ftype, levels, codesA.get(i, {}).get(f)) for i in ids]
        lag = []
        for L in range(1, 11):
            pr = [(v[k], v[k + L]) for k in range(len(v) - L) if v[k] is not None and v[k + L] is not None]
            if pr:
                lag.append(np.mean([a == b for a, b in pr]))
        vv = [x for x in v if x is not None]
        mode = Counter(vv).most_common(1)[0][0] if vv else None
        fr = []
        for gq in sorted(set(groups)):
            xs = [x for x, gg in zip(v, groups) if gg == gq and x is not None]
            if xs:
                fr.append(np.mean([x == mode for x in xs]))
        out[f] = (float(np.mean(lag)) if lag else float('nan'), float(np.var(fr)) if fr else float('nan'))
    return out


# ================================================================================================ text-side helpers
def resid_on(M, X):
    i0, i1 = np.triu_indices(M.shape[0], 1)
    y = K.double_centre(M)[i0, i1]
    A = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    return y - A @ b


def adjacency_excess(M, pos, X):
    i0, i1 = np.triu_indices(M.shape[0], 1)
    r = resid_on(M, X)
    dp = np.abs(pos[i0] - pos[i1])
    return float(r[dp <= 4].mean() - r[dp > 20].mean())


def length_X(toks):
    n = len(toks)
    i0, i1 = np.triu_indices(n, 1)
    ln = np.log(np.array([len(t) for t in toks], float))
    return np.column_stack([np.abs(ln[i0] - ln[i1]), ln[i0] + ln[i1]])


def dial_shares(toks):
    out = []
    for words in toks:
        e_any = sum('e' in w for w in words)
        e2 = sum('ee' in w for w in words)
        m_any = sum('i' in w for w in words)
        m2 = sum('ii' in w for w in words)
        u = Counter(x for w in words for x in K.GLYPH_RE.findall(w))
        k, t = u['k'] + u['ckh'], u['t'] + u['cth']
        out.append({'e2_share': e2 / e_any if e_any else float('nan'), 'minim2_share': m2 / m_any if m_any else float('nan'),
                    'k_share': k / (k + t) if k + t else float('nan'), 'ch_share': u['ch'] / (u['ch'] + u['sh']) if u['ch'] + u['sh'] else float('nan')})
    return out


def mid_types(toks, rng, k, lo=3, hi=30, exclude=()):
    c = Counter(w for t in toks for w in t)
    cand = [w for w, n in c.items() if lo <= n <= hi and w not in exclude]
    return list(rng.choice(cand, size=min(k, len(cand)), replace=False))


# ================================================================================================ worker
def _init():
    os.environ['OMP_NUM_THREADS'] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    W['V'] = v_data()
    W['BR'] = br_data()
    W['setup'] = json.load(open(RES / 'calib_setup780.json', encoding='utf-8'))
    _prepare(W['V'], W['setup'], 'V')
    _prepare(W['BR'], W['setup'], 'BR')


def _prepare(D, S, corpus):
    org = organ_feats(D['gate'], corpus) if corpus == 'V' else organ_feats(S['br_shared_gate'], corpus)
    P = {'org': org, 'recs': records(D['codes']['A'], D['ids'], org)}
    P['pools'] = donor_pools(D)
    P['pools_q'] = donor_pools(D, same_group=True)
    P['rho'] = stay_probs(P['recs'], org)
    P['rho_q'] = stay_probs(P['recs'], org, D['group'])
    feats_all = [f for fs in org.values() for f in fs]
    P['dis'], P['margB'] = disagreement(D['codes'], D['ids'], feats_all)
    if corpus == 'V':
        T1 = K.double_centre(D['T']['T1'])
        w, v = np.linalg.eigh(T1)
        P['text_score'] = v[:, -1]
    D['P'] = P


def synth_codes(D, gen, rng, **kw):
    P = D['P']
    if gen == 'markov':
        recs, hs = gen_markov(D, P, rng, quire=False)
    elif gen == 'quire':
        recs, hs = gen_markov(D, P, rng, quire=True)
    elif gen == 'trend':
        recs, hs = gen_trend(D, P, rng, kw['scale'])
    elif gen == 'shared':
        recs, hs = gen_shared(D, P, rng, kw['scale'], kw['width'])
    cA = to_codes(recs, D['ids'], P['org'])
    cB = perturb_B(cA, P['dis'], P['margB'], rng)
    return cA, cB, hs


def v_engine(D, toks, codes_by_set, heights, gate=None, X=None):
    gate = gate or D['gate']
    C, Y = K.picture_matrices('V', D['ids'], codes_by_set, gate, heights)
    T = K.text_similarity(toks, 'V') if toks is not D['toks'] else D['T']
    return K.Engine(T, C, Y, D['X'] if X is None else X)


def task(args):
    kind, setting, rep = args
    t0 = time.time()
    D, S = W['V'], W['setup']
    rng = np.random.default_rng(SEED[kind] + 100_000 * hash_setting(setting) + rep)
    if kind == 'k1':
        g = S['k1_settings'][setting]
        cA, cB, hs = synth_codes(D, g['gen'], rng, scale=g.get('scale'), width=g.get('width'))
        eng = v_engine(D, D['toks'], {'A': cA, 'B': cB}, hs)
        res = K.decide(eng, D['blocks'], rng)
    elif kind == 'k2':
        res = k2_replicate(D, S, setting, rng)
    elif kind == 'k3':
        res = k3_replicate(D, S, setting, rng)
    elif kind in ('k4', 'k4z'):
        res = k4_replicate(W['BR'], D, S, kind, setting, rng)
    out = {'kind': kind, 'setting': setting, 'rep': rep, 'Zmax': res['Zmax'], 'pmin_local': res['pmin_local'],
           'Z': {m: res[m]['Z'] for m in ('T1', 'T2')}, 'sec': round(time.time() - t0, 1)}
    return out


def hash_setting(s):
    return sum((k + 1) * ord(c) for k, c in enumerate(s)) % 997


# ================================================================================================ K2
def sessions(D, variant, rng):
    n = len(D['ids'])
    lab = np.full(n, -1)
    if variant == 'contig':
        i, s = 0, 0
        while i < n:
            L = int(rng.integers(4, 13))
            lab[i:i + L] = s
            i += L
            s += 1
    else:
        bif = np.minimum(D['leaf'], D['conj'])
        ub = list(np.unique(bif))
        rng.shuffle(ub)
        s, k = 0, 0
        while k < len(ub):
            m = int(rng.integers(2, 5))
            for b in ub[k:k + m]:
                lab[bif == b] = s
            k += m
            s += 1
    return lab


def k2_generate(D, S, variant, r, kappa, rng):
    n = len(D['ids'])
    lab = sessions(D, variant, rng)
    pool = [w for t in D['toks'] for w in t]
    rng.shuffle(pool)
    toks, k = [], 0
    for t in D['toks']:
        toks.append(list(pool[k:k + len(t)]))
        k += len(t)
    used = set()
    P = D['P']
    recs = [None] * n
    hs = [None] * n
    for s in np.unique(lab):
        idx = np.where(lab == s)[0]
        Ws = mid_types(D['toks'], rng, 10, exclude=used)
        used.update(Ws)
        for i in idx:
            m = int(rng.poisson(r))
            for _ in range(m):
                toks[i][int(rng.integers(len(toks[i])))] = Ws[int(rng.integers(len(Ws)))]
        far = [j for j in range(n) if lab[j] != s and np.min(np.abs(D['pos'][idx] - D['pos'][j])) > POOL_EXCL]
        if len(far) < 5:
            far = [j for j in range(n) if lab[j] != s]
        Ds = list(rng.choice(far, size=min(5, len(far)), replace=False))
        for i in idx:
            pool_i = P['pools'][i]
            d = Ds[int(rng.integers(len(Ds)))] if rng.random() < kappa else pool_i[int(rng.integers(len(pool_i)))]
            recs[i] = P['recs'][d]
            hs[i] = D['heights'][d]
    cA = to_codes(recs, D['ids'], P['org'])
    cB = perturb_B(cA, P['dis'], P['margB'], rng)
    return toks, cA, cB, hs


def k2_covariates(D, toks):
    feats = {f: dict(D['feats'][f]) for f in D['ids']}
    for f, sh in zip(D['ids'], dial_shares(toks)):
        feats[f].update(sh)
    X, _ = K.v_covariates(D['pages'], feats, [len(t) for t in toks])
    return X


def k2_replicate(D, S, setting, rng):
    p = S['k2_settings'][setting]
    toks, cA, cB, hs = k2_generate(D, S, p['variant'], p['r'], p['kappa'], rng)
    eng = v_engine(D, toks, {'A': cA, 'B': cB}, hs, X=k2_covariates(D, toks))
    return K.decide(eng, D['blocks'], rng)


# ================================================================================================ K3
def spelled_family(word, inventory, rng):
    u = K.GLYPH_RE.findall(word)
    fam = [word]
    tries = 0
    while len(fam) < 3 and tries < 50:
        tries += 1
        v = list(u)
        k = int(rng.integers(len(v)))
        v[k] = inventory[int(rng.integers(len(inventory)))]
        w = ''.join(v)
        if w not in fam:
            fam.append(w)
    return fam


def k3_replicate(D, S, setting, rng):
    variant, key_set, r = setting.split('|')
    r = float(r)
    n = len(D['ids'])
    k = int(rng.integers(10, n - 9))
    shift = np.roll(np.arange(n), k)            # page i (text) gets the picture of page shift[i]
    other = 'B' if key_set == 'A' else 'A'
    gate = D['gate']
    feats = gate['entered_content']
    if variant == 'leaf':
        feats = [f for f in feats if f in K.ORGANS['leaf']]
    toks = [list(t) for t in D['toks']]
    inv = sorted({u for t in D['toks'] for w in t for u in K.GLYPH_RE.findall(w)})
    used = set()
    desc = {}
    for f in feats:
        ftype, levels = K.CONTENT[f]
        for v in range(len(levels)):
            ws = mid_types(D['toks'], rng, 2, exclude=used)
            used.update(ws)
            desc[(f, v)] = [spelled_family(w, inv, rng) for w in ws] if variant == 'spelled' else [[w] for w in ws]
    codes_key = D['codes'][key_set]
    for i in range(n):
        src = D['ids'][shift[i]]
        for f in feats:
            ftype, levels = K.CONTENT[f]
            v = K.norm_value(ftype, levels, codes_key.get(src, {}).get(f))
            if v is None:
                continue
            for _ in range(int(rng.poisson(r))):
                fam = desc[(f, v)][int(rng.integers(2))]
                toks[i][int(rng.integers(len(toks[i])))] = fam[int(rng.integers(len(fam)))]
    codes_c = {'S': D['codes'][other]}
    C, Y = K.picture_matrices('V', D['ids'], codes_c, gate, D['heights'])
    T = K.text_similarity(toks, 'V')
    eng = K.Engine(T, C, Y, D['X'])
    return K.decide(eng, D['blocks'], rng, identity=shift)


# ================================================================================================ K4 (Brunschwig)
def degrade(codes, ids, feats, q, margins, rng):
    out = {}
    for i in ids:
        r = dict(codes.get(i, {}))
        for f in feats:
            if rng.random() < q.get(f, 0.0):
                vals, w = zip(*margins[f].items())
                r[f] = vals[int(rng.choice(len(vals), p=np.array(w, float) / sum(w)))]
        out[i] = r
    return out


V_LENGTHS = None


def truncate(tok_lists, rng, mode='first', half=False):
    global V_LENGTHS
    out = []
    for t in tok_lists:
        ok = [n for n in V_LENGTHS if n <= len(t)] or [len(t)]
        n = int(ok[int(rng.integers(len(ok)))])
        if half:
            n = max(n // 2, 5)
        if mode == 'first':
            out.append(t[:n])
        else:
            s = int(rng.integers(0, len(t) - n + 1))
            out.append(t[s:s + n])
    return out


def word_code(tok_lists, v_types_by_rank, k, rng):
    c = Counter(w for t in tok_lists for w in t)
    ranked = [w for w, _ in c.most_common()]
    need = len(ranked) * k
    forms = list(v_types_by_rank)
    units_pool = [K.GLYPH_RE.findall(w) for w in v_types_by_rank[:500]]
    while len(forms) < need:
        a = units_pool[int(rng.integers(len(units_pool)))]
        b = units_pool[int(rng.integers(len(units_pool)))]
        w = ''.join(a[:max(1, len(a) // 2)] + b[len(b) // 2:])
        if w not in forms:
            forms.append(w)
    spell = {w: forms[i * k:(i + 1) * k] for i, w in enumerate(ranked)}
    return [[spell[w][int(rng.integers(k))] for w in t] for t in tok_lists]


STOP_HEAD = {'von', 'wasser', 'krut', 'kraut', 'blumen', 'blůmen', 'blüt', 'bluet', 'blůt', 'loub', 'wurtzel', 'der', 'die',
             'das', 'vnd', 'oder', 'gebrant', 'gemeine', 'wild', 'wilden', 'groß', 'grossen', 'kleinen'}


def name_stems(heading):
    ws = re.findall(r'[a-zäöüßęů]+', heading.lower())
    return [w[:5] for w in ws if w not in STOP_HEAD and len(w) >= 3]


def uses_only_tokens(e):
    L = K.br_lines()
    raw = ' '.join(ln.strip() for ln in L[e['head_line'] + 1:e['end_line']] if ln.strip() and not ln.strip().startswith(('[', '---')))
    m = re.search(r'(?:^|[\s.])A\s+[A-ZÄÖÜ]', raw)
    if not m:
        return None
    return K.br_clean([raw[m.start():]])


def k4_replicate(B, D, S, kind, setting, rng):
    global V_LENGTHS
    if V_LENGTHS is None:
        V_LENGTHS = [len(t) for t in D['toks']]
    n_all = len(B['ids'])
    abl = setting
    elig = list(range(n_all))
    if abl == 'uses_only':
        elig = [i for i in elig if B.setdefault('uses', {}).setdefault(i, uses_only_tokens(B['entries'][i])) is not None
                and len(B['uses'][i]) >= 41]
    sub = sorted(rng.choice(elig, size=min(95, len(elig)), replace=False))
    ents = [dict(B['entries'][i], rank=k) for k, i in enumerate(sub)]
    ids = [B['ids'][i] for i in sub]
    if abl == 'uses_only':
        full = [B['uses'][i] for i in sub]
    else:
        full = [B['toks'][i] for i in sub]
    if abl == 'names_masked':
        full = [[w for w in t if not any(w.startswith(s) for s in name_stems(B['entries'][i]['heading']))] for t, i in zip(full, sub)]
    toks = truncate(full, rng, mode='window' if abl == 'window' else 'first', half=(abl == 'half'))
    corpus = 'BR'
    if abl in ('code_k1', 'code_k4'):
        vr = [w for w, _ in Counter(w for t in D['toks'] for w in t).most_common()]
        toks = word_code(toks, vr, 1 if abl == 'code_k1' else 4, rng)
        corpus = 'V'
    g = S['br_shared_gate']
    if kind == 'k4z':
        sub_D = {'ids': ids, 'heights': [B['heights'][i] for i in sub], 'pos': np.array([2 * k for k in range(len(sub))]),
                 'leaf': np.array([-1] * len(sub)), 'conj': np.array([-2] * len(sub)), 'group': [B['group'][i] for i in sub],
                 'codes': {s: {i: B['codes'][s].get(i, {}) for i in ids} for s in 'AB'}, 'gate': g}
        _prepare_sub(sub_D, B)
        cA, cB, hs = synth_codes(sub_D, setting, rng)
        codes_by_set = {'A': cA, 'B': cB}
        heights = hs
    else:
        q, marg = S['br_degrade_q'], {f: Counter(v) for f, v in S['br_margins'].items()}
        codes_by_set = {s: degrade(B['codes'][s], ids, g['entered_content'], q, marg, rng) for s in 'AB'}
        heights = [B['heights'][i] for i in sub]
    C, Y = K.picture_matrices('BR', ids, codes_by_set, g, heights)
    T = K.text_similarity(toks, corpus)
    X = K.br_covariates(ents, [len(t) for t in toks])
    eng = K.Engine(T, C, Y, X)
    return K.decide(eng, K.br_blocks(ents), rng)


def _prepare_sub(sub_D, B):
    P = B['P']
    org = P['org']
    sub_D['P'] = {'org': org, 'recs': records(sub_D['codes']['A'], sub_D['ids'], org), 'dis': P['dis'], 'margB': P['margB']}
    sub_D['P']['pools'] = donor_pools(sub_D)
    sub_D['P']['pools_q'] = donor_pools(sub_D, same_group=True)
    sub_D['P']['rho'] = stay_probs(sub_D['P']['recs'], org)
    sub_D['P']['rho_q'] = stay_probs(sub_D['P']['recs'], org, sub_D['group'])


# ================================================================================================ stages
def stage_setup():
    t0 = time.time()
    rng = np.random.default_rng(SEED['setup'])
    D, B = v_data(), br_data()
    S = {'v_gate': D['gate'], 'br_gate': B['gate'], 'n_v': len(D['ids']), 'n_br': len(B['ids'])}
    log(f"V-A1 gate: passes {D['gate']['passes']}; entered content {D['gate']['entered_content']}; organs {D['gate']['organs']}; style {D['gate']['entered_style']}")
    log(f"BR gate: passes {B['gate']['passes']}; entered content {B['gate']['entered_content']}; style {B['gate']['entered_style']}")
    shared = [f for f in D['gate']['entered_content'] if f in B['gate']['entered_content']]
    S['br_shared_gate'] = {'entered_content': shared, 'entered_style': B['gate']['entered_style'],
                           'organs': sorted({o for o, fs in K.ORGANS.items() if any(f in shared for f in fs)})}
    log(f"shared content features: {shared}")
    uo = [uses_only_tokens(e) for e in B['entries']]
    S['br_uses_only_eligible'] = int(sum(1 for t in uo if t is not None and len(t) >= 41))
    log(f"BR entries eligible for the uses-only row: {S['br_uses_only_eligible']} of {len(B['entries'])}")
    # degradation of BR codes to V's alpha
    q, margins = {}, {}
    for f in shared:
        aV = D['gate']['features'][f]['alpha']
        ftype, levels = K.CONTENT[f]
        vals = [str(B['codes'][s].get(i, {}).get(f, 'unclear')).lower() for s in 'AB' for i in B['ids']]
        margins[f] = Counter(vals)
        lo, hi = 0.0, 1.0
        for _ in range(14):
            mid = (lo + hi) / 2
            als = []
            for _r in range(8):
                cd = {s: degrade(B['codes'][s], B['ids'], [f], {f: mid}, {f: margins[f]}, rng) for s in 'AB'}
                pairs = [(a, b) for i in B['ids'] if (a := K.norm_value(ftype, levels, cd['A'][i].get(f))) is not None
                         and (b := K.norm_value(ftype, levels, cd['B'][i].get(f))) is not None]
                als.append(K.kripp_alpha(pairs, ftype, len(levels)))
            if np.nanmean(als) > aV:
                lo = mid
            else:
                hi = mid
        q[f] = 0.0 if B['gate']['features'][f]['alpha'] <= aV else (lo + hi) / 2
        log(f"  degrade {f}: alpha V {aV:.3f}, BR {B['gate']['features'][f]['alpha']:.3f} -> q {q[f]:.3f}")
    S['br_degrade_q'], S['br_margins'] = q, {f: dict(c) for f, c in margins.items()}
    # V generator parameters
    _prepare(D, S, 'V')
    P = D['P']
    real_lag = lag1_mean(P['recs'])
    S['real_lag1_mean'] = real_lag
    sc_trend = bisect_scale(D, P, lambda D_, P_, r, s: gen_trend(D_, P_, r, s), real_lag, rng)
    S['k1_settings'] = {'markov': {'gen': 'markov'}, 'quire': {'gen': 'quire'}, 'trend': {'gen': 'trend', 'scale': sc_trend}}
    for w in (8, 16, 32):
        sc = bisect_scale(D, P, lambda D_, P_, r, s, w=w: gen_shared(D_, P_, r, s, w), real_lag, rng)
        S['k1_settings'][f'shared_w{w}'] = {'gen': 'shared', 'scale': sc, 'width': w}
    log(f"real mean lag-1 organ agreement {real_lag:.3f}; trend scale {sc_trend:.2f}; shared scales "
        + ', '.join(f"w{w} {S['k1_settings'][f'shared_w{w}']['scale']:.2f}" for w in (8, 16, 32)))
    # fidelity gate per generator (pictures only)
    feats = D['gate']['entered_content']
    real = fidelity_stats(D['codes']['A'], D['ids'], D['group'], feats)
    fid = {}
    for name, g in S['k1_settings'].items():
        sims = []
        for _ in range(200):
            cA, _cB, _h = synth_codes(D, g['gen'], rng, scale=g.get('scale'), width=g.get('width'))
            sims.append(fidelity_stats(cA, D['ids'], D['group'], feats))
        outside = []
        for f in feats:
            for j, nm in ((0, 'lag1_10'), (1, 'quire_var')):
                arr = np.array([s[f][j] for s in sims if s[f][j] == s[f][j]])
                lo, hi = np.percentile(arr, [5, 95]) if len(arr) else (np.nan, np.nan)
                if not (lo <= real[f][j] <= hi):
                    outside.append(f'{f}:{nm}')
        n_checks = 2 * len(feats)
        allow = int(binom.ppf(0.95, n_checks, 0.10))        # a correct generator passes with probability >= 0.95
        fid[name] = {'outside': outside, 'n_checks': n_checks, 'allowed': allow, 'passes': len(outside) <= allow}
        log(f"fidelity {name}: {len(outside)} outside {outside} -> {'PASS' if fid[name]['passes'] else 'FAIL'}")
    S['k1_fidelity'] = fid
    S['k1_real_fidelity'] = real
    # K2 anchors and parameters
    C, Y = K.picture_matrices('V', D['ids'], D['codes'], D['gate'], D['heights'])
    LX = length_X(D['toks'])
    aT = adjacency_excess(D['T']['T1'], D['pos'], LX)
    aT2 = adjacency_excess(D['T']['T2'], D['pos'], LX)
    aC = adjacency_excess(C, D['pos'], np.zeros((LX.shape[0], 0)))
    S['k2_anchor'] = {'text_T1': aT, 'text_T2': aT2, 'pictures_C': aC}
    log(f"K2 anchors: text T1 {aT:.4f}, T2 {aT2:.4f}; pictures C {aC:.4f}")
    S['k2_settings'] = {}
    for variant in ('contig', 'misbind'):
        lo, hi = 0.0, 12.0
        for _ in range(10):
            mid = (lo + hi) / 2
            v = np.mean([adjacency_excess(K.text_similarity(k2_generate(D, S, variant, mid, 0.0, rng)[0], 'V')['T1'], D['pos'], LX)
                         for _ in range(6)])
            lo, hi = (mid, hi) if v < aT else (lo, mid)
        r = (lo + hi) / 2
        lo, hi = 0.0, 1.0
        for _ in range(10):
            mid = (lo + hi) / 2
            vs = []
            for _r in range(6):
                _t, cA, cB, hs = k2_generate(D, S, variant, 0.0, mid, rng)
                Cs, _Ys = K.picture_matrices('V', D['ids'], {'A': cA, 'B': cB}, D['gate'], hs)
                vs.append(adjacency_excess(Cs, D['pos'], np.zeros((LX.shape[0], 0))))
            lo, hi = (mid, hi) if np.mean(vs) < aC else (lo, mid)
        kap = (lo + hi) / 2
        S['k2_settings'][f'{variant}_anchored'] = {'variant': variant, 'r': r, 'kappa': kap, 'counted': True}
        S['k2_settings'][f'{variant}_x2'] = {'variant': variant, 'r': 2 * r, 'kappa': min(1.0, 2 * kap), 'counted': False}
        log(f"K2 {variant}: r {r:.3f} tokens/page, kappa {kap:.3f}")
    S['runtime_s'] = time.time() - t0
    json.dump(S, open(RES / 'calib_setup780.json', 'w', encoding='utf-8'), indent=1, default=float)
    log('setup done')


def run_tasks(tasks, out_name):
    path = RES / out_name
    done = set()
    if path.exists():
        for ln in open(path, encoding='utf-8'):
            d = json.loads(ln)
            done.add((d['kind'], d['setting'], d['rep']))
    todo = [t for t in tasks if tuple(t) not in done]
    log(f'{out_name}: {len(done)} done, {len(todo)} to run')
    t0 = time.time()
    with Pool(WORKERS, initializer=_init) as pool, open(path, 'a', encoding='utf-8') as fh:
        for k, r in enumerate(pool.imap_unordered(task, todo, chunksize=2)):
            fh.write(json.dumps(r) + '\n')
            fh.flush()
            if (k + 1) % 100 == 0:
                log(f'  {out_name}: {k + 1}/{len(todo)} ({time.time() - t0:.0f}s)')
    log(f'{out_name} done ({time.time() - t0:.0f}s)')


def stage_k1():
    S = json.load(open(RES / 'calib_setup780.json', encoding='utf-8'))
    tasks = [('k1', s, r) for s in S['k1_settings'] for r in range(N_K1)]
    run_tasks(tasks, 'k1_780.jsonl')


def stage_k1bind():
    S = json.load(open(RES / 'calib_setup780.json', encoding='utf-8'))
    rows = [json.loads(ln) for ln in open(RES / 'k1_780.jsonl', encoding='utf-8')]
    rows += [json.loads(ln) for ln in open(RES / 'k2_780.jsonl', encoding='utf-8')] if (RES / 'k2_780.jsonl').exists() else []
    q = {}
    for s in S['k1_settings']:
        if S['k1_fidelity'][s]['passes']:
            z = [r['Zmax'] for r in rows if r['kind'] == 'k1' and r['setting'] == s]
            q[('k1', s)] = np.percentile(z, 99)
    for s, p in S['k2_settings'].items():
        if p['counted']:
            z = [r['Zmax'] for r in rows if r['kind'] == 'k2' and r['setting'] == s]
            if z:
                q[('k2', s)] = np.percentile(z, 99)
    kind, s = max(q, key=q.get)
    log(f'binding setting: {kind} {s} (q99 {q[(kind, s)]:.3f}); extending to {N_K1_BIND} replicates')
    run_tasks([(kind, s, r) for r in range(N_K1_BIND)], f'{kind}_780.jsonl')


def stage_k2():
    S = json.load(open(RES / 'calib_setup780.json', encoding='utf-8'))
    tasks = [('k2', s, r) for s, p in S['k2_settings'].items() for r in range(N_K2 if p['counted'] else N_K2X2)]
    run_tasks(tasks, 'k2_780.jsonl')


def stage_k3():
    tasks = [('k3', f'{v}|{ks}|{r}', rep) for v in ('exact', 'spelled', 'leaf') for ks in 'AB' for r in K3_GRID for rep in range(N_K3)]
    run_tasks(tasks, 'k3_780.jsonl')


def stage_k4():
    tasks = [('k4z', g, r) for g in ('markov', 'quire') for r in range(N_K4Z)]
    tasks += [('k4', a, r) for a in ('main', 'uses_only', 'half', 'code_k1', 'code_k4', 'window', 'names_masked') for r in range(N_K4)]
    run_tasks(tasks, 'k4_780.jsonl')


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def stage_summary():
    S = json.load(open(RES / 'calib_setup780.json', encoding='utf-8'))
    rows = []
    for f in ('k1_780.jsonl', 'k2_780.jsonl', 'k3_780.jsonl', 'k4_780.jsonl'):
        if (RES / f).exists():
            rows += [json.loads(ln) for ln in open(RES / f, encoding='utf-8')]
    out = {'k1': {}, 'k2': {}}
    q = {}
    for s in S['k1_settings']:
        z = np.array([r['Zmax'] for r in rows if r['kind'] == 'k1' and r['setting'] == s])
        if len(z):
            q99 = float(np.percentile(z, 99))
            out['k1'][s] = {'n': len(z), 'q99': q99, 'fidelity_pass': S['k1_fidelity'][s]['passes']}
            if S['k1_fidelity'][s]['passes']:
                q[('k1', s)] = q99
    for s, p in S['k2_settings'].items():
        z = np.array([r['Zmax'] for r in rows if r['kind'] == 'k2' and r['setting'] == s])
        if len(z):
            q99 = float(np.percentile(z, 99))
            out['k2'][s] = {'n': len(z), 'q99': q99, 'counted': p['counted'], 'fp_at_q': None}
            if p['counted']:
                q[('k2', s)] = q99
    any_pass = any(S['k1_fidelity'][s]['passes'] for s in S['k1_settings'])
    zstar = max(q.values()) if q else float('nan')
    out['z_star'] = zstar
    out['binding'] = list(max(q, key=q.get)) if q else None
    out['fallback'] = not any_pass
    # N-sheet rule: misbinding false-positive rate under the decision at z*
    z_mis = [r['Zmax'] for r in rows if r['kind'] == 'k2' and r['setting'] == 'misbind_anchored']
    out['misbind_fp_at_zstar'] = float(np.mean(np.array(z_mis) > zstar)) if z_mis else None
    for s in out['k2']:
        zz = [r['Zmax'] for r in rows if r['kind'] == 'k2' and r['setting'] == s]
        out['k2'][s]['fp_at_q'] = float(np.mean(np.array(zz) > zstar)) if zz else None
    # K3
    mde = {}
    for v in ('exact', 'spelled', 'leaf'):
        mde[v] = {}
        for ks in 'AB':
            pts = {}
            for r in K3_GRID:
                z = np.array([x['Zmax'] for x in rows if x['kind'] == 'k3' and x['setting'] == f'{v}|{ks}|{r}'])
                pts[r] = float(np.mean(z > zstar)) if len(z) else float('nan')
            m = next((r for r in K3_GRID if pts[r] >= 0.8 and all(pts[r2] >= 0.8 for r2 in K3_GRID if r2 >= r)), None)
            mde[v][ks] = {'points': pts, 'MDE80': m}
        ms = [mde[v][ks]['MDE80'] for ks in 'AB']
        mde[v]['MDE80'] = None if any(x is None for x in ms) else max(ms)
    out['k3'] = mde
    # K4
    zb = {}
    for g in ('markov', 'quire'):
        z = np.array([r['Zmax'] for r in rows if r['kind'] == 'k4z' and r['setting'] == g])
        if len(z):
            zb[g] = float(np.percentile(z, 99))
    zstar_br = max(zb.values()) if zb else float('nan')
    thr = max(zstar, zstar_br)
    out['z_star_br'] = zstar_br
    out['z_star_br_by_gen'] = zb
    out['k4_threshold'] = thr
    out['k4'] = {}
    for a in ('main', 'uses_only', 'half', 'code_k1', 'code_k4', 'window', 'names_masked'):
        z = np.array([r['Zmax'] for r in rows if r['kind'] == 'k4' and r['setting'] == a])
        if len(z):
            k = int((z > thr).sum())
            out['k4'][a] = {'n': len(z), 'genre_power': k / len(z), 'wilson95': wilson(k, len(z)),
                            'Zmax_median': float(np.median(z))}
    json.dump(out, open(RES / 'calib780.json', 'w', encoding='utf-8'), indent=1)
    log(json.dumps(out, indent=1)[:3000])


if __name__ == '__main__':
    RES.mkdir(exist_ok=True)
    {'setup': stage_setup, 'k1': stage_k1, 'k1bind': stage_k1bind, 'k2': stage_k2, 'k3': stage_k3, 'k4': stage_k4,
     'summary': stage_summary}[sys.argv[1]]()
