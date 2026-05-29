"""PHASE_738 follow-up: C2056 five correction-lanes under the within-line token-shuffle null
(Test C / correct instrument).

C2056 registered five post-heat correction lanes (source = qo-k = startswith 'qok'):
  ok (vessel), ot (transfer), ch (active monitor), oke (cool-stabilize=ok-e), sh (passive).
Original residuals were measured "above 5-gram" — but PHASE_738 established the char-5-gram
is the WRONG INSTRUMENT for these token-adjacency claims (qok sources are long; the prefix
is distal from the boundary; suffix-sentinel control is ungeneratable, Test E 28% fidelity).

The CORRECT token-level null is the within-line token shuffle (composition control), which
is immune to char-windowing. C2056's own numbers already cite "real +X% above shuffle"; this
script isolates and SIGNIFICANCE-TESTS that composition-controlled excess for all five lanes,
replacing the invalidated 5-gram-residual framing.

Targets (matching PHASE_731 prefix_bigram_rate): ok=['ok'], ot=['ot'], ch=['ch'],
ok-e=['oke'], sh=['sh']. Source = startswith('qok'). Reference: broad qo->ch (C2056 cites
+25pp), and broad qo->ch/sh (= PHASE_738 Test C, already known above composition).

DECISION (per expert sign-off): a lane is CONFIRMED real token-order structure if real rate
> within-line-shuffle at p<0.05 (Bonferroni across 5 lanes, alpha=0.01). Lanes failing ->
demote (their old 5-gram-residual standing is invalid; Test C is the bar).
N_shuffle=500.
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
RESULTS = PROJECT/'phases/PHASE_738_QO_CHSH_WINDOW_CONTROL/results/c2056_lanes_testC.json'
N_SHUF=500

tx=Transcript(); ld=defaultdict(list)
for tok in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w=tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines=[ld[k] for k in sorted(ld)]
print(f'{len(word_lines)} lines, {sum(len(l) for l in word_lines)} tokens')

def make_pred(srcpfx):
    return lambda w: w.startswith(srcpfx)
def cond_prefix(lines, srcpred, tgts):
    tot=hit=0
    for l in lines:
        for i in range(len(l)-1):
            if srcpred(l[i]):
                tot+=1
                if any(l[i+1].startswith(t) for t in tgts): hit+=1
    return (hit/tot if tot else 0.0), tot
def shuffle_lines(lines,rng):
    out=[]
    for l in lines:
        ll=l[:]; rng.shuffle(ll); out.append(ll)
    return out

qok = make_pred('qok')
nqok = sum(1 for l in word_lines for i in range(len(l)-1) if qok(l[i]))
print(f"qo-k (startswith 'qok') non-final occurrences: {nqok}\n")

LANES = [('qok->ok','qok',['ok']), ('qok->ot','qok',['ot']), ('qok->ch','qok',['ch']),
         ('qok->oke (ok-e)','qok',['oke']), ('qok->sh','qok',['sh'])]
REFS  = [('broad qo->ch','qo',['ch']), ('broad qo->ch/sh','qo',['ch','sh'])]

alpha = 0.05/len(LANES)
print(f'Bonferroni alpha = 0.05/{len(LANES)} = {alpha:.3f}\n')
rng=random.Random(11); out={}
print(f'{"lane":>18} {"N":>6} {"real":>7} {"shuffle":>8} {"z":>7} {"p":>7}  verdict')
print('-'*72)
for name,src,tgts in LANES+REFS:
    pred=make_pred(src)
    real,tot=cond_prefix(word_lines,pred,tgts)
    shuf=[cond_prefix(shuffle_lines(word_lines,rng),pred,tgts)[0] for _ in range(N_SHUF)]
    sm=float(np.mean(shuf)); ss=float(np.std(shuf))
    z=(real-sm)/ss if ss>0 else float('inf'); p=float((np.array(shuf)>=real).mean())
    is_lane = (name,src,tgts) in LANES or name.startswith('qok')
    if name in [l[0] for l in LANES]:
        verdict = 'CONFIRMED (above composition)' if p<alpha else 'DEMOTE (not above composition)'
    else:
        verdict = 'ref'
    print(f'{name:>18} {tot:>6} {real:>7.4f} {sm:>8.4f} {z:>+7.2f} {p:>7.4f}  {verdict}')
    out[name]={'N':tot,'real':real,'shuffle_mean':sm,'shuffle_sd':ss,'z':z,'p':p,
               'above_composition':bool(p<alpha),'verdict':verdict}

lanes_conf=[n for n,_,_ in LANES if out[n]['above_composition']]
lanes_dem =[n for n,_,_ in LANES if not out[n]['above_composition']]
print(f'\nLANES CONFIRMED above composition ({len(lanes_conf)}/5): {lanes_conf}')
print(f'LANES DEMOTED ({len(lanes_dem)}/5): {lanes_dem}')
out['_summary']={'confirmed':lanes_conf,'demoted':lanes_dem,'alpha':alpha,'n_shuffle':N_SHUF}
RESULTS.write_text(json.dumps(out,indent=2))
print(f'\nWritten to {RESULTS}')
