"""PHASE_738: qo->CHSH window-control discriminating test.

Resolves whether C549 (qo->ch/sh) and C2056 (correction lanes) survive the 5-gram null
as GENUINE above-char-Markov structure, or whether the survival is the boundary-identity-
loss / window-blindness artifact found in PHASE_737 (C2064): a char-5-gram only sees the
last 4 chars before a token boundary, so it cannot condition on a LONG source token's qo
prefix (distal: qokeedy -> boundary context "eedy ") and "survival" is then uninformative.

THREE COMPLEMENTARY TESTS (all on qo-prefixed source -> next-token-starts-ch/sh):

  TEST B (length-split, windowing DIAGNOSTIC): standard per-synth-own-shuffle 5-gram null
    on SHORT-qo (len<=4, qo IN window) vs LONG-qo (len>=5, qo distal) aggregates.
    PRED: SHORT-qo DEMOTE (p>=.05), LONG-qo SURVIVE (p<.05) -> verdict is LENGTH-driven.

  TEST A (sentinel-injection, MECHANISM confirmation): re-run LONG-qo with a prefix-family
    sentinel appended to every token (qo->\x03, ch/sh->\x04, other->\x05) so the null CAN
    condition on qo-family at the boundary regardless of length. Metric computed on the
    augmented tokens (sentinel is a SUFFIX; startswith front-checks unaffected).
    PRED: LONG-qo survival COLLAPSES (p>=.05) -> windowing confirmed as the cause.
    (If it still survives -> genuine supra-local structure, C549 holds as above-Markov.)

  TEST C (within-line token shuffle, CORRECT instrument): is the qo->ch/sh adjacency real
    token-order structure (above COMPOSITION)? real rate vs distribution of within-line
    token-shuffle rates (the token/class-level null, immune to char windowing).
    PRED: real >> shuffle (p<.05) for all-qo/short/long -> adjacency is real token-order.

COMBINED VERDICT (pre-registered):
  B length-dependent + A collapse + C real  -> C549/C2056 are REAL token-order structure;
      char-5-gram is the WRONG instrument (verdict is windowing); "above-char-Markov"
      framing was an artifact. Banner Layer-1: above-composition real, NOT above-char-Markov.
  A NO-collapse (long-qo survives sentinel) + C real -> genuine supra-local structure;
      C549 holds as above-Markov (stronger than the consolidation banner currently says).
  C fails -> adjacency not even above composition -> full demote.

N_synth=200, N_shuffle_per=12, order=5 (identical machinery to PHASE_735/737). N_shuf_C=500.
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

RESULTS = PROJECT/'phases/PHASE_738_QO_CHSH_WINDOW_CONTROL/results/window_control.json'
N_SYNTH=200; N_SHUF=12; ORDER=5; N_SHUF_C=500
TGT=('ch','sh')

print('Loading Currier B...')
tx=Transcript(); ld=defaultdict(list)
for tok in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w=tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines=[ld[k] for k in sorted(ld)]
print(f'  {len(word_lines)} lines, {sum(len(l) for l in word_lines)} tokens')

def is_qo(w): return w.startswith('qo')
def src_short(w): return is_qo(w) and len(w)<=4
def src_long(w):  return is_qo(w) and len(w)>=5
def src_allqo(w): return is_qo(w)

# report Ns
nS=sum(1 for l in word_lines for i in range(len(l)-1) if src_short(l[i]))
nL=sum(1 for l in word_lines for i in range(len(l)-1) if src_long(l[i]))
nA=nS+nL
print(f'  qo-source non-final occurrences: SHORT(len<=4)={nS}  LONG(len>=5)={nL}  ALL={nA}')

def cond_prefix(lines, pred, tgt=TGT):
    tot=hit=0
    for l in lines:
        for i in range(len(l)-1):
            if pred(l[i]):
                tot+=1
                if l[i+1].startswith(tgt): hit+=1
    return hit/tot if tot else 0.0
def shuffle_lines(lines,rng):
    out=[]
    for l in lines:
        ll=l[:]; rng.shuffle(ll); out.append(ll)
    return out
def excess(lines, fn, n_shuf, rng):
    base=fn(lines); sh=[fn(shuffle_lines(lines,rng)) for _ in range(n_shuf)]
    return base-np.mean(sh), base

PREDS={'short':src_short,'long':src_long,'allqo':src_allqo}

# ===== TEST C: within-line token shuffle (correct instrument) =====
print('\n=== TEST C: within-line token-shuffle null (correct instrument) ===')
rngc=random.Random(7); testC={}
for name,pred in PREDS.items():
    real=cond_prefix(word_lines, pred)
    shuf=[cond_prefix(shuffle_lines(word_lines,rngc), pred) for _ in range(N_SHUF_C)]
    sm=np.mean(shuf); ss=np.std(shuf)
    z=(real-sm)/ss if ss>0 else float('inf'); p=float((np.array(shuf)>=real).mean())
    testC[name]={'real':real,'shuffle_mean':float(sm),'shuffle_sd':float(ss),'z':float(z),'p':p,
                 'real_above_composition': p<0.05}
    print(f'  {name:>6}: real={real:.4f} shuffle={sm:.4f} z={z:+.2f} p={p:.4f} '
          f'-> {"REAL token-order" if p<0.05 else "NOT above composition"}')

# ===== 5-gram machinery (identical) =====
def train(lines,order,sent=None):
    c=defaultdict(lambda: defaultdict(int))
    for wl in lines:
        toks=[w+sent(w) for w in wl] if sent else wl
        s=' '.join(toks); p='\x01'*(order-1)+s+'\x02'
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

# ===== TEST B: standard 5-gram null, length-split =====
print('\n=== TEST B: standard char-5-gram null, length-split ===')
rng=random.Random(0)
realB={};
for name in ('short','long'):
    e,v=excess(word_lines, lambda l,p=PREDS[name]: cond_prefix(l,p), 30, rng)
    realB[name]={'excess':e,'val':v}; print(f'  REAL {name}-qo->chsh: rate={v:.4f} excess-over-shuffle={e:+.4f}')
counts5=train(word_lines,ORDER)
print(f'  5-gram: {len(counts5)} contexts. {N_SYNTH} synth...')
synthB={'short':[],'long':[]}
prng=random.Random(42); nprng=np.random.RandomState(42)
for s in range(N_SYNTH):
    synth=[samp(counts5,ORDER,len(wl),nprng) for wl in word_lines]
    for name in ('short','long'):
        e,_=excess(synth, lambda l,p=PREDS[name]: cond_prefix(l,p), N_SHUF, prng); synthB[name].append(e)
    if (s+1)%50==0:
        print(f'    [B {s+1}/{N_SYNTH}]')
        RESULTS.write_text(json.dumps({'testC':testC,'realB':realB,'progressB':s+1},indent=2))

# ===== TEST A: sentinel-injection, long-qo =====
def fam(w):
    if w.startswith('qo'): return '\x03'
    if w.startswith(('ch','sh')): return '\x04'
    return '\x05'
print('\n=== TEST A: sentinel-injection (prefix-family in boundary window), long-qo ===')
aug_lines=[[w+fam(w) for w in l] for l in word_lines]
# metric on augmented tokens: front-anchored startswith still works (sentinel is suffix)
def src_long_aug(w): return w.startswith('qo') and (len(w)-1)>=5   # -1 for trailing sentinel
def cond_prefix_aug(lines):
    tot=hit=0
    for l in lines:
        for i in range(len(l)-1):
            if src_long_aug(l[i]):
                tot+=1
                if l[i+1].startswith(TGT): hit+=1
    return hit/tot if tot else 0.0
eA,vA=excess(aug_lines, cond_prefix_aug, 30, rng)
print(f'  REAL long-qo->chsh (augmented): rate={vA:.4f} excess-over-shuffle={eA:+.4f}')
counts5a=train(word_lines,ORDER,sent=fam)
print(f'  sentinel 5-gram: {len(counts5a)} contexts. {N_SYNTH} synth...')
synthA=[]
for s in range(N_SYNTH):
    synth=[samp(counts5a,ORDER,len(wl),nprng) for wl in aug_lines]
    e,_=excess(synth, cond_prefix_aug, N_SHUF, prng); synthA.append(e)
    if (s+1)%50==0:
        print(f'    [A {s+1}/{N_SYNTH}]')

# ===== verdicts =====
def verdict(real_e, synth_list):
    se=np.array(synth_list); m=se.mean(); sd=se.std()
    z=(real_e-m)/sd if sd>0 else float('inf'); p=float((se>=real_e).mean())
    return float(m),float(sd),float(z),p
print(f'\n{"="*92}')
out={'testC':testC}
print('TEST B (standard 5-gram, length-split):')
for name in ('short','long'):
    m,sd,z,p=verdict(realB[name]['excess'], synthB[name])
    v='SURVIVE' if p<0.05 else 'DEMOTE'
    print(f'  {name:>5}-qo: real_exc={realB[name]["excess"]:+.4f} synth_exc={m:+.4f} z={z:+.2f} p={p:.3f} -> {v}')
    out[f'B_{name}']={'real_excess':realB[name]['excess'],'real_val':realB[name]['val'],
                      'synth_mean':m,'synth_sd':sd,'z':z,'p':p,'verdict':v}
mA,sdA,zA,pA=verdict(eA, synthA)
vA_=('SURVIVE' if pA<0.05 else 'COLLAPSE')
print(f'\nTEST A (sentinel-injection, long-qo): real_exc={eA:+.4f} synth_exc={mA:+.4f} z={zA:+.2f} p={pA:.3f} -> {vA_}')
out['A_long_sentinel']={'real_excess':eA,'real_val':vA,'synth_mean':mA,'synth_sd':sdA,'z':zA,'p':pA,'verdict':vA_}

# combined
b_lengthdep = (out['B_short']['verdict']=='DEMOTE') and (out['B_long']['verdict']=='SURVIVE')
a_collapse  = (vA_=='COLLAPSE')
c_real      = all(testC[n]['real_above_composition'] for n in PREDS)
print(f'\n{"="*92}\nCOMBINED:')
print(f'  B length-dependent (short demote & long survive): {b_lengthdep}')
print(f'  A sentinel collapse (windowing is the cause):      {a_collapse}')
print(f'  C real token-order (above composition):            {c_real}')
if c_real and b_lengthdep and a_collapse:
    cv='REAL TOKEN-ORDER, WRONG-INSTRUMENT: C549/C2056 above-composition but NOT above-char-Markov (5-gram survival was windowing)'
elif c_real and not a_collapse:
    cv='ABOVE-MARKOV CONFIRMED: long-qo survives even with qo-family in-window (genuine supra-local structure)'
elif not c_real:
    cv='FULL DEMOTE: adjacency not above composition'
else:
    cv='MIXED: see individual tests'
print(f'\n  VERDICT: {cv}')
out['combined']={'B_length_dependent':b_lengthdep,'A_collapse':a_collapse,'C_real':c_real,'verdict':cv}
RESULTS.write_text(json.dumps(out,indent=2))
print(f'\nWritten to {RESULTS}')
