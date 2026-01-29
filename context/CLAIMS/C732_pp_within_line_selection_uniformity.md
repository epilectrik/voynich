# C732: PP Within-Line Selection Uniformity

**Status:** VALIDATED | **Tier:** 2 | **Phase:** PP_LINE_LEVEL_STRUCTURE | **Scope:** A

## Finding

Beyond MIDDLE incompatibility (C728), PP selection within Currier A lines shows no structured patterns across three independent dimensions:

### SUFFIX Coherence (T5): Marginal

| Metric | Value |
|--------|-------|
| Observed same-SUFFIX match rate | 0.3264 |
| Folio-level expected rate | 0.3190 |
| Null (shuffled) match rate | 0.3054 +/- 0.0024 |
| Observed/expected ratio | 1.02x |
| p (observed > null) | < 0.001 |

Statistically significant but effect size is negligible (1.02x vs 1.3x threshold). SUFFIX selection within lines matches folio-level frequency distributions almost exactly.

### Diversity Scaling (T6): Near-Expected

| Metric | Value |
|--------|-------|
| Mean residual (obs - hypergeometric expected) | -0.097 |
| SD residual | 0.735 |
| Effect size (|mean|/SD) | 0.132 |
| Bootstrap 95% CI | [-0.135, -0.059] |
| Direction | Slightly LESS diverse than expected |

Lines have marginally fewer unique MIDDLEs than hypergeometric expectation — consistent with incompatibility restricting the effective pool. But the effect is tiny (0.097 fewer unique MIDDLEs per line).

### Folio Position Trajectory (T8): Absent

| Metric | Value |
|--------|-------|
| Early-late JS divergence | 0.586 |
| Within-third JS divergence | 0.738 |
| Early-late / within ratio | 0.794 |
| p (observed > null) | 0.633 |

No change in PP composition from early to late lines within a folio. Early and late thirds are actually MORE similar than random thirds, consistent with uniform sampling from a stable pool throughout the folio.

## Implication

After accounting for MIDDLE incompatibility, PP selection within lines is uniform across SUFFIX, diversity, and position dimensions. The folio PP pool (C703) is drawn from uniformly, with incompatibility (C475/C728) as the only structured filter. This confirms that individual lines are not actively "specified" — they are compatibility-valid random draws from a stable, homogeneous pool.

## Provenance

- Script: `phases/PP_LINE_LEVEL_STRUCTURE/scripts/pp_dimension_tests.py` (T5, T6, T8)
- Confirms: C703 (PP pool is folio-homogeneous), C728 (incompatibility is sole driver)
- Consistent with: C233 (line independence), C234 (position-free within line)
