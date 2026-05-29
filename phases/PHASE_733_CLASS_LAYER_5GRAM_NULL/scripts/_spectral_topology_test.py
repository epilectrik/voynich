"""CLEAN topology test: second-eigenvalue (lambda2) of the 49x49 class transition matrix.

The partition-ARI test was confounded by run_merge's hardcoded role constraints (random
matrix -> ARI 0.669, shuffle -> 0.804). lambda2 of the raw transition matrix bypasses that
entirely: it measures how much macro-state structure exists beyond the stationary
distribution, with NO algorithmic constraints.

Real spectrum (t2_spectral.json): lambda2=0.208, lambda3=0.135.
Shuffle destroys transition order -> rows collapse to marginal -> lambda2 -> ~0 (floor).
The question: does the 5-gram reproduce lambda2 (and lambda3)?

PRE-REGISTERED:
- 5-gram lambda2 ~= real lambda2 (within shuffle->real range, say >60% of the way from
  shuffle floor to real) -> eigenstructure morphology-reproducible -> cascade.
- 5-gram lambda2 ~= shuffle floor (near 0, <30% of the way) -> eigenstructure above-Markov
  -> macro-automaton SURVIVES.
- in between -> partial.

flush + JSON.
"""
import sys, json, functools, random
import numpy as np
from pathlib import Path
from collections import defaultdict
print = functools.partial(print, flush=True)
PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript

RESULTS = PROJECT_ROOT/'phases/PHASE_733_CLASS_LAYER_5GRAM_NULL/results/spectral_topology_test.json'
N_SYNTH=50; N_SHUFFLE=30; ORDER=5
ac=list(range(1,50)); c2i={c:i for i,c in enumerate(ac)}; n_cls=49
ctm=json.load(open(PROJECT_ROOT/'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))
ttc={t:int(c) for t,c in ctm['token_to_class'].items()}

tx=Transcript(); ld=defaultdict(list)
for tok in tx.currier_b():
    w=tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines=[ld[k] for k in sorted(ld.keys())]

def eigs(class_lines):
    counts=np.zeros((n_cls,n_cls))
    for line in class_lines:
        seq=[c for c in line if c is not None]
        for a,b in zip(seq,seq[1:]): counts[c2i[a]][c2i[b]]+=1
    rs=counts.sum(1,keepdims=True)
    P=np.divide(counts,rs,where=rs>0,out=np.zeros_like(counts))
    ev=np.sort(np.abs(np.linalg.eigvals(P)))[::-1]
    return ev[1], ev[2]  # lambda2, lambda3 magnitudes

real_cl=[[ttc.get(w) for w in wl] for wl in word_lines]
real_l2, real_l3 = eigs(real_cl)
print(f'REAL: lambda2={real_l2:.4f}, lambda3={real_l3:.4f}  (t2 reported l2=0.208, l3=0.135)')

# shuffle floor
rng=random.Random(7)
real_seqs=[[c for c in line if c is not None] for line in real_cl]
sh_l2=[]; sh_l3=[]
for _ in range(N_SHUFFLE):
    sl=[]
    for s in real_seqs:
        ss=s[:]; rng.shuffle(ss); sl.append(ss)
    l2,l3=eigs(sl); sh_l2.append(l2); sh_l3.append(l3)
sh_l2_m, sh_l2_sd = float(np.mean(sh_l2)), float(np.std(sh_l2))
sh_l3_m = float(np.mean(sh_l3))
print(f'SHUFFLE floor: lambda2={sh_l2_m:.4f}+/-{sh_l2_sd:.4f}, lambda3={sh_l3_m:.4f}')

# 5-gram
def train(lines,order):
    c=defaultdict(lambda: defaultdict(int))
    for wl in lines:
        s=' '.join(wl); p='\x01'*(order-1)+s+'\x02'
        for i in range(order-1,len(p)): c[p[i-(order-1):i]][p[i]]+=1
    return {k:dict(v) for k,v in c.items()}
def samp(counts,order,target,rng):
    out=[];ctx='\x01'*(order-1);buf=[];a=0
    while len(out)<target and a<target*60:
        a+=1;cand=counts.get(ctx)
        if not cand: ctx='\x01'*(order-1);continue
        ch=rng.choices(list(cand.keys()),weights=list(cand.values()),k=1)[0]
        if ch=='\x02':
            if buf:out.append(''.join(buf));buf=[]
            ctx='\x01'*(order-1)
            if len(out)>=target:break
            continue
        if ch==' ':
            if buf:out.append(''.join(buf));buf=[]
            ctx=(ctx+ch)[-(order-1):];continue
        buf.append(ch);ctx=(ctx+ch)[-(order-1):]
    if buf and len(out)<target:out.append(''.join(buf))
    return out[:target]
counts5=train(word_lines,ORDER); srng=random.Random(42)
sy_l2=[]; sy_l3=[]
for s in range(N_SYNTH):
    sl=[samp(counts5,ORDER,len(wl),srng) for wl in word_lines]
    scl=[[ttc.get(w) for w in wl] for wl in sl]
    l2,l3=eigs(scl); sy_l2.append(l2); sy_l3.append(l3)
    if (s+1)%10==0: print(f'  [{s+1}/{N_SYNTH}] 5gram lambda2 mean={np.mean(sy_l2):.4f}')
sy_l2_m, sy_l2_sd = float(np.mean(sy_l2)), float(np.std(sy_l2))
sy_l3_m = float(np.mean(sy_l3))

print(f'\n=== SPECTRAL TOPOLOGY RESULT (lambda2 = macro-state structure) ===')
print(f'  REAL lambda2:    {real_l2:.4f}')
print(f'  5-gram lambda2:  {sy_l2_m:.4f} +/- {sy_l2_sd:.4f}')
print(f'  SHUFFLE floor:   {sh_l2_m:.4f} +/- {sh_l2_sd:.4f}')
# fraction of the way from shuffle floor to real
frac = (sy_l2_m - sh_l2_m) / (real_l2 - sh_l2_m) if real_l2 != sh_l2_m else float('nan')
print(f'  5-gram is {frac*100:.0f}% of the way from shuffle floor to real')
print(f'  lambda3: real {real_l3:.4f}, 5-gram {sy_l3_m:.4f}, shuffle {sh_l3_m:.4f}')

print(f'\n=== VERDICT ===')
if frac >= 0.60:
    print('  5-gram reproduces most of the macro-state eigenstructure -> MORPHOLOGY-REPRODUCIBLE -> cascade.')
    verdict='MORPHOLOGY_REPRODUCIBLE_CASCADE'
elif frac < 0.30:
    print('  5-gram lambda2 near shuffle floor -> macro-state eigenstructure is ABOVE-MARKOV.')
    print('  Macro-automaton SURVIVES. Cascade STOPS at C2023.')
    verdict='ABOVE_MARKOV_SURVIVES'
else:
    print(f'  5-gram reproduces {frac*100:.0f}% of the eigenstructure -> PARTIAL.')
    verdict='PARTIAL'

RESULTS.write_text(json.dumps({
    'real_lambda2':real_l2,'real_lambda3':real_l3,
    'fivegram_lambda2_mean':sy_l2_m,'fivegram_lambda2_sd':sy_l2_sd,'fivegram_lambda3_mean':sy_l3_m,
    'shuffle_lambda2_mean':sh_l2_m,'shuffle_lambda2_sd':sh_l2_sd,'shuffle_lambda3_mean':sh_l3_m,
    'fraction_floor_to_real':frac,'verdict':verdict,
},indent=2))
print(f'\nWritten to {RESULTS}')
