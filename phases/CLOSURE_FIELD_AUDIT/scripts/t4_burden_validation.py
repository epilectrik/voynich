#!/usr/bin/env python3
"""
T4: Burden-based metric validation for Phase 567 (CLOSURE_FIELD_AUDIT).

Validates whether the new burden-based metrics (PCV, SAHB, QGY, REF, CRE, MPZF)
improve discrimination between the full model and null/baseline models.

Tests:
  P2       - Anchor test: line packet shape recovery
  NP1-NP7  - Primary tests: full model vs null/baseline
  CD1-CD8  - Comparative diagnostics

Input:
  t2_burden_runs.json              - Full model results (90 runs)
  t3_burden_null_runs.json         - Null/baseline results (~4,200 runs)
  t2b_supervisory_interface_unrouted.json - Supervisory tokens (for P2)

Output:
  t4_burden_validation.json
"""

import json
import sys
import os
import math
from datetime import datetime
from collections import defaultdict

import numpy as np
from scipy import stats


class NumpyEncoder(json.JSONEncoder):
    """Handle numpy types in JSON serialization."""
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE, "results")

T2_PATH = os.path.join(RESULTS_DIR, "t2_burden_runs.json")
T3_PATH = os.path.join(RESULTS_DIR, "t3_burden_null_runs.json")
SV_PATH = os.path.join(
    os.path.dirname(BASE),
    "VIRTUAL_APPARATUS_COUPLING", "results",
    "t2b_supervisory_interface_unrouted.json"
)
OUT_PATH = os.path.join(RESULTS_DIR, "t4_burden_validation.json")

SV_NAMES = ["T", "RC", "S", "C", "TR", "X", "Y"]


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


# ===================================================================
# P2: Anchor test  --  line packet shape recovery
# ===================================================================
def run_p2(sv_data):
    """
    Group token contributions by packet_phase (SPEC/WORK/CLOSE).
    For each SV (7 total), Kruskal-Wallis on contribution magnitudes
    across the 3 phases.
    PASS: >= 5/7 SVs have p < 0.05.
    """
    tokens = sv_data["token_signals"]

    # Build groups: phase -> list of contribution vectors
    phase_contribs = defaultdict(list)
    for t in tokens:
        pp = t.get("packet_phase")
        if pp in ("SPEC", "WORK", "CLOSE"):
            phase_contribs[pp].append(t["contributions"])

    per_sv = {}
    n_sig = 0
    for sv_idx, sv_name in enumerate(SV_NAMES):
        groups = []
        for phase in ("SPEC", "WORK", "CLOSE"):
            magnitudes = [abs(c[sv_idx]) for c in phase_contribs[phase]]
            groups.append(magnitudes)

        if all(len(g) > 0 for g in groups):
            H_stat, p_val = stats.kruskal(*groups)
        else:
            H_stat, p_val = 0.0, 1.0

        sig = p_val < 0.05
        if sig:
            n_sig += 1

        per_sv[sv_name] = {
            "H": round(H_stat, 4),
            "p": round(p_val, 6),
            "significant": sig
        }

    result = "PASS" if n_sig >= 5 else "FAIL"
    return {
        "result": result,
        "n_significant": n_sig,
        "threshold": 5,
        "per_sv": per_sv
    }


# ===================================================================
# Helpers: extract preferred-profile full-model data
# ===================================================================
def get_preferred_runs(t2_data):
    """
    For each folio, select the profile with the highest PCV.
    Returns dict: folio -> run_dict (with profile key added).
    """
    preferred = {}
    for folio, profiles in t2_data["primary_runs"].items():
        best_profile = max(profiles.keys(), key=lambda p: profiles[p]["PCV"])
        run = dict(profiles[best_profile])
        run["_profile"] = best_profile
        preferred[folio] = run
    return preferred


def get_null_means(t3_data, null_key, metric_key):
    """Return dict: folio -> mean value for a given null model and metric."""
    out = {}
    for folio, vals in t3_data["null_runs"][null_key].items():
        out[folio] = vals.get(metric_key, 0.0)
    return out


def get_baseline_by_folio(t3_data, baseline_key):
    """Return dict: folio -> run_dict for a given baseline."""
    out = {}
    for run in t3_data["baseline_runs"][baseline_key]:
        out[run["folio"]] = run
    return out


# ===================================================================
# NP1: Full PCV > N1 (phase-shuffled)
# ===================================================================
def run_np1(preferred, t3_data):
    n1_pcv = get_null_means(t3_data, "N1", "mean_PCV")
    folios = sorted(preferred.keys())
    details = []
    n_pass = 0
    for fo in folios:
        full_val = preferred[fo]["PCV"]
        null_val = n1_pcv.get(fo, 0.0)
        passed = full_val > null_val
        if passed:
            n_pass += 1
        details.append({
            "folio": fo,
            "full_PCV": round(full_val, 6),
            "N1_mean_PCV": round(null_val, 6),
            "pass": passed
        })
    result = "PASS" if n_pass >= 14 else "FAIL"
    return {
        "result": result,
        "n_folios_passing": n_pass,
        "n_total": len(folios),
        "threshold": 14,
        "details": details
    }


# ===================================================================
# NP2: Full SAHB < N1 (lower burden = better)
# ===================================================================
def run_np2(preferred, t3_data):
    n1_sahb = get_null_means(t3_data, "N1", "mean_SAHB")
    folios = sorted(preferred.keys())
    details = []
    n_pass = 0
    for fo in folios:
        full_val = preferred[fo]["SAHB"]
        null_val = n1_sahb.get(fo, 0.0)
        passed = full_val < null_val
        if passed:
            n_pass += 1
        details.append({
            "folio": fo,
            "full_SAHB": round(full_val, 6),
            "N1_mean_SAHB": round(null_val, 6),
            "pass": passed
        })
    result = "PASS" if n_pass >= 14 else "FAIL"
    return {
        "result": result,
        "n_folios_passing": n_pass,
        "n_total": len(folios),
        "threshold": 14,
        "details": details
    }


# ===================================================================
# NP3: Full QGY > N2 (contribution-shuffled)
# ===================================================================
def run_np3(preferred, t3_data):
    n2_qgy = get_null_means(t3_data, "N2", "mean_QGY")
    folios = sorted(preferred.keys())
    details = []
    n_pass = 0
    # Check for degeneracy (all zeroes)
    full_all_zero = all(preferred[fo]["QGY"] == 0.0 for fo in folios)
    null_all_zero = all(n2_qgy.get(fo, 0.0) == 0.0 for fo in folios)
    if full_all_zero and null_all_zero:
        return {
            "result": "NOT_EVALUABLE",
            "reason": "QGY is 0 for both full and N2 across all folios",
            "n_folios_passing": 0,
            "n_total": len(folios),
            "threshold": 14,
            "details": []
        }

    for fo in folios:
        full_val = preferred[fo]["QGY"]
        null_val = n2_qgy.get(fo, 0.0)
        passed = full_val > null_val
        if passed:
            n_pass += 1
        details.append({
            "folio": fo,
            "full_QGY": round(full_val, 6),
            "N2_mean_QGY": round(null_val, 6),
            "pass": passed
        })
    result = "PASS" if n_pass >= 14 else "FAIL"
    return {
        "result": result,
        "n_folios_passing": n_pass,
        "n_total": len(folios),
        "threshold": 14,
        "details": details
    }


# ===================================================================
# NP4: Full QGY > N4 (random walk)
# ===================================================================
def run_np4(preferred, t3_data):
    n4_qgy = get_null_means(t3_data, "N4", "mean_QGY")
    folios = sorted(preferred.keys())
    details = []
    n_pass = 0

    full_all_zero = all(preferred[fo]["QGY"] == 0.0 for fo in folios)
    null_all_zero = all(n4_qgy.get(fo, 0.0) == 0.0 for fo in folios)
    if full_all_zero and null_all_zero:
        return {
            "result": "NOT_EVALUABLE",
            "reason": "QGY is 0 for both full and N4 across all folios",
            "n_folios_passing": 0,
            "n_total": len(folios),
            "threshold": 14,
            "details": []
        }

    for fo in folios:
        full_val = preferred[fo]["QGY"]
        null_val = n4_qgy.get(fo, 0.0)
        passed = full_val > null_val
        if passed:
            n_pass += 1
        details.append({
            "folio": fo,
            "full_QGY": round(full_val, 6),
            "N4_mean_QGY": round(null_val, 6),
            "pass": passed
        })
    result = "PASS" if n_pass >= 14 else "FAIL"
    return {
        "result": result,
        "n_folios_passing": n_pass,
        "n_total": len(folios),
        "threshold": 14,
        "details": details
    }


# ===================================================================
# NP5: Full REF > mean(N1-N4) REF
# ===================================================================
def run_np5(preferred, t3_data):
    folios = sorted(preferred.keys())

    # Collect null REF means per folio
    null_ref_means = {}
    for fo in folios:
        null_vals = []
        for nk in ("N1", "N2", "N3", "N4"):
            val = t3_data["null_runs"][nk].get(fo, {}).get("mean_REF_mean", 0.0)
            null_vals.append(val)
        null_ref_means[fo] = np.mean(null_vals)

    # Check degeneracy
    full_all_zero = all(preferred[fo]["REF_mean"] == 0.0 for fo in folios)
    null_all_zero = all(null_ref_means[fo] == 0.0 for fo in folios)
    if full_all_zero and null_all_zero:
        return {
            "result": "NOT_EVALUABLE",
            "reason": "REF is 0 for both full and all null models across all folios (degenerate - no eligible excursions at line boundaries)",
            "n_folios_passing": 0,
            "n_total": len(folios),
            "threshold": 14,
            "details": []
        }

    details = []
    n_pass = 0
    for fo in folios:
        full_val = preferred[fo]["REF_mean"]
        null_val = null_ref_means[fo]
        passed = full_val > null_val
        if passed:
            n_pass += 1
        details.append({
            "folio": fo,
            "full_REF": round(full_val, 6),
            "mean_null_REF": round(null_val, 6),
            "pass": passed
        })
    result = "PASS" if n_pass >= 14 else "FAIL"
    return {
        "result": result,
        "n_folios_passing": n_pass,
        "n_total": len(folios),
        "threshold": 14,
        "details": details
    }


# ===================================================================
# NP6: B10 sensitivity under PCV (adaptive)
# ===================================================================
def run_np6(preferred, t3_data):
    b10 = get_baseline_by_folio(t3_data, "B10")
    folios = sorted(preferred.keys())

    full_pcv_vals = [preferred[fo]["PCV"] for fo in folios]
    b10_pcv_vals = [b10[fo]["PCV"] for fo in folios if fo in b10]

    mean_full = np.mean(full_pcv_vals)
    mean_b10 = np.mean(b10_pcv_vals)

    abs_delta = mean_full - mean_b10

    # Dynamic range: all PCV values across all model types
    all_pcv = list(full_pcv_vals) + list(b10_pcv_vals)
    # Also include baselines and null means
    for bk in t3_data["baseline_runs"]:
        for run in t3_data["baseline_runs"][bk]:
            all_pcv.append(run["PCV"])
    for nk in t3_data["null_runs"]:
        for fo in t3_data["null_runs"][nk]:
            all_pcv.append(t3_data["null_runs"][nk][fo].get("mean_PCV", 0.0))
    dyn_range = max(all_pcv) - min(all_pcv)

    rel_delta_pct = (abs_delta / dyn_range * 100) if dyn_range > 0 else 0.0

    # Cohen's d
    pooled_std = np.sqrt(
        (np.std(full_pcv_vals, ddof=1) ** 2 + np.std(b10_pcv_vals, ddof=1) ** 2) / 2
    )
    cohens_d = abs_delta / pooled_std if pooled_std > 0 else 0.0

    passed = abs(abs_delta) > 0.01 or abs(rel_delta_pct) > 2.0 or abs(cohens_d) > 0.3

    return {
        "result": "PASS" if passed else "FAIL",
        "mean_full_PCV": round(mean_full, 6),
        "mean_B10_PCV": round(mean_b10, 6),
        "absolute_delta": round(abs_delta, 6),
        "dynamic_range": round(dyn_range, 6),
        "relative_delta_pct": round(rel_delta_pct, 4),
        "cohens_d": round(cohens_d, 4),
        "criteria": {
            "abs_delta_gt_0.01": abs(abs_delta) > 0.01,
            "rel_delta_gt_2pct": abs(rel_delta_pct) > 2.0,
            "cohens_d_gt_0.3": abs(cohens_d) > 0.3
        }
    }


# ===================================================================
# NP7: S contribution to SAHB (soft gate)
# ===================================================================
def run_np7(preferred):
    """
    Estimate S's share of SAHB from zone occupancy data.

    SAHB excludes high-S contacts (by design of asymmetric scoring).
    We estimate S_share as the fraction of total warning+hard_stop contacts
    (excluding S) that S contributes after the asymmetric correction.

    Since SAHB already applies S-asymmetry, we measure what fraction of the
    total burden (sum of all SVs' warning+hard_stop contacts, excluding the
    S high contacts) comes from S's remaining warning+hard_stop after
    correction.

    Approach: Use warning_contacts and hard_stop_contacts per SV from T2.
    S contacts are already the post-correction values in SAHB scoring.
    We compute S_share = S_contacts / total_contacts (all SVs).
    """
    total_all_sv = 0
    total_s = 0

    for fo, run in preferred.items():
        wc = run.get("warning_contacts", {})
        hc = run.get("hard_stop_contacts", {})
        for sv in SV_NAMES:
            w = wc.get(sv, 0) if isinstance(wc, dict) else 0
            h = hc.get(sv, 0) if isinstance(hc, dict) else 0
            total_all_sv += w + h
            if sv == "S":
                total_s += w + h

    s_share_pct = (total_s / total_all_sv * 100) if total_all_sv > 0 else 0.0
    passed = s_share_pct < 30.0

    return {
        "result": "PASS" if passed else "FAIL",
        "s_share_pct": round(s_share_pct, 2),
        "total_S_contacts": total_s,
        "total_all_contacts": total_all_sv,
        "threshold_pct": 30.0,
        "note": "SOFT PASS criterion: S_share < 30%"
    }


# ===================================================================
# CD1: Old viability vs PCV correlation
# ===================================================================
def run_cd1(preferred):
    folios = sorted(preferred.keys())
    old_viab = [preferred[fo]["old_viability"] for fo in folios]
    pcv = [preferred[fo]["PCV"] for fo in folios]

    # Pearson
    if np.std(old_viab) == 0 or np.std(pcv) == 0:
        pearson_r, pearson_p = 0.0, 1.0
    else:
        pearson_r, pearson_p = stats.pearsonr(old_viab, pcv)

    # Spearman
    spearman_r, spearman_p = stats.spearmanr(old_viab, pcv)

    return {
        "pearson_r": round(float(pearson_r), 4),
        "pearson_p": round(float(pearson_p), 6),
        "spearman_r": round(float(spearman_r), 4),
        "spearman_p": round(float(spearman_p), 6),
        "interpretation": (
            "Low correlation: PCV and old_viability measure different things"
            if abs(pearson_r) < 0.5
            else "Moderate-to-high correlation: PCV partially overlaps with old_viability"
        )
    }


# ===================================================================
# CD2: SAHB vs old hazard burden
# ===================================================================
def run_cd2(preferred):
    """
    Compare S's contribution under old vs new scoring.
    Under old scoring: S warning+hard_stop are counted equally to other SVs.
    Under SAHB: S high contacts are excluded (asymmetric).
    We estimate the fraction of edge contacts removed by S asymmetry.
    """
    folios = sorted(preferred.keys())
    total_s_contacts = 0
    total_non_s_contacts = 0

    for fo in folios:
        wc = preferred[fo].get("warning_contacts", {})
        hc = preferred[fo].get("hard_stop_contacts", {})
        for sv in SV_NAMES:
            w = wc.get(sv, 0) if isinstance(wc, dict) else 0
            h = hc.get(sv, 0) if isinstance(hc, dict) else 0
            if sv == "S":
                total_s_contacts += w + h
            else:
                total_non_s_contacts += w + h

    total = total_s_contacts + total_non_s_contacts
    s_fraction = total_s_contacts / total if total > 0 else 0.0

    return {
        "total_S_warning_hardstop": total_s_contacts,
        "total_nonS_warning_hardstop": total_non_s_contacts,
        "S_fraction_of_all_edge_contacts": round(s_fraction, 4),
        "fraction_removed_by_asymmetry": round(s_fraction, 4),
        "note": "SAHB excludes high-S contacts; this fraction shows how much edge burden S dominates under old scoring"
    }


# ===================================================================
# CD3: QGY vs Y_final by model type
# ===================================================================
def run_cd3(preferred, t3_data):
    folios = sorted(preferred.keys())

    # Full model
    full_qgy = np.mean([preferred[fo]["QGY"] for fo in folios])
    full_yfinal = np.mean([preferred[fo]["old_y_final"] for fo in folios])

    # B2
    b2 = get_baseline_by_folio(t3_data, "B2")
    b2_qgy = np.mean([b2[fo]["QGY"] for fo in folios if fo in b2])
    b2_yfinal = np.mean([b2[fo]["old_y_final"] for fo in folios if fo in b2])

    # Nulls
    null_results = {}
    for nk in ("N1", "N2", "N3", "N4"):
        nk_qgy = np.mean([
            t3_data["null_runs"][nk][fo].get("mean_QGY", 0.0)
            for fo in folios if fo in t3_data["null_runs"][nk]
        ])
        nk_yfinal = np.mean([
            t3_data["null_runs"][nk][fo].get("mean_old_y_final", 0.0)
            for fo in folios if fo in t3_data["null_runs"][nk]
        ])
        null_results[nk] = {
            "mean_QGY": round(float(nk_qgy), 6),
            "mean_Y_final": round(float(nk_yfinal), 6)
        }

    n2_paradox = (
        null_results["N2"]["mean_QGY"] < full_qgy
        and null_results["N2"]["mean_Y_final"] > full_yfinal
    )

    return {
        "full": {"mean_QGY": round(float(full_qgy), 6), "mean_Y_final": round(float(full_yfinal), 6)},
        "B2": {"mean_QGY": round(float(b2_qgy), 6), "mean_Y_final": round(float(b2_yfinal), 6)},
        **null_results,
        "N2_paradox_inversion": n2_paradox,
        "note": "N2 paradox: N2 QGY < full QGY even if N2 Y_final > full Y_final"
    }


# ===================================================================
# CD4: REF by model type
# ===================================================================
def run_cd4(preferred, t3_data):
    folios = sorted(preferred.keys())

    full_ref = np.mean([preferred[fo]["REF_mean"] for fo in folios])
    full_elig = np.mean([preferred[fo]["REF_eligible_fraction"] for fo in folios])
    full_worst = np.mean([preferred[fo]["REF_worsened_fraction"] for fo in folios])

    b2 = get_baseline_by_folio(t3_data, "B2")
    b2_ref = np.mean([b2[fo]["REF_mean"] for fo in folios if fo in b2])

    null_ref = {}
    for nk in ("N1", "N2", "N3", "N4"):
        vals = [
            t3_data["null_runs"][nk][fo].get("mean_REF_mean", 0.0)
            for fo in folios if fo in t3_data["null_runs"][nk]
        ]
        null_ref[nk] = round(float(np.mean(vals)), 6)

    degenerate = (
        full_ref == 0.0
        and all(v == 0.0 for v in null_ref.values())
        and b2_ref == 0.0
    )

    result = {
        "full": {
            "REF_mean": round(float(full_ref), 6),
            "REF_eligible_fraction": round(float(full_elig), 6),
            "REF_worsened_fraction": round(float(full_worst), 6),
        },
        "B2": {"REF_mean": round(float(b2_ref), 6)},
    }
    result.update({nk: {"REF_mean": v} for nk, v in null_ref.items()})
    result["degenerate"] = degenerate
    if degenerate:
        result["note"] = "degenerate - no eligible excursions at line boundaries"

    return result


# ===================================================================
# CD5: B10 under old vs new metrics
# ===================================================================
def run_cd5(preferred, t3_data):
    b10 = get_baseline_by_folio(t3_data, "B10")
    folios = sorted(preferred.keys())

    metrics = {
        "old_viability": {"higher_better": True},
        "PCV": {"higher_better": True},
        "SAHB": {"higher_better": False},
        "QGY": {"higher_better": True},
    }

    deltas = {}
    for metric, info in metrics.items():
        full_vals = [preferred[fo].get(metric, 0.0) for fo in folios]
        b10_vals = [b10[fo].get(metric, 0.0) for fo in folios if fo in b10]
        mean_full = float(np.mean(full_vals))
        mean_b10 = float(np.mean(b10_vals))
        delta = mean_full - mean_b10
        deltas[metric] = {
            "mean_full": round(mean_full, 6),
            "mean_B10": round(mean_b10, 6),
            "delta": round(delta, 6),
            "direction": "full better" if (
                (delta > 0 and info["higher_better"])
                or (delta < 0 and not info["higher_better"])
            ) else "B10 better or equal"
        }

    return {
        "deltas": deltas,
        "note": "Does CLOSE recovery become load-bearing under better metrics?"
    }


# ===================================================================
# CD6: CRE_strict vs CRE_soft
# ===================================================================
def run_cd6(preferred, t3_data):
    folios = sorted(preferred.keys())

    full_strict = float(np.mean([preferred[fo]["CRE_strict"] for fo in folios]))
    full_soft = float(np.mean([preferred[fo]["CRE_soft"] for fo in folios]))

    null_strict = {}
    null_soft = {}
    for nk in ("N1", "N2", "N3", "N4"):
        s_vals = [
            t3_data["null_runs"][nk][fo].get("mean_CRE_strict", 0.0)
            for fo in folios if fo in t3_data["null_runs"][nk]
        ]
        sf_vals = [
            t3_data["null_runs"][nk][fo].get("mean_CRE_soft", 0.0)
            for fo in folios if fo in t3_data["null_runs"][nk]
        ]
        null_strict[nk] = round(float(np.mean(s_vals)), 6)
        null_soft[nk] = round(float(np.mean(sf_vals)), 6)

    window_masking = full_soft > full_strict

    return {
        "full": {
            "CRE_strict": round(full_strict, 6),
            "CRE_soft": round(full_soft, 6),
        },
        "null_CRE_strict": null_strict,
        "null_CRE_soft": null_soft,
        "window_truncation_masking": window_masking,
        "note": "CRE_soft > CRE_strict indicates window truncation masks real returns"
    }


# ===================================================================
# CD7: QGY/Y_final ratio by model type
# ===================================================================
def run_cd7(preferred, t3_data):
    folios = sorted(preferred.keys())

    full_ratio = float(np.mean([preferred[fo]["qgy_ratio"] for fo in folios]))

    results = {"full": round(full_ratio, 6)}

    # B2 and B10
    for bk in ("B2", "B10"):
        bdata = get_baseline_by_folio(t3_data, bk)
        vals = [bdata[fo]["qgy_ratio"] for fo in folios if fo in bdata]
        results[bk] = round(float(np.mean(vals)), 6) if vals else 0.0

    # Nulls
    for nk in ("N1", "N2", "N3", "N4"):
        vals = [
            t3_data["null_runs"][nk][fo].get("mean_qgy_ratio", 0.0)
            for fo in folios if fo in t3_data["null_runs"][nk]
        ]
        results[nk] = round(float(np.mean(vals)), 6)

    full_higher_than_nulls = all(
        full_ratio > results[nk] for nk in ("N1", "N2", "N3", "N4")
    )

    results["full_higher_than_all_nulls"] = full_higher_than_nulls
    results["note"] = "Does full have higher quality fraction than nulls?"

    return results


# ===================================================================
# CD8: NP3/NP4 graded diagnostic
# ===================================================================
def run_cd8(preferred, t3_data):
    folios = sorted(preferred.keys())

    full_qgy = [preferred[fo]["QGY"] for fo in folios]

    diagnostics = {}
    for nk in ("N2", "N4"):
        null_qgy = [
            t3_data["null_runs"][nk][fo].get("mean_QGY", 0.0)
            for fo in folios if fo in t3_data["null_runs"][nk]
        ]

        median_full = float(np.median(full_qgy))
        median_null = float(np.median(null_qgy))

        # Mann-Whitney U
        if len(full_qgy) > 0 and len(null_qgy) > 0:
            u_stat, p_val = stats.mannwhitneyu(
                full_qgy, null_qgy, alternative="greater"
            )
            # Rank-biserial effect size: r = 1 - 2U/(n1*n2)
            n1, n2 = len(full_qgy), len(null_qgy)
            rank_biserial = 1.0 - (2.0 * u_stat) / (n1 * n2)
        else:
            u_stat, p_val, rank_biserial = 0.0, 1.0, 0.0

        diagnostics[nk] = {
            "median_full_QGY": round(median_full, 6),
            f"median_{nk}_QGY": round(median_null, 6),
            "U_statistic": round(float(u_stat), 4),
            "p_value": round(float(p_val), 6),
            "rank_biserial": round(float(rank_biserial), 4),
        }

    return diagnostics


# ===================================================================
# Main
# ===================================================================
def main():
    print("=" * 70)
    print("T4: Burden-based metric validation (Phase 567)")
    print("=" * 70)

    # Load data
    print("\nLoading input files...")
    t2_data = load_json(T2_PATH)
    t3_data = load_json(T3_PATH)
    sv_data = load_json(SV_PATH)
    print(f"  T2: {t2_data['metadata']['n_runs']} runs")
    print(f"  T3: {t3_data['metadata']['total_runs']} runs")
    print(f"  SV: {sv_data['metadata']['n_tokens']} tokens")

    # Extract preferred profiles
    preferred = get_preferred_runs(t2_data)
    print(f"\n  Preferred profiles selected for {len(preferred)} folios:")
    for fo in sorted(preferred.keys()):
        p = preferred[fo]["_profile"]
        pcv = preferred[fo]["PCV"]
        print(f"    {fo}: {p} (PCV={pcv:.5f})")

    # ---------------------------------------------------------------
    # P2: Anchor test
    # ---------------------------------------------------------------
    print("\n" + "-" * 50)
    print("ANCHOR TEST: P2 (Line Packet Shape Recovery)")
    print("-" * 50)
    p2 = run_p2(sv_data)
    print(f"  Result: {p2['result']} ({p2['n_significant']}/7 SVs significant, need >= {p2['threshold']})")
    for sv_name, sv_info in p2["per_sv"].items():
        sig_mark = "*" if sv_info["significant"] else " "
        print(f"    {sig_mark} {sv_name}: H={sv_info['H']:.2f}, p={sv_info['p']:.6f}")

    # ---------------------------------------------------------------
    # NP1-NP7
    # ---------------------------------------------------------------
    print("\n" + "-" * 50)
    print("PRIMARY TESTS (NP1-NP7)")
    print("-" * 50)

    np1 = run_np1(preferred, t3_data)
    print(f"\n  NP1 (Full PCV > N1): {np1['result']} ({np1['n_folios_passing']}/{np1['n_total']} folios, need >= {np1['threshold']})")

    np2 = run_np2(preferred, t3_data)
    print(f"  NP2 (Full SAHB < N1): {np2['result']} ({np2['n_folios_passing']}/{np2['n_total']} folios, need >= {np2['threshold']})")

    np3 = run_np3(preferred, t3_data)
    print(f"  NP3 (Full QGY > N2):  {np3['result']} ({np3.get('n_folios_passing', 'N/A')}/{np3.get('n_total', 'N/A')} folios, need >= {np3.get('threshold', 'N/A')})")

    np4 = run_np4(preferred, t3_data)
    print(f"  NP4 (Full QGY > N4):  {np4['result']} ({np4.get('n_folios_passing', 'N/A')}/{np4.get('n_total', 'N/A')} folios, need >= {np4.get('threshold', 'N/A')})")

    np5 = run_np5(preferred, t3_data)
    print(f"  NP5 (Full REF > null): {np5['result']} ({np5.get('n_folios_passing', 'N/A')}/{np5.get('n_total', 'N/A')} folios, need >= {np5.get('threshold', 'N/A')})")

    np6 = run_np6(preferred, t3_data)
    print(f"  NP6 (B10 PCV sensitivity): {np6['result']}")
    print(f"       abs_delta={np6['absolute_delta']:.6f}, rel_delta={np6['relative_delta_pct']:.2f}%, Cohen's d={np6['cohens_d']:.4f}")

    np7 = run_np7(preferred)
    print(f"  NP7 (S share of SAHB): {np7['result']} (S_share={np7['s_share_pct']:.1f}%, threshold <{np7['threshold_pct']}%)")

    # ---------------------------------------------------------------
    # CD1-CD8
    # ---------------------------------------------------------------
    print("\n" + "-" * 50)
    print("COMPARATIVE DIAGNOSTICS (CD1-CD8)")
    print("-" * 50)

    cd1 = run_cd1(preferred)
    print(f"\n  CD1 (old_viability vs PCV):")
    print(f"       Pearson r={cd1['pearson_r']:.4f} (p={cd1['pearson_p']:.6f})")
    print(f"       Spearman r={cd1['spearman_r']:.4f} (p={cd1['spearman_p']:.6f})")
    print(f"       {cd1['interpretation']}")

    cd2 = run_cd2(preferred)
    print(f"\n  CD2 (SAHB vs old hazard burden):")
    print(f"       S edge contacts: {cd2['total_S_warning_hardstop']}")
    print(f"       non-S edge contacts: {cd2['total_nonS_warning_hardstop']}")
    print(f"       S fraction: {cd2['S_fraction_of_all_edge_contacts']:.4f}")

    cd3 = run_cd3(preferred, t3_data)
    print(f"\n  CD3 (QGY vs Y_final by model type):")
    print(f"       Full:  QGY={cd3['full']['mean_QGY']:.6f}, Y_final={cd3['full']['mean_Y_final']:.6f}")
    print(f"       B2:    QGY={cd3['B2']['mean_QGY']:.6f}, Y_final={cd3['B2']['mean_Y_final']:.6f}")
    for nk in ("N1", "N2", "N3", "N4"):
        print(f"       {nk}:    QGY={cd3[nk]['mean_QGY']:.6f}, Y_final={cd3[nk]['mean_Y_final']:.6f}")
    print(f"       N2 paradox inversion: {cd3['N2_paradox_inversion']}")

    cd4 = run_cd4(preferred, t3_data)
    print(f"\n  CD4 (REF by model type):")
    print(f"       Full REF={cd4['full']['REF_mean']:.6f}, eligible={cd4['full']['REF_eligible_fraction']:.4f}, worsened={cd4['full']['REF_worsened_fraction']:.4f}")
    print(f"       Degenerate: {cd4['degenerate']}")

    cd5 = run_cd5(preferred, t3_data)
    print(f"\n  CD5 (B10 old vs new metrics):")
    for metric, info in cd5["deltas"].items():
        print(f"       {metric}: full={info['mean_full']:.6f}, B10={info['mean_B10']:.6f}, delta={info['delta']:.6f} ({info['direction']})")

    cd6 = run_cd6(preferred, t3_data)
    print(f"\n  CD6 (CRE_strict vs CRE_soft):")
    print(f"       Full: strict={cd6['full']['CRE_strict']:.6f}, soft={cd6['full']['CRE_soft']:.6f}")
    print(f"       Window truncation masking: {cd6['window_truncation_masking']}")

    cd7 = run_cd7(preferred, t3_data)
    print(f"\n  CD7 (qgy_ratio by model type):")
    for k in ("full", "B2", "B10", "N1", "N2", "N3", "N4"):
        print(f"       {k}: {cd7[k]:.6f}" if isinstance(cd7[k], float) else f"       {k}: {cd7[k]}")
    print(f"       Full higher than all nulls: {cd7['full_higher_than_all_nulls']}")

    cd8 = run_cd8(preferred, t3_data)
    print(f"\n  CD8 (NP3/NP4 graded diagnostic):")
    for nk in ("N2", "N4"):
        d = cd8[nk]
        print(f"       vs {nk}: median_full={d['median_full_QGY']:.6f}, "
              f"median_{nk}={d[f'median_{nk}_QGY']:.6f}, "
              f"U={d['U_statistic']:.1f}, p={d['p_value']:.6f}, "
              f"r_rb={d['rank_biserial']:.4f}")

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    all_np = {
        "NP1": np1, "NP2": np2, "NP3": np3, "NP4": np4,
        "NP5": np5, "NP6": np6, "NP7": np7
    }
    tests_passed = [k for k, v in all_np.items() if v["result"] == "PASS"]
    tests_failed = [k for k, v in all_np.items() if v["result"] == "FAIL"]
    tests_ne = [k for k, v in all_np.items() if v["result"] == "NOT_EVALUABLE"]

    np_pass_count = len(tests_passed)
    anchor_pass = p2["result"] == "PASS"

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Anchor P2: {'PASS' if anchor_pass else 'FAIL'}")
    print(f"  Primary tests: {np_pass_count}/{len(all_np)} passed")
    if tests_passed:
        print(f"    Passed: {', '.join(tests_passed)}")
    if tests_failed:
        print(f"    Failed: {', '.join(tests_failed)}")
    if tests_ne:
        print(f"    Not evaluable: {', '.join(tests_ne)}")
    print("=" * 70)

    # ---------------------------------------------------------------
    # Write output
    # ---------------------------------------------------------------
    output = {
        "metadata": {
            "phase": 567,
            "script": "t4_burden_validation.py",
            "timestamp": datetime.now().isoformat(),
            "input_files": {
                "t2": os.path.basename(T2_PATH),
                "t3": os.path.basename(T3_PATH),
                "sv": os.path.basename(SV_PATH),
            },
            "n_folios": len(preferred),
            "preferred_profiles": {
                fo: preferred[fo]["_profile"] for fo in sorted(preferred.keys())
            }
        },
        "anchor_test": {
            "P2": p2
        },
        "primary_tests": {
            "NP1": np1,
            "NP2": np2,
            "NP3": np3,
            "NP4": np4,
            "NP5": np5,
            "NP6": np6,
            "NP7": np7,
        },
        "comparative_diagnostics": {
            "CD1": cd1,
            "CD2": cd2,
            "CD3": cd3,
            "CD4": cd4,
            "CD5": cd5,
            "CD6": cd6,
            "CD7": cd7,
            "CD8": cd8,
        },
        "summary": {
            "anchor_pass": anchor_pass,
            "np_pass_count": np_pass_count,
            "np_total": len(all_np),
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_not_evaluable": tests_ne,
        }
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=1, cls=NumpyEncoder)
    print(f"\nResults written to {OUT_PATH}")


if __name__ == "__main__":
    main()
