#!/usr/bin/env python3
"""PHASE_763 — glyph-level re-test of "kernel-centric". Definitions: ../PRE_REGISTRATION.md (locked, commit af4a55b).

Arm W: centred random-walk closeness Y_g on the within-token renewal chain vs an edge-anchored run-block permutation.
Arm S: I(X_g(t); C(t+1) | F(t)) (Miller-Madow) vs the PHASE_756 N5 null (glyph edges, beta = 2).
Decision: kernel {k, e, B} mean z vs matched control triads. Power certification by planted effects, folio
bootstraps, Currier A / Latin / generator floors.
Order of computation per arm: null -> gates -> certification -> observed (blind until the gates and power are fixed).
Run:  python kernel_retest.py [--smoke]
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('C:/git/voynich')
# own numba cache (git-ignored): cached kernels of the importlib-loaded N5 module must not mix with PHASE_756's cache
os.environ['NUMBA_CACHE_DIR'] = str(ROOT / 'phases/PHASE_763_KERNEL_GLYPH_RETEST/scripts/__pycache__/numba')

import numpy as np  # noqa: E402
from numba import njit  # noqa: E402
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript  # noqa: E402


def _imp(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod          # lets numba's cache re-import the module by name
    spec.loader.exec_module(mod)
    return mod


N5 = _imp('n5', 'phases/PHASE_756_C957_JOINT_NULL/scripts/c957_joint_null_n5.py')
SC = _imp('spacing', 'phases/PHASE_761_SPACING_ROBUSTNESS/scripts/spacing_check.py')
sys.path.insert(0, str(ROOT / 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts'))
import naibbe_harness as NH  # noqa: E402

SMOKE = '--smoke' in sys.argv
OUT = ROOT / 'phases/PHASE_763_KERNEL_GLYPH_RETEST/results'
OUT.mkdir(parents=True, exist_ok=True)
TAG = '_smoke' if SMOKE else ''
LOGF = open(OUT / f'run_log{TAG}.txt', 'w', encoding='utf-8')

SEED = 763
R_W = 20 if SMOKE else 1000          # Arm W null (H, ZL, S2, types, A, Latin)
R_W_SMALL = 10 if SMOKE else 200     # Arm W null for B downsamples and generator members
N_BOOT = 5 if SMOKE else 200
N_DOWN = 2 if SMOKE else 100
N_GEN = 1 if SMOKE else 20
PLANT_CAL, PLANT_N = (2, 4) if SMOKE else (20, 100)
PI_GRID = [0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0]
MDE80 = 2.485
BETA = 2.0
BURN, ANNEAL = (60, 30) if SMOKE else (2000, 1000)
PILOT_N, PILOT_THIN = (30, 5) if SMOKE else (500, 5)
MAIN_N = 20 if SMOKE else 300
GEN_N = 10 if SMOKE else 300
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
SCHEMES = {'S1': {'ch': 'B', 'sh': 'B'},
           'S2': {'ch': 'B', 'sh': 'B', 'ckh': 'B', 'cth': 'B', 'cph': 'B', 'cfh': 'B'}}
RAWSET = {'S1': {'k': {'k'}, 'e': {'e'}, 'B': {'ch', 'sh'}},
          'S2': {'k': {'k'}, 'e': {'e'}, 'B': {'ch', 'sh', 'ckh', 'cth', 'cph', 'cfh'}}}
KERNEL = ('k', 'e', 'B')
PREREG_CONTROLS = {
    ('W', 'S1'): {'k': ['t', 'a', 'd', 'o', 'p'], 'e': ['a', 'd', 't', 'o', 'l'], 'B': ['o', 'q', 't', 'l', 'p']},
    ('S', 'S1'): {'k': ['a', 'd', 'o', 't', 'ckh'], 'e': ['a', 'd', 'o', 't', 'l'], 'B': ['p', 't', 'o', 's', 'cth']},
    ('W', 'S2'): {'k': ['t', 'a', 'd', 'o', 'l'], 'e': ['a', 'd', 't', 'o', 'l'], 'B': ['o', 't', 'l', 'a', 'd']},
    ('S', 'S2'): {'k': ['a', 'd', 'o', 't', 'l'], 'e': ['a', 'd', 'o', 't', 'l'], 'B': ['p', 't', 'o', 's', 'l']},
}
T0 = time.time()
RES = {'phase': 'PHASE_763', 'pre_registration_commit': 'af4a55b', 'smoke': SMOKE, 'deviations': []}


def log(*a):
    msg = ' '.join(str(x) for x in a)
    print(f'[{time.time() - T0:7.0f}s] {msg}', flush=True)
    LOGF.write(f'[{time.time() - T0:7.0f}s] {msg}\n')
    LOGF.flush()


def save(name=None):
    fn = OUT / (name or f'interim{TAG}.json')
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(RES, f, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))


def lower_priority():
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS') else 10)
    except Exception as e:  # noqa: BLE001
        log('priority not lowered:', e)


def sch_units(w, sch):
    return [sch.get(g, g) for g in GLYPH_RE.findall(w)]


# ================================================================================================ triad decision
def select_controls(feat, freq, pool, kernel, k=5):
    """feat: unit -> 3 features; freq: unit -> raw frequency for the flag. Returns controls, flags."""
    units = list(pool) + list(kernel)
    X = np.array([feat[g] for g in units], dtype=float)
    sd = X.std(0)
    sd[sd == 0] = 1.0
    Z = (X - X.mean(0)) / sd
    idx = {g: i for i, g in enumerate(units)}
    ctrl, flags = {}, {}
    for kk in kernel:
        d = sorted((float(np.linalg.norm(Z[idx[kk]] - Z[idx[g]])), g) for g in pool if g not in kernel)
        ctrl[kk] = [g for _, g in d[:k]]
        flags[kk] = bool(ctrl[kk]) and all(freq[kk] > 2 * freq[g] for g in ctrl[kk])
    return ctrl, flags


def triad_test(z, ctrl, kernel):
    kernel = [g for g in kernel if g in z]
    K = float(np.mean([z[g] for g in kernel]))
    pools = [[c for c in ctrl[g] if c in z] for g in kernel]
    sc = [float(np.mean([z[c] for c in tri])) for tri in itertools.product(*pools) if len(set(tri)) == len(tri)]
    sc = np.array(sc)
    if len(sc) == 0:
        return {'K': K, 'p': float('nan'), 'E': float('nan'), 'n_triads': 0}
    return {'K': K, 'p': float((1 + (sc >= K).sum()) / (1 + len(sc))), 'E': float(K - np.median(sc)),
            'n_triads': int(len(sc)), 'triad_median': float(np.median(sc))}


def decide(test, flags, z, ctrl, kernel=KERNEL):
    out = dict(test)
    fl = [g for g in kernel if flags.get(g)]
    if fl:
        unf = [g for g in kernel if not flags.get(g)]
        out['unflagged_test'] = triad_test(z, ctrl, unf) if unf else None
    return out


# ================================================================================================ Arm W machinery
@njit(cache=True)
def nb_seed(s):
    np.random.seed(s)


@njit(cache=True)
def w_counts(node, lens, tok_start, tok_nruns, tok_w, S, START, END):
    C = np.zeros((S, S))
    tot = 0.0
    for t in range(len(tok_start)):
        w = tok_w[t]
        if w == 0:
            continue
        tot += w
        s0 = tok_start[t]
        prev = START
        for r in range(tok_nruns[t]):
            x = node[s0 + r]
            C[prev, x] += w
            C[x, x] += w * (lens[s0 + r] - 1)
            prev = x
        C[prev, END] += w
    C[END, START] += tot
    return C


@njit(cache=True)
def w_permute(node, lens, tok_start, tok_nruns, elig, out_node, out_len, maxn):
    out_node[:] = node
    out_len[:] = lens
    tn = np.empty(maxn, dtype=np.int64)
    tl = np.empty(maxn, dtype=np.int64)
    for q in range(len(elig)):
        t = elig[q]
        s0 = tok_start[t]
        n = tok_nruns[t]
        m = n - 2
        for attempt in range(100):
            for i in range(m):
                tn[i] = node[s0 + 1 + i]
                tl[i] = lens[s0 + 1 + i]
            for a in range(m - 1, 0, -1):
                b = np.random.randint(a + 1)
                x = tn[a]
                tn[a] = tn[b]
                tn[b] = x
                y = tl[a]
                tl[a] = tl[b]
                tl[b] = y
            ok = True
            prev = node[s0]
            for i in range(m):
                if tn[i] == prev:
                    ok = False
                    break
                prev = tn[i]
            if ok and prev == node[s0 + n - 1]:
                ok = False
            if ok:
                for i in range(m):
                    out_node[s0 + 1 + i] = tn[i]
                    out_len[s0 + 1 + i] = tl[i]
                break


@njit(cache=True)
def w_plant(node, lens, tok_start, tok_nruns, kern, pi):
    nk = len(kern)
    for t in range(len(tok_start)):
        n = tok_nruns[t]
        if n < 3:
            continue
        if np.random.random() >= pi:
            continue
        s0 = tok_start[t]
        order = np.random.permutation(nk)
        for oi in range(nk):
            g = kern[order[oi]]
            j = -1
            for r in range(1, n - 1):
                if node[s0 + r] == g:
                    j = r
                    break
            if j <= 1:
                continue
            if node[s0] == g or node[s0 + 1] == g:
                continue
            if node[s0 + j - 1] == node[s0 + j + 1]:
                continue
            gn = node[s0 + j]
            gl = lens[s0 + j]
            for r in range(j, 1, -1):
                node[s0 + r] = node[s0 + r - 1]
                lens[s0 + r] = lens[s0 + r - 1]
            node[s0 + 1] = gn
            lens[s0 + 1] = gl


def w_features(seqs):
    inst, pos, inter = Counter(), defaultdict(float), Counter()
    for u in seqs:
        L = len(u)
        for i, g in enumerate(u):
            inst[g] += 1
            pos[g] += 0.5 if L == 1 else i / (L - 1)
            if 0 < i < L - 1:
                inter[g] += 1
    return {g: (float(np.log(inst[g])), pos[g] / inst[g], inter[g] / inst[g]) for g in inst}, dict(inst)


class WCorpus:
    def __init__(self, seqs, folios, nodes=None, min_cover=0.99):
        inst = Counter(u for s in seqs for u in s)
        total = sum(inst.values())
        order = sorted(inst, key=lambda g: (-inst[g], g))
        if nodes is None:
            nodes, cum = [], 0
            for g in order:
                if cum >= min_cover * total:
                    break
                nodes.append(g)
                cum += inst[g]
        else:
            nodes = [g for g in nodes if inst.get(g, 0) > 0]
        self.nodes = nodes
        m = len(nodes)
        self.m, self.X, self.START, self.END, self.S = m, m, m + 1, m + 2, m + 3
        nid = {g: i for i, g in enumerate(nodes)}
        self.nid = nid
        rn, rl, ts, tr = [], [], [], []
        for s in seqs:
            ids = [nid.get(u, m) for u in s]
            ts.append(len(rn))
            n, prev = 0, None
            for x in ids:
                if x == prev:
                    rl[-1] += 1
                else:
                    rn.append(x)
                    rl.append(1)
                    n += 1
                    prev = x
            tr.append(n)
        self.node = np.array(rn, dtype=np.int64)
        self.lens = np.array(rl, dtype=np.int64)
        self.tok_start = np.array(ts, dtype=np.int64)
        self.tok_nruns = np.array(tr, dtype=np.int64)
        self.elig = np.flatnonzero(self.tok_nruns >= 4).astype(np.int64)
        self.maxn = int(self.tok_nruns.max()) if len(tr) else 1
        fl = sorted(set(folios))
        fid = {f: i for i, f in enumerate(fl)}
        self.folio = np.array([fid[f] for f in folios], dtype=np.int64)
        self.n_folios = len(fl)
        self.ones = np.ones(len(seqs))
        self.feat, self.inst = w_features(seqs)
        self.bigrams = int(sum(len(s) + 1 for s in seqs))

    def counts(self, node=None, lens=None, w=None):
        return w_counts(self.node if node is None else node, self.lens if lens is None else lens, self.tok_start,
                        self.tok_nruns, self.ones if w is None else w, self.S, self.START, self.END)


def w_stats(C, m, gidx):
    """Returns (Y over gidx, rwb over gidx, h over V'). None if the chain is not usable."""
    rs = C.sum(1, keepdims=True)
    if np.any(rs == 0):
        return None
    P = C / rs
    S = P.shape[0]
    A = P.T - np.eye(S)
    A[-1, :] = 1.0
    b = np.zeros(S)
    b[-1] = 1.0
    pi = np.linalg.solve(A, b)
    Z = np.linalg.inv(np.eye(S) - P + np.outer(np.ones(S), pi))
    ET = (np.diag(Z)[None, :] - Z) / pi[None, :]
    np.fill_diagonal(ET, 0.0)
    sub = ET[:m, :m]
    h = sub.sum(0) + sub.sum(1)
    Htot = sub.sum()
    rwb = pi[:m] * (Htot - h)
    hg = h[gidx]
    return hg.mean() - hg, rwb[gidx], h


def rwb_direct(C, m):
    """Direct RWB from fundamental matrices with t absorbing (identity check)."""
    P = C / C.sum(1, keepdims=True)
    S = P.shape[0]
    out = np.zeros(m)
    for t in range(m):
        keep = [i for i in range(S) if i != t]
        Q = P[np.ix_(keep, keep)]
        N = np.linalg.inv(np.eye(S - 1) - Q)
        pos = {s: i for i, s in enumerate(keep)}
        for g in range(m):
            if g == t:
                continue
            out[g] += sum(N[pos[s], pos[g]] for s in range(m) if s not in (t, g))
    return out


def sp_betweenness(C, nodes_idx):
    import networkx as nx
    P = C / C.sum(1, keepdims=True)
    G = nx.DiGraph()
    S = P.shape[0]
    for i in range(S):
        for j in range(S):
            if i != j and P[i, j] > 0:
                G.add_edge(i, j, weight=-np.log(P[i, j]))
    bc = nx.betweenness_centrality(G, weight='weight', normalized=True)
    return np.array([bc.get(i, 0.0) for i in nodes_idx])


def w_null(WC, gidx, R, seed, want_sp=False):
    nb_seed(seed)
    on, ol = np.empty_like(WC.node), np.empty_like(WC.lens)
    Ys, Rw, Sp = [], [], []
    for _ in range(R):
        w_permute(WC.node, WC.lens, WC.tok_start, WC.tok_nruns, WC.elig, on, ol, WC.maxn)
        C = WC.counts(on, ol)
        st = w_stats(C, WC.m, gidx)
        Ys.append(st[0])
        Rw.append(st[1])
        if want_sp:
            Sp.append(sp_betweenness(C, gidx))
    out = {'Y': np.array(Ys), 'RWB': np.array(Rw)}
    if want_sp:
        out['SP'] = np.array(Sp)
    return out


def zs(obs, null):
    mu, sd = null.mean(0), null.std(0)
    sd = np.where(sd > 0, sd, np.nan)
    return (obs - mu) / sd, mu, sd


def arm_w(name, seqs, folios, R, seed, fixed=None, nodes=None, want_sp=False, boot=0, boot_seed=None,
          kernel=KERNEL, pool=None):
    """fixed: dict with 'controls' (and optionally 'G') to reuse; pool: explicit pool (Latin)."""
    WC = WCorpus(seqs, folios, nodes=nodes)
    if pool is None:
        pool = [g for g in WC.nodes if g not in kernel and WC.inst.get(g, 0) >= 200]
    G = [g for g in list(pool) + list(kernel) if g in WC.nid]
    gidx = np.array([WC.nid[g] for g in G], dtype=np.int64)
    if fixed is not None:
        ctrl = {k: [c for c in v if c in G] for k, v in fixed['controls'].items()}
        flags = fixed.get('flags', {k: False for k in kernel})
    elif kernel:
        ctrl, flags = select_controls(WC.feat, WC.inst, pool, [k for k in kernel if k in WC.nid])
    else:
        ctrl, flags = {}, {}
    null = w_null(WC, gidx, R, seed, want_sp=want_sp)
    muY, sdY = null['Y'].mean(0), null['Y'].std(0)
    res = {'name': name, 'tokens': len(seqs), 'bigrams': WC.bigrams, 'nodes': WC.nodes, 'G': G,
           'eligible_tokens': int(len(WC.elig)), 'controls': ctrl, 'flags': flags, 'R': R,
           '_WC': WC, '_gidx': gidx, '_muY': muY, '_sdY': sdY, '_null': null}
    return res


def arm_w_observe(res, kernel=KERNEL):
    WC, gidx = res['_WC'], res['_gidx']
    C = WC.counts()
    Y, rwb, h = w_stats(C, WC.m, gidx)
    z, _, _ = zs(Y, res['_null']['Y'])
    zr, _, _ = zs(rwb, res['_null']['RWB'])
    G = res['G']
    zd = {g: float(z[i]) for i, g in enumerate(G)}
    res['z'] = zd
    res['z_rwb'] = {g: float(zr[i]) for i, g in enumerate(G)}
    res['Y_obs'] = {g: float(Y[i]) for i, g in enumerate(G)}
    res['rank_by_z'] = sorted(G, key=lambda g: -zd[g] if np.isfinite(zd[g]) else 1e9)
    if kernel:
        res['test'] = decide(triad_test(zd, res['controls'], kernel), res['flags'], zd, res['controls'], kernel)
        res['test_rwb'] = triad_test(res['z_rwb'], res['controls'], kernel)
    return res


def w_boot_E(res, n, seed, triad=None, ctrl=None):
    """Folio/block bootstrap of E with null mean/SD fixed. triad: kernel tuple (default KERNEL)."""
    WC, gidx, G = res['_WC'], res['_gidx'], res['G']
    triad = triad or KERNEL
    ctrl = ctrl or res['controls']
    rng = np.random.default_rng(seed)
    Es, skipped = [], 0
    for _ in range(n):
        draw = rng.integers(0, WC.n_folios, WC.n_folios)
        fw = np.bincount(draw, minlength=WC.n_folios).astype(float)
        st = w_stats(WC.counts(w=fw[WC.folio]), WC.m, gidx)
        if st is None:
            skipped += 1
            continue
        z = (st[0] - res['_muY']) / np.where(res['_sdY'] > 0, res['_sdY'], np.nan)
        zd = {g: float(z[i]) for i, g in enumerate(G)}
        Es.append(triad_test(zd, ctrl, triad)['E'])
    Es = np.array(Es)
    return {'n': int(len(Es)), 'skipped': skipped, 'q025': float(np.nanpercentile(Es, 2.5)),
            'q05': float(np.nanpercentile(Es, 5)), 'q95': float(np.nanpercentile(Es, 95)),
            'q975': float(np.nanpercentile(Es, 97.5)), 'mean': float(np.nanmean(Es))}


def same_sets(a, b):
    return set(a) == set(b) and all(set(a[k]) == set(b[k]) for k in a)


def note_node_pool(res):
    WC = res['_WC']
    miss = sorted(g for g, c in WC.inst.items() if c >= 200 and g not in WC.nid and g not in KERNEL)
    if miss:
        RES['deviations'].append({'what': f"{res['name']}: units with >= 200 instances fall outside the 99% node set "
                                          f"(merged into X, never ranked) and are therefore not in the pool", 'units': miss})


def public(res):
    return {k: v for k, v in res.items() if not k.startswith('_')}


# ================================================================================================ data loaders
def load_b_readable():
    tx = Transcript()
    words, folios = [], []
    for t in tx.currier_b():
        if t.placement and t.placement.startswith('P'):
            w = t.word.strip()
            if w and '*' not in w:
                words.append(w)
                folios.append(t.folio)
    return words, folios


def load_a_readable():
    tx = Transcript()
    words, folios = [], []
    for t in tx.currier_a():
        if t.placement and t.placement.startswith('P'):
            w = t.word.strip()
            if w and '*' not in w:
                words.append(w)
                folios.append(t.folio)
    return words, folios


def load_zl(fsec):
    lines = SC.load()
    w_words, w_folios, s_lines, s_secs, s_folios, dropped = [], [], [], [], [], set()
    for folio, segs in lines:
        if folio not in fsec:
            dropped.add(folio)
            continue
        for seg in segs:
            ln = []
            for tok, _ in seg:
                ok = SC.readable(tok) and bool(GLYPH_RE.findall(tok))
                ln.append(tok if ok else None)
                if ok:
                    w_words.append(tok)
                    w_folios.append(folio)
            if ln:
                s_lines.append(ln)
                s_secs.append(fsec[folio])
                s_folios.append(folio)
    return w_words, w_folios, s_lines, s_secs, s_folios, sorted(dropped)


def latin_words(key):
    if key == 'mesue':
        txt = (ROOT / 'sources/mesue_grabadin/mesue_grabadin_latin_full.txt').read_text(encoding='utf-8', errors='replace')
    elif key == 'rupescissa':
        txt = '\n'.join((ROOT / 'sources/rupescissa/rupescissa_latin_1561.txt').read_text(
            encoding='utf-8', errors='replace').split('\n')[200:])
    else:
        t = (ROOT / 'sources/sismel_testamentum/sismel_testamentum_assembled.txt').read_text(encoding='utf-8',
                                                                                         errors='replace')
        parts = re.split(r'={10,}\nSPREAD (\d+) — ([LR])[^\n]*\n={10,}\n', t)
        keep = []
        for i in range(1, len(parts) - 2, 3):
            if parts[i + 1] != 'L':
                continue
            body = parts[i + 2]
            if 'TESTAMENTUM' not in body[:400]:
                continue
            body = re.split(r'\n\s*─{5,}', body)[0]
            ls = [ln for ln in body.split('\n') if 'TESTAMENTUM' not in ln and not re.match(r'^\s*f\.\s*\d', ln)]
            keep.append('\n'.join(ls))
        txt = '\n'.join(keep)
    txt = txt.lower().replace('ſ', 's')
    txt = re.sub(r'([a-z])[-¬]\s*\n\s*(?:\d+\s+)?([a-z])', r'\1\2', txt)
    return re.findall(r'[a-z]+', txt)


def latin_span(words, target, rng, nblocks=83):
    cum = np.concatenate([[0], np.cumsum([len(w) + 1 for w in words])])
    if cum[-1] <= target:
        span = words
    else:
        max_start = int(np.searchsorted(cum, cum[-1] - target, side='right') - 1)
        s = int(rng.integers(0, max(1, max_start)))
        e = int(np.searchsorted(cum, cum[s] + target, side='left'))
        span = words[s:e]
    blocks = np.array_split(np.arange(len(span)), nblocks)
    folios = np.empty(len(span), dtype=np.int64)
    for bi, b in enumerate(blocks):
        folios[b] = bi
    return span, list(folios)


# ================================================================================================ Arm S machinery
CTM = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', encoding='utf-8'))
T2C = {w: int(c) for w, c in CTM['token_to_class'].items()}
ROLE_NAMES = sorted(set(CTM['class_to_role'].values()))
C2R = {int(c): ROLE_NAMES.index(r) + 1 for c, r in CTM['class_to_role'].items()}


def lenbin(n):
    return 0 if n <= 2 else (4 if n >= 6 else n - 2)


class SCorpus:
    """Arm-S view of a corpus: N5 Data + per-type arrays + fixed pair positions (lines with >= 5 certain tokens)."""

    def __init__(self, lines, secs, line_folios, schemes=('S1', 'S2'), stat_units=None):
        self.D = D = N5.Data(lines, secs, 'GLYPH')
        V = D.vocab
        raw = [GLYPH_RE.findall(w) for w in V]
        fr = sorted({r[0] for r in raw})
        self.fid = {u: i for i, u in enumerate(fr)}
        self.nF = len(fr)
        self.Fr = np.array([self.fid[r[0]] for r in raw], dtype=np.int64)
        self.Cl = np.array([T2C.get(w, 0) for w in V], dtype=np.int64)
        self.Ro = np.array([C2R.get(int(c), 0) if c > 0 else 0 for c in self.Cl], dtype=np.int64)
        self.Lb = np.array([lenbin(len(r)) for r in raw], dtype=np.int64)
        cert = np.array([sum(w is not None for w in ln) for ln in lines])
        gated = cert[D.line_of] >= 5
        self.idx = np.flatnonzero(D.valid_edge & gated).astype(np.int64)
        fl = sorted(set(line_folios))
        fmap = {f: i for i, f in enumerate(fl)}
        self.pair_folio = np.array([fmap[line_folios[D.line_of[p]]] for p in self.idx], dtype=np.int64)
        self.n_folios = len(fl)
        a0 = D.tok0[self.idx]
        self.units, self.X, self.pool, self.feat, self.freq, self.ctrl, self.flags = {}, {}, {}, {}, {}, {}, {}
        for s in schemes:
            su = [sch_units(w, SCHEMES[s]) for w in V]
            allu = sorted({u for x in su for u in x})
            # eligibility / features on the left-token multiset (real text)
            n = len(a0)
            elig, pos, inter, inst = Counter(), defaultdict(float), Counter(), Counter()
            cnt = Counter(a0.tolist())
            for v, c in cnt.items():
                u = su[v]
                L = len(u)
                for g in set(u[1:]) - {u[0]}:
                    elig[g] += c
                for i, g in enumerate(u):
                    inst[g] += c
                    pos[g] += c * (0.5 if L == 1 else i / (L - 1))
                    if 0 < i < L - 1:
                        inter[g] += c
            pool = [g for g in allu if g not in KERNEL and elig[g] >= 200]
            units = pool + [k for k in KERNEL if inst[k] > 0]
            if stat_units is not None:
                units = [u for u in stat_units if u in allu]
            self.pool[s] = pool
            self.units[s] = units
            self.feat[s] = {g: (elig[g] / n, pos[g] / inst[g], inter[g] / inst[g]) for g in inst}
            self.freq[s] = {g: elig[g] for g in inst}
            ctrl, flags = select_controls(self.feat[s], self.freq[s], pool, [k for k in KERNEL if inst[k] > 0])
            for k in KERNEL:
                if elig[k] < 200:
                    flags[k] = True
            self.ctrl[s], self.flags[s] = ctrl, flags
            uid = {g: j for j, g in enumerate(units)}
            Xm = np.zeros((len(V), len(units)), dtype=np.int64)
            for v, u in enumerate(su):
                for g in set(u):
                    if g in uid:
                        Xm[v, uid[g]] = 1
            self.X[s] = Xm
        self.eligibility = {s: {k: int(self.freq[s].get(k, 0)) for k in KERNEL} for s in schemes}


def _ent(c, N):
    c = c[c > 0]
    p = c / N
    return float(-(p * np.log(p)).sum() + (len(c) - 1) / (2.0 * N))


def cmi_units(strat, y, Xc, nS, nY, w=None):
    N = float(len(strat) if w is None else w.sum())
    Hs = _ent(np.bincount(strat, weights=w, minlength=nS).astype(float), N)
    Hys = _ent(np.bincount(strat * nY + y, weights=w, minlength=nS * nY).astype(float), N)
    out = np.empty(Xc.shape[1])
    for j in range(Xc.shape[1]):
        sx = strat * 2 + Xc[:, j]
        Hxs = _ent(np.bincount(sx, weights=w, minlength=nS * 2).astype(float), N)
        Hxys = _ent(np.bincount(sx * nY + y, weights=w, minlength=nS * 2 * nY).astype(float), N)
        out[j] = (Hxs + Hys - Hxys - Hs) / np.log(2)
    return out


def s_stats(SCo, tok, schemes=('S1', 'S2'), variants=('P', 'R1', 'R2', 'U'), w=None):
    a = tok[SCo.idx]
    b = tok[SCo.idx + 1]
    Fa, Fb = SCo.Fr[a], SCo.Fr[b]
    Cb, Rb = SCo.Cl[b], SCo.Ro[b]
    out = {}
    for s in schemes:
        Xc = SCo.X[s][a]
        d = {}
        if 'P' in variants:
            d['P'] = cmi_units(Fa, Cb, Xc, SCo.nF, 50, w)
        if 'R1' in variants:
            d['R1'] = cmi_units(Fa, Fb, Xc, SCo.nF, SCo.nF, w)
        if 'R2' in variants:
            d['R2'] = cmi_units(Fa * 5 + SCo.Lb[a], Rb, Xc, SCo.nF * 5, 6, w)
        if 'U' in variants:
            d['U'] = cmi_units(np.zeros_like(Fa), Cb, Xc, 1, 50, w)
        out[s] = d
    return out


class Chain:
    def __init__(self, D, seed, start):
        self.D = D
        self.tok = D.tok0.copy()
        N5.nb_seed(seed)
        if start == 'N1':
            N5.nb_shuffle_medial(self.tok, D.mov_pos, D.mov_start, D.mov_cnt)
        self.C = np.zeros_like(D.R)
        N5.nb_counts(self.tok, D.valid_edge, D.line_of, D.sec_line, D.last_u, D.first_u, D.NF, self.C)
        self.L1 = np.array([int(np.abs(self.C - D.R).sum())], dtype=np.int64)
        self.au = ANNEAL if start == 'N1' else 0
        self.sweep = 0

    def run(self, n, reseed=None):
        D = self.D
        if reseed is not None:
            N5.nb_seed(reseed)
        N5.nb_sweeps(self.tok, self.C, D.R, self.L1, n, BETA, self.au, self.sweep, D.n_prop, D.cumw, D.mov_pos,
                     D.mov_start, D.mov_cnt, D.valid_edge, D.sec_line, D.last_u, D.first_u, D.NF)
        self.sweep += n


def s_null(SCo, seeds, nsamp, thin, schemes, variants, keep_every=None, pilot_seed=None, gate_units=None):
    """Runs the N5 chains; returns draws dict[s][v] -> array (chains, draws, U) plus diagnostics and snapshots."""
    D = SCo.D
    draws = {s: {v: [] for v in variants} for s in schemes}
    diag = {'fc': [], 'tv': []}
    snaps = []
    chains = []
    for ci, sd in enumerate(seeds):
        ch = Chain(D, sd, 'real' if ci < len(seeds) // 2 or len(seeds) == 1 else 'N1')
        ch.run(BURN)
        chains.append(ch)
    per = [{s: {v: [] for v in variants} for s in schemes} for _ in seeds]

    def sample(ci, ch, k):
        st = s_stats(SCo, ch.tok, schemes, variants)
        for s in schemes:
            for v in variants:
                per[ci][s][v].append(st[s][v])
        diag['fc'].append(N5.frac_changed(D, ch.tok))
        diag['tv'].append(N5.group_tv(D, ch.C))

    for ci, ch in enumerate(chains):
        N5.nb_seed(seeds[ci] + 500)
        for k in range(nsamp):
            ch.run(thin)
            sample(ci, ch, k)
            if keep_every and (ci * nsamp + k) % keep_every == 0:
                snaps.append(ch.tok.copy())
    out = {s: {v: np.array([per[ci][s][v] for ci in range(len(seeds))]) for v in variants} for s in schemes}
    return out, diag, snaps, chains, per


def s_gates(SCo, draws, diag, gate_units):
    D = SCo.D
    rh, es = {}, {}
    for s, units in gate_units.items():
        arr = draws[s]['P']
        for g in units:
            j = SCo.units[s].index(g)
            x = arr[:, :, j]
            rh[f'{s}:{g}'] = float(N5.rhat_rank(x))
            es[f'{s}:{g}'] = float(N5.ess_bulk(x))
    tv = np.array(diag['tv']).mean(0)
    tol = np.array(D.tol)
    fc = float(np.mean(diag['fc']))
    ok_r = all(v < 1.05 for v in rh.values())
    ok_e = all(v >= 1000 for v in es.values()) if not SMOKE else True
    ok_tv = bool(np.all(tv <= tol))
    ok_fc = fc >= 0.50
    return {'rhat': rh, 'ess': es, 'tv_mean': dict(zip(D.group_names, tv.tolist())),
            'tol': dict(zip(D.group_names, tol.tolist())), 'fraction_changed': fc,
            'ok_rhat': ok_r, 'ok_ess': ok_e, 'ok_tv': ok_tv, 'ok_fc': ok_fc,
            'passed': bool(ok_r and ok_e and ok_tv and ok_fc)}


def gate_units_of(SCo, schemes=('S1', 'S2')):
    out = {}
    for s in schemes:
        u = set(KERNEL) & set(SCo.units[s])
        for k in KERNEL:
            u |= set(SCo.ctrl[s].get(k, []))
        out[s] = sorted(u)
    return out


def s_observe(SCo, draws, schemes, variants, extra=None):
    st = s_stats(SCo, SCo.D.tok0, schemes, variants)
    res = {}
    for s in schemes:
        res[s] = {}
        for v in variants:
            null = draws[s][v].reshape(-1, draws[s][v].shape[-1])
            z, mu, sd = zs(st[s][v], null)
            zd = {g: float(z[j]) for j, g in enumerate(SCo.units[s])}
            r = {'z': zd, 'obs': {g: float(st[s][v][j]) for j, g in enumerate(SCo.units[s])},
                 'excess': {g: float(st[s][v][j] - mu[j]) for j, g in enumerate(SCo.units[s])},
                 'MDE80_raw': {g: float(MDE80 * sd[j]) for j, g in enumerate(SCo.units[s])},
                 'rank_by_z': sorted(SCo.units[s], key=lambda g: -zd[g] if np.isfinite(zd[g]) else 1e9)}
            r['test'] = decide(triad_test(zd, SCo.ctrl[s], KERNEL), SCo.flags[s], zd, SCo.ctrl[s])
            res[s][v] = r
    return res


def s_boot_E(SCo, draws, n, seed, s='S1'):
    null = draws[s]['P'].reshape(-1, draws[s]['P'].shape[-1])
    mu, sd = null.mean(0), null.std(0)
    rng = np.random.default_rng(seed)
    Es = []
    for _ in range(n):
        dr = rng.integers(0, SCo.n_folios, SCo.n_folios)
        fw = np.bincount(dr, minlength=SCo.n_folios).astype(float)[SCo.pair_folio]
        st = s_stats(SCo, SCo.D.tok0, (s,), ('P',), w=fw)[s]['P']
        z = (st - mu) / np.where(sd > 0, sd, np.nan)
        zd = {g: float(z[j]) for j, g in enumerate(SCo.units[s])}
        Es.append(triad_test(zd, SCo.ctrl[s], KERNEL)['E'])
    Es = np.array(Es)
    return {'n': int(len(Es)), 'q025': float(np.nanpercentile(Es, 2.5)), 'q05': float(np.nanpercentile(Es, 5)),
            'q95': float(np.nanpercentile(Es, 95)), 'q975': float(np.nanpercentile(Es, 97.5)),
            'mean': float(np.nanmean(Es))}


def s_plant(SCo, tok, pi, T, rng, s='S1'):
    """Arm S plant on a copy of tok (see pre-registration)."""
    D = SCo.D
    tok = tok.copy()
    medial = (D.zone == 1) & (D.tok0 >= 0)
    V = D.vocab
    raw_first = [GLYPH_RE.findall(w)[0] for w in V]
    rawset = RAWSET[s]
    kern_members = {k: SCo.X[s][:, SCo.units[s].index(k)] for k in KERNEL if k in SCo.units[s]}
    by_line = defaultdict(list)
    for p in SCo.idx:
        by_line[D.line_of[p]].append(p)
    for li, ps in by_line.items():
        s0, L = D.line_start[li], D.line_len[li]
        med = [q for q in range(s0, s0 + L) if medial[q]]
        for p in ps:
            if not medial[p + 1]:
                continue
            for k in rng.permutation(list(kern_members)):
                t = tok[p]
                if not kern_members[k][t] or raw_first[t] in rawset[k]:
                    continue
                if SCo.Cl[tok[p + 1]] in T[k]:
                    continue
                if rng.random() >= pi:
                    continue
                cands = [q for q in med if q not in (p, p + 1) and SCo.Cl[tok[q]] in T[k]]
                if not cands:
                    continue
                q = cands[int(rng.integers(0, len(cands)))]
                tok[p + 1], tok[q] = tok[q], tok[p + 1]
    return tok


# ================================================================================================ stages
def stage_arm_w_H(words_b, folios_b):
    log('== Arm W: H S1 null (R = %d)' % R_W)
    seqs1 = [sch_units(w, SCHEMES['S1']) for w in words_b]
    W1 = arm_w('H_S1', seqs1, folios_b, R_W, SEED, want_sp=True)
    log('   nodes', len(W1['nodes']), '| G', W1['G'], '| eligible tokens', W1['eligible_tokens'])
    log('   controls', W1['controls'], 'flags', W1['flags'])
    note_node_pool(W1)
    if not same_sets(W1['controls'], PREREG_CONTROLS[('W', 'S1')]):
        RES['deviations'].append({'what': 'Arm W S1 controls differ from the pre-registered table',
                                  'rule': W1['controls'], 'prereg': PREREG_CONTROLS[('W', 'S1')]})
    # identity check on the real chain (not a statistic)
    WC = W1['_WC']
    C = WC.counts()
    st = w_stats(C, WC.m, np.arange(WC.m))
    rd = rwb_direct(C, WC.m)
    rel = float(np.max(np.abs(rd - st[1]) / np.abs(rd)))
    log(f'   RWB identity check: max relative error {rel:.2e}')
    RES['rwb_identity_max_rel_err'] = rel
    return W1, seqs1


def certify_w(W1):
    log('== Arm W: power certification (plants on null bases)')
    WC, gidx, G = W1['_WC'], W1['_gidx'], W1['G']
    kern = np.array([WC.nid[k] for k in KERNEL], dtype=np.int64)
    mu, sd = W1['_muY'], np.where(W1['_sdY'] > 0, W1['_sdY'], np.nan)
    on, ol = np.empty_like(WC.node), np.empty_like(WC.lens)

    def one(base_seed, pi):
        nb_seed(base_seed)
        w_permute(WC.node, WC.lens, WC.tok_start, WC.tok_nruns, WC.elig, on, ol, WC.maxn)
        pn, pl = on.copy(), ol.copy()
        w_plant(pn, pl, WC.tok_start, WC.tok_nruns, kern, pi)
        Y = w_stats(WC.counts(pn, pl), WC.m, gidx)[0]
        zd = {g: float((Y[i] - mu[i]) / sd[i]) for i, g in enumerate(G)}
        return triad_test(zd, W1['controls'], KERNEL)

    cal = {}
    pistar = None
    for pi in PI_GRID:
        r = [one(763_100 + i, pi) for i in range(PLANT_CAL)]
        cal[pi] = float(np.mean([x['E'] for x in r]))
        log(f'   pi {pi}: mean E {cal[pi]:.2f}')
        if cal[pi] >= MDE80:
            pistar = pi
            break
    out = {'calibration_mean_E': cal, 'pi_star': pistar}
    if pistar is None:
        out.update({'certified': False, 'detection': None})
    else:
        r = [one(763_200 + i, pistar) for i in range(PLANT_N)]
        det = float(np.mean([x['p'] <= 0.05 for x in r]))
        out.update({'detection': det, 'certified': det >= 0.80, 'mean_E_at_pi_star': float(np.mean([x['E'] for x in r]))})
    log('   certification', out)
    return out


def stage_arm_s(name, SCo, seeds, pilot_seed, snaps_every=None):
    log(f'== Arm S [{name}]: pilot (seed {pilot_seed})')
    gu = gate_units_of(SCo)
    ch = Chain(SCo.D, pilot_seed, 'real')
    ch.run(BURN)
    N5.nb_seed(pilot_seed + 500)
    ser = defaultdict(list)
    for _ in range(PILOT_N):
        ch.run(PILOT_THIN)
        st = s_stats(SCo, ch.tok, ('S1', 'S2'), ('P',))
        for s, units in gu.items():
            for g in units:
                ser[f'{s}:{g}'].append(st[s]['P'][SCo.units[s].index(g)])
    taus = {}
    for key, x in ser.items():
        x = np.array(x)
        e = N5.ess_bulk(x[None, :])
        taus[key] = float(PILOT_THIN * len(x) / max(e, 1e-9))
    T = int(max(10, np.ceil(max(taus.values()))))
    log(f'   tau (sweeps) max {max(taus.values()):.1f} -> thin T = {T}')
    log(f'== Arm S [{name}]: main chains {seeds}, {MAIN_N} samples each at thin {T}')
    draws, diag, snaps, chains, per = s_null(SCo, seeds, MAIN_N, T, ('S1', 'S2'), ('P', 'R1', 'R2', 'U'),
                                             keep_every=snaps_every)
    gates = s_gates(SCo, draws, diag, gu)
    extended = False
    if gates['ok_rhat'] and gates['ok_tv'] and gates['ok_fc'] and not gates['ok_ess']:
        log('   ESS short -> extending each chain to %d samples' % (2 * MAIN_N))
        extended = True
        for ci, chn in enumerate(chains):
            N5.nb_seed(seeds[ci] + 900)
            for _ in range(MAIN_N):
                chn.run(T)
                st = s_stats(SCo, chn.tok, ('S1', 'S2'), ('P', 'R1', 'R2', 'U'))
                for s in ('S1', 'S2'):
                    for v in ('P', 'R1', 'R2', 'U'):
                        per[ci][s][v].append(st[s][v])
                diag['fc'].append(N5.frac_changed(SCo.D, chn.tok))
                diag['tv'].append(N5.group_tv(SCo.D, chn.C))
        draws = {s: {v: np.array([per[ci][s][v] for ci in range(len(seeds))]) for v in ('P', 'R1', 'R2', 'U')}
                 for s in ('S1', 'S2')}
        gates = s_gates(SCo, draws, diag, gu)
    gates.update({'thin': T, 'tau_sweeps': taus, 'extended': extended, 'n_draws': int(draws['S1']['P'].shape[0]
                                                                                    * draws['S1']['P'].shape[1])})
    log(f"   gates passed={gates['passed']} rhat_ok={gates['ok_rhat']} ess_ok={gates['ok_ess']} "
        f"tv_ok={gates['ok_tv']} fc={gates['fraction_changed']:.3f} (min ESS "
        f"{min(gates['ess'].values()):.0f}, max R-hat {max(gates['rhat'].values()):.4f})")
    return draws, gates, snaps, T


def certify_s(SCo, draws, snaps):
    log('== Arm S: power certification (plants on N5 draws)')
    s = 'S1'
    null = draws[s]['P'].reshape(-1, draws[s]['P'].shape[-1])
    mu, sd = null.mean(0), null.std(0)
    sd = np.where(sd > 0, sd, np.nan)
    rng0 = np.random.default_rng(SEED)
    cls1 = Counter(SCo.Cl[SCo.D.tok0[SCo.idx]].tolist())
    tot = sum(cls1.values())
    big = sorted(c for c, v in cls1.items() if c > 0 and v / tot >= 0.01)
    T = {k: set(rng0.choice(big, 5, replace=False).tolist()) for k in KERNEL}
    log('   T_g', {k: sorted(v) for k, v in T.items()}, '| classes >= 1%:', len(big))

    def one(bi, pi, pseed):
        tok = s_plant(SCo, snaps[bi % len(snaps)], pi, T, np.random.default_rng(pseed))
        st = s_stats(SCo, tok, (s,), ('P',))[s]['P']
        z = (st - mu) / sd
        zd = {g: float(z[j]) for j, g in enumerate(SCo.units[s])}
        return triad_test(zd, SCo.ctrl[s], KERNEL)

    cal, pistar = {}, None
    for pi in PI_GRID:
        r = [one(i, pi, 763_300 + i) for i in range(PLANT_CAL)]
        cal[pi] = float(np.mean([x['E'] for x in r]))
        log(f'   pi {pi}: mean E {cal[pi]:.2f}')
        if cal[pi] >= MDE80:
            pistar = pi
            break
    out = {'T_g': {k: sorted(v) for k, v in T.items()}, 'calibration_mean_E': cal, 'pi_star': pistar,
           'n_bases': len(snaps)}
    if pistar is None:
        out.update({'certified': False, 'detection': None})
    else:
        r = [one(i, pistar, 763_400 + i) for i in range(PLANT_N)]
        det = float(np.mean([x['p'] <= 0.05 for x in r]))
        out.update({'detection': det, 'certified': det >= 0.80, 'mean_E_at_pi_star': float(np.mean([x['E'] for x in r]))})
    log('   certification', out)
    return out


def arm_status(test, signs_ok, p_extra_ok=True):
    p = test['p']
    if p <= 0.05 and signs_ok and p_extra_ok:
        return 'PASS'
    if p >= 0.5:
        return 'FAIL'
    return 'INCONCLUSIVE'


def main():
    lower_priority()
    log('PHASE_763 kernel re-test', 'SMOKE' if SMOKE else 'FULL')
    lines_p, secs_p, keys_p = N5.load_primary()
    fsec = {}
    for k, s in zip(keys_p, secs_p):
        fsec.setdefault(k[0], s)
    line_folios_p = [k[0] for k in keys_p]
    words_b, folios_b = load_b_readable()
    RES['data'] = {'B_readable_tokens': len(words_b), 'B_lines_primary': len(lines_p)}
    log('B readable tokens', len(words_b))

    # ---------------------------------------------------------------- Arm W, H S1: null, certification, observed
    W1, seqs1 = stage_arm_w_H(words_b, folios_b)
    certW = certify_w(W1)
    RES['arm_W'] = {'certification': certW}
    save()
    arm_w_observe(W1)
    WC = W1['_WC']
    sp_null = W1['_null']['SP']
    rng = np.random.default_rng(SEED + 1)
    bag = []
    for _ in range(N_BOOT):
        wts = np.bincount(rng.integers(0, len(seqs1), len(seqs1)), minlength=len(seqs1)).astype(float)
        bag.append(sp_betweenness(WC.counts(w=wts), W1['_gidx']))
    sp_obs = np.mean(bag, axis=0)
    zsp, _, _ = zs(sp_obs, sp_null)
    W1['z_shortest_path'] = {g: float(zsp[i]) for i, g in enumerate(W1['G'])}
    W1['boot'] = w_boot_E(W1, N_BOOT, SEED + 2)
    log('   H S1 test', W1['test'], '| boot', W1['boot'])
    RES['arm_W']['H_S1'] = public(W1)
    save()

    # robustness: S2, ZL; type-weighted
    seqs2 = [sch_units(w, SCHEMES['S2']) for w in words_b]
    W2 = arm_w_observe(arm_w('H_S2', seqs2, folios_b, R_W, SEED + 10))
    note_node_pool(W2)
    if not same_sets(W2['controls'], PREREG_CONTROLS[('W', 'S2')]):
        RES['deviations'].append({'what': 'Arm W S2 controls differ from the pre-registered table',
                                  'rule': W2['controls'], 'prereg': PREREG_CONTROLS[('W', 'S2')]})
    log('   S2 test', W2['test'])
    zw_words, zw_folios, zs_lines, zs_secs, zs_folios, zl_dropped = load_zl(fsec)
    RES['data'].update({'ZL_readable_tokens': len(zw_words), 'ZL_lines': len(zs_lines), 'ZL_dropped_folios': zl_dropped})
    WZ = arm_w_observe(arm_w('ZL_S1', [sch_units(w, SCHEMES['S1']) for w in zw_words], zw_folios, R_W, SEED + 20))
    log('   ZL test', WZ['test'])
    types = sorted(set(words_b))
    WT = arm_w_observe(arm_w('H_S1_types', [sch_units(w, SCHEMES['S1']) for w in types], ['T'] * len(types), R_W,
                             SEED + 30, fixed={'controls': W1['controls'], 'flags': W1['flags']}))
    log('   type-weighted test', WT['test'])
    RES['arm_W'].update({'H_S2': public(W2), 'ZL_S1': public(WZ), 'H_S1_types': public(WT)})
    save()

    # floors: Currier A
    log('== Arm W floor (a): Currier A')
    words_a, folios_a = load_a_readable()
    WA = arm_w_observe(arm_w('A_S1', [sch_units(w, SCHEMES['S1']) for w in words_a], folios_a, R_W, SEED + 40))
    target = WA['bigrams']
    rng = np.random.default_rng(SEED + 41)
    fol_b = sorted(set(folios_b))
    by_f = defaultdict(list)
    for i, f in enumerate(folios_b):
        by_f[f].append(i)
    downE = []
    for r in range(N_DOWN):
        order = rng.permutation(len(fol_b))
        sel, cnt = [], 0
        for fi in order:
            for i in by_f[fol_b[fi]]:
                sel.append(i)
                cnt += len(seqs1[i]) + 1
            if cnt >= target:
                break
        sub = arm_w_observe(arm_w(f'B_down_{r}', [seqs1[i] for i in sel], [folios_b[i] for i in sel], R_W_SMALL,
                                  SEED + 1000 + r, fixed={'controls': W1['controls'], 'flags': W1['flags']},
                                  nodes=W1['nodes'], pool=[g for g in W1['G'] if g not in KERNEL]))
        downE.append(sub['test']['E'])
    downE = np.array(downE)
    A_inside = bool(np.nanpercentile(downE, 2.5) <= WA['test']['E'] <= np.nanpercentile(downE, 97.5))
    RES['arm_W']['floor_A'] = {'A': public(WA), 'B_downsample_E': downE.tolist(),
                               'B_down_q025': float(np.nanpercentile(downE, 2.5)),
                               'B_down_q975': float(np.nanpercentile(downE, 97.5)), 'A_inside_B_range': A_inside}
    log('   A test', WA['test'], '| B downsample E range', RES['arm_W']['floor_A']['B_down_q025'],
        RES['arm_W']['floor_A']['B_down_q975'], '| inside:', A_inside)
    save()

    # floors: Latin
    log('== Arm W floor (b): Latin')
    lat = {}
    for li, key in enumerate(('mesue', 'rupescissa', 'sismel')):
        words = latin_words(key)
        span, blocks = latin_span(words, W1['bigrams'], np.random.default_rng(SEED + 50 + li))
        seqsL = [list(w) for w in span]
        WL = arm_w(f'LAT_{key}', seqsL, blocks, R_W, SEED + 60 + li, kernel=())
        arm_w_observe(WL, kernel=())
        G = WL['G']
        pool = [g for g in G if WL['_WC'].inst.get(g, 0) >= 200]
        best = None
        for tri in itertools.combinations(pool, 3):
            ctrl, _ = select_controls(WL['_WC'].feat, WL['_WC'].inst, [g for g in pool if g not in tri], list(tri))
            t = triad_test(WL['z'], ctrl, tri)
            if best is None or t['E'] > best[1]['E']:
                best = (tri, t, ctrl)
        bb = w_boot_E(WL, N_BOOT, SEED + 70 + li, triad=best[0], ctrl=best[2])
        lat[key] = {'words_total': len(words), 'span_tokens': len(span), 'bigrams': WL['bigrams'],
                    'pool': pool, 'z': WL['z'], 'best_triad': list(best[0]), 'best_test': best[1],
                    'best_controls': best[2], 'boot': bb}
        log(f'   {key}: span {len(span)} tokens, best triad {best[0]} E {best[1]["E"]:.2f} boot {bb}')
    distinctive = all(W1['boot']['q025'] > lat[k]['boot']['q975'] for k in lat)
    RES['arm_W']['floor_Latin'] = {'corpora': lat, 'B_kernel_E_q025': W1['boot']['q025'], 'distinctive': distinctive}
    log('   Latin distinctive:', distinctive)
    save()

    # ---------------------------------------------------------------- Arm S, H
    SCo = SCorpus(lines_p, secs_p, line_folios_p)
    log('Arm S pairs', len(SCo.idx), '| eligibility', SCo.eligibility, '| controls S1', SCo.ctrl['S1'],
        '| S2', SCo.ctrl['S2'])
    for s in ('S1', 'S2'):
        if not same_sets(SCo.ctrl[s], PREREG_CONTROLS[('S', s)]):
            RES['deviations'].append({'what': f'Arm S {s} controls differ from the pre-registered table',
                                      'rule': SCo.ctrl[s], 'prereg': PREREG_CONTROLS[('S', s)]})
    seeds_H = [76300, 76301, 76302, 76303]
    draws, gates, snaps, T_H = stage_arm_s('H', SCo, seeds_H, 76390, snaps_every=12)
    RES['arm_S'] = {'H_gates': gates, 'pairs': int(len(SCo.idx)), 'eligibility': SCo.eligibility,
                    'controls': SCo.ctrl, 'flags': SCo.flags, 'pools': SCo.pool}
    save()
    certS = certify_s(SCo, draws, snaps)
    RES['arm_S']['certification'] = certS
    save()
    obsS = s_observe(SCo, draws, ('S1', 'S2'), ('P', 'R1', 'R2', 'U'))
    bootS = s_boot_E(SCo, draws, N_BOOT, SEED + 80)
    RES['arm_S']['H'] = obsS
    RES['arm_S']['H_boot'] = bootS
    log('   H S1 primary test', obsS['S1']['P']['test'], '| boot', bootS)
    for v in ('R1', 'R2', 'U'):
        log(f'   H S1 {v} test', obsS['S1'][v]['test'])
    log('   H S2 primary test', obsS['S2']['P']['test'])
    save()

    # Arm S, ZL
    SZ = SCorpus(zs_lines, zs_secs, zs_folios)
    drawsZ, gatesZ, _, _ = stage_arm_s('ZL', SZ, [76310, 76311, 76312, 76313], 76391)
    obsZ = s_observe(SZ, drawsZ, ('S1',), ('P',))
    RES['arm_S']['ZL'] = {'gates': gatesZ, 'controls': SZ.ctrl, 'flags': SZ.flags, 'obs': obsZ,
                          'pairs': int(len(SZ.idx))}
    log('   ZL primary test', obsZ['S1']['P']['test'])
    save()

    # ---------------------------------------------------------------- generator floors (both arms)
    log('== Generator floors')
    sk = NH.load_skeleton()
    assert [tuple(k) for k in sk['keys']] == [tuple(k) for k in keys_p], 'skeleton / primary line order differ'
    m_gv1 = NH.load_version('GV1')
    pt = NH.plaintext('P-REC', m_gv1)
    timm = NH.Timm(sk['B'], sk['folio'])
    gen = {'NAIBBE_GV1_PREC_STREAM_SR0_V0': [], 'TIMM': []}
    for kind in gen:
        for mb in range(N_GEN):
            seed = 763_500_000 + (0 if kind == 'TIMM' else 1_000_000) + mb
            if kind == 'TIMM':
                corpus = timm.generate(sk['B'], np.random.default_rng(seed))
            else:
                toks, _ = NH.gen_stream(m_gv1, pt, seed, sk['n_certain'], False)
                corpus = NH.pour(toks, sk['B'])
            corpus = [[w if (w is None or GLYPH_RE.findall(w)) else None for w in ln] for ln in corpus]
            wtoks = [(w, sk['folio'][li]) for li, ln in enumerate(corpus) for w in ln if w is not None]
            GW = arm_w_observe(arm_w(f'{kind}_{mb}', [sch_units(w, SCHEMES['S1']) for w, _ in wtoks],
                                     [f for _, f in wtoks], R_W_SMALL, SEED + 2000 + mb))
            SG = SCorpus(corpus, secs_p, line_folios_p, schemes=('S1',))
            dr, dg, _, _, _ = s_null(SG, [seed % 1_000_000 + 7, seed % 1_000_000 + 8], GEN_N, T_H, ('S1',), ('P',))
            gg = s_gates(SG, dr, dg, gate_units_of(SG, ('S1',)))
            so = s_observe(SG, dr, ('S1',), ('P',))['S1']['P']
            gen[kind].append({'W_E': GW['test']['E'], 'W_p': GW['test']['p'], 'S_E': so['test']['E'],
                              'S_p': so['test']['p'], 'S_gates_passed': gg['passed'], 'S_min_ess': min(gg['ess'].values()),
                              'S_eligibility': SG.eligibility['S1'], 'class_coverage': float(np.mean(SG.Cl[SG.D.tok0[SG.idx]] > 0))})
            log(f'   {kind} member {mb}: W E {GW["test"]["E"]:.2f} | S E {so["test"]["E"]:.2f} '
                f'(gates {gg["passed"]})')
            RES['generators'] = gen
            save()
    gsum = {}
    for kind, rows in gen.items():
        wE = np.array([r['W_E'] for r in rows])
        sE = np.array([r['S_E'] for r in rows])
        gsum[kind] = {'W_q025': float(np.nanpercentile(wE, 2.5)), 'W_q975': float(np.nanpercentile(wE, 97.5)),
                      'S_q025': float(np.nanpercentile(sE, 2.5)), 'S_q975': float(np.nanpercentile(sE, 97.5)),
                      'B_W_inside': bool(np.nanpercentile(wE, 2.5) <= W1['test']['E'] <= np.nanpercentile(wE, 97.5)),
                      'B_S_inside': bool(np.nanpercentile(sE, 2.5) <= obsS['S1']['P']['test']['E']
                                         <= np.nanpercentile(sE, 97.5))}
    RES['generator_summary'] = gsum
    log('   generator summary', gsum)
    save()

    # ---------------------------------------------------------------- verdict (locked rules)
    tW, tS = W1['test'], obsS['S1']['P']['test']
    E_W, E_S = tW['E'], tS['E']
    sgn = lambda e: np.sign(e) if np.isfinite(e) else 0  # noqa: E731
    w_signs = {'S2': sgn(W2['test']['E']) == sgn(E_W), 'ZL': sgn(WZ['test']['E']) == sgn(E_W)}
    w_zl_p = WZ['test']['p'] <= 0.10
    s_signs = {'R1': sgn(obsS['S1']['R1']['test']['E']) == sgn(E_S), 'R2': sgn(obsS['S1']['R2']['test']['E']) == sgn(E_S),
               'ZL': sgn(obsZ['S1']['P']['test']['E']) == sgn(E_S), 'S2': sgn(obsS['S2']['P']['test']['E']) == sgn(E_S)}
    s_zl_p = obsZ['S1']['P']['test']['p'] <= 0.10 and gatesZ['passed']
    unfl_ok = lambda t: t.get('unflagged_test') is None or t['unflagged_test']['p'] <= 0.05  # noqa: E731
    stW = arm_status(tW, all(w_signs.values()) and E_W > 0, w_zl_p and unfl_ok(tW))
    stS = arm_status(tS, all(s_signs.values()) and E_S > 0, s_zl_p and unfl_ok(tS))
    if not (gates['passed']):
        stS = 'INCONCLUSIVE (gates)'
    if stW == 'FAIL' and not certW['certified']:
        stW = 'INCONCLUSIVE (uncertified)'
    if stS == 'FAIL' and not certS['certified']:
        stS = 'INCONCLUSIVE (uncertified)'
    # Holm over the two arm p-values
    ps = sorted([('W', tW['p']), ('S', tS['p'])], key=lambda x: x[1])
    holm = {}
    rej = True
    for i, (a, p) in enumerate(ps):
        thr = 0.05 / (2 - i)
        rej = rej and p <= thr
        holm[a] = bool(rej)
    passW = stW == 'PASS' and holm['W']
    passS = stS == 'PASS' and holm['S']
    floors_hit = []
    if RES['arm_W']['floor_A']['A_inside_B_range']:
        floors_hit.append('A (script/lexicon)')
    if not distinctive:
        floors_hit.append('Latin (not distinguishable from the best-case letter triad of an alphabetic script)')
    for kind, g in gsum.items():
        if g['B_W_inside']:
            floors_hit.append(f'{kind} (Arm W)')
        if g['B_S_inside']:
            floors_hit.append(f'{kind} (Arm S)')
    killed = (stW == 'FAIL' and stS == 'FAIL'
              and W1['boot']['q95'] < MDE80 and bootS['q95'] < MDE80)
    if passW and passS:
        verdict = 'PASS, FLOOR-SCOPED' if floors_hit else 'PASS'
    elif passW or passS:
        verdict = 'MIXED'
    elif killed:
        verdict = 'KILLED'
    else:
        verdict = 'NOT ESTABLISHED'
    RES['verdict'] = {'arm_W_status': stW, 'arm_S_status': stS, 'holm': holm, 'arm_W_pass': passW,
                      'arm_S_pass': passS, 'W_robustness_signs': w_signs, 'W_ZL_p_ok': bool(w_zl_p),
                      'S_robustness_signs': s_signs, 'S_ZL_p_ok': bool(s_zl_p), 'floors_reproducing': floors_hit,
                      'certified': {'W': certW['certified'], 'S': certS['certified']},
                      'equivalence_q95': {'W': W1['boot']['q95'], 'S': bootS['q95']}, 'E': {'W': E_W, 'S': E_S},
                      'p': {'W': tW['p'], 'S': tS['p']}, 'VERDICT': verdict}
    RES['runtime_s'] = time.time() - T0
    log('VERDICT (locked rules):', verdict)
    log(json.dumps(RES['verdict'], default=str))
    save(f'kernel_retest{TAG}.json')


if __name__ == '__main__':
    main()
