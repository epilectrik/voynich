#!/usr/bin/env python3
"""PHASE_780 engine: texts, text similarity (T1 word tf-idf, T2 within-word unit-trigram tf-idf), coder agreement
(Krippendorff's alpha), picture similarity (Gower), pair covariates, the partial-correlation statistic S and its nulls.
No file in this module computes S on the real Voynich alignment; that happens only in the locked run script."""
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
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')

# ------------------------------------------------------------------------------------------------ codebook
CONTENT = {
    'root_present': ('nominal', ['yes', 'no']),
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
    'symmetry': ('nominal', ['symmetric', 'asymmetric']),
    'non_plant_element': ('nominal', ['none', 'animal_or_human', 'object']),
}
STYLE = {
    'pigments': ('set', ['green', 'blue', 'red_brown', 'yellow', 'other']),
    'fill': ('ordinal', ['outline_only', 'partly_painted', 'fully_painted']),
    'drawing_height': ('ordinal', ['<1/3', '1/3-2/3', '>2/3']),
    'line_weight': ('ordinal', ['thin', 'heavy']),
    'shading': ('nominal', ['none', 'hatching']),
}
CORPUS_ONLY = {'flower_colour': 'V', 'pigments': 'V', 'fill': 'V', 'shading': 'BR'}


def features_for(corpus, block):
    spec = CONTENT if block == 'content' else STYLE
    return {f: v for f, v in spec.items() if CORPUS_ONLY.get(f, corpus) == corpus}


def norm_value(ftype, levels, v):
    """Coder value -> internal value; None for unclear / missing / invalid."""
    if v is None:
        return None
    if ftype == 'set':
        if isinstance(v, str):
            v = [v]
        v = [x for x in v if x in levels]
        return frozenset(v) if v else (frozenset() if v == [] else None)
    v = str(v).strip().lower()
    if v in ('unclear', '', 'na', 'none_coded'):
        return None
    lv = [x.lower() for x in levels]
    return lv.index(v) if v in lv else None


# ------------------------------------------------------------------------------------------------ agreement
def _dist(ftype, a, b, nlev):
    if ftype == 'nominal':
        return 0.0 if a == b else 1.0
    if ftype == 'ordinal':                     # interval metric on ranks (declared approximation of the ordinal metric)
        return ((a - b) / max(nlev - 1, 1)) ** 2
    if ftype == 'set':
        u = a | b
        return 0.0 if not u else 1.0 - len(a & b) / len(u)
    raise ValueError(ftype)


def kripp_alpha(pairs, ftype, nlev):
    """Two coders. pairs: list of (value_A, value_B) per unit with both present. Krippendorff's alpha = 1 - Do/De."""
    vals = [x for p in pairs for x in p]
    if len(pairs) < 5:
        return float('nan')
    do = np.mean([_dist(ftype, a, b, nlev) for a, b in pairs])
    n = len(vals)
    tot = 0.0
    cnt = 0
    for i in range(n):
        for j in range(i + 1, n):
            tot += _dist(ftype, vals[i], vals[j], nlev)
            cnt += 1
    de = tot / cnt if cnt else 0.0
    return float('nan') if de == 0 else float(1.0 - do / de)


def load_codes(corpus, cset):
    """data/codes_<corpus>_<set>.json: {image_code: {feature: value, ...}}"""
    return json.load(open(DATA / f'codes_{corpus}_{cset}.json', encoding='utf-8'))


def agreement(corpus, units, codes_a, codes_b, alpha_min=0.60):
    out = {}
    for block in ('content', 'style'):
        for f, (ftype, levels) in features_for(corpus, block).items():
            pairs = []
            for u in units:
                a = norm_value(ftype, levels, codes_a.get(u, {}).get(f))
                b = norm_value(ftype, levels, codes_b.get(u, {}).get(f))
                if a is not None and b is not None:
                    pairs.append((a, b))
            al = kripp_alpha(pairs, ftype, len(levels))
            pa = float(np.mean([_dist(ftype, a, b, len(levels)) == 0 for a, b in pairs])) if pairs else float('nan')
            out[f] = {'block': block, 'type': ftype, 'n_pairable': len(pairs), 'alpha': al, 'pct_agree': pa,
                      'enters': bool(al == al and al >= alpha_min)}
    return out


# ------------------------------------------------------------------------------------------------ picture similarity
def gower(units, codes, feats):
    """Similarity matrix over `feats` {name: (type, levels)}; pairs with no commonly observed feature get NaN."""
    n = len(units)
    num = np.zeros((n, n))
    den = np.zeros((n, n))
    for f, (ftype, levels) in feats.items():
        vals = [norm_value(ftype, levels, codes.get(u, {}).get(f)) for u in units]
        for i in range(n):
            if vals[i] is None:
                continue
            for j in range(i + 1, n):
                if vals[j] is None:
                    continue
                s = 1.0 - (_dist(ftype, vals[i], vals[j], len(levels)) if ftype != 'ordinal'
                           else abs(vals[i] - vals[j]) / max(len(levels) - 1, 1))
                num[i, j] += s
                den[i, j] += 1
    with np.errstate(invalid='ignore', divide='ignore'):
        m = num / den
    m = np.triu(m, 1)
    m = m + m.T
    m[den + den.T == 0] = np.nan
    np.fill_diagonal(m, 1.0)
    return m


def picture_similarity(corpus, units, codes_by_set, gate, block):
    feats = {f: v for f, v in features_for(corpus, block).items() if gate.get(f, {}).get('enters')}
    if not feats:
        return np.zeros((len(units), len(units))), []
    mats = [gower(units, codes_by_set[c], feats) for c in sorted(codes_by_set)]
    return np.nanmean(np.stack(mats), axis=0), sorted(feats)


# ------------------------------------------------------------------------------------------------ texts
def voynich_texts(folios):
    import pandas as pd
    df = pd.read_csv(ROOT / 'data/transcriptions/interlinear_full_words.txt', sep='\t', dtype=str)
    df = df[(df['transcriber'] == 'H') & (df['folio'].isin(folios))]
    df = df[df['placement'].fillna('').str.startswith('P')]
    df = df[df['word'].fillna('').str.strip() != '']
    df = df[~df['word'].str.contains(r'\*', regex=True)]
    by = defaultdict(list)
    for f, w in zip(df['folio'], df['word']):
        by[f].append(w)
    return [by[f] for f in folios]


def br_clean_entry(lines):
    txt = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith('[WOODCUT') or s.startswith('---') or s.startswith('['):
            continue
        txt.append(s)
    s = ' '.join(txt)
    s = re.sub(r'(\w)\s*/\s*', r'\1 ', s)
    s = s.lower()
    toks = re.findall(r'[a-zäöüßęůꝛſ]+', s)
    return [t for t in toks if len(t) > 1]


def br_texts(entries):
    L = open(ROOT / 'sources/brunschwig_1500/brunschwig_1500_corrected.txt', encoding='utf-8').read().split('\n')
    return [br_clean_entry(L[e['head_line'] + 1:e['end_line']]) for e in entries]


def units_of(word, corpus):
    return GLYPH_RE.findall(word) if corpus == 'V' else list(word)


def tfidf_cosine(docs):
    """docs: list of Counters. Returns the cosine similarity matrix of tf-idf vectors (tf = 1 + log count)."""
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
    return M @ M.T


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
    t2 = tfidf_cosine(docs2)
    return {'T1': t1, 'T2': t2}


# ------------------------------------------------------------------------------------------------ statistic
def pair_index(n):
    return np.triu_indices(n, 1)


def fixed_covariates(meta, lengths):
    """meta: list of dicts with 'pos', 'block' (quire or chapter), 'leaf' (or None). Pair covariates that do not move
    with the pictures."""
    n = len(meta)
    iu = pair_index(n)
    pos = np.array([m['pos'] for m in meta], float)
    blk = np.array([m['block'] for m in meta])
    leaf = np.array([(-1 if m.get('leaf') is None else m['leaf']) for m in meta])
    ln = np.log(np.array(lengths, float))
    cols = [np.log1p(np.abs(pos[iu[0]] - pos[iu[1]])),
            (blk[iu[0]] == blk[iu[1]]).astype(float),
            ((leaf[iu[0]] == leaf[iu[1]]) & (leaf[iu[0]] >= 0)).astype(float),
            np.abs(ln[iu[0]] - ln[iu[1]]),
            ln[iu[0]] + ln[iu[1]]]
    cols = [c for c in cols if np.std(c) > 0]
    return np.column_stack(cols)


def partial_S(T, C, Y, Xf, iu):
    """Partial correlation of T and C pair vectors given fixed covariates Xf and style similarity Y (pair vectors)."""
    t, c = T[iu], C[iu]
    ok = ~np.isnan(c)
    cols = [np.ones(ok.sum()), Xf[ok]]
    y = Y[iu][ok]
    if np.std(y) > 0:
        cols.append(y[:, None])
    X = np.column_stack([cols[0][:, None]] + cols[1:])
    bt, *_ = np.linalg.lstsq(X, t[ok], rcond=None)
    bc, *_ = np.linalg.lstsq(X, c[ok], rcond=None)
    rt, rc = t[ok] - X @ bt, c[ok] - X @ bc
    d = np.sqrt((rt @ rt) * (rc @ rc))
    return float(rt @ rc / d) if d > 0 else 0.0


def permute(M, p):
    return M[np.ix_(p, p)]


def null_shift(T, C, Y, Xf, iu, kmin=3):
    n = C.shape[0]
    vals = []
    for k in range(kmin, n - kmin + 1):
        p = np.roll(np.arange(n), k)
        vals.append(partial_S(T, permute(C, p), permute(Y, p), Xf, iu))
    return np.array(vals)


def null_block(T, C, Y, Xf, iu, blocks, rng, nperm=2000):
    blocks = np.asarray(blocks)
    groups = [np.where(blocks == b)[0] for b in np.unique(blocks)]
    vals = []
    for _ in range(nperm):
        p = np.arange(len(blocks))
        for g in groups:
            p[g] = rng.permutation(g)
        vals.append(partial_S(T, permute(C, p), permute(Y, p), Xf, iu))
    return np.array(vals)


def zscore(s, null):
    sd = null.std(ddof=1)
    return float((s - null.mean()) / sd) if sd > 0 else float('nan')
