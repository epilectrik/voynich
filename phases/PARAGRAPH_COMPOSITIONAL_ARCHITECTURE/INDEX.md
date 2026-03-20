# Phase 615: Paragraph Compositional Architecture

**Status:** COMPLETE
**Verdict:** COMPOSITIONAL_ARCHITECTURE_CONFIRMED
**Constraints:** C1792-C1798
**Date:** 2026-03-20

---

## Research Question

How do paragraph-level specifications compose to produce folio-level operational identity? Two sub-questions:
1. **Sequential (Block A):** Do paragraph headers follow a transition grammar, and do headers specify body operational domain?
2. **Aggregate (Block B):** Does the set of paragraph shape features predict where a folio sits in the apparatus manifold?

## Blocking Tests

| Test | Description | Metric | Result | Verdict |
|------|-------------|--------|--------|---------|
| A1.5 | Header clusters independent of gallows | ARI=0.006 | Clusters are NOT recoding gallows | PASS |
| A1 | Expanded transition grammar | chi2=261 vs 53.7, z=5.18 | Non-random beyond gallows alone | PASS |
| A2 | Header divergence → body divergence | r=0.029, p=0.56 | No correlation | NULL |
| A3 | Specification compression arc | rho=-0.053, p=0.02 | Slight divergence, not convergence | REVERSED |
| A4 | Header atoms → body domain | dR2=+0.063, z=12.14 | Strong prediction beyond controls | PASS |
| B2 | Mantel: shape → manifold | r=0.314, partial r=0.281 | Significant, section-controlled | PASS |
| B2.5 | Per-section Mantel | Stars=0.257, Herbal=0.350, Bio=0.119 | Not section-driven | PASS |
| B3 | Feature-PC axis pairs | 15/110 significant after FDR | Multiple channels | PASS |
| B4 | Benchmark vs prior | r=0.314 > C1722 r=0.279 (22 vs 42 dim) | Competitive | PASS |

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| `scripts/compositional_architecture.py` | ~45s | `results/compositional_architecture_results.json` |

## Key Findings

- **Header transition grammar (C1792):** (gallows, header_cluster) state pairs follow non-random sequential transitions within folios (chi2=261, z=5.18). This is much richer than gallows-only transitions (chi2=53.7). Header clusters are independent of gallows type (ARI=0.006).
- **Consecutive header independence (C1793):** Header divergence does not predict body divergence (lag-1 r=0.029, lag-2 r=0.008). Paragraphs relate through state sequences, not similarity chains.
- **Specification divergence (C1794):** Later paragraphs within folios slightly diverge in header specification (rho=-0.053, p=0.02), refuting convergence predictions. Each paragraph maintains a distinct specification.
- **Header-to-body domain prediction (C1795):** Header atom fractions predict body operational domain beyond gallows+section controls (dR2=+0.063, z=12.14). The header specifies WHICH operational domain the body emphasizes.
- **Paragraph shape → apparatus manifold (C1796):** 22-dimensional paragraph shape vector predicts folio apparatus manifold position (Mantel r=0.314, partial r=0.281 controlling for section). First evidence that paragraph composition encodes folio-level operational identity.
- **Multi-section Mantel (C1797):** Effect is broad: Herbal r=0.350, Stars r=0.257, Bio r=0.119. Not driven by a single section.
- **Per-axis feature channels (C1798):** 15 significant feature-PC pairs after FDR. Dominant: zone_0 × PC1 (rho=-0.643), hdr_d × PC4 (rho=-0.475). Full shape vector (r=0.314) outperforms C1722 routing (r=0.279, 42 dim).

## Null/Reversed Results

- **A2 (consecutive independence):** Expected correlation, found none. Paragraphs don't relate through header similarity.
- **A3 (convergence):** Expected convergence, found slight divergence. Later paragraphs maintain or increase specification distinctness.

## Dependencies

- Phase 580 (apparatus manifold, 5 PCs)
- Phase 611-614 (gallows characterization, header specification grammar)
- C1722 (routing distance), C1709 (PP distance)
