"""PHASE 743 - CORRECTED tests per lean-expert rigor review.

F1 fix: don't declare SET off MIDDLE (lowest-power, base 0.034). Use a POOLED, directional PREFIX-lag-1
  statistic across all rings (higher power than per-ring Stouffer), one-sided vs within-ring shuffle.
  Also cross-ref the individually-sig rings against C759-active folios (zone-grammar leakage check).
F2 fix: A_only (1.5%) is floored by the shared A∩B pool (denominator artifact) and has ~6 tokens in S
  -> p=0.80 uninformative. Test the RESOLVABLE contrast: the `neither` (novel, non-A non-B) cell
  (S 15.2% vs R 8.1%) AND the full 4-category distribution, within-folio null.
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
C759_ACTIVE = {'f73r', 'f72r3', 'f72r2', 'f72v1', 'f70v1', 'f72v2', 'f70v2', 'f68r3'}  # PHASE_742 sig folios

# ---------- rebuild ring loci (ordered within-locus) ----------
loci = defaultdict(list)
for t in tx.azc(h_only=True):
    w = (t.word or '').strip()
    if not w or '*' in w or not t.placement: continue
    loci[(t.folio, t.line, t.placement)].append((getattr(t, 'line_initial', 0), w))
rings = []
for (fol, ln, pl), toks in loci.items():
    if len(toks) < 12: continue
    try: toks = sorted(toks, key=lambda x: int(x[0]))
    except (TypeError, ValueError): pass
    rings.append({'folio': fol, 'placement': pl, 'prefixes': [morph.extract(w).prefix or '_' for _, w in toks]})

# ========== F1 CORRECTED: pooled directional PREFIX lag-1 ==========
def match_pairs(seq): return sum(1 for i in range(len(seq) - 1) if seq[i] == seq[i + 1]), len(seq) - 1
obs_m = obs_t = 0
for r in rings:
    m, t_ = match_pairs(r['prefixes']); obs_m += m; obs_t += t_
obs_rate = obs_m / obs_t
rng = np.random.default_rng(0); B = 10000; ge = 0; null_rates = np.empty(B)
arrs = [np.array(r['prefixes'], dtype=object) for r in rings]
for b in range(B):
    m = t_ = 0
    for a in arrs:
        p = rng.permutation(a); m += int(np.sum(p[:-1] == p[1:])); t_ += len(a) - 1
    null_rates[b] = m / t_
    if m / t_ >= obs_rate: ge += 1
p_pref = (ge + 1) / (B + 1)
print(f"F1 CORRECTED - pooled PREFIX lag-1 (all {len(rings)} rings, {obs_t} pairs):")
print(f"  observed {obs_rate:.4f} vs null mean {null_rates.mean():.4f} (95th {np.percentile(null_rates,95):.4f})  "
      f"one-sided p={p_pref:.4f}  -> {'sequence signal' if p_pref<0.05 else 'no pooled PREFIX sequence'}")
# per-ring sig + C759 overlap
sig_rings = []
for r in rings:
    seq = r['prefixes']; m, t_ = match_pairs(seq)
    if t_ < 1: continue
    a = np.array(seq, dtype=object); cnt = 0
    for _ in range(2000):
        pp = rng.permutation(a)
        if int(np.sum(pp[:-1] == pp[1:])) >= m: cnt += 1
    if (cnt + 1) / 2001 < 0.05: sig_rings.append(r['folio'])
n_in759 = sum(1 for f in sig_rings if f in C759_ACTIVE)
print(f"  individually-sig rings: {len(sig_rings)} on folios {sorted(set(sig_rings))}; "
      f"{n_in759}/{len(sig_rings)} on C759-active folios -> "
      f"{'residual = C759 zone-grammar leakage' if sig_rings and n_in759==len(sig_rings) else 'mixed/independent'}")

# ========== F2 CORRECTED: neither-cell + 4-category, within-folio null ==========
A_mid = set(); B_mid = set()
for t in tx.currier_a():
    w = (t.word or '').strip()
    if w and '*' not in w and (m := morph.extract(w).middle): A_mid.add(m)
for t in tx.currier_b():
    w = (t.word or '').strip()
    if w and '*' not in w and (m := morph.extract(w).middle): B_mid.add(m)
def cat(m):
    if m is None: return 'none'
    a, b = m in A_mid, m in B_mid
    return 'both' if a and b else ('A_only' if a else ('B_only' if b else 'neither'))
rows = []
for t in tx.azc(h_only=True):
    if t.folio not in ZODIAC: continue
    w = (t.word or '').strip()
    if not w or '*' in w or not t.placement: continue
    g = 'S' if t.placement[0] == 'S' else ('R' if t.placement[0] == 'R' else None)
    if g: rows.append((t.folio, g, cat(morph.extract(w).middle)))

byf = defaultdict(lambda: {'g': [], 'c': []})
for fol, g, c in rows: byf[fol]['g'].append(g); byf[fol]['c'].append(c)
def neither_gap(gs, cs):
    sN = [cs[i] == 'neither' for i in range(len(gs)) if gs[i] == 'S']
    rN = [cs[i] == 'neither' for i in range(len(gs)) if gs[i] == 'R']
    if not sN or not rN: return 0.0
    return np.mean(sN) - np.mean(rN)
allg = [r[1] for r in rows]; allc = [r[2] for r in rows]
obs_gap = neither_gap(allg, allc)
fg = {f: np.array(byf[f]['g'], dtype=object) for f in byf}; fc = {f: byf[f]['c'] for f in byf}
rng2 = np.random.default_rng(1); ge2 = 0; gaps = np.empty(B)
for b in range(B):
    L, C = [], []
    for f in byf:
        a = fg[f]; L.extend((rng2.permutation(a) if len(a) > 1 else a).tolist()); C.extend(fc[f])
    g = neither_gap(L, C); gaps[b] = g
    if abs(g) >= abs(obs_gap): ge2 += 1
p_neither = (ge2 + 1) / (B + 1)
sN = np.mean([c == 'neither' for g, c in zip(allg, allc) if g == 'S'])
rN = np.mean([c == 'neither' for g, c in zip(allg, allc) if g == 'R'])
print(f"\nF2 CORRECTED - `neither`(novel) rate S vs R, within-folio null:")
print(f"  S novel={sN:.3f}  R novel={rN:.3f}  gap={obs_gap:+.3f}  two-sided p={p_neither:.4f}  "
      f"-> {'LABELS carry more novel MIDDLEs (real component difference)' if p_neither<0.05 else 'no difference'}")

res = {'F1_pooled_prefix': {'obs_rate': round(obs_rate, 4), 'null_mean': round(float(null_rates.mean()), 4),
        'p_one_sided': round(p_pref, 4), 'n_pairs': obs_t, 'sig_rings_folios': sorted(set(sig_rings)),
        'sig_on_C759_active': f"{n_in759}/{len(sig_rings)}"},
       'F2_neither': {'S_novel': round(float(sN), 4), 'R_novel': round(float(rN), 4),
        'gap': round(float(obs_gap), 4), 'p_two_sided': round(p_neither, 4),
        'verdict': 'LABELS_MORE_NOVEL' if p_neither < 0.05 else 'no_diff'}}
(OUT / 'corrected_tests.json').write_text(json.dumps(res, indent=2))
print(f"\nSaved {OUT / 'corrected_tests.json'}")
