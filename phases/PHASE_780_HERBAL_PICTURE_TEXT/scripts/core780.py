#!/usr/bin/env python3
"""PHASE_780 engine (v2 design): codebook and organs, coder agreement gate, organ-level picture similarity, style
similarity, double-centring, texts and text similarity (T1 word tf-idf, T2 within-word unit-trigram tf-idf), pair
covariates, the partial-correlation statistic S with a fast permutation engine (Frisch-Waugh), N-local and N-shift
nulls, and the decision statistic. No function here is ever applied to the real Voynich alignment at k = 0 except in
the locked run script."""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
PH = ROOT / 'phases/PHASE_780_HERBAL_PICTURE_TEXT'
DATA = PH / 'data'
CODE_DIR = ROOT / 'external/phase780_coding'
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')

# ------------------------------------------------------------------------------------------------ codebook (v2)
CONTENT = {
    'root_form': ('nominal', ['none_visible', 'single_taproot', 'few_branched', 'many_branched_or_fibrous', 'swollen']),
    'root_size': ('ordinal', ['none', 'small', 'medium', 'large']),
    'stem_count': ('ordinal', ['1', '2-3', '4+']),
    'leaf_type': ('nominal', ['simple_entire', 'simple_toothed_or_lobed', 'compound', 'grass_or_needle', 'none', 'mixed']),
    'leaf_size': ('ordinal', ['small', 'medium', 'large']),
    'leaf_count': ('ordinal', ['0', '1-5', '6-15', '16+']),
    'flowers': ('nominal', ['none', 'flowers', 'fruits_or_seed_heads', 'both']),
    'flower_count': ('ordinal', ['0', '1', '2-5', '6+']),
    'flower_colour': ('nominal', ['none', 'blue', 'red_or_pink', 'yellow', 'white_or_unpainted', 'mixed']),
    'habit': ('nominal', ['upright_herb', 'sprawling_or_climbing', 'shrub_or_tree_like']),
}
ORGANS = {'root': ['root_form', 'root_size'], 'stem': ['stem_count'], 'leaf': ['leaf_type', 'leaf_size', 'leaf_count'],
          'flower': ['flowers', 'flower_count', 'flower_colour'], 'habit': ['habit']}
STYLE = {'fill': ('ordinal', ['outline_only', 'partly_painted', 'fully_painted']),
         'line_weight': ('ordinal', ['thin', 'heavy']),
         'shading': ('nominal', ['none', 'hatching'])}
CORPUS_ONLY = {'shading': 'BR'}     # the Brunschwig copy is hand-coloured: colour and fill are coded in both corpora
ALPHA_MIN, COVER_MIN, MIN_ORGANS_GATE, MIN_FEATS_GATE, MIN_ORGANS_PAIR = 0.60, 0.80, 3, 4, 3


def features_for(corpus, spec):
    return {f: v for f, v in spec.items() if CORPUS_ONLY.get(f, corpus) == corpus}


def norm_value(ftype, levels, v):
    if v is None:
        return None
    v = str(v).strip().lower()
    if v in ('unclear', '', 'na', 'n/a', 'none_coded'):
        return None
    lv = [x.lower() for x in levels]
    return lv.index(v) if v in lv else None


def fsim(ftype, nlev, a, b):
    if ftype == 'nominal':
        return 1.0 if a == b else 0.0
    return 1.0 - abs(a - b) / max(nlev - 1, 1)


# ------------------------------------------------------------------------------------------------ agreement gate
def kripp_alpha(pairs, ftype, nlev):
    if len(pairs) < 5:
        return float('nan')
    if ftype == 'nominal':
        d = lambda a, b: 0.0 if a == b else 1.0  # noqa: E731
    else:
        d = lambda a, b: ((a - b) / max(nlev - 1, 1)) ** 2  # noqa: E731
    do = float(np.mean([d(a, b) for a, b in pairs]))
    vals = np.array([x for p in pairs for x in p], float)
    if ftype == 'nominal':
        cnt = Counter(vals.tolist())
        n = len(vals)
        de = 1.0 - sum(c * (c - 1) for c in cnt.values()) / (n * (n - 1))
    else:
        diff = (vals[:, None] - vals[None, :]) / max(nlev - 1, 1)
        n = len(vals)
        de = float((diff ** 2).sum() / (n * (n - 1)))
    return float('nan') if de == 0 else float(1.0 - do / de)


def gate(corpus, units, codes_a, codes_b):
    """Per-feature alpha and coverage; the corpus passes if the entered content features cover >= 3 organs and
    number >= 4."""
    out = {}
    n = len(units)
    for spec, block in ((CONTENT, 'content'), (STYLE, 'style')):
        for f, (ftype, levels) in features_for(corpus, spec).items():
            pairs, both = [], 0
            for u in units:
                a = norm_value(ftype, levels, codes_a.get(u, {}).get(f))
                b = norm_value(ftype, levels, codes_b.get(u, {}).get(f))
                if a is not None and b is not None:
                    pairs.append((a, b))
                    both += 1
            al = kripp_alpha(pairs, ftype, len(levels))
            cov = both / n if n else 0.0
            out[f] = {'block': block, 'type': ftype, 'alpha': al, 'coverage': cov, 'n_pairable': len(pairs),
                      'pct_agree': float(np.mean([a == b for a, b in pairs])) if pairs else float('nan'),
                      'enters': bool(al == al and al >= ALPHA_MIN and cov >= COVER_MIN)}
    ent = [f for f, v in out.items() if v['block'] == 'content' and v['enters']]
    organs = {o for o, fs in ORGANS.items() if any(f in ent for f in fs)}
    return {'features': out, 'entered_content': ent, 'organs': sorted(organs),
            'entered_style': [f for f, v in out.items() if v['block'] == 'style' and v['enters']],
            'passes': len(ent) >= MIN_FEATS_GATE and len(organs) >= MIN_ORGANS_GATE}


# ------------------------------------------------------------------------------------------------ picture similarity
def encode(units, codes, feats, spec):
    """Integer-coded values (None -> -1) per feature: {f: np.array}."""
    out = {}
    for f in feats:
        ftype, levels = spec[f]
        out[f] = np.array([(-1 if (v := norm_value(ftype, levels, codes.get(u, {}).get(f))) is None else v) for u in units])
    return out


def organ_similarity(enc, entered):
    """Content similarity for one coder set: per organ the mean over its entered features observed for both pages,
    then the mean over organs observed for both pages; NaN where fewer than MIN_ORGANS_PAIR organs are shared."""
    n = len(next(iter(enc.values())))
    tot = np.zeros((n, n))
    cnt = np.zeros((n, n))
    for o, fs in ORGANS.items():
        fs = [f for f in fs if f in entered]
        if not fs:
            continue
        s_num = np.zeros((n, n))
        s_den = np.zeros((n, n))
        for f in fs:
            ftype, levels = CONTENT[f]
            v = enc[f].astype(float)
            ok = v >= 0
            both = ok[:, None] & ok[None, :]
            if ftype == 'nominal':
                s = (v[:, None] == v[None, :]).astype(float)
            else:
                s = 1.0 - np.abs(v[:, None] - v[None, :]) / max(len(levels) - 1, 1)
            s_num += np.where(both, s, 0.0)
            s_den += both
        has = s_den > 0
        tot += np.where(has, s_num / np.maximum(s_den, 1), 0.0)
        cnt += has
    with np.errstate(invalid='ignore', divide='ignore'):
        m = np.where(cnt >= MIN_ORGANS_PAIR, tot / np.maximum(cnt, 1), np.nan)
    np.fill_diagonal(m, np.nan)
    return m


def style_similarity(enc, entered_style, heights):
    n = len(heights)
    num = np.zeros((n, n))
    den = np.zeros((n, n))
    for f in entered_style:
        ftype, levels = STYLE[f]
        v = enc[f].astype(float)
        ok = v >= 0
        both = ok[:, None] & ok[None, :]
        s = (v[:, None] == v[None, :]).astype(float) if ftype == 'nominal' else 1.0 - np.abs(v[:, None] - v[None, :]) / max(len(levels) - 1, 1)
        num += np.where(both, s, 0.0)
        den += both
    h = np.asarray(heights, float)
    num += 1.0 - np.abs(h[:, None] - h[None, :])
    den += 1
    m = num / den
    np.fill_diagonal(m, np.nan)
    return m


def picture_matrices(corpus, units, codes_by_set, g, heights):
    sets = sorted(codes_by_set)
    C = np.nanmean(np.stack([organ_similarity(encode(units, codes_by_set[s], g['entered_content'], CONTENT), g['entered_content'])
                             for s in sets]), axis=0)
    Y = np.nanmean(np.stack([style_similarity(encode(units, codes_by_set[s], g['entered_style'], STYLE), g['entered_style'], heights)
                             for s in sets]), axis=0)
    return C, Y


def _fill_neutral(M):
    """No centring (descriptive variant): undefined pairs take the mean of the defined off-diagonal entries."""
    M = np.array(M, float)
    np.fill_diagonal(M, np.nan)
    M[np.isnan(M)] = np.nanmean(M)
    np.fill_diagonal(M, 0.0)
    return M


def double_centre(M):
    """Remove row and column means over defined off-diagonal entries; undefined pairs become 0 (the neutral value)."""
    M = np.array(M, float)
    np.fill_diagonal(M, np.nan)
    r = np.nanmean(M, axis=1)
    g = np.nanmean(M)
    D = M - r[:, None] - r[None, :] + g
    D[np.isnan(D)] = 0.0
    np.fill_diagonal(D, 0.0)
    return D


# ------------------------------------------------------------------------------------------------ texts
def voynich_texts(folios, interior_only=False):
    import pandas as pd
    df = pd.read_csv(ROOT / 'data/transcriptions/interlinear_full_words.txt', sep='\t', dtype=str)
    df = df[(df['transcriber'] == 'H') & (df['folio'].isin(folios))]
    df = df[df['placement'].fillna('').str.startswith('P')]
    df = df[df['word'].fillna('').str.strip() != '']
    df = df[~df['word'].str.contains(r'\*', regex=True)]
    if interior_only:
        df = df[(df['line_initial'].astype(int) > 1) & (df['line_final'].astype(int) > 1)]
    by = defaultdict(list)
    for f, w in zip(df['folio'], df['word']):
        by[f].append(w)
    return [by[f] for f in folios]


def br_clean(lines):
    keep = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith('[') or s.startswith('---'):
            continue
        keep.append(s)
    s = ' '.join(keep)
    s = re.sub(r'\[[^\]]*\]', ' ', s)
    s = re.sub(r'([a-zäöüſ])-\s+([a-zäöüſ])', r'\1\2', s)
    s = s.lower().replace('ſ', 's')
    toks = re.findall(r'[a-zäöüßęů]+', s)
    return [t for t in toks if len(t) > 1]


_BR_LINES = None


def br_lines():
    global _BR_LINES
    if _BR_LINES is None:
        _BR_LINES = open(ROOT / 'sources/brunschwig_1500/brunschwig_1500_corrected.txt', encoding='utf-8').read().split('\n')
    return _BR_LINES


def br_texts(entries):
    L = br_lines()
    return [br_clean(L[e['head_line'] + 1:e['end_line']]) for e in entries]


def br_uses_only(tokens_lines):
    """Text from the first virtue paragraph mark onward (a single capital letter A starting a paragraph)."""
    return tokens_lines


def units_of(word, corpus):
    return GLYPH_RE.findall(word) if corpus == 'V' else list(word)


def tfidf_cosine(docs):
    n = len(docs)
    df = Counter()
    for d in docs:
        df.update(d.keys())
    vocab = {t: k for k, t in enumerate(df)}
    idf = np.array([math.log(n / df[t]) for t in vocab])
    M = np.zeros((n, len(vocab)))
    for i, d in enumerate(docs):
        for t, c in d.items():
            M[i, vocab[t]] = (1 + math.log(c)) * idf[vocab[t]]
    nr = np.linalg.norm(M, axis=1)
    nr[nr == 0] = 1.0
    M = M / nr[:, None]
    S = M @ M.T
    np.fill_diagonal(S, np.nan)
    return S


def text_similarity(token_lists, corpus):
    t1 = tfidf_cosine([Counter(t) for t in token_lists])
    docs2 = []
    for toks in token_lists:
        c = Counter()
        for w in toks:
            u = ['<'] + units_of(w, corpus) + ['>']
            for k in range(len(u) - 2):
                c[tuple(u[k:k + 3])] += 1
        docs2.append(c)
    return {'T1': t1, 'T2': tfidf_cosine(docs2)}


# ------------------------------------------------------------------------------------------------ covariates
def conjugate(folio_num, quire_first):
    return 2 * quire_first + 7 - folio_num


def v_covariates(pages, feats, lengths):
    """pages: dicts with folio, quire, leaf, pos; feats: page features dict; lengths: tokens per page."""
    n = len(pages)
    i0, i1 = np.triu_indices(n, 1)
    pos = np.array([p['pos'] for p in pages], float)
    dpos = np.abs(pos[i0] - pos[i1])
    quires = sorted({p['quire'] for p in pages})
    qi = np.array([quires.index(p['quire']) for p in pages])
    first = {q: min(p['leaf'] for p in pages if p['quire'] == q) for q in quires}
    special = {87: 90, 90: 87, 93: 96, 96: 93, 94: 95, 95: 94}
    leaf = np.array([p['leaf'] for p in pages])
    conj = np.array([special.get(l, conjugate(l, (l - 1) // 8 * 8 + 1)) for l in leaf])
    cols, names = [], []
    pairq = [tuple(sorted((qi[a], qi[b]))) for a, b in zip(i0, i1)]
    cats = sorted(set(pairq))
    for c in cats[1:]:
        cols.append(np.array([pq == c for pq in pairq], float))
        names.append(f'quirepair_{quires[c[0]]}{quires[c[1]]}')
    for nm, v in (('dpos1', dpos == 1), ('dpos2', dpos == 2), ('dpos3_4', (dpos >= 3) & (dpos <= 4))):
        cols.append(v.astype(float)); names.append(nm)
    cols.append(np.log1p(dpos)); names.append('log1p_dpos')
    cols.append((leaf[i0] == leaf[i1]).astype(float)); names.append('same_leaf')
    cols.append((conj[i0] == leaf[i1]).astype(float)); names.append('same_bifolium')
    ln = np.log(np.asarray(lengths, float))
    cols += [np.abs(ln[i0] - ln[i1]), ln[i0] + ln[i1]]; names += ['dlogn', 'slogn']
    for k in ('tokens_per_line', 'line_edge_share', 'n_paragraphs'):
        v = np.array([feats[p['folio']][k] for p in pages], float)
        cols += [np.abs(v[i0] - v[i1]), v[i0] + v[i1]]; names += [f'd_{k}', f's_{k}']
    for k in ('e2_share', 'minim2_share', 'k_share', 'ch_share'):
        v = np.array([feats[p['folio']][k] for p in pages], float)
        v[np.isnan(v)] = np.nanmean(v)
        cols.append(np.abs(v[i0] - v[i1])); names.append(f'd_{k}')
    X = np.column_stack(cols)
    keep = X.std(axis=0) > 0
    return X[:, keep], [nm for nm, k in zip(names, keep) if k]


def br_covariates(entries, lengths):
    n = len(entries)
    i0, i1 = np.triu_indices(n, 1)
    pos = np.array([e['rank'] for e in entries], float)
    dpos = np.abs(pos[i0] - pos[i1])
    ch = np.array([e['chapter'] or '?' for e in entries])
    ln = np.log(np.asarray(lengths, float))
    cols = [(ch[i0] == ch[i1]).astype(float), (dpos == 1).astype(float), (dpos == 2).astype(float),
            ((dpos >= 3) & (dpos <= 4)).astype(float), np.log1p(dpos), np.abs(ln[i0] - ln[i1]), ln[i0] + ln[i1]]
    X = np.column_stack(cols)
    return X[:, X.std(axis=0) > 0]


# ------------------------------------------------------------------------------------------------ statistic engine
class Engine:
    """Partial correlation of double-centred text and content similarity given fixed covariates and style.
    Fixed covariates are partialled out once; per permutation only C and Y are re-residualised."""

    def __init__(self, T_by_m, C, Y, Xf, use_style=True, centre=True):
        n = C.shape[0]
        self.n = n
        self.i0, self.i1 = np.triu_indices(n, 1)
        X = np.column_stack([np.ones(len(self.i0)), Xf])
        Q, _ = np.linalg.qr(X)
        self.Q = Q.astype(np.float32)
        prep = double_centre if centre else _fill_neutral
        self.dcC = prep(C).astype(np.float32)
        self.dcY = prep(Y).astype(np.float32) if use_style else None
        self.rT = {}
        for m, T in T_by_m.items():
            t = prep(T)[self.i0, self.i1]
            self.rT[m] = (t - Q @ (Q.T @ t)).astype(np.float32)
        self.measures = list(T_by_m)

    def _resid(self, V):            # V: B x P
        return V - (V @ self.Q) @ self.Q.T

    def stats(self, perms):
        """perms: B x n permutation array (pictures permuted). Returns {m: array of S (B,)}."""
        a, b = perms[:, self.i0], perms[:, self.i1]
        rc = self._resid(self.dcC[a, b])
        out = {}
        if self.dcY is not None:
            ry = self._resid(self.dcY[a, b])
            yy = (ry * ry).sum(1)
            okY = yy > 1e-12
            bc = np.where(okY, (rc * ry).sum(1) / np.where(okY, yy, 1), 0.0)
            rc = rc - bc[:, None] * ry
        for m in self.measures:
            rt = np.broadcast_to(self.rT[m], rc.shape)
            if self.dcY is not None:
                bt = np.where(okY, (ry @ self.rT[m]) / np.where(okY, yy, 1), 0.0)
                rt = rt - bt[:, None] * ry
            num = (rt * rc).sum(1)
            den = np.sqrt((rt * rt).sum(1) * (rc * rc).sum(1))
            out[m] = np.where(den > 0, num / np.where(den > 0, den, 1), 0.0)
        return out

    def stats_batched(self, perms, bs=400):
        res = {m: [] for m in self.measures}
        for k in range(0, len(perms), bs):
            s = self.stats(perms[k:k + bs])
            for m in self.measures:
                res[m].append(s[m])
        return {m: np.concatenate(v) for m, v in res.items()}


def local_perms(blocks, B, rng):
    blocks = np.asarray(blocks)
    n = len(blocks)
    P = np.tile(np.arange(n), (B, 1))
    for g in (np.where(blocks == b)[0] for b in np.unique(blocks)):
        if len(g) < 2:
            continue
        keys = rng.random((B, len(g)))
        P[:, g] = g[np.argsort(keys, axis=1)]
    return P


def shift_perms(n, kmin=3):
    return np.array([np.roll(np.arange(n), k) for k in range(kmin, n - kmin + 1)])


N_LOCAL = 10_000


def decide(engine, blocks, rng, n_local=N_LOCAL, identity=None):
    """Observed S (at the given base alignment `identity`, default the identity) with its N-local and N-shift nulls;
    returns per measure S, z_local, p_local, z_shift and Z = min(z_local, z_shift), plus Zmax over measures.
    The base alignment is a permutation applied before the nulls (used by the controls)."""
    n = engine.n
    base = np.arange(n) if identity is None else np.asarray(identity)
    obs = engine.stats(base[None, :])
    L = local_perms(blocks, n_local, rng)
    loc = engine.stats_batched(base[L])
    Sh = shift_perms(n)
    sh = engine.stats_batched(base[Sh])
    out = {}
    for m in engine.measures:
        s = float(obs[m][0])
        zl = (s - loc[m].mean()) / loc[m].std(ddof=1)
        zs = (s - sh[m].mean()) / sh[m].std(ddof=1)
        out[m] = {'S': s, 'z_local': float(zl), 'p_local': float((1 + (loc[m] >= s).sum()) / (1 + len(loc[m]))),
                  'z_shift': float(zs), 'Z': float(min(zl, zs))}
    out['Zmax'] = max(out[m]['Z'] for m in engine.measures)
    out['pmin_local'] = min(out[m]['p_local'] for m in engine.measures)
    return out


def v_blocks(pages):
    return [f"{p['quire']}_{(p['leaf'] - min(q['leaf'] for q in pages if q['quire'] == p['quire'])) // 2}" for p in pages]


def br_blocks(entries):
    out, cnt = [], Counter()
    for e in entries:
        ch = e['chapter'] or '?'
        out.append(f'{ch}_{cnt[ch] // 4}')
        cnt[ch] += 1
    return out
