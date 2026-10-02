"""PHASE_779 -- The minimal device (v2, after the lean-expert design audit): a sampler of page x line-type
composition, line-position vocabulary and two-unit junction routing, the measured specification of Currier B
(C2093-C2095 cells; D6/C956; C2082, C1212/C1563). Which of B's other registered regularities is it not outside?

Device (a sampler of measured rules, not a production method):
  STOCK    tokens drawn without replacement from the page x line-type (paragraph-first / body) multiset, so every
           generated page x line-type cell has exactly B's composition. Lower rung: page-only stocks. Sensitivity 'w':
           with replacement (depletion only; composition statistics are not read on it).
  ZONE     candidate x P_s(z | w): per-word for words with n >= NMIN_ZONE, else P_s(z | first unit, last unit), else
           P(z); smoothed toward P(z) with pseudo-count KZ (audit edit 3). 'memo' variant: per-word tables for every
           word (carries rare words' B positions; descriptive).
  ROUTING  candidate x P_s(u(w) | e_prev) / P(u(w)), within-line pairs only; P_s smoothed toward P(u) with pseudo-count
           kappa (chosen on D2 alone in the pre-lock fidelity gate); R2a: last unit; R2: last two units -> first unit;
           R3: last two -> first two units (audit edits 1-2).
  Weight = n_rem(w) x zone x routing (line-initial slots: zone only). No paragraph state, line memory, interior rule
  or repeat rule.
Plants (power controls on the primary rung): weight multipliers with a declared grid (audit edit 29).
Header extension (+H): B-fitted line-type tables (descriptive; exposure-carrying).
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts'))
sys.path.insert(0, str(ROOT / 'phases/PHASE_778_GRILLE_RIVAL_PANEL/scripts'))
import panel_stats as S  # noqa: E402
import grille778 as G8  # noqa: E402  (skeleton with sections and paragraph-first flags)

GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
GALLOWS = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
FP = {'p', 'f', 'cph', 'cfh'}
ZONES = ('I', 'M', 'F')
NMIN_ZONE = 5          # per-word zone table only for words seen at least this often (audit edit 3)
KZ = 1.0               # zone smoothing pseudo-count toward P(zone)
KAPPA_GRID = (0.5, 2.0, 8.0)   # routing smoothing pseudo-counts, chosen on D2 alone (fidelity gate)
COMMON_MIN = 10        # common tokens for the pair-zero statistic (C2081 form)
_MORPH = None
_CLS = None


def units(w):
    return GLYPH_RE.findall(w)


def skeleton():
    return G8.skeleton()


def zone_of(p, n):
    return 'I' if p == 0 else ('F' if p == n - 1 else 'M')


def erun(w):
    return min(max((len(m) for m in re.findall(r'e+', w)), default=0), 2)


def family(w):
    u0 = units(w)[0]
    return 'q' if w.startswith('qo') else ('c' if u0 in ('ch', 'sh') else None)


# ================================================================================================ specification
def spec_tables(sk, kappa=2.0, kz=KZ, nmin=NMIN_ZONE):
    """Corpus-wide tables (declared exposure): zone tables with back-off, within-line routing tables with smoothing
    toward the first-unit marginal, line-type tables for the header extension, common-token index."""
    pz = Counter()
    zw, zfl = defaultdict(Counter), defaultdict(Counter)
    wc = Counter()
    r1, r2, r3 = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    u1c, u2c = Counter(), Counter()
    hfirst, hlast, afirst, alast = Counter(), Counter(), Counter(), Counter()
    zf = {t: defaultdict(Counter) for t in ('H', 'B', 'A')}
    zl = {t: defaultdict(Counter) for t in ('H', 'B', 'A')}
    n_header = n_all = 0
    for ln, par in zip(sk['lines'], sk['par_initial']):
        n = len(ln)
        prev = None
        for p, w in enumerate(ln):
            if w is None:
                prev = None
                continue
            z = zone_of(p, n)
            u = units(w)
            pz[z] += 1
            zw[w][z] += 1
            zfl[(u[0], u[-1])][z] += 1
            wc[w] += 1
            afirst[u[0]] += 1
            alast[u[-1]] += 1
            n_all += 1
            if par:
                hfirst[u[0]] += 1
                hlast[u[-1]] += 1
                n_header += 1
            for t in ('H' if par else 'B', 'A'):
                zf[t][u[0]][z] += 1
                zl[t][u[-1]][z] += 1
            if prev is not None:                      # within-line junction population (D2's)
                pu = units(prev)
                r1[pu[-1]][u[0]] += 1
                r2[tuple(pu[-2:])][u[0]] += 1
                r3[tuple(pu[-2:])][tuple(u[:2])] += 1
                u1c[u[0]] += 1
                u2c[tuple(u[:2])] += 1
            prev = w
    Pz = {z: pz[z] / sum(pz.values()) for z in ZONES}

    def zsmooth(c):
        n = sum(c.values())
        return {z: (c[z] + kz * Pz[z]) / (n + kz) for z in ZONES}
    zone_word = {w: zsmooth(c) for w, c in zw.items() if wc[w] >= nmin}
    zone_word_all = {w: zsmooth(c) for w, c in zw.items()}
    zone_fl = {k: zsmooth(c) for k, c in zfl.items()}
    u1 = sorted(u1c); u1i = {u: i for i, u in enumerate(u1)}
    u2 = sorted(u2c); u2i = {u: i for i, u in enumerate(u2)}
    P1 = np.array([u1c[u] for u in u1], float); P1 /= P1.sum()
    P2 = np.array([u2c[u] for u in u2], float); P2 /= P2.sum()

    def rsmooth(r, keys, P):
        out = {}
        for k, c in r.items():
            n = sum(c.values())
            v = (np.array([c[u] for u in keys], float) + kappa * P) / (n + kappa)
            out[k] = v / P                       # divided by the first-unit marginal (audit edit 1)
        return out
    common = sorted(w for w, c in wc.items() if c >= COMMON_MIN)
    return {'Pz': Pz, 'zone_word': zone_word, 'zone_word_all': zone_word_all, 'zone_fl': zone_fl,
            'route1': rsmooth(r1, u1, P1), 'route2': rsmooth(r2, u1, P1), 'route3': rsmooth(r3, u2, P2),
            'u1i': u1i, 'u2i': u2i, 'kappa': kappa, 'kz': kz, 'nmin': nmin, 'wc': wc,
            'ph_first': {u: (hfirst[u] + 0.5) / (afirst[u] + 1.0) for u in afirst},
            'ph_last': {u: (hlast[u] + 0.5) / (alast[u] + 1.0) for u in alast}, 'ph_base': n_header / n_all,
            'zone_first': {t: {u: zsmooth(c) for u, c in d.items()} for t, d in zf.items()},
            'zone_last': {t: {u: zsmooth(c) for u, c in d.items()} for t, d in zl.items()},
            'common': common, 'cidx': {w: i for i, w in enumerate(common)}}


def zone_weights(T, w, memo=False):
    if memo:
        return T['zone_word_all'][w]
    if w in T['zone_word']:
        return T['zone_word'][w]
    u = units(w)
    return T['zone_fl'].get((u[0], u[-1]), T['Pz'])


# ================================================================================================ device
def generate(sk, T, rung='R2', stock='L', replace=False, memo=False, header=False, plant=None, lam=0.0, rng=None,
             prohibit=None):
    """One corpus on B's skeleton.
    rung: R0 (stock only) | R1 (+zone) | R2a | R2 | R3 (+routing). stock: 'L' page x line type | 'P' page only.
    plant: None | 'P1' line memory | 'P2' paragraph palette | 'P6' pair prohibition (cells in `prohibit`) |
           'P7' e-run persistence | 'P8' family alternation | 'P10' per-line hapax propensity | 'P11' medial tilt |
           'P12' ok after qok; lam = the plant's strength."""
    rng = np.random.default_rng() if rng is None else rng
    assert rung in ('R0', 'R1', 'R2a', 'R2', 'R3')
    cells = defaultdict(list)
    for li, (f, par) in enumerate(zip(sk['folio'], sk['par_initial'])):
        cells[(f, ('H' if par else 'B') if stock == 'L' else 'A')].append(li)
    hap = {w for w, c in T['wc'].items() if c == 1}
    out = [None] * len(sk['lines'])
    pid, cur, lastf = [], -1, None
    for f, t in zip(sk['folio'], sk['par_initial']):
        if t or f != lastf:
            cur += 1
        pid.append(cur); lastf = f
    pal = {}
    for key, idx in cells.items():
        st = Counter(w for li in idx for w in sk['lines'][li] if w is not None)
        words = list(st)
        cnt = np.array([st[w] for w in words], float)
        U = [units(w) for w in words]
        f1 = np.array([T['u1i'].get(u[0], -1) for u in U])
        f2 = np.array([T['u2i'].get(tuple(u[:2]), -1) for u in U])
        zt = {z: np.array([zone_weights(T, w, memo)[z] for w in words]) for z in ZONES}
        if header:
            ph = np.clip(np.array([T['ph_first'][u[0]] * T['ph_last'][u[-1]] / T['ph_base'] for u in U]), 0, 1)

            def adj(t_, z):
                return np.array([T['zone_first'][t_].get(u[0], T['zone_first']['A'][u[0]])[z] / T['zone_first']['A'][u[0]][z]
                                 * T['zone_last'][t_].get(u[-1], T['zone_last']['A'][u[-1]])[z] / T['zone_last']['A'][u[-1]][z]
                                 for u in U])
            zH = {z: zt[z] * adj('H', z) * ph for z in ZONES}
            zB = {z: zt[z] * adj('B', z) * (1 - ph) for z in ZONES}
        ecls = np.array([erun(w) for w in words])
        fam = np.array([{'q': 1, 'c': 2}.get(family(w), 0) for w in words])
        isok = np.array([w.startswith('ok') for w in words])
        ishap = np.array([w in hap for w in words])
        pref = [_prefix(w) for w in words] if plant == 'P2' else None
        for li in idx:
            ln = sk['lines'][li]
            n = len(ln)
            par = sk['par_initial'][li]
            new, prev, prev_i = [], None, -1
            inline = set()
            if plant == 'P2':
                if pid[li] not in pal:
                    base = Counter(pref)
                    keys = list(base)
                    alpha = lam * np.array([base[k] for k in keys], float) / len(words)
                    pal[pid[li]] = dict(zip(keys, rng.dirichlet(alpha + 1e-9) * len(keys)))
                tilt = np.array([pal[pid[li]].get(pr_, 1.0) for pr_ in pref])
            if plant == 'P10':
                g = rng.gamma(1.0 / lam ** 2, lam ** 2) if lam > 0 else 1.0
            ns = sum(1 for w in ln if w is not None)
            k = 0
            for p, w in enumerate(ln):
                if w is None:
                    new.append(None); prev, prev_i = None, -1
                    continue
                z = zone_of(p, n)
                wgt = cnt.copy()
                if rung != 'R0':
                    wgt = wgt * ((zH if par else zB)[z] if header else zt[z])
                if prev is not None and rung in ('R2a', 'R2', 'R3'):
                    pu = units(prev)
                    if rung == 'R3':
                        pr = T['route3'].get(tuple(pu[-2:]))
                        if pr is not None:
                            wgt = wgt * np.where(f2 >= 0, pr[np.maximum(f2, 0)], 1.0)
                    else:
                        pr = (T['route2'] if rung == 'R2' else T['route1']).get(tuple(pu[-2:]) if rung == 'R2' else pu[-1])
                        if pr is not None:
                            wgt = wgt * np.where(f1 >= 0, pr[np.maximum(f1, 0)], 1.0)
                if plant and lam > 0:
                    if plant == 'P1' and inline:
                        share = np.array([sum(x in inline for x in u) / len(u) for u in U])
                        wgt = wgt * (1 + lam * share)
                    elif plant == 'P2':
                        wgt = wgt * tilt
                    elif plant == 'P6' and prev is not None and prohibit is not None and prev in prohibit:
                        banned = prohibit[prev]
                        wgt = wgt * np.array([0.0 if x in banned else 1.0 for x in words])
                    elif plant == 'P7' and prev_i >= 0:
                        wgt = wgt * (1 + lam * (ecls == ecls[prev_i]))
                    elif plant == 'P8' and prev_i >= 0 and fam[prev_i]:
                        wgt = wgt * (1 + lam * ((fam > 0) & (fam != fam[prev_i])))
                    elif plant == 'P10':
                        wgt = wgt * np.where(ishap, g, 1.0)
                    elif plant == 'P11' and 0 < k < ns - 1 and ns >= 6:
                        q = min(4, int(5 * (k - 1) / max(ns - 2, 1)))
                        wgt = wgt * np.where(ecls == 2, 1 + lam * (q - 2) / 2.0, 1.0)
                    elif plant == 'P12' and prev is not None and prev.startswith('qok'):
                        wgt = wgt * (1 + lam * isok)
                wgt = np.maximum(wgt, 0.0)
                tot = wgt.sum()
                if tot <= 0:
                    wgt = cnt.copy(); tot = wgt.sum()
                i = int(rng.choice(len(words), p=wgt / tot))
                new.append(words[i])
                prev, prev_i = words[i], i
                inline.update(U[i])
                k += 1
                if not replace:
                    cnt[i] -= 1
            out[li] = new
    return out


# ================================================================================================ statistics
def _morph():
    global _MORPH
    if _MORPH is None:
        from scripts.voynich import Morphology
        _MORPH = Morphology()
    return _MORPH


def _prefix(w, cache={}):
    if w not in cache:
        e = _morph().extract(w)
        cache[w] = (e.prefix or e.articulator or '')
    return cache[w]


def _js(p, q):
    keys = set(p) | set(q)
    P = np.array([p.get(k, 0.0) for k in keys]); Q = np.array([q.get(k, 0.0) for k in keys])
    M = 0.5 * (P + Q)

    def kl(a, b):
        m = a > 0
        return float((a[m] * np.log2(a[m] / b[m])).sum())
    return 0.5 * kl(P, M) + 0.5 * kl(Q, M)


def _dist(c):
    t = sum(c.values())
    return {k: v / t for k, v in c.items()} if t else {}


def _classes():
    global _CLS
    if _CLS is None:
        ctm = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', encoding='utf-8'))
        _CLS = {t: int(c) for t, c in ctm['token_to_class'].items()}
    return _CLS


def _mi(pairs):
    N = sum(pairs.values())
    if not N:
        return float('nan')
    ra, rb = Counter(), Counter()
    for (a, b), n in pairs.items():
        ra[a] += n; rb[b] += n
    return float(sum(n / N * np.log2(n * N / (ra[a] * rb[b])) for (a, b), n in pairs.items()))


def _entropy_reduction(lines, folios, rng, unit_level, n_shuf=20):
    def mean_H(ls):
        hs = []
        for ln in ls:
            s = [w for w in ln if w is not None]
            if len(s) < 4:
                continue
            items = [u for w in s for u in units(w)] if unit_level else s
            c = np.array(list(Counter(items).values()), float); p = c / c.sum()
            hs.append(float(-(p * np.log2(p)).sum()))
        return float(np.mean(hs))
    h = mean_H(lines)
    by = defaultdict(list)
    for i, f in enumerate(folios):
        by[f].append(i)
    hs = []
    for _ in range(n_shuf):
        sh = [None] * len(lines)
        for f, idx in by.items():
            tk = [w for i in idx for w in lines[i] if w is not None]
            rng.shuffle(tk)
            it = iter(tk)
            for i in idx:
                sh[i] = [None if w is None else next(it) for w in lines[i]]
        hs.append(mean_H(sh))
    return 100 * (np.mean(hs) - h) / np.mean(hs)


def predictions(lines, sk, c957, T, rng):
    """Definitions in PRE_REGISTRATION.md (v2). Counted: P1u, P2, P7, P8, P10, P11, P12 (+ P6z pair zeros, computed
    at the verdict from the pair counts returned here). Consistency / descriptive: P1t, P3, P4, P5, P6n, P9, X_*."""
    folios, par = sk['folio'], sk['par_initial']
    hap = {w for w, c in T['wc'].items() if c == 1}
    cls = _classes()
    out = {}
    out['P1u_unit_line_homogeneity_pct'] = float(_entropy_reduction(lines, folios, rng, True))
    out['P1t_token_line_homogeneity_pct'] = float(_entropy_reduction(lines, folios, rng, False))
    # P2: mean within-folio between-paragraph PREFIX JSD, body lines only, paragraphs >= 10 body tokens
    pid, cur, lastf = [], -1, None
    for f, t in zip(folios, par):
        if t or f != lastf:
            cur += 1
        pid.append(cur); lastf = f
    pd = defaultdict(Counter)
    for li, ln in enumerate(lines):
        if par[li]:
            continue
        for w in ln:
            if w is not None:
                pd[(folios[li], pid[li])][_prefix(w)] += 1
    byf = defaultdict(list)
    for (f, p), c in pd.items():
        if sum(c.values()) >= 10:
            byf[f].append(_dist(c))
    fol_means = []
    for f, ds in byf.items():
        if len(ds) >= 2:
            fol_means.append(np.mean([_js(ds[i], ds[j]) for i in range(len(ds)) for j in range(i + 1, len(ds))]))
    out['P2_paragraph_prefix_jsd'] = float(np.mean(fol_means)) if fol_means else float('nan')
    # P3, P4, P5 (consistency / line-type contrasts, not counted)
    mH = mB = nH = nB = gH = gO = nHl = nOl = fpH = fpB = tH = tB = 0
    for li, ln in enumerate(lines):
        s = [w for w in ln if w is not None]
        if not s:
            continue
        lastu = units(s[-1])[-1] == 'm'; firstg = units(s[0])[0] in GALLOWS
        fpc = sum(any(u in FP for u in units(w)) for w in s)
        if par[li]:
            nH += 1; mH += lastu; nHl += 1; gH += firstg; tH += len(s); fpH += fpc
        else:
            nB += 1; mB += lastu; nOl += 1; gO += firstg; tB += len(s); fpB += fpc
    out['P3_m_final_header_minus_body'] = mH / max(nH, 1) - mB / max(nB, 1)
    out['P4_gallows_initial_header_minus_other'] = gH / max(nHl, 1) - gO / max(nOl, 1)
    out['P5_fp_share_header_minus_body'] = fpH / max(tH, 1) - fpB / max(tB, 1)
    # pairs: P6n, P7, P8, P12, class-pair MI, common-pair counts
    bad = set(tuple(x) for x in c957)
    p6n = agree = tot7 = alt = tot8 = ok12 = tot12 = 0
    cpairs = Counter()
    cc = Counter()
    for ln in lines:
        seq = [w for w in ln if w is not None]
        prev_c = None
        for w in seq:
            c = cls.get(w)
            if c is not None:
                if prev_c is not None:
                    cc[(prev_c, c)] += 1
                prev_c = c
        for a, b in zip(ln, ln[1:]):
            if a is None or b is None:
                continue
            p6n += (a, b) in bad
            tot7 += 1; agree += erun(a) == erun(b)
            fa, fb = family(a), family(b)
            if fa and fb:
                tot8 += 1; alt += fa != fb
            if a.startswith('qok'):
                if b.startswith('ok'):
                    tot12 += 1; ok12 += 1
                elif b.startswith(('ot', 'ol')):
                    tot12 += 1
            if a in T['cidx'] and b in T['cidx']:
                cpairs[(T['cidx'][a], T['cidx'][b])] += 1
    out['P6n_c957_bigram_count'] = int(p6n)
    out['P7_erun_lag1_agree'] = agree / max(tot7, 1)
    out['P8_qo_chsh_alternation'] = alt / max(tot8, 1)
    out['P12_ok_after_qok_share'] = ok12 / max(tot12, 1) if tot12 else float('nan')
    out['X_class_pair_mi'] = _mi(cc)
    # P9 descriptive
    by = defaultdict(list)
    for i, f in enumerate(folios):
        by[f].append(i)
    p9 = 0.0
    for f, idx in by.items():
        q = np.array([w.startswith('qok') for i in idx for w in lines[i] if w is not None], float)
        if len(q) >= 10:
            p9 = max(p9, float(np.convolve(q, np.ones(10), 'valid').max()))
    out['P9_max_qok_window'] = p9
    # P10: line-length-adjusted within-folio hapax dispersion, body lines only
    num = 0.0; nl = 0; nf = 0
    for f, idx in by.items():
        rows = [(sum(1 for w in lines[i] if w is not None), sum(1 for w in lines[i] if w is not None and w in hap))
                for i in idx if not par[i] and any(w is not None for w in lines[i])]
        if len(rows) < 2:
            continue
        ntot = sum(r[0] for r in rows); htot = sum(r[1] for r in rows)
        if ntot == 0 or htot == 0:
            continue
        pf = htot / ntot
        num += sum((c - n * pf) ** 2 / (n * pf) for n, c in rows)
        nl += len(rows); nf += 1
    out['P10_hapax_dispersion'] = num / (nl - nf) if nl - nf > 0 else float('nan')
    # P11: medial positions only, lines >= 6 tokens, relative medial quintiles
    qall, qe = Counter(), Counter()
    for ln in lines:
        s = [w for w in ln if w is not None]
        L = len(s)
        if L < 6:
            continue
        for k in range(1, L - 1):
            q = min(4, int(5 * (k - 1) / (L - 2)))
            qall[q] += 1
            if erun(s[k]) == 2:
                qe[q] += 1
    out['P11_erun_medial_quintile_jsd'] = float(_js(_dist(qe), _dist(qall)))
    # extras
    c5, seen = Counter(), Counter()
    maxrun = 1
    for ln in lines:
        seg, run = [], 1
        for a, b in zip(ln, ln[1:]):
            if a is not None and b is not None and a == b:
                run += 1; maxrun = max(maxrun, run)
            else:
                run = 1
        for w in ln + [None]:
            if w is None:
                for i in range(len(seg) - 4):
                    c5[tuple(seg[i:i + 5])] += 1
                seg = []
            else:
                seg.append(w)
        key = ' '.join(w for w in ln if w is not None)
        if key:
            seen[key] += 1
    out['X_rpt5'] = int(sum(n for n in c5.values() if n >= 2))
    out['X_duplicate_lines'] = int(sum(n - 1 for n in seen.values() if n > 1))
    out['X_max_identical_run'] = int(maxrun)
    return out, cpairs


COUNTED = ['P1u_unit_line_homogeneity_pct', 'P2_paragraph_prefix_jsd', 'P7_erun_lag1_agree', 'P8_qo_chsh_alternation',
           'P10_hapax_dispersion', 'P11_erun_medial_quintile_jsd', 'P12_ok_after_qok_share']   # + P6z at the verdict
DESCRIPTIVE = ['P1t_token_line_homogeneity_pct', 'P3_m_final_header_minus_body', 'P4_gallows_initial_header_minus_other',
               'P5_fp_share_header_minus_body', 'P6n_c957_bigram_count', 'P9_max_qok_window', 'X_class_pair_mi',
               'X_rpt5', 'X_duplicate_lines', 'X_max_identical_run']
PLANTS = {'P1u_unit_line_homogeneity_pct': ('P1', (0.1, 0.25, 0.5, 1.0, 2.0)),
          'P2_paragraph_prefix_jsd': ('P2', (50.0, 20.0, 10.0, 5.0, 2.0)),       # Dirichlet concentration (smaller = stronger)
          'P6z_pair_zeros': ('P6', (5, 10, 20)),                                     # cells prohibited
          'P7_erun_lag1_agree': ('P7', (0.1, 0.25, 0.5, 1.0, 2.0)),
          'P8_qo_chsh_alternation': ('P8', (0.1, 0.25, 0.5, 1.0, 2.0)),
          'P10_hapax_dispersion': ('P10', (0.1, 0.25, 0.5, 1.0, 2.0)),
          'P11_erun_medial_quintile_jsd': ('P11', (0.1, 0.25, 0.5, 1.0, 2.0)),
          'P12_ok_after_qok_share': ('P12', (0.1, 0.25, 0.5, 1.0, 2.0))}


def fidelity(lines, sk):
    """Generated-vs-input diagnostics: raw MI(previous last two units; next first unit) within lines, and raw
    last-unit -> first-unit MI on the first and second half of each page's lines (depletion diagnostic)."""
    by = defaultdict(list)
    for li, f in enumerate(sk['folio']):
        by[f].append(li)
    half_of = {}
    for f, idx in by.items():
        for j, li in enumerate(idx):
            half_of[li] = 0 if j < len(idx) / 2 else 1
    p2, halves = Counter(), {0: Counter(), 1: Counter()}
    for li, ln in enumerate(lines):
        for a, b in zip(ln, ln[1:]):
            if a is None or b is None:
                continue
            ua, ub = units(a), units(b)
            p2[(tuple(ua[-2:]), ub[0])] += 1
            halves[half_of[li]][(ua[-1], ub[0])] += 1
    return {'mi_route2_raw': _mi(p2), 'mi_edge_first_half_raw': _mi(halves[0]), 'mi_edge_second_half_raw': _mi(halves[1])}


# ================================================================================================ Metropolis sampler
MH_SWEEPS = 10


def generate_mh(sk, T, rung='R2', stock='L', memo=False, header=False, plant=None, lam=0.0, rng=None, prohibit=None,
                sweeps=MH_SWEEPS, init='seq', diag=False):
    """Within-cell Metropolis sampler (the declared fallback, audit edit 5 iii): the cell's tokens are assigned to its
    slots; the target is the product over slots of the zone weight and, for slots with a within-line predecessor, the
    routing weight (and the plant's terms); proposals swap two slots' tokens; composition is exact by construction and
    there is no depletion. Starts from the sequential sampler's output (init 'seq') or a within-cell shuffle ('shuffle');
    `sweeps` sweeps of n_slots proposals each. Returns lines, or (lines, diagnostics) with diag=True."""
    rng = np.random.default_rng() if rng is None else rng
    assert rung in ('R0', 'R1', 'R2a', 'R2', 'R3')
    if rung == 'R0':
        lines = generate(sk, T, 'R0', stock, False, memo, header, None, 0.0, rng, None)
        return (lines, {'acc': 1.0, 'changed': 1.0}) if diag else lines
    if init == 'seq':
        start = generate(sk, T, rung, stock, False, memo, header, plant, lam, rng, prohibit)
    else:
        start = generate(sk, T, 'R0', stock, False, memo, header, None, 0.0, rng, None)
    lines = [list(ln) if ln is not None else None for ln in start]
    cells = defaultdict(list)
    for li, (f, par) in enumerate(zip(sk['folio'], sk['par_initial'])):
        cells[(f, ('H' if par else 'B') if stock == 'L' else 'A')].append(li)
    hap = {w for w, c in T['wc'].items() if c == 1}
    pid, cur, lastf = [], -1, None
    for f, t in zip(sk['folio'], sk['par_initial']):
        if t or f != lastf:
            cur += 1
        pid.append(cur); lastf = f
    route = {'R1': None, 'R2a': T['route1'], 'R2': T['route2'], 'R3': T['route3']}[rung]
    uidx = T['u2i'] if rung == 'R3' else T['u1i']
    n_acc = n_prop = n_changed = n_slots_all = 0
    for key, idx in cells.items():
        slots = [(li, p) for li in idx for p, w in enumerate(sk['lines'][li]) if w is not None]
        n = len(slots)
        if n < 2:
            continue
        tok = [lines[li][p] for li, p in slots]
        init_tok = list(tok)
        slot_of = {sl: i for i, sl in enumerate(slots)}
        zone_s = [zone_of(p, len(sk['lines'][li])) for li, p in slots]
        pred = [slot_of.get((li, p - 1)) if p > 0 and sk['lines'][li][p - 1] is not None else None for li, p in slots]
        succ = [slot_of.get((li, p + 1)) if p + 1 < len(sk['lines'][li]) and sk['lines'][li][p + 1] is not None else None
                for li, p in slots]
        par_s = [sk['par_initial'][li] for li, p in slots]
        cache = {}

        def feats(w):
            if w not in cache:
                u = units(w)
                zw = zone_weights(T, w, memo)
                if header:
                    ph = min(1.0, T['ph_first'][u[0]] * T['ph_last'][u[-1]] / T['ph_base'])
                    zH = {z: zw[z] * T['zone_first']['H'].get(u[0], T['zone_first']['A'][u[0]])[z] / T['zone_first']['A'][u[0]][z]
                          * T['zone_last']['H'].get(u[-1], T['zone_last']['A'][u[-1]])[z] / T['zone_last']['A'][u[-1]][z] * ph
                          for z in ZONES}
                    zB = {z: zw[z] * T['zone_first']['B'].get(u[0], T['zone_first']['A'][u[0]])[z] / T['zone_first']['A'][u[0]][z]
                          * T['zone_last']['B'].get(u[-1], T['zone_last']['A'][u[-1]])[z] / T['zone_last']['A'][u[-1]][z] * (1 - ph)
                          for z in ZONES}
                else:
                    zH = zB = zw
                ukey = tuple(u[:2]) if rung == 'R3' else u[0]
                cache[w] = (zH, zB, tuple(u[-2:]) if rung in ('R2', 'R3') else u[-1], uidx.get(ukey, -1), erun(w),
                            family(w), w.startswith('qok'), w.startswith('ok'), w in hap,
                            _prefix(w) if plant == 'P2' else None, set(u))
            return cache[w]
        pal = {}
        if plant == 'P2':
            base = Counter(_prefix(w) for w in tok)
            keys = list(base)
            alpha = lam * np.array([base[k] for k in keys], float) / max(len(set(tok)), 1)
            for li in idx:
                if pid[li] not in pal:
                    pal[pid[li]] = dict(zip(keys, rng.dirichlet(alpha + 1e-9) * len(keys)))
        gline = {}
        if plant == 'P10':
            for li in idx:
                gline[li] = rng.gamma(1.0 / lam ** 2, lam ** 2) if lam > 0 else 1.0
        line_len = {li: sum(1 for w in sk['lines'][li] if w is not None) for li in idx}
        kpos = {i: sum(1 for q in range(p) if sk['lines'][li][q] is not None) for i, (li, p) in enumerate(slots)}

        def slot_term(i, w):
            zH, zB, e, ui, ec, fam_, isqok, isok, ishap, pref, useq = feats(w)
            t = (zH if par_s[i] else zB)[zone_s[i]]
            if plant and lam > 0:
                li = slots[i][0]
                if plant == 'P2':
                    t *= pal[pid[li]].get(pref, 1.0)
                elif plant == 'P10' and ishap:
                    t *= gline[li]
                elif plant == 'P11':
                    L = line_len[li]; k = kpos[i]
                    if L >= 6 and 0 < k < L - 1 and ec == 2:
                        q = min(4, int(5 * (k - 1) / (L - 2)))
                        t *= max(0.0, 1 + lam * (q - 2) / 2.0)     # clamped, as in the sequential sampler
            return t

        def pair_term(wp, w):
            fp, fw = feats(wp), feats(w)
            t = 1.0
            if route is not None:
                pr = route.get(fp[2])
                if pr is not None and fw[3] >= 0:
                    t *= pr[fw[3]]
            if plant and lam > 0:
                if plant == 'P6' and prohibit is not None and wp in prohibit and w in prohibit[wp]:
                    t = 0.0
                elif plant == 'P7' and fp[4] == fw[4]:
                    t *= 1 + lam
                elif plant == 'P8' and fp[5] and fw[5] and fp[5] != fw[5]:
                    t *= 1 + lam
                elif plant == 'P12' and fp[6] and fw[7]:
                    t *= 1 + lam
            return t

        def line_term(li):
            seen = set(); t = 1.0
            for p, w in enumerate(sk['lines'][li]):
                if w is None:
                    continue
                u = feats(tok[slot_of[(li, p)]])[10]
                if seen:
                    t *= 1 + lam * sum(x in seen for x in u) / len(u)
                seen |= u
            return t

        def local(i, w_i, j, w_j):
            cur = {i: w_i, j: w_j}

            def at(k):
                return cur.get(k, tok[k])
            t = 1.0
            touched = set()
            for k in (i, j):
                t *= slot_term(k, at(k))
                if pred[k] is not None:
                    touched.add((pred[k], k))
                if succ[k] is not None:
                    touched.add((k, succ[k]))
            for a_, b_ in touched:
                t *= pair_term(at(a_), at(b_))
            return t
        n_slots_all += n
        for sweep in range(sweeps):
            for _ in range(n):
                i, j = int(rng.integers(n)), int(rng.integers(n))
                if i == j or tok[i] == tok[j]:
                    continue
                n_prop += 1
                before = local(i, tok[i], j, tok[j]); after = local(i, tok[j], j, tok[i])
                if plant == 'P1' and lam > 0:
                    li, lj = slots[i][0], slots[j][0]
                    lb = line_term(li) * (line_term(lj) if lj != li else 1.0)
                    tok[i], tok[j] = tok[j], tok[i]
                    la = line_term(li) * (line_term(lj) if lj != li else 1.0)
                    tok[i], tok[j] = tok[j], tok[i]
                    before *= lb; after *= la
                if after > 0 and (before <= 0 or after >= before or rng.random() < after / before):
                    tok[i], tok[j] = tok[j], tok[i]
                    n_acc += 1
        n_changed += sum(1 for x, y in zip(tok, init_tok) if x != y)
        for (li, p), w in zip(slots, tok):
            lines[li][p] = w
    d = {'acc': n_acc / max(n_prop, 1), 'changed': n_changed / max(n_slots_all, 1)}
    return (lines, d) if diag else lines


def load_c957():
    return json.load(open(OUT / 'c957_bigrams.json', encoding='utf-8'))['bigrams']
