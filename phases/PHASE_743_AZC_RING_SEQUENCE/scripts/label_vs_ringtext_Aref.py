"""PHASE 743 - Does the A-reference live in AZC LABELS or RING-TEXT? (splits C326)

C326 (Tier 2, v1.8 import): AZC folios share "A-references" within clusters (soft, 1.31x). It POOLED all
AZC tokens. We now know labels (S placements / short @Lz loci) and ring-text (R / long @Cc loci) are
different components. Q: do they reference A-vocabulary DIFFERENTLY?

MEASURE (order-independent, death-zone-safe): per AZC token, classify its MIDDLE by membership in the
Currier A vs Currier B MIDDLE inventories -> {A_only, B_only, both, neither}. "References A" = MIDDLE is
in A's inventory (esp. A_only). Compare S (labels) vs R (ring-text), WITHIN zodiac folios where both occur.
NULL = within-folio permutation of the S/R label (preserves folio + per-folio S/R counts), statistic =
Cramer's V of (S vs R) x (A_only vs not), one-sided, B=10000 (same machinery as the C759/C457 audits).
"""
import sys, functools, json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
print = functools.partial(print, flush=True)
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology

OUT = Path('phases/PHASE_743_AZC_RING_SEQUENCE/results'); OUT.mkdir(parents=True, exist_ok=True)
tx = Transcript(); morph = Morphology()
ZF = json.load(open('results/azc_folio_features.json')).get('folios', {})
ZODIAC = {f for f, d in ZF.items() if d.get('section') == 'Z'}

def mids(it):
    s = set()
    for t in it:
        w = (t.word or '').strip()
        if not w or '*' in w: continue
        m = morph.extract(w).middle
        if m: s.add(m)
    return s

A_mid = mids(tx.currier_a()); B_mid = mids(tx.currier_b())
print(f"A MIDDLE inventory: {len(A_mid)}  B MIDDLE inventory: {len(B_mid)}  (shared {len(A_mid & B_mid)})")

def cat(m):
    if m is None: return 'none'
    a, b = m in A_mid, m in B_mid
    return 'both' if (a and b) else ('A_only' if a else ('B_only' if b else 'neither'))

# zodiac AZC tokens, split S(labels) vs R(ring-text)
rows = []   # (folio, group, middle_category)
for t in tx.azc(h_only=True):
    if t.folio not in ZODIAC: continue
    w = (t.word or '').strip()
    if not w or '*' in w: continue
    pl = t.placement
    if not pl: continue
    grp = 'S' if pl[0] == 'S' else ('R' if pl[0] == 'R' else None)
    if grp is None: continue
    rows.append((t.folio, grp, cat(morph.extract(w).middle)))

def dist(group):
    c = Counter(x[2] for x in rows if x[1] == group); n = sum(c.values())
    return n, {k: round(c.get(k, 0) / n, 3) for k in ('A_only', 'B_only', 'both', 'neither')}

nS, dS = dist('S'); nR, dR = dist('R')
print(f"\nLABELS (S, n={nS}):    {dS}")
print(f"RING-TEXT (R, n={nR}): {dR}")
a_share = lambda d: d['A_only'] + d['both']; b_share = lambda d: d['B_only'] + d['both']
print(f"\n  A-share (A_only+both): S={a_share(dS):.3f}  R={a_share(dR):.3f}")
print(f"  B-share (B_only+both): S={b_share(dS):.3f}  R={b_share(dR):.3f}")
print(f"  A_only (A-exclusive):  S={dS['A_only']:.3f}  R={dR['A_only']:.3f}")

# within-folio null: Cramer's V of (group) x (A_only vs not), permute group label within folio
def cramers_v(labels, isA):
    t = np.zeros((2, 2))
    for g, a in zip(labels, isA): t[0 if g == 'S' else 1, int(a)] += 1
    n = t.sum()
    if n == 0 or t.sum(0).min() == 0 or t.sum(1).min() == 0: return 0.0
    rs = t.sum(1, keepdims=True); cs = t.sum(0, keepdims=True); exp = rs @ cs / n
    return float(np.sqrt(float(np.nansum((t - exp) ** 2 / exp)) / n))

byf = defaultdict(lambda: {'g': [], 'a': []})
for fol, grp, c in rows:
    byf[fol]['g'].append(grp); byf[fol]['a'].append(c == 'A_only')
multi = [f for f in byf if len(set(byf[f]['g'])) > 1]
allg = [r[1] for r in rows]; alla = [r[2] == 'A_only' for r in rows]
V_obs = cramers_v(allg, alla)
fg = {f: np.array(byf[f]['g'], dtype=object) for f in byf}; fa = {f: byf[f]['a'] for f in byf}
rng = np.random.default_rng(0); B = 10000; ge = 0; vp = np.empty(B)
for b in range(B):
    L, A = [], []
    for f in byf:
        a = fg[f]; L.extend((rng.permutation(a) if len(a) > 1 else a).tolist()); A.extend(fa[f])
    v = cramers_v(L, A); vp[b] = v
    if v >= V_obs: ge += 1
p = (ge + 1) / (B + 1); p95 = float(np.percentile(vp, 95))
# per-folio direction: A_only rate S vs R
pf = {}
for f in multi:
    gs = byf[f]['g']; as_ = byf[f]['a']
    sA = np.mean([as_[i] for i in range(len(gs)) if gs[i] == 'S']) if any(g == 'S' for g in gs) else None
    rA = np.mean([as_[i] for i in range(len(gs)) if gs[i] == 'R']) if any(g == 'R' for g in gs) else None
    if sA is not None and rA is not None: pf[f] = round(sA - rA, 3)
n_SgtR = sum(1 for d in pf.values() if d > 0)
print(f"\nWITHIN-FOLIO NULL (A_only x S/R, B={B}): V_obs={V_obs:.4f} vs null 95th={p95:.4f}  p={p:.4f}  "
      f"-> {'S/R DIFFER in A-reference' if V_obs > p95 else 'NO S/R difference (A-ref is component-blind)'}")
print(f"  per-folio (folios with both S&R, n={len(pf)}): S A_only-rate > R in {n_SgtR}/{len(pf)} folios")

res = {'phase': 'PHASE_743', 'measure': 'MIDDLE in A/B inventory; labels(S) vs ring-text(R), zodiac, within-folio',
       'A_inv': len(A_mid), 'B_inv': len(B_mid),
       'S': {'n': nS, 'dist': dS, 'A_share': round(a_share(dS), 3)},
       'R': {'n': nR, 'dist': dR, 'A_share': round(a_share(dR), 3)},
       'within_folio': {'V_obs': round(V_obs, 4), 'null_p95': round(p95, 4), 'p_one_sided': round(p, 4),
                        'verdict': 'S_R_DIFFER' if V_obs > p95 else 'NO_DIFFERENCE',
                        'per_folio_S_gt_R': f"{n_SgtR}/{len(pf)}"}}
(OUT / 'label_vs_ringtext_Aref.json').write_text(json.dumps(res, indent=2))
print(f"\nSaved {OUT / 'label_vs_ringtext_Aref.json'}")
