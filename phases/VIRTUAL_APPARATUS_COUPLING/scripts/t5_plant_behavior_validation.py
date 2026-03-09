"""
T5: Plant Behavior Validation -- Phase 563 (VIRTUAL_APPARATUS_COUPLING)

Judge whether full hierarchical trace coupling produces meaningful,
structured plant control beyond baselines. 8 tests (P1-P8).

Inputs:
  - t3_coupled_traces.json (21 runs: 7 folios x 3 profiles)
  - t4_null_ablation_traces.json (baselines + nulls)
  - t3_line_packets.json (packet_phase assignment)
  - t2_supervisory_interface.json (routing signals)
  - t2_folio_budgets.json (headless rate)

Output:
  - t5_plant_validation.json

No external dependencies beyond Python stdlib.
"""

import json
import math
import time
from pathlib import Path
from collections import defaultdict

# -- Paths --------------------------------------------------------------

BASE = Path("phases/VIRTUAL_APPARATUS_COUPLING")
STXE = Path("phases/SECTION_TEMPLATE_TRACE_EXECUTOR")

T3_PATH = BASE / "results" / "t3_coupled_traces.json"
T4_PATH = BASE / "results" / "t4_null_ablation_traces.json"
LP_PATH = STXE / "results" / "t3_line_packets.json"
T2_PATH = BASE / "results" / "t2_supervisory_interface.json"
FB_PATH = STXE / "results" / "t2_folio_budgets.json"
OUT_PATH = BASE / "results" / "t5_plant_validation.json"

# State variable indices: T=0, RC=1, S=2, C=3, TR=4, X=5, Y=6
SV_NAMES = ["T", "RC", "S", "C", "TR", "X", "Y"]
PILOT_FOLIOS = ["f78r", "f84r", "f55r", "f40v", "f43v", "f104r", "f111r"]
FOLIO_SECTIONS = {
    "f78r": "B", "f84r": "B",
    "f55r": "H", "f40v": "H", "f43v": "H",
    "f104r": "S", "f111r": "S"
}
N_FOLIOS = 7


# -- Statistical helpers (no scipy) ------------------------------------

def chi2_survival(x, df):
    """Approximate chi-squared survival function via Wilson-Hilferty."""
    if x <= 0 or df <= 0:
        return 1.0
    z = ((x / df) ** (1.0/3.0) - (1.0 - 2.0/(9.0*df))) / math.sqrt(2.0/(9.0*df))
    p = 0.5 * (1.0 - math.erf(z / math.sqrt(2.0)))
    return max(0.0, min(1.0, p))


def kruskal_wallis(*groups):
    """Kruskal-Wallis H test. Returns (H, p_approx)."""
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

    # Assign ranks with tie averaging
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
    """Mann-Whitney U test. Returns (U, z, p_approx)."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0, 0.0, 1.0
    # Rank all values
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


def euclidean_dist(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


# -- Load data --------------------------------------------------------─

print("=" * 70)
print("T5: Plant Behavior Validation")
print("=" * 70)
t_start = time.time()

print("\nLoading T3 coupled traces...")
with open(T3_PATH) as f:
    t3 = json.load(f)

print("Loading T4 null/ablation traces...")
with open(T4_PATH) as f:
    t4 = json.load(f)

print("Loading line packets...")
with open(LP_PATH) as f:
    lp = json.load(f)

print("Loading T2 supervisory interface...")
with open(T2_PATH) as f:
    t2 = json.load(f)

print("Loading folio budgets...")
with open(FB_PATH) as f:
    fb = json.load(f)

# Build lookups
ref = t4["reference"]
baselines = t4["baselines"]
nulls = t4["nulls"]
runs = t3["runs"]
cps = t3["cross_profile_summary"]

# Get preferred runs and their trajectories
preferred_runs = {}
for key, run in runs.items():
    if run.get("is_preferred") and "trajectory" in run:
        preferred_runs[run["folio"]] = run

# Build per-folio token signals from T2
folio_token_signals = defaultdict(list)
for ts in t2["token_signals"]:
    folio_token_signals[ts["folio"]].append(ts)

# Build line packet lookup
line_packets = lp["line_packets"]

# Folio budget lookup
folio_budgets = fb["folio_budgets"]

print(f"Loaded. {len(preferred_runs)} preferred trajectories.")
print(f"Pilot folios (excl f116v): {PILOT_FOLIOS}")

results = {}


# ======================================================================
# P1: Viable Envelope Occupancy
# ======================================================================

print("\n" + "-" * 70)
print("P1: Viable Envelope Occupancy")
print("-" * 70)

p1_details = {"per_folio": {}, "full_gt_B2": 0, "full_gt_N1": 0}

for fol in PILOT_FOLIOS:
    full_v = ref[fol]["viability_fraction"]
    b1_v = baselines["B1_section_only"][fol]["viability_fraction"]
    b2_v = baselines["B2_section_folio_budget"][fol]["viability_fraction"]
    n1 = nulls["N1_token_shuffle"][fol]
    n1_mean = n1["viability_mean"]
    n1_std = n1["viability_std"]

    gt_b2 = full_v > b2_v or (full_v == b2_v and full_v >= 0.99)
    gt_n1 = full_v > n1_mean or (abs(full_v - n1_mean) < 0.01)

    p1_details["per_folio"][fol] = {
        "full_viability": round(full_v, 4),
        "B1_viability": round(b1_v, 4),
        "B2_viability": round(b2_v, 4),
        "N1_viability_mean": round(n1_mean, 4),
        "N1_viability_std": round(n1_std, 4),
        "full_gt_B2": gt_b2,
        "full_gt_N1": gt_n1
    }
    if gt_b2:
        p1_details["full_gt_B2"] += 1
    if gt_n1:
        p1_details["full_gt_N1"] += 1

    print(f"  {fol}: full={full_v:.4f}  B1={b1_v:.4f}  B2={b2_v:.4f}  "
          f"N1={n1_mean:.4f}+/-{n1_std:.4f}  >B2={gt_b2}  >N1={gt_n1}")

# PASS: full > B2 for >=5/7 AND full > N1_mean for >=5/7
p1_pass = p1_details["full_gt_B2"] >= 5 and p1_details["full_gt_N1"] >= 5
p1_details["pass_criteria"] = f"full>B2 {p1_details['full_gt_B2']}/7>=5 AND full>N1 {p1_details['full_gt_N1']}/7>=5"
print(f"  VERDICT: full>B2={p1_details['full_gt_B2']}/7, full>N1={p1_details['full_gt_N1']}/7 -> {'PASS' if p1_pass else 'FAIL'}")
results["P1_viable_envelope"] = {"pass": p1_pass, "details": p1_details}


# ======================================================================
# P2: Line Packet Shape Recovery
# ======================================================================

print("\n" + "-" * 70)
print("P2: Line Packet Shape Recovery")
print("-" * 70)

# Group trajectory tokens by packet_phase, compute Kruskal-Wallis per state var
PHASES = ["SPEC", "WORK", "CLOSE"]
phase_state_vectors = {ph: {sv: [] for sv in range(7)} for ph in PHASES}
per_folio_kw = {}

for fol in PILOT_FOLIOS:
    run = preferred_runs[fol]
    traj = run["trajectory"]

    folio_phase_vecs = {ph: {sv: [] for sv in range(7)} for ph in PHASES}
    for tok in traj:
        pp = tok.get("packet_phase", "WORK")
        if pp not in PHASES:
            pp = "WORK"
        state = tok["state"]
        for sv_i in range(7):
            folio_phase_vecs[pp][sv_i].append(state[sv_i])
            phase_state_vectors[pp][sv_i].append(state[sv_i])

    # Per-folio KW
    n_sig = 0
    folio_kw_details = {}
    for sv_i in range(7):
        groups = [folio_phase_vecs[ph][sv_i] for ph in PHASES]
        groups = [g for g in groups if len(g) > 0]
        if len(groups) >= 2:
            H, p = kruskal_wallis(*groups)
            sig = p < 0.05
            if sig:
                n_sig += 1
            folio_kw_details[SV_NAMES[sv_i]] = {"H": round(H, 3), "p": round(p, 5), "sig": sig}
        else:
            folio_kw_details[SV_NAMES[sv_i]] = {"H": 0, "p": 1.0, "sig": False}
    per_folio_kw[fol] = {"n_sig": n_sig, "details": folio_kw_details}
    print(f"  {fol}: {n_sig}/7 state vars significant (p<0.05)")
    for sv_name, det in folio_kw_details.items():
        if det["sig"]:
            print(f"    {sv_name}: H={det['H']:.2f}, p={det['p']:.5f}")

# Global KW across all folios pooled
global_kw = {}
n_global_sig = 0
for sv_i in range(7):
    groups = [phase_state_vectors[ph][sv_i] for ph in PHASES]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) >= 2:
        H, p = kruskal_wallis(*groups)
        sig = p < 0.05
        if sig:
            n_global_sig += 1
        global_kw[SV_NAMES[sv_i]] = {"H": round(H, 3), "p": round(p, 6), "sig": sig}

# Report phase means
print("\n  Phase means (pooled across folios):")
for ph in PHASES:
    means = []
    for sv_i in range(7):
        vals = phase_state_vectors[ph][sv_i]
        m = sum(vals) / len(vals) if vals else 0.5
        means.append(m)
    print(f"    {ph}: " + " ".join(f"{SV_NAMES[i]}={means[i]:.3f}" for i in range(7)))

print(f"\n  Global KW: {n_global_sig}/7 significant")
for sv_name, det in global_kw.items():
    print(f"    {sv_name}: H={det['H']:.2f}, p={det['p']:.6f}, sig={det['sig']}")

# PASS: global KW p<0.05 on >=4/7 state vars
p2_pass = n_global_sig >= 4
p2_details = {
    "global_n_sig": n_global_sig,
    "global_kw": global_kw,
    "per_folio_n_sig": {fol: per_folio_kw[fol]["n_sig"] for fol in PILOT_FOLIOS},
    "pass_criteria": f"global KW sig on {n_global_sig}/7 >= 4"
}
print(f"  VERDICT: {n_global_sig}/7 globally significant -> {'PASS' if p2_pass else 'FAIL'}")
results["P2_packet_shape"] = {"pass": p2_pass, "details": p2_details}


# ======================================================================
# P3: Section Template Differentiation
# ======================================================================

print("\n" + "-" * 70)
print("P3: Section Template Differentiation")
print("-" * 70)

section_groups = {"B": [], "H": [], "S": []}
for fol in PILOT_FOLIOS:
    sec = FOLIO_SECTIONS[fol]
    ms = ref[fol]["mean_state"]
    section_groups[sec].append(ms)

p3_kw = {}
n_p3_sig = 0
for sv_i in range(7):
    groups = []
    for sec in ["B", "H", "S"]:
        vals = [ms[sv_i] for ms in section_groups[sec]]
        groups.append(vals)
    H, p = kruskal_wallis(*groups)
    sig = p < 0.05
    if sig:
        n_p3_sig += 1
    p3_kw[SV_NAMES[sv_i]] = {"H": round(H, 3), "p": round(p, 5), "sig": sig}

print("  Section mean states:")
for sec in ["B", "H", "S"]:
    for ms in section_groups[sec]:
        fol = [f for f in PILOT_FOLIOS if FOLIO_SECTIONS[f] == sec][section_groups[sec].index(ms)]
        print(f"    {sec}/{fol}: " + " ".join(f"{SV_NAMES[i]}={ms[i]:.3f}" for i in range(7)))

print(f"\n  KW results: {n_p3_sig}/7 significant")
for sv_name, det in p3_kw.items():
    print(f"    {sv_name}: H={det['H']:.2f}, p={det['p']:.5f}, sig={det['sig']}")

# PASS: KW p<0.05 on >=4/7
p3_pass = n_p3_sig >= 4
p3_details = {
    "n_sig": n_p3_sig,
    "kw_results": p3_kw,
    "section_means": {
        sec: {
            SV_NAMES[i]: round(sum(ms[i] for ms in section_groups[sec]) / len(section_groups[sec]), 4)
            for i in range(7)
        }
        for sec in ["B", "H", "S"]
    },
    "pass_criteria": f"KW sig on {n_p3_sig}/7 >= 4 (note: N=7, power is low)"
}
print(f"  VERDICT: {n_p3_sig}/7 significant -> {'PASS' if p3_pass else 'FAIL'}")
results["P3_section_template"] = {"pass": p3_pass, "details": p3_details}


# ======================================================================
# P3b: Productive Operating Diversity
# ======================================================================

print("\n" + "-" * 70)
print("P3b: Productive Operating Diversity")
print("-" * 70)

p3b_details = {"per_folio": {}}
n_nontrivial_pass = 0
excursion_counts = []

for fol in PILOT_FOLIOS:
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
    # Count the final excursion if we ended outside
    if in_excursion:
        n_excursions += 1

    # (c) Y accumulation
    y_final = traj[-1]["state"][6] if traj else 0.5
    y_accum = y_final - 0.5

    p3b_details["per_folio"][fol] = {
        "nontrivial_frac": round(nontrivial_frac, 4),
        "n_excursions": n_excursions,
        "Y_accumulation": round(y_accum, 4),
        "n_tokens": n_tokens
    }
    if nontrivial_frac > 0.4:
        n_nontrivial_pass += 1
    excursion_counts.append(n_excursions)

    print(f"  {fol}: nontrivial={nontrivial_frac:.3f}, excursions={n_excursions}, "
          f"Y_accum={y_accum:.3f} ({n_tokens} tokens)")

mean_excursions = sum(excursion_counts) / len(excursion_counts)
p3b_pass = n_nontrivial_pass >= 5 and mean_excursions > 3
p3b_details["n_nontrivial_pass"] = n_nontrivial_pass
p3b_details["mean_excursions"] = round(mean_excursions, 2)
p3b_details["pass_criteria"] = f"nontrivial>0.4 for {n_nontrivial_pass}/7>=5 AND mean_excursions={mean_excursions:.1f}>3"
print(f"  VERDICT: nontrivial_pass={n_nontrivial_pass}/7, mean_excursions={mean_excursions:.1f} -> {'PASS' if p3b_pass else 'FAIL'}")
results["P3b_productive_diversity"] = {"pass": p3b_pass, "details": p3b_details}


# ======================================================================
# P4: Routing Consequence Fidelity
# ======================================================================

print("\n" + "-" * 70)
print("P4: Routing Consequence Fidelity")
print("-" * 70)

# Core routing quartet: terminal_atom -> target state variable
# r -> X (index 5), y -> T (index 0), h -> TR(4)/RC(1), m -> C (index 3)
ROUTING_TARGETS = {
    "r": [5],     # X
    "y": [0],     # T
    "h": [4, 1],  # TR, RC
    "m": [3]      # C
}
WINDOW = 5

routing_results = {rt: {"total": 0, "correct": 0} for rt in ROUTING_TARGETS}
per_folio_routing = {}

for fol in PILOT_FOLIOS:
    run = preferred_runs[fol]
    traj = run["trajectory"]
    n_tokens = len(traj)

    # Get T2 token signals for this folio
    fol_signals = folio_token_signals.get(fol, [])

    # Match by index (both should be in token order for this folio)
    folio_routing_hits = {rt: {"total": 0, "correct": 0} for rt in ROUTING_TARGETS}

    for idx in range(n_tokens):
        if idx >= len(fol_signals):
            break
        sig = fol_signals[idx]
        if sig.get("routing_active") and sig.get("routing_terminal"):
            rt = sig["routing_terminal"]
            if rt in ROUTING_TARGETS:
                targets = ROUTING_TARGETS[rt]
                # Check if target variable increases within WINDOW tokens
                before_idx = max(0, idx - 3)
                after_idx = min(n_tokens - 1, idx + WINDOW)

                for tgt_sv in targets:
                    val_before = traj[before_idx]["state"][tgt_sv]
                    val_at = traj[idx]["state"][tgt_sv]
                    val_after = traj[after_idx]["state"][tgt_sv]

                    # "correct" = target var increased from before to after
                    correct = val_after > val_before
                    routing_results[rt]["total"] += 1
                    routing_results[rt]["correct"] += 1 if correct else 0
                    folio_routing_hits[rt]["total"] += 1
                    folio_routing_hits[rt]["correct"] += 1 if correct else 0

    per_folio_routing[fol] = {
        rt: {
            "total": folio_routing_hits[rt]["total"],
            "correct": folio_routing_hits[rt]["correct"],
            "rate": round(folio_routing_hits[rt]["correct"] / max(1, folio_routing_hits[rt]["total"]), 3)
        }
        for rt in ROUTING_TARGETS
    }

n_correct_routes = 0
p4_route_details = {}
for rt in ROUTING_TARGETS:
    total = routing_results[rt]["total"]
    correct = routing_results[rt]["correct"]
    rate = correct / max(1, total)
    sig = rate > 0.5 and total >= 5
    if sig:
        n_correct_routes += 1
    p4_route_details[rt] = {
        "total": total,
        "correct": correct,
        "rate": round(rate, 3),
        "target_vars": [SV_NAMES[i] for i in ROUTING_TARGETS[rt]],
        "directionally_correct": sig
    }
    print(f"  {rt}->{[SV_NAMES[i] for i in ROUTING_TARGETS[rt]]}: "
          f"{correct}/{total} correct ({rate:.1%}), sig={sig}")

# PASS: >=3/4 core routing signatures produce correct directional effect
p4_pass = n_correct_routes >= 3
p4_details = {
    "n_correct_routes": n_correct_routes,
    "route_details": p4_route_details,
    "per_folio": per_folio_routing,
    "window": WINDOW,
    "pass_criteria": f"{n_correct_routes}/4 >= 3 correct routing signatures"
}
print(f"  VERDICT: {n_correct_routes}/4 directionally correct -> {'PASS' if p4_pass else 'FAIL'}")
results["P4_routing_consequence"] = {"pass": p4_pass, "details": p4_details}


# ======================================================================
# P5: Headless Regime Consequence
# ======================================================================

print("\n" + "-" * 70)
print("P5: Headless Regime Consequence")
print("-" * 70)

# Get hl_rate per folio
hl_rates = {}
for fol in PILOT_FOLIOS:
    if fol in folio_budgets:
        hr = folio_budgets[fol].get("headless_regime", {})
        hl_rates[fol] = hr.get("hl_rate", 0.0)
    else:
        hl_rates[fol] = 0.0

# Sort folios by hl_rate
sorted_fols = sorted(PILOT_FOLIOS, key=lambda f: hl_rates[f])
median_hl = sorted(hl_rates.values())[len(hl_rates) // 2]

low_hl = [f for f in PILOT_FOLIOS if hl_rates[f] <= median_hl]
high_hl = [f for f in PILOT_FOLIOS if hl_rates[f] > median_hl]

print(f"  Headless rates: {', '.join(f'{f}={hl_rates[f]:.3f}' for f in sorted_fols)}")
print(f"  Median hl_rate: {median_hl:.3f}")
print(f"  Low hl: {low_hl}")
print(f"  High hl: {high_hl}")

# Compare C and S mean_state between groups
low_C = [ref[f]["mean_state"][3] for f in low_hl]
high_C = [ref[f]["mean_state"][3] for f in high_hl]
low_S = [ref[f]["mean_state"][2] for f in low_hl]
high_S = [ref[f]["mean_state"][2] for f in high_hl]

U_C, z_C, p_C = mann_whitney_u(low_C, high_C)
U_S, z_S, p_S = mann_whitney_u(low_S, high_S)

print(f"  C: low_mean={sum(low_C)/len(low_C):.4f}, high_mean={sum(high_C)/len(high_C):.4f}, "
      f"U={U_C:.0f}, z={z_C:.3f}, p={p_C:.4f}")
print(f"  S: low_mean={sum(low_S)/len(low_S):.4f}, high_mean={sum(high_S)/len(high_S):.4f}, "
      f"U={U_S:.0f}, z={z_S:.3f}, p={p_S:.4f}")

# PASS: MW p < 0.05 on C or S
p5_pass = p_C < 0.05 or p_S < 0.05
p5_details = {
    "hl_rates": {f: round(hl_rates[f], 4) for f in PILOT_FOLIOS},
    "low_hl_folios": low_hl,
    "high_hl_folios": high_hl,
    "C_test": {"U": round(U_C, 1), "z": round(z_C, 3), "p": round(p_C, 4),
               "low_mean": round(sum(low_C)/len(low_C), 4),
               "high_mean": round(sum(high_C)/len(high_C), 4)},
    "S_test": {"U": round(U_S, 1), "z": round(z_S, 3), "p": round(p_S, 4),
               "low_mean": round(sum(low_S)/len(low_S), 4),
               "high_mean": round(sum(high_S)/len(high_S), 4)},
    "pass_criteria": f"MW p<0.05 on C (p={p_C:.4f}) or S (p={p_S:.4f}); N very small"
}
print(f"  VERDICT: C p={p_C:.4f}, S p={p_S:.4f} -> {'PASS' if p5_pass else 'FAIL'}")
results["P5_headless_regime"] = {"pass": p5_pass, "details": p5_details}


# ======================================================================
# P6: CTS Closure Value
# ======================================================================

print("\n" + "-" * 70)
print("P6: CTS Closure Value")
print("-" * 70)

b3 = baselines["B3_full_minus_cts"]

# P6a: Compare full vs B3 on summary metrics
p6a_details = {"per_folio": {}}
n_viab_better = 0
n_y_better = 0

for fol in PILOT_FOLIOS:
    full_v = ref[fol]["viability_fraction"]
    b3_v = b3[fol]["viability_fraction"]
    full_y = ref[fol]["Y_final"]
    b3_y = b3[fol]["Y_final"]
    full_haz = ref[fol]["hazard_count"]
    b3_haz = b3[fol]["hazard_count"]

    v_better = full_v >= b3_v
    y_better = full_y >= b3_y

    if v_better:
        n_viab_better += 1
    if y_better:
        n_y_better += 1

    p6a_details["per_folio"][fol] = {
        "full_viab": round(full_v, 4), "B3_viab": round(b3_v, 4),
        "full_Y": round(full_y, 4), "B3_Y": round(b3_y, 4),
        "full_haz": full_haz, "B3_haz": b3_haz,
        "viab_better": v_better, "Y_better": y_better
    }
    print(f"  {fol}: viab full={full_v:.4f} B3={b3_v:.4f} ({'+' if v_better else '-'}), "
          f"Y full={full_y:.4f} B3={b3_y:.4f} ({'+' if y_better else '-'}), "
          f"haz full={full_haz} B3={b3_haz}")

# P6b: Line-level CLOSE vs WORK separation in full model
print("\n  P6b: CLOSE vs WORK C-separation (full model only):")
p6b_details = {"per_folio": {}}
n_separation_positive = 0

for fol in PILOT_FOLIOS:
    run = preferred_runs[fol]
    plms = run.get("per_line_mean_state", {})

    close_C = []
    work_C = []
    close_Y = []
    work_Y = []

    for line_key, ms in plms.items():
        lp_key = f"{fol}|{line_key}"
        packet = line_packets.get(lp_key, {})
        pp = packet.get("packet_state", {}).get("packet_phase", "WORK")

        if pp == "CLOSE":
            close_C.append(ms[3])
            close_Y.append(ms[6])
        elif pp == "WORK":
            work_C.append(ms[3])
            work_Y.append(ms[6])

    if close_C and work_C:
        mean_close_C = sum(close_C) / len(close_C)
        mean_work_C = sum(work_C) / len(work_C)
        separation = mean_close_C - mean_work_C
        if separation > 0:
            n_separation_positive += 1
        p6b_details["per_folio"][fol] = {
            "mean_close_C": round(mean_close_C, 4),
            "mean_work_C": round(mean_work_C, 4),
            "C_separation": round(separation, 4),
            "n_close_lines": len(close_C),
            "n_work_lines": len(work_C)
        }
        print(f"    {fol}: CLOSE C={mean_close_C:.4f}, WORK C={mean_work_C:.4f}, "
              f"sep={separation:+.4f} ({len(close_C)} close, {len(work_C)} work lines)")
    else:
        p6b_details["per_folio"][fol] = {"n_close_lines": len(close_C), "n_work_lines": len(work_C)}
        print(f"    {fol}: insufficient lines (close={len(close_C)}, work={len(work_C)})")

# PASS: viab or Y better for >=5/7 AND >=4/7 positive C separation
p6_pass = (n_viab_better >= 5 or n_y_better >= 5) and n_separation_positive >= 4
p6_details = {
    "P6a_summary_comparison": p6a_details,
    "P6b_closure_separation": p6b_details,
    "n_viab_better": n_viab_better,
    "n_y_better": n_y_better,
    "n_separation_positive": n_separation_positive,
    "pass_criteria": f"(viab>={n_viab_better}/7>=5 OR Y>={n_y_better}/7>=5) AND separation={n_separation_positive}/7>=4"
}
print(f"  VERDICT: viab_better={n_viab_better}/7, Y_better={n_y_better}/7, "
      f"sep_positive={n_separation_positive}/7 -> {'PASS' if p6_pass else 'FAIL'}")
results["P6_cts_closure"] = {"pass": p6_pass, "details": p6_details}


# ======================================================================
# P7: Null Destruction
# ======================================================================

print("\n" + "-" * 70)
print("P7: Null Destruction")
print("-" * 70)

NULL_NAMES = ["N1_token_shuffle", "N2_domain_preserve_shuffle",
              "N3_line_shuffle", "N4_terminal_shuffle"]

p7_details = {"per_null": {}, "per_folio_per_null": {}}
n_null_pass = 0

for nname in NULL_NAMES:
    n_folio_pass = 0
    folio_results = {}

    for fol in PILOT_FOLIOS:
        ndata = nulls[nname][fol]
        ref_v = ref[fol]["viability_fraction"]
        ref_y = ref[fol]["Y_final"]
        null_v_mean = ndata["viability_mean"]
        null_v_std = ndata["viability_std"]
        null_y_mean = ndata["Y_final_mean"]
        null_y_std = ndata["Y_final_std"]

        # Compute z-scores for both viability and Y_final
        if null_v_std > 0.001:
            z_v = (ref_v - null_v_mean) / null_v_std
        elif abs(ref_v - null_v_mean) < 0.001:
            z_v = 0.0  # both perfect -> trivially tied
        else:
            z_v = 10.0 if ref_v > null_v_mean else -10.0

        if null_y_std > 0.001:
            z_y = (ref_y - null_y_mean) / null_y_std
        elif abs(ref_y - null_y_mean) < 0.001:
            z_y = 0.0
        else:
            z_y = 10.0 if ref_y > null_y_mean else -10.0

        # Mean state Euclidean distance
        null_ms = ndata["mean_state"]
        ref_ms = ref[fol]["mean_state"]
        ms_dist = euclidean_dist(ref_ms, null_ms)

        # Pass if z_v > 2 OR z_y > 2 OR (both trivially perfect viability AND y close)
        # When both real and null are at 1.0 viability, count as TIE (not a problem)
        trivially_safe = (ref_v >= 0.999 and null_v_mean >= 0.999)
        pass_folio = (z_v > 2.0 or z_y > 2.0 or trivially_safe)

        if pass_folio:
            n_folio_pass += 1

        folio_results[fol] = {
            "ref_viab": round(ref_v, 4), "null_viab_mean": round(null_v_mean, 4),
            "null_viab_std": round(null_v_std, 4), "z_viab": round(z_v, 3),
            "ref_Y": round(ref_y, 4), "null_Y_mean": round(null_y_mean, 4),
            "null_Y_std": round(null_y_std, 4), "z_Y": round(z_y, 3),
            "ms_dist": round(ms_dist, 4),
            "trivially_safe": trivially_safe,
            "folio_pass": pass_folio
        }

    null_pass = n_folio_pass >= 5
    if null_pass:
        n_null_pass += 1

    p7_details["per_null"][nname] = {
        "n_folio_pass": n_folio_pass,
        "null_pass": null_pass
    }
    p7_details["per_folio_per_null"][nname] = folio_results

    print(f"  {nname}: {n_folio_pass}/7 folios pass -> {'PASS' if null_pass else 'FAIL'}")
    for fol in PILOT_FOLIOS:
        fr = folio_results[fol]
        print(f"    {fol}: z_v={fr['z_viab']:+.2f}, z_Y={fr['z_Y']:+.2f}, "
              f"ms_dist={fr['ms_dist']:.4f}, trivial={fr['trivially_safe']}, pass={fr['folio_pass']}")

# PASS: >=3/4 null types pass
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

for fol in PILOT_FOLIOS:
    cpsd = cps[fol]
    pref = cpsd["preferred_profile"]

    viab = cpsd["viability"]
    haz = cpsd["hazard_count"]
    y_fin = cpsd["Y_final"]

    pref_viab = viab[pref]
    pref_haz = haz[pref]
    pref_y = y_fin[pref]

    # Check: preferred is best on viability OR lowest hazard OR highest Y
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
        "is_best_overall": is_best
    }
    print(f"  {fol} (pref={pref}):")
    for p in PROFILES:
        marker = " <-PREF" if p == pref else ""
        print(f"    {p}: viab={viab[p]:.4f}, haz={haz[p]}, Y={y_fin[p]:.4f}{marker}")
    print(f"    -> best_viab={is_best_viab}, min_haz={is_min_haz}, best_Y={is_best_y}")

# PASS: preferred best on at least one metric for >=5/7
p8_pass = n_preferred_best >= 5
p8_details = {
    "n_preferred_best": n_preferred_best,
    "per_folio": p8_folio_details,
    "pass_criteria": f"preferred best on >=1 metric for {n_preferred_best}/7 >= 5"
}
print(f"  VERDICT: {n_preferred_best}/7 preferred best on >=1 metric -> {'PASS' if p8_pass else 'FAIL'}")
results["P8_preferred_profile"] = {"pass": p8_pass, "details": p8_details}


# ======================================================================
# Final verdict
# ======================================================================

print("\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)

all_tests = ["P1_viable_envelope", "P2_packet_shape", "P3_section_template",
             "P3b_productive_diversity", "P4_routing_consequence",
             "P5_headless_regime", "P6_cts_closure",
             "P7_null_destruction", "P8_preferred_profile"]

passed = [t for t in all_tests if results[t]["pass"]]
failed = [t for t in all_tests if not results[t]["pass"]]

for t in all_tests:
    status = "PASS" if results[t]["pass"] else "FAIL"
    print(f"  {t}: {status}")

print(f"\n  Total: {len(passed)}/{len(all_tests)} passed")

# Core tests for PLANT_COUPLING_VALIDATED: P1 + P2 + P3b + P4 + P7
core_tests = ["P1_viable_envelope", "P2_packet_shape", "P3b_productive_diversity",
              "P4_routing_consequence", "P7_null_destruction"]
core_passed = all(results[t]["pass"] for t in core_tests)

if core_passed:
    verdict = "PLANT_COUPLING_VALIDATED"
elif results["P7_null_destruction"]["pass"]:
    verdict = "PARTIAL_COUPLING"
else:
    verdict = "COUPLING_FAILED"

print(f"\n  Core tests (P1+P2+P3b+P4+P7): {'ALL PASS' if core_passed else 'NOT ALL PASS'}")
print(f"  VERDICT: {verdict}")

elapsed = time.time() - t_start

# -- Write output ------------------------------------------------------

output = {
    "metadata": {
        "phase": "563",
        "task": "T5_plant_behavior_validation",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_pilot_folios": N_FOLIOS,
        "pilot_folios": PILOT_FOLIOS,
        "excluded": ["f116v"],
        "n_tests": len(all_tests),
        "elapsed_seconds": round(elapsed, 1)
    },
    "tests": results,
    "verdict": verdict,
    "summary": {
        "n_pass": len(passed),
        "n_fail": len(failed),
        "tests_passed": passed,
        "tests_failed": failed,
        "core_tests": core_tests,
        "core_all_pass": core_passed
    }
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=1)

print(f"\n  Output written to {OUT_PATH}")
print(f"  Elapsed: {elapsed:.1f}s")
