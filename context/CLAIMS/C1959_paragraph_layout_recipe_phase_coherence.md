# C1959: Paragraph Layout-Order Recipe-Phase Coherence on Matched Folios

**Tier:** 3 (PROVISIONAL)
**Scope:** B, paragraph, ordering, recipe-correspondence, layout
**Phase:** PARAGRAPH_ORDERING_DISAMBIGUATION (Phase 643)
**Extends:** C1399 (paragraph ordering null at corpus-aggregate scope), C1400 (state-coupling independence), C845 (paragraph self-containment as topology)
**Relates to:** C1287 (paragraph-header MARKING enrichment), C858 (paragraph count reflects complexity), C1888 (recipe-folio correspondence Tier 3), C1882-C1956 (matched folio↔recipe pairs)
**Resolves:** Pushback on C1399's interpretive overreach ("paragraphs are genuinely parallel subroutines, not sequential steps") that conflated three distinct claims about paragraph independence.

---

## Statement

On confirmed-match folio↔recipe pairs (Currier B), **paragraph layout-order on the page corresponds to recipe-phase order in the matched chapter**. Paragraphs encoding setup/specification phases appear earlier on the folio than paragraphs encoding primary procedure, which appear earlier than iteration/sub-procedure paragraphs, which appear earlier than closure paragraphs.

This is **compatible with** C1399/C1400 (paragraphs are state-coupling-independent at corpus-aggregate scope) but **falsifies** the strong-form interpretive reading of C1399 that paragraphs are operationally interchangeable / not sequential at the individual-folio level when measured against external referents.

---

## Empirical evidence (Test B, Phase 643)

For each confirmed-match folio, each paragraph was assigned a recipe-phase ordinal (1=setup/specification, 2=primary procedure, 3=iteration/sub-procedure, 4=closure) based on prior atom-decode-style reading against the matched Catalan recipe. Spearman rho computed between paragraph layout-position and recipe-phase ordinal.

### Initial 5 matches (Phase 643 — Test B)

| Folio | Match | n_paragraphs | rho | perm p | Significant? |
|-------|-------|:---:|:---:|:---:|:-:|
| f84r | II.12.0 (gold dissolution / putrefaction) | 18 | +0.827 | 0.0005 | ✓ |
| f86v3 | II.10.0 (3-day coniuncció) | 7 | +0.896 | 0.025 | ✓ |
| f75r | III.19.0 (aqua vitae × 4-9 reflux) | 3 | +0.866 | 0.681 | underpowered |
| f78r | III.36.0 (mercury congelation) | 8 | +0.577 | 0.246 | underpowered |
| f82r | III.19.3 (lunaria 3-day sealed) | 4 | +0.894 | 0.314 | underpowered |

### Extended evidence (Phase 644 REVERSE_PREDICTED_ATOM_VERIFICATION — Test B Extended)

Two additional confirmed matches added 2026-04-25 (reverse-predicted from blind test, then atom-decode verified at STRONG SUPPORT):

| Folio | Match | n_paragraphs | rho | perm p | Significant? |
|-------|-------|:---:|:---:|:---:|:-:|
| f108v | III.29.0 (mercury sublimation) | 10 | +0.924 | **0.0020** | ✓★ |
| f79v | II.8.0 (first liquefaction) | 7 | +0.954 | **0.0050** | ✓★ |

### Further extension (Phase 646 RECIPE_REVERSE_FOLIO_SEARCH)

One additional confirmed match added 2026-04-25 via reverse-direction signature search (recipe → folio):

| Folio | Match | n_paragraphs | rho | perm p | Significant? |
|-------|-------|:---:|:---:|:---:|:-:|
| f77r | III.28.0 (4-element temperament) | 13 | +0.861 | **0.0005** | ✓★ |

f77r has within-line 4-clusters at L11 and L34 matching recipe's `.iiii. elements`. 4 paragraph-initial line-starts at L1-L4 form a 4-element specification block. Recipe is theoretical-exposition + operational iteration; folio profile is high-qokeedy + low-dar matching the abstract recipe character. Atom-decode score: 7 MATCH / 1 WEAK / 0 MISMATCH = STRONG SUPPORT.

### Aggregate across all 8 confirmed matches

- **Mean rho: ~+0.85**
- All 8 folios show positive direction (8/8)
- **5 folios reach strict significance (perm p < 0.05):** f84r, f86v3, f108v, f79v, f77r
- **3 folios at n≥10 reach strict significance:** f84r (n=18), f108v (n=10), f77r (n=13)
- Random-phase null mean rho = +0.245 (Test F subtest c, n=10 unmatched B folios with random phase assignments)

**Effect size: ~3.5x noise floor.**

---

## Three-claim distinction

The semantic content of "paragraph independence" was previously conflated. Three distinct claims must be tracked separately:

| Claim | Status | Evidence |
|-------|--------|----------|
| **(1) State-coupling independence** | TRUE at corpus-aggregate scope | C1399, C1400 (preserved measurements) |
| **(2) Operational interchangeability** | UNTESTED | No constraint measures paragraph-shuffle outcome preservation |
| **(3) Semantic layout-ordering on matched folios** | TRUE on confirmed matches | C1959 (this constraint) |

The strong-form interpretive phrasing of C1399 ("paragraphs are genuinely parallel subroutines, not sequential steps") collapsed (1), (2), and (3). C1959 establishes that (3) holds on matched folios.

---

## Operational interpretation

Folio paragraphs behave like blocks in a modern lab SOP: each block is internally self-contained (state-coupling-independent, per C1399/C1400 and C845), but the document as a whole has a meaningful linear reading order (specification → primary → iteration → closure). The blocks could in principle be executed in alternative orders without state-coupling problems, but the document's layout reflects the natural operational sequence of the matched recipe.

This is consistent with the **production-engineered workshop implementation** framing of Currier B: a workshop reference structured for an operator who reads through paragraphs in order on the page while not requiring them to execute that order.

---

## Falsifiable predictions

1. **CONFIRMED 2026-04-25:** New confirmed matches should show layout-phase rho > 0 with permutation p < 0.10 when n_paragraphs ≥ 7. f108v (n=10, rho=+0.924, p=0.002) and f79v (n=7, rho=+0.954, p=0.005) both confirmed at strict significance.
2. Folios with no recipe correspondence should show no consistent layout-phase signal (random-phase null in Phase 643 confirmed mean rho ~0.25 baseline).
3. Paragraph-shuffle of a confirmed-match folio should DECREASE recipe-anchor scoring (operational interchangeability, claim 2, predicted false).
4. The same effect should appear on near-MATCH folios when phase ordinals are assigned via atom-decode-style reading (Phase 643 Test F (b) used default-ascending assignment which was methodologically biased; proper test pending).

## Tier 2 promotion threshold

Per expert-advisor's stated criterion: *"If 3+ additional confirmed-match folios with n≥10 paragraphs reach individual significance (and direction holds), this could be reconsidered for Tier 2."*

**As of 2026-04-25:** 2 additional matches (f108v, f79v) added beyond original 2 individually-significant (f84r, f86v3). Strict reading: short of 3-additional threshold by 1. Pragmatic reading: 4/7 strict-significance + 7/7 positive direction + reverse-prediction validation suggests the constraint is empirically stronger than originally registered. Tier 3 retained pending explicit promotion review.

---

## Caveats

- N=7 matches is moderate for aggregate statistical claims
- Phase ordinals assigned by reading folio-against-recipe (interpretive judgment); independent verification would strengthen
- Recipe-folio correspondence is itself Tier 3 (per C1888); C1959 inherits that uncertainty
- Test F (b) attempted to extend the finding to MODERATE-tier near-MATCH folios but used default-ascending phase assignment which is methodologically biased toward rho > 0; proper near-MATCH generalization test deferred
- Operational interchangeability (claim 2) was not directly tested

---

## Method

- 5 confirmed-match folios from atom_decode_vs_catalan: f75r, f84r, f78r, f86v3, f82r (f76r excluded due to INCONCLUSIVE atom-decode score)
- Paragraph counts derived from `Transcript.currier_b()` with par_initial flags, labels excluded
- Phase ordinals manually assigned per atom-decode reading (rationale documented per folio in script)
- Spearman rank correlation, permutation null with 2000 iterations, fixed seed 42

**Script:** `phases/PARAGRAPH_ORDERING_DISAMBIGUATION/scripts/test_B_layout_phase_correlation.py`
**Results:** `phases/PARAGRAPH_ORDERING_DISAMBIGUATION/results/test_B_results.json`
**Findings:** `phases/PARAGRAPH_ORDERING_DISAMBIGUATION/results/findings.md`
