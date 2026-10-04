#!/usr/bin/env python3
"""PHASE_782 descriptive anchors (never verdict-bearing): meaningful texts with original line breaks.

- Brunschwig 1500 (print lines): core782.load_brunschwig.
- Aberdeen Bestiary (c. 1200, Latin manuscript; `sources/aberdeen_bestiary/aberdeen_pages.json`): the site's
  transcription marks each manuscript line end with a backslash; on the 150 'explicit' pages `ab\\cd` is a mid-word
  break and `ab\\ cd` a break between words. Mid-word breaks make both edge tokens fragments (excluded, so the lines
  become ineligible at that edge). The 49 'space' pages, where the two kinds of break look the same, are not used.
  First unit: the first letter, lower-cased; editorial brackets removed.

  python anchor782.py    -> results/anchors782.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core782 as C  # noqa: E402

AB = C.ROOT / 'sources/aberdeen_bestiary/aberdeen_pages.json'
WORD = re.compile(r'[a-zæœ]+')


def load_aberdeen():
    out = []
    for pg in json.load(open(AB, encoding='utf-8')):
        if pg.get('linebreak_style') != 'explicit' or not pg.get('has_transcription'):
            continue
        raw = pg['latin_raw'].replace('[', '').replace(']', '')
        parts = re.split(r'\\', raw)
        carry = False                                # the previous line ended mid-word
        for k, seg in enumerate(parts):
            last_line = k == len(parts) - 1
            mid_break = (not last_line) and (k + 1 < len(parts)) and not parts[k + 1][:1].isspace() and parts[k + 1] != ''
            words = WORD.findall(seg.lower())
            if not words:
                carry = mid_break
                continue
            toks = [tuple(w) for w in words]
            if carry:
                toks[0] = None
            if mid_break:
                toks[-1] = None
            out.append(C.Line(pg['folio'], False, toks))
            carry = mid_break
    return out


def main(L=30):
    rng = np.random.default_rng(782_900_000)
    B = C.load_b()
    b = C.ChunkSet(B, rng, L=L, K=2 * L).excess(500, rng)
    res = {'L': L, 'B_clean_median': float(np.median(b))}
    for name, lines in (('brunschwig_1500', C.load_brunschwig()), ('aberdeen_bestiary', load_aberdeen())):
        cs = C.ChunkSet(lines, rng, within_groups=False, L=L, K=2 * L)
        e = cs.excess(500, rng)
        sh = C.ChunkSet(C.shuffle_lines(lines, rng), rng, within_groups=False, L=L, K=2 * L).excess(500, rng)
        res[name] = {'lines': len(lines), 'eligible_lines': cs.n_eligible, 'chunks': len(e),
                     'tokens_per_line_mean': float(np.mean([len(L.toks) for L in lines])),
                     'median_excess': float(np.median(e)), 'shuffled_median_excess': float(np.median(sh)),
                     'auc_vs_own_shuffle': C.auc_block(e, sh, rng, B=2000),
                     'auc_B_clean_vs_anchor': C.auc_block(b, e, rng, B=2000)}
    json.dump(res, open(C.PH / 'results/anchors782.json', 'w', encoding='utf-8'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
