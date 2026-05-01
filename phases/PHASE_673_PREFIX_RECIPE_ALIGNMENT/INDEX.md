# Phase 673: PREFIX-Recipe Content Alignment (External Anchor Test)

**Status:** COMPLETE
**Started:** 2026-05-01
**Goal:** Test whether PREFIX rates in matched Voynich folios correlate with corresponding gloss-aligned recipe-content categories (external anchor).

## Origin

After Phases 670-672 found increasingly narrow prefix-positional patterns (terminal gradient, bimodal class, sh-vs-ch on fixed frame), crazy-expert flagged the methodology as drifting:

> "Three phases of prefix-positional analysis with progressively narrower frames is the signature of a researcher fitting noise."

> "The honest test is: does prefix-position predict something OUTSIDE the position loop. The permutation phase will produce a publishable-looking number. The recipe-alignment phase will produce knowledge."

This phase implements the proposed external anchor test using the 11 matched Voynich-Pseudo-Lull folio-recipe pairs from Phase 668.

## Pre-Registered Hypothesis

PREFIX rates in matched Voynich folios should correlate with corresponding recipe-content category densities, where category alignments follow existing PREFIX glosses:

| PREFIX | Gloss source | Predicted category |
|--------|--------------|--------------------|
| qo | C1300 (near-pure THERMAL channel) | heat |
| ch | C929 (active test) | monitor |
| sh | C929 (passive monitor) | monitor |
| ok | C1962 (thermal regime / fire-degree) | heat or monitor |
| ot | C1962 (transfer / iteration cycles) | transfer or iter |
| ol | C1962 (vessel-content state monitoring) | vessel or monitor |
| lk | C930 (fire-method monitoring) | heat or monitor |

Pre-registered prediction: positive correlation between rate and gloss-aligned category density. Falsification: zero or wrong-direction correlations.

## Data

- **11 matched folios** from Phase 668 (8 coherent + 3 partial), excluding rejected (f77v, f82v) and unmatched (f107r, f80r)
- **Voynich side:** per-folio PREFIX rates (body-only, lines >= 4) for 8 prefixes (qo, ch, sh, ok, ot, ol, lk, lch)
- **Recipe side:** per-chapter keyword density in 6 content categories (heat, monitor, transfer, iter, vessel, complete) extracted from `testamentum_complete_english.txt` using line-range metadata in `pseudo_lull_structural_profile.json`
- **48 (prefix, category) cells** tested with Spearman correlation + 5000-shuffle permutation null

## Results

### Primary test (qo vs heat density)

| | Value |
|---|---|
| N folios | 11 |
| Spearman rho | -0.1182 |
| Two-sided p (10k permutations) | 0.7340 |
| Verdict | **NULL** |

qo-rate does not correlate with recipe heat-keyword density across matched folios.

### Multi-prefix × multi-category matrix

| PREFIX | heat | monitor | transfer | iter | vessel | complete |
|--------|------|---------|----------|------|--------|----------|
| qo | -0.118 | -0.418 | +0.491 | +0.273 | -0.173 | -0.209 |
| ch | -0.045 | -0.282 | -0.018 | -0.491 | -0.009 | +0.491 |
| sh | -0.473 | -0.164 | +0.145 | -0.227 | -0.009 | +0.218 |
| ok | +0.173 | **+0.645*** | -0.473 | -0.418 | +0.136 | +0.309 |
| ot | -0.173 | +0.336 | -0.218 | +0.073 | -0.327 | **+0.618*** |
| ol | -0.164 | +0.109 | -0.091 | -0.064 | +0.400 | -0.109 |
| lk | -0.018 | -0.100 | -0.118 | -0.218 | -0.064 | +0.182 |
| lch | -0.264 | -0.500 | +0.364 | -0.173 | -0.055 | +0.073 |

\* = uncorrected p < 0.05 (5000-shuffle permutation)

Two cells passed uncorrected p < 0.05:
- ok ↔ monitor: rho=+0.645, p=0.0418
- ot ↔ complete: rho=+0.618, p=0.0494

**Multiple-comparison correction (Bonferroni):** threshold 0.05 / 48 = 0.001. **Zero cells survive.**

Expected positives by chance at uncorrected α=0.05 with 48 tests: ~2.4. Observed: 2. Within chance frequency.

## Verdict

**External alignment NULL.** PREFIX gloss system does not produce folio-level density predictions for corresponding recipe content. The two uncorrected positives (ok↔monitor, ot↔complete) are loose semantic matches but indistinguishable from chance.

This does NOT falsify the underlying PREFIX glosses (which were derived from intra-folio operational patterns and category-level distributions). It DOES limit the scale at which they operationalize: PREFIX glosses survive at category level (qo=THERMAL category 59%, C1300) but fail at folio-density alignment level (qo-rate ≠ recipe heat density).

The clean negative result confirms crazy-expert's framing: internal-to-internal permutation tests would have produced significance from sheer power; the external anchor test produces a clean null.

## Constraint Updates

### C1984 (Tier 3, observation): Folio-level PREFIX-content alignment fails

Across 11 Phase-668-validated Voynich-Pseudo-Lull folio-recipe pairs, PREFIX rates (qo, ch, sh, ok, ot, ol, lk, lch) tested against keyword-density categories (heat, monitor, transfer, iter, vessel, complete) show no surviving correlations after multiple-comparison correction. 2/48 cells passed uncorrected p<0.05 (ok↔monitor rho=+0.645 p=0.042; ot↔complete rho=+0.618 p=0.049) — within chance frequency (~2.4 expected).

The PREFIX gloss system survives at category level (intra-folio operational distributions, e.g., C1300 qo=59% THERMAL category) but fails at folio-density-prediction level (cross-folio rate vs recipe content density). Glosses operationalize at within-folio operational classification, not at cross-folio content density alignment.

**Tier:** 3 (Currier B observation; constrains future scale claims)

## Methodological Note

This phase explicitly broke from the internal-permutation pattern of Phases 670-672 in response to crazy-expert's critique that the previous test design would always produce numbers regardless of substantive meaning. The clean null demonstrates the value of external anchoring: had this phase used yet another within-line permutation test, it would have produced more "significant" prefix-positional differences without addressing whether those differences carry semantic content.

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_prefix_recipe_alignment.py | qo primary test + 8x6 multi-prefix matrix with permutation null | ~30s |

## Relationship to Existing Constraints

- **C1300** (qo near-pure THERMAL channel, 59% intra-folio): Survives. C1984 limits the claim's scale: qo→THERMAL is a within-folio operational classification, not a cross-folio density predictor.
- **C929** (sh=passive monitor, ch=active test): Survives at category level. C1984 limits cross-folio gloss-density alignment.
- **C1962** (4-axis o-prefix runtime channel taxonomy): Survives at category level; 16/16 within-sample top-1 fit on matched recipes is intra-folio. Cross-folio density alignment fails per C1984.
- **C930** (lk fire-method monitoring): Survives at category level.
- **C1983** (sh-vs-ch differential position on e->y, Phase 672): Within-folio positional finding; C1984 doesn't address.
- **C1971** (Phase 668 coherent recipe matchings): The matchings themselves are validated at the operational-level. C1984 shows that operational coherence does not translate to keyword-density correlation at the prefix-rate level.

## Suggested Follow-up

- **Paragraph-level alignment:** This phase used folio-level (n=11). Paragraph-level (~70 data points across 11 folios) would have higher power but requires recipe-section alignment.
- **Different scale of operationalization:** Test PREFIX glosses against folio-section operational labels (heat-step, transfer-step, observation-step) rather than keyword-density. May survive where keyword-density fails.
- **Content-vector approach:** Instead of keyword counts, use the 4-channel feature vectors (k, h, e, t) per chapter and per Voynich folio kernel composition. Already known to align (Phase 627-668). C1984 shows the keyword-density operationalization specifically is not predictive.
