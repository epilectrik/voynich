"""P-L8: l-terminal MIDDLE fraction predicts LOW AXM self-transition.

If l = "redirect" (exit main loop), then l-terminal fraction should
negatively correlate with AXM self-transition rate per folio.
Mirror of C1384: k-initial rho=+0.620 (stay in loop).
Prediction: rho between -0.4 and -0.6, p<0.01.
"""

import json
import math
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology

PROJECT = Path(__file__).resolve().parent


def normal_cdf(z):
    if z < -8: return 0.0
    if z > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    t = 1.0 / (1.0 + p * abs(z))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z / 2.0)
    return 0.5 * (1.0 + sign * y)


def spearman_rho(x, y):
    n = len(x)
    if n < 3: return 0.0, 1.0
    def rankdata(vals):
        indexed = sorted(enumerate(vals), key=lambda t: t[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and indexed[j][1] == indexed[i][1]:
                j += 1
            avg = (i + j - 1) / 2.0 + 1
            for kk in range(i, j):
                ranks[indexed[kk][0]] = avg
            i = j
        return ranks
    rx, ry = rankdata(x), rankdata(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if dx == 0 or dy == 0: return 0.0, 1.0
    rho = num / (dx * dy)
    if abs(rho) >= 1.0: return rho, 0.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    p = 2 * (1 - normal_cdf(abs(t_stat)))
    return rho, p


tx = Transcript()
morph = Morphology()

# Load AXM data
with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
          'axm_residual_decomposition.json', encoding='utf-8') as f:
    axm_data = json.load(f)
folio_axm = {f: d['axm_self'] for f, d in axm_data['folio_data'].items()}
folio_section = {f: d['section'] for f, d in axm_data['folio_data'].items()}

# Per-folio: l-terminal fraction, k-initial fraction, l-atom fraction
folio_counts = defaultdict(lambda: {
    'total': 0, 'l_terminal': 0, 'k_initial': 0, 'l_atom': 0,
    'l_initial': 0
})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid:
        continue
    f = token.folio
    folio_counts[f]['total'] += 1
    if mid[-1] == 'l':
        folio_counts[f]['l_terminal'] += 1
    if mid[0] == 'k':
        folio_counts[f]['k_initial'] += 1
    if mid[0] == 'l':
        folio_counts[f]['l_initial'] += 1
    if 'l' in mid:
        folio_counts[f]['l_atom'] += 1

# Filter to folios with AXM data and enough tokens
folios = [f for f in folio_axm if folio_counts[f]['total'] >= 50]
print(f"Folios: {len(folios)}")

# ============================================================
# P-L8: l-terminal fraction vs AXM self-transition
# ============================================================
print(f"\n{'='*70}")
print("P-L8: l-TERMINAL FRACTION vs AXM SELF-TRANSITION")
print(f"{'='*70}")
print("Prediction: rho between -0.4 and -0.6\n")

axm_vals = [folio_axm[f] for f in folios]

# l-terminal
lt_fracs = [folio_counts[f]['l_terminal'] / folio_counts[f]['total'] for f in folios]
rho_lt, p_lt = spearman_rho(lt_fracs, axm_vals)
print(f"  l-terminal vs AXM: rho={rho_lt:+.4f}, p={p_lt:.6f}")

# k-initial (for comparison — should reproduce C1384 rho=+0.620)
ki_fracs = [folio_counts[f]['k_initial'] / folio_counts[f]['total'] for f in folios]
rho_ki, p_ki = spearman_rho(ki_fracs, axm_vals)
print(f"  k-initial vs AXM:  rho={rho_ki:+.4f}, p={p_ki:.6f} (C1384 reference: +0.620)")

# l-initial
li_fracs = [folio_counts[f]['l_initial'] / folio_counts[f]['total'] for f in folios]
rho_li, p_li = spearman_rho(li_fracs, axm_vals)
print(f"  l-initial vs AXM:  rho={rho_li:+.4f}, p={p_li:.6f}")

# l-atom (any position)
la_fracs = [folio_counts[f]['l_atom'] / folio_counts[f]['total'] for f in folios]
rho_la, p_la = spearman_rho(la_fracs, axm_vals)
print(f"  l-atom vs AXM:     rho={rho_la:+.4f}, p={p_la:.6f}")

# ============================================================
# Within-section control
# ============================================================
print(f"\n{'='*70}")
print("WITHIN-SECTION: l-terminal vs AXM")
print(f"{'='*70}")

for sec in sorted(set(folio_section[f] for f in folios)):
    idx = [f for f in folios if folio_section[f] == sec]
    if len(idx) < 5:
        continue
    lt_sec = [folio_counts[f]['l_terminal'] / folio_counts[f]['total'] for f in idx]
    axm_sec = [folio_axm[f] for f in idx]
    rho, p = spearman_rho(lt_sec, axm_sec)
    print(f"  {sec} (n={len(idx):>2d}): rho={rho:+.4f} p={p:.4f}")

# ============================================================
# Comprehensive: ALL terminal atoms vs AXM
# ============================================================
print(f"\n{'='*70}")
print("ALL TERMINAL ATOMS vs AXM SELF-TRANSITION (comprehensive ranking)")
print(f"{'='*70}")

atoms = 'a d e h k o n i m y c p f s t r l q'.split()

# Per-folio terminal atom counts
folio_term = defaultdict(lambda: defaultdict(int))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid:
        continue
    f = token.folio
    folio_term[f][mid[-1]] += 1

print(f"\n  {'Atom':<5s} {'rho':>8s} {'p':>10s} {'mean%':>8s} {'direction':>12s}")
print(f"  {'-'*5} {'-'*8} {'-'*10} {'-'*8} {'-'*12}")

results = []
for atom in atoms:
    fracs = [folio_term[f].get(atom, 0) / folio_counts[f]['total'] for f in folios]
    mean_pct = sum(fracs) / len(fracs) * 100
    rho, p = spearman_rho(fracs, axm_vals)
    results.append((atom, rho, p, mean_pct))

results.sort(key=lambda x: x[1])
for atom, rho, p, mean_pct in results:
    direction = 'anti-AXM' if rho < -0.2 else 'pro-AXM' if rho > 0.2 else 'neutral'
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    marker = ' <-- l' if atom == 'l' else ' <-- k' if atom == 'k' else ''
    print(f"  {atom:<5s} {rho:>+8.4f} {p:>10.6f} {mean_pct:>7.2f}% {direction:>12s} {sig}{marker}")

# ============================================================
# Partial: l-terminal after controlling for k-initial
# ============================================================
print(f"\n{'='*70}")
print("PARTIAL: l-terminal after controlling for k-initial")
print(f"{'='*70}")

n = len(folios)
mean_k = sum(ki_fracs) / n
mean_lt = sum(lt_fracs) / n
klt_num = sum((ki_fracs[i] - mean_k) * (lt_fracs[i] - mean_lt) for i in range(n))
kk_den = sum((ki_fracs[i] - mean_k) ** 2 for i in range(n))
beta = klt_num / kk_den if kk_den > 0 else 0
intercept = mean_lt - beta * mean_k
lt_resid = [lt_fracs[i] - beta * ki_fracs[i] - intercept for i in range(n)]
rho_resid, p_resid = spearman_rho(lt_resid, axm_vals)
rho_lt_k, _ = spearman_rho(lt_fracs, ki_fracs)

print(f"  l-terminal / k-initial correlation: rho={rho_lt_k:+.4f}")
print(f"  l-terminal residual (after k-initial): rho={rho_resid:+.4f} p={p_resid:.6f}")

# ============================================================
# k/l ratio vs AXM (the "stay vs redirect" ratio)
# ============================================================
print(f"\n{'='*70}")
print("k-INITIAL / l-TERMINAL RATIO vs AXM")
print(f"{'='*70}")

kl_ratios = [ki_fracs[i] / (lt_fracs[i] + 0.001) for i in range(n)]
rho_kl, p_kl = spearman_rho(kl_ratios, axm_vals)
print(f"  k-initial/l-terminal ratio vs AXM: rho={rho_kl:+.4f} p={p_kl:.6f}")
print(f"  (Positive = more k relative to l → higher AXM dwell)")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-L8 SUMMARY")
print(f"{'='*70}")

print(f"\n  l-terminal vs AXM: rho={rho_lt:+.4f}, p={p_lt:.6f}")
print(f"  k-initial vs AXM:  rho={rho_ki:+.4f}, p={p_ki:.6f}")
print(f"  Predicted: l-terminal rho between -0.4 and -0.6")

if -0.6 <= rho_lt <= -0.4 and p_lt < 0.01:
    print(f"  RESULT: CONFIRMED (rho={rho_lt:+.4f} in predicted range)")
elif rho_lt < -0.3 and p_lt < 0.01:
    print(f"  RESULT: CLOSE (rho={rho_lt:+.4f}, outside [-0.6,-0.4] but significant)")
elif rho_lt < 0 and p_lt < 0.05:
    print(f"  RESULT: DIRECTIONALLY CORRECT (rho={rho_lt:+.4f}, weaker than predicted)")
elif rho_lt < 0:
    print(f"  RESULT: DIRECTIONALLY CORRECT but not significant (p={p_lt:.6f})")
else:
    print(f"  RESULT: FAILED (rho={rho_lt:+.4f} is not negative)")

print(f"\n  l-terminal after k control: rho={rho_resid:+.4f}")
print(f"  k/l ratio vs AXM: rho={rho_kl:+.4f}")
if rho_kl > 0.5:
    print(f"  The k/l 'stay vs redirect' ratio is a strong AXM predictor")
