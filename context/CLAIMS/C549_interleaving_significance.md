# C549: qo/ch-sh Interleaving Significance

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> qo-family and ch/sh-family tokens interleave at 56.3%, significantly above the 50.6% random expectation (z=10.27, p<0.001). This represents a grammatical preference for alternation, not random distribution.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/interleaving_significance.py`

### Observed vs Expected

| Metric | Value |
|--------|-------|
| Total transitions | 3,634 |
| Observed interleaving | 56.3% (2,045) |
| Same-family | 43.7% (1,589) |
| Null expectation (shuffle) | 50.6% |
| Theoretical expectation | 50.0% |
| **Excess interleaving** | **5.7 percentage points** |

### Statistical Test

| Test | Value |
|------|-------|
| Z-score | 10.27 |
| p-value | < 0.000001 |
| Monte Carlo N | 10,000 |

### By REGIME

| REGIME | Interleave Rate | vs Expected |
|--------|-----------------|-------------|
| REGIME_3 | 59.0% | 1.18x |
| REGIME_2 | 57.8% | 1.16x |
| REGIME_1 | 57.5% | 1.15x |
| REGIME_4 | 52.2% | 1.04x |

---

## Interpretation

The grammar **prefers alternation** between qo-family (escape/venting) and ch/sh-family (precision/application) operations. This is not random mixing - it's a structural preference.

**REGIME pattern:**
- REGIME_3 (intervention) shows strongest alternation (59.0%)
- REGIME_4 (precision) shows near-baseline alternation (52.2%)

This suggests different operational modes:
- High-intervention contexts cycle rapidly between energy families
- Precision contexts allow more sustained same-family sequences

---

## Relationship to C544

C544 documented the interleaving pattern qualitatively. C549 establishes that this pattern is **statistically significant** - the 56.3% rate exceeds random by 10+ standard deviations.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C544 | Quantified - establishes significance of interleaving |
| C547 | Related - qo-chains cluster in REGIME_1 |
| C412 | Extended - sister-escape anticorrelation at transition level |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** interleaving_significance.py

---

## Navigation

<- [C548_manuscript_level_envelope.md](C548_manuscript_level_envelope.md) | [INDEX.md](INDEX.md) ->
