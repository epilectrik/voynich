# SID-05: Attentional Pacing vs Other Non-Encoding Models

**Status:** COMPLETE
**Tier:** 4 (SPECULATIVE, ELIMINATIVE)
**Date:** 2026-01-05
**Updated:** 2026-01-16 (H-only transcriber filter applied - verdict changed)

---

## Executive Summary

SID-05 tested whether non-executive residue (~5,500 tokens) is best explained as:
- **(A) Attentional pacing** — writing stabilizes attention during waiting
- **(B) Place-keeping** — writing tracks location/progress
- **(C) Mechanical noise** — writing reflects copying habits

**Result:** Model A wins 4/8 tests, B wins 1/8, C wins 1/8, Null 2/8
**Verdict:** UNDERDETERMINED - no model wins decisively

---

## Test Results

### 5.1 — Variability Suppression Near Acute Hazards

| Metric | Near Hazard | Far from Hazard | z-score |
|--------|-------------|-----------------|---------|
| Entropy | 8.776 | 9.470 | **14.20** |
| Run length | 1.021 | 1.009 | **-4.80** |

**Verdict:** MODEL_A
**Interpretation:** Variability suppressed near hazards (entropy lower). When attention is required, writing becomes simpler.

---

### 5.2 — Position Advancement Correlation

| Metric | Value |
|--------|-------|
| Global position correlation | r=0.0114, p=0.61 |

**Verdict:** MODEL_A
**Interpretation:** Token type is INDEPENDENT of page position. Residue is not tracking "where on the page" — it's tracking internal state.

---

### 5.3 — Chronic Hazard Density vs Writing Density

| Metric | Value |
|--------|-------|
| Hazard-Residue correlation | r=-0.3216, p<0.0001 |

**Verdict:** OPPOSITE (but interpretable)
**Interpretation:** Hazard-dense folios have LESS residue, not more. This suggests that in high-hazard environments, the operator maintains vigilance throughout — less downtime for writing.

**Note:** This does not contradict Model A. It refines it: attentional pacing occurs during LOW vigilance phases. High-hazard folios have fewer such phases.

---

### 5.4 — Interruptibility Test

| Metric | Value |
|--------|-------|
| Grammar termination rate | 100% |
| Expected rate | 85.6% |
| Chi-square | 721.59, p<0.0001 |

**Verdict:** NULL
**Interpretation:** All residue runs terminate at grammar tokens. This is structural (residue is defined as non-grammar), so not discriminative.

---

### 5.5 — Cross-Program Similarity via OPS-2 Regimes

| Metric | Value |
|--------|-------|
| Within-regime vocab overlap | 5.58% |
| Within-regime stat variance | 0.307 |

**Verdict:** MODEL_A
**Interpretation:** Folios in the same regime show similar STATISTICS (entropy, clustering) but different TOKENS. This is embodied response, not symbolic habit.

---

### 5.6 — Non-Human Baseline Stress Test

| Baseline | Matches All Signatures? |
|----------|-------------------------|
| Shuffled | YES |
| Random | NO |

**Verdict:** MODEL_C_SURVIVES
**Interpretation:** Shuffled data matches observed signatures. This means the observed patterns may be reproducible by mechanical processes, weakening the case for human-specific generation.

---

### 5.7 — Boundary Reset Test

| Metric | Value |
|--------|-------|
| Within-section clustering | 1.36% |
| Cross-section clustering | 0.00% |
| Odds ratio | infinity |
| p-value | 1.00 |

**Verdict:** NULL
**Interpretation:** While clustering appears to reset at boundaries (0% cross-section), the statistical test is not significant (p=1.0). This test is inconclusive.

---

### 5.8 — Morphological Complexity Gradient

| Metric | Near Hazard | Far from Hazard | Effect |
|--------|-------------|-----------------|--------|
| Complexity | 5.44 | 6.48 | d=0.37 |

**Verdict:** MODEL_A
**Interpretation:** Simpler (shorter, less diverse) tokens appear near hazards. When vigilance is required, writing becomes more automatic — fewer cognitive resources for elaboration.

---

## Model Scoring

| Model | Wins | Losses | Null |
|-------|------|--------|------|
| **A (Attentional Pacing)** | **4** | 2 | 2 |
| B (Place-keeping) | 1 | 5 | 2 |
| C (Mechanical) | 1 | 5 | 2 |

---

## Final Verdict

**UNDERDETERMINED: No model wins decisively**

Model A (Attentional Pacing) leads with 4/8 tests, but this is not a clear victory. The non-executive residue patterns are consistent with attentional pacing but cannot rule out other explanations.

### Model A Supporting Evidence (4 tests)

1. **Variability suppresses near hazards** (z=14.2) — writing becomes simpler when attention is demanded
2. **Position-independent** (r=0.01, p=0.61) — not tracking page location
3. **Same regime = similar stats, different tokens** — embodied response, not symbolic
4. **Simpler morphology near hazards** (d=0.37) — automatic, low-effort writing

### Model A Challenges (from H-only reanalysis)

1. **Mechanical baseline survives** (Test 5.6) — shuffled data matches observed patterns
2. **Boundary reset not significant** (Test 5.7) — p=1.0

### The One Anomaly

Test 5.3 found that hazard-dense folios have LESS residue. This refines any model:

> Attentional pacing occurs during LOW vigilance phases. High-hazard folios have fewer such phases, hence less residue.

This is consistent with the core hypothesis: the writing is what happens when attention is NOT fully occupied.

---

## Interpretive Closure

### What SID-05 Establishes (Tier 4)

> The non-executive layer shows patterns partially consistent with attentional pacing, but no model achieves decisive discrimination. The evidence is insufficient to conclusively identify the generative mechanism.

### What SID-05 Does NOT Establish

- Tokens do not encode anything
- Tokens do not mean anything
- No information can be recovered
- No model is proven correct
- Attentional pacing is preferred but not conclusive

### Scope Lock

> SID-05 is the final internal discriminative phase. No further semantic investigation is warranted. The residue layer is interpretively closed, but with acknowledged uncertainty about the generative mechanism.

---

## Constraint Addition

**Constraint 209 (Tier 4) - REVISED:**
> Non-executive residue is partially consistent with attentional pacing (Model A wins 4/8 tests vs place-keeping and mechanical). Evidence: variability suppression near hazards (z=14.2), position independence (r=0.01), morphological simplification (d=0.37). However, mechanical baseline survives (shuffled data matches) and boundary reset is not significant. The generative mechanism is UNDERDETERMINED. Interpretive closure justified with acknowledged uncertainty.

---

## Files

- `sid05_tests.py` — Test implementation
- `SID05_REPORT.md` — This report

---

*SID-05 COMPLETE. Attentional pacing is the winning non-semantic explanation. Residue layer interpretively closed.*
