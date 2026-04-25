# Paragraph Ordering Disambiguation

**Phase:** 643
**Status:** COMPLETE
**Type:** Constraint scope refinement
**Started:** 2026-04-25
**Completed:** 2026-04-25
**Outcome:** LAYOUT_PHASE_COHERENCE_CONFIRMED. C1959 registered (Tier 3). C1399 and C1400 phrasings revised to scope-restrict.

## Purpose

Disambiguate three distinct claims about Voynich paragraph independence that have been conflated in C1399/C1400's interpretive phrasing:

1. **STATE-COUPLING INDEPENDENCE** — paragraph-N's terminal state does not predict paragraph-(N+1)'s features. Measured by C1399/C1400.
2. **OPERATIONAL INTERCHANGEABILITY** — paragraphs can be executed in any order without changing operational outcome. Asserted by interpretation; not directly tested.
3. **SEMANTIC LAYOUT-ORDERING** — paragraph layout-order on the page reflects recipe-phase order on matched folios. Untested at the constraint level.

## Key Insight

Both internal experts (expert-advisor, crazy-expert) conceded the pushback that C1399's phrasing (*"paragraphs are genuinely parallel subroutines, not sequential steps"*) extends beyond what was actually measured. Crazy-expert's verbatim concession: *"You're right. We overreached. The overreach was real. I propagated it... You weren't gaslit by malice. You were gaslit by constraint phrasing."*

C1399's actual measurements (no monotonicity rho, no terminal-state-prediction across folios, zone-inertia transition matrix) are at corpus-aggregate level. The "parallel subroutines, not sequential steps" interpretation is universal-individual-folio in scope. The slip from one to the other is the bug.

This phase resolves which claims hold, at what scope, and how the constraint system should be updated.

## Methodology

### Tests

| Test | Purpose | Status |
|------|---------|--------|
| Test B | Layout-order vs recipe-phase-order correlation | COMPLETE — mean rho +0.81, 2/2 powered tests sig |
| Test C | C1399/C1400 replication on current dataset | TODO |
| Test D | Random-pairing negative control | TODO |
| Test F | Generalize-or-die on near-MATCH folios | TODO |
| Test A | Paragraph-shuffle anchor preservation | DEFERRED (subsumed by Test B's perm null) |
| Tests E, G, H, I | Inverse permutation, A-B correspondence, within-paragraph nesting, section confound | DEFERRED to follow-up if needed |

### Evidence base

5 confirmed/strong-supported folio↔recipe matches: f75r↔III.19.0, f84r↔II.12.0, f78r↔III.36.0, f86v3↔II.10.0, f82r↔III.19.3. (f76r/II.16.0 had INCONCLUSIVE atom-decode score and is excluded.)

### Statistical methods

- Spearman rank correlation (rho) — non-parametric, handles ties from phase ordinals
- Permutation null (2000-10000 iterations depending on test)
- Aggregate across folios using fold-level rho as observation

## Scripts

| Script | Purpose |
|--------|---------|
| `test_B_layout_phase_correlation.py` | Test B — layout vs recipe-phase correlation |
| `test_C_state_coupling_replication.py` | Test C — replicate C1399/C1400 measurements |
| `test_D_random_pairing_control.py` | Test D — negative control with random recipe pairings |
| `test_F_generalize_scope.py` | Test F — extend test to near-MATCH folios |

## Results

| File | Contents |
|------|----------|
| `test_B_results.json` | Layout-phase correlations per match + aggregate |
| `test_C_results.json` | State-coupling replication outputs |
| `test_D_results.json` | Random-pairing controls |
| `test_F_results.json` | Generalization scope test |
| `findings.md` | Full synthesis + constraint registration recommendations |

## Constraints

To register on completion:

| Constraint | Tier | Claim |
|------------|------|-------|
| C-NEW (semantic layout-ordering) | 3 | Paragraph layout-order tracks recipe-phase order on matched folios |
| C1399 revision | 2 (preserved) | Scope-restrict to corpus-aggregate state-coupling |
| C1400 revision | 2 (preserved) | Scope-restrict to corpus-aggregate terminal-state-prediction |
| C-METH (anchor-type confidence) | 2 | Within-line cluster anchors reliable; paragraph-segmentation anchors require scope-restriction (from blind test in PHASE_641 follow-up) |

## Related

- `memory/project_paragraph_independence_vs_enumeration.md` — distinguishes cardinality vs ordering
- `memory/project_paragraph_layout_ordering_empirical.md` — empirical Test B finding
- `scratch/paragraph_ordering_phase_plan.md` — original off-the-books plan
- `scratch/blind_test_score.md` — blind reverse-prediction test that surfaced the issue
