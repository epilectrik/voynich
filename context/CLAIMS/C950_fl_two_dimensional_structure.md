# C950: FL Two-Dimensional Structure (PREFIX x STAGE)

**Tier:** 2 | **Scope:** B | **Phase:** FL_RESOLUTION_TEST (precursor investigation)

## Statement

FL is a two-dimensional annotation system where PREFIX determines line position (WHERE) and STAGE determines value (WHAT). The two dimensions are correlated (chi-squared p = 4.8 x 10^-82, Cramer's V = 0.349) but not redundant.

## Evidence

**PREFIX positional groups (Kruskal-Wallis p = 10^-15):**

| Group | Prefixes | Mean Line Position |
|-------|----------|-------------------|
| CTRL | da, sa, so | 0.32 (early) |
| ENER | sh, qo, ch | 0.52 (mid) |
| BARE | (none) | 0.61 (default) |
| FREQ | ok, ot | 0.62 (late) |
| LATE_AUX | lk, ar | 0.64+ (end) |

**STAGE gradient survives within prefixes:**
- da: rho = +0.64, p < 0.0001
- sh: rho = +0.53, p = 0.01

**PREFIX x STAGE lock:**
- INIT/EARL stages exclusively da/sa prefixes
- TERMINAL stages shift to ch/lk
- Chi-squared p = 4.8 x 10^-82

## Interpretation

The two dimensions reflect a structured annotation convention: early prefixes mark where early-condition observations are written; late prefixes mark where completion/acceptance is noted. The correlation is physical (assessment timing naturally corresponds to assessed state), not computational.

## Provenance

- Precursor investigation scripts (scratchpad)
- Related: C777, C949
