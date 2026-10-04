#!/usr/bin/env python3
"""PHASE_782 optional hand-label check (pre-registration v2, E10). Output is restricted to: aligned words per group
(line-initial / other), first-character agreement between the OCR token and Ponzi's hand label per group, and the
number of line-initial disagreements where the OCR token starts with a fragment stroke and the label does not. It can
only block REACHED (line-initial agreement more than 10 points below the others, or at least 5 such disagreements).
The labelled words are OCR training data (augmentation rows), so the OCR output on them is in-sample: the check
cannot clear the edge confound. No first-character distributions are printed."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core782 as C  # noqa: E402


def main():
    C._check_cs()
    frag = set(C.cs_marginals()['fragment_strokes'])
    blocks = {}
    page, cur = None, None
    for ln in open(C.CS_FILE, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if ln.startswith('###PAGE'):
            page = ln.split()[1]
            continue
        if re.match(r'^#\s+cs-', ln):
            cur = ln.split()[-1]
            blocks[cur] = []
            continue
        if ln.startswith('#') or not ln.strip():
            continue
        if cur is not None:
            blocks[cur].append(ln.split())
    groups = {'line_initial': [0, 0], 'other': [0, 0]}
    frag_disagree = 0
    unaligned = 0
    for row in open(C.EXT / 'gt_words.txt', encoding='utf-8'):
        if '.AAA_' not in row:
            continue
        ident = row.split()[0]
        m = re.match(r'^cs\d+-cs(\d+)-([\d.]+)-L(\d+)\.(\d+)\.AAA_(.+)$', ident)
        if not m:
            unaligned += 1
            continue
        pg, pos, li, wi, label = m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5)
        if wi == 99:
            unaligned += 1
            continue
        bid = f'cs-{pg.zfill(3)}-{pos}'
        lines = blocks.get(bid)
        if not lines or li < 1 or li > len(lines) or wi > len(lines[li - 1]):
            unaligned += 1
            continue
        tok = lines[li - 1][wi - 1]
        g = 'line_initial' if wi == 1 else 'other'
        groups[g][0] += 1
        agree = tok[:1] == label[:1]
        groups[g][1] += int(agree)
        if g == 'line_initial' and not agree and tok[:1] in frag and label[:1] not in frag:
            frag_disagree += 1
    out = {'aligned': {g: v[0] for g, v in groups.items()},
           'first_char_agreement': {g: (v[1] / v[0] if v[0] else None) for g, v in groups.items()},
           'line_initial_fragment_disagreements': frag_disagree, 'unaligned_or_unknown_position': unaligned}
    li, ot = out['first_char_agreement']['line_initial'], out['first_char_agreement']['other']
    block = (li is not None and ot is not None and (ot - li) > 0.10) or frag_disagree >= 5
    out['blocks_REACHED'] = bool(block)
    json.dump(out, open(C.PH / 'results/handlabel782.json', 'w', encoding='utf-8'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
