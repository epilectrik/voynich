"""Run Test B (layout-order vs recipe-phase-order) on the two newly verified
matches: f108v ↔ III.29.0 and f79v ↔ II.8.0.

Phase ordinals assigned per atom-decode reading:
  1 = setup/specification
  2 = primary procedure
  3 = iteration / sub-procedure
  4 = closure
"""
from __future__ import annotations
import io, sys, json, re
from pathlib import Path
from collections import defaultdict

if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"C:\git\voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript


# Phase assignments based on atom-decode reading of each folio against recipe
NEW_MATCHES = [
    {
        "folio": "f108v",
        "recipe_id": "III.29.0",
        "summary": "Mercury sublimation. Setup→long-decoction→three-operations→closure",
        # 10 paragraphs total. P1-P3 setup short. P4-P8 mid-procedure phases.
        # P9 (L33-L51, 19 lines) = sustained sublimation body. P10 (L52, 4 tokens) = closure.
        # Reading: progressive intensification from setup to long-body to closure.
        "phases": [1, 1, 1, 2, 2, 2, 2, 2, 3, 4],
        "rationale": ("P1-P3 are short opening paragraphs (setup/specification). "
                      "P4-P8 are mid-folio body paragraphs (primary procedure phases). "
                      "P9 is the long sustained-operation body (L33-L51, 19 lines) — "
                      "the sublimation iteration. P10 is the 4-token closure."),
    },
    {
        "folio": "f79v",
        "recipe_id": "II.8.0",
        "summary": "First liquefaction. Setup→cut/divide→add-materials→3-day-balneum→closure",
        # 7 paragraphs.
        # P1 (L1-L9, 9 lines): primary preparation/cutting/dividing
        # P2 (L10-L11, 2 lines): material addition setup
        # P3 (L12-L22, 11 lines): main material introduction + 3-day balneum
        #     (the L19 3-anchor + 3 dar tokens sit in this paragraph)
        # P4 (L23-L27, 5 lines): bath continues
        # P5 (L28-L32, 5 lines): bath continues
        # P6 (L33-L36, 4 lines): wind-down
        # P7 (L37-L42, 6 lines): closure
        "phases": [1, 2, 2, 3, 3, 3, 4],
        "rationale": ("P1 is the long opening with cutting/dividing (setup). "
                      "P2 starts material addition. P3 is the main body containing "
                      "L19's 3-run + dar (3-day balneum onset). P4-P5 continue "
                      "the bath. P6 winds down. P7 closes."),
    },
]


def get_paragraph_count(folio):
    tx = Transcript()
    para_idx = 0
    seen_any = False
    for t in tx.currier_b():
        if t.folio != folio:
            continue
        if t.placement and t.placement.startswith("L"):
            continue
        if t.par_initial and seen_any:
            para_idx += 1
        seen_any = True
    return para_idx + 1 if seen_any else 0


def spearman_rho(xs, ys):
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


print("Test B Extended — layout-order vs recipe-phase-order on newly verified matches")
print("=" * 80)

results = []
for m in NEW_MATCHES:
    actual_n = get_paragraph_count(m["folio"])
    if len(m["phases"]) != actual_n:
        print(f"\n⚠️  {m['folio']}: actual_paras={actual_n} but phases len={len(m['phases'])}")
        # Pad/truncate
        if actual_n > len(m["phases"]):
            phases = m["phases"] + [m["phases"][-1]] * (actual_n - len(m["phases"]))
        else:
            phases = m["phases"][:actual_n]
    else:
        phases = m["phases"]

    layout = list(range(1, actual_n + 1))
    rho = spearman_rho(layout, phases)
    p = perm_p(layout, phases, rho, n_perm=2000)
    sig = "✓" if p < 0.10 else "·"
    sig2 = "★" if p < 0.05 else ""

    print(f"\n{m['folio']} ↔ {m['recipe_id']}: {m['summary']}")
    print(f"  Paragraphs (n={actual_n}): phases {phases}")
    print(f"  Rationale: {m['rationale']}")
    print(f"  Spearman rho = {rho:+.4f}  (perm p = {p:.4f}) {sig}{sig2}")
    results.append({"folio": m["folio"], "recipe_id": m["recipe_id"],
                    "n": actual_n, "rho": rho, "p": p, "phases": phases})

# Combine with prior 5 matches
prior_results = [
    {"folio": "f84r", "rho": 0.827, "p": 0.0005, "n": 18},
    {"folio": "f86v3", "rho": 0.896, "p": 0.025, "n": 7},
    {"folio": "f75r", "rho": 0.866, "p": 0.681, "n": 3},
    {"folio": "f78r", "rho": 0.577, "p": 0.246, "n": 8},
    {"folio": "f82r", "rho": 0.894, "p": 0.314, "n": 4},
]

print("\n" + "=" * 80)
print("AGGREGATE — All 7 confirmed matches")
print("=" * 80)

all_results = prior_results + results
mean_rho = sum(r["rho"] for r in all_results) / len(all_results)
n_positive = sum(1 for r in all_results if r["rho"] > 0)
n_significant = sum(1 for r in all_results if r["p"] < 0.10)
n_strict_sig = sum(1 for r in all_results if r["p"] < 0.05)

print(f"\n  Mean rho across {len(all_results)} matches: {mean_rho:+.4f}")
print(f"  Folios with rho > 0:            {n_positive}/{len(all_results)}")
print(f"  Folios with perm p < 0.10:      {n_significant}/{len(all_results)}")
print(f"  Folios with perm p < 0.05:      {n_strict_sig}/{len(all_results)}")
print()
print(f"  Per-folio:")
for r in all_results:
    sig = "✓" if r["p"] < 0.10 else "·"
    sig2 = "★" if r["p"] < 0.05 else ""
    print(f"    {r['folio']:<8}  rho={r['rho']:+.3f}  p={r['p']:.3f}  {sig}{sig2}  (n={r['n']})")

# Tier 2 promotion criterion
print()
if n_strict_sig >= 3:
    print(f"  ► Tier 2 promotion criterion MET: {n_strict_sig} folios at p<0.05.")
    print(f"    Per expert-advisor: 3+ individually-significant folios is the threshold.")
elif n_significant >= 4:
    print(f"  ► Approaching Tier 2 — {n_significant} folios at p<0.10 (need {n_strict_sig} at p<0.05).")
else:
    print(f"  ► Tier 3 retained — {n_strict_sig} folios at p<0.05 (need ≥3 for Tier 2).")

out = ROOT / "phases" / "REVERSE_PREDICTED_ATOM_VERIFICATION" / "results" / "test_B_extended.json"
out.write_text(json.dumps({
    "test": "Test B Extended — Phase 643 layout-phase correlation on new matches",
    "new_matches": results,
    "all_confirmed_matches_aggregate": {
        "n": len(all_results),
        "mean_rho": mean_rho,
        "n_positive": n_positive,
        "n_p_lt_010": n_significant,
        "n_p_lt_005": n_strict_sig,
    },
    "tier_recommendation": "Tier 2 if n_p_lt_005 >= 3 else Tier 3",
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nWrote {out.relative_to(ROOT)}")
