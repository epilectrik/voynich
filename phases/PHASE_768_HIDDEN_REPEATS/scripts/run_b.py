#!/usr/bin/env python3
"""PHASE_768: hidden repeats in Currier B (run only after the pre-registration lock).

Primary: TOK, n = 4, joint null N5j; thresholds fixed from the controls in PRE_REGISTRATION.md. Descriptive: n = 3,
MID and CLS, single-rule nulls N5g and N5c, interior and cross-folio splits, B's most frequent repeated 4-grams.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hr768 as HR  # noqa: E402

OUT = HR.ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/results'
T0 = time.time()
LOCK = None                    # filled in with the lock commit
T4, CEIL4 = 11.48, 3.56        # PRE_REGISTRATION.md (controls only)
LOCAL_MAX_X3, NAIBBE_MIN_X3 = 2.34, 2.79


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def verdict(x4, p4):
    if x4 >= T4 and p4 <= 0.025:
        return 'WORD-LEVEL PHRASE REPEATS PRESENT'
    if x4 <= CEIL4 or p4 > 0.05:
        return 'NONE DETECTED'
    return 'INDETERMINATE'


def n3_reading(x3):
    if x3 <= LOCAL_MAX_X3:
        return 'within B-like first-order local structure'
    if x3 < NAIBBE_MIN_X3:
        return 'between the local-rule reference and Naibbe'
    return 'at or above the Naibbe level (beyond first-order local rules; cause not determined)'


def top_repeats(sk, n=4, k=25):
    """B's most frequent repeated n-grams (within lines, no blockers), with the folios they occur in."""
    cnt, fol = Counter(), defaultdict(set)
    for ln, f in zip(sk['lines'], sk['folios']):
        for i in range(len(ln) - n + 1):
            w = ln[i:i + n]
            if None in w:
                continue
            key = ' '.join(w)
            cnt[key] += 1
            fol[key].add(f)
    return [{'ngram': g, 'count': c, 'folios': sorted(fol[g])} for g, c in cnt.most_common(k) if c >= 2]


def main():
    sk = HR.b_skeleton()
    reps = {'TOK': lambda w: w, 'MID': HR.middle, 'CLS': HR.token_class}
    log('B under N5j (primary), N5g and N5c (descriptive)')
    res = HR.analyse(sk['lines'], sk, reps, units=('JOINT', 'GLYPH', 'CLASS'), seed=768900, log=log)
    prim = res['JOINT']['reps']['TOK']
    x4, p4 = prim['n4_all']['X'], prim['n4_all']['p']
    x3 = prim['n3_all']['X']
    out = {'pre_registration': LOCK, 'results': res,
           'primary': {'X4': x4, 'p4': p4, 'obs4': prim['n4_all']['obs'], 'null_mean4': prim['n4_all']['null_mean'],
                       'interior_p4': prim['n4_interior']['p'], 'cross_folio_p4': prim['n4_cross_folio']['p'],
                       'verdict': verdict(x4, p4)},
           'n3_descriptive': {'X3': x3, 'p3': prim['n3_all']['p'], 'obs3': prim['n3_all']['obs'],
                              'null_mean3': prim['n3_all']['null_mean'], 'reading': n3_reading(x3)},
           'top_repeated_4grams': top_repeats(sk, 4), 'top_repeated_3grams': top_repeats(sk, 3),
           'runtime_s': None}
    out['runtime_s'] = round(time.time() - T0, 1)
    json.dump(out, open(OUT / 'hidden_repeats_B.json', 'w'), indent=1)
    log(f"PRIMARY (TOK, n=4, N5j): X4 {x4:.2f} (obs {prim['n4_all']['obs']}, null {prim['n4_all']['null_mean']:.1f}), "
        f"p {p4:.3f} -> {out['primary']['verdict']}")
    log(f"n=3 descriptive: X3 {x3:.2f} (p {prim['n3_all']['p']:.3f}) -> {out['n3_descriptive']['reading']}")
    log('done')


if __name__ == '__main__':
    main()
