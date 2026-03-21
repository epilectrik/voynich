# Phase 621: ROSETTES_VISUAL_GRAMMAR_CORRELATION

**Status:** COMPLETE
**Verdict:** VISUAL_GRAMMAR_INDEPENDENT
**Constraints:** C1824-C1826
**Script runtime:** ~15s

## Question

Does the visual imagery of each rosette correlate with its operational grammar profile? Framed as a C138 exception test — null hypothesis is that visual features do NOT correlate with grammar.

## Framing

C138/C140 (Tier 1) establish illustration epiphenomenality (swap invariance p=1.0). Rosettes are structurally unusual: text embedded within diagram, classified as metalayer index (C1126). This tests whether C138's manuscript-wide null has a rosettes-specific exception.

**Contamination disclosure:** Visual descriptions written during this project with access to grammar profiles. Hypothesis set informed by both visual and grammar inspection.

## Primary Hypotheses (3 pre-registered)

| # | Visual Feature | Grammar Prediction | Result | Effect |
|---|---|---|---|---|
| H1 | has_liquid_medium | higher e-HEAD | **NEGATIVE** | r_rb = -0.300 (wrong direction) |
| H2 | has_plan_view | higher o-HEAD | POSITIVE | r_rb = +0.143 (weak, correct) |
| H3 | visual complexity | higher compound rate | POSITIVE | rho = 0.025 (negligible) |

**Composite alignment:** 0.156 (below permutation null mean of 0.338)
**Permutation p-value:** 0.888 (10,000 shuffles)
**Effect size:** -1.17 (observed is WORSE than random)

## Predictions

| Test | Name | Result | Key Metric |
|------|------|--------|------------|
| T1 | Composite alignment (C138 exception) | **FAIL** | composite=0.156, p=0.888 |
| T2 | Grammar uniformity despite visual diversity | **FAIL** | rho(fc, JSD)=0.533 |
| T3 | Spatial non-prediction (C1818 replication) | **PASS** | delta=0.007 |

## Key Findings

### 1. No Visual-Grammar Correlation (C1824)
The composite alignment score (0.156) is below the permutation null mean (0.338). Random shuffling of visual features produces BETTER alignment than the actual mapping. Visual imagery does not predict grammar profiles at the rosette entity level. **C138 holds at the metalayer entity level.**

### 2. Visual Diversity Partially Predicts Grammar Diversity (C1825)
Unexpectedly, rho(feature_count, mean_pairwise_JSD) = 0.533. Entities with more complex visual descriptions tend to be more grammatically distinctive (higher mean JSD to other entities). This does NOT mean visual content predicts grammar content — it means visual and grammar complexity co-vary, possibly because both reflect the entity's functional prominence.

### 3. Spatial Non-Prediction Replicated (C1826)
Mean adjacent JSD (0.080) ≈ mean non-adjacent JSD (0.073), delta = 0.007. Replicates C1818 at the category level.

### H1 Reversal
The strongest a priori hypothesis (liquid medium → higher e-HEAD) went the wrong direction. Liquid entities (NE, CENTER, EAST, SW, SE) have mean e-HEAD = 0.219 vs non-liquid (NW, NORTH, WEST, SOUTH) = 0.239. EAST (the most aqueous rosette) is the exception — it IS e-HEAD dominant (31.3%). But the other liquid entities pull the group average down. The visual water-bath interpretation doesn't generalize to the grammar.

### Notable Exploratory Correlations
All labeled EXPLORATORY (N=9, no correction):
- plan_view × THERMAL: rho = +0.762
- architectural × THERMAL: rho = +0.762
- fountain × e_head: rho = +0.650
- fountain × OPERATION: rho = +0.650
- radial × FLOW: rho = +0.575
- spiral_text × compound_rate: rho = +0.575

These are suggestive but with N=9 and 120 pairs tested, multiple comparison correction would eliminate all.

## Visual Feature Distribution

| Entity | Tokens | Features | Key Visual Tags |
|--------|--------|----------|-----------------|
| NW | 31 | 8 | plan_view, architectural, botanical, radial |
| NORTH | 42 | 4 | star_field, cloud_steam, botanical, radial |
| NE | 53 | 6 | liquid, architectural, star_field, spiral_text |
| WEST | 28 | 5 | star_field, cloud_steam, botanical, radial |
| CENTER | 67 | 3 | liquid, radial, alembics |
| EAST | 32 | 7 | liquid, cloud_steam, bead_ring, fountain |
| SW | 45 | 6 | liquid, star_field, cloud_steam, bead_ring |
| SOUTH | 37 | 1 | radial |
| SE | 28 | 8 | liquid, plan_view, architectural, pipes_tubes |

## Caveats

1. **N=9** — fundamentally underpowered. Even a true correlation may not be detectable.
2. **Contaminated descriptions** — visual features coded from descriptions written with grammar knowledge.
3. **Feature extraction is keyword-based** — sensitive to description writing style. SOUTH has only 1 feature because its description is brief ("Visually very similar to NORTH").
4. **H1 group split is lopsided** — 5 liquid vs 4 non-liquid. More entities in the liquid group reduces discrimination.

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| `rosettes_visual_grammar_correlation.py` | ~15s | `rosettes_visual_grammar_correlation.json` (37.7 KB) |

## Data Sources

- Phase 620 entity profiles (9 rosettes, 28-67 tokens each)
- Visual descriptions from `rosettes_annotated.json` (merged from `rosettes_reference.json`)
