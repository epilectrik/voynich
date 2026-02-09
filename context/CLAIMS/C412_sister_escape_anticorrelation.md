# C412: Sister-QO Anticorrelation (Revised)

**Tier:** 2 | **Status:** CLOSED | **Phase:** SISTER

> **TERMINOLOGY NOTE (2026-01-31):** Original "escape" terminology replaced with
> "qo-density" per C397/C398 revision. QO is the energy lane (k-rich, 70.7%)
> operating hazard-DISTANT. The anticorrelation with ch-preference is valid;
> the interpretation has been corrected.

---

## Claim

Sister-pair preference (ch vs sh) is significantly anticorrelated with qo-density. Programs with higher ch-preference (CHSH-dominant) have lower qo-density (less QO-lane activity).

## Evidence

| Metric | Value |
|--------|-------|
| Spearman rho | -0.326 |
| p-value | 0.002 |
| N (programs) | 82 |

## Component Analysis

| Correlation | rho | p |
|-------------|-----|---|
| ch-pref vs qo-density | **-0.326** | **0.002** |
| ch-pref vs hazard density | -0.043 | 0.700 |
| ch-pref vs max safe run | -0.020 | 0.857 |

The anticorrelation is specific to qo-density, not hazard density or safe run length.

## Quartile Profile

| Quartile | ch-Preference | QO-Density |
|----------|---------------|------------|
| Q1 (Low QO) | 70.3% | Lower |
| Q4 (High QO) | 61.9% | Higher |

## Interpretation (Revised 2026-01-31)

Given the lane model (C643, C645):
- CHSH lane (ch/sh prefixes) is e-rich (68.7%), handles hazard-adjacent contexts
- QO lane (qo prefix) is k-rich (70.7%), operates hazard-distant

The anticorrelation means: **Programs emphasizing CHSH (stability) use less QO (energy).**
This is lane balance, not "escape" behavior.

## Related Constraints

- C408 - Sister pairs are equivalence classes
- C410 - Sister choice is section-conditioned
- C397 - qo-prefix post-source frequency (REVISED)
- C643 - QO-CHSH rapid alternation
- C645 - CHSH post-hazard dominance

---

## Verification (2026-01-09)

**STATUS: CONFIRMED**

Independent verification using exact original methodology reproduced results:

| Metric | Original | Verified |
|--------|----------|----------|
| N (folios) | 82 | 82 |
| Spearman rho | -0.326 | -0.327 |
| p-value | 0.002 | 0.0027 |

**Quartile analysis confirms monotonic relationship:**
| Quartile | ch-preference | qo-density |
|----------|---------------|------------|
| Q1 (Low QO) | 68.8% | 7.1% |
| Q4 (High QO) | 58.1% | 24.7% |

**Prior discrepancy explained:** A separate re-analysis incorrectly used ch-density (`ch/total`) instead of ch-preference (`ch/(ch+sh)`). These are different metrics. The original C412 claim uses ch-preference and is correct.

**Verification script:** `phases/exploration/c412_verification.py`

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
