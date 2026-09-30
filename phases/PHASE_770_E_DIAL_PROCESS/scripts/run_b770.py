#!/usr/bin/env python3
"""PHASE_770: run on B after the lock (PRE_REGISTRATION.md section 15). Do not run before LOCK is filled.

Arm 0  S3c on the context-adjusted outcome (H, ZL); the one-unit sensitivity.
Arm A  A2 (v3 classifier, feature version fixed at lock) with the gate at B's point, the A3 veto, the ZL rule and the
       no-flip checks; descriptives A1 (per stratum, effective folios, LOFO), A4, A5 (with plant envelopes), exclusion list.
Arm B  B1 per dial (H, ZL; MIN also on F), strength and its lower 80% bound, B2 (split fixed at lock; joint pairing
       null; Westfall-Young), the NOT SHARED power check by simulation at the lower bound (folio and drift versions),
       B3, the consistent-run sensitivity, and the descriptives (all pairs, tetrads, paragraph share, OKOT, BENCH,
       crowding probe).
Arm C  C1 (null (b); ZL; Q13 / Q20 signs; leaf / opening; quire halves; without f76r; null (a) descriptive), C2 and face K.
D0     the e-dial S3c on Currier A.
Writes results/e_dial_process_B.json and results/run_log.txt (opened lazily).
"""
from __future__ import annotations

import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cal770 as C  # noqa: E402
import calB770 as CB  # noqa: E402
import cal0_770 as C0  # noqa: E402
import clf770 as K  # noqa: E402
import desc770 as D  # noqa: E402
import bank770 as BK  # noqa: E402
import excl770 as EX  # noqa: E402

LOCK = 'phase770-lock'    # git tag on the lock commit; the scripts must be unchanged since the tag (R4)
A2_VERSION = 'raw'        # fixed at lock from the gate map (clf_v3_H81_770.json)
B2_SPLIT = 'block'        # fixed at lock from calibrated power under drift (calBj_*.json)
B2_ZCRIT = 3.2            # calibrated critical |z| (99th percentile of max |z| over the three dials under the worst
                          # H0 of the joint certification, calBj770.py), fixed at lock
B3_ZCRIT = 3.76           # calibrated critical |z| for B3 (calB3_770.py), fixed at lock
NPERM = 2000
EXTEND = True            # bank extension at run time
MAX_EXT_ROUNDS = 20      # extension rounds per bank
EXT_DRAWS = 30000        # draws per model per extension round
DRY = False
DRY_STREAM = None
OUT = HERE.parent / 'results'
BANKDIR = OUT / 'calib/bank'
T0 = time.time()
LOG = None


def log(*a):
    global LOG
    if LOG is None:
        LOG = open(OUT / 'run_log.txt', 'w', encoding='utf-8')
    msg = f'[{time.time() - T0:8.1f}s] ' + ' '.join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + '\n')
    LOG.flush()


def verify_lock():
    """The scripts must equal the lock tag's version, and the frozen banks must match their recorded checksums."""
    import hashlib
    import subprocess
    root = HERE.parents[2]
    r = subprocess.run(['git', 'rev-parse', '--verify', LOCK], cwd=root, capture_output=True, text=True)
    assert r.returncode == 0, f'lock tag {LOCK} not found'
    r = subprocess.run(['git', 'diff', '--quiet', LOCK, '--', 'phases/PHASE_770_E_DIAL_PROCESS/scripts'], cwd=root)
    assert r.returncode == 0, 'scripts changed since the lock tag'
    sums = dict(line.split(': ') for line in (OUT / 'calib/bank_checksums.txt').read_text().split('\n') if ': ' in line)
    for name, digest in sums.items():
        name = name.lstrip('*')
        h = hashlib.sha256((BANKDIR / name).read_bytes()).hexdigest()
        assert h == digest.strip(), f'bank checksum mismatch: {name}'
    log('lock verified:', LOCK, '| banks match their checksums')


def perm_p(St, yy, stat, nperm, seed, two_sided=False):
    rng = np.random.default_rng(seed)
    cm = C.E.cell_means(yy, St.cell)
    R0 = (yy - cm)[:, None]
    o = float(stat(R0)[0])
    if not np.isfinite(o):
        return o, 1.0, R0, None
    null = []
    for _ in range(0, nperm, 250):
        Yp = C.B.perm_batch(yy, St.cell, 250, rng)
        null.append(stat((Yp - cm[None, :]).T))
    null = np.concatenate(null)
    if two_sided:
        mu = np.nanmean(null)
        p = float((1 + (np.abs(null - mu) >= abs(o - mu)).sum()) / (1 + nperm))
    else:
        p = float((1 + (null >= o).sum()) / (1 + nperm))
    return o, p, R0, null


def load_b_track(tr, extra=('f76r',)):
    """B records for another transcription track (same filters as the H analysis set)."""
    from scripts.voynich import Transcript
    pv = C.E.zl_page_vars()
    rows = []
    for t in Transcript().all(h_only=False):
        if t.transcriber != tr or t.language != 'B' or t.is_label:
            continue
        pl = t.placement or ''
        if not (pl.startswith('P') or (t.folio in extra and pl.startswith('R'))):
            continue
        w = t.word.strip()
        if w:
            rows.append((w, t.folio, t.line, t.par_initial, t.section, '*' in w))
    return C.X.fix_hands(C.E._assemble(rows, pv), {'f115r': '3'})


# ------------------------------------------------------------------------------------------------ Arm 0
def arm0(sets):
    out = {}
    for label in ('H', 'ZL'):
        A = sets[label]
        St = C.Stats(A)
        y = A.O['y']
        raw = float(St.S3c(St.residuals(y[:, None]))[0])
        ya = C0.adjust(A, y[:, None])[:, 0]
        o, p, _, _ = perm_p(St, ya[St.m], St.S3c, NPERM, zlib.crc32(f'arm0/{label}'.encode()))
        ya1 = C0.adjust(A, y[:, None], attr='prev1')[:, 0]
        o1, p1, _, _ = perm_p(St, ya1[St.m], St.S3c, NPERM, zlib.crc32(f'arm0/{label}/1'.encode()))
        out[label] = {'S3c': raw, 'S3c_adj': o, 'p_adj': p, 'ratio': o / raw if raw else None,
                      'S3c_adj_prev1': o1, 'p_adj_prev1': p1}
        log('Arm 0', label, out[label])
    cal = json.load(open(OUT / 'calib/cal0.json'))
    pw_ok = cal['H81']['M1_x1.0']['power_01'] >= 0.9 and cal['ZL']['M1_x1.0']['power_01'] >= 0.9
    h = out['H']
    if h['S3c'] < 0.16:
        v = 'UNRESOLVED (no component to explain: unadjusted S3c < 0.16)'
    elif h['S3c_adj'] < 0.16:
        v = 'NOTE (S3c_adj below the materiality line)'
    elif h['p_adj'] > 0.01:
        v = 'NOTE (not significant at calibrated power >= 0.9)' if pw_ok else 'UNRESOLVED (power < 0.9)'
    else:
        v = 'C2086 STANDS against the neighbour-context model'
    if v.startswith('C2086') and (out['ZL']['S3c_adj'] < 0.16 or out['ZL']['p_adj'] > 0.01):
        v += ' (ZL-dependent: ZL leg fails)'
    out['verdict'] = v
    log('Arm 0 verdict:', v)
    return out


# ------------------------------------------------------------------------------------------------ Arm A
def observe(A):
    St = C.Stats(A)
    y = A.O['y'][St.m]
    R0 = (y - C.E.cell_means(y, St.cell))[:, None]
    s3c, s3f = float(St.S3c(R0)[0]), float(St.S3far(R0)[0])
    F = St.features(St.quarter_cov(R0), scale_free=(A2_VERSION == 'free'))[0]
    return St, R0, s3c, s3f, F


def load_bank(set_name, A, St, s3c, s3f):
    """The frozen bank for a set (generated if absent), extended with frozen seeds while any model has < 200
    replicates within +-0.03 of B's (S3c, S3far), up to MAX_DRAWS per model in total."""
    tag = f'v3_{set_name}_770'
    if not (BANKDIR / f'bank_{tag}.npz').exists():
        P = C.Plants(A)
        BK.T0 = time.time()
        keep, counts, d14 = BK.generate(A, St, P, tag, n_accept=BK.N_ACCEPT, max_draws=BK.MAX_DRAWS)
        BK.save(keep, counts, d14, tag, set_name, 770)
    bank = dict(np.load(BANKDIR / f'bank_{tag}.npz'))
    info = json.load(open(BANKDIR / f'bank_{tag}.json'))
    ext = 0
    while EXTEND and ext < MAX_EXT_ROUNDS:
        near = (np.abs(bank['S3c'] - s3c) <= 0.03) & (np.abs(bank['S3far'] - s3f) <= 0.03)
        short = [m for m in info['classes'] if (np.asarray(bank['model'])[near] == m).sum() < 200
                 and info['counts'][m]['draws'] < BK.MAX_DRAWS]
        if not short:
            break
        ext += 1
        P = C.Plants(A)
        keep, counts, _ = BK.generate(A, St, P, f'{tag}_ext{ext}', models=short, with_d14=False,
                                      n_accept=BK.N_ACCEPT, max_draws=EXT_DRAWS)
        for k in bank:
            bank[k] = np.concatenate([bank[k], np.array(keep[k])]) if len(keep[k]) else bank[k]
        for m in short:
            info['counts'][m]['draws'] += counts[m]['draws']
            info['counts'][m]['S3c_accepted'] += counts[m]['S3c_accepted']
        log('bank', set_name, 'extension', ext, 'models', short)
    info['extensions'] = ext
    return bank, info


def gate_at(clf, s3c, s3f):
    rows, ok = {}, True
    for m, cls in clf.classes.items():
        if cls not in ('S', 'P', 'X'):
            continue
        ev = clf.split[m][2]
        Zev = clf.Z[ev]
        sel = (np.abs(Zev[:, 0] - s3c) <= 0.03) & (np.abs(Zev[:, 1] - s3f) <= 0.03)
        n = int(sel.sum())
        if n < 30:
            rows[m] = {'n': n}
            continue
        v, _ = clf.verdict(Zev[sel])
        fS, fP = float((v == 'STATIC-DOMINANT').mean()), float((v == 'POSITION-DEPENDENT-DOMINANT').mean())
        r = {'n': n, 'static': fS, 'position': fP}
        if cls == 'S':
            r['pass'] = fS >= 0.70 and fP <= 0.05
        elif cls == 'P':
            r['pass'] = fP >= 0.70 and fS <= 0.05
        elif clf.d14[m] <= 0.15:                         # mixtures gated by their own D14 class
            r['pass'] = fP <= 0.15
        elif clf.d14[m] >= 0.5:
            r['pass'] = fS <= 0.15
        if 'pass' in r and not r['pass']:
            ok = False
        rows[m] = r
    nS = sum(1 for m, r in rows.items() if 'pass' in r and clf.classes[m] == 'S')
    nP = sum(1 for m, r in rows.items() if 'pass' in r and clf.classes[m] == 'P')
    return {'gate_pass': ok and nS > 0 and nP > 0, 'n_static_evaluated': nS, 'n_position_evaluated': nP, 'rows': rows}


def fresh_gate(A, St, clf, s3c, s3f, target=100, max_draws=60000):
    """The gate at B's point on fresh replicates (frozen seed tag 'gatefresh'), not the replicates the thresholds were
    selected on (lean-expert lock audit R9): for every gated model (frozen classes S and P; mixtures with D14 <= 0.15
    or >= 0.5), draws with the bank's scale prior until `target` replicates fall within +-0.03 of (S3c, S3far) or
    max_draws; the same criteria as the gate map; both classes must be evaluated (n >= 30)."""
    pilot = json.load(open(OUT / 'calib/pilot.json'))
    P = C.Plants(A)
    rows, ok = {}, True
    for m, cls in clf.classes.items():
        gated = cls in ('S', 'P') or (cls == 'X' and (clf.d14[m] <= 0.15 or clf.d14[m] >= 0.5))
        if not gated:
            continue
        s_star = pilot['grid_S3c'][m]['s_star']
        rng = np.random.default_rng(zlib.crc32(f'gatefresh/{m}'.encode()))
        Zs, n_draw = [], 0
        while sum(len(z) for z in Zs) < target and n_draw < max_draws:
            scales = np.exp(rng.uniform(np.log(0.55 * s_star), np.log(1.5 * s_star), BK.BATCH))
            R = St.residuals(P.draw(m, scales, rng))
            a, b = St.S3c(R), St.S3far(R)
            ok_ = (np.abs(a - s3c) <= 0.03) & (np.abs(b - s3f) <= 0.03)
            n_draw += BK.BATCH
            if ok_.any():
                F = St.features(St.quarter_cov(R[:, ok_]), scale_free=(A2_VERSION == 'free'))
                Zs.append(np.column_stack([a[ok_], b[ok_], F]))
        Z = np.concatenate(Zs) if Zs else np.zeros((0, 2))
        n = len(Z)
        if n < 30:
            rows[m] = {'n': n, 'draws': n_draw}
            continue
        v, _ = clf.verdict(Z)
        fS, fP = float((v == 'STATIC-DOMINANT').mean()), float((v == 'POSITION-DEPENDENT-DOMINANT').mean())
        r = {'n': n, 'draws': n_draw, 'static': fS, 'position': fP}
        if cls == 'S':
            r['pass'] = fS >= 0.70 and fP <= 0.05
        elif cls == 'P':
            r['pass'] = fP >= 0.70 and fS <= 0.05
        elif clf.d14[m] <= 0.15:
            r['pass'] = fP <= 0.15
        else:
            r['pass'] = fS <= 0.15
        ok = ok and r['pass']
        rows[m] = r
    nS = sum(1 for m, r in rows.items() if 'pass' in r and clf.classes[m] == 'S')
    nP = sum(1 for m, r in rows.items() if 'pass' in r and clf.classes[m] == 'P')
    return {'gate_pass': ok and nS > 0 and nP > 0, 'n_static_evaluated': nS, 'n_position_evaluated': nP, 'rows': rows}


def classify(set_name, A):
    St, R0, s3c, s3f, F = observe(A)
    bank, info = load_bank(set_name, A, St, s3c, s3f)
    ref = json.load(open(BANKDIR / 'bank_v3_H81_770.json'))       # classes and D14 frozen from the H81 bank (R2)
    info['classes'], info['D14'] = ref['classes'], ref['D14']
    clf = K.Classifier(bank, info, A2_VERSION)
    v, sc = clf.verdict(np.concatenate([[s3c, s3f], F])[None])
    return {'S3c': s3c, 'S3far': s3f, 'features': F.tolist(), 'verdict': str(v[0]), 'P_static': float(sc['pS'][0]),
            'log_bf_new': float(sc['log_bf_new'][0]), 'fit_ok': bool(sc['fit_ok'][0]), 'best_model': sc['best'][0],
            'bank_extensions': info.get('extensions', 0)}, clf, bank, St, R0


def armA(sets):
    out = {}
    h, clf, bank, St, R0 = classify('H81', sets['H'])
    out['H'] = h
    out['gate_at_B_in_sample'] = gate_at(clf, h['S3c'], h['S3far'])
    in_window = BK.S3C_LO <= h['S3c'] <= BK.S3C_HI
    out['gate_at_B'] = fresh_gate(sets['H'], St, clf, h['S3c'], h['S3far']) if in_window else {'gate_pass': False}
    log('Arm A gate at B (fresh draws):', {k: out['gate_at_B'][k] for k in out['gate_at_B'] if k != 'rows'})
    if DRY:                                           # dry run: exercise the fresh-draw gate at a fixed point
        out['dry_fresh_gate_check'] = fresh_gate(sets['H'], St, clf, 0.32, 0.09, target=30, max_draws=2000)
        log('dry fresh-gate check:', {k: v for k, v in out['dry_fresh_gate_check'].items() if k != 'rows'})
    D_, pD = C.ParaOrder(St, nperm=NPERM).stat_and_p(R0)
    out['A3'] = {'D': float(D_[0]), 'p': float(pD[0])}
    z, _, _, _, _ = classify('ZL', sets['ZL'])
    out['ZL'] = z
    for name, key in (('H80', 'H80'), ('H81_full3', 'full3'), ('H81_cons3', 'cons3')):
        out[f'noflip_{key}'] = classify(name, sets[key])[0]
    # verdict
    v = h['verdict']
    reasons = []
    if not (BK.S3C_LO <= h['S3c'] <= BK.S3C_HI):                   # applicability: B inside the bank window
        v, reasons = 'UNRESOLVED', reasons + ['S3c outside the bank window']
    if not out['gate_at_B']['gate_pass']:
        v, reasons = 'UNRESOLVED', reasons + ['gate fails at B\'s point']
    if v == 'STATIC-DOMINANT' and out['A3']['p'] <= 0.01:
        v, reasons = 'UNRESOLVED', reasons + ['A3 veto']
    if v in ('STATIC-DOMINANT', 'POSITION-DEPENDENT-DOMINANT'):
        zin = BK.S3C_LO <= out['ZL']['S3c'] <= BK.S3C_HI
        pz = out['ZL']['P_static'] if v == 'STATIC-DOMINANT' else 1 - out['ZL']['P_static']
        if not zin:
            v, reasons = 'UNRESOLVED', reasons + ['ZL outside the bank window']
        elif pz < 0.5:
            v, reasons = 'UNRESOLVED', reasons + ['ZL rule']
    if v in ('STATIC-DOMINANT', 'POSITION-DEPENDENT-DOMINANT'):
        for key in ('H80', 'full3', 'cons3'):
            o = out[f'noflip_{key}']
            if not (BK.S3C_LO <= o['S3c'] <= BK.S3C_HI):
                o['evaluable'] = False                  # outside the bank window: reported, no veto (R1)
                continue
            o['evaluable'] = True
            opp = (1 - o['P_static']) if v == 'STATIC-DOMINANT' else o['P_static']
            if opp >= 0.8:
                v, reasons = 'UNRESOLVED', reasons + [f'no-flip {key}']
    bound = {'STATIC-DOMINANT': 'position-dependent models with D14 >= 0.5 disfavoured; slow drift (D14 ~0.2) not '
                                'distinguished',
             'POSITION-DEPENDENT-DOMINANT': 'static models with D14 <= 0.15 disfavoured; mechanism not '
                                            'distinguished'}.get(v)
    out['verdict'] = {'verdict': v, 'bound': bound, 'reasons_unresolved': reasons}
    log('Arm A:', out['verdict'], '| H', {k: h[k] for k in ('S3c', 'S3far', 'P_static', 'log_bf_new', 'fit_ok',
                                                            'best_model')}, '| A3 p', out['A3']['p'])
    # descriptives
    out['A1'] = D.a1_descriptives(St, R0)
    out['A4'] = {}
    for k, msk in D.edge_versions(sets['H']).items():
        Asub = C.Analysis('E', recs=sets['H'].recs, amap_leg=(sets['H'].amap, sets['H'].leg))
        Asub.O = C.subset_O(sets['H'].O, msk)
        out['A4'][k] = dict(zip(('S3c', 'S3far'), D.s3_centred(Asub)))
    V = D.Variogram(St)
    obs = V(R0)
    P = C.Plants(sets['H'])
    pilot = json.load(open(OUT / 'calib/pilot.json'))
    env = {}
    rng = np.random.default_rng(7760)
    for m in ('M1', 'M2b:4', 'M3', 'M6:0.97', 'M8:20'):
        Y = P.draw(m, np.full(100, pilot['grid_S3c'][m]['s_star']), rng)
        vals = V(St.residuals(Y))
        env[m] = {str(k_): [float(np.quantile(v_, 0.05)), float(np.quantile(v_, 0.95))] for k_, v_ in vals.items()}
    out['A5'] = {'observed': {str(k_): float(v_[0]) for k_, v_ in obs.items()}, 'envelopes_5_95': env}
    near = np.abs(bank['S3c'] - h['S3c']) <= 0.03
    sub = {k_: v_[near] for k_, v_ in bank.items()}
    info = json.load(open(BANKDIR / 'bank_v3_H81_770.json'))
    ex = EX.Excluder(sub, info)
    pv = ex.pvals(np.concatenate([[h['S3far']], St.features(St.quarter_cov(R0))[0]])[None])
    out['exclusion_p'] = {m: float(p_[0]) for m, p_ in pv.items()}
    log('Arm A exclusion (p <= 0.01):', [m for m, p_ in out['exclusion_p'].items() if p_ <= 0.01])
    return out


# ------------------------------------------------------------------------------------------------ Arm B
def build_pairs(recs, amap_leg, zl=False, split=None, subset=None):
    pairs = {}
    for yd in CB.DIALS_Y:
        ce = ('prev',) if yd == 'CS' else ()
        AE = C.Analysis('E', recs=recs, amap_leg=amap_leg, zl=zl, pair_dials=('E', yd), subset=subset)
        sub_y = subset if (subset is None or yd != 'MIN') else 'consZ'
        AY = C.Analysis(yd, recs=recs, amap_leg=amap_leg, zl=zl, pair_dials=('E', yd), cell_extra=ce, subset=sub_y)
        pairs[yd] = (AE, AY, CB.CrossDial(AE, AY, split=split or B2_SPLIT))
    return pairs


def b2_joint(pairs, seed):
    """X per dial with the joint pairing null (one relabelling for all dials) and Westfall-Young adjusted p."""
    Pi = list(pairs.values())[0][2].relabellings(NPERM, seed)
    obs, zo, zn = {}, {}, {}
    for yd, (AE, AY, CD) in pairs.items():
        RE, RY = CD.residuals(AE.O['y'][:, None], AY.O['y'][:, None])
        o, n = CD.X_stat(RE, RY, Pi)
        z, zn_, p2 = CB.z_and_p(o, n)
        obs[yd] = {'X': float(o[0]), 'z': float(z[0]), 'p2': float(p2[0])}
        zo[yd], zn[yd] = float(z[0]), zn_[:, 0]
    mx = np.max(np.abs(np.stack([zn[yd] for yd in pairs], axis=1)), axis=1)
    for yd in pairs:
        obs[yd]['p_WY'] = float((1 + (mx >= abs(zo[yd])).sum()) / (1 + NPERM)) if np.isfinite(zo[yd]) else 1.0
    return obs


def strength_bounds(yd, s3c_obs):
    """Folio logit-SD estimate and its lower 80% bound from the dial's calibration curve (mean and SD of S3c under
    M1 plants on the dial's own cells)."""
    cal = json.load(open(OUT / 'calib/calB.json'))['B1'][yd]['curve']
    xs = np.array(sorted(float(k) for k in cal))
    mu = np.array([cal[str(x)]['S3c_mean'] for x in xs])
    sd = np.array([cal[str(x)]['S3c_sd'] for x in xs])
    est = float(np.interp(s3c_obs, mu, xs)) if s3c_obs > mu[0] else 0.0
    lower = float(np.interp(s3c_obs, mu + 0.84 * sd, xs)) if s3c_obs > (mu + 0.84 * sd)[0] else 0.0
    return est, lower, bool(s3c_obs > mu[-1])


def power_at(pairs_yd, yd, s_lower, split):
    """Power of B2 (|z| >= B2_ZCRIT) at rho 0.7 with Y at the lower strength bound: folio-level and drifting versions,
    200 replicates each, frozen seeds; returns the minimum."""
    AE, AY, _ = pairs_yd
    CD = CB.CrossDial(AE, AY, split=split)
    PP = CB.PairPlants(AE, AY)
    pilot = json.load(open(OUT / 'calib/pilot.json'))
    sE, s6 = pilot['grid_S3c']['M1']['s_star'], pilot['grid_S3c']['M6:0.97']['s_star']
    Pi = CD.relabellings(500, 7770)
    res = {}
    for kind in ('folio', 'drift'):
        rng = np.random.default_rng(zlib.crc32(f'power/{yd}/{kind}'.encode()))
        ps = []
        for _ in range(4):
            YE, YY = PP.draw(kind, sE if kind == 'folio' else s6, s_lower if kind == 'folio' else s_lower * s6 / sE,
                             0.7, rng, 50)
            RE, RY = CD.residuals(YE, YY)
            o, n = CD.X_stat(RE, RY, Pi)
            ps.append(np.abs(CB.z_and_p(o, n)[0]) >= B2_ZCRIT)
        res[kind] = float(np.concatenate(ps).mean())
    res['min'] = min(res.values())
    return res


def armB(sets):
    out = {'split': B2_SPLIT}
    H, Z = sets['H'], sets['ZL']
    amap_leg = (H.amap, H.leg)
    pairs = build_pairs(H.recs, amap_leg)
    zpairs = build_pairs(Z.recs, (None, H.leg), zl=True)
    # B1
    out['B1'] = {}
    f_recs = load_b_track('F')
    for yd, (AE, AY, CD) in pairs.items():
        r = {}
        for label, A in (('H', AY), ('ZL', zpairs[yd][1])):
            St = C.Stats(A)
            o, p, _, _ = perm_p(St, A.O['y'][St.m], St.S3c, NPERM, zlib.crc32(f'B1/{yd}/{label}'.encode()))
            r[label] = {'S3c': o, 'p': p}
        if yd == 'MIN':
            AF = C.Analysis('MIN', recs=f_recs, amap_leg=(None, H.leg))
            St = C.Stats(AF)
            o, p, _, _ = perm_p(St, AF.O['y'][St.m], St.S3c, NPERM, zlib.crc32('B1/MIN/F'.encode()))
            r['F_sensitivity'] = {'S3c': o, 'p': p}
        r['own_component'] = bool(r['H']['p'] <= 0.01 and np.sign(r['ZL']['S3c']) == np.sign(r['H']['S3c'])
                                  and r['ZL']['p'] <= 0.05)
        r['strength'], r['strength_lower80'], r['strength_beyond_grid'] = strength_bounds(yd, r['H']['S3c'])
        out['B1'][yd] = r
        log('B1', yd, r)
    # B2 on H (joint null, Westfall-Young) and on ZL
    out['B2_H'] = b2_joint(pairs, 7771)
    out['B2_ZL'] = b2_joint(zpairs, 7772)
    out['B2_verdict'] = {}
    for yd in CB.DIALS_Y:
        h, z = out['B2_H'][yd], out['B2_ZL'][yd]
        if abs(h['z']) >= B2_ZCRIT and np.sign(z['X']) == np.sign(h['X']) and z['p2'] <= 0.05:
            v = 'SHARED (+)' if h['X'] > 0 else 'SHARED (-)'
        elif h['p2'] > 0.05 and z['p2'] > 0.05:
            pw = power_at(pairs[yd], yd, out['B1'][yd]['strength_lower80'], B2_SPLIT)
            out['B1'][yd]['power_at_lower80'] = pw
            v = 'NOT SHARED (bounded)' if pw['min'] >= 0.8 else 'UNRESOLVED (power < 0.8 at the lower bound)'
        else:
            v = 'UNRESOLVED'
        out['B2_verdict'][yd] = v
    log('B2 H', out['B2_H'], '| ZL', out['B2_ZL'], '| verdicts', out['B2_verdict'])
    # B3
    out['B3'] = {}
    for label, P_ in (('H', pairs), ('ZL', zpairs)):
        Pi = list(P_.values())[0][2].relabellings(NPERM, 7773)
        for yd, (AE, AY, CD) in P_.items():
            RE, RY = CD.residuals(AE.O['y'][:, None], AY.O['y'][:, None])
            o3, n3 = CD.B3_stat(RE, RY, Pi)
            z, _, p2 = CB.z_and_p(o3, n3)
            out['B3'].setdefault(yd, {})[label] = {'B3': float(o3[0]), 'z': float(z[0]), 'p2': float(p2[0])}
    for yd, r in out['B3'].items():                   # descriptive (power ~0.06 at the calibrated |z| 3.76)
        r['exceeds_calibrated_z'] = bool(abs(r['H']['z']) >= B3_ZCRIT)
    log('B3', out['B3'])
    # consistent-run sensitivity
    cpairs = build_pairs(H.recs, amap_leg, subset='cons3')
    out['B2_consistent_runs'] = b2_joint(cpairs, 7774)
    log('B2 consistent runs', out['B2_consistent_runs'])
    # descriptives: other dial pairs, tetrads, paragraph share, OKOT / BENCH, crowding probe
    yy = {}
    for a_, b_ in (('CS', 'KTH'), ('CS', 'MIN'), ('KTH', 'MIN')):
        Aa = C.Analysis(a_, recs=H.recs, amap_leg=amap_leg, pair_dials=(a_, b_), cell_extra=('prev',) if a_ == 'CS' else ())
        Ab = C.Analysis(b_, recs=H.recs, amap_leg=amap_leg, pair_dials=(a_, b_))
        CD = CB.CrossDial(Aa, Ab, split=B2_SPLIT)
        Pi = CD.relabellings(NPERM, 7775)
        Ra, Rb = CD.residuals(Aa.O['y'][:, None], Ab.O['y'][:, None])
        o, n = CD.X_stat(Ra, Rb, Pi)
        yy[f'{a_}-{b_}'] = {'X': float(o[0]), 'p2': float(CB.z_and_p(o, n)[2][0])}
    out['other_pairs'] = yy
    r = {('E', d): out['B2_H'][d]['X'] for d in CB.DIALS_Y}
    r.update({('CS', 'KTH'): yy['CS-KTH']['X'], ('CS', 'MIN'): yy['CS-MIN']['X'], ('KTH', 'MIN'): yy['KTH-MIN']['X']})
    g = lambda a, b: r.get((a, b), r.get((b, a)))  # noqa: E731
    out['tetrads'] = {'E.CS*KTH.MIN - E.KTH*CS.MIN': g('E', 'CS') * g('KTH', 'MIN') - g('E', 'KTH') * g('CS', 'MIN'),
                      'E.CS*KTH.MIN - E.MIN*CS.KTH': g('E', 'CS') * g('KTH', 'MIN') - g('E', 'MIN') * g('CS', 'KTH'),
                      'E.KTH*CS.MIN - E.MIN*CS.KTH': g('E', 'KTH') * g('CS', 'MIN') - g('E', 'MIN') * g('CS', 'KTH')}
    out['paragraph_share'] = {}
    for yd in ('E',) + CB.DIALS_Y:
        A = C.Analysis(yd, recs=H.recs, amap_leg=amap_leg, cell_extra=('prev',) if yd == 'CS' else ())
        r_ = C.B.Battery(A.O, A.Xcov).evaluate(A.O['y'], nperm=NPERM, seed=7776, stats=('S3P',), within_folio_para=True)
        out['paragraph_share'][yd] = {'S3P_within': r_['S3P'], 'p': r_['p_S3P']}
    out['descriptive_dials'] = {}
    for yd in ('OKOT', 'BENCH'):
        A = C.Analysis(yd, recs=H.recs, amap_leg=amap_leg)
        St = C.Stats(A)
        o, p, _, _ = perm_p(St, A.O['y'][St.m], St.S3c, NPERM, zlib.crc32(f'B1/{yd}'.encode()))
        AE = C.Analysis('E', recs=H.recs, amap_leg=amap_leg, pair_dials=('E', yd))
        AY = C.Analysis(yd, recs=H.recs, amap_leg=amap_leg, pair_dials=('E', yd))
        CD = CB.CrossDial(AE, AY, split=B2_SPLIT)
        Pi = CD.relabellings(NPERM, 7777)
        RE, RY = CD.residuals(AE.O['y'][:, None], AY.O['y'][:, None])
        xo, xn = CD.X_stat(RE, RY, Pi)
        out['descriptive_dials'][yd] = {'S3c': o, 'p': p, 'X': float(xo[0]), 'X_p2': float(CB.z_and_p(xo, xn)[2][0])}
    out['crowding'] = {}
    for yd in ('E',) + CB.DIALS_Y:
        A = C.Analysis(yd, recs=H.recs, amap_leg=amap_leg, cell_extra=('prev',) if yd == 'CS' else ())
        out['crowding'][yd] = D.crowding_probe(A, nperm=NPERM)
    log('Arm B descriptives', {k: out[k] for k in ('other_pairs', 'tetrads', 'paragraph_share', 'descriptive_dials')})
    return out


# ------------------------------------------------------------------------------------------------ Arm C
def c1(A):
    St = C.Stats(A)
    y = A.O['y'][St.m]
    R0 = (y - C.E.cell_means(y, St.cell))[:, None]
    d = St.page_turn_terms(R0)[:, 0]
    K_ = float(d.sum())
    _, pb = St.page_turn_test(R0, nflip=NPERM * 5, by='chain')
    _, pa = St.page_turn_test(R0, nflip=NPERM * 5, by='transition')
    r = {'K': K_, 'p_b': float(pb[0]), 'p_a_descriptive': float(pa[0]),
         'K_Q13': float(d[St.T_quire == 'M'].sum()), 'K_Q20': float(d[St.T_quire == 'T'].sum()),
         'K_leaf': float(d[St.T_kind == 'leaf_turn'].sum()), 'K_opening': float(d[St.T_kind == 'opening'].sum()),
         'K_quire_halves': {f'{qn}_half{h}': float(d[(St.T_quire == q) & (St.T_half == h)].sum())
                            for q, qn in (('M', 'Q13'), ('T', 'Q20')) for h in (0, 1)},
         'face_K': float(St.page_turn_terms(R0, St.FACES)[:, 0].sum()), 'n_transitions': int(len(d))}
    return r, St, R0


def armC(sets):
    out = {}
    h, St, R0 = c1(sets['H'])
    z, _, _ = c1(sets['ZL'])
    n80, _, _ = c1(sets['H80'])
    out.update({'H': h, 'ZL': z, 'without_f76r': n80})
    def h_ok(r):
        return bool(r['K'] > 0 and r['p_b'] <= 0.01
                    and np.sign(r['K_Q13']) == np.sign(r['K_Q20']) == np.sign(r['K']))
    # descriptive (lean-expert lock audit E1: power under null (b) 0.06-0.12 at B's strength)
    rule = h_ok(h) and np.sign(z['K']) == np.sign(h['K']) and z['p_b'] <= 0.05
    v = ('descriptive: the pre-specified continuity criteria are met' if rule
         else 'descriptive: the pre-specified continuity criteria are not met')
    if h_ok(h) != h_ok(n80):
        v += ' [80-folio-set-dependent: f76r excluded, f115r uninformative]'
    out['verdict'] = v
    log('Arm C:', v, '| H', {k: h[k] for k in ('K', 'p_b', 'K_Q13', 'K_Q20', 'K_leaf', 'K_opening', 'face_K')},
        '| ZL K', z['K'], 'p_b', z['p_b'])
    out['C2'] = D.c2_summary(St, R0, nperm=NPERM)
    log('C2', out['C2'])
    return out


# ------------------------------------------------------------------------------------------------ D0
def d0():
    recs = D.load_a_h()
    if DRY:                                           # dry run: a habit3b control poured into Currier A's skeleton
        recs = C.E.pour_tokens(recs, DRY_STREAM)
    A = C.Analysis('E', recs=recs, amap_leg=(None, {}))
    St = C.Stats(A)
    o, p, _, _ = perm_p(St, A.O['y'][St.m], St.S3c, NPERM, 7780)
    r = {'folios': len(A.pages), 'informative': int(St.m.sum()), 'S3c': o, 'p': p}
    log('D0 Currier A:', r)
    return r


def dry_setup():
    """DRY RUN (code check before the lock; never on B): a habit3b control stream is poured into B's skeleton for every
    analysis set (H, ZL, F, 80-folio), small banks with a 'dry' tag, outputs in results/dryrun/. Exercises every code
    path without computing any statistic on B's outcomes."""
    global OUT, BANKDIR, LOCK, A2_VERSION, B2_SPLIT, load_b_track, EXTEND, DRY, MAX_EXT_ROUNDS, EXT_DRAWS, DRY_STREAM
    EXTEND, DRY, MAX_EXT_ROUNDS, EXT_DRAWS = True, True, 1, 1000       # one small extension round is exercised
    C.DRY_FAKE_CONS = True                                              # consistency subsets: pseudo-random masks
    sys.path.insert(0, str(HERE.parents[2] / 'phases/PHASE_768_HIDDEN_REPEATS/scripts'))
    import hr768 as HR
    import hr768v2 as V
    import neg770v3 as NG
    base_out = OUT
    OUT = base_out / 'dryrun'
    (OUT / 'calib').mkdir(parents=True, exist_ok=True)
    BANKDIR = OUT / 'calib/bank'
    BANKDIR.mkdir(parents=True, exist_ok=True)
    for f in ('cal0.json', 'calB.json', 'pilot.json'):
        (OUT / 'calib' / f).write_text((base_out / 'calib' / f).read_text(encoding='utf-8'), encoding='utf-8')
    BK.OUT = BANKDIR
    BK.N_ACCEPT, BK.MAX_DRAWS = 250, 15000
    BK.MODELS = ['M1', 'M2b:4', 'M3', 'M6:0.95', 'M4:0.99', 'MIX:M3/0.25']   # dry run: one of each class
    global B2_ZCRIT, B3_ZCRIT
    LOCK, A2_VERSION, B2_SPLIT = LOCK or 'DRYRUN', A2_VERSION or 'raw', B2_SPLIT or 'block'
    B2_ZCRIT = B2_ZCRIT or 3.0
    B3_ZCRIT = B3_ZCRIT or 3.0
    sk = HR.b_skeleton()
    flat = lambda lines: [w for ln in lines for w in ln if w is not None]  # noqa: E731
    stream = flat(V.habit3b_lines(sk, 770999))
    extra = flat(V.habit3b_lines(sk, 771999))
    DRY_STREAM = stream + extra
    H0 = C.Analysis('E')
    recsH = C.E.pour_tokens(H0.recs, NG.stream81(stream, extra, H0.recs))
    z_recs = [r for r in C.E.load_b_zl() if r[1] in set(x[1] for x in H0.recs)]
    long_stream = stream + extra
    recsZ = C.E.pour_tokens(C.X.fix_hands(z_recs, {'f115r': '3'}), long_stream)
    recs80 = C.E.pour_tokens(C.E.load_b_h(), stream)
    load_b_track = lambda tr, extra=('f76r',): recsH  # noqa: E731
    leg = (None, H0.leg)
    sets = {'H': C.Analysis('E', recs=recsH, amap_leg=leg), 'ZL': C.Analysis('E', recs=recsZ, amap_leg=leg, zl=True),
            'H80': C.Analysis('E', recs=recs80, amap_leg=leg)}
    sets['full3'] = C.Analysis('E', recs=recsH, amap_leg=leg, cell_extra=('full3',))
    sets['cons3'] = C.Analysis('E', recs=recsH, amap_leg=leg, subset='cons3')
    return sets


def main():
    dry = len(sys.argv) > 1 and sys.argv[1] == '--dry'
    if dry:
        sets = dry_setup()
    assert LOCK and A2_VERSION and B2_SPLIT and B2_ZCRIT and B3_ZCRIT, 'fill the lock constants first'
    res = {'pre_registration': LOCK, 'A2_version': A2_VERSION, 'B2_split': B2_SPLIT, 'dry_run': dry}
    if not dry:
        verify_lock()
        sets = {'H': C.Analysis('E'), 'ZL': C.Analysis('E', zl=True),
                'H80': C.Analysis('E', set81=False, f115r_hand=None)}
        sets['full3'] = C.Analysis('E', recs=sets['H'].recs, amap_leg=(sets['H'].amap, sets['H'].leg),
                                   cell_extra=('full3',))
        sets['cons3'] = C.Analysis('E', subset='cons3')
    res['arm0'] = arm0(sets)
    json.dump(res, open(OUT / 'e_dial_process_B.json', 'w'), indent=1, default=float)
    res['armA'] = armA(sets)
    json.dump(res, open(OUT / 'e_dial_process_B.json', 'w'), indent=1, default=float)
    res['armB'] = armB(sets)
    json.dump(res, open(OUT / 'e_dial_process_B.json', 'w'), indent=1, default=float)
    res['armC'] = armC(sets)
    res['D0'] = d0()
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'e_dial_process_B.json', 'w'), indent=1, default=float)
    log('VERDICTS | Arm 0:', res['arm0']['verdict'], '| Arm A:', res['armA']['verdict']['verdict'],
        '| Arm B:', res['armB']['B2_verdict'], '| Arm C (descriptive):', res['armC']['verdict'])
    log('done')


if __name__ == '__main__':
    main()
