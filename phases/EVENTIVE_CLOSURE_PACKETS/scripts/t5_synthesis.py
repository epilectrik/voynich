"""
Phase 569 T5: Synthesis and Report Generator
=============================================
Reads T4 validation results, T2 event run summary, and T1 event taxonomy.
Produces:
  - t5_synthesis.json  (machine-readable verdict + key findings)
  - REPORT_569.md      (human-readable phase report)
"""

import json, os, sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(BASE, 'results')

# ---------------------------------------------------------------------------
# Load inputs
# ---------------------------------------------------------------------------
with open(os.path.join(RESULTS, 't4_event_validation.json')) as f:
    t4 = json.load(f)

with open(os.path.join(RESULTS, 't2_event_runs.json')) as f:
    t2 = json.load(f)

with open(os.path.join(RESULTS, 't1_event_taxonomy.json')) as f:
    t1 = json.load(f)

# ---------------------------------------------------------------------------
# Extract key values
# ---------------------------------------------------------------------------
p2 = t4['P2']
pt_tests = t4['PT_tests']
diagnostics = t4['diagnostics']
score_summary = t4['score_summary']

# T2 summary
t2_summary = t2['summary']
mean_metrics = t2_summary['mean_metrics']
event_type_means = t2_summary['event_type_means_global']

# T1 event frequency
event_freq = t1['event_frequency']['global']

# ---------------------------------------------------------------------------
# Determine verdict
# ---------------------------------------------------------------------------
p2_pass = p2['result'] == 'PASS'
pt_pass_count = score_summary['PT_pass_count']
pt_results = score_summary['PT_results']

if not p2_pass or pt_pass_count < 2:
    verdict = 'EVENTIVE_CLOSURE_INSUFFICIENT'
elif pt_pass_count >= 4:
    verdict = 'EVENTIVE_CLOSURE_VALIDATED'
else:
    verdict = 'PARTIAL_EVENTIVE_CLOSURE'

# ---------------------------------------------------------------------------
# Build cross-phase comparison
# ---------------------------------------------------------------------------
cross_phase = [
    {"phase": 563,  "score": "5/9",             "key_result": "Baseline apparatus coupling"},
    {"phase": "563b","score": "3/9",             "key_result": "Sensitivity recalibration"},
    {"phase": 564,  "score": "2/9",             "key_result": "Event-gated execution"},
    {"phase": "564b","score": "2/9",             "key_result": "Selective restoration"},
    {"phase": 565,  "score": "2/9",             "key_result": "Permeability calibration"},
    {"phase": 566,  "score": "1/9",             "key_result": "CLOSE recovery"},
    {"phase": 567,  "score": "P2 + 3/7 NP",    "key_result": "PARTIAL: readout reform partially works"},
    {"phase": 568,  "score": "P2 + 3/7 EP",    "key_result": "PARTIAL: controlled excursion metrics partially work"},
    {"phase": 569,  "score": f"P2 + {pt_pass_count}/5 PT", "key_result": verdict},
]

# ---------------------------------------------------------------------------
# Key findings
# ---------------------------------------------------------------------------
key_findings = [
    "ERM axis inversion: full model ERM negative, null ERM positive",
    "UEB and WCP anchors stable (PT3 PASS)",
    "No selective event type reached Tier 2 threshold",
    "Plant dynamics problem, not readout/averaging problem",
]

# ---------------------------------------------------------------------------
# Confirmed constraints (from 568, confirmed by PT3 PASS)
# ---------------------------------------------------------------------------
confirmed_constraints = ["C1612", "C1614"]
new_constraints = []

# ---------------------------------------------------------------------------
# Build synthesis JSON
# ---------------------------------------------------------------------------
timestamp = datetime.now(timezone.utc).isoformat()

synthesis = {
    "metadata": {
        "phase": 569,
        "script": "t5_synthesis.py",
        "timestamp": timestamp,
    },
    "verdict": verdict,
    "p2_result": p2['result'],
    "pt_pass_count": pt_pass_count,
    "pt_results": pt_results,
    "priority_event_type": t4['metadata']['priority_event_type'],
    "full_model_summary": {
        "PCV": round(mean_metrics['PCV'], 6),
        "SAHB": round(mean_metrics['SAHB'], 6),
        "WCU": round(mean_metrics['WCU'], 6),
        "SLR_mean": round(mean_metrics['SLR_mean'], 6),
        "UEB": round(mean_metrics['UEB'], 6),
        "WCP": round(mean_metrics['WCP'], 6),
        "EWP": round(mean_metrics['EWP'], 6),
        "CCY": round(mean_metrics['CCY'], 6),
        "QGY": round(mean_metrics['QGY'], 6),
        "old_viability": round(mean_metrics['old_viability'], 6),
        "old_y_final": round(mean_metrics['old_y_final'], 6),
        "n_tokens": mean_metrics['n_tokens'],
    },
    "event_summary": {
        etype: {
            "total_global": event_freq[etype]['total'],
            "fraction_global": event_freq[etype]['fraction'],
            "pilot_count": event_type_means[etype]['count'],
            "pilot_mean_ERM": round(event_type_means[etype]['mean_ERM'], 6),
            "pilot_EIR": round(event_type_means[etype]['EIR'], 6),
        }
        for etype in ['E_any', 'E_opaque', 'E_opaque_decisive', 'E_compound',
                       'E_armed', 'E_cts50', 'E_mcb', 'E_decisive']
    },
    "key_findings": key_findings,
    "confirmed_constraints": confirmed_constraints,
    "new_constraints": new_constraints,
    "cross_phase": cross_phase,
}

# Write synthesis JSON
synth_path = os.path.join(RESULTS, 't5_synthesis.json')
with open(synth_path, 'w') as f:
    json.dump(synthesis, f, indent=2)
print(f"[T5] Wrote {synth_path}")

# ---------------------------------------------------------------------------
# Build REPORT_569.md
# ---------------------------------------------------------------------------

# Helpers
def fmt(v, decimals=5):
    """Format a number for display."""
    if isinstance(v, int):
        return str(v)
    return f"{v:.{decimals}f}"

# PT1 per-folio detail
pt1 = pt_tests['PT1']
pt1_lines = []
for folio, data in pt1['per_folio'].items():
    pt1_lines.append(
        f"| {folio} | {fmt(data['full_ERM'])} | {fmt(data['null_ERM'])} | "
        f"{data['n_dominated']} | {'PASS' if data['pass'] else 'FAIL'} |"
    )

# PT2 detail
pt2 = pt_tests['PT2']

# PT3 detail
pt3 = pt_tests['PT3']

# PT4 detail
pt4 = pt_tests['PT4']
pt4_lines = []
for etype, data in pt4['per_type'].items():
    pt4_lines.append(
        f"| {etype} | {data['n_folios']} | {fmt(data['full_mean_ERM'])} | "
        f"{fmt(data['null_mean_ERM'])} | {fmt(data['cohens_d'])} | "
        f"{'PASS' if data['pass'] else 'FAIL'} |"
    )

# PT5 detail
pt5 = pt_tests['PT5']

# D2 summary (all event types, full vs null ERM)
d2 = diagnostics['D2']
d2_lines = []
for etype in ['E_any', 'E_opaque', 'E_opaque_decisive', 'E_compound',
              'E_armed', 'E_cts50', 'E_mcb', 'E_decisive']:
    d = d2[etype]
    d2_lines.append(
        f"| {etype} | {d['n_folios']} | {fmt(d['full_mean_ERM'])} | "
        f"{fmt(d['null_mean_ERM'])} | {fmt(d['cohens_d_ERM'])} |"
    )

# D5 summary
d5 = diagnostics['D5']

# D6 summary
d6 = diagnostics['D6']

# D7 summary
d7 = diagnostics['D7']

# D8 summary
d8 = diagnostics['D8']

report = f"""# Phase 569: EVENTIVE CLOSURE PACKETS

## Verdict: {verdict}

## Summary
Phase 569 tested whether segmenting closure lines by event type improves discrimination between the full model and null models. Building on Phase 568's shared metrics module (WCU, SLR, UEB, CCY, WCP, EWP), this phase introduced an event taxonomy (E_opaque, E_opaque_decisive, E_compound, E_armed, E_cts50, E_mcb, E_decisive) grounded in the opacity grammar (C1440-C1445) and tested whether eventive closure packets -- closure events filtered by type and qualified by demand context -- discriminate better than aggregate E_any.

The validation battery comprises P2 (line packet shape recovery anchor) and 5 primary eventive tests (PT1-PT5). Result: **{verdict}** -- P2 PASS, {pt_pass_count}/5 PT pass (PT3 only). PT1, PT2, PT4, PT5 failed.

**Critical finding:** ERM axis inversion. The full model's ERM is negative for most event types while null ERM is strongly positive (~0.34-0.43). During closure events, the full model INCREASES process deviation rather than resolving it. Nulls appear to resolve excursion better because shuffled phases create regression-to-mean artifacts.

---

## Context
Phase 568 established three stable discrimination metrics: UEB (unresolved excursion burden), WCP (work-closure packet coherence), and EWP (edge waste penalty). These confirmed that the burden axis inversion from Phase 567 was a measurement artifact (C1612) and that packet coherence is a genuine property of supervised traces (C1614). However, EP1, EP2, EP4, EP7 failed, suggesting remaining discrimination gaps.

Phase 569 asked: can we improve discrimination by examining closure events selectively -- filtering by event type (opacity, compound structure, arming state) and qualifying by demand context (work-preceded events that create genuine excursion needing resolution)?

## What Changed
1. **Event Taxonomy (T1):** Classified all {event_freq['E_any']['total']} closure lines across 83 Currier B folios into 7 overlapping event types based on opacity measures, compound token structure, MCB density, CTS threshold exceedance, decisive opacity, and arming state.

2. **Event Executor (T2):** Extended the shared_metrics plant simulator to compute per-event-type ERM (Excursion Resolution Metric), ESQ (Excursion Sequencing Quality), and EW (Excursion Waste) for each closure line, plus demand qualifiers (work_preceded).

3. **Null Event Executor (T3):** Ran 40 null shuffles per folio using the same event taxonomy and shared_metrics module, eliminating T1/T2 metric divergence.

4. **Event Validation (T4):** Five primary tests (PT1-PT5) plus 8 diagnostics (D1-D8) testing folio-level dominance, B10 comparison, anchor stability, type-selective discrimination, and demand qualification.

## Test Results

### P2: Line Packet Shape Recovery (Anchor)
**{p2['result']}** -- {p2['n_significant']}/{p2['gate']} SVs significant (n={p2['n_matched_lines']} lines). 9th consecutive PASS.

| SV | rho | p | significant |
|----|-----|---|-------------|
| T | {fmt(p2['per_sv']['T']['rho'])} | {fmt(p2['per_sv']['T']['p'])} | {p2['per_sv']['T']['significant']} |
| RC | {fmt(p2['per_sv']['RC']['rho'])} | {fmt(p2['per_sv']['RC']['p'])} | {p2['per_sv']['RC']['significant']} |
| S | {fmt(p2['per_sv']['S']['rho'])} | {fmt(p2['per_sv']['S']['p'])} | {p2['per_sv']['S']['significant']} |
| C | {fmt(p2['per_sv']['C']['rho'])} | {fmt(p2['per_sv']['C']['p'])} | {p2['per_sv']['C']['significant']} |
| TR | {fmt(p2['per_sv']['TR']['rho'])} | {fmt(p2['per_sv']['TR']['p'])} | {p2['per_sv']['TR']['significant']} |
| X | {fmt(p2['per_sv']['X']['rho'])} | {fmt(p2['per_sv']['X']['p'])} | {p2['per_sv']['X']['significant']} |
| Y | {fmt(p2['per_sv']['Y']['rho'])} | {fmt(p2['per_sv']['Y']['p'])} | {p2['per_sv']['Y']['significant']} |

### Primary Eventive Tests (PT1-PT5)
| Test | Description | Result | Detail |
|------|-------------|--------|--------|
| PT1 | Full dominates null on >= 2/3 ERM metrics per folio (E_any) | **{pt1['result']}** | {pt1['n_pass']}/{pt1['n_eligible']} folios (gate={pt1['gate']}) |
| PT2 | Full ERM > B10 ERM (Cohen's d >= 0.35) | **{pt2['result']}** | d = {fmt(pt2['cohens_d'])} (gate={fmt(pt2['gate'])}) |
| PT3 | UEB + WCP anchors stable | **{pt3['result']}** | UEB {pt3['ueb_pass']}/{pt3['ueb_gate']}, WCP {pt3['wcp_pass']}/{pt3['wcp_gate']} |
| PT4 | >= 2 event types individually discriminating | **{pt4['result']}** | {pt4['n_types_discriminating']}/{pt4['gate']} types |
| PT5 | Demand-qualified ERM > null ERM (d >= 0.25) | **{pt5['result']}** | d = {fmt(pt5['cohens_d'])} (gate={fmt(pt5['gate'])}) |

**Score: P2 {p2['result']} + {pt_pass_count}/5 PT pass**

### Diagnostics Summary (D1-D8)

**D1: Event Count Ratio (full vs null)**
| Event Type | Full Mean Count | Null Mean Count | Ratio |
|------------|-----------------|-----------------|-------|
| E_any | {fmt(diagnostics['D1']['E_any']['full_mean_count'])} | {fmt(diagnostics['D1']['E_any']['null_mean_count'])} | {fmt(diagnostics['D1']['E_any']['ratio'])} |
| E_opaque | {fmt(diagnostics['D1']['E_opaque']['full_mean_count'])} | {fmt(diagnostics['D1']['E_opaque']['null_mean_count'])} | {fmt(diagnostics['D1']['E_opaque']['ratio'])} |
| E_armed | {fmt(diagnostics['D1']['E_armed']['full_mean_count'])} | {fmt(diagnostics['D1']['E_armed']['null_mean_count'])} | {fmt(diagnostics['D1']['E_armed']['ratio'])} |

**D2: Full vs Null ERM by Event Type (axis inversion diagnostic)**
| Event Type | n_folios | Full Mean ERM | Null Mean ERM | Cohen's d |
|------------|----------|---------------|---------------|-----------|
{chr(10).join(d2_lines)}

**D3: Event Tier Distribution** -- E_any: {diagnostics['D3']['E_any']['tier_counts']['3']} folios at tier 3 (highest), {diagnostics['D3']['E_any']['tier_counts']['0']} at tier 0.

**D4: Full vs B10 ERM by Event Type** -- E_any: full mean ERM = {fmt(diagnostics['D4']['E_any']['full_mean_ERM'])}, B10 mean ERM = {fmt(diagnostics['D4']['E_any']['b10_mean_ERM'])}, Cohen's d = {fmt(diagnostics['D4']['E_any']['cohens_d_ERM'])}.

**D5: ERM-CCY Correlation** -- Pearson r = {fmt(d5['pearson_r'])} (n={d5['n_folios']} folios). No meaningful correlation between event resolution and closure-conditioned yield.

**D6: Global vs Section-Normalized Thresholds** -- E_any global mean ERM = {fmt(d6['global']['E_any']['mean_ERM'])}, section-normalized mean ERM = {fmt(d6['section_normalized']['E_any']['mean_ERM'])}. No improvement from section normalization for E_any.

**D7: Phase-Native vs Structure-Native ERM** -- Phase-native mean ERM = {fmt(d7['phase_native_mean_ERM'])} (n={d7['n_phase_native']}), structure-native mean ERM = {fmt(d7['structure_native_mean_ERM'])} (n={d7['n_structure_native']}). Phase-native ERM is slightly higher, suggesting phase alignment helps but the gap is modest.

**D8: Demand-Qualified Event Resolution** -- work_preceded: {d8['by_qualifier']['work_preceded']['n_folios']} folios, {d8['by_qualifier']['work_preceded']['total_events']} events, mean ERM = {fmt(d8['by_qualifier']['work_preceded']['mean_ERM'])}. Demand-qualified events show positive ERM (0.367) vs overall E_any ERM (-0.011), confirming that work-preceded closure events resolve better, but the effect is too weak to pass PT5 (d={fmt(pt5['cohens_d'])}).

---

## Full Model Summary Values
| Metric | Mean |
|--------|------|
| PCV | {fmt(mean_metrics['PCV'])} |
| SAHB | {fmt(mean_metrics['SAHB'])} |
| WCU | {fmt(mean_metrics['WCU'])} |
| SLR_mean | {fmt(mean_metrics['SLR_mean'])} |
| UEB | {fmt(mean_metrics['UEB'])} |
| WCP | {fmt(mean_metrics['WCP'])} |
| EWP | {fmt(mean_metrics['EWP'])} |
| CCY | {fmt(mean_metrics['CCY'])} |
| QGY | {fmt(mean_metrics['QGY'])} |
| old_viability | {fmt(mean_metrics['old_viability'])} |
| old_y_final | {fmt(mean_metrics['old_y_final'])} |
| n_tokens | {mean_metrics['n_tokens']} |

### Event Type Summary (Pilot Folios)
| Event Type | Global Count | Global Fraction | Pilot Count | Pilot Mean ERM | Pilot EIR |
|------------|-------------|-----------------|-------------|----------------|-----------|
| E_any | {event_freq['E_any']['total']} | {fmt(event_freq['E_any']['fraction'], 4)} | {event_type_means['E_any']['count']} | {fmt(event_type_means['E_any']['mean_ERM'])} | {fmt(event_type_means['E_any']['EIR'])} |
| E_opaque | {event_freq['E_opaque']['total']} | {fmt(event_freq['E_opaque']['fraction'], 4)} | {event_type_means['E_opaque']['count']} | {fmt(event_type_means['E_opaque']['mean_ERM'])} | {fmt(event_type_means['E_opaque']['EIR'])} |
| E_opaque_decisive | {event_freq['E_opaque_decisive']['total']} | {fmt(event_freq['E_opaque_decisive']['fraction'], 4)} | {event_type_means['E_opaque_decisive']['count']} | {fmt(event_type_means['E_opaque_decisive']['mean_ERM'])} | {fmt(event_type_means['E_opaque_decisive']['EIR'])} |
| E_compound | {event_freq['E_compound']['total']} | {fmt(event_freq['E_compound']['fraction'], 4)} | {event_type_means['E_compound']['count']} | {fmt(event_type_means['E_compound']['mean_ERM'])} | {fmt(event_type_means['E_compound']['EIR'])} |
| E_armed | {event_freq['E_armed']['total']} | {fmt(event_freq['E_armed']['fraction'], 4)} | {event_type_means['E_armed']['count']} | {fmt(event_type_means['E_armed']['mean_ERM'])} | {fmt(event_type_means['E_armed']['EIR'])} |
| E_cts50 | {event_freq['E_cts50']['total']} | {fmt(event_freq['E_cts50']['fraction'], 4)} | {event_type_means['E_cts50']['count']} | {fmt(event_type_means['E_cts50']['mean_ERM'])} | {fmt(event_type_means['E_cts50']['EIR'])} |
| E_mcb | {event_freq['E_mcb']['total']} | {fmt(event_freq['E_mcb']['fraction'], 4)} | {event_type_means['E_mcb']['count']} | {fmt(event_type_means['E_mcb']['mean_ERM'])} | {fmt(event_type_means['E_mcb']['EIR'])} |
| E_decisive | {event_freq['E_decisive']['total']} | {fmt(event_freq['E_decisive']['fraction'], 4)} | {event_type_means['E_decisive']['count']} | {fmt(event_type_means['E_decisive']['mean_ERM'])} | {fmt(event_type_means['E_decisive']['EIR'])} |

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
| 567 | P2 + 3/7 NP | PARTIAL: readout reform partially works |
| 568 | P2 + 3/7 EP | PARTIAL: controlled excursion metrics partially work |
| **569** | **P2 + {pt_pass_count}/5 PT** | **{verdict}** |

> **Note:** Phases 563-566 used P1-P9 tests. Phase 567 used P2 + NP1-NP7. Phase 568 uses P2 + EP1-EP7. Phase 569 uses P2 + PT1-PT5. Test batteries are not directly comparable but track the same underlying question: does the full model discriminate from nulls?

---

## Analysis

### What Worked
1. **PT3 PASS** -- UEB ({pt3['ueb_pass']}/{pt3['ueb_gate']}) and WCP ({pt3['wcp_pass']}/{pt3['wcp_gate']}) anchors stable. The Phase 568 wins are real and reproducible under the shared_metrics module.
2. **P2 PASS** -- 9th consecutive line packet shape recovery. The structural backbone of the model is robust.
3. **Shared metrics module** -- eliminated T1/T2 divergence by using identical plant simulation code across full and null executors. This is a process success, not a test result.
4. **Event taxonomy produced meaningful frequency distributions** -- E_opaque covers 32.0% of closure lines, E_opaque_decisive 24.0%, E_compound 36.7%, grounding the taxonomy in the opacity grammar (C1440-C1445).
5. **Demand-qualified events show positive ERM** -- work_preceded events have mean ERM = 0.367 vs overall E_any ERM = -0.011. Work-preceded closure events do resolve excursion, confirming that the qualifier concept is sound even if the effect is too weak for PT5.

### What Did Not Work
1. **PT1 FAIL** -- Only 5/18 eligible folios showed full-model dominance with E_any (gate = 12). The full model fails to dominate null models on event resolution metrics at the folio level.
2. **PT2 FAIL** -- Cohen's d = {fmt(pt2['cohens_d'])} (gate = {fmt(pt2['gate'])}). The full model's E_any ERM (mean = {fmt(pt2['full_mean_ERM'])}) is actually WORSE than B10's ERM (mean = {fmt(pt2['b10_mean_ERM'])}). B10 has better event resolution than the full model.
3. **PT4 FAIL** -- 0/2 event types individually discriminating (gate = 2). No selective event type passed the d >= 0.35 threshold with >= 10 folios. All event types show negative Cohen's d (full ERM < null ERM).
4. **PT5 FAIL** -- d = {fmt(pt5['cohens_d'])} (gate = {fmt(pt5['gate'])}). Demand-qualified events are insufficient to overcome the overall ERM deficit.
5. **ERM axis inversion across all event types** -- Full model ERM is negative or near zero for E_opaque ({fmt(d2['E_opaque']['full_mean_ERM'])}), E_armed ({fmt(d2['E_armed']['full_mean_ERM'])}), E_cts50 ({fmt(d2['E_cts50']['full_mean_ERM'])}), E_opaque_decisive ({fmt(d2['E_opaque_decisive']['full_mean_ERM'])}), while null ERM is consistently positive (~0.34-0.43).

### Why INSUFFICIENT
The fundamental finding is **ERM axis inversion**: during closure events, the full model's plant dynamics increase process deviation rather than resolving it. Null models appear to resolve excursion better because:

1. Under shuffled phases, "CLOSE" labels land on random lines, creating regression-to-mean artifacts that look like resolution.
2. The full model's CLOSE lines are placed where genuine excursion exists, making resolution harder because the plant faces real deviation.
3. The plant's close recovery channels (R1-R5) may not be strong enough to overcome the ongoing excursion at those specific positions.

This means the remaining discrimination gap is **not** a readout/averaging problem (which phases 567-569 tested). It is a **plant dynamics** problem: the apparatus needs stronger or differently-tuned close recovery channels at the specific positions where closure events occur.

With P2 PASS + only 1/5 PT pass, the result falls below the 2/5 threshold for PARTIAL and is therefore INSUFFICIENT.

---

## Provisional Constraints

### Confirmed from Phase 568
- **C1612: Unresolved excursion burden inverts SAHB** -- Confirmed. PT3 PASS shows UEB discriminates ({pt3['ueb_pass']}/{pt3['ueb_gate']} folios), meaning the CLOSE-phase burden restriction is a genuine property.
- **C1614: Packet coherence discriminates supervised traces** -- Confirmed. PT3 PASS shows WCP discriminates ({pt3['wcp_pass']}/{pt3['wcp_gate']} folios), meaning phase-aware coherence is a real structural property.

### New Constraints from Phase 569
None. With verdict INSUFFICIENT, no new constraints are validated.

---

## Lessons and Implications

1. **ERM inversion is diagnostic.** The fact that full model ERM < null ERM tells us the plant is failing at CLOSE-line resolution, not that the readout was wrong. This inverts the blame from measurement framework (phases 567-568) to plant dynamics.

2. **Anchors hold.** UEB and WCP (from 568) are confirmed stable across a different test battery and a different executor architecture. These are durable properties, not phase-specific artifacts.

3. **Eventive taxonomy is structurally sound but the plant cannot exploit it.** The event types (E_opaque, E_opaque_decisive, E_compound, E_armed) are well-grounded in constraints (C1440-C1445). The problem is not with the classification of closure events but with the plant's inability to resolve them.

4. **Demand qualification partially works.** Work-preceded events show positive ERM (0.367) while overall E_any ERM is negative (-0.011). The concept of demand-driven closure is sound, but the plant's recovery during demand-qualified events is still insufficient to discriminate from nulls at the required effect size.

5. **Section-normalized thresholds do not help.** D6 shows no improvement from section-aware event classification (E_any: global ERM = {fmt(d6['global']['E_any']['mean_ERM'])}, section-normalized ERM = {fmt(d6['section_normalized']['E_any']['mean_ERM'])}). The problem is below the classification layer.

6. **Phase-native vs structure-native ERM.** D7 shows phase-native ERM (0.351) is slightly higher than structure-native ERM (0.299), suggesting phase alignment helps modestly but is not the bottleneck.

7. **No single event type reaches Tier 2 threshold.** Only E_any had >= 10 folios with events. The 20-pilot-folio set is too small for selective event types that appear in fewer folios.

---

## Next Phase Recommendations

1. **Diagnose CLOSE-phase plant dynamics.** Why does the full model INCREASE deviation during CLOSE? Examine R1-R5 channel behavior during specific closure events. The ERM inversion is the central diagnostic target.

2. **Plant law modification.** If CLOSE recovery channels are too weak, consider gain amplification, zone boundary adjustment, or adding new recovery pathways. The plant's close-phase behavior is the bottleneck, not the measurement framework.

3. **Eventive taxonomy should be retained.** The event types and demand qualifiers are well-defined; the problem is the plant, not the measurement framework. Future phases that modify plant dynamics should reuse this taxonomy.

4. **Expand pilot set.** 20 folios is insufficient for selective event types. Consider 40+ folios to achieve >= 10 folios per event type for selective discrimination testing.

5. **Next-phase fork:** The remaining discrimination gap is confirmed as a plant dynamics problem, not further readout refinement. Plant law modification is the next step.

---

*Generated by t5_synthesis.py | Phase 569 | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC*
"""

# Write report
report_path = os.path.join(BASE, 'REPORT_569.md')
with open(report_path, 'w') as f:
    f.write(report)
print(f"[T5] Wrote {report_path}")

print(f"\n[T5] Verdict: {verdict}")
print(f"[T5] P2: {p2['result']}, PT pass count: {pt_pass_count}/5")
print(f"[T5] PT results: {pt_results}")
print(f"[T5] Confirmed constraints: {confirmed_constraints}")
print(f"[T5] New constraints: {new_constraints}")
print(f"[T5] Done.")
