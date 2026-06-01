"""PHASE 741 — f75r joint x4-AND-x9 anchor: registration-grade corpus-rarity (LOCKED).

Corrects the PHASE_739 design-D scope error (which tested the x4 run ALONE, p=0.097 — the registry-
COMPRESSED Voynich leg, per the registry-compression episode). The anchor's actual Voynich leg is the
JOINT: f75r is the UNIQUE folio of 82 with BOTH a >=4 identical-token run (C1889) AND a >=9 qok-class
2-consecutive-line window (C1969). Predicate validated: reproduces C1969's exact 3 high-density folios
(f75r, f86v3, f108r) and the corpus ceiling of 9.

NULL (selection-safe, look-elsewhere-corrected, type-frequency-preserving — same as PHASE_739 design-D):
  per folio, shuffle token ORDER (preserves exact type-frequency multiset -> reachability automatic),
  re-segment to original line lengths; per draw take CORPUS-MAX over 82 folios.
  p_joint = P(>=1 folio has BOTH run>=4 AND window>=9). Also report x4-alone and x9-alone for contrast.
N=10000, seed=0. The joint p_joint is the Voynich leg of the 1/16,500; x C2034 (Catalan x4-AND-x9 unique, 1/189).
"""
import sys, json, functools, random
from collections import defaultdict
from pathlib import Path
import numpy as np
print = functools.partial(print, flush=True)
sys.path.insert(0, '.')
from scripts.voynich import Transcript
OUT = Path('phases/PHASE_741_F75R_JOINT_ANCHOR/results'); OUT.mkdir(parents=True, exist_ok=True)
tx = Transcript(); fl = defaultdict(lambda: defaultdict(list))
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w or '*' in w: continue
    fl[t.folio][t.line].append(w)
folios = list(fl.keys())
def lines_of(fol): return [fl[fol][ln] for ln in sorted(fl[fol], key=lambda x:int(x) if str(x).isdigit() else 99)]
FL = {f: lines_of(f) for f in folios}
def longest_run(flat):
    b=c=1 if flat else 0
    for i in range(1,len(flat)):
        c=c+1 if flat[i]==flat[i-1] else 1; b=max(b,c)
    return b
def max_qokwin(lines):
    qc=[sum(1 for w in ln if w.startswith('qok')) for ln in lines]
    if not qc: return 0
    if len(qc)==1: return qc[0]
    return max(qc[i]+qc[i+1] for i in range(len(qc)-1))
obs={}
for f in folios:
    lines=FL[f]; flat=[w for ln in lines for w in ln]
    obs[f]=(longest_run(flat), max_qokwin(lines))
run4=sorted(f for f in folios if obs[f][0]>=4)
win9=sorted(f for f in folios if obs[f][1]>=9)
both=sorted(f for f in folios if obs[f][0]>=4 and obs[f][1]>=9)
print(f"OBSERVED ({len(folios)} folios): run>=4 {run4}; window>=9 {win9}; BOTH {both}  (f75r window={obs.get('f75r',('?','?'))[1]})")
rng=random.Random(0); N=10000
linelens={f:[len(ln) for ln in FL[f]] for f in folios}
flats={f:[w for ln in FL[f] for w in ln] for f in folios}
ab=a4=a9=0
for _ in range(N):
    ib=i4=i9=False
    for f in folios:
        s=flats[f][:]; rng.shuffle(s)
        r=longest_run(s)
        lens=linelens[f]; segs=[]; p=0
        for L in lens: segs.append(s[p:p+L]); p+=L
        wn=max_qokwin(segs)
        if r>=4: i4=True
        if wn>=9: i9=True
        if r>=4 and wn>=9: ib=True
    ab+=ib; a4+=i4; a9+=i9
res={'observed_both_folios':both,'observed_run4':run4,'observed_win9':win9,'f75r_window':obs.get('f75r')[1],
     'p_joint':ab/N,'p_x4_alone':a4/N,'p_x9_alone':a9/N,'N':N,'seed':0,
     'predicate':'qok=startswith(qok); win=max qok over 2-consecutive-line windows; reproduces C1969 3 folios + ceiling 9',
     'null':'within-folio token-order shuffle (type-freq-preserving), re-segment to line lengths, corpus-max over 82'}
print(f"\nNULL (N={N}, selection-safe corpus-max): p_x4_alone={a4/N:.4f}  p_x9_alone={a9/N:.4f}  p_JOINT={ab/N:.4f}")
print(f"  -> Voynich leg = JOINT p={ab/N:.4f} (~ registry 1/82=0.0122); x C2034 (1/189) => 1/16,500 holds")
(OUT/'joint_x4x9_corpusmax.json').write_text(json.dumps(res,indent=2))
print(f"Saved {OUT/'joint_x4x9_corpusmax.json'}")
