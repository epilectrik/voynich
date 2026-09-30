#!/usr/bin/env python3
"""PHASE_771 post-hoc DESCRIPTIVES (after the locked run; not verdicts).

(a) The unit after the initial 'o' in label o-words vs text o-words in paragraph-first lines (header register) and
    in other lines, all length-standardised to the label length profile (strata 2..7+).
(b) Arm E, Currier A: last-unit shares of pre-break words vs continuation-line-final words vs interior words.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

OUT = Z.ROOT / 'phases/PHASE_771_LABEL_O_AND_DRAWING_BREAKS/results/posthoc771.json'
SHOW = ['k', 't', 'l', 'r', 'e', 's', 'pf', 'd', 'bench', 'ch']


def main():
    recs = Z.load()
    lines = S.text_lines(recs)
    items = S.label_o_items(recs)
    prof = Counter(it[-2] for it in items)
    lab = defaultdict(Counter)
    for it in items:
        lab[it[-2]][it[-1]] += 1
    head, body = defaultdict(Counter), defaultdict(Counter)
    for ln in lines:
        for w in (w for s in ln['segs'] for w in s):
            if Z.readable(w) and w.startswith('o') and not w.startswith('qo') and len(Z.units(w)) >= 2:
                u = Z.units(w)
                (head if ln['par_start'] else body)[S.lstratum(len(u))][S.cat(u[1])] += 1

    def standardised(tab):
        """Share of each category, averaged over strata with the label length profile as weights."""
        tot = sum(prof.values())
        out = Counter()
        for L, wL in prof.items():
            n = sum(tab[L].values())
            if n == 0:
                continue
            for c, v in tab[L].items():
                out[c] += (wL / tot) * v / n
        return {c: round(out[c], 3) for c in SHOW}
    res = {'a_unit_after_o_length_standardised': {
        'labels': standardised(lab), 'text_o_words_paragraph_first_lines': standardised(head),
        'text_o_words_other_lines': standardised(body),
        'n': {'labels': len(items), 'header_o_words': sum(sum(c.values()) for c in head.values()),
              'body_o_words': sum(sum(c.values()) for c in body.values())}}}
    # (b) last units at A breaks
    words, breaks = S.edge_tables(lines)
    fin = Counter(w['last'] for w in words if w['lang'] == 'A' and w['i_end'] == 0 and not w['par_last_line'])
    mid = Counter(w['last'] for w in words if w['lang'] == 'A' and w['i_start'] > 0 and w['i_end'] > 0)
    pre = Counter(Z.units(b['pre'])[-1] for b in breaks if b['lang'] == 'A')
    units = [u for u, _ in (fin + mid + pre).most_common(10)]
    share = lambda c: {u: round(c[u] / sum(c.values()), 3) for u in units}
    res['b_A_last_unit_shares'] = {'continuation_line_final': share(fin), 'pre_break': share(pre), 'interior': share(mid),
                                   'n': {'final': sum(fin.values()), 'pre_break': sum(pre.values()),
                                         'interior': sum(mid.values())}}
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
