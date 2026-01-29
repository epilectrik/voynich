# C625: Hazard Circuit Token Mapping

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** HAZARD_CIRCUIT_TOKEN_RESOLUTION

## Statement

The 17 forbidden transitions map to the hazard circuit (C601: FL_HAZ -> FQ_CONN -> EN_CHSH) with directional bias: **6/12 classifiable forbidden pairs are reverse-circuit flows** (EN->FQ, EN->FL, FQ->FL), versus 29% reverse in all hazard transitions (Fisher p=0.193, odds ratio 2.44). Circuit topology (reverse + self-loop) explains **9/12 classifiable pairs (75%)**. Five forbidden pairs involve 4 tokens (c, ee, he, t) outside the 49-class system, of which ee and he have zero Currier B corpus occurrences.

## Evidence

### Sub-Group Classification

| Sub-Group | Classes | Forbidden Tokens |
|-----------|---------|-----------------|
| EN_CHSH | {8, 31} | chedy, shedy, chol, chey, shey |
| FQ_CONN | {9} | aiin, or, o |
| FQ_CLOSER | {23} | dy, r, l |
| FL_HAZ | {7, 30} | ar, dal, al |
| UNCLASSIFIED | -- | c, ee, he, t |

### Direction Distribution (Classifiable Only)

| Direction | Forbidden | All Hazard | Rate |
|-----------|-----------|------------|------|
| REVERSE | 6 | 77 | 7.8% |
| SELF_LOOP | 3 | 73 | 4.1% |
| FORWARD | 2 | 102 | 2.0% |
| CROSS_GROUP | 1 | 13 | 7.7% |
| UNCLASSIFIABLE | 5 | -- | -- |

Fisher's exact test (REVERSE vs non-REVERSE x forbidden vs not): odds ratio 2.44, p=0.193.

### Traffic Volume

| Direction | Volume | Unique Pairs |
|-----------|--------|-------------|
| FORWARD | 241 | 102 |
| SELF_LOOP | 219 | 73 |
| REVERSE | 145 | 77 |
| CROSS_GROUP | 44 | 13 |

Highest-traffic sub-group pair: FL_HAZ->EN_CHSH (96 volume, 42 unique) = FORWARD.

### Unclassified Tokens

| Token | B Occurrences | Kernel-Adjacent |
|-------|--------------|-----------------|
| c | 2 | No |
| ee | 0 | Yes |
| he | 0 | Yes |
| t | 3 | No |

ee and he are kernel-adjacent (e, h) but never appear as standalone tokens in Currier B. Their forbidden status is structurally trivial -- they cannot participate in any transitions.

## Interpretation

Reverse-circuit flows are over-represented among forbidden transitions at 2.44x, trending but not statistically significant (p=0.193) given the small sample of 12 classifiable pairs. The circuit direction FL->FQ->EN establishes a preferred flow, and 6/12 forbidden pairs block the reverse direction. Including 3 self-loop restrictions (within EN_CHSH and FL_HAZ), circuit topology explains 75% of classifiable forbidden transitions.

The 5 unclassifiable pairs (involving c, ee, he, t) are structurally trivial: ee and he have zero corpus occurrences, while c and t have 2-3 occurrences each. These are extreme-rarity tokens at the boundary of the classification system.

## Extends

- **C601**: Maps all 17 forbidden transitions to C601's circuit sub-groups
- **C624**: Resolves the 6.4% selectivity ratio -- forbidden transitions are directionally structured within the circuit

## Related

C109, C541, C542, C586, C601, C622, C623, C624
