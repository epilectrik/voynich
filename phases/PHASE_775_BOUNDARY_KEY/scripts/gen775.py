"""PHASE_775 controls: context-keyed ciphers written in B's forms (message present), their shuffled-plaintext twins, and
the no-message generators of PHASE_768/774. B supplies its skeleton and, for the B-like alphabets, its within-line
continuation counts per ending (adjacent pairs, declared) -- the same class of exposure as the habit generators.

Context-keyed cipher (true key K1 or K2): the plaintext unit stream (words, B's certain-token count, one plaintext
segment) is written left to right; each token's alphabet is chosen by the ending of the previously written token
(line start or blocker: '^'). Alphabet A_c maps the plaintext unit of global frequency rank j to the j-th most frequent
B token that follows ending c in B (B's continuation list), continuing into B's global token list and then synthetic
B-like strings when the list runs out. With homophones = h, unit rank j owns h consecutive slots and one is drawn at
random per occurrence. The mapping is a bijection per context (h = 1), which is all rank decoding needs; the B-like
assignment only makes the key sequence behave like B's.
"""
from __future__ import annotations

import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')


def _imp(name, rel):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


G = _imp('gen774', 'phases/PHASE_774_VARIANT_MERGE/scripts/gen774.py')
K = _imp('key775', 'phases/PHASE_775_BOUNDARY_KEY/scripts/key775.py')
HR = G.HR

_CONT = {}
_LT = None


def b_line_types(sk):
    """'H' for a paragraph's first line (the line holds a par_initial token), 'B' otherwise, in skeleton order.
    A structural property of the page layout (positions), not of B's token order."""
    global _LT
    if _LT is not None:
        return _LT
    from scripts.voynich import Transcript
    lines, secs, keys = HR.N5.load_primary()
    assert [len(x) for x in lines] == [len(x) for x in sk['lines']], 'skeleton mismatch'
    head = set()
    for t in Transcript().currier_b(exclude_uncertain=False):
        if t.placement and t.placement.startswith('P') and t.par_initial:
            head.add((t.folio, t.line))
    _LT = ['H' if k in head else 'B' for k in keys]
    return _LT


def ef_groups(sk):
    """EF permutation groups: folio x line type (paragraph-first line or body line)."""
    return [f'{f}|{t}' for f, t in zip(sk['folios'], b_line_types(sk))]


def b_continuations(sk, k):
    """B's continuation lists: ending (last k glyph units) of the previous token -> tokens by frequency; '^' for line
    starts and tokens after a blocker. Adjacent pairs within lines only."""
    if k in _CONT:
        return _CONT[k]
    cont = defaultdict(Counter)
    glob = Counter()
    for ln in sk['lines']:
        prev = None
        for w in ln:
            if w is None:
                prev = None
                continue
            c = '^' if prev is None else K.ending(prev, k)
            cont[c][w] += 1
            glob[w] += 1
            prev = w
    lists = {c: [t for t, _ in sorted(v.items(), key=lambda x: (-x[1], x[0]))] for c, v in cont.items()}
    gl = [t for t, _ in sorted(glob.items(), key=lambda x: (-x[1], x[0]))]
    _CONT[k] = (lists, gl)
    return _CONT[k]


def keyed_cipher(stream, sk, k, seed, homophones=1):
    """Context-keyed cipher of `stream` (plaintext units aligned with B's certain tokens) in B's skeleton."""
    rng = np.random.default_rng(seed)
    lists, gl = b_continuations(sk, k)
    uc = Counter(stream)
    units = sorted(uc, key=lambda u: (-uc[u], rng.random()))
    urank = {u: i for i, u in enumerate(units)}
    need = len(units) * homophones
    alpha = {}
    synth = G.synthetic_strings(gl, need, set(gl), seed + 17, 2, 10)      # shared tail, one list for all contexts

    def alphabet(c):
        if c not in alpha:
            base = list(lists.get(c, []))
            seen = set(base)
            for src in (gl, synth):
                for t in src:
                    if len(base) >= need:
                        break
                    if t not in seen:
                        base.append(t)
                        seen.add(t)
            assert len(base) >= need
            alpha[c] = base
        return alpha[c]
    out, it = [], iter(stream)
    for ln in sk['lines']:
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            u = next(it)
            c = '^' if prev is None else K.ending(prev, k)
            A = alphabet(c)
            j = urank[u] * homophones + (int(rng.integers(homophones)) if homophones > 1 else 0)
            t = A[j]
            cur.append(t)
            prev = t
        out.append(cur)
    return out


def plaintext_order_index(stream, sk, n_shuffle=50, seed=0):
    """O: the plaintext's own word-order information at the level rank decoding can see. Plug-in mutual information
    (bits) between consecutive words' global frequency ranks (1..20, 21+ pooled) within B's lines, minus its mean over
    within-folio shuffles of the words (layout kept)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    uc = Counter(stream)
    order = sorted(uc, key=lambda u: (-uc[u], u))
    rk = {u: min(i + 1, K.R_MAX) for i, u in enumerate(order)}
    sym = np.array([rk[u] for u in stream], dtype=np.int64)
    fol = [f for ln, f in zip(sk['lines'], sk['folios']) for w in ln if w is not None]
    pos_line = []
    li = 0
    for ln in sk['lines']:
        for w in ln:
            if w is not None:
                pos_line.append(li)
        li += 1
    pos_line = np.array(pos_line)
    same = np.r_[False, pos_line[1:] == pos_line[:-1]]
    idx2 = np.flatnonzero(same)

    def mi(x):
        a, b = x[idx2 - 1], x[idx2]
        Kk = K.R_MAX + 1
        j = np.bincount(a * Kk + b, minlength=Kk * Kk).reshape(Kk, Kk).astype(float)
        n = j.sum()
        pa, pb, pj = j.sum(1) / n, j.sum(0) / n, j / n
        nz = pj > 0
        return float((pj[nz] * np.log2(pj[nz] / np.outer(pa, pb)[nz])).sum())
    by = defaultdict(list)
    for i, f in enumerate(fol):
        by[f].append(i)
    groups = [np.array(v) for v in by.values()]
    base = mi(sym)
    null = []
    for _ in range(n_shuffle):
        x = sym.copy()
        for g in groups:
            x[g] = x[rng.permutation(g)]
        null.append(mi(x))
    return base - float(np.mean(null))
