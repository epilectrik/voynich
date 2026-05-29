"""Is the AXM attractor's 0.698 self-transition above-composition, or a frequency
artifact of AXM being 68% of tokens? (The elephant the audit thread kept circling.)

C976: AXM macro-state = 32 classes, 67.7% of mass, 0.698 self-transition (the operational
attractor at the core of the macro-automaton / Tier 0 closed-loop picture).
C2061: λ2 (raw-49) is above the 5-gram null (p=0.000) — BUT λ2 is a scalar aggregating ALL
off-floor structure; it did NOT isolate whether the AXM self-loop specifically is above
composition. C1010: the 6-state partition has spectral-clustering ARI=0.059 — NOT spectrally
natural, "structurally forced" by role/depletion invariants. So λ2's excess might live in the
depletion-asymmetry directions, not the AXM self-loop. The "big block self-transitions a lot
because it's big" null is LIVE and has never been run.

PRE-REGISTERED (locked, expert-designed pivot after the ablation design was killed as foregone+rigged):

PRIMARY: AXM self-transition rate under per-synth-own-shuffle 5-gram null.
  M = P(token_{t+1} in AXM-class | token_t in AXM-class), within-line. Real = ~0.698.
  real_excess = M_real − M_real_within_line_shuffle  (shuffle ≈ composition expectation).
  For N=200 5-gram synth: synth_excess = M_synth − M_synth_OWN_shuffle.
  VERDICT:
    real_excess > synth_excess at p_emp < 0.05 -> AXM self-cohesion is ABOVE-Markov
      (vindicates the attractor as designed structure; sharpens C978 0.698 measured->above-composition).
    p_emp >= 0.05 -> AXM self-cohesion is COMPOSITION/Markov-reproducible
      (scope-correction on the macro-automaton interpretation: the attractor is "big bucket
      self-transitions a lot because it's big" + char-statistics, not designed cohesion).

COMPANION: submatrix-λ2 localization. λ2 of the AXM-block-only submatrix (renormalized) vs
  the non-AXM submatrix. Where does the slow-mixing live — attractor or lanes?

GATE-ZERO: confirm the 5-gram reproduces a known surviving bigram (qo->ch/sh, C549) in THIS
  pipeline as a sanity check that the synth generation is sound. (PHASE_731: qo->ch/sh real
  excess should exceed synth excess — the C549 survival.)

Discipline: per-synth-own-shuffle mandatory; raw-49 / scalar only (never merged 6×6);
flush + interim JSON.
"""
import sys, json, functools, random
import numpy as np
from collections import defaultdict
from pathlib import Path
sys = __import__('sys')
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
print = functools.partial(print, flush=True)
PROJECT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript

RESULTS = PROJECT/'phases/PHASE_736_AXM_ATTRACTOR_COMPOSITION/results/axm_composition_test.json'
N_SYNTH = 200; N_SHUF = 12; ORDER = 5
AXM = {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49}
ac = list(range(1,50)); c2i = {c:i for i,c in enumerate(ac)}; n_cls = 49

print('Loading Currier B + class map...')
ttc = {t:int(c) for t,c in json.load(open(PROJECT/'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))['token_to_class'].items()}
tx = Transcript(); ld = defaultdict(list)
for tok in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines = [ld[k] for k in sorted(ld.keys())]
print(f'  {len(word_lines)} lines, {sum(len(l) for l in word_lines)} tokens')

# AXM self-transition rate: over within-line adjacent token pairs where BOTH tokens are
# classified, P(next in AXM | current in AXM).
def axm_self_rate(lines):
    tot = hit = 0
    for l in lines:
        cls = [ttc.get(w) for w in l]
        for i in range(len(cls)-1):
            a,b = cls[i], cls[i+1]
            if a is None or b is None: continue
            if a in AXM:
                tot += 1
                if b in AXM: hit += 1
    return hit/tot if tot else 0.0

def qo_chsh_rate(lines):
    """gate-zero: P(next starts ch/sh | current starts qo)."""
    tot=hit=0
    for l in lines:
        for i in range(len(l)-1):
            if l[i].startswith('qo'):
                tot+=1
                if l[i+1].startswith('ch') or l[i+1].startswith('sh'): hit+=1
    return hit/tot if tot else 0.0

def shuffle_excess(lines, fn, n_shuf, rng):
    base = fn(lines)
    sh=[]
    for _ in range(n_shuf):
        sl=[]
        for l in lines:
            ll=l[:]; rng.shuffle(ll); sl.append(ll)
        sh.append(fn(sl))
    return base - np.mean(sh), base, float(np.mean(sh))

# ===== REAL =====
rng = random.Random(0)
real_axm_exc, real_axm, real_axm_shuf = shuffle_excess(word_lines, axm_self_rate, 30, rng)
real_qo_exc, real_qo, real_qo_shuf = shuffle_excess(word_lines, qo_chsh_rate, 30, rng)
print(f'\nREAL AXM self-transition: {real_axm:.4f}, shuffle(composition) {real_axm_shuf:.4f}, excess {real_axm_exc:+.4f}')
print(f'REAL qo->ch/sh (gate-zero): {real_qo:.4f}, shuffle {real_qo_shuf:.4f}, excess {real_qo_exc:+.4f}')

# ===== submatrix λ2 localization =====
def build_matrix(lines):
    C=np.zeros((n_cls,n_cls))
    for l in lines:
        cls=[ttc.get(w) for w in l]
        for i in range(len(cls)-1):
            a,b=cls[i],cls[i+1]
            if a is not None and b is not None: C[c2i[a]][c2i[b]]+=1
    return C
def lam2_of(C):
    rs=C.sum(1,keepdims=True); P=np.divide(C,rs,where=rs>0,out=np.zeros_like(C))
    ev=np.sort(np.abs(np.linalg.eigvals(P)))[::-1]
    return float(ev[1]) if len(ev)>1 else 0.0
Cfull=build_matrix(word_lines)
axm_idx=[c2i[c] for c in AXM]; non_idx=[c2i[c] for c in ac if c not in AXM]
lam2_full=lam2_of(Cfull)
lam2_axm=lam2_of(Cfull[np.ix_(axm_idx,axm_idx)])
lam2_non=lam2_of(Cfull[np.ix_(non_idx,non_idx)])
print(f'\nSubmatrix λ2 localization:')
print(f'  full-49 λ2 = {lam2_full:.4f}')
print(f'  AXM-block-only (32x32) λ2 = {lam2_axm:.4f}')
print(f'  non-AXM (17x17) λ2 = {lam2_non:.4f}')

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
print(f'\n5-gram: {len(counts5)} contexts. Running {N_SYNTH} synth (per-synth-own-shuffle)...')

prng=random.Random(42); nprng=np.random.RandomState(42)
synth_axm_exc=[]; synth_qo_exc=[]; synth_axm_lam2=[]
for s in range(N_SYNTH):
    synth=[samp(counts5,ORDER,len(wl),nprng) for wl in word_lines]
    e_axm,_,_=shuffle_excess(synth, axm_self_rate, N_SHUF, prng)
    e_qo,_,_=shuffle_excess(synth, qo_chsh_rate, N_SHUF, prng)
    synth_axm_exc.append(e_axm); synth_qo_exc.append(e_qo)
    synth_axm_lam2.append(lam2_of(build_matrix(synth)[np.ix_(axm_idx,axm_idx)]))
    if (s+1)%50==0:
        print(f'  [{s+1}/{N_SYNTH}] AXM synth_exc mean={np.mean(synth_axm_exc):+.4f}')
        RESULTS.write_text(json.dumps({'real_axm_excess':real_axm_exc,'progress':s+1},indent=2))

def verdict(real_exc, synth_excs, label):
    se=np.array(synth_excs); m=se.mean(); sd=se.std()
    z=(real_exc-m)/sd if sd>0 else float('inf')
    p=float((se>=real_exc).mean())
    print(f'  [{label}] real_exc={real_exc:+.4f} synth_exc={m:+.4f}±{sd:.4f} z={z:+.2f} p_emp={p:.4f}')
    return {'real_excess':real_exc,'synth_mean':float(m),'synth_sd':float(sd),'z':float(z),'p_emp':p}

print(f'\n=== RESULTS ===')
print(f'GATE-ZERO (qo->ch/sh, should survive like C549):')
gz=verdict(real_qo_exc, synth_qo_exc, 'qo->chsh')
print(f'PRIMARY (AXM self-transition above-composition):')
ax=verdict(real_axm_exc, synth_axm_exc, 'AXM-self')
print(f'\nCOMPANION λ2 localization: full {lam2_full:.4f}, AXM-block {lam2_axm:.4f}, non-AXM {lam2_non:.4f}')
print(f'  5-gram AXM-block λ2: mean {np.mean(synth_axm_lam2):.4f} (real AXM-block {lam2_axm:.4f})')

print(f'\n=== VERDICT ===')
gate_ok = gz['p_emp'] < 0.10
print(f'  Gate-zero (qo->chsh survives): {"PASS" if gate_ok else "FAIL — pipeline suspect"}')
if not gate_ok:
    print('  GATE-ZERO FAILED — the 5-gram pipeline does not reproduce the known C549 survival. Result suspect.')
if ax['p_emp'] < 0.05:
    print(f'  AXM self-cohesion is ABOVE-Markov (p={ax["p_emp"]:.4f}) -> attractor is designed structure, NOT')
    print(f'  composition artifact. Sharpens C978 0.698 measured->above-composition. Macro-automaton vindicated.')
    v='AXM_ABOVE_COMPOSITION'
else:
    print(f'  AXM self-cohesion is COMPOSITION/Markov-reproducible (p={ax["p_emp"]:.4f}) -> the attractor self-loop')
    print(f'  is "big bucket self-transitions because it is big" + char-stats, NOT designed cohesion.')
    print(f'  SCOPE-CORRECTION on the macro-automaton interpretation.')
    v='AXM_COMPOSITION_ARTIFACT'

RESULTS.write_text(json.dumps({
    'gate_zero_qochsh':gz,'gate_ok':bool(gate_ok),
    'primary_axm_self':ax,
    'real_axm_self_rate':real_axm,'real_axm_shuffle':real_axm_shuf,
    'lam2_full':lam2_full,'lam2_axm_block':lam2_axm,'lam2_non_axm':lam2_non,
    'lam2_axm_block_5gram_mean':float(np.mean(synth_axm_lam2)),
    'verdict':v,'n_synth':N_SYNTH},indent=2))
print(f'\nWritten to {RESULTS}')
