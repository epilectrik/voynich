"""PHASE_764 shared machinery: corpus loaders (B from ZL / H, gibberish G, meaningful M), chunking, statistics.

A corpus is a list of SEGMENTS; a segment is a list of words; a word is a tuple of units. Pairs are formed only
between adjacent words inside a segment (a dropped token splits its line: never bridged).
Statistics are plug-in MI in bits, shuffle-corrected against permutations of word order within each segment
(vectorised: all shuffles of a chunk in one argsort).
"""
from __future__ import annotations

import glob
import importlib.util
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
GB = ROOT / 'external/gaskell-bowern'


def _imp(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ================================================================================================ loaders
def load_b_zl(merge_uncertain=True, unit='GLYPH'):
    """ZL 3b Currier B, P placement. Returns list of (folio, segments). Uncertain spaces (',') merged when
    merge_uncertain (PHASE_761 rule); unreadable tokens split segments."""
    SC = _imp('spacing764', 'phases/PHASE_761_SPACING_ROBUSTNESS/scripts/spacing_check.py')
    out = []
    for folio, segs in SC.load():
        new_segs = []
        for seg in segs:
            toks = list(seg)
            if merge_uncertain:
                merged = []
                for t, sep in toks:
                    if sep == ',' and merged:
                        merged[-1] = (merged[-1][0] + t, merged[-1][1])
                    else:
                        merged.append((t, sep))
                toks = merged
            cur = []
            for t, _ in toks:
                if SC.readable(t) and t:
                    cur.append(units_b(t, unit))
                else:
                    if len(cur) >= 1:
                        new_segs.append(cur)
                    cur = []
            if cur:
                new_segs.append(cur)
        if new_segs:
            out.append((folio, new_segs))
    return out


def load_b_h(unit='GLYPH'):
    """H track Currier B, P placement; uncertain ('*') tokens split segments."""
    from scripts.voynich import Transcript
    tx = Transcript()
    lines = defaultdict(list)
    order = []
    for t in tx.currier_b(exclude_uncertain=False):
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if not w:
            continue
        key = (t.folio, t.line)
        if key not in lines:
            order.append(key)
        lines[key].append(None if ('*' in w or t.is_uncertain) else units_b(w, unit))
    by_folio = defaultdict(list)
    for key in order:
        cur = []
        for w in lines[key]:
            if w is None:
                if cur:
                    by_folio[key[0]].append(cur)
                cur = []
            else:
                cur.append(w)
        if cur:
            by_folio[key[0]].append(cur)
    folios = list(dict.fromkeys(k[0] for k in order))
    return [(f, by_folio[f]) for f in folios if by_folio[f]]


def units_b(w, unit):
    return tuple(GLYPH_RE.findall(w)) if unit == 'GLYPH' else tuple(w)


def _clean_word(w):
    w = unicodedata.normalize('NFD', w.lower())
    return ''.join(c for c in w if c.isalpha())


def lines_from_text(text):
    """Segments from raw text: a word that is empty after cleaning splits its line; letterless lines dropped."""
    segs = []
    for raw in text.split('\n'):
        cur = []
        any_word = False
        for tok in raw.split():
            w = _clean_word(tok)
            if w:
                cur.append(tuple(w))
                any_word = True
            else:
                if cur:
                    segs.append(cur)
                cur = []
        if cur:
            segs.append(cur)
    return segs


def load_gibberish():
    z = zipfile.ZipFile(GB / 'data/gibberish_transcriptions.zip')
    out = {}
    for n in sorted(z.namelist()):
        if n.endswith('.txt'):
            name = Path(n).stem.replace('Gibberish - ', '')
            out[name] = lines_from_text(z.read(n).decode('utf-8', errors='replace'))
    return out


def load_meaningful():
    z = zipfile.ZipFile(GB / 'data/meaningful.zip')
    out = {}
    for n in sorted(z.namelist()):
        if n.endswith('.txt') and n.replace('\\', '/').startswith('texts/'):
            out[Path(n).stem] = lines_from_text(z.read(n).decode('utf-8', errors='replace'))
    return out


def n_pairs(segs):
    return sum(len(s) - 1 for s in segs)


# ================================================================================================ chunking
def chunk_pairs(segs_seq, start, P):
    """Consecutive segments from index start until exactly P within-segment pairs (last segment truncated)."""
    out, got = [], 0
    i = start
    while got < P and i < len(segs_seq):
        s = segs_seq[i]
        need = P - got
        if len(s) - 1 <= need:
            if len(s) >= 2:
                out.append(s)
                got += len(s) - 1
        else:
            out.append(s[:need + 1])
            got += need
        i += 1
    return out if got == P else None


def rewrap(words_segs, lengths, rng):
    """Re-wrap a flat word stream (respecting its segment breaks) into lines with lengths drawn from `lengths`."""
    out = []
    for seg in words_segs:
        i = 0
        while i < len(seg):
            L = int(rng.choice(lengths))
            out.append(seg[i:i + max(L, 1)])
            i += max(L, 1)
    return [s for s in out if s]


# ================================================================================================ statistics
class Chunk:
    """Integer encoding of a chunk for vectorised statistics."""

    def __init__(self, segs, topk=None):
        words = [w for s in segs for w in s]
        seg_id = np.concatenate([[i] * len(s) for i, s in enumerate(segs)]).astype(np.int64)
        self.n = len(words)
        self.seg = seg_id
        first = np.zeros(self.n, bool)
        last = np.zeros(self.n, bool)
        pos = 0
        for s in segs:
            first[pos] = True
            last[pos + len(s) - 1] = True
            pos += len(s)
        self.first, self.last = first, last
        self.pair_pos = np.flatnonzero(seg_id[:-1] == seg_id[1:]) if self.n > 1 else np.array([], int)
        L1 = [w[-1] for w in words]
        F1 = [w[0] for w in words]
        L2 = [w[-2] if len(w) >= 2 else '#' for w in words]
        self.words = words
        self.L1, self.nL1 = self._enc(L1, topk)
        self.F1, self.nF1 = self._enc(F1, topk)
        self.L2, self.nL2 = self._enc(L2, topk)
        wid = {}
        self.wid = np.array([wid.setdefault(w, len(wid)) for w in words])

    @staticmethod
    def _enc(vals, topk):
        if topk:
            common = [u for u, _ in Counter(vals).most_common(topk - 1)]
            m = {u: i for i, u in enumerate(common)}
            return np.array([m.get(v, len(common)) for v in vals]), len(common) + 1
        m = {}
        arr = np.array([m.setdefault(v, len(m)) for v in vals])
        return arr, len(m)

    def perms(self, R, rng, edge_fixed=False):
        keys = rng.random((R, self.n))
        if edge_fixed:
            keys[:, self.first] = -1.0
            keys[:, self.last] = 2.0
            keys[:, self.first & self.last] = 0.5
        keys = keys + self.seg[None, :] * 4.0
        return np.argsort(keys, axis=1, kind='stable')


def _mi_rows(x, y, nx, ny):
    """x, y: (R, m) int arrays -> MI (bits) per row."""
    R, m = x.shape
    code = (np.arange(R)[:, None] * (nx * ny) + x * ny + y).ravel()
    J = np.bincount(code, minlength=R * nx * ny).reshape(R, nx, ny).astype(float) / m
    px = J.sum(2, keepdims=True)
    py = J.sum(1, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = J * np.log2(J / (px * py))
    return np.nansum(t, axis=(1, 2))


def _cmi_rows(x, y, z, nx, ny, nz):
    """I(X;Y|Z) per row, bits."""
    R, m = x.shape
    base = np.arange(R)[:, None]
    J = np.bincount((base * (nx * ny * nz) + (z * nx + x) * ny + y).ravel(),
                    minlength=R * nx * ny * nz).reshape(R, nz, nx, ny).astype(float) / m
    pz = J.sum((2, 3), keepdims=True)
    pxz = J.sum(3, keepdims=True)
    pyz = J.sum(2, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = J * np.log2(J * pz / (pxz * pyz))
    return np.nansum(t, axis=(1, 2, 3))


def stat_S1(C, order):
    """order: (R, n) permutations (row 0 may be identity)."""
    a = order[:, C.pair_pos]
    b = order[:, C.pair_pos + 1]
    return _mi_rows(C.L1[a], C.F1[b], C.nL1, C.nF1)


def stat_S2(C, order):
    a = order[:, C.pair_pos]
    b = order[:, C.pair_pos + 1]
    return _cmi_rows(C.L2[a], C.F1[b], C.L1[a], C.nL2, C.nF1, C.nL1)


def stat_S3(C, order):
    """I(F1(word at position); zone(position)); zone from fixed positions."""
    zone = np.where(C.first, 0, np.where(C.last, 2, 1))
    zone = np.where(C.first & C.last, 0, zone)
    f = C.F1[order]
    return _mi_rows(f, np.broadcast_to(zone, f.shape), C.nF1, 3)


def shuffle_corrected(C, stat, R, rng, edge_fixed=False):
    """Returns (observed, null_mean, p_one_sided, excess)."""
    ident = np.arange(C.n)[None, :]
    obs = float(stat(C, ident)[0])
    null = stat(C, C.perms(R, rng, edge_fixed))
    return obs, float(null.mean()), float((1 + (null >= obs).sum()) / (1 + R)), obs - float(null.mean())


def repetition_S4(C):
    pp = C.pair_pos
    O = int((C.wid[pp] == C.wid[pp + 1]).sum())
    X = 0.0
    for s in np.unique(C.seg):
        ids = C.wid[C.seg == s]
        if len(ids) < 2:
            continue
        cnt = np.bincount(ids)
        X += float((cnt * (cnt - 1)).sum()) / len(ids)
    return float(np.log((O + 0.5) / (X + 0.5)))


def near_repeat_rate(C):
    def ed1(a, b):
        if a == b:
            return True
        la, lb = len(a), len(b)
        if abs(la - lb) > 1:
            return False
        if la == lb:
            return sum(x != y for x, y in zip(a, b)) <= 1
        if la > lb:
            a, b = b, a
        i = 0
        while i < len(a) and a[i] == b[i]:
            i += 1
        return a[i:] == b[i + 1:]
    pp = C.pair_pos
    if len(pp) == 0:
        return float('nan')
    return float(np.mean([ed1(C.words[p], C.words[p + 1]) for p in pp]))


def retention(C):
    """Pair-weighted E[1/n]: adjacency retained by the within-segment shuffle."""
    lens = np.bincount(C.seg)
    w = lens - 1
    ok = lens >= 2
    return float((w[ok] / lens[ok]).sum() / w[ok].sum()) if ok.any() else float('nan')


def entropy_F1(C):
    p = np.bincount(C.F1) / C.n
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())
