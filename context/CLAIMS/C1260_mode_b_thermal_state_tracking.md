# C1260: Mode B Thermal State Tracking

**Tier:** 2
**Scope:** B
**Phase:** GRADIENT_DECOMPOSITION (Phase 451)
**Date:** 2026-02-24

## Statement

Within Mode B sequential tracks, energy balance state variables propagate between consecutive B lines: e_frac (rho=0.376, p=0.000), ke_ratio (rho=0.228, p=0.000), qo_frac (rho=0.186, p=0.000), k_frac (rho=0.139, p=0.000). FL stage does NOT propagate (rho=0.026, p=0.56). Lag-1 autocorrelation survives permutation for ke_ratio (p=0.002). No ordinal progression in energy variables -- the B-track maintains steady-state thermal context while independently assessing material state each cycle. Only line length shows monotonic decline (rho=-0.243, p=0.000).

## Architecture

- **Energy state propagates.** Each B line inherits thermal context from its predecessor. The e/k balance (stability vs energy) carries forward.
- **Material state does not propagate.** FL stage (what the material looks like) is independently assessed each cycle. No memory of previous FL reading.
- **Steady-state operation.** No ordinal drift in energy variables (all p > 0.07). The B-track maintains thermal equilibrium, not a progressive ramp.
- **Lines shorten monotonically.** Token count decreases through the B-track (rho=-0.243). Later cycles are more concise.

## Key Findings

| Signal | Variable | rho | p-value | Status |
|--------|----------|-----|---------|--------|
| S2 | e_frac | 0.376 | 0.000 | SIGNAL |
| S2 | ke_ratio | 0.228 | 0.000 | SIGNAL |
| S2 | qo_frac | 0.186 | 0.000 | SIGNAL |
| S2 | k_frac | 0.139 | 0.000 | SIGNAL |
| S3 | terminal_frac | 0.145 | 0.001 | SIGNAL |
| S1 | mean_fl | 0.026 | 0.560 | NULL |
| S3 | bare_frac | 0.092 | 0.023 | NULL (sub-Bonferroni) |

| Ordinal | Variable | rho | p-value | Status |
|---------|----------|-----|---------|--------|
| S4 | n_toks | -0.243 | 0.000 | LINE SHORTENING |
| S4 | e_frac | 0.067 | 0.072 | NULL |
| S4 | ke_ratio | -0.046 | 0.216 | NULL |
| S4 | qo_frac | -0.057 | 0.124 | NULL |

| Autocorrelation | Variable | r | perm_p | Status |
|-----------------|----------|---|--------|--------|
| S5 | ke_ratio | 0.250 | 0.002 | SIGNAL |
| S5 | e_frac | 0.385 | 0.039 | Sub-Bonferroni |
| S5 | k_frac | 0.152 | 0.068 | NULL |

## Interpretation

The B-track carries thermal context: how hot/energetic the system is (e_frac, k_frac, ke_ratio) and how much thermal processing is occurring (qo_frac). But it independently reads the material state each cycle (FL null). This matches a fractional distillation process where the operator maintains temperature awareness across cycles but re-evaluates what the material looks like each time.

## Data

- 616 consecutive B->B pairs from 162 B-track sequences
- 722 Mode B lines across 134 sequences (ordinal test)
- Bonferroni threshold p < 0.007 (7 signal variables)

## Provenance

- Phase 451 follow-up: S1-S5
- Builds on C1258 (parallel mode tracks), C1259 (gradient decomposition)
- Extends C1227 (FL resets are B-track internal) with direct propagation test
