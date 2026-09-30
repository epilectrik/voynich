"""PHASE_776 audit: line homogeneity of the plants (controls only), to place the line-clustering plant against C1214
(B's lines 3.8% lower atom-composition entropy than a within-folio shuffle; registered value, not recomputed on B).
Statistic here: mean per-line Shannon entropy of class labels (lines with >= 4 mapped tokens), plant vs within-folio
shuffle of its tokens (20 shuffles); reduction in %. Writes results/audit/audit776_linehomog.json.
"""
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit776 as A  # noqa: E402


def line_entropy(lines, X):
    import numpy as np
    out = []
    for ln in lines:
        c = [X.TOKEN_CLASS.get(w, 0) for w in ln if w is not None]
        c = [x for x in c if x > 0]
        if len(c) < 4:
            continue
        _, n = np.unique(c, return_counts=True)
        p = n / n.sum()
        out.append(float(-(p * np.log2(p)).sum()))
    return float(np.mean(out))


def main():
    X = A._setup()
    import numpy as np
    sk = X.HR.b_skeleton()
    res = {}
    for fam, par, seed in [('edge2_line', 0.0, 9190), ('edge2_line', 0.3, 9140), ('edge2_line', 0.6, 9142),
                           ('habit', 1.0, 9100), ('edge3', 1.0, 9150)]:
        lines = A.make_lines(X, sk, fam, par, seed)
        assert lines != sk['lines']
        obs = line_entropy(lines, X)
        rng = np.random.default_rng(seed + 3)
        by = {}
        for li, f in enumerate(sk['folios']):
            by.setdefault(f, []).append(li)
        sh = []
        for _ in range(20):
            new = [list(ln) for ln in lines]
            for f, lis in by.items():
                pos = [(li, p) for li in lis for p, w in enumerate(lines[li]) if w is not None]
                toks = [lines[li][p] for li, p in pos]
                perm = rng.permutation(len(toks))
                for (li, p), j in zip(pos, perm):
                    new[li][p] = toks[j]
            sh.append(line_entropy(new, X))
        m = float(np.mean(sh))
        res[f'{fam}|{par}|{seed}'] = {'obs': obs, 'shuffle': m, 'reduction_pct': 100 * (m - obs) / m}
        print(fam, par, seed, round(obs, 4), round(m, 4), round(100 * (m - obs) / m, 2), flush=True)
    json.dump(res, open(HERE.parent.parent / 'results' / 'audit' / 'audit776_linehomog.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
