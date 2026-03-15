# Phase 593: TERMINAL_ROUTING_FOLIO_FINGERPRINT

**Status:** COMPLETE
**Date:** 2026-03-15
**Constraints:** C1721, C1722, C1723

## Objective

Test whether per-folio TERM→HEAD transition matrices (7 terminals × 6 HEADs = 42-cell vectors) vary across the 83 Currier B folios beyond noise and section effects, and whether that variation correlates with the apparatus manifold (C1670) or accent PCs (C1367). This directly addresses C1570's open falsification criterion #1: "If token-level (not folio-averaged) deployment features recover within-section folio discrimination."

## Method

- **Data:** 82 B folios, 61 with ≥100 MIDDLE-atom transitions (threshold 100; sensitivity at 50/100/150/200)
- **TERM extraction:** MIDDLE terminal atom via `decompose_middle_hmt()`, NOT suffix (C1564: suffix carries zero routing info)
- **HEAD extraction:** MIDDLE head atom via `decompose_middle_hmt()`
- **T0:** PCA on 61×42 transition proportion matrix → effective rank, top loadings, per-terminal variance
- **T1:** Per-folio 7×6 count matrices → proportion vectors (same-line consecutive pairs only)
- **T2:** Permutation distance test (JSD, 1000 shuffles) + ICC + folio-length confound check
- **T3:** Within-section discrimination (distance variance permutation test, 1000 shuffles per section) + REGIME confound
- **T4:** Mantel test (JSD × apparatus Euclidean, 57 overlapping folios) + partial Mantel (section-controlled)
- **T5:** Spearman correlations between routing PCs and accent PCs (FDR-corrected)

## Key Results

| Test | Metric | Value | Significance |
|------|--------|-------|-------------|
| T0 | Effective rank | 11 | vs apparatus 5.88 |
| T0 | PC1 / PC2 | 26.3% / 21.5% | bare→e, y→headless dominant |
| T2 | Mean JSD | 0.284 | < null p99 (0.289) |
| T2 | Token-shuffle p | 0.539 | NOT significant — folios MORE similar than random |
| T2 | ICC | 0.0015 | ≈ 0, CI crosses zero |
| T2 | Length confound rho | -0.635 | p < 1e-7, strong artifact |
| T3 | Section structure | p = 0.001 | Real |
| T3 | Within-section (B) | p = 0.913 | No folio discrimination |
| T3 | Within-section (C) | p = 0.991 | No folio discrimination |
| T3 | Within-section (H) | p = 1.000 | No folio discrimination |
| T3 | Within-section (S) | p = 0.846 | No folio discrimination |
| T4 | Mantel r | 0.279 | p = 0.001 |
| T4 | Partial Mantel r | 0.212 | p = 0.001 (section-controlled) |
| T5 | rPC1 × aPC1 | rho = 0.603 | q < 1e-5 |
| T5 | rPC3 × aPC3 | rho = 0.586 | q < 1e-5 |
| T5 | Significant correlations | 4/24 | FDR q < 0.05 |

## Interpretation

**Terminal routing is NOT a folio fingerprint.** The global TERM→HEAD routing grammar (C1563) is so dominant that individual folios are indistinguishable from each other — they are MORE similar than independent token-shuffling produces (mean JSD 0.284 < null p99 0.289, p=0.539). Within sections, folio routing profiles are pure noise (all p > 0.84). C1570 criterion #1 is NOT met.

**Routing IS section-parameterized and apparatus-correlated.** Section structure is real (p=0.001, silhouette=0.15). The section-level routing variation correlates with the apparatus manifold even after controlling for section identity (partial Mantel r=0.212, p=0.001). Routing PC1 aligns with accent PC1 (dynamics intensity, rho=0.603). The apparatus configuration parameterizes how strongly sections express the global routing grammar.

**The routing space is high-dimensional and bare-terminal dominated.** Effective rank 11 (vs apparatus 5.88). "Bare" terminal MIDDLEs (no terminal atom) contribute the most folio-to-folio variance (0.0061 vs 0.0029 for y-terminal). A strong length confound exists (rho=-0.635): short folios appear artifactually distinctive due to sampling variance. After length correction, effective rank drops to 8 and mean JSD drops to 0.083.

**Verdict: SECTION_ONLY with CROSS_SECTION_APPARATUS_LINK.** Routing variation is real at section level and tracks apparatus configuration, but does not reach individual folio granularity.

## Constraints

### C1721: Terminal routing is section-parameterized, not folio-specific
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Per-folio TERM→HEAD transition matrices (61 Currier B folios, ≥100 transitions each, 42-cell vectors from MIDDLE-atom decomposition) do NOT discriminate folios within sections. ICC = 0.0015 (≈0), token-shuffle null not exceeded (p=0.539, folios MORE similar than random). Within-section distance variance is indistinguishable from noise in all 4 tested sections (B: p=0.91, C: p=0.99, H: p=1.00, S: p=0.85). Section structure is real (p=0.001, silhouette=0.15). C1570 criterion #1 (token-level features discriminate folios within sections) is NOT met. The global routing grammar (C1563) homogenizes routing profiles within sections. Strong length confound (rho=-0.635): short folios appear artifactually distinctive.

### C1722: Section-level routing correlates with apparatus manifold
**Tier:** 2 (ESTABLISHED) | **Scope:** B

TERM→HEAD routing distance (JSD) correlates with apparatus manifold distance across 57 B folios: Mantel r=0.279 (p=0.001). This survives section control: partial Mantel r=0.212 (p=0.001). Routing PC1 aligns with accent PC1 (dynamics intensity): rho=0.603 (q<1e-5). Routing PC3 aligns with accent PC3: rho=0.586 (q<1e-5). 4/24 routing-accent correlations are FDR-significant. Apparatus configuration parameterizes how sections express the global routing grammar, but this parameterization operates at section level, not folio level.

### C1723: Routing space is high-dimensional and bare-terminal dominated
**Tier:** 2 (ESTABLISHED) | **Scope:** B

The TERM→HEAD routing space has effective rank 11 (11 PCs for 90% variance), nearly double the apparatus manifold's effective rank (5.88). PC1 (26.3%) loads on bare→e (+0.55) and bare→k (+0.33); PC2 (21.5%) loads on y→headless (+0.62) and bare→a (-0.39). "Bare" terminal MIDDLEs (no terminal atom) contribute the most cross-folio variance (0.0061) vs y-terminal (0.0029), l-terminal (0.0012), r-terminal (0.0008). The m-terminal row has near-zero variance (2.5e-5), consistent with m's rare, constrained role. High dimensionality reflects the 42-cell measurement space dispersing the section-level signal across many weakly-loaded PCs.

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/terminal_routing_fingerprint.py` | ~80 sec |

## Results

| File | Content |
|------|---------|
| `results/terminal_routing_fingerprint_results.json` | Full results: T0-T5 with PCA, JSD distances, ICC, permutation tests, Mantel/partial Mantel, accent correlations, sensitivity analysis, verdict |
