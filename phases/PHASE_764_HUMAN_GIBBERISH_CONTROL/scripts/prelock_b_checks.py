#!/usr/bin/env python3
"""PHASE_764 pre-lock B-only checks (lean-expert audit E2). Uses no gibberish or meaningful data.

(a) full-B S1 under this pipeline (target 0.215-0.228 bits, PHASE_761 / C1212);
(b) full-B S2 (raw and top-4 binned), shuffle-corrected, with z;
(c) power curve: fraction of B chunks exceeding their own within-segment shuffle null at p <= 0.05, at
    P = 100, 150, 224, 300, 400 within-segment pairs, for S1 (raw, top-6 binned) and S2 (raw, top-4 binned).
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import g764 as G  # noqa: E402

OUT = G.ROOT / 'phases/PHASE_764_HUMAN_GIBBERISH_CONTROL/results'
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7640)


def folio_sections():
    from scripts.voynich import Transcript
    return {t.folio: t.section for t in Transcript().currier_b()}


def flat(corpus, fsec):
    segs, sec, fol = [], [], []
    for f, ss in corpus:
        for s in ss:
            segs.append(s)
            sec.append(fsec.get(f))
            fol.append(f)
    return segs, sec, fol


def draw_chunk(segs, sec, fol, P, rng, tries=100):
    pairs_per = np.array([len(s) - 1 for s in segs])
    fol_arr = np.array(fol)
    folios = sorted(set(fol))
    fw = np.array([pairs_per[fol_arr == f].sum() for f in folios], float)
    fw /= fw.sum()
    for _ in range(tries):
        f = folios[rng.choice(len(folios), p=fw)]
        idx = np.flatnonzero(fol_arr == f)
        start = int(rng.choice(idx))
        s0 = sec[start]
        j = start
        while j < len(segs) and sec[j] == s0:
            j += 1
        ch = G.chunk_pairs(segs[start:j], 0, P)
        if ch is not None:
            return ch, f
    return None, None


def main():
    fsec = folio_sections()
    res = {}
    for name, corpus in (('ZL_merged', G.load_b_zl(True)), ('ZL_allspaces', G.load_b_zl(False)), ('H', G.load_b_h())):
        segs = [s for _, ss in corpus for s in ss]
        C = G.Chunk(segs)
        Cb = G.Chunk(segs, topk=4)
        s1 = G.shuffle_corrected(C, G.stat_S1, 50, rng)
        s2 = G.shuffle_corrected(C, G.stat_S2, 50, rng)
        s2b = G.shuffle_corrected(Cb, G.stat_S2, 50, rng)
        res[name] = {'words': C.n, 'pairs': int(len(C.pair_pos)), 'S1': s1, 'S2_raw': s2, 'S2_top4': s2b}
        print(name, 'words', C.n, 'pairs', len(C.pair_pos), '| S1 excess %.3f' % s1[3],
              '| S2 raw excess %.4f' % s2[3], '| S2 top4 excess %.4f' % s2b[3], flush=True)
    corpus = G.load_b_zl(True)
    segs, sec, fol = flat(corpus, fsec)
    power = {}
    for P in (100, 150, 224, 300, 400):
        hits = defaultdict(list)
        for _ in range(200):
            ch, _ = draw_chunk(segs, sec, fol, P, rng)
            for lab, topk, stat in (('S1_raw', None, G.stat_S1), ('S1_top6', 6, G.stat_S1),
                                    ('S2_raw', None, G.stat_S2), ('S2_top4', 4, G.stat_S2)):
                C = G.Chunk(ch, topk=topk)
                o, m, p, e = G.shuffle_corrected(C, stat, 200, rng)
                hits[lab].append((p <= 0.05, e))
        power[P] = {lab: {'power': float(np.mean([h[0] for h in v])), 'median_excess': float(np.median([h[1] for h in v]))}
                    for lab, v in hits.items()}
        print('P', P, {k: round(v['power'], 3) for k, v in power[P].items()}, flush=True)
    res['power_ZL_merged'] = power
    json.dump(res, open(OUT / 'prelock_b_checks.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
