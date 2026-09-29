#!/usr/bin/env python3
"""PHASE_767 pre-lock control computations required by the lean audit (E5, E7, E9, E10, E14). CONTROLS ONLY:
Currier B is read only for its line-length distribution.

A. N = 20,000: the frozen calibration sequence is replayed exactly (seed 767, same corpus order) to attach per-window
   extras (V>=2, T80, pair coverage) and, on each corpus's first window, F3 minus its within-line-shuffle mean; the
   replayed medians must equal results/calibration_controls.json.
B. New native syllable-written texts (E14): Chinese Union Version NT in character-by-character Pinyin (toned and
   toneless) and Lahu Si NT.
C. V4 alternative syllabifier (no onset clusters) for the five SYL training texts.
D. N = 10,000 controls (V5 / E8): F1-F3 and extras for every control corpus.
E. E10 spelling-variation control: k = 2, 4, 8, 16 spellings per syllable type for the syllabified training texts and
   the native texts; F1-F3, extras.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tu767 as T  # noqa: E402

OUT = T.ROOT / 'phases/PHASE_767_TOKEN_UNIT_TEST/results'
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def base_todo():
    return [(f'WORD_{l}', lambda l=l: T.eu_word(l)) for l in T.EU] + \
           [(f'SYL_{l}', lambda l=l: T.eu_syl(l)) for l in T.EU] + \
           [('NAT_pinyin_tones', lambda: T.pinyin(True)), ('NAT_pinyin_notones', lambda: T.pinyin(False)),
            ('NAT_vietnamese', T.vietnamese)] + \
           [(f'HOW_{n.split(" - ")[1]}', lambda n=n: T.held_out_word(n)) for n in T.HELD_OUT_WORD]


NEW_NATIVES = [('NAT_cuv_tones', lambda: T.cuv_pinyin(True)), ('NAT_cuv_notones', lambda: T.cuv_pinyin(False)),
               ('NAT_lahu', T.lahu)]


def f123(win):
    return {'F1_vocab': T.f_vocab(win), 'F2_heaps': T.f_heaps(win), 'F3_bigram_gain': T.f_bigram_gain(win)}


def main():
    lengths = T.b_line_lengths()
    frozen = json.load(open(OUT / 'calibration_controls.json'))
    res = {'A_N20000': {}, 'B_new_natives_N20000': {}, 'C_V4_syl_N20000': {}, 'D_N10000': {}, 'E_variant_spelling': {}}

    # ---------------------------------------------------------------- A: replay the frozen sequence
    rng = np.random.default_rng(767)
    rng_x = np.random.default_rng(7670)
    for name, fn in base_todo():
        segs = fn()
        wins = T.windows(segs, 20_000, lengths, rng, 5)
        per = [T.features(w, rng) for w in wins]
        med = {f: float(np.median([p[f] for p in per])) for f in T.FEATURES}
        assert med == frozen[name]['features'], (name, med, frozen[name]['features'])
        ex = [T.extras(w) for w in wins]
        res['A_N20000'][name] = {'windows': len(wins), 'features': med, 'per_window': per, 'extras_per_window': ex,
                                 'F3_minus_shuffle_first_window': T.f_bigram_shuffle_delta(wins[0], rng_x)}
        log('A', name, 'replayed OK', len(wins), 'windows')
    json.dump(res, open(OUT / 'prelock_controls.json', 'w'), indent=1)

    # ---------------------------------------------------------------- B: new natives
    rng = np.random.default_rng(7671)
    for name, fn in NEW_NATIVES:
        wins = T.windows(fn(), 20_000, lengths, rng, 5)
        per = [T.features(w, rng) for w in wins]
        res['B_new_natives_N20000'][name] = {
            'windows': len(wins), 'features': {f: float(np.median([p[f] for p in per])) for f in T.FEATURES},
            'per_window': per, 'extras_per_window': [T.extras(w) for w in wins],
            'F3_minus_shuffle_first_window': T.f_bigram_shuffle_delta(wins[0], rng_x)}
        log('B', name, len(wins), {k: round(v, 3) for k, v in res['B_new_natives_N20000'][name]['features'].items()})
    json.dump(res, open(OUT / 'prelock_controls.json', 'w'), indent=1)

    # ---------------------------------------------------------------- C: V4 syllabifier
    rng = np.random.default_rng(7672)
    for l in T.EU:
        wins = T.windows(T.eu_syl(l, maximal_onset=False), 20_000, lengths, rng, 5)
        per = [T.features(w, rng) for w in wins]
        res['C_V4_syl_N20000'][f'SYL_{l}'] = {
            'windows': len(wins), 'features': {f: float(np.median([p[f] for p in per])) for f in T.FEATURES},
            'per_window': per, 'extras_per_window': [T.extras(w) for w in wins]}
        log('C', l, {k: round(v, 3) for k, v in res['C_V4_syl_N20000'][f'SYL_{l}']['features'].items()})
    json.dump(res, open(OUT / 'prelock_controls.json', 'w'), indent=1)

    # ---------------------------------------------------------------- D: N = 10,000 controls
    rng = np.random.default_rng(7673)
    for name, fn in base_todo() + NEW_NATIVES + [(f'SYLV4_{l}', lambda l=l: T.eu_syl(l, maximal_onset=False))
                                                 for l in T.EU]:
        wins = T.windows(fn(), 10_000, lengths, rng, 5)
        per = [f123(w) for w in wins]
        res['D_N10000'][name] = {'windows': len(wins),
                                 'features': {f: float(np.median([p[f] for p in per])) for f in per[0]},
                                 'per_window': per, 'extras_per_window': [T.extras(w) for w in wins]}
        log('D', name, len(wins))
    json.dump(res, open(OUT / 'prelock_controls.json', 'w'), indent=1)

    # ---------------------------------------------------------------- E: spelling variation
    rng = np.random.default_rng(7674)
    texts = [(f'SYL_{l}', lambda l=l: T.eu_syl(l)) for l in T.EU] + \
            [('NAT_pinyin_tones', lambda: T.pinyin(True)), ('NAT_vietnamese', T.vietnamese)] + \
            [x for x in NEW_NATIVES if x[0] != 'NAT_cuv_notones']
    for name, fn in texts:
        base = fn()
        for k in (2, 4, 8, 16):
            wins = T.windows(T.syl_variant_spelling(base, k, 767000 + k), 20_000, lengths, rng, 2)
            per = [f123(w) for w in wins]
            ex = [T.extras(w) for w in wins]
            res['E_variant_spelling'][f'{name}_k{k}'] = {
                'windows': len(wins), 'features': {f: float(np.median([p[f] for p in per])) for f in per[0]},
                'extras': {f: float(np.median([e[f] for e in ex])) for f in ex[0]}}
        log('E', name, 'done')
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'prelock_controls.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
