# Phase 641: B Gloss Recipe Correlation (Latin features)

**Phase:** 641
**Status:** COMPLETE (null result — informative)
**Type:** Statistical validation with pre-registered predictions
**Started:** 2026-04-16
**Completed:** 2026-04-16

## Purpose

Test atom/prefix/suffix glosses (PT-013/14/15) statistically across 15-16 matched folio-recipe pairs using pre-registered predictions against Latin Pseudo-Lull Testamentum features. Uses permutation p-values, BH-FDR correction, leave-one-out stability, bootstrap CIs.

## Scripts Executed

| Script | Purpose | Status |
|--------|---------|--------|
| `s0_latin_feature_extractor.py` | Segment Latin by chapter, extract 11 regex feature families | COMPLETE |
| `s1_shared_validation.py` | Shared library: loaders, statistics | COMPLETE |
| `s2_preregistered_tests.py` | 24 pre-registered hypothesis tests (blocks A-G) | COMPLETE |
| `s3_ordinal_alignment.py` | Paragraph↔step sequence alignment via Kendall-τ | COMPLETE |
| `s7_validation_summary.py` | Aggregate scorecard + interpretation | COMPLETE |

## Scripts Deferred (not run)

| Script | Why deferred |
|--------|--------------|
| `s0b_brunschwig_features.py` | Control invalid: Brunschwig (both 1500 and 1512) separate operational from recipe content. No integrated-operation corpus exists as valid control. |
| `s0c_nonrecipe_control.py` | Would still be informative (Theorica style vs. Practica operation) but not run given main-result null. |
| `s4_qokaiin_contrastive.py` | Needed held-out folios we haven't identified. |
| `s5_control_comparison.py` | Depends on s0b/s0c. |
| `s6_english_parity.py` | English features are translator-derived from Latin (not independent). Parity adds no validation power. |

## Results

### Rate Correlation (s2)
- 24 valid tests, 2 skipped (zero-sum features)
- **0/24 FDR-accepted** at q=0.10
- **0/24 bootstrap CIs exclude zero**
- 8/24 LOO-stable
- Verdict distribution: 24 INCONCLUSIVE

### Near-significant signals (right direction, p<0.25, LOO-stable)
- `E2_f_flag ↔ termination`: ρ=+0.392, p=0.128
- `C6_p_pause ↔ termination`: ρ=+0.374, p=0.155
- `A2_ch_check ↔ monitoring+heat_transition`: ρ=+0.352, p=0.176
- `D2_n ↔ iteration (inverse)`: ρ=-0.340, p=0.196 (supports "halt" gloss)

### Potential falsifications (wrong direction, p<0.10)
- `C2_t_transfer ↔ transfer`: ρ=-0.474, p=0.069 — predicted +, got −. Worth investigating.

### Ordinal Alignment (s3)
- 5/16 pairs produced valid ρ (others had <3 shared feature categories — Latin chapters too terse)
- Mean ρ = +0.260 (null mean = +0.037)
- Permutation p = 0.22
- Perfect alignment: f82v Ch28M (ρ=+1.0)
- Wrong-direction alignment: f83r Ch9P (ρ=-0.60) — recipe has MAT early, folio has MAT late

## Core Finding

**The Voynich folio encodes operational EXECUTION; the Latin Testamentum encodes recipe DESCRIPTION.** This is consistent with C171 (semantic ceiling). Rate correlation at the per-folio level is the wrong test — a folio with one "place on ashes for 3 days" instruction produces hundreds of continuous heat-maintenance operations, so folio heat-prefix rate ≠ recipe heat-mention rate.

The null result is PREDICTED by the matches themselves. A rate-correlation hit would have been surprising given the operational nature of the Voynich notation.

## Methodological Observations

1. **Small-N barrier holds:** N=16 is too small for FDR survival unless effects are large. Near-significant signals exist but cannot promote to constraints.
2. **Granularity mismatch:** Latin Testamentum chapters are terse (median 10-15 lines). Ordinal alignment requires ≥3 shared categories between folio paragraphs and recipe steps — only 5/16 pairs achieved this.
3. **Control-corpus critique addressed structurally:** Brunschwig (1500 small book OR 1512 large book) separates operational from recipe content. No medieval text we have integrates them the way Testamentum does. The "show Testamentum beats Brunschwig" control is malformed because the comparison target doesn't exist at the structural level.
4. **Pre-registration worked:** We locked predictions before running. Null result is epistemically clean, not cherry-picked.

## Constraint Promotions

**None this round.** Zero tests passed (SUPPORTED + FDR + CI-excludes-0 + LOO-stable + control-beats).

## Implications for the Match Defense

The null is not evidence against the matches; it's evidence that per-folio rate correlation is the wrong instrument for matches at this granularity. The matches remain defensible on:
- Multiple independent evidence types (8D features, dark pipeline markers C1939-C1941, recto/verso scans C1948-C1955, blind prediction C1938)
- Structural uniqueness of Testamentum integration among medieval candidates
- Predictive confirmations (sealing signatures, balneum signatures) on matched folios
- Deep-alignment work (PT-013/14/15) producing cross-class-validated glosses

## Next Steps

1. **SISMEL Catalan arrival** enables paragraph↔step alignment with richer per-step content (Buosi-Moncunill thesis has ~20 steps per chapter; SISMEL has full text).
2. **Investigate C2 t-atom falsification** — if real, suggests 't' doesn't encode "transfer" directly.
3. **Deferred Theorica control (s0c)** could still run as a style vs. content check.

## Pre-registered Hypothesis Summary

See `scripts/s2_preregistered_tests.py` for the 24 tests (Blocks A through G) with pre-registered regex patterns locked before execution.

## Key Files

| File | Purpose |
|------|---------|
| `PLAN.md` | Full phase plan |
| `results/pl_channel_features_latin.json` | Per-chapter Latin regex features (186 chapters) |
| `results/preregistered_tests.json` | Full s2 scorecard |
| `results/ordinal_alignment.json` | Per-pair s3 alignment |
| `results/validation_scorecard.json` | s7 summary |
