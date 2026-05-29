"""PHASE_738 Test E: SENTINEL FIDELITY (the non-circular proof, mandatory per expert sign-off).

The Test D SURVIVE could mean (a) the suffix-sentinel is ungeneratable so the synth tags
qo-tokens with wrong sentinels -> Test D biased toward SURVIVE -> uninformative, OR
(b) a real sentinel-invariant supra-token signal. (a) and (b) predict the SAME residual
pattern (A~=D~=standard-B). To distinguish WITHOUT circular inference, MEASURE the synth's
sentinel-emission fidelity DIRECTLY (crazy-expert's discriminating test).

For each synth qo-token T=BASE+EMITTED (BASE=T[:-1], EMITTED=T[-1]): is EMITTED the CORRECT
unique sentinel qo_sent[BASE]? Stratify by len(BASE).
  - reversal TRUE  -> fidelity HIGH for short-qo (qo in window), LOW for long-qo (qo distal)
    -> Test D's surviving residual sits exactly where the sentinel is corrupt -> SURVIVE = artifact.
  - reversal FALSE -> fidelity HIGH across lengths -> conditioning worked -> SURVIVE is REAL
    supra-token signal (a positive finding).

Uses the SAME token-sentinel model as Test D. N_synth=50 (enough for a rate).
"""
import sys, functools, random, json
import numpy as np
from collections import defaultdict
from pathlib import Path
print = functools.partial(print, flush=True)
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
PROJECT = Path('C:/git/voynich'); sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript
RESULTS = PROJECT/'phases/PHASE_738_QO_CHSH_WINDOW_CONTROL/results/sentinel_fidelity.json'
N_SYNTH=50; ORDER=5

tx=Transcript(); ld=defaultdict(list)
for tok in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w=tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines=[ld[k] for k in sorted(ld)]
qo_tokens=sorted({w for l in word_lines for w in l if w.startswith('qo')})
qo_sent={w:chr(0x100+i) for i,w in enumerate(qo_tokens)}
qo_sent_chars=set(qo_sent.values())
def fam(w):
    if w.startswith('qo'): return qo_sent[w]
    if w.startswith(('ch','sh')): return '\x04'
    return '\x05'
def train(lines,order,sent):
    c=defaultdict(lambda: defaultdict(int))
    for wl in lines:
        s=' '.join(w+sent(w) for w in wl); p='\x01'*(order-1)+s+'\x02'
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

counts=train(word_lines,ORDER,fam)
print(f'qo-tokens={len(qo_tokens)}; generating {N_SYNTH} synth corpora for fidelity audit...')
# strata: short BASE (qo, len<=4) vs long BASE (qo, len>=5)
tally={'short':{'n':0,'correct':0,'sentinel_is_qo':0},'long':{'n':0,'correct':0,'sentinel_is_qo':0}}
novel_qo=0
nprng=np.random.RandomState(123)
for s in range(N_SYNTH):
    synth=[samp(counts,ORDER,len(wl),nprng) for wl in word_lines]
    for l in synth:
        for T in l:
            if not T.startswith('qo'): continue
            if len(T)<2: continue
            base, emitted = T[:-1], T[-1]
            strat = 'short' if len(base)<=4 else 'long'
            tally[strat]['n']+=1
            if emitted in qo_sent_chars: tally[strat]['sentinel_is_qo']+=1
            if base in qo_sent:
                if qo_sent[base]==emitted: tally[strat]['correct']+=1
            else:
                novel_qo+=1
    if (s+1)%25==0: print(f'  [{s+1}/{N_SYNTH}]')

print(f'\n{"="*78}')
print(f'SENTINEL-EMISSION FIDELITY (synth qo-tokens, BASE+EMITTED):')
out={}
for strat in ('short','long'):
    t=tally[strat]; n=t['n']
    fid = t['correct']/n if n else 0.0
    isqo = t['sentinel_is_qo']/n if n else 0.0
    out[strat]={'n':n,'fidelity_correct_unique':fid,'frac_sentinel_in_qo_family':isqo}
    print(f'  {strat:>5}-qo (len BASE {"<=4" if strat=="short" else ">=5"}): n={n:>6} '
          f'correct-unique-sentinel={fid:.3f}  sentinel-is-a-qo-char={isqo:.3f}')
print(f'\n  novel (synth qo-base not in real vocab): {novel_qo}')
delta = out['short']['fidelity_correct_unique'] - out['long']['fidelity_correct_unique']
print(f'\n  fidelity gap short-minus-long = {delta:+.3f}')
if out['long']['fidelity_correct_unique'] < 0.5 and delta>0.10:
    concl='REVERSAL VINDICATED: long-qo sentinel fidelity LOW + length-dependent -> Test D biased toward SURVIVE -> SURVIVE uninformative. C549 rests on Test C.'
elif out['long']['fidelity_correct_unique'] >= 0.7:
    concl='REVERSAL WRONG: long-qo sentinel fidelity HIGH -> conditioning worked -> Test D SURVIVE is a REAL supra-token signal (positive finding).'
else:
    concl='AMBIGUOUS: intermediate fidelity; interpret with care.'
print(f'\n  CONCLUSION: {concl}')
out['fidelity_gap_short_minus_long']=delta; out['conclusion']=concl; out['n_synth']=N_SYNTH
RESULTS.write_text(json.dumps(out,indent=2))
print(f'\nWritten to {RESULTS}')
