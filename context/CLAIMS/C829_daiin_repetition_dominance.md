# C829: daiin Repetition Dominance

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_ROUTING_TOPOLOGY | **Scope:** A

## Finding

The token **daiin** accounts for **22.4% of all within-line repetitions** (80 of 357). As the CC trigger that initiates the B control loop (C816), daiin repetition may encode control-loop iteration count.

## Key Numbers

| Metric | Value |
|--------|-------|
| daiin repeats | 80 |
| Total repeats | 357 |
| daiin share | 22.4% |
| Next highest (chol) | 43 (12.0%) |
| daiin dominance ratio | 1.86x over #2 |

## Top Repeated Tokens

| Token | Count | MIDDLE | Known Function |
|-------|-------|--------|----------------|
| **daiin** | 80 | iin | CC trigger, control loop initiator (C816) |
| chol | 43 | ol | Common structural |
| chor | 12 | or | Kernel-adjacent |
| shol | 11 | ol | Common structural |
| s | 10 | s | Single-character primitive |
| or | 10 | or | Kernel transition |

## Extreme Examples

Lines with multiple daiin occurrences:

| Location | daiin count | Line content |
|----------|-------------|--------------|
| f89r2.3 | 4 | toy **daiin daiin daiin** ody qokeey cheoldy qody cheor s ain **daiin** oky cheody cheoky |
| f89r2.9 | 3 | **daiin** cheok okeol **daiin** dal dair qokeey okeol **daiin** ykeody okeeeo ees cheey ykeol cheo cheky |
| f101r1.8 | 4 | olaiin oteol chor oteey chokchey kor **daiin** shok chol chol qoky **daiin** ol s al ydar **daiin** or ory okeey **daiin** shea daiin okol chear |

## Interpretation

Given that:
- daiin initiates the control loop at position 0.413 (C816)
- daiin routes to CHSH lane at 90.8% (C817)
- daiin has zero forbidden transitions (C820)

Multiple daiin tokens in a single A record may specify **how many control cycles** the corresponding B procedure requires. This is consistent with:

- **C287-C290:** Repetition encodes instance multiplicity ("do this N times"), not arithmetic quantity
- **C469:** Parametric information encoded categorically, not numerically
- **C482:** B invariant to A line length - vocabulary determines viability, but repetition count may encode intensity parameters

## Proposed Functional Model

```
1x daiin = initiate 1 control cycle
2x daiin = initiate 2 control cycles
3x daiin = initiate 3 control cycles
4x daiin = initiate 4 control cycles (intensive procedure)
```

This maps to practical operations like multi-pass distillation, repeated heating cycles, or iterative purification steps.

## Tier Assessment

- **daiin dominance (22.4%):** Tier 2 (empirical fact)
- **Cycle count interpretation:** Tier 3 (plausible but not proven)

## Provenance

- Script: `phases/A_RECORD_B_ROUTING_TOPOLOGY/scripts/t9_repeat_function.py`
- Related: C816 (daiin control loop position), C817 (daiin lane routing), C820 (CC hazard immunity)
