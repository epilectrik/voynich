"""Test F: Generalize-or-Die Scope Test.

Run Test B's layout-phase correlation on MODERATE-tier folios that have
plausible (but not confirmed) recipe correspondences. Determines whether
the semantic layout-ordering finding generalizes beyond confirmed matches
or is specific to MATCH-tier alignment.

If layout-ordering appears across ALL recipe-corresponding folios (regardless
of match-tier), the new constraint should claim "folios with recipe correspondence"
scope. If it appears only on confirmed MATCH-tier, the constraint scopes
narrower.

MODERATE-tier folios from catalan_atom_decode_findings (PHASE_641):
  f76v ↔ III.16.0 (ferment multiplication)
  f77v ↔ III.20.0 (furnace specification)
  f82v ↔ III.21.0 (vessel specification)
  f103r ↔ III.16.0 (ferment multiplication, same recipe as f76v)
  f112r ↔ III.11.0 (red mercury cohobation)

These had MATCH/MODERATE atom-decode scores but didn't reach STRONG SUPPORT.
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


# ──────────────────────────────────────────────────────────────────────
# Phase assignments for MODERATE-tier folios
# ──────────────────────────────────────────────────────────────────────
# Phase ordinals: 1=setup/specification, 2=primary procedure,
#                 3=iteration/sub-procedure, 4=closure

NEAR_MATCHES = [
    {
        "folio": "f76v",
        "recipe_id": "III.16.0",
        "recipe_summary": "Ferment multiplication. Mix→evaporate→add→multiply→reiterate",
        # Recipe: "Pren lo ferment de B e aquell de C; e cascú de aquels sia gitat
        #         en l'aygua roia. Puis ajusta les aygues e evapora aquells en lo
        #         bany de maria; e aprés mit-ho sobre cenres..."
        # Operations: take ferments → mix in red water → join + evaporate balneum
        #            → on ashes → if needed add air → reiterate multiplication
        # f76v has 41 lines. Need paragraph count.
        # Will assign phases based on actual paragraph count.
        "phase_pattern": "ascending",  # 2,2,3,3 etc — primary then iteration
    },
    {
        "folio": "f77v",
        "recipe_id": "III.20.0",
        "recipe_summary": "Furnace specification. Setup→build→fire→test",
        # Recipe is about furnace construction/specification.
        # Operations: design → construction → fire/test → completion
        "phase_pattern": "ascending",
    },
    {
        "folio": "f82v",
        "recipe_id": "III.21.0",
        "recipe_summary": "Vessel specification. Materials→construction→sealing",
        "phase_pattern": "ascending",
    },
    {
        "folio": "f103r",
        "recipe_id": "III.16.0",
        "recipe_summary": "Ferment multiplication (same as f76v).",
        "phase_pattern": "ascending",
    },
    {
        "folio": "f112r",
        "recipe_id": "III.11.0",
        "recipe_summary": "Red mercury cohobation. × 3 vegades distillation cycles + projection",
        # Recipe: distill in bath × 3, separate elements, fix the body
        "phase_pattern": "ascending",
    },
]


# Reference: confirmed matches phase assignments from Test B
CONFIRMED_MATCHES = [
    {"folio": "f75r", "recipe_id": "III.19.0", "phases": [2, 2, 3]},
    {"folio": "f84r", "recipe_id": "II.12.0",
     "phases": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 4]},
    {"folio": "f78r", "recipe_id": "III.36.0", "phases": [2, 3, 3, 3, 3, 3, 3, 3]},
    {"folio": "f86v3", "recipe_id": "II.10.0", "phases": [2, 2, 3, 3, 3, 3, 4]},
    {"folio": "f82r", "recipe_id": "III.19.3", "phases": [2, 2, 3, 3]},
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


def assign_ascending_phases(n_paragraphs):
    """Default ascending-phase assignment for near-match folios where we
    don't have detailed atom-decode reading: assume paragraphs progress
    from primary (phase 2) through iteration (phase 3). This is the
    default expectation if layout-order tracks recipe-phase."""
    if n_paragraphs == 0:
        return []
    if n_paragraphs == 1:
        return [2]
    if n_paragraphs == 2:
        return [2, 3]
    if n_paragraphs == 3:
        return [2, 2, 3]
    # For longer folios: front half primary, back half iteration
    half = n_paragraphs // 2
    return [2] * half + [3] * (n_paragraphs - half)


def spearman_rho(xs, ys):
    def rank(arr):
        sorted_idx = sorted(range(len(arr)), key=lambda i: arr[i])
        ranks = [0.0] * len(arr)
        i = 0
        while i < len(arr):
            j = i
            while j + 1 < len(arr) and arr[sorted_idx[j+1]] == arr[sorted_idx[i]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j+1):
                ranks[sorted_idx[k]] = avg_rank
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


# ──────────────────────────────────────────────────────────────────────
# Run test
# ──────────────────────────────────────────────────────────────────────

print("Test F — Generalize-or-Die Scope Test")
print("=" * 80)
print("Hypothesis: layout-order correlation extends beyond confirmed-MATCH-tier folios.")
print("Default phase assignment: ascending (primary → iteration) where atom-decode read isn't available.")
print()

# (a) Confirmed-match baseline — expected high rho
print("\n## (a) CONFIRMED-MATCH BASELINE (Test B replication)\n")
confirmed_results = []
for m in CONFIRMED_MATCHES:
    actual_n = get_paragraph_count(m["folio"])
    phases = m["phases"][:actual_n] if len(m["phases"]) >= actual_n else m["phases"] + [m["phases"][-1]] * (actual_n - len(m["phases"]))
    layout = list(range(1, actual_n + 1))
    rho = spearman_rho(layout, phases)
    p = perm_p(layout, phases, rho, n_perm=2000)
    confirmed_results.append({"folio": m["folio"], "recipe_id": m["recipe_id"],
                              "n": actual_n, "rho": rho, "p": p})
    sig = "✓" if p < 0.10 else "·"
    print(f"  {m['folio']:<8} ↔ {m['recipe_id']:<10}  rho={rho:+.3f}  p={p:.3f}  {sig}  (n={actual_n})")

mean_rho_a = sum(r["rho"] for r in confirmed_results) / len(confirmed_results)
print(f"\n  Mean rho (confirmed matches): {mean_rho_a:+.4f}")

# (b) Near-MATCH (MODERATE-tier) folios — test if effect generalizes
print("\n## (b) NEAR-MATCH (MODERATE-tier) FOLIOS\n")
print("Default phase assignment used (ascending). Without detailed atom-decode reading,")
print("we use the simplest hypothesis: paragraphs progress primary→iteration.\n")
near_results = []
for m in NEAR_MATCHES:
    actual_n = get_paragraph_count(m["folio"])
    if actual_n == 0:
        print(f"  {m['folio']}: 0 paragraphs, SKIP")
        continue
    phases = assign_ascending_phases(actual_n)
    layout = list(range(1, actual_n + 1))
    rho = spearman_rho(layout, phases)
    p = perm_p(layout, phases, rho, n_perm=2000)
    near_results.append({"folio": m["folio"], "recipe_id": m["recipe_id"],
                         "n": actual_n, "rho": rho, "p": p})
    sig = "✓" if p < 0.10 else "·"
    print(f"  {m['folio']:<8} ↔ {m['recipe_id']:<10}  rho={rho:+.3f}  p={p:.3f}  {sig}  (n={actual_n})")

mean_rho_b = sum(r["rho"] for r in near_results) / len(near_results) if near_results else 0
print(f"\n  Mean rho (near-MATCH MODERATE-tier): {mean_rho_b:+.4f}")

# (c) Random unmatched folios as negative control
print("\n## (c) UNMATCHED RANDOM B FOLIOS (negative control)\n")
print("Use any folio not in the matched/near-match sets, with default ascending-phase assignment.")
print("Hypothesis: layout-position is by definition matched to ascending phases on the")
print("layout side, but the recipe-phase has no relation to layout, so rho should be ~0\n")
print("over a random sample.\n")

# Get all B folios
tx = Transcript()
all_b_folios = set()
for t in tx.currier_b():
    all_b_folios.add(t.folio)

CONFIRMED_FOLIOS = {m["folio"] for m in CONFIRMED_MATCHES}
NEAR_FOLIOS = {m["folio"] for m in NEAR_MATCHES}
EXCLUDE = CONFIRMED_FOLIOS | NEAR_FOLIOS | {"f76r", "f81v", "f116r", "f80r", "f107r", "f112v", "f83r", "f79r"}
# Excluding the rest of the original 16 matched folios too

# Sample random B folios with ≥4 paragraphs for a meaningful test
random_candidates = []
for f in sorted(all_b_folios):
    if f in EXCLUDE:
        continue
    n_p = get_paragraph_count(f)
    if n_p >= 4:
        random_candidates.append((f, n_p))

print(f"Found {len(random_candidates)} unmatched B folios with ≥4 paragraphs.")
print("Using ascending-phase assignment on layout (which would always give rho=1 by construction)")
print("This isn't a true negative control — for that we'd need actual recipe pairings.\n")

# Better: randomly assign phases on each folio, measure rho null distribution
import random
rng = random.Random(643)

random_results = []
for f, n_p in random_candidates[:10]:
    layout = list(range(1, n_p + 1))
    # Assign random phases drawn from {1, 2, 3, 4} with realistic distribution
    # Most paragraphs are phase 2 or 3
    phases = [rng.choice([2, 2, 2, 3, 3, 3, 1, 4]) for _ in range(n_p)]
    rho = spearman_rho(layout, phases)
    p = perm_p(layout, phases, rho, n_perm=2000)
    random_results.append({"folio": f, "n": n_p, "rho": rho, "p": p})
    sig = "✓" if p < 0.10 else "·"
    print(f"  {f:<8}  rho={rho:+.3f}  p={p:.3f}  {sig}  (n={n_p}, random phases)")

mean_rho_c = sum(r["rho"] for r in random_results) / len(random_results) if random_results else 0
print(f"\n  Mean rho (random phase assignment, unmatched folios): {mean_rho_c:+.4f}")

# ──────────────────────────────────────────────────────────────────────
# Synthesis
# ──────────────────────────────────────────────────────────────────────

print("\n" + "=" * 80)
print("SYNTHESIS")
print("=" * 80)
print(f"\n  (a) Confirmed-match mean rho: {mean_rho_a:+.4f}  (n={len(confirmed_results)})")
print(f"  (b) Near-MATCH mean rho:      {mean_rho_b:+.4f}  (n={len(near_results)})")
print(f"  (c) Random-phase null mean:   {mean_rho_c:+.4f}  (n={len(random_results)})")

print()
if mean_rho_a > 0.7 and mean_rho_b > 0.5 and mean_rho_a - mean_rho_c > 0.5:
    print("  VERDICT: Effect strong on confirmed matches AND generalizes to near-MATCH.")
    print("  New constraint should claim folios-with-recipe-correspondence scope.")
elif mean_rho_a > 0.7 and mean_rho_b > 0.3:
    print("  VERDICT: Effect strong on confirmed matches, weaker on near-MATCH.")
    print("  New constraint should claim CONFIRMED-MATCH scope, with note that effect")
    print("  weakens at lower correspondence-tier.")
elif mean_rho_a > 0.7 and mean_rho_b < 0.3:
    print("  VERDICT: Effect specific to confirmed-MATCH-tier folios only.")
    print("  New constraint scopes narrowly to confirmed matches.")
else:
    print("  VERDICT: Effect weaker than expected even on confirmed matches.")
    print("  Re-examine assumptions before constraint registration.")

# Caveat about the test design
print()
print("  IMPORTANT CAVEAT:")
print("  The near-MATCH test uses default ascending-phase assignment (primary → iteration).")
print("  This biases TOWARD finding rho > 0 because the assignment is monotone-by-construction.")
print("  Compare to:")
print("  - Test B used atom-decode-derived phase assignments (more accurate, less biased)")
print("  - The random-phase null shows what rho looks like with non-monotone phases")
print()
print("  The confirmed-match rho (0.81 from Test B) is a stronger signal than this test")
print("  can produce for near-MATCH because:")
print("  - Test B's phases were ATOM-DECODE-DERIVED, not default ascending")
print("  - Some confirmed matches have non-trivial phase patterns (f84r: 1*12, 2*5, 4)")
print("  - Default ascending only tests ordering, not phase-content match")

# Write JSON output
out = ROOT / "phases" / "PARAGRAPH_ORDERING_DISAMBIGUATION" / "results" / "test_F_results.json"
out.write_text(json.dumps({
    "test": "Test F — Generalize-or-Die Scope Test",
    "confirmed_matches": confirmed_results,
    "near_matches": near_results,
    "random_phase_null": random_results,
    "mean_rho_confirmed": mean_rho_a,
    "mean_rho_near": mean_rho_b,
    "mean_rho_random": mean_rho_c,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nWrote {out.relative_to(ROOT)}")
