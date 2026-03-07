# C1564: Suffix Carries Zero Forward Information to Next HEAD

**Tier:** 2
**Scope:** B, suffix, HEAD, cross-token, information, null, compositionality, C1003, C1510, C1412, C1422
**Phase:** ATOM_ARCHITECTURE_CLEANUP (Phase 549)
**Date:** 2026-03-06

## Claim

Suffixed vs bare tokens produce near-identical next-HEAD distributions (JSD=0.0021). This is the smallest JSD in the entire Phase 549 analysis. Suffix is purely intra-token information with no inter-token forward propagation to HEAD domain selection. Extends C1003 (pairwise compositionality, no three-way synergy) to the cross-token boundary: suffix scope terminates completely at the token edge. Consistent with C1510 (suffix encodes outcomes/conditions not actions) -- outcomes of the current instruction do not alter the domain selection of the next instruction.

## Evidence

### Suffixed vs bare next-HEAD distribution

| Measure | Value |
|---|---|
| JSD (suffixed vs bare -> next HEAD) | 0.0021 |
| For comparison: articulated vs non-art HEAD JSD | 0.1092 |
| For comparison: header vs body MODIFIER JSD | 0.0850 |
| For comparison: Q3->Q4 HEAD JSD | 0.0185 |

JSD=0.0021 is effectively zero in the context of all other distributional comparisons in this phase, which range from 0.008 to 0.110.

### Interpretation

The suffix slot encodes OUTCOMES (what resulted) and CONDITIONS (what applies) per C1510, never ACTIONS or PARAMETERS. This finding shows that outcome information is also not FORWARD-PROPAGATED -- it does not influence what operational domain the next instruction selects. The next instruction's HEAD domain is determined by the current token's TERMINAL atom (C1563) and the next token's PREFIX (C1411), not by whether the current instruction was suffixed or bare.

### Information boundary

```
SUFFIX scope:  |<-- INTRA-TOKEN ONLY -->|
               |                        |
TOKEN N:  [PREFIX][MIDDLE][SUFFIX]   TOKEN N+1: [PREFIX][MIDDLE][SUFFIX]
                      |                                |
                 outcomes here                    not affected
                 do NOT propagate ------X------>  by N's suffix
```

## Falsification Criteria

1. If specific suffix types (e.g., -am, -edy) show significant next-HEAD divergence when analyzed individually
2. If the JSD increases substantially under higher-resolution analysis (e.g., at MIDDLE HEAD level rather than aggregate HEAD)
3. If cross-token suffix->HEAD coupling appears in specific sections or REGIMEs

## Source

`phases/ATOM_ARCHITECTURE_CLEANUP/results/atom_cleanup.json`
