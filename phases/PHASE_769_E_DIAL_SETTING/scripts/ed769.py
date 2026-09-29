"""PHASE_769 shared machinery: is the e-run 'dial' set per folio once the word's frame and position are held fixed?

Occurrence = one run of the glyph unit 'e' inside a token (glyph units c[tkpf]h|[cs]h|i+[nrlm]|.). For each occurrence:
  frame  = the token with every e-run collapsed to a single e, plus the run's index in the token;
  y      = 1 if the run has 2+ e's (the PHASE_758 1-vs-2+ contrast), else 0;
  cell   = (frame, run index, line zone [initial / medial / final token], header line or not,
            paragraph-length tercile, section, scribal hand).
Null: y is permuted among the occurrences of the same cell (across folios), which preserves every frame-, position-,
paragraph-length-, section- and hand-specific rate and destroys any folio-specific setting.
Residual r = y - (cell mean). Statistics:
  S1 = sum over folios of n_f * mean(r | folio)^2       (any folio dependence of the dial given the frame);
  S2 = mean over K random halvings of the frame set of the Pearson correlation, across folios with >= MIN_OCC
       occurrences in each half, between the folio's mean residual on half A and on half B
       (a folio-level setting shared ACROSS words; spelling reuse of one word cannot produce it).
Paragraph level (secondary): the same with paragraphs, permuting within cell x folio.
i-runs (secondary): the same with the minim count of i+[nrlm] groups (y = 2+ minims).
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
ZL = ROOT / 'data/transcriptions/reference/ZL_official.txt'
MIN_OCC = 5
K_SPLITS = 50


# ------------------------------------------------------------------------------------------------ hands
def zl_page_vars():
    out = {}
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
        if m:
            d = dict(re.findall(r'\$(\w)=(\w*)', m.group(2)))
            out[m.group(1)] = d
    return out


# ------------------------------------------------------------------------------------------------ corpora
def load_b_h():
    """Currier B, H track, P placement, labels excluded, uncertain tokens dropped. Returns a list of token records:
    (word, folio, line_key, pos_in_line, line_len, paragraph_id, header_line, section, hand)."""
    from scripts.voynich import Transcript
    pv = zl_page_vars()
    rows = []
    for t in Transcript().currier_b(exclude_uncertain=False):
        if not (t.placement and t.placement.startswith('P')):
            continue
        w = t.word.strip()
        if not w:
            continue
        rows.append((w, t.folio, t.line, t.par_initial, t.section, '*' in w))
    return _assemble(rows, pv)


def _assemble(rows, pv):
    """rows: (word, folio, line, par_initial, section, uncertain) in manuscript order."""
    lines = defaultdict(list)
    order = []
    for r in rows:
        key = (r[1], r[2])
        if key not in lines:
            order.append(key)
        lines[key].append(r)
    recs = []
    pid = -1
    prev_folio = None
    for key in order:
        ln = lines[key]
        header = any(r[3] for r in ln)                  # the line carries a paragraph-initial token
        if key[0] != prev_folio or header:              # a new folio, or a marked paragraph start
            pid += 1
        prev_folio = key[0]
        n = len(ln)
        for p, r in enumerate(ln):
            if r[5]:
                continue                                # uncertain token: dropped
            hand = pv.get(r[1], {}).get('H', '') or '?'
            recs.append((r[0], r[1], key, p, n, pid, header, r[4], hand))
    return recs


def load_b_zl(merge_uncertain=True):
    """Currier B, ZL 3b, P placement; paragraph starts from ZL '<%>' markers; section from the page header ($I)
    mapped to the H-track section codes via the folio; hand from $H."""
    sys.path.insert(0, str(ROOT / 'phases/PHASE_761_SPACING_ROBUSTNESS/scripts'))
    import spacing_check as SC
    pv = zl_page_vars()
    from scripts.voynich import Transcript
    sec_of = {}
    for t in Transcript().currier_b(exclude_uncertain=False):
        sec_of.setdefault(t.folio, t.section)
    rows = []
    lang = None
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', raw)
        if m:
            L = re.search(r'\$L=(\w)', m.group(2))
            lang = L.group(1) if L else None
            continue
        m = re.match(r'^<(f\w+)\.(\d+),([@+=*&~])(\w+)>\s+(.*)$', raw.rstrip('\n'))
        if not m or lang != 'B' or not m.group(4).startswith('P'):
            continue
        folio, line, text = m.group(1), m.group(2), m.group(5)
        par_start = '<%>' in text
        text = SC.clean(text)
        toks = []
        for seg in text.split('<->'):
            seg = re.sub(r'<[^>]*>', '', seg).strip()
            sep = None
            for part in re.split(r'([.,])', seg):
                if part in ('.', ','):
                    sep = part
                elif part:
                    if merge_uncertain and sep == ',' and toks:
                        toks[-1] = toks[-1] + part
                    else:
                        toks.append(part)
                    sep = None
        for i, w in enumerate(toks):
            rows.append((w, folio, line, par_start and i == 0, sec_of.get(folio, '?'), not SC.readable(w)))
    return _assemble(rows, pv)


def pour_tokens(recs, stream):
    """Replace the words of B's records with a control token stream (skeleton, strata and folios kept)."""
    it = iter(stream)
    return [(next(it),) + r[1:] for r in recs]


# ------------------------------------------------------------------------------------------------ occurrences
def e_runs(word):
    """Glyph units, the (start, length) of each e-run, and the collapsed frame string."""
    g = GLYPH_RE.findall(word)
    runs, frame, i = [], [], 0
    while i < len(g):
        if g[i] == 'e':
            j = i
            while j < len(g) and g[j] == 'e':
                j += 1
            runs.append(j - i)
            frame.append('e')
            i = j
        else:
            frame.append(g[i])
            i += 1
    return runs, ''.join(frame)


def i_runs(word):
    """Minim groups i+[nrlm]: counts of i per group, and the frame with each group collapsed to a single i."""
    g = GLYPH_RE.findall(word)
    runs, frame = [], []
    for u in g:
        m = re.fullmatch(r'(i+)([nrlm])', u)
        if m:
            runs.append(len(m.group(1)))
            frame.append('i' + m.group(2))
        else:
            frame.append(u)
    return runs, ''.join(frame)


def occurrences(recs, kind='e'):
    """Arrays for every run occurrence: y, cell id, folio idx, paragraph idx, frame idx, plus labels."""
    plen = Counter(r[5] for r in recs)
    q = np.quantile(np.array(list(plen.values()), dtype=float), [1 / 3, 2 / 3])
    fn = e_runs if kind == 'e' else i_runs
    # top / bottom half of each folio's lines (for the long-range statistic S3)
    folio_lines = defaultdict(list)
    for r in recs:
        if not folio_lines[r[1]] or folio_lines[r[1]][-1] != r[2]:
            if r[2] not in folio_lines[r[1]]:
                folio_lines[r[1]].append(r[2])
    half_of = {}
    for f, keys in folio_lines.items():
        cut = (len(keys) + 1) // 2
        for i, k in enumerate(keys):
            half_of[k] = 0 if i < cut else 1
    ys, cells, fol, par, frames, halves = [], [], [], [], [], []
    for w, folio, key, p, n, pid, header, sec, hand in recs:
        runs, frame = fn(w)
        if not runs:
            continue
        zone = 0 if p == 0 else (2 if p == n - 1 else 1)
        pl = 0 if plen[pid] <= q[0] else (1 if plen[pid] <= q[1] else 2)
        for j, L in enumerate(runs):
            ys.append(1 if L >= 2 else 0)
            fk = (frame, j)
            cells.append((fk, zone, header, pl, sec, hand))
            fol.append(folio)
            par.append(pid)
            frames.append(fk)
            halves.append(half_of[key])
    cid = {c: i for i, c in enumerate(dict.fromkeys(cells))}
    fid = {f: i for i, f in enumerate(dict.fromkeys(fol))}
    frid = {f: i for i, f in enumerate(dict.fromkeys(frames))}
    O = {'y': np.array(ys, dtype=float), 'cell': np.array([cid[c] for c in cells]),
         'folio': np.array([fid[f] for f in fol]), 'par': np.array(par), 'frame': np.array([frid[f] for f in frames]),
         'folio_names': list(fid), 'n_frames': len(frid), 'n_cells': len(cid),
         'half': np.array(halves, dtype=np.int64)}
    # informative occurrences: cells spanning >= 2 folios (only these can move under the null)
    cf = defaultdict(set)
    for c, f in zip(O['cell'], O['folio']):
        cf[c].add(f)
    O['informative'] = np.array([len(cf[c]) >= 2 for c in O['cell']])
    return O


# ------------------------------------------------------------------------------------------------ statistics
def cell_means(y, cell):
    s = np.bincount(cell, weights=y)
    n = np.bincount(cell)
    return (s / np.maximum(n, 1))[cell]


def s1(r, unit, nunits):
    s = np.bincount(unit, weights=r, minlength=nunits)
    n = np.bincount(unit, minlength=nunits)
    ok = n > 0
    return float((s[ok] ** 2 / n[ok]).sum())


def s2(r, unit, nunits, splits, min_occ=MIN_OCC):
    vals = []
    for A in splits:
        sa = np.bincount(unit[A], weights=r[A], minlength=nunits)
        na = np.bincount(unit[A], minlength=nunits)
        B = ~A
        sb = np.bincount(unit[B], weights=r[B], minlength=nunits)
        nb = np.bincount(unit[B], minlength=nunits)
        ok = (na >= min_occ) & (nb >= min_occ)
        if ok.sum() < 5:
            continue
        pa, pb = sa[ok] / na[ok], sb[ok] / nb[ok]
        if pa.std() == 0 or pb.std() == 0:
            continue
        vals.append(float(np.corrcoef(pa, pb)[0, 1]))
    return float(np.mean(vals)) if vals else float('nan')


def s3(r, unit, half, nunits, splits, min_occ=MIN_OCC):
    """Long-range cross-frame coherence: correlation across folios between the mean residual of frame-half A in the
    folio's top half of lines and of frame-half B in its bottom half (and the reverse), averaged over splits.
    Local persistence along the text (lag of a few tokens) cannot produce it."""
    vals = []
    for A in splits:
        cs = []
        for ha, hb in ((0, 1), (1, 0)):
            ma = A & (half == ha)
            mb = (~A) & (half == hb)
            sa = np.bincount(unit[ma], weights=r[ma], minlength=nunits)
            na = np.bincount(unit[ma], minlength=nunits)
            sb = np.bincount(unit[mb], weights=r[mb], minlength=nunits)
            nb = np.bincount(unit[mb], minlength=nunits)
            ok = (na >= min_occ) & (nb >= min_occ)
            if ok.sum() < 5:
                continue
            pa, pb = sa[ok] / na[ok], sb[ok] / nb[ok]
            if pa.std() == 0 or pb.std() == 0:
                continue
            cs.append(float(np.corrcoef(pa, pb)[0, 1]))
        if cs:
            vals.append(float(np.mean(cs)))
    return float(np.mean(vals)) if vals else float('nan')


def test3(O, nperm=2000, seed=769, splits_seed=7690, y=None, k_splits=K_SPLITS):
    """Folio level: S1, S2 and the long-range S3, with permutation p-values (permute within cell)."""
    rng = np.random.default_rng(seed)
    m = O['informative']
    yy = (O['y'] if y is None else y)[m]
    cell = O['cell'][m]
    _, unit = np.unique(O['folio'][m], return_inverse=True)
    unit = unit.ravel()
    half = O['half'][m]
    nunits = int(unit.max()) + 1
    splits = make_splits({'n_frames': O['n_frames'], 'frame': O['frame'][m]}, splits_seed, k_splits)
    cm = cell_means(yy, cell)
    r = yy - cm
    obs = (s1(r, unit, nunits), s2(r, unit, nunits, splits), s3(r, unit, half, nunits, splits))
    nulls = [[], [], []]
    for _ in range(nperm):
        rp = permute_within(yy, cell, rng) - cm
        nulls[0].append(s1(rp, unit, nunits))
        nulls[1].append(s2(rp, unit, nunits, splits))
        nulls[2].append(s3(rp, unit, half, nunits, splits))
    out = {'n_occ': int(m.sum()), 'n_units': nunits}
    for name, o, nv in zip(('S1', 'S2', 'S3'), obs, nulls):
        nv = np.array(nv, dtype=float)
        ok = ~np.isnan(nv)
        out[name] = o
        out[f'{name}_null_mean'] = float(nv[ok].mean()) if ok.any() else float('nan')
        out[f'{name}_null_sd'] = float(nv[ok].std(ddof=1)) if ok.sum() > 1 else float('nan')
        out[f'p_{name}'] = float((1 + (nv[ok] >= o).sum()) / (1 + ok.sum())) if (ok.any() and not np.isnan(o)) else 1.0
    out['S1_ratio'] = out['S1'] / out['S1_null_mean']
    return out


def make_splits(O, seed, k=K_SPLITS):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(k):
        half = rng.random(O['n_frames']) < 0.5
        out.append(half[O['frame']])
    return out


def permute_within(y, groups, rng):
    """Shuffle y within groups (vectorised: random keys sorted within group)."""
    order = np.lexsort((rng.random(len(y)), groups))
    ysorted = y[order]
    # positions of each group are contiguous in `order`; a second independent sort gives the permuted assignment
    order2 = np.lexsort((rng.random(len(y)), groups))
    out = np.empty_like(y)
    out[order2] = ysorted
    return out


def test(O, level='folio', nperm=2000, seed=769, splits_seed=7690, y=None):
    """Observed S1, S2 and permutation p-values at folio level (permute within cell) or paragraph level (permute
    within cell x folio). Only informative occurrences enter."""
    rng = np.random.default_rng(seed)
    m = O['informative']
    yy = (O['y'] if y is None else y)[m]
    cell = O['cell'][m]
    if level == 'folio':
        unit = O['folio'][m]
        group = cell
    else:
        unit = O['par'][m]
        _, group = np.unique(np.stack([cell, O['folio'][m]], axis=1), axis=0, return_inverse=True)
        group = group.ravel()
    _, unit = np.unique(unit, return_inverse=True)
    unit = unit.ravel()
    nunits = int(unit.max()) + 1
    Om = {'n_frames': O['n_frames'], 'frame': O['frame'][m]}
    splits = make_splits(Om, splits_seed)
    cm = cell_means(yy, group)
    r = yy - cm
    obs1, obs2 = s1(r, unit, nunits), s2(r, unit, nunits, splits)
    null1, null2 = [], []
    for _ in range(nperm):
        yp = permute_within(yy, group, rng)
        rp = yp - cm
        null1.append(s1(rp, unit, nunits))
        null2.append(s2(rp, unit, nunits, splits))
    null1, null2 = np.array(null1), np.array(null2)
    ok2 = ~np.isnan(null2)
    return {'n_occ': int(m.sum()), 'n_units': nunits, 'S1': obs1, 'S1_null_mean': float(null1.mean()),
            'S1_ratio': obs1 / float(null1.mean()), 'p_S1': float((1 + (null1 >= obs1).sum()) / (1 + nperm)),
            'S2': obs2, 'S2_null_mean': float(null2[ok2].mean()), 'S2_null_sd': float(null2[ok2].std(ddof=1)),
            'p_S2': float((1 + (null2[ok2] >= obs2).sum()) / (1 + ok2.sum()))}
