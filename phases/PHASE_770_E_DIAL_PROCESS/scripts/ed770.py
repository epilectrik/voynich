"""PHASE_770 shared machinery: PHASE_769's occurrence / cell / permutation engine generalised to any spelling dial, with
the page and paragraph structure the three arms need.

Dials (outcome = marked value of one unit; frame = the token with every unit of the dial replaced by a class symbol,
e-runs collapsed, plus the unit's slot index):
  E     one e vs a run of 2+            (marked: 2+)
  CS    ch vs sh                        (marked: sh)
  KT    plain k vs plain t              (marked: t)
  MIN   i+[nrlm] with 1 vs 2+ minims    (marked: 2+)
  BENCH plain vs benched gallows        (marked: benched)
Cell = (frame, slot) x line zone x header line x paragraph-length tercile x section x hand (PHASE_769 definition).
"""
from __future__ import annotations

import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'phases/PHASE_769_E_DIAL_SETTING/scripts'))
import ed769 as E  # noqa: E402
import ed769b as B  # noqa: E402

GLYPH_RE = E.GLYPH_RE
GALLOWS = {'k': 'k', 't': 't', 'p': 'p', 'f': 'f', 'ckh': 'k', 'cth': 't', 'cph': 'p', 'cfh': 'f'}
DIALS = ('E', 'CS', 'KT', 'MIN', 'BENCH')


def _is_unit(u, dial):
    if dial == 'E':
        return u == 'e'
    if dial == 'CS':
        return u in ('ch', 'sh')
    if dial == 'KT':
        return u in ('k', 't')
    if dial == 'MIN':
        return re.fullmatch(r'i+[nrlm]', u) is not None
    if dial == 'BENCH':
        return u in GALLOWS
    raise ValueError(dial)


def _symbol(u, dial):
    return {'E': 'e', 'CS': 'X', 'KT': 'K', 'MIN': 'I' + u[-1], 'BENCH': 'G' + GALLOWS.get(u, '')}[dial]


def _marked(u, dial, run=1):
    if dial == 'E':
        return int(run >= 2)
    if dial == 'CS':
        return int(u == 'sh')
    if dial == 'KT':
        return int(u == 't')
    if dial == 'MIN':
        return int(len(u) >= 3)
    return int(len(u) == 3)


SPECIAL = ('KTH', 'OKOT')          # position-defined dials (need the morphology)
SPECIAL_SYMBOL = {'KTH': 'T', 'OKOT': 'O'}
_MORPH = None
_MCACHE = {}


def _morph(w):
    """(articulator, atomize prefix, first atom) from scripts.voynich.Morphology, cached."""
    global _MORPH
    if w in _MCACHE:
        return _MCACHE[w]
    if _MORPH is None:
        from scripts.voynich import Morphology
        _MORPH = Morphology()
    try:
        a = _MORPH.atomize(w)
        e = _MORPH.extract(w)
        res = (e.articulator or '', a.prefix or '', a.atoms[0] if a.atoms else None)
    except Exception:                                  # unparseable token: no special unit
        res = ('', '', None)
    _MCACHE[w] = res
    return res


def special_units(w, g, dial):
    """Glyph indices -> outcome for the position-defined dials:
    KTH  plain k / t as the HEAD atom (first atom after the prefix; e.g. qok-, chk-, sht-), marked value t;
    OKOT the gallows of an ok / ot prefix (the sister-prefix choice), marked value t."""
    art, pre, head = _morph(w)
    c2g, c = {}, 0
    for i, u in enumerate(g):
        c2g[c] = i
        c += len(u)
    if dial == 'KTH':
        if head is None or head[1] != 'HEAD' or head[0] not in ('k', 't'):
            return {}
        gi = c2g.get(len(art) + len(pre))
    elif dial == 'OKOT':
        if pre not in ('ok', 'ot'):
            return {}
        gi = c2g.get(len(art) + 1)
    else:
        return {}
    if gi is None or g[gi] not in ('k', 't'):
        return {}
    return {gi: int(g[gi] == 't')}


def units(w, dials):
    """For a token and a tuple of dials: {dial: [(outcome, glyph start, glyph end)]} and the joint frame (every unit of
    every listed dial replaced by its class symbol; e-runs collapsed). With one dial this is the dial's own frame."""
    if isinstance(dials, str):
        dials = (dials,)
    g = GLYPH_RE.findall(w)
    spec = {d: special_units(w, g, d) for d in dials if d in SPECIAL}
    out = {d: [] for d in dials}
    fr = []
    i = 0
    while i < len(g):
        u = g[i]
        hit = None
        for d in dials:
            if (i in spec[d]) if d in SPECIAL else _is_unit(u, d):
                hit = d
                break
        if hit == 'E':
            j = i
            while j < len(g) and g[j] == 'e':
                j += 1
            out['E'].append((_marked(u, 'E', j - i), i, j))
            fr.append('e')
            i = j
            continue
        if hit in SPECIAL:
            out[hit].append((spec[hit][i], i, i + 1))
            fr.append(SPECIAL_SYMBOL[hit])
        elif hit is not None:
            out[hit].append((_marked(u, hit), i, i + 1))
            fr.append(_symbol(u, hit))
        else:
            fr.append(u)
        i += 1
    return out, ''.join(fr)


def load_b_h_plus(extra=('f76r',)):
    """ed769.load_b_h with the R-placement lines of the listed folios added (f76r: paragraph text coded R in H and P in
    ZL; PHASE_769's P-only filter dropped it)."""
    from scripts.voynich import Transcript
    pv = E.zl_page_vars()
    rows = []
    for t in Transcript().currier_b(exclude_uncertain=False):
        pl = t.placement or ''
        if not (pl.startswith('P') or (t.folio in extra and pl.startswith('R'))):
            continue
        w = t.word.strip()
        if not w:
            continue
        rows.append((w, t.folio, t.line, t.par_initial, t.section, '*' in w))
    return E._assemble(rows, pv)


def page_structure(recs):
    """Per line key: index on the page, page line count, paragraph order on the page, header / paragraph-final flags."""
    folio_lines, par_lines, par_order = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in recs:
        f, key, pid = r[1], r[2], r[5]
        if key not in folio_lines[f]:
            folio_lines[f].append(key)
        if key not in par_lines[pid]:
            par_lines[pid].append(key)
        if pid not in par_order[f]:
            par_order[f].append(pid)
    S = {}
    for f, keys in folio_lines.items():
        L = len(keys)
        for i, k in enumerate(keys):
            S[k] = {'line': i, 'L': L, 'quarter': min(3, (4 * i) // L), 'relpos': (i + 0.5) / L,
                    'page_edge': i < 2 or i >= L - 2}
    for f, pids in par_order.items():
        for j, pid in enumerate(pids):
            keys = par_lines[pid]
            for i, k in enumerate(keys):
                S[k].update({'par_idx': j, 'n_par': len(pids), 'par_first': i == 0, 'par_last': i == len(keys) - 1,
                             'par_nlines': len(keys), 'par_line': i})
    return S


def fix_hands(recs, override):
    """Replace the hand of the listed folios (e.g. {'f115r': '3'}: blank $H in ZL, surrounded by hand 3 in Q20)."""
    return [r[:8] + (override[r[1]],) if r[1] in override else r for r in recs]


def collapsed_units(w):
    """The token's glyph units with every dial class collapsed (e-run -> e, minim group -> I+final, ch/sh -> X, any
    gallows -> G), so no dial outcome is visible (lean-expert v2 check: raw units leak E and MIN outcomes)."""
    g = GLYPH_RE.findall(w)
    out, i = [], 0
    while i < len(g):
        u = g[i]
        if u == 'e':
            while i < len(g) and g[i] == 'e':
                i += 1
            out.append('e')
            continue
        if u in ('ch', 'sh'):
            out.append('X')
        elif u in GALLOWS:
            out.append('G')
        elif re.fullmatch(r'i+[nrlm]', u):
            out.append('I' + u[-1])
        else:
            out.append(u)
        i += 1
    return out


def line_context(recs):
    """Per (line key, position): the last two collapsed units of the preceding token on the line ('prev', primary; C2082
    places boundary routing there) and its last collapsed unit ('prev1', sensitivity); 'START' for the first token, 'GAP'
    when the preceding token was dropped as uncertain. Per line key: collapsed-unit count, fullness = count / the
    page's median line count, and its tercile over all lines. Collapsed units keep dial outcomes out of both."""
    by_line = defaultdict(dict)
    for r in recs:
        by_line[r[2]][r[3]] = r[0]
    prev, prev1, glyphs = {}, {}, {}
    for key, toks in by_line.items():
        glyphs[key] = sum(len(collapsed_units(w)) for w in toks.values())
        for p in toks:
            if p == 0:
                prev[(key, p)] = prev1[(key, p)] = 'START'
            elif p - 1 in toks:
                cu = collapsed_units(toks[p - 1])
                prev[(key, p)] = '.'.join(cu[-2:])
                prev1[(key, p)] = cu[-1]
            else:
                prev[(key, p)] = prev1[(key, p)] = 'GAP'
    page = defaultdict(list)
    for key, g in glyphs.items():
        page[key[0]].append(g)
    med = {f: float(np.median(v)) for f, v in page.items()}
    full = {key: g / med[key[0]] if med[key[0]] > 0 else 1.0 for key, g in glyphs.items()}
    cut = np.quantile(np.array(list(full.values())), [1 / 3, 2 / 3])
    full3 = {key: 0 if v <= cut[0] else (1 if v <= cut[1] else 2) for key, v in full.items()}
    return prev, prev1, full, full3


def occurrences(recs, dial, amap=None, pair_dials=None, cell_extra=(), amapZ=None, par_init=None):
    """Occurrence arrays for one dial. pair_dials: the dials whose units are abstracted in the split key 'jkey' (the
    joint frame), so that a token-type split for a pair of dials never breaks either dial's frame. cell_extra: extra
    attributes appended to the cell, from 'prev' (last two collapsed units of the preceding token, or START / GAP),
    'prev1' (last collapsed unit), 'full3' (line fullness tercile, collapsed units) and 'pos5' (position-in-line
    quintile). amap / amapZ: H -> F / H -> ZL token maps for the
    'cons' (H and F read the unit alike) and 'consZ' (H and ZL alike) flags. par_init: keep units that are the first
    glyph of a paragraph's first token (the paragraph-initial gallows); default: kept for every dial except KTH."""
    plen = Counter(r[5] for r in recs)
    q = np.quantile(np.array(list(plen.values()), dtype=float), [1 / 3, 2 / 3])
    S = page_structure(recs)
    prev_of, prev1_of, full_of, full3_of = line_context(recs)
    half, quartfar = {}, {}
    by_folio = defaultdict(list)
    for k, s in S.items():
        by_folio[k[0]].append((s['line'], k))
    for f, lst in by_folio.items():
        L = len(lst)
        cut = (L + 1) // 2
        qn = max(1, math.ceil(L / 4))
        for i, k in sorted(lst):
            half[k] = 0 if i < cut else 1
            quartfar[k] = 0 if i < qn else (1 if i >= L - qn else -1)
    par_lines = defaultdict(list)
    for r in recs:
        if r[2] not in par_lines[r[5]]:
            par_lines[r[5]].append(r[2])
    phalf = {}
    for pid_, keys in par_lines.items():                 # PHASE_769 paragraph halves (middle line of odd dropped)
        L = len(keys)
        for i, k in enumerate(keys):
            phalf[k] = -1 if L < 4 else (0 if i < L // 2 else (1 if i >= L - L // 2 else -1))
    rows = defaultdict(list)
    jd = tuple(pair_dials) if pair_dials else (dial,)
    keep_par_init = (dial != 'KTH') if par_init is None else par_init
    for w, folio, key, p, n, pid, header, sec, hand in recs:
        u, frame = units(w, dial)
        runs = u[dial]
        if not runs:
            continue
        jkey = units(w, jd)[1] if pair_dials else frame
        zone = 0 if p == 0 else (2 if p == n - 1 else 1)
        pl = 0 if plen[pid] <= q[0] else (1 if plen[pid] <= q[1] else 2)
        fw = amap.get((folio, key[1], p)) if amap is not None else None
        fu, ffr = units(fw, dial) if fw else ({dial: []}, None)
        f_ok = fw is not None and ffr == frame and len(fu[dial]) == len(runs)
        zw = amapZ.get((folio, key[1], p)) if amapZ is not None else None
        zu, zfr = units(zw, dial) if zw else ({dial: []}, None)
        z_ok = zw is not None and zfr == frame and len(zu[dial]) == len(runs)
        s = S[key]
        ctx = {'prev': prev_of[(key, p)], 'prev1': prev1_of[(key, p)], 'full3': full3_of[key],
               'pos5': min(4, (5 * p) // n)}
        extra = tuple(ctx[c] for c in cell_extra)
        for j, (y, s0, s1) in enumerate(runs):
            pig = bool(p == 0 and header and s0 == 0)
            if pig and not keep_par_init:
                continue
            rows['y'].append(y)
            rows['par_init_glyph'].append(pig)
            rows['consZ'].append(bool(z_ok and zu[dial][j][0] == y))
            rows['cell'].append(((frame, j), zone, header, pl, sec, hand) + extra)
            rows['prev'].append(ctx['prev'])
            rows['prev1'].append(ctx['prev1'])
            rows['fullness'].append(full_of[key])
            rows['pos5'].append(ctx['pos5'])
            rows['full3'].append(ctx['full3'])
            rows['to_end'].append(n - 1 - p)
            rows['folio'].append(folio)
            rows['par'].append(pid)
            rows['token'].append(frame)
            rows['jkey'].append(jkey)
            rows['word'].append(w)
            rows['half'].append(half[key])
            rows['quart'].append(quartfar[key])
            rows['quarter'].append(s['quarter'])
            rows['line_idx'].append(s['line'])
            rows['relpos'].append(s['relpos'])
            rows['page_edge'].append(s['page_edge'])
            rows['par_idx'].append(s['par_idx'])
            rows['par_line'].append(s['par_line'])
            rows['phalf'].append(phalf[key])
            rows['par_first'].append(s['par_first'])
            rows['par_last'].append(s['par_last'])
            rows['final'].append(s1 == len(GLYPH_RE.findall(w)))
            rows['cons'].append(bool(f_ok and fu[dial][j][0] == y))
            rows['line'].append(key)
    cid = {c: i for i, c in enumerate(dict.fromkeys(rows['cell']))}
    fid = {f: i for i, f in enumerate(dict.fromkeys(rows['folio']))}
    tid = {t: i for i, t in enumerate(dict.fromkeys(rows['token']))}
    jid = {t: i for i, t in enumerate(dict.fromkeys(rows['jkey']))}
    O = {'dial': dial, 'y': np.array(rows['y'], dtype=float), 'cell': np.array([cid[c] for c in rows['cell']]),
         'folio': np.array([fid[f] for f in rows['folio']]), 'par': np.array(rows['par']),
         'token': np.array([tid[t] for t in rows['token']]), 'token_str': list(tid), 'n_tokens': len(tid),
         'jkey': np.array([jid[t] for t in rows['jkey']]), 'jkey_str': list(jid), 'n_jkeys': len(jid),
         'folio_names': list(fid), 'line_keys': rows['line']}
    for k in ('half', 'quart', 'quarter', 'line_idx', 'par_idx', 'par_line', 'phalf', 'pos5', 'to_end', 'full3'):
        O[k] = np.array(rows[k])
    O['relpos'] = np.array(rows['relpos'], dtype=float)
    O['fullness'] = np.array(rows['fullness'], dtype=float)
    O['prev'] = rows['prev']
    O['prev1'] = rows['prev1']
    for k in ('page_edge', 'par_first', 'par_last', 'final', 'cons', 'consZ', 'par_init_glyph'):
        O[k] = np.array(rows[k], dtype=bool)
    O['folio_nlines'] = {fid[f]: len(v) for f, v in by_folio.items() if f in fid}
    cf = defaultdict(set)
    for c, f in zip(O['cell'], O['folio']):
        cf[c].add(f)
    O['informative'] = np.array([len(cf[c]) >= 2 for c in O['cell']])
    return O


# ------------------------------------------------------------------------------------------------ tracks, alignment
def track_lines_plus(tr, extra=('f76r',)):
    """ed769b.track_lines with the R-placement lines of the listed folios added (same filters otherwise)."""
    from scripts.voynich import Transcript
    out = defaultdict(list)
    for t in Transcript().all(h_only=False):
        if t.transcriber != tr or t.language != 'B' or t.is_label:
            continue
        pl = t.placement or ''
        if not (pl.startswith('P') or (t.folio in extra and pl.startswith('R'))):
            continue
        w = t.word.strip()
        if w:
            out[(t.folio, t.line)].append(w)
    return out


def zl_lines():
    """ZL 3b B paragraph text by (folio, ZL line id), uncertain tokens dropped (ed769.load_b_zl)."""
    out = defaultdict(list)
    for r in E.load_b_zl():
        out[r[2]].append(r[0])
    return out


def collapse_all(w):
    """Every dial class collapsed: e-runs -> e, ch/sh -> X, any gallows (plain or benched) -> G, minim groups -> I+final."""
    g = GLYPH_RE.findall(w)
    out, i = [], 0
    while i < len(g):
        u = g[i]
        if u == 'e':
            while i < len(g) and g[i] == 'e':
                i += 1
            out.append('e')
            continue
        if u in ('ch', 'sh'):
            out.append('X')
        elif u in GALLOWS:
            out.append('G')
        elif re.fullmatch(r'i+[nrlm]', u):
            out.append('I' + u[-1])
        else:
            out.append(u)
        i += 1
    return ''.join(out)


def _align_pairs(h, o):
    import difflib
    pairs = {}
    sm = difflib.SequenceMatcher(None, h, o, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal' or (op == 'replace' and i2 - i1 == j2 - j1):
            for a, b in zip(range(i1, i2), range(j1, j2)):
                pairs[a] = o[b]
    return pairs


def alignment(H, O, key_map=None):
    """H -> other-track token map per line (PHASE_758 rule) and folio legibility with every dial class collapsed
    (share of H tokens whose collapse_all form is not matched by an aligned token). key_map maps H line keys to the
    other track's keys (None: identical keys)."""
    amap, leg = {}, defaultdict(lambda: [0, 0])
    for key, h in H.items():
        o = O.get(key_map.get(key) if key_map else key)
        if o is None:
            continue
        pairs = _align_pairs(h, o)
        for i, w in enumerate(h):
            ow = pairs.get(i)
            amap[(key[0], key[1], i)] = ow
            leg[key[0]][0] += 1
            if ow is None or collapse_all(ow) != collapse_all(w):
                leg[key[0]][1] += 1
    return amap, {f: d / n for f, (n, d) in leg.items() if n}


def zl_content_map(H, Z, min_ratio=0.5):
    """Map H line keys to ZL line keys by content, page by page: each H line to the ZL line of the same page with the
    highest token-sequence similarity (difflib ratio >= min_ratio), one-to-one, greedy by similarity."""
    import difflib
    zp = defaultdict(list)
    for k in Z:
        zp[k[0]].append(k)
    cand = []
    for hk, h in H.items():
        for zk in zp.get(hk[0], []):
            r = difflib.SequenceMatcher(None, h, Z[zk], autojunk=False).ratio()
            if r >= min_ratio:
                cand.append((r, hk, zk))
    cand.sort(key=lambda x: -x[0])
    m, used = {}, set()
    for r, hk, zk in cand:
        if hk in m or zk in used:
            continue
        m[hk] = zk
        used.add(zk)
    return m
