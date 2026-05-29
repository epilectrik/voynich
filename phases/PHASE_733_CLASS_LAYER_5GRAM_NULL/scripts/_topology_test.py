"""CASCADE-RESOLVING TEST: does the 5-gram reproduce the 6-STATE TOPOLOGY (C976),
not just the scalar first-order class MI (C2023, which it does reproduce)?

C2023 (first-order class MI) FAILED the 5-gram null (per-synth excess +0.042 vs real +0.0485,
p=0.21) — the class-transition MI is morphology-derivable. The open question: does that
cascade to the C976 macro-automaton (49->6 compression, holdout-ARI 0.939, spectral gap 0.894)?

Both experts: first-order MI reproducibility does NOT entail topology reproducibility.
Topology is a global/second-order property. Run the discriminating test.

METHOD: exactly the C976 holdout loop (t9), but feed 5-gram-SYNTHETIC corpora instead of
held-out folio subsets. For each synth corpus: project tokens->classes (same map), build
49x49 transition matrix, run the SAME constraint-preserving merge, compute ARI vs the
canonical 6-state partition + record n_states.

REFERENCE BASELINES:
- Real corpus merge -> should reproduce canonical (ARI ~ 1.0, 6 states). Sanity.
- Holdout baseline (C976 t9): real subsets give mean ARI 0.939, 100% 6 states.

PRE-REGISTERED VERDICT (locked):
- 5-gram synth mean ARI vs canonical >= 0.70 AND modal n_states == 6
    -> TOPOLOGY IS MORPHOLOGY-REPRODUCIBLE. Macro-automaton (C976-C978) cascades from C2023.
       BIG demotion.
- 5-gram synth mean ARI < 0.50 OR modal n_states != 6
    -> TOPOLOGY IS ABOVE-MARKOV. Macro-automaton SURVIVES, vindicated by a sharper null
       than it has ever passed. Cascade STOPS at C2023.
- 0.50 <= ARI < 0.70 -> PARTIAL; report and reconsider.

Expert-advisor pre-registered prediction: SURVIVAL (topology not entailed by first-order MI).
flush + interim JSON.
"""
import sys, json, functools, random
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import adjusted_rand_score

print = functools.partial(print, flush=True)
PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript

MSA = PROJECT_ROOT / 'phases/MINIMAL_STATE_AUTOMATON'
RESULTS = PROJECT_ROOT / 'phases/PHASE_733_CLASS_LAYER_5GRAM_NULL/results/topology_test.json'
N_SYNTH = 50
ORDER = 5

# ===== merge machinery (copied verbatim from t9_holdout_stability.py) =====
DEPLETED_PAIRS = [
    (11,36),(13,40),(9,33),(24,30),(14,46),(9,27),(9,32),(5,34),(47,11),
    (19,33),(7,32),(11,14),(3,33),(33,38),(18,28),(7,47),(13,5),(10,28),
]
CC_CLASSES={10,11,12}; FQ_CLASSES={9,13,14,23}; FL_HAZ={7,30}; FL_SAFE={38,40}
def get_role(c):
    if c in CC_CLASSES: return 'CC'
    if c in FQ_CLASSES: return 'FQ'
    if c in FL_HAZ: return 'FL_HAZ'
    if c in FL_SAFE: return 'FL_SAFE'
    en_set=({8}|set(range(31,50)))-{7,30,38,40}
    if c in en_set: return 'EN'
    return 'AX'
def check_role_integrity(partition):
    for group in partition:
        roles=set(get_role(c) for c in group)
        if 'CC' in roles and len(roles)>1: return False
        if 'FQ' in roles and len(roles)>1: return False
        if 'FL_HAZ' in roles and 'FL_SAFE' in roles: return False
        if ('FL_HAZ' in roles or 'FL_SAFE' in roles):
            if roles-{'FL_HAZ','FL_SAFE'}: return False
    return True
def check_depletion(partition, counts, all_classes):
    cls_to_idx={c:i for i,c in enumerate(all_classes)}
    cls_to_part={}
    for pi,group in enumerate(partition):
        for c in group: cls_to_part[c]=pi
    for src,tgt in DEPLETED_PAIRS:
        if src in cls_to_part and tgt in cls_to_part and cls_to_part[src]==cls_to_part[tgt]:
            return False
    n_p=len(partition)
    merged=np.zeros((n_p,n_p))
    for i,gi in enumerate(partition):
        for j,gj in enumerate(partition):
            for ci in gi:
                for cj in gj:
                    merged[i][j]+=counts[cls_to_idx[ci]][cls_to_idx[cj]]
    row=merged.sum(axis=1); col=merged.sum(axis=0); tot=merged.sum()
    md=set()
    for src,tgt in DEPLETED_PAIRS:
        if src in cls_to_part and tgt in cls_to_part:
            md.add((cls_to_part[src],cls_to_part[tgt]))
    for ps,pt in md:
        rev_exp=row[pt]*col[ps]/tot if tot>0 else 0
        if rev_exp>=5 and merged[pt][ps]/rev_exp<0.2: return False
    return True
def check_constraints(p,c,a): return check_role_integrity(p) and check_depletion(p,c,a)
def run_merge(counts, probs, all_classes):
    n=len(all_classes); cls_to_idx={c:i for i,c in enumerate(all_classes)}
    partition=[set([c]) for c in all_classes]
    consecutive_rejects=0
    while len(partition)>2 and consecutive_rejects<200:
        n_p=len(partition); profiles=[]
        for group in partition:
            total_out=0; profile=np.zeros(n)
            for c in group:
                idx=cls_to_idx[c]; rs=probs[idx].sum()
                profile+=probs[idx]*rs; total_out+=rs
            profiles.append(profile/total_out if total_out>0 else np.ones(n)/n)
        cands=[]
        for i in range(n_p):
            for j in range(i+1,n_p):
                jsd=jensenshannon(profiles[i],profiles[j])
                cands.append((1.0 if np.isnan(jsd) else jsd,i,j))
        cands.sort()
        merged=False
        for dist,i,j in cands:
            np_part=[p for k,p in enumerate(partition) if k!=i and k!=j]
            np_part.append(partition[i]|partition[j])
            if check_constraints(np_part,counts,all_classes):
                partition=np_part; consecutive_rejects=0; merged=True; break
            else: consecutive_rejects+=1
        if not merged: break
    return [sorted(g) for g in partition]
def part_labels(partition, all_classes):
    lab={}
    for si,g in enumerate(partition):
        for c in g: lab[c]=si
    return [lab.get(c,-1) for c in all_classes]

# ===== load canonical + class map =====
t3=json.load(open(MSA/'results/t3_merged_automaton.json'))
canonical=t3['final_partition']; canonical_n=t3['n_final_states']
all_classes=list(range(1,50)); cls_to_idx={c:i for i,c in enumerate(all_classes)}; n_cls=49
canon_labels=part_labels([set(g) for g in canonical], all_classes)
print(f'Canonical: {canonical_n} states, sizes {sorted(len(g) for g in canonical)}')

ctm=json.load(open(PROJECT_ROOT/'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))
ttc={t:int(c) for t,c in ctm['token_to_class'].items()}

# ===== build real corpus lines (currier_b, class-projected) =====
tx=Transcript()
lines_dict=defaultdict(list)
for tok in tx.currier_b():
    w=tok.word.strip()
    if not w or '*' in w: continue
    lines_dict[(tok.folio,tok.line)].append(w)
word_lines=[lines_dict[k] for k in sorted(lines_dict.keys())]

def matrix_from_classlines(class_lines):
    counts=np.zeros((n_cls,n_cls))
    for line in class_lines:
        seq=[c for c in line if c is not None]
        for a,b in zip(seq,seq[1:]):
            counts[cls_to_idx[a]][cls_to_idx[b]]+=1
    rs=counts.sum(axis=1,keepdims=True)
    probs=np.divide(counts,rs,where=rs>0,out=np.zeros_like(counts))
    return counts,probs

# REAL sanity
real_cl=[[ttc.get(w) for w in wl] for wl in word_lines]
rc,rp=matrix_from_classlines(real_cl)
real_part=run_merge(rc,rp,all_classes)
real_ari=adjusted_rand_score(canon_labels, part_labels(real_part,all_classes))
print(f'\nREAL corpus merge: {len(real_part)} states, ARI vs canonical = {real_ari:.3f}  (sanity, expect ~6 / ~1.0)')

# ===== 5-gram =====
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
counts5=train(word_lines,ORDER)

print(f'\n=== 5-gram topology null ({N_SYNTH} synth corpora) ===')
rng=random.Random(42)
aris=[]; nstates=[]
interim={'canonical_n':canonical_n,'real_sanity_ari':real_ari,'real_sanity_nstates':len(real_part),
         'holdout_baseline_ari':0.939,'n_synth':N_SYNTH,'aris':[],'nstates':[]}
for s in range(N_SYNTH):
    sl=[samp(counts5,ORDER,len(wl),rng) for wl in word_lines]
    scl=[[ttc.get(w) for w in wl] for wl in sl]
    sc,sp=matrix_from_classlines(scl)
    spart=run_merge(sc,sp,all_classes)
    ari=adjusted_rand_score(canon_labels, part_labels(spart,all_classes))
    aris.append(ari); nstates.append(len(spart))
    interim['aris'].append(ari); interim['nstates'].append(len(spart))
    if (s+1)%10==0:
        print(f'  [{s+1}/{N_SYNTH}] mean ARI={np.mean(aris):.3f}, modal nstates={max(set(nstates),key=nstates.count)}')
        RESULTS.write_text(json.dumps(interim,indent=2))

mean_ari=float(np.mean(aris)); sd_ari=float(np.std(aris))
modal_n=max(set(nstates),key=nstates.count)
from collections import Counter as C
nstate_dist=dict(C(nstates))
print(f'\n=== TOPOLOGY TEST RESULT ===')
print(f'  Real sanity: {len(real_part)} states, ARI {real_ari:.3f}')
print(f'  Holdout baseline (C976): mean ARI 0.939, 100% 6 states')
print(f'  5-gram synth: mean ARI {mean_ari:.3f} +/- {sd_ari:.3f}, modal nstates {modal_n}')
print(f'  5-gram nstate distribution: {nstate_dist}')

print(f'\n=== VERDICT ===')
if mean_ari >= 0.70 and modal_n == 6:
    verdict='MORPHOLOGY_REPRODUCIBLE_CASCADE'
    print('  TOPOLOGY IS MORPHOLOGY-REPRODUCIBLE. Macro-automaton cascades from C2023. BIG demotion.')
elif mean_ari < 0.50 or modal_n != 6:
    verdict='ABOVE_MARKOV_SURVIVES'
    print('  TOPOLOGY IS ABOVE-MARKOV. Macro-automaton (C976-C978) SURVIVES — vindicated by a')
    print('  sharper null than it has ever passed. Cascade STOPS at C2023.')
else:
    verdict='PARTIAL'
    print(f'  PARTIAL (ARI {mean_ari:.3f}). Reconsider.')

interim.update({'mean_ari':mean_ari,'sd_ari':sd_ari,'modal_nstates':modal_n,
                'nstate_distribution':nstate_dist,'verdict':verdict,'status':'complete'})
RESULTS.write_text(json.dumps(interim,indent=2))
print(f'\nWritten to {RESULTS}')
