# PP_POOL_CLASSIFICATION Phase

**Status:** COMPLETE | **Constraints:** C656-C659 | **Tier:** 2

## Question

Do the 404 PP MIDDLEs form discrete functional pools based on A-record co-occurrence, or is the PP space continuous?

## Answer

**Continuous.** PP MIDDLEs do not cluster into discrete pools by any axis tested. A-record co-occurrence produces no silhouette above 0.025 (threshold: 0.25). B-side behavioral profiles are also continuous (best silhouette: 0.237 at k=2, with a degenerate 2-vs-91 split). The two axes are independent (ARI=0.052). Material class creates a gradient in co-occurrence (36.2% entropy reduction), but not a partition (NMI=0.13).

The "toolbox" metaphor is partially right — different records have different PP compositions with material-class bias — but the toolboxes shade into each other along a continuous gradient. There are no discrete pool boundaries.

## Scripts

| Script | Tests | Verdict |
|--------|-------|---------|
| pp_cooccurrence_clustering.py | 1-4 | CONTINUOUS (sil=0.016) |
| pp_pool_validation.py | 5-7 | BEHAVIORAL_CONTINUOUS, INDEPENDENT |

## Findings

### Test 1: PP Co-Occurrence Matrix (C656)
203 PP MIDDLEs (≥3 A records) form the co-occurrence space:
- **Jaccard matrix**: 76.0% zero pairs, mean non-zero Jaccard=0.023, max=0.246
- **Single connected component** (all 203 PP reachable)
- **201 excluded** (50% of PP appear in <3 records)
- Mean degree: 48.5 co-occurrence partners per PP

### Test 2: Hierarchical Clustering (C656, C657)
No discrete pools across all methods:
- **UPGMA**: max silhouette = 0.016 at k=20
- **Ward**: max silhouette = 0.018 at k=20
- **Complete**: failed (degenerate)
- Baselines: k=4 (material) sil=0.005, k=2 (pathway) sil=0.005
- Forced k=20: Pool 18 dominates with 69/203 members (34%)

### Test 3: Attribute Alignment (C658)
| Axis | NMI | Chi2 p | Cramér's V | Redundant? |
|------|-----|--------|------------|------------|
| Material class | 0.129 | 0.002 | 0.392 | No |
| Pathway | 0.032 | 0.516 | 0.299 | No |
| Lane character | 0.062 | 0.317 | 0.320 | No |
| Section | 0.087 | — | — | No |

- Material entropy: overall 1.88 bits → within-pool 1.20 bits (36.2% reduction)
- ARI vs existing pp_classification clusters: 0.057 (independent)
- No axis is redundant with co-occurrence structure

### Test 4: Section-Controlled Analysis (C656)
- Within-Herbal (163 PP): same result (sil=0.020, no discrete pools)
- Consistency ARI (full vs Herbal-only): 0.406 (moderate)
- Section NMI: 0.087 — pools barely capture section
- Conclusion: section membership does NOT explain co-occurrence (which itself is continuous)

### Test 5: B-Side Behavioral Clustering (C657)
93 PP MIDDLEs with ≥10 B-side bigrams:
- Mean pairwise JSD: 0.537 (substantial behavioral diversity)
- Best silhouette: 0.237 at k=2 (below 0.25 threshold)
- Degenerate split: 2 outliers vs 91 in main cluster
- Lane character ARI: 0.010 (morphology doesn't predict behavior)

### Test 6: Cross-Validation (C659)
- Overlap: 84 PP in both clustering attempts
- **ARI: 0.052** — co-occurrence and behavior are independent
- Chi2 p=0.109 (not significant)
- Co-occurrence structure tells you nothing about behavioral profile, and vice versa

### Test 7: Pool Census
Role variance explained by forced co-occurrence pools (eta-squared):
| Role | eta² |
|------|------|
| AUXILIARY | 0.247 |
| ENERGY_OPERATOR | 0.174 |
| FREQUENT_OPERATOR | 0.144 |
| CORE_CONTROL | 0.087 |
| FLOW_OPERATOR | 0.080 |

Pools capture ~15% of role variance on average. This is gradient signal, not discrete structure.

## Constraints Produced

| ID | Name | Finding |
|----|------|---------|
| C656 | PP Co-Occurrence Continuity | Max silhouette 0.016 (threshold 0.25), one component, 76% zero-Jaccard |
| C657 | PP Behavioral Profile Continuity | Best silhouette 0.237 (degenerate k=2), mean JSD=0.537 |
| C658 | PP Material Gradient | 36.2% entropy reduction as gradient (NMI=0.13), not partition |
| C659 | PP Axis Independence | Co-occurrence–behavior ARI=0.052, no axis captures another (all NMI < 0.15) |

## Structural Conclusion

PP MIDDLEs form a **continuous parameter space**, not a vocabulary of discrete process types. This extends two prior findings:

1. **C631 extension**: Within-class MIDDLE continuity (silhouette < 0.25 in 34/36 classes) now extends to cross-class PP continuity. The entire PP vocabulary is a continuous landscape.

2. **C506 extension**: PP composition non-propagation to B classes (cosine=0.995) is consistent with continuity — if PP formed discrete pools, you'd expect pool-specific B class profiles. Instead, all PP compose the same B class distribution because they occupy a gradient, not bins.

**What PP structure actually looks like:**
- Material class creates a weak gradient (36.2% entropy reduction) — ANIMAL-enriched PP and HERB-enriched PP partially segregate in co-occurrence, but most PP are MIXED or NEUTRAL (56% combined)
- Role composition creates moderate gradient (15% variance explained) — some PP are AX-heavy, some EN-heavy, but these shade into each other
- No single axis (material, pathway, lane, section, behavior) captures more than 13% of PP structure
- The axes are independent of each other (all cross-axis NMI < 0.15)

The PP vocabulary is a high-dimensional continuous space where each MIDDLE occupies a unique position defined by weak gradients across multiple independent axes. Classification into discrete groups is structurally unsupported.

## Data Dependencies

| File | Source Phase |
|------|-------------|
| middle_classes_v2_backup.json | A_INTERNAL_STRATIFICATION |
| pp_role_foundation.json | A_TO_B_ROLE_PROJECTION |
| pp_classification.json | PP_CLASSIFICATION |
| lane_pp_discrimination.json | LANE_CHANGE_HOLD_ANALYSIS |
| en_census.json | EN_ANATOMY |
| class_token_map.json | CLASS_COSURVIVAL_TEST |
