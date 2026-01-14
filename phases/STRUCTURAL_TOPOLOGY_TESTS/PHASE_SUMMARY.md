# Phase: STRUCTURAL_TOPOLOGY_TESTS

## Summary

**Purpose:** Exploit historical matching insights to generate internal structural tests against Tier 0-2 constraints.

**Status:** COMPLETED
**Tests Run:** 7/7
**Significant Findings:** 6/7 (one partial)

---

## Results Overview

| Test | Question | Verdict | Significance |
|------|----------|---------|--------------|
| 1. M-C Gap | Why does system need STABLE+DISTINCT? | **SIGNIFICANT_ANOMALY** | M-C is 0% in C/S zones, 26.3% in P-zone |
| 2. Forbidden Strategies | Are strategies categorically impossible? | **CATEGORICAL_BOUNDARY** | 17 programs (20.5%) have AGGRESSIVE=0% |
| 3. Phase Transitions | What marks phase transitions? | **STRONG_MARKERS** | HT step=-0.38 (p<1.2e-6); escape gradient 5.3%→0% |
| 4. OPPORTUNISTIC | What distinguishes judgment-critical programs? | **JUDGMENT_AXIS** | High qo_density, low LINK, high recovery |
| 5. Compatibility Pedagogy | Does topology govern A ordering? | **TOPOLOGY_CONSTRAINED** | 22.3% hub savings, front-loaded bridges |
| 6. PREFIX Bias | Do control-flow roles show positional bias? | **PARTIALLY_CONFIRMED** | Line-level confirmed; program-level needs testing |
| 7. Irrecoverability | Is irrecoverability by design? | **DESIGN_FEATURE** | Multiple converging barriers |

---

## Key Findings

### Test 1: M-C Gap Investigation

**M-C (stable, distinct) shows unique zone restriction:**

| Zone | M-C | Baseline | Status |
|------|-----|----------|--------|
| C | **0.0%** | 13.7% | ABSENT |
| P | **26.3%** | 13.7% | 2× CONCENTRATED |
| R | 7.2% | 13.7% | Reduced |
| S | **0.2%** | 13.7% | ABSENT |

**Interpretation:** M-C may represent "classification invariants" - reference conditions introduced early (P-zone) but not present at initialization (C) or final output (S).

### Test 2: Forbidden Strategy Boundaries

**CONSERVATIVE_WAITING archetype (17 folios) has AGGRESSIVE = 0.000:**

| Defining Property | Threshold |
|-------------------|-----------|
| link_density | > 0.404 |
| waiting_profile | HIGH/EXTREME |
| intervention_style | CONSERVATIVE |

**Interpretation:** This is a CATEGORICAL prohibition boundary, matching historical "4th degree" (forbidden, not just inadvisable).

### Test 3: Phase Transition Markers

**Multiple grammatical markers identified:**

| Marker | Signal | p-value |
|--------|--------|---------|
| HT step change | -0.385 at AZC entry | < 1.2e-6 |
| R-series escape | 5.3% → 1.84% → 0% | < 0.0001 |
| LINK distribution | Monitoring→intervention boundary | Documented |
| C vs S asymmetry | Jaccard = 0.073 | < 0.001 |

**Interpretation:** Grammar encodes "signs of change" - phase transition markers matching historical heads/hearts/tails.

### Test 4: OPPORTUNISTIC Program Structure

**Judgment-critical programs characterized by:**

| Feature | OPPORTUNISTIC-High | OPPORTUNISTIC-Low |
|---------|-------------------|-------------------|
| qo_density | > 0.181 | < 0.123 |
| recovery_ops | > 19 | < 8 |
| link_density | < 0.342 | > 0.404 |
| HT density | LOW | HIGH |

**Interpretation:** OPPORTUNISTIC is a third axis beyond cautious/aggressive - "skillful timing" programs with escape infrastructure instead of monitoring infrastructure.

### Test 5: Compatibility-Driven Pedagogy

**A-registry ordering serves graph navigation:**

| Finding | Evidence |
|---------|----------|
| 95.7% MIDDLE incompatibility | Sparse navigation problem |
| 21 hub MIDDLEs | Bridges between regions |
| 22.3% hub savings | Strategic rationing |
| Front-loaded novelty (21.2%) | Bridges introduced early |

**Interpretation:** Ordering is topology-constrained, not just memory-optimized. A-registry implements "graph navigation pedagogy."

### Test 6: PREFIX Positional Bias

**Line-level grammar confirmed (C371, C375):**
- Line-initial: so (6.3x), ych (7.0x), pch (5.2x)
- Line-final: lo (3.7x), al (2.7x)

**Program-level gradient:** Not yet tested (requires further analysis).

### Test 7: Irrecoverability Audit

**Multiple converging barriers to identity recovery:**

| Barrier | Mechanism |
|---------|-----------|
| Zone-material orthogonality | Can't infer identity from placement |
| 95.7% MIDDLE incompatibility | Can't infer from co-occurrence |
| M-C gap | Can't map to external classification |
| Layer transitions | One-way information loss |
| No A-B coupling (C384) | Can't bypass decision grammar |

**Interpretation:** Irrecoverability is architectural, not accidental. The system is designed so identity cannot be recovered.

---

## Success Criteria Assessment

| Criterion | Status |
|-----------|--------|
| At least 4/7 tests significant | ✓ (6/7) |
| No contradiction of Tier 0-2 | ✓ |
| New Tier 3 hypotheses generated | ✓ (4 proposed) |
| M-C shows distinguishing property | ✓ (zone restriction) |
| Phase transitions have markers | ✓ (5 identified) |

**Phase Status:** SUCCESS

---

## Constraint Disposition (Expert Reviewed)

| # | Constraint | Disposition | Rationale |
|---|------------|-------------|-----------|
| **C490** | Categorical Strategy Exclusion | **PROMOTED to Tier 2** | Grammar-level exclusion, categorical not gradient |
| C491 | Judgment-Critical Program Axis | Tier 3 (speculative) | Interpretive label, not grammar invariant |
| **C492** | PREFIX Phase-Exclusive Legality | **PROMOTED to Tier 2** | Hard legality exclusion, invariant under frequency |
| C493 | Architectural Irrecoverability | NOT ADDED | Already implied by C384, C475, C383, C469 |

### Expert Guidance Applied

- **C490:** Reframed as pure grammar property ("no grammar-compatible realization exists")
- **C492:** Reframed as pure legality constraint (avoid "stable but distinct" interpretation)
- **C491:** Kept Tier 3 because "judgment-critical" is interpretive, not necessary
- **C493:** Recognized as synthesis insight, not new atomic fact (avoid double-counting)

### Interpretive Note on Irrecoverability

*Multiple independent Tier 2 constraints jointly enforce architectural irrecoverability; no single mechanism is responsible:*
- C384 (No entry-level A-B coupling)
- C475 (Atomic MIDDLE incompatibility)
- C383 (Global type system without semantics)
- C469 (Categorical resolution principle)
- Zone-material orthogonality

---

## Epistemic Status

All findings remain **Tier 3-4 exploratory**:

- Strengthen interpretive plausibility
- Generate testable structural hypotheses
- Do NOT enable semantic decoding
- Do NOT promote to Tier 2 without corroboration

---

## Files Generated

| File | Test | Verdict |
|------|------|---------|
| `phase_specification.md` | - | Pre-registration |
| `mc_gap_analysis.md` | 1 | SIGNIFICANT_ANOMALY |
| `forbidden_strategy_boundaries.md` | 2 | CATEGORICAL_BOUNDARY |
| `phase_transition_markers.md` | 3 | STRONG_MARKERS |
| `opportunistic_structure.md` | 4 | JUDGMENT_AXIS |
| `compatibility_pedagogy.md` | 5 | TOPOLOGY_CONSTRAINED |
| `prefix_positional_bias.md` | 6 | PARTIALLY_CONFIRMED |
| `irrecoverability_audit.md` | 7 | DESIGN_FEATURE |

---

## Connection to Historical Matching

This phase exploited HISTORICAL_STRUCTURAL_MATCHING_II findings:

| Historical Finding | Structural Test | Result |
|-------------------|-----------------|--------|
| Tria prima maps to 3/4 classes | M-C gap investigation | M-C is zone-restricted invariant |
| 4th degree fire is FORBIDDEN | Strategy boundaries | Categorical prohibition confirmed |
| Heads/hearts/tails grammar | Phase transition markers | 5 markers identified |
| "Skillful operator" | OPPORTUNISTIC structure | Judgment axis characterized |
| Ars memoria ordering | Compatibility pedagogy | Topology constrains ordering |

---

## Recommended Follow-Up

1. **Test PREFIX × program-position gradient** (Test 6 completion)
2. **Characterize M-C entries in detail** (what do they represent?)
3. **Map OPPORTUNISTIC programs to HT behavior** (deeper analysis)
4. **Test irrecoverability quantitatively** (entropy measurements)

---

*Phase completed 2026-01-13*
