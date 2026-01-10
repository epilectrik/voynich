# C412: Sister-Escape Anticorrelation

**Tier:** 2 | **Status:** CLOSED | **Phase:** SISTER

---

## Claim

Sister-pair preference (ch vs sh) is significantly anticorrelated with qo-escape density. Programs with higher ch-preference exhibit fewer recovery affordances.

## Evidence

| Metric | Value |
|--------|-------|
| Spearman rho | -0.326 |
| p-value | 0.002 |
| N (programs) | 82 |

## Component Analysis

| Correlation | rho | p |
|-------------|-----|---|
| ch-pref vs escape density | **-0.326** | **0.002** |
| ch-pref vs hazard density | -0.043 | 0.700 |
| ch-pref vs max safe run | -0.020 | 0.857 |

The anticorrelation is specific to escape density, not hazard density or safe run length.

## Quartile Profile

| Quartile | ch-Preference | Escape Density |
|----------|---------------|----------------|
| Q1 (Brittle) | 70.3% | Lower |
| Q4 (Forgiving) | 61.9% | Higher |

## Related Constraints

- C408 - Sister pairs are equivalence classes
- C410 - Sister choice is section-conditioned
- C397 - qo-prefix = escape route

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
| Quartile | ch-preference | escape-density |
|----------|---------------|----------------|
| Q1 (Low escape) | 68.8% | 7.1% |
| Q4 (High escape) | 58.1% | 24.7% |

**Prior discrepancy explained:** A separate re-analysis incorrectly used ch-density (`ch/total`) instead of ch-preference (`ch/(ch+sh)`). These are different metrics. The original C412 claim uses ch-preference and is correct.

**Verification script:** `phases/exploration/c412_verification.py`

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
