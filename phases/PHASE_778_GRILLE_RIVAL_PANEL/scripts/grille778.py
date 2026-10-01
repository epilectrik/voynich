"""PHASE_778 -- Rival-generator panel II: the table-and-grille method (Rugg 2004; Hyde & Rugg 2014 'Hoaxing the
Voynich Manuscript, part 7: producing the text'; Rugg & Taylor 2016; Zandbergen 2021).

Published mechanics implemented (quotations verified against the Hyde & Rugg page, results/hyde_rugg_2014_part7.html):
  TABLE   'The table is divided into sets of three columns' (prefix | root | suffix), R rows deep ('about forty rows
          deep'), G column sets across; filled 'one category at a time' with fragment frequencies 'similar to the
          frequencies in Voynichese'; 'Some of the cells are empty. That's deliberate.'
  GRILLE  a card with three holes, one per column, at different heights: row offsets (0, o1, o2).
  MOVE    the next word = three cells across (the next column set) and an arbitrary number of rows up or down:
          'you can't simply move it three cells to the right horizontally ... The key thing is not to have any regular
          pattern in those vertical moves.'
  LINE    at the end of a line on the page: 'move your grille back to the first three columns of the table, a bit
          further down' (so the k-th word of a line comes from the k-th column set); if the last column set is reached
          before the line ends ('use the grille in some way to generate more words'), continue from the first set.
  REPEAT  the same word twice in a row: 'simply write it down and keep going' (keep) or 'move the grille further up or
          down so that you get a different word' (avoid).
  TABLES  'You'll eventually need to produce a different table'; assistants 'using different tables and grilles'.
Beyond the published description (declared tiers, see PRE_REGISTRATION.md): real rows (Zandbergen 2021 / M5b),
frequency- and length-ordered rows (Rugg & Taylor), the same-height grille, per-word random placement (the public
implementations' rule), per-word grille changes; and the exposed steelman: CHAIN rows and JUNCTION REDRAW, both built
from B's adjacent edge-glyph bigram table (the G-EDGE exposure class).

Corpus format: list of lines of tokens / None blockers on B's skeleton (PHASE_757 harness conventions); the panel
statistics are PHASE_757's panel_stats (D2-D6), unchanged.
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
import naibbe_harness as H757  # noqa: E402  (noise model, M1, G-EDGE positive controls)
import panel_stats as S  # noqa: E402  (D2-D6, descriptives)

GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
CORE_STOLFI = ('cth', 'ckh', 'cph', 'cfh', 't', 'p', 'k', 'f')
MANTLE_STOLFI = ('ch', 'sh', 'ee')
_MORPH = None


def units(w):
    return GLYPH_RE.findall(w)


# ================================================================================================ skeleton
def skeleton():
    """Currier B, H track, P placement, labels excluded; uncertain tokens are blockers (PHASE_756/757 data), with the
    section and the paragraph-first flag per line."""
    from scripts.voynich import Transcript
    tx = Transcript()
    lines, meta = defaultdict(list), {}
    for t in tx.currier_b(exclude_uncertain=False):
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if not w:
            continue
        key = (t.folio, t.line)
        lines[key].append(None if t.is_uncertain else w)
        if key not in meta:
            meta[key] = (t.folio, t.section, bool(t.par_initial))
    keys = list(lines)
    B = [lines[k] for k in keys]
    return {'lines': B, 'folio': [meta[k][0] for k in keys], 'section': [meta[k][1] for k in keys],
            'par_initial': [meta[k][2] for k in keys], 'keys': keys,
            'n_certain': sum(w is not None for ln in B for w in ln)}


# ================================================================================================ parsers
def parse_stolfi(w):
    """Stolfi-layer split (M5's rule): the first core glyph (gallows) or, failing that, the first mantle glyph
    (ch, sh, ee) is the root; everything before is the prefix, everything after the suffix."""
    for pool in (CORE_STOLFI, MANTLE_STOLFI):
        best = None
        for g in pool:
            i = w.find(g)
            if i >= 0 and (best is None or i < best[0]):
                best = (i, g)
        if best:
            i, g = best
            return w[:i], g, w[i + len(g):]
    return ('', w[0], w[1:]) if w else ('', '', '')


def parse_morph(w):
    """The project's morphology (scripts/voynich.py): prefix = articulator + PREFIX, root = MIDDLE, suffix = SUFFIX.
    Tokens the morphology cannot rebuild are kept whole as a root."""
    global _MORPH
    if _MORPH is None:
        from scripts.voynich import Morphology
        _MORPH = Morphology()
    e = _MORPH.extract(w)
    l, c, r = (e.articulator or '') + (e.prefix or ''), e.middle or '', e.suffix or ''
    return (l, c, r) if l + c + r == w else ('', w, '')


PARSERS = {'morph': parse_morph, 'stolfi': parse_stolfi}


def inventory(sk, parser):
    """Fragment inventories from B's certain tokens (unigram exposure): triples (real words split), the three column
    marginals, the whole-word roots the morphology could not split, the edge-glyph bigram table (CHAIN rows and
    JUNCTION REDRAW only; the G-EDGE exposure class) and its conditional form."""
    p = PARSERS[parser]
    trip, L, C, R, whole = Counter(), Counter(), Counter(), Counter(), set()
    edge = Counter()
    for ln in sk['lines']:
        prev = None
        for w in ln:
            if w is None:
                prev = None
                continue
            l, c, r = p(w)
            if parser == 'morph' and l == '' and r == '' and c == w and len(w) > 1 and _MORPH.extract(w).middle != w:
                whole.add(w)
            trip[(l, c, r)] += 1
            L[l] += 1
            C[c] += 1
            R[r] += 1
            if prev is not None:
                edge[(units(prev)[-1], units(w)[0])] += 1
            prev = w
    cond = defaultdict(dict)
    for (a, b), n in edge.items():
        cond[a][b] = n
    cond = {a: {b: n / sum(d.values()) for b, n in d.items()} for a, d in cond.items()}
    cmax = {a: max(d.values()) for a, d in cond.items()}
    return {'triples': trip, 'L': L, 'C': C, 'R': R, 'edge': edge, 'cond': cond, 'cmax': cmax, 'whole': whole,
            'types': set(w for ln in sk['lines'] for w in ln if w is not None)}


# ================================================================================================ tables
def _sample(items, counts, size, alpha, rng):
    w = np.asarray(counts, float) ** alpha
    idx = rng.choice(len(items), size=size, p=w / w.sum())
    return [items[i] for i in idx]


def fill(inv, cfg, rng):
    """T = R x G entries, drawn fresh for every member. 'indep': each column drawn independently from its marginal
    (Rugg: one category at a time); 'real': rows are real B words split in three (Zandbergen / M5b). Draw weight =
    frequency ** alpha. Entries are never placed in transcript order."""
    T = cfg['R'] * cfg['G']
    if cfg['rows'] == 'real':
        items = list(inv['triples'])
        return _sample(items, [inv['triples'][t] for t in items], T, cfg['alpha'], rng)
    cols = []
    for col in ('L', 'C', 'R'):
        items = list(inv[col])
        cols.append(_sample(items, [inv[col][t] for t in items], T, cfg['alpha'], rng))
    return list(zip(*cols))


def _entry_freq(e, inv, rows):
    if rows == 'real':
        return inv['triples'][e]
    return inv['L'][e[0]] * inv['C'][e[1]] * inv['R'][e[2]]


def arrange(ent, cfg, inv, rng):
    """Row-major reading order of the entries (consecutive column sets of one row are consecutive entries)."""
    order = cfg['order']
    n = len(ent)
    if order == 'random':
        return [ent[i] for i in rng.permutation(n)]
    tie = rng.random(n)
    if order == 'freq':
        key = [(-_entry_freq(e, inv, cfg['rows']), tie[i]) for i, e in enumerate(ent)]
    elif order == 'length':
        key = [(len(''.join(e)), tie[i]) for i, e in enumerate(ent)]
    elif order == 'chain':
        return _chain(ent, inv['edge'], rng)
    else:
        raise ValueError(order)
    return [ent[i] for i in sorted(range(n), key=lambda i: key[i])]


def _chain(ent, edge, rng):
    """STEELMAN (exposed): greedy arrangement so that the first glyph unit of the next entry follows the last unit of
    the previous one with B's edge-bigram preference (floor 0.1 per available entry)."""
    groups = defaultdict(list)
    for e in ent:
        w = ''.join(e)
        groups[units(w)[0] if w else ''].append(e)
    for g in groups.values():
        rng.shuffle(g)
    firsts = list(groups)
    pref = {u: np.array([edge.get((u, f), 0) + 0.1 for f in firsts]) for u in set(b for _, b in edge) | set(a for a, _ in edge)}
    flat = np.array([0.1] * len(firsts))
    out, cur, remaining = [], None, len(ent)
    while remaining:
        avail = np.array([len(groups[u]) for u in firsts], float)
        w = avail * (pref.get(cur, flat) if cur is not None else 1.0)
        u = firsts[rng.choice(len(firsts), p=w / w.sum())]
        e = groups[u].pop()
        out.append(e)
        remaining -= 1
        ww = ''.join(e)
        cur = units(ww)[-1] if ww else cur
    return out


class Table:
    def __init__(self, entries, R, G):
        assert len(entries) == R * G
        self.R, self.G = R, G
        self.L = [e[0] for e in entries]
        self.C = [e[1] for e in entries]
        self.S = [e[2] for e in entries]

    def word(self, r, g, grille):
        o1, o2 = grille
        R, G = self.R, self.G
        return self.L[(r % R) * G + g] + self.C[((r + o1) % R) * G + g] + self.S[((r + o2) % R) * G + g]


def build_table(inv, cfg, rng):
    return Table(arrange(fill(inv, cfg, rng), cfg, inv, rng), cfg['R'], cfg['G'])


# ================================================================================================ generator
GRILLE_SETS = {
    'distinct': [(o1, o2) for o1 in range(1, 5) for o2 in range(1, 5) if o1 != o2],   # three different heights, window <= 5
    'all': [(o1, o2) for o1 in range(3) for o2 in range(3)],                           # window 3, equal heights allowed
    'same': [(0, 0)],                                                                   # holes at one height (word = row)
}
DEFAULT = {'parser': 'morph', 'rows': 'indep', 'alpha': 1.0, 'order': 'random', 'R': 40, 'G': 16, 'd': 5,
           'pos': 'reset', 'repeat': 'keep', 'redraw': False, 'scope': 'all', 'n_tab': 1, 's_tab': 0.5,
           'grilles': 'distinct', 's_gr': 0.05, 'd_line': (1, 3)}


def generate(sk, inv, cfg, rng):
    """One corpus on B's skeleton. Tables are drawn fresh. The walker state (row r, column set g, grille, table)
    carries across lines within a scope unit (corpus / section / folio); a new unit starts with a fresh table set.
    d: int = vertical shift range per word; 'R' = a uniformly random row per word; 'RP' = a uniformly random row and
    column set per word (the public implementations' placement). s_gr: probability of a new grille at a line start,
    or 'word' = a new grille for every word. redraw: junction redraw (STEELMAN, exposed): accept the word with
    probability P_B(first unit | previous last unit) / max over first units, otherwise shift the grille vertically and
    redraw (at most 10 tries, then keep)."""
    cfg = {**DEFAULT, **cfg}
    R, G, d = cfg['R'], cfg['G'], cfg['d']
    grilles = GRILLE_SETS[cfg['grilles']]
    scope = cfg['scope']
    unit_of = (lambda li: 'all') if scope == 'all' else (lambda li: sk['section'][li]) if scope == 'section' \
        else (lambda li: sk['folio'][li])
    dmax = R if d in ('R', 'RP') else max(int(d), 1)
    s_gr = cfg['s_gr']
    tables, out = {}, []
    cur_unit, tabs, ti, r, g, grille = None, None, 0, 0, 0, grilles[0]
    dl_lo, dl_hi = cfg['d_line']
    info = {'empty_redraws': 0, 'repeat_redraws': 0, 'junction_redraws': 0, 'whole_root_affixed': 0, 'n_units': 0}
    whole = inv['whole']
    cond, cmax = inv['cond'], inv['cmax']

    def advance():
        nonlocal r, g
        if d == 'RP':
            r, g = int(rng.integers(R)), int(rng.integers(G))
            return
        g += 1
        if g == G:
            g = 0
            r = (r + 1) % R
        r = int(rng.integers(R)) if d == 'R' else (r + int(rng.integers(-d, d + 1))) % R

    for li, ln in enumerate(sk['lines']):
        u = unit_of(li)
        if u != cur_unit:
            if u not in tables:
                tables[u] = [build_table(inv, cfg, rng) for _ in range(cfg['n_tab'])]
            cur_unit, tabs = u, tables[u]
            ti, r, g = int(rng.integers(cfg['n_tab'])), int(rng.integers(R)), 0
            grille = grilles[int(rng.integers(len(grilles)))]
        if sk['par_initial'][li] and cfg['n_tab'] > 1 and rng.random() < cfg['s_tab']:
            ti, r = int(rng.integers(cfg['n_tab'])), int(rng.integers(R))
        if s_gr != 'word' and rng.random() < s_gr:
            grille = grilles[int(rng.integers(len(grilles)))]
        if cfg['pos'] == 'reset' and d != 'RP':
            g = 0
            r = (r + int(rng.integers(dl_lo, dl_hi + 1))) % R
        tab = tabs[ti]
        prev, new = None, []
        for w in ln:
            if w is None:
                new.append(None)
                prev = None
                continue
            if s_gr == 'word':
                grille = grilles[int(rng.integers(len(grilles)))]
            if d == 'RP':
                r, g = int(rng.integers(R)), int(rng.integers(G))
            word = tab.word(r, g, grille)
            tries = 0
            while (not word or (cfg['repeat'] == 'avoid' and word == prev)) and tries < 8:
                r = (r + int(rng.integers(-dmax, dmax + 1))) % R
                word = tab.word(r, g, grille)
                tries += 1
                info['empty_redraws' if not word else 'repeat_redraws'] += 1
            if cfg['redraw'] and prev is not None and word:
                pl = units(prev)[-1]
                for _ in range(10):
                    p = cond.get(pl, {}).get(units(word)[0], 0.0) / cmax.get(pl, 1.0)
                    if rng.random() < p:
                        break
                    r = (r + int(rng.integers(-dmax, dmax + 1))) % R
                    nw = tab.word(r, g, grille)
                    info['junction_redraws'] += 1
                    if nw:
                        word = nw
            if not word:
                word = 'o'
            c_frag = tab.C[(((r + grille[0]) % R) * G + g)] if d != 'RP' else None
            if c_frag in whole and len(word) > len(c_frag):
                info['whole_root_affixed'] += 1
            new.append(word)
            prev = word
            advance()
        out.append(new)
    info['n_units'] = len(tables)
    return out, info


# ================================================================================================ surface statistics
def _dist(counter):
    tot = sum(counter.values())
    return {k: v / tot for k, v in counter.items()}


def _js(p, q):
    keys = set(p) | set(q)
    P = np.array([p.get(k, 0.0) for k in keys])
    Q = np.array([q.get(k, 0.0) for k in keys])
    M = 0.5 * (P + Q)

    def kl(a, b):
        m = a > 0
        return float((a[m] * np.log2(a[m] / b[m])).sum())
    return 0.5 * kl(P, M) + 0.5 * kl(Q, M)


def composition(lines):
    toks = [w for ln in lines for w in ln if w is not None]
    return {'len': _dist(Counter(len(units(w)) for w in toks)),
            'first': _dist(Counter(units(w)[0] for w in toks)),
            'last': _dist(Counter(units(w)[-1] for w in toks))}


def surface(lines, folios, b=None, types_b=None):
    """Composition-level statistics only (the fit stage): types, hapax type fraction, Zipf slope, mean token length,
    adjacent- and distant-folio type-set Jaccard, and the Jensen-Shannon divergences (bits) of the token-length,
    first-glyph-unit and last-glyph-unit distributions from B's; attested fraction (descriptive)."""
    C = S.Corpus(lines, folios)
    desc = S.descriptives(C)
    sets, order = {}, []
    for ln, f in zip(lines, folios):
        if f not in sets:
            sets[f] = set()
            order.append(f)
        sets[f].update(w for w in ln if w is not None)
    jac = lambda a, b_: len(a & b_) / max(len(a | b_), 1)
    adj = [jac(sets[order[i]], sets[order[i + 1]]) for i in range(len(order) - 1)]
    dist = [jac(sets[order[i]], sets[order[j]]) for i in range(len(order)) for j in range(i + 10, len(order))]
    out = {'types': desc['types'], 'hapax': desc['hapax_type_fraction'], 'zipf': desc['zipf_slope'],
           'mean_len': desc['mean_token_length'], 'jac_adj': float(np.mean(adj)), 'jac_dist': float(np.mean(dist))}
    comp = composition(lines)
    if b is not None:
        for k in ('len', 'first', 'last'):
            out['js_' + k] = _js(comp[k], b['comp'][k])
    else:
        out['comp'] = comp
    if types_b is not None:
        toks = [w for ln in lines for w in ln if w is not None]
        out['attested'] = sum(w in types_b for w in toks) / len(toks)
    return out


SCALE = {'types': 500.0, 'hapax': 0.05, 'zipf': 0.10, 'mean_len': 0.30, 'jac_adj': 0.02, 'jac_dist': 0.02,
         'js_len': 0.02, 'js_first': 0.02, 'js_last': 0.02}
DECLARED_FITTED = 1.0          # the declared tolerance; C2 (pre-lock control) showed B's own resampler cannot reach it
PARTIAL_BOUND = 2.0            # declared tolerance
_FITTED_BOUND = None


def fitted_bound():
    """FITTED bar calibrated on the positive controls (confirmation-pass edit 1): the larger of the M1 and G-EDGE
    nine-statistic distances recorded by prelock_controls778.py (C2), unrounded. Falls back to the declared 1.0 if
    the control file is absent."""
    global _FITTED_BOUND
    if _FITTED_BOUND is None:
        fn = OUT / 'prelock_controls778.json'
        if fn.exists():
            md = json.load(open(fn, encoding='utf-8'))['C2']['mean_distance']
            _FITTED_BOUND = float(max(md.values()))
        else:
            _FITTED_BOUND = DECLARED_FITTED
    return _FITTED_BOUND


def deviations(s, b):
    return {k: abs(s[k] - (b[k] if k in b else 0.0)) / SCALE[k] for k in SCALE}


def distance(s, b):
    return float(np.mean(list(deviations(s, b).values())))


def band(dist, bound=None):
    b = fitted_bound() if bound is None else bound
    return 'FITTED' if dist <= b else ('PARTIAL' if dist <= PARTIAL_BOUND else 'UNFITTED')


def b_surface(sk):
    fn = OUT / 'b_surface778.json'
    if fn.exists():
        return json.load(open(fn, encoding='utf-8'))
    s = surface(sk['lines'], sk['folio'])
    s.update({'js_len': 0.0, 'js_first': 0.0, 'js_last': 0.0})
    s['comp'] = {k: {str(kk): vv for kk, vv in d.items()} for k, d in s['comp'].items()}
    json.dump(s, open(fn, 'w', encoding='utf-8'), indent=1)
    return json.load(open(fn, encoding='utf-8'))


def load_b(sk):
    b = b_surface(sk)
    b['comp'] = {k: {(int(kk) if k == 'len' else kk): vv for kk, vv in d.items()} for k, d in b['comp'].items()}
    return b
