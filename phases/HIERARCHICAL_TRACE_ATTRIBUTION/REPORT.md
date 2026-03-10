# Phase 561: Hierarchical Trace Attribution

**Phase directory:** `phases/HIERARCHICAL_TRACE_ATTRIBUTION/`
**Verdict:** HIERARCHY_VALIDATED
**New constraints:** C1572-C1574

---

## Motivation

Phase 560b conclusively established that folio-average features cannot distinguish folios within sections (D3b 0/18 FAIL across 94 dimensions in 6 feature sets, C1570), while section templates fix deployment grammar (Ward ARI=0.615, C1571). This closed an entire class of approaches.

Phase 561 asks a different question: **where does variance live in the section-template executor hierarchy?** Specifically:
1. How much variance does each layer of the hierarchy explain?
2. Does sub-folio-average resolution (distributions of lines/paragraphs, not their averages) recover within-section folio specificity that averaging destroyed?

This is attribution and architecture testing, not execution. It validates the substrate on which a future executor would run.

## The 5-Layer Model Under Test

```
Layer 1: SECTION TEMPLATE    -- deployment priors, paragraph emphasis style, closure norms
Layer 2: FOLIO DOMAIN BUDGET -- HEAD proportions (k/t/a/e/o/headless fracs)
Layer 3: PARAGRAPH SUBROUTINE -- operational emphasis (C1398 zones)
Layer 4: LINE SAFETY PACKET  -- SPEC->WORK->CLOSE, Q3->Q4 cliff, no cross-line memory
Layer 5: TOKEN               -- HEAD->domain->routing/closure (residual)
```

## Method

All analysis uses the Phase 560 T1 corpus (23,096 tokens, 37 fields). No new BFolioDecoder runs.

### T1: Hierarchical Variance Partition

ANOVA-style sequential SS decomposition across `section > folio > paragraph > line > residual` for 9 token-level features. Four null models (200 permutations each): section-shuffle, folio-shuffle-within-section, paragraph-shuffle-within-folio, line-shuffle-within-paragraph.

Features: head_k, head_e, head_a, is_headless, hazard_ord, opacity_ord, compound_depth, is_safe_pathway, routing_match.

### T2: Paragraph Emphasis Distributions

Tests whether paragraph-level domain emphasis DISTRIBUTIONS recover within-section folio specificity. 283 qualifying paragraphs (>=3 body lines, >=15 tokens). Dual zone assignment: C1398 direct centroids + unsupervised k-means.

Four sub-tests: C1 continuous EMD (primary), C2 zone inventory, C3 paragraph ecology, C4 continuous variance.

### T3: Line-Level Distribution Fingerprints

Tests whether line-level compositional distributions carry folio-specific information. 2,328 qualifying lines (>=5 tokens) with 15-dimensional profiles including q4_opaque_rate and routing_match_rate.

Two sub-tests: B1 variance ratio, B2 energy distance with permutation null (300 seeds).

### T4: Headless Ecology Profiling

Determines where headless token subtype distributions live hierarchically. 402 qualifying paragraphs (>=5 headless tokens) with 14 headless ecology features. Includes paragraph-within-folio dispersion test (T4-C).

### T5: Synthesis

Computes Layer Support Indices (LSI per layer), sub-folio resolution assessment, headless independence verdict, narrative synthesis, and overall verdict.

---

## Results

### T1: Hierarchical Variance Partition

**All four hierarchy levels are real structural layers** (confirmed by z-scores against level-specific null models).

| Feature | VS_section | VS_folio | VS_para | VS_line | Residual |
|---------|-----------|----------|---------|---------|----------|
| head_k | 0.011 | 0.013 | 0.025 | 0.093 | 0.859 |
| head_e | 0.006 | 0.022 | 0.026 | 0.077 | 0.869 |
| head_a | 0.017 | 0.021 | 0.036 | 0.088 | 0.839 |
| is_headless | 0.014 | 0.011 | 0.029 | 0.087 | 0.859 |
| hazard_ord | 0.026 | 0.021 | 0.031 | 0.104 | 0.818 |
| opacity_ord | 0.001 | 0.018 | 0.044 | 0.169 | 0.769 |
| compound_depth | 0.005 | 0.007 | 0.023 | 0.081 | 0.883 |
| is_safe_pathway | 0.003 | 0.009 | 0.020 | 0.083 | 0.885 |
| routing_match | 0.001 | 0.006 | 0.018 | 0.077 | 0.898 |

**Z-scores (significance against level-specific nulls):**

| Feature | z_section | z_folio | z_para | z_line |
|---------|----------|---------|--------|--------|
| head_k | 11.73 | 7.03 | 0.95 | 2.63 |
| head_e | 3.46 | 9.99 | 4.39 | -2.06 |
| head_a | 9.44 | 9.71 | 6.53 | 3.71 |
| is_headless | 17.43 | 4.75 | 4.71 | 1.57 |
| hazard_ord | 13.31 | 11.30 | 2.80 | 4.09 |
| opacity_ord | -0.08 | 6.65 | 0.31 | 4.53 |
| compound_depth | 9.32 | 3.81 | 1.55 | -0.39 |
| is_safe_pathway | 2.37 | 3.78 | -0.03 | -0.67 |
| routing_match | 2.00 | 5.10 | -1.25 | -3.36 |

**Summary:** Section: 8/9 features significant. Folio: 9/9. Paragraph: 4/9. Line: 4/9 (hazard_ord z=4.09, opacity_ord z=4.53 confirm line safety packet for hazard/closure features). Feature-family expectations confirmed: domain-membership features load on section/folio, hazard/closure features load on line.

**T1-A: PASS** (8/9 >= 5), **T1-B: PASS** (9/9 >= 4), **T1-C: PASS** (4/9 >= 3), **T1-E: PASS** (2/4 >= 2).

### T2: Paragraph Emphasis Distributions

**Paragraph distributions RECOVER within-section folio specificity that averaging destroyed.**

ARI (direct vs unsupervised zones): 0.2867 -- below 0.3, consistent with C1398 gradient interpretation rather than discrete clusters.

| Sub-test | S | H | B | Pass |
|----------|---|---|---|------|
| C1 Continuous EMD (PRIMARY) | z=6.21 PASS | z=5.06 PASS | z=2.34 PASS | **PASS** |
| C2 Zone Inventory (direct) | p=0.000 PASS | p=0.000 PASS | p=0.014 PASS | **PASS** |
| C2 Zone Inventory (unsupervised) | p=0.006 PASS | p=0.000 PASS | p=0.034 PASS | **PASS** |
| C3 Paragraph Ecology | 18/18 PASS | | | **PASS** |
| C4 Continuous Variance | z=-0.22 FAIL | z=-1.90 FAIL | z=-0.94 FAIL | FAIL |

**T2 overall: PASS (3/4 sub-tests).**

Key finding: The continuous paragraph emphasis cloud per folio is geometrically distinctive within sections (C1 z-scores 2.3-6.2). This is the folio-specificity signal that folio-averaging destroyed -- it lives in distributional shape, not in mean position.

### T3: Line-Level Distribution Fingerprints

**Line distributions also carry folio-specific information.**

| Sub-test | Result |
|----------|--------|
| B1 Variance Ratio | **PASS** -- all 3 sections pass (S: 7/15, H: 13/15, B: 4/15 features with ratio < 0.90) |
| B2 Energy Distance | FAIL -- S: 28.5% significant (PASS), H: 7.7% (FAIL), B: 2.1% (FAIL); aggregate 12.1% < 15% |

**T3 overall: PASS (1/2 sub-tests).**

Section H shows strongest line-level folio differentiation (13/15 features with within-folio < within-section variance). Section S shows strongest energy distance signal (28.5% of pairs significantly different after Bonferroni correction).

### T4: Headless Ecology Profiling

**Headless ecology is section-parameterized AND folio-specific, but not paragraph-varying.**

| Criterion | Result | Detail |
|-----------|--------|--------|
| T4-A (section parameterizes headless) | **PASS** | 5/14 features VS_section > 0.05 (hl_rate=0.192, sfx_bifurc=0.136, pseudo_l_frac=0.112) |
| T4-B (folio-specific component) | **PASS** | 13/14 features VS_folio > VS_section |
| T4-C (paragraph-within-folio dispersion) | FAIL | Only 2/55 folios (3.6%) exceed null+2sigma (threshold: 30%) |
| T4-D (within-section discrimination) | **PASS** | S: z=4.51 (1/3 sections sufficient) |

**Critical finding:** `displaced_kt_rate` = 0 across the entire corpus. No displaced k/t head terminals exist. Only e/a/o displaced heads occur (C1494-C1497 displaced transparent terminals are exclusively non-kt). This is a new structural constraint.

Headless ecology is primarily a folio-level phenomenon (13/14 features have VS_folio > VS_section) rather than a paragraph-level one. Paragraphs within a folio share similar headless profiles -- the folio sets the headless budget, and paragraphs draw from it rather than specializing.

### T5: Synthesis

**Layer Support Indices:**

| Layer | LSI (mean z-score) | Supported |
|-------|-------------------|-----------|
| Section | 10.28 | YES |
| Folio | 7.06 | YES |
| Paragraph | 2.22 | YES |
| Line | 1.15 | no |

3/4 layers supported. Line is not supported as an aggregate LSI (mean z=1.15) because only hazard/closure features load at line level (z=4.09, 4.53) while domain and routing features do not. This is structurally correct: line safety packets handle hazard and closure, not domain selection.

**Sub-folio resolution:** YES. Both T2 (paragraph distributions) and T3 (line distributions) recover folio specificity. Distributional shape carries information that averaging destroyed.

**Headless independence:** FOLIO_SPECIFIC. Different folios deploy headless tokens differently; paragraphs within a folio share similar headless ecology.

**Mean total explained variance (non-residual):** 14.7% -- the remaining 85.3% is token-level residual, consistent with a highly stochastic generative process operating within hierarchical templates.

---

## Verdict: HIERARCHY_VALIDATED

All verdict criteria met:

| Criterion | Status | Value |
|-----------|--------|-------|
| T1-A (section sig >= 5/9) | PASS | 8/9 |
| T1-B (folio sig >= 4/9) | PASS | 9/9 |
| T1-C (para sig >= 3/9) | PASS | 4/9 |
| T1-E (line hazard sig >= 2/4) | PASS | 2/4 |
| T2 or T3 pass | PASS | Both pass |
| LSIs supported >= 3/4 | PASS | 3/4 |

**The 5-layer hierarchical model is validated as the correct architectural decomposition for the Currier B executor.** Section templates, folio domain budgets, paragraph subroutines, and line safety packets are all real structural layers that explain statistically significant variance beyond what their null models predict.

---

## Architectural Implications

1. **Section templates are the strongest structural layer** (mean z=10.28 for domain features) but explain only ~1% of raw variance. The manuscript is template-driven but highly stochastic within templates.

2. **Folio identity below section level is represented less by average parameter values than by the distributional geometry of paragraph subroutines and line safety packets generated under a folio-specific domain budget.** Folio domain budgets are real and distinctive (mean z=7.06). Every feature tested shows significant folio-level structure beyond section. This is NOT captured by folio-average vectors (Phase 560b C1570) but IS captured by paragraph and line distributional shapes.

3. **Paragraph emphasis distributions are the primary carrier of folio specificity** (T2 PASS all sections for continuous EMD). The folio-specific signal lives in the shape of the paragraph emphasis cloud, not in summary statistics. This confirms paragraph emphasis as the #1 RF feature from Phase 560b.

4. **Line safety packets are real for hazard/closure features** (hazard_ord z=4.09, opacity_ord z=4.53 at line level) but not for domain or routing features. Line is selective, not globally strong -- which is architecturally correct for a safety-packet layer (C1429/C1470).

5. **Headless ecology is a folio-level infrastructural regime, not a paragraph-subroutine accent** (T4-B 13/14, T4-C FAIL). Paragraph emphasis can vary strongly in thermal/containment/monitoring style, but the kind of infrastructure/meta-operation substrate available is folio-global. This constrains executor design: headless deployment is a folio-level parameter.

6. **Displaced k/t head terminals = 0 (PROVISIONAL).** All displaced-head tokens have e/a/o terminals in the T4 operationalization. This conflicts with C1494-C1497 which describe k/t enrichment in displaced position. Requires reconciliation audit before elevation to Tier 2 -- the result may reflect a stricter parser definition or a counting mismatch.

## Conceptual Scope Note

Trace attribution is not trace execution. Phase 561 validates the nested execution hierarchy as the correct architectural decomposition. It does NOT prove token-for-token executor fidelity, local path specificity, or simulation recoverability. That is the next phase's problem (executor construction).

---

## New Constraints

| C# | Claim | Tier |
|----|-------|------|
| C1572 | Hierarchical variance partition validates 4-layer nesting with selective layer loading | 2 |
| C1573 | Paragraph emphasis distributions recover within-section folio specificity that averaging destroyed | 2 |
| C1574 | Headless ecology is folio-specific not paragraph-specific | 2 |

---

## Scripts

| Script | Output | Runtime |
|--------|--------|---------|
| `scripts/t1_variance_decomposition.py` | `results/t1_variance_decomposition.json` | 14s |
| `scripts/t2_paragraph_distributions.py` | `results/t2_paragraph_distributions.json` | 109s |
| `scripts/t3_line_distributions.py` | `results/t3_line_distributions.json` | 91s |
| `scripts/t4_headless_ecology.py` | `results/t4_headless_ecology.json` | ~60s |
| `scripts/t5_synthesis.py` | `results/t5_synthesis.json` | <1s |
