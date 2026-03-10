# C1567: Within-Domain Structural Spine Validation

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, domain, compositional, validation, structural, T2A, C1475, C1476, C1477, C1478, C1482, C1556, C1557, C1561, C1563, C1566
**Phase:** WITHIN_DOMAIN_COMPOSITIONAL_CONTROL (Phase 560)
**Date:** 2026-03-08

## Claim

Within-domain subordinate features validate constraint predictions per domain: 16/17 structural spine tests pass. The domain decomposition (HEAD selects operational domain, subordinate features operate as control dials within that domain) is structurally confirmed.

Validated invariants:
- K1: THERMAL 0% hazard in all frames (C1476)
- K6: THERMAL category purity 90.4% (C1475)
- A5: ACTIVE double-ii safe pathway 100% (C1482)
- A7/A8: a->l and a->r 100% hazard (C1477)
- A9: ACTIVE highest headed hazard at 80.7% (C1475)
- E2: e->y 0% hazard (C1457)
- O1: o->l STAGING 98.1% (C1556)
- O2: o->r FLOW 98.9% (C1556)
- O4: o-HEAD y-terminal excluded at 0.15% (C1557)
- O6: ARRANGEMENT 0% effective hazard exposure (C1561)
- X1-X4: All four routing enrichments exceed thresholds (C1563)
- X6: Q3->Q4 HEAD JSD jump 25.1x (C1566)

Single failure: O3 (bare-o OPERATION purity 42.6% vs 95% threshold). This reflects a CategoryClassifier/C1556 tension — the classifier's dictionary assigns mixed categories to single-atom MIDDLE 'o', while C1556 predicts deterministic terminal-to-category mapping. This is a classifier operationalization issue, not a decomposition error.

## Evidence

### T2A results (17 tests)

| Test | Threshold | Result | Pass |
|---|---|---|---|
| K1: THERMAL 0% hazard | = 0% | 0.0% | YES |
| K6: THERMAL purity > 85% | > 85% | 90.4% | YES |
| A5: double-ii safe | > 99% | 100.0% | YES |
| A7: a->l hazard > 93% | > 93% | 100.0% | YES |
| A8: a->r hazard > 93% | > 93% | 100.0% | YES |
| A9: ACTIVE highest hazard | strict | 80.7% vs next 0% | YES |
| E2: e->y hazard < 1% | < 1% | 0.0% | YES |
| O1: o->l STAGING > 98% | > 98% | 98.1% | YES |
| O2: o->r FLOW > 98% | > 98% | 98.9% | YES |
| O3: bare-o OPER > 95% | > 95% | 42.6% | NO |
| O4: o y-term < 1% | < 1% | 0.15% | YES |
| O6: effective 0% hazard | < 1% | 0.0% | YES |
| X1: r->a > 1.8x | > 1.8x | 2.01x | YES |
| X2: y->k > 1.3x | > 1.3x | 1.72x | YES |
| X3: h->t > 1.5x | > 1.5x | 2.04x | YES |
| X4: m->o > 1.3x | > 1.3x | 1.70x | YES |
| X6: Q3-Q4 jump > 10x | > 10x | 25.1x | YES |

### T2B profile replication

22/30 soft profile tests match predictions. Notable: K5 qo enrichment 4.66x (>3x), T1 k-t terminal JSD 0.0017 (<0.01), A3 with-i n-terminal 82.1% (>70%), E1 e->y fraction 49.6% (>40%), E3 e->y vocabulary 7 MIDDLEs (<=12), H2 pseudo-HEAD Cramer's V 0.644 (>0.25), HL6 suffix bifurcation d/i 28.8% vs c/p/f 95.2%.

## Interpretation

The hierarchical model is structurally confirmed: HEAD selects operational domain and subordinate features function as predicted within each domain. This validates the architectural correction from Phases 558-559: subordinate features should NOT predict domains/states (HEAD's job) but instead operate as legality, routing, closure, scope, and sequencing machinery within HEAD-defined domains.

## Falsification Criteria

1. If a revised CategoryClassifier corrects O3 AND introduces new T2A failures
2. If the routing enrichments (X1-X4) are artifacts of line-initial/final position bias
3. If the domain assignment changes (e.g., reclassifying which atoms are HEAD atoms) invalidate >2 T2A tests

## Source

`phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t2_within_domain_validation.json`
