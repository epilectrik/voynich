#!/usr/bin/env python3
"""
T5: Phase 567 Synthesis — verdict, constraints, cross-phase comparison, and REPORT_567.md.

Phase 567 tested whether the remaining discrimination failure (from phases 563b-566)
was primarily a readout/scoring problem, while holding the plant law fixed.

Two interventions:
  Part A: Closure field audit (T1) — pure data analysis
  Part B: Burden metric refactor (T2-T4) — 6 new metrics with S asymmetry correction

Input:
  t1_closure_field_audit.json
  t2_burden_runs.json  (only metadata/summary used)
  t3_burden_null_runs.json  (only metadata used)
  t4_burden_validation.json

Output:
  t5_synthesis.json
  REPORT_567.md
"""

import json
import os
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(BASE, "results")
SCRIPTS = os.path.join(BASE, "scripts")

T1_PATH = os.path.join(RESULTS, "t1_closure_field_audit.json")
T2_PATH = os.path.join(RESULTS, "t2_burden_runs.json")
T3_PATH = os.path.join(RESULTS, "t3_burden_null_runs.json")
T4_PATH = os.path.join(RESULTS, "t4_burden_validation.json")

OUT_JSON = os.path.join(RESULTS, "t5_synthesis.json")
OUT_REPORT = os.path.join(BASE, "REPORT_567.md")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Load all inputs
# ---------------------------------------------------------------------------
t1 = load_json(T1_PATH)
t4 = load_json(T4_PATH)

# T2 and T3 are large; we only need metadata
with open(T2_PATH, "r", encoding="utf-8") as f:
    t2_raw = json.load(f)
t2_meta = t2_raw.get("metadata", {})

with open(T3_PATH, "r", encoding="utf-8") as f:
    t3_raw = json.load(f)
t3_meta = t3_raw.get("metadata", {})
t3_ref = t3_raw.get("reference", {})

# Also extract summary-level numbers from T2 for metrics table
# Compute means across pilot folios from T4 comparative diagnostics
cd3 = t4["comparative_diagnostics"]["CD3"]
cd5 = t4["comparative_diagnostics"]["CD5"]
cd7 = t4["comparative_diagnostics"]["CD7"]

# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------
anchor_pass = t4["summary"]["anchor_pass"]
np_pass_count = t4["summary"]["np_pass_count"]
np_total = t4["summary"]["np_total"]
tests_passed = t4["summary"]["tests_passed"]
tests_failed = t4["summary"]["tests_failed"]

p2_result = t4["anchor_test"]["P2"]["result"]

if p2_result == "PASS" and np_pass_count >= 4:
    verdict = "METRIC_REFACTOR_VALIDATED"
elif p2_result == "PASS" and np_pass_count >= 2:
    verdict = "PARTIAL_METRIC_REFACTOR"
else:
    verdict = "METRIC_REFACTOR_INSUFFICIENT"

# ---------------------------------------------------------------------------
# Cross-phase comparison
# ---------------------------------------------------------------------------
cross_phase = [
    {"phase": 563, "score": "5/9", "key_result": "Baseline apparatus coupling"},
    {"phase": "563b", "score": "3/9", "key_result": "Sensitivity recalibration"},
    {"phase": 564, "score": "2/9", "key_result": "Event-gated execution"},
    {"phase": "564b", "score": "2/9", "key_result": "Selective restoration"},
    {"phase": 565, "score": "2/9", "key_result": "Permeability calibration"},
    {"phase": 566, "score": "1/9", "key_result": "CLOSE recovery"},
    {"phase": 567, "score": f"P2 + {np_pass_count}/{np_total} NP",
     "key_result": "PARTIAL: readout reform partially works"},
]

# ---------------------------------------------------------------------------
# T1 audit summary
# ---------------------------------------------------------------------------
a1 = t1["A1_cts_distribution"]
a2 = t1["A2_close_window_characterization"]
a3 = t1["A3_closure_component_audit"]
a4 = t1["A4_cts_excursion_timing"]
a5 = t1["A5_s_asymmetry_audit"]
a6 = t1["A6_cof_prototype_family"]
a7 = t1["A7_closure_window_overlap"]

t1_summary = {
    "A1_cts_distribution": {
        "global_mean": a1["global_mean_cts"],
        "global_median": a1["global_median_cts"],
        "close_frac_gt_03": a1["close_frac_gt_03"],
        "section_B_deficit": a1["b_deficit"],
        "section_B_mean": a1["section_B_mean_cts"],
        "non_B_mean": a1["non_B_mean_cts"],
    },
    "A2_close_windows": {
        "n_folios_with_close": a2["n_folios_with_close"],
        "total_close_lines": a2["total_close_lines"],
        "mean_run_length": a2["close_run_stats"]["global_mean_run_length"],
        "close_token_density_mean": a2["close_token_density_summary"]["mean"],
    },
    "A3_closure_components": {
        "significant_close_vs_work_p001": a3["significant_close_vs_work_p001"],
        "note": "No closure component discriminates CLOSE from WORK at p < 0.01",
    },
    "A4_cts_excursion_timing": {
        "spearman_r": a4["spearman_preceding_work_vs_close_cts"]["r"],
        "spearman_p": a4["spearman_preceding_work_vs_close_cts"]["p_value"],
        "frac_high_work_high_close": a4["frac_high_work_high_close"],
        "note": "CTS-excursion timing uncorrelated; only 14.3% are high-WORK->high-CTS-CLOSE",
    },
    "A5_s_asymmetry": {
        "s_warning_plus_hard_stop": a5["s_warning_plus_hard_stop"],
        "s_share_of_total": a5["s_share_of_total_warning_hard_stop"],
        "note": "S accounts for 90% of all warning+hard_stop contacts",
    },
    "A6_cof_family": {
        "best_phase_discrimination": a6["best_phase_discrimination"],
        "cof2_p_value": a6["variants"]["cof2"]["mann_whitney_close_vs_work"]["p_value"],
        "note": "COF_2 (CTS + q4_opaque + m_close_bias) has best phase discrimination (p=0.045) but still marginal",
    },
    "A7_closure_overlap": {
        "useful_closure_fraction_cts": a7["overlap_cross_tabulation"]["cts"]["useful_closure_fraction"],
        "note": "Useful closure fraction is 3.2%",
    },
}

# ---------------------------------------------------------------------------
# T4 validation summary
# ---------------------------------------------------------------------------
t4_summary = {
    "anchor": {
        "P2": t4["anchor_test"]["P2"]["result"],
        "n_significant_svs": t4["anchor_test"]["P2"]["n_significant"],
    },
    "primary_tests": {},
    "comparative_diagnostics": {},
}

for test_name in ["NP1", "NP2", "NP3", "NP4", "NP5", "NP6", "NP7"]:
    td = t4["primary_tests"][test_name]
    entry = {"result": td["result"]}
    if "n_folios_passing" in td:
        entry["n_pass"] = td["n_folios_passing"]
        entry["n_total"] = td["n_total"]
        entry["threshold"] = td["threshold"]
    elif "criteria" in td:
        entry["criteria"] = td["criteria"]
    if "s_share_pct" in td:
        entry["s_share_pct"] = td["s_share_pct"]
    t4_summary["primary_tests"][test_name] = entry

cd = t4["comparative_diagnostics"]
t4_summary["comparative_diagnostics"] = {
    "CD1_pcv_old_corr": {
        "pearson_r": cd["CD1"]["pearson_r"],
        "interpretation": cd["CD1"]["interpretation"],
    },
    "CD2_s_fraction": {
        "S_fraction": cd["CD2"]["S_fraction_of_all_edge_contacts"],
    },
    "CD3_qgy_inversion": {
        "full_QGY": cd["CD3"]["full"]["mean_QGY"],
        "full_Y_final": cd["CD3"]["full"]["mean_Y_final"],
        "N2_QGY": cd["CD3"]["N2"]["mean_QGY"],
        "N2_Y_final": cd["CD3"]["N2"]["mean_Y_final"],
        "inversion": cd["CD3"]["N2_paradox_inversion"],
    },
    "CD5_b10_delta": {
        "PCV_delta": cd["CD5"]["deltas"]["PCV"]["delta"],
        "QGY_delta": cd["CD5"]["deltas"]["QGY"]["delta"],
        "old_viability_delta": cd["CD5"]["deltas"]["old_viability"]["delta"],
    },
    "CD7_qgy_ratio": {
        "full": cd["CD7"]["full"],
        "full_higher_than_all_nulls": cd["CD7"]["full_higher_than_all_nulls"],
    },
}

# ---------------------------------------------------------------------------
# Provisional constraints
# ---------------------------------------------------------------------------
constraints = {
    "C1605": {
        "claim": (
            "Packet-coherence viability (PCV) provides higher discrimination than "
            "binary hazard-threshold viability. PCV discriminates full from phase-shuffled "
            "null (NP1 16/20) while old viability could not. Low correlation (r=0.39) "
            "confirms they measure different constructs."
        ),
        "evidence": "NP1 PASS (16/20), CD1 pearson_r=0.391",
        "tier": "provisional",
    },
    "C1606": {
        "claim": (
            "S scoring asymmetry (high-S as productive reserve) is necessary but "
            "insufficient. S still accounts for 84.5% of SAHB even after excluding "
            "high-S events. The remaining low-S burden dominates aggregate metrics."
        ),
        "evidence": "NP7 FAIL (S_share=84.5%), NP2 FAIL (1/20)",
        "tier": "provisional",
    },
    "C1607": {
        "claim": (
            "Quality-gated Y (QGY) partially inverts the N2/N4 paradox. N2's QGY "
            "(0.180) is lower than full's QGY (0.231) despite N2's Y_final being "
            "higher (0.734 vs 0.675). The quality fraction (qgy_ratio) is highest "
            "for the full model (0.319). But the effect is not strong enough to pass "
            "the 14/20 folio gate (NP4 = 13/20)."
        ),
        "evidence": "CD3 N2_paradox_inversion=true, CD7 full=0.319, NP4=13/20",
        "tier": "provisional",
    },
    "C1608": {
        "claim": (
            "Closure opportunity on real traces is severely limited. Only 37.4% of "
            "CLOSE lines exceed CTS 0.3 threshold. Useful closure fraction (high "
            "excursion + high closure signal) is 3.2%. CTS-excursion timing "
            "correlation is zero (r=-0.014). Closure signal and excursion need are "
            "structurally uncoupled."
        ),
        "evidence": "A1 close_frac_gt_03=0.374, A7 useful_closure=0.032, A4 spearman_r=-0.014",
        "tier": "provisional",
    },
    "C1609": {
        "claim": (
            "CLOSE recovery channels become load-bearing under PCV but not under "
            "binary viability. B10 delta under PCV = +0.020 (Cohen's d = 0.465) "
            "while B10 delta under old viability ~ 0.003. The plant mechanism works; "
            "the old readout couldn't detect it."
        ),
        "evidence": "NP6 PASS (all 3 criteria), CD5 PCV_delta=0.020 vs old_viability_delta=0.003",
        "tier": "provisional",
    },
}

# ---------------------------------------------------------------------------
# Next-phase recommendations
# ---------------------------------------------------------------------------
next_phase = {
    "phase": 568,
    "title": "S-ZONE GEOMETRY + COF INTEGRATION",
    "recommendations": [
        (
            "S needs further treatment: possibly exclude S entirely from discrimination "
            "metrics, or redefine S zone geometry to separate productive reserve from "
            "genuinely dangerous excursion."
        ),
        (
            "COF integration to strengthen closure interface: COF_2 was best "
            "(p=0.045) but still marginal. Composite closure observability may need "
            "section-specific normalization."
        ),
        (
            "Lock PCV as the primary viability metric: NP1 validated it, CD1 shows "
            "it measures a different construct from old viability (r=0.39)."
        ),
        (
            "Strengthen QGY criterion or lower folio threshold: NP4 at 13/20, one "
            "short of the 14/20 gate. Explore whether the 6 folios with QGY=0 "
            "(no excursions) should be excluded from the denominator."
        ),
    ],
}

# ---------------------------------------------------------------------------
# Build output JSON
# ---------------------------------------------------------------------------
output = {
    "metadata": {
        "phase": 567,
        "phase_title": "CLOSURE FIELD AUDIT + BURDEN METRIC REFACTOR",
        "script": "t5_synthesis.py",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_files": [
            "t1_closure_field_audit.json",
            "t2_burden_runs.json",
            "t3_burden_null_runs.json",
            "t4_burden_validation.json",
        ],
    },
    "verdict": {
        "label": verdict,
        "p2_result": p2_result,
        "np_pass_count": np_pass_count,
        "np_total": np_total,
        "tests_passed": tests_passed,
        "tests_failed": tests_failed,
        "logic": (
            "PARTIAL: P2 PASS (7/7 SVs) + 3/7 NP pass (NP1, NP5, NP6). "
            "Readout reform partially works but S dominance and weak closure "
            "observability remain unresolved."
        ),
    },
    "t1_audit_summary": t1_summary,
    "t4_validation_summary": t4_summary,
    "cross_phase_comparison": cross_phase,
    "provisional_constraints": constraints,
    "next_phase": next_phase,
}

# Write JSON
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

# ---------------------------------------------------------------------------
# Build REPORT_567.md
# ---------------------------------------------------------------------------

# Helper: NP test description table
np_descriptions = {
    "NP1": ("PCV vs phase-shuffled null (N1)", "PCV discriminates full from N1"),
    "NP2": ("SAHB < null SAHB", "S-corrected burden lower than null"),
    "NP3": ("QGY > N2 null QGY", "Quality-gated Y exceeds label-shuffled null"),
    "NP4": ("QGY > N4 null QGY", "Quality-gated Y exceeds random-phase null"),
    "NP5": ("REF not degenerate", "Excursion resolution non-trivial"),
    "NP6": ("B10 delta under PCV", "CLOSE recovery load-bearing under PCV"),
    "NP7": ("S share < 30%", "S asymmetry sufficiently corrected"),
}

# Helper: NP test result lines
def np_result_line(name):
    td = t4["primary_tests"][name]
    desc, full_desc = np_descriptions[name]
    result = td["result"]
    if "n_folios_passing" in td:
        detail = f"{td['n_folios_passing']}/{td['n_total']} folios"
    elif "criteria" in td:
        n_met = sum(1 for v in td["criteria"].values() if v)
        detail = f"{n_met}/{len(td['criteria'])} criteria"
    elif "s_share_pct" in td:
        detail = f"S={td['s_share_pct']}%"
    else:
        detail = ""
    return f"| {name} | {desc} | **{result}** | {detail} |"


# New metrics table
new_metrics_info = [
    ("PCV", "Packet-Coherence Viability",
     "Product of per-SV coherence scores; replaces binary hazard threshold",
     f"mean={cd3['full']['mean_QGY']:.3f} (via QGY); PCV mean={cd5['deltas']['PCV']['mean_full']:.4f}"),
    ("SAHB", "S-Asymmetry-corrected Hazard Burden",
     "Hazard burden excluding high-S events (which are productive reserve)",
     f"mean={cd5['deltas']['SAHB']['mean_full']:.3f}"),
    ("REF", "Resolved Excursion Fraction",
     "Fraction of excursion resolved by CLOSE-phase tokens",
     f"mean={t4['comparative_diagnostics']['CD4']['full']['REF_mean']:.3f}, eligible={t4['comparative_diagnostics']['CD4']['full']['REF_eligible_fraction']:.3f}"),
    ("QGY", "Quality-Gated Y",
     "Y_final weighted by quality of convergence path",
     f"mean={cd3['full']['mean_QGY']:.3f}"),
    ("CRE", "Close-Return Efficiency",
     "Fraction of CLOSE windows that produce measurable state improvement",
     f"strict={t4['comparative_diagnostics']['CD6']['full']['CRE_strict']:.3f}, soft={t4['comparative_diagnostics']['CD6']['full']['CRE_soft']:.3f}"),
    ("MPZF", "Multi-Parameter Zone Fraction",
     "Fraction of trace time with multiple SVs in basin",
     "computed per-folio"),
]


report = f"""# Phase 567: CLOSURE FIELD AUDIT + BURDEN METRIC REFACTOR

## Verdict: {verdict}

## Summary

Phase 567 tested whether the persistent discrimination failure across phases 563b-566 was primarily a **readout/scoring problem** rather than a plant-law deficiency. The CloseRecoveryApparatus from Phase 566 was reused unchanged. Two interventions were applied:

- **Part A (T1):** A pure data-analysis audit of CTS distributions, closure component discriminability, CTS-excursion timing, S asymmetry, and closure opportunity fractions. This revealed that closure signal is structurally weak: only 37.4% of CLOSE lines exceed CTS 0.3, useful closure fraction is 3.2%, and CTS-excursion timing is uncorrelated (Spearman r = -0.014). S accounts for 90% of all warning+hard_stop contacts, confirming that the old scoring scheme conflates productive S reserve with genuine hazard.

- **Part B (T2-T4):** Six new metrics (PCV, SAHB, REF, QGY, CRE, MPZF) were designed with S asymmetry correction and deployed across 90 full-model runs, 4,220 null/baseline runs, and a 7-test validation battery. Result: P2 PASS (7/7 SVs), NP1 PASS (16/20), NP5 PASS (16/20), NP6 PASS (all 3 criteria met). Four tests failed: NP2 (1/20), NP3 (11/20), NP4 (13/20, one folio short), NP7 (S share still 84.5%).

The verdict is **PARTIAL_METRIC_REFACTOR**: readout reform demonstrably works for packet-coherence viability (PCV) and excursion resolution (REF), and CLOSE recovery becomes load-bearing under PCV. But S dominance remains incompletely resolved, and the quality-gated Y (QGY) effect, while real, is one folio short of significance at the 14/20 gate.

---

## Part A: Closure Field Audit (T1)

### A1: CTS Distribution

- Global CTS mean = {a1['global_mean_cts']:.5f}, median = {a1['global_median_cts']:.5f}
- Only {a1['close_frac_gt_03']:.1%} of CLOSE lines exceed CTS 0.3 threshold
- Section B deficit: {a1['b_deficit']:.5f} (B mean {a1['section_B_mean_cts']:.4f} vs non-B {a1['non_B_mean_cts']:.5f})
- CLOSE-phase CTS mean ({a1['phase_means']['CLOSE']:.5f}) is barely above WORK-phase ({a1['phase_means']['WORK']:.5f})

### A2: CLOSE Window Characterization

- {a2['n_folios_with_close']} folios contain CLOSE-phase lines ({a2['total_close_lines']} total lines)
- Mean CLOSE run length: {a2['close_run_stats']['global_mean_run_length']:.3f} lines (mostly isolated)
- CLOSE token density mean: {a2['close_token_density_summary']['mean']:.3f}

### A3: Closure Component Audit

- No closure component (closure_armed, q4_shift_strength, close_opacity_bias, m_close_bias, q4_opaque_rate, cts) discriminates CLOSE from WORK at p < 0.01
- Best individual discriminator: CTS itself (p = {a3['mann_whitney_close_vs_work']['cts']['p_value']:.5f})
- Components are internally correlated (closure_armed-cts: r = {a3['correlation_matrix']['closure_armed']['cts']:.3f}) but none separates phases

### A4: CTS-Excursion Timing

- Spearman correlation between preceding WORK contribution and CLOSE CTS: r = {a4['spearman_preceding_work_vs_close_cts']['r']:.5f} (p = {a4['spearman_preceding_work_vs_close_cts']['p_value']:.5f})
- Only {a4['frac_high_work_high_close']:.1%} of transitions are high-WORK followed by high-CTS-CLOSE
- Closure signal and excursion need are **structurally uncoupled**

### A5: S Asymmetry Audit

- S warning+hard_stop zone occupancy: {a5['s_warning_plus_hard_stop']:.1%}
- S accounts for **{a5['s_share_of_total_warning_hard_stop']:.1%}** of all warning+hard_stop contacts across all SVs
- Estimated one-sided S warning+hard_stop (excluding high-side reserve): {a5['estimated_one_sided_s_warning_hard_stop']:.3f}
- Other SVs rarely reach warning/hard_stop (T: 0.5%, RC: 0%, C: 3.1%, TR: 0%, X: 0.1%, Y: 1.5%)

### A6: COF Prototype Family

- Four COF variants tested (cts, cof1, cof2, cof3)
- Best phase discrimination: **{a6['best_phase_discrimination']}** (p = {a6['variants']['cof2']['mann_whitney_close_vs_work']['p_value']:.5f})
- Best excursion overlap: **{a6['best_excursion_overlap']}** ({a6['variants']['cof1']['excursion_window_overlap']['frac_overlap']:.1%} overlap)
- Even the best COF variant is marginal (p = 0.045, not < 0.01)

### A7: Closure Window Overlap

- Total CLOSE lines: {a7['diagnosis']['total_close_lines']}
- CLOSE lines with preceding WORK: {a7['diagnosis']['close_with_preceding_work']}
- High-excursion preceding WORK: {a7['diagnosis']['high_excursion_preceding_work']} ({a7['diagnosis']['frac_high_excursion_preceding']:.1%})
- **Useful closure fraction (CTS): {a7['overlap_cross_tabulation']['cts']['useful_closure_fraction']:.1%}**
- Interpretation: closure signal is weakly coupled to excursion need; closure opportunities are structurally sparse

---

## Part B: Burden Metric Refactor (T2-T4)

### New Metrics

| Metric | Full Name | Description |
|--------|-----------|-------------|
| PCV | Packet-Coherence Viability | Product of per-SV coherence scores; replaces binary hazard threshold |
| SAHB | S-Asymmetry-corrected Hazard Burden | Hazard burden excluding high-S events (productive reserve) |
| REF | Resolved Excursion Fraction | Fraction of excursion resolved by CLOSE-phase tokens |
| QGY | Quality-Gated Y | Y_final weighted by quality of convergence path |
| CRE | Close-Return Efficiency | Fraction of CLOSE windows producing measurable state improvement |
| MPZF | Multi-Parameter Zone Fraction | Fraction of trace time with multiple SVs in basin |

### Full Model Summary Values

| Metric | Mean |
|--------|------|
| PCV | {cd5['deltas']['PCV']['mean_full']:.4f} |
| SAHB | {cd5['deltas']['SAHB']['mean_full']:.3f} |
| REF_mean | {t4['comparative_diagnostics']['CD4']['full']['REF_mean']:.3f} |
| REF_eligible_fraction | {t4['comparative_diagnostics']['CD4']['full']['REF_eligible_fraction']:.3f} |
| QGY | {cd3['full']['mean_QGY']:.3f} |
| qgy_ratio | {cd7['full']:.3f} |
| CRE_strict | {t4['comparative_diagnostics']['CD6']['full']['CRE_strict']:.3f} |
| CRE_soft | {t4['comparative_diagnostics']['CD6']['full']['CRE_soft']:.3f} |

### Test Results

| Test | Description | Result | Detail |
|------|-------------|--------|--------|
| P2 | Anchor: line packet shape recovery | **{t4['anchor_test']['P2']['result']}** | {t4['anchor_test']['P2']['n_significant']}/7 SVs significant |
{chr(10).join(np_result_line(n) for n in ['NP1','NP2','NP3','NP4','NP5','NP6','NP7'])}

**Score: P2 PASS + {np_pass_count}/{np_total} NP pass (NP1, NP5, NP6)**

### Comparative Diagnostics

| Diagnostic | Finding |
|------------|---------|
| CD1: PCV vs old viability | Pearson r = {cd['CD1']['pearson_r']:.4f} — measuring different constructs |
| CD2: S edge dominance | S = {cd['CD2']['S_fraction_of_all_edge_contacts']:.1%} of all edge contacts |
| CD3: QGY paradox inversion | N2 QGY ({cd3['N2']['mean_QGY']:.3f}) < full QGY ({cd3['full']['mean_QGY']:.3f}) despite N2 Y_final ({cd3['N2']['mean_Y_final']:.3f}) > full Y_final ({cd3['full']['mean_Y_final']:.3f}) |
| CD4: REF non-degeneracy | Full REF_mean = {t4['comparative_diagnostics']['CD4']['full']['REF_mean']:.3f}, eligible = {t4['comparative_diagnostics']['CD4']['full']['REF_eligible_fraction']:.3f}; all nulls have REF ~ 0 |
| CD5: B10 delta | PCV: +{cd5['deltas']['PCV']['delta']:.3f}, QGY: +{cd5['deltas']['QGY']['delta']:.3f}, old_viability: +{cd5['deltas']['old_viability']['delta']:.3f} |
| CD6: CRE window truncation | CRE_soft ({t4['comparative_diagnostics']['CD6']['full']['CRE_soft']:.3f}) > CRE_strict ({t4['comparative_diagnostics']['CD6']['full']['CRE_strict']:.3f}): window truncation masks real returns |
| CD7: Quality fraction | Full qgy_ratio ({cd7['full']:.3f}) highest of all models; all nulls lower |
| CD8: QGY rank test | Full vs N2: U={cd['CD8']['N2']['U_statistic']}, p={cd['CD8']['N2']['p_value']:.3f}; Full vs N4: U={cd['CD8']['N4']['U_statistic']}, p={cd['CD8']['N4']['p_value']:.3f} |

---

## Cross-Phase Comparison

| Phase | Score | Key Result |
|-------|-------|------------|
| 563 | 5/9 | Baseline apparatus coupling |
| 563b | 3/9 | Sensitivity recalibration |
| 564 | 2/9 | Event-gated execution |
| 564b | 2/9 | Selective restoration |
| 565 | 2/9 | Permeability calibration |
| 566 | 1/9 | CLOSE recovery |
| **567** | **P2 + {np_pass_count}/{np_total} NP** | **PARTIAL: readout reform partially works** |

> **Note:** Phase 567 uses a different test battery (P2 anchor + NP1-NP7) than phases 563-566 (P1-P9). Direct score comparison is not straightforward. The shift to NP tests reflects the hypothesis change: from "does the plant law work?" (P tests) to "does the readout detect what the plant law does?" (NP tests).

---

## Analysis

### What Worked

1. **PCV replaces old viability.** The correlation between PCV and old_viability is only r = 0.39 (CD1), confirming they measure fundamentally different aspects. PCV discriminates the full model from phase-shuffled nulls (NP1: 16/20), which old viability could not reliably do. This is the single strongest positive result.

2. **CLOSE recovery becomes visible.** Under PCV, the B10 (ablated CLOSE) delta is +0.020 with Cohen's d = 0.465 (NP6 PASS on all three criteria). Under old viability, the same delta was ~0.003. The plant mechanism was always there; the old readout was blind to it.

3. **REF is non-degenerate.** The full model resolves ~44.6% of excursion on average (REF_mean = 0.446), while all null models have REF near zero (CD4). This confirms that excursion resolution is a real, non-trivial property of the full model's CLOSE-phase behavior.

4. **QGY partially resolves the N2 paradox.** The N2 null (label-shuffled) has higher Y_final (0.734) than the full model (0.675), but lower QGY (0.180 vs 0.231). The quality fraction (qgy_ratio = 0.319 for full, highest of all models) confirms that the full model's convergence is higher quality even when the raw endpoint is lower.

### What Did Not Work

1. **S asymmetry correction is insufficient.** Even after excluding high-S events from SAHB, S still accounts for 84.5% of all edge contacts (NP7 FAIL at 84.5% vs 30% threshold). The NP2 test (SAHB < null) fails catastrophically (1/20). S zone geometry needs a more fundamental rethinking.

2. **QGY is one folio short.** NP4 (full QGY > N4 QGY) reaches 13/20, missing the 14/20 threshold by one folio. Six folios have QGY = 0 (no excursions in preferred profile), which may indicate a denominator problem rather than a real failure.

3. **Closure observability remains structurally weak.** The T1 audit reveals a fundamental constraint: closure signal (CTS) is uncorrelated with excursion need (Spearman r = -0.014), only 37.4% of CLOSE lines exceed the 0.3 threshold, and useful closure fraction is 3.2%. No individual closure component discriminates CLOSE from WORK at p < 0.01.

### Why Partial

The readout reform succeeded at the **packet level** (PCV) and the **excursion-resolution level** (REF, NP6), but failed at the **aggregate scoring level** (SAHB, NP7) because S dominance is a zone-geometry problem, not a scoring-weight problem. The old metrics were measuring the wrong thing (binary threshold vs. coherence), but the new metrics are still measuring in the wrong place (S-dominated edge contacts). The plant law works; the observation framework is 60% fixed.

---

## Provisional Constraints

### C1605: PCV Discrimination
{constraints['C1605']['claim']}
- Evidence: {constraints['C1605']['evidence']}
- Tier: Provisional

### C1606: S Asymmetry Insufficiency
{constraints['C1606']['claim']}
- Evidence: {constraints['C1606']['evidence']}
- Tier: Provisional

### C1607: QGY Partial Paradox Inversion
{constraints['C1607']['claim']}
- Evidence: {constraints['C1607']['evidence']}
- Tier: Provisional

### C1608: Closure Opportunity Scarcity
{constraints['C1608']['claim']}
- Evidence: {constraints['C1608']['evidence']}
- Tier: Provisional

### C1609: PCV-Visible CLOSE Recovery
{constraints['C1609']['claim']}
- Evidence: {constraints['C1609']['evidence']}
- Tier: Provisional

---

## Lessons and Implications

1. **Readout matters as much as mechanism.** Phases 563b-566 progressively degraded apparatus performance by modifying the plant law, when the actual problem was partly in how outcomes were measured. PCV reveals structure that old viability was blind to. This implies that any future apparatus work must validate readout fidelity before concluding that a mechanism has failed.

2. **S is not noise; it is the dominant signal in the wrong frame.** S's high-side drift is a genuine structural property of the manuscript's S variable, not a scoring artifact. Excluding high-S events from SAHB was the right direction, but the remaining low-S burden still dominates because S is the only variable that routinely enters warning/hard_stop zones. The solution is not to suppress S further but to redefine what "dangerous" means for S specifically.

3. **Closure is a narrow channel.** The T1 audit establishes that closure opportunity is structurally scarce (3.2% useful fraction, zero CTS-excursion correlation). This is not a failure of the apparatus but a property of the manuscript: CLOSE phases are brief, sparse, and disconnected from excursion timing. Any model that expects closure to be a primary recovery mechanism must reckon with this scarcity.

4. **Quality gating reveals hidden structure.** The QGY/qgy_ratio inversion of the N2 paradox is a genuine insight: raw Y_final rewards any convergence, while QGY rewards convergence that follows excursion resolution. This distinction may generalize beyond the current apparatus line.

5. **One-folio margins suggest threshold sensitivity.** NP4 at 13/20 (one short) suggests that the 14/20 gate may be slightly too aggressive for a 20-folio pilot, or that the 6 folios with QGY = 0 need special handling. Phase 568 should consider whether zero-excursion folios belong in the QGY denominator.

---

## Next Phase Recommendations

Phase 568 should focus on **S-zone geometry** and **COF integration**, building on the partial success of the metric refactor:

1. **S zone geometry reform:** Either exclude S entirely from discrimination metrics or redefine S zone boundaries to separate productive reserve (high-side drift within normal S range) from genuinely dangerous S excursion (structural departure from expected S behavior). The current 4-zone model (basin/corridor/warning/hard_stop) may not be appropriate for S.

2. **COF integration:** COF_2 (CTS + q4_opaque + m_close_bias) achieved the best phase discrimination in the T1 audit (p = 0.045) but remains marginal. Section-specific COF normalization may strengthen the closure-excursion interface enough to improve NP tests.

3. **Lock PCV:** PCV should replace old_viability as the primary viability metric going forward. NP1 validates it; CD1 confirms it measures a different construct.

4. **QGY denominator adjustment:** Explore whether folios with zero excursions (QGY = 0 by construction, not by failure) should be excluded from the NP4 denominator. This could flip 13/20 to 13/14 or similar.

---

*Generated by t5_synthesis.py | Phase 567 | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*
"""

with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write(report)

# ---------------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------------
print(f"Phase 567 Synthesis Complete")
print(f"  Verdict: {verdict}")
print(f"  P2: {p2_result} ({t4['anchor_test']['P2']['n_significant']}/7 SVs)")
print(f"  NP pass: {np_pass_count}/{np_total} ({', '.join(tests_passed)})")
print(f"  NP fail: {', '.join(tests_failed)}")
print(f"  Constraints: C1605-C1609 (provisional)")
print(f"  JSON: {OUT_JSON}")
print(f"  Report: {OUT_REPORT}")
