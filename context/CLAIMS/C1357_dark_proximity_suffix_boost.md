# C1357: Dark Proximity Weakly Boosts Terminal Suffix

**Tier:** 2
**Scope:** B
**Phase:** LAYERED_GRAMMAR_TEST (473)

## Constraint

Bridge tokens adjacent to dark tokens (distance ≤ 1) have higher terminal suffix rate than bridge tokens far from dark tokens (distance ≥ 3 or no dark on line): 25.2% vs 20.7% (Z=3.51, p<0.001). The effect survives PREFIX control — 12 of 16 tested PREFIX groups show higher terminal fraction near dark tokens. However, Cramer's V = 0.042, indicating a statistically significant but practically small effect. Dark proximity slightly pushes bridge tokens toward specification/endpoint behavior.

## Evidence

From layered_grammar_test.py test T4 (2,344 near-dark bridge tokens, 15,804 far-from-dark):

| Suffix category | Near dark | Far from dark |
|----------------|-----------|---------------|
| terminal | **25.2%** | **20.7%** |
| bare | 61.8% | 67.2% |
| iterate | 11.7% | 10.5% |
| connector | 1.3% | 1.6% |

| Metric | Value |
|--------|-------|
| Chi-squared | 32.24 |
| p | <0.001 |
| Cramer's V | 0.042 |
| Terminal Z | 3.505 |
| Terminal p | <0.001 |

**PREFIX-controlled terminal shift (selected):**

| PREFIX | Near term | Far term | Diff |
|--------|----------|---------|------|
| ol | 38.5% | 28.5% | +10.0% |
| te | 17.6% | 9.8% | +7.9% |
| pch | 16.2% | 9.8% | +6.4% |
| BARE | 14.2% | 8.8% | +5.4% |
| ok | 18.6% | 14.0% | +4.6% |

## Interpretation

Dark tokens slightly push nearby bridge tokens toward terminal suffix (specification mode per C1309). This is consistent with dark tokens as parameterization signals: when a dark token specifies context, the nearby grammar tokens are more likely to terminate/specify rather than continue/iterate. But V=0.042 means dark proximity explains less than 0.2% of suffix variance — this is a detectable trace, not a major pathway.

Combined with C1354 (dark influence is local), this suggests dark tokens have a very localized ripple effect: they constrain the next grammar token's class (C1351) and slightly bias nearby tokens' suffix choice toward terminal, but neither effect propagates to the line-level grammar regime.

## Provenance

- layered_grammar_test.json: test T4
- Extends: C1351 (dark constrains next token — suffix is a secondary local effect)
- Extends: C1342 (PREFIX modulates suffix — dark proximity is an additional, weaker modulator)
- Extends: C1309 (terminal = specification voice — dark proximity biases toward specification)
- Bounded by: C1354 (local not contextual — consistent with very localized dark influence)

## Status

CONFIRMED — dark proximity boosts terminal suffix (Z=3.51, V=0.042), PREFIX-controlled. Effect is real but tiny.
