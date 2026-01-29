# PP_LINE_LEVEL_STRUCTURE

**Status:** COMPLETE | **Constraints:** C728-C733 | **Scope:** A

## Objective

Determine whether PP (Pipeline-Participating) tokens within individual Currier A lines are randomly drawn from the folio-level PP pool (C703) or exhibit structured selection patterns. Eight tests with gated execution.

## Method

Two scripts testing 8 hypotheses across two dimensions:

**Script 1 (Gated Core):** PP MIDDLE co-occurrence structure
- T1: Within-line co-occurrence vs random shuffle (1000 permutations)
- T2: C475 incompatibility as sole driver (gated on T1 PASS)
- T3: Attraction cluster detection (gated on T2 PASS)

**Script 2 (Independent Battery):** Morphological dimensions
- T4: PREFIX-MIDDLE cross-coupling within lines
- T5: SUFFIX coherence within lines
- T6: PP diversity scaling vs hypergeometric
- T7: Adjacent line PP vocabulary overlap
- T8: PP composition by folio position

Null model: within-folio shuffle preserving line lengths (1000 iterations, seed 42).

## Key Findings

**C475 incompatibility is the sole driver of within-line co-occurrence structure.** PP MIDDLE selection from the folio pool is random after accounting for incompatibility. No attraction, no clustering, no enrichment. Lines are compatibility-valid subsets.

**PREFIX-MIDDLE coupling exists within lines** (T4 PASS), but may be a secondary expression of the same incompatibility mechanism.

**Adjacent lines share more PP vocabulary** (T7 PASS), indicating soft local continuity (~10% Jaccard increase over distant lines).

**No structure in SUFFIX, diversity, or folio position** (T5, T6, T8 FAIL). PP selection is uniform across these dimensions.

## Test Results

| Test | Key Metric | Result | Constraint |
|------|-----------|--------|------------|
| T1: Co-occurrence structure | 5460 vs 5669 unique pairs, p<0.001 | PASS | C728 |
| T2: C475 as driver | 0 avoidance violations, legal p=1.0 | FAIL (explains all) | C728, C729 |
| T3: Attraction clusters | -- | SKIPPED (T2 FAIL) | -- |
| T4: PREFIX-MIDDLE coupling | MI ratio 2.79x, p<0.001 | PASS | C730 |
| T5: SUFFIX coherence | Ratio 1.02x (threshold 1.3x) | FAIL | C732 |
| T6: Diversity scaling | Effect 0.13 (threshold 0.2) | FAIL | C732 |
| T7: Adjacent line similarity | Jaccard ratio 1.10x, p=0.001 | PASS | C731 |
| T8: Folio position trajectory | Ratio 0.79, p=0.633 | FAIL | C732 |
| T9a: Whole-token free shuffle | 20,757 vs 21,646 unique, p<0.001 | PASS | C733 |
| T9b: Whole-token variant shuffle | 20,757 vs 21,094 unique, p<0.001 | PASS | C733 |

**Summary: 5 PASS, 3 FAIL, 1 FAIL-but-informative (T2), 1 SKIPPED**

## Scenario Outcome

This phase was designed with three scenarios:
- **A: Random draw** — Lines are random samples from folio pool
- **B: C475 explains all** — Lines are compatibility-valid subsets (no further structure)
- **C: Structure beyond incompatibility** — Lines are active specifications

**Result: Scenario B at MIDDLE level, Scenario C at whole-token level.** MIDDLE co-occurrence is fully explained by C475 incompatibility (T1+T2). But whole-token co-occurrence shows structure BEYOND MIDDLE assignment (T9b): the specific PREFIX+SUFFIX variant chosen for each MIDDLE is coordinated within lines. ~62% of word-level structure comes from MIDDLE incompatibility, ~38% from token variant selection.

## Data Summary

| Metric | Value |
|--------|-------|
| A folios | 114 |
| Total A lines | 1,562 |
| Lines with PP tokens | 1,547 (99.0%) |
| Lines with 2+ PP tokens | 1,506 (96.4%) |
| Total PP token occurrences | 8,916 |
| Unique PP MIDDLEs | 389 |
| Unique PP word forms | 2,372 |
| Token/MIDDLE ratio | 6.10x |
| Observed co-occurring MIDDLE pair types | 5,460 |
| Observed co-occurring word pair types | 20,757 |
| Within-folio avoidance pairs | 15,518 |
| Avoidance violations | 0 |

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `scripts/pp_cooccurrence_tests.py` | T1-T3 | `results/pp_cooccurrence_tests.json` |
| `scripts/pp_whole_token_test.py` | T9a-T9b | `results/pp_whole_token_tests.json` |
| `scripts/pp_dimension_tests.py` | T4-T8 | `results/pp_dimension_tests.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C728 | PP Co-occurrence Incompatibility Compliance | Non-random but fully explained by C475 |
| C729 | C475 Record-Level Scope | Zero avoidance violations across 19,576 pair occurrences |
| C730 | PP PREFIX-MIDDLE Within-Line Coupling | MI 2.79x between-line, p<0.001 |
| C731 | PP Adjacent Line Continuity | Jaccard ratio 1.10x, p=0.001 |
| C732 | PP Within-Line Selection Uniformity | No SUFFIX/diversity/position structure |
| C733 | PP Token Variant Line Structure | Whole-token structure beyond MIDDLE assignment, p<0.001 |

## Data Dependencies

- `scripts/voynich.py` (canonical transcript library)
- `phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json` (RI/PP classification, loaded by RecordAnalyzer)

## Cross-References

- C475 (MIDDLE incompatibility): Confirmed at record level (C729), sole co-occurrence driver (C728)
- C697 (PREFIX clustering): Consistent with T4's PREFIX-MIDDLE coupling (C730)
- C703 (PP folio homogeneity): Confirmed — pool is stable, draw is random within compatibility
- C233 (line independence): Not violated by T7's adjacency effect (population-level, not deterministic)
- C234 (position-free): All tests use set-based statistics, no positional assumptions
- C660-C663 (PREFIX-MIDDLE selectivity): T4 extends to within-line cross-token level
