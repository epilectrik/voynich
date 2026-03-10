"""
T4b: Null & Ablation Executor (Recalibrated)
=============================================
Phase 563b — ROUTING_ACCUMULATION_AND_DYNAMIC_RECALIBRATION

Runs 20 pilot folios under degraded supervisory interfaces (6 baselines + 4 nulls)
to test which layers carry real plant-level signal.

Execution engine matches T3b:
  - Recalibrated profiles from T1b
  - Routing accumulator (ROUTING_DECAY=0.7, ROUTING_GAIN=0.5, multiplicative)
  - Headless profile modulation via apply_headless_modulation()

Run types:
  REF  = Full reference                              20 runs
  B1   = Section-mean contributions                  20 runs
  B2   = Folio-mean contributions                    20 runs
  B3   = Undo CTS modulation                         20 runs
  B4   = Disable routing accumulator                  20 runs
  B5   = Skip headless modulation (keep HL tokens)   20 runs
  B6   = Skip headless mod AND replace HL contribs   20 runs
  N1   = Token shuffle within folio (50 perms)      1000 runs
  N2   = Domain-preserving form shuffle (50 perms)  1000 runs
  N3   = Line shuffle within section (50 perms)     1000 runs
  N4   = Within-line token position shuffle (50 perm)1000 runs
  Total                                             4140 runs

Inputs:
  - t1b_apparatus_recalibrated.json
  - t2b_supervisory_interface_unrouted.json

Output:
  - t4b_null_ablation_traces.json
"""

import json
import time
import random
import copy
import math
from pathlib import Path
from collections import defaultdict
import sys

# ---------------------------------------------------------------------------
# Import apparatus
# ---------------------------------------------------------------------------
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
from t1_apparatus_family_builder import (
    VirtualApparatus, STATE_VARS, HAZARD_BOUNDARIES, N_VARS
)
from t1b_apparatus_recalibration import apply_headless_modulation

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
phase_dir = script_dir.parent
results_dir = phase_dir / "results"
T1B_PATH = results_dir / "t1b_apparatus_recalibrated.json"
T2B_PATH = results_dir / "t2b_supervisory_interface_unrouted.json"
OUTPUT_PATH = results_dir / "t4b_null_ablation_traces.json"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ROUTING_DECAY = 0.7
ROUTING_GAIN = 0.5
N_PERMS = 50

SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}

# Routing effects (C1563) — same as T2b/T3b
ROUTING_EFFECTS = {
    'r': {'boost': {'X': 1.4}, 'suppress': {'S': 0.6, 'C': 0.7, 'Y': 0.7}},
    'y': {'boost': {'T': 1.4}, 'suppress': {'X': 0.7, 'C': 0.7}},
    'h': {'boost': {'TR': 1.4, 'RC': 1.3}, 'suppress': {'X': 0.7, 'T': 0.7}},
    'm': {'boost': {'C': 1.4}, 'suppress': {'T': 0.7, 'X': 0.7, 'TR': 0.7}},
    'n': {'boost': {'S': 1.2}, 'suppress': {'X': 0.8, 'T': 0.8}},
    'l': {'boost': {'TR': 1.2, 'S': 1.2}, 'suppress': {'X': 0.8}},
}

# 20 Pilot Folios
PILOT_FOLIOS = [
    "f78r", "f84r", "f79r", "f81v",           # B
    "f55r", "f40v", "f43v", "f34r",            # H
    "f31r", "f39v", "f95r1",                   # H
    "f104r", "f111r", "f116r", "f105r", "f108v",  # S
    "f66r", "f85r1",                           # T
    "f86v5", "f86v6",                          # C
]


# ---------------------------------------------------------------------------
# Sort key
# ---------------------------------------------------------------------------
def sort_key(tok):
    try:
        ln = int(tok["line"])
    except (ValueError, TypeError):
        ln = 0
    lp = tok.get("line_pos", 0.0)
    if not isinstance(lp, (int, float)):
        lp = 0.0
    return (ln, lp)


# ---------------------------------------------------------------------------
# Core execution engine (matches T3b logic)
# ---------------------------------------------------------------------------
def run_execution(tokens, profile_params, *, use_routing=True):
    """
    Execute a folio token sequence against an apparatus profile.

    Each token dict must have: 'contributions', 'line', 'routing_active', 'routing_terminal'

    Routing accumulator:
      - routing_accum starts at [0.0]*7
      - Resets to [0.0]*7 at line boundaries
      - Routing event: accum[i] += (mult - 1.0) * ROUTING_GAIN
      - Effective sensitivity: base_sensitivity * (1.0 + routing_accum[i])
      - Decay: accum[i] *= ROUTING_DECAY (after computing dV)
    """
    app = VirtualApparatus(profile_params)
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {
            "viability_fraction": 1.0,
            "hazard_count": 0,
            "Y_final": 0.5,
            "mean_state": [0.5] * N_VARS,
            "max_T": 0.5, "min_S": 0.5, "max_C": 0.5, "max_X": 0.5,
        }

    state = [0.5] * N_VARS
    routing_accum = [0.0] * N_VARS
    prev_line = None
    n_viable = 0
    hazard_count = 0
    state_sum = [0.0] * N_VARS
    max_T = 0.0
    min_S = 1.0
    max_C = 0.0
    max_X = 0.0

    for tok in tokens:
        # Line boundary detection -> reset routing accumulator
        cur_line = tok.get("line", "?")
        if cur_line != prev_line:
            routing_accum = [0.0] * N_VARS
            prev_line = cur_line

        # Routing event -> add to accumulator
        if use_routing and tok.get("routing_active") and tok.get("routing_terminal"):
            rt = tok["routing_terminal"]
            if rt in ROUTING_EFFECTS:
                effects = ROUTING_EFFECTS[rt]
                for sv, mult in effects.get('boost', {}).items():
                    routing_accum[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_GAIN
                for sv, mult in effects.get('suppress', {}).items():
                    routing_accum[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_GAIN

        # Compute dV with routing-modulated sensitivity
        contribs = tok["contributions"]
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            eff_sens = app.sensitivity(sv) * (1.0 + routing_accum[i])
            dV[i] = contribs[i] * eff_sens

        # Update state
        state = app.update(state, dV)

        # Decay accumulator
        routing_accum = [a * ROUTING_DECAY for a in routing_accum]

        # Hazard check
        in_bounds = True
        for i, var in enumerate(STATE_VARS):
            lo, hi = HAZARD_BOUNDARIES[var]
            if lo is not None and state[i] < lo:
                in_bounds = False
            if hi is not None and state[i] > hi:
                in_bounds = False

        if in_bounds:
            n_viable += 1
        else:
            hazard_count += 1

        # Track extrema and sums
        if state[0] > max_T:
            max_T = state[0]
        if state[2] < min_S:
            min_S = state[2]
        if state[3] > max_C:
            max_C = state[3]
        if state[5] > max_X:
            max_X = state[5]
        for i in range(N_VARS):
            state_sum[i] += state[i]

    mean_state = [state_sum[i] / n_tokens for i in range(N_VARS)]

    return {
        "viability_fraction": round(n_viable / n_tokens, 6),
        "hazard_count": hazard_count,
        "Y_final": round(state[SV_INDEX['Y']], 6),
        "max_T": round(max_T, 6),
        "min_S": round(min_S, 6),
        "max_C": round(max_C, 6),
        "max_X": round(max_X, 6),
        "mean_state": [round(v, 6) for v in mean_state],
    }


# ---------------------------------------------------------------------------
# Contribution manipulation
# ---------------------------------------------------------------------------
def undo_cts(tok):
    """Undo CTS modulation on a token's contributions."""
    contribs = list(tok["contributions"])
    cts = tok.get("cts", 0.0)
    if cts == 0.0:
        return contribs
    c_factor = 1.0 + 0.3 * cts
    s_factor = 1.0 + 0.2 * cts
    y_factor = 1.0 + 0.4 * cts
    if abs(s_factor) > 1e-10:
        contribs[2] /= s_factor
    if abs(c_factor) > 1e-10:
        contribs[3] /= c_factor
    if abs(y_factor) > 1e-10:
        contribs[6] /= y_factor
    return contribs


def make_tok_with_contribs(tok, contribs):
    """Create a new token dict with replaced contributions."""
    t = dict(tok)
    t["contributions"] = contribs
    return t


# ---------------------------------------------------------------------------
# Null model shufflers
# ---------------------------------------------------------------------------
def null_n1_token_shuffle(tokens, rng):
    """N1: Shuffle all tokens within folio. Routing info moves with tokens."""
    shuffled = list(tokens)
    rng.shuffle(shuffled)
    return shuffled


def null_n2_domain_preserve_shuffle(tokens, rng):
    """N2: Within each domain group, shuffle contribution vectors + routing info."""
    domain_groups = defaultdict(list)
    for i, t in enumerate(tokens):
        domain_groups[t.get("domain", "")].append(i)

    out = list(tokens)  # copy references
    for domain, indices in domain_groups.items():
        if len(indices) <= 1:
            continue
        # Collect the full token dicts for shuffling
        group_tokens = [tokens[i] for i in indices]
        rng.shuffle(group_tokens)
        for j, orig_idx in enumerate(indices):
            out[orig_idx] = group_tokens[j]
    return out


def null_n3_line_shuffle(tokens, section_line_pool, rng):
    """N3: Replace folio lines with randomly sampled lines from section pool."""
    # Group folio tokens by line (preserving order within lines)
    folio_lines = defaultdict(list)
    line_order = []
    for t in tokens:
        lk = t.get("line", "?")
        if lk not in folio_lines:
            line_order.append(lk)
        folio_lines[lk].append(t)

    n_folio_lines = len(line_order)
    if not section_line_pool:
        return list(tokens)

    # Sample n_folio_lines lines from section pool
    if len(section_line_pool) >= n_folio_lines:
        sampled = rng.sample(section_line_pool, n_folio_lines)
    else:
        sampled = [rng.choice(section_line_pool) for _ in range(n_folio_lines)]

    # Flatten sampled lines
    out = []
    for line_tokens in sampled:
        out.extend(line_tokens)
    return out


def null_n4_within_line_shuffle(tokens, rng):
    """N4: Shuffle token positions within each line."""
    line_groups = defaultdict(list)
    line_order = []
    for t in tokens:
        lk = t.get("line", "?")
        if lk not in line_groups:
            line_order.append(lk)
        line_groups[lk].append(t)

    out = []
    for lk in line_order:
        line_toks = list(line_groups[lk])
        rng.shuffle(line_toks)
        out.extend(line_toks)
    return out


# ---------------------------------------------------------------------------
# Aggregate null results
# ---------------------------------------------------------------------------
def aggregate_null_results(perm_results):
    """Aggregate list of per-perm result dicts."""
    n = len(perm_results)
    if n == 0:
        return {"viability_mean": 0.0, "viability_std": 0.0,
                "hazard_count_mean": 0.0, "Y_final_mean": 0.0,
                "mean_state": [0.5] * N_VARS, "per_perm": []}

    viabilities = [r["viability_fraction"] for r in perm_results]
    hazards = [r["hazard_count"] for r in perm_results]
    y_finals = [r["Y_final"] for r in perm_results]

    v_mean = sum(viabilities) / n
    v_std = math.sqrt(sum((v - v_mean)**2 for v in viabilities) / n)
    h_mean = sum(hazards) / n
    y_mean = sum(y_finals) / n

    state_sums = [0.0] * N_VARS
    for r in perm_results:
        for i in range(N_VARS):
            state_sums[i] += r["mean_state"][i]
    mean_state = [state_sums[i] / n for i in range(N_VARS)]

    per_perm = [{"viability_fraction": r["viability_fraction"],
                 "hazard_count": r["hazard_count"],
                 "Y_final": r["Y_final"]} for r in perm_results]

    return {
        "viability_mean": round(v_mean, 6),
        "viability_std": round(v_std, 6),
        "hazard_count_mean": round(h_mean, 4),
        "Y_final_mean": round(y_mean, 6),
        "mean_state": [round(v, 6) for v in mean_state],
        "max_T_mean": round(sum(r["max_T"] for r in perm_results) / n, 6),
        "min_S_mean": round(sum(r["min_S"] for r in perm_results) / n, 6),
        "max_C_mean": round(sum(r["max_C"] for r in perm_results) / n, 6),
        "max_X_mean": round(sum(r["max_X"] for r in perm_results) / n, 6),
        "per_perm": per_perm,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    print("=" * 70)
    print("T4b: Null & Ablation Executor (Recalibrated)")
    print("Phase 563b — ROUTING_ACCUMULATION_AND_DYNAMIC_RECALIBRATION")
    print("=" * 70)

    # ── Load inputs ───────────────────────────────────────────────────
    print("\nLoading inputs...")

    with open(T1B_PATH) as f:
        t1b_data = json.load(f)
    folio_assignments = t1b_data["folio_assignments"]
    recal_profiles = t1b_data["profiles"]
    print(f"  T1b folio assignments: {len(folio_assignments)}")

    with open(T2B_PATH) as f:
        t2b_data = json.load(f)
    all_tokens = t2b_data["token_signals"]
    print(f"  T2b tokens: {len(all_tokens)}")

    # ── Index tokens ─────────────────────────────────────────────────
    print("\nIndexing tokens...")
    tokens_by_folio = defaultdict(list)
    tokens_by_section = defaultdict(list)
    folio_section_map = {}

    for tok in all_tokens:
        folio = tok["folio"]
        section = tok["section"]
        tokens_by_folio[folio].append(tok)
        tokens_by_section[section].append(tok)
        if folio not in folio_section_map:
            folio_section_map[folio] = section

    # Sort each folio
    for fid in tokens_by_folio:
        tokens_by_folio[fid].sort(key=sort_key)

    # Pre-compute section means
    section_means = {}
    for sec, toks in tokens_by_section.items():
        n = len(toks)
        sums = [0.0] * N_VARS
        for t in toks:
            for i in range(N_VARS):
                sums[i] += t["contributions"][i]
        section_means[sec] = [sums[i] / n for i in range(N_VARS)]

    # Pre-compute folio means
    folio_means = {}
    for fid, toks in tokens_by_folio.items():
        n = len(toks)
        sums = [0.0] * N_VARS
        for t in toks:
            for i in range(N_VARS):
                sums[i] += t["contributions"][i]
        folio_means[fid] = [sums[i] / n for i in range(N_VARS)]

    # Build section line pools for N3 (list of line token-lists per section)
    section_line_pool = defaultdict(list)  # section -> list of [tok, tok, ...]
    for sec, sec_toks in tokens_by_section.items():
        line_groups = defaultdict(list)
        for t in sec_toks:
            lk = f"{t['folio']}|{t['line']}"
            line_groups[lk].append(t)
        section_line_pool[sec] = list(line_groups.values())

    # Pre-compute folio headless rates
    folio_hl_rates = {}
    for fid, toks in tokens_by_folio.items():
        n_hl = sum(1 for t in toks if t.get("headless_subtype", "HEADED") != "HEADED")
        folio_hl_rates[fid] = n_hl / len(toks) if toks else 0.0

    # ── Determine pilot folios ───────────────────────────────────────
    pilot_info = {}
    n_skipped = 0
    for fid in PILOT_FOLIOS:
        toks = tokens_by_folio.get(fid, [])
        if not toks:
            print(f"  WARNING: {fid} has 0 tokens in T2b, skipping")
            n_skipped += 1
            continue

        fa = folio_assignments.get(fid, {})
        pref = fa.get("preferred_profile", "A2_SEALED_RECIRCULATION")
        sec = fa.get("section", folio_section_map.get(fid, "?"))
        regime = fa.get("regime", "?")

        pilot_info[fid] = {
            "preferred_profile": pref,
            "section": sec,
            "regime": regime,
            "n_tokens": len(toks),
            "hl_rate": folio_hl_rates.get(fid, 0.20),
        }
        print(f"  {fid}: {len(toks)} tokens, sec={sec}, pref={pref}, hl={folio_hl_rates.get(fid, 0):.3f}")

    print(f"  Pilot folios loaded: {len(pilot_info)}")
    print(f"  Skipped: {n_skipped}")

    # ── Run all traces ───────────────────────────────────────────────
    total_runs = len(pilot_info) * (1 + 6 + 4 * N_PERMS)
    print(f"\nTotal planned runs: {total_runs}")

    reference_results = {}
    baseline_results = {f"B{i}": {} for i in range(1, 7)}
    null_results = {f"N{i}": {} for i in range(1, 5)}
    run_count = 0

    for fid in sorted(pilot_info.keys()):
        toks = tokens_by_folio[fid]
        info = pilot_info[fid]
        pref = info["preferred_profile"]
        sec = info["section"]
        hl_rate = info["hl_rate"]
        base_profile = recal_profiles[pref]

        # Profile WITH headless modulation
        profile_hl = apply_headless_modulation(base_profile, hl_rate)
        # Profile WITHOUT headless modulation
        profile_no_hl = dict(base_profile)

        # ── REF ────────────────────────────────────────────────────
        ref_result = run_execution(toks, profile_hl, use_routing=True)
        reference_results[fid] = ref_result
        run_count += 1

        # ── B1: Section-mean contributions ─────────────────────────
        sec_mean = section_means.get(sec, [0.0] * N_VARS)
        b1_toks = [make_tok_with_contribs(t, sec_mean) for t in toks]
        baseline_results["B1"][fid] = run_execution(b1_toks, profile_hl, use_routing=True)
        run_count += 1

        # ── B2: Folio-mean contributions ───────────────────────────
        f_mean = folio_means.get(fid, [0.0] * N_VARS)
        b2_toks = [make_tok_with_contribs(t, f_mean) for t in toks]
        baseline_results["B2"][fid] = run_execution(b2_toks, profile_hl, use_routing=True)
        run_count += 1

        # ── B3: Undo CTS ──────────────────────────────────────────
        b3_toks = [make_tok_with_contribs(t, undo_cts(t)) for t in toks]
        baseline_results["B3"][fid] = run_execution(b3_toks, profile_hl, use_routing=True)
        run_count += 1

        # ── B4: No routing ─────────────────────────────────────────
        baseline_results["B4"][fid] = run_execution(toks, profile_hl, use_routing=False)
        run_count += 1

        # ── B5: No headless modulation (keep HL token contribs) ────
        baseline_results["B5"][fid] = run_execution(toks, profile_no_hl, use_routing=True)
        run_count += 1

        # ── B6: No headless modulation AND replace HL contribs ─────
        b6_toks = []
        for t in toks:
            if t.get("headless_subtype", "HEADED") != "HEADED":
                b6_toks.append(make_tok_with_contribs(t, sec_mean))
            else:
                b6_toks.append(t)
        baseline_results["B6"][fid] = run_execution(b6_toks, profile_no_hl, use_routing=True)
        run_count += 1

        # ── N1: Token shuffle ──────────────────────────────────────
        n1_perms = []
        for p in range(N_PERMS):
            rng = random.Random(42 + p)
            shuffled = null_n1_token_shuffle(toks, rng)
            n1_perms.append(run_execution(shuffled, profile_hl, use_routing=True))
            run_count += 1
        null_results["N1"][fid] = aggregate_null_results(n1_perms)

        # ── N2: Domain-preserving form shuffle ─────────────────────
        n2_perms = []
        for p in range(N_PERMS):
            rng = random.Random(42 + p)
            shuffled = null_n2_domain_preserve_shuffle(toks, rng)
            n2_perms.append(run_execution(shuffled, profile_hl, use_routing=True))
            run_count += 1
        null_results["N2"][fid] = aggregate_null_results(n2_perms)

        # ── N3: Line shuffle within section ────────────────────────
        n3_perms = []
        pool = section_line_pool.get(sec, [])
        for p in range(N_PERMS):
            rng = random.Random(42 + p)
            shuffled = null_n3_line_shuffle(toks, pool, rng)
            n3_perms.append(run_execution(shuffled, profile_hl, use_routing=True))
            run_count += 1
        null_results["N3"][fid] = aggregate_null_results(n3_perms)

        # ── N4: Within-line token shuffle ──────────────────────────
        n4_perms = []
        for p in range(N_PERMS):
            rng = random.Random(42 + p)
            shuffled = null_n4_within_line_shuffle(toks, rng)
            n4_perms.append(run_execution(shuffled, profile_hl, use_routing=True))
            run_count += 1
        null_results["N4"][fid] = aggregate_null_results(n4_perms)

        elapsed_so_far = time.time() - t_start
        print(f"  {fid}: {run_count}/{total_runs} runs  ({elapsed_so_far:.1f}s)")

    # ── Summary statistics ────────────────────────────────────────────
    elapsed = time.time() - t_start
    print(f"\n{'=' * 70}")
    print(f"SUMMARY ({run_count} runs in {elapsed:.1f}s)")
    print(f"{'=' * 70}")

    # Viability table: REF vs baselines
    print(f"\n  {'Folio':<8} {'REF':>7}  {'B1':>7} {'B2':>7} {'B3':>7} "
          f"{'B4':>7} {'B5':>7} {'B6':>7}  {'N1m':>7} {'N2m':>7} {'N3m':>7} {'N4m':>7}")
    print(f"  {'-'*8} {'-'*7}  {'-'*7} {'-'*7} {'-'*7} "
          f"{'-'*7} {'-'*7} {'-'*7}  {'-'*7} {'-'*7} {'-'*7} {'-'*7}")

    ref_beats_b2 = 0
    ref_beats_n1 = 0
    n_compared = 0

    for fid in sorted(pilot_info.keys()):
        rv = reference_results[fid]["viability_fraction"]
        b_vals = [baseline_results[f"B{i}"].get(fid, {}).get("viability_fraction", 0)
                  for i in range(1, 7)]
        n_vals = [null_results[f"N{i}"].get(fid, {}).get("viability_mean", 0)
                  for i in range(1, 5)]

        if rv > b_vals[1]:  # B2
            ref_beats_b2 += 1
        if rv > n_vals[0]:  # N1
            ref_beats_n1 += 1
        n_compared += 1

        b_str = " ".join(f"{v:>7.4f}" for v in b_vals)
        n_str = " ".join(f"{v:>7.4f}" for v in n_vals)
        print(f"  {fid:<8} {rv:>7.4f}  {b_str}  {n_str}")

    print(f"\n  REF > B2: {ref_beats_b2}/{n_compared}")
    print(f"  REF > N1 mean: {ref_beats_n1}/{n_compared}")

    # Baseline deltas
    print(f"\n  Baseline delta from REF:")
    print(f"  {'Folio':<8} {'dB1':>7} {'dB2':>7} {'dB3':>7} {'dB4':>7} {'dB5':>7} {'dB6':>7}")
    print(f"  {'-'*8} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
    for fid in sorted(pilot_info.keys()):
        rv = reference_results[fid]["viability_fraction"]
        deltas = [baseline_results[f"B{i}"].get(fid, {}).get("viability_fraction", rv) - rv
                  for i in range(1, 7)]
        d_str = " ".join(f"{d:>+7.4f}" for d in deltas)
        print(f"  {fid:<8} {d_str}")

    # Mean viability per model
    print(f"\n  Mean viability across folios:")
    ref_viabs = [reference_results[f]["viability_fraction"] for f in sorted(pilot_info.keys())]
    print(f"    REF:  {sum(ref_viabs)/len(ref_viabs):.4f}")
    for bi in range(1, 7):
        bk = f"B{bi}"
        viabs = [baseline_results[bk].get(f, {}).get("viability_fraction", 0)
                 for f in sorted(pilot_info.keys())]
        print(f"    {bk}:   {sum(viabs)/len(viabs):.4f}")
    for ni in range(1, 5):
        nk = f"N{ni}"
        viabs = [null_results[nk].get(f, {}).get("viability_mean", 0)
                 for f in sorted(pilot_info.keys())]
        print(f"    {nk}:   {sum(viabs)/len(viabs):.4f}")

    # ── Build output ─────────────────────────────────────────────────
    output = {
        "metadata": {
            "phase": "563b",
            "task": "T4b_null_ablation_executor",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_pilot_folios": len(PILOT_FOLIOS),
            "n_folios_run": len(pilot_info),
            "n_folios_skipped": n_skipped,
            "n_perms": N_PERMS,
            "total_runs": run_count,
            "elapsed_seconds": round(elapsed, 1),
            "routing_decay": ROUTING_DECAY,
            "routing_gain": ROUTING_GAIN,
            "state_variables": STATE_VARS,
            "hazard_boundaries": HAZARD_BOUNDARIES,
        },
        "reference": reference_results,
        "baselines": {
            "B1_section_mean": baseline_results["B1"],
            "B2_folio_mean": baseline_results["B2"],
            "B3_full_minus_cts": baseline_results["B3"],
            "B4_full_minus_routing": baseline_results["B4"],
            "B5_full_minus_headless_mod": baseline_results["B5"],
            "B6_full_minus_all_headless": baseline_results["B6"],
        },
        "nulls": {
            "N1_token_shuffle": null_results["N1"],
            "N2_domain_preserve_shuffle": null_results["N2"],
            "N3_line_shuffle": null_results["N3"],
            "N4_within_line_shuffle": null_results["N4"],
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=1)

    file_size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"\n  Output: {OUTPUT_PATH}")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"\nDone. {run_count} runs in {elapsed:.1f}s")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
