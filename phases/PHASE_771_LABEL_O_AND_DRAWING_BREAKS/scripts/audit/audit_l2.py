#!/usr/bin/env python3
"""PHASE_771 lock audit, Arm L follow-up (text only; no label content). How the primary mixture weights respond when a
sample drawn from ONE text reference differs from the pooled token reference in word length, weighting or page type.
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

recs = Z.load()
lines = S.text_lines(recs)
comps = S.ref_matrix(S.references(lines))


def strata(lines_):
    """Counts of the reference units by word length in units (capped at 7), for each reference."""
    out = {k: Counter() for k in S.REFS}
    vec = {}
    for ln in lines_:
        for w in (w for s in ln['segs'] for w in s):
            if not Z.readable(w):
                continue
            u = Z.units(w)
            L = min(len(u), 7)
            for key, ok, idx in (('init', True, 0), ('qo', w.startswith('qo') and len(u) > 2, 2),
                                 ('o', u[0] == 'o' and len(u) > 1, 1)):
                if ok:
                    vec.setdefault((key, L), np.zeros(len(S.CATS)))[S.CIDX[S.cat(u[idx])]] += 1
                    out[key][L] += 1
    return out, vec


n_by_len, vec = strata(lines)
for key in S.REFS:
    print(f'{key}: tokens by length (units)', dict(sorted(n_by_len[key].items())))
    for L in range(2, 8):
        v = vec.get((key, L))
        if v is None or v.sum() < 50:
            continue
        w = S.em_weights(v, comps)
        print(f'   length {L}: n={int(v.sum()):5d}  EM weights (qo, o, init) of this stratum vs pooled refs: '
              f'{np.round(w, 3)}')

# AZC diagram text (ring / circle loci on pages without a language)
azc = [{'folio': r['folio'], 'lang': 'NA', 'section': r['section'], 'segs': S.words_of(r)} for r in recs
       if r['lang'] == 'NA' and not r['kind'].startswith(('P', 'L'))]
ca = S.references(azc)
for key in ('o', 'init'):
    w = S.em_weights(ca[key], comps)
    print(f'AZC diagram-text {key}-reference sample (n={int(ca[key].sum())}) vs P-text refs: EM weights {np.round(w, 3)}')
