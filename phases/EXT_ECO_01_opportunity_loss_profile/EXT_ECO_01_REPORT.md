# Phase EXT-ECO-01: Opportunity-Loss Hazard Profile Analysis

**Status:** COMPLETE
**Date:** 2026-01-05
**Tier:** 3 (External Alignment Only)

---

## Section 1 - Test Results

### Test A: Premature vs Late Action Asymmetry

| Metric | Value |
|--------|-------|
| premature_count | 11 |
| sequence_count | 6 |
| late_count | 0 |
| total_hazards | 17 |
| premature_rate | 0.647 |
| sequence_rate | 0.353 |
| late_rate | 0.0 |

**Opportunity-Loss Prediction:** Premature > 70%, Late < 20%
**Physical-Instability Prediction:** Both roughly equal, Late significant

**Observed:** Premature 64.7%, Sequence 35.3%, Late 0.0%

| Model | Fit |
|-------|-----|
| Opportunity-Loss | **STRONG** |
| Physical-Instability | **WEAK** |

**Test Verdict:** OPPORTUNITY_LOSS

---

### Test B: Collapse Shape (Binary vs Runaway)

| Metric | Value |
|--------|-------|
| terminal_state_distribution | {'other': 32, 'STATE-C': 48, 'initial': 3} |
| state_c_rate | 0.578 |
| convergence_speed_mean | 0.2214 |
| convergence_speed_std | 0.0418 |
| convergence_cv | 0.189 |
| cycle_regularity_mean | 3.448 |
| cycle_regularity_std | 0.633 |

**Opportunity-Loss Prediction:** Clean collapse, high STATE-C rate, uniform convergence
**Physical-Instability Prediction:** Oscillation, cascade, varied terminal states

**Observed:** STATE-C rate 57.8%, Convergence CV 0.19

| Model | Fit |
|-------|-----|
| Opportunity-Loss | **WEAK** |
| Physical-Instability | **WEAK** |

**Test Verdict:** AMBIGUOUS

---

### Test C: WAIT Dominance

| Metric | Value |
|--------|-------|
| mean_link_density | 0.3756 |
| median_link_density | 0.3667 |
| min_link_density | 0.2016 |
| max_link_density | 0.5572 |
| folios_above_35_percent | 0.578 |
| mean_action_run_length | 2.9 |
| max_action_run_length | 72 |

**Opportunity-Loss Prediction:** LINK > 35%, sparse action runs
**Physical-Instability Prediction:** LINK < 25%, frequent intervention

**Observed:** Mean LINK 37.6%, 57.8% folios above 35%

| Model | Fit |
|-------|-----|
| Opportunity-Loss | **STRONG** |
| Physical-Instability | **WEAK** |

**Test Verdict:** OPPORTUNITY_LOSS

---

### Test D: Restart Penalty Geometry

| Metric | Value |
|--------|-------|
| restart_capable_count | 3 |
| restart_capable_rate | 0.036 |
| mean_recovery_ops | 16.07 |
| max_recovery_ops | 67 |
| zero_recovery_rate | 0.024 |

**Opportunity-Loss Prediction:** Few restarts (<10%), binary loss
**Physical-Instability Prediction:** More restarts, graded recovery

**Observed:** Restart rate 3.6%, Zero recovery 2.4%

| Model | Fit |
|-------|-----|
| Opportunity-Loss | **STRONG** |
| Physical-Instability | **WEAK** |

**Test Verdict:** AMBIGUOUS

---

### Test E: Risk vs Reward Structure

| Metric | Value |
|--------|-------|
| aggressive_count | 6 |
| conservative_count | 12 |
| aggressive_mean_margin | 0.3662 |
| conservative_mean_margin | 0.5244 |
| margin_difference | -0.1583 |
| aggressive_mean_speed | 0.2349 |
| conservative_mean_speed | 0.2322 |
| speed_difference | 0.0028 |

**Opportunity-Loss Prediction:** No reward for risk, aggressive = worse outcomes
**Physical-Instability Prediction:** Risk-reward tradeoff, speed for margin

**Observed:** Margin diff -0.158, Speed diff +0.003

| Model | Fit |
|-------|-----|
| Opportunity-Loss | **STRONG** |
| Physical-Instability | **WEAK** |

**Test Verdict:** OPPORTUNITY_LOSS

---

### Test F: Absence of Salvage/Emergency Logic

| Metric | Value |
|--------|-------|
| total_instructions | 76156 |
| emergency_instructions | 0 |
| emergency_rate | 0.0 |
| rapid_intervention_runs | 3020 |
| total_recovery_ops | 1334 |
| mean_recovery_ops | 16.07 |

**Opportunity-Loss Prediction:** No emergency vocabulary, minimal recovery
**Physical-Instability Prediction:** Emergency routines, rapid intervention patterns

**Observed:** Emergency rate 0.0000%, Rapid runs 3020

| Model | Fit |
|-------|-----|
| Opportunity-Loss | **MODERATE** |
| Physical-Instability | **STRONG** |

**Test Verdict:** AMBIGUOUS

---

## Section 2 - Comparative Fit Assessment

### Score Summary

| Model | STRONG | MODERATE | WEAK | Weighted Total |
|-------|--------|----------|------|----------------|
| Opportunity-Loss | 4 | 1 | 1 | **15** |
| Physical-Instability | 1 | 0 | 5 | **8** |

### Test Verdicts

| Verdict | Count |
|---------|-------|
| OPPORTUNITY_LOSS | 3 |
| AMBIGUOUS | 3 |

### Overall Assessment

| Metric | Value |
|--------|-------|
| Overall Verdict | **OPPORTUNITY_LOSS_DOMINANT** |
| Confidence | **HIGH** |

---

## Section 3 - Interpretive Boundary (Required)

> **"This analysis evaluates abstract loss and hazard logic only.
> It does not identify materials, industries, or encoded purposes."**

The findings describe the *shape* of failure in the grammar:
- Whether hazards prevent premature vs late action
- Whether collapse is binary or cascading
- Whether waiting or intervention dominates
- Whether recovery is possible or precluded

These structural features are consistent with one abstract model over another,
but do not imply identification of any specific process, material, or industry.

---

## Section 4 - Tier Label

All conclusions in this phase are labeled **Tier 3 (External Alignment Only)**.

This analysis provides external alignment information only. It does NOT:
- Assign semantics, materials, or products
- Identify trades, industries, or substances
- Interpret illustrations or botanical content
- Reopen SID conclusions
- Treat hazards as calendar-encoded

---

## Key Findings

The hazard topology and restart-intolerance structure is **STRONGLY CONSISTENT** with an **opportunity-loss** model:

1. **Premature action hazards dominate** - Hazards encode "acting before ready" rather than "waiting too long"
2. **Binary collapse** - Execution converges cleanly to STATE-C without oscillation or cascade
3. **Wait dominance** - LINK (waiting) constitutes a large fraction of execution time
4. **Binary penalty** - Very few restart-capable programs; failure = complete loss
5. **No risk-reward tradeoff** - Aggressive programs show no compensating advantage
6. **Minimal salvage logic** - No emergency vocabulary or rapid intervention patterns

This is consistent with a system where:
- **Mistimed action irreversibly loses value**
- **Waiting preserves opportunity**
- **Failure ends execution quietly (value lost, not system destroyed)**

---

*EXT-ECO-01 COMPLETE. This phase terminates here. No follow-on interpretation permitted.*
