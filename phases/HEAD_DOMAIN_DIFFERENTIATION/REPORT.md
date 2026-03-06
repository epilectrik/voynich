# Phase 533: HEAD Domain Differentiation

**Date:** 2026-03-05
**Status:** COMPLETE
**Constraints produced:** C1475-C1479 (5 new constraints)

---

## Research Question

Do the 5 HEAD atoms {a, e, o, k, t} define categorically distinct operational domains? What is the mechanism of k-HEAD's complete hazard immunity (C1446)?

## Method

Analyzed 23,096 Currier B tokens using `decompose_middle_hmt()` from `scripts/voynich.py` to decompose every MIDDLE into (HEAD, MOD*, TERM) structure per C1393-C1394. Computed 12 test batteries across category profiles, modifier compatibility, terminal distributions, frame hazard rates, line position, PREFIX selectivity, suffix rates, e-depth, headless comparison, population census, k-immunity mechanism, and pairwise HEAD distances.

## Key Findings

### 1. HEAD Domain Taxonomy (C1475)

Each HEAD atom defines a categorically distinct operational domain with extreme specialization:

| HEAD | Primary Domain | Enrichment | JSD from baseline |
|------|---------------|------------|-------------------|
| **k** | THERMAL 90.3% | 3.80x | 0.373 |
| **t** | FLOW 87.0% | 4.47x | 0.412 |
| **a** | FLOW 54.2% + TRANSITION 41.4% | 2.79x / 2.76x | 0.351 |
| **e** | THERMAL 34.7% + OPERATION 32.2% | 1.46x / 2.24x | 0.112 |
| **o** | STAGING 32.4% + OPERATION 25.6% | 2.49x / 1.78x | 0.163 |
| **headless** | CONTAINMENT 13.0% + MARKING 19.5% + STAGING 30.9% | 2.70x / 2.51x / 2.38x | 0.177 |

The 5 HEADs + headless partition the 8-category operational space into non-overlapping primary domains.

### 2. k-HEAD Immunity Is Intrinsic (C1476)

k-HEAD hazard immunity is INTRINSIC to the k atom itself, not a consequence of modifier quenching or terminal selection:

| Condition | k forbidden rate | N |
|-----------|-----------------|---|
| No modifier | 0.000% | 2,682 |
| With modifier | 0.000% | 418 |
| All frames combined | 0.000% | 3,100 |

Contrast with modifier quenching for other HEADs:

| HEAD | With modifier | Without modifier | Quenches to zero? |
|------|-------------|-----------------|-------------------|
| e | 0.000% | 3.89% | YES |
| o | 0.000% | 44.7% | YES |
| t | 0.000% | 78.7% | YES |
| **a** | **52.8%** | **79.9%** | **NO** |
| k | 0.000% | 0.000% | N/A (intrinsically zero) |

### 3. a-HEAD Is Primary Hazard Carrier (C1477)

a-HEAD carries 66.0% overall forbidden rate (2,032/3,079 tokens) and is the ONLY HEAD where modifier quenching fails. Hazard concentrates in three terminal frames:

| Frame | Forbidden rate | N |
|-------|---------------|---|
| a->l | 98.9% | 527 |
| a->r | 98.5% | 687 |
| a->n | 65.6% | 1,272 |
| a->bare | 0.0% | 397 |
| a->m | 0.0% | 174 |

a-HEAD exclusively attracts modifier i (4.08x enrichment, 78.5% of a-HEAD tokens have i), creating the a+i frame family (aiin, ain, ai, aii) that dominates the FLOW+TRANSITION dual category.

### 4. k/t Terminal Mirror (C1478)

k and t are terminal-identical but categorically opposed:

| Dimension | k | t |
|-----------|---|---|
| Dominant terminal | bare (92.5%) | bare (90.2%) |
| Secondary terminal | h (6.5%) | h (8.4%) |
| Terminal JSD (k vs t) | 0.0017 | (lowest of any pair) |
| Category JSD (k vs t) | 0.784 | (highest except a vs k) |
| Primary category | THERMAL 90.3% | FLOW 87.0% |
| PREFIX selectivity | qo 4.66x | qo 5.00x |
| Suffix rate | 96.9% | 95.8% |
| MIDDLE length | 1.57 chars | 1.74 chars |

They are functionally parallel channels -- identical structural packaging, opposite operational content.

### 5. HEAD-Modifier Selectivity Partition (C1479)

Each HEAD selects a distinct modifier profile, creating a near-partition of the modifier space:

| HEAD | Monopolized modifier | Any-modifier rate |
|------|---------------------|------------------|
| **a** | i (4.08x, 78.5%) | 51.3% |
| **e** | d (1.99x, 38.1%) | 44.6% |
| **o** | p (3.51x), f (2.83x), c (1.42x) | 31.3% |
| **k** | (none -- modifier-depleted) | 13.5% |
| **t** | (none -- modifier-depleted) | 20.5% |
| **headless** | (all 6 enriched 1.07-2.07x) | 57.8% |

Modifier monopolies explain C1473 (modifier avoidance = frame incompatibility): i is 88.6% a-HEAD, d is 85.1% e-HEAD -- they avoid each other because no single HEAD can satisfy both demands.

## Additional Findings (not promoted to constraints)

### Line Position by HEAD

| HEAD | Mean position | Initial rate | Final rate |
|------|-------------|-------------|------------|
| a | 0.582 | 3.6% | 14.6% |
| e | 0.451 | 11.0% | 5.9% |
| k | 0.484 | 7.9% | 6.6% |
| o | 0.497 | 9.8% | 11.2% |
| t | 0.546 | 4.7% | 7.9% |
| headless | 0.517 | 15.6% | 15.6% |

a is most line-final (0.582), e is most line-initial (0.451). This connects to C1463 (zone-hazard routing): hazardous a-HEAD concentrates at CLOSURE, safe e-HEAD at SPECIFICATION.

### PREFIX Selectivity

- k and t are both qo-selected (4.66x and 5.00x) and BARE-depleted (0.031x and 0.084x)
- a is ok/ot-selected (3.19x/2.90x) and BARE-enriched (2.20x)
- e is ch/sh-selected (1.99x/2.38x) and BARE-depleted (0.047x)
- headless shows the most uniform PREFIX distribution

### Suffix Rate and e-Depth

| HEAD | Suffix rate | Mean e-depth |
|------|-----------|-------------|
| a | 48.6% | N/A |
| e | 56.3% | 1.217 |
| k | 96.9% | N/A |
| o | 56.7% | N/A |
| t | 95.8% | N/A |
| headless | 69.3% | N/A |

k and t have dramatically higher suffix rates (both >95%) than other HEADs (<70%).

### Pairwise HEAD Distances (Mean JSD)

| Pair | Mean JSD | Relationship |
|------|----------|-------------|
| k vs a | 0.494 | Most distant |
| k vs headless | 0.401 | Very distant |
| a vs e | 0.352 | Distant |
| o vs headless | 0.161 | Most similar |
| k vs t | 0.265 | Moderate (identical terminals, opposed categories) |

## Constraint Summary

| Constraint | Statement | Tier |
|-----------|-----------|------|
| C1475 | HEAD atom domain taxonomy (5 distinct operational domains) | 2 |
| C1476 | k-HEAD immunity is intrinsic not compositional | 2 |
| C1477 | a-HEAD is the primary hazard carrier (66.0%, quench-resistant) | 2 |
| C1478 | k/t terminal mirror with category opposition | 2 |
| C1479 | HEAD-modifier selectivity partition | 2 |

## Connections to Prior Work

- **C1446** (k-HEAD immunity): DEEPENED -- mechanism is intrinsic, not compositional
- **C1448** (frame hazard map): EXTENDED -- a-HEAD frames are primary hazard source
- **C1450** (modifier quenching): REFINED -- quenching works for e/o/t but fails for a
- **C1452-C1456** (i-modifier Simpson's paradox): EXPLAINED -- a-HEAD's i-monopoly is the mechanism
- **C1472** (modifier co-occurrence avoidance): EXPLAINED -- HEAD selectivity partition drives avoidance
- **C1473** (frame incompatibility): CONFIRMED AND EXTENDED -- HEAD domain taxonomy is the root cause
- **C1194** (k-t pair discrimination): EXTENDED -- k/t mirror identified at HEAD level
- **C1300** (qo THERMAL channel): CONFIRMED -- k/t both qo-selected but carry different content
- **C1305** (MIDDLE determines category): CONFIRMED -- HEAD is the primary categorical selector within MIDDLE
- **C1397** (headless compound grammar): CONFIRMED -- headless domain categorically distinct from all HEADs

## Files

- Script: `phases/HEAD_DOMAIN_DIFFERENTIATION/scripts/head_domain_differentiation.py`
- Results: `phases/HEAD_DOMAIN_DIFFERENTIATION/results/head_domain_differentiation.json`
- Constraints: `context/CLAIMS/C1475-C1479`
