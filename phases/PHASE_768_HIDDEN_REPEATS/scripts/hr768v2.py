"""PHASE_768 v2 protocol (lean audit edits E3, E4, E6, E7, E8): multi-chain null with convergence gates,
distinct-type and low-L1 robustness statistics, habit3b, held-out texts and codebooks in B's forms.

Builds on hr768 (skeleton, loaders, N5 hookup, Windows, generators).
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

import numpy as np

import hr768 as HR
from hr768 import GLYPH_RE, NS, N5, ROOT, TU, NH, token_class

N_CHAINS, NSAMP_CHAIN, THIN, BURN, ANNEAL = 4, 50, 10, 2000, 1000
SPLITS = ('all', 'interior', 'cross_folio', 'distinct')


# ------------------------------------------------------------------------------------------------ statistics
def repeat_counts2(tok, rep, W, extra=None):
    """For each n: (RPT all, RPT interior, RPT cross-folio, number of distinct repeated sequences)."""
    sym = rep[np.where(tok >= 0, tok, 0)]
    if extra is not None:
        sym = sym * 64 + extra
    out = {}
    for nn in NS:
        w = W.win[nn]
        cols = np.stack([sym[w + k] for k in range(nn)], axis=1)
        _, inv, cnt = np.unique(cols, axis=0, return_inverse=True, return_counts=True)
        inv = inv.ravel()
        rep_occ = cnt[inv] >= 2
        fol = W.folio_of_pos[w]
        pair = np.unique(np.stack([inv, fol], axis=1), axis=0)
        nfol = np.bincount(pair[:, 0], minlength=len(cnt))
        cross = rep_occ & (nfol[inv] >= 2)
        out[nn] = (int(rep_occ.sum()), int((rep_occ & W.interior[nn]).sum()), int(cross.sum()),
                   int((cnt >= 2).sum()))
    return out


def summarise2(obs, samples, L1s):
    """samples: per chain, list of per-sample dicts; L1s: per chain, list of L1 values."""
    flat = [s for ch in samples for s in ch]
    L = np.array([l for ch in L1s for l in ch], dtype=float)
    low = L <= np.quantile(L, 0.25)
    out = {}
    for nn in NS:
        for j, name in enumerate(SPLITS):
            o = obs[nn][j]
            nv = np.array([s[nn][j] for s in flat], dtype=float)
            out[f'n{nn}_{name}'] = {'obs': o, 'null_mean': float(nv.mean()), 'null_sd': float(nv.std(ddof=1)),
                                    'X': (o + 1) / (float(nv.mean()) + 1),
                                    'p': float((1 + (nv >= o).sum()) / (1 + len(nv)))}
        nv = np.array([s[nn][0] for s in flat], dtype=float)[low]
        o = obs[nn][0]
        out[f'n{nn}_lowL1'] = {'obs': o, 'null_mean': float(nv.mean()), 'X': (o + 1) / (float(nv.mean()) + 1),
                               'p': float((1 + (nv >= o).sum()) / (1 + len(nv))), 'n_samples': int(low.sum())}
    return out


def analyse2(lines, sk, reps, units=('JOINT',), seed=768000, extras=None, log=print, gate_rep='TOK'):
    """Per null: N_CHAINS chains from independent shuffled starts, NSAMP_CHAIN samples each (thinned by THIN) after
    BURN sweeps (annealed over the first ANNEAL). Gates: R-hat(RPT_4) and R-hat(L1) <= 1.05, ESS(RPT_4) >= 100."""
    res = {}
    for ui, u in enumerate(units):
        D = HR.make_data(lines, sk['sections'], u)
        W = HR.Windows(D, sk['folios'])
        R = {k: HR.rep_array(D, f) for k, f in reps.items()}
        pos_extra = {k: (b, np.asarray(a, dtype=np.int64)) for k, (b, a) in (extras or {}).items()}
        obs = {k: repeat_counts2(D.tok0, R[k], W) for k in R}
        for k, (b, a) in pos_extra.items():
            obs[k] = repeat_counts2(D.tok0, R[b], W, a)
        samples = {k: [[] for _ in range(N_CHAINS)] for k in obs}
        L1s = [[] for _ in range(N_CHAINS)]
        fcs = []
        for c in range(N_CHAINS):
            def cb(tok, C, L1, c=c):
                L1s[c].append(L1)
                fcs.append(float(N5.frac_changed(D, tok)))
                for k in R:
                    samples[k][c].append(repeat_counts2(tok, R[k], W))
                for k, (b, a) in pos_extra.items():
                    samples[k][c].append(repeat_counts2(tok, R[b], W, a))
            N5.run_chain(D, HR.BETA, seed + 100 * ui + c, 'N1', BURN, ANNEAL, NSAMP_CHAIN, THIN, cb)
        edges = int(D.R.sum())
        rpt4 = np.array([[s[4][0] for s in samples[gate_rep][c]] for c in range(N_CHAINS)], dtype=float)
        L1a = np.array(L1s, dtype=float)
        diag = {'edges': edges, 'L1_over_edges': float(L1a.mean()) / edges, 'frac_changed': float(np.mean(fcs)),
                'rhat_RPT4': N5.rhat_rank(rpt4), 'rhat_L1': N5.rhat_rank(L1a), 'ess_RPT4': N5.ess_bulk(rpt4),
                'first_units': D.NF, 'last_units': D.NL}
        diag['gates_pass'] = bool(diag['rhat_RPT4'] <= 1.05 and diag['rhat_L1'] <= 1.05 and diag['ess_RPT4'] >= 100)
        res[u] = {'diagnostics': diag, 'reps': {k: summarise2(obs[k], samples[k], L1s) for k in obs}}
        t = res[u]['reps'][gate_rep]
        log(f'    N5{HR.NULL_TAG[u]} [4 chains]: L1/edges {diag["L1_over_edges"]:.3f} fc {diag["frac_changed"]:.3f} '
            f'Rhat {diag["rhat_RPT4"]:.3f}/{diag["rhat_L1"]:.3f} ESS {diag["ess_RPT4"]:.0f} '
            f'{"PASS" if diag["gates_pass"] else "FAIL"} | {gate_rep}: X3 {t["n3_all"]["X"]:.2f} '
            f'p {t["n3_all"]["p"]:.3f}, X4 {t["n4_all"]["X"]:.2f} p {t["n4_all"]["p"]:.3f}, '
            f'X4dist {t["n4_distinct"]["X"]:.2f}, X4low {t["n4_lowL1"]["X"]:.2f}')
    return res


# ------------------------------------------------------------------------------------------------ habit3b (E8)
def habit3b_lines(sk, seed, min_tok_ctx=20, min_ctx=5):
    """habit3 plus a (class, last two glyph units) backoff context before (class, last glyph), and class / unigram
    successors conditioned on the line quintile of the position being generated."""
    rng = np.random.default_rng(seed)
    initial = Counter()
    ctxT, ctxJ2, ctxJ1, ctxCQ, ctxQ = (defaultdict(Counter) for _ in range(5))

    def quint(p, n):
        return min(4, int(5 * p / max(n, 1)))
    for ln in sk['lines']:
        prev = None
        n = len(ln)
        for p, w in enumerate(ln):
            if w is None:
                prev = None
                continue
            q = quint(p, n)
            ctxQ[q][w] += 1
            if prev is None:
                initial[w] += 1
            else:
                g = GLYPH_RE.findall(prev)
                c = token_class(prev)
                ctxT[prev][w] += 1
                ctxJ2[(c, tuple(g[-2:]))][w] += 1
                ctxJ1[(c, g[-1])][w] += 1
                ctxCQ[(c, q)][w] += 1
            prev = w
    cache = {}

    def draw(key, counter):
        if key not in cache:
            keys = list(counter)
            pr = np.array([counter[k] for k in keys], dtype=float)
            cache[key] = (keys, np.cumsum(pr / pr.sum()))
        keys, cum = cache[key]
        return keys[min(int(np.searchsorted(cum, rng.random())), len(keys) - 1)]

    out = []
    for ln in sk['lines']:
        prev, cur = None, []
        n = len(ln)
        for p, w in enumerate(ln):
            if w is None:
                cur.append(None)
                prev = None
                continue
            q = quint(p, n)
            if prev is None:
                t = draw('init', initial)
            else:
                g = GLYPH_RE.findall(prev)
                c = token_class(prev)
                t = None
                for key, table, thr in ((('T', prev), ctxT.get(prev), min_tok_ctx),
                                        (('J2', c, tuple(g[-2:])), ctxJ2.get((c, tuple(g[-2:]))), min_ctx),
                                        (('J1', c, g[-1]), ctxJ1.get((c, g[-1])), min_ctx),
                                        (('CQ', c, q), ctxCQ.get((c, q)), min_ctx)):
                    if table and sum(table.values()) >= thr:
                        t = draw(key, table)
                        break
                if t is None:
                    t = draw(('Q', q), ctxQ[q])
            cur.append(t)
            prev = t
        out.append(cur)
    return out


# ------------------------------------------------------------------------------------------------ held-out texts (E3a)
def _clean_words(txt):
    txt = txt.replace('ſ', 's')
    txt = re.sub(r'([A-Za-z])[-¬]\s*\n\s*(?:\d+\s+)?([A-Za-z])', r'\1\2', txt)
    return [''.join(w) for seg in TU.G.lines_from_text(txt) for w in seg]


def heldout_stream(name):
    """Held-out word-written texts; none informs C4 or T4. The Antidotarium (17,292 words) is too short and excluded."""
    if name in ('LAT_codicillus', 'ITA_dante'):
        m = NH.load_version('GV1')
        return list(NH.plaintext('P-REC' if name == 'LAT_codicillus' else 'P-ITA', m)[1])
    if name == 'LAT_mesue':
        return _clean_words((ROOT / 'sources/mesue_grabadin/mesue_grabadin_latin_full.txt').read_text(
            encoding='utf-8', errors='replace'))
    if name == 'LAT_rupescissa':
        return _clean_words('\n'.join((ROOT / 'sources/rupescissa/rupescissa_latin_1561.txt').read_text(
            encoding='utf-8', errors='replace').split('\n')[200:]))
    if name == 'LAT_sismel':
        s = (ROOT / 'sources/sismel_testamentum/sismel_testamentum_assembled.txt').read_text(encoding='utf-8',
                                                                                          errors='replace')
        parts = re.split(r'={10,}\nSPREAD (\d+) — ([LR])[^\n]*\n={10,}\n', s)
        pages = []
        for i in range(1, len(parts) - 2, 3):
            if parts[i + 1] == 'L' and 'TESTAMENTUM' in parts[i + 2][:400]:
                body = re.split(r'\n\s*─{5,}', parts[i + 2])[0]
                pages.append('\n'.join(l for l in body.split('\n') if 'TESTAMENTUM' not in l
                                       and not re.match(r'^\s*f\.\s*\d', l)))
        return _clean_words('\n\n'.join(pages))
    if name == 'TUR_nt':
        return [''.join(w) for seg in TU.G.lines_from_text(TU._gb('Modern - Turkish - Literary - NT')) for w in seg]
    raise ValueError(name)


HELDOUT = ('LAT_codicillus', 'LAT_mesue', 'LAT_rupescissa', 'LAT_sismel', 'ITA_dante', 'TUR_nt')


# ------------------------------------------------------------------------------------------------ B-form codebooks (E4)
def b_types_by_freq(sk, seed):
    rng = np.random.default_rng(seed)
    c = Counter(w for ln in sk['lines'] for w in ln if w is not None)
    types = list(c)
    tie = rng.random(len(types))
    order = sorted(range(len(types)), key=lambda i: (-c[types[i]], tie[i]))
    return [types[i] for i in order]


def synthetic_b_types(sk, n_needed, exclude, seed):
    """B-like types from a glyph-unit trigram model over B's type list (each type counted once); new distinct strings."""
    rng = np.random.default_rng(seed)
    types = sorted({w for ln in sk['lines'] for w in ln if w is not None})
    tri = defaultdict(Counter)
    for w in types:
        g = ['^', '^'] + GLYPH_RE.findall(w) + ['$']
        for a, b, c in zip(g, g[1:], g[2:]):
            tri[(a, b)][c] += 1
    cum = {k: (list(v), np.cumsum(np.array(list(v.values()), dtype=float) / sum(v.values()))) for k, v in tri.items()}
    out, seen = [], set(exclude)
    while len(out) < n_needed:
        a, b, s = '^', '^', []
        while True:
            keys, cm = cum[(a, b)]
            c = keys[min(int(np.searchsorted(cm, rng.random())), len(keys) - 1)]
            if c == '$' or len(s) > 12:
                break
            s.append(c)
            a, b = b, c
        w = ''.join(s)
        if 2 <= len(s) <= 10 and w not in seen:
            seen.add(w)
            out.append(w)
    return out


def codebook_stream(words, k, sk, seed):
    """Word types -> B types by frequency rank (ties random); k distinct B-form spellings per word type, one chosen
    uniformly per occurrence; synthetic B-like types appended when B's inventory runs out."""
    rng = np.random.default_rng(seed)
    wc = Counter(words)
    wt = list(wc)
    tie = rng.random(len(wt))
    order = sorted(range(len(wt)), key=lambda i: (-wc[wt[i]], tie[i]))
    rank = {wt[i]: r for r, i in enumerate(order)}
    btypes = b_types_by_freq(sk, seed + 1)
    need = len(wt) * k
    if need > len(btypes):
        btypes = btypes + synthetic_b_types(sk, need - len(btypes), set(btypes), seed + 2)
    return [btypes[rank[w] * k + int(rng.integers(k))] for w in words]
