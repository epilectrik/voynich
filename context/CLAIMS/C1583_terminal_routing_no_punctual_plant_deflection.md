# C1583: Terminal routing grammar does NOT produce observable punctual plant deflections

**Tier:** 2
**Phase:** 563 (VIRTUAL_APPARATUS_COUPLING)
**Scope:** B, virtual apparatus, routing, terminal, negative, C1563, C1564, C1470

## Claim

Core terminal routing grammar (C1563: r->a 2.23x, h->t 1.89x, y->k 1.60x, m->o 1.55x) does NOT produce observable isolated local plant deflections at token level. 0/4 routing signatures are directionally correct (rates 0.45-0.50, near chance at window=5). Routing effect is absorbed into sustained domain dynamics, not measurable as punctual single-token deflection. This is a MECHANISTIC finding: routing operates as sustained domain rebalancing over line segments, not as single-token state kicks.

## Evidence

- P4 routing consequence: 0/4 routing signatures directionally correct
- Routing detection rates: ~0.45-0.50 at window=5 (indistinguishable from chance baseline ~0.50)
- All 4 major routing pairs tested: r->a, h->t, y->k, m->o
- Consistent with C1564 (suffix carries zero forward HEAD information, JSD=0.0021)
- Consistent with C1470 (cross-line hazard correlation entirely folio-mediated)

## Provenance

- T5: `phases/VIRTUAL_APPARATUS_COUPLING/scripts/t5_plant_behavior_validation.py`
- Builds on: C1563 (terminal-to-next-HEAD routing grammar), C1564 (suffix zero forward info), C1470 (cross-line hazard folio-mediated)
