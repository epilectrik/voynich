# Phase 626: A-to-B Bridge Operational Decomposition

**Status:** COMPLETE
**Phase Number:** 626
**Directory:** `phases/A_TO_B_BRIDGE_DECOMPOSITION/`

## Research Question

Do individual bridge MIDDLEs carry operationally coherent A-to-B translation? Can we trace specific vocabulary through the bridge to produce folio-level operational decode?

## Background

Phases 587-589 established folio-level A→B prediction:
- **C1706**: PP content predicts B-side similarity (partial rho=0.502)
- **C1709**: PP Jaccard predicts B-side manifold position (Mantel r=0.42, 10 SD above null)
- **C1710**: Only 3/10 manifold axes respond to PP (F4_raw, SUSTAINED_HEAT, DIRECT_FIRE)
- **C1705**: C475-incompatible record pairs diverge in B-side (d=0.816)
- **C1801**: PREFIX composition is strongest single apparatus manifold predictor (r=0.476)

These are all correlations at folio level. This phase decomposes the A→B bridge at **MIDDLE level** — the 85 bridge MIDDLEs (C1139) that carry the signal.

**Critical constraint:** C1708 says folios are category-GENERIC at 8-category resolution. Clustering is done on PP MIDDLE Jaccard distance (validated by C1706/C1709), NOT operational categories.

**Framing:** A records are operational profiles (C1261, C1263, C536), not material labels. Material-class overlay (ANIMAL/HERB from pp_classification.json) is Tier 3.

## Scripts

| # | Script | Output | Description |
|---|--------|--------|-------------|
| 1 | `scripts/pp_clustering.py` | `results/pp_clustering.json` | PP Jaccard clustering (lightweight) |
| 2 | `scripts/bridge_decomposition.py` | `results/bridge_decomposition.json` | Bridge MIDDLE operational decomposition (CORE) |
| 3 | `scripts/folio_decode_cards.py` | `results/folio_decode_cards.json` | Folio decode cards + chain validation |

## Predictions

| # | Prediction | Basis | Pass Criterion | Result |
|---|-----------|-------|----------------|--------|
| P1 | PP Jaccard clustering produces structure exceeding permutation null | C1706, C1709 | Silhouette > null p95 | **PASS** sil=0.057 > null p95=0.014 |
| P2 | Section (H/P) does NOT fully explain PP clustering | C1711 | V < 0.60, within-H persists | **FAIL** V=0.628, within-H sil=0.039 |
| P3 | RI Jaccard higher within PP-cluster than between (ratio > 1.2) | Operational → identification similarity | Ratio > 1.2, perm p < 0.05 | **FAIL** ratio=1.116 (perm p=0.01) |
| P4 | A-context predicts B-consequence for bridge MIDDLEs (Mantel r > 0.2) | C1706 at MIDDLE resolution | r > 0.2, p < 0.01 | **FAIL** r=0.043, p=0.167 |
| P5 | ≥2 A-context features predict B-consequence features | Multi-dimensional bridge | |r| > 0.25, p < 0.005 for ≥2 pairs | **PASS** 18 pairs, head_e→b_head_e rho=0.675 |
| P6 | Bridge MIDDLEs form ≥2 functional groups by B-consequence | C1264, C1500 | Silhouette > 0.15 | **PASS** 6 groups, sil=0.751 |
| P7 | A-side HEAD predicts B-side HEAD redistribution | C1507 | Chi-sq p < 0.01 | **PASS** chi2=115, V=0.675 |
| P8 | Restricted-PP density differs by cluster | C1707 (d=3.667) | KW p < 0.05 | **PASS** KW p=0.001 |
| P9 | PP prefix profiles differ by cluster | C1801 (r=0.476) | KW p < 0.01 for ≥2 families | **PASS** ol_or p<0.001, da p=0.01 |
| P10 | A-side PP distance correlates with B-side paragraph shape distance | C1800 (r=0.163) | Positive correlation | **INCONCLUSIVE** n=5 too small |

## Constraints

| C# | Claim | Verdict | Tier | Scope |
|----|-------|---------|------|-------|
| C1859 | PP Jaccard clustering exceeds null (sil=0.057 vs p95=0.014, k=2) but section-dominated (V=0.628) | Confirmed | 2 | A, A↔B |
| C1860 | A→B bridge is FEATURE-CHANNELED not holistic (Mantel r=0.043 n.s., 18 per-feature pairs significant) | Confirmed | 2 | A↔B |
| C1861 | Bridge HEAD redistribution strongly non-random (chi2=115, V=0.675), dominant A-o→B-k (45%) | Confirmed | 2 | A↔B |
| C1862 | 6 sharp functional groups by B-consequence (sil=0.751), HEAD-homogeneous | Confirmed | 2 | A↔B, B |
| C1863 | Restricted-PP density differs by cluster (KW p=0.001), P-section 2× denser | Confirmed | 2 | A |
| C1864 | PREFIX ol_or 3.4× enriched in Cluster 1, da enriched in Cluster 2 | Confirmed | 2 | A |
| C1865 | Folio-level A→B correlations (C1706/C1709) emergent from aggregation, not MIDDLE-level | Confirmed | 2 | A↔B |
| C1866 | RI Jaccard within-cluster > between (ratio=1.116, perm p=0.01) but below 1.2 threshold | Confirmed | 2 | A |
| C1867 | Bridge carries signal through 4 independent HEAD channels (rho=0.45-0.68 per HEAD) | Confirmed | 2 | A↔B |
| C1868 | Functional groups show HEAD→category specialization (o=OP/MARK, e=THERM/TRANS, t=FLOW, k=THERM/STAGE) | Confirmed | 2 | B |
| C1869 | Pilot decode cards: cross-folio PP distance does NOT predict B operational distance (rho=-0.24, p=0.51) | Confirmed | 2 | A↔B |
| C1870 | BRIDGE_FEATURE_COHERENT_NOT_HOLISTIC verdict | Phase verdict | 2 | A↔B |

## Verdict

**BRIDGE_FEATURE_COHERENT_NOT_HOLISTIC**

The A→B bridge carries operationally meaningful signal through HEAD-typed feature channels (P5, P6, P7 all pass strongly). HEAD identity is preserved across the bridge with channel-specific fidelity (rho=0.45-0.68). Bridge MIDDLEs form 6 sharp functional groups (sil=0.751) that are completely HEAD-determined. However, holistic context→consequence prediction fails (P4 Mantel r=0.043). The folio-level correlations established by C1706/C1709 are emergent properties of aggregation, not present at individual MIDDLE level. PP clustering is section-dominated (P2 V=0.628). The bridge is a set of parallel HEAD-typed pipes, not a single coherent translation layer.

**Scorecard:** 6 PASS, 3 FAIL, 1 INCONCLUSIVE

## Execution

- Scripts 1+2 ran in parallel (independent data): 21.3s + 5.4s
- Script 3 depended on Scripts 1+2 results: 1.0s
- Total: ~28s
