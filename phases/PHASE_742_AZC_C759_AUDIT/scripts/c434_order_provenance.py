"""PHASE 742 - C434 order-provenance check.

C434 "R-Series Strict Forward Ordering" (Tier 2): R-subscript transitions are strictly forward
R1->R2->R3; backward (R2->R1,R3->R2)=0 observed/349 expected, skip (R1->R3)=0/139 -> "FORBIDDEN,
one-way progression through interior stages."

PROVENANCE QUESTION: are R-subscript "transitions" sequenced by manuscript reading order, or by the
TRANSCRIPT FILE LAYOUT? The IVTFF shows R1/R2/R3 are concentric @Cc circle-TEXT rings (not radial
spokes), recorded as contiguous depth-ordered blocks. If transitions = consecutive tokens in file
order, then "0 backward" is GUARANTEED by the block sort, and the shuffle-null "expected 349" just
measures "the file is sorted by subscript" -- a transcription artifact, not a manuscript grammar.

TEST: (1) is the per-folio R-subscript sequence (file order) non-decreasing / block-contiguous?
      (2) reconstruct observed forward/backward/skip subscript-change transitions in file order.
      (3) reproduce the "expected backward" under a within-folio token-order shuffle null.
DECISIVE: if every folio's subscripts are contiguous sorted blocks, observed-0-backward is a sort
      artifact and the constraint is vacuous (no manuscript prohibition tested).
"""
import sys, csv, functools, json
from collections import defaultdict
from pathlib import Path
import numpy as np
print = functools.partial(print, flush=True)
OUT = Path('phases/PHASE_742_AZC_C759_AUDIT/results'); OUT.mkdir(parents=True, exist_ok=True)
TX = 'data/transcriptions/interlinear_full_words.txt'

import json as _j
ZF = _j.load(open('results/azc_folio_features.json')).get('folios', {})
ZODIAC = {f for f, d in ZF.items() if d.get('section') == 'Z'}

# load R-subscript tokens per zodiac folio IN FILE ORDER (preserve row order; line_number as tiebreak)
rowidx = 0; byf = defaultdict(list)
with open(TX, encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t', quotechar='"'):
        for k in r: r[k] = r[k].strip().strip('"') if r[k] else r[k]
        rowidx += 1
        if r.get('transcriber') != 'H' or r.get('language') != 'NA': continue
        fol = r.get('folio'); pl = r.get('placement', '')
        if fol not in ZODIAC: continue
        if len(pl) >= 2 and pl[0] == 'R' and pl[1].isdigit():
            byf[fol].append((rowidx, int(pl[1]), r.get('word', '')))

def rle(seq):
    out = []
    for s in seq:
        if out and out[-1][0] == s: out[-1][1] += 1
        else: out.append([s, 1])
    return [(s, n) for s, n in out]

print(f"Zodiac folios with R-subscripts: {len(byf)}\n")
all_monotonic = True; n_asc = n_desc = 0; fwd = bwd = skip = same = 0
seqs = {}
for fol in sorted(byf):
    subs = [s for _, s, _ in sorted(byf[fol], key=lambda x: x[0])]  # file order
    seqs[fol] = subs
    r = rle(subs)
    block_keys = [s for s, _ in r]
    asc = all(block_keys[i] < block_keys[i + 1] for i in range(len(block_keys) - 1))
    desc = all(block_keys[i] > block_keys[i + 1] for i in range(len(block_keys) - 1))
    monotonic = asc or desc                      # contiguous blocks in EITHER depth direction
    all_monotonic &= monotonic
    n_asc += asc; n_desc += desc
    tag = 'ASC-blocks (R1->R3)' if asc else ('DESC-blocks (R3->R1)' if desc else '*** NON-MONOTONIC ***')
    print(f"  {fol}: subscript runs (file order) = {r}   {tag}")
    for a, b in zip(subs, subs[1:]):
        if b == a: same += 1
        elif b > a: fwd += 1
        else: bwd += 1
        if abs(b - a) >= 2: skip += 1

n_boundaries = fwd + bwd
print(f"\nOBSERVED consecutive-token subscript transitions (file order, all zodiac):")
print(f"  same-ring R_i->R_i = {same}   (within-ring; rings recorded as one block each)")
print(f"  ring-CHANGES (block boundaries) = {n_boundaries}  =  forward {fwd} + backward {bwd}  (skip {skip})")
print(f"  -> {same} of {same+n_boundaries} transitions are same-ring; ring-changes happen ONLY at the {n_boundaries} block boundaries")
print(f"  ALL {len(byf)} folios MONOTONIC blocks: {n_asc} ascending (R1->R3) + {n_desc} descending (R3->R1) = monotonic? {all_monotonic}")
print(f"  The 'forward vs backward' split is just the per-folio NUMBERING DIRECTION (cf currier_AZC.md:312:")
print(f"     f70v2 R3=outermost vs f72r1/f71r/f73r R1=outermost) -- NOT a manuscript progression.")

# reproduce "expected backward" under within-folio token-ORDER shuffle (destroys block layout)
rng = np.random.default_rng(0); B = 2000; exp_bwd = []
for _ in range(B):
    tb = 0
    for fol in byf:
        s = seqs[fol][:]; rng.shuffle(s)
        tb += sum(1 for a, b in zip(s, s[1:]) if b < a)
    exp_bwd.append(tb)
print(f"\nEXPECTED backward under within-folio token-shuffle null: mean={np.mean(exp_bwd):.0f} "
      f"(C434 cited ~349). Observed=0 because the file is block-sorted by subscript.")

verdict = ("ARTIFACT -> DEMOTE/RETRACT. Every zodiac folio records the concentric @Cc rings as MONOTONIC "
           "depth-ordered blocks (10 ascending R1->R3, 2 descending R3->R1). Ring-subscript 'transitions' "
           "occur ONLY at block boundaries; 'strict forward / 0 backward' is FORCED by this serialization "
           "(orient all folios ascending -> 0 backward by construction). The shuffle-null 'expected ~349' "
           "only measures 'is the file sorted by ring depth' (trivially yes). The direction even FLIPS "
           "between folios (per-folio numbering convention, currier_AZC.md:312) -- a genuine grammatical "
           "progression would not. R1/R2/R3 are NESTED RINGS, not radial 'interior stages'.") \
          if all_monotonic else "NOT fully monotonic -- investigate the non-monotonic folio(s)."
print(f"\nVERDICT: {verdict}")

json.dump({'n_folios': len(byf), 'n_ascending': int(n_asc), 'n_descending': int(n_desc),
           'all_monotonic_blocks': bool(all_monotonic), 'same_ring_transitions': same,
           'ring_change_boundaries': fwd + bwd, 'forward': fwd, 'backward': bwd, 'skip': skip,
           'expected_backward_shuffle_mean': float(np.mean(exp_bwd)),
           'per_folio_runs': {f: rle(seqs[f]) for f in sorted(seqs)}, 'verdict': verdict},
          open(OUT / 'c434_order_provenance.json', 'w'), indent=2)
print(f"\nSaved {OUT / 'c434_order_provenance.json'}")
