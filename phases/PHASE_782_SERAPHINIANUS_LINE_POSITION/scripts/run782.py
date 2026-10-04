#!/usr/bin/env python3
"""PHASE_782 locked run (pre-registration v2 plus any recorded lock amendments). One run on the real Codex order.

  python run782.py      verifies the lock checksums, sets PHASE782_RUN=locked, computes the primary verdict, the
                        opposite-label variants, the sensitivities and the descriptives -> results/verdict782.json,
                        results/run_log782.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core782 as C  # noqa: E402
import calib782 as K  # noqa: E402

RES = C.PH / 'results'
LOG = RES / 'run_log782.txt'


def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')


def verify_lock():
    ck = json.load(open(RES / 'input_checksums782.json', encoding='utf-8'))
    for rel, h in ck['files'].items():
        p = C.ROOT / rel
        got = hashlib.sha256(open(p, 'rb').read()).hexdigest()
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


def s1_excess(lines, rng, L=40, R=500, include_first=False):
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


def four(Bclean, Bheavy, CSraw, CStwo, CSguard, rng, iid=False):
    nra = C.auc_block(Bheavy, CSraw, rng, B=K.B_BOOT, iid=iid)
    nrb = C.auc_block(Bheavy, CStwo, rng, B=K.B_BOOT, iid=iid)
    ra = C.auc_block(Bclean, CSraw, rng, B=K.B_BOOT, iid=iid)
    rb = C.auc_block(Bclean, CSguard, rng, B=K.B_BOOT, iid=iid)
    return {'NR_a': nra, 'NR_b': nrb, 'R_a': ra, 'R_b': rb, 'label': C.label([nra, nrb], [ra, rb])}


def arm(Blines, CSlines, frag, tag, **kw):
    """Excess arrays for one setting: B clean, B heavy (20 realisations), CS raw, CS two characters, CS guarded."""
    kw_b = {k: v for k, v in kw.items() if k not in ('cs_exclude',)}
    kw_c = {k: v for k, v in kw.items() if k not in ('cs_exclude',)}
    cs_ex = kw.get('cs_exclude')
    rng = K.stable_rng(f'B-clean{tag}')
    Bc = _ex(Blines, rng, kw_b)
    Bh = []
    for r in range(K.N_REAL):
        rr = K.stable_rng(f'B-heavy{tag}', r)
        Bh.append(_ex(C.degrade(Blines, *K.NOISE['heavy'], rr, K.W['margB']), rr, kw_b))
    rng = K.stable_rng(f'CS{tag}')
    raw = _ex(CSlines, rng, kw_c, exclude=cs_ex)
    two_kw = dict(kw_c)
    two_kw.pop('topk', None)
    two = _ex(CSlines, rng, {**two_kw, 'first_n': 2, 'topk_per_chunk': (kw_c.get('topk') or 25) - 1}, exclude=cs_ex)
    gd = _ex(C.guard(CSlines, frag), rng, kw_c, exclude=cs_ex)
    return Bc, Bh, raw, two, gd


def _ex(lines, rng, kw, exclude=None):
    kw = dict(kw)
    norm = kw.pop('normalise', False)
    if exclude is not None:
        kw['exclude'] = exclude
    return C.ChunkSet(lines, rng, **kw).excess(K.R_PERM, rng, normalise=norm)


def main():
    t0 = time.time()
    ck = verify_lock()
    os.environ['PHASE782_RUN'] = 'locked'          # set only here, after the lock check (no import side effect)
    log(f'lock verified ({ck.get("tag")}); PHASE782_RUN=locked')
    K._init()
    frag = K.W['frag']
    B = K.W['B']
    CS = C.load_cs()
    out = {'lock': ck.get('tag'), 'fragment_strokes': ''.join(frag)}
    # ---------------- primary
    Bc, Bh, raw, two, gd = arm(B, CS, frag, '')
    prim = four(Bc, Bh, raw, two, gd, K.stable_rng('boot-primary'))
    out['primary'] = prim
    out['medians'] = {'B_clean': float(np.median(Bc)), 'B_heavy': float(np.median(np.concatenate(Bh))),
                      'CS_raw': float(np.median(raw)), 'CS_two': float(np.median(two)), 'CS_guarded': float(np.median(gd))}
    out['n_chunks'] = {'B': len(Bc), 'CS_raw': len(raw), 'CS_two': len(two), 'CS_guarded': len(gd)}
    log(f"PRIMARY: {prim['label']}; NR(a) {prim['NR_a']}; NR(b) {prim['NR_b']}; R(a) {prim['R_a']}; R(b) {prim['R_b']}")
    log(f"medians {out['medians']}; chunks {out['n_chunks']}")
    # ---------------- opposite-label variants
    variants = {'top8': {'topk': 8}, 'interior': {'interior': True, 'K': 40}, 'normalised': {'normalise': True}}
    vres = {}
    for name, kw in variants.items():
        v = four(*arm(B, CS, frag, f'-{name}', **kw), K.stable_rng(f'boot-{name}'))
        vres[name] = v
        log(f"variant {name}: {v['label']}")
    out['variants'] = vres
    final = prim['label']
    opposite = {'NOT REACHED': 'REACHED', 'REACHED': 'NOT REACHED'}.get(final)
    if opposite and any(v['label'] == opposite for v in vres.values()):
        final = 'UNRESOLVED'
    out['verdict'] = final
    log(f'VERDICT: {final}')
    # ---------------- sensitivities (cannot change the label)
    sens = {}
    sens['iid_bootstrap'] = four(Bc, Bh, raw, two, gd, K.stable_rng('boot-iid'), iid=True)
    sens['no_paragraph_exclusion'] = four(*arm(B, CS, frag, '-nofirst', include_first=True), K.stable_rng('b-nf'))
    blockfirst = [C.Line(L.unit, L.flags['block_first'], L.toks, L.brk, L.group, L.flags) for L in CS]
    sens['cs_block_first_only'] = four(*arm(B, blockfirst, frag, '-bf'), K.stable_rng('b-bf'))
    sens['b_drop_break'] = four(*arm(B, CS, frag, '-brk', drop_break=True), K.stable_rng('b-brk'))
    sens['L30'] = four(*arm(B, CS, frag, '-L30', L=30, K=60), K.stable_rng('b-L30'))
    sens['L60'] = four(*arm(B, CS, frag, '-L60', L=60, K=120), K.stable_rng('b-L60'))
    for nm, fl in (('cs_wide_blocks_excluded', 'wide_block'), ('cs_long_lines_excluded', 'long_line'),
                   ('cs_block_code_23_excluded', 'block_code_23')):
        sens[nm] = four(*arm(B, CS, frag, f'-{nm}', cs_exclude=lambda L, f=fl: L.flags.get(f, False)),
                        K.stable_rng(f'b-{nm}'))
    CSnum = C.load_cs(numerals_excluded=False)
    sens['cs_numerals_included'] = four(*arm(B, CSnum, frag, '-num'), K.stable_rng('b-num'))
    BH = load_b_h()
    K.W['margB'] = C.unit_marginals(BH)
    sens['b_h_track'] = four(*arm(BH, CS, frag, '-H'), K.stable_rng('b-H'))
    K.W['margB'] = C.unit_marginals(B)
    out['sensitivities'] = {k: {'label': v['label'], **{q: v[q] for q in ('NR_a', 'NR_b', 'R_a', 'R_b')}} for k, v in sens.items()}
    log('sensitivities: ' + '; '.join(f'{k} {v["label"]}' for k, v in sens.items()))
    # ---------------- descriptives
    desc = {}
    Bm = [K.stable_rng('B-matched', r) for r in range(K.N_REAL)]
    Bmat = [_ex(C.degrade(B, *K.NOISE['matched'], rr, K.W['margB']), rr, {}) for rr in Bm]
    desc['effect_bits'] = {'B_clean_minus_CS': float(np.median(Bc) - np.median(raw)),
                           'B_matched_minus_CS': float(np.median(np.concatenate(Bmat)) - np.median(raw)),
                           'B_heavy_minus_CS': float(np.median(np.concatenate(Bh)) - np.median(raw))}
    rng = K.stable_rng('B-clean')
    cb = C.ChunkSet(B, rng)
    eb, parts_b = cb.excess(K.R_PERM, rng, zone_parts=True)
    per_sec = defaultdict(list)
    for g, e in zip(cb.chunk_group, eb):
        per_sec[g].append(e)
    desc['B_per_section_median'] = {g: float(np.median(v)) for g, v in per_sec.items()}
    rng = K.stable_rng('CS')
    ccs = C.ChunkSet(CS, rng)
    ec, parts_c = ccs.excess(K.R_PERM, rng, zone_parts=True)
    desc['zone_parts'] = {
        'B': {'zone_excess_median': np.median([p['zone_excess'] for p in parts_b], 0).tolist(),
              'top_unit_share_median': float(np.median([p['top_unit_share'] for p in parts_b]))},
        'CS': {'zone_excess_median': np.median([p['zone_excess'] for p in parts_c], 0).tolist(),
               'top_unit_share_median': float(np.median([p['top_unit_share'] for p in parts_c]))}}
    rng = K.stable_rng('lenclass')
    desc['length_class_null_median'] = {
        'B': float(np.median(C.ChunkSet(B, rng).excess(K.R_PERM, rng, length_class=True))),
        'CS': float(np.median(C.ChunkSet(CS, rng).excess(K.R_PERM, rng, length_class=True)))}
    rng = K.stable_rng('S1')
    s1b, s1c = s1_excess(B, rng), s1_excess(CS, rng)
    desc['S1'] = {'B_median': float(np.median(s1b)), 'CS_median': float(np.median(s1c)),
                  'auc_B_vs_CS': C.auc_block(s1b, s1c, rng, B=K.B_BOOT)}
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
    log(f"descriptive: effect {desc['effect_bits']}; zone parts {desc['zone_parts']}; S1 {desc['S1']}")
    out['runtime_s'] = round(time.time() - t0, 1)
    json.dump(out, open(RES / 'verdict782.json', 'w', encoding='utf-8'), indent=1, default=float)
    log(f'run done ({out["runtime_s"]} s)')


if __name__ == '__main__':
    main()
