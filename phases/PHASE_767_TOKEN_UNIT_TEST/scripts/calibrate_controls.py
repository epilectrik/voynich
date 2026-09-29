#!/usr/bin/env python3
"""PHASE_767 pre-lock calibration on CONTROL corpora only (Currier B features are not computed here).

B is read only for its line-length distribution (used to re-wrap every corpus). Output: control feature values,
so the feature-validation rule can be fixed before the pre-registration is locked.
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
OUT.mkdir(parents=True, exist_ok=True)
T0 = time.time()
N = 20_000


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def main():
    rng = np.random.default_rng(767)
    lengths = T.b_line_lengths()
    log(f'B line lengths: {len(lengths)} lines, mean {np.mean(lengths):.2f}')
    res = {}
    todo = [(f'WORD_{l}', lambda l=l: T.eu_word(l)) for l in T.EU] + \
           [(f'SYL_{l}', lambda l=l: T.eu_syl(l)) for l in T.EU] + \
           [('NAT_pinyin_tones', lambda: T.pinyin(True)), ('NAT_pinyin_notones', lambda: T.pinyin(False)),
            ('NAT_vietnamese', T.vietnamese)] + \
           [(f'HOW_{n.split(" - ")[1]}', lambda n=n: T.held_out_word(n)) for n in T.HELD_OUT_WORD]
    for name, fn in todo:
        segs = fn()
        ntok = sum(len(s) for s in segs)
        feats, nw, per = T.corpus_features_full(segs, N, lengths, rng)
        res[name] = {'tokens': ntok, 'windows': nw, 'features': feats, 'per_window': per}
        log(name, ntok, nw, {k: round(v, 3) for k, v in (feats or {}).items()})
        json.dump(res, open(OUT / 'calibration_controls.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
