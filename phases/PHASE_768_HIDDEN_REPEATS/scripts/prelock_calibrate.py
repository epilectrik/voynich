#!/usr/bin/env python3
"""PHASE_768 pre-lock calibration on CONTROL corpora only. Currier B supplies its skeleton (lines, blockers, sections,
folios) and, for the habit generator, its class-bigram and emission frequencies; no repeat statistic is computed on B.

Positive controls (a message is present):
  P1  five word-written NTs (Latin, Italian, Spanish, German, English), TOK, plus position-attached spelling variants
      with k = 4 and k = 16 spellings (TOK_k4, TOK_k16);
  P3  the Naibbe cipher (GV1) of three real plaintexts (P-REC Codicillus recipes, P-PHA Antidotarium, P-ITA Dante),
      TOK, MID, CLS and ORACLE (the plaintext chunk behind each token).
Negative controls (no message):
  N2  a local-rule generator fitted on B (class-bigram chain + class emission), TOK, MID, CLS;
  N1  Timm-Schinner self-citation output (reference: copies earlier words), TOK, MID, CLS.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hr768 as HR  # noqa: E402

OUT = HR.ROOT / 'phases/PHASE_768_HIDDEN_REPEATS/results'
OUT.mkdir(parents=True, exist_ok=True)
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def main():
    sk = HR.b_skeleton()
    n = HR.n_certain(sk)
    log(f'skeleton: {len(sk["lines"])} lines, {n} certain tokens')
    res = {}
    ident = lambda w: w  # noqa: E731

    # ---------------------------------------------------------------- P1 natural texts (+ spelling variants)
    for i, lang in enumerate(('la', 'it', 'es', 'de', 'en')):
        stream = HR.natural_stream(lang)[:n]
        lines = HR.pour(stream, sk)
        npos = sum(len(ln) for ln in lines)
        rng = np.random.default_rng(768100 + i)
        extras = {'TOK_k4': ('TOK', rng.integers(0, 4, npos)), 'TOK_k16': ('TOK', rng.integers(0, 16, npos))}
        log(f'P1 WORD_{lang}')
        res[f'P1_WORD_{lang}'] = HR.analyse(lines, sk, {'TOK': ident}, units=('LETTER', 'CLASS'), seed=768110 + 10 * i,
                                            extras=extras, log=log)
        json.dump(res, open(OUT / 'prelock_calibration.json', 'w'), indent=1)

    # ---------------------------------------------------------------- P3 Naibbe with oracle
    for j, pid in enumerate(('P-REC', 'P-PHA', 'P-ITA')):
        toks, chunks = HR.naibbe_stream(pid, 768001 + j, n)
        votes = defaultdict(Counter)
        for t, c in zip(toks, chunks):
            votes[t][c] += 1
        oracle = {t: c.most_common(1)[0][0] for t, c in votes.items()}
        purity = sum(c.most_common(1)[0][1] for c in votes.values()) / len(toks)
        lines = HR.pour(toks, sk)
        log(f'P3 Naibbe {pid} (token -> chunk purity {purity:.4f}; {len(set(toks))} types, {len(set(chunks))} chunks)')
        r = HR.analyse(lines, sk, {'TOK': ident, 'MID': HR.middle, 'CLS': HR.token_class,
                                   'ORACLE': lambda w: oracle.get(w, w)}, units=('GLYPH', 'CLASS'),
                       seed=768210 + 10 * j, log=log)
        r['oracle_purity'] = purity
        res[f'P3_NAIBBE_{pid}'] = r
        json.dump(res, open(OUT / 'prelock_calibration.json', 'w'), indent=1)

    # ---------------------------------------------------------------- N2 habit generator, N1 Timm
    log('N2 habit generator')
    res['N2_HABIT'] = HR.analyse(HR.habit_lines(sk, 768301), sk, {'TOK': ident, 'MID': HR.middle,
                                                                  'CLS': HR.token_class},
                                 units=('GLYPH', 'CLASS'), seed=768310, log=log)
    json.dump(res, open(OUT / 'prelock_calibration.json', 'w'), indent=1)
    log('N1 Timm')
    res['N1_TIMM'] = HR.analyse(HR.timm_lines(sk, 767101), sk, {'TOK': ident, 'MID': HR.middle,
                                                                'CLS': HR.token_class},
                                units=('GLYPH', 'CLASS'), seed=768410, log=log)
    res['runtime_s'] = round(time.time() - T0, 1)
    json.dump(res, open(OUT / 'prelock_calibration.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
