"""Falsification test (crazy-expert Q3) for the 'distributed λ2 → explains C1010' story.

Compute the SECOND eigenvector of the full-49 class transition operator. Examine its
LOADING: is it concentrated on a few AXM classes (within-AXM gradient → 'distributed' is
FALSE, eigenstructure is attractor-internal, would predict HIGH spectral ARI, contradicts
C1010, story COLLAPSES) or spread across both AXM and non-AXM blocks with no block-boundary
alignment (story SURVIVES as a measurement)?

Metric: |loading| mass on AXM classes vs non-AXM classes, and concentration (participation
ratio / top-k share). If the 2nd eigenvector loads heavily on a handful of classes within one
block → concentrated. If spread → distributed.
"""
import sys, json, functools
import numpy as np
from collections import defaultdict
from pathlib import Path
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
print = functools.partial(print, flush=True)
PROJECT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript

AXM = {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49}
ac = list(range(1,50)); c2i = {c:i for i,c in enumerate(ac)}; n_cls = 49
ttc = {t:int(c) for t,c in json.load(open(PROJECT/'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))['token_to_class'].items()}
tx = Transcript(); ld = defaultdict(list)
for tok in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines = [ld[k] for k in sorted(ld.keys())]

C = np.zeros((n_cls,n_cls))
for l in word_lines:
    cls=[ttc.get(w) for w in l]
    for i in range(len(cls)-1):
        a,b=cls[i],cls[i+1]
        if a is not None and b is not None: C[c2i[a]][c2i[b]]+=1
rs=C.sum(1,keepdims=True); P=np.divide(C,rs,where=rs>0,out=np.zeros_like(C))

# right eigenvectors; sort by |eigenvalue|
vals, vecs = np.linalg.eig(P)
order = np.argsort(np.abs(vals))[::-1]
lam2 = abs(vals[order[1]])
v2 = np.abs(np.real(vecs[:, order[1]]))
v2 = v2 / v2.sum() if v2.sum() > 0 else v2  # normalize to loading distribution

axm_idx = [c2i[c] for c in AXM]; non_idx = [c2i[c] for c in ac if c not in AXM]
axm_load = v2[axm_idx].sum(); non_load = v2[non_idx].sum()
# AXM is 32/49 classes = 65% of classes; if loading ~proportional, axm_load~0.65
axm_class_frac = len(AXM)/n_cls

# concentration: participation ratio (1/sum(p^2)); top-5 share
pr = 1.0/np.sum(v2**2) if np.sum(v2**2)>0 else 0
top5 = np.sort(v2)[::-1][:5].sum()
# which classes carry the loading
load_by_class = sorted([(ac[i], v2[i]) for i in range(n_cls)], key=lambda x:-x[1])[:8]

print(f'lambda2 = {lam2:.4f}')
print(f'2nd-eigenvector loading: AXM-block {axm_load:.3f} vs non-AXM {non_load:.3f} (AXM is {axm_class_frac:.2f} of classes)')
print(f'Participation ratio: {pr:.1f} of {n_cls} classes (high = spread, low = concentrated)')
print(f'Top-5 classes carry {top5:.3f} of the loading')
print(f'Top-8 loading classes (class, |loading|):')
for c,l in load_by_class:
    blk = 'AXM' if c in AXM else 'lane'
    print(f'  class {c:>2} ({blk}): {l:.4f}')

# verdict
print(f'\n=== VERDICT ===')
spread = pr > 10 and top5 < 0.6
boundary_aligned = abs(axm_load - axm_class_frac) > 0.25  # loading concentrated in one block beyond class-proportion
if spread and not boundary_aligned:
    print('  SPREAD across classes, not block-boundary-aligned -> "distributed" SURVIVES.')
    print('  Consistent with C1010 non-spectral partition (slow mode is not a block phenomenon).')
    verdict='DISTRIBUTED_SURVIVES'
elif not spread:
    print('  CONCENTRATED on few classes -> "distributed" is FALSE. C1010 story COLLAPSES.')
    print('  The slow mode is a within-block gradient; eigenstructure is localized.')
    verdict='CONCENTRATED_STORY_COLLAPSES'
else:
    print('  Block-boundary-aligned -> eigenstructure tracks the AXM/non-AXM split; ambiguous for C1010.')
    verdict='BOUNDARY_ALIGNED'
print(f'  verdict: {verdict}')

Path(PROJECT/'phases/PHASE_736_AXM_ATTRACTOR_COMPOSITION/results/eigenvector_loading.json').write_text(json.dumps({
    'lambda2':float(lam2),'axm_block_loading':float(axm_load),'non_axm_loading':float(non_load),
    'axm_class_fraction':float(axm_class_frac),'participation_ratio':float(pr),'top5_share':float(top5),
    'top8_classes':[(int(c),float(l)) for c,l in load_by_class],'verdict':verdict},indent=2))
print('\nWritten.')
