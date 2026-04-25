"""Test B for f77r ↔ III.28.0.

f77r is theoretical exposition of 4-element framework + operational guidance.
13 paragraphs total. Phase assignment based on operational reading:
  P1-P4: 4 line-initial paragraphs (specification of 4 elements: terra, aygua, ayre, foch)
  P5-P12: body iteration paragraphs (combining water+earth, repeating decoctions)
  P13: closure
"""
from __future__ import annotations
import io, sys, json
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"C:\git\voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript


def get_paragraphs(folio):
    tx = Transcript()
    para_idx = 0
    seen = False
    for t in tx.currier_b():
        if t.folio != folio:
            continue
        if t.placement and t.placement.startswith("L"):
            continue
        if t.par_initial and seen:
            para_idx += 1
        seen = True
    return para_idx + 1 if seen else 0


def spearman_rho(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    def rank(arr):
        sorted_idx = sorted(range(len(arr)), key=lambda i: arr[i])
        ranks = [0.0] * len(arr)
        i = 0
        while i < len(arr):
            j = i
            while j + 1 < len(arr) and arr[sorted_idx[j+1]] == arr[sorted_idx[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j+1):
                ranks[sorted_idx[k]] = avg
            i = j + 1
        return ranks
    n = len(xs)
    rx = rank(xs); ry = rank(ys)
    mx = sum(rx) / n; my = sum(ry) / n
    cov = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    vx = sum((r - mx)**2 for r in rx) ** 0.5
    vy = sum((r - my)**2 for r in ry) ** 0.5
    if vx == 0 or vy == 0:
        return 0.0
    return cov / (vx * vy)


def perm_p(xs, ys, rho_obs, n_perm=2000, seed=42):
    import random
    rng = random.Random(seed)
    target = abs(rho_obs)
    count = 0
    ys_perm = list(ys)
    for _ in range(n_perm):
        rng.shuffle(ys_perm)
        if abs(spearman_rho(xs, ys_perm)) >= target - 1e-12:
            count += 1
    return (count + 1) / (n_perm + 1)


n_paras = get_paragraphs("f77r")
print(f"f77r paragraphs: {n_paras}")

# Phase assignments (locked before viewing rho):
# 4 line-initial markers at L1-L4 = 4-element specification block
# Body paragraphs = primary procedure
# Final = closure
phases = [1] * 4 + [2] * 8 + [3]  # 13 total
if len(phases) != n_paras:
    # Adjust to actual paragraph count
    if n_paras > len(phases):
        phases = phases + [phases[-1]] * (n_paras - len(phases))
    else:
        phases = phases[:n_paras]

layout = list(range(1, n_paras + 1))
rho = spearman_rho(layout, phases)
p = perm_p(layout, phases, rho, n_perm=2000)
sig = "✓" if p < 0.10 else "·"
sig2 = "★" if p < 0.05 else ""

print(f"\nf77r ↔ III.28.0 (4-element exposition + iteration)")
print(f"  Paragraphs (n={n_paras}): {phases}")
print(f"  Spearman rho = {rho:+.4f}")
print(f"  Permutation p = {p:.4f}  {sig}{sig2}")

# Save
out = ROOT / "phases" / "RECIPE_REVERSE_FOLIO_SEARCH" / "results" / "test_B_f77r.json"
out.write_text(json.dumps({
    "folio": "f77r", "recipe_id": "III.28.0",
    "n_paragraphs": n_paras, "phases": phases,
    "rho": rho, "p": p, "significant_005": p < 0.05,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nWrote {out.relative_to(ROOT)}")
