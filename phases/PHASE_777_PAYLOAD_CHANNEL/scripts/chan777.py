"""PHASE_777 machinery: is one glyph position per word a message channel, with the rest of the word rule-built filler?

Channels (one symbol per certain token):
  F1  first glyph unit          F2  second glyph unit ('-' if the word has one unit)
  L1  last glyph unit           L2  second-to-last glyph unit ('-' if one unit)
  GAL first gallows-family unit in the word (k, t, p, f, ckh, cth, cph, cfh) or '0'

Statistic per channel: RPT_n = the number of within-line windows of n consecutive tokens (no blocker) whose channel
symbol sequence occurs >= 2 times in the corpus (n = 5, 7), and DIST_n (distinct repeated sequences). A payload
carrying natural-language letters repeats 5- and 7-symbol runs (common words) far beyond any first-order chain.

Exact nulls (within folio x line type, cells keyed so that every key is invariant under the permutation):
  EF-F   for start-of-word channels: cells = (group, zone, own last two units, preceding token's last two units).
         Every slot keeps its last two units, so every slot's preceding ending is invariant. P(word start | preceding
         ending, own ending) is preserved: the junction coupling and the routing survive; the START symbol sequence is
         scrambled among words with the same ending that follow the same ending.
  EF-L   for end-of-word channels: cells = (group, zone, own first unit, following token's first unit). Every slot keeps
         its first unit, so every slot's following start is invariant. P(word ending | own start, following start) is
         preserved; the END symbol sequence is scrambled.
  EF-K2  for interior channels: cells = (group, zone, first unit, last two units, preceding last two units)
         (PHASE_776); edges and routing preserved, interiors scrambled.
D = RPT(corpus) - mean RPT(null); p = (1 + #{null >= obs}) / (1 + R).
"""
from __future__ import annotations

import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
GALLOWS = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
NS = (5, 7)


def _imp(name, rel):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


E = _imp('ef774', 'phases/PHASE_774_VARIANT_MERGE/scripts/ef774.py')
GK = _imp('gen775', 'phases/PHASE_775_BOUNDARY_KEY/scripts/gen775.py')
G = GK.G
HR = G.HR
HR2 = G.HR2


def units(w):
    return GLYPH_RE.findall(w)


CHANNELS = {
    'F1': lambda w: units(w)[0],
    'F2': lambda w: (units(w)[1] if len(units(w)) > 1 else '-'),
    'L1': lambda w: units(w)[-1],
    'L2': lambda w: (units(w)[-2] if len(units(w)) > 1 else '-'),
    'GAL': lambda w: next((u for u in units(w) if u in GALLOWS), '0'),
}
CHANNEL_NULL = {'F1': 'EF-F', 'F2': 'EF-F', 'L1': 'EF-L', 'L2': 'EF-L', 'GAL': 'EF-K2'}


# ------------------------------------------------------------------------------------------------ exact nulls
def _reset_cells(C, keys):
    """Install per-position cell keys (None for blockers) into an ef774.Corpus."""
    n = len(C.tok)
    cell_key = {}
    cell = np.full(n, -1, dtype=np.int64)
    for p in range(n):
        if C.tok[p] >= 0:
            cell[p] = cell_key.setdefault(keys[p], len(cell_key))
    C.cell = cell
    C.n_cells = len(cell_key)
    movable = cell >= 0
    C.mpos = np.flatnonzero(movable)
    C.P = C.mpos[np.argsort(cell[C.mpos], kind='stable')]
    cs = np.bincount(cell[C.mpos], minlength=len(cell_key))
    C.cell_sizes = cs
    C.frac_movable = float(cs[cs >= 2].sum() / max(1, movable.sum()))
    return C


def build_null(lines, groups, kind):
    C = E.Corpus(lines, groups, sig=E.sig_fl2, ns=(2,))
    n = len(C.tok)
    first = [units(w)[0] for w in C.vocab]
    last2 = [tuple(units(w)[-2:]) for w in C.vocab]
    gid = C.fol_of                          # group ids (folio x line type when groups are ef_groups)
    keys = [None] * n
    for p in range(n):
        t = C.tok[p]
        if t < 0:
            continue
        z = int(C.zone[p])
        g = int(gid[p])
        if kind == 'EF-F':
            prev = ('^',) if (p == 0 or C.line_of[p - 1] != C.line_of[p] or C.tok[p - 1] < 0) else last2[C.tok[p - 1]]
            keys[p] = (g, z, last2[t], prev)
        elif kind == 'EF-L':
            nxt = '$' if (p == n - 1 or C.line_of[p + 1] != C.line_of[p] or C.tok[p + 1] < 0) else first[C.tok[p + 1]]
            keys[p] = (g, z, first[t], nxt)
        elif kind == 'EF-K2':
            prev = ('^',) if (p == 0 or C.line_of[p - 1] != C.line_of[p] or C.tok[p - 1] < 0) else last2[C.tok[p - 1]]
            keys[p] = (g, z, first[t], last2[t], prev)
        else:
            raise ValueError(kind)
    return _reset_cells(C, keys)


# ------------------------------------------------------------------------------------------------ statistics
class Channel:
    def __init__(self, C, fn):
        ids = {}
        self.sym = np.array([ids.setdefault(fn(w), len(ids)) for w in C.vocab], dtype=np.int64)
        self.S = len(ids)
        self.C = C
        n = len(C.tok)
        blk = C.tok < 0
        self.win = {}
        for nn in NS:
            st = np.arange(n - nn + 1)
            ok = C.line_of[st] == C.line_of[st + nn - 1]
            for k in range(nn):
                ok &= ~blk[st + k]
            self.win[nn] = st[ok]

    def counts(self, tok):
        s = self.sym[np.where(tok >= 0, tok, 0)]
        out = {}
        for nn in NS:
            w = self.win[nn]
            key = s[w]
            for k in range(1, nn):
                key = np.unique(key * self.S + s[w + k], return_inverse=True)[1].ravel().astype(np.int64)
            _, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
            rep = cnt[inv.ravel()] >= 2
            out[f'RPT{nn}'] = int(rep.sum())
            out[f'DIST{nn}'] = int((cnt >= 2).sum())
        return out


def _summ(o, v, R):
    v = np.asarray(v, dtype=float)
    sd = float(v.std(ddof=1))
    return {'obs': int(o), 'null_mean': float(v.mean()), 'null_sd': sd, 'D': float(o - v.mean()),
            'z': float((o - v.mean()) / max(sd, 1e-9)), 'p': float((1 + (v >= o).sum()) / (1 + R))}


def run(lines, groups, R=200, seed=0, channels=tuple(CHANNELS)):
    rng = np.random.default_rng(seed)
    out = {}
    corp = {}
    for ch in channels:
        kind = CHANNEL_NULL[ch]
        if kind not in corp:
            corp[kind] = build_null(lines, groups, kind)
        C = corp[kind]
        K = Channel(C, CHANNELS[ch])
        obs = K.counts(C.tok)
        null = [K.counts(C.sample(rng)) for _ in range(R)]
        out[ch] = {st: _summ(obs[st], [x[st] for x in null], R) for st in obs}
        out[ch]['_null'] = kind
        out[ch]['_cells'] = {'n_cells': C.n_cells, 'frac_movable': C.frac_movable, 'symbols': K.S}
    return out


# ------------------------------------------------------------------------------------------------ payload controls
_POOLS = None


def b_pools(sk):
    """B's tokens by (channel symbol) and by (preceding ending, channel symbol), for start channels; the marginal of
    each channel. Exposure: adjacent pairs keyed by ending (the same class as the edge generators)."""
    global _POOLS
    if _POOLS is not None:
        return _POOLS
    by_sym = {ch: defaultdict(Counter) for ch in CHANNELS}
    by_ctx = {ch: defaultdict(Counter) for ch in CHANNELS}
    for ln in sk['lines']:
        prev = None
        for w in ln:
            if w is None:
                prev = None
                continue
            ctx = ('^',) if prev is None else tuple(units(prev)[-2:])
            for ch, fn in CHANNELS.items():
                s = fn(w)
                by_sym[ch][s][w] += 1
                by_ctx[ch][(ctx, s)][w] += 1
            prev = w
    _POOLS = {'by_sym': by_sym, 'by_ctx': by_ctx}
    return _POOLS


def letter_stream(words, n, offset=0):
    """The plaintext as a letter stream (a-z only), n letters from `offset` letters in."""
    s = ''.join(re.sub(r'[^a-z]', '', w.lower()) for w in words)
    assert offset + n <= len(s), f'plaintext too short: {len(s)} letters'
    return list(s[offset:offset + n])


def payload_lines(stream, sk, channel, seed, routing=True):
    """Trithemius-style: each plaintext letter is written as a B-like word whose `channel` symbol stands for the letter
    (letters mapped to symbols by frequency rank, many-to-one when the letters outnumber the symbols), the rest of the
    word filler drawn from B's tokens with that symbol -- preferring, when routing=True, tokens that follow the
    preceding ending in B (the junction rule kept as far as the payload allows)."""
    rng = np.random.default_rng(seed)
    P = b_pools(sk)
    marg = Counter({s: sum(c.values()) for s, c in P['by_sym'][channel].items()})
    lc = Counter(stream)
    letters = sorted(lc, key=lambda x: (-lc[x], x))
    syms = [s for s, _ in sorted(marg.items(), key=lambda x: (-x[1], str(x[0])))]
    # deficit matching of letters onto the channel's marginal
    tot = sum(marg.values())
    n = len(stream)
    import heapq
    heap = [(-marg[s] / tot * n, s) for s in syms]
    heapq.heapify(heap)
    lmap = {}
    for L in letters:
        negd, s = heapq.heappop(heap)
        lmap[L] = s
        heapq.heappush(heap, (negd + lc[L], s))
    cache = {}

    def draw(key, counter):
        if key not in cache:
            ks = list(counter)
            p = np.array([counter[k] for k in ks], dtype=float)
            cache[key] = (ks, np.cumsum(p / p.sum()))
        ks, cum = cache[key]
        return ks[min(int(np.searchsorted(cum, rng.random())), len(ks) - 1)]
    out, it = [], iter(stream)
    for ln in sk['lines']:
        prev, cur = None, []
        for w in ln:
            if w is None:
                cur.append(None)
                prev = None
                continue
            s = lmap[next(it)]
            ctx = ('^',) if prev is None else tuple(units(prev)[-2:])
            pool = P['by_ctx'][channel].get((ctx, s)) if routing else None
            t = draw((ctx, s), pool) if pool and sum(pool.values()) >= 3 else draw(('S', s), P['by_sym'][channel][s])
            cur.append(t)
            prev = t
        out.append(cur)
    return out, lmap


def twin_letters(stream, sk, seed):
    return G.twin_stream(stream, sk, seed)
