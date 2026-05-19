"""
PHASE_704: Antidotarium Nicolai d<1.0 absolute-distance test for f104-105.

Closes the Section S 4-folio source gap question: are f104r, f104v, f105r,
f105v matches for Antidotarium Nicolai compound-pharmacy recipes?

Previous test (_antidotarium_baseline_matcher.py) used top-1 mode and
produced degenerate result (66% of Antidotarium recipes collapse to f34v
— per memory `feedback_top1_matcher_mode_is_degenerate.md`). This test
uses hypothesis-driven absolute-distance gating (d < 1.0) per validated
C1971 methodology.

Test design (LOCKED before running):

1. Compute Antidotarium vs Voynich 8D distance matrix (TUNED_DIMS).

2. Global distance distribution (calibration):
   - What is the minimum d achieved by any Antidotarium recipe vs any
     Voynich folio? If min(d) >> 1.0, the threshold is too strict for
     this corpus and the test is uninformative (no matches anywhere).

3. Per-target-folio analysis: for each of f104r, f104v, f105r, f105v:
   - Report closest 5 Antidotarium recipes (by d)
   - Count Antidotarium recipes within d < 1.0
   - Count within d < 1.5 (relaxed)

4. In-domain controls:
   - Section B alchemy folios (e.g., f75-84): should NOT match Antidotarium
     (Codicillus-alchemy class, not pharmacy)
   - matched-S folios (e.g., f103r, f106r): already PL-attributed
     (Codicillus-Mercuriorum), should NOT match Antidotarium
   - f57v anomaly folio: random control

5. Discriminating verdict:
   - PASS if at least 1 Antidotarium recipe at d<1.0 to any f104-105
     folio AND these matches are SPECIFIC (not present at same density
     to control folios)
   - FAIL if no f104-105 folio has any Antidotarium match at d<1.0
   - INCONCLUSIVE if matches are non-specific (present equally for
     controls — would indicate feature-space limitation, not Section S
     identification)
"""

import sys, io, json, math, re
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "phases" / "RECIPE_FOLIO_CORRESPONDENCE" / "scripts"))
sys.path.insert(0, str(ROOT / "phases" / "PER_DOMAIN_BRIDGE_CALIBRATION" / "scripts"))

from shared_628 import (
    load_b_operational_profiles, load_b_deployment_features,
    load_regime_mapping,
    TUNED_DIMS, build_pl_vector, build_v_vector,
    compute_residuals, standardize,
)

OUT_PATH = ROOT / 'phases' / 'PHASE_704_ANTIDOTARIUM_F104_105' / 'results' / 'antidotarium_d1_test.json'

TARGET_FOLIOS = ['f104r', 'f104v', 'f105r', 'f105v']

# Controls (per project context)
SECTION_B_ALCHEMY_CONTROL = ['f75r', 'f76r', 'f77r', 'f78r', 'f79r', 'f80r',
                             'f81r', 'f82r', 'f83r', 'f84r']  # balneology
MATCHED_S_CONTROL = ['f103r', 'f106r', 'f108r', 'f112r', 'f114r']  # PL-attributed
F57V_CONTROL = ['f57v']  # known anomaly

D_THRESHOLD = 1.0
D_RELAXED = 1.5


def main():
    print("Loading Antidotarium features...")
    with open(ROOT / "sources" / "antidotarium_nicolai"
             / "antidotarium_nicolai_compound_features.json", encoding="utf-8") as f:
        a_data = json.load(f)
    recipes = a_data["recipes"]
    n_recipes = len(recipes)
    print(f"  {n_recipes} Antidotarium recipes")

    print("\nLoading Voynich side...")
    op_profiles = load_b_operational_profiles()
    deploy_features, _ = load_b_deployment_features()
    regime_map = load_regime_mapping()

    with open(ROOT / "phases" / "ATOM_FOLIO_ATLAS" / "results" / "folio_atlas.json",
              encoding="utf-8") as f:
        atlas = json.load(f)

    all_b_folios = sorted(op_profiles.keys())
    n_v = len(all_b_folios)
    print(f"  {n_v} Voynich folios")

    # Build folio -> index map
    folio_idx = {f: i for i, f in enumerate(all_b_folios)}

    def section_of(folio):
        if folio in atlas:
            return atlas[folio].get("section", "?")
        m = re.search(r"(\d+)", folio)
        if m:
            num = int(m.group(1))
            if 87 <= num <= 102:
                return "B"
            if 103 <= num <= 116:
                return "S"
            return "H"
        return "?"

    # Build vectors
    n_dims = len(TUNED_DIMS)
    pl_raw = [build_pl_vector(r, TUNED_DIMS) for r in recipes]
    v_raw = [build_v_vector(f, op_profiles, deploy_features, TUNED_DIMS) for f in all_b_folios]

    for i in range(n_recipes):
        for d, (_, _, sign) in enumerate(TUNED_DIMS):
            pl_raw[i][d] *= sign

    pl_resid = compute_residuals(pl_raw)
    v_resid = compute_residuals(v_raw)
    all_std = standardize(pl_resid + v_resid)
    pl_std = all_std[:n_recipes]
    v_std = all_std[n_recipes:]

    # Compute distance matrix (recipes x folios)
    print("\nComputing distance matrix...")
    dmat = [[0.0] * n_v for _ in range(n_recipes)]
    for i in range(n_recipes):
        for j in range(n_v):
            dmat[i][j] = math.sqrt(sum((pl_std[i][d] - v_std[j][d]) ** 2
                                        for d in range(n_dims)))

    # ================================================================
    # CALIBRATION: global distance distribution
    # ================================================================
    print()
    print("=" * 90)
    print("CALIBRATION: global distance distribution")
    print("=" * 90)

    all_distances = [dmat[i][j] for i in range(n_recipes) for j in range(n_v)]
    all_distances_sorted = sorted(all_distances)
    n_below_d1 = sum(1 for d in all_distances if d < D_THRESHOLD)
    n_below_d15 = sum(1 for d in all_distances if d < D_RELAXED)

    print(f"\nTotal (recipe, folio) pairs: {len(all_distances)}")
    print(f"  Min d: {min(all_distances):.4f}")
    print(f"  Median d: {all_distances_sorted[len(all_distances_sorted)//2]:.4f}")
    print(f"  Max d: {max(all_distances):.4f}")
    print(f"  d < 1.0 pairs: {n_below_d1} ({100*n_below_d1/len(all_distances):.2f}%)")
    print(f"  d < 1.5 pairs: {n_below_d15} ({100*n_below_d15/len(all_distances):.2f}%)")

    if n_below_d1 == 0:
        print("\n  WARNING: zero pairs at d<1.0. Threshold too strict for Antidotarium features.")
    elif n_below_d1 < 10:
        print("\n  NOTE: very few d<1.0 pairs. d<1.0 hits will be highly informative.")

    # ================================================================
    # PER-TARGET ANALYSIS: f104-105
    # ================================================================
    def report_folio(folio, label):
        if folio not in folio_idx:
            print(f"\n  {label} {folio}: NOT FOUND in Voynich folios")
            return None
        j = folio_idx[folio]
        # Distances from all recipes to this folio
        d_to_folio = [(i, dmat[i][j]) for i in range(n_recipes)]
        d_to_folio.sort(key=lambda x: x[1])
        n_d1 = sum(1 for _, d in d_to_folio if d < D_THRESHOLD)
        n_d15 = sum(1 for _, d in d_to_folio if d < D_RELAXED)
        return {
            "folio": folio, "label": label,
            "section": section_of(folio),
            "regime": regime_map.get(folio, "?"),
            "top5_recipes": [(recipes[i]["name"], dmat[i][j]) for i, _ in d_to_folio[:5]],
            "n_recipes_below_d1": n_d1,
            "n_recipes_below_d15": n_d15,
            "min_distance": d_to_folio[0][1],
        }

    print()
    print("=" * 90)
    print("TARGET FOLIOS: f104r, f104v, f105r, f105v (Section S 4-folio gap)")
    print("=" * 90)

    target_results = []
    for folio in TARGET_FOLIOS:
        r = report_folio(folio, "TARGET")
        if r:
            target_results.append(r)
            print(f"\n  {folio} (section={r['section']}, regime={r['regime']}):")
            print(f"    Min distance: {r['min_distance']:.4f}")
            print(f"    Recipes at d<1.0: {r['n_recipes_below_d1']}")
            print(f"    Recipes at d<1.5: {r['n_recipes_below_d15']}")
            print(f"    Top-5 closest Antidotarium recipes:")
            for name, d in r['top5_recipes']:
                marker = " <-- d<1.0" if d < D_THRESHOLD else (" (d<1.5)" if d < D_RELAXED else "")
                print(f"      {name:<20}  d={d:.4f}{marker}")

    # ================================================================
    # CONTROLS
    # ================================================================
    print()
    print("=" * 90)
    print("CONTROL: Section B alchemy folios (should NOT match Antidotarium)")
    print("=" * 90)
    section_b_results = []
    for folio in SECTION_B_ALCHEMY_CONTROL:
        r = report_folio(folio, "B_ALCHEMY_CTRL")
        if r:
            section_b_results.append(r)

    n_b_d1 = sum(r["n_recipes_below_d1"] for r in section_b_results)
    print(f"\n  Section B controls ({len(section_b_results)} folios):")
    print(f"    Total Antidotarium matches at d<1.0: {n_b_d1}")
    print(f"    Per-folio breakdown:")
    for r in section_b_results:
        if r["n_recipes_below_d1"] > 0 or r["min_distance"] < 1.5:
            print(f"      {r['folio']}: min_d={r['min_distance']:.3f}, d<1.0={r['n_recipes_below_d1']}, d<1.5={r['n_recipes_below_d15']}")
    if all(r["min_distance"] >= 1.5 for r in section_b_results):
        print(f"    All Section B controls have min_d >= 1.5 (no matches)")

    print()
    print("=" * 90)
    print("CONTROL: matched-S folios (PL Mercuriorum, should NOT match Antidotarium)")
    print("=" * 90)
    matched_s_results = []
    for folio in MATCHED_S_CONTROL:
        r = report_folio(folio, "MATCHED_S_CTRL")
        if r:
            matched_s_results.append(r)
    n_ms_d1 = sum(r["n_recipes_below_d1"] for r in matched_s_results)
    print(f"\n  matched-S controls ({len(matched_s_results)} folios):")
    print(f"    Total Antidotarium matches at d<1.0: {n_ms_d1}")
    print(f"    Per-folio breakdown:")
    for r in matched_s_results:
        if r["n_recipes_below_d1"] > 0 or r["min_distance"] < 1.5:
            print(f"      {r['folio']}: min_d={r['min_distance']:.3f}, d<1.0={r['n_recipes_below_d1']}, d<1.5={r['n_recipes_below_d15']}")
    if all(r["min_distance"] >= 1.5 for r in matched_s_results):
        print(f"    All matched-S controls have min_d >= 1.5 (no matches)")

    print()
    print("=" * 90)
    print("CONTROL: f57v anomaly")
    print("=" * 90)
    f57v_results = []
    for folio in F57V_CONTROL:
        r = report_folio(folio, "F57V_CTRL")
        if r:
            f57v_results.append(r)
            print(f"  {r['folio']}: min_d={r['min_distance']:.3f}, d<1.0={r['n_recipes_below_d1']}, d<1.5={r['n_recipes_below_d15']}")

    # ================================================================
    # VERDICT
    # ================================================================
    print()
    print("=" * 90)
    print("VERDICT")
    print("=" * 90)

    n_target_d1 = sum(r["n_recipes_below_d1"] for r in target_results)
    n_b_d1_total = sum(r["n_recipes_below_d1"] for r in section_b_results)
    n_ms_d1_total = sum(r["n_recipes_below_d1"] for r in matched_s_results)
    n_targets = len(target_results)
    n_b = len(section_b_results)
    n_ms = len(matched_s_results)

    target_rate = n_target_d1 / n_targets if n_targets else 0
    b_rate = n_b_d1_total / n_b if n_b else 0
    ms_rate = n_ms_d1_total / n_ms if n_ms else 0

    print(f"\n  d<1.0 matches per folio:")
    print(f"    Target (f104-105):    {n_target_d1} matches / {n_targets} folios = {target_rate:.2f} per folio")
    print(f"    B-alchemy control:    {n_b_d1_total} matches / {n_b} folios = {b_rate:.2f} per folio")
    print(f"    matched-S control:    {n_ms_d1_total} matches / {n_ms} folios = {ms_rate:.2f} per folio")

    if n_target_d1 == 0:
        verdict = ("FAIL: zero f104-105 folios have any Antidotarium recipe at d<1.0. "
                   "Antidotarium does not identify the Section S 4-folio gap source.")
    elif target_rate > max(b_rate, ms_rate) * 1.5:
        verdict = (f"PASS (specific): f104-105 has {target_rate:.2f} matches/folio at d<1.0 "
                   f"vs B-alchemy {b_rate:.2f} and matched-S {ms_rate:.2f} per folio. "
                   "Antidotarium matches are concentrated on target folios — candidate source identified.")
    elif n_target_d1 > 0 and target_rate <= max(b_rate, ms_rate) * 1.5:
        verdict = (f"INCONCLUSIVE (non-specific): f104-105 has {n_target_d1} d<1.0 matches "
                   "but controls show comparable density. Could be feature-space artifact, "
                   "not specific Section S identification.")
    else:
        verdict = "INCONCLUSIVE (unexpected pattern, manual review needed)"

    print(f"\n  {verdict}")

    out = {
        "method": "PHASE_704 Antidotarium Nicolai d<1.0 absolute-distance test for f104-105",
        "n_antidotarium_recipes": n_recipes,
        "n_voynich_folios": n_v,
        "d_thresholds": {"primary": D_THRESHOLD, "relaxed": D_RELAXED},
        "global_distance_distribution": {
            "min": min(all_distances),
            "median": all_distances_sorted[len(all_distances_sorted)//2],
            "max": max(all_distances),
            "n_below_d1": n_below_d1,
            "n_below_d15": n_below_d15,
            "total_pairs": len(all_distances),
        },
        "target_results": target_results,
        "section_b_control_results": section_b_results,
        "matched_s_control_results": matched_s_results,
        "f57v_control": f57v_results,
        "summary_rates": {
            "target_d1_per_folio": target_rate,
            "section_b_d1_per_folio": b_rate,
            "matched_s_d1_per_folio": ms_rate,
        },
        "verdict": verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
