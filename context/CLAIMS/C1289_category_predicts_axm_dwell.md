# C1289: Category Composition Predicts AXM Self-Transition Rate

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_MECHANISM_DECOMPOSITION (Phase 455)
**Date:** 2026-02-24

## Statement

Folio-level category composition predicts AXM self-transition rate. THERMAL fraction: rho=+0.520 (p<0.001). TRANSITION fraction: rho=-0.519 (p<0.001). Both survive Bonferroni correction. MARKING: rho=-0.249 (p=0.024, nominal only). Mean AXM self-rate=0.662, std=0.128. N=82 B folios.

## Architecture

- **Explains part of C1169 residual.** C1169 found 27% genuine design freedom in AXM self-transition variance (LOO R2=0.732). Category composition, specifically THERMAL and TRANSITION fractions, explains a substantial portion of this residual. High-THERMAL folios have sticky AXM states; high-TRANSITION folios have fluid state transitions.
- **Mechanistic connection to escape.** THERMAL drives AXM dwell (+0.520) AND drives escape via qo-PREFIX (C1277, rho=+0.780). TRANSITION drives AXM exit (-0.519) AND prevents escape (C1281, rho=-0.598). The same category axis (THERMAL vs TRANSITION) controls both AXM dynamics and escape probability.
- **AXM dwell = sustained processing.** AXM is the dominant macro-state (33/49 classes). High AXM self-transition means the system stays in its main operational mode. THERMAL vocabulary sustains this; TRANSITION vocabulary breaks it. In process terms: heating maintains the main loop, closing/finalizing exits it.

## Provenance

- Partially resolves C1169 (27% AXM residual variance)
- Connects C1277 (THERMAL escape mediation) and C1285 (TRANSITION role redirection) to macro-state dynamics
- Extends C1006 (AXM dwell is topology artifact) with category-mediated explanation
