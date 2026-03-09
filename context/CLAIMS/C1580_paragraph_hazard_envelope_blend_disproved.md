# C1580: Paragraph domain composition does NOT predict line hazard envelope

**Tier:** 2
**Phase:** 562b (SECTION_TEMPLATE_TRACE_EXECUTOR closure+paragraph mini-audit)
**Scope:** B, paragraph, hazard, envelope, cloud, blend, negative

## Claim

Paragraph domain composition does NOT reliably predict the distribution of line-level hazard envelopes. E3 hazard LL with paragraph envelope blend (weight=0.3) is WORSE than E2 hazard LL: -1.097 vs -1.092 (delta -0.005). Within-paragraph hazard envelope standard deviation (0.563) exceeds between-paragraph standard deviation (0.090), confirming paragraphs are not envelope-consistent.

This disproves the hypothesis that paragraph cloud geometry can be projected to line-level hazard expectations. Paragraph cloud information (C1573, C1576) operates at aggregate geometric level (folio-specific cloud shape), not at line-level hazard prediction. For 563 (virtual apparatus coupling), paragraph cloud should be treated as an offline trace-distribution validator, not an online hazard controller input.

## Evidence

- E2 hazard mean LL: -1.092
- E3 hazard mean LL (blend=0.3): -1.097 (WORSE)
- Within-paragraph envelope std: 0.563
- Between-paragraph envelope std: 0.090
- Overall composite E3 still > E2 (+0.017) only because CTS closure gain (+0.039) overwhelms hazard degradation

## Provenance

- T8, T9: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/`
- Builds on: C1573 (paragraph EMD folio specificity), C1576 (paragraph cloud aggregate not token-level)
