"""
Phase 564b T5: Synthesis -- aggregate results, cross-phase comparison, verdict.

Reads:
  - t4_behavior_validation.json  (9 tests + 3 diagnostics)
  - t2_selective_restoration_runs.json  (composite metrics: viability, Y_final, hazard)
  - t3_null_ablation_runs.json  (reference runs for composite metrics)
  - t1_selective_restoration_apparatus.json (apparatus config for BETA values)

Writes:
  - t5_synthesis.json

Verdict logic:
  - SELECTIVE_RESTORATION_VALIDATED: P1+P2+P3+P4+P7 all PASS, plus >=1 of P5/P6/P8
  - PARTIAL_SELECTIVE_RESTORATION: P1+P2+P7 pass but P3 or P4 weak
  - SELECTIVE_RESTORATION_FAILED: Core tests do not all pass
"""

import json
import os
from datetime import datetime

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, "results")

# -- Load inputs --------------------------------------------------------------

with open(os.path.join(RESULTS_DIR, "t4_behavior_validation.json")) as f:
    t4 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t2_selective_restoration_runs.json")) as f:
    t2 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t3_null_ablation_runs.json")) as f:
    t3 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t1_selective_restoration_apparatus.json")) as f:
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

# -- Phase 563, 563b, 564 reference results ------------------------------------

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
        "564b": pass_str(test_results[t]),
    }

# -- Regressions and improvements ---------------------------------------------

regressions_563 = []
improvements_563 = []
regressions_564 = []
improvements_564 = []

for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]:
    # vs 563
    if results_563[t] is True and test_results[t] is not True:
        regressions_563.append(t)
    if results_563[t] is not True and test_results[t] is True:
        improvements_563.append(t)
    # vs 564
    if results_564[t] is True and test_results[t] is not True:
        regressions_564.append(t)
    if results_564[t] is not True and test_results[t] is True:
        improvements_564.append(t)

# -- Verdict -------------------------------------------------------------------

core_pass = all(test_results[t] for t in ["P1", "P2", "P3", "P4", "P7"])
secondary_pass = any(test_results[t] for t in ["P5", "P6", "P8"])
weak_core = all(test_results[t] for t in ["P1", "P2", "P7"])

if core_pass and secondary_pass:
    verdict = "SELECTIVE_RESTORATION_VALIDATED"
elif weak_core:
    verdict = "PARTIAL_SELECTIVE_RESTORATION"
else:
    verdict = "SELECTIVE_RESTORATION_FAILED"

# -- Verdict rationale ---------------------------------------------------------

# Extract key metrics from T4 for the rationale
p1_full_gt_b2 = tests["P1"]["P1a"]["full_gt_B2"]
p1_full_gt_n1 = tests["P1"]["P1a"]["full_gt_N1"]
p1_mean_viab = tests["P1"]["P1b"]["mean_viability"]
p1_folios_lt_1 = tests["P1"]["P1b"]["folios_lt_1"]
p2_n_sig = tests["P2"]["n_significant"]
p3_mean_cycles = tests["P3"]["mean_cycles"]
p3_bounded_frac = tests["P3"]["mean_bounded_fraction"]
p3_n_meeting = tests["P3"]["n_meeting_both"]
p7_null_pass = tests["P7"]["null_types_pass"]
d1_ratio = diag["D1"]["mean_corridor_ratio"]
d2_occ = diag["D2"]["mean_corridor_occupancy"]
d3_delta = diag["D3"]["mean_viab_delta"]
d3_n_gt = diag["D3"]["n_full_gt_B9"]

# BETA values from apparatus config
beta_x = t1["apparatus_config"]["BETA"]["X"]

verdict_rationale = (
    f"SELECTIVE_RESTORATION_FAILED: Only {n_pass}/9 tests pass (P2, P8), identical score to Phase 564. "
    f"The piecewise 3-zone selective restoration architecture IS mechanistically correct: "
    f"D1 confirms supervisory signal dominates restoring in the corridor (mean ratio={d1_ratio:.2f}), "
    f"D2 confirms substantial corridor occupancy ({d2_occ:.1%}), and D3/B9 (uniform restoring) produces "
    f"the strongest ablation signal in the entire apparatus line (mean viability delta=+{d3_delta:.3f}, "
    f"with individual folios dropping to 0.44-0.48). However, the edge barrier "
    f"(BETA values 2-5x higher than planned, especially BETA_X={beta_x}) creates an impenetrable "
    f"boundary that prevents viability loss for all models including nulls. Mean viability={p1_mean_viab:.5f}, "
    f"only {p1_folios_lt_1}/20 folios have viability<1.0 (need >=8). "
    f"P7 null destruction fails: {p7_null_pass}/4 null types destroyed. "
    f"This is a PROGRESSIVE negative result: unlike 564 which was a universal absorber everywhere, "
    f"564b proves the zone geometry is correct and identifies edge barrier strength as the specific "
    f"remaining free parameter."
)

# -- Summary table -------------------------------------------------------------

# Build P2 key_metric
p2_max_H = max(tests["P2"]["per_sv"][sv]["H"] for sv in tests["P2"]["per_sv"])
p2_max_sv = max(tests["P2"]["per_sv"], key=lambda sv: tests["P2"]["per_sv"][sv]["H"])

summary_table = {
    "P1_viable_envelope": {
        "pass": False,
        "key_metric": (
            f"full_gt_B2={p1_full_gt_b2}/20, full_gt_N1={p1_full_gt_n1}/20; "
            f"mean_viab={p1_mean_viab:.5f}, folios_lt_1={p1_folios_lt_1}/20 (need >=8)"
        )
    },
    "P2_packet_shape": {
        "pass": True,
        "key_metric": f"n_significant={p2_n_sig}/7 SVs; strongest H={p2_max_H:.1f} ({p2_max_sv})"
    },
    "P3_bounded_cycles": {
        "pass": False,
        "key_metric": (
            f"mean_cycles={p3_mean_cycles:.1f}, "
            f"bounded_frac={p3_bounded_frac:.3f}, "
            f"n_meeting_both={p3_n_meeting}/20"
        )
    },
    "P4_routing_consequence": {
        "pass": False,
        "key_metric": (
            f"P4a: {tests['P4']['P4a']['n_correct']}/4 correct; "
            f"P4b: viab_delta={tests['P4']['P4b']['full_vs_B4_viab_delta']:.5f}"
        )
    },
    "P5_headless_config": {
        "pass": False,
        "key_metric": (
            f"P5a: C_better={tests['P5']['P5a']['C_better']}/20, "
            f"S_better={tests['P5']['P5a']['S_better']}/20; "
            f"P5b: H={tests['P5']['P5b']['H']:.4f}, p={tests['P5']['P5b']['p']:.3f}"
        )
    },
    "P6_cts_closure": {
        "pass": False,
        "key_metric": (
            f"viab_better={tests['P6']['viab_better']}/20, "
            f"C_sep_positive={tests['P6']['C_sep_positive']}/20; "
            "full=B3 identical (CTS has no effect under impenetrable edge barrier)"
        )
    },
    "P7_null_destruction": {
        "pass": False,
        "key_metric": (
            f"null_types_pass={p7_null_pass}/4; "
            "all null viab~1.0 with std~0 (edge barrier prevents viability loss for all inputs)"
        )
    },
    "P8_profile_superiority": {
        "pass": True,
        "key_metric": (
            f"preferred_best={tests['P8']['preferred_best']}/20 "
            "(trivially true: all viab~1.0, discrimination on Y_final only)"
        )
    },
    "P9_section_template": {
        "pass": None,
        "key_metric": (
            f"n_significant={tests['P9']['n_significant']}/7 SVs; SECONDARY"
        )
    }
}

# -- Composite metrics from t3 reference runs ---------------------------------

# Reference runs in T3 are the preferred-profile full model runs
ref = t3["reference"]
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

composite_metrics = {
    "mean_viability": round(mean_viab, 5),
    "mean_Y_final": round(mean_y, 4),
    "total_hazard_events": total_hazard,
    "folios_with_perfect_viability": f"{n_perfect_viab}/{len(viabilities)}",
    "mean_corridor_occupancy": round(d2_occ, 4),
    "mean_corridor_signal_ratio": round(d1_ratio, 2),
    "B9_mean_viab_delta": round(d3_delta, 3),
    "comparison": {
        "563":  {"mean_viability": 0.9616, "mean_Y_final": 0.878, "total_hazard": 34, "perfect_viab": "4/7"},
        "563b": {"mean_viability": 0.9635, "mean_Y_final": 0.848, "total_hazard": 255, "perfect_viab": "12/20"},
        "564":  {"mean_viability": 1.0, "mean_Y_final": 0.7366, "total_hazard": 0, "perfect_viab": "20/20"},
        "564b": {
            "mean_viability": round(mean_viab, 5),
            "mean_Y_final": round(mean_y, 4),
            "total_hazard": total_hazard,
            "perfect_viab": f"{n_perfect_viab}/{len(viabilities)}",
            "corridor_occupancy": round(d2_occ, 4),
            "signal_ratio": round(d1_ratio, 2)
        }
    }
}

# -- Diagnostic status ---------------------------------------------------------

diagnostic_status = {
    "D1_signal_ratio": {
        "status": "OK" if not diag["D1"]["quasi_gate_failed"] else "FAILED",
        "value": round(d1_ratio, 2),
        "quasi_gate": "PASS" if not diag["D1"]["quasi_gate_failed"] else "FAIL",
        "per_sv": {sv: round(diag["D1"]["per_sv"][sv]["ratio"], 2)
                   for sv in diag["D1"]["per_sv"]}
    },
    "D2_corridor_occupancy": {
        "status": "OK" if not diag["D2"]["quasi_gate_failed"] else "FAILED",
        "value": round(d2_occ, 4),
        "quasi_gate": "PASS" if not diag["D2"]["quasi_gate_failed"] else "FAIL",
        "per_sv": {sv: round(diag["D2"]["per_sv"][sv]["corridor"], 4)
                   for sv in diag["D2"]["per_sv"]}
    },
    "D3_B9_comparison": {
        "status": "INFORMATIVE",
        "mean_delta": round(d3_delta, 3),
        "n_full_gt_B9": d3_n_gt,
        "largest_drops": []
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

# -- Lessons learned -----------------------------------------------------------

lessons_learned = [
    (
        "The piecewise zone architecture IS correct (D1 OK, D2 OK, B9 proves zones matter). "
        "564b establishes that the 563-564 bracket can be resolved with spatially selective "
        "restoration. The corridor functions exactly as designed: signal dominates restoring "
        f"(ratio {d1_ratio:.2f}), and state regularly enters the corridor ({d2_occ:.1%} occupancy)."
    ),
    (
        f"The edge barrier is now the discriminability bottleneck. BETA values (especially "
        f"BETA_X={beta_x}, up from spec's 16.0) create an impenetrable boundary that prevents "
        f"viability loss for all models including nulls. T1's V5 self-test drove these values "
        f"up to ensure P99 input resilience, but this made the edge too strong for real-world "
        f"supervisory signals."
    ),
    (
        "B9 (uniform restoring) produced the strongest ablation signal in the entire apparatus "
        f"line: mean viability delta +{d3_delta:.3f}, with individual folios dropping to 0.44-0.48. "
        f"This is the first ablation to produce large, consistent viability differences. It proves "
        f"that the zone geometry (not just overall strength) matters for viability outcomes."
    ),
    (
        f"P2 packet shape ({p2_n_sig}/7 significant) remains the most robust coupling signal "
        "across all four phases (563, 563b, 564, 564b). It survived over-stabilization, "
        "under-stabilization, parametric recalibration, and zone restructuring. Line-level "
        "SPEC/WORK/CLOSE differentiation is architecture-independent."
    ),
    (
        "The basin calibration (gamma_basin values 2-8x higher than spec for some SVs) "
        "contributes to over-stiffness near equilibrium but is partially offset by the "
        "corridor signal ratio. The basin is too stiff and the edge is impenetrable, but "
        "the corridor in between works correctly."
    ),
    (
        "Unlike Phase 564 where the cubic restoring force was a universal absorber everywhere, "
        "564b's failure is localized: the edge barrier specifically. The basin and corridor "
        "zones show appropriate dynamics. This makes 564b a progressive negative result: "
        "it narrows the parametric space to a single identified parameter."
    ),
]

# -- Build output --------------------------------------------------------------

output = {
    "metadata": {
        "phase": "564b",
        "task": "T5_synthesis",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "verdict": verdict,
        "n_tests_total": 9,
        "n_tests_pass": n_pass,
        "n_tests_fail": n_fail,
        "n_constraints_proposed": 0
    },
    "verdict_rationale": verdict_rationale,
    "comparison_563_vs_563b_vs_564_vs_564b": comparison,
    "regressions_from_563": regressions_563,
    "regressions_from_564": regressions_564,
    "improvements_from_564": improvements_564,
    "summary_table": summary_table,
    "composite_metrics": composite_metrics,
    "diagnostic_status": diagnostic_status,
    "lessons_learned": lessons_learned,
    "constraints_note": (
        "SELECTIVE_RESTORATION_FAILED: no new constraints. This phase is a documented "
        "negative result that narrows the parametric space: zone geometry confirmed correct, "
        "edge barrier strength identified as the remaining free parameter."
    ),
    "implications_for_next_phase": [
        (
            "Reduce BETA values by 50-70% (especially X: 80.0 -> 25-30). The edge should "
            "resist P95 inputs but NOT make viability universal. Allow occasional P99 breaches."
        ),
        (
            "Reduce basin gamma values (S: 0.25 -> 0.10, X: 0.18 -> 0.08, Y: 0.25 -> 0.05). "
            "The basin should be genuinely soft -- state should drift within the basin with "
            "minimal restoring force."
        ),
        (
            "Target viability regime: full model ~0.92-0.97, baselines ~0.88-0.94, "
            "nulls ~0.80-0.90. This gives room for P1 (viability envelope), P7 (null "
            "destruction), and P6 (CTS closure) to discriminate."
        ),
        (
            "V5 self-test should be relaxed: edge barrier should prevent hazard violation "
            "under P95 input, not P99. Allow occasional P99 breaches to create viability "
            "variation."
        ),
        (
            "Cross-coupling may need attention if routing (P4) remains undetectable after "
            "edge recalibration. With softer edges, routing effects that currently cannot "
            "reach boundaries may become visible."
        ),
    ]
}

# -- Write output --------------------------------------------------------------

out_path = os.path.join(RESULTS_DIR, "t5_synthesis.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=1)

# -- Print summary -------------------------------------------------------------

print(f"Phase 564b T5 Synthesis")
print(f"=" * 60)
print(f"Verdict: {verdict}")
print(f"Tests: {n_pass}/9 pass, {n_fail}/9 fail")
print()

print("Cross-phase comparison:")
print(f"  {'Test':<6} {'563':<6} {'563b':<6} {'564':<6} {'564b':<6}")
print(f"  {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]:
    c = comparison[t]
    print(f"  {t:<6} {c['563']:<6} {c['563b']:<6} {c['564']:<6} {c['564b']:<6}")

print()
print(f"Regressions from 563: {regressions_563}")
print(f"Regressions from 564: {regressions_564}")
print(f"Improvements from 564: {improvements_564}")

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

print()
print("B9 largest viability drops:")
for drop in diagnostic_status["D3_B9_comparison"]["largest_drops"]:
    print(f"  {drop['folio']}: {drop['full_viab']:.3f} -> {drop['B9_viab']:.3f} "
          f"(delta={drop['viab_delta']:.3f})")

print()
print(f"Constraints proposed: 0")
print(f"Output: {out_path}")
