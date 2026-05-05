"""KILLER TEST v2 — adds REGIME stratification (C1404) + Mode B mediation (C1260).

Pre-reg additions (locked before running):
  P5: Within REGIME_1 (the dominant cluster), S vs B mean z difference, p<0.05 permutation
  P6: After residualizing folio z on Mode-B-line-fraction, S vs B difference survives p<0.05
"""
import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Build paragraph-aware sequences
folio_paragraph_seq = defaultdict(list)
folio_section = {}
folio_para_counter = defaultdict(int)
for t in tx.currier_b():
    if not t.placement.startswith('P'):
        continue
    if not t.word or '*' in t.word:
        continue
    a = morph.atomize(t.word)
    e_depth = a.e_depth
    if getattr(t, 'par_initial', False):
        folio_para_counter[t.folio] += 1
    para = folio_para_counter[t.folio]
    folio_paragraph_seq[t.folio].append((para, t.line, t.word, e_depth))
    folio_section[t.folio] = t.section

# Load REGIME map
with open(Path(__file__).resolve().parents[3] / 'data' / 'regime_folio_mapping.json', 'r') as f:
    regime_data = json.load(f)['regime_assignments']
folio_regime = {f: d['regime'] for f, d in regime_data.items()}

# Compute Mode B fraction per folio (using BDecoder.analyze_folio_lines)
print("Computing Mode B fraction per folio...")
folio_mode_b_frac = {}
for f in folio_paragraph_seq.keys():
    try:
        line_analyses = decoder.analyze_folio_lines(f)
    except Exception as e:
        line_analyses = []
    if not line_analyses:
        folio_mode_b_frac[f] = None
        continue
    n_total = sum(1 for la in line_analyses if la.suffix_mode is not None)
    n_b = sum(1 for la in line_analyses if la.suffix_mode == 'B')
    folio_mode_b_frac[f] = (n_b / n_total) if n_total > 0 else None

# Killer z function (same as v1)
def killer_z(seq, n_perm=500, seed=0):
    pairs = []
    for i in range(len(seq) - 1):
        p1, l1, t1, e1 = seq[i]
        p2, l2, t2, e2 = seq[i+1]
        if p1 != p2 or t1 == t2:
            continue
        pairs.append((e1, e2))
    if len(pairs) < 30:
        return None, None, len(pairs)
    e1s = np.array([p[0] for p in pairs], dtype=float)
    e2s = np.array([p[1] for p in pairs], dtype=float)
    if np.std(e1s) == 0 or np.std(e2s) == 0:
        return None, None, len(pairs)
    actual = np.corrcoef(e1s, e2s)[0, 1]
    all_e = np.array([e for p, l, t, e in seq], dtype=float)
    rng = np.random.default_rng(seed)
    null_corrs = []
    for _ in range(n_perm):
        shuf = all_e.copy()
        rng.shuffle(shuf)
        pe1, pe2 = [], []
        for i in range(len(seq) - 1):
            p1, l1, t1, _ = seq[i]
            p2, l2, t2, _ = seq[i+1]
            if p1 != p2 or t1 == t2:
                continue
            pe1.append(shuf[i])
            pe2.append(shuf[i+1])
        if len(pe1) < 2:
            null_corrs.append(0.0)
            continue
        a1, a2 = np.array(pe1), np.array(pe2)
        if np.std(a1) == 0 or np.std(a2) == 0:
            null_corrs.append(0.0)
            continue
        null_corrs.append(np.corrcoef(a1, a2)[0, 1])
    null_mean = np.mean(null_corrs)
    null_std = np.std(null_corrs)
    z = (actual - null_mean) / null_std if null_std > 0 else 0
    return actual, z, len(pairs)

# Run killer for all folios
print("Running killer test...")
results = []
for f, seq in folio_paragraph_seq.items():
    if len(seq) < 60:
        continue
    actual, z, n_pairs = killer_z(seq, n_perm=500, seed=hash(f) % 2**31)
    if z is None:
        continue
    sec = folio_section.get(f, '?')
    reg = folio_regime.get(f, '?')
    mb = folio_mode_b_frac.get(f)
    results.append((f, sec, reg, mb, actual, z, n_pairs))

# REGIME breakdown
print()
print("REGIME breakdown by section:")
print(f"  {'sec':<3}  {'REGIME':<10}  {'n':>3}  {'mean_z':>8}  {'sig_z>2':>9}")
sec_reg = defaultdict(list)
for f, sec, reg, mb, actual, z, np_ in results:
    sec_reg[(sec, reg)].append((f, z))
for (sec, reg), rs in sorted(sec_reg.items()):
    zs = [r[1] for r in rs]
    sig = sum(1 for z in zs if z > 2)
    print(f"  {sec:<3}  {reg:<10}  {len(zs):>3}  {np.mean(zs):>+8.2f}  {sig:>3}/{len(zs):<3}")

# P5: Within-REGIME_1 S vs B
print()
print("P5: Within REGIME_1 — S vs B")
s_r1 = [z for f, sec, reg, mb, a, z, np_ in results if sec == 'S' and reg == 'REGIME_1']
b_r1 = [z for f, sec, reg, mb, a, z, np_ in results if sec == 'B' and reg == 'REGIME_1']
print(f"  S | REGIME_1: n={len(s_r1)}, mean_z={np.mean(s_r1):+.2f}" if s_r1 else "  S | REGIME_1: n=0")
print(f"  B | REGIME_1: n={len(b_r1)}, mean_z={np.mean(b_r1):+.2f}" if b_r1 else "  B | REGIME_1: n=0")
if s_r1 and b_r1:
    actual_diff_r1 = np.mean(s_r1) - np.mean(b_r1)
    pooled = list(s_r1) + list(b_r1)
    n_s = len(s_r1)
    rng = np.random.default_rng(42)
    null = []
    for _ in range(10000):
        rng.shuffle(pooled)
        null.append(np.mean(pooled[:n_s]) - np.mean(pooled[n_s:]))
    p_r1 = sum(1 for d in null if d >= actual_diff_r1) / len(null)
    print(f"  Difference: {actual_diff_r1:+.3f}  permutation p={p_r1:.4f}")
else:
    p_r1 = 1.0
    print("  Insufficient data for REGIME_1 comparison.")

# P6: Mode B mediation — residualize folio z on Mode B fraction
print()
print("P6: Mode B mediation — residualize folio z on Mode-B-line fraction")
print("  Mode B fraction by section:")
sec_mb = defaultdict(list)
for f, sec, reg, mb, a, z, np_ in results:
    if mb is not None:
        sec_mb[sec].append(mb)
for sec in sorted(sec_mb.keys()):
    print(f"    {sec}: n={len(sec_mb[sec])}, mean Mode B frac={np.mean(sec_mb[sec])*100:.1f}%")

# Linear regression: z = a + b * mode_b_frac, get residuals
valid = [(f, sec, reg, mb, z) for f, sec, reg, mb, a, z, np_ in results if mb is not None]
if valid:
    mb_arr = np.array([v[3] for v in valid])
    z_arr = np.array([v[4] for v in valid])
    if np.std(mb_arr) > 0:
        slope = np.cov(mb_arr, z_arr)[0,1] / np.var(mb_arr)
        intercept = np.mean(z_arr) - slope * np.mean(mb_arr)
        z_resid = z_arr - (slope * mb_arr + intercept)
        print(f"  Regression: z = {intercept:+.3f} + {slope:+.3f} * mode_b_frac")
        print(f"  After residualization (z - predicted):")
        sec_zresid = defaultdict(list)
        for (f, sec, reg, mb, _), zr in zip(valid, z_resid):
            sec_zresid[sec].append(zr)
        for sec in sorted(sec_zresid.keys()):
            zr = sec_zresid[sec]
            print(f"    {sec}: n={len(zr)}, mean z_resid={np.mean(zr):+.3f}, sig>2: {sum(1 for z in zr if z > 2)}/{len(zr)}")
        # S vs B test on residual
        s_resid = sec_zresid.get('S', [])
        b_resid = sec_zresid.get('B', [])
        if s_resid and b_resid:
            actual_diff_mb = np.mean(s_resid) - np.mean(b_resid)
            pooled = list(s_resid) + list(b_resid)
            n_s = len(s_resid)
            rng = np.random.default_rng(43)
            null = []
            for _ in range(10000):
                rng.shuffle(pooled)
                null.append(np.mean(pooled[:n_s]) - np.mean(pooled[n_s:]))
            p_mb = sum(1 for d in null if d >= actual_diff_mb) / len(null)
            print(f"  S vs B on residualized z: diff={actual_diff_mb:+.3f}, p={p_mb:.4f}")
        else:
            p_mb = 1.0
    else:
        p_mb = 1.0
        print("  Mode B fraction has no variance; cannot residualize.")
else:
    p_mb = 1.0
    print("  No Mode B fractions computed; cannot residualize.")

# Final pre-reg verdict (P1-P6)
print()
print("="*70)
print("FINAL PRE-REG VERDICT (P1-P6)")
print("="*70)

# Recompute P1-P4 from results
s_zs = [z for f, sec, reg, mb, a, z, np_ in results if sec == 'S']
b_zs = [z for f, sec, reg, mb, a, z, np_ in results if sec == 'B']
actual_diff = np.mean(s_zs) - np.mean(b_zs)
pooled = list(s_zs) + list(b_zs)
n_s = len(s_zs)
rng = np.random.default_rng(44)
null = []
for _ in range(10000):
    rng.shuffle(pooled)
    null.append(np.mean(pooled[:n_s]) - np.mean(pooled[n_s:]))
p1 = sum(1 for d in null if d >= actual_diff) / len(null)

top5 = ['f112v', 'f108r', 'f95r2', 'f111r', 'f55v']
top5_survivors = sum(1 for f5 in top5 if any(r[0] == f5 and r[5] > 2 for r in results))

s_frac_sig = sum(1 for z in s_zs if z > 2) / len(s_zs)
b_count_sig = sum(1 for z in b_zs if z > 2)

P1 = p1 < 0.01
P2 = float(np.mean(s_zs)) >= 1.5
P3 = top5_survivors >= 3
P4 = (s_frac_sig >= 0.30) and (b_count_sig == 0)
P5 = p_r1 < 0.05
P6 = p_mb < 0.05 if 'p_mb' in dir() else False

print(f"  P1: S vs B p<0.01                          {'PASS' if P1 else 'FAIL'}  (p={p1:.4f})")
print(f"  P2: S mean z >= 1.5                        {'PASS' if P2 else 'FAIL'}  (mean={float(np.mean(s_zs)):.3f})")
print(f"  P3: >=3 of top-5 survive                   {'PASS' if P3 else 'FAIL'}  ({top5_survivors}/5)")
print(f"  P4: S frac>2 >= 30% AND B frac>2 == 0      {'PASS' if P4 else 'FAIL'}  (S={s_frac_sig*100:.1f}%, B={b_count_sig}/{len(b_zs)})")
print(f"  P5: Within REGIME_1, S vs B p<0.05         {'PASS' if P5 else 'FAIL'}  (p={p_r1:.4f})")
print(f"  P6: Mode-B-residualized S vs B p<0.05      {'PASS' if P6 else 'FAIL'}  (p={p_mb:.4f})")
print()
n_pass = sum([P1, P2, P3, P4, P5, P6])
print(f"  CRITERIA PASSED: {n_pass}/6")
if n_pass == 6:
    print(f"  REGISTRATION: TIER 2 CLEAN (all controls pass)")
elif n_pass >= 4:
    print(f"  REGISTRATION: TIER 3 (some controls fail; report what survives)")
else:
    print(f"  REGISTRATION: NULL (insufficient survival)")

# Save results to phase folder later
print()
print("Folio-level results (for phase results dir):")
print(f"  {'folio':<8}  {'sec':<3}  {'regime':<10}  {'mode_b':>6}  {'lag1':>8}  {'z':>6}  {'pairs':>5}")
for f, sec, reg, mb, a, z, np_ in sorted(results, key=lambda x: -x[5]):
    mb_s = f"{mb*100:.0f}%" if mb is not None else "?"
    print(f"  {f:<8}  {sec:<3}  {reg:<10}  {mb_s:>6}  {a:>+8.4f}  {z:>+6.2f}  {np_:>5}")
