"""PHASE_701: Lullian wheels combinatorial structure test on rosettes foldout.

PRE-REGISTERED HYPOTHESIS

Ramon Llull's Ars Magna uses 9 principles (B-K, skipping J) arranged in
concentric wheels with combinatorial all-to-all rotation generating pair
relationships. Pseudo-Lull alchemical tradition adopted this formalism.

If the Voynich 9-rosette foldout implements Lullian-style combinatorial
structure:

  H1 (Vocabulary distinctness): Each of the 9 rosettes has DISTINCT vocabulary,
     reflecting one principle each. Jaccard distance between rosette MIDDLE
     sets should be HIGH (>0.7) for non-adjacent pairs.

  H2 (9-fold partition): The 9 rosettes partition into 9 distinct clusters
     (not merging into smaller groups).

  H3 (All-to-all combinatorial pattern): Pairwise vocabulary overlap follows
     Lullian combinatorial structure — every pair of rosettes shares
     some specific vocabulary representing the BC/BD/CD/etc. combinations.

  H4 (Topology check): The connection topology between rosettes should be
     consistent with Lullian wheel rotation (all-to-all via rotation),
     NOT hub-and-spoke or network topology.

If H1-H3 PASS and H4 supports Lullian structure: rosettes implement Llull's
Ars Magna combinatorial system at the foldout level.

If H4 fails (hub-and-spoke confirmed): rosettes are NETWORK/TOPOLOGY diagram
(per existing C1128/C1130 project findings), NOT Lullian wheels.

If H1-H2 fail (rosettes share vocabulary heavily): generic indexing
hypothesis confirmed (per C1128).

DATA LIMITATIONS:
- Some rosette ring texts are NOT_TRANSCRIBED (NE, EAST, SW, SE)
- We can only test pairs where both have token data
- Affects statistical power but does not invalidate the test
"""
import json
import math
import sys, io
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("C:/git/voynich")


def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return 1.0 - inter / union if union else 0.0


def overlap_coefficient(set_a, set_b):
    """Size-normalized overlap: |A∩B| / min(|A|,|B|)"""
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / min(len(set_a), len(set_b))


def main():
    d = json.load(open(ROOT / "data/rosettes_unified.json", encoding="utf-8"))
    grid = d["rosette_grid"]
    topology = d["topology"]

    # =================================================================
    # STEP 1: Extract per-rosette MIDDLE sets and metadata
    # =================================================================
    rosette_data = {}
    for pos, info in grid.items():
        profile = info.get("combined_profile", {})
        n_tokens = profile.get("n_tokens", 0)
        unique_middles = set(profile.get("unique_middles", []))
        bridge_middles = set(profile.get("bridge_middles", []))
        nonbridge = set(profile.get("nonbridge_middles", []))
        kernel = profile.get("kernel", {})
        rosette_data[pos] = {
            "n_tokens": n_tokens,
            "type": info.get("type", "?"),
            "connects_to": info.get("connects_to", []),
            "unique_middles": unique_middles,
            "bridge_middles": bridge_middles,
            "nonbridge_middles": nonbridge,
            "kernel": kernel,
            "transcription_status": "FULL" if n_tokens >= 10 else "PARTIAL/MISSING",
        }

    print("="*70)
    print("PHASE_701: LULLIAN WHEELS COMBINATORIAL TEST")
    print("="*70)
    print()
    print("Per-rosette data inventory:")
    print(f"{'Position':>8} {'Type':>10} {'N tokens':>10} {'Unique MIDDLE':>15} {'Status':>10}")
    for pos in ["NW", "NORTH", "NE", "WEST", "CENTER", "EAST", "SW", "SOUTH", "SE"]:
        r = rosette_data.get(pos, {})
        print(f"{pos:>8} {r.get('type','?'):>10} {r.get('n_tokens','?'):>10} "
              f"{len(r.get('unique_middles', set())):>15} {r.get('transcription_status','?'):>10}")

    # Identify which rosettes have enough data for testing
    testable = [pos for pos in rosette_data if rosette_data[pos]["n_tokens"] >= 10]
    print(f"\nTestable rosettes (n_tokens >= 10): {testable}")
    print(f"Excluded due to insufficient data: {[p for p in rosette_data if p not in testable]}")

    # =================================================================
    # STEP 2: Pairwise MIDDLE distance matrix
    # =================================================================
    print("\n" + "="*70)
    print("H1: VOCABULARY DISTINCTNESS (Jaccard distances)")
    print("="*70)
    print()
    print("If Lullian: high distances expected (>0.7) — each rosette distinct")
    print("If generic indexing: lower distances expected (<0.5)")
    print()

    pairs = []
    for i, a in enumerate(testable):
        for b in testable[i+1:]:
            ma = rosette_data[a]["unique_middles"]
            mb = rosette_data[b]["unique_middles"]
            j = jaccard(ma, mb)
            oc = overlap_coefficient(ma, mb)
            connected = b in rosette_data[a]["connects_to"]
            pairs.append((a, b, j, oc, connected))

    print(f"{'Pair':>20} {'Jaccard':>9} {'Overlap':>9} {'Conn':>6}")
    print(f"{'-'*20} {'-'*9} {'-'*9} {'-'*6}")
    for a, b, j, oc, c in pairs:
        marker = " (CONNECTED)" if c else ""
        print(f"{a+'-'+b:>20} {j:>9.4f} {oc:>9.4f} {('Y' if c else 'N'):>6}{marker}")

    mean_jaccard = sum(j for _, _, j, _, _ in pairs) / len(pairs)
    print(f"\nMean Jaccard distance: {mean_jaccard:.4f}")
    print(f"H1 verdict: {'PASS (high distance, distinct)' if mean_jaccard > 0.7 else 'FAIL (vocabularies overlap)'}")

    # Connected vs unconnected pairs
    conn_jaccards = [j for _, _, j, _, c in pairs if c]
    unconn_jaccards = [j for _, _, j, _, c in pairs if not c]
    if conn_jaccards and unconn_jaccards:
        mean_conn = sum(conn_jaccards) / len(conn_jaccards)
        mean_unconn = sum(unconn_jaccards) / len(unconn_jaccards)
        print(f"\nConnected pairs: mean Jaccard = {mean_conn:.4f}")
        print(f"Unconnected pairs: mean Jaccard = {mean_unconn:.4f}")
        print(f"  If Lullian (combinatorial): connected pairs should have HIGHER overlap")
        print(f"    (because they share the combinatorial relationship)")
        print(f"  If hub-and-spoke topology: connection structure is geometric, vocab unrelated")

    # =================================================================
    # STEP 3: Topology check — is the connection structure Lullian?
    # =================================================================
    print("\n" + "="*70)
    print("H4: TOPOLOGY STRUCTURE")
    print("="*70)
    print()

    # Count edges
    edges = set()
    for pos, info in grid.items():
        for conn in info.get("connects_to", []):
            edge = tuple(sorted([pos, conn]))
            edges.add(edge)
    n_edges = len(edges)
    print(f"Total connections: {n_edges}")
    print(f"All edges: {sorted(edges)}")

    # If Lullian wheel: all pairs connected (9 nodes → C(9,2) = 36 edges)
    # If hub-and-spoke (1 center + 8 outer): CENTER ↔ 8 outer = 8 edges
    # If our observed pattern: spoke-with-ring = 12 edges (4 center-cardinal + 8 cardinal-corner)
    n_all_pairs = len(rosette_data) * (len(rosette_data) - 1) // 2
    print(f"All-to-all (Lullian): {n_all_pairs} edges expected")
    print(f"Hub-and-spoke (8 outer + center): 8 edges expected")
    print(f"Spoke-with-ring: 12 edges expected")
    print(f"Observed: {n_edges} edges")
    print()
    if n_edges >= n_all_pairs * 0.5:
        print("Topology: Approaching all-to-all → Lullian POSSIBLE")
        h4 = "PASS"
    elif n_edges == 8:
        print("Topology: Pure hub-and-spoke (CENTER↔outer)")
        h4 = "FAIL — not Lullian (hub structure)"
    elif n_edges == 12:
        print("Topology: Spoke-and-ring (CENTER↔cardinals, cardinals↔corners)")
        h4 = "FAIL — network/topology diagram, not Lullian wheel"
    else:
        print(f"Topology: Custom structure ({n_edges} edges)")
        h4 = f"AMBIGUOUS — {n_edges} edges does not match Lullian wheel pattern"
    print(f"H4 verdict: {h4}")

    # =================================================================
    # STEP 4: CENTER vs outer-8 distinction
    # =================================================================
    print("\n" + "="*70)
    print("CENTER vs OUTER-8 STRUCTURAL DISTINCTION")
    print("="*70)
    print()

    if "CENTER" in testable:
        center_middles = rosette_data["CENTER"]["unique_middles"]
        outer_pooled = set()
        for p in testable:
            if p != "CENTER":
                outer_pooled |= rosette_data[p]["unique_middles"]
        center_unique_to_center = center_middles - outer_pooled
        center_shared = center_middles & outer_pooled
        print(f"CENTER unique MIDDLEs: {len(center_middles)}")
        print(f"  Unique to CENTER (not in any outer): {len(center_unique_to_center)}")
        print(f"  Shared with at least one outer: {len(center_shared)}")
        if len(center_middles) > 0:
            print(f"  CENTER-distinctiveness: {len(center_unique_to_center)/len(center_middles):.2%}")

    # =================================================================
    # STEP 5: Are there 9 distinct clusters?
    # =================================================================
    print("\n" + "="*70)
    print("H2: 9-FOLD CLUSTER PARTITION")
    print("="*70)
    print()

    # Test: how many of the testable rosettes have vocabulary that distinguishes
    # them from all others?
    n_testable = len(testable)
    distinct_count = 0
    for pos in testable:
        own = rosette_data[pos]["unique_middles"]
        others_pooled = set()
        for other in testable:
            if other != pos:
                others_pooled |= rosette_data[other]["unique_middles"]
        unique_to_pos = own - others_pooled
        if len(unique_to_pos) >= 3:  # at least 3 unique MIDDLEs distinguishes
            distinct_count += 1
    print(f"Testable rosettes: {n_testable}")
    print(f"Rosettes with ≥3 unique MIDDLEs (not in any other): {distinct_count}")
    print(f"If Lullian 9-fold partition: expect 9/9 (or proportional for testable subset)")
    if n_testable >= 6:
        h2 = "PASS" if distinct_count / n_testable >= 0.7 else "FAIL"
    else:
        h2 = "INSUFFICIENT DATA"
    print(f"H2 verdict: {h2} ({distinct_count}/{n_testable} testable rosettes are distinct)")

    # =================================================================
    # FINAL VERDICT
    # =================================================================
    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print()
    print(f"  H1 (Vocabulary distinctness, mean Jaccard > 0.7): "
          f"{'PASS' if mean_jaccard > 0.7 else 'FAIL'} (mean = {mean_jaccard:.4f})")
    print(f"  H2 (9-fold partition, ≥70% distinct): {h2}")
    print(f"  H4 (Topology Lullian): {h4}")
    print()

    # Pre-registered decision
    if h4.startswith("FAIL") and mean_jaccard <= 0.7:
        verdict = "LULLIAN WHEELS HYPOTHESIS FALSIFIED"
        reasoning = ("Topology is network/hub-and-spoke (NOT Lullian wheel rotation). "
                     "Vocabulary overlap pattern does not show 9-fold combinatorial structure. "
                     "Rosettes function as topology/network diagram (consistent with project's "
                     "existing C1128/C1130 findings: generic indexing + random transition).")
    elif h4.startswith("FAIL") and mean_jaccard > 0.7:
        verdict = "PARTIAL: Topology not Lullian but vocabulary distinct"
        reasoning = ("Rosettes have distinct vocabulary per position but connection topology "
                     "is not Lullian wheel rotation. Each rosette may represent a distinct "
                     "category, but the combinatorial-wheel framework doesn't fit.")
    else:
        verdict = "INCONCLUSIVE — requires fuller transcription"
        reasoning = "Insufficient data to discriminate Lullian from alternatives."

    print(f"  VERDICT: {verdict}")
    print(f"  REASONING: {reasoning}")

    # Save
    OUT = ROOT / "phases/PHASE_701_LULLIAN_WHEELS/results/lullian_wheels_test.json"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "method": "Lullian wheels combinatorial structure test on rosettes foldout",
        "testable_rosettes": testable,
        "n_edges_observed": n_edges,
        "n_edges_lullian_expected": n_all_pairs,
        "mean_jaccard_distance": mean_jaccard,
        "h1_verdict": "PASS" if mean_jaccard > 0.7 else "FAIL",
        "h2_verdict": h2,
        "h4_verdict": h4,
        "final_verdict": verdict,
        "reasoning": reasoning,
        "pairs_data": [{"a": a, "b": b, "jaccard": j, "overlap": o, "connected": c}
                       for a, b, j, o, c in pairs],
    }, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
