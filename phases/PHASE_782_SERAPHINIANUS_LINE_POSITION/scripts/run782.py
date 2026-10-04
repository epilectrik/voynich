#!/usr/bin/env python3
"""PHASE_782 locked run (pre-registration v4). One run on the real Codex order.

  python run782.py         verifies the lock (required files, checksums, configuration), sets PHASE782_RUN=locked only
                           after that, computes the primary verdict, the opposite-label variants, the sensitivities and
                           the descriptives -> results/verdict782.json (written after every stage), results/run_log782.txt
  python run782.py --dry   the same code paths on the WITHIN-LINE-SHUFFLED Codex (never sets the run flag; refuses to
                           run if it is set) -> results/dryrun/ ; used before the lock to exercise every path.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core782 as C  # noqa: E402
K = None            # calib782, imported in main() after the configuration is set

DRY = '--dry' in sys.argv
RES = C.PH / 'results'
OUT_DIR = RES / 'dryrun' if DRY else RES
LOG = OUT_DIR / ('dry_log782.txt' if DRY else 'run_log782.txt')
OUT = OUT_DIR / ('dry_verdict782.json' if DRY else 'verdict782.json')
P = 'phases/PHASE_782_SERAPHINIANUS_LINE_POSITION/'
REQ = {P + 'PRE_REGISTRATION.md', P + 'scripts/core782.py', P + 'scripts/calib782.py', P + 'scripts/run782.py',
       'data/transcriptions/reference/ZL_official.txt', 'data/transcriptions/interlinear_full_words.txt',
       'external/phase782_seraphinianus/CS_OCR_TRANSLITERATION.txt'}


def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')


def save(out):
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1, default=float)


def verify_lock():
    ck = json.load(open(RES / 'input_checksums782.json', encoding='utf-8'))
    assert REQ <= set(ck['files']), 'lock file incomplete'
    for rel, h in ck['files'].items():
        got = hashlib.sha256(open(C.ROOT / rel, 'rb').read()).hexdigest()
        assert got == h, f'checksum mismatch: {rel}'
    return ck


def load_b_h():
    """Sensitivity: H-track Currier B (interlinear file), P placement, true line positions, '*' tokens excluded."""
    import pandas as pd
    df = pd.read_csv(C.ROOT / 'data/transcriptions/interlinear_full_words.txt', sep='\t', dtype=str)
    df = df[(df['transcriber'] == 'H') & (df['language'] == 'B') & (df['placement'].fillna('').str.startswith('P'))]
    df = df[df['word'].fillna('').str.strip() != '']
    lines = []
    for (f, ln), g in df.groupby(['folio', 'line_number'], sort=False):
        toks = [None if '*' in w else tuple(C.GLYPH_RE.findall(w)) for w in g['word']]
        first = str(g['par_initial'].iloc[0]) == '1'
        lines.append(C.Line(f, first, toks, group=g['section'].iloc[0]))
    return lines


def s1_excess(lines, rng, L, R=500, include_first=False):
    """Descriptive S1: MI(last unit of word t; first unit of word t+1) over adjacent readable pairs within lines,
    minus the within-line permutation mean, per chunk of L eligible lines."""
    el = [ln for ln in lines if C.eligible(ln, include_first)]
    out = []
    for c0 in range(0, len(el) - L + 1, L):
        words, lid = [], []
        for li, ln in enumerate(el[c0:c0 + L]):
            for i, t in enumerate(ln.toks):
                if t is not None:
                    words.append((t, i))
                    lid.append(li)
        n = len(words)
        lid = np.array(lid)
        pos = np.array([w[1] for w in words])
        pair = np.flatnonzero((lid[:-1] == lid[1:]) & (pos[1:] - pos[:-1] == 1))
        lu = {u: k for k, u in enumerate(sorted({w[0][-1] for w in words}))}
        fu = {u: k for k, u in enumerate(sorted({w[0][0] for w in words}))}
        Lv = np.array([lu[w[0][-1]] for w in words])
        Fv = np.array([fu[w[0][0]] for w in words])
        keys = rng.random((R, n)) + lid[None, :] * 2.0
        perm = np.vstack([np.arange(n)[None, :], np.argsort(keys, axis=1, kind='stable')])
        mi = C.mi_rows(Lv[perm][:, pair], Fv[perm][:, pair + 1], len(lu), len(fu))
        out.append(float(mi[0] - mi[1:].mean()))
    return np.array(out)


def s4_repetition(lines):
    """Descriptive S4: adjacent identical words within eligible lines (adjacent readable positions),
    log((O+0.5)/(E+0.5)) with E the within-line permutation expectation sum_c c(c-1)/n per line."""
    O, E = 0, 0.0
    for ln in lines:
        if not C.eligible(ln):
            continue
        for a, b in zip(ln.toks[:-1], ln.toks[1:]):
            if a is not None and b is not None and a == b:
                O += 1
        rd = [t for t in ln.toks if t is not None]
        if len(rd) >= 2:
            cnt = Counter(rd)
            E += sum(c * (c - 1) for c in cnt.values()) / len(rd)
    return {'O': O, 'E': E, 'log_OE': float(np.log((O + 0.5) / (E + 0.5)))}


def four(Bclean, Bheavy, CSraw, CStwo, CSguard, rng, iid=False):
    nra = C.auc_block(Bheavy, CSraw, rng, B=K.B_BOOT, iid=iid)
    nrb = C.auc_block(Bheavy, CStwo, rng, B=K.B_BOOT, iid=iid)
    ra = C.auc_block(Bclean, CSraw, rng, B=K.B_BOOT, iid=iid)
    rb = C.auc_block(Bclean, CSguard, rng, B=K.B_BOOT, iid=iid)
    return {'NR_a': nra, 'NR_b': nrb, 'R_a': ra, 'R_b': rb, 'label': C.label([nra, nrb], [ra, rb])}


def _ex(lines, rng, kw, exclude=None, counts=None, name=None):
    kw = dict(kw)
    norm = kw.pop('normalise', False)
    if exclude is not None:
        kw['exclude'] = exclude
    cs = K.CSET(lines, rng, **kw)
    e = cs.excess(K.R_PERM, rng, normalise=norm)
    if counts is not None:
        counts[name] = {'eligible_lines': cs.n_eligible, 'chunks': len(e), 'chunks_short_medial': cs.n_short_medial,
                        'leftover_lines': cs.n_leftover_lines}
    return e


def guard_drops(lines, frag):
    """Primary-eligible lines by whether the guard excludes a line-edge token (those lines drop from guarded CS)."""
    fr = set(frag)
    c = Counter()
    for ln in lines:
        if not C.eligible(ln):
            continue
        first, last = ln.toks[0], ln.toks[-1]
        f_ex = len(first) == 1 or first[0] in fr
        l_ex = len(last) == 1 or last[0] in fr
        c['both' if f_ex and l_ex else 'first' if f_ex else 'last' if l_ex else 'kept'] += 1
    return dict(c)


def arm(Blines, CSlines, frag, tag, counts=None, **kw):
    """Excess arrays for one setting: B clean, B heavy (20 realisations), CS raw, CS two characters, CS guarded."""
    cs_ex = kw.pop('cs_exclude', None)
    rng = K.stable_rng(f'B-clean{tag}')
    Bc = _ex(Blines, rng, kw, counts=counts, name='B_clean')
    Bh, hc = [], []
    for r in range(K.N_REAL):
        rr = K.stable_rng(f'B-heavy{tag}', r)
        cc = {}
        Bh.append(_ex(C.degrade(Blines, *K.NOISE['heavy'], rr, K.W['margB']), rr, kw, counts=cc, name='x'))
        hc.append(cc['x']['chunks'])
    if counts is not None:
        counts['B_heavy_chunks_median'] = float(np.median(hc))
    rng = K.stable_rng(f'CS{tag}')
    raw = _ex(CSlines, rng, kw, exclude=cs_ex, counts=counts, name='CS_raw')
    two_kw = dict(kw)
    tk = two_kw.pop('topk', None)
    two = _ex(CSlines, rng, {**two_kw, 'first_n': 2, 'topk_per_chunk': (tk - 1) if tk else 24}, exclude=cs_ex,
              counts=counts, name='CS_two')
    gd = _ex(C.guard(CSlines, frag), rng, kw, exclude=cs_ex, counts=counts, name='CS_guarded')
    return Bc, Bh, raw, two, gd


def main():
    t0 = time.time()
    OUT_DIR.mkdir(exist_ok=True)
    if DRY:
        assert os.environ.get('PHASE782_RUN') != 'locked', 'dry mode must not run with the run flag set'
        L0 = int(os.environ.get('PHASE782_L', '30'))
        cfg = {'L': L0, 'K': 2 * L0}
        tag = 'DRY RUN (within-line-shuffled Codex)'
    else:
        ck = verify_lock()
        cfg = ck['config']
        tag = ck.get('tag')
        os.environ['PHASE782_RUN'] = 'locked'      # set only here, after the lock check (no import side effect)
    os.environ['PHASE782_L'] = str(cfg['L'])
    os.environ['PHASE782_TOPK'] = str(cfg.get('topk') or 0)
    global K
    import calib782 as K_mod
    K = K_mod
    assert K.CHUNK_KW == {'L': cfg['L'], 'K': cfg['K'], **({'topk': cfg['topk']} if cfg.get('topk') else {})}, \
        'configuration mismatch'
    log(f'{"DRY" if DRY else "LOCKED"} run; lock {tag}; config {K.CHUNK_KW}; python {platform.python_version()}, '
        f'numpy {np.__version__}')
    K._init()
    frag = K.W['frag']
    B = K.W['B']
    CS = C.load_cs(rng=K.stable_rng('dry-shuffle')) if DRY else C.load_cs()
    out = {'lock': tag, 'dry': DRY, 'config': K.CHUNK_KW, 'fragment_strokes': ''.join(frag),
           'versions': {'python': platform.python_version(), 'numpy': np.__version__}}
    # ---------------- primary
    counts = {}
    Bc, Bh, raw, two, gd = arm(B, CS, frag, '', counts=counts)
    prim = four(Bc, Bh, raw, two, gd, K.stable_rng('boot-primary'))
    out['primary'] = prim
    out['medians'] = {'B_clean': float(np.median(Bc)), 'B_heavy': float(np.median(np.concatenate(Bh))),
                      'CS_raw': float(np.median(raw)), 'CS_two': float(np.median(two)), 'CS_guarded': float(np.median(gd))}
    out['counts'] = counts
    out['guard_edge_drops'] = guard_drops(CS, frag)
    log(f"PRIMARY: {prim['label']}; NR(a) {prim['NR_a']}; NR(b) {prim['NR_b']}; R(a) {prim['R_a']}; R(b) {prim['R_b']}")
    log(f"medians {out['medians']}; counts {counts}; guard edge drops {out['guard_edge_drops']}")
    save(out)
    # ---------------- opposite-label variants
    variants = {'top8': {'topk': 8}, 'interior': {'interior': True}, 'normalised': {'normalise': True}}   # interior K = L
    vres = {}
    for name, kw in variants.items():
        vc = {}
        v = four(*arm(B, CS, frag, f'-{name}', counts=vc, **kw), K.stable_rng(f'boot-{name}'))
        v['counts'] = vc
        vres[name] = v
        log(f"variant {name}: {v['label']}")
    out['variants'] = vres
    final = prim['label']
    opposite = {'NOT REACHED': 'REACHED', 'REACHED': 'NOT REACHED'}.get(final)
    if opposite and any(v['label'] == opposite for v in vres.values()):
        final = 'UNRESOLVED'
    out['verdict'] = final
    log(f'VERDICT: {final}')
    save(out)
    # ---------------- sensitivities (cannot change the label)
    sens = {}
    sens['iid_bootstrap'] = four(Bc, Bh, raw, two, gd, K.stable_rng('boot-iid'), iid=True)
    sens['no_paragraph_exclusion'] = four(*arm(B, CS, frag, '-nofirst', include_first=True), K.stable_rng('b-nf'))
    blockfirst = [C.Line(L.unit, L.flags['block_first'], L.toks, L.brk, L.group, L.flags) for L in CS]
    sens['cs_block_first_only'] = four(*arm(B, blockfirst, frag, '-bf'), K.stable_rng('b-bf'))
    sens['b_drop_break'] = four(*arm(B, CS, frag, '-brk', drop_break=True), K.stable_rng('b-brk'))
    for Lx in [x for x in (30, 40, 60) if x != K.CFG_L]:
        sens[f'L{Lx}'] = four(*arm(B, CS, frag, f'-L{Lx}', L=Lx, K=2 * Lx), K.stable_rng(f'b-L{Lx}'))
    for nm, fl in (('cs_wide_blocks_excluded', 'wide_block'), ('cs_long_lines_excluded', 'long_line'),
                   ('cs_block_code_23_excluded', 'block_code_23')):
        sens[nm] = four(*arm(B, CS, frag, f'-{nm}', cs_exclude=lambda L, f=fl: L.flags.get(f, False)),
                        K.stable_rng(f'b-{nm}'))
    CSnum = C.load_cs(numerals_excluded=False, rng=K.stable_rng('dry-shuffle-num')) if DRY else \
        C.load_cs(numerals_excluded=False)
    sens['cs_numerals_included'] = four(*arm(B, CSnum, frag, '-num'), K.stable_rng('b-num'))
    BH = load_b_h()
    marg_ZL = K.W['margB']
    K.W['margB'] = C.unit_marginals(BH)
    sens['b_h_track'] = four(*arm(BH, CS, frag, '-H'), K.stable_rng('b-H'))
    K.W['margB'] = marg_ZL
    out['sensitivities'] = {k: {'label': v['label'], **{q: v[q] for q in ('NR_a', 'NR_b', 'R_a', 'R_b')}}
                            for k, v in sens.items()}
    log('sensitivities: ' + '; '.join(f'{k} {v["label"]}' for k, v in sens.items()))
    save(out)
    # ---------------- descriptives
    desc = {}
    Bmat = []
    for r in range(K.N_REAL):
        rr = K.stable_rng('B-matched', r)
        Bmat.append(_ex(C.degrade(B, *K.NOISE['matched'], rr, K.W['margB']), rr, {}))
    desc['effect_bits'] = {'B_clean_minus_CS': float(np.median(Bc) - np.median(raw)),
                           'B_matched_minus_CS': float(np.median(np.concatenate(Bmat)) - np.median(raw)),
                           'B_heavy_minus_CS': float(np.median(np.concatenate(Bh)) - np.median(raw))}
    rng = K.stable_rng('B-clean')
    cb = K.CSET(B, rng)
    eb, parts_b = cb.excess(K.R_PERM, rng, zone_parts=True)
    per_sec = defaultdict(list)
    for g, e in zip(cb.chunk_group, eb):
        per_sec[g].append(e)
    desc['B_per_section_median'] = {g: float(np.median(v)) for g, v in per_sec.items()}
    rng = K.stable_rng('CS')
    ccs = K.CSET(CS, rng)
    ec, parts_c = ccs.excess(K.R_PERM, rng, zone_parts=True)

    def zp(parts):
        return {'zone_excess_median': np.median([p['zone_excess'] for p in parts], 0).tolist(),
                'top_unit_share_of_excess_median': float(np.nanmedian([p['top_unit_share_of_excess'] for p in parts])),
                'top_unit_excess_bits_median': float(np.median([p['top_unit_excess_bits'] for p in parts])),
                'top_unit_share_of_observed_mi_median': float(np.median([p['top_unit_share_of_observed_mi'] for p in parts]))}
    desc['zone_parts'] = {'B': zp(parts_b), 'CS': zp(parts_c)}
    rng = K.stable_rng('lenclass')
    desc['length_class_null_median'] = {
        'B': float(np.median(K.CSET(B, rng).excess(K.R_PERM, rng, length_class=True))),
        'CS': float(np.median(K.CSET(CS, rng).excess(K.R_PERM, rng, length_class=True)))}
    rng = K.stable_rng('S1')
    s1b, s1c = s1_excess(B, rng, L=K.CFG_L), s1_excess(CS, rng, L=K.CFG_L)
    desc['S1'] = {'B_median': float(np.median(s1b)), 'CS_median': float(np.median(s1c)),
                  'auc_B_vs_CS': C.auc_block(s1b, s1c, rng, B=K.B_BOOT)}
    desc['S4'] = {'B': s4_repetition(B), 'CS': s4_repetition(CS)}
    drops = {}
    for nm, lines in (('B', B), ('CS', CS)):
        c = Counter()
        for L in lines:
            if L.first:
                c['paragraph_first'] += 1
            elif len(L.toks) < 3:
                c['under_3_positions'] += 1
            elif L.toks[0] is None or L.toks[-1] is None:
                c['edge_unreadable'] += 1
            else:
                c['eligible'] += 1
        drops[nm] = dict(c)
    desc['line_drops'] = drops
    out['descriptive'] = desc
    log(f"descriptive: effect {desc['effect_bits']}; zone parts {desc['zone_parts']}; S1 {desc['S1']}; S4 {desc['S4']}")
    out['runtime_s'] = round(time.time() - t0, 1)
    save(out)
    log(f'run done ({out["runtime_s"]} s)')


if __name__ == '__main__':
    main()
