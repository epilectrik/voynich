"""PHASE_778 harness gates (mechanics only; no panel statistic).

G1  Page reproduction (Zandbergen 2021): a table whose rows are one folio's words split in three, read with the
    published line rule (back to the first column set, one row down per line) and no vertical wandering, reproduces
    that folio verbatim; with a grille whose holes sit at different heights (o1, o2) and the root/suffix columns
    shifted up by o1/o2, it reproduces it again (grille/shift equivalence).
G2  Binomial word length (Zandbergen Tables 4-6): three wheels of 24 fragments with length counts 3/9/9/3 over lengths
    0-3, 0-3 and 1-4 give, over all 13,824 combinations, exactly the binomial word-length distribution 27, 243, 972,
    2268, 3402, 3402, 2268, 972, 243, 27.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grille778 as X  # noqa: E402


def g1(sk, folio='f26r'):
    idx = [i for i, f in enumerate(sk['folio']) if f == folio]
    lines = [sk['lines'][i] for i in idx]
    G = max(len(ln) for ln in lines)
    R = len(lines)
    results = {}
    for grille in ((0, 0), (1, 2)):
        o1, o2 = grille
        ent = [('', '', '')] * (R * G)
        for li, ln in enumerate(lines):
            for p, w in enumerate(ln):
                if w is None:
                    continue
                l, c, r = X.parse_morph(w)
                # the prefix sits in row li; the root/suffix are placed so that holes at +o1/+o2 land on them
                e = list(ent[li * G + p]); e[0] = l; ent[li * G + p] = tuple(e)
                e = list(ent[((li + o1) % R) * G + p]); e[1] = c; ent[((li + o1) % R) * G + p] = tuple(e)
                e = list(ent[((li + o2) % R) * G + p]); e[2] = r; ent[((li + o2) % R) * G + p] = tuple(e)
        tab = X.Table(ent, R, G)
        out = []
        r = -1
        for li, ln in enumerate(lines):
            r = (r + 1) % R
            g = 0
            new = []
            for w in ln:
                if w is None:
                    new.append(None)
                else:
                    new.append(tab.word(r, g, grille))
                g += 1
            out.append(new)
        results[str(grille)] = out == lines
    return results


def g2():
    rng = np.random.default_rng(0)
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def wheel(lengths, counts):
        frags = []
        for L, n in zip(lengths, counts):
            for _ in range(n):
                frags.append(''.join(rng.choice(list(alphabet), size=L)) if L else '')
        return frags
    W1 = wheel((0, 1, 2, 3), (3, 9, 9, 3))
    W2 = wheel((0, 1, 2, 3), (3, 9, 9, 3))
    W3 = wheel((1, 2, 3, 4), (3, 9, 9, 3))
    hist = Counter(len(a + b + c) for a in W1 for b in W2 for c in W3)
    expected = {1: 27, 2: 243, 3: 972, 4: 2268, 5: 3402, 6: 3402, 7: 2268, 8: 972, 9: 243, 10: 27}
    return {'hist': dict(sorted(hist.items())), 'pass': dict(hist) == expected}


if __name__ == '__main__':
    sk = X.skeleton()
    r1 = g1(sk)
    r2 = g2()
    res = {'G1_page_reproduction': r1, 'G2_binomial_length': r2, 'pass': all(r1.values()) and r2['pass']}
    print(json.dumps(res, indent=1))
    json.dump(res, open(X.OUT / 'gates778.json', 'w', encoding='utf-8'), indent=1)
