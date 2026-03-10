"""
T5b: Plant Behavior Validation (Recalibrated)
==============================================
Phase 563b — ROUTING_ACCUMULATION_AND_DYNAMIC_RECALIBRATION

8-test battery (P1-P8) on expanded 20-folio pilot set.

Tests:
  P1:  Viable envelope occupancy (full > B2 + N1)
  P2:  Line packet shape recovery (KW across SPEC/WORK/CLOSE)
  P3:  Section template differentiation (SECONDARY, not gating)
  P3b: Productive operating diversity (enhanced with bounded excursions)
  P4:  Routing consequence fidelity (REDESIGNED: cumulative between-subjects)
  P5:  Headless regime consequence (REDESIGNED: P5a full vs B6, P5b HL split)
  P6:  CTS closure value
  P7:  Null destruction
  P8:  Preferred profile superiority

Core pass criteria (PLANT_COUPLING_VALIDATED): P1 + P2 + P3b + P4 + P7
P3 is SECONDARY (reported, not gating). P5, P6, P8 strongly preferred.

Inputs:
  - t3b_coupled_traces.json
  - t4b_null_ablation_traces.json
  - t2b_supervisory_interface_unrouted.json
  - t3_line_packets.json (from SECTION_TEMPLATE_TRACE_EXECUTOR)

Output:
  - t5b_plant_validation.json
"""

import json
import math
import time
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path("phases/VIRTUAL_APPARATUS_COUPLING")
STXE = Path("phases/SECTION_TEMPLATE_TRACE_EXECUTOR")

T3B_PATH = BASE / "results" / "t3b_coupled_traces.json"
T4B_PATH = BASE / "results" / "t4b_null_ablation_traces.json"
T2B_PATH = BASE / "results" / "t2b_supervisory_interface_unrouted.json"
LP_PATH = STXE / "results" / "t3_line_packets.json"
OUT_PATH = BASE / "results" / "t5b_plant_validation.json"

SV_NAMES = ["T", "RC", "S", "C", "TR", "X", "Y"]
N_VARS = 7

PILOT_FOLIOS = [
    "f78r", "f84r", "f79r", "f81v",
    "f55r", "f40v", "f43v", "f34r",
    "f31r", "f39v", "f95r1",
    "f104r", "f111r", "f116r", "f105r", "f108v",
    "f66r", "f85r1",
    "f86v5", "f86v6",
]
N_FOLIOS = 20

# Core routing quartet for P4
ROUTING_QUARTET = {
    'r': {'target_sv': 5, 'target_name': 'X'},
    'y': {'target_sv': 0, 'target_name': 'T'},
    'h': {'target_sv': 4, 'target_name': 'TR'},
    'm': {'target_sv': 3, 'target_name': 'C'},
}
ROUTING_WINDOW = 7


# ---------------------------------------------------------------------------
# Statistical helpers (no scipy)
# ---------------------------------------------------------------------------
def chi2_survival(x, df):
    if x <= 0 or df <= 0:
        return 1.0
    z = ((x / df) ** (1.0/3.0) - (1.0 - 2.0/(9.0*df))) / math.sqrt(2.0/(9.0*df))
    p = 0.5 * (1.0 - math.erf(z / math.sqrt(2.0)))
    return max(0.0, min(1.0, p))


def kruskal_wallis(*groups):
    groups = [g for g in groups if len(g) > 0]
    if len(groups) < 2:
        return 0.0, 1.0
    all_data = []
    for i, g in enumerate(groups):
        for v in g:
            all_data.append((v, i))
    all_data.sort(key=lambda x: x[0])
    N = len(all_data)
    if N < 3:
        return 0.0, 1.0
    ranks = [0.0] * N
    i = 0
    while i < N:
        j = i
        while j < N and all_data[j][0] == all_data[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    group_ranks = [[] for _ in groups]
    for idx, (val, gid) in enumerate(all_data):
        group_ranks[gid].append(ranks[idx])
    H = 0.0
    for gr in group_ranks:
        if len(gr) == 0:
            continue
        n_i = len(gr)
        R_i = sum(gr)
        H += R_i ** 2 / n_i
    H = (12.0 / (N * (N + 1))) * H - 3.0 * (N + 1)
    df = len(groups) - 1
    p = chi2_survival(H, df)
    return H, p


def mann_whitney_u(x, y):
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0, 0.0, 1.0
    combined = [(v, 0) for v in x] + [(v, 1) for v in y]
    combined.sort(key=lambda t: t[0])
    N = len(combined)
    ranks = [0.0] * N
    i = 0
    while i < N:
        j = i
        while j < N and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    R1 = sum(ranks[i] for i in range(N) if combined[i][1] == 0)
    U1 = R1 - nx * (nx + 1) / 2.0
    U2 = nx * ny - U1
    U = min(U1, U2)
    mu = nx * ny / 2.0
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12.0) if nx + ny > 1 else 1.0
    z = (U - mu) / sigma if sigma > 0 else 0.0
    p = 2.0 * 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    p = min(p, 1.0)
    return U, z, p


def sort_key(tok):
    try:
        ln = int(tok["line"])
    except (ValueError, TypeError):
        ln = 0
    lp = tok.get("line_pos", 0.0)
    if not isinstance(lp, (int, float)):
        lp = 0.0
    return (ln, lp)


def safe_mean(vals):
    return sum(vals) / len(vals) if vals else 0.0


def safe_std(vals):
    if len(vals) < 2:
        return 0.0
    m = safe_mean(vals)
    return math.sqrt(sum((v - m)**2 for v in vals) / len(vals))


# ======================================================================
# Load data
# ======================================================================
print("=" * 70)
print("T5b: Plant Behavior Validation (Recalibrated)")
print("Phase 563b — ROUTING_ACCUMULATION_AND_DYNAMIC_RECALIBRATION")
print("=" * 70)
t_start = time.time()

print("\nLoading T3b coupled traces...")
with open(T3B_PATH) as f:
    t3b = json.load(f)

print("Loading T4b null/ablation traces...")
with open(T4B_PATH) as f:
    t4b = json.load(f)

print("Loading T2b supervisory interface...")
with open(T2B_PATH) as f:
    t2b = json.load(f)

print("Loading line packets...")
try:
    with open(LP_PATH) as f:
        lp_data = json.load(f)
    line_packets = lp_data["line_packets"]
    print(f"  {len(line_packets)} line packets loaded")
except Exception as e:
    print(f"  WARNING: Could not load line packets: {e}")
    line_packets = {}

# Build lookups
ref = t4b["reference"]
baselines = t4b["baselines"]
nulls = t4b["nulls"]
t3b_runs = t3b["runs"]
t3b_cps = t3b["cross_profile_summary"]

# Get preferred runs from T3b (have trajectories)
preferred_runs = {}
for key, run in t3b_runs.items():
    if run.get("is_preferred") and "trajectory" in run:
        preferred_runs[run["folio"]] = run

# Build per-folio sorted T2b tokens (for P4)
t2b_tokens_by_folio = defaultdict(list)
for tok in t2b["token_signals"]:
    t2b_tokens_by_folio[tok["folio"]].append(tok)
for fol in t2b_tokens_by_folio:
    t2b_tokens_by_folio[fol].sort(key=sort_key)

# Section mapping from T3b cross_profile_summary
folio_sections = {}
for fol, cps_data in t3b_cps.items():
    folio_sections[fol] = cps_data.get("section", "?")

# Headless rates from T3b runs
folio_hl_rates = {}
for key, run in t3b_runs.items():
    if run.get("is_preferred"):
        folio_hl_rates[run["folio"]] = run.get("headless_rate", 0.25)

# Filter to pilot folios that are actually present
pilot_folios = [f for f in PILOT_FOLIOS if f in ref and f in preferred_runs]
print(f"\nPilot folios with data: {len(pilot_folios)}/{N_FOLIOS}")

results = {}


# ======================================================================
# P1: Viable Envelope Occupancy
# ======================================================================
print("\n" + "-" * 70)
print("P1: Viable Envelope Occupancy")
print("-" * 70)

p1_details = {"per_folio": {}, "full_gt_B2": 0, "full_gt_N1": 0}

for fol in pilot_folios:
    full_v = ref[fol]["viability_fraction"]
    b2_v = baselines["B2_folio_mean"][fol]["viability_fraction"]
    n1 = nulls["N1_token_shuffle"][fol]
    n1_mean = n1["viability_mean"]

    gt_b2 = full_v > b2_v or (full_v == b2_v and full_v >= 0.99)
    gt_n1 = full_v > n1_mean or (abs(full_v - n1_mean) < 0.01)

    p1_details["per_folio"][fol] = {
        "full_viab": round(full_v, 4),
        "B2_viab": round(b2_v, 4),
        "N1_viab_mean": round(n1_mean, 4),
        "full_gt_B2": gt_b2,
        "full_gt_N1": gt_n1,
    }
    if gt_b2:
        p1_details["full_gt_B2"] += 1
    if gt_n1:
        p1_details["full_gt_N1"] += 1
    print(f"  {fol}: full={full_v:.4f}  B2={b2_v:.4f}  N1={n1_mean:.4f}  "
          f">B2={gt_b2}  >N1={gt_n1}")

p1_pass = p1_details["full_gt_B2"] >= 14 and p1_details["full_gt_N1"] >= 14
p1_details["pass_criteria"] = (
    f"full>B2 {p1_details['full_gt_B2']}/{len(pilot_folios)}>=14 AND "
    f"full>N1 {p1_details['full_gt_N1']}/{len(pilot_folios)}>=14"
)
print(f"  VERDICT: full>B2={p1_details['full_gt_B2']}/{len(pilot_folios)}, "
      f"full>N1={p1_details['full_gt_N1']}/{len(pilot_folios)} -> "
      f"{'PASS' if p1_pass else 'FAIL'}")
results["P1_viable_envelope"] = {"pass": p1_pass, "details": p1_details}


# ======================================================================
# P2: Line Packet Shape Recovery
# ======================================================================
print("\n" + "-" * 70)
print("P2: Line Packet Shape Recovery")
print("-" * 70)

PHASES = ["SPEC", "WORK", "CLOSE"]
phase_state_vectors = {ph: {sv: [] for sv in range(N_VARS)} for ph in PHASES}

for fol in pilot_folios:
    run = preferred_runs[fol]
    traj = run["trajectory"]

    for tok in traj:
        line_key = tok.get("line", "?")
        lp_key = f"{fol}|{line_key}"
        packet = line_packets.get(lp_key, {})
        pp = packet.get("packet_state", {}).get("packet_phase", "WORK")
        if pp not in PHASES:
            pp = "WORK"

        state = tok["state"]
        for sv_i in range(N_VARS):
            phase_state_vectors[pp][sv_i].append(state[sv_i])

# Global KW across all folios pooled
global_kw = {}
n_global_sig = 0
for sv_i in range(N_VARS):
    groups = [phase_state_vectors[ph][sv_i] for ph in PHASES]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) >= 2:
        H, p = kruskal_wallis(*groups)
        sig = p < 0.05
        if sig:
            n_global_sig += 1
        global_kw[SV_NAMES[sv_i]] = {"H": round(H, 3), "p": round(p, 6), "sig": sig}

# Phase means
print("  Phase means (pooled):")
for ph in PHASES:
    means = []
    for sv_i in range(N_VARS):
        vals = phase_state_vectors[ph][sv_i]
        means.append(safe_mean(vals))
    n_toks = len(phase_state_vectors[ph][0])
    print(f"    {ph} (n={n_toks}): " +
          " ".join(f"{SV_NAMES[i]}={means[i]:.3f}" for i in range(N_VARS)))

print(f"\n  Global KW: {n_global_sig}/{N_VARS} significant")
for sv_name, det in global_kw.items():
    print(f"    {sv_name}: H={det['H']:.2f}, p={det['p']:.6f}, sig={det['sig']}")

p2_pass = n_global_sig >= 4
p2_details = {
    "global_n_sig": n_global_sig,
    "global_kw": global_kw,
    "pass_criteria": f"global KW sig on {n_global_sig}/{N_VARS} >= 4",
}
print(f"  VERDICT: {n_global_sig}/{N_VARS} -> {'PASS' if p2_pass else 'FAIL'}")
results["P2_packet_shape"] = {"pass": p2_pass, "details": p2_details}


# ======================================================================
# P3: Section Template Differentiation (SECONDARY — not gating)
# ======================================================================
print("\n" + "-" * 70)
print("P3: Section Template Differentiation (SECONDARY)")
print("-" * 70)

# Group folios by section
section_groups = defaultdict(list)
for fol in pilot_folios:
    sec = folio_sections.get(fol, "?")
    ms = ref[fol]["mean_state"]
    section_groups[sec].append((fol, ms))

sections_present = sorted(section_groups.keys())
print(f"  Sections: {sections_present}")
for sec in sections_present:
    fols = [f for f, _ in section_groups[sec]]
    print(f"    {sec}: {fols}")

# KW across all sections
p3_kw = {}
n_p3_sig = 0
for sv_i in range(N_VARS):
    groups = []
    for sec in sections_present:
        vals = [ms[sv_i] for _, ms in section_groups[sec]]
        groups.append(vals)
    H, p = kruskal_wallis(*groups)
    sig = p < 0.05
    if sig:
        n_p3_sig += 1
    p3_kw[SV_NAMES[sv_i]] = {"H": round(H, 3), "p": round(p, 5), "sig": sig}

print(f"\n  KW results ({len(sections_present)} sections): {n_p3_sig}/{N_VARS} significant")
for sv_name, det in p3_kw.items():
    print(f"    {sv_name}: H={det['H']:.2f}, p={det['p']:.5f}, sig={det['sig']}")

# Also report B/H/S triplet if we have 5+ sections
if len(sections_present) >= 3 and all(s in [sec for sec in sections_present] for s in ["B", "H", "S"]):
    bhs_kw = {}
    n_bhs_sig = 0
    for sv_i in range(N_VARS):
        groups = []
        for sec in ["B", "H", "S"]:
            vals = [ms[sv_i] for _, ms in section_groups[sec]]
            groups.append(vals)
        H, p = kruskal_wallis(*groups)
        sig = p < 0.05
        if sig:
            n_bhs_sig += 1
        bhs_kw[SV_NAMES[sv_i]] = {"H": round(H, 3), "p": round(p, 5), "sig": sig}
    print(f"  B/H/S triplet: {n_bhs_sig}/{N_VARS} significant")

p3_pass = n_p3_sig >= 4
p3_details = {
    "n_sections": len(sections_present),
    "sections": sections_present,
    "n_sig": n_p3_sig,
    "kw_results": p3_kw,
    "is_secondary": True,
    "pass_criteria": f"KW sig on {n_p3_sig}/{N_VARS} >= 4 (SECONDARY, not gating)",
}
print(f"  VERDICT: {n_p3_sig}/{N_VARS} -> {'PASS' if p3_pass else 'FAIL'} (SECONDARY)")
results["P3_section_template"] = {"pass": p3_pass, "details": p3_details}


# ======================================================================
# P3b: Productive Operating Diversity (ENHANCED)
# ======================================================================
print("\n" + "-" * 70)
print("P3b: Productive Operating Diversity (Enhanced)")
print("-" * 70)

p3b_details = {"per_folio": {}}
n_nontrivial_pass = 0
excursion_counts = []
bounded_excursion_counts = []

for fol in pilot_folios:
    run = preferred_runs[fol]
    traj = run["trajectory"]
    n_tokens = len(traj)

    # (a) fraction of tokens with at least one variable outside [0.4, 0.6]
    n_nontrivial = 0
    for tok in traj:
        state = tok["state"]
        if any(v > 0.6 or v < 0.4 for v in state):
            n_nontrivial += 1
    nontrivial_frac = n_nontrivial / n_tokens if n_tokens > 0 else 0

    # (b) count excursions: runs of tokens outside [0.4, 0.6] then return inside
    in_excursion = False
    n_excursions = 0
    for tok in traj:
        state = tok["state"]
        outside = any(v > 0.6 or v < 0.4 for v in state)
        inside = all(0.4 <= v <= 0.6 for v in state)
        if outside and not in_excursion:
            in_excursion = True
        elif inside and in_excursion:
            n_excursions += 1
            in_excursion = False
    if in_excursion:
        n_excursions += 1

    # (c) Bounded-excursion quality (NEW in 563b)
    #     Count excursions that (a) push past 0.65/below 0.35 (meaningful)
    #     AND (b) return to all-inside [0.4, 0.6] within 30 tokens
    in_bounded = False
    bounded_start = -1
    n_bounded = 0
    for i, tok in enumerate(traj):
        state = tok["state"]
        meaningful = any(v > 0.65 or v < 0.35 for v in state)
        all_settled = all(0.4 <= v <= 0.6 for v in state)

        if not in_bounded:
            if meaningful:
                in_bounded = True
                bounded_start = i
        else:
            if all_settled:
                if (i - bounded_start) <= 30:
                    n_bounded += 1
                in_bounded = False
            elif (i - bounded_start) > 30:
                in_bounded = False
                if meaningful:
                    in_bounded = True
                    bounded_start = i

    # (d) Y accumulation
    y_final = traj[-1]["state"][6] if traj else 0.5

    p3b_details["per_folio"][fol] = {
        "nontrivial_frac": round(nontrivial_frac, 4),
        "n_excursions": n_excursions,
        "n_bounded_excursions": n_bounded,
        "Y_final": round(y_final, 4),
        "n_tokens": n_tokens,
    }
    if nontrivial_frac > 0.4:
        n_nontrivial_pass += 1
    excursion_counts.append(n_excursions)
    bounded_excursion_counts.append(n_bounded)

    print(f"  {fol}: nontrivial={nontrivial_frac:.3f}, excursions={n_excursions}, "
          f"bounded={n_bounded}, Y={y_final:.3f} ({n_tokens} tokens)")

mean_excursions = safe_mean(excursion_counts)
mean_bounded = safe_mean(bounded_excursion_counts)
p3b_pass = n_nontrivial_pass >= 14 and mean_excursions > 3
p3b_details["n_nontrivial_pass"] = n_nontrivial_pass
p3b_details["mean_excursions"] = round(mean_excursions, 2)
p3b_details["mean_bounded_excursions"] = round(mean_bounded, 2)
p3b_details["pass_criteria"] = (
    f"nontrivial>0.4 for {n_nontrivial_pass}/{len(pilot_folios)}>=14 AND "
    f"mean_excursions={mean_excursions:.1f}>3"
)
print(f"  VERDICT: nontrivial_pass={n_nontrivial_pass}/{len(pilot_folios)}, "
      f"mean_excursions={mean_excursions:.1f}, mean_bounded={mean_bounded:.1f} -> "
      f"{'PASS' if p3b_pass else 'FAIL'}")
results["P3b_productive_diversity"] = {"pass": p3b_pass, "details": p3b_details}


# ======================================================================
# P4: Routing Consequence Fidelity (REDESIGNED: cumulative between-subjects)
# ======================================================================
print("\n" + "-" * 70)
print("P4: Routing Consequence Fidelity (Between-Subjects)")
print("-" * 70)

p4_route_details = {}
n_correct_routes = 0

for rt, info in ROUTING_QUARTET.items():
    target_sv = info["target_sv"]
    target_name = info["target_name"]

    group_a_vals = []  # in routing window for this type
    group_b_vals = []  # not in any routing window

    for fol in pilot_folios:
        traj = preferred_runs[fol]["trajectory"]
        t2b_toks = t2b_tokens_by_folio.get(fol, [])
        n = min(len(traj), len(t2b_toks))

        # Mark positions in ANY routing window (any type)
        in_any_window = set()
        # Mark positions in THIS routing type's window
        in_this_window = set()

        for i in range(n):
            tok = t2b_toks[i]
            if tok.get("routing_active") and tok.get("routing_terminal"):
                terminal = tok["routing_terminal"]
                if terminal in ROUTING_QUARTET:
                    for j in range(i + 1, min(i + 1 + ROUTING_WINDOW, n)):
                        in_any_window.add(j)
                    if terminal == rt:
                        for j in range(i + 1, min(i + 1 + ROUTING_WINDOW, n)):
                            in_this_window.add(j)

        # Collect target state variable values
        for i in range(n):
            sv_val = traj[i]["state"][target_sv]
            if i in in_this_window:
                group_a_vals.append(sv_val)
            elif i not in in_any_window:
                group_b_vals.append(sv_val)

    # Mann-Whitney test
    U, z, p = mann_whitney_u(group_a_vals, group_b_vals)
    a_mean = safe_mean(group_a_vals)
    b_mean = safe_mean(group_b_vals)
    correct = a_mean > b_mean and p < 0.05

    if correct:
        n_correct_routes += 1

    p4_route_details[rt] = {
        "target_sv": target_name,
        "n_group_a": len(group_a_vals),
        "n_group_b": len(group_b_vals),
        "group_a_mean": round(a_mean, 6),
        "group_b_mean": round(b_mean, 6),
        "delta": round(a_mean - b_mean, 6),
        "U": round(U, 1),
        "z": round(z, 3),
        "p": round(p, 5),
        "correct": correct,
    }
    print(f"  {rt}->{target_name}: A_mean={a_mean:.4f} B_mean={b_mean:.4f} "
          f"delta={a_mean-b_mean:+.4f}, U={U:.0f}, z={z:.3f}, p={p:.5f} "
          f"-> {'CORRECT' if correct else 'WRONG'}")

p4_pass = n_correct_routes >= 3
p4_details = {
    "n_correct_routes": n_correct_routes,
    "route_details": p4_route_details,
    "routing_window": ROUTING_WINDOW,
    "pass_criteria": f"{n_correct_routes}/4 >= 3 correct routing signatures",
}
print(f"  VERDICT: {n_correct_routes}/4 correct -> {'PASS' if p4_pass else 'FAIL'}")
results["P4_routing_consequence"] = {"pass": p4_pass, "details": p4_details}


# ======================================================================
# P5: Headless Regime Consequence (REDESIGNED)
# ======================================================================
print("\n" + "-" * 70)
print("P5: Headless Regime Consequence (Redesigned)")
print("-" * 70)

# P5a: Full vs B6 (no headless at all)
print("  P5a: Full (REF) vs B6 (no headless)")
b6 = baselines["B6_full_minus_all_headless"]

n_c_better = 0
n_s_better = 0
p5a_folio_details = {}

for fol in pilot_folios:
    ref_ms = ref[fol]["mean_state"]
    b6_ms = b6[fol]["mean_state"]
    ref_c = ref_ms[3]
    b6_c = b6_ms[3]
    ref_s = ref_ms[2]
    b6_s = b6_ms[2]
    ref_v = ref[fol]["viability_fraction"]
    b6_v = b6[fol]["viability_fraction"]

    c_better = ref_c > b6_c
    s_better = ref_s > b6_s
    if c_better:
        n_c_better += 1
    if s_better:
        n_s_better += 1

    p5a_folio_details[fol] = {
        "ref_C": round(ref_c, 4), "B6_C": round(b6_c, 4), "C_better": c_better,
        "ref_S": round(ref_s, 4), "B6_S": round(b6_s, 4), "S_better": s_better,
        "ref_viab": round(ref_v, 4), "B6_viab": round(b6_v, 4),
    }
    print(f"    {fol}: C ref={ref_c:.4f} B6={b6_c:.4f} ({'+' if c_better else '-'}), "
          f"S ref={ref_s:.4f} B6={b6_s:.4f} ({'+' if s_better else '-'})")

p5a_pass = n_c_better >= 14 or n_s_better >= 14
print(f"    P5a: C_better={n_c_better}/{len(pilot_folios)}, "
      f"S_better={n_s_better}/{len(pilot_folios)} -> {'PASS' if p5a_pass else 'FAIL'}")

# P5b: HL split — compare high-HL vs low-HL folios on mean C and S
print("\n  P5b: HL split (high vs low headless rate)")
sorted_fols = sorted(pilot_folios, key=lambda f: folio_hl_rates.get(f, 0.25))
median_idx = len(sorted_fols) // 2
median_hl = folio_hl_rates.get(sorted_fols[median_idx], 0.25)

low_hl_fols = sorted_fols[:median_idx]
high_hl_fols = sorted_fols[median_idx:]

print(f"    Low HL ({len(low_hl_fols)}): {low_hl_fols}")
print(f"    High HL ({len(high_hl_fols)}): {high_hl_fols}")

low_C = [ref[f]["mean_state"][3] for f in low_hl_fols]
high_C = [ref[f]["mean_state"][3] for f in high_hl_fols]
low_S = [ref[f]["mean_state"][2] for f in low_hl_fols]
high_S = [ref[f]["mean_state"][2] for f in high_hl_fols]

U_C, z_C, p_C = mann_whitney_u(low_C, high_C)
U_S, z_S, p_S = mann_whitney_u(low_S, high_S)

print(f"    C: low_mean={safe_mean(low_C):.4f}, high_mean={safe_mean(high_C):.4f}, "
      f"U={U_C:.0f}, z={z_C:.3f}, p={p_C:.4f}")
print(f"    S: low_mean={safe_mean(low_S):.4f}, high_mean={safe_mean(high_S):.4f}, "
      f"U={U_S:.0f}, z={z_S:.3f}, p={p_S:.4f}")

p5b_pass = p_C < 0.05 or p_S < 0.05
print(f"    P5b: C p={p_C:.4f}, S p={p_S:.4f} -> {'PASS' if p5b_pass else 'FAIL'}")

p5_pass = p5a_pass or p5b_pass
p5_details = {
    "P5a": {
        "n_C_better": n_c_better,
        "n_S_better": n_s_better,
        "per_folio": p5a_folio_details,
        "pass": p5a_pass,
    },
    "P5b": {
        "low_hl_folios": low_hl_fols,
        "high_hl_folios": high_hl_fols,
        "C_test": {"U": round(U_C, 1), "z": round(z_C, 3), "p": round(p_C, 4),
                   "low_mean": round(safe_mean(low_C), 4),
                   "high_mean": round(safe_mean(high_C), 4)},
        "S_test": {"U": round(U_S, 1), "z": round(z_S, 3), "p": round(p_S, 4),
                   "low_mean": round(safe_mean(low_S), 4),
                   "high_mean": round(safe_mean(high_S), 4)},
        "pass": p5b_pass,
    },
    "pass_criteria": f"P5a ({p5a_pass}) OR P5b ({p5b_pass})",
}
print(f"  P5 VERDICT: P5a={p5a_pass} OR P5b={p5b_pass} -> {'PASS' if p5_pass else 'FAIL'}")
results["P5_headless_regime"] = {"pass": p5_pass, "details": p5_details}


# ======================================================================
# P6: CTS Closure Value
# ======================================================================
print("\n" + "-" * 70)
print("P6: CTS Closure Value")
print("-" * 70)

b3 = baselines["B3_full_minus_cts"]

# P6a: Full vs B3 on viability/Y
n_viab_better = 0
n_y_better = 0
p6a_folio = {}

for fol in pilot_folios:
    full_v = ref[fol]["viability_fraction"]
    b3_v = b3[fol]["viability_fraction"]
    full_y = ref[fol]["Y_final"]
    b3_y = b3[fol]["Y_final"]

    v_better = full_v >= b3_v
    y_better = full_y >= b3_y
    if v_better:
        n_viab_better += 1
    if y_better:
        n_y_better += 1

    p6a_folio[fol] = {
        "full_viab": round(full_v, 4), "B3_viab": round(b3_v, 4), "viab_better": v_better,
        "full_Y": round(full_y, 4), "B3_Y": round(b3_y, 4), "Y_better": y_better,
    }
    print(f"  {fol}: viab full={full_v:.4f} B3={b3_v:.4f} ({'+' if v_better else '-'}), "
          f"Y full={full_y:.4f} B3={b3_y:.4f} ({'+' if y_better else '-'})")

# P6b: CLOSE vs WORK C-separation from trajectory
print("\n  P6b: CLOSE vs WORK C-separation:")
n_separation_positive = 0
p6b_folio = {}

for fol in pilot_folios:
    traj = preferred_runs[fol]["trajectory"]

    # Compute per-line mean state
    line_states = defaultdict(list)
    for tok in traj:
        line_states[tok["line"]].append(tok["state"])

    close_C = []
    work_C = []
    for line_key, states in line_states.items():
        lp_key = f"{fol}|{line_key}"
        packet = line_packets.get(lp_key, {})
        pp = packet.get("packet_state", {}).get("packet_phase", "WORK")

        mean_C = safe_mean([s[3] for s in states])
        if pp == "CLOSE":
            close_C.append(mean_C)
        elif pp == "WORK":
            work_C.append(mean_C)

    if close_C and work_C:
        sep = safe_mean(close_C) - safe_mean(work_C)
        if sep > 0:
            n_separation_positive += 1
        p6b_folio[fol] = {
            "mean_close_C": round(safe_mean(close_C), 4),
            "mean_work_C": round(safe_mean(work_C), 4),
            "C_separation": round(sep, 4),
            "n_close": len(close_C), "n_work": len(work_C),
        }
        print(f"    {fol}: CLOSE_C={safe_mean(close_C):.4f}, WORK_C={safe_mean(work_C):.4f}, "
              f"sep={sep:+.4f} ({len(close_C)} close, {len(work_C)} work)")
    else:
        p6b_folio[fol] = {"n_close": len(close_C), "n_work": len(work_C)}
        print(f"    {fol}: insufficient lines (close={len(close_C)}, work={len(work_C)})")

p6_pass = n_viab_better >= 14 and n_separation_positive >= 14
p6_details = {
    "P6a": {"n_viab_better": n_viab_better, "n_y_better": n_y_better, "per_folio": p6a_folio},
    "P6b": {"n_separation_positive": n_separation_positive, "per_folio": p6b_folio},
    "pass_criteria": (
        f"viab_better {n_viab_better}/{len(pilot_folios)}>=14 AND "
        f"sep_positive {n_separation_positive}/{len(pilot_folios)}>=14"
    ),
}
print(f"  VERDICT: viab_better={n_viab_better}/{len(pilot_folios)}, "
      f"sep_positive={n_separation_positive}/{len(pilot_folios)} -> "
      f"{'PASS' if p6_pass else 'FAIL'}")
results["P6_cts_closure"] = {"pass": p6_pass, "details": p6_details}


# ======================================================================
# P7: Null Destruction
# ======================================================================
print("\n" + "-" * 70)
print("P7: Null Destruction")
print("-" * 70)

NULL_NAMES = [
    "N1_token_shuffle", "N2_domain_preserve_shuffle",
    "N3_line_shuffle", "N4_within_line_shuffle",
]

p7_details = {"per_null": {}, "per_folio_per_null": {}}
n_null_pass = 0

for nname in NULL_NAMES:
    n_folio_pass = 0
    folio_results = {}

    for fol in pilot_folios:
        ndata = nulls[nname][fol]
        ref_v = ref[fol]["viability_fraction"]
        ref_y = ref[fol]["Y_final"]
        null_v_mean = ndata["viability_mean"]
        null_v_std = ndata["viability_std"]
        null_y_mean = ndata["Y_final_mean"]

        # Compute Y_final_std from per_perm
        y_vals = [p["Y_final"] for p in ndata["per_perm"]]
        null_y_std = safe_std(y_vals)

        # z-scores
        if null_v_std > 0.001:
            z_v = (ref_v - null_v_mean) / null_v_std
        elif abs(ref_v - null_v_mean) < 0.001:
            z_v = 0.0
        else:
            z_v = 10.0 if ref_v > null_v_mean else -10.0

        if null_y_std > 0.001:
            z_y = (ref_y - null_y_mean) / null_y_std
        elif abs(ref_y - null_y_mean) < 0.001:
            z_y = 0.0
        else:
            z_y = 10.0 if ref_y > null_y_mean else -10.0

        trivially_safe = (ref_v >= 0.999 and null_v_mean >= 0.999)
        pass_folio = (z_v > 2.0 or z_y > 2.0 or trivially_safe)

        if pass_folio:
            n_folio_pass += 1

        folio_results[fol] = {
            "ref_viab": round(ref_v, 4), "null_viab_mean": round(null_v_mean, 4),
            "null_viab_std": round(null_v_std, 4), "z_viab": round(z_v, 3),
            "ref_Y": round(ref_y, 4), "null_Y_mean": round(null_y_mean, 4),
            "null_Y_std": round(null_y_std, 4), "z_Y": round(z_y, 3),
            "trivially_safe": trivially_safe, "folio_pass": pass_folio,
        }

    null_pass = n_folio_pass >= 14
    if null_pass:
        n_null_pass += 1

    p7_details["per_null"][nname] = {"n_folio_pass": n_folio_pass, "null_pass": null_pass}
    p7_details["per_folio_per_null"][nname] = folio_results

    print(f"  {nname}: {n_folio_pass}/{len(pilot_folios)} folios pass -> "
          f"{'PASS' if null_pass else 'FAIL'}")
    for fol in pilot_folios:
        fr = folio_results[fol]
        print(f"    {fol}: z_v={fr['z_viab']:+.2f}, z_Y={fr['z_Y']:+.2f}, "
              f"trivial={fr['trivially_safe']}, pass={fr['folio_pass']}")

p7_pass = n_null_pass >= 3
p7_details["n_null_pass"] = n_null_pass
p7_details["pass_criteria"] = f"{n_null_pass}/4 >= 3 null types destroyed"
print(f"  VERDICT: {n_null_pass}/4 null types pass -> {'PASS' if p7_pass else 'FAIL'}")
results["P7_null_destruction"] = {"pass": p7_pass, "details": p7_details}


# ======================================================================
# P8: Preferred Profile Superiority
# ======================================================================
print("\n" + "-" * 70)
print("P8: Preferred Profile Superiority")
print("-" * 70)

PROFILES = ["A1_BATH_REFLUX", "A2_SEALED_RECIRCULATION", "A3_DISTILL_COLLECT"]
n_preferred_best = 0
p8_folio_details = {}

for fol in pilot_folios:
    cpsd = t3b_cps[fol]
    pref = cpsd["preferred_profile"]

    viab = cpsd["viability"]
    haz = cpsd["hazard_counts"]
    y_fin = cpsd["Y_final"]

    pref_viab = viab[pref]
    pref_haz = haz[pref]
    pref_y = y_fin[pref]

    best_viab = max(viab.values())
    min_haz = min(haz.values())
    best_y = max(y_fin.values())

    is_best_viab = pref_viab >= best_viab - 0.001
    is_min_haz = pref_haz <= min_haz
    is_best_y = pref_y >= best_y - 0.001

    is_best = is_best_viab or is_min_haz or is_best_y
    if is_best:
        n_preferred_best += 1

    p8_folio_details[fol] = {
        "preferred": pref,
        "viab": {p: round(v, 4) for p, v in viab.items()},
        "haz": haz,
        "Y_final": {p: round(v, 4) for p, v in y_fin.items()},
        "is_best_viab": is_best_viab,
        "is_min_haz": is_min_haz,
        "is_best_Y": is_best_y,
        "is_best_overall": is_best,
    }
    print(f"  {fol} (pref={pref}):")
    for p in PROFILES:
        marker = " <-PREF" if p == pref else ""
        print(f"    {p}: viab={viab[p]:.4f}, haz={haz[p]}, Y={y_fin[p]:.4f}{marker}")
    print(f"    -> best_viab={is_best_viab}, min_haz={is_min_haz}, best_Y={is_best_y}")

p8_pass = n_preferred_best >= 14
p8_details = {
    "n_preferred_best": n_preferred_best,
    "per_folio": p8_folio_details,
    "pass_criteria": f"preferred best on >=1 metric for {n_preferred_best}/{len(pilot_folios)} >= 14",
}
print(f"  VERDICT: {n_preferred_best}/{len(pilot_folios)} -> {'PASS' if p8_pass else 'FAIL'}")
results["P8_preferred_profile"] = {"pass": p8_pass, "details": p8_details}


# ======================================================================
# Final verdict
# ======================================================================
print("\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)

all_tests = [
    "P1_viable_envelope", "P2_packet_shape", "P3_section_template",
    "P3b_productive_diversity", "P4_routing_consequence",
    "P5_headless_regime", "P6_cts_closure",
    "P7_null_destruction", "P8_preferred_profile",
]

passed = [t for t in all_tests if results[t]["pass"]]
failed = [t for t in all_tests if not results[t]["pass"]]

for t in all_tests:
    status = "PASS" if results[t]["pass"] else "FAIL"
    secondary = " (SECONDARY)" if t == "P3_section_template" else ""
    print(f"  {t}: {status}{secondary}")

print(f"\n  Total: {len(passed)}/{len(all_tests)} passed")

# Core tests: P1 + P2 + P3b + P4 + P7 (P3 is secondary, not gating)
core_tests = [
    "P1_viable_envelope", "P2_packet_shape", "P3b_productive_diversity",
    "P4_routing_consequence", "P7_null_destruction",
]
core_passed = all(results[t]["pass"] for t in core_tests)

if core_passed:
    verdict = "PLANT_COUPLING_VALIDATED"
elif len(passed) >= 5:
    verdict = "PARTIAL_COUPLING"
else:
    verdict = "COUPLING_FAILED"

print(f"\n  Core tests (P1+P2+P3b+P4+P7): {'ALL PASS' if core_passed else 'NOT ALL PASS'}")
for ct in core_tests:
    print(f"    {ct}: {'PASS' if results[ct]['pass'] else 'FAIL'}")
print(f"\n  VERDICT: {verdict}")

elapsed = time.time() - t_start

# ======================================================================
# Write output
# ======================================================================
output = {
    "metadata": {
        "phase": "563b",
        "task": "T5b_plant_behavior_validation",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_pilot_folios": N_FOLIOS,
        "n_folios_with_data": len(pilot_folios),
        "pilot_folios": pilot_folios,
        "n_tests": len(all_tests),
        "elapsed_seconds": round(elapsed, 1),
    },
    "tests": results,
    "verdict": verdict,
    "summary": {
        "n_pass": len(passed),
        "n_fail": len(failed),
        "tests_passed": passed,
        "tests_failed": failed,
        "core_tests": core_tests,
        "core_all_pass": core_passed,
    },
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=1)

print(f"\n  Output: {OUT_PATH}")
print(f"  Elapsed: {elapsed:.1f}s")
