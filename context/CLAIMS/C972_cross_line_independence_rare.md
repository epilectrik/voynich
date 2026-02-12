# C972: Cross-Line Independence Stronger Than Random Markov

**Tier:** 2 | **Scope:** B | **Phase:** FINGERPRINT_UNIQUENESS

## Statement

Voynich B's cross-line mutual information (0.521 bits) is significantly lower than any random Markov chain on 49 states with matched density, uniform distribution, or Zipf-weighted frequencies (null MI: 0.72-0.77, p = 0.000 across all ensembles).

## Evidence

- Cross-line MI measured as I(last token of line N; first token of line N+1)
- Observed: 0.521 bits
- All three null ensembles produce HIGHER cross-line MI:
  - NULL-D (density-matched): mean 0.767, p = 0.000
  - NULL-E (uniform): mean 0.772, p = 0.000
  - NULL-F (Zipf-weighted): mean 0.718, p = 0.000
- N = 1,000 simulations per ensemble, each simulating 2,488 lines with real line-length distribution

## Non-Discriminating Properties (same test)

- **F5 (first-order BIC sufficiency):** 100% of all null chains also prefer first-order. Universal, not discriminating.
- **F6 (sharp hazard gate):** KL ratio = 1.0x at 49-class level. Gate operates within roles (C967), not visible at class granularity.

## Interpretation

The grammar resets at line boundaries harder than random Markov dynamics predict. This is the single strongest discriminator in the entire fingerprint — the line is a genuine execution boundary, not an artifact of text layout. Confirms C360 (line-invariant grammar) and C966 (no cross-line memory) with null-model validation.

## Provenance

- Confirms: C360 (no cross-line memory), C966 (first-order sufficiency)
- Method: `phases/FINGERPRINT_UNIQUENESS/scripts/t2_markov_dynamics.py`
- Results: `phases/FINGERPRINT_UNIQUENESS/results/t2_dynamics.json`
