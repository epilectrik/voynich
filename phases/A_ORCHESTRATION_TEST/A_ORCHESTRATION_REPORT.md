# A-Orchestration Hypothesis Test

**Phase:** A_ORCHESTRATION_TEST
**Date:** 2026-01-19
**Status:** COMPLETE - FALSIFIED

---

## Hypothesis

Within a multi-token Currier A entry, token ORDER may encode a trajectory through B programs (REGIMEs).

**Model:**
```
A entry: [token1] [token2] [token3]
           ↓         ↓         ↓
        REGIME_2  REGIME_3  REGIME_4
         (gentle)  (medium)  (intense)
```

**Prediction:** Early position → lower REGIME ordinal, late position → higher REGIME ordinal.

---

## Test Design

1. Identify multi-token A entries (3+ tokens per line)
2. For each token, find B folios where that vocabulary appears
3. Get REGIME ordinal of those B folios (1=gentle, 4=aggressive)
4. Compute Kendall's tau: position vs mean REGIME ordinal
5. Control: shuffle positions within entries, re-run

---

## Results

### Data Summary

| Metric | Value |
|--------|-------|
| Multi-token A entries (3+) | 1,521 |
| Total tokens in entries | 11,322 |
| Average entry length | 7.4 tokens |
| A tokens appearing in B | 33.6% |
| Data points for correlation | 8,421 |

### Position-REGIME Correlation

| Metric | Value |
|--------|-------|
| **Kendall's tau** | **0.0255** |
| p-value | 0.000989 |

**Interpretation:** Statistically significant but practically meaningless. A tau of 0.025 indicates essentially no relationship.

### Position-wise Breakdown

| Position | Mean Ordinal | N | Std |
|----------|-------------|---|-----|
| 1 | 2.408 | 970 | 0.530 |
| 2 | 2.446 | 1185 | 0.436 |
| 3 | 2.440 | 1153 | 0.452 |
| 4 | 2.463 | 1117 | 0.401 |
| 5 | 2.446 | 951 | 0.414 |
| 6 | 2.442 | 803 | 0.422 |
| 7 | 2.451 | 692 | 0.423 |
| 8 | 2.486 | 531 | 0.374 |
| 9 | 2.456 | 382 | 0.401 |
| 10 | 2.486 | 226 | 0.373 |

**Key observation:** All positions have mean ordinals between 2.40-2.49 - a range of only 0.08 on a 1-4 scale. This is effectively flat.

### Permutation Test

| Metric | Value |
|--------|-------|
| Null distribution mean | -0.0017 |
| Null distribution std | 0.0069 |
| 95th percentile | 0.0096 |
| Observed tau | 0.0255 |
| Permutation p-value | 0.0010 |

The observed tau is ~3.7 standard deviations from the null, but the absolute effect size is negligible.

---

## Verdict: FALSIFIED

**Token position within A entries does NOT encode REGIME trajectory.**

### Evidence

1. **Tau = 0.0255** - Below the pre-registered threshold of 0.15
2. **Position-wise means are flat** - Range of only 0.08 across 10 positions
3. **No escalation pattern** - Position 1 (2.408) vs Position 10 (2.486) is negligible

### Implications

- **C234 (POSITION_FREE) is reinforced** - Position truly carries no meaningful information
- **C482 (batch semantics) remains valid** - A entries don't encode ordered operands
- **SEL-F falsification stands** - Neither internal (B→B) nor external (A→B) chaining exists

---

## Refinement Test: Non-Monotonic Differentiation

The initial test assumed monotonic escalation (gentle → intense). A refinement tested whether positions simply have DIFFERENT REGIME distributions, regardless of order.

### Results

| Test | Value | Interpretation |
|------|-------|----------------|
| Chi-squared | 403.4 | Significant (large N) |
| p-value | < 0.000001 | Significant |
| **Cramer's V** | **0.0158** | **NEGLIGIBLE** |

### Position-wise REGIME Percentages

| Position | R1% | R2% | R3% | R4% |
|----------|-----|-----|-----|-----|
| 1 | 52.5 | 11.8 | 17.7 | 18.0 |
| 5 | 53.3 | 11.3 | 18.2 | 17.2 |
| 10 | 51.1 | 12.3 | 17.7 | 18.9 |

**All positions have effectively identical REGIME distributions.** The ~1-2% variation is noise.

### Verdict: FALSIFIED

Both monotonic correlation AND non-monotonic differentiation are ruled out. Position carries zero information about REGIME selection.

---

## What This Rules Out

The "A as workflow orchestrator" interpretation is falsified. An A entry compatible with multiple REGIMEs means:

> "This material/product can be processed at ANY of these intensity levels, depending on operator choice"

NOT:

> "Process this material first at gentle, then at intense levels in sequence"

And NOT:

> "Different positions in the entry specify different processing steps"

---

## Constraint Update

No new constraint needed. This test reinforces existing constraints:

- **C234 (POSITION_FREE):** Confirmed - zero semantic content in position
- **C240 (NON_SEQUENTIAL):** Confirmed - A does not encode trajectories
- **C384 (no entry-level coupling):** Confirmed - no trajectory coupling either

Add to Tier 1 falsifications:
> "A-orchestration hypothesis: Token position in A entries encodes REGIME trajectory" - FALSIFIED (tau=0.025, Cramer's V=0.016, A_ORCHESTRATION_TEST)

---

## Files

| File | Purpose |
|------|---------|
| `a_orchestration_test.py` | Monotonic correlation test (Kendall's tau) |
| `a_orchestration_differentiation.py` | Distributional differentiation test (Chi-squared, Cramer's V) |
| `A_ORCHESTRATION_REPORT.md` | This report |
| `results/a_orchestration_test.json` | Raw results |

---

*Phase complete: 2026-01-19*
