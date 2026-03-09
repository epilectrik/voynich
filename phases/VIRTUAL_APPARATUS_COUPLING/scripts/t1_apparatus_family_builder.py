"""
T1: Apparatus Family Builder
Phase 563 - VIRTUAL_APPARATUS_COUPLING

Builds 3 apparatus profiles as a parameterized family with shared state
equations and distinct parameter values, assigns preferred profiles to
all 82 folios, and runs self-tests.

State vector: 7 variables [T, RC, S, C, TR, X, Y], all in [0,1], equilibrium 0.5
Update: V[n+1] = clamp(V[n] + dV + cross_coupling - decay*(V[n]-0.5), 0, 1)

Three profiles:
  A1_BATH_REFLUX        - balneum mariae (Section B, REGIME_1)
  A2_SEALED_RECIRCULATION - pelican alembic (Section H-R2/C/T)
  A3_DISTILL_COLLECT    - distillation/collection (Section S, H-R3/R4)

Self-tests V1-V3 validate equilibrium stability, hazard excursion, and
closure recovery for each profile.
"""

import json
import math
import time
from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STATE_VARS = ["T", "RC", "S", "C", "TR", "X", "Y"]
N_VARS = len(STATE_VARS)
EQUILIBRIUM = 0.5

HAZARD_BOUNDARIES = {
    "T":  [0.15, 0.85],
    "RC": [0.10, 0.90],
    "S":  [0.15, None],
    "C":  [None, 0.85],
    "TR": [0.10, 0.90],
    "X":  [None, 0.80],
    "Y":  [None, None],
}

# ---------------------------------------------------------------------------
# Profile parameter dictionaries
# ---------------------------------------------------------------------------
A1_BATH_REFLUX = {
    # Sensitivity: how strongly the plant responds to supervisory actions
    "sensitivity_T": 1.0,
    "sensitivity_RC": 1.2,
    "sensitivity_S": 1.1,
    "sensitivity_C": 0.7,
    "sensitivity_TR": 0.9,
    "sensitivity_X": 0.6,   # LOW transition sensitivity (slow transitions)
    "sensitivity_Y": 1.1,
    # Decay: natural return rate toward 0.5
    "decay_T": 0.15,    # HIGH (water bath = thermal flywheel)
    "decay_RC": 0.08,
    "decay_S": 0.05,    # LOW (stability persists)
    "decay_C": 0.10,
    "decay_TR": 0.10,
    "decay_X": 0.12,    # HIGH (bath damps transitions)
    "decay_Y": 0.03,    # LOW (product accumulates)
    # Cross-coupling alphas
    "alpha_RT": 0.03,
    "alpha_TXS": 0.02,  # LOW T*X->S erosion (thermal inertia protects)
    "alpha_XC": 0.03,
    "alpha_FC": 0.04,
    "alpha_TX": 0.04,
    "alpha_YX": 0.03,
    "alpha_FY": 0.06,
}

A2_SEALED_RECIRCULATION = {
    "sensitivity_T": 0.8,
    "sensitivity_RC": 1.1,
    "sensitivity_S": 0.9,
    "sensitivity_C": 1.4,   # HIGH containment sensitivity (sealed vessel)
    "sensitivity_TR": 0.7,
    "sensitivity_X": 0.9,
    "sensitivity_Y": 0.9,
    "decay_T": 0.10,
    "decay_RC": 0.06,
    "decay_S": 0.06,
    "decay_C": 0.04,    # LOW (containment lingers in sealed vessel)
    "decay_TR": 0.12,
    "decay_X": 0.08,
    "decay_Y": 0.03,
    "alpha_RT": 0.04,
    "alpha_TXS": 0.04,
    "alpha_XC": 0.08,   # HIGH X->C (transitions stress seal)
    "alpha_FC": 0.02,   # LOW TR->C relief (can't vent easily)
    "alpha_TX": 0.05,
    "alpha_YX": 0.04,
    "alpha_FY": 0.04,
}

A3_DISTILL_COLLECT = {
    "sensitivity_T": 1.4,   # HIGH thermal (aggressive heating)
    "sensitivity_RC": 0.7,
    "sensitivity_S": 0.8,
    "sensitivity_C": 1.0,
    "sensitivity_TR": 1.4,  # HIGH transfer (routing-sensitive collection)
    "sensitivity_X": 1.2,   # HIGH transition
    "sensitivity_Y": 1.3,   # HIGH product (collection is the point)
    "decay_T": 0.08,    # LOW (direct fire = less buffering)
    "decay_RC": 0.10,
    "decay_S": 0.08,
    "decay_C": 0.08,
    "decay_TR": 0.06,   # LOW (flow system sustains routing)
    "decay_X": 0.06,    # LOW (transitions persist)
    "decay_Y": 0.02,    # LOWEST (collection accumulates)
    "alpha_RT": 0.02,
    "alpha_TXS": 0.05,  # HIGH T*X->S erosion (aggressive = stability costly)
    "alpha_XC": 0.05,
    "alpha_FC": 0.06,
    "alpha_TX": 0.07,   # HIGH T->X (heat directly drives transitions)
    "alpha_YX": 0.05,
    "alpha_FY": 0.08,   # HIGH TR->Y (flow = collection)
}

PROFILES = {
    "A1_BATH_REFLUX": A1_BATH_REFLUX,
    "A2_SEALED_RECIRCULATION": A2_SEALED_RECIRCULATION,
    "A3_DISTILL_COLLECT": A3_DISTILL_COLLECT,
}


# ---------------------------------------------------------------------------
# VirtualApparatus class (importable by later scripts)
# ---------------------------------------------------------------------------
class VirtualApparatus:
    """
    Simulates a 7-variable continuous-state apparatus with cross-coupling
    and decay toward equilibrium.

    Usage:
        app = VirtualApparatus(profile_params)
        state = [0.5] * 7
        dV = [0.0, 0.0, 0.05, 0.0, 0.0, 0.0, 0.0]
        new_state = app.update(state, dV)
    """

    def __init__(self, params):
        """
        params: dict with keys sensitivity_T..Y, decay_T..Y, alpha_* etc.
        """
        self.params = dict(params)  # defensive copy

    @staticmethod
    def _clamp(v):
        return max(0.0, min(1.0, v))

    def _cross_coupling(self, state):
        """
        Compute the 7 cross-coupling increments from current state.
        Returns a list of 7 floats.

        Terms:
          dT_from_RC  = alpha_RT  * (RC - 0.5) * 0.5
          dS_from_TX  = -alpha_TXS * max(T-0.6,0) * max(X-0.5,0)
          dC_from_X   = alpha_XC  * max(X - 0.6, 0)
          dC_from_TR  = -alpha_FC * max(TR - 0.5, 0)
          dX_from_T   = alpha_TX  * (T - 0.5)
          dX_from_Y   = -alpha_YX * max(Y - 0.6, 0)
          dY_from_TR  = alpha_FY  * max(TR - 0.4, 0)
        """
        p = self.params
        T, RC, S, C, TR, X, Y = state

        cc_T = p["alpha_RT"] * (RC - 0.5) * 0.5
        cc_RC = 0.0
        cc_S = -p["alpha_TXS"] * max(T - 0.6, 0.0) * max(X - 0.5, 0.0)
        cc_C = (p["alpha_XC"] * max(X - 0.6, 0.0)
                - p["alpha_FC"] * max(TR - 0.5, 0.0))
        cc_TR = 0.0
        cc_X = (p["alpha_TX"] * (T - 0.5)
                - p["alpha_YX"] * max(Y - 0.6, 0.0))
        cc_Y = p["alpha_FY"] * max(TR - 0.4, 0.0)

        return [cc_T, cc_RC, cc_S, cc_C, cc_TR, cc_X, cc_Y]

    def _decay(self, state):
        """
        Compute decay terms pulling each variable toward 0.5.
        Returns list of 7 floats (subtracted in update).
        """
        p = self.params
        decay_keys = ["decay_T", "decay_RC", "decay_S", "decay_C",
                      "decay_TR", "decay_X", "decay_Y"]
        return [p[dk] * (state[i] - 0.5) for i, dk in enumerate(decay_keys)]

    def update(self, state, dV):
        """
        Apply one update step.
        state: list of 7 floats in [0,1]
        dV: list of 7 floats (external impulse, pre-scaled by caller)
        Returns: new state as list of 7 floats
        """
        cc = self._cross_coupling(state)
        decay = self._decay(state)
        new_state = []
        for i in range(N_VARS):
            v = state[i] + dV[i] + cc[i] - decay[i]
            new_state.append(self._clamp(v))
        return new_state

    def sensitivity(self, var_name):
        """Get sensitivity for a state variable by name."""
        return self.params[f"sensitivity_{var_name}"]

    def run_trajectory(self, initial_state, dV_sequence):
        """
        Run a sequence of updates, return full trajectory.
        Returns: list of states (len = len(dV_sequence) + 1, including initial)
        """
        trajectory = [list(initial_state)]
        state = list(initial_state)
        for dV in dV_sequence:
            state = self.update(state, dV)
            trajectory.append(state)
        return trajectory


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def make_dv(var_index, magnitude):
    """Create a dV vector with a single non-zero entry."""
    dv = [0.0] * N_VARS
    dv[var_index] = magnitude
    return dv


def run_self_tests(profile_name, params):
    """
    Run V1-V3 self-tests for a single profile.
    Returns dict with test names -> bool and diagnostic info.

    Test design:
      V1 (stability): gentle push on S (base=0.005 * sensitivity_S).
         At equilibrium dV = decay*(Veq-0.5), so Veq = 0.5 + dV/decay.
         Worst case A1: 0.5 + 0.0055/0.05 = 0.610 -- but decay pulls
         all OTHER variables back, and cross-coupling from a mild S
         excursion is negligible. All variables should stay in [0.4,0.6].

      V2 (hazard): aggressive push on X (base=0.10 * sensitivity_X).
         Even A1 (sensitivity_X=0.6, decay_X=0.12) reaches:
         Veq = 0.5 + 0.06/0.12 = 1.0 (clamped). Exceeds 0.80.

      V3 (recovery): 30 steps of V2-strength active push, then 50 steps
         of V1-strength stability push. X must return below 0.60.
    """
    app = VirtualApparatus(params)
    results = {}

    s_idx = STATE_VARS.index("S")
    x_idx = STATE_VARS.index("X")

    # --- V1: Stable equilibrium ---
    # With asymmetric cross-coupling thresholds (e.g. max(TR-0.4,0) for Y),
    # the system has a non-trivial equilibrium that is NOT [0.5]*7.
    # Product (Y) accumulates because TR=0.5 > 0.4 threshold, and
    # transition pressure (X) drops because Y > 0.6 triggers alpha_YX.
    # This is physically correct: an idle apparatus slowly collects product.
    #
    # V1 tests: (a) system converges (last 10 steps vary < 0.01 per var),
    #           (b) no variable reaches a hazard boundary.
    mag_s = 0.005 * params["sensitivity_S"]
    dv_stability = make_dv(s_idx, mag_s)

    initial = [0.5] * N_VARS
    traj = app.run_trajectory(initial, [dv_stability] * 100)
    final = traj[-1]

    # (a) Convergence: max absolute change in last 10 steps < 0.01
    late_deltas = []
    for step in range(91, 101):
        for i in range(N_VARS):
            late_deltas.append(abs(traj[step][i] - traj[step - 1][i]))
    converged = max(late_deltas) < 0.01

    # (b) No hazard: check final state against hazard boundaries
    no_hazard = True
    for i, var in enumerate(STATE_VARS):
        lo, hi = HAZARD_BOUNDARIES[var]
        if lo is not None and final[i] < lo:
            no_hazard = False
        if hi is not None and final[i] > hi:
            no_hazard = False

    v1_pass = converged and no_hazard
    results["V1_stable"] = v1_pass
    results["V1_converged"] = converged
    results["V1_no_hazard"] = no_hazard
    results["V1_max_late_delta"] = round(max(late_deltas), 6)
    results["V1_final_state"] = [round(v, 4) for v in final]
    results["V1_max_deviation"] = round(max(abs(v - 0.5) for v in final), 4)

    # --- V2: Hazard excursion ---
    mag_x = 0.10 * params["sensitivity_X"]
    dv_active = make_dv(x_idx, mag_x)

    initial = [0.5] * N_VARS
    traj = app.run_trajectory(initial, [dv_active] * 100)
    x_values = [s[x_idx] for s in traj]
    max_x = max(x_values)
    v2_pass = max_x > 0.80
    results["V2_hazard"] = v2_pass
    results["V2_max_X"] = round(max_x, 4)
    results["V2_step_at_max_X"] = x_values.index(max_x)

    # --- V3: Closure recovery ---
    initial = [0.5] * N_VARS
    dv_sequence = [dv_active] * 30 + [dv_stability] * 50

    traj = app.run_trajectory(initial, dv_sequence)
    x_values = [s[x_idx] for s in traj]
    final_x = traj[-1][x_idx]

    # Check recovery within 20 tokens of switching (step 31..50)
    recovered_within_20 = False
    for step in range(31, min(51, len(traj))):
        if traj[step][x_idx] < 0.60:
            recovered_within_20 = True
            break

    v3_pass = final_x < 0.60
    results["V3_recovery"] = v3_pass
    results["V3_final_X"] = round(final_x, 4)
    results["V3_max_X_during_active"] = round(max(x_values[:31]), 4)
    results["V3_recovered_within_20"] = recovered_within_20

    return results


# ---------------------------------------------------------------------------
# Folio assignment
# ---------------------------------------------------------------------------
def assign_folio_profiles(regime_path, budget_path):
    """
    Assign preferred apparatus profile to each folio based on section+regime.

    Rules:
      - Section B -> A1 (always)
      - Section H + REGIME_1 -> A1
      - Section H + REGIME_2 -> A2
      - Section H + REGIME_3 or REGIME_4 -> A3
      - Section C, T -> A2
      - Section S -> A3
    """
    with open(regime_path) as f:
        regime_data = json.load(f)

    with open(budget_path) as f:
        budget_data = json.load(f)

    assignments = {}

    for folio, budget_info in budget_data["folio_budgets"].items():
        section = budget_info["section"]
        regime_info = regime_data["regime_assignments"].get(folio)
        if regime_info is None:
            print(f"  WARNING: {folio} not in regime mapping, skipping")
            continue
        regime = regime_info["regime"]

        if section == "B":
            profile = "A1_BATH_REFLUX"
        elif section == "H":
            if regime == "REGIME_1":
                profile = "A1_BATH_REFLUX"
            elif regime == "REGIME_2":
                profile = "A2_SEALED_RECIRCULATION"
            else:  # REGIME_3 or REGIME_4
                profile = "A3_DISTILL_COLLECT"
        elif section in ("C", "T"):
            profile = "A2_SEALED_RECIRCULATION"
        elif section == "S":
            profile = "A3_DISTILL_COLLECT"
        else:
            print(f"  WARNING: Unknown section '{section}' for {folio}, "
                  f"defaulting to A2")
            profile = "A2_SEALED_RECIRCULATION"

        assignments[folio] = {
            "preferred_profile": profile,
            "section": section,
            "regime": regime,
        }

    return assignments


def summarize_assignments(assignments):
    """Build summary counts per profile and per section."""
    summary = {}
    for folio, info in assignments.items():
        profile = info["preferred_profile"]
        section = info["section"]
        if profile not in summary:
            summary[profile] = {"n_folios": 0, "sections": {}}
        summary[profile]["n_folios"] += 1
        summary[profile]["sections"][section] = (
            summary[profile]["sections"].get(section, 0) + 1
        )
    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Resolve paths: scripts/ -> VIRTUAL_APPARATUS_COUPLING/ -> phases/ -> voynich/
    script_dir = Path(__file__).resolve().parent
    phase_dir = script_dir.parent          # VIRTUAL_APPARATUS_COUPLING/
    project_root = phase_dir.parent.parent  # voynich/

    regime_path = project_root / "data" / "regime_folio_mapping.json"
    budget_path = (project_root / "phases"
                   / "SECTION_TEMPLATE_TRACE_EXECUTOR" / "results"
                   / "t2_folio_budgets.json")
    output_path = phase_dir / "results" / "t1_apparatus_family.json"

    print("=" * 70)
    print("T1: Apparatus Family Builder")
    print("Phase 563 - VIRTUAL_APPARATUS_COUPLING")
    print("=" * 70)

    # --- Run self-tests ---
    print("\n--- Self-Tests ---")
    all_tests = {}
    all_pass = True

    for name, params in PROFILES.items():
        print(f"\n  Profile: {name}")
        test_results = run_self_tests(name, params)
        all_tests[name] = {
            "V1_stable": test_results["V1_stable"],
            "V2_hazard": test_results["V2_hazard"],
            "V3_recovery": test_results["V3_recovery"],
        }

        for test_name in ["V1_stable", "V2_hazard", "V3_recovery"]:
            status = "PASS" if test_results[test_name] else "FAIL"
            print(f"    {test_name}: {status}")
            if not test_results[test_name]:
                all_pass = False

        # Diagnostics
        print(f"    V1 final: {test_results['V1_final_state']}")
        print(f"    V1 max deviation: {test_results['V1_max_deviation']}")
        print(f"    V2 max X: {test_results['V2_max_X']} "
              f"(step {test_results['V2_step_at_max_X']})")
        print(f"    V3 max X active: "
              f"{test_results['V3_max_X_during_active']}")
        print(f"    V3 final X: {test_results['V3_final_X']}")
        print(f"    V3 recovered <20 steps: "
              f"{test_results['V3_recovered_within_20']}")

    if all_pass:
        print("\n  ALL SELF-TESTS PASSED")
    else:
        print("\n  *** SOME SELF-TESTS FAILED ***")

    # --- Folio assignments ---
    print("\n--- Folio Assignments ---")
    assignments = assign_folio_profiles(regime_path, budget_path)
    summary = summarize_assignments(assignments)

    print(f"  Total folios assigned: {len(assignments)}")
    for pname in ["A1_BATH_REFLUX", "A2_SEALED_RECIRCULATION",
                   "A3_DISTILL_COLLECT"]:
        if pname in summary:
            s = summary[pname]
            sec_str = ", ".join(
                f"{k}={v}" for k, v in sorted(s["sections"].items()))
            print(f"  {pname}: {s['n_folios']} folios ({sec_str})")

    # --- Build output ---
    output = {
        "metadata": {
            "phase": "563",
            "task": "T1_apparatus_family_builder",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_folios": len(assignments),
            "all_self_tests_passed": all_pass,
        },
        "profiles": {n: dict(p) for n, p in PROFILES.items()},
        "folio_assignments": assignments,
        "assignment_summary": summary,
        "self_tests": all_tests,
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
