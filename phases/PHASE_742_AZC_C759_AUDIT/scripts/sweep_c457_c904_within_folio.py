"""PHASE 742 sweep - exposed-class audit: C457 (HT S>R) + C904 (-ry S-zone) under within-folio nulls.

Both pin a feature to a cross-folio placement letter, pooled, NO within-folio control (same class as
C759). Test: does the feature<->position association survive a within-folio position-label permutation?

C457: HT tokens prefer S over R in Zodiac AZC (chi2=32.57, p<1e-4, V=0.105, S=39.7% > R=29.5%, N=2952).
  HT classification replicated EXACTLY from phases/exploration/ht_azc_placement_test.py (prefix heuristic).
C904: -ry suffix 3.18x enriched in S-zones (19/39 -ry in S, 48.7% vs 15.3% baseline). Tiny N -> fragile.

NULL: within each folio permute the position-family label (no replacement), feature fixed; recompute the
  statistic; one-sided survive iff stat_obs > 95th pct; exact p, B=10000, seed=0.
"""
import sys, json, csv, functools
from collections import defaultdict
from pathlib import Path
import numpy as np
print = functools.partial(print, flush=True)
sys.path.insert(0, '.')
from scripts.voynich import Morphology

OUT = Path('phases/PHASE_742_AZC_C759_AUDIT/results'); OUT.mkdir(parents=True, exist_ok=True)
TX = 'data/transcriptions/interlinear_full_words.txt'
morph = Morphology()

# ---- HT classifier (verbatim from C457 original script) ----
HT_PRE = {'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc'}
B_PRE  = {'ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol'}
b_vocab = set()
try:
    g = json.load(open('results/canonical_grammar.json'))
    b_vocab = {t['symbol'] for t in g.get('terminals', {}).get('list', []) if 'symbol' in t}
except Exception:
    pass
def is_ht(tok):
    if '*' in tok or '?' in tok: return None
    for p in sorted(HT_PRE, key=len, reverse=True):
        if tok.startswith(p): return True
    for p in sorted(B_PRE, key=len, reverse=True):
        if tok.startswith(p): return False
    if tok in b_vocab: return False
    return True   # default -> HT (residue definition)

# ---- load AZC tokens with section + placement ----
zfeat = json.load(open('results/azc_folio_features.json')).get('folios', {})
ZODIAC = {f for f, d in zfeat.items() if d.get('section') == 'Z'}
rows = []
with open(TX, encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t', quotechar='"'):
        if r.get('transcriber', '').strip() != 'H': continue
        if r.get('language', '').strip() != 'NA': continue
        w = r.get('word', '').strip()
        pl = r.get('placement', '').strip()
        if not w or not pl: continue
        rows.append({'folio': r.get('folio', '').strip(), 'word': w, 'pl': pl})
print(f"Zodiac folios: {len(ZODIAC)}  | AZC H-track tokens loaded: {len(rows)}")

def fam(pl): return pl[0] if pl and pl[0] in ('R', 'S', 'C') else 'OTHER'

def within_folio_p(items, stat_fn, B=10000, seed=0):
    """items: list of (folio, label, feature). Permute LABEL within folio, feature fixed."""
    by_f = defaultdict(lambda: {'lab': [], 'feat': []})
    for fol, lab, feat in items:
        by_f[fol]['lab'].append(lab); by_f[fol]['feat'].append(feat)
    flab = {f: np.array(d['lab'], dtype=object) for f, d in by_f.items()}
    ffeat = {f: d['feat'] for f, d in by_f.items()}
    obs = stat_fn([i[1] for i in items], [i[2] for i in items])
    rng = np.random.default_rng(seed); ge = 0; vals = np.empty(B)
    for b in range(B):
        L, F = [], []
        for f in by_f:
            a = flab[f]
            L.extend((rng.permutation(a) if len(a) > 1 else a).tolist()); F.extend(ffeat[f])
        v = stat_fn(L, F); vals[b] = v
        if v >= obs: ge += 1
    return obs, (ge + 1) / (B + 1), float(np.percentile(vals, 95)), float(vals.mean())

def cramers_v_2x2(labels, feats, A, Bc):
    """V for (label in {A,Bc}) x (feature bool)."""
    t = np.zeros((2, 2))
    for lab, fe in zip(labels, feats):
        if lab == A: t[0, int(fe)] += 1
        elif lab == Bc: t[1, int(fe)] += 1
    n = t.sum()
    if n == 0 or t.sum(0).min() == 0 or t.sum(1).min() == 0: return 0.0
    rs = t.sum(1, keepdims=True); cs = t.sum(0, keepdims=True); exp = rs @ cs / n
    chi2 = float(np.nansum((t - exp) ** 2 / exp))
    return float(np.sqrt(chi2 / n))

# ================= C457: HT x (R vs S), Zodiac only =================
print("\n" + "=" * 60 + "\nC457: HT preference S vs R (Zodiac AZC)")
c457 = []
for r in rows:
    if r['folio'] not in ZODIAC: continue
    fm = fam(r['pl'])
    if fm not in ('R', 'S'): continue
    ht = is_ht(r['word'])
    if ht is None: continue
    c457.append((r['folio'], fm, ht))
# reproduce pooled rates
rt = sum(1 for _, f, h in c457 if f == 'R' and h); rn = sum(1 for _, f, h in c457 if f == 'R')
st = sum(1 for _, f, h in c457 if f == 'S' and h); sn = sum(1 for _, f, h in c457 if f == 'S')
print(f"  pooled: R HT={rt}/{rn} ({rt/rn:.1%})  S HT={st}/{sn} ({st/sn:.1%})  (C457: R 29.5%, S 39.7%)")
stat457 = lambda L, F: cramers_v_2x2(L, F, 'R', 'S')
v457, p457, p95_457, nullm457 = within_folio_p(c457, stat457)
# per-folio: how many folios have S HT-rate > R HT-rate
pf = defaultdict(lambda: {'R': [0, 0], 'S': [0, 0]})
for fol, fm, h in c457:
    pf[fol][fm][0] += int(h); pf[fol][fm][1] += 1
pf_dir = {f: (d['S'][0]/d['S'][1] if d['S'][1] else None, d['R'][0]/d['R'][1] if d['R'][1] else None)
          for f, d in pf.items() if d['S'][1] >= 5 and d['R'][1] >= 5}
n_SgtR = sum(1 for s, r in pf_dir.values() if s > r)
print(f"  V_obs={v457:.4f}  within-folio null mean={nullm457:.4f} 95th={p95_457:.4f}  p={p457:.4f}  "
      f"-> {'SURVIVE' if v457 > p95_457 else 'DEMOTE (folio-shadow)'}")
print(f"  per-folio (>=5 R & >=5 S): {n_SgtR}/{len(pf_dir)} folios have S HT-rate > R HT-rate")

# ================= C904: -ry x (S vs non-S), all AZC =================
print("\n" + "=" * 60 + "\nC904: -ry enrichment in S-zone (all AZC)")
c904 = []
for r in rows:
    fm = fam(r['pl'])
    lab = 'S' if fm == 'S' else 'nonS'
    ry = morph.extract(r['word']).suffix == 'ry'
    c904.append((r['folio'], lab, ry))
nry = sum(1 for _, _, y in c904 if y); nry_s = sum(1 for _, l, y in c904 if y and l == 'S')
print(f"  -ry tokens={nry}  in S={nry_s} ({nry_s/nry:.1%})  baseline S rate="
      f"{sum(1 for _,l,_ in c904 if l=='S')/len(c904):.1%}  (C904: 48.7% vs 15.3%)")
# statistic: fraction of -ry tokens that land in S (so permuting position labels within folio tests
#   whether -ry lands in S more than the folio's own position mix predicts)
def ry_in_s_frac(L, F):
    tot = sum(1 for fe in F if fe); s = sum(1 for l, fe in zip(L, F) if fe and l == 'S')
    return s / tot if tot else 0.0
v904, p904, p95_904, nullm904 = within_folio_p(c904, ry_in_s_frac)
print(f"  obs -ry-in-S frac={v904:.4f}  within-folio null mean={nullm904:.4f} 95th={p95_904:.4f}  p={p904:.4f}  "
      f"-> {'SURVIVE' if v904 > p95_904 else 'DEMOTE (folio-shadow)'}  [N_-ry={nry}, fragile]")

res = {
  'phase': 'PHASE_742 sweep', 'null': 'within-folio position-label permutation, feature fixed; one-sided',
  'B': 10000, 'seed': 0,
  'C457': {'R_ht': [rt, rn], 'S_ht': [st, sn], 'V_obs': round(v457, 4), 'null_mean': round(nullm457, 4),
           'null_p95': round(p95_457, 4), 'p_one_sided': round(p457, 4),
           'verdict': 'SURVIVE' if v457 > p95_457 else 'DEMOTE_folio_shadow',
           'per_folio_S_gt_R': f"{n_SgtR}/{len(pf_dir)}"},
  'C904': {'n_ry': nry, 'ry_in_S': nry_s, 'obs_frac': round(v904, 4), 'null_mean': round(nullm904, 4),
           'null_p95': round(p95_904, 4), 'p_one_sided': round(p904, 4),
           'verdict': 'SURVIVE' if v904 > p95_904 else 'DEMOTE_folio_shadow', 'note': 'tiny N, fragile'},
}
(OUT / 'sweep_c457_c904.json').write_text(json.dumps(res, indent=2))
print(f"\nSaved {OUT / 'sweep_c457_c904.json'}")
