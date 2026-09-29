#!/usr/bin/env python3
"""PHASE_766 data preparation: map Zandbergen item numbers (pharmaceutical section, f87-f102) to ZL label lines.

ZL tags many labels with <!NNa>/<!NNb>/<!NN>. Untagged labels are numbered by the section's counting rule, observed on
tagged pages: a container label (@Lc) starts a new item N with suffix 'a'; the first fragment label (@Lf) after it is
N 'b'; every further @Lf is the next item; a continuation line ('+') belongs to the previous item. Counting starts at
the first label of f88r = item 1. The rule is checked against every tag; the count resyncs at each tag, and
disagreements are reported.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path('C:/git/voynich')
ZL = ROOT / 'data/transcriptions/reference/ZL_official.txt'
OUT = ROOT / 'phases/PHASE_766_LABEL_REFERENCE_CONSISTENCY/results'
OUT.mkdir(parents=True, exist_ok=True)


def label_lines():
    out = []
    for raw in open(ZL, encoding='utf-8', errors='replace'):
        m = re.match(r'^<(f(\d+)[rv]\d?)\.(\d+),([@+=*&~])(L\w*)>\s+(.*)$', raw.rstrip('\n'))
        if not m or not (88 <= int(m.group(2)) <= 102):
            continue
        text = m.group(6)
        tag = re.search(r'<!(\d+)([a-z]?)>', text)
        word = re.sub(r'<[^>]*>', '', text).strip()
        out.append({'folio': m.group(1), 'locus': int(m.group(3)), 'cont': m.group(4) == '+', 'type': m.group(5),
                    'tag': (int(tag.group(1)), tag.group(2)) if tag else None, 'word': word})
    return out


def main():
    L = label_lines()
    n, after_c, prev = 0, False, None
    checks, events = [], []
    for rec in L:
        if rec['cont'] and prev is not None:
            num, suf = prev
        elif rec['type'].startswith('Lc'):
            n += 1
            num, suf = n, 'a'
            after_c = True
        else:
            if after_c:
                num, suf = n, 'b'
                after_c = False
            else:
                n += 1
                num, suf = n, ''
        rec['sim'] = (num, suf)
        if rec['tag'] is not None:
            ok = rec['tag'][0] == num
            checks.append(ok)
            if not ok:
                events.append({'folio': rec['folio'], 'locus': rec['locus'], 'tag': rec['tag'], 'simulated': (num, suf)})
            n = rec['tag'][0]                                  # resync
            num = n
            rec['sim'] = (num, rec['tag'][1] or suf)
        rec['item'] = rec['sim'][0]
        rec['source'] = 'tag' if rec['tag'] is not None else 'count'
        prev = rec['sim']
    agree = sum(checks)
    print(f'labels f88-f102: {len(L)} | tagged: {len(checks)} | rule agrees with tag: {agree}/{len(checks)}')
    for e in events:
        print('  disagreement', e)
    # uncertainty: a counted item is 'verified' if the count between its neighbouring tags had no disagreement
    tagged_idx = [i for i, r in enumerate(L) if r['tag'] is not None]
    bad_after = {e['folio'] + '.' + str(e['locus']) for e in events}
    json.dump(L, open(OUT / 'item_map.json', 'w', encoding='utf-8'), indent=1)
    first_tag = tagged_idx[0] if tagged_idx else None
    print('first tagged label index', first_tag, L[first_tag]['folio'] if first_tag is not None else None,
          'tag', L[first_tag]['tag'] if first_tag is not None else None, '| simulated before resync',
          (checks[0] if checks else None))
    return L


if __name__ == '__main__':
    main()
