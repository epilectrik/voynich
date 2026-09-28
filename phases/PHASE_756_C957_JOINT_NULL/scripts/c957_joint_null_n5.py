#!/usr/bin/env python3
"""PHASE_756 — C957 joint null N5 + cross-track check. See ../PRE_REGISTRATION.md (locked, commit 766b1cd).

N5: MCMC over within-line permutations of movable MEDIAL tokens (INITIAL, FINAL and uncertain blockers fixed),
target pi ∝ exp(-beta * L1), L1 = sum over sections of |C_s(state) - C_s(real)| for the (last unit -> first unit)
edge-count matrix. Units: EVA characters and PHASE_754 glyph units. beta chosen from diagnostics only.

Usage: python c957_joint_null_n5.py [--smoke]   (smoke: tiny run, no statistics printed)
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from numba import njit
from scipy.stats import norm, rankdata

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript  # noqa: E402

OUT = ROOT / 'phases/PHASE_756_C957_JOINT_NULL/results'
OUT.mkdir(parents=True, exist_ok=True)
SMOKE = '--smoke' in sys.argv
if SMOKE:
    OUT = Path('C:/Users/EPILEC~1/AppData/Local/Temp/claude/C--git-voynich/e451f3a8-445d-45a0-bf5f-3a967a8e452a/scratchpad')

GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
MIN_FREQ = 10
E_PRIMARY, E_SECONDARY = 3.0, 5.0
BETA_GRID = [0.5, 1.0, 2.0, 4.0, 8.0]
PILOT_SWEEPS, PILOT_ANNEAL, PILOT_EVERY = 1000, 500, 10
BURN, ANNEAL, NSAMP, THIN = 2000, 1000, 1000, 5
SEEDS = {'EVA': (75601, 75605), 'GLYPH': (75611, 75615), 'EVA_C957DATA': (75621, 75625)}
PILOT_SEED = {'EVA': 75690, 'GLYPH': 75695, 'EVA_C957DATA': 75680}
MIN_GROUP_EDGES = 1000
OTHER_TRACKS = ['F', 'C', 'V', 'T', 'G', 'U']
if SMOKE:
    BETA_GRID = [1.0, 4.0]
    PILOT_SWEEPS, PILOT_ANNEAL = 60, 30
    BURN, ANNEAL, NSAMP, THIN = 40, 20, 30, 2


def log(*a):
    print(*a, flush=True)


# ================================================================================================ data
def load_primary():
    """Currier B, H track, P placement, labels excluded; uncertain tokens kept as blockers (None)."""
    tx = Transcript()
    lines, sect = defaultdict(list), {}
    for t in tx.currier_b(exclude_uncertain=False):
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if not w:
            continue
        key = (t.folio, t.line)
        lines[key].append(None if t.is_uncertain else w)
        sect.setdefault(key, set()).add(t.section)
    keys = list(lines)
    assert all(len(sect[k]) == 1 for k in keys), 'line spans sections'
    return [lines[k] for k in keys], [next(iter(sect[k])) for k in keys], keys


def load_c957_identical():
    """PHASE_753 / C957 pipeline: all Currier B placements, uncertain dropped (neighbours joined)."""
    tx = Transcript()
    lines, sect = defaultdict(list), {}
    for t in tx.currier_b():
        w = t.word.replace('*', '').strip()
        if w:
            key = (t.folio, t.line)
            lines[key].append(w)
            sect.setdefault(key, t.section)
    keys = list(lines)
    return [lines[k] for k in keys], [sect[k] for k in keys], keys


def units(word, unit):
    if unit.startswith('EVA'):
        return word[0], word[-1]
    g = GLYPH_RE.findall(word)
    return g[0], g[-1]


class Data:
    """Flat arrays for one corpus and one edge unit."""

    def __init__(self, line_list, sections, unit, common_words=None):
        self.unit = unit
        self.line_list = line_list
        words = [w for ln in line_list for w in ln if w is not None]
        cnt = Counter(words)
        self.tok_counts = cnt
        self.common = common_words if common_words is not None else sorted(w for w, c in cnt.items() if c >= MIN_FREQ)
        self.K = len(self.common)
        cid = {w: i for i, w in enumerate(self.common)}
        self.vocab = sorted(cnt)
        vid = {w: i for i, w in enumerate(self.vocab)}
        firsts = sorted({units(w, unit)[0] for w in self.vocab})
        lasts = sorted({units(w, unit)[1] for w in self.vocab})
        self.firsts, self.lasts = firsts, lasts
        fid = {u: i for i, u in enumerate(firsts)}
        lid = {u: i for i, u in enumerate(lasts)}
        self.NF, self.NL = len(firsts), len(lasts)
        self.first_u = np.array([fid[units(w, unit)[0]] for w in self.vocab], dtype=np.int64)
        self.last_u = np.array([lid[units(w, unit)[1]] for w in self.vocab], dtype=np.int64)
        self.v_common = np.array([cid.get(w, -1) for w in self.vocab], dtype=np.int64)
        secs = sorted(set(sections))
        self.sections = secs
        sid = {s: i for i, s in enumerate(secs)}
        self.S = len(secs)
        self.sec_line = np.array([sid[s] for s in sections], dtype=np.int64)

        tok, line_of, zone = [], [], []
        line_start, line_len = [], []
        for li, ln in enumerate(line_list):
            line_start.append(len(tok))
            line_len.append(len(ln))
            for p, w in enumerate(ln):
                tok.append(-1 if w is None else vid[w])
                line_of.append(li)
                zone.append(0 if p == 0 else (2 if p == len(ln) - 1 else 1))
        self.tok0 = np.array(tok, dtype=np.int64)
        self.line_of = np.array(line_of, dtype=np.int64)
        self.zone = np.array(zone, dtype=np.int64)
        self.line_start = np.array(line_start, dtype=np.int64)
        self.line_len = np.array(line_len, dtype=np.int64)
        n = len(tok)
        ve = np.zeros(n, dtype=np.bool_)
        ve[:-1] = (self.line_of[:-1] == self.line_of[1:]) & (self.tok0[:-1] >= 0) & (self.tok0[1:] >= 0)
        self.valid_edge = ve
        movable = (self.zone == 1) & (self.tok0 >= 0)
        mov_pos, mov_start, mov_cnt = [], [], []
        for li in range(len(line_list)):
            s0 = self.line_start[li]
            ps = [p for p in range(s0, s0 + self.line_len[li]) if movable[p]]
            mov_start.append(len(mov_pos))
            mov_cnt.append(len(ps))
            mov_pos.extend(ps)
        self.mov_pos = np.array(mov_pos, dtype=np.int64)
        self.mov_start = np.array(mov_start, dtype=np.int64)
        self.mov_cnt = np.array(mov_cnt, dtype=np.int64)
        w = self.mov_cnt * (self.mov_cnt - 1) / 2.0
        self.cumw = np.cumsum(w)
        self.n_prop = int(self.mov_cnt[self.mov_cnt >= 2].sum())
        # fraction-changed mask: movable positions in lines with >= 2 movable tokens not all of one type
        fc = np.zeros(n, dtype=np.bool_)
        frozen_line = np.ones(len(line_list), dtype=np.bool_)
        for li in range(len(line_list)):
            if self.mov_cnt[li] >= 2:
                ps = self.mov_pos[self.mov_start[li]: self.mov_start[li] + self.mov_cnt[li]]
                if len(set(self.tok0[ps].tolist())) > 1:
                    fc[ps] = True
                    frozen_line[li] = False
        self.fc_pos = np.flatnonzero(fc)
        self.frozen_line = frozen_line
        self.R = np.zeros((self.S, self.NL * self.NF), dtype=np.int64)
        nb_counts(self.tok0, self.valid_edge, self.line_of, self.sec_line, self.last_u, self.first_u, self.NF, self.R)
        # TV groups
        edges_per_sec = self.R.sum(axis=1)
        big = [s for s in range(self.S) if edges_per_sec[s] >= MIN_GROUP_EDGES]
        small = [s for s in range(self.S) if edges_per_sec[s] < MIN_GROUP_EDGES]
        groups = {s: [s] for s in big}
        if small:
            target = min(big, key=lambda s: edges_per_sec[s])
            groups[target] = groups[target] + small
        self.groups = [sorted(v) for v in groups.values()]
        self.group_names = ['+'.join(secs[s] for s in g) for g in self.groups]
        self.K_coupling, self.tol = [], []
        for g in self.groups:
            m = self.R[g].sum(axis=0).reshape(self.NL, self.NF).astype(float)
            p = m / m.sum()
            prod = np.outer(p.sum(axis=1), p.sum(axis=0))
            k = 0.5 * np.abs(p - prod).sum()
            self.K_coupling.append(float(k))
            self.tol.append(float(min(0.02, 0.10 * k)))
        self.real_pairs = nb_pair_counts(self.tok0, self.valid_edge, self.v_common, self.K)
        # frozen-line real pair counts (constant under N5)
        fl_mask = self.frozen_line[self.line_of]
        tok_f = np.where(fl_mask, self.tok0, -1)
        ve_f = self.valid_edge & fl_mask
        self.frozen_pairs = nb_pair_counts(tok_f, ve_f, self.v_common, self.K)

    def summary(self):
        return {'unit': self.unit, 'lines': len(self.line_list), 'tokens': int((self.tok0 >= 0).sum()),
                'blockers': int((self.tok0 < 0).sum()), 'common_tokens': self.K, 'vocab': len(self.vocab),
                'first_units': self.NF, 'last_units': self.NL, 'sections': self.sections,
                'edges_per_section': {self.sections[s]: int(self.R[s].sum()) for s in range(self.S)},
                'tv_groups': self.group_names, 'coupling_K': dict(zip(self.group_names, self.K_coupling)),
                'tolerance': dict(zip(self.group_names, self.tol)),
                'movable_medial_tokens': int(self.mov_cnt.sum()), 'proposals_per_sweep': self.n_prop,
                'fraction_changed_denominator': int(len(self.fc_pos)),
                'frozen_lines': int(self.frozen_line.sum()),
                'real_common_bigrams': int(self.real_pairs.sum())}


# ================================================================================================ numba kernels
@njit(cache=True)
def nb_seed(s):
    np.random.seed(s)


@njit(cache=True)
def nb_counts(tok, valid_edge, line_of, sec_line, last_u, first_u, NF, C):
    C[:, :] = 0
    for p in range(len(tok) - 1):
        if valid_edge[p]:
            C[sec_line[line_of[p]], last_u[tok[p]] * NF + first_u[tok[p + 1]]] += 1


@njit(cache=True)
def nb_pair_counts(tok, valid_edge, v_common, K):
    out = np.zeros(K * K, dtype=np.int32)
    for p in range(len(tok) - 1):
        if valid_edge[p]:
            a = v_common[tok[p]]
            b = v_common[tok[p + 1]]
            if a >= 0 and b >= 0:
                out[a * K + b] += 1
    return out


@njit(cache=True)
def nb_shuffle_medial(tok, mov_pos, mov_start, mov_cnt):
    for li in range(len(mov_cnt)):
        m = mov_cnt[li]
        s0 = mov_start[li]
        for a in range(m - 1, 0, -1):
            b = np.random.randint(a + 1)
            pa = mov_pos[s0 + a]
            pb = mov_pos[s0 + b]
            t = tok[pa]
            tok[pa] = tok[pb]
            tok[pb] = t


@njit(cache=True)
def _val(tok, p, i, j, ti, tj):
    if p == i:
        return tj
    if p == j:
        return ti
    return tok[p]


@njit(cache=True)
def nb_sweeps(tok, C, R, L1, n_sweeps, beta_target, anneal_until, sweep0, n_prop, cumw, mov_pos, mov_start,
              mov_cnt, valid_edge, sec_line, last_u, first_u, NF):
    """Run n_sweeps sweeps in place. Returns number of accepted non-trivial swaps."""
    total_w = cumw[-1]
    acc = 0
    ks = np.empty(4, dtype=np.int64)
    cells = np.empty(8, dtype=np.int64)
    dc = np.empty(8, dtype=np.int64)
    for t in range(n_sweeps):
        g = sweep0 + t
        if anneal_until > 0 and g < anneal_until:
            beta = beta_target * g / anneal_until
        else:
            beta = beta_target
        for _ in range(n_prop):
            u = np.random.random() * total_w
            li = np.searchsorted(cumw, u, side='right')
            if li >= len(cumw):
                li = len(cumw) - 1
            m = mov_cnt[li]
            if m < 2:
                continue
            a = np.random.randint(m)
            b = np.random.randint(m - 1)
            if b >= a:
                b += 1
            i = mov_pos[mov_start[li] + a]
            j = mov_pos[mov_start[li] + b]
            if i > j:
                i, j = j, i
            ti = tok[i]
            tj = tok[j]
            if ti == tj:
                continue
            nk = 0
            for k in (i - 1, i, j - 1, j):
                dup = False
                for q in range(nk):
                    if ks[q] == k:
                        dup = True
                if not dup:
                    ks[nk] = k
                    nk += 1
            nc = 0
            for q in range(nk):
                k = ks[q]
                if not valid_edge[k]:
                    continue
                old = last_u[tok[k]] * NF + first_u[tok[k + 1]]
                new = last_u[_val(tok, k, i, j, ti, tj)] * NF + first_u[_val(tok, k + 1, i, j, ti, tj)]
                if old == new:
                    continue
                for cell, d in ((old, -1), (new, 1)):
                    found = False
                    for r in range(nc):
                        if cells[r] == cell:
                            dc[r] += d
                            found = True
                    if not found:
                        cells[nc] = cell
                        dc[nc] = d
                        nc += 1
            s = sec_line[li]
            dL1 = 0
            for r in range(nc):
                c0 = C[s, cells[r]] - R[s, cells[r]]
                dL1 += abs(c0 + dc[r]) - abs(c0)
            if dL1 <= 0 or beta == 0.0 or np.random.random() < np.exp(-beta * dL1):
                tok[i] = tj
                tok[j] = ti
                for r in range(nc):
                    C[s, cells[r]] += dc[r]
                L1[0] += dL1
                acc += 1
    return acc


# ================================================================================================ chain driver
def group_tv(D, C):
    out = []
    for g in D.groups:
        a = C[g].sum(axis=0).astype(float)
        r = D.R[g].sum(axis=0).astype(float)
        out.append(0.5 * np.abs(a / a.sum() - r / r.sum()).sum())
    return out


def run_chain(D, beta, seed, start, burn, anneal, nsamp, thin, on_sample):
    tok = D.tok0.copy()
    nb_seed(seed)
    if start == 'N1':
        nb_shuffle_medial(tok, D.mov_pos, D.mov_start, D.mov_cnt)
    C = np.zeros_like(D.R)
    nb_counts(tok, D.valid_edge, D.line_of, D.sec_line, D.last_u, D.first_u, D.NF, C)
    L1 = np.array([int(np.abs(C - D.R).sum())], dtype=np.int64)
    args = (D.n_prop, D.cumw, D.mov_pos, D.mov_start, D.mov_cnt, D.valid_edge, D.sec_line, D.last_u, D.first_u, D.NF)
    au = anneal if start == 'N1' else 0
    nb_sweeps(tok, C, D.R, L1, burn, beta, au, 0, *args)
    sweep = burn
    for _ in range(nsamp):
        nb_sweeps(tok, C, D.R, L1, thin, beta, au, sweep, *args)
        sweep += thin
        on_sample(tok, C, int(L1[0]))
    assert int(np.abs(C - D.R).sum()) == int(L1[0]), 'L1 bookkeeping drift'
    return tok


def frac_changed(D, tok):
    return float((tok[D.fc_pos] != D.tok0[D.fc_pos]).mean())


def frac_changed_all(D, tok):
    ok = D.tok0 >= 0
    return float((tok[ok] != D.tok0[ok]).mean())


# ================================================================================================ convergence diagnostics
def _z_scale(x):
    r = rankdata(x.ravel(), method='average').reshape(x.shape)
    return norm.ppf((r - 0.375) / (x.size + 0.25))


def _split(x):
    n = x.shape[1] // 2
    return np.vstack([x[:, :n], x[:, x.shape[1] - n:]])


def _rhat(x):
    n = x.shape[1]
    between = n * np.var(x.mean(axis=1), ddof=1)
    within = np.mean(np.var(x, axis=1, ddof=1))
    return float(np.sqrt((between / within + n - 1) / n))


def rhat_rank(x):
    x = np.asarray(x, dtype=float)
    if np.ptp(x) == 0:
        return 1.0
    s = _split(x)
    rb = _rhat(_z_scale(s))
    f = np.abs(s - np.median(s))
    rt = _rhat(_z_scale(f)) if np.ptp(f) > 0 else 1.0
    return max(rb, rt)


def _autocov(x):
    n = x.shape[1]
    xc = x - x.mean(axis=1, keepdims=True)
    f = np.fft.rfft(xc, n=2 * n, axis=1)
    ac = np.fft.irfft(f * np.conj(f), axis=1)[:, :n] / n
    return ac


def _ess(x):
    m, n = x.shape
    acov = _autocov(x)
    chain_mean = x.mean(axis=1)
    mean_var = acov[:, 0].mean() * n / (n - 1.0)
    var_plus = mean_var * (n - 1.0) / n
    if m > 1:
        var_plus += np.var(chain_mean, ddof=1)
    rho = np.zeros(n)
    rho_even, rho[0] = 1.0, 1.0
    rho_odd = 1.0 - (mean_var - acov[:, 1].mean()) / var_plus
    rho[1] = rho_odd
    t = 1
    while t < n - 3 and (rho_even + rho_odd) > 0.0:
        rho_even = 1.0 - (mean_var - acov[:, t + 1].mean()) / var_plus
        rho_odd = 1.0 - (mean_var - acov[:, t + 2].mean()) / var_plus
        if rho_even + rho_odd >= 0:
            rho[t + 1] = rho_even
            rho[t + 2] = rho_odd
        t += 2
    max_t = t - 2
    if rho_even > 0:
        rho[max_t + 1] = rho_even
    t = 1
    while t <= max_t - 2:
        if rho[t + 1] + rho[t + 2] > rho[t - 1] + rho[t]:
            rho[t + 1] = (rho[t - 1] + rho[t]) / 2.0
            rho[t + 2] = rho[t + 1]
        t += 2
    tau = -1.0 + 2.0 * rho[:max_t + 1].sum() + rho[max_t + 1:max_t + 2].sum()
    tau = max(tau, 1.0 / np.log10(m * n))
    return float(m * n / tau)


def ess_bulk(x):
    x = np.asarray(x, dtype=float)
    if np.ptp(x) == 0:
        return float(x.size)
    return _ess(_z_scale(_split(x)))


# ================================================================================================ pilot (beta choice)
def pilot(D, name):
    rows = []
    for bi, beta in enumerate(BETA_GRID):
        per_start = {}
        for si, start in enumerate(('real', 'N1')):
            rec = {'L1': [], 'tv': [], 'fc': []}

            def on_sample(tok, C, L1, rec=rec):
                rec['L1'].append(L1)
                rec['tv'].append(group_tv(D, C))
                rec['fc'].append(frac_changed(D, tok))

            burn = PILOT_SWEEPS - PILOT_SWEEPS // 2
            nsamp = (PILOT_SWEEPS // 2) // PILOT_EVERY
            run_chain(D, beta, PILOT_SEED[name] + 10 * bi + si, start, burn, PILOT_ANNEAL, nsamp, PILOT_EVERY, on_sample)
            tv = np.array(rec['tv'])
            per_start[start] = {'mean_L1': float(np.mean(rec['L1'])), 'mean_tv': tv.mean(axis=0).tolist(),
                                'fraction_changed': float(np.mean(rec['fc']))}
        edges = int(D.R.sum())
        c1 = per_start['real']['fraction_changed'] >= 0.50
        c2 = all(per_start[s]['mean_tv'][g] <= D.tol[g] for s in per_start for g in range(len(D.groups)))
        l_real, l_n1 = per_start['real']['mean_L1'], per_start['N1']['mean_L1']
        c3 = (abs(l_n1 - l_real) <= 0.10 * max(l_real, 1e-9)) or (l_real <= 0.01 * edges and l_n1 <= 0.01 * edges)
        row = {'beta': beta, 'real_start': per_start['real'], 'N1_start': per_start['N1'],
               'fraction_changed_ok': bool(c1), 'tv_ok': bool(c2), 'anneal_agreement_ok': bool(c3),
               'admissible': bool(c1 and c2 and c3)}
        rows.append(row)
        log(f"  pilot {name} beta={beta}: fc={per_start['real']['fraction_changed']:.3f} "
            f"L1 real/N1={l_real:.0f}/{l_n1:.0f} tv_real={[round(v, 4) for v in per_start['real']['mean_tv']]} "
            f"tol={[round(v, 4) for v in D.tol]} -> admissible={row['admissible']}")
    return rows


# ================================================================================================ main runs
def pass1(D, name, beta, scale):
    seed0 = SEEDS[name][0]
    sums = []
    diag = defaultdict(list)
    for c in range(4):
        tot = np.zeros(D.K * D.K, dtype=np.float64)
        n = [0]

        def on_sample(tok, C, L1, tot=tot, n=n):
            tot += nb_pair_counts(tok, D.valid_edge, D.v_common, D.K)
            n[0] += 1
        t0 = time.time()
        run_chain(D, beta, seed0 + c, 'real' if c < 2 else 'N1', BURN * scale, ANNEAL * scale, NSAMP * scale, THIN,
                  on_sample)
        sums.append((tot, n[0]))
        log(f"  {name} pass1 chain {c + 1}: {time.time() - t0:.1f}s")
    E = sum(t for t, _ in sums) / sum(n for _, n in sums)
    Ea = (sums[0][0] + sums[1][0]) / (sums[0][1] + sums[1][1])
    Eb = (sums[2][0] + sums[3][0]) / (sums[2][1] + sums[3][1])
    ca, cb = set(np.flatnonzero(Ea >= E_PRIMARY)), set(np.flatnonzero(Eb >= E_PRIMARY))
    jac = len(ca & cb) / max(1, len(ca | cb))
    return E, jac


def pass2(D, name, beta, scale, cand_masks, track):
    seed0 = SEEDS[name][1]
    per_chain = []
    for c in range(4):
        rec = {k: [] for k in cand_masks}
        rec.update({'L1': [], 'fc': [], 'fc_all': [], 'tv': []})
        rec['zero_hits'] = np.zeros(int(track.sum()), dtype=np.int64)
        rec['zero_ind'] = []

        def on_sample(tok, C, L1, rec=rec):
            pc = nb_pair_counts(tok, D.valid_edge, D.v_common, D.K)
            z = pc == 0
            for k, m in cand_masks.items():
                rec[k].append(int((z & m).sum()))
            zt = z[track]
            rec['zero_hits'] += zt
            rec['zero_ind'].append(zt.copy())
            rec['L1'].append(L1)
            rec['fc'].append(frac_changed(D, tok))
            rec['fc_all'].append(frac_changed_all(D, tok))
            rec['tv'].append(group_tv(D, C))
        t0 = time.time()
        run_chain(D, beta, seed0 + c, 'real' if c < 2 else 'N1', BURN * scale, ANNEAL * scale, NSAMP * scale, THIN,
                  on_sample)
        per_chain.append(rec)
        log(f"  {name} pass2 chain {c + 5}: {time.time() - t0:.1f}s")
    return per_chain


def pval(Znull, zreal):
    Znull = np.asarray(Znull, dtype=float)
    return float((1 + (Znull >= zreal - 1e-9).sum()) / (1 + len(Znull)))


def analyse_unit(D, name, track_attest):
    """Full procedure for one unit: pilot, beta*, pass 1, pass 2 with retries. Returns result dict."""
    log(f"\n=== {name}: {D.summary()}")
    pil = pilot(D, name)
    admissible = [r['beta'] for r in pil if r['admissible']]
    res = {'data': D.summary(), 'pilot': pil, 'admissible_betas': admissible}
    if not admissible:
        res.update({'achieved': False, 'reason': 'no admissible beta'})
        log(f"  {name}: NO ADMISSIBLE BETA")
        return res
    for beta in sorted(admissible, reverse=True):
        for scale in (1, 2):
            log(f"  {name}: main run beta={beta} scale={scale}")
            E, jac = pass1(D, name, beta, scale)
            extra = 1
            while jac < 0.95 and extra < 4:
                extra *= 2
                E2, jac = pass1(D, name, beta, scale * extra)
                E = E2
            real = D.real_pairs
            cand3, cand5 = E >= E_PRIMARY, E >= E_SECONDARY
            real0 = real == 0
            fragile = np.zeros_like(cand3)
            for k in np.flatnonzero((cand3 | cand5) & real0):
                a, b = D.common[k // D.K], D.common[k % D.K]
                if track_attest['F'].get((a, b), 0) > 0 or track_attest['C'].get((a, b), 0) > 0:
                    fragile[k] = True
            cand_masks = {'Z3_clean': cand3 & ~fragile, 'Z3_raw': cand3, 'Z5_clean': cand5 & ~fragile, 'Z5_raw': cand5}
            track = (cand3 | cand5) & real0
            chains = pass2(D, name, beta, scale, cand_masks, track)
            Z3 = np.array([c['Z3_clean'] for c in chains])
            L1s = np.array([c['L1'] for c in chains])
            FC = np.array([c['fc'] for c in chains])
            TV = np.array([c['tv'] for c in chains])          # chains x samples x groups
            diag = {'rhat_Z3': rhat_rank(Z3), 'rhat_L1': rhat_rank(L1s), 'rhat_fc': rhat_rank(FC),
                    'ess_Z3': ess_bulk(Z3), 'ess_L1': ess_bulk(L1s), 'ess_fc': ess_bulk(FC),
                    'fraction_changed_mean': float(FC.mean()),
                    'fraction_changed_all_positions_mean': float(np.mean([c['fc_all'] for c in chains])),
                    'tv_mean': dict(zip(D.group_names, TV.mean(axis=(0, 1)).tolist())),
                    'tv_q95': dict(zip(D.group_names, np.quantile(TV, 0.95, axis=(0, 1)).tolist())),
                    'L1_mean': float(L1s.mean()), 'candidate_jaccard_pass1': float(jac)}
            ok = (diag['rhat_Z3'] < 1.05 and diag['rhat_L1'] < 1.05 and diag['rhat_fc'] < 1.05
                  and diag['ess_Z3'] >= 1000 and diag['ess_L1'] >= 1000 and diag['ess_fc'] >= 1000
                  and diag['fraction_changed_mean'] >= 0.50
                  and all(TV.mean(axis=(0, 1))[g] <= D.tol[g] for g in range(len(D.groups))))
            diag['passed'] = bool(ok)
            if SMOKE:
                ok = True          # exercise the summary code; smoke output is never interpreted
            log(f"  {name} diagnostics (beta={beta}, scale={scale}): " +
                ', '.join(f"{k}={v:.4g}" if isinstance(v, float) else f"{k}={v}" for k, v in diag.items()
                          if not isinstance(v, dict)))
            log(f"     tv_mean={diag['tv_mean']} tol={dict(zip(D.group_names, D.tol))}")
            res.setdefault('attempts', []).append({'beta': beta, 'scale': scale, 'diagnostics': diag})
            if ok:
                res.update(summarise(D, name, beta, scale, E, cand_masks, fragile, track, chains, diag))
                res['achieved'] = True
                return res
    res.update({'achieved': False, 'reason': 'diagnostics failed at every admissible beta'})
    return res


def summarise(D, name, beta, scale, E, cand_masks, fragile, track, chains, diag):
    real = D.real_pairs
    out = {'beta_star': beta, 'scale': scale, 'diagnostics': diag}
    Zall = {k: np.concatenate([c[k] for c in chains]).astype(float) for k in cand_masks}
    L1 = np.concatenate([c['L1'] for c in chains]).astype(float)
    zero_ind = np.concatenate([np.array(c['zero_ind']) for c in chains])       # samples x tracked
    track_idx = np.flatnonzero(track)
    P0 = zero_ind.mean(axis=0)
    stats = {}
    for k, m in cand_masks.items():
        zr = int((m & (real == 0)).sum())
        Zn = Zall[k]
        st = {'n_candidates': int(m.sum()), 'Z_real': zr, 'null_mean': float(Zn.mean()), 'null_sd': float(Zn.std()),
              'null_q95': float(np.quantile(Zn, 0.95)), 'null_q99': float(np.quantile(Zn, 0.99)),
              'null_max': float(Zn.max()), 'p': pval(Zn, zr)}
        # L1 extrapolation
        b = float(np.polyfit(L1, Zn, 1)[0]) if np.ptp(L1) > 0 else 0.0
        Zp = Zn - b * L1
        st['L1_slope'] = b
        st['null_mean_extrapolated'] = float(Zp.mean())
        st['p_extrap'] = pval(Zp, zr)
        # leave-one-cell-out
        zero_cands = [k2 for k2 in np.flatnonzero(m & (real == 0))]
        if zero_cands:
            pos = {int(t): i for i, t in enumerate(track_idx)}
            best = min(zero_cands, key=lambda c: (P0[pos[int(c)]], -E[c]))
            col = zero_ind[:, pos[int(best)]].astype(float)
            st['loo_cell'] = f"{D.common[best // D.K]}->{D.common[best % D.K]}"
            st['p_loo'] = pval(Zn - col, zr - 1)
        else:
            st['loo_cell'] = None
            st['p_loo'] = st['p']
        stats[k] = st
        if not SMOKE:
            log(f"  {name} {k}: cand={st['n_candidates']} Z_real={zr} null {st['null_mean']:.2f}±{st['null_sd']:.2f} "
                f"q99={st['null_q99']} p={st['p']:.4f} | extrap mean {st['null_mean_extrapolated']:.2f} "
                f"p'={st['p_extrap']:.4f} | loo[{st['loo_cell']}] p={st['p_loo']:.4f}")
    out['stats'] = stats
    out['p'] = stats['Z3_clean']['p']
    out['p_extrap'] = stats['Z3_clean']['p_extrap']
    out['p_loo'] = stats['Z3_clean']['p_loo']
    cand3 = cand_masks['Z3_raw']
    out['frozen_share_of_candidate_expected_mass'] = float(D.frozen_pairs[cand3].sum() / max(E[cand3].sum(), 1e-9))
    out['track_fragile_cells'] = [f"{D.common[k // D.K]}->{D.common[k % D.K]}" for k in np.flatnonzero(fragile)]
    per_pair = []
    for i, k in enumerate(track_idx):
        per_pair.append({'pair': f"{D.common[k // D.K]}->{D.common[k % D.K]}", 'E': round(float(E[k]), 3),
                         'P0': round(float(P0[i]), 4), 'candidate_E3': bool(cand3[k]),
                         'candidate_E5': bool(cand_masks['Z5_raw'][k]), 'track_fragile': bool(fragile[k])})
    per_pair.sort(key=lambda r: (r['P0'], -r['E']))
    out['per_pair'] = per_pair
    return out


# ================================================================================================ cross-track
def track_pairs():
    tx = Transcript()
    lines = defaultdict(lambda: defaultdict(list))
    concat = Counter()
    for t in tx.all(h_only=False):
        w = t.word.strip()
        if not w:
            continue
        if '*' not in w:
            concat[w] += 1
        if t.transcriber not in OTHER_TRACKS or t.language != 'B' or t.is_label:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        lines[t.transcriber][(t.folio, t.line)].append(None if '*' in w else w)
    att = {}
    for tr in OTHER_TRACKS:
        c = Counter()
        for ln in lines[tr].values():
            for a, b in zip(ln, ln[1:]):
                if a is not None and b is not None:
                    c[(a, b)] += 1
        att[tr] = c
    return att, concat


# ================================================================================================ verdict
def verdict(eva, gly):
    if not eva.get('achieved'):
        return 'NULL-NOT-ACHIEVED'
    pE = eva['p']
    if gly.get('achieved'):
        pG = gly['p']
        if pG >= 0.10:
            return 'REDUCES'
        if pE < 0.01 and pG < 0.01:
            ok = all(u['p_extrap'] < 0.01 and u['p_loo'] < 0.01 for u in (eva, gly))
            return 'RESIDUAL' if ok else 'FRAGILE'
        if pG < 0.01 and pE >= 0.01:
            return 'FRAGILE'
        return 'INCONCLUSIVE'
    if pE >= 0.10:
        return 'REDUCES'
    return 'INCONCLUSIVE'


def main():
    t_start = time.time()
    att, concat = track_pairs()
    log('other-track pair counts: ' + ', '.join(f"{k}={sum(v.values())}" for k, v in att.items()))
    lines, secs, _ = load_primary()
    results = {}
    D_eva = Data(lines, secs, 'EVA')
    D_gly = Data(lines, secs, 'GLYPH', common_words=D_eva.common)
    assert D_eva.K == D_gly.K
    results['EVA'] = analyse_unit(D_eva, 'EVA', att)
    json.dump({'interim': 'EVA done'}, open(OUT / 'interim.json', 'w'))
    results['GLYPH'] = analyse_unit(D_gly, 'GLYPH', att)
    v = verdict(results['EVA'], results['GLYPH'])
    log(f"\nVERDICT (locked rules): {v}" if not SMOKE else 'smoke run: verdict suppressed')
    # C957-identical data, reported only (EVA unit)
    l2, s2, _ = load_c957_identical()
    D_c957 = Data(l2, s2, 'EVA_C957DATA')
    results['EVA_C957DATA'] = analyse_unit(D_c957, 'EVA_C957DATA', att)

    # per-pair enrichment: other tracks, concatenations, PHASE_753 P0
    p753 = {}
    f753 = ROOT / 'phases/PHASE_753_C957_THREE_NULL_SCREEN/results/c957_three_null_screen.json'
    if f753.exists():
        for r in json.load(open(f753, encoding='utf-8'))['per_pair']:
            p753[r['pair']] = {'P0_N1_753': r.get('P0_N1'), 'P0_N2_753': r.get('P0_N2'), 'P0_N4_753': r.get('P0_N4')}
    for name in ('EVA', 'GLYPH', 'EVA_C957DATA'):
        for r in results[name].get('per_pair', []):
            a, b = r['pair'].split('->')
            r['other_tracks'] = {tr: att[tr].get((a, b), 0) for tr in OTHER_TRACKS}
            r['concat_any_track'] = concat.get(a + b, 0)
            r.update(p753.get(r['pair'], {}))
    out = {'phase': 'PHASE_756', 'pre_registration_commit': '766b1cd', 'smoke': SMOKE,
           'settings': {'beta_grid': BETA_GRID, 'pilot_sweeps': PILOT_SWEEPS, 'burn': BURN, 'anneal': ANNEAL,
                        'samples_per_chain': NSAMP, 'thin': THIN, 'seeds': SEEDS, 'pilot_seeds': PILOT_SEED},
           'verdict': v, 'results': results, 'runtime_s': round(time.time() - t_start, 1)}
    fn = 'c957_joint_null_n5_SMOKE.json' if SMOKE else 'c957_joint_null_n5.json'
    json.dump(out, open(OUT / fn, 'w', encoding='utf-8'), indent=1, default=float)
    log(f"written {OUT / fn}  ({out['runtime_s']}s)")


if __name__ == '__main__':
    main()
