"""FLOOR CONTROL for the topology test.

The topology test gave 5-gram synth ARI=0.762 vs canonical (vs real baseline 0.937).
The script called that "morphology-reproducible." BUT run_merge has hardcoded
role-integrity + depleted-pair constraints that force much of the 6-state structure
regardless of transition data. So 0.762 may be the constraint FLOOR, not data reproduction.

DISCRIMINATING CONTROL: feed run_merge transition matrices with NO sequential structure
but matched composition, and see what ARI they yield:
  (a) WITHIN-LINE SHUFFLE of real classes (composition preserved, order destroyed)
  (b) UNIFORM-RANDOM transition matrix (absolute floor; only role constraints bind)

INTERPRETATION:
- If shuffle ARI ~= 5-gram ARI (0.76) -> the partition is role-constraint-dominated;
  the topology test CANNOT discriminate. C976 neither vindicated nor demoted by this test.
- If shuffle ARI << 5-gram ARI (0.76) ~= real (0.94) -> 5-gram reproduces data topology
  -> morphology-shadow -> cascade (demote C976).
- If 5-gram (0.76) sits between shuffle floor and real (0.94) -> PARTIAL; the topology is
  partly data-driven (survives partially) and partly morphology-reproducible.

flush + JSON.
"""
import sys, json, functools, random
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import adjusted_rand_score

print = functools.partial(print, flush=True)
PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript

MSA = PROJECT_ROOT/'phases/MINIMAL_STATE_AUTOMATON'
RESULTS = PROJECT_ROOT/'phases/PHASE_733_CLASS_LAYER_5GRAM_NULL/results/topology_floor_control.json'
N_SHUFFLE = 30
N_RANDOM = 15

# merge machinery (verbatim)
DEPLETED_PAIRS=[(11,36),(13,40),(9,33),(24,30),(14,46),(9,27),(9,32),(5,34),(47,11),(19,33),(7,32),(11,14),(3,33),(33,38),(18,28),(7,47),(13,5),(10,28)]
CC_CLASSES={10,11,12};FQ_CLASSES={9,13,14,23};FL_HAZ={7,30};FL_SAFE={38,40}
def get_role(c):
    if c in CC_CLASSES:return'CC'
    if c in FQ_CLASSES:return'FQ'
    if c in FL_HAZ:return'FL_HAZ'
    if c in FL_SAFE:return'FL_SAFE'
    if c in ({8}|set(range(31,50)))-{7,30,38,40}:return'EN'
    return'AX'
def cri(p):
    for g in p:
        r=set(get_role(c) for c in g)
        if 'CC' in r and len(r)>1:return False
        if 'FQ' in r and len(r)>1:return False
        if 'FL_HAZ' in r and 'FL_SAFE' in r:return False
        if ('FL_HAZ' in r or 'FL_SAFE' in r) and (r-{'FL_HAZ','FL_SAFE'}):return False
    return True
def cdep(p,counts,ac):
    c2i={c:i for i,c in enumerate(ac)};c2p={}
    for pi,g in enumerate(p):
        for c in g:c2p[c]=pi
    for s,t in DEPLETED_PAIRS:
        if s in c2p and t in c2p and c2p[s]==c2p[t]:return False
    n_p=len(p);m=np.zeros((n_p,n_p))
    for i,gi in enumerate(p):
        for j,gj in enumerate(p):
            for ci in gi:
                for cj in gj:m[i][j]+=counts[c2i[ci]][c2i[cj]]
    row=m.sum(1);col=m.sum(0);tot=m.sum();md=set()
    for s,t in DEPLETED_PAIRS:
        if s in c2p and t in c2p:md.add((c2p[s],c2p[t]))
    for ps,pt in md:
        re=row[pt]*col[ps]/tot if tot>0 else 0
        if re>=5 and m[pt][ps]/re<0.2:return False
    return True
def run_merge(counts,probs,ac):
    n=len(ac);c2i={c:i for i,c in enumerate(ac)};part=[set([c]) for c in ac];cr=0
    while len(part)>2 and cr<200:
        n_p=len(part);profs=[]
        for g in part:
            to=0;pr=np.zeros(n)
            for c in g:
                idx=c2i[c];rs=probs[idx].sum();pr+=probs[idx]*rs;to+=rs
            profs.append(pr/to if to>0 else np.ones(n)/n)
        cands=[]
        for i in range(n_p):
            for j in range(i+1,n_p):
                d=jensenshannon(profs[i],profs[j]);cands.append((1.0 if np.isnan(d) else d,i,j))
        cands.sort();merged=False
        for d,i,j in cands:
            npart=[p for k,p in enumerate(part) if k!=i and k!=j];npart.append(part[i]|part[j])
            if cri(npart) and cdep(npart,counts,ac):part=npart;cr=0;merged=True;break
            else:cr+=1
        if not merged:break
    return [sorted(g) for g in part]
def plabels(p,ac):
    l={}
    for si,g in enumerate(p):
        for c in g:l[c]=si
    return [l.get(c,-1) for c in ac]

t3=json.load(open(MSA/'results/t3_merged_automaton.json'))
canonical=t3['final_partition']
ac=list(range(1,50));c2i={c:i for i,c in enumerate(ac)};n_cls=49
canon_labels=plabels([set(g) for g in canonical],ac)
ctm=json.load(open(PROJECT_ROOT/'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))
ttc={t:int(c) for t,c in ctm['token_to_class'].items()}

tx=Transcript();ld=defaultdict(list)
for tok in tx.currier_b():
    w=tok.word.strip()
    if not w or '*' in w:continue
    ld[(tok.folio,tok.line)].append(w)
word_lines=[ld[k] for k in sorted(ld.keys())]
# real classified per-line sequences
real_seqs=[[ttc.get(w) for w in wl] for wl in word_lines]
real_seqs=[[c for c in line if c is not None] for line in real_seqs]

def matrix(class_lines):
    counts=np.zeros((n_cls,n_cls))
    for line in class_lines:
        for a,b in zip(line,line[1:]):counts[c2i[a]][c2i[b]]+=1
    rs=counts.sum(1,keepdims=True)
    return counts,np.divide(counts,rs,where=rs>0,out=np.zeros_like(counts))

# (a) SHUFFLE floor
print(f'=== SHUFFLE floor ({N_SHUFFLE} within-line shuffles through run_merge) ===')
rng=random.Random(7);sh_aris=[];sh_n=[]
for s in range(N_SHUFFLE):
    shuffled=[]
    for seq in real_seqs:
        ss=seq[:];rng.shuffle(ss);shuffled.append(ss)
    c,p=matrix(shuffled);part=run_merge(c,p,ac)
    sh_aris.append(adjusted_rand_score(canon_labels,plabels(part,ac)));sh_n.append(len(part))
    if (s+1)%10==0:print(f'  [{s+1}/{N_SHUFFLE}] mean ARI={np.mean(sh_aris):.3f}, modal n={max(set(sh_n),key=sh_n.count)}')
sh_mean=float(np.mean(sh_aris));sh_sd=float(np.std(sh_aris))

# (b) UNIFORM-RANDOM floor (random transition matrix, only role constraints bind)
print(f'\n=== UNIFORM-RANDOM floor ({N_RANDOM} random matrices through run_merge) ===')
rr=np.random.default_rng(7);rnd_aris=[];rnd_n=[]
# match total transition count
ntrans=sum(len(s)-1 for s in real_seqs if len(s)>1)
for s in range(N_RANDOM):
    counts=rr.integers(0,3,size=(n_cls,n_cls)).astype(float)  # near-uniform low counts
    rs=counts.sum(1,keepdims=True);probs=np.divide(counts,rs,where=rs>0,out=np.zeros_like(counts))
    part=run_merge(counts,probs,ac)
    rnd_aris.append(adjusted_rand_score(canon_labels,plabels(part,ac)));rnd_n.append(len(part))
rnd_mean=float(np.mean(rnd_aris));rnd_sd=float(np.std(rnd_aris))

print(f'\n=== FLOOR CONTROL RESULT ===')
print(f'  Real / holdout baseline ARI:     ~0.937')
print(f'  5-gram synth ARI (topology test): 0.762')
print(f'  SHUFFLE floor ARI:                {sh_mean:.3f} +/- {sh_sd:.3f}  (modal n={max(set(sh_n),key=sh_n.count)})')
print(f'  UNIFORM-RANDOM floor ARI:         {rnd_mean:.3f} +/- {rnd_sd:.3f}  (modal n={max(set(rnd_n),key=rnd_n.count)})')

print(f'\n=== INTERPRETATION ===')
gap_5gram_to_real = 0.937 - 0.762
gap_shuffle_to_5gram = 0.762 - sh_mean
print(f'  shuffle->5gram gap: {gap_shuffle_to_5gram:+.3f}   5gram->real gap: {gap_5gram_to_real:+.3f}')
if abs(0.762 - sh_mean) < 0.05:
    print('  5-gram ARI ~= shuffle floor -> partition is ROLE-CONSTRAINT-DOMINATED.')
    print('  Topology test CANNOT discriminate. C976 neither vindicated nor demoted by this test.')
    verdict='UNINFORMATIVE_ROLE_CONSTRAINT_DOMINATED'
elif sh_mean < 0.762 - 0.10 and 0.762 > 0.937 - 0.10:
    print('  5-gram reproduces real topology well above shuffle floor -> MORPHOLOGY-SHADOW -> cascade.')
    verdict='MORPHOLOGY_SHADOW_CASCADE'
else:
    print('  5-gram (0.762) sits between shuffle floor and real (0.937) -> PARTIAL.')
    print('  Topology is partly data-driven (above shuffle floor) but the 5-gram reproduces')
    print('  a substantial fraction of it. Macro-automaton partially morphology-derivable.')
    verdict='PARTIAL'

RESULTS.write_text(json.dumps({
    'real_baseline':0.937,'fivegram_ari':0.762,
    'shuffle_floor_mean':sh_mean,'shuffle_floor_sd':sh_sd,
    'random_floor_mean':rnd_mean,'random_floor_sd':rnd_sd,
    'verdict':verdict,
},indent=2))
print(f'\nWritten to {RESULTS}')
