"""
T5: A2 Forgivingness Audit
Phase 572 - PRODUCTIVE_DISRUPTION_EXPANSION (Track B)

Analyzes why the A2_SEALED_RECIRCULATION profile washes out the grammar
advantage, using the same T1-T3 data as T4.

Core concept: Forgivingness Index (FI) = mean null DYE per profile.
If A2 FI is highest, the null model converts disruption into Y just as
well as the real grammar, erasing the DYE advantage.

Input:
  - t1_full_scale_setup.json  (folio configs, profiles, eligibility)
  - t2_full_model_runs.json   (M0/M1 per-event detail)
  - t3_null_runs.json         (M4f demand-matched null perms)

Output:
  - t5_a2_audit.json
  - REPORT_572_A2_AUDIT.md
"""

import json
import sys
import os
import math
import statistics
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
PHASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PHASE_DIR / "results"

# ---------------------------------------------------------------------------
# Load inputs
# ---------------------------------------------------------------------------
print("Loading T1, T2, T3 data...")
t1 = json.load(open(RESULTS_DIR / "t1_full_scale_setup.json"))
t2 = json.load(open(RESULTS_DIR / "t2_full_model_runs.json"))
t3 = json.load(open(RESULTS_DIR / "t3_null_runs.json"))

eligible_folios = t1["eligible_folios"]
folio_configs = t1["folio_configs"]
profiles_map = t1["summary"]["profiles"]  # profile -> list of folios

print(f"  Eligible folios: {len(eligible_folios)}")
print(f"  Profiles: {list(profiles_map.keys())}")

# ---------------------------------------------------------------------------
# Core helpers (same as T4)
# ---------------------------------------------------------------------------
PROCESS_SVS = [0, 1, 2, 3, 4, 5]


def aggregate_dev(state_vec):
    return sum(abs(state_vec[i] - 0.5) for i in PROCESS_SVS) / len(PROCESS_SVS)


def select_events(events):
    wp = [e for e in events if "work_preceded" in e.get("demand_qualifiers", [])]
    if len(wp) >= 2:
        return wp, "work_preceded"
    dem = [e for e in events if "demanded" in e.get("demand_qualifiers", [])]
    if len(dem) >= 2:
        return dem, "demanded"
    return events, "E_any"


def compute_dye(event):
    dv = event["dv_magnitude_sum"]
    if dv < 0.001:
        return 0.0
    return event["y_gain_event"] / dv


def mean_dv_per_event(event):
    if event["n_close_tokens"] == 0:
        return 0.0
    return event["dv_magnitude_sum"] / event["n_close_tokens"]


def safe_mean(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def safe_std(values):
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


# ---------------------------------------------------------------------------
# Step 1: Compute per-folio metrics (same pipeline as T4)
# ---------------------------------------------------------------------------
print("\n=== Step 1: Per-folio metric computation ===")

folio_metrics = {}

for folio in eligible_folios:
    cfg = folio_configs[folio]
    profile = cfg["profile"]
    section = cfg["section"]

    # M1 events
    if folio not in t2["primary_runs"]:
        continue
    m1_events = t2["primary_runs"][folio]["M1"]["per_event_detail"]
    sel_m1, tier_m1 = select_events(m1_events)

    if len(sel_m1) == 0:
        continue

    # Per-event M1 DYE and dV
    m1_dyes = [compute_dye(e) for e in sel_m1]
    m1_dvs = [mean_dv_per_event(e) for e in sel_m1]
    m1_dv_sums = [e["dv_magnitude_sum"] for e in sel_m1]
    m1_ygs = [e["y_gain_event"] for e in sel_m1]

    mean_m1_dye = safe_mean(m1_dyes)
    mean_m1_dv = safe_mean(m1_dvs)
    total_m1_dv = sum(m1_dv_sums)
    total_m1_yg = sum(m1_ygs)
    dva_m1 = safe_mean(m1_dv_sums)

    # M4f null DYE (mean across perms)
    if folio not in t3["m4f_demand_matched"]:
        continue
    all_perms = t3["m4f_demand_matched"][folio]["all_perms"]

    perm_mean_dyes = []
    perm_mean_dvs = []
    perm_mean_dv_sums = []
    for perm in all_perms:
        matched = perm["matched_events"]
        sel_null, _ = select_events(matched)
        if len(sel_null) == 0:
            continue
        null_dyes = [compute_dye(e) for e in sel_null]
        null_dvs = [mean_dv_per_event(e) for e in sel_null]
        null_dv_sums = [e["dv_magnitude_sum"] for e in sel_null]
        perm_mean_dyes.append(safe_mean(null_dyes))
        perm_mean_dvs.append(safe_mean(null_dvs))
        perm_mean_dv_sums.append(safe_mean(null_dv_sums))

    if len(perm_mean_dyes) == 0:
        continue

    mean_m4f_dye = safe_mean(perm_mean_dyes)
    mean_m4f_dv = safe_mean(perm_mean_dvs)
    dva_m4f = safe_mean(perm_mean_dv_sums)

    dye_advantage = mean_m1_dye - mean_m4f_dye

    # EPV (Event-level P-Value proxy: fraction of perms where null DYE < M1 DYE)
    n_below = sum(1 for pd in perm_mean_dyes if pd < mean_m1_dye)
    epv = n_below / len(perm_mean_dyes)

    # YGA: total Y gain advantage
    perm_yg_totals = []
    for perm in all_perms:
        matched = perm["matched_events"]
        sel_null, _ = select_events(matched)
        perm_yg_totals.append(sum(e["y_gain_event"] for e in sel_null))
    yga = total_m1_yg - safe_mean(perm_yg_totals)

    # DVA: disruption volume advantage
    dva = dva_m1 - dva_m4f

    # DYC: DYE consistency (std of M1 per-event DYEs)
    dyc = safe_std(m1_dyes)

    # Entry deviation (for mechanistic test)
    entry_devs = [aggregate_dev(e["close_pre_state"]) for e in sel_m1]
    mean_entry_dev = safe_mean(entry_devs)

    folio_metrics[folio] = {
        "profile": profile,
        "section": section,
        "eligibility_class": cfg["eligibility_class"],
        "n_events_m1": len(sel_m1),
        "selection_tier": tier_m1,
        "mean_m1_dye": mean_m1_dye,
        "mean_m4f_dye": mean_m4f_dye,
        "dye_advantage": dye_advantage,
        "epv": epv,
        "dva_m1": dva_m1,
        "dva_m4f": dva_m4f,
        "dva": dva,
        "mean_m1_dv": mean_m1_dv,
        "mean_m4f_dv": mean_m4f_dv,
        "mean_yga": yga,
        "dyc": dyc,
        "mean_entry_dev": mean_entry_dev,
        "F1": cfg["F1"],
        "F2": cfg["F2"],
        "F3": cfg["F3"],
        "F4_raw": cfg["F4_raw"],
        "F5": cfg["F5"],
    }

print(f"  Computed metrics for {len(folio_metrics)} folios")

# Group by profile
by_profile = defaultdict(list)
for folio, m in folio_metrics.items():
    by_profile[m["profile"]].append((folio, m))

for p, items in sorted(by_profile.items()):
    print(f"  {p}: {len(items)} folios")

# ---------------------------------------------------------------------------
# Step 2: Forgivingness Index (FI)
# ---------------------------------------------------------------------------
print("\n=== Step 2: Forgivingness Index (FI) ===")

fi_results = {}
for profile in sorted(by_profile.keys()):
    m4f_dyes = [m["mean_m4f_dye"] for _, m in by_profile[profile]]
    fi = safe_mean(m4f_dyes)
    fi_results[profile] = {
        "FI": round(fi, 6),
        "n_folios": len(m4f_dyes),
        "min": round(min(m4f_dyes), 6) if m4f_dyes else 0.0,
        "max": round(max(m4f_dyes), 6) if m4f_dyes else 0.0,
        "std": round(safe_std(m4f_dyes), 6),
    }
    print(f"  {profile}: FI={fi:.6f} (n={len(m4f_dyes)}, min={min(m4f_dyes):.4f}, max={max(m4f_dyes):.4f}, std={safe_std(m4f_dyes):.4f})")

# ---------------------------------------------------------------------------
# Step 3: DVA-DYE Decomposition by Profile
# ---------------------------------------------------------------------------
print("\n=== Step 3: DVA-DYE Decomposition ===")

dva_dye_decomp = {}
for profile in sorted(by_profile.keys()):
    items = by_profile[profile]
    result = {
        "mean_M1_dV": round(safe_mean([m["mean_m1_dv"] for _, m in items]), 6),
        "mean_M4f_dV": round(safe_mean([m["mean_m4f_dv"] for _, m in items]), 6),
        "mean_M1_DYE": round(safe_mean([m["mean_m1_dye"] for _, m in items]), 6),
        "mean_M4f_DYE": round(safe_mean([m["mean_m4f_dye"] for _, m in items]), 6),
        "mean_DYE_advantage": round(safe_mean([m["dye_advantage"] for _, m in items]), 6),
        "mean_DVA": round(safe_mean([m["dva"] for _, m in items]), 6),
        "mean_YGA": round(safe_mean([m["mean_yga"] for _, m in items]), 6),
        "mean_DVA_M1": round(safe_mean([m["dva_m1"] for _, m in items]), 6),
        "mean_DVA_M4f": round(safe_mean([m["dva_m4f"] for _, m in items]), 6),
        "n_folios": len(items),
    }
    dva_dye_decomp[profile] = result
    print(f"\n  {profile} (n={len(items)}):")
    print(f"    M1 dV/tok={result['mean_M1_dV']:.4f}  M4f dV/tok={result['mean_M4f_dV']:.4f}")
    print(f"    M1 DYE={result['mean_M1_DYE']:.4f}  M4f DYE={result['mean_M4f_DYE']:.4f}")
    print(f"    DYE advantage={result['mean_DYE_advantage']:.4f}")
    print(f"    DVA M1={result['mean_DVA_M1']:.4f}  DVA M4f={result['mean_DVA_M4f']:.4f}  net DVA={result['mean_DVA']:.4f}")
    print(f"    YGA={result['mean_YGA']:.4f}")

# ---------------------------------------------------------------------------
# Step 4: Section-Profile Interaction
# ---------------------------------------------------------------------------
print("\n=== Step 4: Section-Profile Interaction ===")

section_profile = defaultdict(list)
for folio, m in folio_metrics.items():
    key = f"{m['section']}|{m['profile']}"
    section_profile[key].append(m)

sp_results = {}
for key in sorted(section_profile.keys()):
    items = section_profile[key]
    n = len(items)
    dye_pass = sum(1 for m in items if m["dye_advantage"] > 0)
    epv_pass = sum(1 for m in items if m["epv"] >= 0.80)
    mean_dye_adv = safe_mean([m["dye_advantage"] for m in items])
    sp_results[key] = {
        "n": n,
        "dye_pass": dye_pass,
        "dye_pass_rate": round(dye_pass / n, 3) if n > 0 else 0,
        "epv_pass": epv_pass,
        "epv_pass_rate": round(epv_pass / n, 3) if n > 0 else 0,
        "mean_dye_adv": round(mean_dye_adv, 6),
    }
    print(f"  {key:40s} n={n:2d}  DYE_pass={dye_pass}/{n} ({dye_pass/n*100:.0f}%)  EPV_pass={epv_pass}/{n} ({epv_pass/n*100:.0f}%)  mean_DYE_adv={mean_dye_adv:.4f}")

# ---------------------------------------------------------------------------
# Step 5: Matched-Profile Audit
# ---------------------------------------------------------------------------
print("\n=== Step 5: Matched-Profile Audit ===")

# 5a: By event count bins
event_bins = {"1-2": (1, 2), "3-5": (3, 5), "6-10": (6, 10), "11+": (11, 999)}
by_event_bin = {}

for bin_name, (lo, hi) in event_bins.items():
    a2_items = [(f, m) for f, m in folio_metrics.items()
                if m["profile"] == "A2_SEALED_RECIRCULATION"
                and lo <= m["n_events_m1"] <= hi]
    non_a2_items = [(f, m) for f, m in folio_metrics.items()
                    if m["profile"] != "A2_SEALED_RECIRCULATION"
                    and lo <= m["n_events_m1"] <= hi]

    entry = {
        "A2": {
            "n": len(a2_items),
            "mean_FI": round(safe_mean([m["mean_m4f_dye"] for _, m in a2_items]), 6),
            "mean_DYE_adv": round(safe_mean([m["dye_advantage"] for _, m in a2_items]), 6),
            "mean_EPV": round(safe_mean([m["epv"] for _, m in a2_items]), 4),
        },
        "non_A2": {
            "n": len(non_a2_items),
            "mean_FI": round(safe_mean([m["mean_m4f_dye"] for _, m in non_a2_items]), 6),
            "mean_DYE_adv": round(safe_mean([m["dye_advantage"] for _, m in non_a2_items]), 6),
            "mean_EPV": round(safe_mean([m["epv"] for _, m in non_a2_items]), 4),
        },
    }
    by_event_bin[bin_name] = entry
    print(f"  Bin {bin_name}:")
    print(f"    A2     n={entry['A2']['n']:2d}  FI={entry['A2']['mean_FI']:.4f}  DYE_adv={entry['A2']['mean_DYE_adv']:.4f}  EPV={entry['A2']['mean_EPV']:.4f}")
    print(f"    non-A2 n={entry['non_A2']['n']:2d}  FI={entry['non_A2']['mean_FI']:.4f}  DYE_adv={entry['non_A2']['mean_DYE_adv']:.4f}  EPV={entry['non_A2']['mean_EPV']:.4f}")

# 5b: By eligibility class
print("\n  By eligibility class:")
elig_classes = sorted(set(m["eligibility_class"] for m in folio_metrics.values()))
by_eligibility = {}

for ec in elig_classes:
    a2_items = [(f, m) for f, m in folio_metrics.items()
                if m["profile"] == "A2_SEALED_RECIRCULATION"
                and m["eligibility_class"] == ec]
    non_a2_items = [(f, m) for f, m in folio_metrics.items()
                    if m["profile"] != "A2_SEALED_RECIRCULATION"
                    and m["eligibility_class"] == ec]

    entry = {
        "A2": {
            "n": len(a2_items),
            "mean_FI": round(safe_mean([m["mean_m4f_dye"] for _, m in a2_items]), 6),
            "mean_DYE_adv": round(safe_mean([m["dye_advantage"] for _, m in a2_items]), 6),
            "mean_EPV": round(safe_mean([m["epv"] for _, m in a2_items]), 4),
        },
        "non_A2": {
            "n": len(non_a2_items),
            "mean_FI": round(safe_mean([m["mean_m4f_dye"] for _, m in non_a2_items]), 6),
            "mean_DYE_adv": round(safe_mean([m["dye_advantage"] for _, m in non_a2_items]), 6),
            "mean_EPV": round(safe_mean([m["epv"] for _, m in non_a2_items]), 4),
        },
    }
    by_eligibility[ec] = entry
    print(f"    {ec:20s}  A2 n={entry['A2']['n']:2d} FI={entry['A2']['mean_FI']:.4f} DYE_adv={entry['A2']['mean_DYE_adv']:.4f} | non-A2 n={entry['non_A2']['n']:2d} FI={entry['non_A2']['mean_FI']:.4f} DYE_adv={entry['non_A2']['mean_DYE_adv']:.4f}")

# ---------------------------------------------------------------------------
# Step 6: Confound Tests
# ---------------------------------------------------------------------------
print("\n=== Step 6: Confound Tests ===")

confound_results = {}
for profile in sorted(by_profile.keys()):
    items = by_profile[profile]
    n_events = [m["n_events_m1"] for _, m in items]
    f1s = [m["F1"] for _, m in items]
    f2s = [m["F2"] for _, m in items]
    f3s = [m["F3"] for _, m in items]
    f4s = [m["F4_raw"] for _, m in items]
    f5s = [m["F5"] for _, m in items]
    dva_vals = [m["dva_m1"] for _, m in items]

    # Eligibility class distribution
    elig_dist = defaultdict(int)
    for _, m in items:
        elig_dist[m["eligibility_class"]] += 1

    # Selection tier distribution
    tier_dist = defaultdict(int)
    for _, m in items:
        tier_dist[m["selection_tier"]] += 1

    entry = {
        "mean_n_events": round(safe_mean(n_events), 2),
        "mean_F1": round(safe_mean(f1s), 4),
        "mean_F2": round(safe_mean(f2s), 4),
        "mean_F3": round(safe_mean(f3s), 4),
        "mean_F4_raw": round(safe_mean(f4s), 4),
        "mean_F5": round(safe_mean(f5s), 4),
        "mean_DVA_M1": round(safe_mean(dva_vals), 6),
        "eligibility_dist": dict(elig_dist),
        "selection_tier_dist": dict(tier_dist),
        "n_folios": len(items),
    }
    confound_results[profile] = entry
    print(f"\n  {profile} (n={len(items)}):")
    print(f"    mean n_events={entry['mean_n_events']:.1f}")
    print(f"    F1={entry['mean_F1']:.4f} F2={entry['mean_F2']:.4f} F3={entry['mean_F3']:.4f} F4={entry['mean_F4_raw']:.4f} F5={entry['mean_F5']:.4f}")
    print(f"    mean DVA(M1)={entry['mean_DVA_M1']:.4f}")
    print(f"    eligibility: {dict(elig_dist)}")
    print(f"    selection tiers: {dict(tier_dist)}")

# ---------------------------------------------------------------------------
# Step 7: Mechanistic Test — Entry Deviation
# ---------------------------------------------------------------------------
print("\n=== Step 7: Mechanistic Test (Entry Deviation) ===")

mech_results = {}
for profile in sorted(by_profile.keys()):
    items = by_profile[profile]
    entry_devs = [m["mean_entry_dev"] for _, m in items]
    mech_results[profile] = {
        "mean_entry_dev": round(safe_mean(entry_devs), 6),
        "min_entry_dev": round(min(entry_devs), 6) if entry_devs else 0.0,
        "max_entry_dev": round(max(entry_devs), 6) if entry_devs else 0.0,
        "std_entry_dev": round(safe_std(entry_devs), 6),
        "n_folios": len(entry_devs),
    }
    print(f"  {profile}: mean_entry_dev={safe_mean(entry_devs):.6f} (n={len(entry_devs)}, min={min(entry_devs):.4f}, max={max(entry_devs):.4f})")

# ---------------------------------------------------------------------------
# Interpretation
# ---------------------------------------------------------------------------
print("\n=== Interpretation ===")

# Determine which profile has highest FI
fi_vals = {p: fi_results[p]["FI"] for p in fi_results}
max_fi_profile = max(fi_vals, key=fi_vals.get)
min_fi_profile = min(fi_vals, key=fi_vals.get)

# Determine A2 DYE advantage relative to others
a2_dye_adv = dva_dye_decomp.get("A2_SEALED_RECIRCULATION", {}).get("mean_DYE_advantage", 0)
a1_dye_adv = dva_dye_decomp.get("A1_BATH_REFLUX", {}).get("mean_DYE_advantage", 0)
a3_dye_adv = dva_dye_decomp.get("A3_DISTILL_COLLECT", {}).get("mean_DYE_advantage", 0)

# A2 entry deviation
a2_entry = mech_results.get("A2_SEALED_RECIRCULATION", {}).get("mean_entry_dev", 0)
a1_entry = mech_results.get("A1_BATH_REFLUX", {}).get("mean_entry_dev", 0)
a3_entry = mech_results.get("A3_DISTILL_COLLECT", {}).get("mean_entry_dev", 0)

interp_parts = []
interp_parts.append(f"Highest FI (null forgivingness): {max_fi_profile} at FI={fi_vals[max_fi_profile]:.4f}.")
interp_parts.append(f"Lowest FI: {min_fi_profile} at FI={fi_vals[min_fi_profile]:.4f}.")
interp_parts.append(f"DYE advantages: A1={a1_dye_adv:.4f}, A2={a2_dye_adv:.4f}, A3={a3_dye_adv:.4f}.")
interp_parts.append(f"Entry deviation: A1={a1_entry:.4f}, A2={a2_entry:.4f}, A3={a3_entry:.4f}.")

if max_fi_profile == "A2_SEALED_RECIRCULATION":
    interp_parts.append("CONFIRMED: A2 has the highest null forgivingness — random disruption converts to Y most easily in A2 folios, washing out the grammar advantage.")
else:
    interp_parts.append(f"UNEXPECTED: {max_fi_profile} has highest FI, not A2. The A2 washout may be driven by other factors.")

if a2_entry < min(a1_entry, a3_entry):
    interp_parts.append("A2 folios enter CLOSE lines with smallest state deviations, consistent with sealed recirculation suppressing perturbations.")
elif a2_entry > max(a1_entry, a3_entry):
    interp_parts.append("A2 folios enter CLOSE lines with LARGEST state deviations — the apparatus is not suppressing perturbations; the null just converts them well.")

interpretation = " ".join(interp_parts)
print(f"\n  {interpretation}")

# ---------------------------------------------------------------------------
# Build output JSON
# ---------------------------------------------------------------------------
output = {
    "metadata": {
        "phase": "572",
        "script": "t5_a2_forgivingness_audit.py",
        "track": "B",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_folios_analyzed": len(folio_metrics),
        "n_eligible": len(eligible_folios),
    },
    "forgivingness_index": fi_results,
    "dva_dye_decomposition": dva_dye_decomp,
    "section_profile_interaction": sp_results,
    "matched_profile_audit": {
        "by_event_bin": by_event_bin,
        "by_eligibility": by_eligibility,
    },
    "confound_tests": confound_results,
    "mechanistic_test": mech_results,
    "per_folio_metrics": {
        f: {k: round(v, 6) if isinstance(v, float) else v for k, v in m.items()}
        for f, m in folio_metrics.items()
    },
    "interpretation": interpretation,
}

out_path = RESULTS_DIR / "t5_a2_audit.json"
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nJSON written to {out_path}")

# ---------------------------------------------------------------------------
# Generate report
# ---------------------------------------------------------------------------
report_lines = []
report_lines.append("# REPORT 572: A2 Forgivingness Audit (T5)")
report_lines.append("")
report_lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}")
report_lines.append(f"**Folios analyzed:** {len(folio_metrics)} / {len(eligible_folios)} eligible")
report_lines.append("")
report_lines.append("## 1. Forgivingness Index (FI)")
report_lines.append("")
report_lines.append("FI = mean null DYE (M4f) per profile. Higher FI means the null model")
report_lines.append("converts random disruption into Y-gain more easily, erasing grammar advantage.")
report_lines.append("")
report_lines.append("| Profile | FI | n | min | max | std |")
report_lines.append("|---------|-----|---|-----|-----|-----|")
for p in sorted(fi_results.keys()):
    r = fi_results[p]
    report_lines.append(f"| {p} | {r['FI']:.4f} | {r['n_folios']} | {r['min']:.4f} | {r['max']:.4f} | {r['std']:.4f} |")
report_lines.append("")

report_lines.append("## 2. DVA-DYE Decomposition")
report_lines.append("")
report_lines.append("| Profile | n | M1 dV/tok | M4f dV/tok | M1 DYE | M4f DYE | DYE adv | DVA M1 | DVA M4f | YGA |")
report_lines.append("|---------|---|-----------|------------|--------|---------|---------|--------|---------|-----|")
for p in sorted(dva_dye_decomp.keys()):
    r = dva_dye_decomp[p]
    report_lines.append(
        f"| {p} | {r['n_folios']} | {r['mean_M1_dV']:.4f} | {r['mean_M4f_dV']:.4f} | "
        f"{r['mean_M1_DYE']:.4f} | {r['mean_M4f_DYE']:.4f} | {r['mean_DYE_advantage']:.4f} | "
        f"{r['mean_DVA_M1']:.4f} | {r['mean_DVA_M4f']:.4f} | {r['mean_YGA']:.4f} |"
    )
report_lines.append("")

report_lines.append("## 3. Section-Profile Interaction")
report_lines.append("")
report_lines.append("| Section|Profile | n | DYE pass | DYE pass% | EPV pass | EPV pass% | mean DYE adv |")
report_lines.append("|--------|---|----------|-----------|----------|-----------|--------------|")
for key in sorted(sp_results.keys()):
    r = sp_results[key]
    report_lines.append(
        f"| {key} | {r['n']} | {r['dye_pass']} | {r['dye_pass_rate']*100:.0f}% | "
        f"{r['epv_pass']} | {r['epv_pass_rate']*100:.0f}% | {r['mean_dye_adv']:.4f} |"
    )
report_lines.append("")

report_lines.append("## 4. Matched-Profile Audit")
report_lines.append("")
report_lines.append("### By Event Count Bin")
report_lines.append("")
report_lines.append("| Bin | A2 n | A2 FI | A2 DYE adv | A2 EPV | non-A2 n | non-A2 FI | non-A2 DYE adv | non-A2 EPV |")
report_lines.append("|-----|------|-------|------------|--------|----------|-----------|----------------|------------|")
for bin_name in ["1-2", "3-5", "6-10", "11+"]:
    r = by_event_bin[bin_name]
    a2 = r["A2"]
    na2 = r["non_A2"]
    report_lines.append(
        f"| {bin_name} | {a2['n']} | {a2['mean_FI']:.4f} | {a2['mean_DYE_adv']:.4f} | {a2['mean_EPV']:.4f} | "
        f"{na2['n']} | {na2['mean_FI']:.4f} | {na2['mean_DYE_adv']:.4f} | {na2['mean_EPV']:.4f} |"
    )
report_lines.append("")

report_lines.append("### By Eligibility Class")
report_lines.append("")
report_lines.append("| Class | A2 n | A2 FI | A2 DYE adv | non-A2 n | non-A2 FI | non-A2 DYE adv |")
report_lines.append("|-------|------|-------|------------|----------|-----------|----------------|")
for ec in sorted(by_eligibility.keys()):
    r = by_eligibility[ec]
    a2 = r["A2"]
    na2 = r["non_A2"]
    report_lines.append(
        f"| {ec} | {a2['n']} | {a2['mean_FI']:.4f} | {a2['mean_DYE_adv']:.4f} | "
        f"{na2['n']} | {na2['mean_FI']:.4f} | {na2['mean_DYE_adv']:.4f} |"
    )
report_lines.append("")

report_lines.append("## 5. Confound Tests")
report_lines.append("")
report_lines.append("| Profile | n | mean n_events | F1 | F2 | F3 | F4 | F5 | DVA(M1) |")
report_lines.append("|---------|---|---------------|-----|-----|-----|-----|-----|---------|")
for p in sorted(confound_results.keys()):
    r = confound_results[p]
    report_lines.append(
        f"| {p} | {r['n_folios']} | {r['mean_n_events']:.1f} | "
        f"{r['mean_F1']:.3f} | {r['mean_F2']:.3f} | {r['mean_F3']:.3f} | "
        f"{r['mean_F4_raw']:.3f} | {r['mean_F5']:.3f} | {r['mean_DVA_M1']:.4f} |"
    )
report_lines.append("")

report_lines.append("## 6. Mechanistic Test (Entry Deviation)")
report_lines.append("")
report_lines.append("Mean |state deviation| at CLOSE line entry. Smaller values mean the system")
report_lines.append("is closer to equilibrium (0.5) when disruption begins.")
report_lines.append("")
report_lines.append("| Profile | mean entry dev | min | max | std | n |")
report_lines.append("|---------|----------------|-----|-----|-----|---|")
for p in sorted(mech_results.keys()):
    r = mech_results[p]
    report_lines.append(
        f"| {p} | {r['mean_entry_dev']:.4f} | {r['min_entry_dev']:.4f} | "
        f"{r['max_entry_dev']:.4f} | {r['std_entry_dev']:.4f} | {r['n_folios']} |"
    )
report_lines.append("")

report_lines.append("## 7. Interpretation")
report_lines.append("")
report_lines.append(interpretation)
report_lines.append("")

report_path = PHASE_DIR / "REPORT_572_A2_AUDIT.md"
with open(report_path, "w") as f:
    f.write("\n".join(report_lines))
print(f"Report written to {report_path}")

print("\nDone.")
