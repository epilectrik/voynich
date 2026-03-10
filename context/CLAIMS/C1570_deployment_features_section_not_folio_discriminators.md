# C1570: Deployment Features Are Section-Level Not Folio-Level Discriminators

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, domain, compositional, deployment, zone, routing, closure, headless, paragraph, section, folio, within-section, discrimination, C1463, C1464, C1466, C1486, C1563, C1567, C1568, C1569
**Phase:** WITHIN_DOMAIN_COMPOSITIONAL_CONTROL (Phase 560b)
**Date:** 2026-03-08

## Claim

Deployment features — zone-conditioned domain profiles, adjacency routing motifs, closure packaging, headless v2 decomposition, and paragraph-conditioned emphasis — are valid structural instruments (T2b: 18/19 pass) and improve section-level classification (RF +6.1pp, COMBINED 90.4%) but do NOT recover within-section folio discrimination **when summarized at folio-average resolution**. D3b tests 0/18 section-set combinations across 6 feature sets (6 to 94 dimensions). Folio specificity is not in deployment packaging at folio-average resolution.

## Evidence

### T2b Instrument Validation

| Tier | Tests | Pass | Threshold |
|------|-------|------|-----------|
| T2bA (constraint replication) | 11 | 10 | ≥10 |
| T2bB (instrument sanity) | 8 | 8 | ≥6 |

Only failure: Z2 IMMUNE-hazard enrichment at WORK zone (1.038 vs 1.1x threshold). All other zone, routing, closure, and paragraph tests pass.

### D3b Within-Section Pairwise Distance (PRIMARY)

Null model: within-domain cross-folio token shuffle preserving domain counts, 100 seeds per section per feature set. Pass threshold: real > null + 2σ in ≥2/3 sections.

| Feature Set | Stars | Herbal | Bio | Overall |
|-------------|-------|--------|-----|---------|
| HEAD (6) | FAIL | FAIL | FAIL | 0/3 |
| MARGINAL (32) | FAIL | FAIL | FAIL | 0/3 |
| DEPLOYMENT (56) | FAIL | FAIL | FAIL | 0/3 |
| FULL_560 (38) | FAIL | FAIL | FAIL | 0/3 |
| FULL_560b (62) | FAIL | FAIL | FAIL | 0/3 |
| COMBINED (94) | FAIL | FAIL | FAIL | 0/3 |

Real pairwise distances are SMALLER than null in most cases — real folios are MORE similar than shuffled versions.

### D5b RF Gain

| Feature Set | RF Accuracy |
|-------------|------------|
| FULL_560 | 84.3% |
| FULL_560b | 85.5% |
| COMBINED | 90.4% |

RF gain COMBINED vs FULL_560: +6.1pp (exceeds 3pp threshold).

### D7 Variance Decomposition

52/56 deployment features have within-section variance ratio > 0.5. Both marginal (31/32) and deployment features carry mostly within-section variance. Section discrimination comes from patterns across features, not individual feature levels.

## Interpretation

The exhaustive D3b result (0/18 across 94 dimensions in 6 feature sets) conclusively establishes that folio-average features — whether marginal domain profiles or deployment packaging — cannot distinguish folios within sections. The section template determines both domain tuning AND deployment grammar. Folio individuality resides in HEAD proportions (domain mix) plus stochastic token-level freedom within section-determined templates.

## Falsification Criteria

1. If token-level (not folio-averaged) deployment features recover within-section folio discrimination
2. If line-level or paragraph-level (not folio-averaged) deployment patterns show folio specificity
3. If a different null model (e.g., section-conditioned generation model) produces different D3b results

## Source

`phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t4b_synthesis.json`
`phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t3b_discriminability.json`
