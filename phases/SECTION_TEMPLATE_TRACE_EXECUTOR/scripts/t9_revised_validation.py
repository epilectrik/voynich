#!/usr/bin/env python3
"""
Phase 562b T9 — Revised Executor Validation
============================================
Validates the revised executor (T8) against the original T4/T5 baseline.
Runs comprehensive test battery across baseline comparison, closure diagnostics,
paragraph cloud diagnostics, and abbreviated null models.
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from scipy import stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parents[1]  # SECTION_TEMPLATE_TRACE_EXECUTOR
RESULTS = BASE / "results"

T4_PATH = RESULTS / "t4_token_traces.json"
T5_PATH = RESULTS / "t5_trace_validation.json"
T7_PATH = RESULTS / "t7_closure_cts.json"
T8_PATH = RESULTS / "t8_revised_traces.json"
T3_PATH = RESULTS / "t3_line_packets.json"

CORPUS_PATH = (BASE.parent / "WITHIN_DOMAIN_COMPOSITIONAL_CONTROL" /
               "results" / "t1_domain_decomposition.json")

OUTPUT_PATH = RESULTS / "t9_revised_validation.json"

AXES = ["domain", "hazard", "routing", "closure", "headless"]
ENVELOPE_MODES = 3  # E1..E4


def load_json(path):
    print(f"  Loading {path.name} ...")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def r5(x):
    """Round to 5 decimal places."""
    if x is None:
        return None
    return round(float(x), 5)


def normalize(dist, keys):
    total = sum(dist.get(k, 0) for k in keys)
    if total == 0:
        return {k: 1.0 / len(keys) for k in keys}
    return {k: dist.get(k, 0) / total for k in keys}


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("=" * 70)
    print("Phase 562b T9 — Revised Executor Validation")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------
    print("\n[1] Loading input files ...")
    t4 = load_json(T4_PATH)
    t5 = load_json(T5_PATH)
    t7 = load_json(T7_PATH)
    t8 = load_json(T8_PATH)
    t3 = load_json(T3_PATH)
    corpus_data = load_json(CORPUS_PATH)

    # Extract token-level LL arrays
    # T4/T8 use keys "per_token_composite_LL" and "per_token_axis_LL"
    # Restructure into the nested format expected by this script
    def restructure_ll(data):
        ll = {"composite": data["per_token_composite_LL"]}
        for axis in AXES:
            ll[axis] = data["per_token_axis_LL"][axis]
        return ll

    orig_ll = restructure_ll(t4)
    rev_ll = restructure_ll(t8)

    n_tokens = len(orig_ll["composite"]["E1"])
    print(f"  Token count: {n_tokens}")

    orig_composite_e4 = np.array(orig_ll["composite"]["E4"])
    rev_composite_e4 = np.array(rev_ll["composite"]["E4"])

    # Build corpus token list for folio/line/paragraph grouping
    # corpus_data may have tokens under various keys — check structure
    corpus_tokens = None
    if "tokens" in corpus_data:
        corpus_tokens = corpus_data["tokens"]
    elif "corpus" in corpus_data:
        corpus_tokens = corpus_data["corpus"]
    else:
        # Try to find tokens in nested structure
        for k in corpus_data:
            if isinstance(corpus_data[k], list) and len(corpus_data[k]) == n_tokens:
                corpus_tokens = corpus_data[k]
                break

    if corpus_tokens is None:
        print("  WARNING: Could not find token list in corpus data.")
        print(f"  Keys available: {list(corpus_data.keys())[:20]}")
        # Try to build minimal token info from t4/t8 metadata or t3 line packets
        corpus_tokens = None

    # Build folio groupings from corpus or from line packets
    folio_indices = defaultdict(list)
    section_indices = defaultdict(list)
    para_indices = defaultdict(list)  # key: "folio|para_idx"
    line_indices = defaultdict(list)  # key: "folio|line"

    if corpus_tokens and len(corpus_tokens) == n_tokens:
        for i, tok in enumerate(corpus_tokens):
            fol = tok.get("folio", "unknown")
            sec = tok.get("section", "unknown")
            folio_indices[fol].append(i)
            section_indices[sec].append(i)
            line_key = f"{fol}|{tok.get('line', '?')}"
            line_indices[line_key].append(i)
            para_key = f"{fol}|{tok.get('para_idx', tok.get('paragraph', '?'))}"
            para_indices[para_key].append(i)
    else:
        # Fallback: try to reconstruct from t3 line packets
        print("  Attempting folio/section grouping from T3 line packets ...")
        # We won't have per-token mapping, but we can still run most tests
        # that don't require folio grouping

    results = {
        "metadata": {
            "phase": "562b",
            "task": "T9_revised_validation",
            "timestamp": datetime.now().isoformat(),
            "n_tokens": n_tokens,
            "baseline": "t4_token_traces.json",
            "revised": "t8_revised_traces.json"
        }
    }

    # ==================================================================
    # A. BASELINE COMPARISON
    # ==================================================================
    print("\n" + "=" * 70)
    print("A. BASELINE COMPARISON")
    print("=" * 70)

    # A1: Composite comparison
    orig_e4_mean = float(np.mean(orig_composite_e4))
    rev_e4_mean = float(np.mean(rev_composite_e4))
    delta_composite = rev_e4_mean - orig_e4_mean
    improved = delta_composite > 0

    print(f"\n  A1: Composite E4 comparison")
    print(f"      Original E4 mean LL: {r5(orig_e4_mean)}")
    print(f"      Revised  E4 mean LL: {r5(rev_e4_mean)}")
    print(f"      Delta:               {r5(delta_composite)}")
    print(f"      Improved:            {improved}")

    a1 = {
        "original_E4": r5(orig_e4_mean),
        "revised_E4": r5(rev_e4_mean),
        "delta": r5(delta_composite),
        "improved": improved
    }

    # A2: Per-axis comparison at E4
    print(f"\n  A2: Per-axis E4 comparison")
    a2 = {}
    for axis in AXES:
        orig_axis = np.array(orig_ll[axis]["E4"])
        rev_axis = np.array(rev_ll[axis]["E4"])
        orig_mean = float(np.mean(orig_axis))
        rev_mean = float(np.mean(rev_axis))
        d = rev_mean - orig_mean
        a2[axis] = {
            "original": r5(orig_mean),
            "revised": r5(rev_mean),
            "delta": r5(d)
        }
        direction = "IMPROVED" if d > 0 else ("DEGRADED" if d < 0 else "UNCHANGED")
        print(f"      {axis:12s}: orig={r5(orig_mean):>10.5f}  rev={r5(rev_mean):>10.5f}"
              f"  delta={r5(d):>10.5f}  {direction}")

    # A3: Monotonicity check on revised results
    rev_means = {}
    for env in ["E1", "E2", "E3", "E4"]:
        rev_means[env] = float(np.mean(np.array(rev_ll["composite"][env])))
    mono_holds = (rev_means["E4"] >= rev_means["E3"] >= rev_means["E2"] > rev_means["E1"])

    print(f"\n  A3: Monotonicity (revised)")
    for env in ["E1", "E2", "E3", "E4"]:
        print(f"      {env}: {r5(rev_means[env])}")
    print(f"      E4 >= E3 >= E2 > E1: {mono_holds}")

    a3 = {env: r5(rev_means[env]) for env in ["E1", "E2", "E3", "E4"]}
    a3["holds"] = mono_holds

    # A4: Wilcoxon signed-rank test (revised E4 vs original E4)
    print(f"\n  A4: Wilcoxon signed-rank test (revised vs original E4)")
    diff = rev_composite_e4 - orig_composite_e4
    # Remove zeros for Wilcoxon
    nonzero_diff = diff[diff != 0]
    if len(nonzero_diff) > 0:
        wilcoxon_stat, wilcoxon_p = stats.wilcoxon(nonzero_diff)
        # Approximate z from the test statistic
        n_eff = len(nonzero_diff)
        # For large n, W ~ N(mu_W, sigma_W)
        mu_w = n_eff * (n_eff + 1) / 4.0
        sigma_w = np.sqrt(n_eff * (n_eff + 1) * (2 * n_eff + 1) / 24.0)
        z_wilcoxon = (wilcoxon_stat - mu_w) / sigma_w
        # Effect size: matched-pairs rank-biserial r = z / sqrt(n)
        effect_r = z_wilcoxon / np.sqrt(n_tokens)
    else:
        wilcoxon_stat = 0
        wilcoxon_p = 1.0
        z_wilcoxon = 0
        effect_r = 0

    print(f"      W statistic: {wilcoxon_stat:.1f}")
    print(f"      z:           {r5(z_wilcoxon)}")
    print(f"      p:           {wilcoxon_p:.2e}")
    print(f"      effect r:    {r5(effect_r)}")
    print(f"      n non-zero:  {len(nonzero_diff)}")

    a4 = {
        "z": r5(z_wilcoxon),
        "p": r5(wilcoxon_p),
        "effect_size_r": r5(effect_r),
        "n": n_tokens,
        "n_nonzero": len(nonzero_diff)
    }

    results["A_baseline_comparison"] = {
        "A1_composite": a1,
        "A2_per_axis": a2,
        "A3_monotonicity": a3,
        "A4_wilcoxon": a4
    }

    # ==================================================================
    # B. CLOSURE DIAGNOSTICS
    # ==================================================================
    print("\n" + "=" * 70)
    print("B. CLOSURE DIAGNOSTICS")
    print("=" * 70)

    # B1: CTS vs packet_phase correlation
    print(f"\n  B1: CTS vs packet_phase (Kruskal-Wallis)")
    line_cts = t7.get("line_cts", {})
    line_packets = t3.get("line_packets", {})

    phase_cts = defaultdict(list)
    matched_lines = 0
    for line_key, cts_data in line_cts.items():
        cts_val = cts_data.get("cts", None) if isinstance(cts_data, dict) else cts_data
        if cts_val is None:
            continue
        pkt = line_packets.get(line_key, {})
        pkt_state = pkt.get("packet_state", {})
        phase = pkt_state.get("packet_phase", None)
        if phase is not None:
            phase_cts[phase].append(float(cts_val))
            matched_lines += 1

    print(f"      Matched lines: {matched_lines}")
    b1 = {}
    if len(phase_cts) >= 2:
        groups = list(phase_cts.values())
        phase_names = list(phase_cts.keys())
        kw_stat, kw_p = stats.kruskal(*groups)
        n_total = sum(len(g) for g in groups)
        k_groups = len(groups)
        # Eta-squared approximation
        eta2 = (kw_stat - k_groups + 1) / (n_total - k_groups) if n_total > k_groups else 0

        print(f"      Phases: {phase_names}")
        for pn in sorted(phase_cts.keys()):
            vals = phase_cts[pn]
            print(f"        {pn:20s}: median={r5(np.median(vals))}, n={len(vals)}")
        print(f"      KW H={r5(kw_stat)}, p={kw_p:.2e}, eta2={r5(eta2)}")

        b1 = {
            "phases": {pn: {"median": r5(np.median(phase_cts[pn])), "n": len(phase_cts[pn])}
                       for pn in sorted(phase_cts.keys())},
            "kw_H": r5(kw_stat),
            "kw_p": r5(kw_p),
            "eta_squared": r5(eta2),
            "n_lines": matched_lines
        }
    else:
        print("      Insufficient phases for KW test")
        b1 = {"note": "insufficient phases", "n_lines": matched_lines}

    # B2: CTS folio-within-section (load T7 V2 z-score)
    print(f"\n  B2: CTS folio-within-section z-score (from T7)")
    t7_validations = t7.get("validations", {})
    v2_data = t7_validations.get("V2_folio_within_section", t7_validations.get("v2", {}))
    v2_z = None
    if isinstance(v2_data, dict):
        v2_z = v2_data.get("z_score", v2_data.get("z", None))
    if v2_z is not None:
        print(f"      V2 z-score: {r5(v2_z)}")
        b2 = {"z_score": r5(v2_z), "verdict": "folio-within-section contribution confirmed"
               if abs(v2_z) > 2 else "marginal"}
    else:
        # Try alternate key structures
        for k in t7_validations:
            if "folio" in k.lower() or "v2" in k.lower():
                val = t7_validations[k]
                if isinstance(val, dict):
                    for subk in val:
                        if "z" in subk.lower():
                            v2_z = val[subk]
                            break
        if v2_z is not None:
            print(f"      V2 z-score: {r5(v2_z)}")
            b2 = {"z_score": r5(v2_z), "verdict": "confirmed" if abs(v2_z) > 2 else "marginal"}
        else:
            print("      V2 z-score not found in T7 validations")
            print(f"      Available keys: {list(t7_validations.keys())}")
            b2 = {"z_score": None, "verdict": "not found in T7"}

    # B3: Paragraph CTS modulation (E3 closure vs E2 closure)
    print(f"\n  B3: Paragraph CTS modulation (E3 vs E2 closure)")
    rev_e2_closure = np.array(rev_ll["closure"]["E2"])
    rev_e3_closure = np.array(rev_ll["closure"]["E3"])
    e2_closure_mean = float(np.mean(rev_e2_closure))
    e3_closure_mean = float(np.mean(rev_e3_closure))
    b3_improved = e3_closure_mean > e2_closure_mean

    print(f"      E2 closure mean LL: {r5(e2_closure_mean)}")
    print(f"      E3 closure mean LL: {r5(e3_closure_mean)}")
    print(f"      E3 > E2:           {b3_improved}")

    b3 = {
        "E2_closure_mean": r5(e2_closure_mean),
        "E3_closure_mean": r5(e3_closure_mean),
        "improved": b3_improved
    }

    # B4: CTS null model — deferred
    print(f"\n  B4: CTS null model")
    print(f"      Deferred — requires re-execution of executor with shuffled CTS")
    b4 = {
        "real_E4_composite": r5(rev_e4_mean),
        "note": "deferred - requires re-execution with shuffled CTS assignments"
    }

    # B5: Line-level closure reconstruction
    print(f"\n  B5: Line-level closure reconstruction")
    cts_values = []
    q4_opaque_values = []
    m_close_bias_values = []
    phase_cts_b5 = defaultdict(list)
    q4_shift_by_section = defaultdict(list)
    cts_high_shift = []
    cts_low_shift = []

    # Collect section medians for q4_shift_strength
    section_shift_vals = defaultdict(list)
    for line_key, pkt in line_packets.items():
        ps = pkt.get("packet_state", {})
        shift = ps.get("q4_shift_strength", None)
        sec = pkt.get("section", "?")
        if shift is not None:
            section_shift_vals[sec].append(float(shift))

    section_shift_medians = {sec: np.median(vals) for sec, vals in section_shift_vals.items()}

    for line_key, cts_data in line_cts.items():
        cts_val = cts_data.get("cts", None) if isinstance(cts_data, dict) else cts_data
        if cts_val is None:
            continue
        cts_val = float(cts_val)

        pkt = line_packets.get(line_key, {})
        profile = pkt.get("profile", None)
        ps = pkt.get("packet_state", {})
        sec = pkt.get("section", "?")

        # (a) CTS vs q4_opaque_rate (profile index 14)
        if profile is not None and len(profile) > 14:
            q4_opaque = float(profile[14])
            cts_values.append(cts_val)
            q4_opaque_values.append(q4_opaque)

        # (b) CTS vs m_close_bias
        mcb = ps.get("m_close_bias", None)
        if mcb is not None:
            m_close_bias_values.append(float(mcb))
            if len(cts_values) > len(m_close_bias_values):
                pass  # alignment issue — collect separately
            # Track separately for correlation
        else:
            m_close_bias_values.append(None)

        # (c) Phase separation
        phase = ps.get("packet_phase", None)
        if phase is not None:
            phase_cts_b5[phase].append(cts_val)

        # (d) q4 discontinuity
        shift = ps.get("q4_shift_strength", None)
        if shift is not None and sec in section_shift_medians:
            if float(shift) > section_shift_medians[sec]:
                cts_high_shift.append(cts_val)
            else:
                cts_low_shift.append(cts_val)

    # B5a: CTS vs q4_opaque_rate
    b5a = {}
    if len(cts_values) > 10 and len(q4_opaque_values) == len(cts_values):
        r_val, p_val = stats.pearsonr(cts_values, q4_opaque_values)
        print(f"      B5a: CTS vs q4_opaque_rate: r={r5(r_val)}, p={p_val:.2e}, n={len(cts_values)}")
        b5a = {"pearson_r": r5(r_val), "p": r5(p_val), "n": len(cts_values)}
    else:
        print(f"      B5a: Insufficient data (cts={len(cts_values)}, q4_opaque={len(q4_opaque_values)})")
        b5a = {"pearson_r": None, "p": None, "note": "insufficient data"}

    # B5b: CTS vs m_close_bias
    b5b = {}
    # Rebuild paired lists for m_close_bias
    cts_for_mcb = []
    mcb_vals = []
    for line_key, cts_data in line_cts.items():
        cts_val = cts_data.get("cts", None) if isinstance(cts_data, dict) else cts_data
        if cts_val is None:
            continue
        pkt = line_packets.get(line_key, {})
        ps = pkt.get("packet_state", {})
        mcb = ps.get("m_close_bias", None)
        if mcb is not None:
            cts_for_mcb.append(float(cts_val))
            mcb_vals.append(float(mcb))

    if len(cts_for_mcb) > 10:
        r_val, p_val = stats.pearsonr(cts_for_mcb, mcb_vals)
        print(f"      B5b: CTS vs m_close_bias: r={r5(r_val)}, p={p_val:.2e}, n={len(cts_for_mcb)}")
        b5b = {"pearson_r": r5(r_val), "p": r5(p_val), "n": len(cts_for_mcb)}
    else:
        print(f"      B5b: Insufficient m_close_bias data (n={len(cts_for_mcb)})")
        b5b = {"pearson_r": None, "p": None, "note": "insufficient data"}

    # B5c: Phase separation
    b5c = {}
    if len(phase_cts_b5) >= 2:
        groups_b5 = list(phase_cts_b5.values())
        phase_names_b5 = list(phase_cts_b5.keys())
        kw_stat_b5, kw_p_b5 = stats.kruskal(*groups_b5)
        n_total_b5 = sum(len(g) for g in groups_b5)
        k_b5 = len(groups_b5)
        eta2_b5 = (kw_stat_b5 - k_b5 + 1) / (n_total_b5 - k_b5) if n_total_b5 > k_b5 else 0

        phase_means = {}
        for pn in sorted(phase_cts_b5.keys()):
            phase_means[f"{pn}_mean"] = r5(np.mean(phase_cts_b5[pn]))
            print(f"      B5c: {pn}: mean CTS={r5(np.mean(phase_cts_b5[pn]))}, n={len(phase_cts_b5[pn])}")
        print(f"      B5c: KW H={r5(kw_stat_b5)}, p={kw_p_b5:.2e}, eta2={r5(eta2_b5)}")

        b5c = {**phase_means, "eta_squared": r5(eta2_b5), "kw_p": r5(kw_p_b5)}
    else:
        print(f"      B5c: Insufficient phase groups")
        b5c = {"note": "insufficient phase groups"}

    # B5d: q4 discontinuity sensitivity
    b5d = {}
    if len(cts_high_shift) > 5 and len(cts_low_shift) > 5:
        mw_stat, mw_p = stats.mannwhitneyu(cts_high_shift, cts_low_shift, alternative='greater')
        print(f"      B5d: High-shift CTS mean={r5(np.mean(cts_high_shift))}, n={len(cts_high_shift)}")
        print(f"           Low-shift  CTS mean={r5(np.mean(cts_low_shift))}, n={len(cts_low_shift)}")
        print(f"           Mann-Whitney p={mw_p:.2e} (one-sided: high > low)")
        b5d = {
            "high_shift_cts_mean": r5(np.mean(cts_high_shift)),
            "low_shift_cts_mean": r5(np.mean(cts_low_shift)),
            "n_high": len(cts_high_shift),
            "n_low": len(cts_low_shift),
            "mann_whitney_p": r5(mw_p)
        }
    else:
        print(f"      B5d: Insufficient data (high={len(cts_high_shift)}, low={len(cts_low_shift)})")
        b5d = {"note": "insufficient data"}

    results["B_closure_diagnostics"] = {
        "B1_cts_vs_phase": b1,
        "B2_folio_within_section": b2,
        "B3_paragraph_cts_modulation": b3,
        "B4_cts_null_model": b4,
        "B5_line_level_reconstruction": {
            "cts_vs_q4_opaque": b5a,
            "cts_vs_m_close_bias": b5b,
            "phase_separation": b5c,
            "q4_discontinuity": b5d
        }
    }

    # ==================================================================
    # C. PARAGRAPH CLOUD DIAGNOSTICS
    # ==================================================================
    print("\n" + "=" * 70)
    print("C. PARAGRAPH CLOUD DIAGNOSTICS")
    print("=" * 70)

    # C1: E3 hazard vs E2 hazard
    print(f"\n  C1: E3 hazard vs E2 hazard")
    rev_e2_hazard = np.array(rev_ll["hazard"]["E2"])
    rev_e3_hazard = np.array(rev_ll["hazard"]["E3"])
    e2_haz_mean = float(np.mean(rev_e2_hazard))
    e3_haz_mean = float(np.mean(rev_e3_hazard))
    c1_improved = e3_haz_mean > e2_haz_mean

    print(f"      E2 hazard mean LL: {r5(e2_haz_mean)}")
    print(f"      E3 hazard mean LL: {r5(e3_haz_mean)}")
    print(f"      E3 > E2:          {c1_improved}")

    c1 = {
        "E2_hazard_mean": r5(e2_haz_mean),
        "E3_hazard_mean": r5(e3_haz_mean),
        "improved": c1_improved
    }

    # C2: E3 overall vs E2 overall
    print(f"\n  C2: E3 composite vs E2 composite")
    rev_e2_comp = np.array(rev_ll["composite"]["E2"])
    rev_e3_comp = np.array(rev_ll["composite"]["E3"])
    e2_comp_mean = float(np.mean(rev_e2_comp))
    e3_comp_mean = float(np.mean(rev_e3_comp))
    e3_ne_e2 = abs(e3_comp_mean - e2_comp_mean) > 1e-8

    print(f"      E2 composite mean LL: {r5(e2_comp_mean)}")
    print(f"      E3 composite mean LL: {r5(e3_comp_mean)}")
    print(f"      E3 != E2:             {e3_ne_e2}")
    if e3_ne_e2:
        print(f"      Delta:                {r5(e3_comp_mean - e2_comp_mean)}")

    c2 = {
        "E2_composite_mean": r5(e2_comp_mean),
        "E3_composite_mean": r5(e3_comp_mean),
        "e3_ne_e2": e3_ne_e2
    }

    # C3: Paragraph hazard envelope consistency
    print(f"\n  C3: Paragraph hazard envelope consistency")
    c3 = {}
    if para_indices and len(para_indices) > 10:
        # Compute within-paragraph and between-paragraph hazard LL variance
        # Use E3 hazard as proxy for envelope-adjusted hazard
        within_entropies = []
        para_means = []
        for para_key, indices in para_indices.items():
            if len(indices) >= 3:
                para_hazard = rev_e3_hazard[indices]
                # Entropy of the hazard distribution within paragraph
                # Use std as proxy for spread (true entropy would need categorical dist)
                within_std = float(np.std(para_hazard))
                within_entropies.append(within_std)
                para_means.append(float(np.mean(para_hazard)))

        if len(within_entropies) > 5:
            mean_within = float(np.mean(within_entropies))
            between_std = float(np.std(para_means))
            consistent = mean_within < between_std

            print(f"      Within-paragraph mean std: {r5(mean_within)}")
            print(f"      Between-paragraph std:     {r5(between_std)}")
            print(f"      Within < Between:          {consistent}")
            print(f"      n paragraphs (>=3 tokens): {len(within_entropies)}")

            c3 = {
                "within_para_entropy": r5(mean_within),
                "between_para_entropy": r5(between_std),
                "consistent": consistent,
                "n_paragraphs": len(within_entropies)
            }
        else:
            print("      Insufficient paragraphs with >=3 tokens")
            c3 = {"note": "insufficient paragraphs"}
    else:
        print("      Paragraph indices not available — computing from hazard distribution")
        # Fallback: report global hazard variance
        global_haz_std = float(np.std(rev_e3_hazard))
        print(f"      Global hazard LL std: {r5(global_haz_std)}")
        c3 = {"note": "paragraph grouping unavailable", "global_hazard_std": r5(global_haz_std)}

    # C4: Blend sensitivity — informational
    print(f"\n  C4: Paragraph hazard blend sensitivity")
    blend_03_hazard = e3_haz_mean  # T8 used blend=0.3
    print(f"      Blend=0.3 E3 hazard LL: {r5(blend_03_hazard)} (from T8)")
    print(f"      Blend=0.2 and 0.4: deferred (require separate executor runs)")

    c4 = {
        "blend_0.3_E3_hazard": r5(blend_03_hazard),
        "note": "informational; 0.2/0.4 deferred — require separate executor runs"
    }

    results["C_paragraph_cloud"] = {
        "C1_e3_hazard": c1,
        "C2_e3_overall": c2,
        "C3_envelope_consistency": c3,
        "C4_blend_sensitivity": c4
    }

    # ==================================================================
    # D. ABBREVIATED NULL MODELS
    # ==================================================================
    print("\n" + "=" * 70)
    print("D. ABBREVIATED NULL MODELS")
    print("=" * 70)

    # D1: Report original T5 N1 z-score
    print(f"\n  D1: Token-shuffle null (N1)")
    # T5 stores null models under tests -> null_models
    t5_tests = t5.get("tests", {})
    t5_null_models = t5_tests.get("null_models", t5.get("null_models", t5.get("D_null_models", {})))
    n1_data = t5_null_models.get("N1", t5_null_models.get("N1_token_shuffle",
              t5_null_models.get("n1", {})))

    n1_z = None
    if isinstance(n1_data, dict):
        n1_z = n1_data.get("z", n1_data.get("z_score", None))
    elif isinstance(n1_data, (int, float)):
        n1_z = float(n1_data)

    # Try alternate structures
    if n1_z is None:
        # Search recursively in t5
        for key in t5:
            if "null" in key.lower() or "N1" in str(key):
                val = t5[key]
                if isinstance(val, dict):
                    for subk in val:
                        if "z" in subk.lower() and "n1" in subk.lower():
                            n1_z = val[subk]
                        elif isinstance(val[subk], dict):
                            for subsubk in val[subk]:
                                if "z" in subsubk.lower():
                                    n1_z = val[subk][subsubk]

    if n1_z is not None:
        print(f"      Original T5 N1 z-score: {r5(n1_z)}")
    else:
        print(f"      N1 z-score not found in T5")
        print(f"      T5 keys: {list(t5.keys())}")
        if "null_models" in t5:
            print(f"      null_models keys: {list(t5['null_models'].keys())}")

    d1 = {
        "original_z": r5(n1_z) if n1_z is not None else None,
        "note": "architecture unchanged; N1 z applies to both original and revised"
    }

    # D2: Report original T5 N4 z-score
    print(f"\n  D2: Domain form-shuffle null (N4)")
    n4_data = t5_null_models.get("N4", t5_null_models.get("N4_domain_form_shuffle",
              t5_null_models.get("N4_form_shuffle", t5_null_models.get("n4", {}))))

    n4_z = None
    if isinstance(n4_data, dict):
        n4_z = n4_data.get("z", n4_data.get("z_score", None))
    elif isinstance(n4_data, (int, float)):
        n4_z = float(n4_data)

    if n4_z is None:
        for key in t5:
            val = t5[key]
            if isinstance(val, dict):
                for subk in val:
                    if "n4" in subk.lower() or "form" in subk.lower():
                        subval = val[subk]
                        if isinstance(subval, dict):
                            for ssk in subval:
                                if "z" in ssk.lower():
                                    n4_z = subval[ssk]

    if n4_z is not None:
        print(f"      Original T5 N4 z-score: {r5(n4_z)}")
    else:
        print(f"      N4 z-score not found in T5")

    d2 = {
        "original_z": r5(n4_z) if n4_z is not None else None,
        "note": "domain axis unchanged; N4 z applies to both original and revised"
    }

    # Bootstrap CI on delta
    print(f"\n  D_bootstrap: Bootstrap CI on composite E4 delta")
    n_boot = 1000
    np.random.seed(42)
    boot_deltas = []
    for _ in range(n_boot):
        idx = np.random.choice(n_tokens, n_tokens, replace=True)
        boot_orig = np.mean(orig_composite_e4[idx])
        boot_rev = np.mean(rev_composite_e4[idx])
        boot_deltas.append(boot_rev - boot_orig)

    boot_deltas = np.array(boot_deltas)
    ci_lo = float(np.percentile(boot_deltas, 2.5))
    ci_hi = float(np.percentile(boot_deltas, 97.5))
    boot_mean = float(np.mean(boot_deltas))

    print(f"      Bootstrap mean delta: {r5(boot_mean)}")
    print(f"      95% CI: [{r5(ci_lo)}, {r5(ci_hi)}]")
    print(f"      CI excludes 0: {ci_lo > 0 or ci_hi < 0}")

    d_bootstrap = {
        "mean_delta": r5(boot_mean),
        "ci_95_low": r5(ci_lo),
        "ci_95_high": r5(ci_hi),
        "ci_excludes_zero": bool(ci_lo > 0 or ci_hi < 0)
    }

    results["D_null_models"] = {
        "D1_token_shuffle": d1,
        "D2_domain_form_shuffle": d2,
        "D_bootstrap_ci": d_bootstrap
    }

    # ==================================================================
    # VERDICT
    # ==================================================================
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    if improved and wilcoxon_p < 0.05:
        verdict = "IMPROVED"
    elif not improved and wilcoxon_p < 0.05:
        verdict = "DEGRADED"
    else:
        verdict = "NEUTRAL"

    # Build summary string
    delta_pct = (delta_composite / abs(orig_e4_mean) * 100) if orig_e4_mean != 0 else 0
    improved_axes = [ax for ax in AXES if a2[ax]["delta"] > 0]
    degraded_axes = [ax for ax in AXES if a2[ax]["delta"] < 0]

    summary_parts = []
    summary_parts.append(f"Revised E4 composite {r5(rev_e4_mean)} vs original {r5(orig_e4_mean)}"
                         f" (delta={r5(delta_composite)}, {r5(delta_pct)}%).")
    if improved_axes:
        summary_parts.append(f"Improved axes: {', '.join(improved_axes)}.")
    if degraded_axes:
        summary_parts.append(f"Degraded axes: {', '.join(degraded_axes)}.")
    summary_parts.append(f"Wilcoxon p={wilcoxon_p:.2e}, effect r={r5(effect_r)}.")
    if mono_holds:
        summary_parts.append("Monotonicity E4>=E3>=E2>E1 holds.")
    else:
        summary_parts.append("WARNING: Monotonicity violated.")

    summary = " ".join(summary_parts)

    print(f"\n  Verdict: {verdict}")
    print(f"  {summary}")

    results["verdict"] = verdict
    results["summary"] = summary

    # ==================================================================
    # Write output
    # ==================================================================
    print(f"\n{'=' * 70}")
    print(f"Writing results to {OUTPUT_PATH.name}")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Done. {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
