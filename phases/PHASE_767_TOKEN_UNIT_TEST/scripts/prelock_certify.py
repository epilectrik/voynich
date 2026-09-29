#!/usr/bin/env python3
"""PHASE_767 pre-lock certification (lean audit E5, E7, E9, E10, E14). CONTROLS ONLY.

Inputs: results/prelock_controls.json. Output: results/prelock_certification.json and a printed summary.
- Feature validation (rule (a)-(c)) with the expanded native set (G&B Pinyin, CUV Pinyin, Vietnamese, Lahu).
- VOCAB = mean(s_F1, s_F2), clipped; margin m_V = median over the 10 training corpora of the window SD of VOCAB.
- E6 rule: PLAIN-SYLLABLE EXCLUDED if VOCAB < 0.5 - 2 m_V; SYLLABLE-SIZED INVENTORY if > 0.5 + 2 m_V; else INDETERMINATE.
- E7 certification on single windows at N = 20,000 and N = 10,000, primary natives, V3 (toneless) and V4 axes.
- E9 screen for V>=2 and T80; LOPO on VOCAB alone; E10 table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tu767 as T  # noqa: E402

OUT = T.ROOT / 'phases/PHASE_767_TOKEN_UNIT_TEST/results'
LANGS = list(T.EU)
NATIVES = ['NAT_pinyin_tones', 'NAT_cuv_tones', 'NAT_vietnamese', 'NAT_lahu']
NATIVES_V3 = ['NAT_pinyin_notones', 'NAT_cuv_notones']
EXCL, SYLS, IND = 'PLAIN-SYLLABLE EXCLUDED', 'SYLLABLE-SIZED INVENTORY', 'INDETERMINATE'


def table(res, n='20k', syl_key='SYL_', v4=False):
    """Uniform view: name -> {'features': medians, 'per_window': [dicts]} merging features and extras."""
    out = {}
    if n == '20k':
        src = dict(res['A_N20000'])
        src.update(res['B_new_natives_N20000'])
        if v4:
            for l in LANGS:
                src[f'SYL_{l}'] = res['C_V4_syl_N20000'][f'SYL_{l}']
    else:
        src = dict(res['D_N10000'])
        if v4:
            for l in LANGS:
                src[f'SYL_{l}'] = res['D_N10000'][f'SYLV4_{l}']
    for k, v in src.items():
        if k.startswith('SYLV4_'):
            continue
        per = [dict(p, **e) for p, e in zip(v['per_window'], v['extras_per_window'])]
        med = {f: float(np.median([p[f] for p in per])) for f in per[0]}
        out[k] = {'features': med, 'per_window': per}
    return out


def axes(tab, feats, langs=LANGS):
    return {f: (float(np.median([tab[f'WORD_{l}']['features'][f] for l in langs])),
                float(np.median([tab[f'SYL_{l}']['features'][f] for l in langs]))) for f in feats}


def s_idx(x, a):
    return (x - a[0]) / (a[1] - a[0])


def validate(tab, feats, natives):
    ax = axes(tab, feats)
    how = [k for k in tab if k.startswith('HOW_')]
    out = {}
    for f in feats:
        sgn = np.sign(ax[f][1] - ax[f][0])
        pairs_ok = all(np.sign(tab[f'SYL_{l}']['features'][f] - tab[f'WORD_{l}']['features'][f]) == sgn
                       for l in LANGS)
        nat = {k: round(s_idx(tab[k]['features'][f], ax[f]), 3) for k in natives}
        ho = {k: s_idx(tab[k]['features'][f], ax[f]) for k in how}
        n_ok = sum(v < 0.5 for v in ho.values())
        out[f] = {'pairs_same_sign': bool(pairs_ok), 'natives': nat, 'heldout_word_side': f'{n_ok}/{len(ho)}',
                  'heldout_fail': {k: round(v, 3) for k, v in ho.items() if v >= 0.5},
                  'valid': bool(pairs_ok and all(v > 0.5 for v in nat.values()) and n_ok >= 12)}
    return out


def vocab(fd, ax):
    return float(np.mean([np.clip(s_idx(fd[f], ax[f]), -1, 2) for f in ('F1_vocab', 'F2_heaps')]))


def margin(tab, ax):
    sds = []
    for k in [f'WORD_{l}' for l in LANGS] + [f'SYL_{l}' for l in LANGS]:
        vals = [vocab(p, ax) for p in tab[k]['per_window']]
        if len(vals) >= 2:
            sds.append(float(np.std(vals, ddof=1)))
    return float(np.median(sds))


def call(x, m):
    return EXCL if x < 0.5 - 2 * m else (SYLS if x > 0.5 + 2 * m else IND)


def certify(tab, natives):
    ax = axes(tab, ['F1_vocab', 'F2_heaps'])
    m = margin(tab, ax)
    nat_windows = {k: [round(vocab(p, ax), 3) for p in tab[k]['per_window']] for k in natives}
    nat_calls = {k: [call(v, m) for v in vs] for k, vs in nat_windows.items()}
    how = sorted(k for k in tab if k.startswith('HOW_'))
    how_vals = {k: round(vocab(tab[k]['features'], ax), 3) for k in how}
    how_calls = {k: call(v, m) for k, v in how_vals.items()}
    n_excl = sum(c == EXCL for c in how_calls.values())
    excl_cert = all(c != EXCL for cs in nat_calls.values() for c in cs) and n_excl >= 12
    syl_cert = all(c == SYLS for cs in nat_calls.values() for c in cs)
    return {'axes': ax, 'margin_mV': m, 'thresholds': [0.5 - 2 * m, 0.5 + 2 * m],
            'native_window_vocab': nat_windows, 'native_window_calls': nat_calls,
            'heldout_vocab': how_vals, 'heldout_calls': how_calls, 'heldout_excluded': f'{n_excl}/{len(how)}',
            'EXCLUDED_certified': bool(excl_cert), 'SYLLABLE_SIZED_certified': bool(syl_cert)}


def lopo(tab):
    out = {}
    for l in LANGS:
        rest = [x for x in LANGS if x != l]
        ax = axes(tab, ['F1_vocab', 'F2_heaps'], rest)
        m = margin(tab, ax)
        for kind in ('WORD', 'SYL'):
            v = vocab(tab[f'{kind}_{l}']['features'], ax)
            want = EXCL if kind == 'WORD' else SYLS
            out[f'{kind}_{l}'] = {'VOCAB': round(v, 3), 'call': call(v, m), 'correct_rule': call(v, m) == want,
                                  'correct_half': (v > 0.5) == (kind == 'SYL')}
    return out


def main():
    res = json.load(open(OUT / 'prelock_controls.json'))
    t20 = table(res, '20k')
    out = {}
    feats = T.FEATURES + ['X_vge2', 'X_t80']
    out['validation_N20000'] = validate(t20, feats, NATIVES)
    out['validation_N20000_V3'] = validate(t20, ['F1_vocab', 'F2_heaps', 'F3_bigram_gain'], NATIVES_V3 +
                                           ['NAT_vietnamese', 'NAT_lahu'])
    out['cert_N20000'] = certify(t20, NATIVES)
    out['cert_N20000_V3'] = certify(t20, NATIVES_V3)
    t20v4 = table(res, '20k', v4=True)
    out['cert_N20000_V4'] = certify(t20v4, NATIVES + NATIVES_V3)
    t10 = table(res, '10k')
    out['validation_N10000'] = validate(t10, ['F1_vocab', 'F2_heaps', 'F3_bigram_gain', 'X_vge2', 'X_t80'], NATIVES)
    out['cert_N10000'] = certify(t10, NATIVES + NATIVES_V3)
    t10v4 = table(res, '10k', v4=True)
    out['cert_N10000_V4'] = certify(t10v4, NATIVES + NATIVES_V3)
    out['lopo_VOCAB_N20000'] = lopo(t20)
    # E10: variant spelling, on the primary N=20k axes
    ax = out['cert_N20000']['axes']
    ax3 = axes(t20, ['F3_bigram_gain'])
    e10 = {}
    for k, v in res['E_variant_spelling'].items():
        e10[k] = {'types': round(10 ** v['features']['F1_vocab']), 'VOCAB': round(vocab(v['features'], ax), 3),
                  'SEQ': round(s_idx(v['features']['F3_bigram_gain'], ax3['F3_bigram_gain']), 3),
                  'vge2': round(10 ** v['extras']['X_vge2']), 'pair_coverage': round(v['extras']['X_pair_coverage'], 3)}
    out['E10_variant_spelling'] = e10
    # descriptive SEQ / F3 baseline / coverage per corpus
    desc = {}
    for k, v in t20.items():
        src = res['A_N20000'].get(k) or res['B_new_natives_N20000'].get(k)
        desc[k] = {'types_20k': round(10 ** v['features']['F1_vocab']), 'VOCAB': round(vocab(v['features'], ax), 3),
                   'SEQ': round(s_idx(v['features']['F3_bigram_gain'], ax3['F3_bigram_gain']), 3),
                   'F3_minus_shuffle': round(src['F3_minus_shuffle_first_window'], 4),
                   'pair_coverage': round(v['features']['X_pair_coverage'], 3)}
    out['descriptive_controls_N20000'] = desc
    json.dump(out, open(OUT / 'prelock_certification.json', 'w'), indent=1)

    for key in ('validation_N20000', 'validation_N20000_V3', 'validation_N10000'):
        print(f'== {key}')
        for f, v in out[key].items():
            print(f'  {f:16s} {"VALID" if v["valid"] else "invalid"} natives {v["natives"]} held-out '
                  f'{v["heldout_word_side"]} {v["heldout_fail"]}')
    for key in ('cert_N20000', 'cert_N20000_V3', 'cert_N20000_V4', 'cert_N10000', 'cert_N10000_V4'):
        c = out[key]
        print(f'== {key}: m_V {c["margin_mV"]:.4f} thresholds {c["thresholds"][0]:.3f}/{c["thresholds"][1]:.3f} | '
              f'EXCLUDED certified {c["EXCLUDED_certified"]} | SYLLABLE-SIZED certified {c["SYLLABLE_SIZED_certified"]}'
              f' | held-out excluded {c["heldout_excluded"]}')
        for k, vs in c['native_window_vocab'].items():
            print(f'    {k:20s} {vs} {sorted(set(c["native_window_calls"][k]))}')
        print('    held-out not excluded:', {k: v for k, v in c['heldout_vocab'].items()
                                             if c['heldout_calls'][k] != EXCL})
    print('== LOPO VOCAB:', {k: (v['VOCAB'], v['call'][:5]) for k, v in out['lopo_VOCAB_N20000'].items()})
    print('== E10:')
    for k, v in e10.items():
        print(f'    {k:24s} {v}')
    print('== descriptive:')
    for k, v in sorted(desc.items(), key=lambda kv: kv[1]['VOCAB']):
        print(f'    {k:22s} {v}')


if __name__ == '__main__':
    main()
