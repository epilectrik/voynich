"""
T3: Trace-Coupled Executor
===========================
Phase 563 — VIRTUAL_APPARATUS_COUPLING

Runs 8 pilot folios token-by-token against ALL 3 apparatus profiles (24 runs).
Tests whether supervisory traces drive the apparatus to section-appropriate
states from a neutral start.

For each (folio, profile) pair:
  1. Initialize state = [0.5]*7
  2. For each token (sorted by line, line_pos):
     a. Look up T2 supervisory contribution (7D vector)
     b. Scale by profile sensitivity: dV[i] = contribution[i] * sensitivity(STATE_VARS[i])
     c. Call apparatus.update(state, dV)
     d. Record state, check hazard boundaries
  3. Compute viability fraction, summary extrema, per-line means

Storage optimization:
  - Full per-token trajectory stored only for preferred-profile runs (8 runs)
  - Summary metrics stored for all 24 runs

Inputs:
  - t1_apparatus_family.json (profiles + folio assignments)
  - t2_supervisory_interface.json (per-token contributions)

Output:
  - t3_coupled_traces.json
"""

import json
import time
from pathlib import Path
from collections import defaultdict
import sys

# ---------------------------------------------------------------------------
# Import apparatus from T1
# ---------------------------------------------------------------------------
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
from t1_apparatus_family_builder import (
    VirtualApparatus, PROFILES, STATE_VARS, HAZARD_BOUNDARIES, N_VARS
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
phase_dir = script_dir.parent
results_dir = phase_dir / "results"
T1_PATH = results_dir / "t1_apparatus_family.json"
T2_PATH = results_dir / "t2_supervisory_interface.json"
OUTPUT_PATH = results_dir / "t3_coupled_traces.json"

# ---------------------------------------------------------------------------
# Pilot folios with expected preferred profiles
# ---------------------------------------------------------------------------
PILOT_FOLIOS = {
    "f78r":  "A1_BATH_REFLUX",
    "f84r":  "A1_BATH_REFLUX",
    "f55r":  "A2_SEALED_RECIRCULATION",
    "f40v":  "A2_SEALED_RECIRCULATION",
    "f43v":  "A3_DISTILL_COLLECT",
    "f104r": "A3_DISTILL_COLLECT",
    "f111r": "A3_DISTILL_COLLECT",
    "f116v": "A2_SEALED_RECIRCULATION",
}

PROFILE_NAMES = ["A1_BATH_REFLUX", "A2_SEALED_RECIRCULATION", "A3_DISTILL_COLLECT"]


# ---------------------------------------------------------------------------
# Hazard boundary checking
# ---------------------------------------------------------------------------
def check_hazard(state):
    """
    Check state against hazard boundaries.
    Returns list of violation dicts, empty if viable.
    """
    violations = []
    for i, var in enumerate(STATE_VARS):
        lo, hi = HAZARD_BOUNDARIES[var]
        if lo is not None and state[i] < lo:
            violations.append({
                "state_var": var,
                "violation_type": f"{var}_LOW",
                "boundary_value": lo,
                "actual_value": round(state[i], 6),
            })
        if hi is not None and state[i] > hi:
            violations.append({
                "state_var": var,
                "violation_type": f"{var}_HIGH",
                "boundary_value": hi,
                "actual_value": round(state[i], 6),
            })
    return violations


def sort_key_for_token(tok):
    """Sort tokens by (line as integer, line_pos as float)."""
    try:
        line_num = int(tok["line"])
    except (ValueError, TypeError):
        line_num = 0
    line_pos = tok.get("line_pos", 0.0)
    if not isinstance(line_pos, (int, float)):
        line_pos = 0.0
    return (line_num, line_pos)


# ---------------------------------------------------------------------------
# Run a single (folio, profile) pair
# ---------------------------------------------------------------------------
def run_folio_profile(folio_tokens, profile_name, profile_params, store_trajectory):
    """
    Execute one folio against one apparatus profile.

    Args:
        folio_tokens: list of T2 token records, pre-sorted by (line, line_pos)
        profile_name: string
        profile_params: dict of profile parameters
        store_trajectory: bool — whether to store per-token trajectory

    Returns: dict with run results
    """
    app = VirtualApparatus(profile_params)
    n_tokens = len(folio_tokens)

    state = [0.5] * N_VARS
    trajectory = [] if store_trajectory else None
    hazard_events = []
    n_viable = 0

    # Track extrema
    max_vals = [0.5] * N_VARS  # track max per variable
    min_vals = [0.5] * N_VARS  # track min per variable

    # Per-line accumulation
    line_state_sums = defaultdict(lambda: {"sum": [0.0] * N_VARS, "count": 0})

    for tok_idx, tok in enumerate(folio_tokens):
        contributions = tok["contributions"]

        # Scale contributions by profile sensitivity
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            sensitivity = app.sensitivity(sv)
            dV[i] = contributions[i] * sensitivity

        # Update apparatus state
        state = app.update(state, dV)

        # Check hazard boundaries
        violations = check_hazard(state)
        if violations:
            for v in violations:
                hazard_events.append({
                    "token_idx": tok_idx,
                    "word": tok.get("word", ""),
                    "violation_type": v["violation_type"],
                    "state_var": v["state_var"],
                    "boundary_value": v["boundary_value"],
                    "state_at_violation": [round(s, 5) for s in state],
                })
        else:
            n_viable += 1

        # Track extrema
        for i in range(N_VARS):
            if state[i] > max_vals[i]:
                max_vals[i] = state[i]
            if state[i] < min_vals[i]:
                min_vals[i] = state[i]

        # Per-line accumulation
        line_key = tok.get("line", "?")
        ls = line_state_sums[line_key]
        for i in range(N_VARS):
            ls["sum"][i] += state[i]
        ls["count"] += 1

        # Store trajectory if requested
        if store_trajectory:
            trajectory.append({
                "token_idx": tok_idx,
                "word": tok.get("word", ""),
                "domain": tok.get("domain", ""),
                "packet_phase": tok.get("packet_phase", ""),
                "state": [round(s, 5) for s in state],
                "dV": [round(d, 6) for d in dV],
            })

    # Compute viability fraction
    viability_fraction = n_viable / n_tokens if n_tokens > 0 else 0.0

    # Summary extrema
    summary_extrema = {}
    for i, sv in enumerate(STATE_VARS):
        summary_extrema[f"max_{sv}"] = round(max_vals[i], 5)
        summary_extrema[f"min_{sv}"] = round(min_vals[i], 5)
    summary_extrema["Y_final"] = round(state[STATE_VARS.index("Y")], 5) if n_tokens > 0 else 0.5

    # Per-line mean state
    per_line_mean = {}
    for lk in sorted(line_state_sums.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        ls = line_state_sums[lk]
        c = ls["count"]
        if c > 0:
            per_line_mean[lk] = [round(ls["sum"][i] / c, 5) for i in range(N_VARS)]

    # Build result
    result = {
        "folio": folio_tokens[0]["folio"] if folio_tokens else "?",
        "profile_name": profile_name,
        "n_tokens": n_tokens,
        "viability_fraction": round(viability_fraction, 5),
        "n_hazard_events": len(hazard_events),
        "hazard_events": hazard_events,
        "summary_extrema": summary_extrema,
        "per_line_mean_state": per_line_mean,
        "final_state": [round(s, 5) for s in state] if n_tokens > 0 else [0.5] * N_VARS,
    }

    if store_trajectory:
        result["trajectory"] = trajectory

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    print("=" * 70)
    print("T3: Trace-Coupled Executor")
    print("Phase 563 — VIRTUAL_APPARATUS_COUPLING")
    print("=" * 70)

    # ── Load inputs ───────────────────────────────────────────────────
    print("\nLoading inputs...")

    with open(T1_PATH) as f:
        t1_data = json.load(f)
    folio_assignments = t1_data["folio_assignments"]
    print(f"  T1 folio assignments: {len(folio_assignments)}")

    with open(T2_PATH) as f:
        t2_data = json.load(f)
    all_tokens = t2_data["token_signals"]
    print(f"  T2 tokens: {len(all_tokens)}")

    # ── Index tokens by folio ─────────────────────────────────────────
    print("\nIndexing tokens by folio...")
    folio_tokens = defaultdict(list)
    for tok in all_tokens:
        folio_tokens[tok["folio"]].append(tok)

    # Sort each folio's tokens by (line, line_pos)
    for fid in folio_tokens:
        folio_tokens[fid].sort(key=sort_key_for_token)

    # ── Determine preferred profiles for pilot folios ─────────────────
    # Use T1 assignments where available; fall back to PILOT_FOLIOS table
    preferred = {}
    for fid, expected_pref in PILOT_FOLIOS.items():
        t1_info = folio_assignments.get(fid)
        if t1_info:
            preferred[fid] = t1_info["preferred_profile"]
        else:
            preferred[fid] = expected_pref
            print(f"  WARNING: {fid} not in T1 assignments, using task table: {expected_pref}")

    # ── Run all 24 traces ─────────────────────────────────────────────
    print(f"\nRunning {len(PILOT_FOLIOS)} folios x {len(PROFILE_NAMES)} profiles = "
          f"{len(PILOT_FOLIOS) * len(PROFILE_NAMES)} runs...")

    runs = {}
    cross_profile_summary = {}
    n_skipped = 0

    for fid in sorted(PILOT_FOLIOS.keys()):
        tokens = folio_tokens.get(fid, [])
        if not tokens:
            print(f"  {fid}: SKIPPED (0 tokens in T2)")
            n_skipped += 1
            continue

        pref = preferred[fid]
        folio_viability = {}
        folio_hazard_count = {}
        folio_y_final = {}

        for prof_name in PROFILE_NAMES:
            is_pref = (prof_name == pref)
            store_traj = is_pref  # Only store full trajectory for preferred

            run_key = f"{fid}|{prof_name}"
            result = run_folio_profile(tokens, prof_name, PROFILES[prof_name], store_traj)
            result["is_preferred"] = is_pref

            runs[run_key] = result

            # Collect cross-profile metrics
            folio_viability[prof_name] = result["viability_fraction"]
            folio_hazard_count[prof_name] = result["n_hazard_events"]
            folio_y_final[prof_name] = result["summary_extrema"]["Y_final"]

            status = "PREF" if is_pref else "    "
            print(f"  {status} {run_key:<45} viability={result['viability_fraction']:.3f}  "
                  f"hazards={result['n_hazard_events']:>4}  Y_final={result['summary_extrema']['Y_final']:.3f}")

        # Build cross-profile summary for this folio
        cross_profile_summary[fid] = {
            "preferred_profile": pref,
            "section": folio_assignments.get(fid, {}).get("section", "?"),
            "regime": folio_assignments.get(fid, {}).get("regime", "?"),
            "n_tokens": len(tokens),
            "viability": folio_viability,
            "hazard_count": folio_hazard_count,
            "Y_final": folio_y_final,
        }

    # ── Compute aggregate statistics ──────────────────────────────────
    print(f"\n{'=' * 70}")
    print("CROSS-PROFILE SUMMARY")
    print(f"{'=' * 70}")

    # Count how often preferred profile wins (best viability)
    pref_wins = 0
    pref_ties = 0
    pref_losses = 0
    total_compared = 0

    for fid, cps in cross_profile_summary.items():
        pref_name = cps["preferred_profile"]
        pref_viab = cps["viability"].get(pref_name, 0)
        other_viabs = [v for k, v in cps["viability"].items() if k != pref_name]
        if not other_viabs:
            continue
        total_compared += 1
        best_other = max(other_viabs)
        if pref_viab > best_other:
            pref_wins += 1
        elif pref_viab == best_other:
            pref_ties += 1
        else:
            pref_losses += 1

    print(f"\n  Preferred profile viability comparison:")
    print(f"    Wins:   {pref_wins}/{total_compared}")
    print(f"    Ties:   {pref_ties}/{total_compared}")
    print(f"    Losses: {pref_losses}/{total_compared}")

    # Per-folio summary table
    print(f"\n  {'Folio':<8} {'Sec':>3} {'Rgm':>6} {'Pref':>28}  "
          f"{'A1 viab':>8} {'A2 viab':>8} {'A3 viab':>8}  "
          f"{'A1 haz':>7} {'A2 haz':>7} {'A3 haz':>7}")
    print(f"  {'-'*8} {'-'*3} {'-'*6} {'-'*28}  "
          f"{'-'*8} {'-'*8} {'-'*8}  "
          f"{'-'*7} {'-'*7} {'-'*7}")

    for fid in sorted(cross_profile_summary.keys()):
        cps = cross_profile_summary[fid]
        sec = cps["section"]
        rgm = cps["regime"]
        pref_name = cps["preferred_profile"]
        v1 = cps["viability"].get("A1_BATH_REFLUX", 0)
        v2 = cps["viability"].get("A2_SEALED_RECIRCULATION", 0)
        v3 = cps["viability"].get("A3_DISTILL_COLLECT", 0)
        h1 = cps["hazard_count"].get("A1_BATH_REFLUX", 0)
        h2 = cps["hazard_count"].get("A2_SEALED_RECIRCULATION", 0)
        h3 = cps["hazard_count"].get("A3_DISTILL_COLLECT", 0)
        print(f"  {fid:<8} {sec:>3} {rgm:>6} {pref_name:>28}  "
              f"{v1:>8.3f} {v2:>8.3f} {v3:>8.3f}  "
              f"{h1:>7} {h2:>7} {h3:>7}")

    # Mean viability per profile (across folios that ran)
    print(f"\n  Mean viability per profile (across pilot folios):")
    for pname in PROFILE_NAMES:
        viabs = [cps["viability"].get(pname, 0) for cps in cross_profile_summary.values()]
        if viabs:
            mean_v = sum(viabs) / len(viabs)
            print(f"    {pname:<30} mean viability = {mean_v:.4f}")

    # ── Build output ──────────────────────────────────────────────────
    elapsed = time.time() - t_start
    print(f"\nElapsed: {elapsed:.1f}s")

    output = {
        "metadata": {
            "phase": "563",
            "task": "T3_trace_coupled_executor",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_pilot_folios": len(PILOT_FOLIOS),
            "n_folios_run": len(PILOT_FOLIOS) - n_skipped,
            "n_folios_skipped": n_skipped,
            "n_profiles": len(PROFILE_NAMES),
            "n_runs": len(runs),
            "elapsed_seconds": round(elapsed, 1),
            "preferred_wins": pref_wins,
            "preferred_ties": pref_ties,
            "preferred_losses": pref_losses,
            "state_variables": STATE_VARS,
            "hazard_boundaries": HAZARD_BOUNDARIES,
            "trajectory_storage": "preferred_only",
        },
        "runs": runs,
        "cross_profile_summary": cross_profile_summary,
    }

    # ── Write output ──────────────────────────────────────────────────
    print(f"\nWriting output to {OUTPUT_PATH}...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=1)

    file_size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"  Output size: {file_size_mb:.1f} MB")
    print(f"\nDone.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
