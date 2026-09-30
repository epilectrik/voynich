#!/usr/bin/env python3
"""PHASE_772 results-wording check (lean-expert, post-unblinding). Read-only: reproduces R/W counts from the
real ZL labels and shows where the within-sign duplicate pairs sit (per sign), plus the otal- family by sign.
Writes nothing."""
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import zod772 as Z  # noqa: E402  (library module: reads only)

labs = Z.load_labels()
print('n labels', len(labs))
signs = [l['sign'] for l in labs]
for norm in ('N1', 'N2'):
    f = Z.NORMS[norm]
    forms = [f(l['form']) for l in labs]
    st = Z.dup_stats(forms, signs)
    print(norm, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in st.items()})
    dw = Counter()
    wforms = defaultdict(list)
    for (i, a), (j, b) in combinations(enumerate(forms), 2):
        if a == b and signs[i] == signs[j]:
            dw[signs[i]] += 1
            wforms[signs[i]].append(a)
    print('  within-sign dup pairs by sign:', dict(dw))
    for s, fs in wforms.items():
        print('   ', s, sorted(Counter(fs).items()))
    rec = Counter(s for s, fo in zip(signs, forms)
                  if any(s2 != s for s2, fo2 in zip(signs, forms) if fo2 == fo))
    size = Counter(signs)
    print('  R by sign:', {s: round(rec[s] / size[s], 2) for s in size})

print('otal- (N0) by sign:', dict(Counter(l['sign'] for l in labs if l['form'].startswith('otal'))))
print('Pisces labels (N0):', [l['form'] for l in labs if l['sign'] == 'Pisces'])
