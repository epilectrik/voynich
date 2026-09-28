#!/usr/bin/env python3
"""PHASE_757 panel runner (definitions: ../PRE_REGISTRATION.md, locked commit a5506cb).

Stages (run in order):
  controls  B's own statistics, positive controls M1 and G-EDGE (N=1000), reference members (N=50),
            certification of discriminators (uses only B and the controls).
  naibbe    64 variants x 1000 Naibbe members.
  verdict   outside tests, rerun of non-excluding variants (fresh seed block), locked verdict, PARTIAL tables.

Implementation note: certification needs z* before k is known; it uses k0 = number of candidate discriminators.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import norm, skew

sys.path.insert(0, str(Path(__file__).parent))
import naibbe_harness as H  # noqa: E402
import panel_stats as S  # noqa: E402

OUT = H.ROOT / 'phases/PHASE_757_NAIBBE_RIVAL_PANEL/results'
OUT.mkdir(parents=True, exist_ok=True)
VERSIONS = ['GV1', 'GV2']
PTS = ['P-REC', 'P-PHA', 'P-ITA', 'P-NH']
LAYOUTS = ['STREAM', 'WRAP']
SRS = [0, 3]
NOISES = ['V0', 'V1']
VARIANTS = list(itertools.product(VERSIONS, PTS, LAYOUTS, SRS, NOISES))
N_MEMBERS, N_CTRL, N_REF = 1000, 1000, 50
DS = ['D2', 'D3', 'D4', 'D5', 'D6']
DESC = ['types', 'hapax_type_fraction', 'zipf_slope', 'mean_token_length', 'duplicate_lines', 'max_identical_run',
        'erun_class_same_lag1', 'max_qok_in_10_window']
RERUN_OFFSET = 5_000_000
BUILT_IN = {'M1': {'D5', 'D6'}, 'GEDGE': {'D2', 'D6'}}
CTRL_SEED = {'M1': 757_900_000, 'GEDGE': 757_910_000, 'BNOISE': 757_920_000, 'TIMM': 757_930_000}
WORKERS = 11
_W = {}


def log(*a):
    print(*a, flush=True)


def _init():
    sk = H.load_skeleton()
    _W['sk'] = sk
    _W['lens'] = [sum(w is not None for w in ln) for ln in sk['B']]
    _W['noise'] = H.noise_model()
    _W['pt'] = {}
    for v in VERSIONS:
        m = H.load_version(v)
        for p in PTS:
            _W['pt'][(v, p)] = H.plaintext(p, m)
    _W['m1'] = H.M1(sk['B'])
    _W['ge'] = H.GEdge(sk['B'])
    _W['timm'] = H.Timm(sk['B'], sk['folio'])


def _pack(st):
    return {'D': [st[d] for d in DS], 'desc': [st['desc'][k] for k in DESC], 'aux': st['aux']}


def naibbe_member(args):
    vi, member, offset = args
    v, p, lay, sr, noise = VARIANTS[vi]
    seed = 757_000_000 + 10_000 * vi + member + offset
    m = H.load_version(v)
    sk, pt = _W['sk'], _W['pt'][(v, p)]
    if lay == 'STREAM':
        toks, chunks = H.gen_stream(m, pt, seed, sk['n_certain'], bool(sr))
        corpus, folios = H.pour(toks, sk['B']), sk['folio']
    else:
        lines, chunks = H.gen_wrap(m, pt, seed, _W['lens'], sk['n_certain'], bool(sr))
        corpus = H.place_blockers(lines, sk['B'])
        folios = [sk['folio'][li] if li < len(sk['B']) else 'EXTRA' for li in range(len(corpus))]
    rng = np.random.default_rng(seed)
    if noise == 'V1':
        corpus = H.apply_noise(corpus, _W['noise'], rng)
    out = _pack(S.all_stats(corpus, folios, rng))
    out.update({'vi': vi, 'member': member, 'offset': offset})
    if lay == 'STREAM' and sr == 0 and noise == 'V0' and member < 20 and offset == 0:
        ch = H.pour(chunks[:sk['n_certain']], sk['B'])
        C = S.Corpus(ch, sk['folio'])
        out['D5_chunk_ceiling'] = S.d5(C, np.random.default_rng(seed + 1))[0]
    return out


def control_member(args):
    kind, member = args
    rng = np.random.default_rng(CTRL_SEED[kind] + member)
    sk = _W['sk']
    if kind == 'M1':
        c = _W['m1'].generate(sk['B'], rng)
    elif kind == 'GEDGE':
        c = _W['ge'].generate(sk['B'], rng)
    elif kind == 'BNOISE':
        c = H.apply_noise(sk['B'], _W['noise'], rng)
    else:
        c = _W['timm'].generate(sk['B'], rng)
    out = _pack(S.all_stats(c, sk['folio'], rng))
    out.update({'kind': kind, 'member': member})
    return out


def outside(b, vals, k):
    vals = np.asarray(vals, dtype=float)
    beyond = b < vals.min() or b > vals.max()
    sd = vals.std(ddof=1)
    if sd == 0:
        return bool(beyond)
    return bool(beyond and abs(b - vals.mean()) / sd > norm.ppf(1 - 0.005 / k))


def summ(vals, b=None):
    vals = np.asarray(vals, dtype=float)
    out = {'mean': float(vals.mean()), 'sd': float(vals.std(ddof=1)), 'min': float(vals.min()),
           'max': float(vals.max()), 'skew': float(skew(vals)) if vals.std() > 0 else 0.0}
    if b is not None and out['sd'] > 0:
        out['z_B'] = (b - out['mean']) / out['sd']
    return out


# ================================================================================================ stages
def stage_controls():
    t0 = time.time()
    _init()
    sk = _W['sk']
    Bst = S.all_stats(sk['B'], sk['folio'], np.random.default_rng(757_999_999))
    B = dict(zip(DS, [Bst[d] for d in DS]))
    log(f"B: {B}")
    tasks = [(k, m) for k in ('M1', 'GEDGE') for m in range(N_CTRL)] + \
            [(k, m) for k in ('BNOISE', 'TIMM') for m in range(N_REF)]
    res = {k: [] for k in CTRL_SEED}
    with Pool(WORKERS, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(control_member, tasks, chunksize=10)):
            res[r['kind']].append(r)
            if (i + 1) % 250 == 0:
                log(f"  controls {i + 1}/{len(tasks)} ({time.time() - t0:.0f}s)")
    k0 = len(DS)
    cert = {}
    for d_i, d in enumerate(DS):
        certifiers = [c for c in ('M1', 'GEDGE') if not outside(B[d], [r['D'][d_i] for r in res[c]], k0)]
        cert[d] = {'certifiers': certifiers, 'usable': bool(certifiers),
                   'certified_by_non_builtin': any(d not in BUILT_IN[c] for c in certifiers),
                   'M1': summ([r['D'][d_i] for r in res['M1']], B[d]),
                   'GEDGE': summ([r['D'][d_i] for r in res['GEDGE']], B[d])}
    usable = [d for d in DS if cert[d]['usable']]
    ref = {c: {d: summ([r['D'][i] for r in res[c]], B[d]) for i, d in enumerate(DS)} for c in ('BNOISE', 'TIMM')}
    out = {'B': B, 'B_aux': Bst['aux'], 'B_desc': Bst['desc'], 'k0': k0, 'certification': cert, 'usable': usable,
           'k': len(usable), 'references': ref,
           'control_desc_means': {c: dict(zip(DESC, np.mean([r['desc'] for r in res[c]], axis=0).tolist()))
                                  for c in res},
           'D1': 'dropped (PHASE_756 verdict not RESIDUAL)', 'runtime_s': round(time.time() - t0, 1)}
    json.dump(out, open(OUT / 'controls_certification.json', 'w', encoding='utf-8'), indent=1)
    np.savez_compressed(OUT / 'controls_raw.npz', **{c: np.array([r['D'] for r in res[c]]) for c in res})
    log(f"certification: usable={usable} k={len(usable)}")
    for d in DS:
        log(f"  {d}: certifiers={cert[d]['certifiers']} non_builtin={cert[d]['certified_by_non_builtin']}")


def run_naibbe(offset, vis):
    t0 = time.time()
    tasks = [(vi, m, offset) for vi in vis for m in range(N_MEMBERS)]
    D = np.full((len(VARIANTS), N_MEMBERS, len(DS)), np.nan)
    DE = np.full((len(VARIANTS), N_MEMBERS, len(DESC)), np.nan)
    ceil = {}
    with Pool(WORKERS, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(naibbe_member, tasks, chunksize=20)):
            D[r['vi'], r['member']] = r['D']
            DE[r['vi'], r['member']] = r['desc']
            if 'D5_chunk_ceiling' in r:
                ceil.setdefault(r['vi'], []).append(r['D5_chunk_ceiling'])
            if (i + 1) % 2000 == 0:
                log(f"  naibbe offset={offset}: {i + 1}/{len(tasks)} ({time.time() - t0:.0f}s)")
                np.savez_compressed(OUT / f'naibbe_raw_offset{offset}_interim.npz', D=D, DE=DE)
    np.savez_compressed(OUT / f'naibbe_raw_offset{offset}.npz', D=D, DE=DE)
    json.dump({str(k): v for k, v in ceil.items()}, open(OUT / f'd5_chunk_ceiling_offset{offset}.json', 'w'))
    log(f"naibbe offset={offset} done ({time.time() - t0:.0f}s)")


def stage_naibbe():
    run_naibbe(0, range(len(VARIANTS)))


def variant_name(vi):
    v, p, lay, sr, noise = VARIANTS[vi]
    return f"{v}/{p}/{lay}/SR{sr}/{noise}"


def evaluate(D, B, usable, nonbuiltin, k):
    rows = []
    for vi in range(len(VARIANTS)):
        outs = [d for d in usable if outside(B[d], D[vi, :, DS.index(d)], k)]
        excl = len(outs) >= 2 and any(nonbuiltin[d] for d in outs)
        rows.append({'variant': variant_name(vi), 'outside': outs, 'n_out': len(outs), 'excludes': bool(excl),
                     'z': {d: summ(D[vi, :, DS.index(d)], B[d]).get('z_B') for d in usable}})
    return rows


def stage_verdict():
    cc = json.load(open(OUT / 'controls_certification.json', encoding='utf-8'))
    B, usable, k = cc['B'], cc['usable'], cc['k']
    nonbuiltin = {d: cc['certification'][d]['certified_by_non_builtin'] for d in DS}
    D0 = np.load(OUT / 'naibbe_raw_offset0.npz')['D']
    rows = evaluate(D0, B, usable, nonbuiltin, k)
    failing = [vi for vi, r in enumerate(rows) if not r['excludes']]
    log(f"first pass: {len(VARIANTS) - len(failing)}/{len(VARIANTS)} variants exclude; rerunning {len(failing)}")
    rerun_rows = {}
    if failing:
        f = OUT / f'naibbe_raw_offset{RERUN_OFFSET}.npz'
        if not f.exists():
            _init()
            run_naibbe(RERUN_OFFSET, failing)
        D1 = np.load(f)['D']
        rr = evaluate(D1, B, usable, nonbuiltin, k)
        rerun_rows = {vi: rr[vi] for vi in failing}
    final_fail = [vi for vi in failing if not rerun_rows[vi]['excludes']]
    if k < 2:
        verdict = 'NOT EXCLUDED'
    else:
        verdict = 'EXCLUDED' if not final_fail else 'NOT EXCLUDED'
    # secondary: D2 removed
    us2 = [d for d in usable if d != 'D2']
    rows2 = evaluate(D0, B, us2, nonbuiltin, max(len(us2), 1)) if us2 else []
    fail2 = [vi for vi, r in enumerate(rows2) if not r['excludes']]
    partial = {}
    for dim, vals in (('version', VERSIONS), ('plaintext', PTS), ('layout', LAYOUTS), ('spacing', SRS),
                      ('noise', NOISES)):
        j = ['version', 'plaintext', 'layout', 'spacing', 'noise'].index(dim)
        partial[dim] = {str(v): sum(1 for vi in range(len(VARIANTS)) if VARIANTS[vi][j] == v and vi not in final_fail)
                        for v in vals}
    DE = np.load(OUT / 'naibbe_raw_offset0.npz')['DE']
    desc = {variant_name(vi): dict(zip(DESC, np.nanmean(DE[vi], axis=0).tolist())) for vi in range(len(VARIANTS))}
    out = {'phase': 'PHASE_757', 'pre_registration_commit': 'a5506cb', 'B': B, 'usable': usable, 'k': k,
           'z_star': float(norm.ppf(1 - 0.005 / k)) if k else None, 'variants': rows,
           'reruns': {variant_name(vi): r for vi, r in rerun_rows.items()},
           'non_excluding_after_rerun': [variant_name(vi) for vi in final_fail], 'verdict': verdict,
           'secondary_D2_removed': {'usable': us2, 'non_excluding_first_pass': [variant_name(vi) for vi in fail2]},
           'partial_excluding_variant_counts': partial, 'naibbe_desc_means': desc,
           'naibbe_D_summary': {variant_name(vi): {d: summ(D0[vi, :, i], B[d]) for i, d in enumerate(DS)}
                                for vi in range(len(VARIANTS))}}
    json.dump(out, open(OUT / 'panel_verdict.json', 'w', encoding='utf-8'), indent=1)
    log(f"VERDICT (locked rules): {verdict}; non-excluding after rerun: {out['non_excluding_after_rerun']}")


if __name__ == '__main__':
    {'controls': stage_controls, 'naibbe': stage_naibbe, 'verdict': stage_verdict}[sys.argv[1]]()
