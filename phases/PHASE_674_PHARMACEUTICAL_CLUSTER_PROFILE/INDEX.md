# Phase 674: Pharmaceutical Cluster Operational Profile

**Status:** COMPLETE (negative — scope limit identified)
**Started:** 2026-05-01
**Goal:** Characterize what Phase 642's 26-folio pharmaceutical-regime cluster is doing operationally, beyond the PC1 axis ("low-heat observational").

## Context

Phase 642 identified a 26-folio cluster (PC1 separates 8-10σ from Testamentum-matched alchemical folios) with high-level characterization "low-heat observational" but never specified what those folios are *operationally* doing. This phase compared the 26 cluster folios against the 11 Phase-668-validated matched alchemical folios on 12 operational dimensions.

## Pre-Registered Hypothesis

The 26-folio cluster has a distinct operational signature from matched alchemical folios on multiple structural dimensions (PREFIX channels, HEAD/TERM/kernel atoms, e-depth, paragraph coupling). Sufficient effect sizes (|d|>1.0) on multiple independent dimensions would justify a Tier 2 cluster-property constraint.

## Phase 1 Results (Naïve All-Folio Comparison)

Multiple very-large effect sizes (|d|>2.0):

| Metric | Cluster (n=26) | Matched (n=11) | Cohen's d |
|---|---|---|---|
| qo-prefix rate | 0.107 | 0.198 | -2.06 |
| HEAD-e rate | 0.177 | 0.319 | **-2.68** |
| TERM-r rate | 0.175 | 0.089 | **+2.59** |
| kernel-e rate | 0.336 | 0.662 | **-2.46** |
| e-depth mean | 0.33 | 0.65 | -2.54 |
| e-depth=0 fraction | 0.745 | 0.519 | **+2.75** |
| TERM-y rate | 0.357 | 0.508 | -2.13 |
| HEAD-a rate | 0.185 | 0.103 | +1.31 |
| HEAD-o rate | 0.156 | 0.095 | +1.51 |
| HEAD-k rate | 0.091 | 0.152 | -1.51 |
| BARE-prefix rate | 0.212 | 0.153 | +1.22 |
| sh-prefix rate | 0.077 | 0.125 | -1.09 |
| mean para Jaccard | 0.056 | 0.099 | -1.03 |
| type-token ratio | 0.77 | 0.55 | +3.15 (size-confounded) |
| hapax rate | 0.83 | 0.73 | +2.50 (size-confounded) |

Initial interpretation: cluster has hapax-heavy, low-thermal, weakly-coupled signature consistent with reference/lookup content; matched has repeated-vocabulary, high-thermal, sequentially-coupled signature consistent with procedural recipes.

## Expert Review

Both experts (expert-advisor and crazy-expert) flagged the headline as section-confounded. Key critiques:

1. **Section confound:** Cluster mostly Herbal, matched mostly Biological/Pharmaceutical. C1404/C939/C1893/C1808 already establish section→PREFIX→category effects. Most rate differences (e-depth, qo, e-HEAD) recapitulate known section-mediated effects.
2. **Effects collapse:** The 7 |d|>2.0 metrics are not independent — they reduce to ~1 axis (e-channel suppression: HEAD-e↔kernel-e↔e-depth↔qo per C1313, C1923, C1284). One finding with several facets, not seven.
3. **Size confound on diversity metrics:** Type-token ratio (+3.15) and hapax rate (+2.50) are textbook Heaps' law artifacts at cluster N=170 vs matched N=410. Drop them.
4. **Paragraph Jaccard is also size-confounded:** Cluster mean=3.4 paragraphs gives ~5 pairs vs matched's ~33 pairs. Variance ratio ~6x. Apparent gradient may vanish at matched n.

Both experts proposed the **within-section test** as the discriminator: compare cluster-Herbal vs matched-Herbal. If d collapses → section recapitulation. If d>1.0 survives → real cluster property.

## Phase 2: Within-Section Test (Verdict)

**Result: Test cannot be run due to zero section overlap.**

| Section | Cluster | Matched |
|---------|---------|---------|
| H (Herbal) | 19 | 0 |
| B (Biological) | 0 | 7 |
| S (Stars/Pharm.) | 2 | 4 |
| C (Cosmological) | 4 | 0 |
| T | 1 | 0 |

The Phase-668 matched-alchemical population has **zero Herbal folios**, while the Phase-642 cluster is 73% Herbal. The only section with both populations is S (cluster n=2, matched n=4 — insufficient power).

We cannot distinguish "cluster property" from "Herbal section property" with this sample. The naïve all-folio |d|>2.0 effects ARE real, but they are likely section-mediated, not cluster-specific.

## Verdict

**Phase 642's 26-folio cluster is largely the Herbal-section signature.** Phase 674's headline operational differences (e-channel suppression, BARE/a-HEAD enrichment, r-TERM doubling) cannot be distinguished from existing section-effects (C939, C1404, C1893, C1808) given zero matched folios in the Herbal section.

This does NOT invalidate Phase 642 — the cluster identification is real (PC1 8-10σ separation). But the cluster's operational signature is the section's operational signature; there is no known *additional* property beyond what section already encodes.

## Constraint Updates

### C1985 (Tier 3, scope-limit observation): Phase 642 cluster maps to Herbal section; operational profile is section-confounded

The 26-folio cluster identified in Phase 642 (PC1 separates 8-10σ from matched alchemical) maps onto the Herbal section: 19/26 cluster folios are H, 4 C, 2 S, 1 T; the 11 matched alchemical folios are 7 B + 4 S, with zero H. Naïve cluster-vs-matched comparison shows multiple |d|>2.0 effects (e-channel suppression, TERM-r doubling, BARE/a-HEAD enrichment) but these recapitulate known section-mediated effects (C939, C1404, C1893, C1808) and cannot be distinguished from them given zero section overlap with matched-H folios.

Limits future cross-population claims: cluster-property claims require either (a) within-section control via additional matched-Herbal folios, or (b) a within-folio test (e.g., paragraph layout-ordering correlation per Phase 668-669 Test B) that bypasses section confound.

**Tier:** 3 (Currier B observation; constrains methodology for cluster-property claims)

## Methodological Note

This phase explicitly demonstrated the value of the section-stratification falsifier. The Phase 1 result (multiple |d|>2.0 effects) would have looked like a strong cluster-property finding without expert-flagged confound testing. Phase 2's section assignment exposed the confound directly: the comparison was structurally impossible to disambiguate without matched-Herbal data.

This is a useful methodological lesson: when comparing two populations that emerged from different sampling processes (cluster from unsupervised clustering on structural features; matched from operational coherence with external recipes), section/section-equivalent confounds should be checked BEFORE any rate-based comparison.

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_cluster_operational_profile.py | All-folio comparison on 12 operational dimensions | ~10s |
| s2_within_section_test.py | Section-stratified test (verdict: insufficient overlap) | ~5s |

## Relationship to Existing Constraints

- **C939** (low-heat herbal section): Survived; this phase's e-channel suppression in cluster is consistent with C939 at the section level.
- **C1404** (section-determined PREFIX programs): Survived; cluster's BARE/a-HEAD enrichment is section-mediated.
- **C1893** (sh/ch redistribute by section): Survived; cluster's sh-suppression is section-effect.
- **C1808** (section significantly affects 13/14 PREFIX fractions): Survived; cluster's qo-suppression is section-effect.
- **Phase 642 cluster identification:** Survived; PC1 separation is real and structurally informative. C1985 only limits the operational-property interpretation, not the cluster identification.

## Suggested Follow-Up

- **Within-Herbal control:** Identify Herbal folios that COULD have been matched to recipes (operationally coherent with some recipe corpus) to enable matched-H vs unmatched-H comparison. Phase 642 itself partially attempted this against Brunschwig.
- **Layout-ordering test on cluster (Test B replication):** Crazy-expert proposed: cluster paragraphs should show ρ≈0 between paragraph layout-position and any phase-ordinal proxy if reference, vs ρ=+0.5+ if procedural. Requires defining a within-folio phase-ordinal proxy (e.g., e-depth gradient across paragraphs).
- **Internal cluster substructure:** The 26 cluster folios may have sub-clusters (Herbal subsection vs Cosmological f85-86 vs S-section f105v/f114r). Sub-clustering analysis could reveal multiple operational sub-types within the cluster.
