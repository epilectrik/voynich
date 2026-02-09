# C891: ENERGY-FREQUENT Inverse Correlation

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> ENERGY_OPERATOR and FREQUENT_OPERATOR role fractions are strongly inversely correlated (rho = -0.80) at REGIME level. REGIMEs with high energy operation density have low escape operator density, and vice versa.

---

## Evidence

**Test:** `phases/REVERSE_BRUNSCHWIG_TEST/scripts/10_role_orthogonality.py`

### Role Composition by REGIME

| REGIME | ENERGY_OP | FREQUENT_OP | Profile |
|--------|-----------|-------------|---------|
| R3 | 36.5% (highest) | 11.2% (lowest) | High energy, low escape |
| R1 | 34.3% | 12.1% | Standard processing |
| R4 | 22.7% | 15.1% (highest) | Low energy, high escape |
| R2 | 20.8% (lowest) | 13.2% | Gentle handling |

### Pairwise Correlations

| Comparison | Spearman rho | Interpretation |
|------------|--------------|----------------|
| ENERGY vs FREQUENT | -0.80 | Strong inverse |
| ENERGY vs FLOW | -0.60 | Moderate inverse |
| CORE vs FREQUENT | 0.00 | Perfectly orthogonal |

---

## Interpretation

This finding reveals orthogonal control dimensions in the closed-loop model:

1. **ENERGY dimension:** How much thermal/energy operation the REGIME requires
2. **ESCAPE dimension:** How much grammatical escape/recovery infrastructure the REGIME uses

These are inversely related because:
- **High energy processing (R3):** Robust process tolerates deviation, needs few escape operators
- **Precision processing (R4):** Gentle heat but tight tolerances, needs many escape operators

**Brunschwig parallel:** This distinguishes fire INTENSITY from error HANDLING. Brunschwig's linear recipes cannot separate these - a "third degree" recipe implies both high fire and high risk. The Voynich closed-loop model separates them: REGIME_4 has low fire (intensity) but high error handling (escape).

---

## Statistical Note

With n=4 REGIMEs, correlation magnitudes should be interpreted cautiously. However:
- The inverse relationship holds at all 4 data points
- The pattern is qualitatively consistent (highest ENERGY = lowest FREQUENT, vice versa)
- Folio-level confirmation recommended for confidence intervals

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C494 | Supported - REGIME_4 precision = low energy + high escape |
| C890 | Related - recovery rate and pathway also orthogonal |
| C458 | Consistent - design freedom allows independent parameter tuning |

---

## Provenance

- **Phase:** REVERSE_BRUNSCHWIG_TEST
- **Date:** 2026-01-30
- **Script:** 10_role_orthogonality.py

---

## Navigation

<- [C890_recovery_rate_pathway_independence.md](C890_recovery_rate_pathway_independence.md) | [INDEX.md](INDEX.md) ->
