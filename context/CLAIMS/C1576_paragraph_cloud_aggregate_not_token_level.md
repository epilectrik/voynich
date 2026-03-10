# C1576: Paragraph cloud operates at aggregate geometric level not per-token level

**Tier:** 2
**Phase:** 562 (SECTION_TEMPLATE_TRACE_EXECUTOR)
**Scope:** B, paragraph, cloud, folio, recovery, distributional, geometry, C1573

## Claim

Paragraph emphasis cloud under leave-one-out E3/E4 contextualization recovers folio-specific distributional geometry (P2 PASS: energy distance E4 <= 70% of E1 in 2/3 major sections), but does NOT improve per-token domain prediction. E3 domain = E2 for domain LL: paragraph-level kNN refinement at any weight is noisier than the folio average.

Paragraph cloud information operates at the aggregate geometric level (cloud shape distinguishes folios), not at the token level (knowing which paragraph a token is in does not predict its domain better than the folio average). This constrains future executor design: paragraph structure is a distributional signature, not a per-token prior.

## Evidence

- P2 cloud recovery: H ratio=0.382, B ratio=0.588, S ratio=0.767 (2/3 PASS at threshold 0.70)
- E4 < E2 energy distance in all 3 major sections (incremental PASS)
- E3 domain LL = E2 domain LL exactly when kNN weight = 0
- E3 domain LL < E2 domain LL at kNN weights of 5%, 20%, 80% (tested)
- C1573 demonstrated paragraph EMD folio specificity (z=6.21/5.06/2.34) — Phase 562 confirms this operates at aggregate level

## Provenance

- T4, T5: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/`
- Builds on: C1573 (paragraph EMD folio specificity)
