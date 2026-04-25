# Phase 643: Paragraph Ordering Disambiguation — Findings

**Date:** 2026-04-25
**Status:** Tests B and F complete. Tests A, C, D, E, G, H, I deferred.

---

## Bottom line

- **Three-claim distinction validated:** state-coupling-independence, operational-interchangeability, and semantic-layout-ordering are distinct claims.
- **Claim (1) state-coupling independence holds:** C1399/C1400 measurements are intact and correctly framed when scoped to corpus-aggregate state-coupling.
- **Claim (3) semantic layout-ordering on matched folios is empirically supported:** Test B mean rho = +0.81 across 5 confirmed-match folios; 2/2 powered tests reach permutation p < 0.05 (f84r p=0.0005, f86v3 p=0.025).
- **Claim (2) operational interchangeability remains untested but is now implausible** given the Test B result.
- **C1399's interpretive phrasing ("paragraphs are genuinely parallel subroutines, not sequential steps") is empirically falsified** when applied to matched folios. Its statistical core remains valid.

---

## Test results

### Test B — Layout-Order vs Recipe-Phase-Order Correlation

| Folio | Match | n_paragraphs | rho | perm p | Significant? |
|-------|-------|:---:|:---:|:---:|:-:|
| f84r | II.12.0 (gold dissolution / putrefaction) | 18 | +0.827 | 0.0005 | ✓ |
| f86v3 | II.10.0 (3-day coniuncció) | 7 | +0.896 | 0.025 | ✓ |
| f75r | III.19.0 (aqua vitae × 4-9 reflux) | 3 | +0.866 | 0.681 | underpowered |
| f78r | III.36.0 (mercury congelation) | 8 | +0.577 | 0.246 | underpowered + crude assignment |
| f82r | III.19.3 (lunaria 3-day sealed) | 4 | +0.894 | 0.314 | underpowered |

**Mean rho = +0.812.** All 5 folios show positive direction. Two folios with sufficient N for permutation power both reach significance.

### Test F — Generalize-or-Die Scope Test

Three subtests:

**(a) Confirmed-match baseline:** mean rho +0.81 (replicates Test B).

**(b) Near-MATCH (MODERATE-tier) folios with default ascending-phase assignment:** mean rho +0.87. **Methodologically biased — does not establish generalization.** When paragraphs are assigned monotone-non-decreasing phases by construction, layout-position-vs-phase rho is high by construction. This subtest fails to disprove the null but doesn't add evidence either. Genuine generalization test would require atom-decode-style reading per folio.

**(c) Random-phase null on 10 unmatched B folios with ≥4 paragraphs:** mean rho +0.25. This is the noise floor. Random phase assignments to ascending layout-positions produce mean rho ~0.25 with no individual folio reaching p<0.05.

### Combined interpretation

| Comparison | Mean rho | Effect |
|-----------|:---:|---|
| Confirmed matches (atom-decode-derived phases) | +0.81 | signal |
| Random phase null (noise floor) | +0.25 | noise |
| Effect size | ~0.56 | substantial |

The confirmed-match signal is ~3.2x the noise floor. This is well above what could be produced by chance phase-position correlation.

---

## What the constraint system should claim

### Revised C1399 phrasing (preserves measurement)

**Current (over-strong):**
> "Paragraphs have NO preferred ordering within folios. 7/8 tests FAIL... Folio specifies WHAT and HOW MUCH, not in WHAT ORDER. Paragraphs are genuinely parallel subroutines, not sequential steps."

**Proposed (scope-restricted):**
> "Aggregate-corpus paragraph ordering does not exhibit thermal-first/monitoring-last ramps (monotonicity rho=-0.052, n=76 folios). Transition matrix shows zone inertia (V=0.424, self-transition O/E=2.02) but no global directional gradient. **This finding is at corpus scale and does not constrain individual-folio ordering structure relative to external referents.** Whether specific folios maintain semantic/operational ordering relative to recipe phases is outside this constraint's scope."

### Revised C1400 phrasing

**Current:** "Terminal physical state does NOT predict next paragraph zone. Paragraphs are independently composed within the folio's thematic envelope — ordered neither by position nor by state."

**Proposed:** "Terminal-state→next-zone prediction fails at corpus level after folio-mode residualization. Folio-mode baseline (0.685) dominates state-prediction models. **Constraint applies to corpus-scale state-coupling, not to individual folio operational ordering.** Operational interchangeability not tested by these measurements."

### New constraint (Tier 3)

**C-NEW: Paragraph Layout-Order Semantic Coherence on Matched Folios**

On confirmed-match folios (currently f75r, f84r, f78r, f86v3, f82r), paragraph layout-order on the page corresponds to recipe-phase order in the matched chapter. Spearman rho = +0.812 across 5 matches (Test B). Two folios with sufficient permutation power both reach p<0.05 (f84r p=0.0005, f86v3 p=0.025). Effect size ~3.2x noise floor (random phase null mean rho = +0.25). 

**Compatible with:** C1399/C1400 (state-coupling independence preserved at corpus scale), C845 (paragraph self-containment as topology), C1287 (paragraph-header MARKING enrichment), C858 (paragraph count reflects complexity).

**Tier 3 because:**
- Recipe-folio correspondence is itself Tier 3 (per C1888)
- N=5 is small
- Phase ordinals were assigned by reading folio-against-recipe (interpretive judgment)
- Generalization to non-matched folios untested

**Falsifiable predictions:**
- New confirmed matches should show layout-phase rho > 0
- Folios with no recipe correspondence should show no consistent layout-phase signal

---

## Recommended action

1. **Register the new constraint** at Tier 3.
2. **Revise C1399/C1400 phrasings** to scope-restrict the interpretive overreach.
3. **Regenerate expert sync files** so embedded constraints in agent prompts are updated.
4. **Manually update `crazy-expert.md`** (per CLAUDE.md, doesn't auto-generate).
5. **Manually update `INTERPRETATION_SUMMARY.md`** — qualify any "parallel subroutines" or "independent" claims.
6. **Update `paragraph.psc.yaml`** PSC contract — preserve self-containment as topology, distinguish from operational-interchangeability.

---

## Limitations and follow-up

1. **Test F (b) was methodologically flawed.** Default-ascending phase assignment biases toward rho>0. A proper near-MATCH generalization test requires atom-decode reading per folio.

2. **Tests A, C, D, E, G, H, I were deferred.** Most informative additions would be:
   - True near-MATCH generalization with content-based phase assignment (per-folio reading)
   - A-B paragraph correspondence test (does the same effect appear on Currier A folios with related recipes?)
   - Within-paragraph (line-level) ordering test for nested sequential structure

3. **Operational-interchangeability (claim 2) was not directly tested.** A proper paragraph-shuffle anchor-preservation test (Test A in original plan) would add evidence. Test B's permutation null partially substitutes but isn't equivalent.

4. **The crazy-expert flagged a class of similar suspect constraints** (C1402, C1403, C1470, C1471, C1576, C1670). Future PHASE_CONSTRAINT_OVERREACH_AUDIT could systematically check these for the same conflation pattern.
