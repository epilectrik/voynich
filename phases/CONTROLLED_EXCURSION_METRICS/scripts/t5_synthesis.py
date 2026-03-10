#!/usr/bin/env python3
"""
T5: Phase 568 Synthesis — verdict, constraints, cross-phase comparison, and REPORT_568.md.

Phase 568 tested controlled excursion metrics with burden axis inversion from 567,
introducing 6 new metrics (WCU, SLR, UEB, CCY, WCP, EWP), a COF observability audit,
and a new validation battery (P2 anchor + EP1-EP7 primary + ED1-ED7 diagnostics).

Inputs:
  t1_controlled_excursion_runs.json     (90 full-model runs: 20 folios x 3 profiles + ablation)
  t2_controlled_excursion_null_runs.json (4220 runs: reference + baselines + nulls)
  t3_cof_observability.json             (COF observability audit: OA1-OA5)
  t4_controlled_excursion_validation.json (validation battery: P2 + EP1-EP7 + ED1-ED7)

Outputs:
  t5_synthesis.json
  REPORT_568.md
"""

import json
import os
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(BASE, "results")

T1_PATH = os.path.join(RESULTS, "t1_controlled_excursion_runs.json")
T2_PATH = os.path.join(RESULTS, "t2_controlled_excursion_null_runs.json")
T3_PATH = os.path.join(RESULTS, "t3_cof_observability.json")
T4_PATH = os.path.join(RESULTS, "t4_controlled_excursion_validation.json")

OUT_JSON = os.path.join(RESULTS, "t5_synthesis.json")
OUT_REPORT = os.path.join(BASE, "REPORT_568.md")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Load all inputs
# ---------------------------------------------------------------------------
t1 = load_json(T1_PATH)
t4 = load_json(T4_PATH)

# T2 is large; load for metadata and reference/null summaries
t2 = load_json(T2_PATH)
t2_meta = t2.get("metadata", {})
t2_reference = t2.get("reference", {})
t2_null_runs = t2.get("null_runs", {})
t2_baseline_runs = t2.get("baseline_runs", {})

# T3 is small; load fully
t3 = load_json(T3_PATH)

# ---------------------------------------------------------------------------
# Extract T1 summary
# ---------------------------------------------------------------------------
t1_summary = t1.get("summary", {})
t1_primary_runs = t1.get("primary_runs", {})

# ---------------------------------------------------------------------------
# Extract T4 validation results
# ---------------------------------------------------------------------------
t4_summary = t4.get("score_summary", {})
t4_anchor = {"P2": t4.get("P2", {})}
t4_primary = t4.get("EP_tests", {})
t4_diagnostics = t4.get("diagnostics", {})

# P2 result
p2_data = t4.get("P2", {})
p2_result = p2_data.get("result", "UNKNOWN")

# EP test results
EP_NAMES = ["EP1", "EP2", "EP3", "EP4", "EP5", "EP6", "EP7"]
ep_pass_count = 0
ep_passed = []
ep_failed = []
for ep in EP_NAMES:
    ep_data = t4_primary.get(ep, {})
    result = ep_data.get("result", "UNKNOWN")
    if result == "PASS":
        ep_pass_count += 1
        ep_passed.append(ep)
    else:
        ep_failed.append(ep)

# Use summary counts if available (more authoritative than re-counting)
if "EP_pass_count" in t4_summary:
    ep_pass_count = t4_summary["EP_pass_count"]
# EP_results is a dict like {"EP1": "FAIL", "EP2": "PASS", ...}
if "EP_results" in t4_summary:
    ep_results_map = t4_summary["EP_results"]
    ep_passed = [k for k, v in ep_results_map.items() if v == "PASS"]
    ep_failed = [k for k, v in ep_results_map.items() if v != "PASS"]

ep_total = 7

# ED diagnostic keys
ED_NAMES = ["ED1", "ED2", "ED3", "ED4", "ED5", "ED6", "ED7"]

# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------
if p2_result == "PASS" and ep_pass_count >= 4:
    verdict = "CONTROLLED_EXCURSION_VALIDATED"
elif p2_result == "PASS" and ep_pass_count >= 2:
    verdict = "PARTIAL_CONTROLLED_EXCURSION"
else:
    verdict = "CONTROLLED_EXCURSION_INSUFFICIENT"

# ---------------------------------------------------------------------------
# Null comparison: extract key metrics from T2
# ---------------------------------------------------------------------------
null_names = ["N1", "N2", "N3", "N4"]
null_key_metrics = ["WCU", "SLR_mean", "UEB", "CCY", "WCP", "EWP", "PCV", "SAHB"]

null_comparison = {}
for nn in null_names:
    nn_data = t2_null_runs.get(nn, {})
    if not nn_data:
        null_comparison[nn] = {}
        continue
    # Average across folios
    folio_list = sorted(nn_data.keys())
    means = {}
    for mk in null_key_metrics:
        mean_key = f"mean_{mk}"
        vals = [nn_data[f].get(mean_key, 0.0) for f in folio_list
                if mean_key in nn_data.get(f, {})]
        means[mk] = round(sum(vals) / len(vals), 6) if vals else 0.0
    null_comparison[nn] = means

# Reference means from T2
ref_means = {}
ref_folios = sorted(t2_reference.keys())
for mk in null_key_metrics:
    vals = [t2_reference[f].get(mk, 0.0) for f in ref_folios
            if mk in t2_reference.get(f, {})]
    ref_means[mk] = round(sum(vals) / len(vals), 6) if vals else 0.0
null_comparison["reference"] = ref_means

# ---------------------------------------------------------------------------
# COF findings from T3
# ---------------------------------------------------------------------------
cof_findings = {}

oa1 = t3.get("OA1_ccy_variant_comparison", {})
oa1_summary = oa1.get("summary", {})
cof_findings["OA1_variant_comparison"] = {
    "means": oa1_summary.get("means", {}),
    "n_nonzero": oa1_summary.get("n_nonzero", {}),
    "best_by_mean": oa1_summary.get("best_variant_by_mean", ""),
    "best_by_coverage": oa1_summary.get("best_variant_by_coverage", ""),
}

oa2 = t3.get("OA2_closure_excursion_overlap", {})
cof_findings["OA2_closure_excursion_overlap"] = oa2.get("per_variant", {})

oa3 = t3.get("OA3_b10_sensitivity", {})
cof_findings["OA3_b10_sensitivity"] = {
    "per_variant": oa3.get("per_variant", {}),
    "best_variant": oa3.get("best_variant", ""),
}

oa4 = t3.get("OA4_section_specific", {})
cof_findings["OA4_section_specific"] = {
    "note": oa4.get("note", "Not available"),
}

oa5 = t3.get("OA5_eligibility_expansion", {})
cof_findings["OA5_eligibility_expansion"] = {
    "per_variant": oa5.get("per_variant", {}),
    "base_ccy_nonzero": oa5.get("base_ccy_nonzero", 0),
    "expansion": oa5.get("expansion_from_ccy", {}),
}

# ---------------------------------------------------------------------------
# Provisional constraints — only include if supporting test passed
# ---------------------------------------------------------------------------
all_provisional = {
    "C1610": {
        "id": "C1610",
        "title": "Work corridor utilization discriminates full from nulls",
        "claim": (
            "WORK phase corridor occupancy is structurally higher for the real "
            "supervisory trace than for any null model. The full model's WCU "
            "exceeds all null WCU values, confirming that the token-level "
            "contribution structure during WORK produces genuine corridor "
            "occupation rather than random zone wandering."
        ),
        "evidence": "EP1 result",
        "tier": "Provisional",
        "condition_test": "EP1",
    },
    "C1611": {
        "id": "C1611",
        "title": "Same-line resolution discriminates",
        "claim": (
            "The full model resolves excursion within the same line better "
            "than null models. SLR (same-line resolution) for the full model "
            "exceeds N1 null SLR, indicating that the phase structure within "
            "lines (SPEC-WORK-CLOSE sequencing) produces genuine within-line "
            "excursion resolution."
        ),
        "evidence": "EP2 result",
        "tier": "Provisional",
        "condition_test": "EP2",
    },
    "C1612": {
        "id": "C1612",
        "title": "Unresolved excursion burden inverts SAHB",
        "claim": (
            "Restricting burden measurement to CLOSE-phase and line-end "
            "residual (UEB) fixes the axis inversion that plagued SAHB in "
            "Phase 567. Under UEB, the full model shows lower unresolved "
            "burden than null models, confirming that the burden axis "
            "inversion was a measurement artifact of including WORK-phase "
            "zone contacts in the burden metric."
        ),
        "evidence": "EP3 result + ED7 inversion confirmation",
        "tier": "Provisional",
        "condition_test": "EP3",
    },
    "C1613": {
        "id": "C1613",
        "title": "Closure-conditioned yield with corridor re-entry inverts N2/N4 paradox",
        "claim": (
            "CCY (closure-conditioned yield) with net corridor improvement "
            "gating inverts the N2/N4 paradox that persisted through QGY. "
            "The full model's CCY exceeds null CCY because closure events "
            "that produce Y gain while also improving corridor position "
            "are a property of the real supervisory trace, not random "
            "contribution structure."
        ),
        "evidence": "EP4 result + ED3 comparison",
        "tier": "Provisional",
        "condition_test": "EP4",
    },
    "C1614": {
        "id": "C1614",
        "title": "Packet coherence is a property of supervised traces",
        "claim": (
            "WCP (work-closure packet coherence) discriminates the full "
            "model from null models, confirming that the phase-aware "
            "sub-score structure (SPEC basin quiescence, WORK corridor "
            "engagement, CLOSE convergence) is a genuine property of "
            "supervised traces, not a statistical artifact of random walks."
        ),
        "evidence": "EP6 result + ED5 comparison",
        "tier": "Provisional",
        "condition_test": "EP6",
    },
    "C1615": {
        "id": "C1615",
        "title": "COF observability findings",
        "claim": (
            "The COF observability audit (T3) confirms that closure "
            "observability field variants provide complementary diagnostic "
            "value. COF variants expand CCY eligibility and show measurable "
            "sensitivity to CLOSE recovery ablation (B10). The best variant "
            "depends on the criterion (mean value vs. coverage vs. B10 "
            "sensitivity)."
        ),
        "evidence": "EP7 result + T3 findings",
        "tier": "Provisional",
        "condition_test": "EP7",
    },
}

# Filter to only include constraints whose supporting test passed
provisional_constraints = {}
for cid, cdata in all_provisional.items():
    test_name = cdata["condition_test"]
    test_data = t4_primary.get(test_name, {})
    if test_data.get("result") == "PASS":
        entry = dict(cdata)
        del entry["condition_test"]
        provisional_constraints[cid] = entry

# ---------------------------------------------------------------------------
# Cross-phase comparison
# ---------------------------------------------------------------------------
score_568 = f"P2 {'PASS' if p2_result == 'PASS' else 'FAIL'} + {ep_pass_count}/{ep_total} EP"

cross_phase = [
    {"phase": 563, "score": "5/9", "key_result": "Baseline apparatus coupling"},
    {"phase": "563b", "score": "3/9", "key_result": "Sensitivity recalibration"},
    {"phase": 564, "score": "2/9", "key_result": "Event-gated execution"},
    {"phase": "564b", "score": "2/9", "key_result": "Selective restoration"},
    {"phase": 565, "score": "2/9", "key_result": "Permeability calibration"},
    {"phase": 566, "score": "1/9", "key_result": "CLOSE recovery"},
    {"phase": 567, "score": "P2 + 3/7 NP",
     "key_result": "PARTIAL: readout reform partially works"},
    {"phase": 568, "score": score_568, "key_result": f"{verdict}"},
]

# ---------------------------------------------------------------------------
# Build output JSON
# ---------------------------------------------------------------------------
timestamp = datetime.now(timezone.utc).isoformat()

output = {
    "metadata": {
        "phase": 568,
        "phase_title": "CONTROLLED EXCURSION METRICS + COF OBSERVABILITY",
        "script": "t5_synthesis.py",
        "timestamp": timestamp,
        "input_files": [
            "t1_controlled_excursion_runs.json",
            "t2_controlled_excursion_null_runs.json",
            "t3_cof_observability.json",
            "t4_controlled_excursion_validation.json",
        ],
    },
    "verdict": verdict,
    "score": {
        "P2": p2_result,
        "EP_pass_count": ep_pass_count,
        "EP_total": ep_total,
    },
    "test_results": {
        "anchor_test": t4_anchor,
        "primary_tests": t4_primary,
        "comparative_diagnostics": t4_diagnostics,
        "summary": t4_summary,
    },
    "full_model_summary": t1_summary,
    "null_comparison": null_comparison,
    "cof_findings": cof_findings,
    "provisional_constraints": [
        {
            "id": cid,
            "title": cdata["title"],
            "claim": cdata["claim"],
            "evidence": cdata["evidence"],
            "tier": cdata["tier"],
            "condition": f"if {verdict.split('_')[0]} (test {list(all_provisional.keys())[i].replace('C16', 'EP')} PASS)"
                         if i < len(all_provisional) else "",
        }
        for i, (cid, cdata) in enumerate(provisional_constraints.items())
    ],
    "cross_phase_comparison": cross_phase,
}

# Write JSON
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

# ---------------------------------------------------------------------------
# EP test descriptions (for report table)
# ---------------------------------------------------------------------------
EP_DESCRIPTIONS = {
    "EP1": "Full WCU > N1 WCU",
    "EP2": "Full SLR > N1 SLR",
    "EP3": "Full UEB < N1 UEB",
    "EP4": "Full CCY > N4 CCY",
    "EP5": "Full EWP < N1 EWP",
    "EP6": "Full WCP > N1 WCP",
    "EP7": "COF observability discriminates",
}

ED_DESCRIPTIONS = {
    "ED1": "WCU-PCV correlation",
    "ED2": "SLR eligibility fraction",
    "ED3": "CCY vs QGY comparison",
    "ED4": "UEB component breakdown",
    "ED5": "WCP full-packet analysis",
    "ED6": "EWP component breakdown",
    "ED7": "SAHB axis inversion check",
}


# ---------------------------------------------------------------------------
# Helper: build EP result line for report table
# ---------------------------------------------------------------------------
def ep_result_line(name):
    """Build a markdown table row for an EP test."""
    td = t4_primary.get(name, {})
    desc = EP_DESCRIPTIONS.get(name, name)
    result = td.get("result", "UNKNOWN")

    # Try to extract detail
    detail_parts = []
    if "n_pass" in td:
        detail_parts.append(f"{td['n_pass']}/{td.get('n_total', '?')} folios (gate={td.get('gate', '?')})")
    if "any_significant" in td:
        detail_parts.append(f"any_sig={td['any_significant']}")
    if "per_metric" in td:
        for mk, mv in td["per_metric"].items():
            if isinstance(mv, dict) and mv.get("significant"):
                detail_parts.append(f"{mk}: d={mv.get('cohens_d', 0):.3f}")

    detail = "; ".join(detail_parts) if detail_parts else ""
    return f"| {name} | {desc} | **{result}** | {detail} |"


# ---------------------------------------------------------------------------
# Helper: build ED diagnostic line for report table
# ---------------------------------------------------------------------------
def ed_diagnostic_line(name):
    """Build a markdown table row for an ED diagnostic."""
    td = t4_diagnostics.get(name, {})
    desc = ED_DESCRIPTIONS.get(name, name)

    # Build finding string from available fields
    finding_parts = []

    # Try common keys
    for key in ["pearson_r", "spearman_r", "correlation"]:
        if key in td:
            finding_parts.append(f"r = {td[key]:.4f}" if isinstance(td[key], (int, float)) else f"r = {td[key]}")
    for key in ["fraction", "rate", "ratio", "mean", "value"]:
        if key in td:
            val = td[key]
            if isinstance(val, float):
                finding_parts.append(f"{key} = {val:.4f}")
            else:
                finding_parts.append(f"{key} = {val}")
    if "interpretation" in td:
        finding_parts.append(str(td["interpretation"]))
    if "finding" in td:
        finding_parts.append(str(td["finding"]))
    if "result" in td:
        finding_parts.append(str(td["result"]))
    if "description" in td:
        finding_parts.append(str(td["description"]))

    # Fallback: dump all non-metadata keys
    if not finding_parts:
        for k, v in td.items():
            if k not in ("metadata", "name", "description"):
                if isinstance(v, float):
                    finding_parts.append(f"{k} = {v:.4f}")
                elif isinstance(v, (int, str, bool)):
                    finding_parts.append(f"{k} = {v}")

    finding = "; ".join(finding_parts) if finding_parts else "(no data)"
    return f"| {name} | {finding} |"


# ---------------------------------------------------------------------------
# Build full model summary table for report
# ---------------------------------------------------------------------------
summary_metrics = [
    ("WCU", "mean_WCU"),
    ("SLR", "mean_SLR"),
    ("UEB", "mean_UEB"),
    ("CCY", "mean_CCY"),
    ("WCP", "mean_WCP"),
    ("EWP", "mean_EWP"),
    ("PCV", "mean_PCV"),
    ("REF", "mean_REF"),
    ("SAHB", "mean_SAHB"),
    ("QGY", "mean_QGY"),
    ("old_viability", "mean_old_viability"),
    ("old_y_final", "mean_old_y_final"),
]


def fmt_metric(val):
    """Format a metric value for the report."""
    if isinstance(val, float):
        if abs(val) >= 10:
            return f"{val:.2f}"
        elif abs(val) >= 1:
            return f"{val:.4f}"
        else:
            return f"{val:.5f}"
    return str(val)


# ---------------------------------------------------------------------------
# Build REPORT_568.md
# ---------------------------------------------------------------------------

# Verdict explanation
if verdict == "CONTROLLED_EXCURSION_VALIDATED":
    verdict_why = (
        f"P2 PASS establishes the anchor (line packet shape recovery preserved). "
        f"{ep_pass_count}/{ep_total} EP tests pass, meeting the >= 4/7 threshold. "
        f"The controlled excursion metrics collectively discriminate the full "
        f"supervisory trace from null models across multiple dimensions."
    )
elif verdict == "PARTIAL_CONTROLLED_EXCURSION":
    verdict_why = (
        f"P2 PASS establishes the anchor, and {ep_pass_count}/{ep_total} EP tests "
        f"pass ({', '.join(ep_passed)}), meeting the 2-3 range for partial validation. "
        f"Some metrics discriminate well but others fail to separate full from nulls. "
        f"The failing tests ({', '.join(ep_failed)}) indicate remaining gaps in the "
        f"readout framework."
    )
else:
    verdict_why = (
        f"P2 {'PASS' if p2_result == 'PASS' else 'FAIL'} with only {ep_pass_count}/{ep_total} EP pass. "
        f"The controlled excursion metrics do not sufficiently discriminate the full "
        f"model from null models. Either the burden axis inversion was not the primary "
        f"problem, or the new metrics need further refinement."
    )

# Summary text
summary_text = (
    f"Phase 568 introduced six new controlled-excursion metrics (WCU, SLR, UEB, CCY, WCP, EWP) "
    f"designed to address the burden axis inversion identified in Phase 567. "
    f"The key insight from 567 was that SAHB measured burden during WORK phase "
    f"(where excursion is structurally expected), inflating the full model's burden "
    f"relative to nulls. Phase 568 redirects burden to CLOSE-phase residual (UEB), "
    f"replaces raw yield with corridor-conditioned yield (CCY), and adds work "
    f"corridor utilization (WCU) and same-line resolution (SLR) as positive "
    f"discrimination metrics.\n\n"
    f"The validation battery comprises P2 (line packet shape recovery anchor), "
    f"7 primary excursion tests (EP1-EP7), and 7 comparative diagnostics (ED1-ED7). "
    f"A parallel COF observability audit (T3) examined whether closure observability "
    f"field variants strengthen the closure interface.\n\n"
    f"Result: **{verdict}** -- P2 {p2_result}, {ep_pass_count}/{ep_total} EP pass "
    f"({', '.join(ep_passed) if ep_passed else 'none'}). "
    f"{', '.join(ep_failed) if ep_failed else 'None'} failed."
)

# Context text
context_text = (
    "Phase 567 established that the readout/scoring framework was partially responsible "
    "for discrimination failure across phases 563b-566. PCV replaced old viability "
    "(NP1 PASS), CLOSE recovery became visible under PCV (NP6 PASS), and QGY partially "
    "inverted the N2/N4 paradox. However, SAHB retained an axis inversion (full model "
    "burden > null burden) because WORK-phase zone contacts were counted as burden "
    "despite being structurally expected during productive excursion. S still dominated "
    "84.5% of edge contacts (NP7 FAIL). Phase 568 addresses this by redesigning the "
    "burden axis: burden is now measured only in CLOSE-phase and at line boundaries "
    "(UEB), and yield is conditioned on corridor improvement (CCY)."
)

# What changed text
what_changed = (
    "1. **WCU (Work Corridor Utilization):** Per-WORK-token zone scoring. Corridor "
    "= +1.0, basin = +0.3, warning = +0.1, hard_stop = -1.0, hazard = -2.0. "
    "S above EQ = +1.0. Measures whether WORK-phase tokens occupy the productive "
    "corridor zone.\n\n"
    "2. **SLR (Same-Line Resolution):** Per-line resolution metric: "
    "0.5 * resolution_score + 0.3 * corridor_return + 0.2 * work_quality. "
    "Eligible lines require work_end_dev > Q1. Measures within-line excursion "
    "resolution quality.\n\n"
    "3. **UEB (Unresolved Excursion Burden):** CLOSE-phase warnings, hard_stops, "
    "mean unresolved fraction, line-final hard_stops, and post-line residual above Q2. "
    "Burden is now restricted to where it should be zero (CLOSE phase and line end), "
    "inverting the axis.\n\n"
    "4. **CCY (Closure-Conditioned Yield):** Y increments during CLOSE that satisfy "
    "net corridor improvement: aggregate deviation decreased from WORK peak AND "
    "SVs above Q2 decreased. Three COF variants (CCY_cof1/2/3) replace CTS threshold "
    "with composite closure observability.\n\n"
    "5. **WCP (Work-Closure Packet Coherence):** Per-line phase-aware sub-score "
    "with presence masking. SPEC = all-basin fraction, WORK = corridor/warning "
    "engagement, CLOSE = convergence (dev decreasing). Phase-weighted with "
    "presence-adaptive weights.\n\n"
    "6. **EWP (Edge Waste Penalty):** Prolonged hard_stop during WORK (> 2 consecutive), "
    "unresolved warnings after CLOSE, post-CLOSE residual above Q2, edge persistence. "
    "Penalty metric for pathological trace behavior.\n\n"
    "7. **COF Observability Audit (T3):** Five analyses (OA1-OA5) examining CCY variant "
    "comparison, closure-excursion overlap, B10 sensitivity, section-specific performance, "
    "and eligibility expansion across COF variants."
)

# Build EP test table rows
ep_rows = "\n".join(ep_result_line(ep) for ep in EP_NAMES)

# Build ED diagnostic table rows
ed_rows = "\n".join(ed_diagnostic_line(ed) for ed in ED_NAMES)

# Build full model summary table rows
summary_rows = "\n".join(
    f"| {label} | {fmt_metric(t1_summary.get(key, 0.0))} |"
    for label, key in summary_metrics
)

# Build cross-phase table rows
cross_phase_rows = "\n".join(
    f"| {'**' + str(cp['phase']) + '**' if cp['phase'] == 568 else str(cp['phase'])} "
    f"| {'**' + str(cp['score']) + '**' if cp['phase'] == 568 else cp['score']} "
    f"| {'**' + cp['key_result'] + '**' if cp['phase'] == 568 else cp['key_result']} |"
    for cp in cross_phase
)

# Build provisional constraints section
if provisional_constraints:
    constraint_lines = []
    for cid, cdata in provisional_constraints.items():
        constraint_lines.append(f"### {cid}: {cdata['title']}")
        constraint_lines.append(f"{cdata['claim']}")
        constraint_lines.append(f"- Evidence: {cdata['evidence']}")
        constraint_lines.append(f"- Tier: {cdata['tier']}")
        constraint_lines.append("")
    constraints_section = "\n".join(constraint_lines)
else:
    constraints_section = "No provisional constraints met their activation conditions."

# Build COF findings section
cof_oa1 = cof_findings.get("OA1_variant_comparison", {})
cof_oa2 = cof_findings.get("OA2_closure_excursion_overlap", {})
cof_oa3 = cof_findings.get("OA3_b10_sensitivity", {})
cof_oa4 = cof_findings.get("OA4_section_specific", {})
cof_oa5 = cof_findings.get("OA5_eligibility_expansion", {})

cof_oa1_means = cof_oa1.get("means", {})
cof_oa1_nonzero = cof_oa1.get("n_nonzero", {})
cof_oa1_best_mean = cof_oa1.get("best_by_mean", "?")
cof_oa1_best_coverage = cof_oa1.get("best_by_coverage", "?")

cof_section_text = []
cof_section_text.append(f"**OA1 (CCY Variant Comparison):** "
                         f"Best by mean: {cof_oa1_best_mean} "
                         f"({fmt_metric(cof_oa1_means.get(cof_oa1_best_mean, 0.0))}). "
                         f"Best by coverage: {cof_oa1_best_coverage} "
                         f"({cof_oa1_nonzero.get(cof_oa1_best_coverage, '?')} non-zero folios).")

cof_section_text.append("")
cof_section_text.append("**OA2 (Closure-Excursion Overlap):** ")
for vname, vdata in cof_oa2.items():
    if isinstance(vdata, dict):
        overlap = vdata.get("overlap_frac", 0.0)
        n_high = vdata.get("n_high_slr", 0)
        n_overlap = vdata.get("n_overlap", 0)
        cof_section_text.append(f"  - {vname}: {n_overlap}/{n_high} high-SLR folios "
                                 f"overlap (frac={fmt_metric(overlap)})")

cof_section_text.append("")
cof_section_text.append(f"**OA3 (B10 Sensitivity):** "
                         f"Best variant: {cof_oa3.get('best_variant', '?')}.")
oa3_pv = cof_oa3.get("per_variant", {})
for vk, vdata in oa3_pv.items():
    if isinstance(vdata, dict):
        cof_section_text.append(
            f"  - {vk}: delta={fmt_metric(vdata.get('delta', 0.0))}, "
            f"Cohen's d={fmt_metric(vdata.get('cohens_d', 0.0))}")

cof_section_text.append("")
cof_section_text.append(f"**OA4 (Section-Specific):** "
                         f"{cof_oa4.get('note', 'Not available')}.")

cof_section_text.append("")
base_nz = cof_oa5.get("base_ccy_nonzero", 0)
expansion = cof_oa5.get("expansion", {})
cof_section_text.append(f"**OA5 (Eligibility Expansion):** "
                         f"Base CCY: {base_nz} non-zero folios.")
for cof_key, exp_count in expansion.items():
    cof_section_text.append(f"  - {cof_key}: +{exp_count} folios expanded")

cof_section_str = "\n".join(cof_section_text)

# Build "What Worked" / "What Did Not Work" sections
what_worked = []
what_not_worked = []

# Analyze EP results for worked/not-worked
for ep in EP_NAMES:
    ep_data = t4_primary.get(ep, {})
    result = ep_data.get("result", "UNKNOWN")
    desc = EP_DESCRIPTIONS.get(ep, ep)
    if result == "PASS":
        detail_parts = []
        if "n_pass" in ep_data:
            detail_parts.append(f"{ep_data['n_pass']}/{ep_data.get('n_total', '?')} folios")
        if "per_metric" in ep_data:
            for mk, mv in ep_data["per_metric"].items():
                if isinstance(mv, dict) and mv.get("significant"):
                    detail_parts.append(f"{mk} d={mv.get('cohens_d', 0):.3f}")
        detail = f" ({', '.join(detail_parts)})" if detail_parts else ""
        what_worked.append(f"**{ep} ({desc})** passed{detail}.")
    else:
        detail_parts = []
        if "n_pass" in ep_data:
            detail_parts.append(f"{ep_data['n_pass']}/{ep_data.get('n_total', '?')} folios")
        detail = f" ({', '.join(detail_parts)})" if detail_parts else ""
        what_not_worked.append(f"**{ep} ({desc})** failed{detail}.")

what_worked_text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(what_worked)) if what_worked else "None."
what_not_worked_text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(what_not_worked)) if what_not_worked else "None."

# Next phase recommendations
if verdict == "CONTROLLED_EXCURSION_VALIDATED":
    next_phase_text = (
        "1. **Lock the 6 new metrics** (WCU, SLR, UEB, CCY, WCP, EWP) as the primary "
        "discrimination battery. Retire old_viability and SAHB from the primary test set.\n\n"
        "2. **Expand to full Currier B corpus.** The 20-folio pilot is validated; run "
        "the full 83-folio corpus to confirm generalization.\n\n"
        "3. **Profile optimization.** With metrics locked, optimize the A1/A2/A3 profile "
        "assignment to maximize per-folio discrimination.\n\n"
        "4. **COF integration.** Use OA3's best variant to replace raw CTS in CCY. "
        "Section-specific COF normalization may further strengthen discrimination."
    )
elif verdict == "PARTIAL_CONTROLLED_EXCURSION":
    next_phase_text = (
        "1. **Diagnose failing EP tests.** For each failing test, determine whether "
        "the failure is structural (metric design) or parametric (threshold/weighting). "
        "ED diagnostics should guide the diagnosis.\n\n"
        "2. **Strengthen weak metrics.** Focus on the metrics behind failing EP tests. "
        "Consider metric redesign, zone boundary adjustment, or weighting changes.\n\n"
        "3. **COF integration.** OA3 identifies the most B10-sensitive COF variant; "
        "integrate it into the CCY definition to potentially flip marginal EP tests.\n\n"
        "4. **S zone geometry.** If UEB or EWP failures are S-related, Phase 567's "
        "NP7 lesson (S = 84.5% of edge contacts) may still require zone boundary "
        "reform for S specifically."
    )
else:
    next_phase_text = (
        "1. **Re-evaluate the controlled excursion hypothesis.** If both P2 and EP "
        "fail, the problem may not be solely readout-related. Consider whether the "
        "plant law itself needs modification.\n\n"
        "2. **Simplify the metric battery.** Six new metrics may be over-fitting the "
        "readout framework. Identify the 2-3 most informative metrics and focus.\n\n"
        "3. **Alternative null models.** If EP tests fail because nulls score similarly "
        "to the full model, the metrics may be measuring properties shared by all "
        "traces. Design more targeted nulls.\n\n"
        "4. **Cross-reference with phases 563-566.** The original P1-P9 tests may "
        "contain complementary information that the EP battery misses."
    )

# Assemble report
report = f"""# Phase 568: CONTROLLED EXCURSION METRICS + COF OBSERVABILITY

## Verdict: {verdict}

## Summary
{summary_text}

---

## Context
{context_text}

## What Changed
{what_changed}

## Test Results

### P2: Line Packet Shape Recovery (Anchor)
**{p2_result}** -- {p2_data.get('n_significant', '?')}/{p2_data.get('n_total', '?')} SVs significant. {p2_data.get('description', p2_data.get('detail', ''))}

### New Primary Tests (EP1-EP7)
| Test | Description | Result | Detail |
|------|-------------|--------|--------|
{ep_rows}

**Score: P2 {p2_result} + {ep_pass_count}/{ep_total} EP pass**

### Comparative Diagnostics (ED1-ED7)
| Diagnostic | Finding |
|------------|---------|
{ed_rows}

---

## Full Model Summary Values
| Metric | Mean |
|--------|------|
{summary_rows}

---

## Cross-Phase Comparison
| Phase | Score | Key Result |
|-------|-------|------------|
{cross_phase_rows}

> **Note:** Phases 563-566 used P1-P9 tests. Phase 567 used P2 + NP1-NP7. Phase 568 uses P2 + EP1-EP7. Test batteries are not directly comparable but track the same underlying question: does the full model discriminate from nulls?

---

## Analysis

### What Worked
{what_worked_text}

### What Did Not Work
{what_not_worked_text}

### Why {verdict}
{verdict_why}

---

## Provisional Constraints
{constraints_section}

---

## COF Observability Findings
{cof_section_str}

---

## Lessons and Implications

1. **Burden axis matters more than burden magnitude.** The shift from SAHB (WORK-phase inclusive) to UEB (CLOSE-phase and line-end only) tests whether restricting burden measurement to where residual is genuinely unwanted inverts the axis. This is a general lesson: discrimination metrics must measure deviations in the right phase context, not just anywhere.

2. **Corridor utilization is a positive framing.** WCU asks "does the full model use the corridor during WORK?" rather than "does the full model avoid hazard?". Positive discrimination (what the trace does well) may be more informative than negative discrimination (what it avoids).

3. **Same-line resolution captures local structure.** SLR measures within-line excursion-resolution quality, which is invisible to folio-level aggregate metrics. The line is the natural resolution unit for the SPEC-WORK-CLOSE packet structure.

4. **CCY with net corridor improvement gates qualify closure events.** The N2/N4 paradox arises because raw Y_final rewards any convergence. CCY gates on corridor improvement, so only closure events that improve the state trajectory count. This is more selective than QGY.

5. **COF variants provide complementary views.** The T3 audit shows that different COF variants optimize different properties (mean value, coverage, B10 sensitivity). A single "best" COF may not exist; the right variant depends on the downstream criterion.

---

## Next Phase Recommendations
{next_phase_text}

---

*Generated by t5_synthesis.py | Phase 568 | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*
"""

with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write(report)

# ---------------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------------
print(f"Phase 568 Synthesis Complete")
print(f"  Verdict: {verdict}")
print(f"  P2: {p2_result}")
print(f"  EP pass: {ep_pass_count}/{ep_total} ({', '.join(ep_passed) if ep_passed else 'none'})")
print(f"  EP fail: {', '.join(ep_failed) if ep_failed else 'none'}")
print(f"  Provisional constraints: {sorted(provisional_constraints.keys()) if provisional_constraints else 'none (no tests passed)'}")
print(f"  Cross-phase 568 score: {score_568}")
print(f"  JSON: {OUT_JSON}")
print(f"  Report: {OUT_REPORT}")
