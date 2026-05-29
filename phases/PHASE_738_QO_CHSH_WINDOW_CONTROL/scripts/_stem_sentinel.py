"""PHASE_738 Test D: STEM-LEVEL sentinel (mandatory completion, per expert sign-off).

Test A used a qo-FAMILY sentinel (one char for all qo-tokens). Both experts flagged that
the surviving +1.7pp residual could be STEM-SPECIFIC local routing the family-sentinel
cannot represent (C2001/C2002: qo-stems route differently — qokedy z=+2.49 vs qotar z=-0.20).

Test D gives each distinct qo-prefixed SOURCE TOKEN a UNIQUE sentinel char (token/stem
resolution) so the order-5 char model can condition on the exact qo-token at the boundary.
ch/sh -> \x04, other -> \x05 (as Test A). Metric: long-qo->ch/sh on augmented tokens.

This is a CONSERVATIVE test for a supra-local claim: per-token sentinels let the model
memorize each qo-token's successor (even rare ones), so collapse is EASY. Therefore:
  - COLLAPSE (p>=.05): residual is token/stem-LOCAL -> "above-char-Markov" framing DEAD;
    C549/C2056 rest entirely on Test C (real token-order above composition). EXPECTED.
  - SURVIVE (p<.05): structure persists even with full token identity in-window ->
    genuinely SUPRA-token (would be a small real claim worth separate registration).

PRE-REGISTERED PREDICTION (both experts): COLLAPSE (residual is at noise floor, stem-local).
N_synth=200, order=5, per-synth-own-shuffle. Identical machinery to Tests A/B.
"""
import sys, json, functools, random
import numpy as np
from collections import defaultdict
from pathlib import Path
print = functools.partial(print, flush=True)
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
PROJECT = Path('C:/git/voynich'); sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript

RESULTS = PROJECT/'phases/PHASE_738_QO_CHSH_WINDOW_CONTROL/results/stem_sentinel.json'
N_SYNTH=200; N_SHUF=12; ORDER=5; TGT=('ch','sh')

print('Loading Currier B...')
tx=Transcript(); ld=defaultdict(list)
for tok in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w=tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines=[ld[k] for k in sorted(ld)]
print(f'  {len(word_lines)} lines, {sum(len(l) for l in word_lines)} tokens')

# per-distinct-qo-token unique sentinel (token/stem resolution)
qo_tokens = sorted({w for l in word_lines for w in l if w.startswith('qo')})
qo_sent = {w: chr(0x100+i) for i,w in enumerate(qo_tokens)}
print(f'  distinct qo-tokens: {len(qo_tokens)} (each gets a unique sentinel)')
def fam(w):
    if w.startswith('qo'): return qo_sent[w]
    if w.startswith(('ch','sh')): return '\x04'
    return '\x05'

aug_lines=[[w+fam(w) for w in l] for l in word_lines]
def src_long_aug(w): return w.startswith('qo') and (len(w)-1)>=5
def cond_prefix_aug(lines):
    tot=hit=0
    for l in lines:
        for i in range(len(l)-1):
            if src_long_aug(l[i]):
                tot+=1
                if l[i+1].startswith(TGT): hit+=1
    return hit/tot if tot else 0.0
def shuffle_lines(lines,rng):
    out=[]
    for l in lines:
        ll=l[:]; rng.shuffle(ll); out.append(ll)
    return out
def excess(lines, fn, n_shuf, rng):
    base=fn(lines); sh=[fn(shuffle_lines(lines,rng)) for _ in range(n_shuf)]
    return base-np.mean(sh), base
def train(lines,order,sent):
    c=defaultdict(lambda: defaultdict(int))
    for wl in lines:
        toks=[w+sent(w) for w in wl]; s=' '.join(toks); p='\x01'*(order-1)+s+'\x02'
        for i in range(order-1,len(p)): c[p[i-(order-1):i]][p[i]]+=1
    return {k:(list(v.keys()),np.array(list(v.values()),float)) for k,v in c.items()}
def samp(counts,order,target,rng):
    out=[];ctx='\x01'*(order-1);buf=[];a=0
    while len(out)<target and a<target*60:
        a+=1;cand=counts.get(ctx)
        if not cand: ctx='\x01'*(order-1);continue
        chars,w=cand; ch=chars[rng.choice(len(chars),p=w/w.sum())]
        if ch=='\x02':
            if buf: out.append(''.join(buf)); buf=[]
            ctx='\x01'*(order-1)
            if len(out)>=target: break
            continue
        if ch==' ':
            if buf: out.append(''.join(buf)); buf=[]
            ctx=(ctx+ch)[-(order-1):]; continue
        buf.append(ch); ctx=(ctx+ch)[-(order-1):]
    if buf and len(out)<target: out.append(''.join(buf))
    return out[:target]

rng=random.Random(0)
eD,vD=excess(aug_lines, cond_prefix_aug, 30, rng)
print(f'  REAL long-qo->chsh (stem-sentinel augmented): rate={vD:.4f} excess-over-shuffle={eD:+.4f}')
counts=train(word_lines,ORDER,fam)
print(f'  stem-sentinel 5-gram: {len(counts)} contexts. {N_SYNTH} synth...')
prng=random.Random(42); nprng=np.random.RandomState(42); synth_exc=[]
for s in range(N_SYNTH):
    synth=[samp(counts,ORDER,len(wl),nprng) for wl in aug_lines]
    e,_=excess(synth, cond_prefix_aug, N_SHUF, prng); synth_exc.append(e)
    if (s+1)%50==0: print(f'    [D {s+1}/{N_SYNTH}]')
se=np.array(synth_exc); m=se.mean(); sd=se.std()
z=(eD-m)/sd if sd>0 else float('inf'); p=float((se>=eD).mean())
verdict='SURVIVE (supra-token)' if p<0.05 else 'COLLAPSE (token/stem-local)'
print(f'\n{"="*80}')
print(f'TEST D (stem/token-resolution sentinel, long-qo): real_exc={eD:+.4f} synth_exc={m:+.4f} z={z:+.2f} p={p:.3f}')
print(f'  -> {verdict}')
print(f'\n  Compare: Test A (family sentinel) residual +0.017 z=2.39; standard-B synth +0.016.')
print(f'  If COLLAPSE: residual was stem-local; "above-char-Markov" framing dropped; C549/C2056 rest on Test C.')
RESULTS.write_text(json.dumps({'real_excess':eD,'real_val':vD,'synth_mean':float(m),'synth_sd':float(sd),
    'z':float(z),'p':p,'verdict':verdict,'n_distinct_qo_tokens':len(qo_tokens),'n_synth':N_SYNTH},indent=2))
print(f'\nWritten to {RESULTS}')
