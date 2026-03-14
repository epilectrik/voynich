# Phase 586: COMPATIBILITY_RECONSTRUCTION

**Status:** COMPLETE
**Date:** 2026-03-14
**Version:** 5.59
**Constraints:** C1696-C1701

## Purpose

Identify which deployment grammar layer creates the discrimination manifold's 0.873 clustering (C983). Phase 585 (C1695) showed atom composition does NOT predict co-occurrence (edge Jaccard 6.4%). This phase tests whether A-native structural constraints (section, folio pool, frequency, PREFIX) explain the manifold by progressive layered reconstruction.

## Critical Design Correction

Original plan applied Currier B grammar (zones, routing, hazards) to Currier A data. Expert review identified this as wrong: A is POSITION_FREE (C234) and NON_SEQUENTIAL (C240). Plan was revised to use only A-native constraints.

## Scripts

| Script | Runtime | Purpose |
|--------|---------|---------|
| `scripts/compatibility_reconstruction.py` | ~44s | 5 progressive models (D0-D4), 10 seeds each |

## Results

### Main Findings

| Model | Rule | Clustering | Jaccard | Precision | Recall | Density |
|-------|------|-----------|---------|-----------|--------|---------|
| Real | --- | 0.873 | 1.000 | 1.000 | 1.000 | 0.0217 |
| D0 | Global frequency | 0.639 | 0.237 | 0.380 | 0.386 | 0.0221 |
| D1 | +Section | 0.643 | 0.247 | 0.392 | 0.400 | 0.0222 |
| D2 | +Folio pool (uniform) | 0.674 | 0.239 | 0.318 | 0.491 | 0.0335 |
| D3 | +Folio pool (weighted) | 0.652 | 0.285 | 0.442 | 0.444 | 0.0218 |
| D4 | +PREFIX selectivity | 0.546 | 0.236 | 0.408 | 0.358 | 0.0190 |

### Progressive Increments

| Transition | Delta Clustering | Delta Jaccard |
|-----------|-----------------|---------------|
| D0 -> D1 | +0.004 | +0.010 |
| D1 -> D2 | +0.032 | -0.007 |
| D2 -> D3 | -0.022 | +0.045 |
| D3 -> D4 | -0.106 | -0.049 |

### Key Findings

1. **Frequency baseline is 0.639, not 0.25.** The CM null (0.25) measures random edge rewiring. D0 simulates actual co-occurrence through frequency-weighted line generation, which naturally produces clustering from hub overlap. The frequency distribution alone explains 73% of the manifold's clustering.

2. **The truly anomalous gap is 0.234** (0.873 - 0.639), not 0.623 (0.873 - 0.25). This gap is NOT explained by any deployment layer.

3. **Section conditioning is negligible** (+0.004 clustering). Currier A is mostly Herbal.

4. **Folio pool restriction adds moderate clustering** (+0.032) but inflates density (0.0335 vs real 0.0217). When density is corrected by frequency weighting (D3), clustering drops back but Jaccard improves.

5. **PREFIX selectivity hurts** (-0.106 clustering, -0.049 Jaccard). PREFIX constraints remove correct edges faster than incorrect ones.

6. **Best model by Jaccard: D3** (0.285). Only 28.5% of real edges reproduced.

## Constraint Verdicts

| C# | Verdict | Description |
|----|---------|-------------|
| C1696 | FREQUENCY_BASELINE_HIGH | D0 clustering 0.639: frequency distribution explains 73% of manifold clustering |
| C1697 | SECTION_EFFECT_NEGLIGIBLE | D1-D0 = +0.004 clustering; section conditioning irrelevant for A manifold |
| C1698 | FOLIO_POOL_MODERATE | D2-D1 = +0.032 clustering but density inflation; pool adds structure, not dominant |
| C1699 | FREQUENCY_CORRECTS_NOT_ADDS | D3-D2 = -0.022 clustering, +0.045 Jaccard; weighting corrects density, best edge match |
| C1700 | PREFIX_SELECTIVITY_HURTS | D4-D3 = -0.106 clustering, -0.049 Jaccard; PREFIX constraints misaligned with co-occurrence |
| C1701 | MANIFOLD_RESIDUAL_CONTENT | Best Jaccard 0.285; 0.234 clustering gap unexplained by deployment layers; residual = content specificity |

## Verdict

**DEPLOYMENT_INSUFFICIENT.** The manifold's 0.873 clustering is:
- 73% frequency distribution (natural hub overlap through co-occurrence)
- 4% folio pool restriction (vocabulary cliques)
- 23% unexplained (line-level content specificity — which MIDDLEs each folio chose for each line)

The "anomalous" clustering (0.873 vs CM null 0.25) is mostly a natural property of frequency-weighted co-occurrence, not a special structural feature. The truly anomalous residual (0.234) reflects content — the specific purpose of each line — which is the data itself, not a grammar rule.
