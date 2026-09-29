#!/usr/bin/env python3
"""PHASE_767: is Currier B's unit inventory as small as syllable-written text? (pre-registration locked at caf7127)

Controls come from the frozen pre-lock outputs (results/prelock_controls.json); B and the reference generators are
computed here for the first time.
"""
from __future__ import annotations

import json
import math
import sys
import time
from collections import OrderedDict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prelock_certify as PC  # noqa: E402
import tu767 as T  # noqa: E402

OUT = T.ROOT / 'phases/PHASE_767_TOKEN_UNIT_TEST/results'
T0 = time.time()
EXCL, SYLS, IND = PC.EXCL, PC.SYLS, PC.IND


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def full_features(win, rng, rng_x):
    fd = T.features(win, rng)
    fd.update(T.extras(win))
    fd['F3_minus_shuffle'] = T.f_bigram_shuffle_delta(win, rng_x)
    return fd


def last_window(segs, n, lengths, rng):
    """B's last n tokens after re-wrapping (the first, partial line truncated)."""
    lines = T.G.rewrap(segs, lengths, rng)
    out, got = [], 0
    for ln in reversed(lines):
        need = n - got
        if len(ln) >= need:
            out.append(ln[len(ln) - need:])
            got = n
            break
        out.append(ln)
        got += len(ln)
    return list(reversed(out)) if got == n else None


def b_by_folio(variant='ZL'):
    _, per_line = T.b_segments(variant)
    folios = OrderedDict()
    for f, segs in per_line:
        folios.setdefault(f, []).extend(segs)
    return folios


def vocab_call(fd, ax, m):
    v = PC.vocab(fd, ax)
    return v, PC.call(v, m)


def seq_index(fd, ax3):
    return PC.s_idx(fd['F3_bigram_gain'], ax3)


def main():
    res_pre = json.load(open(OUT / 'prelock_controls.json'))
    t20 = PC.table(res_pre, '20k')
    t10 = PC.table(res_pre, '10k')
    c20 = PC.certify(t20, PC.NATIVES)
    c20v3 = PC.certify(t20, PC.NATIVES_V3)
    c20v4 = PC.certify(PC.table(res_pre, '20k', v4=True), PC.NATIVES + PC.NATIVES_V3)
    c10 = PC.certify(t10, PC.NATIVES + PC.NATIVES_V3)
    ax20, m20 = c20['axes'], c20['margin_mV']
    ax10, m10 = c10['axes'], c10['margin_mV']
    ax3 = PC.axes(t20, ['F3_bigram_gain'])['F3_bigram_gain']
    log(f'axes N20k {ax20} m_V {m20:.4f} | N10k m_V {m10:.4f} | certified EXCLUDED N20k {c20["EXCLUDED_certified"]}, '
        f'N10k {c10["EXCLUDED_certified"]}')

    lengths = T.b_line_lengths()
    rng = np.random.default_rng(767767)
    rng_x = np.random.default_rng(767768)
    out = {'pre_registration': 'caf7127', 'axes_N20000': ax20, 'mV_N20000': m20, 'axes_N10000': ax10, 'mV_N10000': m10}

    # ------------------------------------------------------------------ primary
    segs, _ = T.b_segments('ZL')
    win = T.windows(segs, 20_000, lengths, rng, 1)[0]
    fd = full_features(win, rng, rng_x)
    v, c = vocab_call(fd, ax20, m20)
    out['B_primary'] = {'features': fd, 'types_20k': round(10 ** fd['F1_vocab']), 'vge2': round(10 ** fd['X_vge2']),
                        't80': round(10 ** fd['X_t80']), 'VOCAB': v, 'call': c, 'SEQ': seq_index(fd, ax3),
                        's_F1': PC.s_idx(fd['F1_vocab'], ax20['F1_vocab']),
                        's_F2': PC.s_idx(fd['F2_heaps'], ax20['F2_heaps'])}
    log(f'PRIMARY: types {out["B_primary"]["types_20k"]} VOCAB {v:.3f} -> {c} | SEQ {out["B_primary"]["SEQ"]:.3f}')

    # ------------------------------------------------------------------ E8 (i) folio bipartitions at N = 10,000
    folios = b_by_folio('ZL')
    names = list(folios)
    ntok = {f: sum(len(s) for s in folios[f]) for f in names}
    total = sum(ntok.values())
    bip = []
    for i in range(20):
        order = list(np.random.default_rng(767800 + i).permutation(len(names)))
        first, got = set(), 0
        for j in order:
            if got >= total / 2:
                break
            first.add(names[j])
            got += ntok[names[j]]
        halves = [[f for f in names if f in first], [f for f in names if f not in first]]
        r = np.random.default_rng(767900 + i)
        row = []
        for h in halves:
            hs = [s for f in h for s in folios[f]]
            w = T.windows(hs, 10_000, lengths, r, 1)[0]
            f123 = {'F1_vocab': T.f_vocab(w), 'F2_heaps': T.f_heaps(w)}
            vv, cc = vocab_call(f123, ax10, m10)
            row.append({'folios': len(h), 'tokens': sum(ntok[f] for f in h), 'VOCAB': round(vv, 3), 'call': cc})
        bip.append(row)
    calls_bip = [h['call'] for row in bip for h in row]
    out['E8_bipartitions'] = bip
    out['E8_bipartition_calls'] = {k: calls_bip.count(k) for k in set(calls_bip)}
    log('E8 (i) bipartition calls:', out['E8_bipartition_calls'],
        'VOCAB range', min(h['VOCAB'] for row in bip for h in row), max(h['VOCAB'] for row in bip for h in row))

    # ------------------------------------------------------------------ E8 (ii) last 20,000 tokens
    lw = last_window(segs, 20_000, lengths, np.random.default_rng(767769))
    f_last = {'F1_vocab': T.f_vocab(lw), 'F2_heaps': T.f_heaps(lw)}
    vl, cl = vocab_call(f_last, ax20, m20)
    out['E8_last_window'] = {'types_20k': round(10 ** f_last['F1_vocab']), 'VOCAB': vl, 'call': cl}
    log(f'E8 (ii) last window: VOCAB {vl:.3f} -> {cl}')

    # ------------------------------------------------------------------ verdict
    certified = {EXCL: c20['EXCLUDED_certified'], SYLS: c20['SYLLABLE_SIZED_certified'], IND: True}[c]
    e8_holds = (all(x == c for x in calls_bip) and cl == c) if c != IND else True
    verdict = c if (c != IND and certified and e8_holds) else IND
    out['verdict'] = verdict
    out['verdict_detail'] = {'primary_call': c, 'certified': certified, 'E8_holds': e8_holds}
    log('VERDICT:', verdict, out['verdict_detail'])

    # ------------------------------------------------------------------ variants
    var = {}
    for name, vname in (('V1_H_track', 'H'), ('V2_uncertain_split', 'ZL_SPLIT')):
        s_v, _ = T.b_segments(vname)
        w_v = T.windows(s_v, 20_000, lengths, np.random.default_rng(767770), 1)[0]
        f_v = {'F1_vocab': T.f_vocab(w_v), 'F2_heaps': T.f_heaps(w_v), 'F3_bigram_gain': T.f_bigram_gain(w_v)}
        vv, cc = vocab_call(f_v, ax20, m20)
        var[name] = {'tokens': sum(len(x) for x in s_v), 'types_20k': round(10 ** f_v['F1_vocab']), 'VOCAB': vv,
                     'call': cc, 'SEQ': seq_index(f_v, ax3)}
    var['V3_toneless_natives'] = {'VOCAB': v, 'call': c, 'certified_EXCLUDED': c20v3['EXCLUDED_certified'],
                                  'note': 'axes unchanged; only the certification set changes'}
    vv, cc = vocab_call(fd, c20v4['axes'], c20v4['margin_mV'])
    var['V4_syllabifier'] = {'VOCAB': vv, 'call': cc, 'mV': c20v4['margin_mV'],
                             'certified_EXCLUDED': c20v4['EXCLUDED_certified']}
    w5 = T.windows(segs, 10_000, lengths, np.random.default_rng(767771), 5)
    v5 = []
    for w in w5:
        vv, cc = vocab_call({'F1_vocab': T.f_vocab(w), 'F2_heaps': T.f_heaps(w)}, ax10, m10)
        v5.append({'VOCAB': vv, 'call': cc})
    var['V5_N10000'] = {'windows': v5, 'certified_EXCLUDED': c10['EXCLUDED_certified']}
    w6 = T.windows(segs, 20_000, None, np.random.default_rng(767772), 1)[0]
    f6 = {'F1_vocab': T.f_vocab(w6), 'F2_heaps': T.f_heaps(w6), 'F3_bigram_gain': T.f_bigram_gain(w6)}
    vv, cc = vocab_call(f6, ax20, m20)
    var['V6_no_rewrap'] = {'VOCAB': vv, 'call': cc, 'SEQ': seq_index(f6, ax3)}
    out['variants'] = var
    for k, x in var.items():
        log('variant', k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in x.items()
                           if kk != 'windows'}, x.get('windows', ''))

    # ------------------------------------------------------------------ k* (E10)
    e10 = res_pre['E_variant_spelling']
    syl_texts = [f'SYL_{l}' for l in T.EU] + ['NAT_pinyin_tones', 'NAT_vietnamese', 'NAT_cuv_tones', 'NAT_lahu']
    med_by_k = {1: float(np.median([PC.vocab(t20[t]['features'], ax20) for t in syl_texts]))}
    for k in (2, 4, 8, 16):
        med_by_k[k] = float(np.median([PC.vocab(e10[f'{t}_k{k}']['features'], ax20) for t in syl_texts]))
    ks = [1, 2, 4, 8, 16]
    kstar = None
    for a, b in zip(ks, ks[1:]):
        va, vb = med_by_k[a], med_by_k[b]
        if (va - v) * (vb - v) <= 0 and va != vb:
            la, lb = math.log2(a), math.log2(b)
            kstar = 2 ** (la + (v - va) / (vb - va) * (lb - la))
            break
    out['E10_kstar'] = {'median_VOCAB_by_k': med_by_k, 'VOCAB_B': v,
                        'k_star': round(kstar, 2) if kstar else ('> 16' if v < med_by_k[16] else '< 1')}
    log('k*:', out['E10_kstar'])

    # ------------------------------------------------------------------ E11 reference generators, Currier A
    refs = {}
    for name, kind, seed in (('Naibbe_GV1', 'NAIBBE', 767001), ('Timm', 'TIMM', 767101)):
        gs = T.reference_generator(kind, seed)
        w = T.windows(gs, 20_000, lengths, np.random.default_rng(seed), 1)[0]
        f = full_features(w, np.random.default_rng(seed + 1), np.random.default_rng(seed + 2))
        vv, cc = vocab_call(f, ax20, m20)
        refs[name] = {'tokens': sum(len(x) for x in gs), 'types_20k': round(10 ** f['F1_vocab']),
                      'vge2': round(10 ** f['X_vge2']), 'VOCAB': vv, 'call': cc, 'SEQ': seq_index(f, ax3),
                      'F3_minus_shuffle': f['F3_minus_shuffle'], 'features': f}
        log('ref', name, refs[name]['types_20k'], round(vv, 3), cc, 'SEQ', round(refs[name]['SEQ'], 3))
    a_segs = T.zl_segments('A')
    wa = T.windows(a_segs, 10_000, lengths, np.random.default_rng(767773), 1)[0]
    fa = {'F1_vocab': T.f_vocab(wa), 'F2_heaps': T.f_heaps(wa)}
    vv, cc = vocab_call(fa, ax10, m10)
    refs['Currier_A_N10000'] = {'types_10k': round(10 ** fa['F1_vocab']), 'VOCAB': vv, 'call': cc}
    log('ref Currier A (N=10k)', refs['Currier_A_N10000'])
    out['references'] = refs

    # ------------------------------------------------------------------ descriptive comparison table
    desc = {}
    for k, v_ in t20.items():
        desc[k] = {'types_20k': round(10 ** v_['features']['F1_vocab']), 'vge2': round(10 ** v_['features']['X_vge2']),
                   't80': round(10 ** v_['features']['X_t80']), 'VOCAB': round(PC.vocab(v_['features'], ax20), 3),
                   'SEQ': round(PC.s_idx(v_['features']['F3_bigram_gain'], ax3), 3),
                   'F4': round(v_['features']['F4_repeat'], 3), 'F5': round(v_['features']['F5_coupling'], 4),
                   'F6': round(v_['features']['F6_near_repeat'], 3)}
    out['controls_table'] = desc
    out['runtime_s'] = round(time.time() - T0, 1)
    json.dump(out, open(OUT / 'token_unit_test.json', 'w'), indent=1, default=float)
    log('done')


if __name__ == '__main__':
    main()
