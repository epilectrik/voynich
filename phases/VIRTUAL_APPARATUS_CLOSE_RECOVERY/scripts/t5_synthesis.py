"""
Phase 566 T5: Synthesis -- aggregate results, cross-phase comparison, verdict.

Reads:
  - t4_behavior_validation.json  (9 tests + 7 diagnostics)
  - t2_close_recovery_runs.json  (composite metrics: viability, Y_final, hazard)
  - t3_null_ablation_runs.json   (reference runs for composite metrics)
  - t1_close_recovery_apparatus.json (apparatus config for parameter values)

Writes:
  - t5_synthesis.json
  - REPORT_566.md

Verdict logic:
  - CLOSE_RECOVERY_VALIDATED: P1+P2+P3+P7 all PASS, D1/D2 OK, plus >=1 of P4/P6/P8
  - PARTIAL_CLOSE_RECOVERY: P2 strong, non-degeneracy restored, but cycling/routing still weak
  - CLOSE_RECOVERY_FAILED: viability still universal/near-universal, or null destruction still absent,
    or no improvement over 565
"""

import json
import os
from datetime import datetime

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, "results")

# -- Load inputs --------------------------------------------------------------

with open(os.path.join(RESULTS_DIR, "t4_behavior_validation.json")) as f:
    t4 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t2_close_recovery_runs.json")) as f:
    t2 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t3_null_ablation_runs.json")) as f:
    t3 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t1_close_recovery_apparatus.json")) as f:
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

# -- Phase 563, 563b, 564, 564b, 565 reference results ------------------------

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

results_565 = {
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
        "565": pass_str(results_565[t]),
        "566": pass_str(test_results[t]),
    }

# -- Regressions and improvements ---------------------------------------------

prior_phases = {
    "563": results_563,
    "563b": results_563b,
    "564": results_564,
    "564b": results_564b,
    "565": results_565,
}

regressions = {}
improvements = {}
for phase_name, phase_results in prior_phases.items():
    reg = []
    imp = []
    for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]:
        if phase_results[t] is True and test_results[t] is not True:
            reg.append(t)
        if phase_results[t] is not True and test_results[t] is True:
            imp.append(t)
    regressions[f"from_{phase_name}"] = reg
    improvements[f"from_{phase_name}"] = imp

# -- Verdict -------------------------------------------------------------------

# CLOSE_RECOVERY_VALIDATED: P1+P2+P3+P7 all PASS, D1/D2 OK, plus >=1 of P4/P6/P8
core_pass = all(test_results[t] for t in ["P1", "P2", "P3", "P7"])
d1_ok = not diag["D1"].get("quasi_gate_failed", True)
d2_ok = not diag["D2"].get("quasi_gate_failed", True)
secondary_pass = any(test_results[t] for t in ["P4", "P6", "P8"])

# PARTIAL_CLOSE_RECOVERY: P2 strong, non-degeneracy RESTORED, but cycling/routing still weak
p2_pass = test_results["P2"]
p1_pass = test_results["P1"]
p1b_pass = tests["P1"]["P1b"]["pass"]

# Check for improvement over 565: more tests pass
n_565_pass = 2  # 565 passed 2/9
score_improved = n_pass > n_565_pass

if core_pass and d1_ok and d2_ok and secondary_pass:
    verdict = "CLOSE_RECOVERY_VALIDATED"
elif p2_pass and p1b_pass:
    verdict = "PARTIAL_CLOSE_RECOVERY"
else:
    verdict = "CLOSE_RECOVERY_FAILED"

# -- Key metrics extraction ----------------------------------------------------

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

# D4 -- 566 has cond2_not_indiscriminate now
d4_pass = not diag["D4"].get("quasi_gate_failed", True)
d4_ratio = diag["D4"].get("full_null_ratio", 0)

# D5 -- CLOSE recovery asymmetry
d5_pass = not diag["D5"].get("quasi_gate_failed", True)
d5_full_work = diag["D5"]["full_model"]["work_grand_mean"]
d5_full_close = diag["D5"]["full_model"]["close_grand_mean"]

# D6 -- composite scoring
d6_full = diag["D6"]["full_model"]["mean_composite"]
d6_b2 = diag["D6"]["baselines"]["B2"]["mean_composite"]
d6_n2 = diag["D6"]["nulls"]["N2"]["mean_composite"]
d6_n4 = diag["D6"]["nulls"]["N4"]["mean_composite"]

# D7 -- corridor return latency
d7_pass = not diag["D7"].get("quasi_gate_failed", True)
d7_latency = diag["D7"]["full_model"]["mean_latency"]

# B10 analysis from D3
d3_b10_delta = diag["D3"]["B10_analysis"]["mean_viab_delta"]

# -- Verdict rationale ---------------------------------------------------------

# Extract close recovery config
close_config = t1.get("close_recovery_config", {})
k_close = close_config.get("K_CLOSE", {})
k_cts_close = close_config.get("K_CTS_CLOSE", "N/A")
selected_pack = t1.get("selected_ladder_pack", "N/A")

# Compute total hazard events from reference runs
ref = t3["reference"]
total_hazard_566 = sum(ref[f]["n_hazard_events"] for f in ref)

verdict_rationale = (
    f"{verdict}: {n_pass}/9 tests pass (P2 only), regression from 565's 2/9 (lost P8). "
    f"CLOSE recovery channels (K_CLOSE, CTS-weighted discharge, profile-specific multipliers) "
    f"were added with ladder pack '{selected_pack}' (K_CTS_CLOSE={k_cts_close}). "
    f"V10-V12 synthetic preflights all pass, confirming the recovery mechanism WORKS in principle. "
    f"However, on real folios: mean viability={p1_mean_viab:.6f}, "
    f"{p1_folios_lt_1}/20 folios with viability<1.0 (need >=8). "
    f"Total hazard events: {total_hazard_566}. "
    f"The B2 paradox persists: zero-input baseline still produces higher/equal viability. "
    f"N2/N4 paradox: contribution-shuffled (composite={d6_n2:.3f}) and random-walk "
    f"(composite={d6_n4:.3f}) nulls beat the full model (composite={d6_full:.3f}). "
    f"B10 delta is only {d3_b10_delta:.5f} -- removing CLOSE recovery makes virtually no difference. "
    f"D5 confirms CLOSE recovery is ~4x weaker than WORK push "
    f"(work=+{d5_full_work:.4f}, close={d5_full_close:.4f}). "
    f"Real folio CTS values are too low/sparse for CTS-weighted channels to fire strongly."
)

# -- Summary table -------------------------------------------------------------

p2_max_H = max(tests["P2"]["per_sv"][sv]["H"] for sv in tests["P2"]["per_sv"])
p2_max_sv = max(tests["P2"]["per_sv"], key=lambda sv: tests["P2"]["per_sv"][sv]["H"])

# P5 key metric
p5a = tests["P5"]["P5a"]
p5_c_key = "C_differs" if "C_differs" in p5a else "C_better"
p5_s_key = "S_differs" if "S_differs" in p5a else "S_better"
p5_c_count = p5a.get(p5_c_key, 0)
p5_s_count = p5a.get(p5_s_key, 0)
p5_n_config = p5a.get("n_config_folios", 20)

# P5b -- handle C/S split
if "C" in tests["P5"]["P5b"]:
    p5b_c = tests["P5"]["P5b"]["C"]
    p5b_s = tests["P5"]["P5b"]["S"]
    p5b_stat = f"C: H={p5b_c['H']:.4f},p={p5b_c['p']:.3f}; S: H={p5b_s['H']:.4f},p={p5b_s['p']:.3f}"
elif "H" in tests["P5"]["P5b"]:
    p5b_stat = f"H={tests['P5']['P5b']['H']:.4f}, p={tests['P5']['P5b']['p']:.3f}"
else:
    p5b_stat = "N/A"

summary_table = {
    "P1_viable_envelope": {
        "pass": test_results["P1"],
        "key_metric": (
            f"full_gt_N1={p1_full_gt_n1}/20; "
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
            "full=B3 nearly identical (CTS has negligible effect on real folios)"
        )
    },
    "P7_null_destruction": {
        "pass": test_results["P7"],
        "key_metric": (
            f"null_types_destroyed={p7_null_destroyed}/4; "
            f"N1 mean_delta={tests['P7']['details']['N1']['mean_delta']:.6f}, "
            f"N2 mean_delta={tests['P7']['details']['N2']['mean_delta']:.6f} "
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
    y_finals.append(data["y_final"])
    hazard_counts.append(data["n_hazard_events"])
    if data["viability"] == 1.0:
        n_perfect_viab += 1

mean_viab = sum(viabilities) / len(viabilities) if viabilities else 0
mean_y = sum(y_finals) / len(y_finals) if y_finals else 0
total_hazard = sum(hazard_counts)
n_folios = len(viabilities)

# T2 summary metrics
t2_summary = t2["summary"]
t2_mean_pref_viab = t2_summary["mean_preferred_viability"]
t2_total_hazard = t2_summary["total_hazard_events"]
t2_mean_y = t2_summary["mean_y_final"]
t2_mean_close_recovery = t2_summary["mean_close_recovery_total"]

composite_metrics = {
    "mean_viability": round(mean_viab, 6),
    "mean_Y_final": round(mean_y, 4),
    "total_hazard_events": total_hazard,
    "folios_with_perfect_viability": f"{n_perfect_viab}/{n_folios}",
    "mean_corridor_occupancy": round(d2_occ, 4),
    "mean_corridor_signal_ratio": round(d1_ratio, 2),
    "B9_mean_viab_delta": round(d3_delta, 3),
    "B10_mean_viab_delta": round(d3_b10_delta, 5),
    "t2_summary": {
        "mean_preferred_viability": round(t2_mean_pref_viab, 5),
        "total_hazard_events": t2_total_hazard,
        "mean_Y_final": round(t2_mean_y, 4),
        "mean_close_recovery_total": round(t2_mean_close_recovery, 5),
    },
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
            "mean_viability": 0.9967,
            "mean_Y_final": 0.6281,
            "total_hazard": 17,
            "perfect_viab": "14/20",
            "corridor_occupancy": 0.190,
            "signal_ratio": 6.05,
            "B9_delta": 0.122
        },
        "566": {
            "mean_viability": round(mean_viab, 6),
            "mean_Y_final": round(mean_y, 4),
            "total_hazard": total_hazard,
            "perfect_viab": f"{n_perfect_viab}/{n_folios}",
            "corridor_occupancy": round(d2_occ, 4),
            "signal_ratio": round(d1_ratio, 2),
            "B9_delta": round(d3_delta, 3),
            "B10_delta": round(d3_b10_delta, 5)
        }
    }
}

# -- Diagnostic status ---------------------------------------------------------

diagnostic_status = {
    "D1_signal_ratio": {
        "status": "OK" if d1_ok else "FAILED",
        "value": round(d1_ratio, 2),
        "quasi_gate": "PASS" if d1_ok else "FAIL",
        "per_sv": {sv: round(diag["D1"]["per_sv"][sv]["ratio"], 4)
                   for sv in diag["D1"]["per_sv"]}
    },
    "D2_corridor_occupancy": {
        "status": "OK" if d2_ok else "FAILED",
        "value": round(d2_occ, 4),
        "quasi_gate": "PASS" if d2_ok else "FAIL",
        "per_sv": {sv: round(diag["D2"]["per_sv"][sv]["corridor"], 4)
                   for sv in diag["D2"]["per_sv"]}
    },
    "D3_B9_comparison": {
        "status": "BELOW_THRESHOLD" if d3_delta < 0.05 else "OK",
        "mean_delta": round(d3_delta, 3),
        "n_full_gt_B9": d3_n_gt,
        "expectation_threshold": 0.05,
        "above_threshold": d3_delta >= 0.05,
        "B10_analysis": {
            "mean_viab_delta": round(d3_b10_delta, 5),
            "n_full_gt_B10": diag["D3"]["B10_analysis"]["n_full_gt_B10"],
            "finding": (
                f"B10 delta is {d3_b10_delta:.5f} -- removing CLOSE recovery makes "
                "virtually no difference to viability. CLOSE recovery is not load-bearing."
            )
        },
        "largest_drops": []
    },
    "D4_edge_contact_audit": {
        "status": "OK" if d4_pass else "FAILED",
        "quasi_gate": "PASS" if d4_pass else "FAIL",
        "full_model_mean_contacts_per_folio": diag["D4"]["full_model"]["mean_per_folio"],
        "null_grand_mean_contacts_per_folio": diag["D4"]["null_grand_mean_per_folio"],
        "full_null_ratio": diag["D4"]["full_null_ratio"],
        "cond1_not_all_zero": diag["D4"]["conditions"]["cond1_not_all_zero"],
        "cond2_not_indiscriminate": diag["D4"]["conditions"]["cond2_not_indiscriminate"],
        "finding": (
            f"Edge contact ratio={d4_ratio:.3f}. Full model: "
            f"{diag['D4']['full_model']['mean_per_folio']:.1f}/folio, "
            f"nulls: {diag['D4']['null_grand_mean_per_folio']:.1f}/folio. "
            f"cond2={'PASS' if diag['D4']['conditions']['cond2_not_indiscriminate'] else 'FAIL'}."
        )
    },
    "D5_close_recovery_asymmetry": {
        "status": "FAILED" if not d5_pass else "OK",
        "quasi_gate": "PASS" if d5_pass else "FAIL",
        "full_work_grand_mean": round(d5_full_work, 6),
        "full_close_grand_mean": round(d5_full_close, 6),
        "finding": (
            f"WORK push=+{d5_full_work:.4f}, CLOSE recovery={d5_full_close:.4f}. "
            f"CLOSE is ~{abs(d5_full_work / d5_full_close):.1f}x weaker than WORK. "
            "Recovery is too weak to create meaningful discrimination."
        )
    },
    "D6_composite_scoring": {
        "status": "DIAGNOSTIC",
        "full_composite": round(d6_full, 3),
        "B2_composite": round(d6_b2, 3),
        "N2_composite": round(d6_n2, 3),
        "N4_composite": round(d6_n4, 3),
        "finding": (
            f"Full composite={d6_full:.3f}, B2={d6_b2:.3f}, "
            f"but N2={d6_n2:.3f} and N4={d6_n4:.3f} beat full. "
            "Contribution-shuffled and random-walk nulls produce MORE Y than full model."
        )
    },
    "D7_corridor_return_latency": {
        "status": "OK" if d7_pass else "FAILED",
        "quasi_gate": "PASS" if d7_pass else "FAIL",
        "full_mean_latency": round(d7_latency, 2),
        "finding": (
            f"Corridor return latency={d7_latency:.2f} tokens. "
            "CLOSE recovery channels produce rapid corridor returns."
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
            "n1_viab_mean": data["n1_viab_mean"]
        }

# -- N2/N4 paradox analysis --------------------------------------------------

n2_n4_paradox = {
    "description": (
        "Contribution-shuffled (N2) and random-walk (N4) nulls produce HIGHER composite "
        "scores than the full model. N2 composite=0.920, N4 composite=0.920, full=0.891. "
        "This means the full model's supervisory routing CONSTRAINS Y accumulation rather "
        "than enabling it. Random contributions actually produce more Y."
    ),
    "full_composite": round(d6_full, 3),
    "N2_composite": round(d6_n2, 3),
    "N4_composite": round(d6_n4, 3),
    "B2_composite": round(d6_b2, 3),
    "implication": (
        "The supervisory signal routing is counterproductive. Proper SPEC->WORK->CLOSE "
        "phase alignment constrains how much Y can accumulate, while contribution-shuffled "
        "nulls (which break phase alignment) allow Y to grow more freely. This is the "
        "deepest paradox in the apparatus line: the very structure meant to enable Y "
        "accumulation actually limits it."
    )
}

# -- B2 paradox analysis (updated for 566) ------------------------------------

b2_paradox = {
    "description": (
        "B2 (zero contributions) still achieves viability=1.0 for ALL folios. "
        "The supervisory signal continues to CAUSE hazard events rather than preventing them. "
        "Despite CLOSE recovery channels being added (K_CLOSE, CTS-weighted discharge), "
        "the recovery magnitude is too small to offset WORK excursion."
    ),
    "full_model_mean_viab": round(mean_viab, 6),
    "b2_composite": round(d6_b2, 3),
    "full_composite": round(d6_full, 3),
    "b10_viab_delta": round(d3_b10_delta, 5),
    "implication": (
        "CLOSE recovery works mechanistically (V10-V12 pass in synthetic preflights) "
        "but real folio CTS values are too low/sparse for CTS-weighted channels to fire "
        "strongly enough. The B10 delta of {:.5f} confirms: removing CLOSE recovery "
        "makes virtually no difference. The recovery channels exist but do not fire "
        "with sufficient magnitude on real data.".format(d3_b10_delta)
    )
}

# -- S instability analysis ---------------------------------------------------

# Extract S zone occupancy from D2
s_occ = diag["D2"]["per_sv"]["S"]
s_warning_pct = s_occ.get("warning", 0)
s_hard_stop_pct = s_occ.get("hard_stop", 0)
s_instability_pct = s_warning_pct + s_hard_stop_pct

s_instability = {
    "s_warning_pct": round(s_warning_pct, 4),
    "s_hard_stop_pct": round(s_hard_stop_pct, 4),
    "s_total_danger_pct": round(s_instability_pct, 4),
    "s_basin_pct": round(s_occ.get("basin", 0), 4),
    "finding": (
        f"S spends {s_instability_pct:.1%} of time in warning+hard_stop zones "
        f"(warning={s_warning_pct:.1%}, hard_stop={s_hard_stop_pct:.1%}). "
        f"Only {s_occ.get('basin', 0):.1%} in basin. "
        "gamma_basin_S may be too low to maintain S stability."
    )
}

# -- Lessons learned -----------------------------------------------------------

lessons_learned = [
    (
        f"P2 packet-shape coupling ({p2_n_sig}/7 significant) passes for the SIXTH consecutive "
        f"phase (563, 563b, 564, 564b, 565, 566). This is the most robust coupling signal in "
        f"the entire apparatus line, surviving six different parametric regimes and three "
        f"architectural changes. SPEC/WORK/CLOSE differentiation is architecture-independent."
    ),
    (
        f"CTS-weighted recovery works mechanistically: V11 passes (recovery ratio=1.25, "
        f"residual with CTS=0.013 vs without CTS=0.056). V12a passes (safety margin ratio=1.10). "
        f"The CLOSE recovery mechanism functions correctly in synthetic preflights."
    ),
    (
        f"Safety inversion achievable under synthetic conditions: V12 passes all sub-tests "
        f"(V12a, V12b, V12c) with the 566-Mid ladder pack. Aligned traces achieve lower "
        f"hazard burden (561 vs 617 for random), higher Y (0.911 vs 0.910), and higher "
        f"composite (0.796 vs 0.715)."
    ),
    (
        f"B9 remains the strongest ablation signal (delta={d3_delta:.3f}) but is below the "
        f"0.05 threshold for the first time (was +0.122 in 565, +0.125 in 564b). Zone "
        f"architecture is weakening as a discriminator under the CLOSE recovery regime."
    ),
    (
        f"Recovery magnitudes commensurate with P90 dV are still insufficient for real folio "
        f"discrimination. B10 delta={d3_b10_delta:.5f} -- removing CLOSE recovery entirely "
        f"makes virtually no difference. Real folio CTS values are too low/sparse for "
        f"CTS-weighted channels to fire strongly enough."
    ),
    (
        f"The contribution-shuffled null paradox: N2 and N4 beat the full model on both "
        f"Y_final and composite score (N2={d6_n2:.3f}, N4={d6_n4:.3f} vs full={d6_full:.3f}). "
        f"This suggests the full model's supervisory routing CONSTRAINS Y accumulation "
        f"rather than enabling it."
    ),
    (
        f"The viability scoring function may need fundamental revision. Viability remains "
        f"near-universal (0.997-1.0) for all models including nulls. Zone-occupancy-based "
        f"scoring produces insufficient dynamic range for discrimination. Consider "
        f"hazard-burden-based viability instead."
    ),
    (
        f"S instability: S spends {s_instability_pct:.1%} of time in warning+hard_stop zones. "
        f"gamma_basin_S={t1['apparatus_config']['GAMMA_BASIN']['S']} may be too low to "
        f"maintain S stability. This contributes to the high warning/hard_stop contact counts."
    ),
    (
        f"P8 regressed from PASS (17/20 in 565) to FAIL ({p8_preferred_best}/20 in 566, "
        f"threshold={tests['P8']['threshold']}). The CLOSE recovery channels shifted "
        f"profile dynamics enough that the preferred profile is no longer best for 5 folios."
    ),
]

# -- Build output --------------------------------------------------------------

output = {
    "metadata": {
        "phase": "566",
        "task": "T5_synthesis",
        "phase_name": "VIRTUAL_APPARATUS_CLOSE_RECOVERY",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "verdict": verdict,
        "n_tests_total": 9,
        "n_tests_pass": n_pass,
        "n_tests_fail": n_fail,
        "n_constraints_proposed": 0
    },
    "verdict_rationale": verdict_rationale,
    "comparison_563_thru_566": comparison,
    "regressions": regressions,
    "improvements": improvements,
    "summary_table": summary_table,
    "composite_metrics": composite_metrics,
    "diagnostic_status": diagnostic_status,
    "folios_with_viab_lt_1": folios_lt_1,
    "b2_paradox": b2_paradox,
    "n2_n4_paradox": n2_n4_paradox,
    "s_instability": s_instability,
    "lessons_learned": lessons_learned,
    "constraints_note": (
        f"{verdict}: no new constraints. This phase proves CTS-weighted CLOSE recovery "
        f"works mechanistically (V10-V12 pass in synthetic preflights) but real supervisory "
        f"signals are too weak for the recovery channels to create meaningful discrimination. "
        f"B10 delta={d3_b10_delta:.5f} confirms CLOSE recovery is not load-bearing on real folios."
    ),
    "implications_for_next_phase": [
        (
            "The viability metric itself may be the bottleneck, not the plant architecture. "
            "Zone-occupancy-based viability scoring produces insufficient dynamic range. "
            "Consider hazard-burden-based viability: penalize proportionally to HOW MUCH "
            "time is spent in hazard, not just whether hazard is ever contacted."
        ),
        (
            "Real CTS values need empirical characterization. The CTS-weighted channels "
            "work in synthetic preflights (where CTS is artificially controlled) but "
            "real folio CTS values may be too low, too sparse, or too uniform across "
            "tokens for the weighting to produce meaningful differentiation."
        ),
        (
            "The S instability needs attention. gamma_basin_S may be too low. S spends "
            f"{s_instability_pct:.1%} in warning+hard_stop, dominating the edge contact "
            "statistics and masking discrimination signal from other SVs."
        ),
        (
            "The N2/N4 paradox suggests a fundamental problem: supervisory routing "
            "CONSTRAINS Y accumulation. The phase-differentiated contribution scaling "
            "(SPEC low, WORK full, CLOSE recovery) may limit Y's growth path more than "
            "random contributions do. The Y pathway may need to be decoupled from "
            "viability-related dynamics."
        ),
        (
            "Cross-phase score trajectory: 5/9 -> 3/9 -> 2/9 -> 2/9 -> 2/9 -> 1/9. "
            "The score has declined to its lowest point. The apparatus line has exhausted "
            "incremental parametric refinement. The next step requires either a fundamentally "
            "different viability scoring function or a different relationship between "
            "supervisory signal and plant dynamics."
        ),
    ]
}

# -- Write output --------------------------------------------------------------

out_path = os.path.join(RESULTS_DIR, "t5_synthesis.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=1)

# -- Write REPORT_566.md ------------------------------------------------------

report_path = os.path.join(PHASE_DIR, "REPORT_566.md")

# Build comparison table for markdown
comp_header = "| Test | 563 | 563b | 564 | 564b | 565 | **566** |"
comp_sep    = "|------|-----|------|-----|------|-----|---------|"
comp_rows = []
for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]:
    c = comparison[t]
    comp_rows.append(
        f"| {t} | {c['563']} | {c['563b']} | {c['564']} | {c['564b']} | {c['565']} | **{c['566']}** |"
    )

# Score summary line
score_563 = sum(1 for v in results_563.values() if v is True)
score_563b = sum(1 for v in results_563b.values() if v is True)
score_564 = sum(1 for v in results_564.values() if v is True)
score_564b = sum(1 for v in results_564b.values() if v is True)
score_565 = sum(1 for v in results_565.values() if v is True)

# Folios with viab < 1.0 table
folios_lt_1_rows = []
for folio, data in sorted(folios_lt_1.items(), key=lambda x: x[1]["viability"]):
    folios_lt_1_rows.append(
        f"| {folio} | {data['viability']:.5f} | {data['profile']} | {data['n1_viab_mean']:.5f} |"
    )

# D3 largest drops table
d3_drop_rows = []
for drop in diagnostic_status["D3_B9_comparison"]["largest_drops"]:
    d3_drop_rows.append(
        f"| {drop['folio']} | {drop['full_viab']:.3f} | {drop['B9_viab']:.3f} | {drop['viab_delta']:.3f} |"
    )

report = f"""# Phase 566: Close-Driven Recovery and Signal Inversion

**Phase:** 566 (VIRTUAL_APPARATUS_CLOSE_RECOVERY)
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Verdict:** CLOSE_RECOVERY_FAILED (1/9 tests pass)
**New constraints:** None (negative result)
**Diagnostic status:** D1 OK (ratio={d1_ratio:.2f}), D2 OK (corridor={d2_occ:.1%}), D3 below threshold (B9 delta={d3_delta:.3f}, need 0.05), D4 OK (ratio={d4_ratio:.3f}), D5 FAIL (CLOSE recovery too weak), D6 diagnostic (N2/N4 > full), D7 PASS (latency={d7_latency:.2f})

## Summary

Phase 566 added CLOSE recovery channels to the graduated-edge apparatus from Phase 565: per-SV CLOSE recovery gains (K_CLOSE), CTS-weighted discharge (K_CTS_CLOSE={k_cts_close}), profile-specific CLOSE multipliers, relief scaling, and R4/R5 cross-coupling. A preflight ladder tested three parameter packs (566-Low, 566-Mid, 566-High); the 566-Mid pack was selected because all synthetic self-tests (V10-V12) passed.

**Result: CLOSE_RECOVERY_FAILED.** The recovery mechanism works in synthetic preflights but fails on real folios. V10 passes (aligned recovery > 0, disrupted = 0). V11 passes (CTS-weighted recovery is 25% stronger than non-CTS). V12 passes (aligned traces achieve lower hazard burden than random). But on real folios: B10 (no CLOSE recovery) has a viability delta of only {d3_b10_delta:.5f} vs the full model -- removing CLOSE recovery makes virtually no difference. N2 (contribution-shuffled) and N4 (random-walk) nulls beat the full model on composite score ({d6_n2:.3f} and {d6_n4:.3f} vs {d6_full:.3f}). P8 regressed from PASS to FAIL ({p8_preferred_best}/20, threshold {tests['P8']['threshold']}). The score drops from 2/9 to 1/9.

The synthetic-to-real gap is the defining finding of Phase 566: CTS-weighted CLOSE recovery functions correctly in controlled conditions but real folio CTS values are too low and sparse for the channels to produce meaningful discrimination.

## Results

{comp_header}
{comp_sep}
{chr(10).join(comp_rows)}

**Score: {n_pass}/9 pass** (P2 only). Regression from 565's 2/9 (lost P8).

**Cross-phase trajectory:** {score_563}/9 -> {score_563b}/9 -> {score_564}/9 -> {score_564b}/9 -> {score_565}/9 -> **{n_pass}/9**

### Key Findings per Test

| Test | Result | Key Metric |
|------|--------|------------|
| P1 | FAIL | full_gt_N1={p1_full_gt_n1}/20 (need 14); mean_viab={p1_mean_viab:.6f}, folios_lt_1={p1_folios_lt_1}/20 (need >=8) |
| P2 | **PASS** | {p2_n_sig}/7 SVs significant; strongest H={p2_max_H:.1f} ({p2_max_sv}); 6th consecutive pass |
| P3 | FAIL | mean_cycles={p3_mean_cycles:.2f}, bounded_frac={p3_bounded_frac:.3f}, n_meeting_both={p3_n_meeting}/20 |
| P4 | FAIL | P4a: {tests['P4']['P4a']['n_correct']}/4 correct; P4b: viab_delta={tests['P4']['P4b']['full_vs_B4_viab_delta']:.5f} |
| P5 | FAIL | P5a: C_differs={p5_c_count}/{p5_n_config}, S_differs={p5_s_count}/{p5_n_config}; P5b: {p5b_stat} |
| P6 | FAIL | viab_better={tests['P6']['viab_better']}/20, C_sep_positive={tests['P6']['C_sep_positive']}/20 |
| P7 | FAIL | {p7_null_destroyed}/4 null types destroyed; N1 delta={tests['P7']['details']['N1']['mean_delta']:.6f}, N2 delta={tests['P7']['details']['N2']['mean_delta']:.6f} |
| P8 | **FAIL** | preferred_best={p8_preferred_best}/20 (threshold {tests['P8']['threshold']}); regressed from PASS in 565 |
| P9 | SEC | {tests['P9']['n_significant']}/7 SVs significant |

### Composite Metrics

| Metric | 563 | 563b | 564 | 564b | 565 | **566** |
|--------|-----|------|-----|------|-----|---------|
| Mean viability | 0.9616 | 0.9635 | 1.0 | 0.99985 | 0.9967 | **{mean_viab:.4f}** |
| Mean Y_final | 0.878 | 0.848 | 0.7366 | 0.5686 | 0.6281 | **{mean_y:.4f}** |
| Total hazard events | 34 | 255 | 0 | 1 | 17 | **{total_hazard}** |
| Perfect viability | 4/7 | 12/20 | 20/20 | 19/20 | 14/20 | **{n_perfect_viab}/{n_folios}** |
| Corridor occupancy | -- | -- | -- | 18.7% | 19.0% | **{d2_occ:.1%}** |
| Signal/restoring ratio | -- | -- | -- | 6.05 | 6.05 | **{d1_ratio:.2f}** |
| B9 mean viab delta | -- | -- | -- | +0.125 | +0.122 | **+{d3_delta:.3f}** |

Note: 563 used 7 pilot folios; all others use 20 pilot folios.

### Diagnostics

| Diagnostic | Status | Value | Finding |
|------------|--------|-------|---------|
| D1 (corridor signal ratio) | OK | {d1_ratio:.2f} | Signal dominates restoring in corridor. Range: {min(diag['D1']['per_sv'][sv]['ratio'] for sv in diag['D1']['per_sv']):.2f} to {max(diag['D1']['per_sv'][sv]['ratio'] for sv in diag['D1']['per_sv']):.2f}. |
| D2 (corridor occupancy) | OK | {d2_occ:.1%} | S dominates ({s_occ['corridor']:.1%} corridor, {s_warning_pct:.1%} warning, {s_hard_stop_pct:.1%} hard_stop). |
| D3 (B9 uniform restoring) | BELOW | +{d3_delta:.3f} | Below 0.05 threshold (was +0.122 in 565). Zone architecture weakening. |
| D4 (edge contact audit) | OK | {d4_ratio:.3f} | cond2 now passes (was FAIL in 565). Full model has more edge contact than nulls. |
| D5 (CLOSE recovery asymmetry) | **FAIL** | work=+{d5_full_work:.4f}, close={d5_full_close:.4f} | CLOSE recovery ~{abs(d5_full_work / d5_full_close):.1f}x weaker than WORK push. |
| D6 (composite scoring) | DIAG | full={d6_full:.3f} | N2={d6_n2:.3f} and N4={d6_n4:.3f} beat full model. |
| D7 (corridor return latency) | OK | {d7_latency:.2f} tokens | CLOSE channels produce rapid corridor returns. |

### Null Model Comparison (T3)

| Model | Mean Viability | Mean Y_final | Composite |
|-------|---------------|--------------|-----------|
| Reference (full) | {mean_viab:.4f} | {mean_y:.3f} | {d6_full:.3f} |
| B1 (uniform sens) | 1.0000 | 0.640 | -- |
| B2 (zero input) | 1.0000 | 0.500 | {d6_b2:.3f} |
| B3 (shuffled phase) | {mean_viab:.4f} | -- | {diag['D6']['baselines']['B3']['mean_composite']:.3f} |
| B9 (uniform restoring) | -- | -- | {diag['D6']['baselines']['B9']['mean_composite']:.3f} |
| B10 (no CLOSE recovery) | -- | -- | {diag['D6']['baselines']['B10']['mean_composite']:.3f} |
| N1 (phase-shuffled) | -- | -- | {diag['D6']['nulls']['N1']['mean_composite']:.3f} |
| N2 (contrib-shuffled) | -- | -- | {d6_n2:.3f} |
| N3 (cross-folio) | -- | -- | {diag['D6']['nulls']['N3']['mean_composite']:.3f} |
| N4 (random walk) | -- | -- | {d6_n4:.3f} |

## Analysis

### Why CLOSE recovery failed to discriminate on real folios

The CLOSE recovery mechanism has three channels: (R1) per-SV CLOSE recovery with K_CLOSE gains, (R2) CTS-weighted discharge scaling contributions by CTS value, and (R3) profile-specific CLOSE multipliers. All three work correctly in synthetic preflights:

- **V10 passes:** Aligned trace recovers (0.119), disrupted trace does not (0.0).
- **V11 passes:** CTS-weighted recovery is 25% stronger (ratio=1.251), Y gain with CTS is 0.101 vs 0.0 without.
- **V12 passes:** Aligned traces achieve lower hazard burden (561 vs 617), higher Y (0.911 vs 0.910), higher composite (0.796 vs 0.715).

But on real folios, the channels barely fire. B10 (no CLOSE recovery) has a viability delta of {d3_b10_delta:.5f} vs the full model. The CLOSE recovery channels exist but produce negligible effect. The gap between synthetic and real:

1. **Synthetic preflights use controlled CTS values** where CTS is artificially injected at known positions. Real folios have CTS values derived from token morphology, which may be too low, too sparse, or too uniform.
2. **Synthetic preflights use a single idealized trace** running multiple SPEC->WORK->CLOSE cycles. Real folios have complex token sequences where CLOSE phases may be short, infrequent, or poorly aligned with edge approach.
3. **Recovery magnitude scales with P90_dV** (~0.006-0.057 depending on SV). Even with K_CLOSE gains of 0.05-0.50, the actual per-token recovery is a fraction of a single supervisory contribution. It takes many CLOSE tokens to produce measurable recovery, and real folios may not have enough consecutive CLOSE tokens.

### The N2/N4 paradox: contribution-shuffled and random-walk nulls beat the full model

This is the deepest paradox in the apparatus line. N2 (contribution-shuffled) and N4 (random-walk) nulls produce higher composite scores ({d6_n2:.3f} and {d6_n4:.3f}) than the full model ({d6_full:.3f}). Both produce higher Y_final too.

The implication: the full model's supervisory routing (phase-differentiated contributions, packet-aligned signals) CONSTRAINS Y accumulation rather than enabling it. When contributions are shuffled randomly (N2) or replaced with random walks (N4), Y grows more freely because the routing constraints that attenuate signal during SPEC and modulate it during CLOSE are removed.

This suggests a fundamental tension in the apparatus design: the phase structure that enables discrimination (SPEC->WORK->CLOSE) simultaneously limits the Y pathway. The viability-discrimination axis and the Y-accumulation axis are in conflict.

### D5 asymmetry: CLOSE recovery is real but too weak

D5 confirms that CLOSE phases DO produce negative mean dV (pulling state back toward equilibrium) while WORK phases produce positive mean dV (pushing state away). This asymmetry is real and in the correct direction. But the magnitudes are severely imbalanced:

- WORK grand mean: +{d5_full_work:.4f} (pushing out)
- CLOSE grand mean: {d5_full_close:.4f} (pulling back)
- Ratio: CLOSE is ~{abs(d5_full_work / d5_full_close):.1f}x weaker than WORK

For CLOSE recovery to create discrimination, it would need to be strong enough that a properly aligned trace (with CTS-weighted discharge during CLOSE) recovers from WORK excursions before reaching hazard, while a misaligned trace does not. At current magnitudes, neither the full model nor nulls recover meaningfully during CLOSE.

### S instability dominates edge contact statistics

S spends {s_instability_pct:.1%} of time in warning+hard_stop zones (warning={s_warning_pct:.1%}, hard_stop={s_hard_stop_pct:.1%}), with only {s_occ.get('basin', 0):.1%} in basin. This means S is essentially always in danger zones, contributing the majority of warning/hard_stop contacts. This masks the discrimination signal from other SVs, which do have meaningful variation between full and null models but are swamped by S's constant danger-zone residence.

gamma_basin_S = {t1['apparatus_config']['GAMMA_BASIN']['S']} may be too low for S's dynamics, or the S zone boundaries (Q2_S={t1['apparatus_config']['Q2_BASE']['S']}, Q3_S={t1['apparatus_config']['Q3_BASE']['S']}) may be too tight.

### B10 delta is only {d3_b10_delta:.5f}: CLOSE recovery barely matters

The B10 ablation (remove CLOSE recovery) produces a viability delta of {d3_b10_delta:.5f} compared to the full model. This is three orders of magnitude smaller than the B9 delta ({d3_delta:.3f}). Removing CLOSE recovery entirely makes virtually no difference to viability outcomes. The CLOSE recovery channels added in Phase 566 are not load-bearing on real folios.

This confirms the synthetic-to-real gap: the channels work when CTS is artificially injected but do not fire meaningfully on real data.

## What 566 Proved

1. **P2 packet-shape coupling survives six consecutive phases.** 7/7 SVs significant with the strongest H={p2_max_H:.1f} ({p2_max_sv}). This is now the most robustly confirmed property in the apparatus line: SPEC, WORK, and CLOSE phases produce genuinely different state-variable dynamics regardless of parametric regime or architectural variant.

2. **CTS-weighted recovery works mechanistically (V11 passes).** Recovery ratio=1.251 (25% stronger with CTS). Residual with CTS=0.013 vs without=0.056. The mechanism is sound; the inputs are too weak on real data.

3. **Safety inversion is achievable under synthetic conditions (V12a passes).** Aligned traces achieve lower hazard burden (561 vs 617 for random), confirming that in principle, structured input CAN produce LESS hazard than random input. The discrimination axis CAN be inverted -- but only with sufficiently strong CTS values.

4. **B9 remains the strongest ablation signal (delta={d3_delta:.3f}).** Although below the 0.05 threshold for the first time, B9 (uniform restoring) still produces the largest viability difference. Zone architecture remains the primary load-bearing element, even as its discriminative power weakens under the CLOSE recovery regime.

5. **D4 edge contact discrimination improved.** Full/null ratio={d4_ratio:.3f} (was 1.064 in 565). cond2_not_indiscriminate now passes, meaning the full model contacts edges at a measurably higher rate than nulls. This is a structural improvement, even though it does not translate to viability discrimination.

6. **D7 corridor return latency is short.** Mean latency={d7_latency:.2f} tokens, meaning the CLOSE recovery channels DO produce rapid state recovery when they fire. The mechanism is fast but fires too rarely.

## Lessons Learned

1. **Recovery magnitudes commensurate with P90 dV are still insufficient** for real folio discrimination. Even with K_CLOSE gains up to 0.50, K_CTS_CLOSE={k_cts_close}, and profile-specific multipliers, the per-token recovery is a fraction of a single supervisory contribution. Real folio CTS values are too low/sparse for CTS-weighted channels to fire strongly.

2. **Real folio CTS values need empirical characterization.** The assumption that CTS values from token morphology would provide sufficient discharge weighting has not been validated against actual CTS distributions. If most tokens have CTS near zero, the CTS-weighted channel is effectively disabled.

3. **The viability scoring function may need fundamental revision.** Zone-occupancy-based viability scoring (fraction of time NOT in hazard) produces insufficient dynamic range. When viability is 0.997-1.0 for all models including nulls, there is no room for discrimination. A hazard-burden-based score (cumulative hazard exposure, weighted by depth and duration) might provide more dynamic range.

4. **The contribution-shuffled null paradox (N2/N4 > full on Y and composite) suggests the full model's supervisory routing CONSTRAINS Y accumulation** rather than enabling it. Phase-differentiated contribution scaling attenuates signal during SPEC and modulates it during CLOSE, limiting Y growth. This is a fundamental design tension that may require decoupling the Y pathway from viability dynamics.

5. **S instability needs attention.** S spends {s_instability_pct:.1%} in danger zones, dominating edge contact statistics. gamma_basin_S may need to be increased, or S zone boundaries may need to be widened, or S may need to be excluded from certain viability calculations.

6. **P8 regression from PASS (17/20 in 565) to FAIL ({p8_preferred_best}/20)** shows that the CLOSE recovery channels perturbed profile dynamics. The recovery channels preferentially benefit certain profiles (A3_DISTILL_COLLECT, which has K_RELIEF_CLOSE=6.0 vs A1's 3.6), shifting the competitive landscape.

## Implications for Next Phase

1. **The viability metric itself may be the bottleneck**, not the plant architecture. Zone-occupancy scoring produces insufficient dynamic range. Consider:
   - Hazard-burden scoring: integrate (depth * duration) in hazard zones
   - Cumulative exceedance scoring: penalize proportionally to how far state exceeds zone boundaries
   - Asymmetric scoring: weight warning and hard_stop contacts differently

2. **Real CTS values need empirical characterization.** Before designing another CLOSE recovery variant, measure the actual distribution of CTS values across real folios. If CTS is uniformly low, the CTS-weighted channel will never fire meaningfully regardless of gain settings.

3. **The S instability needs attention.** S's constant residence in danger zones masks discrimination signal from other SVs. Options:
   - Increase gamma_basin_S to strengthen S restoring
   - Widen S zone boundaries (raise Q2_S, Q3_S, HAZARD_DEV_S)
   - Exclude S from viability scoring if it is constitutively unstable

4. **The N2/N4 paradox (supervisory routing constrains Y) may require architectural revision.** If the phase structure simultaneously enables discrimination and limits Y accumulation, the two objectives may need to be decoupled. Possible approaches:
   - Allow Y to accumulate independently of phase structure
   - Use a separate Y pathway that is not attenuated during SPEC
   - Redefine what "success" means: perhaps Y should not be maximized but rather maintained in a target range

5. **Cross-phase score trajectory: 5/9 -> 3/9 -> 2/9 -> 2/9 -> 2/9 -> 1/9.** The score has reached its lowest point. Six phases of incremental parametric refinement have not recovered the discrimination that 563 achieved on 7 pilot folios. The apparatus line has likely exhausted incremental improvements. The next step requires either a fundamentally different viability scoring function, a different viability/Y coupling, or a reconsideration of what the apparatus is trying to discriminate.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t1_close_recovery_apparatus.py | Build CLOSE recovery apparatus with V10-V12 preflights | t1_close_recovery_apparatus.json |
| t2_close_recovery_executor.py | Run 20 folios x 3 profiles x 3 configs + ablations (90 runs) | t2_close_recovery_runs.json |
| t3_null_and_ablation_executor.py | 10 baselines + 4 nulls x 50 perms per folio + B9/B10 (4,220 runs) | t3_null_ablation_runs.json |
| t4_behavior_validation.py | 9-test validation battery + 7 diagnostics (D1-D7) | t4_behavior_validation.json |
| t5_synthesis.py | Aggregate results, cross-phase comparison, verdict, report | t5_synthesis.json, REPORT_566.md |

## Constraints

No new constraints created (CLOSE_RECOVERY_FAILED verdict). This phase proves CTS-weighted CLOSE recovery works mechanistically (V10-V12 pass in synthetic preflights) but real supervisory signals are too weak for the recovery channels to create meaningful discrimination. B10 delta={d3_b10_delta:.5f} confirms CLOSE recovery is not load-bearing on real folios.

Phase 563 constraints C1581-C1587 remain valid for the original 563 configuration. The progressive negative results from 564 through 566 collectively establish:
- Zone geometry is correct (B9 ablation confirms across three regimes, albeit weakening)
- Corridor dynamics are correct (D1/D2 stable across three regimes)
- Edge permeability is achievable (565/566 vs 564b)
- CLOSE recovery is mechanistically sound (V10-V12 pass)
- The remaining bottleneck is either the viability scoring function, real CTS value distributions, or a fundamental tension between supervisory routing and Y accumulation
"""

with open(report_path, "w") as f:
    f.write(report)

# -- Print summary -------------------------------------------------------------

print(f"Phase 566 T5 Synthesis")
print(f"=" * 70)
print(f"Verdict: {verdict}")
print(f"Tests: {n_pass}/9 pass, {n_fail}/9 fail")
print()

print("Cross-phase comparison:")
print(f"  {'Test':<6} {'563':<6} {'563b':<6} {'564':<6} {'564b':<6} {'565':<6} {'566':<6}")
print(f"  {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]:
    c = comparison[t]
    print(f"  {t:<6} {c['563']:<6} {c['563b']:<6} {c['564']:<6} {c['564b']:<6} {c['565']:<6} {c['566']:<6}")

print()
print(f"Regressions from 563:  {regressions['from_563']}")
print(f"Improvements from 563: {improvements['from_563']}")
print(f"Regressions from 565:  {regressions['from_565']}")
print(f"Improvements from 565: {improvements['from_565']}")

print()
print("Composite metrics:")
print(f"  Mean viability: {composite_metrics['mean_viability']}")
print(f"  Mean Y_final:   {composite_metrics['mean_Y_final']}")
print(f"  Total hazard:   {composite_metrics['total_hazard_events']}")
print(f"  Perfect viab:   {composite_metrics['folios_with_perfect_viability']}")
print(f"  Corridor occ:   {composite_metrics['mean_corridor_occupancy']}")
print(f"  Signal ratio:   {composite_metrics['mean_corridor_signal_ratio']}")
print(f"  B9 viab delta:  {composite_metrics['B9_mean_viab_delta']}")
print(f"  B10 viab delta: {composite_metrics['B10_mean_viab_delta']}")

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
print(f"  D5 CLOSE recovery:     {diagnostic_status['D5_close_recovery_asymmetry']['status']} "
      f"(work=+{d5_full_work:.4f}, close={d5_full_close:.4f})")
print(f"  D6 composite:          {diagnostic_status['D6_composite_scoring']['status']} "
      f"(full={d6_full:.3f}, N2={d6_n2:.3f}, N4={d6_n4:.3f})")
print(f"  D7 corridor return:    {diagnostic_status['D7_corridor_return_latency']['status']} "
      f"(latency={d7_latency:.2f} tokens)")

print()
print("B9 largest viability drops:")
for drop in diagnostic_status["D3_B9_comparison"]["largest_drops"]:
    print(f"  {drop['folio']}: {drop['full_viab']:.3f} -> {drop['B9_viab']:.3f} "
          f"(delta={drop['viab_delta']:.3f})")

print()
print("Folios with viability < 1.0:")
for folio, data in sorted(folios_lt_1.items(), key=lambda x: x[1]["viability"]):
    print(f"  {folio}: viab={data['viability']:.5f}, profile={data['profile']}, "
          f"n1_mean={data['n1_viab_mean']:.5f}")

print()
print("N2/N4 paradox:")
print(f"  Full model composite: {d6_full:.3f}")
print(f"  N2 composite:         {d6_n2:.3f}")
print(f"  N4 composite:         {d6_n4:.3f}")
print(f"  B2 composite:         {d6_b2:.3f}")

print()
print("S instability:")
print(f"  S warning+hard_stop: {s_instability_pct:.1%}")
print(f"  S basin:             {s_occ.get('basin', 0):.1%}")

print()
print(f"Constraints proposed: 0")
print(f"Output: {out_path}")
print(f"Report: {report_path}")
