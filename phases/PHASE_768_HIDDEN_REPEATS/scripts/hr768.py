"""PHASE_768 shared machinery: does Currier B repeat ordered sequences beyond its local rules?

Every corpus is laid into B's own P-text skeleton (H track: same lines, same line lengths, uncertain-token blockers in
place, B's section and folio labels), so window counts are identical across corpora. The null is the PHASE_756 N5
chain (within-line permutations of medial tokens; line-initial and line-final tokens and blockers fixed; soft penalty
on per-section junction-pair counts, beta = 2), run with two junction definitions:
  N5g: last glyph of a token -> first glyph of the next (B's boundary coupling, C1212/C1563);
  N5c: class of a token -> class of the next (B's class-level local rules, e.g. C549 alternation, C2082 routing).
Statistic: for a representation R (a function of the token) and n = 3, 4, RPT = number of within-line windows of n
consecutive tokens (no blocker inside) whose R-sequence occurs at least twice in the corpus.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
os.environ.setdefault('NUMBA_CACHE_DIR', str(ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/scripts/__pycache__/numba'))
sys.path.insert(0, str(ROOT))
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
CLASS_MAP = ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
BETA = 2.0
NS = (3, 4)
SEED_OFFSET = {'GLYPH': 0, 'LETTER': 1, 'CLASS': 1, 'JOINT': 2}   # as used by the first calibration run
NULL_TAG = {'GLYPH': 'g', 'LETTER': 'l', 'CLASS': 'c', 'JOINT': 'j'}


def _imp(name, rel):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


N5 = _imp('n5_768', 'phases/PHASE_756_C957_JOINT_NULL/scripts/c957_joint_null_n5.py')
NH = _imp('naibbe768', 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts/naibbe_harness.py')
TU = _imp('tu767_for768', 'phases/PHASE_767_TOKEN_UNIT_TEST/scripts/tu767.py')

_CM = json.load(open(CLASS_MAP, encoding='utf-8'))
TOKEN_CLASS = {w: str(c) for w, c in _CM['token_to_class'].items()}
_MORPH = None


def token_class(w):
    return TOKEN_CLASS.get(w, 'UN')


def middle(w):
    global _MORPH
    if _MORPH is None:
        from scripts.voynich import Morphology
        _MORPH = Morphology()
    try:
        m = _MORPH.extract(w).middle
    except Exception:
        m = None
    return m if m else w


# ------------------------------------------------------------------------------------------------ N5 junction units
_orig_units = N5.units


def _units(word, unit):
    if unit == 'CLASS':
        c = token_class(word)
        return c, c
    if unit == 'JOINT':                      # class and edge glyph together: preserves both kinds of junction rule
        c = token_class(word)
        g = GLYPH_RE.findall(word)
        return f'{c}|{g[0]}', f'{c}|{g[-1]}'
    if unit == 'LETTER':
        return word[0], word[-1]
    return _orig_units(word, unit)


N5.units = _units            # Data.__init__ looks up the module-level name at call time


# ------------------------------------------------------------------------------------------------ skeleton and corpora
def b_skeleton():
    """B (H track, P placement): lines with None blockers, section per line, folio per line."""
    lines, secs, keys = N5.load_primary()
    return {'lines': lines, 'sections': secs, 'folios': [k[0] for k in keys]}


def pour(stream, sk):
    it = iter(stream)
    return [[None if w is None else next(it) for w in ln] for ln in sk['lines']]


def n_certain(sk):
    return sum(w is not None for ln in sk['lines'] for w in ln)


def natural_stream(lang):
    """A Gaskell & Bowern NT as a flat word stream (PHASE_764 cleaning)."""
    return [''.join(w) for seg in TU.eu_word(lang) for w in seg]


def naibbe_stream(pid, seed, n):
    """Naibbe GV1 ciphertext of a real plaintext (no space removal), with the plaintext chunk behind each token."""
    m = NH.load_version('GV1')
    pt = NH.plaintext(pid, m)
    import random
    random.seed(seed)
    lines = pt[0]
    i = random.randrange(len(lines))
    toks, chunks = [], []
    while len(toks) < n:
        ct, ch = NH.encrypt_line(m, lines[i % len(lines)])
        assert len(ct) == len(ch), 'token / chunk misalignment'
        toks.extend(ct)
        chunks.extend(ch)
        i += 1
    return toks[:n], chunks[:n]


def timm_lines(sk, seed):
    """Timm-Schinner self-citation output in B's skeleton (PHASE_757 reference member)."""
    NHsk = NH.load_skeleton()
    assert [len(x) for x in NHsk['B']] == [len(x) for x in sk['lines']], 'skeleton mismatch'
    return NH.Timm(NHsk['B'], NHsk['folio']).generate(NHsk['B'], np.random.default_rng(seed))


def habit_lines(sk, seed):
    """Local-rule generator with no message: within-line class-bigram Markov chain fitted on B, tokens emitted from
    each class's B frequency distribution (UN emits B's unclassified tokens). Restarts after a blocker."""
    rng = np.random.default_rng(seed)
    init, trans, emit = Counter(), defaultdict(Counter), defaultdict(Counter)
    for ln in sk['lines']:
        prev = None
        for w in ln:
            if w is None:
                prev = None
                continue
            c = token_class(w)
            emit[c][w] += 1
            if prev is None:
                init[c] += 1
            else:
                trans[prev][c] += 1
            prev = c

    def draw(counter):
        keys = list(counter)
        p = np.array([counter[k] for k in keys], dtype=float)
        return keys[int(rng.choice(len(keys), p=p / p.sum()))]

    out = []
    for ln in sk['lines']:
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            c = draw(init if prev is None or not trans[prev] else trans[prev])
            cur.append(draw(emit[c]))
            prev = c
        out.append(cur)
    return out


def habit2_lines(sk, seed):
    """Stronger local-rule generator with no message: each token is drawn from B's tokens conditioned on the previous
    token's class AND last glyph (B's word-ending routing and junction coupling together), backing off to the previous
    class, then to the unigram. Line-initial tokens (and tokens after a blocker) come from B's line-initial tokens."""
    rng = np.random.default_rng(seed)
    initial, ctx2, ctx1, uni = Counter(), defaultdict(Counter), defaultdict(Counter), Counter()
    for ln in sk['lines']:
        prev = None
        for w in ln:
            if w is None:
                prev = None
                continue
            uni[w] += 1
            if prev is None:
                initial[w] += 1
            else:
                ctx2[(token_class(prev), GLYPH_RE.findall(prev)[-1])][w] += 1
                ctx1[token_class(prev)][w] += 1
            prev = w
    cache = {}

    def draw(counter):
        key = id(counter)
        if key not in cache:
            keys = list(counter)
            p = np.array([counter[k] for k in keys], dtype=float)
            cache[key] = (keys, np.cumsum(p / p.sum()))
        keys, cum = cache[key]
        return keys[min(int(np.searchsorted(cum, rng.random())), len(keys) - 1)]

    out = []
    for ln in sk['lines']:
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            if prev is None:
                t = draw(initial)
            else:
                c2 = ctx2.get((token_class(prev), GLYPH_RE.findall(prev)[-1]))
                c1 = ctx1.get(token_class(prev))
                t = draw(c2) if c2 and sum(c2.values()) >= 5 else (draw(c1) if c1 else draw(uni))
            cur.append(t)
            prev = t
        out.append(cur)
    return out


def habit3_lines(sk, seed, min_tok_ctx=20, min_joint_ctx=5):
    """Strongest local-rule generator with no message: a first-order token model fitted on B. The next token is drawn
    from B's successors of the previous token when that token has >= min_tok_ctx within-line successors; otherwise
    from the (class, last glyph) context (>= min_joint_ctx), then the class context, then the unigram. Contexts are
    thresholded so rare tokens do not replay B's actual sequences."""
    rng = np.random.default_rng(seed)
    initial, ctxT, ctx2, ctx1, uni = Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), Counter()
    for ln in sk['lines']:
        prev = None
        for w in ln:
            if w is None:
                prev = None
                continue
            uni[w] += 1
            if prev is None:
                initial[w] += 1
            else:
                ctxT[prev][w] += 1
                ctx2[(token_class(prev), GLYPH_RE.findall(prev)[-1])][w] += 1
                ctx1[token_class(prev)][w] += 1
            prev = w
    cache = {}

    def draw(key, counter):
        if key not in cache:
            keys = list(counter)
            p = np.array([counter[k] for k in keys], dtype=float)
            cache[key] = (keys, np.cumsum(p / p.sum()))
        keys, cum = cache[key]
        return keys[min(int(np.searchsorted(cum, rng.random())), len(keys) - 1)]

    out = []
    for ln in sk['lines']:
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            if prev is None:
                t = draw('init', initial)
            else:
                cT = ctxT.get(prev)
                j = (token_class(prev), GLYPH_RE.findall(prev)[-1])
                c2 = ctx2.get(j)
                c1 = ctx1.get(token_class(prev))
                if cT and sum(cT.values()) >= min_tok_ctx:
                    t = draw(('T', prev), cT)
                elif c2 and sum(c2.values()) >= min_joint_ctx:
                    t = draw(('J',) + j, c2)
                elif c1:
                    t = draw(('C', token_class(prev)), c1)
                else:
                    t = draw('uni', uni)
            cur.append(t)
            prev = t
        out.append(cur)
    return out


# ------------------------------------------------------------------------------------------------ statistics
class Windows:
    """Window index arrays over the flat token positions of a Data object (fixed for all chain samples)."""

    def __init__(self, D, folios):
        self.D = D
        ln_of = D.line_of
        n = len(D.tok0)
        start = D.line_start
        length = D.line_len
        pos_in_line = np.arange(n) - start[ln_of]
        self.edge = (pos_in_line == 0) | (pos_in_line == length[ln_of] - 1)
        fol_id = {f: i for i, f in enumerate(dict.fromkeys(folios))}
        self.folio_of_pos = np.array([fol_id[folios[li]] for li in ln_of], dtype=np.int64)
        self.win = {}
        for nn in NS:
            ok = []
            for p in range(n - nn + 1):
                if ln_of[p] == ln_of[p + nn - 1]:
                    ok.append(p)
            self.win[nn] = np.array(ok, dtype=np.int64)
        blk = D.tok0 < 0                                   # blockers are fixed under N5
        for nn in NS:
            w = self.win[nn]
            bad = np.zeros(len(w), dtype=bool)
            for k in range(nn):
                bad |= blk[w + k]
            self.win[nn] = w[~bad]
        self.interior = {nn: ~np.any(np.stack([self.edge[self.win[nn] + k] for k in range(nn)]), axis=0) for nn in NS}


def rep_array(D, fn):
    """Map vocabulary ids to representation ids (int)."""
    ids = {}
    return np.array([ids.setdefault(fn(w), len(ids)) for w in D.vocab], dtype=np.int64)


def repeat_counts(tok, rep, W, extra=None):
    """For each n: (RPT all, RPT interior, RPT cross-folio). `extra` = optional per-position symbol override
    (array aligned with tok) used for position-attached variant markers."""
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
        out[nn] = (int(rep_occ.sum()), int((rep_occ & W.interior[nn]).sum()), int(cross.sum()))
    return out


def make_data(lines, sections, unit):
    return N5.Data(lines, sections, unit)


def run_null(D, seed, burn=2000, anneal=1000, nsamp=200, thin=10, on_sample=None):
    """N5 chain from a shuffled start (annealed), beta = 2; returns diagnostics."""
    diag = {'L1': [], 'frac_changed': []}

    def cb(tok, C, L1):
        diag['L1'].append(L1)
        diag['frac_changed'].append(float(N5.frac_changed(D, tok)))
        if on_sample is not None:
            on_sample(tok)
    N5.run_chain(D, BETA, seed, 'N1', burn, anneal, nsamp, thin, cb)
    edges = int(D.R.sum())
    return {'edges': edges, 'L1_mean': float(np.mean(diag['L1'])), 'L1_over_edges': float(np.mean(diag['L1'])) / edges,
            'frac_changed_mean': float(np.mean(diag['frac_changed']))}


def summarise(obs, null_list):
    """obs: {n: (all, interior, cross)}; null_list: list of the same. Returns X and one-sided p per n and split."""
    out = {}
    for nn in NS:
        for j, name in enumerate(('all', 'interior', 'cross_folio')):
            o = obs[nn][j]
            nv = np.array([s[nn][j] for s in null_list], dtype=float)
            out[f'n{nn}_{name}'] = {'obs': o, 'null_mean': float(nv.mean()), 'null_sd': float(nv.std(ddof=1)),
                                    'X': (o + 1) / (float(nv.mean()) + 1),
                                    'p': float((1 + (nv >= o).sum()) / (1 + len(nv)))}
    return out


def analyse(lines, sk, reps, units=('GLYPH', 'CLASS'), seed=768, nsamp=200, extras=None, log=print):
    """Run both nulls on one corpus laid into the skeleton. reps: {name: fn(word) -> symbol}. extras: {name:
    (rep_name, per-position int array)} for variant-marker representations. Returns results per null and rep."""
    res = {}
    for u in units:
        D = make_data(lines, sk['sections'], u)
        W = Windows(D, sk['folios'])
        R = {k: rep_array(D, f) for k, f in reps.items()}
        pos_extra = {}
        if extras:
            for k, (base, arr) in extras.items():
                pos_extra[k] = (base, np.asarray(arr, dtype=np.int64))
        obs = {k: repeat_counts(D.tok0, R[k], W) for k in R}
        for k, (base, arr) in pos_extra.items():
            obs[k] = repeat_counts(D.tok0, R[base], W, arr)
        samples = {k: [] for k in obs}

        def on_sample(tok):
            for k in R:
                samples[k].append(repeat_counts(tok, R[k], W))
            for k, (base, arr) in pos_extra.items():
                samples[k].append(repeat_counts(tok, R[base], W, arr))
        diag = run_null(D, seed + SEED_OFFSET[u], nsamp=nsamp, on_sample=on_sample)
        res[u] = {'diagnostics': diag, 'reps': {k: summarise(obs[k], samples[k]) for k in obs}}
        log(f'    null N5{NULL_TAG[u]}: L1/edges {diag["L1_over_edges"]:.3f} '
            f'frac_changed {diag["frac_changed_mean"]:.3f} | ' +
            ' | '.join(f'{k}: X3 {res[u]["reps"][k]["n3_all"]["X"]:.2f} p {res[u]["reps"][k]["n3_all"]["p"]:.3f}, '
                       f'X4 {res[u]["reps"][k]["n4_all"]["X"]:.2f} p {res[u]["reps"][k]["n4_all"]["p"]:.3f}'
                       for k in res[u]['reps']))
    return res
