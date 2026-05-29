"""Symmetry control: per-synth-own-shuffle lambda2 excess (parallel to the C2023 metric).

Makes the lambda2 survival audit-proof and methodologically symmetric with the C2023 demotion.
For each 5-gram synth corpus: compute its lambda2 AND its own within-line-shuffle lambda2 floor;
synth_excess = synth_lambda2 - synth_own_shuffle_lambda2. Compare to real excess (0.206-0.118=0.088).

Expert prediction: synth excess ~= 0 (synth lambda2 already at shuffle floor), real excess +0.088.
If so, lambda2 survival is unimpeachable and exactly parallel to the C2023 per-synth metric.
"""
import sys, json, functools, random
import numpy as np
from pathlib import Path
from collections import defaultdict
print = functools.partial(print, flush=True)
PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript

RESULTS = PROJECT_ROOT/'phases/PHASE_733_CLASS_LAYER_5GRAM_NULL/results/lambda2_excess_symmetry.json'
N_SYNTH=40; N_SHUF_PER=8; ORDER=5
ac=list(range(1,50)); c2i={c:i for i,c in enumerate(ac)}; n_cls=49
ttc={t:int(c) for t,c in json.load(open(PROJECT_ROOT/'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))['token_to_class'].items()}
tx=Transcript(); ld=defaultdict(list)
for tok in tx.currier_b():
    w=tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines=[ld[k] for k in sorted(ld.keys())]

def lam2(class_lines):
    counts=np.zeros((n_cls,n_cls))
    for line in class_lines:
        seq=[c for c in line if c is not None]
        for a,b in zip(seq,seq[1:]): counts[c2i[a]][c2i[b]]+=1
    rs=counts.sum(1,keepdims=True)
    P=np.divide(counts,rs,where=rs>0,out=np.zeros_like(counts))
    return np.sort(np.abs(np.linalg.eigvals(P)))[::-1][1]

def own_shuffle_excess(class_lines, n_shuf, rng):
    base=lam2(class_lines)
    seqs=[[c for c in line if c is not None] for line in class_lines]
    shuf=[]
    for _ in range(n_shuf):
        sl=[]
        for s in seqs:
            ss=s[:]; rng.shuffle(ss); sl.append(ss)
        shuf.append(lam2(sl))
    return base - np.mean(shuf), base

rng=random.Random(7)
real_cl=[[ttc.get(w) for w in wl] for wl in word_lines]
real_excess, real_l2 = own_shuffle_excess(real_cl, 20, rng)
print(f'REAL: lambda2={real_l2:.4f}, own-shuffle excess={real_excess:+.4f}')

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
synth_excess=[]
for s in range(N_SYNTH):
    sl=[samp(counts5,ORDER,len(wl),srng) for wl in word_lines]
    scl=[[ttc.get(w) for w in wl] for wl in sl]
    exc,_=own_shuffle_excess(scl, N_SHUF_PER, srng)
    synth_excess.append(exc)
    if (s+1)%10==0: print(f'  [{s+1}/{N_SYNTH}] synth excess mean={np.mean(synth_excess):+.4f}')

m=float(np.mean(synth_excess)); sd=float(np.std(synth_excess))
z=(real_excess-m)/sd if sd>0 else float('nan')
p=sum(1 for x in synth_excess if x>=real_excess)/len(synth_excess)
print(f'\n=== LAMBDA2 EXCESS SYMMETRY RESULT ===')
print(f'  REAL lambda2 own-shuffle excess:  {real_excess:+.4f}')
print(f'  5-gram synth excess: mean {m:+.4f} +/- {sd:.4f}')
print(f'  z={z:+.2f}, p_emp(synth>=real)={p:.4f}')
clean = p < 0.05
print(f'\n  {"CLEAN: lambda2 survival is audit-proof and symmetric with C2023 metric." if clean else "NOT clean — reconsider."}')
print(f'  (Contrast: C2023 scalar-MI excess p=0.21 [reproduced/fails]; lambda2 excess p={p:.3f} [{"survives" if clean else "?"}])')
RESULTS.write_text(json.dumps({'real_lambda2':real_l2,'real_excess':real_excess,
    'synth_excess_mean':m,'synth_excess_sd':sd,'z':z,'p_emp':p,'clean':bool(clean)},indent=2))
print(f'\nWritten to {RESULTS}')
