"""PHASE_777 lock audit: how much of each start channel does EF-F actually scramble? (controls only)
Share of certain slots whose F1 (F2) symbol is fixed by the EF-F cell key (word of <= 2 (<= 3) glyph units), and the
channel-effective movable share (slots in cells holding >= 2 distinct channel symbols), on B-fitted generator output
and payload controls. B's unigram token-length profile (declared marginal class) for comparison."""
import json
import sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit777 as A  # noqa: E402
X = A._setup()
sk = X.HR.b_skeleton()
out = {}
P = X.b_pools(sk)
tokc = Counter()
for s, c in P['by_sym']['F1'].items():
    tokc.update(c)
tot = sum(tokc.values())
out['B_unigram_share_le2_units'] = sum(v for w, v in tokc.items() if len(X.units(w)) <= 2) / tot
out['B_unigram_share_le3_units'] = sum(v for w, v in tokc.items() if len(X.units(w)) <= 3) / tot
n = X.HR.n_certain(sk)
cands = {'habit3': X.HR.habit3_lines(sk, 424242),
         'edge2': __import__('eig776').edge_only_lines(sk, 424243, k=2) if False else None}
sys.path.insert(0, str(HERE.parent.parent.parent / 'PHASE_776_EIGENSTRUCTURE_EF' / 'scripts'))
import eig776 as X6  # noqa: E402
cands['edge2'] = X6.edge_only_lines(sk, 424243, k=2)
words = X.G.plaintext_words('LAT_mesue')
cands['pay_F1_mesue'] = X.payload_lines(X.letter_stream(words, n, 0), sk, 'F1', 424244)[0]
cands['pay_F2_mesue'] = X.payload_lines(X.letter_stream(words, n, 0), sk, 'F2', 424245)[0]
import numpy as np  # noqa: E402
for name, lines in cands.items():
    assert lines != sk['lines']
    C = X.build_null(lines, X.GK.ef_groups(sk), 'EF-F')
    r = {'movable': C.frac_movable}
    for ch in ('F1', 'F2'):
        K = X.Channel(C, X.CHANNELS[ch])
        pos = C.mpos
        cellsym = {}
        for p in pos:
            cellsym.setdefault(int(C.cell[p]), set()).add(int(K.sym[C.tok[p]]))
        eff = np.mean([len(cellsym[int(C.cell[p])]) >= 2 for p in pos])
        r[f'{ch}_effective_movable'] = float(eff)
    out[name] = r
print(json.dumps(out, indent=1))
json.dump(out, open(A.OUT / 'chaneff777.json', 'w'), indent=1)
