"""
Phase 565 T5: Synthesis -- aggregate results, cross-phase comparison, verdict.

Reads:
  - t4_behavior_validation.json  (9 tests + 4 diagnostics)
  - t2_permeability_runs.json  (composite metrics: viability, Y_final, hazard)
  - t3_null_ablation_runs.json  (reference runs for composite metrics)
  - t1_permeability_apparatus.json (apparatus config for parameter values)

Writes:
  - t5_synthesis.json

Verdict logic:
  - PERMEABILITY_CALIBRATION_VALIDATED: P1+P2+P3+P7 all PASS, D1/D2 OK, plus >=1 of P4/P6/P8
  - PARTIAL_PERMEABILITY: P2 strong, non-degeneracy restored, but cycling (P3) or routing (P4) still weak
  - PERMEABILITY_FAILED: viability still universal/near-universal, or null destruction still absent,
    or no improvement over 564b
"""

import json
import os
from datetime import datetime

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, "results")

# -- Load inputs --------------------------------------------------------------

with open(os.path.join(RESULTS_DIR, "t4_behavior_validation.json")) as f:
    t4 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t2_permeability_runs.json")) as f:
    t2 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t3_null_ablation_runs.json")) as f:
    t3 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t1_permeability_apparatus.json")) as f:
    t1 = json.load(f)

tests = t4["tests"]
diag = t4["diagnostics"]

# -- Extract test pass/fail ----------------------------------------------------

test_results = {
    "P1": tests["P1"]["pass"],
    "P2": tests["P2"]["pass"],
    "P3": tests["P3"]["pass"],
    "P4": tests["P4"]["pass"],
    "P5": tests["P5"]["pass"],
    "P6": tests["P6"]["pass"],
    "P7": tests["P7"]["pass"],
    "P8": tests["P8"]["pass"],
    "P9": tests["P9"]["pass"],  # None = SEC
}

n_pass = sum(1 for v in test_results.values() if v is True)
n_fail = sum(1 for v in test_results.values() if v is not True)  # None (SEC) counts as not-pass

# -- Phase 563, 563b, 564, 564b reference results -----------------------------

results_563 = {
    "P1": True, "P2": True, "P3": False, "P4": False,
    "P5": False, "P6": True, "P7": True, "P8": True, "P9": None
}

results_563b = {
    "P1": False, "P2": True, "P3": False, "P4": False,
    "P5": False, "P6": True, "P7": False, "P8": True, "P9": None
}

results_564 = {
    "P1": False, "P2": True, "P3": False, "P4": False,
    "P5": False, "P6": False, "P7": False, "P8": True, "P9": None
}

results_564b = {
    "P1": False, "P2": True, "P3": False, "P4": False,
    "P5": False, "P6": False, "P7": False, "P8": True, "P9": None
}

# -- Cross-phase comparison table ----------------------------------------------

def pass_str(v):
    if v is True:
        return "PASS"
    if v is False:
        return "FAIL"
    return "SEC"

comparison = {}
for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]:
    comparison[t] = {
        "563": pass_str(results_563[t]),
        "563b": pass_str(results_563b[t]),
        "564": pass_str(results_564[t]),
        "564b": pass_str(results_564b[t]),
        "565": pass_str(test_results[t]),
    }

# -- Regressions and improvements ---------------------------------------------

regressions_563 = []
improvements_563 = []
regressions_563b = []
improvements_563b = []
regressions_564 = []
improvements_564 = []
regressions_564b = []
improvements_564b = []

for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]:
    # vs 563
    if results_563[t] is True and test_results[t] is not True:
        regressions_563.append(t)
    if results_563[t] is not True and test_results[t] is True:
        improvements_563.append(t)
    # vs 563b
    if results_563b[t] is True and test_results[t] is not True:
        regressions_563b.append(t)
    if results_563b[t] is not True and test_results[t] is True:
        improvements_563b.append(t)
    # vs 564
    if results_564[t] is True and test_results[t] is not True:
        regressions_564.append(t)
    if results_564[t] is not True and test_results[t] is True:
        improvements_564.append(t)
    # vs 564b
    if results_564b[t] is True and test_results[t] is not True:
        regressions_564b.append(t)
    if results_564b[t] is not True and test_results[t] is True:
        improvements_564b.append(t)

# -- Verdict -------------------------------------------------------------------

# PERMEABILITY_CALIBRATION_VALIDATED: P1+P2+P3+P7 all PASS, D1/D2 OK, plus >=1 of P4/P6/P8
core_pass = all(test_results[t] for t in ["P1", "P2", "P3", "P7"])
d1_ok = not diag["D1"].get("quasi_gate_failed", True)
d2_ok = not diag["D2"].get("quasi_gate_failed", True)
secondary_pass = any(test_results[t] for t in ["P4", "P6", "P8"])

# PARTIAL_PERMEABILITY: P2 strong, non-degeneracy RESTORED (P1 pass or close), but cycling/routing still weak
p2_pass = test_results["P2"]
p1_pass = test_results["P1"]
p7_pass = test_results["P7"]

# Non-degeneracy "restored" means P1b passes (mean viability in band AND enough folios < 1.0)
p1b_pass = tests["P1"]["P1b"]["pass"]

# Check for improvement over 564b: more tests pass, or viability moved meaningfully
n_564b_pass = 2  # 564b passed 2/9
score_improved = n_pass > n_564b_pass

if core_pass and d1_ok and d2_ok and secondary_pass:
    verdict = "PERMEABILITY_CALIBRATION_VALIDATED"
elif p2_pass and p1b_pass and not p7_pass:
    # P2 strong, non-degeneracy restored (viability in band), but null destruction still weak
    verdict = "PARTIAL_PERMEABILITY"
else:
    # viability still universal/near-universal, OR null destruction absent, OR no improvement
    verdict = "PERMEABILITY_FAILED"

# -- Key metrics extraction ----------------------------------------------------

p1_full_gt_b2 = tests["P1"]["P1a"]["full_gt_B2"]
p1_full_gt_n1 = tests["P1"]["P1a"]["full_gt_N1"]
p1_mean_viab = tests["P1"]["P1b"]["mean_viability"]
p1_folios_lt_1 = tests["P1"]["P1b"]["folios_lt_1"]
p2_n_sig = tests["P2"]["n_significant"]
p3_mean_cycles = tests["P3"]["mean_cycles"]
p3_bounded_frac = tests["P3"]["mean_bounded_fraction"]
p3_n_meeting = tests["P3"]["n_meeting_both"]
p7_null_destroyed = tests["P7"]["null_types_destroyed"]
p8_preferred_best = tests["P8"]["preferred_best"]
d1_ratio = diag["D1"]["mean_corridor_ratio"]
d2_occ = diag["D2"]["mean_corridor_occupancy"]
d3_delta = diag["D3"]["mean_viab_delta"]
d3_n_gt = diag["D3"]["n_full_gt_B9"]
d4_pass = not diag["D4"].get("quasi_gate_failed", True)
d4_ratio = diag["D4"].get("full_null_ratio", 0)

# -- Verdict rationale ---------------------------------------------------------

# Extract BETA values from apparatus config
beta1 = t1["apparatus_config"].get("BETA1", {})
beta2 = t1["apparatus_config"].get("BETA2", {})
beta1_x = beta1.get("X", "N/A")
beta2_x = beta2.get("X", "N/A")

# Compute total hazard events from reference runs
ref = t3["reference"]
total_hazard_565 = sum(ref[f]["n_hazard_events"] for f in ref)

verdict_rationale = (
    f"{verdict}: {n_pass}/9 tests pass (P2, P8), same score as Phase 564b. "
    f"The graduated edge calibration (BETA1_X={beta1_x}, BETA2_X={beta2_x}, down from 564b's BETA_X=80.0) "
    f"successfully made the edge permeable: {total_hazard_565} total hazard events "
    f"(vs 1 in 564b, 0 in 564). Mean viability={p1_mean_viab:.6f}, "
    f"{p1_folios_lt_1}/20 folios with viability<1.0 (need >=8). "
    f"D1 OK (ratio={d1_ratio:.2f}), D2 OK (occupancy={d2_occ:.1%}), D3 OK (B9 delta=+{d3_delta:.3f}). "
    f"However, P1 fails: mean viability {p1_mean_viab:.4f} exceeds the 0.995 ceiling, "
    f"full_gt_B2={p1_full_gt_b2}/20 (threshold 14). "
    f"The B2 paradox: zero-contribution baseline achieves viability=1.0 for ALL folios. "
    f"The supervisory signal CAUSES hazard events rather than preventing them. "
    f"P7 fails: {p7_null_destroyed}/4 null types destroyed; null viabilities are actually "
    f"HIGHER than reference for many folios because shuffling disrupts constructive alignment, "
    f"producing FEWER hazard events. "
    f"D4 fails: edge contact is indiscriminate (full/null ratio={d4_ratio:.3f}). "
    f"The discrimination axis is inverted: stronger signals produce MORE hazard, not less."
)

# -- Summary table -------------------------------------------------------------

p2_max_H = max(tests["P2"]["per_sv"][sv]["H"] for sv in tests["P2"]["per_sv"])
p2_max_sv = max(tests["P2"]["per_sv"], key=lambda sv: tests["P2"]["per_sv"][sv]["H"])

# P5 key metric -- handle different field names between phases
p5a = tests["P5"]["P5a"]
p5_c_key = "C_differs" if "C_differs" in p5a else "C_better"
p5_s_key = "S_differs" if "S_differs" in p5a else "S_better"
p5_c_count = p5a.get(p5_c_key, 0)
p5_s_count = p5a.get(p5_s_key, 0)
p5_n_config = p5a.get("n_config_folios", 20)

# P5b -- handle single-H structure or C/S split
if "H" in tests["P5"]["P5b"]:
    p5b_stat = f"H={tests['P5']['P5b']['H']:.4f}, p={tests['P5']['P5b']['p']:.3f}"
elif "C" in tests["P5"]["P5b"]:
    p5b_c = tests["P5"]["P5b"]["C"]
    p5b_s = tests["P5"]["P5b"]["S"]
    p5b_stat = f"C: H={p5b_c['H']:.4f},p={p5b_c['p']:.3f}; S: H={p5b_s['H']:.4f},p={p5b_s['p']:.3f}"
else:
    p5b_stat = "N/A"

summary_table = {
    "P1_viable_envelope": {
        "pass": test_results["P1"],
        "key_metric": (
            f"full_gt_B2={p1_full_gt_b2}/20, full_gt_N1={p1_full_gt_n1}/20; "
            f"mean_viab={p1_mean_viab:.6f}, folios_lt_1={p1_folios_lt_1}/20 (need >=8)"
        )
    },
    "P2_packet_shape": {
        "pass": test_results["P2"],
        "key_metric": f"n_significant={p2_n_sig}/7 SVs; strongest H={p2_max_H:.1f} ({p2_max_sv})"
    },
    "P3_bounded_cycles": {
        "pass": test_results["P3"],
        "key_metric": (
            f"mean_cycles={p3_mean_cycles:.2f}, "
            f"bounded_frac={p3_bounded_frac:.3f}, "
            f"n_meeting_both={p3_n_meeting}/20"
        )
    },
    "P4_routing_consequence": {
        "pass": test_results["P4"],
        "key_metric": (
            f"P4a: {tests['P4']['P4a']['n_correct']}/4 correct; "
            f"P4b: viab_delta={tests['P4']['P4b']['full_vs_B4_viab_delta']:.5f}"
        )
    },
    "P5_headless_config": {
        "pass": test_results["P5"],
        "key_metric": (
            f"P5a: {p5_c_key}={p5_c_count}/{p5_n_config}, "
            f"{p5_s_key}={p5_s_count}/{p5_n_config}; "
            f"P5b: {p5b_stat}"
        )
    },
    "P6_cts_closure": {
        "pass": test_results["P6"],
        "key_metric": (
            f"viab_better={tests['P6']['viab_better']}/20, "
            f"C_sep_positive={tests['P6']['C_sep_positive']}/20; "
            "full=B3 identical (CTS has no effect when edge contact is indiscriminate)"
        )
    },
    "P7_null_destruction": {
        "pass": test_results["P7"],
        "key_metric": (
            f"null_types_destroyed={p7_null_destroyed}/4; "
            f"N1 mean_delta={tests['P7']['details']['N1']['mean_delta']:.6f}, "
            f"N3 mean_delta={tests['P7']['details']['N3']['mean_delta']:.6f} "
            "(nulls have HIGHER viability than full model for some folios)"
        )
    },
    "P8_profile_superiority": {
        "pass": test_results["P8"],
        "key_metric": (
            f"preferred_best={p8_preferred_best}/20 "
            f"(threshold={tests['P8']['threshold']})"
        )
    },
    "P9_section_template": {
        "pass": test_results["P9"],
        "key_metric": (
            f"n_significant={tests['P9']['n_significant']}/7 SVs; SECONDARY"
        )
    }
}

# -- Composite metrics from T3 reference runs ---------------------------------

viabilities = []
y_finals = []
hazard_counts = []
n_perfect_viab = 0

for folio, data in ref.items():
    viabilities.append(data["viability"])
    y_finals.append(data["Y_final"])
    hazard_counts.append(data["n_hazard_events"])
    if data["viability"] == 1.0:
        n_perfect_viab += 1

mean_viab = sum(viabilities) / len(viabilities) if viabilities else 0
mean_y = sum(y_finals) / len(y_finals) if y_finals else 0
total_hazard = sum(hazard_counts)
n_folios = len(viabilities)

composite_metrics = {
    "mean_viability": round(mean_viab, 6),
    "mean_Y_final": round(mean_y, 4),
    "total_hazard_events": total_hazard,
    "folios_with_perfect_viability": f"{n_perfect_viab}/{n_folios}",
    "mean_corridor_occupancy": round(d2_occ, 4),
    "mean_corridor_signal_ratio": round(d1_ratio, 2),
    "B9_mean_viab_delta": round(d3_delta, 3),
    "comparison": {
        "563": {
            "mean_viability": 0.9616,
            "mean_Y_final": 0.878,
            "total_hazard": 34,
            "perfect_viab": "4/7"
        },
        "563b": {
            "mean_viability": 0.9635,
            "mean_Y_final": 0.848,
            "total_hazard": 255,
            "perfect_viab": "12/20"
        },
        "564": {
            "mean_viability": 1.0,
            "mean_Y_final": 0.7366,
            "total_hazard": 0,
            "perfect_viab": "20/20"
        },
        "564b": {
            "mean_viability": 0.99985,
            "mean_Y_final": 0.5686,
            "total_hazard": 1,
            "perfect_viab": "19/20",
            "corridor_occupancy": 0.1867,
            "signal_ratio": 6.05,
            "B9_delta": 0.125
        },
        "565": {
            "mean_viability": round(mean_viab, 6),
            "mean_Y_final": round(mean_y, 4),
            "total_hazard": total_hazard,
            "perfect_viab": f"{n_perfect_viab}/{n_folios}",
            "corridor_occupancy": round(d2_occ, 4),
            "signal_ratio": round(d1_ratio, 2),
            "B9_delta": round(d3_delta, 3)
        }
    }
}

# -- Diagnostic status ---------------------------------------------------------

diagnostic_status = {
    "D1_signal_ratio": {
        "status": "OK" if not diag["D1"].get("quasi_gate_failed", True) else "FAILED",
        "value": round(d1_ratio, 2),
        "quasi_gate": "PASS" if not diag["D1"].get("quasi_gate_failed", True) else "FAIL",
        "per_sv": {sv: round(diag["D1"]["per_sv"][sv]["ratio"], 4)
                   for sv in diag["D1"]["per_sv"]}
    },
    "D2_corridor_occupancy": {
        "status": "OK" if not diag["D2"].get("quasi_gate_failed", True) else "FAILED",
        "value": round(d2_occ, 4),
        "quasi_gate": "PASS" if not diag["D2"].get("quasi_gate_failed", True) else "FAIL",
        "per_sv": {sv: round(diag["D2"]["per_sv"][sv]["corridor"], 4)
                   for sv in diag["D2"]["per_sv"]}
    },
    "D3_B9_comparison": {
        "status": "INFORMATIVE",
        "mean_delta": round(d3_delta, 3),
        "n_full_gt_B9": d3_n_gt,
        "expectation_threshold": 0.05,
        "above_threshold": d3_delta >= 0.05,
        "largest_drops": []
    },
    "D4_edge_contact_audit": {
        "status": "FAILED" if diag["D4"].get("quasi_gate_failed", True) else "OK",
        "quasi_gate": "FAIL" if diag["D4"].get("quasi_gate_failed", True) else "PASS",
        "full_model_mean_contacts_per_folio": diag["D4"]["full_model"]["mean_per_folio"],
        "null_grand_mean_contacts_per_folio": diag["D4"]["null_grand_mean_per_folio"],
        "full_null_ratio": diag["D4"]["full_null_ratio"],
        "cond1_not_all_zero": diag["D4"]["conditions"]["cond1_not_all_zero"],
        "cond2_not_indiscriminate": diag["D4"]["conditions"]["cond2_not_indiscriminate"],
        "finding": (
            "Edge contact IS happening (cond1 pass) but is indiscriminate between "
            f"full model ({diag['D4']['full_model']['mean_per_folio']:.1f}/folio) and "
            f"nulls ({diag['D4']['null_grand_mean_per_folio']:.1f}/folio). "
            f"Full/null ratio={diag['D4']['full_null_ratio']:.3f} -- "
            "packet alignment does not determine who reaches the edge."
        )
    }
}

# Extract the largest B9 viability drops for D3
d3_data = diag["D3"]["per_folio"]
drops = sorted(d3_data, key=lambda x: x["viab_delta"], reverse=True)
for drop in drops[:5]:
    diagnostic_status["D3_B9_comparison"]["largest_drops"].append({
        "folio": drop["folio"],
        "full_viab": drop["full_viab"],
        "B9_viab": drop["B9_viab"],
        "viab_delta": round(drop["viab_delta"], 3)
    })

# -- Folios with viab < 1.0: which profiles? ----------------------------------

folios_lt_1 = {}
for folio, data in tests["P1"]["per_folio"].items():
    if data["full_viab"] < 1.0:
        # Find profile from P8
        p8_data = tests["P8"]["per_folio"].get(folio, {})
        profile = p8_data.get("preferred_profile", "unknown")
        folios_lt_1[folio] = {
            "viability": data["full_viab"],
            "profile": profile,
            "b2_viab": data["b2_viab"],
            "n1_viab_mean": data["n1_viab_mean"]
        }

# -- B2 paradox analysis ------------------------------------------------------

b2_paradox = {
    "description": (
        "B2 (zero contributions) achieves viability=1.0 for ALL folios. "
        "The supervisory signal CAUSES hazard events rather than preventing them. "
        "The plant currently penalizes strong signals rather than rewarding aligned ones. "
        "The model with no input is the safest."
    ),
    "full_model_mean_viab": round(mean_viab, 6),
    "b2_viab_all_folios": 1.0,
    "folios_where_full_lt_b2": sum(
        1 for f, d in tests["P1"]["per_folio"].items()
        if d["full_viab"] < d["b2_viab"]
    ),
    "implication": (
        "The discrimination axis is inverted. Structured input produces MORE excursion "
        "and MORE hazard than zero input. For P1/P7 to work, the plant needs a mechanism "
        "where structured input REDUCES hazard exposure compared to random/absent input."
    )
}

# -- Lessons learned -----------------------------------------------------------

lessons_learned = [
    (
        f"The graduated edge IS now permeable: {total_hazard} hazard events vs 1 in 564b "
        f"vs 0 in 564. BETA1_X={beta1_x}/BETA2_X={beta2_x} (down from 564b's BETA_X=80.0) "
        f"allow state variables to reach and breach hazard boundaries. The edge permeability "
        f"calibration succeeded in its primary objective."
    ),
    (
        f"B9 ablation delta remains strong at +{d3_delta:.3f} (vs +0.125 in 564b). "
        f"Zone architecture is confirmed across two parametric regimes: the selective "
        f"restoration geometry is load-bearing regardless of edge stiffness."
    ),
    (
        f"P2 packet shape ({p2_n_sig}/7 significant) passes for the fifth consecutive phase "
        f"(563, 563b, 564, 564b, 565). This is the most robust coupling signal in the "
        f"entire apparatus line, surviving five different parametric regimes and two "
        f"architectural changes. SPEC/WORK/CLOSE differentiation is genuinely architecture-independent."
    ),
    (
        "The B2 paradox reveals a fundamental calibration problem: the supervisory signal "
        "CAUSES hazard events rather than preventing them. B2 (zero contributions) achieves "
        "viability=1.0 for ALL folios while the full model produces hazard events in 6/20. "
        "The discrimination axis is inverted: stronger signals produce MORE hazard, not less."
    ),
    (
        "P7 null failure has a specific mechanism: shuffled nulls produce WEAKER effective "
        "signals (because shuffling disrupts constructive alignment between supervisory "
        "contributions) which means FEWER hazard events. Null viabilities are actually "
        "HIGHER than reference for many folios. To make P7 work, the plant needs a mechanism "
        "where structured input REDUCES hazard exposure compared to random input."
    ),
    (
        "D4 edge contact is indiscriminate: full model and nulls contact edges at similar "
        f"rates (ratio={d4_ratio:.3f}). The graduated edge is being reached, but packet "
        "alignment does not determine WHO reaches it."
    ),
    (
        "The fundamental calibration challenge is now clear. 563 was too loose (viab=0.96), "
        "564/564b were impenetrable (viab=1.0), and 565 is in between (viab=0.997) but the "
        "discrimination axis is wrong. The needed insight: packet-aligned signals should "
        "produce bounded excursions that AVOID hazard through coordinated CLOSE recovery, "
        "while misaligned signals should produce unbounded excursions that hit hazard "
        "boundaries. Currently the CLOSE recovery mechanism (discharge events, thermal "
        "recovery) is too weak to differentiate."
    ),
    (
        "What must change: discharge events during CLOSE need to be strong enough that a "
        "properly aligned trace (SPEC->WORK->CLOSE) recovers from WORK excursions before "
        "hitting hazard, while a misaligned trace (WORK during CLOSE, etc.) does not recover. "
        "This means discharge rates need to increase significantly, or the relationship "
        "between packet phase and edge approach needs to change."
    ),
]

# -- Build output --------------------------------------------------------------

output = {
    "metadata": {
        "phase": "565",
        "task": "T5_synthesis",
        "phase_name": "VIRTUAL_APPARATUS_PERMEABILITY_CALIBRATION",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "verdict": verdict,
        "n_tests_total": 9,
        "n_tests_pass": n_pass,
        "n_tests_fail": n_fail,
        "n_constraints_proposed": 0
    },
    "verdict_rationale": verdict_rationale,
    "comparison_563_vs_563b_vs_564_vs_564b_vs_565": comparison,
    "regressions": {
        "from_563": regressions_563,
        "from_563b": regressions_563b,
        "from_564": regressions_564,
        "from_564b": regressions_564b,
    },
    "improvements": {
        "from_563": improvements_563,
        "from_563b": improvements_563b,
        "from_564": improvements_564,
        "from_564b": improvements_564b,
    },
    "summary_table": summary_table,
    "composite_metrics": composite_metrics,
    "diagnostic_status": diagnostic_status,
    "folios_with_viab_lt_1": folios_lt_1,
    "b2_paradox": b2_paradox,
    "lessons_learned": lessons_learned,
    "constraints_note": (
        f"{verdict}: no new constraints. This phase proves the edge IS now permeable "
        f"({total_hazard} hazard events) but reveals that the discrimination axis is inverted: "
        "structured supervisory input produces MORE hazard than absent or random input. "
        "The CLOSE recovery mechanism needs strengthening to invert this relationship."
    ),
    "implications_for_next_phase": [
        (
            "Strengthen CLOSE recovery mechanism: discharge events during CLOSE must be "
            "powerful enough that a properly aligned trace (SPEC->WORK->CLOSE) recovers "
            "from WORK excursions before hitting hazard boundaries. Currently discharge "
            "magnitudes are too small to produce measurable recovery."
        ),
        (
            "Invert the discrimination axis: the plant must reward packet alignment, not "
            "penalize signal strength. A well-aligned trace should produce BOUNDED "
            "excursions (WORK pushes out, CLOSE pulls back) that stay below hazard. "
            "A misaligned trace should produce UNBOUNDED excursions (WORK pushes out, "
            "CLOSE fails to recover) that breach hazard."
        ),
        (
            "Consider phase-asymmetric edge stiffness: during CLOSE, increase effective "
            "restoring force (helping recovery). During WORK, decrease it (allowing "
            "exploration). This creates a natural asymmetry where CLOSE phases pull "
            "state back from edges while WORK phases allow approach."
        ),
        (
            "The basin/corridor/edge geometry is confirmed correct across two parametric "
            "regimes. Do NOT change zone boundaries or D1/D2 corridor dynamics. The "
            "problem is exclusively in how CLOSE recovery interacts with edge approach."
        ),
        (
            "Cross-phase score trajectory: 5/9 -> 3/9 -> 2/9 -> 2/9 -> 2/9. "
            "The score has plateaued but the nature of failure has changed from "
            "'everything wrong' (564) to 'edge impenetrable' (564b) to 'edge permeable "
            "but discrimination inverted' (565). Each phase narrows the problem."
        ),
    ]
}

# -- Write output --------------------------------------------------------------

out_path = os.path.join(RESULTS_DIR, "t5_synthesis.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=1)

# -- Print summary -------------------------------------------------------------

print(f"Phase 565 T5 Synthesis")
print(f"=" * 70)
print(f"Verdict: {verdict}")
print(f"Tests: {n_pass}/9 pass, {n_fail}/9 fail")
print()

print("Cross-phase comparison:")
print(f"  {'Test':<6} {'563':<6} {'563b':<6} {'564':<6} {'564b':<6} {'565':<6}")
print(f"  {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]:
    c = comparison[t]
    print(f"  {t:<6} {c['563']:<6} {c['563b']:<6} {c['564']:<6} {c['564b']:<6} {c['565']:<6}")

print()
print(f"Regressions from 563:  {regressions_563}")
print(f"Improvements from 563: {improvements_563}")
print(f"Regressions from 564b: {regressions_564b}")
print(f"Improvements from 564b: {improvements_564b}")

print()
print("Composite metrics:")
print(f"  Mean viability: {composite_metrics['mean_viability']}")
print(f"  Mean Y_final:   {composite_metrics['mean_Y_final']}")
print(f"  Total hazard:   {composite_metrics['total_hazard_events']}")
print(f"  Perfect viab:   {composite_metrics['folios_with_perfect_viability']}")
print(f"  Corridor occ:   {composite_metrics['mean_corridor_occupancy']}")
print(f"  Signal ratio:   {composite_metrics['mean_corridor_signal_ratio']}")
print(f"  B9 viab delta:  {composite_metrics['B9_mean_viab_delta']}")

print()
print("Diagnostic status:")
print(f"  D1 signal ratio:       {diagnostic_status['D1_signal_ratio']['status']} "
      f"(ratio={diagnostic_status['D1_signal_ratio']['value']})")
print(f"  D2 corridor occupancy: {diagnostic_status['D2_corridor_occupancy']['status']} "
      f"(occupancy={diagnostic_status['D2_corridor_occupancy']['value']})")
print(f"  D3 B9 comparison:      {diagnostic_status['D3_B9_comparison']['status']} "
      f"(mean_delta={diagnostic_status['D3_B9_comparison']['mean_delta']}, "
      f"n_full_gt_B9={diagnostic_status['D3_B9_comparison']['n_full_gt_B9']})")
print(f"  D4 edge contact audit: {diagnostic_status['D4_edge_contact_audit']['status']} "
      f"(ratio={diagnostic_status['D4_edge_contact_audit']['full_null_ratio']})")

print()
print("B9 largest viability drops:")
for drop in diagnostic_status["D3_B9_comparison"]["largest_drops"]:
    print(f"  {drop['folio']}: {drop['full_viab']:.3f} -> {drop['B9_viab']:.3f} "
          f"(delta={drop['viab_delta']:.3f})")

print()
print("Folios with viability < 1.0:")
for folio, data in sorted(folios_lt_1.items(), key=lambda x: x[1]["viability"]):
    print(f"  {folio}: viab={data['viability']:.5f}, profile={data['profile']}, "
          f"b2_viab={data['b2_viab']:.5f}, n1_mean={data['n1_viab_mean']:.5f}")

print()
print("B2 paradox:")
print(f"  Full model mean viability: {b2_paradox['full_model_mean_viab']}")
print(f"  B2 viability (all folios): {b2_paradox['b2_viab_all_folios']}")
print(f"  Folios where full < B2: {b2_paradox['folios_where_full_lt_b2']}/20")

print()
print(f"Constraints proposed: 0")
print(f"Output: {out_path}")
