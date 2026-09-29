#!/usr/bin/env python3
"""PHASE_765 — B vs step notations, prose, gibberish and constrained non-notation. Definitions: ../PRE_REGISTRATION.md
(locked d9bb96f). Every corpus is joined into running text and re-cut to B's segment-length distribution; profile
P1-P3 per 197-pair chunk; class-balanced scaling; unit-level bootstrap decision; variants V1-V8.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import time
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'PHASE_764_HUMAN_GIBBERISH_CONTROL/scripts'))
import g764 as G  # noqa: E402
import sn765 as SN  # noqa: E402

ROOT = G.ROOT
OUT = ROOT / 'phases/PHASE_765_STEP_NOTATION_COMPARISON/results'
OUT.mkdir(parents=True, exist_ok=True)
LOG = open(OUT / 'run_log.txt', 'w', encoding='utf-8')
T0 = time.time()
P, R_SHUF, N_CH, N_CH_B, N_BOOT = 197, 200, 100, 400, 1000
RES = {'phase': 'PHASE_765', 'pre_registration_commit': 'd9bb96f'}
GLYPH_RE = G.GLYPH_RE


def log(*a):
    msg = ' '.join(str(x) for x in a)
    print(f'[{time.time() - T0:6.0f}s] {msg}', flush=True)
    LOG.write(f'[{time.time() - T0:6.0f}s] {msg}\n')
    LOG.flush()


def save():
    json.dump(RES, open(OUT / 'step_compare.json', 'w', encoding='utf-8'), indent=1,
              default=lambda o: o.item() if hasattr(o, 'item') else str(o))


# ============================================================================================ text -> streams
def norm_tok(tok, keep_case=False, digits=False):
    t = unicodedata.normalize('NFD', tok if keep_case else tok.lower())
    t = ''.join(c for c in t if c.isalnum())
    if digits:
        t = re.sub(r'\d+', '#', t)
    return t


def streams_from_paragraph_text(text, digits=False):
    """Paragraphs (blank-line separated) joined across line breaks; a token empty after normalisation splits."""
    out = []
    for para in re.split(r'\n\s*\n', text):
        cur = []
        for tok in para.split():
            w = norm_tok(tok, digits=digits)
            if w:
                cur.append(tuple(w))
            else:
                if cur:
                    out.append(cur)
                cur = []
        if cur:
            out.append(cur)
    return out


def digitise(streams):
    return [[tuple(re.sub(r'\d+', '#', ''.join(w))) for w in s] for s in streams]


def b_streams(unit='GLYPH'):
    """ZL Currier B joined within folio (uncertain spaces merged); unreadable tokens and <-> split. Returns
    list of (folio, stream)."""
    SC = G._imp('spacing765', 'phases/PHASE_761_SPACING_ROBUSTNESS/scripts/spacing_check.py')
    out = []
    cur_f, cur = None, []
    for folio, segs in SC.load():
        if folio != cur_f:
            if cur:
                out.append((cur_f, cur))
            cur_f, cur = folio, []
        for si, seg in enumerate(segs):
            if si > 0 and cur:          # drawing interruption splits
                out.append((cur_f, cur))
                cur = []
            merged = []
            for t, sep in seg:
                if sep == ',' and merged:
                    merged[-1] = (merged[-1][0] + t, merged[-1][1])
                else:
                    merged.append((t, sep))
            for t, _ in merged:
                if SC.readable(t) and t:
                    cur.append(G.units_b(t, unit))
                else:
                    if cur:
                        out.append((cur_f, cur))
                    cur = []
    if cur:
        out.append((cur_f, cur))
    return out


def gen_streams(kind, seed, unit='GLYPH', authorial=False):
    NH = G._imp('naibbe765', 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/scripts/naibbe_harness.py')
    sk = NH.load_skeleton()
    if kind == 'NAIBBE':
        m = NH.load_version('GV1')
        pt = NH.plaintext('P-REC', m)
        toks, _ = NH.gen_stream(m, pt, seed, sk['n_certain'], False)
        corpus = NH.pour(toks, sk['B'])
    else:
        corpus = NH.Timm(sk['B'], sk['folio']).generate(sk['B'], np.random.default_rng(seed))
    out = []
    cur_f, cur = None, []
    for ln, f in zip(corpus, sk['folio']):
        if authorial or f != cur_f:
            if cur:
                out.append((cur_f, cur))
            cur = []
        cur_f = f
        for w in ln:
            if w is None or not GLYPH_RE.findall(w):
                if cur:
                    out.append((cur_f, cur))
                cur = []
            else:
                cur.append(G.units_b(w, unit))
    if cur:
        out.append((cur_f, cur))
    return out


def recut(streams, lengths, rng):
    """streams: list of (label, stream). Returns list of (label, line)."""
    out = []
    for lab, s in streams:
        i = 0
        while i < len(s):
            L = max(1, int(rng.choice(lengths)))
            out.append((lab, s[i:i + L]))
            i += L
    return out


# ============================================================================================ statistics
def nr_matrix(types):
    """Boolean T x T: edit distance exactly 1 (substitution or single insertion/deletion)."""
    T = len(types)
    M = np.zeros((T, T), bool)
    exact = {w: i for i, w in enumerate(types)}
    sub = defaultdict(list)
    for i, w in enumerate(types):
        for k in range(len(w)):
            sub[(len(w), k, w[:k] + w[k + 1:])].append(i)
            d = w[:k] + w[k + 1:]
            j = exact.get(d)
            if j is not None:
                M[i, j] = M[j, i] = True
    for idx in sub.values():
        if len(idx) > 1:
            for a in idx:
                for b in idx:
                    if a != b:
                        M[a, b] = True
    return M


def chunk_stats(lines, rng):
    C = G.Chunk(lines)
    o, m, p, e = G.shuffle_corrected(C, G.stat_S1, R_SHUF, rng)
    h = G.entropy_F1(C)
    P1 = e / h if h > 0 else float('nan')
    pp = C.pair_pos
    O2 = int((C.wid[pp] == C.wid[pp + 1]).sum())
    E2 = 0.0
    for s in np.unique(C.seg):
        ids = C.wid[C.seg == s]
        if len(ids) >= 2:
            cnt = np.bincount(ids)
            E2 += float((cnt * (cnt - 1)).sum()) / len(ids)
    P2 = float(np.log((O2 + 0.5) / (E2 + 0.5)))
    types = [None] * (C.wid.max() + 1)
    for w, i in zip(C.words, C.wid):
        types[i] = w
    NR = nr_matrix(types)
    O3 = int(NR[C.wid[pp], C.wid[pp + 1]].sum())
    perm = C.perms(R_SHUF, rng)
    wa = C.wid[perm[:, pp]]
    wb = C.wid[perm[:, pp + 1]]
    E3 = float(NR[wa, wb].sum(1).mean())
    P3 = float(np.log((O3 + 0.5) / (E3 + 0.5)))
    P4 = len(set(C.words)) / C.n
    return [P1, P2, P3, P4, O2, E2, O3, E3]


def corpus_chunks(recut_lines, n, rng, first_only=False):
    """Random-start chunks of exactly P pairs from consecutive re-cut lines; returns list of (label_of_first, lines)."""
    lines = [l for _, l in recut_lines]
    labs = [lab for lab, _ in recut_lines]
    out = []
    if first_only:
        ch = G.chunk_pairs(lines, 0, P)
        return [(labs[0], ch)] if ch is not None else []
    tries = 0
    while len(out) < n and tries < n * 20:
        tries += 1
        st = int(rng.integers(0, len(lines)))
        ch = G.chunk_pairs(lines, st, P)
        if ch is not None:
            out.append((labs[st], ch))
    return out


# ============================================================================================ corpora
def build_corpora(variant=None):
    """Returns dict name -> (unit, streams as list of (label, stream))."""
    digits = variant == 'V6'
    C = {}
    unit_b = 'EVA' if variant == 'V1' else 'GLYPH'
    if variant == 'V5':
        C['B'] = ('B', [(f, s) for f, segs in G.load_b_zl(True) for s in segs])
    else:
        C['B'] = ('B', b_streams(unit_b))
    thr = {'V4a': 0.25, 'V4b': 0.35}.get(variant)
    knit, prose, _ = SN.needlework(thr)
    for k, v in knit.items():
        C[k] = ('SN-KNIT', [(k, s) for s in (digitise(v) if digits else v)])
    for k, v in prose.items():
        C[k] = ('PP', [(k, s) for s in (digitise(v) if digits else v)])
    for k, v in SN.chess().items():
        if variant == 'V3':
            v = [[tuple(''.join(w).lower()) for w in s] for s in v]
        C[k] = ('SN-CHESS', [(k, s) for s in (digitise(v) if digits else v)])
    # AGC merged, identical files counted once
    seen, agc = set(), []
    for prog in ('Comanche055', 'Luminary099'):
        for f in sorted((SN.EXT / 'apollo-11' / prog).glob('*.agc')):
            h = hashlib.sha1(f.read_bytes()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            stream = []
            for line in open(f, encoding='utf-8', errors='replace'):
                for tok in line.split('#', 1)[0].split():
                    w = norm_tok(tok, digits=digits)
                    if w:
                        stream.append(tuple(w))
            if len(stream) >= 10:
                agc.append((f.stem, stream))
    C['AGC'] = ('SN-AGC', agc)
    # Latin procedural prose
    lat = {}
    t = (ROOT / 'sources/antidotarium_nicolai/antidotarium_nicolai_latin_plain.txt').read_text(encoding='utf-8', errors='replace')
    lat['LAT_antidotarium'] = t
    lat['LAT_mesue'] = (ROOT / 'sources/mesue_grabadin/mesue_grabadin_latin_full.txt').read_text(encoding='utf-8', errors='replace')
    lat['LAT_rupescissa'] = '\n'.join((ROOT / 'sources/rupescissa/rupescissa_latin_1561.txt').read_text(
        encoding='utf-8', errors='replace').split('\n')[200:])
    s = (ROOT / 'sources/sismel_testamentum/sismel_testamentum_assembled.txt').read_text(encoding='utf-8', errors='replace')
    parts = re.split(r'={10,}\nSPREAD (\d+) — ([LR])[^\n]*\n={10,}\n', s)
    pages = []
    for i in range(1, len(parts) - 2, 3):
        if parts[i + 1] == 'L' and 'TESTAMENTUM' in parts[i + 2][:400]:
            body = re.split(r'\n\s*─{5,}', parts[i + 2])[0]
            pages.append('\n'.join(l for l in body.split('\n') if 'TESTAMENTUM' not in l and not re.match(r'^\s*f\.\s*\d', l)))
    lat['LAT_sismel'] = '\n\n'.join(pages)
    for k, txt in lat.items():
        txt = txt.replace('ſ', 's')
        txt = re.sub(r'([A-Za-z])[-¬]\s*\n\s*(?:\d+\s+)?([A-Za-z])', r'\1\2', txt)
        C[k] = ('PP-L', [(k, st) for st in streams_from_paragraph_text(txt, digits)])
    # M, G
    zm = zipfile.ZipFile(G.GB / 'data/meaningful.zip')
    for n in sorted(zm.namelist()):
        if n.startswith('texts/') and n.endswith('.txt'):
            C['M_' + Path(n).stem] = ('M', [(n, st) for st in streams_from_paragraph_text(
                zm.read(n).decode('utf-8', 'replace'), digits)])
    zg = zipfile.ZipFile(G.GB / 'data/gibberish_transcriptions.zip')
    g_incl = {k for k, v in G.load_gibberish().items() if G.n_pairs(v) >= 197}
    for n in sorted(zg.namelist()):
        if n.endswith('.txt') and Path(n).stem.replace('Gibberish - ', '') in g_incl:
            raw = zg.read(n).decode('utf-8', 'replace')
            joined = re.sub(r'\n(?!\s*\n)', ' ', raw)       # join lines within the sample (blank lines stay breaks)
            C['G_' + Path(n).stem.replace('Gibberish - ', '')] = ('G', [(n, st) for st in streams_from_paragraph_text(joined, digits)])
    # CN
    unit_g = 'EVA' if variant == 'V1' else 'GLYPH'
    for r in range(5):
        C[f'CN_naibbe_{r}'] = ('CN', gen_streams('NAIBBE', 765001 + r, unit_g, authorial=(variant == 'V5')))
        C[f'CN_timm_{r}'] = ('CN', gen_streams('TIMM', 765101 + r, unit_g, authorial=(variant == 'V5')))
    rog = SN._gutenberg_body((SN.EXT / 'step_notation/gutenberg/pg10681.txt').read_text(encoding='utf-8', errors='replace'))
    C['CN_roget'] = ('CN', [('roget', st) for st in streams_from_paragraph_text(rog, digits)])
    return C


# ============================================================================================ analysis
def compute(Cdict, lengths, seed, prior=None, authorial=()):
    """Returns dict name -> (unit, array chunks x 8, chunk labels). Corpora named in `authorial` keep their own
    lines (variant V5); all others are re-cut to B's segment-length distribution."""
    rng = np.random.default_rng(seed)
    out = dict(prior or {})
    for name, (unit, streams) in Cdict.items():
        rc = streams if name in authorial else recut(streams, lengths, rng)
        n = N_CH_B if unit == 'B' else N_CH
        chs = corpus_chunks(rc, n, rng, first_only=(unit == 'G'))
        if not chs:
            continue
        vals = np.array([chunk_stats(ch, rng) for _, ch in chs])
        out[name] = (unit, vals, [lab for lab, _ in chs])
    return out


CLASSES = ['SN', 'PP', 'PP-L', 'M', 'G', 'CN']


def class_of(unit):
    return 'SN' if unit.startswith('SN') else unit


def scales(stats, cols, cov=False):
    """Class-balanced pooled within-class SD (or covariance) of chunk-level values."""
    per_class = defaultdict(list)
    for name, (unit, vals, _) in stats.items():
        if unit == 'B':
            continue
        per_class[class_of(unit)].append((unit, vals[:, cols]))
    covs = []
    for cl in CLASSES:
        items = per_class.get(cl, [])
        if not items:
            continue
        if cl == 'SN':
            subs = defaultdict(list)
            for unit, v in items:
                subs[unit].append(v)
            w, X = [], []
            for sub, vs in subs.items():
                for v in vs:
                    w.append(np.full(len(v), 1.0 / (len(subs) * len(vs) * len(v))))
                    X.append(v)
        else:
            w, X = [], []
            for unit, v in items:
                w.append(np.full(len(v), 1.0 / (len(items) * len(v))))
                X.append(v)
        w = np.concatenate(w); X = np.vstack(X)
        ok = np.all(np.isfinite(X), axis=1)
        w, X = w[ok] / w[ok].sum(), X[ok]
        mu = (w[:, None] * X).sum(0)
        D = X - mu
        covs.append((w[:, None, None] * D[:, :, None] * D[:, None, :]).sum(0))
    Cp = np.mean(covs, axis=0)
    return Cp if cov else np.sqrt(np.diag(Cp))


def distances(stats, cols, maha=False):
    bvals = stats['B'][1][:, cols]
    bprof = np.nanmedian(bvals, axis=0)
    if maha:
        Ci = np.linalg.pinv(scales(stats, cols, cov=True))
        f = lambda X: np.sqrt(np.einsum('ij,jk,ik->i', X - bprof, Ci, X - bprof))  # noqa: E731
    else:
        sd = scales(stats, cols)
        f = lambda X: np.sqrt((((X - bprof) / sd) ** 2).sum(1))  # noqa: E731
    per_chunk = {name: f(vals[:, cols]) for name, (unit, vals, _) in stats.items()}
    return per_chunk, f


def decide(stats, per_chunk, rng):
    units = defaultdict(list)
    for name, (unit, vals, _) in stats.items():
        if unit != 'B':
            units[unit].append(name)
    d = {name: float(np.nanmean(v)) for name, v in per_chunk.items()}
    med = {u: float(np.median([d[n] for n in ns])) for u, ns in units.items()}
    boots = defaultdict(list)
    for _ in range(N_BOOT):
        for u, ns in units.items():
            if len(ns) == 1:
                v = per_chunk[ns[0]]
                boots[u].append(float(np.nanmean(v[rng.integers(0, len(v), len(v))])))
            else:
                pick = rng.integers(0, len(ns), len(ns))
                boots[u].append(float(np.median([d[ns[i]] for i in pick])))
    boots = {u: np.array(v) for u, v in boots.items()}
    comp = ['M', 'PP', 'PP-L', 'G']
    wins, vs_cn, stab = {}, {}, {}
    for g in ('SN-KNIT', 'SN-CHESS', 'SN-AGC'):
        stab[g] = {k: float((boots[g] < boots[k]).mean()) for k in comp + ['CN']}
        wins[g] = all(stab[g][k] >= 0.90 for k in comp)
        vs_cn[g] = stab[g]['CN'] >= 0.90
    pairs = [(n, 'NEEDLEPROSE_' + n[5:]) for n in units.get('SN-KNIT', []) if 'NEEDLEPROSE_' + n[5:] in d]
    nearer = sum(d[a] < d[b] for a, b in pairs)
    paired = {'pairs': len(pairs), 'notation_nearer': nearer,
              'contradicts': bool(len(pairs) >= 6 and nearer < (2 / 3) * len(pairs))}
    if all(wins.values()) and all(vs_cn.values()) and not paired['contradicts']:
        verdict = 'SUPPORT'
    elif not any(wins.values()):
        verdict = 'NOT SUPPORTED'
    else:
        verdict = 'PARTIAL'
    notes = [g for g in wins if wins[g] and not vs_cn[g]]
    sn = [d[n] for u in ('SN-KNIT', 'SN-CHESS', 'SN-AGC') for n in units.get(u, [])]
    oth = [d[n] for u in comp for n in units.get(u, [])]
    mw = mannwhitneyu(sn, oth, alternative='less')
    return {'unit_median_d': med, 'stability': stab, 'wins': wins, 'beats_CN': vs_cn, 'paired': paired,
            'rule_bound_not_notation_specific': notes, 'verdict': verdict,
            'mann_whitney_corpora_p': float(mw.pvalue), 'corpus_d': d,
            'nearest10': sorted(d, key=d.get)[:10]}


def main():
    rng = np.random.default_rng(765)
    lengths = [len(s) for _, segs in G.load_b_zl(True) for s in segs]
    RES['B_segment_length_median'] = float(np.median(lengths))
    Cd = build_corpora()
    RES['corpora'] = {k: (u, len(s), sum(len(x) for _, x in s)) for k, (u, s) in Cd.items()}
    log('corpora:', {u: sum(1 for k, (uu, _) in Cd.items() if uu == u) for u in sorted({u for u, _ in Cd.values()})})
    stats = compute(Cd, lengths, 7651)
    log('stats computed for', len(stats), 'corpora')
    raw = {n: {'unit': u, 'median': np.nanmedian(v, axis=0).tolist(), 'n_chunks': len(v)} for n, (u, v, _) in stats.items()}
    RES['corpus_profiles_P1_P2_P3_P4_O2_E2_O3_E3'] = raw
    save()
    cols = [0, 1, 2]
    per_chunk, f = distances(stats, cols)
    base = decide(stats, per_chunk, np.random.default_rng(7652))
    bchunks = per_chunk['B']
    base['floor_B_self'] = float(np.nanmean(bchunks))
    # B halves split
    labs = np.array(stats['B'][2])
    fols = sorted(set(labs))
    sd = scales(stats, cols)
    hs = []
    rr = np.random.default_rng(7653)
    for _ in range(100):
        half = set(rr.choice(fols, len(fols) // 2, replace=False))
        m1 = np.array([l in half for l in labs])
        a = np.nanmedian(stats['B'][1][m1][:, cols], axis=0)
        b = np.nanmedian(stats['B'][1][~m1][:, cols], axis=0)
        hs.append(float(np.sqrt((((a - b) / sd) ** 2).sum())))
    base['B_halves_distance_median'] = float(np.median(hs))
    RES['primary'] = base
    log('PRIMARY verdict', base['verdict'], '| unit medians', {k: round(v, 3) for k, v in base['unit_median_d'].items()},
        '| wins', base['wins'], '| beats CN', base['beats_CN'], '| paired', base['paired'],
        '| floor', round(base['floor_B_self'], 3), '| halves', round(base['B_halves_distance_median'], 3))
    log('nearest10', base['nearest10'])
    save()

    # ---------------- variants
    var = {}
    pc, _ = distances(stats, [0, 1, 2, 3]); var['V2_with_P4'] = decide(stats, pc, np.random.default_rng(1))
    pc, _ = distances(stats, cols, maha=True); var['V7_mahalanobis'] = decide(stats, pc, np.random.default_rng(2))
    for nm, cc in (('V8a_drop_P1', [1, 2]), ('V8b_drop_P2', [0, 2]), ('V8c_drop_P3', [0, 1])):
        pc, _ = distances(stats, cc); var[nm] = decide(stats, pc, np.random.default_rng(3))
    log('variants V2/V7/V8', {k: v['verdict'] for k, v in var.items()})
    save()
    gens = lambda Cv: {n for n in Cv if n.startswith(('CN_naibbe', 'CN_timm'))}  # noqa: E731
    specs = {
        'V1': lambda Cv: {'B'} | gens(Cv),
        'V3': lambda Cv: {n for n, (u, _) in Cv.items() if u == 'SN-CHESS'},
        'V4a': lambda Cv: {n for n in Cv if n.startswith(('KNIT_', 'NEEDLEPROSE_'))},
        'V4b': lambda Cv: {n for n in Cv if n.startswith(('KNIT_', 'NEEDLEPROSE_'))},
        'V5': lambda Cv: {'B'} | gens(Cv),
        'V6': lambda Cv: {n for n in Cv if n != 'B' and n not in gens(Cv)},
    }
    for vname, sel in specs.items():
        Cv = build_corpora(vname)
        names = sel(Cv)
        keep = {n: v for n, v in stats.items() if n not in names}
        if vname in ('V4a', 'V4b'):
            keep = {n: v for n, v in keep.items() if not n.startswith(('KNIT_', 'NEEDLEPROSE_'))}
        auth = names if vname == 'V5' else ()
        sv = compute({n: Cv[n] for n in names}, lengths, 7660, prior=keep, authorial=auth)
        pc, _ = distances(sv, cols)
        var[vname] = decide(sv, pc, np.random.default_rng(4))
        log('variant', vname, var[vname]['verdict'], {k: round(v, 3) for k, v in var[vname]['unit_median_d'].items()})
        RES['variants'] = {k: {kk: vv for kk, vv in v.items() if kk != 'corpus_d'} for k, v in var.items()}
        save()
    # ---------------- locked verdict
    moves = [k for k, v in var.items() if {base['verdict'], v['verdict']} == {'SUPPORT', 'NOT SUPPORTED'}]
    final = 'PARTIAL' if moves else base['verdict']
    RES['verdict'] = {'primary': base['verdict'], 'variants_moving': moves, 'VERDICT': final,
                      'rule_bound_not_notation_specific': base['rule_bound_not_notation_specific']}
    RES['runtime_s'] = time.time() - T0
    log('VERDICT (locked rules):', final, '| moving variants', moves)
    save()


if __name__ == '__main__':
    main()
