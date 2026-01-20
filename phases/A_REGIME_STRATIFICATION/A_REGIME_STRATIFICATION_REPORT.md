# A-REGIME Stratification Phase

**Phase:** A_REGIME_STRATIFICATION
**Date:** 2026-01-19
**Status:** COMPLETE - PARTIALLY SUPPORTED (frequency confounded)

---

## Background

During the A_ORCHESTRATION_TEST phase, we discovered that 39.3% of A tokens appearing in B are REGIME-specific (appear in only one REGIME). This raised the question: does A vocabulary encode REGIME constraints?

## Tests Conducted

| Test | Question | Result |
|------|----------|--------|
| T1 | Do PREFIX/SUFFIX predict REGIME compatibility? | **SUFFIX YES**, PREFIX NO |
| T2 | Are REGIME-specific tokens rare artifacts? | **YES - MAJOR CONFOUND** |
| T3 | Do REGIME-specific tokens have distinct AZC profiles? | NO |
| T4 | Do constraints cluster on A folios? | INCONCLUSIVE |

---

## T1: Morphological Analysis

### PREFIX Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Chi-squared | 4.43 | Not significant |
| p-value | 0.817 | No effect |
| Cramer's V | 0.068 | Negligible |

**PREFIX does NOT predict compatibility category.**

### SUFFIX Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Chi-squared | 28.36 | Significant |
| p-value | 0.0004 | Strong |
| **Cramer's V** | **0.159** | **Moderate effect** |

**SUFFIX PREDICTS compatibility category.**

Key suffix patterns:

| Suffix | Single-REGIME | Partial | Universal | Interpretation |
|--------|---------------|---------|-----------|----------------|
| `-r` | 4.2% | 4.7% | **11.5%** | Enriched in universal |
| `-ar` | **8.2%** | 5.0% | 2.4% | Enriched in single-REGIME |
| `-or` | **6.9%** | 6.5% | 2.0% | Enriched in single-REGIME |
| `-aiin` | **7.3%** | 4.7% | 4.4% | Slightly enriched in single |

### Interpretation

SUFFIX encodes something related to REGIME compatibility. Tokens ending in `-r` are more likely to be universal (work with all REGIMEs), while tokens ending in `-ar`, `-or` are more likely to be REGIME-specific.

This aligns with C466-C467 (PREFIX/SUFFIX encode control-flow participation) and suggests SUFFIX may encode operational constraints that manifest as REGIME restrictions.

---

## T2: Frequency Analysis

### CRITICAL FINDING: Frequency Confound

| Category | N | Mean Freq | Median | Hapax % |
|----------|---|-----------|--------|---------|
| Single-REGIME | 450 | 2.54 | 1.0 | **55.6%** |
| Partial (2-3) | 443 | 4.05 | 2.0 | 37.9% |
| Universal (4) | 252 | **21.93** | **8.0** | 13.1% |

**Mann-Whitney U test:**
- U = 18,764
- p < 0.000001
- Effect size r = **0.669** (LARGE)

**Chi-squared (Frequency tier × Compatibility):**
- Cramer's V = **0.383** (LARGE)

### Interpretation

The "39% single-REGIME" finding is **heavily confounded by frequency**:

1. Single-REGIME tokens are predominantly **rare** (median = 1, 55.6% hapax)
2. Universal tokens are **common** (median = 8, 13.1% hapax)
3. A rare token has fewer opportunities to appear across multiple REGIMEs

**Conclusion:** Much of the apparent REGIME stratification is an artifact. Rare tokens appear single-REGIME not because they encode REGIME constraints, but because they haven't been observed enough to appear across REGIMEs.

### Frequency-Stratified Breakdown

| Frequency Tier | Single% | Partial% | Universal% |
|----------------|---------|----------|------------|
| Hapax (1x) | 55.4% | 37.3% | 7.3% |
| Rare (2-5x) | 38.5% | 45.8% | 15.7% |
| Common (6-20x) | 17.6% | 37.9% | 44.5% |
| Frequent (>20x) | 4.7% | 12.8% | **82.6%** |

Even among **frequent tokens**, only 4.7% are single-REGIME. This suggests that most "REGIME-specific" vocabulary is just undersampled, not genuinely constrained.

---

## T3: AZC Cross-Reference

| Position | Single% | Partial% | Universal% |
|----------|---------|----------|------------|
| P1 (first) | 1.2% | 0.6% | 0.1% |
| MIDDLE | 98.2% | 98.7% | 99.2% |
| FINAL | 0.6% | 0.7% | 0.7% |

**Chi-squared test:** Cramer's V = 0.048 (negligible)

**Conclusion:** Position profile is essentially identical across compatibility categories. No AZC zone enrichment for REGIME-specific tokens.

---

## T4: Folio Clustering

### Descriptive Statistics

| Metric | Value |
|--------|-------|
| Mean single-REGIME % | 17.7% |
| Std | 5.3% |
| Range | 5.2% - 33.3% |
| Coefficient of Variation | **0.301** |

### Chi-squared Test

| Metric | Value |
|--------|-------|
| Chi-squared | 228.15 |
| Degrees of freedom | 226 |
| p-value | 0.447 |
| Cramer's V | 0.137 |

**Conclusion:** Despite high CV suggesting clustering, chi-squared is not significant. Variation is likely noise rather than systematic clustering.

---

## Overall Verdict

### What's Real

1. **SUFFIX predicts compatibility** (Cramer's V = 0.159, p = 0.0004)
   - `-r` suffix → universal compatibility
   - `-ar`, `-or` suffixes → REGIME-specific

### What's Artifact

2. **The 39% "single-REGIME" rate is largely frequency artifact**
   - Among frequent tokens (>20x), only 4.7% are single-REGIME
   - Rare tokens simply haven't had enough exposure

### What's Uninformative

3. PREFIX does not predict compatibility
4. No AZC zone enrichment
5. No systematic folio clustering

---

## Constraint Implications

### New Constraint (Proposed)

**C4XX (TIER 2):** SUFFIX partially predicts REGIME compatibility. Tokens with `-r` suffix are enriched in universal compatibility (11.5% vs 4.2% baseline), while `-ar`/`-or` suffixes are enriched in single-REGIME compatibility (Cramer's V = 0.159, p < 0.001).

**Provenance:** A_REGIME_STRATIFICATION T1

### Existing Constraint Updates

**C466-C467:** (PREFIX/SUFFIX encode control-flow participation) - Extended with evidence that SUFFIX encodes REGIME-related operational constraints.

### Warning Note

The naive "39% of A tokens are REGIME-specific" claim should NOT become a constraint. It is frequency-confounded. The corrected claim is:

> Among frequent A tokens (>20 occurrences), only 4.7% are single-REGIME. Most apparent REGIME stratification is sampling artifact.

---

## Files

| File | Purpose |
|------|---------|
| `regime_stratification_tests.py` | Main test script (T1-T4) |
| `A_REGIME_STRATIFICATION_REPORT.md` | This report |
| `results/regime_stratification_tests.json` | Raw results |

---

*Phase complete: 2026-01-19*
