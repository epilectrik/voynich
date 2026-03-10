"""
Phase 564 T5: Synthesis — aggregate results, cross-phase comparison, verdict.

Reads:
  - t4_behavior_validation.json  (9 tests + 2 diagnostics)
  - t2_event_gated_runs.json     (composite metrics: viability, Y_final, hazard)

Writes:
  - t5_synthesis.json

Verdict logic:
  - EVENT_GATED_COUPLING_VALIDATED: P1+P2+P3+P4+P7 all PASS, plus >=1 of P5/P6/P8
  - PARTIAL_EVENT_COUPLING: P1+P2+P7 pass but P3 or P4 weak
  - EVENT_GATING_FAILED: No improvement over 563 on P3/P4
"""

import json
import os
from datetime import datetime

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, "results")

# ── Load inputs ─────────────────────────────────────────────────────────────

with open(os.path.join(RESULTS_DIR, "t4_behavior_validation.json")) as f:
    t4 = json.load(f)

with open(os.path.join(RESULTS_DIR, "t2_event_gated_runs.json")) as f:
    t2 = json.load(f)

tests = t4["tests"]
diag = t4["diagnostics"]

# ── Extract test pass/fail ──────────────────────────────────────────────────

test_results = {
    "P1": tests["P1_viable_envelope"]["pass"],
    "P2": tests["P2_packet_shape"]["pass"],
    "P3": tests["P3_bounded_cycles"]["pass"],
    "P4": tests["P4_routing_consequence"]["pass"],
    "P5": tests["P5_headless_config"]["pass"],
    "P6": tests["P6_cts_closure"]["pass"],
    "P7": tests["P7_null_destruction"]["pass"],
    "P8": tests["P8_profile_superiority"]["pass"],
    "P9": tests["P9_section_template"]["pass"],  # None = SEC
}

n_pass = sum(1 for v in test_results.values() if v is True)
n_fail = sum(1 for v in test_results.values() if v is not True)  # None (SEC) counts as not-pass

# ── Phase 563 and 563b reference results ────────────────────────────────────

results_563 = {
    "P1": True, "P2": True, "P3": False, "P4": False,
    "P5": False, "P6": True, "P7": True, "P8": True, "P9": None
}

results_563b = {
    "P1": False, "P2": True, "P3": False, "P4": False,
    "P5": False, "P6": True, "P7": False, "P8": True, "P9": None
}

# ── Cross-phase comparison table ────────────────────────────────────────────

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
        "564": pass_str(test_results[t]),
    }

# ── Regressions and improvements ───────────────────────────────────────────

regressions_563 = []
improvements_563 = []
regressions_563b = []
improvements_563b = []

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

# ── Verdict ─────────────────────────────────────────────────────────────────

core_pass = all(test_results[t] for t in ["P1", "P2", "P3", "P4", "P7"])
secondary_pass = any(test_results[t] for t in ["P5", "P6", "P8"])
weak_core = all(test_results[t] for t in ["P1", "P2", "P7"])

if core_pass and secondary_pass:
    verdict = "EVENT_GATED_COUPLING_VALIDATED"
elif weak_core:
    verdict = "PARTIAL_EVENT_COUPLING"
else:
    verdict = "EVENT_GATING_FAILED"

# ── Verdict rationale ──────────────────────────────────────────────────────

verdict_rationale = (
    "EVENT_GATING_FAILED: Only 2/9 tests pass (P2, P8), down from 5/9 in Phase 563 "
    "and 3/9 in Phase 563b. The nonlinear restoring force (cubic stiffening d_nonlinear=1.0-1.5) "
    "combined with original linear decay parameters creates an impenetrable equilibrium basin. "
    "Universal viability=1.0 collapses all viability-based discrimination: P1 (full=B2=N1=1.0), "
    "P6 (full=B3 identical), P7 (0/4 null types destroyed, all viab=1.0 with std=0). "
    "P3 bounded cycles (mean=2.8, bounded_frac=0.126) show only A3 profile folios oscillate. "
    "P4 routing (1/4 correct) regressed from 563b (2/4): only m->C survives (p~0, delta=+0.063). "
    "The event-gated architecture adds too many restoring mechanisms (linear + cubic + threshold + "
    "phase multiplier), each individually reasonable but combined creating over-stabilization "
    "that kills all discriminability."
)

# ── Summary table ──────────────────────────────────────────────────────────

summary_table = {
    "P1_viable_envelope": {
        "pass": False,
        "key_metric": "full_gt_B2=0/20, full_gt_N1=0/20; all viabilities=1.0 (full=B2=N1)"
    },
    "P2_packet_shape": {
        "pass": True,
        "key_metric": f"n_significant=7/7 SVs; strongest H={max(tests['P2_packet_shape']['per_sv'][sv]['H'] for sv in tests['P2_packet_shape']['per_sv']):.1f} (Y)"
    },
    "P3_bounded_cycles": {
        "pass": False,
        "key_metric": (
            f"mean_cycles={tests['P3_bounded_cycles']['mean_n_cycles']:.1f}, "
            f"bounded_frac={tests['P3_bounded_cycles']['mean_bounded_fraction']:.3f}, "
            f"n_meeting_both={tests['P3_bounded_cycles']['n_folios_meeting_both']}/20"
        )
    },
    "P4_routing_consequence": {
        "pass": False,
        "key_metric": (
            "P4a: 1/4 correct (m->C only, delta=+0.063, p~0); "
            "r->X wrong dir, y->T wrong dir, h->TR wrong dir"
        )
    },
    "P5_headless_config": {
        "pass": False,
        "key_metric": (
            f"P5a: n_c_better={tests['P5_headless_config']['P5a']['n_c_better']}/20, "
            f"n_s_better={tests['P5_headless_config']['P5a']['n_s_better']}/20; "
            f"P5b: C p={tests['P5_headless_config']['P5b']['C']['p']:.3f}, "
            f"S p={tests['P5_headless_config']['P5b']['S']['p']:.3f}"
        )
    },
    "P6_cts_closure": {
        "pass": False,
        "key_metric": (
            f"viab_better={tests['P6_cts_closure']['n_viab_better']}/20, "
            f"sep_positive={tests['P6_cts_closure']['n_sep_positive']}/20; "
            "full=B3 identical (CTS has no effect under over-stiffened plant)"
        )
    },
    "P7_null_destruction": {
        "pass": False,
        "key_metric": (
            f"null_types_pass={tests['P7_null_destruction']['n_null_types_pass']}/4; "
            "all null viab=1.0 with std=0 (plant cannot distinguish structured from random)"
        )
    },
    "P8_profile_superiority": {
        "pass": True,
        "key_metric": (
            f"preferred_best={tests['P8_profile_superiority']['n_preferred_best']}/20 "
            "(trivially true: all viab=1.0, discrimination on Y_final only)"
        )
    },
    "P9_section_template": {
        "pass": None,
        "key_metric": (
            f"n_significant={tests['P9_section_template']['n_significant']}/7 SVs (S, Y); SECONDARY"
        )
    }
}

# ── Composite metrics from t2 ──────────────────────────────────────────────

runs = t2["runs"]
viabilities = []
y_finals = []
hazard_counts = []
n_perfect_viab = 0

# Only preferred profile runs (primary runs)
for key, run in runs.items():
    if run.get("is_preferred", False):
        s = run["summary"]
        viabilities.append(s["viability_fraction"])
        y_finals.append(s["Y_final"])
        hazard_counts.append(s["hazard_count"])
        if s["viability_fraction"] == 1.0:
            n_perfect_viab += 1

mean_viab = sum(viabilities) / len(viabilities) if viabilities else 0
mean_y = sum(y_finals) / len(y_finals) if y_finals else 0
total_hazard = sum(hazard_counts)

composite_metrics = {
    "mean_viability": round(mean_viab, 4),
    "mean_Y_final": round(mean_y, 4),
    "total_hazard_events": total_hazard,
    "folios_with_perfect_viability": f"{n_perfect_viab}/{len(viabilities)}",
    "comparison": {
        "563":  {"mean_viability": 0.9616, "mean_Y_final": 0.878, "total_hazard": 34, "perfect_viab": "4/7"},
        "563b": {"mean_viability": 0.9635, "mean_Y_final": 0.848, "total_hazard": 255, "perfect_viab": "12/20"},
        "564":  {
            "mean_viability": round(mean_viab, 4),
            "mean_Y_final": round(mean_y, 4),
            "total_hazard": total_hazard,
            "perfect_viab": f"{n_perfect_viab}/{len(viabilities)}"
        }
    }
}

# ── Lessons learned ─────────────────────────────────────────────────────────

lessons_learned = [
    (
        "Over-stabilization is as fatal as under-stabilization. Phase 563 had too little "
        "decay leading to hazard violations. Phase 564 has too much restoring force — "
        "universal viability=1.0 kills all discrimination. The cubic restoring force "
        "(d_nonlinear=1.0-1.5) combined with the original 563 linear decay parameters "
        "absorbs all supervisory signal variation before it can reach hazard boundaries."
    ),
    (
        "Self-test V7 is a necessary but not sufficient gate. Synthetic inputs (dV=0.08-0.15) "
        "produce oscillation; real supervisory traces (dV~0.01-0.05) do not. Future self-tests "
        "must calibrate dV magnitudes against actual supervisory signal distributions."
    ),
    (
        "A3 profile CAN oscillate (5/20 folios meet P3 criterion). The architecture is not "
        "wrong — the parametric regime is. Linear decay needs reduction (not increase) when "
        "cubic stiffening is added. Profile-dependent oscillation confirms the mechanism: "
        "A3 (DISTILL_COLLECT, highest sensitivity) produces 5-13 cycles in S-section folios; "
        "A1 (BATH_REFLUX, lowest sensitivity) produces 0 cycles."
    ),
    (
        "P2 packet shape (7/7 significant) is the most robust coupling signal across all "
        "three phases (563, 563b, 564). It survived over-stabilization, under-stabilization, "
        "and parametric recalibration. Line-level SPEC/WORK/CLOSE remains the primary "
        "grammar-to-apparatus coupling channel."
    ),
    (
        "m->C routing remains the strongest and most robust routing signal. It passed in "
        "563b (delta=+0.065, p~0) and 564 (delta=+0.063, p~0). All other routes (r->X, "
        "y->T, h->TR) failed in 564, regressing from 563b where h->TR also passed."
    ),
    (
        "The additive architecture (linear + cubic + threshold + phase multiplier) layers "
        "too many restoring mechanisms. Each is individually reasonable; combined they create "
        "an impenetrable equilibrium basin. D1 shows B7 (minus thresholds) has identical "
        "outcomes. D2 shows B8 (fixed WORK law) has identical outcomes. Both confirm the "
        "restoring force dominates all other dynamics."
    ),
]

# ── Build output ────────────────────────────────────────────────────────────

output = {
    "metadata": {
        "phase": "564",
        "task": "T5_synthesis",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "verdict": verdict,
        "n_tests_total": 9,
        "n_tests_pass": n_pass,
        "n_tests_fail": n_fail,
        "n_constraints_proposed": 0
    },
    "verdict_rationale": verdict_rationale,
    "comparison_563_vs_563b_vs_564": comparison,
    "regressions_from_563": regressions_563,
    "regressions_from_563b": regressions_563b,
    "improvements_from_563": improvements_563,
    "improvements_from_563b": improvements_563b,
    "summary_table": summary_table,
    "composite_metrics": composite_metrics,
    "lessons_learned": lessons_learned,
    "constraints_note": (
        "EVENT_GATING_FAILED: no new constraints. Phase 563 constraints C1581-C1587 "
        "remain valid for the original 563 configuration. This phase is a documented "
        "negative result."
    )
}

# ── Write output ────────────────────────────────────────────────────────────

out_path = os.path.join(RESULTS_DIR, "t5_synthesis.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=1)

# ── Print summary ───────────────────────────────────────────────────────────

print(f"Phase 564 T5 Synthesis")
print(f"=" * 60)
print(f"Verdict: {verdict}")
print(f"Tests: {n_pass}/9 pass, {n_fail}/9 fail")
print()

print("Cross-phase comparison:")
print(f"  {'Test':<6} {'563':<6} {'563b':<6} {'564':<6}")
print(f"  {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
for t in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"]:
    print(f"  {t:<6} {comparison[t]['563']:<6} {comparison[t]['563b']:<6} {comparison[t]['564']:<6}")

print()
print(f"Regressions from 563: {regressions_563}")
print(f"Regressions from 563b: {regressions_563b}")
print(f"Improvements from 563: {improvements_563}")
print(f"Improvements from 563b: {improvements_563b}")

print()
print("Composite metrics:")
print(f"  Mean viability: {composite_metrics['mean_viability']}")
print(f"  Mean Y_final:   {composite_metrics['mean_Y_final']}")
print(f"  Total hazard:   {composite_metrics['total_hazard_events']}")
print(f"  Perfect viab:   {composite_metrics['folios_with_perfect_viability']}")

print()
print(f"Constraints proposed: 0")
print(f"Output: {out_path}")
