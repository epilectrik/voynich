"""PHASE_769 v2 machinery (lean audit edits E1-E12): batched permutation engine, covariate-adjusted S3c (primary),
S3far, S3-dis, S3-int, S3-cons, S3-k, the paragraph arm S3P, folio covariates (incl. H-F legibility), plants.

Occurrence arrays are built here (not in ed769) so every per-run attribute is aligned in one pass.
"""
from __future__ import annotations

import difflib
import math
import re
from collections import Counter, defaultdict

import numpy as np
import scipy.sparse as sp

import ed769 as E

GLYPH_RE = E.GLYPH_RE
MIN_OCC = 5
K_SPLITS = 50


# ------------------------------------------------------------------------------------------------ tracks and legibility
def track_lines(tr):
    from scripts.voynich import Transcript
    out = defaultdict(list)
    for t in Transcript().all(h_only=False):
        if t.transcriber != tr or t.language != 'B' or t.is_label:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if w:
            out[(t.folio, t.line)].append(w)
    return out


def collapse_e(w):
    return re.sub('e+', 'e', w)


def hf_alignment():
    """Token alignment H -> F per line (PHASE_758 rule: equal blocks and equal-length replace blocks 1:1).
    Returns {(folio, line, h_index): F word or None} and the folio legibility (share of H tokens whose e-collapsed
    form is not matched by an aligned F token), for folios with F coverage."""
    H, F = track_lines('H'), track_lines('F')
    amap, leg = {}, defaultdict(lambda: [0, 0])
    for key, h in H.items():
        f = F.get(key)
        if f is None:
            continue
        pairs = {}
        sm = difflib.SequenceMatcher(None, h, f, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == 'equal' or (op == 'replace' and i2 - i1 == j2 - j1):
                for a, b in zip(range(i1, i2), range(j1, j2)):
                    pairs[a] = f[b]
        for i, w in enumerate(h):
            fw = pairs.get(i)
            amap[(key[0], key[1], i)] = fw
            leg[key[0]][0] += 1
            if fw is None or collapse_e(fw) != collapse_e(w):
                leg[key[0]][1] += 1
    return amap, {f: d / n for f, (n, d) in leg.items() if n}


# ------------------------------------------------------------------------------------------------ occurrences
def occurrences2(recs, kind='e', amap=None):
    plen = Counter(r[5] for r in recs)
    q = np.quantile(np.array(list(plen.values()), dtype=float), [1 / 3, 2 / 3])
    fn = E.e_runs if kind == 'e' else E.i_runs
    folio_lines, par_lines = defaultdict(list), defaultdict(list)
    for r in recs:
        if r[2] not in folio_lines[r[1]]:
            folio_lines[r[1]].append(r[2])
        if r[2] not in par_lines[r[5]]:
            par_lines[r[5]].append(r[2])
    half, quart = {}, {}
    for f, keys in folio_lines.items():
        L = len(keys)
        cut = (L + 1) // 2
        qn = max(1, math.ceil(L / 4))
        for i, k in enumerate(keys):
            half[k] = 0 if i < cut else 1
            quart[k] = 0 if i < qn else (1 if i >= L - qn else -1)
    phalf = {}
    for p, keys in par_lines.items():
        L = len(keys)
        for i, k in enumerate(keys):
            if L < 4:
                phalf[k] = -1
            elif i < L // 2:
                phalf[k] = 0
            elif i >= L - L // 2:
                phalf[k] = 1
            else:
                phalf[k] = -1                          # middle line of an odd paragraph: dropped
    rows = defaultdict(list)
    for w, folio, key, p, n, pid, header, sec, hand in recs:
        runs, frame = fn(w)
        if not runs:
            continue
        g = GLYPH_RE.findall(w)
        zone = 0 if p == 0 else (2 if p == n - 1 else 1)
        pl = 0 if plen[pid] <= q[0] else (1 if plen[pid] <= q[1] else 2)
        # run positions in glyph units (for token-final and after-k flags)
        pos, i = [], 0
        while i < len(g):
            if kind == 'e' and g[i] == 'e':
                j = i
                while j < len(g) and g[j] == 'e':
                    j += 1
                pos.append((i, j))
                i = j
            elif kind == 'i' and re.fullmatch(r'i+[nrlm]', g[i]):
                pos.append((i, i + 1))
                i += 1
            else:
                i += 1
        fw = amap.get((folio, key[1], p)) if amap is not None else None
        f_runs = fn(fw)[0] if fw else None
        f_same_frame = fw is not None and fn(fw)[1] == frame
        for j, L in enumerate(runs):
            s0, s1 = pos[j]
            y = 1 if L >= 2 else 0
            rows['y'].append(y)
            rows['cell'].append(((frame, j), zone, header, pl, sec, hand))
            rows['folio'].append(folio)
            rows['par'].append(pid)
            rows['token'].append(frame)                               # split key: collapsed token string
            rows['half'].append(half[key])
            rows['quart'].append(quart[key])
            rows['phalf'].append(phalf[key])
            rows['final'].append(s1 == len(g))
            rows['after_k'].append(s0 > 0 and g[s0 - 1] == 'k')
            rows['cons'].append(bool(f_same_frame and f_runs is not None and len(f_runs) == len(runs)
                                     and (1 if f_runs[j] >= 2 else 0) == y))
            rows['line'].append(key)
    cid = {c: i for i, c in enumerate(dict.fromkeys(rows['cell']))}
    fid = {f: i for i, f in enumerate(dict.fromkeys(rows['folio']))}
    tid = {t: i for i, t in enumerate(dict.fromkeys(rows['token']))}
    O = {'y': np.array(rows['y'], dtype=float), 'cell': np.array([cid[c] for c in rows['cell']]),
         'folio': np.array([fid[f] for f in rows['folio']]), 'par': np.array(rows['par']),
         'token': np.array([tid[t] for t in rows['token']]), 'token_str': list(tid),
         'half': np.array(rows['half']), 'quart': np.array(rows['quart']), 'phalf': np.array(rows['phalf']),
         'final': np.array(rows['final']), 'after_k': np.array(rows['after_k']), 'cons': np.array(rows['cons']),
         'folio_names': list(fid), 'n_tokens': len(tid), 'line_keys': rows['line']}
    cf = defaultdict(set)
    for c, f in zip(O['cell'], O['folio']):
        cf[c].add(f)
    O['informative'] = np.array([len(cf[c]) >= 2 for c in O['cell']])
    return O


def folio_covariates(recs, O, legibility):
    lines, toks, pars = defaultdict(set), Counter(), defaultdict(set)
    for r in recs:
        lines[r[1]].add(r[2])
        toks[r[1]] += 1
        pars[r[1]].add(r[5])
    med = float(np.median(list(legibility.values()))) if legibility else 0.0
    X = []
    for f in O['folio_names']:
        L = len(lines[f])
        X.append([math.log(L), toks[f] / L, len(pars[f]), legibility.get(f, med)])
    X = np.array(X, dtype=float)
    X = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1)
    return np.hstack([np.ones((len(X), 1)), X])


# ------------------------------------------------------------------------------------------------ permutation engine
def perm_batch(y, groups, B, rng):
    """B within-group permutations of y: returns (B, n)."""
    n = len(y)
    stable = np.argsort(groups, kind='stable')
    keys = rng.random((B, n)) + groups[None, :] * 2.0
    rnd = np.argsort(keys, axis=1)
    out = np.empty((B, n))
    out[:, stable] = y[rnd]
    return out


class Coherence:
    """Split-half cross-frame coherence between two regions (e.g. top / bottom half of a folio's lines) over units
    (folios or paragraphs). mode 'corr': mean over splits and swaps of the (optionally covariate-adjusted) Pearson
    correlation across units with >= min_occ occurrences in each region; mode 'sum': sum over units of
    (sum r in region 1) x (sum r in region 2), no minimum counts."""

    def __init__(self, unit, region, token, n_tokens, n_units, splits_seed=7690, k=K_SPLITS, X=None,
                 min_occ=MIN_OCC, mode='corr', regions=(0, 1)):
        rng = np.random.default_rng(splits_seed)
        n = len(unit)
        self.mode, self.blocks = mode, []
        rows, cols = [], []
        r0, r1 = regions
        base = 0
        for _ in range(k):
            inA = (rng.random(n_tokens) < 0.5)[token]
            for g1, g2 in (((inA, r0), (~inA, r1)), ((~inA, r0), (inA, r1))):
                m1 = g1[0] & (region == g1[1])
                m2 = g2[0] & (region == g2[1])
                for m in (m1, m2):
                    idx = np.flatnonzero(m)
                    rows.append(base + unit[idx])
                    cols.append(idx)
                    base += n_units
                self.blocks.append(len(self.blocks))
        self.n_units = n_units
        self.M = sp.csr_matrix((np.ones(sum(len(c) for c in cols)), (np.concatenate(rows), np.concatenate(cols))),
                               shape=(base, n))
        cnt = np.asarray(self.M.sum(axis=1)).ravel().reshape(-1, 2, n_units)
        self.cnt = cnt
        self.proj = []
        for b in range(cnt.shape[0]):
            n1, n2 = cnt[b, 0], cnt[b, 1]
            ok = (n1 >= min_occ) & (n2 >= min_occ) if mode == 'corr' else np.ones(n_units, bool)
            P = []
            if X is not None and mode == 'corr' and ok.sum() > X.shape[1] + 2:
                for w in (n1[ok], n2[ok]):
                    Xq = X[ok]
                    W = np.diag(w)
                    P.append(np.eye(ok.sum()) - Xq @ np.linalg.pinv(Xq.T @ W @ Xq) @ Xq.T @ W)
            self.proj.append((ok, P))

    def __call__(self, R):
        """R: (n, B) residuals -> (B,) statistic."""
        S = (self.M @ R).reshape(-1, 2, self.n_units, R.shape[1])
        if self.mode == 'sum':
            return (S[:, 0] * S[:, 1]).sum(axis=1).sum(axis=0)
        vals = []
        for b in range(S.shape[0]):
            ok, P = self.proj[b]
            if ok.sum() < 5:
                continue
            a = S[b, 0][ok] / self.cnt[b, 0][ok][:, None]
            c = S[b, 1][ok] / self.cnt[b, 1][ok][:, None]
            if P:
                a, c = P[0] @ a, P[1] @ c
            a = a - a.mean(0)
            c = c - c.mean(0)
            den = np.sqrt((a * a).sum(0) * (c * c).sum(0))
            vals.append(np.where(den > 0, (a * c).sum(0) / np.where(den > 0, den, 1), np.nan))
        return np.nanmean(np.array(vals), axis=0) if vals else np.full(R.shape[1], np.nan)


def s1_batch(R, unit, n_units):
    M = sp.csr_matrix((np.ones(len(unit)), (unit, np.arange(len(unit)))), shape=(n_units, len(unit)))
    S = M @ R
    n = np.asarray(M.sum(axis=1)).ravel()
    ok = n > 0
    return (S[ok] ** 2 / n[ok][:, None]).sum(0)


def _ed(a, b, cap):
    if abs(len(a) - len(b)) >= cap:
        return cap
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j - 1] + (a[i - 1] != b[j - 1]), prev[j] + 1, cur[j - 1] + 1)
        if min(cur) >= cap:
            return cap
        prev = cur
    return min(prev[-1], cap)


class Dis:
    """S3-dis: sum over folios of sum_{i top, j bottom, ED(frame_i, frame_j) >= 3} r_i r_j."""

    def __init__(self, unit, half, token, token_str, n_units):
        n = len(unit)
        self.Mt = sp.csr_matrix((np.ones(int((half == 0).sum())), (unit[half == 0], np.flatnonzero(half == 0))),
                                shape=(n_units, n))
        self.Mb = sp.csr_matrix((np.ones(int((half == 1).sum())), (unit[half == 1], np.flatnonzero(half == 1))),
                                shape=(n_units, n))
        I, J = [], []
        edc = {}
        by = defaultdict(lambda: ([], []))
        for i in range(n):
            by[unit[i]][half[i]].append(i)
        for u, (top, bot) in by.items():
            for i in top:
                for j in bot:
                    a, b = token[i], token[j]
                    key = (a, b) if a <= b else (b, a)
                    if key not in edc:
                        edc[key] = _ed(GLYPH_RE.findall(token_str[a]), GLYPH_RE.findall(token_str[b]), 3)
                    if edc[key] <= 2:
                        I.append(i)
                        J.append(j)
        self.I, self.J = np.array(I, dtype=np.int64), np.array(J, dtype=np.int64)
        self.n_near = len(I)

    def __call__(self, R):
        tot = ((self.Mt @ R) * (self.Mb @ R)).sum(0)
        near = (R[self.I] * R[self.J]).sum(0) if self.n_near else 0.0
        return tot - near


# ------------------------------------------------------------------------------------------------ the full battery
class Battery:
    """All statistics on one occurrence set (restricted to informative occurrences and an optional subset mask)."""

    def __init__(self, O, X=None, subset=None, paragraph=True, k=K_SPLITS):
        m = O['informative'].copy()
        if subset is not None:
            m &= subset
        self.m = m
        self.cell = O['cell'][m]
        _, fu = np.unique(O['folio'][m], return_inverse=True)
        self.fu = fu.ravel()
        self.nf = int(self.fu.max()) + 1
        fnames = np.array(O['folio_names'])[np.unique(O['folio'][m])]
        self.X = None
        if X is not None:
            keep = np.unique(O['folio'][m])
            self.X = X[keep]
        tok = O['token'][m]
        self.S3 = Coherence(self.fu, O['half'][m], tok, O['n_tokens'], self.nf, k=k)
        self.S3c = Coherence(self.fu, O['half'][m], tok, O['n_tokens'], self.nf, k=k, X=self.X)
        self.S3far = Coherence(self.fu, O['quart'][m], tok, O['n_tokens'], self.nf, k=k, X=self.X)
        self.dis = Dis(self.fu, O['half'][m], tok, O['token_str'], self.nf)
        self.par = None
        if paragraph:
            _, pu = np.unique(O['par'][m], return_inverse=True)
            self.pu = pu.ravel()
            self.S3P = Coherence(self.pu, O['phalf'][m], tok, O['n_tokens'], int(self.pu.max()) + 1, k=k, mode='sum')
            _, g2 = np.unique(np.stack([self.cell, self.fu], axis=1), axis=0, return_inverse=True)
            self.cell_x_folio = g2.ravel()

    def evaluate(self, y, nperm=1000, seed=769, batch=250, stats=('S1', 'S3', 'S3c', 'S3far', 'S3dis', 'S3P'),
                 within_folio_para=False):
        rng = np.random.default_rng(seed)
        yy = y[self.m]
        cm = E.cell_means(yy, self.cell)
        R0 = (yy - cm)[:, None]
        fns = {'S1': lambda R: s1_batch(R, self.fu, self.nf), 'S3': self.S3, 'S3c': self.S3c, 'S3far': self.S3far,
               'S3dis': self.dis}
        if hasattr(self, 'S3P'):
            fns['S3P'] = self.S3P
        stats = [s for s in stats if s in fns]
        obs = {s: float(fns[s](R0)[0]) for s in stats}
        nulls = {s: [] for s in stats}
        groups = self.cell_x_folio if within_folio_para else self.cell
        cm_null = E.cell_means(yy, groups) if within_folio_para else cm
        if within_folio_para:
            R0w = (yy - cm_null)[:, None]
            obs = {s: float(fns[s](R0w)[0]) for s in stats}
        done = 0
        while done < nperm:
            b = min(batch, nperm - done)
            Y = perm_batch(yy, groups, b, rng)
            R = (Y - cm_null[None, :]).T
            for s in stats:
                nulls[s].append(fns[s](R))
            done += b
        out = {'n_occ': int(self.m.sum()), 'n_folios': self.nf}
        for s in stats:
            nv = np.concatenate(nulls[s])
            ok = ~np.isnan(nv)
            o = obs[s]
            out[s] = o
            out[f'{s}_null_mean'] = float(nv[ok].mean()) if ok.any() else float('nan')
            out[f'{s}_null_sd'] = float(nv[ok].std(ddof=1)) if ok.sum() > 1 else float('nan')
            out[f'p_{s}'] = float((1 + (nv[ok] >= o).sum()) / (1 + ok.sum())) if ok.any() and not np.isnan(o) else 1.0
        return out


# ------------------------------------------------------------------------------------------------ plants (synthetic y)
def base_logit(O):
    p = np.clip(E.cell_means(O['y'], O['cell']), 0.01, 0.99)
    return np.log(p / (1 - p))


def draw(lg, rng):
    return (rng.random(len(lg)) < 1 / (1 + np.exp(-lg))).astype(float)


def plant(O, mode, s, rng, lines_of=None):
    lg = base_logit(O)
    if mode == 'SHARED':
        return draw(lg + rng.normal(0, s, len(O['folio_names']))[O['folio']], rng)
    if mode == 'SHARED_PARA':
        _, pu = np.unique(O['par'], return_inverse=True)
        pu = pu.ravel()
        return draw(lg + rng.normal(0, s, pu.max() + 1)[pu], rng)
    if mode == 'SHARED_K':
        d = rng.normal(0, s, len(O['folio_names']))[O['folio']]
        return draw(lg + np.where(O['after_k'], d, 0.0), rng)
    if mode == 'WORDSPEC':
        key = O['token'] * 1000 + O['folio']
        _, inv = np.unique(key, return_inverse=True)
        return draw(lg + rng.normal(0, s, inv.max() + 1)[inv.ravel()], rng)
    if mode == 'LOCAL':
        p = 1 / (1 + np.exp(-lg))
        y = np.zeros(len(lg))
        prev_res, prev_f = 0.0, -1
        for t in range(len(lg)):
            sh = s * prev_res if O['folio'][t] == prev_f else 0.0
            y[t] = float(rng.random() < 1 / (1 + np.exp(-(lg[t] + sh))))
            prev_res, prev_f = y[t] - p[t], O['folio'][t]
        return y
    if mode == 'DRIFT':
        # random walk over each folio's lines, started at 0 (no folio intercept); increments scaled so that the
        # SD across folios of the folio-mean walk equals s
        line_ids = O['line_idx']
        walks, fmeans = {}, []
        for f in range(len(O['folio_names'])):
            L = O['folio_nlines'][f]
            w = np.concatenate([[0.0], np.cumsum(rng.normal(0, 1, L - 1))]) if L > 1 else np.zeros(1)
            walks[f] = w
            fmeans.append(w.mean())
        scale = s / (np.std(fmeans) if np.std(fmeans) > 0 else 1)
        d = np.array([walks[f][l] for f, l in zip(O['folio'], line_ids)]) * scale
        return draw(lg + d, rng)
    if mode == 'COPY':
        p = 1 / (1 + np.exp(-lg))
        y = (rng.random(len(lg)) < p).astype(float)
        for t in range(len(lg)):
            src = O['copy_src'][t]
            if src >= 0 and rng.random() < s:
                y[t] = y[src]
        return y
    raise ValueError(mode)


def add_structure(O):
    """Per-occurrence line index within folio, folio line counts, and the most recent earlier same-folio occurrence
    whose collapsed token is exactly one glyph-unit edit away (for the COPY control)."""
    line_idx, nlines = [], {}
    seen = defaultdict(dict)
    for f, key in zip(O['folio'], O['line_keys']):
        d = seen[f]
        if key not in d:
            d[key] = len(d)
        line_idx.append(d[key])
    O['line_idx'] = np.array(line_idx)
    O['folio_nlines'] = {f: len(d) for f, d in seen.items()}
    toks = [GLYPH_RE.findall(t) for t in O['token_str']]
    src = np.full(len(O['y']), -1)
    last_by_folio = defaultdict(list)
    edc = {}
    for t in range(len(O['y'])):
        f, a = O['folio'][t], O['token'][t]
        for u in reversed(last_by_folio[f][-60:]):
            b = O['token'][u]
            if a == b:
                continue
            key = (a, b) if a < b else (b, a)
            if key not in edc:
                edc[key] = _ed(toks[a], toks[b], 2)
            if edc[key] == 1:
                src[t] = u
                break
        last_by_folio[f].append(t)
    O['copy_src'] = src
    return O
