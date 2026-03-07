# C1546: Universal HEAD Atom Hazard Source Immunity (All 5 HEADs at 0%, N=16,819)

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, hazard, immunity, universal, source, a, e, o, k, t, C1446, C1475, C1476, C1528
**Phase:** HAZARD_PREFIX_INTEGRATION (Phase 546)
**Date:** 2026-03-06

## Claim

ALL five HEAD atoms {a, e, o, k, t} have exactly 0% hazard source rate across 16,819 headed tokens (chi-squared=4411.9, V=0.219). No headed MIDDLE ever initiates a forbidden transition. All 1,537 hazard source tokens come exclusively from HEADLESS MIDDLEs (24.49% of 6,277 headless tokens). This EXTENDS C1446 (k-HEAD immunity) and C1476 (k-HEAD intrinsic immunity) from k alone to ALL HEAD atoms — hazard source immunity is a UNIVERSAL property of the HEAD slot, not a k-specific property.

## Evidence

### Per-HEAD source counts (B corpus, Phase 546 analysis)

| HEAD atom | Total tokens | Source tokens | Source rate |
|---|---|---|---|
| e | 7,002 | 0 | 0.000% |
| o | 2,717 | 0 | 0.000% |
| a | 3,079 | 0 | 0.000% |
| k | 3,100 | 0 | 0.000% |
| t | 921 | 0 | 0.000% |
| **All headed** | **16,819** | **0** | **0.000%** |
| HEADLESS | 6,277 | 1,537 | 24.486% |

Chi-squared = 4411.9, Cramer's V = 0.219, p < 0.0001.

### Three-way base x HEAD x hazard decomposition

Within EVERY PREFIX base, headed tokens have 0% source rate:

| Base | Headed source rate | Headless source rate |
|---|---|---|
| e-base | 0.0% | 22.4% |
| a-base | 0.0% | 13.3% |
| o-base | 0.0% | 8.0% |
| h-base | 0.0% | 4.7% |
| k-base | 0.0% | 2.0% |
| BARE | 0.0% | 8.2% |

HEAD immunity is INTRINSIC to the HEAD slot, not mediated by PREFIX base selection.

### The 9 hazard source MIDDLEs

All 9 source MIDDLEs in the 17 forbidden transitions begin with non-HEAD atoms: dy, l, c, he, chey, shey, chedy, shedy, chol. The first character of each is {d, l, c, h} — none from {a, e, o, k, t}.

## Interpretation

The HEAD+MOD*+TERM instruction grammar (C1394) places a DOMAIN-SELECTING atom at position 0. This domain selection categorically prevents the MIDDLE from being a hazard source. The mechanism is structural: HEAD atoms define operational domains (C1475) that are categorically incompatible with initiating forbidden transitions. Headless MIDDLEs lack this domain anchor and can enter hazard-source configurations. This makes HEAD presence vs absence the PRIMARY binary safety gate in the instruction grammar.

## Relationship to Prior Constraints

- **EXTENDS C1446** (k-HEAD complete hazard immunity): From k-only to all 5 HEAD atoms
- **EXTENDS C1476** (k-HEAD intrinsic immunity): Intrinsic property applies to entire HEAD class
- **CONFIRMS C1475** (HEAD categorical domain differentiation): Domain selection prevents hazard sourcing
- **CONNECTS C1528** (hazard classes map to distinct atom territories): Source territories are exclusively headless

## Falsification Criteria

1. If any headed MIDDLE is found to initiate a forbidden transition in extended corpus data
2. If HEAD-initial MIDDLEs are added to the forbidden pair set upon revision
3. If the 0% rate is shown to be an artifact of sample size (binomial upper bound at 95% CI: 0.022% for N=16,819)

## Source

`phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json`
