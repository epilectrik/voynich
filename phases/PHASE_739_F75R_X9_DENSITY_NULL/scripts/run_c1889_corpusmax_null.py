"""PHASE 739 (design D): selection-safe corpus-max null on C1889's 4-identical-token run.
Tests the Voynich leg of the C1889 x C2034 ~1/16,500 anchor.
Null: within-folio token-ORDER shuffle (preserves exact per-folio type frequencies =>
reachability automatic), corpus-max over 82 folios, 10k iters. KILL if p_corpus>0.05."""
import sys, json, functools, random
from collections import defaultdict
import numpy as np
print = functools.partial(print, flush=True)
sys.path.insert(0,'.')
from scripts.voynich import Transcript
tx=Transcript()

# per-folio ordered token sequence (H-track, P-placement, exclude labels/uncertain) — same filter as off-books
fl=defaultdict(lambda: defaultdict(list))
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w=t.word.strip()
    if not w or '*' in w: continue
    fl[t.folio][t.line].append(w)
def ordered(fol):
    out=[]
    for ln in sorted(fl[fol], key=lambda x:int(x) if str(x).isdigit() else 99):
        out+=fl[fol][ln]
    return out
folios=list(fl.keys())
seqs={f:ordered(f) for f in folios}

def longest_run(s):
    best=cur=1 if s else 0
    for i in range(1,len(s)):
        cur=cur+1 if s[i]==s[i-1] else 1
        if cur>best: best=cur
    return best

# OBSERVED
obs_runs={f:longest_run(seqs[f]) for f in folios}
obs_corpus_max=max(obs_runs.values())
ge4=[f for f in folios if obs_runs[f]>=4]
ge3=[f for f in folios if obs_runs[f]>=3]
print(f"N folios={len(folios)}  observed corpus-max run={obs_corpus_max}")
print(f"folios with run>=4: {sorted(ge4)}  (n={len(ge4)})")
print(f"folios with run>=3: n={len(ge3)}")

# NULL: 10k corpus-max draws (within-folio order shuffle preserves type freq exactly)
rng=random.Random(0); N=10000
corpus_max_null=np.empty(N,int)
n_folios_ge4=np.zeros(N,int); n_folios_ge3=np.zeros(N,int)
f75_self_ge4=0
work={f:list(seqs[f]) for f in folios}
for it in range(N):
    cmax=0; c4=0; c3=0
    for f in folios:
        s=work[f]; rng.shuffle(s)
        r=longest_run(s)
        if r>cmax: cmax=r
        if r>=4: c4+=1
        if r>=3: c3+=1
        if f=='f75r' and r>=4: f75_self_ge4+=1
    corpus_max_null[it]=cmax; n_folios_ge4[it]=c4; n_folios_ge3[it]=c3

p_corpus=float(np.mean(corpus_max_null>=4))
p_self_f75r=f75_self_ge4/N
print(f"\n=== NULL (10k corpus-wide within-folio order-shuffles) ===")
print(f"p_corpus = P(corpus-max run >= 4) = {p_corpus:.4f}   [KILL if >0.05]")
print(f"null corpus-max: mean={corpus_max_null.mean():.2f} max={corpus_max_null.max()} "
      f"dist>= [3]:{np.mean(corpus_max_null>=3):.3f} [4]:{p_corpus:.4f} [5]:{np.mean(corpus_max_null>=5):.4f}")
print(f"expected #folios reaching >=4 per draw: {n_folios_ge4.mean():.3f} (observed {len(ge4)})")
print(f"expected #folios reaching >=3 per draw: {n_folios_ge3.mean():.2f} (observed {len(ge3)})")
print(f"f75r self-shuffle P(run>=4) = {p_self_f75r:.4f}  (off-books per-folio ~0.0049; corpus-max pays look-elsewhere)")
verdict = "KILL (C1889 1/82 is selection artifact -> demote, anchor Voynich leg deflates)" if p_corpus>0.05 else "HARDEN (4-run corpus-rare beyond density -> C1889 secured, register p_corpus)"
print(f"\nVERDICT: {verdict}")

json.dump({"n_folios":len(folios),"observed_corpus_max":obs_corpus_max,"folios_ge4":sorted(ge4),
           "n_ge4":len(ge4),"n_ge3":len(ge3),"p_corpus":p_corpus,"p_self_f75r":p_self_f75r,
           "null_corpus_max_mean":float(corpus_max_null.mean()),"null_corpus_max_max":int(corpus_max_null.max()),
           "exp_folios_ge4":float(n_folios_ge4.mean()),"exp_folios_ge3":float(n_folios_ge3.mean()),
           "kill_threshold":0.05,"verdict":"KILL" if p_corpus>0.05 else "HARDEN","N":N},
          open("phases/PHASE_739_F75R_X9_DENSITY_NULL/results/c1889_corpusmax_null.json","w"),indent=2)
