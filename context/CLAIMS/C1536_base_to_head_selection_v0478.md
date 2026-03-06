# C1536: Base-to-HEAD Selection V=0.478 -- Each Base Selects a Distinct Operational Domain

**Tier:** 2
**Scope:** GLOBAL, PREFIX, atom, base, HEAD, domain, selection, category, V=0.478, C1218, C1219, C1475, C1507
**Phase:** PREFIX_ATOM_TAXONOMY (Phase 544)
**Date:** 2026-03-06

## Claim

PREFIX base character (final position) predicts MIDDLE HEAD atom with chi-squared=21,946.2, p<0.001, Cramer's V=0.478. Each of the 8 base characters selects a distinct operational domain. V=0.478 is 89% of MIDDLE HEAD category specificity (V=0.511, C1475), making PREFIX base nearly as strong a domain selector as MIDDLE HEAD itself.

## Evidence

### Base-to-HEAD selection profiles (B tokens only)

| Base | Dominant HEAD | % | Second HEAD | % | Headless % | N |
|---|---|---|---|---|---|---|
| o | k (THERMAL) | 57.1 | t (FLOW) | 18.0 | 19.3 | 4,683 |
| h | e (STABILITY) | 65.7 | o (ARRANGE) | 11.9 | 10.3 | 6,993 |
| a | headless | 95.8 | k | 1.2 | 95.8 | 1,887 |
| k | e (STABILITY) | 49.0 | a (CONTAIN) | 39.1 | 7.6 | 2,228 |
| t | e (STABILITY) | 43.4 | a (CONTAIN) | 37.3 | 11.6 | 1,508 |
| l | k (THERMAL) | 37.8 | e (STABILITY) | 17.6 | 19.8 | 1,048 |
| e | e (STABILITY) | 52.4 | headless | 30.7 | 30.7 | 576 |
| r | a (CONTAIN) | 49.5 | o (ARRANGE) | 26.2 | 14.9 | 309 |

### Domain specialization summary

| Domain | Primary Base | Mechanism |
|---|---|---|
| THERMAL (k-HEAD) | o-base | qo=64% k-HEAD |
| STABILITY (e-HEAD) | h-base | ch/sh=66% e-HEAD |
| HEADLESS | a-base | da/sa/ka/ta=94-96% headless |
| STABILITY+CONTAINMENT | k-base, t-base | 49/43% e + 39/37% a |
| MIXED THERMAL/STABILITY | l-base | 38% k + 18% e |
| CONTAINMENT+ARRANGEMENT | r-base | 50% a + 26% o |

### Statistical test

Chi-squared = 21,946.2 (df=35), p < 0.001, Cramer's V = 0.478. N = 19,232 B tokens with PREFIX.

## Interpretation

The PREFIX base is a DOMAIN SELECTOR operating at nearly the same discriminative power as the MIDDLE HEAD atom itself. This confirms C1219 (base determines MIDDLE content) at HEAD-atom resolution and extends it beyond cosine similarity to categorical domain specificity. The o-base/THERMAL and h-base/STABILITY channels map directly to the two-channel thermal architecture (C1313). The a-base/HEADLESS pathway is the categorical gateway to the headless compound domain (C1488-C1498).

## Falsification Criteria

1. If V drops below 0.30 on replication
2. If any two bases have >80% HEAD profile overlap (JSD < 0.02)
3. If base-to-HEAD association is fully mediated by modifier (conditioning on modifier eliminates base effect)

## Source

`phases/PREFIX_ATOM_TAXONOMY/results/prefix_atom_taxonomy.json`
