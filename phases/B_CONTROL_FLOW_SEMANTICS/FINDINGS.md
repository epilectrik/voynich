# B_CONTROL_FLOW_SEMANTICS Findings

**Date:** 2026-01-29
**Status:** COMPLETE
**Tier:** 3 (Semantic Interpretation)

## Executive Summary

Currier B text encodes a **batch processing control system** with forward-biased state progression (59.2%), exception handling via FQ escape routes, and kernel-based (k/h/e) state transitions. The system tracks material through FL stages (INITIAL->TERMINAL) with monitoring checkpoints (LINK) and control markers (daiin/ol).

## Key Findings

### 1. Role Semantics

| Role | Share | Function | Key Feature |
|------|-------|----------|-------------|
| EN | 31.2% | State transition | 91.9% kernel, self-loops 38.5% |
| FL | 4.7% | Material state index | Kernel-free, 5 stages |
| FQ | 12.5% | Escape handler | 80.4% triggered by hazard |
| CC | 3.2% | Control markers | daiin=init, ol=continue |
| AX | 17.9% | Support/monitoring | Includes LINK checkpoints |

### 2. Kernel Semantics

Position ordering: **e (0.404) < h (0.410) < k (0.443)**

- 'e' = stability/setup (earliest)
- 'h' = alignment (middle)
- 'k' = activation (latest)

Most common combo: "he" (31.4%)

### 3. Control Flow Grammar

High-probability transitions:
- EN->EN (38.5%) - processing continues
- CC->EN (37.7%) - control triggers processing
- FQ->EN (29.5%) - escape recovers to processing

Escape pattern:
- FL->FQ (16.0%) - hazard state triggers escape

### 4. Process Domain

| Test | Result | Interpretation |
|------|--------|----------------|
| Forward bias | 59.2% | Moderately forward |
| Monotonic lines | 59.7% | Mostly orderly |
| Full loops | 1.7% | Rarely cyclic |
| Backward | 40.8% | Corrections allowed |

**Verdict:** Batch processing with correction capability

### 5. Section Variation

- BIO: Highest EN (40.1%) - intensive processing
- HERBAL_B: Highest FL/FQ - state-heavy
- FL/FQ ratio ~0.37 across sections (similar stability)

## Semantic Model

```
BATCH PROCESSING CONTROL SYSTEM
+------------------------------------------------------------------+
|  MONITORING      PROCESSING       STATE          ESCAPE           |
|     LINK    -->     EN      -->    FL     -->     FQ             |
|   (check)       (k/h/e ops)     (stage)      (if hazard)         |
|                     ^              |              |               |
|                     +--------------+--------------+               |
|                         (loop back to processing)                 |
+------------------------------------------------------------------+

Control injection: CC (daiin=init, ol=continue) -> EN

Kernel pattern: e-setup -> h-align -> k-activate
```

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C873 | Kernel Semantic Pattern | e<h<k positional ordering |
| C874 | CC Token Functions | daiin=init (0.370), ol=continue (0.461) |
| C875 | Escape Trigger Grammar | 80.4% from hazard FL stages |
| C876 | LINK Checkpoint Function | Position 0.405, routes to EN |
| C877 | Transition Grammar | EN self-loop 38.5%, CC->EN 37.7% |
| C878 | Section Program Variation | BIO=high EN, HERBAL_B=high FL/FQ |
| C879 | Process Domain Verdict | Batch processing, 59.2% forward |
| C880 | Integrated Control Model | See semantic model above |

## Confidence Assessment

- **HIGH:** Role distribution, transition grammar, FL stages, CC positions
- **MEDIUM:** Kernel semantics, escape triggers, LINK function
- **LOW:** Process domain labels, specific semantic interpretations

## Structural Provenance

Built on Tier 2 constraints: C467, C552, C770-C815, C788-C791, C804-C809, C855-C862

No contradictions with existing constraints found.
