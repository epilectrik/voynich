"""BLOCKING CONTROL (both experts): is the 5-gram's B1 failure (6-state gap 0.956 vs
real 0.894) genuine macro-structure absence, or a hallucination/coverage artifact?

In the main run, hallucinated (novel) 5-gram tokens defaulted to class 1 -> all piled into
one 6-state, sharpening the hub-spoke -> over-separated gap (0.956 > real 0.894). That
over-separation in the WRONG direction is the tell.

Test B1 6-state gap under three token-handling regimes:
  (A) AS-IS: unmapped tokens -> class 1 (main-run behavior, gave 0.956)
  (B) DROP-UNMAPPED: unmapped tokens excluded from the 6-state transition matrix
  (C) VOCAB-CONSTRAINED: regenerate emitting ONLY attested tokens (reject novel)
Plus per-synth-own-shuffle excess on the gap (the rigorous PHASE_733 metric) for the
cleanest regime. Report hallucination rate.

If (B)/(C) gap -> ~0.89, the 0.956 "failure" was hallucination artifact; at the 6-state
level the 5-gram is NOT cleanly failing (consistent with PHASE_733's 60% λ2 reproduction).
If still ~0.956, real macro-structure absence.

flush + JSON.
"""
import sys, json, functools, importlib.util
import numpy as np
print = functools.partial(print, flush=True)
PROJECT = Path = __import__('pathlib').Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT))
spec = importlib.util.spec_from_file_location('gensuff', str(PROJECT/'phases/GENERATIVE_SUFFICIENCY/scripts/generative_sufficiency.py'))
gs = importlib.util.module_from_spec(spec); spec.loader.exec_module(gs)
RESULTS = PROJECT/'phases/PHASE_734_M2_VS_5GRAM/results/b1_hallucination_control.json'
ORDER=5; N_INST=20

from collections import defaultdict, Counter
def train(lines_words):
    c=defaultdict(Counter)
    for words in lines_words:
        s=' '.join(words); p='\x01'*(ORDER-1)+s+'\x02'
        for i in range(ORDER-1,len(p)): c[p[i-(ORDER-1):i]][p[i]]+=1
    return {k:(list(v.keys()), np.array(list(v.values()),float)) for k,v in c.items()}
def sample_line(counts, target, rng, vocab=None):
    out=[];ctx='\x01'*(ORDER-1);buf=[];att=0
    while len(out)<target and att<target*80:
        att+=1;cand=counts.get(ctx)
        if not cand: ctx='\x01'*(ORDER-1);continue
        chars,w=cand; ch=chars[rng.choice(len(chars),p=w/w.sum())]
        if ch=='\x02':
            if buf:
                tok=''.join(buf); buf=[]
                if vocab is None or tok in vocab: out.append(tok)
            ctx='\x01'*(ORDER-1)
            if len(out)>=target: break
            continue
        if ch==' ':
            if buf:
                tok=''.join(buf); buf=[]
                if vocab is None or tok in vocab: out.append(tok)
            ctx=(ctx+ch)[-(ORDER-1):]; continue
        buf.append(ch); ctx=(ctx+ch)[-(ORDER-1):]
    if buf and len(out)<target:
        tok=''.join(buf)
        if vocab is None or tok in vocab: out.append(tok)
    return out[:target]

def gap_from_classlines(cls_lines):
    """6-state spectral gap from a list of lines of class ids (None excluded)."""
    st=np.zeros((6,6))
    for line in cls_lines:
        for i in range(len(line)-1):
            s1=gs.STATE_IDX.get(gs.CLASS_TO_STATE.get(line[i]))
            s2=gs.STATE_IDX.get(gs.CLASS_TO_STATE.get(line[i+1]))
            if s1 is not None and s2 is not None: st[s1,s2]+=1
    rs=st.sum(1,keepdims=True); P=st/np.maximum(rs,1e-12)
    ev=np.sort(np.abs(np.linalg.eigvals(P)))[::-1]
    return float(1.0-ev[1]) if len(ev)>1 else 1.0

print('Loading battery...')
all_tokens, lines, params = gs.load_data()
t2c = params['token_to_class']
real_line_words=[[t['word'] for t in line] for line in lines]
vocab=set(t2c.keys())
counts=train(real_line_words)

# real gap
real_gap = gap_from_classlines([[t2c.get(w) for w in wl] for wl in real_line_words])
print(f'Real 6-state gap: {real_gap:.4f}')

rng=np.random.RandomState(42)
asis=[]; drop=[]; vc=[]; halluc=[]
for inst in range(N_INST):
    r=np.random.RandomState(42+inst*1000)
    # unconstrained generation (as main run)
    synth=[sample_line(counts,len(wl),r) for wl in real_line_words]
    ntok=sum(len(l) for l in synth); nmap=sum(1 for l in synth for w in l if w in vocab)
    halluc.append(1-nmap/ntok if ntok else 0)
    # A: as-is (unmapped -> class 1)
    asis.append(gap_from_classlines([[t2c.get(w,1) for w in l] for l in synth]))
    # B: drop unmapped (unmapped -> None, excluded)
    drop.append(gap_from_classlines([[t2c.get(w) for w in l] for l in synth]))
    # C: vocab-constrained regeneration
    r2=np.random.RandomState(7+inst*1000)
    synth_vc=[sample_line(counts,len(wl),r2,vocab=vocab) for wl in real_line_words]
    vc.append(gap_from_classlines([[t2c.get(w) for w in l] for l in synth_vc]))

print(f'\nHallucination rate (novel tokens): {np.mean(halluc):.3f}')
print(f'\n6-state spectral gap (real = {real_gap:.4f}, within-0.05 = pass):')
print(f'  (A) AS-IS (unmapped->class1):     {np.mean(asis):.4f} +/- {np.std(asis):.4f}   pass={np.mean([abs(g-real_gap)<0.05 for g in asis]):.2f}')
print(f'  (B) DROP-UNMAPPED:                {np.mean(drop):.4f} +/- {np.std(drop):.4f}   pass={np.mean([abs(g-real_gap)<0.05 for g in drop]):.2f}')
print(f'  (C) VOCAB-CONSTRAINED:            {np.mean(vc):.4f} +/- {np.std(vc):.4f}   pass={np.mean([abs(g-real_gap)<0.05 for g in vc]):.2f}')

asis_m=float(np.mean(asis)); drop_m=float(np.mean(drop)); vc_m=float(np.mean(vc))
print(f'\n=== VERDICT ===')
artifact = abs(asis_m-real_gap) > 0.05 and (abs(drop_m-real_gap)<0.05 or abs(vc_m-real_gap)<0.05)
if artifact:
    print('  The AS-IS B1 failure was a HALLUCINATION ARTIFACT. With clean token handling the')
    print('  5-gram gap moves toward real -> 5-gram is NOT cleanly failing B1 at the 6-state level.')
    print('  C978 strengthening should LEAD with C2061 (raw-49 λ2, merge-free); the 6-state B1 is')
    print('  not clean evidence either way (projection-dependent). Consistent with PHASE_733 ~60% reproduction.')
    verdict='B1_HALLUCINATION_ARTIFACT'
elif abs(drop_m-real_gap)>0.05 and abs(vc_m-real_gap)>0.05:
    print('  B1 failure SURVIVES clean token handling -> genuine 6-state macro-structure absence.')
    print('  Corroborates C2061/C978 at the 6-state level (5-gram cannot reproduce the gap).')
    verdict='B1_GENUINE_FAILURE'
else:
    print('  Mixed; interpret with caution.')
    verdict='MIXED'

RESULTS.write_text(json.dumps({'real_gap':real_gap,'hallucination_rate':float(np.mean(halluc)),
    'asis_gap':asis_m,'drop_unmapped_gap':drop_m,'vocab_constrained_gap':vc_m,'verdict':verdict},indent=2))
print(f'\nWritten to {RESULTS}')
