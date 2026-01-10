# Human Track Constraints (C166-C172, C341-C348, C404-C406, C413-C419)

> **Quick reference:** [HT_CONTEXT_SUMMARY.md](HT_CONTEXT_SUMMARY.md) (context-sufficient)
> **Formal hierarchy:** [HT_HIERARCHY.md](HT_HIERARCHY.md) (CANONICAL)

**Scope:** HT layer structure, behavior, non-operational status
**Status:** CLOSED

---

## Structural Properties (C166-C172)

### C166 - Zero Forbidden Seam Presence
**Tier:** 2 | **Status:** CLOSED
0/35 HT tokens appear at forbidden transition boundaries.
**Source:** UTC

### C167 - 80.7% Section-Exclusive
**Tier:** 2 | **Status:** CLOSED
Most HT tokens appear in only one section.
**Source:** MCS

### C168 - Single Unified Layer
**Tier:** 2 | **Status:** CLOSED
HT forms one coherent layer, not multiple overlapping systems.
**Source:** NESS

### C169 - Hazard Avoidance
**Tier:** 2 | **Status:** CLOSED
HT tokens average 4.84 distance from hazards (vs 2.5 expected).
**Source:** UTC

### C170 - Morphologically Distinct
**Tier:** 2 | **Status:** CLOSED
HT tokens are statistically distinct from grammar tokens (p<0.001).
**Source:** UTC

### C172 - SUPERSEDED
**Tier:** 2 | **Status:** SUPERSEDED
Original "99.6% LINK-proximal" claim superseded by C342.
**Source:** HTD

---

## Program Stratification (C341-C342)

### C341 - HT-Program Stratification
**Tier:** 2 | **Status:** CLOSED
HT density varies by waiting profile: EXTREME 15.9% > HIGH 10.4% > MODERATE 8.5% > LOW 5.7%. Kruskal-Wallis p < 0.0001.
**Source:** HTD

### C342 - HT-LINK Decoupling
**Tier:** 2 | **Status:** CLOSED
HT density independent of LINK density at folio level (ρ=0.010, p=0.93). "More LINK = more random mark-making" is FALSIFIED.
**Source:** HTD

---

## Morphology and Synchrony (C347-C348)

### C347 - Disjoint Prefix Vocabulary
**Tier:** 2 | **Status:** CLOSED
HT prefixes (yk-, op-, yt-, sa-, etc.) have ZERO overlap with A/B prefixes (ch-, qo-, sh-, etc.). 71.3% of HT types decompose into HT_PREFIX + MIDDLE + SUFFIX. Third formal layer, not scribal noise.
**Source:** HT-MORPH

### C348 - Phase Synchrony
**Tier:** 2 | **Status:** CLOSED
HT prefixes are phase-synchronized: EARLY (op-, pc-, do-), LATE (ta-). Grammar synchrony V=0.136 (p<0.0001). Regime association V=0.123.
**Source:** HT-STATE

---

## Closure Tests (C404-C406)

### C404 - Terminal Independence
→ See [C404_ht_non_operational.md](C404_ht_non_operational.md)

### C405 - Causal Decoupling
**Tier:** 2 | **Status:** CLOSED
HT presence doesn't alter subsequent grammar probabilities. Chi2 significant but V=0.10 (negligible). HT has no advisory role.
**Source:** HTC

### C406 - Generative Structure
**Tier:** 2 | **Status:** CLOSED
HT follows Zipf distribution (exponent 0.892, R²=0.92) with 67.5% hapax rate. Consistent with productive compositional system.
**Source:** HTC

### C413 - Grammar Trigger
→ See [C413_ht_grammar_trigger.md](C413_ht_grammar_trigger.md)

---

## Correlation vs Prediction (C414-C418)

### C414 - Strong Grammar Association
**Tier:** 2 | **Status:** CLOSED
HT tokens show extremely strong statistical associations with surrounding grammar context (chi2=934 for prefix vs. local grammar distribution, p<10^-145). Confirms HT is NOT noise and IS grammar-synchronized.
**Source:** HT-INFO

### C415 - Non-Predictivity
**Tier:** 1 | **Status:** CLOSED (FALSIFICATION)
HT tokens do NOT improve prediction of subsequent line content or grammar composition. Models conditioned on HT perform no better (and often worse) than baseline. MAE worsens by 0.003-0.005.
**Decisively rules out:** functional annotation, metadata encoding, Currier-A-like classification.
**Source:** HT-INFO

### C416 - Directional Asymmetry (Quantified)
**Tier:** 2 | **Status:** CLOSED
Grammar->HT influence: Cramer's V=0.324 (strong). HT->Grammar influence: V=0.202 (weak). Ratio: 1.6x stronger forward. Coupling is strictly unidirectional.
**Source:** HT-INFO

### C417 - Modular Additive Structure
**Tier:** 2 | **Status:** CLOSED
HT subcomponents (prefix/core/suffix) carry independent, additive signal with NO interaction or synergy. Permutation test p=1.0 for synergy. Interaction model performs 3.9% WORSE than additive.
**Source:** HT-INFO

### C418 - Positional Specialization Without Informativeness
**Tier:** 2 | **Status:** CLOSED
HT displays consistent positional biases (core 'd'=69.6% line-initial, 'am'=52.8% line-final). But these biases do NOT encode recoverable information about content.
**Source:** HT-INFO

---

## System-Specific Patterns (C419)

### C419 - HT Positional Specialization in Currier A
**Tier:** 2 | **Status:** CLOSED

> In Currier A, HT tokens exhibit strong and systematic **entry-boundary-aligned positional bias**, distinct from Currier B.

**Evidence:**
- HT is enriched 2.61× at **line-initial positions** (p < 10⁻¹²⁶)
- Simplex forms (notably `d`) are enriched at **line-final positions** (55.8%)
- HT shows **zero occurrence at category transition seams** (0 / 4,486)
- HT morphology in A favors `-or/-ol`, distinct from B's `-edy`
- HT shows **weak category correlation** (Cramér's V = 0.130), significantly above B but still non-predictive

**Constraint:**
> HT in Currier A is **structurally aligned with entry boundaries and registry layout**, while remaining *non-operative* and *non-determinative* of category assignment.

**Notes:**
- HT does *not* define entries, categories, or repetition
- HT remains fully removable without altering registry structure
- This contrasts with Currier B, where HT aligns with temporal/attentional context and shows zero predictivity

**Source:** HT-A

---

## AZC-Specific Patterns (HT-AZC-NOTE-01)

### HT-AZC-NOTE-01: Third Anchoring Pressure (Diagram Labels)
**Status:** OBSERVATION | **Source:** HT-AZC (2026-01-09)

AZC HT shows a distinct pattern from both A and B:

| Metric | Currier A | Currier B | AZC |
|--------|-----------|-----------|-----|
| Line-initial enrichment | 2.61× | ~2× | 1.7× |
| Line-final enrichment | LOW | LOW | 1.35× (unique) |
| HT density | 5.5% | 3.76% | 6.5% |
| Simplex rate | 13.9% | 14.5% | 23.7% |

**Key finding:** AZC uniquely shows BOTH line-initial AND line-final enrichment.

**Mechanism:** Driven by L-placement (label/marginalia) text:
- L-placement: 88.8% initial, 95% final (almost ALL at boundaries)
- L-placement lines are short (1-3 tokens)
- HT density by line length: Short 15.1% > Medium 8.0% > Long 5.9%
- Single-token lines: 41.7% HT rate (5/12)

**Interpretation:** In AZC diagrams, HT concentrates in short label text, appearing at both boundaries because the lines are inherently short. This constitutes a **third anchoring pressure** distinct from:
- A: Registry layout (entry boundaries)
- B: Temporal/attentional context (execution phase)
- AZC: Diagram geometry (label positions)

**Note:** Sample sizes are modest (L-placement: 80 HT tokens). Pattern is clear but may refine with larger analysis.

---

## AAZ Coordination (C344)

### C344 - HT-A Inverse Coupling
**Tier:** 2 | **Status:** CLOSED
HT density negatively correlates with A-vocabulary reference (rho=-0.367, p<0.001). High-HT programs use LESS registry vocabulary. HT tracks cognitive spare capacity.
**Source:** AAZ

---

## Interpretation Summary

| Claim | Tier |
|-------|------|
| HT is a formal layer | 2 (proven) |
| HT is non-operational | 2 (proven) |
| HT is structured but non-predictive | 2 (proven, C414-C418) |
| HT in A = layout-synchronous practice | 3 (interpretation, C419) |
| HT in B = phase/attention-synchronous practice | 3 (interpretation) |
| **HT = dual-purpose attention + training mechanism** | 3 (interpretation) |
| HT = random doodling/scribbling | 1 (falsified, too much structure) |
| HT = functional annotation | 1 (falsified, C415) |

---

## Frozen Summary Statement

> **HT is a structured, modular, and grammar-responsive human-generated notation layer that exhibits strong contextual correlation but no predictive or causal influence on system behavior.**

This statement survived all tests in the HT-INFO exploration cycle.

**Tier 3 Interpretation:** HT functions as a **dual-purpose attention mechanism**:
1. Maintained operator attention/alertness during waiting phases
2. Trained guild members in the art of the written form

This is NOT "doodling" or "scribbling" - the evidence (3.29x rare grapheme engagement, 28.5% boundary-pushing forms, systematic family rotation) shows deliberate skill acquisition.

**System-specific refinement:** HT shows **three distinct anchoring pressures**:
- Currier A: Registry layout (entry boundaries)
- Currier B: Temporal/attentional context (execution phase)
- AZC: Diagram geometry (label positions)

Same layer, same non-operational status, same dual-purpose function, different structural alignment by text type.

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
