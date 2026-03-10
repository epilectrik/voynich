"""
T1b: Apparatus Recalibration
Phase 563b - ROUTING_ACCUMULATION_AND_DYNAMIC_RECALIBRATION

Updates the 3 apparatus profiles with revised decay/cross-coupling parameters,
adds a headless modulation function, runs decomposed recalibration self-tests
(R1/R2/R3), and validates with V1-V4.

Parameter changes:
  - Decay reductions (~30-40% on T, X) to allow excursion
  - Cross-coupling strengthening (alpha_YX, alpha_FC) for return dynamics
  - A2 decay_C slight increase (containment recovery)

Decomposition:
  R1 = decay-only changes
  R2 = cross-coupling-only changes
  R3 = full recalibration (both)

Self-tests:
  V1 (stability), V2 (hazard excursion), V3 (recovery), V4 (headless modulation)
"""

import json
import sys
import time
from pathlib import Path
from copy import deepcopy

# Import from T1
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
from t1_apparatus_family_builder import (
    VirtualApparatus, STATE_VARS, N_VARS, HAZARD_BOUNDARIES, EQUILIBRIUM,
    make_dv, run_self_tests, assign_folio_profiles, summarize_assignments,
)

# ---------------------------------------------------------------------------
# Original profiles (for comparison and decomposition baselines)
# ---------------------------------------------------------------------------
ORIGINAL_PROFILES = {
    "A1_BATH_REFLUX": {
        "sensitivity_T": 1.0, "sensitivity_RC": 1.2, "sensitivity_S": 1.1,
        "sensitivity_C": 0.7, "sensitivity_TR": 0.9, "sensitivity_X": 0.6,
        "sensitivity_Y": 1.1,
        "decay_T": 0.15, "decay_RC": 0.08, "decay_S": 0.05,
        "decay_C": 0.10, "decay_TR": 0.10, "decay_X": 0.12, "decay_Y": 0.03,
        "alpha_RT": 0.03, "alpha_TXS": 0.02, "alpha_XC": 0.03, "alpha_FC": 0.04,
        "alpha_TX": 0.04, "alpha_YX": 0.03, "alpha_FY": 0.06,
    },
    "A2_SEALED_RECIRCULATION": {
        "sensitivity_T": 0.8, "sensitivity_RC": 1.1, "sensitivity_S": 0.9,
        "sensitivity_C": 1.4, "sensitivity_TR": 0.7, "sensitivity_X": 0.9,
        "sensitivity_Y": 0.9,
        "decay_T": 0.10, "decay_RC": 0.06, "decay_S": 0.06,
        "decay_C": 0.04, "decay_TR": 0.12, "decay_X": 0.08, "decay_Y": 0.03,
        "alpha_RT": 0.04, "alpha_TXS": 0.04, "alpha_XC": 0.08, "alpha_FC": 0.02,
        "alpha_TX": 0.05, "alpha_YX": 0.04, "alpha_FY": 0.04,
    },
    "A3_DISTILL_COLLECT": {
        "sensitivity_T": 1.4, "sensitivity_RC": 0.7, "sensitivity_S": 0.8,
        "sensitivity_C": 1.0, "sensitivity_TR": 1.4, "sensitivity_X": 1.2,
        "sensitivity_Y": 1.3,
        "decay_T": 0.08, "decay_RC": 0.10, "decay_S": 0.08,
        "decay_C": 0.08, "decay_TR": 0.06, "decay_X": 0.06, "decay_Y": 0.02,
        "alpha_RT": 0.02, "alpha_TXS": 0.05, "alpha_XC": 0.05, "alpha_FC": 0.06,
        "alpha_TX": 0.07, "alpha_YX": 0.05, "alpha_FY": 0.08,
    },
}

# ---------------------------------------------------------------------------
# Parameter changes specification
# ---------------------------------------------------------------------------
PARAMETER_CHANGES = {
    "A1_BATH_REFLUX": {
        "decay_T":   {"old": 0.15, "new": 0.10, "rationale": "Allow thermal excursion"},
        "decay_X":   {"old": 0.12, "new": 0.08, "rationale": "Allow transition excursion"},
        "alpha_YX":  {"old": 0.03, "new": 0.04, "rationale": "Product dampens transitions -> creates return"},
    },
    "A2_SEALED_RECIRCULATION": {
        "decay_T":   {"old": 0.10, "new": 0.07, "rationale": "Allow thermal excursion"},
        "decay_X":   {"old": 0.08, "new": 0.05, "rationale": "Allow transition excursion"},
        "decay_C":   {"old": 0.04, "new": 0.05, "rationale": "Slight INCREASE - help containment recover"},
        "alpha_FC":  {"old": 0.02, "new": 0.04, "rationale": "Internal transfer relieves containment stress"},
        "alpha_YX":  {"old": 0.04, "new": 0.05, "rationale": "Product dampens transitions -> creates return"},
    },
    "A3_DISTILL_COLLECT": {
        "decay_T":   {"old": 0.08, "new": 0.05, "rationale": "Allow thermal excursion"},
        "decay_X":   {"old": 0.06, "new": 0.04, "rationale": "Allow transition excursion"},
        "alpha_YX":  {"old": 0.05, "new": 0.07, "rationale": "Product dampens transitions -> creates return"},
    },
}

# ---------------------------------------------------------------------------
# Build recalibrated profiles (R3 = full)
# ---------------------------------------------------------------------------
def build_recalibrated_profiles():
    """Apply all parameter changes to original profiles."""
    profiles = {}
    for name, orig in ORIGINAL_PROFILES.items():
        p = dict(orig)
        changes = PARAMETER_CHANGES.get(name, {})
        for param_key, change in changes.items():
            p[param_key] = change["new"]
        profiles[name] = p
    return profiles


def build_decay_only_profiles():
    """R1: Apply only decay changes, keep original cross-coupling."""
    decay_params = {"decay_T", "decay_X", "decay_C"}  # decay_C only changed for A2
    profiles = {}
    for name, orig in ORIGINAL_PROFILES.items():
        p = dict(orig)
        changes = PARAMETER_CHANGES.get(name, {})
        for param_key, change in changes.items():
            if param_key in decay_params:
                p[param_key] = change["new"]
        profiles[name] = p
    return profiles


def build_crosscoupling_only_profiles():
    """R2: Apply only cross-coupling changes, keep original decay."""
    alpha_params = {"alpha_YX", "alpha_FC"}
    profiles = {}
    for name, orig in ORIGINAL_PROFILES.items():
        p = dict(orig)
        changes = PARAMETER_CHANGES.get(name, {})
        for param_key, change in changes.items():
            if param_key in alpha_params:
                p[param_key] = change["new"]
        profiles[name] = p
    return profiles


# ---------------------------------------------------------------------------
# Headless modulation function (exported for T3b)
# ---------------------------------------------------------------------------
def apply_headless_modulation(profile_params, folio_hl_rate):
    """
    Modulate apparatus profile based on folio headless rate.

    Higher headless rate -> more containment/stability infrastructure:
      - Higher C/S sensitivity (headless tokens build containment)
      - Slower C/S decay (infrastructure persists)
      - Stronger X->C coupling (transitions channeled through containment)

    Parameters:
        profile_params: dict of apparatus parameters
        folio_hl_rate: fraction of headless tokens in folio (typically 0.15-0.40)

    Returns:
        dict: modulated parameters (new dict, does not modify input)
    """
    params = dict(profile_params)
    hl_norm = folio_hl_rate / 0.25  # normalized to reference rate

    # Higher headless -> more containment/stability sensitivity
    params['sensitivity_C'] *= (1.0 + 0.15 * (hl_norm - 1.0))
    params['sensitivity_S'] *= (1.0 + 0.10 * (hl_norm - 1.0))

    # Higher headless -> slower C/S decay (infrastructure persists)
    params['decay_C'] *= max(0.5, 1.0 - 0.10 * (hl_norm - 1.0))
    params['decay_S'] *= max(0.5, 1.0 - 0.10 * (hl_norm - 1.0))

    # Higher headless -> stronger X->C coupling
    params['alpha_XC'] *= (1.0 + 0.10 * (hl_norm - 1.0))

    return params


# ---------------------------------------------------------------------------
# V4: Headless modulation test
# ---------------------------------------------------------------------------
def run_v4_headless_test(profile_name, params):
    """
    V4: Verify headless modulation raises C and S means.

    Uses a realistic mixed-activity scenario (mild T, X, and S pushes) so
    that cross-coupling activates C movement. A pure S-only push leaves C
    at exactly 0.5 because no external force or cross-coupling input reaches
    C without X or TR deviating first.

    Run 100 steps with mixed activity for:
      - hl_rate = 0.40 (high headless)
      - hl_rate = 0.15 (low headless)

    PASS if C_mean and S_mean are both higher for hl_rate=0.40.
    """
    s_idx = STATE_VARS.index("S")
    c_idx = STATE_VARS.index("C")
    t_idx = STATE_VARS.index("T")
    x_idx = STATE_VARS.index("X")

    results = {}

    for hl_rate in [0.15, 0.40]:
        mod_params = apply_headless_modulation(params, hl_rate)
        app = VirtualApparatus(mod_params)

        # Mixed-activity dV: mild thermal + mild transition + stability push
        # This exercises cross-coupling paths that feed C (alpha_XC, alpha_FC)
        # Magnitudes kept gentle to avoid saturation (A2 has sensitivity_C=1.4)
        dv_mixed = [0.0] * N_VARS
        dv_mixed[t_idx] = 0.008 * mod_params["sensitivity_T"]   # mild thermal
        dv_mixed[x_idx] = 0.012 * mod_params["sensitivity_X"]   # mild transition
        dv_mixed[s_idx] = 0.005 * mod_params["sensitivity_S"]   # stability push

        initial = [0.5] * N_VARS
        traj = app.run_trajectory(initial, [dv_mixed] * 100)

        # Mean of last 20 steps
        c_vals = [traj[step][c_idx] for step in range(81, 101)]
        s_vals = [traj[step][s_idx] for step in range(81, 101)]

        label = f"hl_{hl_rate:.2f}"
        results[label] = {
            "hl_rate": hl_rate,
            "C_mean_last20": round(sum(c_vals) / len(c_vals), 6),
            "S_mean_last20": round(sum(s_vals) / len(s_vals), 6),
            "final_state": [round(v, 4) for v in traj[-1]],
        }

    # Compare
    c_high = results["hl_0.40"]["C_mean_last20"]
    c_low = results["hl_0.15"]["C_mean_last20"]
    s_high = results["hl_0.40"]["S_mean_last20"]
    s_low = results["hl_0.15"]["S_mean_last20"]

    v4_pass = (c_high > c_low) and (s_high > s_low)

    return {
        "V4_headless": v4_pass,
        "V4_C_high_hl": c_high,
        "V4_C_low_hl": c_low,
        "V4_C_delta": round(c_high - c_low, 6),
        "V4_S_high_hl": s_high,
        "V4_S_low_hl": s_low,
        "V4_S_delta": round(s_high - s_low, 6),
        "V4_details": results,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    phase_dir = Path(__file__).resolve().parent.parent  # VIRTUAL_APPARATUS_COUPLING/
    project_root = phase_dir.parent.parent  # voynich/

    regime_path = project_root / "data" / "regime_folio_mapping.json"
    budget_path = (project_root / "phases"
                   / "SECTION_TEMPLATE_TRACE_EXECUTOR" / "results"
                   / "t2_folio_budgets.json")
    output_path = phase_dir / "results" / "t1b_apparatus_recalibrated.json"

    print("=" * 70)
    print("T1b: Apparatus Recalibration")
    print("Phase 563b - ROUTING_ACCUMULATION_AND_DYNAMIC_RECALIBRATION")
    print("=" * 70)

    # Build profile variants
    recalibrated = build_recalibrated_profiles()  # R3 = full
    decay_only = build_decay_only_profiles()       # R1
    crosscoupling_only = build_crosscoupling_only_profiles()  # R2

    profile_names = ["A1_BATH_REFLUX", "A2_SEALED_RECIRCULATION",
                     "A3_DISTILL_COLLECT"]

    # --- Decomposition: R1, R2, R3 self-tests ---
    print("\n--- Recalibration Decomposition ---")

    decomposition = {}
    variant_labels = {
        "R1_decay_only": decay_only,
        "R2_crosscoupling_only": crosscoupling_only,
        "R3_full": recalibrated,
    }

    for pname in profile_names:
        print(f"\n  Profile: {pname}")
        decomposition[pname] = {}

        # Also show original for comparison
        orig_results = run_self_tests(pname, ORIGINAL_PROFILES[pname])
        print(f"    Original:  V1={'PASS' if orig_results['V1_stable'] else 'FAIL'}  "
              f"V2={'PASS' if orig_results['V2_hazard'] else 'FAIL'}  "
              f"V3={'PASS' if orig_results['V3_recovery'] else 'FAIL'}")
        print(f"      V1 final: {orig_results['V1_final_state']}")
        print(f"      V2 max_X: {orig_results['V2_max_X']}")
        print(f"      V3 final_X: {orig_results['V3_final_X']}")
        decomposition[pname]["original"] = {
            "V1_stable": orig_results["V1_stable"],
            "V2_hazard": orig_results["V2_hazard"],
            "V3_recovery": orig_results["V3_recovery"],
            "V1_final_state": orig_results["V1_final_state"],
            "V1_max_deviation": orig_results["V1_max_deviation"],
            "V2_max_X": orig_results["V2_max_X"],
            "V3_final_X": orig_results["V3_final_X"],
            "V3_recovered_within_20": orig_results["V3_recovered_within_20"],
        }

        for variant_name, variant_profiles in variant_labels.items():
            results = run_self_tests(pname, variant_profiles[pname])
            print(f"    {variant_name:25s}:  V1={'PASS' if results['V1_stable'] else 'FAIL'}  "
                  f"V2={'PASS' if results['V2_hazard'] else 'FAIL'}  "
                  f"V3={'PASS' if results['V3_recovery'] else 'FAIL'}")
            print(f"      V1 final: {results['V1_final_state']}")
            print(f"      V2 max_X: {results['V2_max_X']}")
            print(f"      V3 final_X: {results['V3_final_X']}")
            decomposition[pname][variant_name] = {
                "V1_stable": results["V1_stable"],
                "V2_hazard": results["V2_hazard"],
                "V3_recovery": results["V3_recovery"],
                "V1_final_state": results["V1_final_state"],
                "V1_max_deviation": results["V1_max_deviation"],
                "V1_max_late_delta": results["V1_max_late_delta"],
                "V2_max_X": results["V2_max_X"],
                "V2_step_at_max_X": results["V2_step_at_max_X"],
                "V3_final_X": results["V3_final_X"],
                "V3_max_X_during_active": results["V3_max_X_during_active"],
                "V3_recovered_within_20": results["V3_recovered_within_20"],
            }

    # --- V1-V3 on final (R3) profiles ---
    print("\n--- Final Recalibrated Self-Tests (V1-V3) ---")
    all_tests = {}
    all_pass = True

    for pname in profile_names:
        print(f"\n  Profile: {pname}")
        test_results = run_self_tests(pname, recalibrated[pname])
        all_tests[pname] = {
            "V1_stable": test_results["V1_stable"],
            "V1_final_state": test_results["V1_final_state"],
            "V1_max_deviation": test_results["V1_max_deviation"],
            "V1_max_late_delta": test_results["V1_max_late_delta"],
            "V1_converged": test_results["V1_converged"],
            "V1_no_hazard": test_results["V1_no_hazard"],
            "V2_hazard": test_results["V2_hazard"],
            "V2_max_X": test_results["V2_max_X"],
            "V2_step_at_max_X": test_results["V2_step_at_max_X"],
            "V3_recovery": test_results["V3_recovery"],
            "V3_final_X": test_results["V3_final_X"],
            "V3_max_X_during_active": test_results["V3_max_X_during_active"],
            "V3_recovered_within_20": test_results["V3_recovered_within_20"],
        }

        for test_name in ["V1_stable", "V2_hazard", "V3_recovery"]:
            status = "PASS" if test_results[test_name] else "FAIL"
            print(f"    {test_name}: {status}")
            if not test_results[test_name]:
                all_pass = False

        print(f"    V1 final: {test_results['V1_final_state']}")
        print(f"    V1 max deviation: {test_results['V1_max_deviation']}")
        print(f"    V2 max X: {test_results['V2_max_X']} "
              f"(step {test_results['V2_step_at_max_X']})")
        print(f"    V3 max X active: {test_results['V3_max_X_during_active']}")
        print(f"    V3 final X: {test_results['V3_final_X']}")
        print(f"    V3 recovered <20 steps: {test_results['V3_recovered_within_20']}")

    # --- V4: Headless modulation ---
    print("\n--- V4: Headless Modulation Tests ---")
    v4_results = {}

    for pname in profile_names:
        print(f"\n  Profile: {pname}")
        v4 = run_v4_headless_test(pname, recalibrated[pname])
        v4_results[pname] = v4

        status = "PASS" if v4["V4_headless"] else "FAIL"
        print(f"    V4_headless: {status}")
        print(f"    C_mean: high_hl={v4['V4_C_high_hl']:.6f}  "
              f"low_hl={v4['V4_C_low_hl']:.6f}  "
              f"delta={v4['V4_C_delta']:+.6f}")
        print(f"    S_mean: high_hl={v4['V4_S_high_hl']:.6f}  "
              f"low_hl={v4['V4_S_low_hl']:.6f}  "
              f"delta={v4['V4_S_delta']:+.6f}")

        # Update all_tests
        all_tests[pname]["V4_headless"] = v4["V4_headless"]
        if not v4["V4_headless"]:
            all_pass = False

    if all_pass:
        print("\n  ALL SELF-TESTS PASSED (V1-V4)")
    else:
        print("\n  *** SOME SELF-TESTS FAILED ***")

    # --- Folio assignments (reuse from T1) ---
    print("\n--- Folio Assignments (reused from T1) ---")
    assignments = assign_folio_profiles(regime_path, budget_path)
    summary = summarize_assignments(assignments)

    print(f"  Total folios assigned: {len(assignments)}")
    for pname in profile_names:
        if pname in summary:
            s = summary[pname]
            sec_str = ", ".join(
                f"{k}={v}" for k, v in sorted(s["sections"].items()))
            print(f"  {pname}: {s['n_folios']} folios ({sec_str})")

    # --- Parameter change summary ---
    print("\n--- Parameter Changes Summary ---")
    for pname in profile_names:
        changes = PARAMETER_CHANGES.get(pname, {})
        if changes:
            print(f"\n  {pname}:")
            for param, info in changes.items():
                pct = (info['new'] - info['old']) / info['old'] * 100
                print(f"    {param}: {info['old']} -> {info['new']} "
                      f"({pct:+.1f}%) -- {info['rationale']}")

    # --- Decomposition summary ---
    print("\n--- Decomposition Summary ---")
    print(f"  {'Profile':<30s} {'Variant':<25s} V2_max_X  V3_final_X")
    print(f"  {'-'*30} {'-'*25} {'-'*8}  {'-'*10}")
    for pname in profile_names:
        for vname in ["original", "R1_decay_only", "R2_crosscoupling_only", "R3_full"]:
            d = decomposition[pname][vname]
            print(f"  {pname:<30s} {vname:<25s} {d['V2_max_X']:.4f}   {d['V3_final_X']:.4f}")

    # --- Build output ---
    output = {
        "metadata": {
            "phase": "563b",
            "task": "T1b_apparatus_recalibration",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_folios": len(assignments),
            "all_self_tests_passed": all_pass,
            "tests_run": ["V1_stable", "V2_hazard", "V3_recovery", "V4_headless"],
        },
        "profiles": {n: dict(p) for n, p in recalibrated.items()},
        "original_profiles": {n: dict(p) for n, p in ORIGINAL_PROFILES.items()},
        "parameter_changes": PARAMETER_CHANGES,
        "decomposition": decomposition,
        "self_tests": all_tests,
        "headless_modulation": {
            "parameters": {
                "reference_hl_rate": 0.25,
                "sensitivity_C_scale": 0.15,
                "sensitivity_S_scale": 0.10,
                "decay_C_scale": 0.10,
                "decay_S_scale": 0.10,
                "alpha_XC_scale": 0.10,
                "min_decay_multiplier": 0.5,
            },
            "v4_results": v4_results,
        },
        "folio_assignments": assignments,
        "assignment_summary": summary,
        "state_spec": {
            "variables": STATE_VARS,
            "hazard_boundaries": HAZARD_BOUNDARIES,
            "equilibrium": EQUILIBRIUM,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=1)

    print(f"\n  Output: {output_path}")
    print(f"  Size: {output_path.stat().st_size:,} bytes")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
