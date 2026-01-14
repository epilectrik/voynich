# C489: HT Correlates with Zone Diversity

**Tier:** 3 | **Status:** CLOSED | **Scope:** HUMAN_TRACK

## Statement

HT density positively correlates with MIDDLE zone diversity (r = 0.24, p = 0.0006). Folios with higher HT density use MIDDLEs from more diverse AZC legality zones.

## Evidence

### Primary Correlation

| Metric | Value |
|--------|-------|
| HT density vs zone diversity | r = 0.242, p = 0.0006 |
| HT TTR vs zone diversity | r = 0.087, p = 0.226 (NS) |

### Group Comparison

| Group | n | Mean Zone Diversity |
|-------|---|---------------------|
| High-HT folios | ~99 | 1.663 |
| Low-HT folios | ~98 | 1.597 |
| Difference | - | t = 3.71, p = 0.0003 |

### Data Scale

| Metric | Value |
|--------|-------|
| Matched folios | 197 |
| HT range | 0.056 - 0.345 |
| Diversity range | 1.30 - 1.91 (entropy) |

## Interpretation

### What This Means

Higher HT density correlates with more diverse MIDDLE zone usage. This supports the **material pressure interpretation**:

> When a folio handles materials from multiple intervention regimes (diverse zones), more human attention is required.

### Zone Diversity as Complexity Proxy

Zone diversity (Shannon entropy across C/P/R/S zones) measures how many different "handling requirements" are active:

| Diversity | Meaning | HT Response |
|-----------|---------|-------------|
| Low (< 1.5) | Few intervention modes | Lower HT |
| High (> 1.7) | Many intervention modes | Higher HT |

### Integration with HT Model

This extends the "material pressure" interpretation from earlier phases:

| Finding | Interpretation |
|---------|----------------|
| HT tracks tail pressure (C477) | Rare discriminators = harder |
| HT tracks zone diversity (this) | Mixed handling = harder |
| HT predicts strategy (C482) | Load profile = strategy fit |

All three point to HT as a **cognitive load balancer**.

### What Zone Diversity Is NOT

Zone diversity is not:
- Material type (that's PREFIX)
- Specific substances (irrecoverable)
- Apparatus components (speculation)

It is: **intervention affordance diversity** - how many different handling modes are needed.

## Related Constraints

- C477: HT tail correlation
- C482: HT strategy prediction
- MIDDLE zone survival profiles (I.L)

## Source

Phase: SEMANTIC_CEILING_EXTENSION
Test: 1B (ht_backpressure.py)
Results: `results/ht_backpressure.json`
