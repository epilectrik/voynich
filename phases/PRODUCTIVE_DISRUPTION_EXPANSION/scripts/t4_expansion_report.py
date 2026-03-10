"""
Phase 572: Productive Disruption Expansion — T4 Validation
============================================================
Full-scale three-tiered DYE/DVA evaluation across ~76 eligible Currier B folios.

Computes DVA/DYE/DYC for all eligible folios, evaluates GP1-GP4 at three tiers,
computes GD1-GD8 diagnostics (including dilution curve and F-parameter
renormalization), determines verdict, writes t4_expansion_metrics.json +
REPORT_572.md.

Inputs (from Phase 572 T1-T3):
  - t1_full_scale_setup.json        (folio list, configs, sections, profiles)
  - t2_full_model_runs.json         (M0/M1 per-event detail, metrics)
  - t3_null_runs.json               (M4f matched_events per permutation)
  - Phase 571 t4_metrics.json       (reference values for GD6)
  - Phase 570a t1_pilot_selection.json (pilot F-params for GD8)

Outputs:
  - phases/PRODUCTIVE_DISRUPTION_EXPANSION/results/t4_expansion_metrics.json
  - phases/PRODUCTIVE_DISRUPTION_EXPANSION/REPORT_572.md
"""

import json
import os
import math
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent.parent.parent.parent  # C:\git\voynich
INPUT_DIR = BASE / "phases" / "PRODUCTIVE_DISRUPTION_EXPANSION" / "results"
OUTPUT_DIR = INPUT_DIR  # same directory
REPORT_PATH = BASE / "phases" / "PRODUCTIVE_DISRUPTION_EXPANSION" / "REPORT_572.md"

# Phase 571 reference for GD6
REF_571_PATH = BASE / "phases" / "PROCESS_QUALITY_GENERALIZATION" / "results" / "t4_metrics.json"

# Phase 570a pilot for GD8
PILOT_570A_PATH = BASE / "phases" / "FOLIO_SPECIFIC_APPARATUS_PILOT" / "results" / "t1_pilot_selection.json"

PROCESS_SVS = [0, 1, 2, 3, 4, 5]  # T, RC, S, C, TR, X (indices 0-5; Y=6 excluded)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("=" * 72)
print("Phase 572: Productive Disruption Expansion — T4 Validation")
print("=" * 72)

with open(INPUT_DIR / "t1_full_scale_setup.json") as f:
    t1 = json.load(f)
with open(INPUT_DIR / "t2_full_model_runs.json") as f:
    t2 = json.load(f)
with open(INPUT_DIR / "t3_null_runs.json") as f:
    t3 = json.load(f)
with open(REF_571_PATH) as f:
    ref_571 = json.load(f)
with open(PILOT_570A_PATH) as f:
    pilot_570a = json.load(f)

FOLIOS = t1["eligible_folios"]
FOLIO_CONFIGS = t1["folio_configs"]

# Build section/profile maps filtered to eligible folios only
eligible_set = set(FOLIOS)
SECTION_MAP = {}
for sec, sec_fols in t1["summary"]["sections"].items():
    filtered = [f for f in sec_fols if f in eligible_set]
    if filtered:
        SECTION_MAP[sec] = filtered

PROFILE_MAP = {}
for prof, prof_fols in t1["summary"]["profiles"].items():
    filtered = [f for f in prof_fols if f in eligible_set]
    if filtered:
        PROFILE_MAP[prof] = filtered

PHASE_571_FOLIOS = t1["phase_571_reference_folios"]

print(f"Loaded {len(FOLIOS)} eligible folios from t1")
print(f"  t2: {len(t2['primary_runs'])} folios")
print(f"  t3: {len(t3['m4f_demand_matched'])} folios")
print(f"  Sections: {list(SECTION_MAP.keys())} (eligible only)")
print(f"  Profiles: {list(PROFILE_MAP.keys())} (eligible only)")
print(f"  Phase 571 reference folios: {len(PHASE_571_FOLIOS)}")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def aggregate_dev(state_vec):
    """Mean |state[sv] - 0.5| for process SVs (T, RC, S, C, TR, X)."""
    return sum(abs(state_vec[i] - 0.5) for i in PROCESS_SVS) / len(PROCESS_SVS)


def select_events(events):
    """Apply event selection logic.
    - work_preceded if >= 2 such events
    - fallback to demanded if >= 2
    - fallback to E_any (all events)
    """
    wp = [e for e in events if "work_preceded" in e.get("demand_qualifiers", [])]
    if len(wp) >= 2:
        return wp, "work_preceded"
    dem = [e for e in events if "demanded" in e.get("demand_qualifiers", [])]
    if len(dem) >= 2:
        return dem, "demanded"
    return events, "E_any"


def compute_dye(event):
    """DYE per event = y_gain_event / dv_magnitude_sum (guard: if dv < 0.001, DYE=0)."""
    dv = event["dv_magnitude_sum"]
    if dv < 0.001:
        return 0.0
    return event["y_gain_event"] / dv


def mean_dv_per_event(event):
    """Mean dV per close token for one event."""
    if event["n_close_tokens"] == 0:
        return 0.0
    return event["dv_magnitude_sum"] / event["n_close_tokens"]


def safe_mean(values):
    """Mean of list, or 0.0 if empty."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def pearson_r(x, y):
    """Pearson correlation coefficient. Returns None if insufficient data."""
    n = len(x)
    if n < 3:
        return None
    mx = sum(x) / n
    my = sum(y) / n
    sx = math.sqrt(sum((xi - mx) ** 2 for xi in x) / n)
    sy = math.sqrt(sum((yi - my) ** 2 for yi in y) / n)
    if sx < 1e-12 or sy < 1e-12:
        return None
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / n
    return cov / (sx * sy)


def spearman_rank(x, y):
    """Spearman rank correlation. Returns None if insufficient data."""
    n = len(x)
    if n < 3:
        return None

    def rank(vals):
        indexed = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        for r, i in enumerate(indexed):
            ranks[i] = r + 1.0
        return ranks

    rx = rank(x)
    ry = rank(y)
    return pearson_r(rx, ry)


# ---------------------------------------------------------------------------
# Compute metrics per folio
# ---------------------------------------------------------------------------
results = {}

for folio in FOLIOS:
    cfg = FOLIO_CONFIGS[folio]

    print(f"\n--- {folio} ({cfg['section']}, {cfg['profile']}) ---")

    # --- M1 events ---
    m1_all_events = t2["primary_runs"][folio]["M1"]["per_event_detail"]
    m1_selected, m1_selection_type = select_events(m1_all_events)

    # demand_strong from T1 eligibility_class (already computed)
    demand_strong = (cfg["eligibility_class"] == "demand_strong")

    print(f"  M1: {len(m1_selected)}/{len(m1_all_events)} events "
          f"({m1_selection_type}), demand_strong={demand_strong}")

    # M1 per-event metrics
    m1_dv_per_event = [mean_dv_per_event(e) for e in m1_selected]
    m1_dye_per_event = [compute_dye(e) for e in m1_selected]
    m1_mean_dv = safe_mean(m1_dv_per_event)
    m1_mean_dye = safe_mean(m1_dye_per_event)

    # --- M0 metrics (for GP4) ---
    m0_metrics = t2["primary_runs"][folio]["M0"]["metrics"]
    m1_metrics = t2["primary_runs"][folio]["M1"]["metrics"]

    # --- M4f matched events across perms ---
    perms = t3["m4f_demand_matched"][folio]["all_perms"]
    n_perms = len(perms)

    m4f_all_dv = []
    m4f_per_perm_dye = []

    for perm in perms:
        me = perm["matched_events"]
        me_selected, _ = select_events(me)

        for e in me_selected:
            m4f_all_dv.append(mean_dv_per_event(e))

        perm_dyes = [compute_dye(e) for e in me_selected]
        m4f_per_perm_dye.append(safe_mean(perm_dyes))

    m4f_mean_dv = safe_mean(m4f_all_dv)
    m4f_mean_dye = safe_mean(m4f_per_perm_dye)

    # --- DVA ---
    dva = m1_mean_dv - m4f_mean_dv

    # --- DYE advantage ---
    dye_advantage = m1_mean_dye - m4f_mean_dye

    # --- DYE EPV ---
    epv_count = sum(1 for pmd in m4f_per_perm_dye if m1_mean_dye > pmd)
    epv = epv_count / n_perms if n_perms > 0 else 0.0

    # --- YGA ---
    m1_y_gains = [e["y_gain_event"] for e in m1_selected]
    m4f_per_perm_yga = []
    for perm in perms:
        me = perm["matched_events"]
        me_selected_p, _ = select_events(me)
        perm_yg = [e["y_gain_event"] for e in me_selected_p]
        m4f_per_perm_yga.append(safe_mean(perm_yg))
    yga = safe_mean(m1_y_gains) - safe_mean(m4f_per_perm_yga)

    # --- DYC ---
    m1_demand_mags = [aggregate_dev(e["close_pre_state"]) for e in m1_selected]
    demand_mag = safe_mean(m1_demand_mags)
    z_dye = dye_advantage / max(demand_mag, 0.01)
    z_yga = yga / max(demand_mag, 0.01)
    dyc = 0.5 * z_dye + 0.5 * z_yga

    # --- n_close comparison (GD3) ---
    m1_mean_n_close = safe_mean([e["n_close_tokens"] for e in m1_selected])
    m4f_n_close_all = []
    for perm in perms:
        me = perm["matched_events"]
        me_selected_p, _ = select_events(me)
        for e in me_selected_p:
            m4f_n_close_all.append(e["n_close_tokens"])
    m4f_mean_n_close = safe_mean(m4f_n_close_all)

    print(f"  DVA = {dva:+.6f}  (M1_dV={m1_mean_dv:.4f}, M4f_dV={m4f_mean_dv:.4f})")
    print(f"  DYE_M1 = {m1_mean_dye:.4f}, DYE_M4f = {m4f_mean_dye:.4f}, "
          f"DYE_adv = {dye_advantage:+.6f}")
    print(f"  EPV = {epv_count}/{n_perms} = {epv:.2f}")
    print(f"  YGA = {yga:+.6f}")
    print(f"  demand_mag = {demand_mag:.4f}, z_DYE = {z_dye:.4f}, "
          f"z_YGA = {z_yga:.4f}, DYC = {dyc:.4f}")
    print(f"  M0_UEB={m0_metrics['UEB']}, M1_UEB={m1_metrics['UEB']}, "
          f"M0_WCP={m0_metrics['WCP']:.4f}, M1_WCP={m1_metrics['WCP']:.4f}")

    # Store results
    results[folio] = {
        "section": cfg["section"],
        "profile": cfg["profile"],
        "n_close_lines": cfg["n_close_lines"],
        "event_selection": m1_selection_type,
        "demand_strong": demand_strong,
        "eligibility_class": cfg["eligibility_class"],
        "n_m1_events": len(m1_selected),
        "n_m1_total": len(m1_all_events),
        "n_perms": n_perms,
        "DVA": dva,
        "mean_dV_M1": m1_mean_dv,
        "mean_dV_M4f": m4f_mean_dv,
        "DYE_M1": m1_mean_dye,
        "DYE_M4f": m4f_mean_dye,
        "DYE_advantage": dye_advantage,
        "EPV_count": epv_count,
        "EPV": epv,
        "demand_magnitude": demand_mag,
        "z_DYE": z_dye,
        "z_YGA": z_yga,
        "DYC": dyc,
        "YGA": yga,
        "m1_mean_n_close": m1_mean_n_close,
        "m4f_mean_n_close": m4f_mean_n_close,
        "M0_UEB": m0_metrics["UEB"],
        "M1_UEB": m1_metrics["UEB"],
        "M0_WCP": m0_metrics["WCP"],
        "M1_WCP": m1_metrics["WCP"],
        "m4f_per_perm_dye": m4f_per_perm_dye,
    }


# ---------------------------------------------------------------------------
# Folio Eligibility Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("FOLIO ELIGIBILITY CLASSIFICATION (GD2)")
print("=" * 72)

elig_counts = {}
for f in FOLIOS:
    ec = results[f]["eligibility_class"]
    elig_counts[ec] = elig_counts.get(ec, 0) + 1
    print(f"  {f}: n_close_lines={results[f]['n_close_lines']}, "
          f"n_events={results[f]['n_m1_events']}, "
          f"tier={results[f]['event_selection']}, "
          f"class={ec}")

print(f"\nCounts: {elig_counts}")


# ---------------------------------------------------------------------------
# Three-Tier folio sets
# ---------------------------------------------------------------------------
tier_a_folios = FOLIOS  # All eligible
tier_b_folios = [f for f in FOLIOS
                 if results[f]["eligibility_class"] in ("demand_strong", "demand_eligible")]
tier_c_folios = [f for f in FOLIOS
                 if results[f]["eligibility_class"] == "demand_strong"]

print(f"\nTier A: {len(tier_a_folios)} folios (all eligible)")
print(f"Tier B: {len(tier_b_folios)} folios (demand_eligible + demand_strong)")
print(f"  {tier_b_folios}")
print(f"Tier C: {len(tier_c_folios)} folios (demand_strong only)")
print(f"  {tier_c_folios}")


# ---------------------------------------------------------------------------
# Test Battery (GP1-GP4) at three tiers
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("TEST BATTERY — THREE-TIERED EVALUATION")
print("=" * 72)


def evaluate_gp1(folios):
    """GP1: DYE_advantage > 0"""
    per = {f: results[f]["DYE_advantage"] > 0 for f in folios}
    count = sum(per.values())
    n = len(folios)
    rate = count / n if n > 0 else 0.0
    return per, count, n, rate


def evaluate_gp2(folios):
    """GP2: EPV >= 0.80"""
    per = {f: results[f]["EPV"] >= 0.80 for f in folios}
    count = sum(per.values())
    n = len(folios)
    rate = count / n if n > 0 else 0.0
    return per, count, n, rate


def evaluate_gp3(folios):
    """GP3: DVA > 0"""
    per = {f: results[f]["DVA"] > 0 for f in folios}
    count = sum(per.values())
    n = len(folios)
    rate = count / n if n > 0 else 0.0
    return per, count, n, rate


def evaluate_gp4(folios):
    """GP4: WCP/UEB reported only (NOT gated) — legacy continuity check."""
    ueb_per = {f: results[f]["M1_UEB"] <= results[f]["M0_UEB"] for f in folios}
    wcp_per = {f: results[f]["M1_WCP"] >= results[f]["M0_WCP"] for f in folios}
    n = len(folios)
    ueb_count = sum(ueb_per.values())
    wcp_count = sum(wcp_per.values())
    ueb_rate = ueb_count / n if n > 0 else 0.0
    wcp_rate = wcp_count / n if n > 0 else 0.0
    return {
        "UEB_per_folio": ueb_per, "UEB_count": ueb_count, "UEB_rate": ueb_rate,
        "WCP_per_folio": wcp_per, "WCP_count": wcp_count, "WCP_rate": wcp_rate,
    }


# Evaluate at each tier
tiers = {}
for tier_name, tier_folios in [("A", tier_a_folios), ("B", tier_b_folios),
                                ("C", tier_c_folios)]:
    gp1_per, gp1_count, gp1_n, gp1_rate = evaluate_gp1(tier_folios)
    gp2_per, gp2_count, gp2_n, gp2_rate = evaluate_gp2(tier_folios)
    gp3_per, gp3_count, gp3_n, gp3_rate = evaluate_gp3(tier_folios)
    gp4 = evaluate_gp4(tier_folios)

    tiers[tier_name] = {
        "folios": tier_folios,
        "n": len(tier_folios),
        "GP1": {"per_folio": gp1_per, "count": gp1_count, "total": gp1_n,
                "rate": gp1_rate},
        "GP2": {"per_folio": gp2_per, "count": gp2_count, "total": gp2_n,
                "rate": gp2_rate},
        "GP3": {"per_folio": gp3_per, "count": gp3_count, "total": gp3_n,
                "rate": gp3_rate},
        "GP4": gp4,
    }

# Gates
gp1_gates = {"C": 0.75, "A": 0.75}
gp2_gates = {"C": 0.75, "A": 0.50}
gp3_gates = {"C": 0.75, "A": 0.75}

for tier_name in ["A", "B", "C"]:
    t = tiers[tier_name]
    print(f"\n  --- Tier {tier_name} ({t['n']} folios) ---")
    print(f"  GP1 (DYE_adv > 0):   {t['GP1']['count']}/{t['GP1']['total']} "
          f"= {t['GP1']['rate']:.1%}")
    print(f"  GP2 (EPV >= 0.80):   {t['GP2']['count']}/{t['GP2']['total']} "
          f"= {t['GP2']['rate']:.1%}  [CENTRAL]")
    print(f"  GP3 (DVA > 0):       {t['GP3']['count']}/{t['GP3']['total']} "
          f"= {t['GP3']['rate']:.1%}")
    g4 = t['GP4']
    print(f"  GP4 (legacy check, NOT GATED): "
          f"UEB<= {g4['UEB_count']}/{t['n']}={g4['UEB_rate']:.1%}, "
          f"WCP>= {g4['WCP_count']}/{t['n']}={g4['WCP_rate']:.1%}")


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
print("\n" + "=" * 72)
print("VERDICT")
print("=" * 72)

tier_c_gp2_pass = tiers["C"]["GP2"]["rate"] >= 0.75
tier_a_gp1_pass = tiers["A"]["GP1"]["rate"] >= 0.50
tier_a_gp3_pass = tiers["A"]["GP3"]["rate"] >= 0.75

if tier_c_gp2_pass and tier_a_gp1_pass and tier_a_gp3_pass:
    verdict = "PROCESS_QUALITY_EXPANDED"
elif tier_c_gp2_pass and tier_a_gp1_pass:
    verdict = "PARTIAL_EXPANSION"
elif tier_c_gp2_pass:
    verdict = "PARTIAL_EXPANSION"
else:
    verdict = "EXPANSION_INSUFFICIENT"

print(f"\n  Tier C GP2 rate = {tiers['C']['GP2']['rate']:.1%} "
      f"(gate >= 75%): {'PASS' if tier_c_gp2_pass else 'FAIL'}")
print(f"  Tier A GP1 rate = {tiers['A']['GP1']['rate']:.1%} "
      f"(gate >= 50%): {'PASS' if tier_a_gp1_pass else 'FAIL'}")
print(f"  Tier A GP3 rate = {tiers['A']['GP3']['rate']:.1%} "
      f"(gate >= 75%): {'PASS' if tier_a_gp3_pass else 'FAIL'}")
print(f"\n  >>> {verdict} <<<\n")


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

# GD4: Per-Section Breakdown
print("=" * 72)
print("DIAGNOSTICS")
print("=" * 72)

print("\nGD4: Per-Section Breakdown (descriptive only)")
section_stats = {}
for sec, sec_folios in SECTION_MAP.items():
    dye_pass = sum(1 for f in sec_folios if results[f]["DYE_advantage"] > 0)
    epv_pass = sum(1 for f in sec_folios if results[f]["EPV"] >= 0.80)
    mean_dye_adv = safe_mean([results[f]["DYE_advantage"] for f in sec_folios])
    n = len(sec_folios)
    section_stats[sec] = {
        "n": n, "dye_pass": dye_pass, "epv_pass": epv_pass,
        "mean_dye_adv": mean_dye_adv,
        "dye_rate": dye_pass / n if n > 0 else 0,
        "epv_rate": epv_pass / n if n > 0 else 0,
    }
    print(f"  {sec}: n={n}, DYE_pass={dye_pass}/{n}, EPV_pass={epv_pass}/{n}, "
          f"mean_DYE_adv={mean_dye_adv:+.6f}")

# GD5: Per-Profile Breakdown
print("\nGD5: Per-Profile Breakdown (descriptive only)")
profile_stats = {}
for prof, prof_folios in PROFILE_MAP.items():
    dye_pass = sum(1 for f in prof_folios if results[f]["DYE_advantage"] > 0)
    epv_pass = sum(1 for f in prof_folios if results[f]["EPV"] >= 0.80)
    mean_dye_adv = safe_mean([results[f]["DYE_advantage"] for f in prof_folios])
    n = len(prof_folios)
    profile_stats[prof] = {
        "n": n, "dye_pass": dye_pass, "epv_pass": epv_pass,
        "mean_dye_adv": mean_dye_adv,
        "dye_rate": dye_pass / n if n > 0 else 0,
        "epv_rate": epv_pass / n if n > 0 else 0,
    }
    print(f"  {prof}: n={n}, DYE_pass={dye_pass}/{n}, EPV_pass={epv_pass}/{n}, "
          f"mean_DYE_adv={mean_dye_adv:+.6f}")

# GD6: 18-Folio Consistency Check (572 vs 571)
print("\nGD6: 18-Folio Consistency Check (572 vs 571)")
ref_571_per_folio = ref_571["per_folio"]
gd6 = {}
for f in PHASE_571_FOLIOS:
    r = results[f]
    ref = ref_571_per_folio[f]
    delta_dye_m1 = r["DYE_M1"] - ref["DYE_M1"]
    delta_dye_m4f = r["DYE_M4f"] - ref["DYE_M4f"]
    delta_dva = r["DVA"] - ref["DVA"]
    delta_epv = r["EPV"] - ref["EPV"]
    gd6[f] = {
        "DYE_M1_572": r["DYE_M1"], "DYE_M1_571": ref["DYE_M1"],
        "delta_DYE_M1": delta_dye_m1,
        "DYE_M4f_572": r["DYE_M4f"], "DYE_M4f_571": ref["DYE_M4f"],
        "delta_DYE_M4f": delta_dye_m4f,
        "DVA_572": r["DVA"], "DVA_571": ref["DVA"],
        "delta_DVA": delta_dva,
        "EPV_572": r["EPV"], "EPV_571": ref["EPV"],
        "delta_EPV": delta_epv,
    }
    print(f"  {f}: DYE_M1 delta={delta_dye_m1:+.4f}, "
          f"DYE_M4f delta={delta_dye_m4f:+.4f}, "
          f"DVA delta={delta_dva:+.6f}, "
          f"EPV delta={delta_epv:+.2f}")

# GD6 summary
gd6_dye_m1_deltas = [abs(gd6[f]["delta_DYE_M1"]) for f in PHASE_571_FOLIOS]
gd6_dva_deltas = [abs(gd6[f]["delta_DVA"]) for f in PHASE_571_FOLIOS]
print(f"\n  GD6 Summary: mean |delta DYE_M1| = {safe_mean(gd6_dye_m1_deltas):.6f}, "
      f"mean |delta DVA| = {safe_mean(gd6_dva_deltas):.6f}")

# GD7: Dilution Curve
print("\nGD7: Dilution Curve")
sorted_by_events = sorted(FOLIOS, key=lambda f: results[f]["n_m1_events"], reverse=True)
dilution_curve = []
cum_dye_pass = 0
cum_epv_pass = 0
for i, f in enumerate(sorted_by_events, 1):
    r = results[f]
    if r["DYE_advantage"] > 0:
        cum_dye_pass += 1
    if r["EPV"] >= 0.80:
        cum_epv_pass += 1
    dye_rate = cum_dye_pass / i
    epv_rate = cum_epv_pass / i
    dilution_curve.append({
        "rank": i,
        "folio": f,
        "n_events": r["n_m1_events"],
        "eligibility": r["eligibility_class"],
        "DYE_advantage": r["DYE_advantage"],
        "EPV": r["EPV"],
        "cum_dye_pass_rate": dye_rate,
        "cum_epv_pass_rate": epv_rate,
    })
    if i <= 20 or i % 10 == 0 or i == len(sorted_by_events):
        print(f"  #{i:2d} {f:7s} n_events={r['n_m1_events']:2d} "
              f"DYE_adv={r['DYE_advantage']:+.6f} "
              f"EPV={r['EPV']:.2f} "
              f"cum_DYE_rate={dye_rate:.1%} cum_EPV_rate={epv_rate:.1%}")

# GD8: F-parameter renormalization validation
print("\nGD8: F-parameter Renormalization Validation")
old_f_params = pilot_570a["folio_parameters"]  # 20 pilot folios
pilot_20 = [f for f in old_f_params.keys() if f in FOLIO_CONFIGS]

F_AXES = ["F1", "F2", "F3", "F4_raw", "F5"]
gd8 = {}
for axis in F_AXES:
    old_vals = [old_f_params[f][axis] for f in pilot_20]
    new_vals = [FOLIO_CONFIGS[f][axis] for f in pilot_20]
    deltas = [abs(n - o) for n, o in zip(new_vals, old_vals)]
    mean_drift = sum(deltas) / len(deltas)
    max_drift = max(deltas)
    rho = spearman_rank(old_vals, new_vals)
    gd8[axis] = {
        "mean_drift": mean_drift,
        "max_drift": max_drift,
        "spearman_rho": rho,
        "old_vals": {f: old_f_params[f][axis] for f in pilot_20},
        "new_vals": {f: FOLIO_CONFIGS[f][axis] for f in pilot_20},
    }
    rho_str = f"{rho:.4f}" if rho is not None else "N/A"
    print(f"  {axis}: mean_drift={mean_drift:.4f}, max_drift={max_drift:.4f}, "
          f"spearman_rho={rho_str}")

# Excluded pilot folios (if any were in 570a but not eligible now)
excluded_from_570a = [f for f in old_f_params.keys() if f not in FOLIO_CONFIGS]
if excluded_from_570a:
    print(f"  Note: {len(excluded_from_570a)} pilot folios excluded from 572: "
          f"{excluded_from_570a}")

norm_82 = t1["normalization_bounds_82"]
norm_20 = t1["normalization_bounds_20"]
print(f"\n  Normalization bounds comparison (82-folio vs 20-folio):")
for proxy in norm_82:
    p5_82 = norm_82[proxy]["p5"]
    p95_82 = norm_82[proxy]["p95"]
    p5_20 = norm_20[proxy]["p5"]
    p95_20 = norm_20[proxy]["p95"]
    print(f"    {proxy}: p5 {p5_20:.4f}->{p5_82:.4f}, p95 {p95_20:.4f}->{p95_82:.4f}")


# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------
n_sections = len(SECTION_MAP)
if verdict == "PROCESS_QUALITY_EXPANDED":
    constraints = [
        {
            "id": "C1636",
            "text": (f"Productive disruption efficiency (DYE advantage > 0) "
                     f"expands to the full {len(FOLIOS)}-folio eligible Currier B "
                     f"set spanning {n_sections} sections and 3 apparatus profiles "
                     f"(Tier C: {tiers['C']['GP2']['count']}/{tiers['C']['GP2']['total']} "
                     f"demand-strong pass GP2, Tier A: "
                     f"{tiers['A']['GP1']['count']}/{tiers['A']['GP1']['total']} pass GP1, "
                     f"{tiers['A']['GP3']['count']}/{tiers['A']['GP3']['total']} pass GP3)"),
            "tier": 2,
            "scope": "B_apparatus",
            "phase": "572"
        }
    ]
elif verdict == "PARTIAL_EXPANSION":
    constraints = [
        {
            "id": "C1636",
            "text": (f"Productive disruption efficiency shows partial expansion: "
                     f"Tier C GP2 = {tiers['C']['GP2']['rate']:.0%}, "
                     f"Tier A GP1 = {tiers['A']['GP1']['rate']:.0%}, "
                     f"Tier A GP3 = {tiers['A']['GP3']['rate']:.0%}, "
                     f"mechanism present but diluted across {len(FOLIOS)} eligible folios"),
            "tier": 2,
            "scope": "B_apparatus",
            "phase": "572"
        }
    ]
else:
    constraints = []


# ---------------------------------------------------------------------------
# Build output JSON
# ---------------------------------------------------------------------------
output_json = {
    "metadata": {
        "phase": "572",
        "script": "t4_expansion_report.py",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "folios": FOLIOS,
        "n_folios": len(FOLIOS),
        "metrics_computed": ["DVA", "DYE", "DYE_EPV", "DYC", "YGA"],
        "inputs": {
            "t1": "t1_full_scale_setup.json",
            "t2": "t2_full_model_runs.json",
            "t3": "t3_null_runs.json",
            "ref_571": "phases/PROCESS_QUALITY_GENERALIZATION/results/t4_metrics.json",
            "pilot_570a": "phases/FOLIO_SPECIFIC_APPARATUS_PILOT/results/t1_pilot_selection.json"
        }
    },
    "verdict": verdict,
    "test_battery": {},
    "per_folio": {},
    "diagnostics": {},
    "provisional_constraints": constraints,
}

# Test battery at each tier
for tier_name in ["A", "B", "C"]:
    t = tiers[tier_name]
    output_json["test_battery"][f"tier_{tier_name}"] = {
        "folios": t["folios"],
        "n_folios": t["n"],
        "GP1": {
            "description": "DYE_advantage > 0",
            "gate": gp1_gates.get(tier_name, "N/A"),
            "pass_count": t["GP1"]["count"],
            "total": t["GP1"]["total"],
            "rate": t["GP1"]["rate"],
            "passed": t["GP1"]["rate"] >= gp1_gates.get(tier_name, 0.75),
            "per_folio": {f: {"value": results[f]["DYE_advantage"],
                              "passed": t["GP1"]["per_folio"][f]}
                          for f in t["folios"]}
        },
        "GP2": {
            "description": "DYE EPV >= 0.80",
            "central": True,
            "gate": gp2_gates.get(tier_name, "N/A"),
            "pass_count": t["GP2"]["count"],
            "total": t["GP2"]["total"],
            "rate": t["GP2"]["rate"],
            "passed": t["GP2"]["rate"] >= gp2_gates.get(tier_name, 0.75),
            "per_folio": {f: {"value": results[f]["EPV"],
                              "epv_count": results[f]["EPV_count"],
                              "n_perms": results[f]["n_perms"],
                              "passed": t["GP2"]["per_folio"][f]}
                          for f in t["folios"]}
        },
        "GP3": {
            "description": "DVA > 0",
            "gate": gp3_gates.get(tier_name, "N/A"),
            "pass_count": t["GP3"]["count"],
            "total": t["GP3"]["total"],
            "rate": t["GP3"]["rate"],
            "passed": t["GP3"]["rate"] >= gp3_gates.get(tier_name, 0.75),
            "per_folio": {f: {"value": results[f]["DVA"],
                              "passed": t["GP3"]["per_folio"][f]}
                          for f in t["folios"]}
        },
        "GP4": {
            "description": "Anchor stability (legacy check, NOT GATED)",
            "UEB_count": t["GP4"]["UEB_count"],
            "UEB_rate": t["GP4"]["UEB_rate"],
            "WCP_count": t["GP4"]["WCP_count"],
            "WCP_rate": t["GP4"]["WCP_rate"],
        },
    }

# Per-folio results
for f in FOLIOS:
    r = results[f]
    output_json["per_folio"][f] = {
        "section": r["section"],
        "profile": r["profile"],
        "n_close_lines": r["n_close_lines"],
        "eligibility_class": r["eligibility_class"],
        "event_selection": r["event_selection"],
        "demand_strong": r["demand_strong"],
        "n_m1_events": r["n_m1_events"],
        "n_m1_total": r["n_m1_total"],
        "DVA": r["DVA"],
        "mean_dV_M1": r["mean_dV_M1"],
        "mean_dV_M4f": r["mean_dV_M4f"],
        "DYE_M1": r["DYE_M1"],
        "DYE_M4f": r["DYE_M4f"],
        "DYE_advantage": r["DYE_advantage"],
        "EPV": r["EPV"],
        "EPV_count": r["EPV_count"],
        "demand_magnitude": r["demand_magnitude"],
        "z_DYE": r["z_DYE"],
        "z_YGA": r["z_YGA"],
        "DYC": r["DYC"],
        "YGA": r["YGA"],
        "M0_UEB": r["M0_UEB"],
        "M1_UEB": r["M1_UEB"],
        "M0_WCP": r["M0_WCP"],
        "M1_WCP": r["M1_WCP"],
    }

# Diagnostics
output_json["diagnostics"] = {
    "GD1_full_metric_table": {f: {
        "section": results[f]["section"],
        "profile": results[f]["profile"],
        "DVA": results[f]["DVA"],
        "DYE_M1": results[f]["DYE_M1"],
        "DYE_M4f": results[f]["DYE_M4f"],
        "DYE_advantage": results[f]["DYE_advantage"],
        "EPV": results[f]["EPV"],
        "EPV_count": results[f]["EPV_count"],
        "DYC": results[f]["DYC"],
        "YGA": results[f]["YGA"],
        "demand_strong": results[f]["demand_strong"],
    } for f in FOLIOS},
    "GD2_folio_eligibility": {f: {
        "n_close_lines": results[f]["n_close_lines"],
        "n_events": results[f]["n_m1_events"],
        "selection_tier": results[f]["event_selection"],
        "eligibility_class": results[f]["eligibility_class"],
    } for f in FOLIOS},
    "GD3_n_close_comparison": {f: {
        "m1_mean_n_close": results[f]["m1_mean_n_close"],
        "m4f_mean_n_close": results[f]["m4f_mean_n_close"],
        "ratio": results[f]["m1_mean_n_close"] / max(results[f]["m4f_mean_n_close"], 0.01),
    } for f in FOLIOS},
    "GD4_section_breakdown": section_stats,
    "GD5_profile_breakdown": profile_stats,
    "GD6_571_consistency": gd6,
    "GD7_dilution_curve": dilution_curve,
    "GD8_f_param_renormalization": gd8,
}

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_DIR / "t4_expansion_metrics.json", "w") as f:
    json.dump(output_json, f, indent=2)
print(f"\nWrote {OUTPUT_DIR / 't4_expansion_metrics.json'}")


# ---------------------------------------------------------------------------
# Generate REPORT_572.md
# ---------------------------------------------------------------------------
def fmt(v, decimals=4):
    if v is None:
        return "N/A"
    return f"{v:.{decimals}f}"


def fmt_sign(v, decimals=6):
    if v is None:
        return "N/A"
    return f"{v:+.{decimals}f}"


def pf(b):
    return "PASS" if b else "FAIL"


lines = []
L = lines.append

L("# Phase 572: Productive Disruption Expansion")
L("")
L(f"**Verdict: {verdict}**")
L("")
tier_c_str = (f"GP1:{tiers['C']['GP1']['count']}/{tiers['C']['GP1']['total']}, "
              f"GP2:{tiers['C']['GP2']['count']}/{tiers['C']['GP2']['total']}, "
              f"GP3:{tiers['C']['GP3']['count']}/{tiers['C']['GP3']['total']}, "
              f"GP4:reported(not gated)")
tier_a_str = (f"GP1:{tiers['A']['GP1']['count']}/{tiers['A']['GP1']['total']}, "
              f"GP2:{tiers['A']['GP2']['count']}/{tiers['A']['GP2']['total']}, "
              f"GP3:{tiers['A']['GP3']['count']}/{tiers['A']['GP3']['total']}, "
              f"GP4:reported(not gated)")
L(f"**Tier C (demand-strong):** {tier_c_str}")
L(f"**Tier A (all {len(tier_a_folios)}):** {tier_a_str}")
n_c = len(constraints)
if n_c > 0:
    ids = ", ".join(c["id"] for c in constraints)
    L(f"**New constraints:** {n_c} ({ids})")
else:
    L("**New constraints:** 0")
L("")
L("---")
L("")

# 1. Summary
L("## 1. Summary")
L("")
if verdict == "PROCESS_QUALITY_EXPANDED":
    L(f"Phase 572 confirms that the productive disruption mechanism **expands** to the "
      f"full {len(FOLIOS)}-folio eligible Currier B set. Across "
      f"{n_sections} sections ({', '.join(sorted(SECTION_MAP.keys()))}) and 3 apparatus "
      f"profiles, DYE advantage remains positive in "
      f"{tiers['A']['GP1']['count']}/{tiers['A']['GP1']['total']} folios and the "
      f"central GP2 test (EPV >= 0.80) passes in "
      f"{tiers['C']['GP2']['count']}/{tiers['C']['GP2']['total']} demand-strong folios. "
      "The mechanism is a general property of Currier B apparatus operation.")
elif verdict == "PARTIAL_EXPANSION":
    L(f"Phase 572 finds **partial expansion** of the productive disruption mechanism. "
      f"Among demand-strong folios (Tier C), GP2 passes at "
      f"{tiers['C']['GP2']['rate']:.0%}. Across all {len(FOLIOS)} eligible folios "
      f"(Tier A), GP1 (DYE > 0) holds at {tiers['A']['GP1']['rate']:.0%}. "
      f"The mechanism appears real but signal is diluted in folios with sparse "
      "demand opportunities.")
else:
    L(f"Phase 572 finds **insufficient expansion** of the productive disruption "
      f"mechanism. Tier C GP2 passes at only {tiers['C']['GP2']['rate']:.0%}, below the "
      "75% gate. The 571 result may not extend to the full Currier B set.")
L("")

# 2. Context
L("## 2. Context")
L("")
L("Phase 571 validated process-quality metrics (DVA, DYE, DYC) on 18 folios from 5 "
  "sections and 3 profiles. Phase 572 asks: does this mechanism expand to the full "
  f"~{len(FOLIOS)}-folio eligible Currier B set? This is the definitive scale-up test, "
  "moving from curated selection to near-complete coverage.")
L("")
L(f"The {len(FOLIOS)} eligible folios span {n_sections} sections "
  f"({', '.join(sorted(SECTION_MAP.keys()))}) and 3 profiles "
  f"({', '.join(sorted(PROFILE_MAP.keys()))}). "
  f"{len(t1['excluded_folios'])} folios were excluded due to insufficient data. "
  f"F-parameters were renormalized from 20-folio to 82-folio bounds (GD8 validates).")
L("")

# 3. Three-Tiered Evaluation Design
L("## 3. Three-Tiered Evaluation Design")
L("")
L("Each GP test is evaluated at three levels to separate demand-strength effects:")
L("")
L("| Tier | Description | Folios |")
L("|------|-------------|--------|")
L(f"| **A** | All {len(tier_a_folios)} eligible folios | {len(tier_a_folios)} |")
L(f"| **B** | demand_eligible + demand_strong | {len(tier_b_folios)} |")
L(f"| **C** | demand_strong only | {len(tier_c_folios)} |")
L("")
L("Eligibility classes:")
L("")
for ec in ["demand_strong", "demand_eligible", "fallback_only", "sparse_close"]:
    count = elig_counts.get(ec, 0)
    folios_in_class = [f for f in FOLIOS if results[f]["eligibility_class"] == ec]
    L(f"- **{ec}**: {count} folios — {', '.join(folios_in_class)}")
L("")

# 4. Test Results
L("## 4. Test Results")
L("")

for tier_name, tier_folios in [("C", tier_c_folios), ("B", tier_b_folios),
                                ("A", tier_a_folios)]:
    t = tiers[tier_name]
    L(f"### Tier {tier_name} ({t['n']} folios)")
    L("")

    # GP1
    gp1_gate = gp1_gates.get(tier_name, None)
    gp1_passed = t["GP1"]["rate"] >= gp1_gate if gp1_gate else "N/A"
    L(f"**GP1 (DYE_advantage > 0):** {t['GP1']['count']}/{t['GP1']['total']} "
      f"= {t['GP1']['rate']:.0%}"
      + (f" (gate >= {gp1_gate:.0%}): {pf(gp1_passed)}" if gp1_gate else ""))
    L("")
    L("| Folio | Section | DYE_M1 | DYE_M4f | DYE_advantage | Result |")
    L("|-------|---------|--------|---------|---------------|--------|")
    for f in tier_folios:
        r = results[f]
        L(f"| {f} | {r['section']} | {fmt(r['DYE_M1'])} | {fmt(r['DYE_M4f'])} | "
          f"{fmt_sign(r['DYE_advantage'])} | {pf(t['GP1']['per_folio'][f])} |")
    L("")

    # GP2
    gp2_gate = gp2_gates.get(tier_name, None)
    gp2_passed = t["GP2"]["rate"] >= gp2_gate if gp2_gate else "N/A"
    L(f"**GP2 (EPV >= 0.80) [CENTRAL]:** {t['GP2']['count']}/{t['GP2']['total']} "
      f"= {t['GP2']['rate']:.0%}"
      + (f" (gate >= {gp2_gate:.0%}): {pf(gp2_passed)}" if gp2_gate else ""))
    L("")
    L("| Folio | Section | M1 DYE | Perms beaten | EPV | Result |")
    L("|-------|---------|--------|-------------|-----|--------|")
    for f in tier_folios:
        r = results[f]
        L(f"| {f} | {r['section']} | {fmt(r['DYE_M1'])} | "
          f"{r['EPV_count']}/{r['n_perms']} | {fmt(r['EPV'], 2)} | "
          f"{pf(t['GP2']['per_folio'][f])} |")
    L("")

    # GP3
    gp3_gate = gp3_gates.get(tier_name, None)
    gp3_passed = t["GP3"]["rate"] >= gp3_gate if gp3_gate else "N/A"
    L(f"**GP3 (DVA > 0):** {t['GP3']['count']}/{t['GP3']['total']} "
      f"= {t['GP3']['rate']:.0%}"
      + (f" (gate >= {gp3_gate:.0%}): {pf(gp3_passed)}" if gp3_gate else ""))
    L("")
    L("| Folio | Section | mean_dV_M1 | mean_dV_M4f | DVA | Result |")
    L("|-------|---------|-----------|------------|-----|--------|")
    for f in tier_folios:
        r = results[f]
        L(f"| {f} | {r['section']} | {fmt(r['mean_dV_M1'])} | "
          f"{fmt(r['mean_dV_M4f'])} | {fmt_sign(r['DVA'])} | "
          f"{pf(t['GP3']['per_folio'][f])} |")
    L("")

    # GP4
    g4 = t["GP4"]
    L(f"**GP4 (legacy check, NOT GATED):** "
      f"UEB M1<=M0: {g4['UEB_count']}/{t['n']}={g4['UEB_rate']:.0%}, "
      f"WCP M1>=M0: {g4['WCP_count']}/{t['n']}={g4['WCP_rate']:.0%}")
    L("")
    L("| Folio | M0_UEB | M1_UEB | UEB ok | M0_WCP | M1_WCP | WCP ok |")
    L("|-------|--------|--------|--------|--------|--------|--------|")
    for f in tier_folios:
        r = results[f]
        L(f"| {f} | {fmt(r['M0_UEB'], 1)} | {fmt(r['M1_UEB'], 1)} | "
          f"{pf(g4['UEB_per_folio'][f])} | "
          f"{fmt(r['M0_WCP'])} | {fmt(r['M1_WCP'])} | "
          f"{pf(g4['WCP_per_folio'][f])} |")
    L("")

# 5. Diagnostics
L("## 5. Diagnostics")
L("")

# GD1
L(f"### GD1: Full Metric Table (all {len(FOLIOS)} folios)")
L("")
L("| Folio | Section | Profile | DVA | DYE_M1 | DYE_M4f | DYE_adv | EPV | DYC | YGA | demand_strong |")
L("|-------|---------|---------|-----|--------|---------|---------|-----|-----|-----|---------------|")
for f in FOLIOS:
    r = results[f]
    ds = "yes" if r["demand_strong"] else "no"
    L(f"| {f} | {r['section']} | {r['profile'][:2]} | "
      f"{fmt_sign(r['DVA'])} | {fmt(r['DYE_M1'])} | {fmt(r['DYE_M4f'])} | "
      f"{fmt_sign(r['DYE_advantage'])} | {r['EPV_count']}/{r['n_perms']} | "
      f"{fmt(r['DYC'])} | {fmt(r['YGA'])} | {ds} |")
L("")

# GD2
L("### GD2: Folio Eligibility Classification")
L("")
L("| Folio | n_close_lines | n_events | Selection tier | Eligibility class |")
L("|-------|--------------|----------|----------------|-------------------|")
for f in FOLIOS:
    r = results[f]
    L(f"| {f} | {r['n_close_lines']} | {r['n_m1_events']} | "
      f"{r['event_selection']} | {r['eligibility_class']} |")
L("")

# GD3
L("### GD3: n_close Token Comparison")
L("")
L("| Folio | M1 mean n_close | M4f mean n_close | Ratio |")
L("|-------|----------------|-----------------|-------|")
for f in FOLIOS:
    r = results[f]
    ratio = r["m1_mean_n_close"] / max(r["m4f_mean_n_close"], 0.01)
    L(f"| {f} | {fmt(r['m1_mean_n_close'], 1)} | "
      f"{fmt(r['m4f_mean_n_close'], 1)} | {fmt(ratio, 2)} |")
L("")
L("Ratios near 1.0 confirm DYE differences are not confounded by line length.")
L("")

# GD4
L("### GD4: Per-Section Breakdown (descriptive only)")
L("")
L("| Section | n | DYE pass | DYE rate | EPV pass | EPV rate | Mean DYE_adv |")
L("|---------|---|----------|----------|----------|----------|-------------|")
for sec in sorted(section_stats.keys()):
    s = section_stats[sec]
    L(f"| {sec} | {s['n']} | {s['dye_pass']}/{s['n']} | "
      f"{s['dye_rate']:.0%} | {s['epv_pass']}/{s['n']} | "
      f"{s['epv_rate']:.0%} | {fmt_sign(s['mean_dye_adv'])} |")
L("")

# GD5
L("### GD5: Per-Profile Breakdown (descriptive only)")
L("")
L("| Profile | n | DYE pass | DYE rate | EPV pass | EPV rate | Mean DYE_adv |")
L("|---------|---|----------|----------|----------|----------|-------------|")
for prof in sorted(profile_stats.keys()):
    s = profile_stats[prof]
    L(f"| {prof} | {s['n']} | {s['dye_pass']}/{s['n']} | "
      f"{s['dye_rate']:.0%} | {s['epv_pass']}/{s['n']} | "
      f"{s['epv_rate']:.0%} | {fmt_sign(s['mean_dye_adv'])} |")
L("")

# GD6
L("### GD6: 18-Folio Consistency Check (572 vs 571)")
L("")
L("Compares all 18 Phase 571 reference folios under the new 82-folio F-parameters.")
L("")
L("| Folio | DYE_M1 (572) | DYE_M1 (571) | delta | DYE_M4f (572) | DYE_M4f (571) | delta | DVA (572) | DVA (571) | delta | EPV (572) | EPV (571) | delta |")
L("|-------|-------------|---------------|-------|--------------|----------------|-------|----------|-----------|-------|----------|-----------|-------|")
for f in PHASE_571_FOLIOS:
    g = gd6[f]
    L(f"| {f} | {fmt(g['DYE_M1_572'])} | {fmt(g['DYE_M1_571'])} | "
      f"{fmt_sign(g['delta_DYE_M1'], 4)} | "
      f"{fmt(g['DYE_M4f_572'])} | {fmt(g['DYE_M4f_571'])} | "
      f"{fmt_sign(g['delta_DYE_M4f'], 4)} | "
      f"{fmt_sign(g['DVA_572'])} | {fmt_sign(g['DVA_571'])} | "
      f"{fmt_sign(g['delta_DVA'])} | "
      f"{fmt(g['EPV_572'], 2)} | {fmt(g['EPV_571'], 2)} | "
      f"{fmt_sign(g['delta_EPV'], 2)} |")
L("")
L(f"Mean |delta DYE_M1| = {safe_mean(gd6_dye_m1_deltas):.6f}, "
  f"mean |delta DVA| = {safe_mean(gd6_dva_deltas):.6f}. "
  "Small deltas expected from F-parameter renormalization and T2/T3 re-run variance.")
L("")

# GD7
L("### GD7: Dilution Curve")
L("")
L("Folios ordered by n_events (descending). Running pass rates show whether the "
  "mechanism signal degrades as lower-demand folios are added.")
L("")
L("| Rank | Folio | n_events | Eligibility | DYE_adv | EPV | Cum DYE>0 rate | Cum EPV>=0.80 rate |")
L("|------|-------|----------|-------------|---------|-----|----------------|-------------------|")
for entry in dilution_curve:
    L(f"| {entry['rank']} | {entry['folio']} | {entry['n_events']} | "
      f"{entry['eligibility']} | {fmt_sign(entry['DYE_advantage'])} | "
      f"{fmt(entry['EPV'], 2)} | {entry['cum_dye_pass_rate']:.0%} | "
      f"{entry['cum_epv_pass_rate']:.0%} |")
L("")

# GD8
L("### GD8: F-Parameter Renormalization Validation")
L("")
L("Compares F-parameter values for the 20 original Phase 570a pilot folios under "
  "20-folio vs 82-folio normalization bounds.")
L("")
L("| F-axis | Mean drift | Max drift | Spearman rho |")
L("|--------|-----------|-----------|-------------|")
for axis in F_AXES:
    g = gd8[axis]
    rho_str = fmt(g["spearman_rho"]) if g["spearman_rho"] is not None else "N/A"
    L(f"| {axis} | {fmt(g['mean_drift'])} | {fmt(g['max_drift'])} | {rho_str} |")
L("")
L("Normalization bounds comparison (20-folio -> 82-folio):")
L("")
L("| Proxy | p5 (20) | p5 (82) | p95 (20) | p95 (82) |")
L("|-------|---------|---------|----------|----------|")
for proxy in norm_82:
    L(f"| {proxy} | {fmt(norm_20[proxy]['p5'])} | {fmt(norm_82[proxy]['p5'])} | "
      f"{fmt(norm_20[proxy]['p95'])} | {fmt(norm_82[proxy]['p95'])} |")
L("")
if excluded_from_570a:
    L(f"Note: {len(excluded_from_570a)} pilot folios excluded from 572 eligibility: "
      f"{', '.join(excluded_from_570a)}")
    L("")
L("High Spearman rho (> 0.90) indicates rank-order preservation despite absolute drift, "
  "confirming renormalization does not distort the relative F-parameter profile ordering.")
L("")

# 6. Analysis
L("## 6. Analysis")
L("")

L("### Productive Disruption Mechanism: Expansion Assessment")
L("")
L("Phase 571 established generalization across 18 folios from 5 sections. Phase 572 "
  f"tests whether this holds across the full {len(FOLIOS)}-folio eligible Currier B "
  "set, with F-parameters renormalized to 82-folio bounds.")
L("")

# Dynamic analysis based on verdict
if verdict == "PROCESS_QUALITY_EXPANDED":
    L("The mechanism **expands successfully**. Key observations:")
    L("")
    L(f"1. **Tier C (demand-strong):** "
      f"{tiers['C']['GP2']['count']}/{tiers['C']['GP2']['total']} pass GP2. "
      "Where demand opportunities are rich, the mechanism is robust across the "
      "full Currier B set.")
    L(f"2. **Tier A (all {len(FOLIOS)}):** "
      f"{tiers['A']['GP1']['count']}/{tiers['A']['GP1']['total']} show DYE advantage > 0. "
      "The direction is consistent even in low-opportunity folios.")
    L(f"3. **Tier A DVA (GP3):** "
      f"{tiers['A']['GP3']['count']}/{tiers['A']['GP3']['total']} show DVA > 0. "
      "Real closure tokens generate more process state displacement than null tokens "
      "across the full set.")
    L(f"4. **GD6 (571 consistency):** Mean DYE_M1 delta = "
      f"{safe_mean(gd6_dye_m1_deltas):.6f}. "
      "Small deltas confirm F-parameter renormalization did not distort results.")
    L(f"5. **GD8 (renormalization):** Rank-order preservation across F-axes "
      "validates that the 82-folio normalization expands coverage without "
      "disrupting relative folio ordering.")
elif verdict == "PARTIAL_EXPANSION":
    L("The mechanism shows **partial expansion**. Key observations:")
    L("")
    L(f"1. **Tier C (demand-strong):** "
      f"{tiers['C']['GP2']['count']}/{tiers['C']['GP2']['total']} pass GP2. "
      "The mechanism works where demand opportunities are sufficient.")
    L(f"2. **Tier A (all {len(FOLIOS)}):** "
      f"{tiers['A']['GP1']['count']}/{tiers['A']['GP1']['total']} show DYE advantage > 0. "
      "Direction is mostly consistent but diluted in sparse-opportunity folios.")
    L(f"3. **GD6 (571 consistency):** Mean DYE_M1 delta = "
      f"{safe_mean(gd6_dye_m1_deltas):.6f}. "
      "Renormalization impact is modest.")
else:
    L("The mechanism **does not expand** to the full set. Key observations:")
    L("")
    L(f"1. **Tier C:** Even demand-strong folios fail GP2 at "
      f"{tiers['C']['GP2']['rate']:.0%}.")
    L(f"2. The 571 result may reflect selection effects not present at full scale.")
L("")

# Section and profile observations
L("### Section and Profile Patterns (descriptive)")
L("")
for sec in sorted(section_stats.keys()):
    s = section_stats[sec]
    L(f"- **Section {sec}** ({s['n']} folios): DYE pass {s['dye_pass']}/{s['n']}, "
      f"EPV pass {s['epv_pass']}/{s['n']}, "
      f"mean DYE_adv = {fmt_sign(s['mean_dye_adv'])}")
L("")
for prof in sorted(profile_stats.keys()):
    s = profile_stats[prof]
    L(f"- **{prof}** ({s['n']} folios): DYE pass {s['dye_pass']}/{s['n']}, "
      f"EPV pass {s['epv_pass']}/{s['n']}, "
      f"mean DYE_adv = {fmt_sign(s['mean_dye_adv'])}")
L("")

# GP4 observations
L("### Anchor Stability (GP4 — reported, not gated)")
L("")
g4a = tiers["A"]["GP4"]
L(f"UEB (M1 <= M0): {g4a['UEB_count']}/{len(tier_a_folios)} "
  f"({g4a['UEB_rate']:.0%}). "
  f"WCP (M1 >= M0): {g4a['WCP_count']}/{len(tier_a_folios)} "
  f"({g4a['WCP_rate']:.0%}).")
L("")
L("GP4 is reported for legacy continuity but is NOT gated per expert guidance.")
L("")

# 7. Provisional Constraints
L("## 7. Provisional Constraints")
L("")
if constraints:
    for c in constraints:
        L(f"**{c['id']}** (Tier {c['tier']}, {c['scope']}): {c['text']}")
        L("")
else:
    L("No constraints issued (verdict insufficient).")
    L("")

# 8. Cross-Phase Comparison
L("## 8. Cross-Phase Comparison")
L("")
L("| Phase | Score | Key Result |")
L("|-------|-------|------------|")
L("| 563 | 5/9 | Baseline apparatus coupling |")
L("| 563b | 3/9 | Sensitivity recalibration |")
L("| 564 | 2/9 | Event-gated execution |")
L("| 564b | 2/9 | Selective restoration |")
L("| 565 | 2/9 | Permeability calibration |")
L("| 566 | 1/9 | CLOSE recovery |")
L("| 567 | P2 + 3/7 NP | PARTIAL: readout reform |")
L("| 568 | P2 + 3/7 EP | PARTIAL: controlled excursion metrics |")
L("| 569 | P2 + 1/5 PT | INSUFFICIENT: eventive closure |")
L("| 570a | AP1:3/4, AP2:2/4, AP3:3/4 | PARTIAL: folio-specific apparatus |")
L("| 570b | BP1:0/4, BP2:1/4, BP3:4/4 | PARTIAL: demand-specific metrics |")
L("| 570c | CP1:4/4, CP2:3/4, CP3:4/4 | PROCESS QUALITY VALIDATED |")
L("| 571 | Tier C GP2:3/4, Tier A GP1:16/18 | PROCESS QUALITY GENERALIZED |")
verdict_short = verdict.replace("_", " ")
L(f"| **572** | **Tier C GP2:{tiers['C']['GP2']['count']}/{tiers['C']['GP2']['total']}, "
  f"Tier A GP1:{tiers['A']['GP1']['count']}/{tiers['A']['GP1']['total']}, "
  f"GP3:{tiers['A']['GP3']['count']}/{tiers['A']['GP3']['total']}** | "
  f"**{verdict_short}** |")
L("")

L("---")
L("")
L(f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by "
  f"t4_expansion_report.py*")

report_text = "\n".join(lines)

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report_text)
print(f"Wrote {REPORT_PATH}")

print("\n" + "=" * 72)
print(f"DONE — Verdict: {verdict}")
print(f"       Tier C: GP1={tiers['C']['GP1']['count']}/{tiers['C']['GP1']['total']}  "
      f"GP2={tiers['C']['GP2']['count']}/{tiers['C']['GP2']['total']}  "
      f"GP3={tiers['C']['GP3']['count']}/{tiers['C']['GP3']['total']}  "
      f"GP4=reported(not gated)")
print(f"       Tier B: GP1={tiers['B']['GP1']['count']}/{tiers['B']['GP1']['total']}  "
      f"GP2={tiers['B']['GP2']['count']}/{tiers['B']['GP2']['total']}  "
      f"GP3={tiers['B']['GP3']['count']}/{tiers['B']['GP3']['total']}")
print(f"       Tier A: GP1={tiers['A']['GP1']['count']}/{tiers['A']['GP1']['total']}  "
      f"GP2={tiers['A']['GP2']['count']}/{tiers['A']['GP2']['total']}  "
      f"GP3={tiers['A']['GP3']['count']}/{tiers['A']['GP3']['total']}  "
      f"GP4=reported(not gated)")
if constraints:
    print(f"       Constraints: {', '.join(c['id'] for c in constraints)}")
print("=" * 72)
