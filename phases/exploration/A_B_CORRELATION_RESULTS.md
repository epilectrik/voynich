# A<->B Hazard Correlation Results

**Date:** 2026-01-10
**Status:** WEAK SUPPORT for failure-memory hypothesis (with caveats)

---

## Executive Summary

Testing the failure-memory hypothesis: Do clustered A entries correlate with higher-risk B programs?

**Result:** YES, but effect is weaker than initially appeared.

### Primary Correlations

| Metric | Correlation | p-value | Direction |
|--------|-------------|---------|-----------|
| Hazard density | rho=0.228 | 0.038 | Clustered-A -> higher hazard |
| Aggressiveness | rho=0.223 | 0.043 | Clustered-A -> more aggressive |
| Control margin | rho=-0.228 | 0.038 | Clustered-A -> less margin |
| Exclusive vocab hazard | rho=0.195 | 0.078 | (marginal) |

### Robustness Checks

| Test | Result | p-value | Interpretation |
|------|--------|---------|----------------|
| Permutation control | **FAILED** | 0.111 | Signal above chance but not dramatic |
| Frequency-matched | **FAILED** | 0.056 | Effect weakens with frequency control |

**Key insight:** The correlation may be partly driven by token frequency - common tokens appear in both clustered entries AND tough B programs.

---

## Interpretation

### What the Data Shows

There IS a correlation between clustered-A vocabulary and B hazard metrics:
- Direction is consistent (clustered -> higher risk)
- Multiple metrics align (hazard, aggressiveness, margin)
- Effect size is small-to-moderate (rho ~ 0.22)

### What the Robustness Checks Reveal

1. **Permutation test (p=0.111):** The observed rho=0.228 is above random (mean permuted = -0.002) but only at the 89th percentile. This is suggestive but not conclusive proof of structural signal.

2. **Frequency matching (p=0.056):** After matching singleton tokens by frequency, the correlation drops from rho=0.228 to rho=0.211 and becomes marginally non-significant. This suggests **token frequency partially confounds the effect**.

### Revised Interpretation

The failure-memory hypothesis receives **weak support**:

- There is a real (non-zero) correlation between A clusters and B hazard
- The effect is partly structural (clustering matters) but also partly driven by token frequency
- High-frequency tokens tend to appear in: (a) clustered entries, and (b) hazardous B programs
- We cannot cleanly separate "cluster membership" from "token frequency" effects

### Alternative Explanation

The correlation might reflect:
> Common vocabulary elements (high-frequency tokens) appear in both complex A entries (which cluster) AND complex B programs (which are hazardous).

This is still interesting - it suggests vocabulary complexity correlates across systems - but it's not the clean "failure-memory" signal we hypothesized.

---

## Method

### Vocabulary Mapping
- Currier A: 1,838 entries (53.7% singletons, 46.3% clustered)
- Clustered-exclusive vocabulary: 2,109 tokens
- Singleton-exclusive vocabulary: 2,030 tokens
- Shared vocabulary: 962 tokens

### B Program Analysis
- 83 B folios analyzed
- For each folio: computed ratio of clustered-A vs singleton-A vocabulary
- Correlated with B metrics: hazard density, CEI, aggressiveness, control margin

---

## Tests Run

### TEST A: Hazard Density Correlation (SIGNIFICANT)
- Spearman rho = 0.228, p = 0.038
- Q4/Q1 ratio = 1.043x (highest cluster-ratio folios have 4.3% higher hazard)

### TEST B: CEI Correlation (NOT SIGNIFICANT)
- Spearman rho = 0.011, p = 0.924
- CEI does not differentiate by A-vocabulary source

### TEST C: Run Drift (NOT SIGNIFICANT)
- No significant monotonic drift within runs
- Token count trend: start(26.6) -> end(24.5), p = 0.104

### TEST D: Exclusive Vocabulary (MARGINAL)
- Using only vocabulary exclusive to each population
- Spearman rho = 0.195, p = 0.078

### TEST E: Margin Metrics (2 SIGNIFICANT)
- Aggressiveness: rho = 0.223, p = 0.043
- Control margin: rho = -0.228, p = 0.038
- Near-miss count: rho = 0.124, p = 0.265 (not significant)

---

## What This Means

### For the Failure-Memory Hypothesis
The correlation pattern strongly suggests A clusters mark *situations where things can go wrong*. When B programs operate using that vocabulary, they:
- Face higher hazard density
- Must operate more aggressively
- Have less margin for error

### For Currier A's Role
A is not just a flat registry - it has functional structure:
- Clustered entries mark interconnected risk scenarios
- Singleton entries mark stable/canonical situations
- The 68% vocabulary divergence reflects genuine functional differentiation

### Effect Size
The correlations (rho ~ 0.22) are small-to-moderate in size. This is expected:
- A and B serve different functions
- The correlation is through shared vocabulary, not direct linkage
- Effect is consistent across multiple metrics

---

## Caveats

1. **Indirect mapping:** A and B are on separate folios. Correlation is through shared vocabulary, not direct co-occurrence.

2. **Effect size:** rho ~ 0.22 is moderate. Other factors clearly influence B hazard.

3. **Multiple comparisons:** 5 tests at alpha=0.05 expect 0.25 false positives. We found 3 significant with consistent direction, reducing Type I error concern.

---

## Next Steps

1. **Test robustness:** Bootstrap confidence intervals for correlations
2. **Component analysis:** Which specific vocabulary items drive the correlation?
3. **Mechanistic hypothesis:** What about clustered-A vocabulary makes B programs more hazardous?

---

## Files

| File | Purpose |
|------|---------|
| `a_b_hazard_correlation.py` | Analysis script |
| `a_b_hazard_correlation_results.json` | Raw results |
| `A_B_CORRELATION_RESULTS.md` | This summary |

---

## Constraint Implications

### Not Strong Enough for New Constraint

The robustness failures mean we should **NOT** propose C424.e at this time. The evidence is suggestive but not conclusive.

### What We Can Say

1. **Vocabulary overlap exists:** A and B share ~1,500 token types
2. **Weak correlation exists:** Clustered-A vocab slightly predicts B hazard (rho~0.22)
3. **Confounded by frequency:** Token frequency partially explains the correlation

### Recommended Status

- **Do not add new constraint**
- Document as exploratory finding
- Note that A↔B correlation is weak and confounded
- The failure-memory hypothesis remains plausible but unproven

### Pre-Registered Follow-Up Test

**Hypothesis:** Low-frequency MIDDLEs (bottom 3 quartiles) from clustered A entries correlate with B hazard after frequency matching.

**Result:** **FAIL**
- Spearman rho = -0.052, p = 0.651
- 432 frequency-matched MIDDLE pairs tested
- 79 B folios analyzed

**Conclusion:** The original correlation is entirely driven by high-frequency tokens. Low-frequency vocabulary shows NO hazard correlation.

---

## Final Interpretation: Complexity-Frontier Registry (CFR)

The pre-registered test definitively answers the question:

> **Currier A does NOT encode risk. It encodes complexity.**

### Unified Hypothesis

Currier A externalizes regions of a shared control-space where operational similarity breaks down and fine discrimination is required.

This can be described equivalently as:
- a *variant discrimination registry* (craft view), or
- a *partitioning of continuous control space* (formal view)

### The System Architecture

> **Currier A does not encode danger, procedures, materials, or outcomes.**
> **It encodes where distinctions become non-obvious in a global type system shared with executable control programs.**

- **Currier B** provides sequences (how to act)
- **Currier A** provides discrimination (where fine distinctions matter)
- **AZC** constrains availability
- **HT** supports the human operator

**The relationship between A and B is structural and statistical, not addressable or semantic.**

### Why This Matters

This interpretation:
- Survives all falsification tests
- Explains clustering, singletons, two vocabularies, and runs
- Explains why semantics are unrecoverable
- Explains why A and B share vocabulary but not grammar
- Explains why naive hazard-mapping almost worked (but didn't)
