"""
Phase 567 T1: Closure Field Audit

Pure data analysis — reads existing results and produces diagnostic statistics
for the closure scoring system (CTS, closure components, COF prototypes).

Seven analyses:
  A1. CTS Distribution
  A2. CLOSE Window Characterization
  A3. Closure Component Audit
  A4. CTS-Excursion Timing
  A5. S Asymmetry Audit
  A6. COF Prototype Family
  A7. Closure-Window Overlap Efficiency
"""

import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats as scipy_stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[3]

SUPERVISORY_PATH = ROOT / "phases" / "VIRTUAL_APPARATUS_COUPLING" / "results" / "t2b_supervisory_interface_unrouted.json"
LINE_PACKETS_PATH = ROOT / "phases" / "SECTION_TEMPLATE_TRACE_EXECUTOR" / "results" / "t3_line_packets.json"
CTS_PATH = ROOT / "phases" / "SECTION_TEMPLATE_TRACE_EXECUTOR" / "results" / "t7_closure_cts.json"
CLOSE_RECOVERY_PATH = ROOT / "phases" / "VIRTUAL_APPARATUS_CLOSE_RECOVERY" / "results" / "t2_close_recovery_runs.json"
OUTPUT_PATH = ROOT / "phases" / "CLOSURE_FIELD_AUDIT" / "results" / "t1_closure_field_audit.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def r5(x):
    """Round to 5 decimal places for JSON output."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(float(x), 5)


def rank_biserial(u, n1, n2):
    """Rank-biserial effect size from Mann-Whitney U."""
    return r5(1 - 2 * u / (n1 * n2)) if n1 * n2 > 0 else None


# ===========================================================================
# Load data
# ===========================================================================
print("Loading data files...")
sup_data = load_json(SUPERVISORY_PATH)
lp_data = load_json(LINE_PACKETS_PATH)
cts_data = load_json(CTS_PATH)
cr_data = load_json(CLOSE_RECOVERY_PATH)

tokens = sup_data["token_signals"]
line_packets = lp_data["line_packets"]
line_cts = cts_data["line_cts"]

n_tokens = len(tokens)
n_lines = len(line_packets)
print(f"  Tokens: {n_tokens}, Lines: {n_lines}")

# ===========================================================================
# Build lookup structures
# ===========================================================================

# Map each line key -> CTS value
line_cts_map = {k: v["cts"] for k, v in line_cts.items()}

# Map each line key -> packet_phase from line_packets
line_phase_map = {}
line_section_map = {}
line_n_tokens_map = {}
for k, lp in line_packets.items():
    line_phase_map[k] = lp["packet_state"]["packet_phase"]
    line_section_map[k] = lp["section"]
    line_n_tokens_map[k] = lp["n_tokens"]

# Per-folio sorted line keys
folio_lines = defaultdict(list)
for k, lp in line_packets.items():
    folio = lp["folio"]
    line_num = lp["line"]
    # Parse line number for sorting (handle numeric lines)
    try:
        ln = int(line_num)
    except ValueError:
        ln = 0
    folio_lines[folio].append((ln, k))

for folio in folio_lines:
    folio_lines[folio].sort(key=lambda x: x[0])

# Tokens grouped by (folio, line)
tokens_by_line = defaultdict(list)
for t in tokens:
    key = f"{t['folio']}|{t['line']}"
    tokens_by_line[key].append(t)


# ===========================================================================
# A1. CTS Distribution
# ===========================================================================
print("\nA1. CTS Distribution...")

all_cts = []
section_cts = defaultdict(list)
phase_cts = defaultdict(list)
folio_cts = defaultdict(list)

for k in line_packets:
    cts_val = line_cts_map.get(k)
    if cts_val is None:
        continue
    all_cts.append(cts_val)
    sec = line_section_map.get(k)
    phase = line_phase_map.get(k)
    folio = line_packets[k]["folio"]
    if sec:
        section_cts[sec].append(cts_val)
    if phase:
        phase_cts[phase].append(cts_val)
    folio_cts[folio].append(cts_val)

# Global histogram
bin_edges = [round(i * 0.1, 1) for i in range(11)]  # 0.0 .. 1.0


def histogram(values, edges):
    counts = [0] * (len(edges) - 1)
    for v in values:
        for i in range(len(edges) - 1):
            if edges[i] <= v < edges[i + 1]:
                counts[i] += 1
                break
        else:
            # Handle v == 1.0 -> last bin
            if v >= edges[-1]:
                counts[-1] += 1
    labels = [f"{edges[i]:.1f}-{edges[i+1]:.1f}" for i in range(len(edges) - 1)]
    return dict(zip(labels, counts))


global_hist = histogram(all_cts, bin_edges)

# Per-section histograms
section_hists = {}
for sec in sorted(section_cts.keys()):
    section_hists[sec] = histogram(section_cts[sec], bin_edges)

# Per-phase histograms
phase_hists = {}
for phase in sorted(phase_cts.keys()):
    phase_hists[phase] = histogram(phase_cts[phase], bin_edges)

# Fraction of CLOSE lines with CTS > thresholds
close_vals = phase_cts.get("CLOSE", [])
n_close = len(close_vals)
close_gt_03 = sum(1 for v in close_vals if v > 0.3) / n_close if n_close else 0
close_gt_05 = sum(1 for v in close_vals if v > 0.5) / n_close if n_close else 0

# Fraction of ALL lines
n_all = len(all_cts)
all_gt_03 = sum(1 for v in all_cts if v > 0.3) / n_all if n_all else 0
all_gt_05 = sum(1 for v in all_cts if v > 0.5) / n_all if n_all else 0

# Section B deficit
b_mean = np.mean(section_cts.get("B", [0])) if section_cts.get("B") else 0.0
non_b_vals = [v for sec, vals in section_cts.items() if sec != "B" for v in vals]
non_b_mean = np.mean(non_b_vals) if non_b_vals else 0.0

# Per-folio mean CTS: top 5 and bottom 5
folio_means = {f: np.mean(vals) for f, vals in folio_cts.items()}
sorted_folios = sorted(folio_means.items(), key=lambda x: x[1])
bottom_5 = [(f, r5(v)) for f, v in sorted_folios[:5]]
top_5 = [(f, r5(v)) for f, v in sorted_folios[-5:]]

a1_result = {
    "global_histogram": global_hist,
    "n_lines": n_all,
    "global_mean_cts": r5(np.mean(all_cts)),
    "global_median_cts": r5(np.median(all_cts)),
    "section_histograms": section_hists,
    "section_means": {s: r5(np.mean(v)) for s, v in sorted(section_cts.items())},
    "section_counts": {s: len(v) for s, v in sorted(section_cts.items())},
    "phase_histograms": phase_hists,
    "phase_means": {p: r5(np.mean(v)) for p, v in sorted(phase_cts.items())},
    "phase_counts": {p: len(v) for p, v in sorted(phase_cts.items())},
    "close_frac_gt_03": r5(close_gt_03),
    "close_frac_gt_05": r5(close_gt_05),
    "all_frac_gt_03": r5(all_gt_03),
    "all_frac_gt_05": r5(all_gt_05),
    "section_B_mean_cts": r5(b_mean),
    "non_B_mean_cts": r5(non_b_mean),
    "b_deficit": r5(b_mean - non_b_mean),
    "per_folio_top5_highest": top_5,
    "per_folio_bottom5_lowest": bottom_5,
}

print(f"  Global mean CTS: {a1_result['global_mean_cts']}")
print(f"  CLOSE lines CTS>0.3: {a1_result['close_frac_gt_03']}")
print(f"  B deficit: {a1_result['b_deficit']}")


# ===========================================================================
# A2. CLOSE Window Characterization
# ===========================================================================
print("\nA2. CLOSE Window Characterization...")

# CLOSE line count per folio
close_count_per_folio = defaultdict(int)
for k, lp in line_packets.items():
    if lp["packet_state"]["packet_phase"] == "CLOSE":
        close_count_per_folio[lp["folio"]] += 1

# Consecutive CLOSE runs per folio
close_run_lengths_per_folio = {}
for folio, lines in folio_lines.items():
    run_lengths = []
    current_run = 0
    for _ln, k in lines:
        phase = line_phase_map.get(k)
        if phase == "CLOSE":
            current_run += 1
        else:
            if current_run > 0:
                run_lengths.append(current_run)
            current_run = 0
    if current_run > 0:
        run_lengths.append(current_run)
    if run_lengths:
        close_run_lengths_per_folio[folio] = {
            "n_runs": len(run_lengths),
            "mean_run_length": r5(np.mean(run_lengths)),
            "max_run_length": max(run_lengths),
        }

all_run_lengths = []
for folio, info in close_run_lengths_per_folio.items():
    all_run_lengths.extend([info["mean_run_length"]] * info["n_runs"])

# CLOSE token density per folio
close_token_density = {}
for folio, lines in folio_lines.items():
    total_tokens = 0
    close_tokens = 0
    for _ln, k in lines:
        nt = line_n_tokens_map.get(k, 0)
        total_tokens += nt
        if line_phase_map.get(k) == "CLOSE":
            close_tokens += nt
    if total_tokens > 0:
        close_token_density[folio] = r5(close_tokens / total_tokens)

# Per-phase mean |contribution| by SV
sv_names = ["T", "RC", "S", "C", "TR", "X", "Y"]
phase_sv_magnitudes = defaultdict(lambda: defaultdict(list))

for t in tokens:
    key = f"{t['folio']}|{t['line']}"
    phase = line_phase_map.get(key)
    if phase is None:
        continue
    contribs = t.get("contributions")
    if contribs is None:
        continue
    for i, sv in enumerate(sv_names):
        phase_sv_magnitudes[phase][sv].append(abs(contribs[i]))

phase_sv_means = {}
for phase in sorted(phase_sv_magnitudes.keys()):
    phase_sv_means[phase] = {
        sv: r5(np.mean(phase_sv_magnitudes[phase][sv]))
        for sv in sv_names
        if phase_sv_magnitudes[phase][sv]
    }

a2_result = {
    "close_count_per_folio": dict(sorted(close_count_per_folio.items())),
    "n_folios_with_close": len(close_count_per_folio),
    "total_close_lines": sum(close_count_per_folio.values()),
    "close_run_stats": {
        "n_folios_with_runs": len(close_run_lengths_per_folio),
        "global_mean_run_length": r5(np.mean(all_run_lengths)) if all_run_lengths else None,
    },
    "close_token_density_summary": {
        "mean": r5(np.mean(list(close_token_density.values()))) if close_token_density else None,
        "median": r5(np.median(list(close_token_density.values()))) if close_token_density else None,
    },
    "per_phase_mean_abs_contribution_by_sv": phase_sv_means,
}

print(f"  Total CLOSE lines: {a2_result['total_close_lines']}")
print(f"  Folios with CLOSE: {a2_result['n_folios_with_close']}")
print(f"  Phase contribution magnitudes (CLOSE vs WORK):")
for sv in sv_names:
    close_v = phase_sv_means.get("CLOSE", {}).get(sv, "N/A")
    work_v = phase_sv_means.get("WORK", {}).get(sv, "N/A")
    print(f"    {sv}: CLOSE={close_v}, WORK={work_v}")


# ===========================================================================
# A3. Closure Component Audit
# ===========================================================================
print("\nA3. Closure Component Audit...")

component_names = ["closure_armed", "q4_shift_strength", "close_opacity_bias", "m_close_bias", "q4_opaque_rate"]

# Extract per-line component values
line_components = {}
for k, lp in line_packets.items():
    ps = lp["packet_state"]
    prof = lp["profile"]
    armed_val = 1.0 if ps.get("closure_armed", False) else 0.0
    line_components[k] = {
        "closure_armed": armed_val,
        "q4_shift_strength": ps.get("q4_shift_strength", 0.0),
        "close_opacity_bias": ps.get("close_opacity_bias", 0.0),
        "m_close_bias": ps.get("m_close_bias", 0.0),
        "q4_opaque_rate": prof[14] if len(prof) > 14 else 0.0,
    }

# Build arrays for correlation matrix (6x6: 5 components + CTS)
all_names = component_names + ["cts"]
n_vars = len(all_names)

# Gather aligned arrays
arrays = {name: [] for name in all_names}
line_keys_ordered = [k for k in line_packets if k in line_components and k in line_cts_map]

for k in line_keys_ordered:
    comp = line_components[k]
    for name in component_names:
        arrays[name].append(comp[name])
    arrays["cts"].append(line_cts_map[k])

# Pearson correlation matrix
corr_matrix = {}
for i, n1 in enumerate(all_names):
    row = {}
    for j, n2 in enumerate(all_names):
        if len(arrays[n1]) > 2 and len(arrays[n2]) > 2:
            r_val, _ = scipy_stats.pearsonr(arrays[n1], arrays[n2])
            row[n2] = r5(r_val)
        else:
            row[n2] = None
    corr_matrix[n1] = row

# Mann-Whitney U: CLOSE vs WORK for each component
mwu_results = {}
close_keys = [k for k in line_keys_ordered if line_phase_map.get(k) == "CLOSE"]
work_keys = [k for k in line_keys_ordered if line_phase_map.get(k) == "WORK"]

for name in component_names + ["cts"]:
    close_vals_c = []
    work_vals_c = []
    for k in close_keys:
        if name == "cts":
            close_vals_c.append(line_cts_map[k])
        else:
            close_vals_c.append(line_components[k][name])
    for k in work_keys:
        if name == "cts":
            work_vals_c.append(line_cts_map[k])
        else:
            work_vals_c.append(line_components[k][name])

    if len(close_vals_c) > 0 and len(work_vals_c) > 0:
        u_stat, p_val = scipy_stats.mannwhitneyu(close_vals_c, work_vals_c, alternative="two-sided")
        mwu_results[name] = {
            "U": r5(u_stat),
            "p_value": float(f"{p_val:.6e}"),
            "n_close": len(close_vals_c),
            "n_work": len(work_vals_c),
            "rank_biserial": rank_biserial(u_stat, len(close_vals_c), len(work_vals_c)),
            "significant_001": bool(p_val < 0.01),
        }
    else:
        mwu_results[name] = {"U": None, "p_value": None}

# Per-section mean for each component
section_component_means = {}
for sec in sorted(section_cts.keys()):
    sec_keys = [k for k in line_keys_ordered if line_section_map.get(k) == sec]
    sec_means = {}
    for name in component_names:
        vals = [line_components[k][name] for k in sec_keys]
        sec_means[name] = r5(np.mean(vals)) if vals else None
    section_component_means[sec] = sec_means

# Which components have p < 0.01
significant_components = [name for name, res in mwu_results.items() if res.get("significant_001")]

a3_result = {
    "correlation_matrix": corr_matrix,
    "mann_whitney_close_vs_work": mwu_results,
    "per_section_component_means": section_component_means,
    "significant_close_vs_work_p001": significant_components,
}

print(f"  Significant CLOSE vs WORK discriminators (p<0.01): {significant_components}")
print(f"  Correlation CTS-closure_armed: {corr_matrix['cts']['closure_armed']}")
print(f"  Correlation CTS-q4_opaque_rate: {corr_matrix['cts']['q4_opaque_rate']}")


# ===========================================================================
# A4. CTS-Excursion Timing
# ===========================================================================
print("\nA4. CTS-Excursion Timing...")

# Per-line mean |contribution| magnitude
line_mean_abs_contrib = {}
for k, tok_list in tokens_by_line.items():
    if not tok_list:
        continue
    line_total = 0.0
    n = 0
    for t in tok_list:
        contribs = t.get("contributions")
        if contribs:
            line_total += sum(abs(c) for c in contribs)
            n += 1
    if n > 0:
        line_mean_abs_contrib[k] = line_total / n

# Compute P75 of WORK-line mean_abs_contribution
work_line_contribs = [line_mean_abs_contrib[k] for k in work_keys if k in line_mean_abs_contrib]
p75_work = float(np.percentile(work_line_contribs, 75)) if work_line_contribs else 0.0

# For each CLOSE line, find immediately preceding WORK line
close_preceding_work = []  # (close_key, close_cts, preceding_work_key, preceding_work_mag)

for folio, lines in folio_lines.items():
    for idx in range(len(lines)):
        _ln, k = lines[idx]
        if line_phase_map.get(k) != "CLOSE":
            continue
        # Look backward for immediately preceding WORK line
        if idx > 0:
            _pln, pk = lines[idx - 1]
            if line_phase_map.get(pk) == "WORK" and pk in line_mean_abs_contrib:
                close_preceding_work.append((
                    k,
                    line_cts_map.get(k, 0.0),
                    pk,
                    line_mean_abs_contrib[pk],
                ))

# Fraction of CLOSE lines that follow high-excursion WORK line
n_close_with_preceding = len(close_preceding_work)
n_high_excursion_preceding = sum(1 for _, _, _, mag in close_preceding_work if mag > p75_work)
frac_high_excursion = n_high_excursion_preceding / n_close_with_preceding if n_close_with_preceding else 0.0

# Spearman correlation between preceding WORK |contribution| and CLOSE CTS
if n_close_with_preceding > 2:
    preceding_mags = [mag for _, _, _, mag in close_preceding_work]
    close_cts_vals = [cts for _, cts, _, _ in close_preceding_work]
    spearman_r, spearman_p = scipy_stats.spearmanr(preceding_mags, close_cts_vals)
else:
    spearman_r, spearman_p = None, None

# Fraction of "high WORK -> high CTS CLOSE" transitions
n_high_work_high_close = sum(
    1 for _, cts, _, mag in close_preceding_work
    if mag > p75_work and cts > 0.3
)
frac_high_both = n_high_work_high_close / n_close_with_preceding if n_close_with_preceding else 0.0

a4_result = {
    "p75_work_contribution": r5(p75_work),
    "n_close_with_preceding_work": n_close_with_preceding,
    "n_high_excursion_preceding": n_high_excursion_preceding,
    "frac_close_following_high_excursion_work": r5(frac_high_excursion),
    "spearman_preceding_work_vs_close_cts": {
        "r": r5(spearman_r) if spearman_r is not None else None,
        "p_value": float(f"{spearman_p:.6e}") if spearman_p is not None else None,
    },
    "n_high_work_high_close_transitions": n_high_work_high_close,
    "frac_high_work_high_close": r5(frac_high_both),
    "total_close_lines": len(close_keys),
}

print(f"  P75 WORK |contribution|: {a4_result['p75_work_contribution']}")
print(f"  Frac CLOSE following high-excursion WORK: {a4_result['frac_close_following_high_excursion_work']}")
print(f"  Spearman r (preceding WORK mag vs CLOSE CTS): {a4_result['spearman_preceding_work_vs_close_cts']['r']}")
print(f"  Frac high WORK -> high CTS CLOSE: {a4_result['frac_high_work_high_close']}")


# ===========================================================================
# A5. S Asymmetry Audit
# ===========================================================================
print("\nA5. S Asymmetry Audit...")

runs = cr_data["runs"]

# Separate primary vs ablation
primary_runs = {k: v for k, v in runs.items() if not k.startswith("ABL_")}
ablation_runs = {k: v for k, v in runs.items() if k.startswith("ABL_")}

# Aggregate S zone occupancy across primary runs
s_zone_agg = {"basin": [], "corridor": [], "warning": [], "hard_stop": []}
all_sv_warning_hard_stop = defaultdict(list)  # sv -> list of (warning + hard_stop) fracs

for k, run in primary_runs.items():
    zo = run.get("zone_occupancy", {})
    s_zo = zo.get("S", {})
    for zone in s_zone_agg:
        s_zone_agg[zone].append(s_zo.get(zone, 0.0))

    # Aggregate all SVs warning+hard_stop for share calculation
    for sv in sv_names:
        sv_zo = zo.get(sv, {})
        whs = sv_zo.get("warning", 0.0) + sv_zo.get("hard_stop", 0.0)
        all_sv_warning_hard_stop[sv].append(whs)

s_mean_zone = {zone: r5(np.mean(vals)) for zone, vals in s_zone_agg.items()}

# S's share of total warning+hard_stop
total_whs_per_run = []
s_whs_per_run = []
for i in range(len(list(primary_runs.keys()))):
    total = sum(all_sv_warning_hard_stop[sv][i] for sv in sv_names)
    s_val = all_sv_warning_hard_stop["S"][i]
    total_whs_per_run.append(total)
    s_whs_per_run.append(s_val)

s_share = r5(np.mean([s / t if t > 0 else 0.0 for s, t in zip(s_whs_per_run, total_whs_per_run)]))

# Per-SV mean zone occupancy
per_sv_mean_zones = {}
for sv in sv_names:
    sv_data = {"basin": [], "corridor": [], "warning": [], "hard_stop": []}
    for k, run in primary_runs.items():
        zo = run.get("zone_occupancy", {}).get(sv, {})
        for zone in sv_data:
            sv_data[zone].append(zo.get(zone, 0.0))
    per_sv_mean_zones[sv] = {zone: r5(np.mean(vals)) for zone, vals in sv_data.items()}

# One-sided estimate: S has upward drift tendency so most warning/hard_stop is above EQ
# Report what we have and note the limitation
s_warning_mean = s_mean_zone["warning"]
s_hard_stop_mean = s_mean_zone["hard_stop"]

a5_result = {
    "n_primary_runs": len(primary_runs),
    "n_ablation_runs": len(ablation_runs),
    "s_mean_zone_occupancy": s_mean_zone,
    "s_warning_plus_hard_stop": r5(s_warning_mean + s_hard_stop_mean) if s_warning_mean and s_hard_stop_mean else None,
    "s_share_of_total_warning_hard_stop": s_share,
    "per_sv_mean_zone_occupancy": per_sv_mean_zones,
    "one_sided_note": (
        "S's upward drift tendency means most warning/hard_stop contacts are above EQ. "
        "Existing data does not break down above/below EQ. T2/T3 will compute one-sided version. "
        "If one-sided scoring reduces S warning/hard_stop by ~50%, S's share drops proportionally."
    ),
    "estimated_one_sided_s_warning_hard_stop": r5((s_warning_mean + s_hard_stop_mean) * 0.5),
}

print(f"  S mean zone occupancy: {s_mean_zone}")
print(f"  S share of total warning+hard_stop: {s_share}")
print(f"  Per-SV warning+hard_stop:")
for sv in sv_names:
    whs = per_sv_mean_zones[sv]["warning"] + per_sv_mean_zones[sv]["hard_stop"]
    print(f"    {sv}: {r5(whs)}")


# ===========================================================================
# A6. COF Prototype Family
# ===========================================================================
print("\nA6. COF Prototype Family...")

# Compute per-section P90 for normalization of raw components
# Components to normalize: q4_opaque_rate, m_close_bias, close_opacity_bias, q4_shift_strength
norm_components = ["q4_opaque_rate", "m_close_bias", "close_opacity_bias", "q4_shift_strength"]

section_p90 = {}
for sec in sorted(section_cts.keys()):
    sec_keys = [k for k in line_keys_ordered if line_section_map.get(k) == sec]
    p90_vals = {}
    for comp_name in norm_components:
        vals = [line_components[k][comp_name] for k in sec_keys]
        if vals:
            p90 = float(np.percentile(vals, 90))
            p90_vals[comp_name] = p90 if p90 > 0 else 1.0  # Avoid div by zero
        else:
            p90_vals[comp_name] = 1.0
    section_p90[sec] = p90_vals


def norm(val, comp_name, section):
    """Normalize a component value using per-section P90."""
    p90 = section_p90.get(section, {}).get(comp_name, 1.0)
    return min(val / p90, 1.0) if p90 > 0 else 0.0


# Compute COF variants for each line
line_cof = {}
for k in line_keys_ordered:
    cts = line_cts_map[k]
    comp = line_components[k]
    sec = line_section_map.get(k, "B")

    nq4 = norm(comp["q4_opaque_rate"], "q4_opaque_rate", sec)
    nmcb = norm(comp["m_close_bias"], "m_close_bias", sec)
    ncob = norm(comp["close_opacity_bias"], "close_opacity_bias", sec)
    nq4s = norm(comp["q4_shift_strength"], "q4_shift_strength", sec)

    cof1 = 0.6 * cts + 0.4 * nq4
    cof2 = 0.5 * cts + 0.25 * nq4 + 0.25 * nmcb
    cof3 = 0.3 * cts + 0.2 * nq4s + 0.2 * ncob + 0.3 * nmcb

    line_cof[k] = {
        "cts": cts,
        "cof1": cof1,
        "cof2": cof2,
        "cof3": cof3,
    }

# Build preceding WORK lookup for excursion-window overlap
# close_preceding_work is already built from A4
preceding_work_mag_for_close = {}
for close_k, close_cts_v, work_k, work_mag in close_preceding_work:
    preceding_work_mag_for_close[close_k] = work_mag

# Evaluate each variant
variant_names = ["cts", "cof1", "cof2", "cof3"]
cof_results = {}

for vname in variant_names:
    all_vals = [line_cof[k][vname] for k in line_keys_ordered]
    close_v = [line_cof[k][vname] for k in close_keys]
    work_v = [line_cof[k][vname] for k in work_keys]

    # Distribution stats
    dist_stats = {
        "mean": r5(np.mean(all_vals)),
        "median": r5(np.median(all_vals)),
        "std": r5(np.std(all_vals)),
        "frac_gt_03": r5(sum(1 for v in all_vals if v > 0.3) / len(all_vals)) if all_vals else 0,
        "frac_gt_05": r5(sum(1 for v in all_vals if v > 0.5) / len(all_vals)) if all_vals else 0,
    }

    # Mann-Whitney U: CLOSE vs WORK
    if len(close_v) > 0 and len(work_v) > 0:
        u_stat, p_val = scipy_stats.mannwhitneyu(close_v, work_v, alternative="two-sided")
        mwu = {
            "U": r5(u_stat),
            "p_value": float(f"{p_val:.6e}"),
            "rank_biserial": rank_biserial(u_stat, len(close_v), len(work_v)),
        }
    else:
        mwu = {"U": None, "p_value": None, "rank_biserial": None}

    # Excursion-window overlap
    n_close_high_cof_and_high_work = 0
    n_close_with_prec = 0
    for k in close_keys:
        if k in preceding_work_mag_for_close:
            n_close_with_prec += 1
            if line_cof[k][vname] > 0.3 and preceding_work_mag_for_close[k] > p75_work:
                n_close_high_cof_and_high_work += 1

    frac_overlap = n_close_high_cof_and_high_work / n_close_with_prec if n_close_with_prec > 0 else 0.0

    cof_results[vname] = {
        "distribution": dist_stats,
        "mann_whitney_close_vs_work": mwu,
        "excursion_window_overlap": {
            "n_close_with_preceding_work": n_close_with_prec,
            "n_high_cof_and_high_work": n_close_high_cof_and_high_work,
            "frac_overlap": r5(frac_overlap),
        },
    }

# Identify best variant
best_discrimination = min(variant_names, key=lambda v: cof_results[v]["mann_whitney_close_vs_work"].get("p_value", 1.0) or 1.0)
best_overlap = max(variant_names, key=lambda v: cof_results[v]["excursion_window_overlap"]["frac_overlap"])

a6_result = {
    "section_p90_normalization": {sec: {k: r5(v) for k, v in p90.items()} for sec, p90 in section_p90.items()},
    "variants": cof_results,
    "best_phase_discrimination": best_discrimination,
    "best_excursion_overlap": best_overlap,
}

print(f"  Best phase discrimination: {best_discrimination} (p={cof_results[best_discrimination]['mann_whitney_close_vs_work']['p_value']})")
print(f"  Best excursion overlap: {best_overlap} (frac={cof_results[best_overlap]['excursion_window_overlap']['frac_overlap']})")
for vname in variant_names:
    vr = cof_results[vname]
    print(f"    {vname}: mean={vr['distribution']['mean']}, MWU p={vr['mann_whitney_close_vs_work']['p_value']}, overlap={vr['excursion_window_overlap']['frac_overlap']}")


# ===========================================================================
# A7. Closure-Window Overlap Efficiency
# ===========================================================================
print("\nA7. Closure-Window Overlap Efficiency...")

# For each CLOSE line: preceding WORK mean |contribution|
# Already have preceding_work_mag_for_close from A4/A6

# Cross-tabulate: high preceding WORK AND high closure signal
# Use CTS > 0.3 and each COF > 0.3
overlap_metrics = {}
for vname in variant_names:
    high_excursion_and_high_closure = 0
    high_excursion_only = 0
    high_closure_only = 0
    neither = 0
    total_close_with_prec = 0

    for k in close_keys:
        if k not in preceding_work_mag_for_close:
            continue
        total_close_with_prec += 1
        high_work = preceding_work_mag_for_close[k] > p75_work
        high_closure = line_cof[k][vname] > 0.3

        if high_work and high_closure:
            high_excursion_and_high_closure += 1
        elif high_work:
            high_excursion_only += 1
        elif high_closure:
            high_closure_only += 1
        else:
            neither += 1

    useful_frac = high_excursion_and_high_closure / len(close_keys) if close_keys else 0.0

    overlap_metrics[vname] = {
        "total_close_with_preceding_work": total_close_with_prec,
        "high_excursion_and_high_closure": high_excursion_and_high_closure,
        "high_excursion_only": high_excursion_only,
        "high_closure_only": high_closure_only,
        "neither": neither,
        "useful_closure_fraction": r5(useful_frac),
    }

# Per-section breakdown
section_overlap = {}
for sec in sorted(section_cts.keys()):
    sec_close_keys = [k for k in close_keys if line_section_map.get(k) == sec]
    sec_metrics = {}
    for vname in variant_names:
        high_both = 0
        total = 0
        for k in sec_close_keys:
            if k not in preceding_work_mag_for_close:
                continue
            total += 1
            if preceding_work_mag_for_close[k] > p75_work and line_cof[k][vname] > 0.3:
                high_both += 1
        sec_metrics[vname] = {
            "n_close": total,
            "n_high_both": high_both,
            "useful_frac": r5(high_both / len(sec_close_keys)) if sec_close_keys else 0.0,
        }
    section_overlap[sec] = sec_metrics

# Diagnosis: weak closure or wrong timing?
total_close_with_prec = sum(1 for k in close_keys if k in preceding_work_mag_for_close)
n_high_work_prec = sum(1 for k in close_keys if k in preceding_work_mag_for_close and preceding_work_mag_for_close[k] > p75_work)
n_high_cts_close = sum(1 for k in close_keys if line_cts_map.get(k, 0) > 0.3)

a7_result = {
    "overlap_cross_tabulation": overlap_metrics,
    "per_section_overlap": section_overlap,
    "diagnosis": {
        "total_close_lines": len(close_keys),
        "close_with_preceding_work": total_close_with_prec,
        "high_excursion_preceding_work": n_high_work_prec,
        "frac_high_excursion_preceding": r5(n_high_work_prec / total_close_with_prec) if total_close_with_prec else 0.0,
        "high_cts_close_lines": n_high_cts_close,
        "frac_high_cts_close": r5(n_high_cts_close / len(close_keys)) if close_keys else 0.0,
        "interpretation": (
            "If frac_high_excursion_preceding is high but useful_closure_fraction is low, "
            "the issue is weak closure signal. If frac_high_excursion_preceding is low, "
            "closure arrives when nothing needs resolving."
        ),
    },
}

print(f"  CLOSE lines with preceding WORK: {total_close_with_prec}")
print(f"  High excursion preceding: {n_high_work_prec} ({a7_result['diagnosis']['frac_high_excursion_preceding']})")
print(f"  High CTS CLOSE: {n_high_cts_close} ({a7_result['diagnosis']['frac_high_cts_close']})")
for vname in variant_names:
    om = overlap_metrics[vname]
    print(f"    {vname}: useful_frac={om['useful_closure_fraction']}, "
          f"high_both={om['high_excursion_and_high_closure']}, "
          f"high_excursion_only={om['high_excursion_only']}, "
          f"high_closure_only={om['high_closure_only']}")


# ===========================================================================
# Assemble and save
# ===========================================================================
output = {
    "metadata": {
        "phase": 567,
        "script": "t1_closure_field_audit.py",
        "n_tokens": n_tokens,
        "n_lines": n_lines,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "A1_cts_distribution": a1_result,
    "A2_close_window_characterization": a2_result,
    "A3_closure_component_audit": a3_result,
    "A4_cts_excursion_timing": a4_result,
    "A5_s_asymmetry_audit": a5_result,
    "A6_cof_prototype_family": a6_result,
    "A7_closure_window_overlap": a7_result,
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\n{'='*60}")
print(f"Results saved to: {OUTPUT_PATH}")
print(f"{'='*60}")

# ===========================================================================
# Summary of key findings
# ===========================================================================
print(f"\n{'='*60}")
print("KEY FINDINGS SUMMARY")
print(f"{'='*60}")

print(f"\n[A1] CTS Distribution:")
print(f"  Global mean CTS: {a1_result['global_mean_cts']}")
print(f"  CLOSE lines CTS>0.3: {a1_result['close_frac_gt_03']} ({n_close} CLOSE lines)")
print(f"  ALL lines CTS>0.3: {a1_result['all_frac_gt_03']}")
print(f"  Section B deficit: {a1_result['b_deficit']} (B mean={a1_result['section_B_mean_cts']} vs non-B={a1_result['non_B_mean_cts']})")

print(f"\n[A2] CLOSE Windows:")
print(f"  {a2_result['total_close_lines']} CLOSE lines across {a2_result['n_folios_with_close']} folios")

print(f"\n[A3] Closure Components:")
print(f"  Significant CLOSE/WORK discriminators (p<0.01): {a3_result['significant_close_vs_work_p001']}")

print(f"\n[A4] Excursion Timing:")
print(f"  {a4_result['frac_close_following_high_excursion_work']} of CLOSE lines follow high-excursion WORK")
print(f"  Spearman r (preceding WORK -> CLOSE CTS): {a4_result['spearman_preceding_work_vs_close_cts']['r']}")

print(f"\n[A5] S Asymmetry:")
print(f"  S share of total warning+hard_stop: {a5_result['s_share_of_total_warning_hard_stop']}")
print(f"  S mean warning+hard_stop: {a5_result['s_warning_plus_hard_stop']}")

print(f"\n[A6] COF Prototypes:")
print(f"  Best phase discrimination: {a6_result['best_phase_discrimination']}")
print(f"  Best excursion overlap: {a6_result['best_excursion_overlap']}")

print(f"\n[A7] Overlap Efficiency:")
diag = a7_result["diagnosis"]
print(f"  Frac CLOSE with high preceding excursion: {diag['frac_high_excursion_preceding']}")
print(f"  Frac CLOSE with high CTS: {diag['frac_high_cts_close']}")
for vname in variant_names:
    print(f"  {vname} useful_closure_fraction: {overlap_metrics[vname]['useful_closure_fraction']}")
