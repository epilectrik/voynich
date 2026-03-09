"""
T4: Null and Ablation Executor
===============================
Phase 563 — VIRTUAL_APPARATUS_COUPLING

Runs 8 pilot folios under degraded supervisory interfaces (5 baselines + 4 nulls)
to test which layers of the supervisory architecture carry real plant-level signal.

Baselines (deterministic, 1 run each):
  B1: Section-mean contributions only (removes folio and line detail)
  B2: Folio-mean contributions only (removes line detail)
  B3: Full minus CTS (disable closure modulation on C, S, Y)
  B4: Full minus routing (undo terminal routing grammar effects)
  B5: Full minus headless regime (headless tokens get section mean)

Nulls (stochastic, 50 permutations each):
  N1: Token shuffle within folio (break line/paragraph structure)
  N2: Domain-preserved shuffle within folio (keep domain sequence, randomize rest)
  N3: Line shuffle within section (same line packets, wrong folio)
  N4: Within-line token shuffle (destroy within-line order)

Input:
  - t1_apparatus_family.json  (profiles + assignments)
  - t2_supervisory_interface.json  (per-token contributions)

Output:
  - t4_null_ablation_traces.json
"""

import json
import math
import time
import random
from pathlib import Path
from collections import defaultdict
import copy
import sys

# ── Import VirtualApparatus from T1 ──────────────────────────────────────────

sys.path.insert(0, str(Path(__file__).resolve().parent))
from t1_apparatus_family_builder import VirtualApparatus, PROFILES, STATE_VARS, HAZARD_BOUNDARIES

N_VARS = len(STATE_VARS)
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}

# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
RESULTS_DIR = PHASE_DIR / "results"

T1_PATH = RESULTS_DIR / "t1_apparatus_family.json"
T2_PATH = RESULTS_DIR / "t2_supervisory_interface.json"
OUTPUT_PATH = RESULTS_DIR / "t4_null_ablation_traces.json"

# ── Constants ─────────────────────────────────────────────────────────────────

PILOT_FOLIOS = ["f78r", "f84r", "f55r", "f40v", "f43v", "f104r", "f111r", "f116v"]

# Preferred profile assignments from task spec
PILOT_PROFILES = {
    "f78r":  "A1_BATH_REFLUX",
    "f84r":  "A1_BATH_REFLUX",
    "f55r":  "A2_SEALED_RECIRCULATION",
    "f40v":  "A2_SEALED_RECIRCULATION",
    "f43v":  "A3_DISTILL_COLLECT",
    "f104r": "A3_DISTILL_COLLECT",
    "f111r": "A3_DISTILL_COLLECT",
    "f116v": "A2_SEALED_RECIRCULATION",
}

N_PERMS = 50

# Routing effects (from T2, needed for B4 undo)
ROUTING_EFFECTS = {
    'r': {'boost': {'X': 1.4}, 'suppress': {'S': 0.6, 'C': 0.7, 'Y': 0.7}},
    'y': {'boost': {'T': 1.4}, 'suppress': {'X': 0.7, 'C': 0.7}},
    'h': {'boost': {'TR': 1.4, 'RC': 1.3}, 'suppress': {'X': 0.7, 'T': 0.7}},
    'm': {'boost': {'C': 1.4}, 'suppress': {'T': 0.7, 'X': 0.7, 'TR': 0.7}},
    'n': {'boost': {'S': 1.2}, 'suppress': {'X': 0.8, 'T': 0.8}},
    'l': {'boost': {'TR': 1.2, 'S': 1.2}, 'suppress': {'X': 0.8}},
}


# ── Execution Engine ──────────────────────────────────────────────────────────

def run_folio_execution(apparatus, contributions_sequence):
    """
    Run a folio through the VirtualApparatus with a sequence of contribution vectors.
    Each contribution is already a 7D vector; we scale by profile sensitivity here.

    Returns summary metrics dict.
    """
    state = [0.5] * N_VARS
    n_tokens = len(contributions_sequence)
    if n_tokens == 0:
        return {
            "viability_fraction": 1.0,
            "hazard_count": 0,
            "Y_final": 0.5,
            "max_T": 0.5, "min_S": 0.5, "max_C": 0.5, "max_X": 0.5,
            "mean_state": [0.5] * N_VARS,
        }

    viable_count = 0
    hazard_event_count = 0
    state_sum = [0.0] * N_VARS
    max_T = 0.0
    min_S = 1.0
    max_C = 0.0
    max_X = 0.0

    for contrib in contributions_sequence:
        # Scale by profile sensitivity
        dV = [0.0] * N_VARS
        for i in range(N_VARS):
            dV[i] = contrib[i] * apparatus.sensitivity(STATE_VARS[i])

        state = apparatus.update(state, dV)

        # Track extrema
        T_val, RC_val, S_val, C_val, TR_val, X_val, Y_val = state
        if T_val > max_T:
            max_T = T_val
        if S_val < min_S:
            min_S = S_val
        if C_val > max_C:
            max_C = C_val
        if X_val > max_X:
            max_X = X_val

        # Check viability (within hazard boundaries)
        in_bounds = True
        for i, var in enumerate(STATE_VARS):
            lo, hi = HAZARD_BOUNDARIES[var]
            if lo is not None and state[i] < lo:
                in_bounds = False
            if hi is not None and state[i] > hi:
                in_bounds = False

        if in_bounds:
            viable_count += 1
        else:
            hazard_event_count += 1

        for i in range(N_VARS):
            state_sum[i] += state[i]

    mean_state = [state_sum[i] / n_tokens for i in range(N_VARS)]

    return {
        "viability_fraction": round(viable_count / n_tokens, 6),
        "hazard_count": hazard_event_count,
        "Y_final": round(state[SV_INDEX['Y']], 6),
        "max_T": round(max_T, 6),
        "min_S": round(min_S, 6),
        "max_C": round(max_C, 6),
        "max_X": round(max_X, 6),
        "mean_state": [round(v, 6) for v in mean_state],
    }


# ── Contribution Manipulation Functions ───────────────────────────────────────

def undo_cts(contrib, cts):
    """
    Undo CTS modulation on C (idx 3), S (idx 2), Y (idx 6).
    CTS modulation was: C *= (1.0 + 0.3 * cts), S *= (1.0 + 0.2 * cts), Y *= (1.0 + 0.4 * cts)
    To undo: divide by those factors.
    """
    result = list(contrib)
    c_factor = 1.0 + 0.3 * cts
    s_factor = 1.0 + 0.2 * cts
    y_factor = 1.0 + 0.4 * cts

    if abs(s_factor) > 1e-10:
        result[2] /= s_factor  # S
    if abs(c_factor) > 1e-10:
        result[3] /= c_factor  # C
    if abs(y_factor) > 1e-10:
        result[6] /= y_factor  # Y
    return result


def undo_routing(contrib, routing_terminal):
    """
    Undo routing effects for a token where routing was active.
    The routing multiplied certain contribution elements by boost/suppress factors.
    To undo: divide by those factors.
    """
    if routing_terminal is None or routing_terminal not in ROUTING_EFFECTS:
        return list(contrib)

    result = list(contrib)
    effects = ROUTING_EFFECTS[routing_terminal]

    for sv, mult in effects.get('boost', {}).items():
        idx = SV_INDEX.get(sv)
        if idx is not None and abs(mult) > 1e-10:
            result[idx] /= mult

    for sv, mult in effects.get('suppress', {}).items():
        idx = SV_INDEX.get(sv)
        if idx is not None and abs(mult) > 1e-10:
            result[idx] /= mult

    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    t_start = time.time()
    print("=" * 70)
    print("T4: Null and Ablation Executor")
    print("Phase 563 - VIRTUAL_APPARATUS_COUPLING")
    print("=" * 70)

    # ── Load T1 and T2 ────────────────────────────────────────────────────
    print("\nLoading inputs...")

    with open(T1_PATH, 'r') as f:
        t1_data = json.load(f)
    folio_assignments = t1_data["folio_assignments"]

    with open(T2_PATH, 'r') as f:
        t2_data = json.load(f)
    all_tokens = t2_data["token_signals"]
    print(f"  Total tokens: {len(all_tokens)}")

    # ── Build per-folio and per-section token groups ──────────────────────
    print("  Building token index...")

    folio_tokens = defaultdict(list)
    section_tokens = defaultdict(list)
    folio_section_map = {}

    for tok in all_tokens:
        folio = tok["folio"]
        section = tok["section"]
        folio_tokens[folio].append(tok)
        section_tokens[section].append(tok)
        if folio not in folio_section_map:
            folio_section_map[folio] = section

    # Verify pilot folios exist; handle missing ones gracefully
    empty_pilots = set()
    for pf in PILOT_FOLIOS:
        if pf not in folio_tokens or len(folio_tokens[pf]) == 0:
            print(f"  WARNING: Pilot folio {pf} not found in T2 data (0 tokens) — will use section mean fallback")
            empty_pilots.add(pf)
            # Ensure it has a section mapping for fallback
            if pf not in folio_section_map:
                folio_section_map[pf] = "H"  # default fallback section
        else:
            print(f"  {pf}: {len(folio_tokens[pf])} tokens, section={folio_section_map.get(pf, '?')}")

    # ── Pre-compute section means and folio means ─────────────────────────
    print("\n  Computing section and folio mean contributions...")

    section_mean = {}
    for sec, tokens in section_tokens.items():
        n = len(tokens)
        if n == 0:
            section_mean[sec] = [0.0] * N_VARS
            continue
        sums = [0.0] * N_VARS
        for tok in tokens:
            for i in range(N_VARS):
                sums[i] += tok["contributions"][i]
        section_mean[sec] = [sums[i] / n for i in range(N_VARS)]

    folio_mean = {}
    for folio, tokens in folio_tokens.items():
        n = len(tokens)
        if n == 0:
            folio_mean[folio] = [0.0] * N_VARS
            continue
        sums = [0.0] * N_VARS
        for tok in tokens:
            for i in range(N_VARS):
                sums[i] += tok["contributions"][i]
        folio_mean[folio] = [sums[i] / n for i in range(N_VARS)]

    # Ensure empty pilot folios have a folio_mean entry (use section mean)
    for pf in empty_pilots:
        sec = folio_section_map.get(pf, "H")
        folio_mean[pf] = section_mean.get(sec, [0.0] * N_VARS)

    # ── Build per-folio line groups for N3 and N4 ─────────────────────────
    # Group tokens by (folio, line) to preserve line structure
    folio_line_tokens = defaultdict(lambda: defaultdict(list))
    for tok in all_tokens:
        folio_line_tokens[tok["folio"]][tok["line"]].append(tok)

    # Group lines by section for N3
    section_lines = defaultdict(list)  # section -> list of (folio, line, [tokens])
    for folio, lines in folio_line_tokens.items():
        sec = folio_section_map.get(folio, "?")
        for line_id, line_toks in lines.items():
            section_lines[sec].append((folio, line_id, line_toks))

    # ── Build apparatus instances for pilot folios ────────────────────────
    pilot_apparatus = {}
    for pf in PILOT_FOLIOS:
        profile_name = PILOT_PROFILES[pf]
        pilot_apparatus[pf] = VirtualApparatus(PROFILES[profile_name])

    # ── Run reference (full model) for comparison ─────────────────────────
    print("\n--- Reference Run (Full Model) ---")
    reference_results = {}
    for pf in PILOT_FOLIOS:
        contribs = [tok["contributions"] for tok in folio_tokens[pf]]
        result = run_folio_execution(pilot_apparatus[pf], contribs)
        reference_results[pf] = result
        print(f"  {pf}: viability={result['viability_fraction']:.4f} "
              f"hazards={result['hazard_count']} Y_final={result['Y_final']:.4f}")

    # ==================================================================
    # BASELINES
    # ==================================================================
    print("\n--- Baselines ---")
    baseline_results = {}

    # ── B1: Section-only ──────────────────────────────────────────────
    print("\n  B1: Section-only mean...")
    b1_results = {}
    for pf in PILOT_FOLIOS:
        sec = folio_section_map.get(pf, "H")
        sec_contrib = section_mean[sec]
        n_tokens = len(folio_tokens[pf])
        contribs = [sec_contrib] * n_tokens
        result = run_folio_execution(pilot_apparatus[pf], contribs)
        b1_results[pf] = result
        print(f"    {pf}: viability={result['viability_fraction']:.4f} "
              f"hazards={result['hazard_count']}")
    baseline_results["B1_section_only"] = b1_results

    # ── B2: Folio-mean ────────────────────────────────────────────────
    print("\n  B2: Folio-mean...")
    b2_results = {}
    for pf in PILOT_FOLIOS:
        f_contrib = folio_mean[pf]
        n_tokens = len(folio_tokens[pf])
        contribs = [f_contrib] * n_tokens
        result = run_folio_execution(pilot_apparatus[pf], contribs)
        b2_results[pf] = result
        print(f"    {pf}: viability={result['viability_fraction']:.4f} "
              f"hazards={result['hazard_count']}")
    baseline_results["B2_section_folio_budget"] = b2_results

    # ── B3: Full minus CTS ────────────────────────────────────────────
    print("\n  B3: Full minus CTS...")
    b3_results = {}
    for pf in PILOT_FOLIOS:
        contribs = []
        for tok in folio_tokens[pf]:
            cts = tok.get("cts", 0.3)
            raw = undo_cts(tok["contributions"], cts)
            contribs.append(raw)
        result = run_folio_execution(pilot_apparatus[pf], contribs)
        b3_results[pf] = result
        print(f"    {pf}: viability={result['viability_fraction']:.4f} "
              f"hazards={result['hazard_count']}")
    baseline_results["B3_full_minus_cts"] = b3_results

    # ── B4: Full minus routing ────────────────────────────────────────
    print("\n  B4: Full minus routing...")
    b4_results = {}
    for pf in PILOT_FOLIOS:
        contribs = []
        for tok in folio_tokens[pf]:
            if tok.get("routing_active"):
                raw = undo_routing(tok["contributions"], tok.get("routing_terminal"))
            else:
                raw = list(tok["contributions"])
            contribs.append(raw)
        result = run_folio_execution(pilot_apparatus[pf], contribs)
        b4_results[pf] = result
        print(f"    {pf}: viability={result['viability_fraction']:.4f} "
              f"hazards={result['hazard_count']}")
    baseline_results["B4_full_minus_routing"] = b4_results

    # ── B5: Full minus headless regime ────────────────────────────────
    print("\n  B5: Full minus headless regime...")
    b5_results = {}
    for pf in PILOT_FOLIOS:
        sec = folio_section_map.get(pf, "H")
        sec_contrib = section_mean[sec]
        contribs = []
        for tok in folio_tokens[pf]:
            if tok.get("headless_subtype", "HEADED") != "HEADED":
                contribs.append(sec_contrib)
            else:
                contribs.append(list(tok["contributions"]))
        result = run_folio_execution(pilot_apparatus[pf], contribs)
        b5_results[pf] = result
        print(f"    {pf}: viability={result['viability_fraction']:.4f} "
              f"hazards={result['hazard_count']}")
    baseline_results["B5_full_minus_headless"] = b5_results

    # ==================================================================
    # NULLS
    # ==================================================================
    print("\n--- Null Models ---")
    null_results = {}
    run_counter = 0
    total_null_runs = 4 * len(PILOT_FOLIOS) * N_PERMS

    # ── N1: Token shuffle within folio ────────────────────────────────
    print("\n  N1: Token shuffle within folio...")
    n1_results = {}
    for pf in PILOT_FOLIOS:
        perm_metrics = []
        base_contribs = [tok["contributions"] for tok in folio_tokens[pf]]
        for perm_idx in range(N_PERMS):
            random.seed(42 + perm_idx)
            shuffled = list(base_contribs)
            random.shuffle(shuffled)
            result = run_folio_execution(pilot_apparatus[pf], shuffled)
            perm_metrics.append(result)
            run_counter += 1
            if run_counter % 200 == 0:
                print(f"    Progress: {run_counter}/{total_null_runs} null runs...")

        n1_results[pf] = _aggregate_null_results(perm_metrics)
    null_results["N1_token_shuffle"] = n1_results

    # ── N2: Domain-preserved shuffle within folio ─────────────────────
    print("\n  N2: Domain-preserved shuffle within folio...")
    n2_results = {}
    for pf in PILOT_FOLIOS:
        perm_metrics = []
        tokens = folio_tokens[pf]

        # Group token indices by domain
        domain_groups = defaultdict(list)
        for idx, tok in enumerate(tokens):
            domain_groups[tok["domain"]].append(idx)

        base_contribs = [tok["contributions"] for tok in tokens]

        for perm_idx in range(N_PERMS):
            random.seed(42 + perm_idx)
            # Within each domain group, shuffle the contribution vectors
            shuffled_contribs = list(base_contribs)  # copy
            for domain, indices in domain_groups.items():
                if len(indices) <= 1:
                    continue
                # Collect contributions for this domain
                domain_contribs = [base_contribs[i] for i in indices]
                random.shuffle(domain_contribs)
                # Reassign
                for j, orig_idx in enumerate(indices):
                    shuffled_contribs[orig_idx] = domain_contribs[j]

            result = run_folio_execution(pilot_apparatus[pf], shuffled_contribs)
            perm_metrics.append(result)
            run_counter += 1
            if run_counter % 200 == 0:
                print(f"    Progress: {run_counter}/{total_null_runs} null runs...")

        n2_results[pf] = _aggregate_null_results(perm_metrics)
    null_results["N2_domain_preserve_shuffle"] = n2_results

    # ── N3: Line shuffle within section ───────────────────────────────
    print("\n  N3: Line shuffle within section...")
    n3_results = {}

    for pf in PILOT_FOLIOS:
        perm_metrics = []
        sec = folio_section_map.get(pf, "H")

        # Get all lines for this section
        all_section_lines = section_lines[sec]

        # Count how many lines the pilot folio originally has
        original_lines = list(folio_line_tokens[pf].keys())
        n_folio_lines = len(original_lines)

        # Collect all contribution-lists per line for the section
        section_line_contribs = []
        for (fid, lid, toks) in all_section_lines:
            line_contribs = [tok["contributions"] for tok in toks]
            section_line_contribs.append(line_contribs)

        for perm_idx in range(N_PERMS):
            random.seed(42 + perm_idx)
            # Randomly sample n_folio_lines from section's line pool (with replacement
            # if needed, but section should have enough lines)
            if len(section_line_contribs) >= n_folio_lines:
                sampled_lines = random.sample(section_line_contribs, n_folio_lines)
            else:
                sampled_lines = random.choices(section_line_contribs, k=n_folio_lines)

            # Flatten sampled lines into token sequence
            flat_contribs = []
            for line_c in sampled_lines:
                flat_contribs.extend(line_c)

            result = run_folio_execution(pilot_apparatus[pf], flat_contribs)
            perm_metrics.append(result)
            run_counter += 1
            if run_counter % 200 == 0:
                print(f"    Progress: {run_counter}/{total_null_runs} null runs...")

        n3_results[pf] = _aggregate_null_results(perm_metrics)
    null_results["N3_line_shuffle"] = n3_results

    # ── N4: Within-line token shuffle ─────────────────────────────────
    print("\n  N4: Within-line token shuffle...")
    n4_results = {}

    for pf in PILOT_FOLIOS:
        perm_metrics = []
        # Get line groups for this folio
        lines_dict = folio_line_tokens[pf]
        # Preserve line ordering by sorting line keys
        sorted_lines = sorted(lines_dict.keys(), key=lambda x: (len(x), x))

        for perm_idx in range(N_PERMS):
            random.seed(42 + perm_idx)
            flat_contribs = []
            for lid in sorted_lines:
                line_toks = lines_dict[lid]
                line_contribs = [tok["contributions"] for tok in line_toks]
                if len(line_contribs) > 1:
                    random.shuffle(line_contribs)
                flat_contribs.extend(line_contribs)

            result = run_folio_execution(pilot_apparatus[pf], flat_contribs)
            perm_metrics.append(result)
            run_counter += 1
            if run_counter % 200 == 0:
                print(f"    Progress: {run_counter}/{total_null_runs} null runs...")

        n4_results[pf] = _aggregate_null_results(perm_metrics)
    null_results["N4_terminal_shuffle"] = n4_results

    # ==================================================================
    # Output
    # ==================================================================
    elapsed = time.time() - t_start
    print(f"\n--- Complete ({elapsed:.1f}s, {run_counter} null runs) ---")

    output = {
        "metadata": {
            "phase": "563",
            "task": "T4_null_and_ablation_executor",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_pilot_folios": len(PILOT_FOLIOS),
            "pilot_folios": PILOT_FOLIOS,
            "n_baselines": 5,
            "n_nulls": 4,
            "n_perms": N_PERMS,
            "elapsed_seconds": round(elapsed, 1),
        },
        "reference": reference_results,
        "baselines": baseline_results,
        "nulls": null_results,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=1)

    file_size = OUTPUT_PATH.stat().st_size
    print(f"\n  Output: {OUTPUT_PATH}")
    print(f"  Size: {file_size:,} bytes")

    # ── Summary table ─────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print("SUMMARY: Viability Fractions")
    print(f"{'=' * 70}")

    header = f"  {'Model':<30}"
    for pf in PILOT_FOLIOS:
        header += f" {pf:>7}"
    print(header)
    print("  " + "-" * (30 + 8 * len(PILOT_FOLIOS)))

    # Reference
    row = f"  {'REFERENCE':<30}"
    for pf in PILOT_FOLIOS:
        row += f" {reference_results[pf]['viability_fraction']:>7.4f}"
    print(row)

    # Baselines
    for bname, bresults in baseline_results.items():
        row = f"  {bname:<30}"
        for pf in PILOT_FOLIOS:
            row += f" {bresults[pf]['viability_fraction']:>7.4f}"
        print(row)

    # Nulls (mean +/- std)
    for nname, nresults in null_results.items():
        row = f"  {nname:<30}"
        for pf in PILOT_FOLIOS:
            mean_v = nresults[pf]["viability_mean"]
            std_v = nresults[pf]["viability_std"]
            row += f" {mean_v:>.3f}s{std_v:.2f}"[:8].rjust(8)
        print(row)

    print(f"\n  Null format: mean(std)")
    print(f"\nDone.")
    return 0


def _aggregate_null_results(perm_metrics):
    """Aggregate a list of per-permutation result dicts into summary stats."""
    n = len(perm_metrics)
    if n == 0:
        return {"viability_mean": 0.0, "viability_std": 0.0,
                "hazard_count_mean": 0.0, "hazard_count_std": 0.0,
                "Y_final_mean": 0.0, "Y_final_std": 0.0,
                "per_perm": []}

    viabilities = [m["viability_fraction"] for m in perm_metrics]
    hazards = [m["hazard_count"] for m in perm_metrics]
    y_finals = [m["Y_final"] for m in perm_metrics]

    def mean_std(vals):
        mu = sum(vals) / len(vals)
        var = sum((v - mu) ** 2 for v in vals) / len(vals)
        return mu, math.sqrt(var)

    v_mean, v_std = mean_std(viabilities)
    h_mean, h_std = mean_std(hazards)
    y_mean, y_std = mean_std(y_finals)

    # Also compute mean_state across perms
    state_sums = [0.0] * N_VARS
    for m in perm_metrics:
        for i in range(N_VARS):
            state_sums[i] += m["mean_state"][i]
    mean_state_across = [state_sums[i] / n for i in range(N_VARS)]

    # Store compact per-perm data (viability, hazard_count, Y_final only)
    per_perm = []
    for m in perm_metrics:
        per_perm.append({
            "viability_fraction": m["viability_fraction"],
            "hazard_count": m["hazard_count"],
            "Y_final": m["Y_final"],
        })

    return {
        "viability_mean": round(v_mean, 6),
        "viability_std": round(v_std, 6),
        "hazard_count_mean": round(h_mean, 4),
        "hazard_count_std": round(h_std, 4),
        "Y_final_mean": round(y_mean, 6),
        "Y_final_std": round(y_std, 6),
        "mean_state": [round(v, 6) for v in mean_state_across],
        "max_T_mean": round(sum(m["max_T"] for m in perm_metrics) / n, 6),
        "min_S_mean": round(sum(m["min_S"] for m in perm_metrics) / n, 6),
        "max_C_mean": round(sum(m["max_C"] for m in perm_metrics) / n, 6),
        "max_X_mean": round(sum(m["max_X"] for m in perm_metrics) / n, 6),
        "per_perm": per_perm,
    }


if __name__ == "__main__":
    raise SystemExit(main())
