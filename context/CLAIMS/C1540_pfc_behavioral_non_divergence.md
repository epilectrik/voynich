# C1540: p/f/c behavioral non-divergence vs stable MODs

**Tier:** 2
**Scope:** GLOBAL, atom, cross-system, instability, JSD, behavioral, C1509, C1499

## Claim

The three "unstable" atoms {p,f,c} identified by C1509 have LOWER mean cross-system JSD(A,B) than the "stable" modifier atoms {i,d,s}: 0.0110 vs 0.0319 (ratio 0.35x). C1509's instability label reflects FUNCTIONAL NICHE specialization (context shifts around the atom), not overall behavioral divergence (the atom's own profile shifting). p/f/c are contextually sensitive but behaviorally stable.

## Evidence

Mean JSD(A,B) across 8 behavioral dimensions (head, terminal, suffix_presence, prefix_base, line_position, paragraph_position, articulator, headed_status):

| Atom | Tier | Mean JSD |
|------|------|----------|
| p | UNSTABLE | 0.0074 |
| c | UNSTABLE | 0.0116 |
| f | UNSTABLE | 0.0141 |
| i | STABLE | 0.0197 |
| s | STABLE | 0.0193 |
| d | STABLE | 0.0567 |

UNSTABLE mean = 0.0110, STABLE_MOD mean = 0.0319, ratio = 0.35x.

The most divergent modifier is d (0.0567), classified as MODERATE in C1509 (not UNSTABLE). d's divergence is driven by headless rate shift (A: 55.1% -> B: 29.0%, delta = 26.1pp) and terminal profile changes (JSD = 0.0919).

## Methodology

Phase 545 analysis. JSD computed as squared Jensen-Shannon divergence between A and B distributions for tokens containing each atom in MIDDLE position. 8 independent behavioral dimensions measured. N: c=3,420 (A=1,324 + B=2,096), p=933 (A=295 + B=638), f=330 (A=115 + B=215).

## Constraints

- Refines C1509 (three-tier stability): instability is NOT behavioral divergence
- Extends C1499 (shared substrate): p/f/c maintain shared behavior despite context shifts
- Consistent with C1509 internal/external JSD ratio 0.41: MIDDLE stable, context shifts

## Phase

Phase 545: Executive Atom Instability
