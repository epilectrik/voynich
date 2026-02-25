# C1296: Tail Type Category Divergence

**Tier:** 2
**Scope:** B
**Phase:** PARAGRAPH_TERMINATION_TRIGGER (Phase 457)
**Date:** 2026-02-24

## Statement

The 3 tail product types (C1232, K-means k=3 on PREFIX domain + MIDDLE family features, silhouette=0.236) have significantly different 8-category profiles. Chi2=139.1, analytic p<1e-22, permutation p=0.001. N=257 paragraphs with 3+ body lines. Cluster 0 is TRANSITION-enriched (20.1% vs 16.7% baseline), Cluster 2 is THERMAL-dominant (33.5% vs 20.6% Cluster 0). The form of termination covaries with operational category but the decision to terminate does not (C1295).

## Architecture

- **Tail form, not tail timing.** C1295 shows no line-level feature predicts WHEN termination occurs. C1296 shows HOW a paragraph terminates (which tail type) correlates with WHAT it was doing (category composition of final lines). Different operational themes produce different shutdown signatures.
- **Cluster 2 = THERMAL shutdown.** THERMAL 33.5% (1.63x enrichment over Cluster 0), OPERATION 16.5%. These paragraphs end with heating/energy vocabulary.
- **Cluster 0 = TRANSITION shutdown.** TRANSITION 20.1%, FLOW 21.5%. These paragraphs end with state-change and transfer vocabulary.
- **Cluster 1 = balanced.** No single dominant category; closest to the corpus average.
- **Connects to C1232 section correlation.** C1232 found tail types are section-correlated. The category divergence provides the mechanistic link: sections specialize by category (C1282), so section-typed paragraphs naturally produce section-typed tail signatures.

## Provenance

- Extends C1232 (3 tail product types, silhouette 0.212) with category-level analysis
- Connects C1282 (category-section differentiation) to paragraph closure mechanism
- Complements C1295 (termination memoryless) by distinguishing tail FORM from tail TIMING
