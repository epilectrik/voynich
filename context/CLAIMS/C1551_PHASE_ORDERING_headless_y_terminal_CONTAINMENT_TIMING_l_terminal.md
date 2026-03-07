# C1551: PHASE_ORDERING Is Exclusively Headless y-Terminal; CONTAINMENT_TIMING Is Exclusively l-Terminal

**Tier:** 2
**Scope:** B, MIDDLE, hazard, PHASE_ORDERING, CONTAINMENT_TIMING, headless, y-terminal, l-terminal, dy, l, PREFIX, C1529, C1530, C1547, C1546
**Phase:** HAZARD_PREFIX_INTEGRATION (Phase 546)
**Date:** 2026-03-06

## Claim

The two dominant hazard classes have completely distinct atom-level signatures. PHASE_ORDERING (41% of forbidden transitions) is carried exclusively by the headless y-terminal MIDDLE 'dy' (675 corpus tokens, 100% of PHASE_ORDERING sources). CONTAINMENT_TIMING is carried exclusively by the l-terminal MIDDLE 'l' (855 corpus tokens, 100% of CONTAINMENT_TIMING sources). Both are spread across multiple PREFIXes — the hazard is MIDDLE-intrinsic, not PREFIX-induced. This confirms C1529 and C1530 at PREFIX-integrated resolution and adds the PREFIX distribution evidence.

## Evidence

### PHASE_ORDERING source MIDDLEs (B corpus, Phase 546)

| Source MIDDLE | Corpus tokens | HEAD status | Terminal atom | PREFIXes observed |
|---|---|---|---|---|
| dy | 675 | HEADLESS (d-initial) | y | ch (305), sh (111), BARE (95), qo (66), ok (38), ot (30), da (12), + others |
| chey | 0 | PHANTOM | y | — |
| shey | 0 | PHANTOM | y | — |

All PHASE_ORDERING sources are: 100% headless, 100% y-terminal. The sole corpus-present source ('dy') appears under 10+ different PREFIXes, confirming the hazard is MIDDLE-determined.

### CONTAINMENT_TIMING source MIDDLEs (B corpus, Phase 546)

| Source MIDDLE | Corpus tokens | HEAD status | Terminal atom | PREFIXes observed |
|---|---|---|---|---|
| l | 855 | HEADLESS (l-initial) | l (bare) | qo (315), ch (155), al (94), sh (73), ok (60), ot (52), da (30), + others |
| chol | 0 | PHANTOM | l | — |

All CONTAINMENT_TIMING sources are: 100% headless, 100% l-terminal. The sole corpus-present source ('l') appears under 12+ different PREFIXes.

### PREFIX distribution of hazard sources

'dy' under ch-PREFIX: 305 tokens (45.2% of dy)
'dy' under sh-PREFIX: 111 tokens (16.4%)
'dy' under BARE: 95 tokens (14.1%)
'dy' under qo-PREFIX: 66 tokens (9.8%)

'l' under qo-PREFIX: 315 tokens (36.8% of l)
'l' under ch-PREFIX: 155 tokens (18.1%)
'l' under al-PREFIX: 94 tokens (11.0%)

Both source MIDDLEs are distributed across all major PREFIX channels — no single PREFIX drives the hazard. PREFIX modulates the RATE of hazard exposure (C1548, C1549) but not the EXISTENCE of hazard-capable MIDDLEs.

## Interpretation

The two dominant hazard classes map to two specific atom-level MIDDLE configurations:
- PHASE_ORDERING = {d-initial, y-terminal} = "seal-end" (C1195 glosses: d=seal, y=end) — sequencing failure when a sealing closure is followed by incompatible operations
- CONTAINMENT_TIMING = {l-initial, l-terminal} = "state" (C1385: l=state/condition marker) — containment failure when a staging/state token is followed by incompatible operations

This decomposition explains WHY these two classes dominate: 'dy' and 'l' are among the most common MIDDLEs in the corpus, appearing under many PREFIXes. The hazard topology is built on the most FREQUENT headless MIDDLEs, not on rare or specialized ones.

## Falsification Criteria

1. If a non-y-terminal MIDDLE is found to source PHASE_ORDERING violations
2. If a non-l-terminal MIDDLE is found to source CONTAINMENT_TIMING violations
3. If PREFIX identity significantly modulates which hazard CLASS a source MIDDLE feeds into (currently, CLASS is 100% MIDDLE-determined)

## Source

`phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json`
