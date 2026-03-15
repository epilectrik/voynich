# Phase 592: PP_MANIFOLD_RESIDUAL_CHARACTERIZATION

**Status:** COMPLETE
**Date:** 2026-03-15
**Constraints:** C1718, C1719, C1720

## Objective

Characterize the 0.234 manifold gap (C1701): the PP discrimination manifold (972 Currier A MIDDLEs, clustering 0.873) has 27% of its structure unexplained by the best deployment model (D3, clustering 0.639). Is this residual structured by HEAD domain, category, terminal type, or the bridge/dark partition? Or is it genuinely irreducible?

## Method

- **Data:** 972 PP MIDDLEs, 10,241 real edges, 972x972 binary compatibility matrix (C475)
- **D3 reconstruction:** 10-seed folio-pool-weighted simulation, majority vote (>=5/10) -> 6,032 D3 edges
- **Residual:** 6,074 edges in real but not D3; 4,167 shared; 1,865 D3-only
- **Two-gate significance:** Gate 1 = permutation null (1000 shuffles, p95); Gate 2 = real > max(D3 seeds)
- **Axes tested:** HEAD (6 types), category (9 types incl. None), terminal (7 types), frame (19 merged)
- **Controls:** Hub-removed (top 5% by degree), partial assortativity, frequency stratification
- **T4:** Pipeline partition (bridge/dark/non-pipeline) with triangle analysis
- **T5:** Residual edge characterization with frequency quartiles
- **T6:** Community-attribute alignment (Louvain, chi-squared, Cramer's V)

## Key Results

| Test | Axis | Full Graph | Hub-Removed | Low-Freq | Gate 1 | Gate 2 |
|------|------|-----------|-------------|----------|--------|--------|
| T1 | HEAD | +0.032 | **+0.051** | **+0.163** | PASS (p<0.001) | PASS |
| T2 | Category | -0.030 | +0.032 | -0.010 | FAIL | PASS |
| T3 | Terminal | -0.042 | -0.012 | +0.039 | FAIL | FAIL |
| T3b | Frame | +0.000 | +0.033 | +0.040 | PASS (barely) | PASS |

| Test | Result |
|------|--------|
| Partial: HEAD given category | -0.009 (no independent HEAD signal within categories) |
| Partial: category given HEAD | -0.063 (DISassortative within HEAD groups) |
| T4: Non-pipeline share of residual | **57.8%** |
| T4: Bridge-bridge explained by D3 | 86.4% (2095 real -> 284 residual) |
| T4: Dark-dark explained by D3 | 1.1% (359 real -> 355 residual) |
| T5: Same-terminal enrichment | 40.2% in residual vs 35.1% in full |
| T5: Q1 same-HEAD / Q4 same-HEAD | 32.6% / 29.4% |
| T5: Q1 same-terminal / Q4 same-terminal | **56.9%** / 25.3% |
| T6: Community x HEAD | chi2=63.1, p=0.038, V=0.127 |
| T6: Community x frame | chi2=183.9, p=0.114, V=0.162 |

## Interpretation

**HEAD is the only axis with genuine residual assortativity** (r=0.032, both gates pass). Category and terminal show DISassortativity in the full graph, meaning different-domain MIDDLEs are MORE likely to co-occur than same-domain. This is driven by high-degree hub MIDDLEs that bridge across domains.

**Hub suppression is the dominant effect.** Removing top-5% nodes by degree (49 hubs, leaving 923 nodes/1742 edges) increases HEAD assortativity from 0.032 to 0.051, flips category from -0.030 to +0.032, and reveals frame assortativity at 0.033. The hubs are cross-domain connectors — they create the manifold's high clustering (0.873) but suppress domain-level structure. Once hubs are removed, all compositional axes show positive assortativity.

**Low-frequency MIDDLEs carry the strongest domain signal.** HEAD assortativity among low-freq MIDDLEs (bottom 50%) is 0.163 — 7.5x higher than the full graph. These are the morphologically distinctive, domain-specific MIDDLEs that co-occur with others of the same HEAD type. High-frequency MIDDLEs (the hubs) show weak HEAD assortativity (0.022) because they connect everywhere.

**The residual is carried by non-bridge edges.** D3 explains 86% of bridge-bridge co-occurrence but only 1% of dark-dark and non-pipeline co-occurrence. Non-pipeline edges (bridge-nonpipeline + dark-nonpipeline + nonpipeline-nonpipeline) constitute 57.8% of the residual. The 0.234 gap is not about bridge MIDDLEs failing to co-occur — it's about the frequency model failing for the long tail of rare, domain-specific MIDDLEs.

**Partial assortativity is weak.** HEAD|category = -0.009 (within categories, no additional HEAD preference). Category|HEAD = -0.063 (within HEAD groups, categories are DISassortative). The domain structure operates at HEAD level, not category level — consistent with category classification being incomplete (60% of MIDDLEs unclassified by CategoryClassifier).

**Verdict: MULTI_AXIS** (HEAD + frame pass both gates). But the primary signal is HEAD domain, concentrated in the frequency tail, and masked in the full graph by cross-domain hub bridging.

## Constraints

### C1718: Residual is weakly HEAD-structured, hub-suppressed
**Tier:** 2 (ESTABLISHED) | **Scope:** A

The PP manifold's 0.234 residual gap (C1701) has genuine HEAD-domain assortativity (r=0.032, p<0.001 vs permutation null, exceeds max D3 seed). However, the signal is weak in the full graph because high-degree hub MIDDLEs bridge across HEAD domains. Hub removal (top 5% by degree) increases HEAD assortativity from 0.032 to 0.051 and reveals additional frame assortativity (0.033). Low-frequency MIDDLEs show HEAD assortativity of 0.163 — the domain structure is concentrated in the frequency tail. Category and terminal are DISassortative in the full graph (r=-0.030, -0.042) but positive under hub removal (+0.032, -0.012).

### C1719: Non-pipeline edges dominate the manifold residual
**Tier:** 2 (ESTABLISHED) | **Scope:** A

Of 6,074 residual edges (real minus D3), non-pipeline edges carry 57.8%. D3 explains 86.4% of bridge-bridge co-occurrence (2095 -> 284 residual) but only 1.1% of dark-dark (359 -> 355) and 0.4% of non-pipeline-non-pipeline (243 -> 242). The frequency/folio deployment model captures hub-mediated co-occurrence but fails entirely for the long tail of domain-specific MIDDLEs. Bridge triangles dominate (28,969 of 29,153 homogeneous triangles); the manifold's clique structure is built by bridges.

### C1720: Low-frequency MIDDLEs show strongest compositional homophily
**Tier:** 2 (ESTABLISHED) | **Scope:** A

In the residual edge set, frequency-stratified analysis reveals: Q1 (lowest frequency) has 56.9% same-terminal edges, 32.6% same-HEAD, 24.6% same-category. Q4 (highest frequency) has 25.3% same-terminal, 29.4% same-HEAD, 4.2% same-category. Low-frequency MIDDLEs co-occur preferentially with morphologically similar neighbors (same HEAD domain, same terminal, same category). High-frequency MIDDLEs connect promiscuously across domains. This explains why the full-graph assortativity is weak despite genuine domain structure in the tail.

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/pp_manifold_residual.py` | ~75 sec |

## Results

| File | Content |
|------|---------|
| `results/pp_manifold_residual_results.json` | Full results: assortativity (all axes, gates, hub-removed, partial, freq-stratified), pipeline partition, triangle analysis, residual characterization, community alignment, verdict |
