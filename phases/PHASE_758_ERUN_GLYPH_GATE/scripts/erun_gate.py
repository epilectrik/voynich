#!/usr/bin/env python3
"""PHASE_758 — e-run family gate. See ../PRE_REGISTRATION.md (locked, commit 10134f7).

Part A: cross-track consistency of e-run length (H vs F, H vs C).
Part B: C1225 — two-parser replication, segmentation migration, unsegmented k+e-run table, conditional-resampling
        nulls (order 1 / order 2), head homogeneity, track F.
Part C: C2031 D and C1967 gradient on track F, N-matched to H.
Historical parser: voynich_pre_c1957.py = scripts/voynich.py at f6015c8 (parent of a52ca08, pre-C1957).
"""
from __future__ import annotations

import difflib
import importlib.util
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology  # noqa: E402

HERE = Path(__file__).parent
OUT = ROOT / 'phases/PHASE_758_ERUN_GLYPH_GATE/results'
OUT.mkdir(parents=True, exist_ok=True)
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
SEED = 758
N_DRAWS, N_BOOT, N_BOOT_DRAWS, N_PERM = 1000, 1000, 50, 1000

spec = importlib.util.spec_from_file_location('voynich_pre_c1957', HERE / 'voynich_pre_c1957.py')
OLD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(OLD)
morph_now = Morphology()
morph_old = OLD.Morphology()
_ED = {}


def log(*a):
    print(*a, flush=True)


def e_depth(w):
    if w not in _ED:
        try:
            _ED[w] = morph_now.atomize(w).e_depth
        except Exception:
            _ED[w] = 0
    return _ED[w]


def ecls(w):
    d = e_depth(w)
    return 0 if d == 0 else (1 if d == 1 else 2)


def units(w):
    return GLYPH_RE.findall(w)


# ================================================================================================ data
tx = Transcript()
TRACK_LINES = {tr: defaultdict(list) for tr in ('H', 'F', 'C')}
H_PAR_START = {}          # (folio, line) -> True if the H line starts a paragraph
SECTION = {}
for t in tx.all(h_only=False):
    if t.transcriber not in TRACK_LINES or t.language != 'B' or t.is_label:
        continue
    if not (t.placement and t.placement.startswith('P')):
        continue
    w = t.word.strip()
    if not w:
        continue
    key = (t.folio, t.line)
    if t.transcriber == 'H' and not TRACK_LINES['H'][key]:
        H_PAR_START[key] = bool(t.par_initial)
    TRACK_LINES[t.transcriber][key].append(w)
    SECTION[t.folio] = t.section


def certain(w):
    return '*' not in w


# ================================================================================================ Part A
def align(h, x):
    """Token alignment: equal blocks 1:1; replace blocks of equal length 1:1; other blocks unaligned."""
    pairs = []
    sm = difflib.SequenceMatcher(None, h, x, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal' or (op == 'replace' and i2 - i1 == j2 - j1):
            pairs.extend(zip(h[i1:i2], x[j1:j2]))
    return pairs


def kappa(conf):
    conf = np.asarray(conf, float)
    n = conf.sum()
    po = np.trace(conf) / n
    pe = (conf.sum(0) * conf.sum(1)).sum() / n ** 2
    k = conf.shape[0]
    return {'n': int(n), 'raw_agreement': po, 'kappa': (po - pe) / (1 - pe) if pe < 1 else float('nan'),
            'pabak': (k * po - 1) / (k - 1)}


def part_a(other):
    H, X = TRACK_LINES['H'], TRACK_LINES[other]
    common = [k for k in H if k in X]
    pairs, eq_lines, dropped_density, kept_density = [], 0, [], []
    for k in common:
        h, x = H[k], X[k]
        pairs.extend((a, b) for a, b in align(h, x) if certain(a) and certain(b))
        dens = sum(len(re.findall('e+', w)) for w in h) / len(h)
        if len(h) == len(x):
            eq_lines += 1
            kept_density.append(dens)
        else:
            dropped_density.append(dens)
    # A1: same skeleton, run-by-run
    run_conf = Counter()
    for a, b in pairs:
        if re.sub('e+', 'E', a) != re.sub('e+', 'E', b):
            continue
        for ra, rb in zip(re.findall('e+', a), re.findall('e+', b)):
            run_conf[(min(len(ra), 3), min(len(rb), 3))] += 1
    a1 = {}
    for L in (1, 2, 3):
        tot = sum(v for (x_, _), v in run_conf.items() if x_ == L)
        agree = run_conf.get((L, L), 0)
        a1[f'H_run_{L}{"+" if L == 3 else ""}'] = {'n': tot, 'agreement': agree / tot if tot else None,
                                                   'to_other': {str(y): v for (x_, y), v in run_conf.items() if x_ == L}}
    # A2
    conf3 = np.zeros((3, 3), int)
    conf2 = np.zeros((2, 2), int)
    for a, b in pairs:
        ca, cb = ecls(a), ecls(b)
        conf3[ca, cb] += 1
        if ca >= 1 or cb >= 1:
            conf2[int(ca == 2), int(cb == 2)] += 1
    k2 = kappa(conf2)
    h_le1_x_2 = int(conf2[0, 1])
    h_2_x_le1 = int(conf2[1, 0])
    cls = 'CONSISTENT' if k2['kappa'] >= 0.80 else ('MODERATE' if k2['kappa'] >= 0.60 else 'FRAGILE')
    big, small = max(h_le1_x_2, h_2_x_le1), min(h_le1_x_2, h_2_x_le1)
    directional = big >= 20 and big >= 2 * max(small, 1)
    return {'other_track': other, 'lines_in_both': len(common), 'aligned_certain_pairs': len(pairs),
            'equal_count_rule': {'retained_lines': eq_lines, 'retention_rate': eq_lines / max(len(common), 1),
                                 'e_run_density_kept': float(np.mean(kept_density)) if kept_density else None,
                                 'e_run_density_dropped': float(np.mean(dropped_density)) if dropped_density else None},
            'A1_run_agreement': a1, 'A2_class3': {**kappa(conf3), 'confusion': conf3.tolist()},
            'A2_1_vs_2plus': {**k2, 'confusion_[H<=1|H2+][X<=1|X2+]': conf2.tolist(),
                              'H<=1_X2+': h_le1_x_2, 'H2+_X<=1': h_2_x_le1},
            'classification': cls, 'directional_bias': bool(directional)}


# ================================================================================================ Part B
def is_ke(mid):
    return bool(mid) and all(c in 'ke' for c in mid) and 'k' in mid and 'e' in mid


def b1(morph):
    tabs = defaultdict(Counter)
    toks = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and is_ke(m.middle):
            grp = 'single-e' if m.middle.count('e') <= 1 else 'multi-e'
            toks.append((t.word, grp, m.middle, m.suffix or ''))
            if m.suffix:
                tabs[grp][m.suffix] += 1
    out = {}
    for g in ('single-e', 'multi-e'):
        tot = sum(tabs[g].values())
        out[g] = {'n_with_suffix': tot, 'n_tokens': sum(1 for x in toks if x[1] == g),
                  'top': {s: [c, round(c / tot, 4)] for s, c in tabs[g].most_common(8)} if tot else {}}
    edy_s = out['single-e']['top'].get('edy', [0, 0])[1]
    edy_m = out['multi-e']['top'].get('edy', [0, 0])[1]
    out['reproduces_published'] = bool(abs(edy_s - 0.624) <= 0.05 and abs(edy_m - 0.118) <= 0.05)
    return out, toks


def run_after_k(w):
    m = re.search(r'k(e+)', w)
    return len(m.group(1)) if m else 0


def b2(old_toks):
    cross = defaultdict(Counter)
    for w, grp, mid, suf in old_toks:
        cross[grp][min(run_after_k(w), 3)] += 1
    single = cross['single-e']
    n = sum(single.values())
    frac = (single[2] + single[3]) / n if n else 0.0
    return {'crosstab': {g: {str(k): v for k, v in sorted(c.items())} for g, c in cross.items()},
            'single_e_fraction_run_ge2_after_k': frac, 'segmentation_artifact': bool(frac >= 0.25)}


def erun_occurrences(words):
    """Every e-run with its head (unit before the run) and next unit (END if the token ends)."""
    occ = []
    for w in words:
        u = units(w)
        i = 0
        while i < len(u):
            if u[i] == 'e':
                j = i
                while j < len(u) and u[j] == 'e':
                    j += 1
                head = u[i - 1] if i > 0 else 'START'
                nxt = u[j] if j < len(u) else 'END'
                occ.append((head, j - i, nxt))
                i = j
            else:
                i += 1
    return occ


def _h_mm(counts):
    c = counts[counts > 0].astype(float)
    n = c.sum()
    p = c / n
    return float(-(p * np.log2(p)).sum() + (len(c) - 1) / (2 * n * math.log(2)))


def mi_mm(a, b, na, nb):
    j = np.bincount(a * nb + b, minlength=na * nb)
    return _h_mm(np.bincount(a, minlength=na)) + _h_mm(np.bincount(b, minlength=nb)) - _h_mm(j)


def part_b_tables(words, label):
    occ = erun_occurrences(words)
    kocc = [(r, n) for h, r, n in occ if h == 'k']
    cnt = Counter(n for _, n in kocc)
    keep = sorted(u for u, c in cnt.items() if c >= 10)
    idx = {u: i for i, u in enumerate(keep)}
    OTHER = len(keep)
    nb = len(keep) + 1

    def code(u):
        return idx.get(u, OTHER)
    rc = np.array([0 if r == 1 else 1 for r, _ in kocc])
    nx = np.array([code(n) for _, n in kocc])
    S_real = mi_mm(rc, nx, 2, nb)
    # transition models over all run endings (next unit != e by construction)
    ord1 = Counter(n for _, _, n in occ)
    ord2 = defaultdict(Counter)
    for h, r, n in occ:
        ord2[h if r == 1 else 'e'][n] += 1

    def sampler(counter):
        ks = list(counter)
        p = np.array([counter[k] for k in ks], float)
        return np.array([code(k) for k in ks]), p / p.sum()
    s1 = sampler(ord1)
    s2_single, s2_multi = sampler(ord2['k']), sampler(ord2['e'])
    rng = np.random.default_rng(SEED)

    def draw1(n_occ):
        return rng.choice(s1[0], size=n_occ, p=s1[1])

    def draw2(rcv):
        out = np.empty(len(rcv), dtype=np.int64)
        m1 = rcv == 0
        out[m1] = rng.choice(s2_single[0], size=int(m1.sum()), p=s2_single[1])
        out[~m1] = rng.choice(s2_multi[0], size=int((~m1).sum()), p=s2_multi[1])
        return out
    S1 = np.array([mi_mm(rc, draw1(len(rc)), 2, nb) for _ in range(N_DRAWS)])
    S2 = np.array([mi_mm(rc, draw2(rc), 2, nb) for _ in range(N_DRAWS)])
    denom = S_real - S1.mean()
    F2 = (S2.mean() - S1.mean()) / denom if denom != 0 else float('nan')
    boots = []
    for _ in range(N_BOOT):
        ii = rng.integers(0, len(rc), len(rc))
        rcb, nxb = rc[ii], nx[ii]
        sr = mi_mm(rcb, nxb, 2, nb)
        s1b = np.mean([mi_mm(rcb, draw1(len(rcb)), 2, nb) for _ in range(N_BOOT_DRAWS)])
        s2b = np.mean([mi_mm(rcb, draw2(rcb), 2, nb) for _ in range(N_BOOT_DRAWS)])
        if sr - s1b != 0:
            boots.append((s2b - s1b) / (sr - s1b))
    q99_1, q99_2 = float(np.quantile(S1, 0.99)), float(np.quantile(S2, 0.99))
    run_len = S_real > q99_1
    kspec = S_real > q99_2
    verdict = 'k-SPECIFIC RESIDUAL' if kspec else ('GENERIC e-RUN TRANSITION' if run_len else 'NO RUN-LENGTH EFFECT')
    table = {('1' if r == 0 else '2+'): {(keep[c] if c < OTHER else 'OTHER'): int(((rc == r) & (nx == c)).sum())
                                         for c in range(nb)} for r in (0, 1)}
    res = {'track': label, 'n_k_runs': int(len(rc)), 'pooled_units': keep + ['OTHER'], 'table': table,
           'S_real_bits': S_real, 'S_ord1': {'mean': float(S1.mean()), 'q99': q99_1},
           'S_ord2': {'mean': float(S2.mean()), 'q99': q99_2}, 'F2_fraction_reproduced_by_order2': float(F2),
           'F2_ci95': [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))] if boots else None,
           'run_length_effect': bool(run_len), 'k_specific_residual': bool(kspec), 'verdict': verdict}
    # B5 homogeneity across heads (conditional on run class)
    HEADS = ['k', 'ch', 'sh', 'o']
    hc = np.array([HEADS.index(h) if h in HEADS else 4 for h, r, n in occ])
    rcl = np.array([0 if r == 1 else 1 for h, r, n in occ])
    nxa = np.array([code(n) for h, r, n in occ])

    def cond_mi(hv):
        tot = 0.0
        for r in (0, 1):
            m = rcl == r
            tot += m.mean() * mi_mm(hv[m], nxa[m], 5, nb)
        return tot
    obs = cond_mi(hc)
    perm = []
    for _ in range(N_PERM):
        hp = hc.copy()
        for r in (0, 1):
            m = np.flatnonzero(rcl == r)
            hp[m] = rng.permutation(hc[m])
        perm.append(cond_mi(hp))
    p = (1 + sum(x >= obs for x in perm)) / (1 + N_PERM)
    per_head = {}
    for hi, hname in enumerate(HEADS + ['other']):
        for r in (0, 1):
            m = (hc == hi) & (rcl == r)
            c = Counter(nxa[m].tolist())
            tot = int(m.sum())
            per_head[f'{hname}/{"1" if r == 0 else "2+"}'] = {
                'n': tot, 'top': {(keep[k] if k < OTHER else 'OTHER'): round(v / tot, 3)
                                  for k, v in c.most_common(4)} if tot else {}}
    res['B5'] = {'cond_mi_head_next_bits': obs, 'perm_mean': float(np.mean(perm)), 'p': p,
                 'verdict': 'HOMOGENEOUS' if p >= 0.05 else 'HEAD-SPECIFIC', 'per_head_next_unit_shares': per_head}
    return res


def track_words(tr):
    return [w for ln in TRACK_LINES[tr].values() for w in ln if certain(w)]


# ================================================================================================ Part C
sys.path.insert(0, str(ROOT / 'phases/PHASE_755_C2031_C2032_RECONCILIATION/scripts'))


def paragraphs_matched(tr, folios):
    """Paragraphs over lines present in both H and F, split at H's paragraph starts; words from track tr."""
    out = []
    for f in sorted(folios):
        keys = [k for k in TRACK_LINES['H'] if k[0] == f and k in TRACK_LINES['F']]
        cur = []
        for k in keys:                         # dict order = reading order
            if H_PAR_START.get(k) and cur:
                out.append(cur)
                cur = []
            cur.extend(w.lower() for w in TRACK_LINES[tr][k] if certain(w))
        if cur:
            out.append(cur)
    return out


def c1():
    import c2031_reconciliation as R
    folios = {f"f{n}{rv}" for n in range(75, 87) for rv in ("r", "v")}
    res = {}
    for tr in ('H', 'F'):
        paras = paragraphs_matched(tr, folios)
        stats = [R.para_stats(p) for p in paras if len(p) >= 2]
        rng = np.random.default_rng(SEED)
        D, e1, e2 = R.D_of(stats)
        Ds = []
        for _ in range(2000):
            idx = rng.integers(0, len(stats), len(stats))
            Ds.append(R.D_of([stats[i] for i in idx])[0])
        res[tr] = {'n_paragraphs': len(stats), 'D': D, 'ci95': [float(np.quantile(Ds, .025)), float(np.quantile(Ds, .975))]}
    h, f = res['H'], res['F']
    same = np.sign(h['D']) == np.sign(f['D'])
    inside = h['ci95'][0] <= f['D'] <= h['ci95'][1]
    if not same or not inside:
        v = 'TRACK-SENSITIVE'
    elif f['ci95'][0] > 0 or f['ci95'][1] < 0:
        v = 'TRACK-ROBUST'
    else:
        v = 'UNDERPOWERED'
    res['verdict'] = v
    return res


FIRE, VESSEL = {'ch', 'sh', 'qo'}, {'ok', 'ot', 'ol', 'or'}


def prefix_of(w):
    if w.startswith('ch'):
        return 'ch'
    if w.startswith('sh'):
        return 'sh'
    if w.startswith('qo'):
        return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in 'ktlr':
        return 'o' + w[1]
    return None


def channel(words):
    pc, bc = Counter(), Counter()
    for w in words:
        p = prefix_of(w)
        if p:
            pc[p] += 1
            bc['F' if p in FIRE else 'V'] += 1
    tot = sum(pc.values())
    if len(words) < 8 or tot < 4:
        return None
    ff, vf = bc['F'] / tot, bc['V'] / tot
    if max(ff, vf) <= 0.70:
        return None
    block = FIRE if ff > vf else VESSEL
    dom = max(block, key=lambda p: pc.get(p, 0))
    return dom if dom in ('qo', 'ch', 'sh') else None


def nonpfx_mean(words):
    v = [e_depth(w) for w in words if prefix_of(w) is None]
    return sum(v) / len(v) if v else 0.0


def c2_paragraphs(tr_class, tr_edepth):
    """C1967 original definitions (all placements, currier_b-style), lines present in both H and F."""
    lines = {tr: defaultdict(list) for tr in ('H', 'F')}
    parstart = {}
    for t in tx.all(h_only=False):
        if t.transcriber not in lines or t.language != 'B' or t.is_label:
            continue
        w = t.word.strip()
        if not w or '*' in w:
            continue
        key = (t.folio, t.line)
        if t.transcriber == 'H' and not lines['H'][key]:
            parstart[key] = bool(t.par_initial)
        lines[t.transcriber][key].append(w)
    paras = []
    folios = sorted({k[0] for k in lines['H']})
    for f in folios:
        keys = [k for k in lines['H'] if k[0] == f and k in lines['F']]
        cur = {'H': [], 'F': []}
        for k in keys:
            if parstart.get(k) and (cur['H'] or cur['F']):
                paras.append(cur)
                cur = {'H': [], 'F': []}
            cur['H'].extend(lines['H'][k])
            cur['F'].extend(lines['F'][k])
        if cur['H'] or cur['F']:
            paras.append(cur)
    labs, vals = [], []
    for p in paras:
        ch = channel(p[tr_class])
        if ch is None:
            continue
        labs.append(ch)
        vals.append(nonpfx_mean(p[tr_edepth]))
    return labs, np.array(vals)


def gradient(labs, vals):
    labs = np.array(labs)
    if not (labs == 'qo').any() or not (labs == 'sh').any():
        return float('nan')
    return float(vals[labs == 'qo'].mean() - vals[labs == 'sh'].mean())


def c2():
    rng = np.random.default_rng(SEED)
    res = {}
    for name, (tc, te) in {'H_matched': ('H', 'H'), 'F_edepth_H_classes': ('H', 'F'), 'F_all': ('F', 'F')}.items():
        labs, vals = c2_paragraphs(tc, te)
        g = gradient(labs, vals)
        perm = [gradient(rng.permutation(labs), vals) for _ in range(10000)]
        p = (sum(x >= g for x in perm)) / 10000
        boots = []
        la = np.array(labs)
        for _ in range(2000):
            idx = np.concatenate([rng.choice(np.flatnonzero(la == c), size=(la == c).sum()) for c in ('qo', 'ch', 'sh')
                                  if (la == c).any()])
            boots.append(gradient(la[idx], vals[idx]))
        res[name] = {'n': dict(Counter(labs)), 'gradient_qo_minus_sh': g, 'perm_p': p,
                     'ci95': [float(np.nanquantile(boots, .025)), float(np.nanquantile(boots, .975))]}
    h = res['H_matched']
    for name in ('F_edepth_H_classes', 'F_all'):
        f = res[name]
        same = np.sign(h['gradient_qo_minus_sh']) == np.sign(f['gradient_qo_minus_sh'])
        inside = h['ci95'][0] <= f['gradient_qo_minus_sh'] <= h['ci95'][1]
        f['verdict'] = ('TRACK-SENSITIVE' if (not same or not inside) else
                        ('TRACK-ROBUST' if f['perm_p'] < 0.05 else 'UNDERPOWERED'))
    return res


# ================================================================================================ main
def annotation_list():
    rows = []
    pat = re.compile(r'e_depth|e-depth|e-run|multi-e|single-e|\bee\b', re.I)
    for line in open(ROOT / 'context/CLAIMS/INDEX.md', encoding='utf-8'):
        m = re.match(r'^\|\s*\*{0,2}(\d{3,4})\*{0,2}\s*\|', line)
        if m and pat.search(line) and '~~' not in line[:20]:
            rows.append(int(m.group(1)))
    return sorted(set(rows))


def main():
    random.seed(SEED)
    out = {'phase': 'PHASE_758', 'pre_registration_commit': '10134f7',
           'A0_encoding_note': ('Landini-Stolfi interlinear: Currier (C) and FSG (F) transliterations converted into EVA '
                                '("consistent and reversible"); both source alphabets write the e glyph as "C", one '
                                'symbol per stroke; Currier merged runs of i-strokes but not of e-strokes '
                                '(voynich.nu/transcr.html, accessed 2026-09-27). So e-run length disagreements are '
                                'reading differences, not conversion artefacts.')}
    out['A'] = {tr: part_a(tr) for tr in ('F', 'C')}
    for tr, r in out['A'].items():
        log(f"A H-vs-{tr}: pairs={r['aligned_certain_pairs']} 1v2+ {r['A2_1_vs_2plus']} class={r['classification']} "
            f"directional={r['directional_bias']}")
        log(f"   run agreement: { {k: (v['n'], None if v['agreement'] is None else round(v['agreement'], 3)) for k, v in r['A1_run_agreement'].items()} }")
    b1_old, old_toks = b1(morph_old)
    b1_new, _ = b1(morph_now)
    out['B1'] = {'historical_parser': b1_old, 'current_parser': b1_new}
    log(f"B1 historical: {b1_old}")
    log(f"B1 current:    {b1_new}")
    out['B2'] = b2(old_toks)
    log(f"B2: {out['B2']}")
    out['B3_B5_H'] = part_b_tables(track_words('H'), 'H')
    log(f"B3/B4 H: S_real={out['B3_B5_H']['S_real_bits']:.4f} ord1={out['B3_B5_H']['S_ord1']} ord2={out['B3_B5_H']['S_ord2']} "
        f"F2={out['B3_B5_H']['F2_fraction_reproduced_by_order2']:.3f} {out['B3_B5_H']['F2_ci95']} -> {out['B3_B5_H']['verdict']}")
    log(f"B5 H: {out['B3_B5_H']['B5']['verdict']} p={out['B3_B5_H']['B5']['p']:.4f}")
    out['B6_F'] = part_b_tables(track_words('F'), 'F')
    out['B6_F']['track_sensitive'] = out['B6_F']['verdict'] != out['B3_B5_H']['verdict']
    log(f"B6 F: verdict={out['B6_F']['verdict']} (track-sensitive={out['B6_F']['track_sensitive']}); B5 {out['B6_F']['B5']['verdict']}")
    out['C1'] = c1()
    log(f"C1: {out['C1']}")
    out['C2'] = c2()
    log(f"C2: {out['C2']}")
    out['annotation_candidates_from_grep'] = annotation_list()
    json.dump(out, open(OUT / 'erun_gate.json', 'w', encoding='utf-8'), indent=1, default=float)
    log(f"written {OUT / 'erun_gate.json'}")


if __name__ == '__main__':
    main()
