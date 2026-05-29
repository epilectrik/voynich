"""PHASE_735: C816 cascade audit — 5-gram null on the CC-family constraints flagged
when C816 (CC positional ordering, "daiin initiates loop") demoted in PHASE_731.

Constraints in scope:
- C558 (positional): daiin line-initial ~27.7%, ol line-final 9.5%
- C819 (positional): daiin line-initial 27.1%, ol/ol_derived medial 85%
- C874 (positional, already Tier 3): daiin mean-pos 0.370, ol mean-pos 0.461
- C600 / C817 (transition/routing): daiin->CHSH 90.8%, ol->CHSH 93.2%, ol_derived->QO 57.4%
- C818 (composition: Class 17 = 88% kernel chars) — EXCLUDED (not a sequential/positional
  claim; 5-gram null is the wrong instrument; flagged separately, stays Tier 2).

METRIC (rigorous, per PHASE_733): per-synth-own-shuffle excess.
For metric M: real_excess = M_real - M_real_within_line_shuffle.
For each of N 5-gram synth corpora: synth_excess = M_synth - M_synth_OWN_within_line_shuffle.
Compare real_excess to the synth_excess distribution. This cancels composition-fidelity.

PRE-REGISTERED VERDICT (locked):
- real_excess > synth_excess at p_emp < 0.05 -> SURVIVES (above-5-gram structure)
- p_emp >= 0.05 -> DEMOTE Tier 2->3 (5-gram-reproducible)

PREDICTIONS (locked):
- Positional (daiin-initial, ol-final, ol-medial, mean-pos): DEMOTE (same metric as C816).
- daiin->CHSH, ol->CHSH: UNCERTAIN — prefix-conditioned transitions like C549 (which survived z=5.79).
- ol_derived->QO: DEMOTE/weak (C817's own table calls it NS, 57.4% vs ~50%).

N_synth=200, N_shuffle_per=12. flush + interim JSON.
"""
import sys, json, functools, random
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
print = functools.partial(print, flush=True)
PROJECT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript

RESULTS = PROJECT/'phases/PHASE_735_C816_CASCADE_AUDIT/results/cascade_batch.json'
N_SYNTH = 200; N_SHUF = 12; ORDER = 5

# Class 17 (ol_derived) token list from C818
OL_DERIVED = {'olaiin','olchedy','olchey','olkaiin','olkain','olkedy','olkeedy','olkeey','olshedy'}

print('Loading Currier B...')
tx = Transcript()
ld = defaultdict(list)
for tok in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio, tok.line)].append(w)
word_lines = [ld[k] for k in sorted(ld.keys())]
print(f'  {len(word_lines)} lines, {sum(len(l) for l in word_lines)} tokens')

# ===== metric functions: each takes a corpus (list of token-lines), returns a scalar =====
def daiin_line_initial(lines):
    tot=init=0
    for l in lines:
        for i,w in enumerate(l):
            if w=='daiin':
                tot+=1
                if i==0: init+=1
    return init/tot if tot else 0.0
def ol_line_final(lines):
    tot=fin=0
    for l in lines:
        for i,w in enumerate(l):
            if w=='ol':
                tot+=1
                if i==len(l)-1: fin+=1
    return fin/tot if tot else 0.0
def token_mean_pos(lines, tok):
    pos=[]
    for l in lines:
        if len(l)<2: continue
        for i,w in enumerate(l):
            if w==tok: pos.append(i/(len(l)-1))
    return float(np.mean(pos)) if pos else 0.0
def ol_medial(lines):
    """ol or ol_derived in medial position (not initial, not final)."""
    tot=med=0
    for l in lines:
        for i,w in enumerate(l):
            if w=='ol' or w in OL_DERIVED:
                tot+=1
                if 0<i<len(l)-1: med+=1
    return med/tot if tot else 0.0
def cond_prefix(lines, src_pred, tgt_prefixes):
    """P(next starts with one of tgt_prefixes | current matches src_pred)."""
    tot=hit=0
    for l in lines:
        for i in range(len(l)-1):
            if src_pred(l[i]):
                tot+=1
                if any(l[i+1].startswith(p) for p in tgt_prefixes): hit+=1
    return hit/tot if tot else 0.0

METRICS = {
    'C558_C819_daiin_initial': (daiin_line_initial, 'positional'),
    'C558_ol_final': (ol_line_final, 'positional'),
    'C819_ol_medial': (ol_medial, 'positional'),
    'C874_daiin_meanpos': (lambda l: token_mean_pos(l,'daiin'), 'positional'),
    'C874_ol_meanpos': (lambda l: token_mean_pos(l,'ol'), 'positional'),
    'C600_C817_daiin_to_chsh': (lambda l: cond_prefix(l, lambda w: w=='daiin', ['ch','sh']), 'transition'),
    'C817_ol_to_chsh': (lambda l: cond_prefix(l, lambda w: w=='ol', ['ch','sh']), 'transition'),
    'C600_C817_olderived_to_qo': (lambda l: cond_prefix(l, lambda w: w in OL_DERIVED, ['qo']), 'transition'),
}

def shuffle_lines(lines, rng):
    out=[]
    for l in lines:
        ll=l[:]; rng.shuffle(ll); out.append(ll)
    return out

def excess(lines, metric_fn, n_shuf, rng):
    base=metric_fn(lines)
    sh=[metric_fn(shuffle_lines(lines,rng)) for _ in range(n_shuf)]
    return base - np.mean(sh), base

# ===== real excesses =====
rng=random.Random(0)
real_excess={}; real_val={}
for name,(fn,kind) in METRICS.items():
    e,v=excess(word_lines, fn, 30, rng)
    real_excess[name]=e; real_val[name]=v
    print(f'  REAL {name}: value={v:.4f} excess-over-shuffle={e:+.4f} [{kind}]')

# ===== 5-gram =====
def train(lines,order):
    c=defaultdict(lambda: defaultdict(int))
    for wl in lines:
        s=' '.join(wl); p='\x01'*(order-1)+s+'\x02'
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
counts5=train(word_lines,ORDER)
print(f'\n5-gram: {len(counts5)} contexts. Running {N_SYNTH} synth corpora...')

synth_excess={name:[] for name in METRICS}
prng=random.Random(42); nprng=np.random.RandomState(42)
for s in range(N_SYNTH):
    synth=[samp(counts5,ORDER,len(wl),nprng) for wl in word_lines]
    for name,(fn,kind) in METRICS.items():
        e,_=excess(synth, fn, N_SHUF, prng)
        synth_excess[name].append(e)
    if (s+1)%50==0:
        print(f'  [{s+1}/{N_SYNTH}]')
        RESULTS.write_text(json.dumps({'real_excess':real_excess,'real_val':real_val,
            'synth_progress':s+1}, indent=2))

# ===== verdicts =====
print(f'\n{"="*80}')
print(f'{"metric":>32} {"kind":>11} {"real_exc":>9} {"synth_exc":>10} {"z":>6} {"p":>6}  verdict')
print('-'*92)
out={}
for name,(fn,kind) in METRICS.items():
    se=np.array(synth_excess[name]); m=se.mean(); sd=se.std()
    z=(real_excess[name]-m)/sd if sd>0 else float('inf')
    p=float((se>=real_excess[name]).mean())
    verdict='SURVIVES' if p<0.05 else 'DEMOTE'
    print(f'{name:>32} {kind:>11} {real_excess[name]:>+9.4f} {m:>+10.4f} {z:>6.2f} {p:>6.3f}  {verdict}')
    out[name]={'kind':kind,'real_excess':real_excess[name],'real_val':real_val[name],
               'synth_excess_mean':float(m),'synth_excess_sd':float(sd),'z':float(z),'p_emp':p,'verdict':verdict}

print(f'\n=== AGGREGATE ===')
surv=[n for n,d in out.items() if d['verdict']=='SURVIVES']
dem=[n for n,d in out.items() if d['verdict']=='DEMOTE']
print(f'  SURVIVES ({len(surv)}): {surv}')
print(f'  DEMOTE ({len(dem)}): {dem}')
print(f'\n  C818 (Class 17 kernel composition): EXCLUDED — composition claim, not sequential. Stays Tier 2.')
RESULTS.write_text(json.dumps({'metrics':out,'survives':surv,'demote':dem,
    'C818':'excluded_composition_claim','n_synth':N_SYNTH}, indent=2))
print(f'\nWritten to {RESULTS}')
