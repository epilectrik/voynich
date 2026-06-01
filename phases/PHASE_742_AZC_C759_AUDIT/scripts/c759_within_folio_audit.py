"""PHASE 742 - C759 audit: position(R/S/C) x PREFIX vocabulary, within-folio null.

C759 (Tier 2): "AZC position determines vocabulary" - chi2=112.59, df=12, p<0.001,
Cramer's V=0.208, POOLED across all AZC folios, NO within-folio control. Position and
folio are confounded (C760: ~70% of AZC MIDDLEs folio-exclusive), so a pooled association
can be pure folio-composition shadow.

NULL (expert-reconciled design, lean-expert + expert-advisor):
  within each folio, PERMUTE the position-label vector (without replacement) among that
  folio's tokens, holding PREFIX fixed. Preserves folio vocab composition AND per-folio
  position counts exactly; destroys only the within-folio position<->prefix link.
  ONE-SIDED: survive iff V_obs > 95th pct. p = (#{V_perm >= V_obs}+1)/(B+1). B=10000, seed=0.
DIAGNOSTIC (lean): per-folio V distribution + mean within-folio null V (the folio-shadow
  floor). If genuine, effect appears WITHIN folios; if Simpson aggregation, ~0 within, large pooled.
Binning: top-6 PREFIX by freq + 'other' = 7 rows x 3 cols -> df=12 (matches C759).
"""
import sys, json, functools
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
print = functools.partial(print, flush=True)
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology

OUT = Path('phases/PHASE_742_AZC_C759_AUDIT/results'); OUT.mkdir(parents=True, exist_ok=True)
tx = Transcript(); morph = Morphology()

# ---- load AZC R/S/C tokens: (folio, pos_class, prefix_bin) ----
rows = []
for t in tx.azc(h_only=True):
    w = t.word.strip()
    if not w or '*' in w:
        continue
    pl = t.placement
    if not pl or pl[0] not in ('R', 'S', 'C'):   # R/S/C only; excludes L,P,W,X,Y,...
        continue
    pre = morph.extract(w).prefix or 'none'
    rows.append((t.folio, pl[0], pre))

pos_n = Counter(r[1] for r in rows)
print(f"N tokens (R/S/C): {len(rows)}  positions: {dict(pos_n)}")

# ---- prefix binning: top-6 + other = 7 categories ----
pre_freq = Counter(r[2] for r in rows)
top6 = [p for p, _ in pre_freq.most_common(6)]
def pbin(p): return p if p in top6 else 'other'
PREFIXES = top6 + ['other']
POSITIONS = ['R', 'S', 'C']
pi = {p: i for i, p in enumerate(PREFIXES)}
ci = {c: i for i, c in enumerate(POSITIONS)}
print(f"top-6 prefixes: {top6}  (+ 'other')")

def cramers_v(table):
    """table: rows=prefix(7) x cols=position(3). V = sqrt(chi2 / (N*(min(r,c)-1)))."""
    t = table.astype(float)
    n = t.sum()
    if n == 0: return 0.0
    rs = t.sum(1, keepdims=True); cs = t.sum(0, keepdims=True)
    exp = rs @ cs / n
    with np.errstate(divide='ignore', invalid='ignore'):
        chi2 = np.nansum(np.where(exp > 0, (t - exp) ** 2 / exp, 0.0))
    k = min(t.shape) - 1
    return float(np.sqrt(chi2 / (n * k))) if k > 0 else 0.0

def build_table(pos_labels, prefixes):
    tbl = np.zeros((len(PREFIXES), len(POSITIONS)))
    for pos, pre in zip(pos_labels, prefixes):
        tbl[pi[pbin(pre)], ci[pos]] += 1
    return tbl

by_folio = defaultdict(lambda: {'pos': [], 'pre': []})
for fol, pos, pre in rows:
    by_folio[fol]['pos'].append(pos); by_folio[fol]['pre'].append(pre)
multi_pos_folios = [f for f in by_folio if len(set(by_folio[f]['pos'])) > 1]
print(f"folios: {len(by_folio)} total, {len(multi_pos_folios)} have >1 position class "
      f"(only these contribute to the within-folio contrast)")

def pooled_within_folio_test(use_rows, B=10000, seed=0):
    """Global Cramer's V vs within-folio position-label permutation null (one-sided)."""
    bf = defaultdict(lambda: {'pos': [], 'pre': []})
    for fol, pos, pre in use_rows:
        bf[fol]['pos'].append(pos); bf[fol]['pre'].append(pre)
    fpos = {f: np.array(d['pos'], dtype=object) for f, d in bf.items()}
    fpre = {f: d['pre'] for f, d in bf.items()}
    V_obs = cramers_v(build_table([r[1] for r in use_rows], [r[2] for r in use_rows]))
    rng = np.random.default_rng(seed); Vp = np.empty(B); ge = 0
    for b in range(B):
        pp, pr = [], []
        for f in bf:
            a = fpos[f]
            pp.extend((rng.permutation(a) if len(a) > 1 else a).tolist()); pr.extend(fpre[f])
        v = cramers_v(build_table(pp, pr)); Vp[b] = v
        if v >= V_obs: ge += 1
    return {'V_obs': round(V_obs, 4), 'null_mean': round(float(Vp.mean()), 4),
            'p95': round(float(np.percentile(Vp, 95)), 4), 'p975': round(float(np.percentile(Vp, 97.5)), 4),
            'p_one_sided': round((ge + 1) / (B + 1), 4),
            'verdict': 'SURVIVE' if V_obs > float(np.percentile(Vp, 95)) else 'DEMOTE_folio_shadow'}

# (1) FULL binning (no-prefix tokens included as 'none' category)
full = pooled_within_folio_test(rows)
print(f"\n[FULL: no-prefix as a category] V_obs={full['V_obs']} null_mean={full['null_mean']} "
      f"95th={full['p95']} | p={full['p_one_sided']} -> {full['verdict']}")

# (2) PREFIXED-ONLY (drop 'none') -- closer to C759's reported 0.208 tabulation
rows_pref = [r for r in rows if r[2] != 'none']
# recompute top6 within prefixed-only so binning is internally consistent
pf6 = [p for p, _ in Counter(r[2] for r in rows_pref).most_common(6)]
PREFIXES = pf6 + ['other']; pi = {p: i for i, p in enumerate(PREFIXES)}
top6 = pf6
prefonly = pooled_within_folio_test(rows_pref)
print(f"[PREFIXED-ONLY: drop no-prefix]  V_obs={prefonly['V_obs']} null_mean={prefonly['null_mean']} "
      f"95th={prefonly['p95']} | p={prefonly['p_one_sided']} -> {prefonly['verdict']}  (C759 reported 0.208)")

# ---- per-folio heterogeneity: each folio vs ITS OWN within-folio null (removes small-N V inflation) ----
# restore full binning for per-folio (uses 'none')
PREFIXES = list(pre_freq.most_common(6)); PREFIXES = [p for p, _ in PREFIXES] + ['other']
pi = {p: i for i, p in enumerate(PREFIXES)}; top6 = PREFIXES[:-1]
rng = np.random.default_rng(1); per_folio = {}; n_sig = 0
for f in by_folio:
    pos = by_folio[f]['pos']; pre = by_folio[f]['pre']
    if len(set(pos)) < 2 or len(pos) < 10:
        continue
    vobs = cramers_v(build_table(pos, pre))
    a = np.array(pos, dtype=object); ge = 0; Bf = 2000
    for _ in range(Bf):
        if cramers_v(build_table(rng.permutation(a).tolist(), pre)) >= vobs: ge += 1
    pf_p = (ge + 1) / (Bf + 1)
    per_folio[f] = {'V': round(vobs, 3), 'p': round(pf_p, 3)}
    if pf_p < 0.05: n_sig += 1
n_tested = len(per_folio)
print(f"\nPER-FOLIO (vs own null, >=10 tok, >1 pos): {n_sig}/{n_tested} folios show position structure at p<0.05")
for f, d in sorted(per_folio.items(), key=lambda x: x[1]['p']):
    print(f"  {f}: V={d['V']} p={d['p']}{'  *' if d['p'] < 0.05 else ''}")

res = {
    'constraint': 'C759', 'phase': 'PHASE_742_AZC_C759_AUDIT',
    'N_tokens': len(rows), 'position_counts': dict(pos_n),
    'null': 'within-folio position-label permutation (no replacement), prefix fixed; one-sided V_obs>95th',
    'B': 10000, 'seed': 0, 'C759_reported_V': 0.208,
    'full_binning': full, 'prefixed_only_binning': prefonly,
    'n_folios_total': len(by_folio), 'n_folios_multi_position': len(multi_pos_folios),
    'per_folio_vs_own_null': per_folio, 'per_folio_n_tested': n_tested, 'per_folio_n_sig_p05': n_sig,
    'headline_verdict': full['verdict'],
}
(OUT / 'c759_within_folio_audit.json').write_text(json.dumps(res, indent=2))
print(f"\nSaved {OUT / 'c759_within_folio_audit.json'}")
