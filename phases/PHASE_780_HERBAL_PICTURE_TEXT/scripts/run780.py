#!/usr/bin/env python3
"""PHASE_780 locked run (see ../PRE_REGISTRATION.md). The only script that evaluates the real Voynich text-picture
alignment.

  python run780.py --checksums   write results/input_checksums780.json (before the lock commit)
  python run780.py run           verify the lock; V-A1 decision and verdict; descriptive companions; V-B2
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

PH = Path('C:/git/voynich/phases/PHASE_780_HERBAL_PICTURE_TEXT')
sys.path.insert(0, str(PH / 'scripts'))
import core780 as K  # noqa: E402
import calib780 as CB  # noqa: E402

ROOT = Path('C:/git/voynich')
RES = PH / 'results'
LOCK = 'phase780-lock'
PHASE = 'phases/PHASE_780_HERBAL_PICTURE_TEXT'
SEED_RUN = 780_900_000
LOCKED = ('PRE_REGISTRATION.md', 'scripts/core780.py', 'scripts/calib780.py', 'scripts/run780.py', 'data/pages_v.json',
          'data/entries_br.json', 'data/key_code.json', 'data/geometry.json', 'data/page_features_v.json',
          'results/calib_setup780.json', 'results/calib780.json')
INPUTS = ('data/transcriptions/interlinear_full_words.txt', 'data/transcriptions/reference/ZL_official.txt',
          'sources/brunschwig_1500/brunschwig_1500_corrected.txt')
CODE_GLOB = 'codes_*_*_*.json'
LOGF = None


def log(msg):
    print(msg, flush=True)
    if LOGF:
        LOGF.write(msg + '\n')
        LOGF.flush()


def sha256(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def code_files():
    return sorted(str(p) for p in (K.DATA / 'codes').glob(CODE_GLOB))


def checksums():
    sums = {p: sha256(ROOT / p) for p in INPUTS}
    sums.update({f'codes::{Path(p).name}': sha256(p) for p in code_files()})
    json.dump(sums, open(RES / 'input_checksums780.json', 'w'), indent=1)
    print('wrote input_checksums780.json with', len(sums), 'entries')


def verify_lock():
    assert subprocess.run(['git', 'rev-parse', '--verify', LOCK], cwd=ROOT, capture_output=True).returncode == 0, 'no lock tag'
    for p in LOCKED:
        assert subprocess.run(['git', 'diff', '--quiet', LOCK, '--', f'{PHASE}/{p}'], cwd=ROOT).returncode == 0, f'{p} changed'
    sums = json.load(open(RES / 'input_checksums780.json'))
    for p in INPUTS:
        assert sha256(ROOT / p) == sums[p], f'input changed: {p}'
    for p in code_files():
        assert sha256(p) == sums[f'codes::{Path(p).name}'], f'codes changed: {p}'
    assert len([k for k in sums if k.startswith('codes::')]) == len(code_files()), 'code file set changed'


def spearman_partial(eng, T, C, Y, X):
    i0, i1 = np.triu_indices(C.shape[0], 1)
    vals = {}
    A = np.column_stack([np.ones(len(i0)), X, rankdata(K.double_centre(Y)[i0, i1])])
    c = rankdata(K.double_centre(C)[i0, i1])
    rc = c - A @ np.linalg.lstsq(A, c, rcond=None)[0]
    for m, M in T.items():
        t = rankdata(K.double_centre(M)[i0, i1])
        rt = t - A @ np.linalg.lstsq(A, t, rcond=None)[0]
        vals[m] = float(rt @ rc / np.sqrt((rt @ rt) * (rc @ rc)))
    return vals


def main():
    global LOGF
    if '--checksums' in sys.argv:
        checksums()
        return
    verify_lock()
    LOGF = open(RES / 'run_log780.txt', 'a', encoding='utf-8')
    t0 = time.time()
    log(f'PHASE_780 run; lock {LOCK} verified; {time.strftime("%Y-%m-%d %H:%M:%S")}')
    cal = json.load(open(RES / 'calib780.json', encoding='utf-8'))
    setup = json.load(open(RES / 'calib_setup780.json', encoding='utf-8'))
    rng = np.random.default_rng(SEED_RUN)
    D = CB.v_data('V-A1')
    g = D['gate']
    out = {'gate': g, 'z_star': cal['z_star'], 'fallback': cal['fallback'], 'n_pages': len(D['ids'])}
    if not g['passes']:
        out['verdict'] = 'CODING FAILED'
        json.dump(out, open(RES / 'verdict780.json', 'w', encoding='utf-8'), indent=1)
        log('VERDICT: CODING FAILED')
        return
    C, Y = K.picture_matrices('V', D['ids'], D['codes'], g, D['heights'])
    eng = K.Engine(D['T'], C, Y, D['X'])
    res = K.decide(eng, D['blocks'], rng)
    out['primary'] = res
    zs = cal['z_star']
    if cal['fallback']:
        outside = {m: res[m]['p_local'] <= 0.005 for m in ('T1', 'T2')}
        rule = 'fallback: exact N-local p <= 0.005'
    else:
        outside = {m: res[m]['Z'] > zs for m in ('T1', 'T2')}
        rule = f'Z = min(z_local, z_shift) > z* = {zs:.3f}'
    out['rule'], out['outside'] = rule, outside
    # descriptive companions
    desc = {}
    eng_ns = K.Engine(D['T'], C, Y, D['X'], use_style=False)
    desc['no_style'] = K.decide(eng_ns, D['blocks'], rng)
    desc['raw_matrices'] = K.decide(K.Engine(D['T'], C, Y, D['X'], centre=False), D['blocks'], rng)
    desc['spearman_partial_S'] = spearman_partial(eng, D['T'], C, Y, D['X'])
    T_int = K.text_similarity(K.voynich_texts(D['ids'], interior_only=True), 'V')
    desc['line_interior'] = K.decide(K.Engine(T_int, C, Y, D['X']), D['blocks'], rng)
    geom = json.load(open(K.DATA / 'geometry.json', encoding='utf-8'))
    one = [k for k, f in enumerate(D['ids'])
           if str(geom[f].get('n_plants_locator', 1)) in ('1', 'None')
           and sum(str(D['codes'][s].get(f, {}).get('n_plants', '1')) == '2+' for s in 'AB') < 2]
    if len(one) < len(D['ids']):
        sub = np.array(one)
        Dp = [D['pages'][k] for k in one]
        X1, _ = K.v_covariates(Dp, D['feats'], [len(D['toks'][k]) for k in one])
        T1 = {m: M[np.ix_(sub, sub)] for m, M in D['T'].items()}
        desc['single_plant_pages'] = dict(K.decide(K.Engine(T1, C[np.ix_(sub, sub)], Y[np.ix_(sub, sub)], X1),
                                                   K.v_blocks(Dp), rng), n=len(one))
    out['descriptive'] = desc
    style_only = (not any(outside.values())) and any(desc['no_style'][m]['Z'] > zs for m in ('T1', 'T2'))
    # verdict
    k4 = cal.get('k4', {})
    gp = k4.get('main', {}).get('genre_power', float('nan'))
    br_ok = setup['br_gate']['passes']
    if any(outside.values()):
        level = 'T1 word' if outside['T1'] else 'T2 glyph-trigram'
        verdict = 'CO-VARIES WITH CODED DRAWN CONTENT'
        out['level'] = level
    elif br_ok and gp >= 0.85:
        verdict = 'NOT DETECTED (genre-powered)'
    else:
        verdict = 'NOT DETECTED (unpowered)'
    out['verdict'] = verdict
    out['style_linked_note'] = style_only
    out['genre_power'] = gp
    out['ablation_rows_at_085'] = [a for a, v in k4.items() if v.get('genre_power', 0) >= 0.85]
    out['MDE80'] = {v: cal['k3'][v]['MDE80'] for v in cal['k3']}
    # V-B2 descriptive (V-A1's entered features)
    try:
        DB = CB.v_data('V-B2')
        CBm, YBm = K.picture_matrices('V', DB['ids'], DB['codes'], g, DB['heights'])
        out['V_B2'] = dict(K.decide(K.Engine(DB['T'], CBm, YBm, DB['X']), DB['blocks'], rng), n=len(DB['ids']))
    except Exception as e:  # descriptive arm only
        out['V_B2'] = {'error': repr(e)}
    out['runtime_s'] = time.time() - t0
    json.dump(out, open(RES / 'verdict780.json', 'w', encoding='utf-8'), indent=1, default=float)
    for m in ('T1', 'T2'):
        r = res[m]
        log(f"{m}: S {r['S']:+.4f}; z_local {r['z_local']:+.2f} (p {r['p_local']:.4f}); z_shift {r['z_shift']:+.2f}; Z {r['Z']:+.2f}; outside {outside[m]}")
    log(f"rule: {rule}; VERDICT: {verdict}; genre power {gp}; style-only note {style_only}")
    for k, v in desc.items():
        if isinstance(v, dict) and 'T1' in v:
            log(f"  {k}: " + '; '.join(f"{m} S {v[m]['S']:+.4f} Z {v[m]['Z']:+.2f}" for m in ('T1', 'T2')))
        else:
            log(f"  {k}: {v}")
    vb = out['V_B2']
    if 'T1' in vb:
        log('  V-B2: ' + '; '.join(f"{m} S {vb[m]['S']:+.4f} z_local {vb[m]['z_local']:+.2f} z_shift {vb[m]['z_shift']:+.2f}" for m in ('T1', 'T2')))
    log('done')


if __name__ == '__main__':
    main()
