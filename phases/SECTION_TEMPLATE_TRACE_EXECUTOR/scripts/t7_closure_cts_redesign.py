"""
Phase 562b T7 — Closure Transition Score (CTS) redesign.

Computes a continuous CTS scalar per line in [0, 1] replacing the old
categorical 5-class closure encoding (87% WORK_SEMI dominated).

CTS = 0.22 * closure_armed_01
    + 0.22 * norm(close_opacity_bias)
    + 0.28 * norm(m_close_bias)
    + 0.18 * norm(q4_shift_strength)
    + 0.10 * norm(q0q4_hazard_slope_pos)

Where norm(x) = min(x / section_p90, 1.0), p90 computed per section.
"""

import json
import math
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------------
PHASES_DIR = Path(__file__).resolve().parents[2]          # phases/
RESULTS_DIR = PHASES_DIR / "SECTION_TEMPLATE_TRACE_EXECUTOR" / "results"

T3_PATH = RESULTS_DIR / "t3_line_packets.json"
T2_PATH = RESULTS_DIR / "t2_folio_budgets.json"
OUT_PATH = RESULTS_DIR / "t7_closure_cts.json"

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
WEIGHTS = {
    "armed":    0.22,
    "cob":      0.22,
    "mcb":      0.28,
    "q4s":      0.18,
    "hazslope": 0.10,
}

SIGMA_FLOORS = {"section": 0.08, "folio": 0.05, "paragraph": 0.05}

HAZARD_ENVELOPE_TYPES = ["SAFE_OPEN", "THERMAL_INTERIOR", "DANGEROUS_CLOSE"]

Q0Q4_HAZARD_SLOPE_IDX = 12

N_PERMS = 50

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def round5(x):
    """Round a float to 5 decimal places."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 0.0
    return round(float(x), 5)


def norm_val(x, p90):
    """Normalize x by section p90, clamp to [0, 1]."""
    if p90 <= 0:
        return 0.0
    return min(x / p90, 1.0)


def compute_cts(armed_01, cob_norm, mcb_norm, q4s_norm, haz_norm):
    """Compute CTS from normalized components."""
    return (WEIGHTS["armed"] * armed_01
            + WEIGHTS["cob"] * cob_norm
            + WEIGHTS["mcb"] * mcb_norm
            + WEIGHTS["q4s"] * q4s_norm
            + WEIGHTS["hazslope"] * haz_norm)


def mean_std_floored(values, floor):
    """Compute mean and std with sigma floor."""
    if len(values) == 0:
        return 0.0, floor
    m = float(np.mean(values))
    s = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    return m, max(s, floor)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("Phase 562b T7 — Closure Transition Score (CTS) Redesign")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Load T3 line packets
    # ------------------------------------------------------------------
    print("\n[1] Loading T3 line packets...")
    with open(T3_PATH, "r") as f:
        t3_data = json.load(f)

    line_packets = t3_data["line_packets"]
    print(f"    Loaded {len(line_packets)} line packets")

    # ------------------------------------------------------------------
    # 2-3. Extract raw features per line
    # ------------------------------------------------------------------
    print("\n[2-3] Extracting raw features per line...")

    # Pre-build per-line raw feature records
    lines = []   # list of dicts with key, section, raw values
    for key, pkt in line_packets.items():
        ps = pkt["packet_state"]
        profile = pkt["profile"]

        armed = 1.0 if ps.get("closure_armed", False) else 0.0
        cob = max(float(ps.get("close_opacity_bias", 0.0)), 0.0)
        mcb = max(float(ps.get("m_close_bias", 0.0)), 0.0)
        q4s = max(float(ps.get("q4_shift_strength", 0.0)), 0.0)

        haz_slope_raw = float(profile[Q0Q4_HAZARD_SLOPE_IDX])
        haz_slope_pos = max(haz_slope_raw, 0.0)

        section = pkt["section"]
        folio = pkt["folio"]
        para_idx = pkt.get("paragraph_idx")
        phase = ps.get("packet_phase", "WORK")
        haz_env = ps.get("hazard_envelope", "THERMAL_INTERIOR")

        lines.append({
            "key": key,
            "section": section,
            "folio": folio,
            "paragraph_idx": para_idx,
            "phase": phase,
            "hazard_envelope": haz_env,
            "armed": armed,
            "cob": cob,
            "mcb": mcb,
            "q4s": q4s,
            "haz_slope_pos": haz_slope_pos,
        })

    print(f"    Extracted features for {len(lines)} lines")

    # ------------------------------------------------------------------
    # 4. Compute per-section p90 for normalization targets
    # ------------------------------------------------------------------
    print("\n[4] Computing per-section p90 values...")

    section_raw = defaultdict(lambda: {"cob": [], "mcb": [], "q4s": [], "haz_slope_pos": []})
    for rec in lines:
        s = rec["section"]
        section_raw[s]["cob"].append(rec["cob"])
        section_raw[s]["mcb"].append(rec["mcb"])
        section_raw[s]["q4s"].append(rec["q4s"])
        section_raw[s]["haz_slope_pos"].append(rec["haz_slope_pos"])

    section_p90 = {}
    for s, raw in sorted(section_raw.items()):
        section_p90[s] = {
            "close_opacity_bias": round5(float(np.percentile(raw["cob"], 90))) if raw["cob"] else 0.0,
            "m_close_bias":       round5(float(np.percentile(raw["mcb"], 90))) if raw["mcb"] else 0.0,
            "q4_shift_strength":  round5(float(np.percentile(raw["q4s"], 90))) if raw["q4s"] else 0.0,
            "q0q4_hazard_slope_pos": round5(float(np.percentile(raw["haz_slope_pos"], 90))) if raw["haz_slope_pos"] else 0.0,
        }
        print(f"    Section {s}: cob_p90={section_p90[s]['close_opacity_bias']:.4f}  "
              f"mcb_p90={section_p90[s]['m_close_bias']:.4f}  "
              f"q4s_p90={section_p90[s]['q4_shift_strength']:.4f}  "
              f"haz_p90={section_p90[s]['q0q4_hazard_slope_pos']:.4f}")

    # ------------------------------------------------------------------
    # 5. Compute CTS per line
    # ------------------------------------------------------------------
    print("\n[5] Computing CTS per line...")

    line_cts = {}
    for rec in lines:
        s = rec["section"]
        p90 = section_p90[s]

        cob_norm = norm_val(rec["cob"], p90["close_opacity_bias"])
        mcb_norm = norm_val(rec["mcb"], p90["m_close_bias"])
        q4s_norm = norm_val(rec["q4s"], p90["q4_shift_strength"])
        haz_norm = norm_val(rec["haz_slope_pos"], p90["q0q4_hazard_slope_pos"])

        cts = compute_cts(rec["armed"], cob_norm, mcb_norm, q4s_norm, haz_norm)

        rec["cts"] = cts
        rec["components"] = {
            "armed": round5(rec["armed"]),
            "cob": round5(cob_norm),
            "mcb": round5(mcb_norm),
            "q4s": round5(q4s_norm),
            "hazslope": round5(haz_norm),
        }

        line_cts[rec["key"]] = {
            "cts": round5(cts),
            "components": rec["components"],
        }

    cts_vals = [rec["cts"] for rec in lines]
    print(f"    CTS range: [{min(cts_vals):.4f}, {max(cts_vals):.4f}]  "
          f"mean={np.mean(cts_vals):.4f}  std={np.std(cts_vals):.4f}")

    # ------------------------------------------------------------------
    # 6. Section-level CTS distributions
    # ------------------------------------------------------------------
    print("\n[6] Section-level CTS distributions...")

    section_cts_vals = defaultdict(list)
    for rec in lines:
        section_cts_vals[rec["section"]].append(rec["cts"])

    section_cts_dist = {}
    for s in sorted(section_cts_vals):
        m, sd = mean_std_floored(section_cts_vals[s], SIGMA_FLOORS["section"])
        section_cts_dist[s] = {"mean": round5(m), "std": round5(sd), "n": len(section_cts_vals[s])}
        print(f"    Section {s}: mean={m:.4f}  std={sd:.4f}  n={len(section_cts_vals[s])}")

    # ------------------------------------------------------------------
    # 7. Folio-level CTS distributions
    # ------------------------------------------------------------------
    print("\n[7] Folio-level CTS distributions...")

    folio_cts_vals = defaultdict(list)
    for rec in lines:
        folio_cts_vals[rec["folio"]].append(rec["cts"])

    folio_cts_dist = {}
    for fol in sorted(folio_cts_vals):
        m, sd = mean_std_floored(folio_cts_vals[fol], SIGMA_FLOORS["folio"])
        folio_cts_dist[fol] = {"mean": round5(m), "std": round5(sd), "n": len(folio_cts_vals[fol])}

    print(f"    {len(folio_cts_dist)} folios computed")

    # ------------------------------------------------------------------
    # 8. Paragraph-level CTS distributions + LOO means
    # ------------------------------------------------------------------
    print("\n[8] Paragraph-level CTS distributions...")

    # Group lines by (folio, paragraph_idx)
    para_lines = defaultdict(list)
    for rec in lines:
        para_key = f"{rec['folio']}|{rec['paragraph_idx']}"
        para_lines[para_key].append(rec)

    paragraph_cts_dist = {}
    n_qualifying = 0
    for pkey in sorted(para_lines):
        precs = para_lines[pkey]
        if len(precs) < 2:
            continue
        n_qualifying += 1

        p_cts = [r["cts"] for r in precs]
        m, sd = mean_std_floored(p_cts, SIGMA_FLOORS["paragraph"])

        # Leave-one-out means: for each line, compute mean of all OTHER lines
        loo_means = {}
        for i, r in enumerate(precs):
            others = [p_cts[j] for j in range(len(p_cts)) if j != i]
            loo_m = float(np.mean(others)) if others else m
            # Use the line number from the key as LOO identifier
            line_key = r["key"]  # "folio|line"
            line_id = line_key.split("|")[1]
            loo_means[line_id] = round5(loo_m)

        paragraph_cts_dist[pkey] = {
            "mean": round5(m),
            "std": round5(sd),
            "n_lines": len(precs),
            "loo_means": loo_means,
        }

    print(f"    {n_qualifying} qualifying paragraphs (>= 2 lines)")

    # ------------------------------------------------------------------
    # 9. Hazard envelope distributions (paragraph + folio level)
    # ------------------------------------------------------------------
    print("\n[9] Hazard envelope distributions...")

    # Folio-level
    folio_haz_lines = defaultdict(list)
    for rec in lines:
        folio_haz_lines[rec["folio"]].append(rec["hazard_envelope"])

    folio_hazard_envelope_dist = {}
    for fol in sorted(folio_haz_lines):
        haz_list = folio_haz_lines[fol]
        n = len(haz_list)
        dist = {}
        for ht in HAZARD_ENVELOPE_TYPES:
            dist[ht] = round5(sum(1 for h in haz_list if h == ht) / n) if n > 0 else 0.0
        folio_hazard_envelope_dist[fol] = dist

    print(f"    {len(folio_hazard_envelope_dist)} folio hazard envelope distributions")

    # Paragraph-level
    paragraph_hazard_envelope_dist = {}
    for pkey in sorted(para_lines):
        precs = para_lines[pkey]
        n = len(precs)
        dist = {}
        for ht in HAZARD_ENVELOPE_TYPES:
            dist[ht] = round5(sum(1 for r in precs if r["hazard_envelope"] == ht) / n) if n > 0 else 0.0
        paragraph_hazard_envelope_dist[pkey] = dist

    print(f"    {len(paragraph_hazard_envelope_dist)} paragraph hazard envelope distributions")

    # ==================================================================
    # VALIDATIONS
    # ==================================================================
    print("\n" + "=" * 70)
    print("VALIDATIONS")
    print("=" * 70)

    # ------------------------------------------------------------------
    # V1: CTS correlates with packet_phase
    # ------------------------------------------------------------------
    print("\n--- V1: CTS vs packet_phase ---")

    phase_cts = defaultdict(list)
    for rec in lines:
        phase_cts[rec["phase"]].append(rec["cts"])

    # Report medians
    phase_medians = {}
    for ph in ["SPEC", "WORK", "CLOSE"]:
        if ph in phase_cts:
            phase_medians[ph] = round5(float(np.median(phase_cts[ph])))
            print(f"    {ph}: median={phase_medians[ph]:.4f}  n={len(phase_cts[ph])}")
        else:
            phase_medians[ph] = 0.0
            print(f"    {ph}: no data")

    # Also report any other phases present
    for ph in sorted(phase_cts):
        if ph not in ["SPEC", "WORK", "CLOSE"]:
            med = round5(float(np.median(phase_cts[ph])))
            phase_medians[ph] = med
            print(f"    {ph}: median={med:.4f}  n={len(phase_cts[ph])}")

    # Kruskal-Wallis across the main three phases
    kw_groups = []
    for ph in ["SPEC", "WORK", "CLOSE"]:
        if ph in phase_cts and len(phase_cts[ph]) > 0:
            kw_groups.append(phase_cts[ph])

    if len(kw_groups) >= 2:
        kw_stat, kw_p = stats.kruskal(*kw_groups)
    else:
        kw_stat, kw_p = 0.0, 1.0

    # PASS if p < 0.001 AND median_CLOSE > median_WORK > median_SPEC
    v1_monotone = (phase_medians.get("CLOSE", 0) > phase_medians.get("WORK", 0) >
                   phase_medians.get("SPEC", 0))
    v1_pass = kw_p < 0.001 and v1_monotone
    v1_verdict = "PASS" if v1_pass else "FAIL"
    print(f"    KW stat={kw_stat:.2f}  p={kw_p:.2e}  monotone={v1_monotone}  -> {v1_verdict}")

    # ------------------------------------------------------------------
    # V2: Folio contributes non-trivial CTS variance beyond section
    # ------------------------------------------------------------------
    print("\n--- V2: Folio within-section CTS variance ---")

    # Build folio->section and folio->mean_cts mappings
    folio_section = {}
    for rec in lines:
        folio_section[rec["folio"]] = rec["section"]

    # Real between-folio variance of folio mean CTS
    folio_means = {f: d["mean"] for f, d in folio_cts_dist.items()}
    real_var = float(np.var(list(folio_means.values())))

    # Permutation null: shuffle lines within section, recompute folio means, get variance
    # Build section -> list of (folio, cts) pairs
    section_line_data = defaultdict(list)
    for rec in lines:
        section_line_data[rec["section"]].append((rec["folio"], rec["cts"]))

    rng = np.random.RandomState(42)
    null_vars = []
    for _ in range(N_PERMS):
        # For each section, shuffle CTS values across lines (keeping folio assignments fixed)
        shuffled_folio_cts = defaultdict(list)
        for s, sdata in section_line_data.items():
            folios_in_section = [d[0] for d in sdata]
            cts_in_section = [d[1] for d in sdata]
            shuffled_cts = list(cts_in_section)
            rng.shuffle(shuffled_cts)
            for fol, c in zip(folios_in_section, shuffled_cts):
                shuffled_folio_cts[fol].append(c)
        # Compute folio means under shuffled
        shuf_folio_means = {f: float(np.mean(v)) for f, v in shuffled_folio_cts.items()}
        null_vars.append(float(np.var(list(shuf_folio_means.values()))))

    null_mean = float(np.mean(null_vars))
    null_std = float(np.std(null_vars))
    v2_z = (real_var - null_mean) / null_std if null_std > 0 else 0.0
    v2_pass = v2_z > 2.0
    v2_verdict = "PASS" if v2_pass else "FAIL"
    print(f"    Real var={real_var:.6f}  null mean={null_mean:.6f}  null std={null_std:.6f}")
    print(f"    z={v2_z:.2f}  -> {v2_verdict}")

    # ------------------------------------------------------------------
    # V3: CTS spread
    # ------------------------------------------------------------------
    print("\n--- V3: CTS spread ---")

    cts_arr = np.array(cts_vals)
    v3_min = float(np.min(cts_arr))
    v3_max = float(np.max(cts_arr))
    v3_mean = float(np.mean(cts_arr))
    v3_std = float(np.std(cts_arr))
    v3_p10 = float(np.percentile(cts_arr, 10))
    v3_p50 = float(np.percentile(cts_arr, 50))
    v3_p90 = float(np.percentile(cts_arr, 90))

    v3_pass = v3_std > 0.05 and v3_max > 0.5
    v3_verdict = "PASS" if v3_pass else "FAIL"

    print(f"    min={v3_min:.4f}  max={v3_max:.4f}  mean={v3_mean:.4f}  std={v3_std:.4f}")
    print(f"    p10={v3_p10:.4f}  p50={v3_p50:.4f}  p90={v3_p90:.4f}")
    print(f"    std>0.05={v3_std > 0.05}  max>0.5={v3_max > 0.5}  -> {v3_verdict}")

    # ==================================================================
    # Build output
    # ==================================================================
    print("\n" + "=" * 70)
    print("Writing output...")

    output = {
        "metadata": {
            "phase": "562b",
            "task": "T7_closure_cts_redesign",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "n_lines": len(lines),
            "cts_formula": "0.22*armed + 0.22*norm(cob) + 0.28*norm(mcb) + 0.18*norm(q4s) + 0.10*norm(hazslope_pos)",
            "sigma_floors": SIGMA_FLOORS,
        },
        "section_p90": section_p90,
        "line_cts": line_cts,
        "section_cts_dist": section_cts_dist,
        "folio_cts_dist": folio_cts_dist,
        "paragraph_cts_dist": paragraph_cts_dist,
        "folio_hazard_envelope_dist": folio_hazard_envelope_dist,
        "paragraph_hazard_envelope_dist": paragraph_hazard_envelope_dist,
        "validations": {
            "V1_cts_vs_phase": {
                "kw_stat": round5(kw_stat),
                "kw_p": round5(kw_p),
                "medians": {k: round5(v) for k, v in phase_medians.items()},
                "verdict": v1_verdict,
            },
            "V2_folio_within_section": {
                "real_var": round5(real_var),
                "null_mean": round5(null_mean),
                "null_std": round5(null_std),
                "z_score": round5(v2_z),
                "n_perms": N_PERMS,
                "verdict": v2_verdict,
            },
            "V3_cts_spread": {
                "min": round5(v3_min),
                "max": round5(v3_max),
                "mean": round5(v3_mean),
                "std": round5(v3_std),
                "p10": round5(v3_p10),
                "p50": round5(v3_p50),
                "p90": round5(v3_p90),
                "verdict": v3_verdict,
            },
        },
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"    Written to {OUT_PATH}")
    print(f"    Output keys: {list(output.keys())}")
    print(f"    line_cts entries: {len(line_cts)}")
    print(f"    folio_cts_dist entries: {len(folio_cts_dist)}")
    print(f"    paragraph_cts_dist entries: {len(paragraph_cts_dist)}")
    print(f"    paragraph_hazard_envelope_dist entries: {len(paragraph_hazard_envelope_dist)}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  V1 (CTS vs phase):           {v1_verdict}")
    print(f"  V2 (folio within section):    {v2_verdict}  (z={v2_z:.2f})")
    print(f"  V3 (CTS spread):             {v3_verdict}  (std={v3_std:.4f}, max={v3_max:.4f})")
    all_pass = v1_pass and v2_pass and v3_pass
    print(f"\n  Overall: {'ALL PASS' if all_pass else 'SOME FAIL'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
