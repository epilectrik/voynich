"""PHASE_779 -- The minimal device: do page vocabulary + line-position vocabulary + two-unit junction routing, the
measured specification of Currier B, reproduce B's other registered regularities without being given them?

Device MIN-D (a sampler of the rules, not a claim about hands):
  PAGE STOCK  each page's own tokens (its multiset of certain P-text tokens); words are drawn from the page's stock
              without replacement, so each generated page has exactly B's composition for that page.
  ZONE        each candidate word is weighted by P_B(zone | word), zone = line-initial / medial / line-final,
              estimated corpus-wide (the specification's line-position vocabulary, D6 / C956).
  ROUTING     each candidate word is weighted by P_B(first glyph unit | previous word's last two glyph units),
              estimated corpus-wide (the two-unit ending routing, C2082; the junction coupling C1212/C1563).
  No paragraph state, no line memory, no interior rule, no repeat rule.
Ladder (rungs): R0 page stock only (= within-page shuffle); R1 + zone; R2a + one-unit routing; R2 + two-unit routing
(previous last two units -> next first unit); R3 + two-unit routing to the next word's first two units.
Variant: R2w draws with replacement from the page's frequencies (composition noise). Plant (positive control for the
paragraph predictions): R2+H, where paragraph-first lines weight each word by a glyph-level header propensity
(P_B(header | first unit) x P_B(header | last unit) / P_B(header), clipped to 1) and its header-line zone weights,
body lines by the complement and the body-line zone weights (a header rule the device is otherwise denied).

Panel: PHASE_757's D2-D6 (panel_stats.py). Predictions: statistics of registered regularities the device was not
given (see PRE_REGISTRATION.md); each is computed identically on B and on every member.
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
import grille778 as G8  # noqa: E402  (skeleton with sections and paragraph-first flags; units())

GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
GALLOWS = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
FP = {'p', 'f', 'cph', 'cfh'}
ZONES = ('I', 'M', 'F')
SMOOTH = 0.5
_MORPH = None


def units(w):
    return GLYPH_RE.findall(w)


def skeleton():
    return G8.skeleton()


# ================================================================================================ specification
def zone_of(p, n):
    return 'I' if p == 0 else ('F' if p == n - 1 else 'M')


def spec_tables(sk):
    """Corpus-wide tables of the specification: P(zone | word) (3 zones, smoothed) and P(first unit | previous last
    two units) and P(first unit | previous last unit) (smoothed), plus the paragraph-first / body zone tables for the
    plant. All are composition or adjacent-pair statistics of B (declared exposure)."""
    zc = defaultdict(lambda: Counter())
    zh = {'H': defaultdict(Counter), 'B': defaultdict(Counter)}
    hcount, wcount = Counter(), Counter()
    hfirst, hlast, afirst, alast = Counter(), Counter(), Counter(), Counter()
    n_header = n_all = 0
    r2, r1, r3 = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    first_all, first2_all = Counter(), Counter()
    for ln, par in zip(sk['lines'], sk['par_initial']):
        n = len(ln)
        prev = None
        for p, w in enumerate(ln):
            if w is None:
                prev = None
                continue
            z = zone_of(p, n)
            zc[w][z] += 1
            zh['H' if par else 'B'][w][z] += 1
            wcount[w] += 1
            hcount[w] += bool(par)
            afirst[u[0]] += 1
            alast[u[-1]] += 1
            n_all += 1
            if par:
                hfirst[u[0]] += 1
                hlast[u[-1]] += 1
                n_header += 1
            u = units(w)
            first_all[u[0]] += 1
            first2_all[tuple(u[:2])] += 1
            if prev is not None:
                pu = units(prev)
                r2[tuple(pu[-2:])][u[0]] += 1
                r1[pu[-1]][u[0]] += 1
                r3[tuple(pu[-2:])][tuple(u[:2])] += 1
            prev = w
    firsts = sorted(first_all)
    fidx = {u: i for i, u in enumerate(firsts)}
    base = np.array([first_all[u] for u in firsts], float)
    base /= base.sum()

    def cond_table(r, keys, bse):
        out = {}
        for k, c in r.items():
            v = np.array([c[u] for u in keys], float) + SMOOTH * bse * len(keys)
            out[k] = v / v.sum()
        return out
    firsts2 = sorted(first2_all)
    f2idx = {u: i for i, u in enumerate(firsts2)}
    base2 = np.array([first2_all[u] for u in firsts2], float)
    base2 /= base2.sum()

    def zone_table(zc_):
        return {w: {z: (c[z] + SMOOTH) / (sum(c.values()) + 3 * SMOOTH) for z in ZONES} for w, c in zc_.items()}
    return {'zone': zone_table(zc), 'zone_H': zone_table(zh['H']), 'zone_B': zone_table(zh['B']),
            'route2': cond_table(r2, firsts, base), 'route1': cond_table(r1, firsts, base),
            'route3': cond_table(r3, firsts2, base2), 'firsts': firsts, 'fidx': fidx, 'base': base,
            'firsts2': firsts2, 'f2idx': f2idx, 'base2': base2,
            'p_header': {w: (hcount[w] + SMOOTH) / (wcount[w] + 2 * SMOOTH) for w in wcount},
            'ph_first': {u: (hfirst[u] + SMOOTH) / (afirst[u] + 2 * SMOOTH) for u in afirst},
            'ph_last': {u: (hlast[u] + SMOOTH) / (alast[u] + 2 * SMOOTH) for u in alast},
            'ph_base': n_header / n_all}


# ================================================================================================ device
def generate(sk, T, rung='R2', replace=False, plant=None, rng=None):
    """One corpus on B's skeleton. rung: R0 (page stock only), R1 (+ zone), R2a (+ one-unit routing), R2 (+ two-unit
    routing). replace: draw with replacement from the page's frequencies. plant 'H': header-aware zone tables."""
    rng = np.random.default_rng() if rng is None else rng
    assert rung in ('R0', 'R1', 'R2a', 'R2', 'R3')
    pages = defaultdict(list)
    for li, f in enumerate(sk['folio']):
        pages[f].append(li)
    out = [None] * len(sk['lines'])
    for f, idx in pages.items():
        stock = Counter(w for li in idx for w in sk['lines'][li] if w is not None)
        words = list(stock)
        cnt = np.array([stock[w] for w in words], float)
        firsts_w = np.array([T['fidx'][units(w)[0]] for w in words])
        firsts2_w = np.array([T['f2idx'][tuple(units(w)[:2])] for w in words])
        zw = {z: np.array([T['zone'][w][z] for w in words]) for z in ZONES}
        if plant == 'H':
            # glyph-level header propensity: P(header | first unit) x P(header | last unit) / P(header), so that rare
            # words inherit their glyphs' conventions (m-final, gallows-initial, f/p)
            ph = np.array([T['ph_first'][units(w)[0]] * T['ph_last'][units(w)[-1]] / T['ph_base'] for w in words])
            ph = np.clip(ph, 0.0, 1.0)
            zH = {z: np.array([T['zone_H'].get(w, T['zone'][w])[z] for w in words]) * ph for z in ZONES}
            zB = {z: np.array([T['zone_B'].get(w, T['zone'][w])[z] for w in words]) * (1 - ph) for z in ZONES}
        for li in idx:
            ln = sk['lines'][li]
            n = len(ln)
            new = []
            prev = None
            for p, w in enumerate(ln):
                if w is None:
                    new.append(None)
                    prev = None
                    continue
                z = zone_of(p, n)
                wgt = cnt.copy()
                if rung != 'R0':
                    zt = (zH if (plant == 'H' and sk['par_initial'][li]) else zB if plant == 'H' else zw)[z]
                    wgt = wgt * zt
                if prev is not None and rung in ('R2', 'R2a', 'R3'):
                    pu = units(prev)
                    if rung == 'R3':
                        pr = T['route3'].get(tuple(pu[-2:]), T['base2'])
                        wgt = wgt * pr[firsts2_w]
                    else:
                        key = tuple(pu[-2:]) if rung == 'R2' else pu[-1]
                        tab = T['route2'] if rung == 'R2' else T['route1']
                        pr = tab.get(key, T['base'])
                        wgt = wgt * pr[firsts_w]
                tot = wgt.sum()
                if tot <= 0:
                    wgt = cnt.copy()
                    tot = wgt.sum()
                i = int(rng.choice(len(words), p=wgt / tot))
                new.append(words[i])
                prev = words[i]
                if not replace:
                    cnt[i] -= 1
            out[li] = new
        if not replace:
            assert cnt.sum() == 0
    return out


# ================================================================================================ predictions
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


def predictions(lines, sk, c957, rng, n_shuf=20):
    """Registered-regularity statistics, computed identically on B and on members (definitions in the pre-registration).
    P1 line homogeneity (C1214 relative): mean within-line token entropy, percent reduction vs within-page shuffles.
    P2 paragraph PREFIX composition (C1811 relative): mean within-folio JSD between paragraphs' PREFIX distributions
       divided by mean between-folio JSD of folio PREFIX distributions.
    P3 line-final m by line type (C1435 relative): share of m-final tokens among line-final tokens, paragraph-first
       lines minus body lines.
    P4 paragraph-initial gallows: share of gallows-initial first words, paragraph-first lines minus other lines.
    P5 top-line f/p: share of tokens containing p/f/cph/cfh, paragraph-first lines minus body lines.
    P6 forbidden token bigrams (C957): total count of the registered zero-count forward bigrams.
    P7 e-run lag-1 agreement: share of adjacent pairs whose e-run classes (0 / 1 / 2+) agree.
    P8 qo / ch-sh alternation (C549 relative): among adjacent pairs where both words start with qo or with ch/sh, the
       share that alternate.
    P9 max qok count in any 10-token window of a folio.
    P10 hapax dispersion: variance-to-mean ratio of per-line counts of corpus-hapax tokens.
    P11 e-run position gradient (C1671 relative): JSD between the five line-quintile distributions of tokens with an
        e-run of 2+ and the quintile distribution of all tokens.
    Also: repeated within-line 5-windows (C2091; B 0), duplicate lines (B 0), max identical run (B 4)."""
    folios = sk['folio']
    par = sk['par_initial']
    toks = [w for ln in lines for w in ln if w is not None]
    # P1
    def mean_H(ls):
        hs = []
        for ln in ls:
            s = [w for w in ln if w is not None]
            if len(s) < 4:
                continue
            c = np.array(list(Counter(s).values()), float); p = c / c.sum()
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
    p1 = 100 * (np.mean(hs) - h) / np.mean(hs)
    # P2
    pid, cur, lastf = [], -1, None
    for f, t in zip(folios, par):
        if t or f != lastf:
            cur += 1
        pid.append(cur); lastf = f
    pdist, fdist = defaultdict(Counter), defaultdict(Counter)
    for li, ln in enumerate(lines):
        for w in ln:
            if w is None:
                continue
            pr = _prefix(w)
            pdist[(folios[li], pid[li])][pr] += 1
            fdist[folios[li]][pr] += 1
    within = []
    byf = defaultdict(list)
    for (f, p), c in pdist.items():
        if sum(c.values()) >= 10:
            byf[f].append(_dist(c))
    for f, ds in byf.items():
        for i in range(len(ds)):
            for j in range(i + 1, len(ds)):
                within.append(_js(ds[i], ds[j]))
    fl = [_dist(c) for c in fdist.values()]
    between = [_js(fl[i], fl[j]) for i in range(len(fl)) for j in range(i + 1, len(fl))]
    p2 = float(np.mean(within) / np.mean(between)) if within and between else float('nan')
    # P3, P4, P5
    mH = mB = nH = nB = 0
    gH = gO = nHl = nOl = 0
    fpH = fpB = tH = tB = 0
    for li, ln in enumerate(lines):
        s = [w for w in ln if w is not None]
        if not s:
            continue
        last = s[-1]; first = s[0]
        if par[li]:
            nH += 1; mH += units(last)[-1] == 'm'
            nHl += 1; gH += units(first)[0] in GALLOWS
            tH += len(s); fpH += sum(any(u in FP for u in units(w)) for w in s)
        else:
            nB += 1; mB += units(last)[-1] == 'm'
            nOl += 1; gO += units(first)[0] in GALLOWS
            tB += len(s); fpB += sum(any(u in FP for u in units(w)) for w in s)
    p3 = mH / max(nH, 1) - mB / max(nB, 1)
    p4 = gH / max(nHl, 1) - gO / max(nOl, 1)
    p5 = fpH / max(tH, 1) - fpB / max(tB, 1)
    # P6, P7, P8
    bad = set(tuple(x) for x in c957)
    p6 = 0; agree = tot7 = 0; alt = tot8 = 0
    for ln in lines:
        for a, b in zip(ln, ln[1:]):
            if a is None or b is None:
                continue
            p6 += (a, b) in bad
            ea = min(max((len(m) for m in re.findall(r'e+', a)), default=0), 2)
            eb = min(max((len(m) for m in re.findall(r'e+', b)), default=0), 2)
            tot7 += 1; agree += ea == eb
            ca = 'q' if a.startswith('qo') else ('c' if a.startswith(('ch', 'sh')) else None)
            cb = 'q' if b.startswith('qo') else ('c' if b.startswith(('ch', 'sh')) else None)
            if ca and cb:
                tot8 += 1; alt += ca != cb
    p7 = agree / max(tot7, 1); p8 = alt / max(tot8, 1)
    # P9
    p9 = 0
    for f, idx in by.items():
        q = np.array([w.startswith('qok') for i in idx for w in lines[i] if w is not None], float)
        if len(q) >= 10:
            p9 = max(p9, float(np.convolve(q, np.ones(10), 'valid').max()))
    # P10
    freq = Counter(toks)
    hl = [sum(1 for w in ln if w is not None and freq[w] == 1) for ln in lines if any(w is not None for w in ln)]
    p10 = float(np.var(hl, ddof=1) / np.mean(hl)) if np.mean(hl) > 0 else float('nan')
    # P11
    qall, qe = Counter(), Counter()
    for ln in lines:
        s = [w for w in ln if w is not None]
        L = len(s)
        for p, w in enumerate(s):
            qn = min(4, int(5 * p / max(L, 1)))
            qall[qn] += 1
            if max((len(m) for m in re.findall(r'e+', w)), default=0) >= 2:
                qe[qn] += 1
    p11 = _js(_dist(qe), _dist(qall))
    # extras
    c5 = Counter()
    seen = Counter()
    maxrun = 1
    for ln in lines:
        seg = []
        run = 1
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
    rpt5 = int(sum(n for n in c5.values() if n >= 2)); dup = int(sum(n - 1 for n in seen.values() if n > 1))
    return {'P1_line_homogeneity_pct': float(p1), 'P2_paragraph_prefix_jsd_ratio': p2, 'P3_m_final_header_minus_body': float(p3),
            'P4_gallows_initial_header_minus_other': float(p4), 'P5_fp_share_header_minus_body': float(p5),
            'P6_c957_bigram_count': int(p6), 'P7_erun_lag1_agree': float(p7), 'P8_qo_chsh_alternation': float(p8),
            'P9_max_qok_window': float(p9), 'P10_hapax_dispersion': float(p10), 'P11_erun_quintile_jsd': float(p11),
            'X_rpt5': rpt5, 'X_duplicate_lines': dup, 'X_max_identical_run': int(maxrun)}


PRED_KEYS = ['P1_line_homogeneity_pct', 'P2_paragraph_prefix_jsd_ratio', 'P3_m_final_header_minus_body',
             'P4_gallows_initial_header_minus_other', 'P5_fp_share_header_minus_body', 'P6_c957_bigram_count',
             'P7_erun_lag1_agree', 'P8_qo_chsh_alternation', 'P9_max_qok_window', 'P10_hapax_dispersion',
             'P11_erun_quintile_jsd']
EXTRA_KEYS = ['X_rpt5', 'X_duplicate_lines', 'X_max_identical_run']


def load_c957():
    return json.load(open(OUT / 'c957_bigrams.json', encoding='utf-8'))['bigrams']
