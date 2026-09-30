#!/usr/bin/env python3
"""PHASE_771 shared statistics (see ../PRE_REGISTRATION.md; v2 after the lean-expert lock audit).

Arm L: mixture weights of three text references for the glyph unit after a label's initial 'o', fitted by grouped EM
       over label length strata with length-matched references (a label o-word of L units is compared with qo-words
       of L+1 units, o-words of L units and words of L-1 units).
Arm E: edge index of words next to a drawing break, from cross-fitted first/last-glyph edge models; paragraph-first
       line starts and paragraph-last line ends are excluded from the edge classes (a break word can never be one).
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zl771 as Z  # noqa: E402

CATS = ['k', 't', 'l', 'r', 'd', 'a', 'e', 'o', 'y', 's', 'ch', 'sh', 'pf', 'bench', 'minim', 'q', 'other']
CIDX = {c: i for i, c in enumerate(CATS)}
REFS = ('qo', 'o', 'init')
LSTRATA = (2, 3, 4, 5, 6, 7)                  # label length in glyph units; 7 = 7 or more
FINE = [[L] for L in LSTRATA]                 # primary grouping: one group per stratum
COARSE = [[2, 3], [4, 5], [6, 7]]             # s7 grouping (small AZC reference corpus)
IDX_CAP = 8
MIN_UNIT = 20
MIN_REF = 10
L_PURE = 2 / 3


def cat(u):
    if u in ('k', 't', 'l', 'r', 'd', 'a', 'e', 'o', 'y', 's', 'ch', 'sh', 'q'):
        return u
    if u in ('p', 'f'):
        return 'pf'
    if u in ('cth', 'ckh', 'cph', 'cfh'):
        return 'bench'
    if u.startswith('i'):
        return 'minim'
    return 'other'


def lstratum(n_units):
    return min(n_units, 7)


# ------------------------------------------------------------------------------------------------------------ text
def words_of(rec, merge_uncertain=False):
    """Word list of a record per segment; with merge_uncertain, words joined across ',' within a segment."""
    out = []
    for seg in rec['segments']:
        ws = []
        for w, sep in seg:
            if merge_uncertain and sep == ',' and ws:
                ws[-1] = ws[-1] + w
            else:
                ws.append(w)
        out.append(ws)
    return out


def text_lines(recs, merge_uncertain=False, kinds=('P',)):
    """Text lines of the given locus kinds: dict(folio, lang, section, kind, par_start, par_end, segs=[[words]])."""
    out = []
    for r in recs:
        if r['kind'][:1] in kinds:
            out.append({'folio': r['folio'], 'lang': r['lang'], 'section': r['section'], 'kind': r['kind'],
                        'par_start': r['par_start'], 'par_end': r['par_end'], 'segs': words_of(r, merge_uncertain)})
    return out


# ---------------------------------------------------------------------------------------------------------- Arm L
def references_by_length(lines, lang=None, line_initial_only=False, exclude_par_first=False, type_weighted=False,
                         init_exclude_oq=False):
    """Per label-length stratum L: counts of the unit after 'qo' in qo-words of L+1 units, after 'o' in o-words of
    L units, and of the first unit of words of L-1 units (7 = 7 or more on the label side)."""
    cnt = {L: {k: np.zeros(len(CATS)) for k in REFS} for L in LSTRATA}
    seen = set()
    for ln in lines:
        if lang is not None and ln['lang'] != lang:
            continue
        if exclude_par_first and ln['par_start']:
            continue
        flat = [w for s in ln['segs'] for w in s]
        for i, w in enumerate(flat):
            if line_initial_only and i > 0:
                break
            if not Z.readable(w):
                continue
            if type_weighted:
                if w in seen:
                    continue
                seen.add(w)
            u = Z.units(w)
            n = len(u)
            if not (init_exclude_oq and u[0] in ('o', 'q')) and n + 1 >= 2:
                cnt[lstratum(n + 1)]['init'][CIDX[cat(u[0])]] += 1
            if w.startswith('qo') and n >= 3:
                cnt[lstratum(n - 1)]['qo'][CIDX[cat(u[2])]] += 1
            elif u[0] == 'o' and n >= 2:
                cnt[lstratum(n)]['o'][CIDX[cat(u[1])]] += 1
    return cnt


def comps_grouped(cnt, groups=FINE, smooth=0.5):
    """G x 3 x cats component matrix; each group's references pool the counts of its member strata."""
    out = []
    for g in groups:
        rows = []
        for k in REFS:
            v = sum(cnt[L][k] for L in g) + smooth
            rows.append(v / v.sum())
        out.append(np.vstack(rows))
    return np.stack(out)


def ref_sizes(cnt, groups=FINE):
    return {'+'.join(map(str, g)): {k: int(sum(cnt[L][k].sum() for L in g)) for k in REFS} for g in groups}


def label_o_items(recs, merge_uncertain=False, h_track=False):
    """(folio, lang, section, kind, stratum, category of the unit after the initial o) for readable o-initial label
    words of at least 2 units."""
    out = []
    if h_track:
        import csv
        H = Z.ROOT / 'data/transcriptions/interlinear_full_words.txt'
        with open(H, encoding='utf-8') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                r = {k: (v.strip('"') if v else '') for k, v in r.items()}
                if r['transcriber'] != 'H' or not r['placement'].startswith('L'):
                    continue
                w = r['word'].strip()
                if Z.readable(w) and w.startswith('o') and not w.startswith('qo') and len(Z.units(w)) >= 2:
                    u = Z.units(w)
                    out.append((r['folio'], r['language'], r['section'], 'H', lstratum(len(u)), cat(u[1])))
        return out
    for r in recs:
        if not r['kind'].startswith('L'):
            continue
        for ws in words_of(r, merge_uncertain):
            for w in ws:
                if Z.readable(w) and w.startswith('o') and not w.startswith('qo') and len(Z.units(w)) >= 2:
                    u = Z.units(w)
                    out.append((r['folio'], r['lang'], r['section'], r['kind'], lstratum(len(u)), cat(u[1])))
    return out


def label_o_word_strings(recs, merge_uncertain=False):
    """(folio, lang, section, word) for readable o-initial label words (descriptive stem-family counts)."""
    out = []
    for r in recs:
        if not r['kind'].startswith('L'):
            continue
        for ws in words_of(r, merge_uncertain):
            for w in ws:
                if Z.readable(w) and w.startswith('o') and not w.startswith('qo') and len(Z.units(w)) >= 2:
                    out.append((r['folio'], r['lang'], r['section'], w))
    return out


def label_system(section):
    if section in ('Z', 'C', 'A'):
        return 'astro_zodiac_cosmo'
    if section in ('P', 'H'):
        return 'pharma_herbal'
    if section == 'B':
        return 'bio'
    return 'other'


def group_index(groups):
    return {L: gi for gi, g in enumerate(groups) for L in g}


def grouped_counts(items, groups=FINE):
    """items with folio at [0], stratum at [-2], category at [-1] -> (folios, C: F x G x cats)."""
    gi = group_index(groups)
    fols = sorted({it[0] for it in items})
    fi = {f: i for i, f in enumerate(fols)}
    C = np.zeros((len(fols), len(groups), len(CATS)))
    for it in items:
        C[fi[it[0]], gi[it[-2]], CIDX[it[-1]]] += 1
    return fols, C


def em_grouped_batch(C, comps_g, iters=500, tol=1e-9):
    """Grouped EM: counts C (B x G x cats) with group-specific components comps_g (G x K x cats) -> weights (B x K)."""
    C = np.asarray(C, float)
    N = C.sum((1, 2))[:, None]
    W = np.full((C.shape[0], comps_g.shape[1]), 1.0 / comps_g.shape[1])
    for _ in range(iters):
        mix = np.einsum('bk,gkc->bgc', W, comps_g)
        acc = np.einsum('gkc,bgc->bk', comps_g, C / mix)
        new = W * acc / N
        if np.max(np.abs(new - W)) < tol:
            return new
        W = new
    return W


def grouped_fit(C, comps_g):
    return em_grouped_batch(C.sum(0)[None], comps_g)[0]


def grouped_boot(C, comps_g, rng, B):
    """Folio-cluster bootstrap of the grouped mixture weights: B x K."""
    nf = C.shape[0]
    idx = rng.integers(0, nf, size=(B, nf))
    W = np.zeros((B, nf))
    np.add.at(W, (np.repeat(np.arange(B), nf), idx.ravel()), 1.0)
    return em_grouped_batch(np.tensordot(W, C, axes=(1, 0)), comps_g)


def g_stat(counts, probs):
    m = counts > 0
    exp = counts.sum() * probs
    return 2.0 * float(np.sum(counts[m] * np.log(counts[m] / exp[m])))


def grouped_g(Ctot, comps_g, w):
    return sum(g_stat(Ctot[g], w @ comps_g[g]) for g in range(Ctot.shape[0]) if Ctot[g].sum() > 0)


def simulate_grouped(nfg, comps_g, weights, alpha, rng, R):
    """R clustered data sets: each (folio, group) cell draws p ~ Dir(alpha * w@comps_g[g]) and counts ~ Mult(n, p).
    Returns R x G x cats totals (summed over folios) and, if R == 1, also the per-folio array."""
    F, G = nfg.shape
    q = np.einsum('k,gkc->gc', np.asarray(weights, float), comps_g)
    tot = np.zeros((R, G, len(CATS)))
    per = np.zeros((F, G, len(CATS))) if R == 1 else None
    for f in range(F):
        for g in range(G):
            n = int(nfg[f, g])
            if n == 0:
                continue
            x = rng.multinomial(n, rng.dirichlet(alpha * q[g], size=R))
            tot[:, g, :] += x
            if per is not None:
                per[f, g] = x[0]
    return tot, per


def grouped_fit_check_p(C, comps_g, alpha, rng, R):
    """Parametric bootstrap p of the grouped G statistic against the fitted mixture, with folio clustering at alpha."""
    Ctot = C.sum(0)
    w = grouped_fit(C, comps_g)
    g0 = grouped_g(Ctot, comps_g, w)
    sims, _ = simulate_grouped(C.sum(2), comps_g, w, alpha, rng, R)
    ws = em_grouped_batch(sims, comps_g)
    gs = np.array([grouped_g(sims[i], comps_g, ws[i]) for i in range(R)])
    return float((1 + np.sum(gs >= g0)) / (R + 1))


def dirichlet_concentration(mat):
    """Method-of-moments Dirichlet-multinomial concentration from a folios x categories count matrix."""
    n = mat.sum(1)
    keep = n >= 5
    mat, n = mat[keep], n[keep]
    p = mat.sum(0) / mat.sum()
    num, den = 0.0, 0.0
    for j in range(mat.shape[1]):
        if p[j] <= 0 or p[j] >= 1:
            continue
        x = mat[:, j] / n
        num += np.sum(n * (x - p[j]) ** 2)
        den += (len(n) - 1) * p[j] * (1 - p[j])
    phi = max(num / den, 1.0 + 1e-6)                      # variance inflation = 1 + (n-1)/(alpha+1) on average
    nbar = (n.sum() - np.sum(n ** 2) / n.sum()) / (len(n) - 1)
    alpha = max((nbar - phi) / (phi - 1.0), 0.5)
    return float(alpha), float(phi)


def dirichlet_concentration_grouped(C):
    """Cell-level concentration for a folio x group x cats array: overdispersion is measured within each group
    (cells of one group share that group's expected distribution) and pooled across groups."""
    num, den, ns = 0.0, 0.0, []
    for g in range(C.shape[1]):
        mat = C[:, g, :]
        n = mat.sum(1)
        keep = n >= 5
        if keep.sum() < 2:
            continue
        mat, n = mat[keep], n[keep]
        p = mat.sum(0) / mat.sum()
        for j in range(mat.shape[1]):
            if p[j] <= 0 or p[j] >= 1:
                continue
            x = mat[:, j] / n
            num += np.sum(n * (x - p[j]) ** 2)
            den += (len(n) - 1) * p[j] * (1 - p[j])
        ns.append(n)
    if den == 0:
        return float('inf')
    phi = max(num / den, 1.0 + 1e-6)
    n = np.concatenate(ns)
    nbar = (n.sum() - np.sum(n ** 2) / n.sum()) / (len(n) - 1)
    return float(max((nbar - phi) / (phi - 1.0), 0.5))


def label_alpha(C):
    """Conservative label concentration: the smaller of the cell-level (within-group) and the folio-pooled estimate."""
    return min(dirichlet_concentration_grouped(C), dirichlet_concentration(C.sum(1))[0])


def text_folio_matrix(lines, which):
    by = defaultdict(lambda: np.zeros(len(CATS)))
    for ln in lines:
        for w in (w for s in ln['segs'] for w in s):
            if not Z.readable(w):
                continue
            u = Z.units(w)
            if which == 'o' and u[0] == 'o' and len(u) > 1 and not w.startswith('qo'):
                by[ln['folio']][CIDX[cat(u[1])]] += 1
            elif which == 'qo' and w.startswith('qo') and len(u) > 2:
                by[ln['folio']][CIDX[cat(u[2])]] += 1
            elif which == 'init':
                by[ln['folio']][CIDX[cat(u[0])]] += 1
    return np.vstack(list(by.values()))


def label_call(w_lo):
    for k, name in zip(range(3), ('o = qo without q', 'ordinary o-words', 'o added to a word')):
        if w_lo[k] >= L_PURE:
            return name
    return 'MIXED / UNRESOLVED'


def power_grouped(nfg, comps_g, alpha, rng, nsim, B, truths):
    """Correct-call (or call-distribution) rates of the grouped rule under clustered draws."""
    out = {}
    for tname, tw in truths.items():
        calls = Counter()
        for _ in range(nsim):
            _, per = simulate_grouped(nfg, comps_g, tw, alpha, rng, 1)
            lo = np.quantile(grouped_boot(per, comps_g, rng, B), 0.025, axis=0)
            calls[label_call(lo)] += 1
        out[tname] = {k: round(v / nsim, 3) for k, v in calls.items()}
    return out


# ---------------------------------------------------------------------------------------------------------- Arm E
def edge_tables(lines):
    """Unbroken-line word table and break list (Currier A and B paragraph text).
    words: dict(folio, lang, section, i_start, i_end, first, last, word, par_first_line, par_last_line) for unbroken
           lines of >= 3 words; breaks: dict(folio, lang, section, post, pre, post_i_start, post_is_last, pre_i_end,
           pre_is_first, n_breaks_line, n_line, par_first_line, par_last_line)."""
    words, breaks = [], []
    for ln in lines:
        if ln['lang'] not in ('A', 'B'):
            continue
        segs = ln['segs']
        flat = [w for s in segs for w in s]
        n = len(flat)
        if len(segs) == 1:
            if n < 3:
                continue
            for i, w in enumerate(flat):
                if Z.readable(w):
                    u = Z.units(w)
                    words.append({'folio': ln['folio'], 'lang': ln['lang'], 'section': ln['section'],
                                  'i_start': i, 'i_end': n - 1 - i, 'first': u[0], 'last': u[-1], 'word': w,
                                  'par_first_line': ln['par_start'], 'par_last_line': ln['par_end']})
            continue
        before = 0
        for j in range(len(segs) - 1):
            before += len(segs[j])
            left, right = segs[j], segs[j + 1]
            if not left or not right:
                continue
            pre, post = left[-1], right[0]
            if not (Z.readable(pre) and Z.readable(post)):
                continue
            breaks.append({'folio': ln['folio'], 'lang': ln['lang'], 'section': ln['section'], 'post': post, 'pre': pre,
                           'post_i_start': before, 'post_is_last': before == n - 1,
                           'pre_i_end': n - before, 'pre_is_first': before - 1 == 0,
                           'n_breaks_line': len(segs) - 1, 'n_line': n,
                           'par_first_line': ln['par_start'], 'par_last_line': ln['par_end']})
    return words, breaks


def _pos(i, n, match):
    """Position class: token index capped at IDX_CAP ('index'), or fifth of the line ('rel')."""
    return min(i, IDX_CAP) if match == 'index' else min(int(5 * i / n), 4)


def _word_keys(w, side, match='index'):
    """(mid key or None, is_edge) for an unbroken-line reference word; (None, None) = excluded (a paragraph-first
    line start on the start side, a paragraph-last line end on the end side)."""
    n = w['i_start'] + w['i_end'] + 1
    if side == 'start':
        if w['i_start'] == 0:
            return (None, None) if w['par_first_line'] else (None, True)
        return (_pos(w['i_start'], n, match), w['i_end'] == 0), False
    if w['i_end'] == 0:
        return (None, None) if w['par_last_line'] else (None, True)
    return (_pos(w['i_end'], n, match), w['i_start'] == 0), False


def break_key(b, side, match='index'):
    if side == 'start':
        return (_pos(b['post_i_start'], b['n_line'], match), bool(b['post_is_last']))
    return (_pos(b['pre_i_end'], b['n_line'], match), bool(b['pre_is_first']))


def break_unit(b, side):
    return Z.units(b['post'])[0] if side == 'start' else Z.units(b['pre'])[-1]


def fit_edge_model(words, lang, side):
    """Unit-level LLR (continuation-line edge vs strictly interior word), rare units pooled."""
    key_u = 'first' if side == 'start' else 'last'
    edge, mid = Counter(), Counter()
    for w in words:
        if w['lang'] != lang:
            continue
        _, is_edge = _word_keys(w, side)
        if is_edge is None:
            continue
        if is_edge:
            edge[w[key_u]] += 1
        elif w['i_start'] > 0 and w['i_end'] > 0:
            mid[w[key_u]] += 1
    tot = edge + mid
    keep = {u for u, c in tot.items() if c >= MIN_UNIT}
    pool = lambda c: Counter({(u if u in keep else '_other'): v for u, v in c.items()})
    e, m = pool(edge), pool(mid)
    keys = sorted(set(e) | set(m) | {'_other'})
    se, sm = sum(e.values()) + 0.5 * len(keys), sum(m.values()) + 0.5 * len(keys)
    llr = {k: float(np.log((e[k] + 0.5) / se) - np.log((m[k] + 0.5) / sm)) for k in keys}
    return lambda u: llr.get(u if u in keep else '_other', llr['_other'])


def folio_halves(folios, seed):
    f = sorted(set(folios))
    rng = np.random.default_rng(seed)
    rng.shuffle(f)
    return set(f[: len(f) // 2]), set(f[len(f) // 2:])


class EdgeArm:
    """Cross-fitted edge index I for one language and side ('start' uses post-break words, 'end' pre-break words)."""

    def __init__(self, words, breaks, lang, side, seed, match='index'):
        self.lang, self.side, self.match = lang, side, match
        W = [w for w in words if w['lang'] == lang]
        self.breaks = [b for b in breaks if b['lang'] == lang]
        self.bfol = sorted({b['folio'] for b in self.breaks})
        fidx = {f: i for i, f in enumerate(self.bfol)}
        self.b_fi = np.array([fidx[b['folio']] for b in self.breaks])
        h1, h2 = folio_halves([w['folio'] for w in W], seed)
        self.dirs = []
        for fit_half, ref_half in ((h1, h2), (h2, h1)):
            model = fit_edge_model([w for w in W if w['folio'] in fit_half], lang, side)
            self.dirs.append(self._prep(model, [w for w in W if w['folio'] in ref_half]))

    def _prep(self, model, ref):
        side = self.side
        rfol = sorted({w['folio'] for w in ref})
        ridx = {f: i for i, f in enumerate(rfol)}
        lvl = [Counter(), Counter(), Counter()]
        elvl = [Counter(), Counter()]
        for w in ref:
            k, is_edge = _word_keys(w, side, self.match)
            if is_edge is None:
                continue
            if is_edge:
                elvl[0][w['section']] += 1
                elvl[1]['*'] += 1
            else:
                lvl[0][(w['section'],) + k] += 1
                lvl[1][k] += 1
                lvl[2][(k[1],)] += 1
        cells, ecells = {}, {}
        b_cell, b_ecell, fallback = [], [], Counter()
        for b in self.breaks:
            k = break_key(b, side, self.match)
            cands = [(0, (b['section'],) + k), (1, k), (2, (k[1],))]
            for level, key in cands:
                if lvl[level][key] >= MIN_REF:
                    break
            fallback[level] += 1
            b_cell.append(cells.setdefault((level, key), len(cells)))
            ek = (0, b['section']) if elvl[0][b['section']] >= MIN_REF else (1, '*')
            b_ecell.append(ecells.setdefault(ek, len(ecells)))
        S = np.zeros((len(rfol), len(cells)))
        C = np.zeros_like(S)
        SE = np.zeros((len(rfol), len(ecells)))
        CE = np.zeros_like(SE)
        ukey = 'first' if side == 'start' else 'last'
        for w in ref:
            k, is_edge = _word_keys(w, side, self.match)
            if is_edge is None:
                continue
            v = model(w[ukey])
            fi = ridx[w['folio']]
            if is_edge:
                for ek, j in ecells.items():
                    if (ek[0] == 0 and ek[1] == w['section']) or ek[0] == 1:
                        SE[fi, j] += v
                        CE[fi, j] += 1
            else:
                for (level, key), j in cells.items():
                    if (level == 0 and key == (w['section'],) + k) or (level == 1 and key == k) or \
                            (level == 2 and key == (k[1],)):
                        S[fi, j] += v
                        C[fi, j] += 1
        return {'model': model, 'nref': len(rfol), 'S': S, 'C': C, 'SE': SE, 'CE': CE,
                'b_cell': np.array(b_cell), 'b_ecell': np.array(b_ecell), 'fallback': dict(fallback),
                'full_mid': S.sum(0) / np.maximum(C.sum(0), 1), 'full_edge': SE.sum(0) / np.maximum(CE.sum(0), 1)}

    def _index(self, d, llr, WB, WF):
        """WB: B x n_break_folios weights; WF: B x n_ref_folios weights -> (I, num, mid, edge) arrays of length B."""
        wb = WB[:, self.b_fi]
        sw = wb.sum(1)
        num = (wb * llr[None, :]).sum(1) / sw
        cs, cc = WF @ d['S'], WF @ d['C']
        mid_cell = np.where(cc > 0, cs / np.maximum(cc, 1e-12), d['full_mid'][None, :])
        es, ec = WF @ d['SE'], WF @ d['CE']
        edge_cell = np.where(ec > 0, es / np.maximum(ec, 1e-12), d['full_edge'][None, :])
        mid = (wb * mid_cell[:, d['b_cell']]).sum(1) / sw
        edge = (wb * edge_cell[:, d['b_ecell']]).sum(1) / sw
        return (num - mid) / (edge - mid), num, mid, edge

    def evaluate(self, units=None, B=2000, rng=None):
        """Point estimate and folio-bootstrap interval. units: optional list of glyph units replacing the break words."""
        if units is None:
            units = [break_unit(b, self.side) for b in self.breaks]
        rng = rng or np.random.default_rng(0)
        nbf = len(self.bfol)
        res = {'n_breaks': len(self.breaks), 'n_break_folios': nbf}
        Is, pts = [], []
        WB = np.zeros((B, nbf))
        np.add.at(WB, (np.repeat(np.arange(B), nbf), rng.integers(0, nbf, size=(B, nbf)).ravel()), 1.0)
        for d in self.dirs:
            llr = np.array([d['model'](u) for u in units])
            one_b, one_f = np.ones((1, nbf)), np.ones((1, d['nref']))
            I0, num0, mid0, edge0 = self._index(d, llr, one_b, one_f)
            pts.append({'I': float(I0[0]), 'num': float(num0[0]), 'mid': float(mid0[0]), 'edge': float(edge0[0]),
                        'fallback': d['fallback']})
            nf = d['nref']
            WF = np.zeros((B, nf))
            np.add.at(WF, (np.repeat(np.arange(B), nf), rng.integers(0, nf, size=(B, nf)).ravel()), 1.0)
            Is.append(self._index(d, llr, WB, WF)[0])
        Iboot = 0.5 * (Is[0] + Is[1])
        res['I'] = 0.5 * (pts[0]['I'] + pts[1]['I'])
        res['ci95'] = [float(np.quantile(Iboot, 0.025)), float(np.quantile(Iboot, 0.975))]
        res['directions'] = pts
        res['call'] = edge_call(res['ci95'])
        return res


def edge_call(ci):
    if ci[0] >= 2 / 3:
        return 'E-seg'
    if ci[1] <= 1 / 3:
        return 'E-line'
    if ci[0] >= 1 / 3 and ci[1] <= 2 / 3:
        return 'PARTIAL'
    return 'UNRESOLVED'
