# Phase: KERNEL_STATE_SEMANTICS

## Status: COMPLETED

## Objective

Determine what k, h, e kernel states actually represent empirically, without assuming the "hazard" interpretation.

---

## Executive Summary

**VERDICT: Two independent constraint layers exist.**

Tests T1-T6 showed that BETWEEN-TOKEN transitions of k, h, e are approximately uniform - no directional flow at the execution level. This initially appeared to contradict C521.

However, T7-T9 revealed the crucial distinction:

| Layer | What It Tests | Result |
|-------|---------------|--------|
| CONSTRUCTION (C521) | Within-token character bigrams | **CONFIRMED** - Strong asymmetry |
| EXECUTION | Between-token transitions | **UNIFORM** at character level |
| CLASS GRAMMAR | 49-class transitions | **REAL STRUCTURE** - ratios 0.20-7.31 |

**C521 is CORRECT. C522 is CORRECT.** The construction and execution layers are independent, as C522 states.

---

## The Two-Layer Discovery

### Layer 1: Construction (Within-Token)

C521 claims within-token directional asymmetry. T9 CONFIRMED all 5 claims:

| Transition | C521 Claim | Observed | Status |
|------------|------------|----------|--------|
| e->h | 0.00 (blocked) | 0.004 | **CONFIRMED** |
| h->k | 0.22 (suppressed) | 0.24 | **CONFIRMED** |
| e->k | 0.27 (suppressed) | 0.44 | **CONFIRMED** |
| h->e | 7.00x (elevated) | 6.09 | **CONFIRMED** |
| k->e | 4.32x (elevated) | 4.02 | **CONFIRMED** |

**This is a TOKEN-BUILDING GRAMMAR.** When constructing tokens, the ordering k -> h -> e is strongly preferred.

### Layer 2: Execution (Between-Token)

T1-T6 showed between-token transitions are uniform at the character level:

| Transition | Observed/Expected | Status |
|------------|-------------------|--------|
| All k,h,e pairs | 0.87 - 1.21 | NEUTRAL |

**Token-to-token transitions do NOT show k,h,e directional flow.**

### Layer 3: Class Grammar

T7 showed the 49-class grammar has REAL structure:

| Metric | Value |
|--------|-------|
| Ratio range | 0.20 - 7.31 |
| Disfavored pairs (ratio < 0.5) | 39 |
| Elevated pairs (ratio > 2.0) | 44 |
| Character-level ratio range | 0.87 - 1.21 |

**The grammar operates at CLASS level, not character level.**

---

## What The "Kernel" Actually Is

T8 showed k, h, e ARE special - but as **morphological building blocks**, not execution states:

### Position Within Token (Key Finding)

| Character | Mean Normalized Position |
|-----------|--------------------------|
| k | 0.356 (early) |
| h | 0.402 (middle) |
| e | 0.565 (late) |

ANOVA: F=250.4, p<0.0001 - positions are significantly different.

This matches C521's construction-level claims: tokens are BUILT in k -> h -> e order.

### Token Coverage

| Character | Token Coverage |
|-----------|----------------|
| k | 31.6% |
| h | 39.7% |
| e | 44.2% |

All are high-coverage morphological elements.

### Role Association

All three kernel characters are strongly associated with EN (Energy) role tokens:
- k tokens: 49.7% EN
- h tokens: 65.5% EN
- e tokens: 54.3% EN

---

## Test Results Summary

### Tests 1-6: Between-Token (Execution Layer)

| Test | Finding | Implication |
|------|---------|-------------|
| T1: Context Profiling | h has no distinct profile | No special "hazard" behavior |
| T2: Transition Ratios | All ratios 0.87-1.21 | Uniform transitions |
| T3: Post-Kernel Trajectory | No directional preference | No k->e or h->e bias |
| T4: Energy Flow Model | 1/4 criteria met | Energy interpretation weak |
| T5: Framing Fit | All framings score 0/5 | No interpretive framework fits |
| T6: Violation Analysis | 15.6% rate, no recovery | "Violations" are normal variation |

### Test 7: Class-Level Grammar

| Finding | Value |
|---------|-------|
| Ratio range | 0.20 - 7.31 (vs 0.87-1.21 char-level) |
| Disfavored pairs | 39 |
| Elevated pairs | 44 |
| Verdict | CLASS-LEVEL HAS REAL STRUCTURE |

### Test 8: Kernel Validity

| Finding | Value |
|---------|-------|
| Position ordering | k(0.356) -> h(0.402) -> e(0.565) |
| Coverage mean | 38.5% |
| Role association | Different distributions (chi2 p<0.05) |
| Evidence for | 3 |
| Evidence against | 2 |
| Verdict | Kernel is MORPHOLOGICAL, not EXECUTION |

### Test 9: Within-Token Transitions (C521 Validation)

| Finding | Value |
|---------|-------|
| C521 claims confirmed | 5/5 |
| e->h blocked | 0.004 ratio (< 0.1) |
| h->k suppressed | 0.24 ratio (< 0.5) |
| e->k suppressed | 0.44 ratio (< 0.5) |
| h->e elevated | 6.09 ratio (> 3.0) |
| k->e elevated | 4.02 ratio (> 2.0) |
| Verdict | C521 CONFIRMED for within-token |

---

## Critical Findings

### 1. C521 and C522 Are Correct

C521 (within-token asymmetry) is CONFIRMED by T9.
C522 (layers are independent) is CONFIRMED by T1-T6 vs T9 comparison.

The "contradiction" between C521 and our T1-T6 results was actually CONFIRMATION of C522's independence claim.

### 2. The "Kernel" Is Morphological

k, h, e form a **construction grammar** for how tokens are built:
- Position ordering: k early, h middle, e late
- Transition preferences: k->e and h->e strongly favored within tokens
- Blocking: e->h essentially forbidden within tokens

This is NOT an execution state machine.

### 3. Class-Level Grammar Is Real

The 49-class system shows genuine transition preferences (ratios 0.20-7.31) that don't exist at the k,h,e character level. The grammar operates at instruction class level.

### 4. "Hazard" Interpretation Needs Revision

The "hazard" framing conflated:
- **Construction constraints** (real, C521 confirmed)
- **Execution state machine** (not supported at character level)

The 17 "forbidden transitions" (C109) should be understood as CLASS-LEVEL constraints, not k,h,e character-level constraints.

---

## Implications for Constraints

### Constraints CONFIRMED

| Constraint | Status | Evidence |
|------------|--------|----------|
| C521 | CONFIRMED | T9: 5/5 claims validated |
| C522 | CONFIRMED | T1-T6 vs T9: layers independent |

### Constraints Requiring Clarification

| Constraint | Issue | Recommendation |
|------------|-------|----------------|
| C109 | "5 hazard failure classes" | Clarify as class-level, not k,h,e level |
| C110-C112 | Hazard topology | Specify operates at class level |
| C104 | h = PHASE_MANAGER | Reframe as morphological role |

### Terminology Revisions

For EXECUTION layer (between-token):

| Old Term | New Term |
|----------|----------|
| hazard state | disfavored class |
| escape | class transition |
| hazard avoidance | class preference |

For CONSTRUCTION layer (within-token):
- "kernel" terminology is APPROPRIATE
- k, h, e construction constraints are REAL

---

## Files Generated

| File | Content |
|------|---------|
| `results/t1_kernel_context_profiling.json` | Context profiles for k, h, e |
| `results/t2_disfavored_transition_decomposition.json` | Between-token transition ratios |
| `results/t3_post_kernel_trajectory.json` | Post-kernel trajectories |
| `results/t4_energy_flow_model.json` | Energy model test results |
| `results/t5_framing_fit_test.json` | Framing comparison |
| `results/t6_violation_context_analysis.json` | Violation analysis |
| `results/t7_class_level_transitions.json` | Class-level transition structure |
| `results/t8_kernel_validity_test.json` | Kernel validity assessment |
| `results/t9_within_token_transitions.json` | C521 validation |

---

## Summary Statement

**The Voynich Currier B text has a three-layer constraint system:**

1. **CONSTRUCTION (C521)**: Within-token character ordering (k -> h -> e) with strong directional preferences
2. **COMPATIBILITY (C475)**: MIDDLE-level class restrictions
3. **EXECUTION (C109)**: Class-level transition preferences operating on 49 instruction classes

The "kernel" (k, h, e) is real but operates at the CONSTRUCTION layer (morphology), not the EXECUTION layer (token-to-token flow). The original "hazard" interpretation incorrectly projected construction-level constraints onto execution-level behavior.
