# C1391: s-Atom Staging Sequence Profile

**Tier:** 2
**Scope:** B
**Phase:** S_ATOM_SEMANTIC_DEEP_DIVE (Phase 501) + PHASE_503_S_MODIFIER (Phase 503)
**Depends on:** C1195 (atom gloss confidence tiers), C1190 (MIDDLE additive composition), C1209 (slot syntax)

## Constraint

Atom s (gloss: "sequence") is the #1 STAGING atom in the system (87.50%, 6.721x enrichment) with perfect compound determinism (6/6 compounds at 100% category purity). s operates in the FQ macro-state (64.6%, 3.59x), not AXM — distinguishing it from other main-loop atoms c (93.5% AXM) and p (88.7% AXM). The sh compound-suffix family is the dominant structural feature: s->h junction at 13.16x enrichment (208 observed), sh occupies terminal position (73.9%), and the first atom X in Xsh determines the compound category across 4 distinct categories. The h-junction effect pulls sh-family compounds toward MONITORING, while non-h compounds (os, es, cs) distribute across OPERATION, STAGING, and MARKING respectively. R4 PRECISION enrichment is 2.55x. NEUTRAL timing dominates at 77.3%. H1 "sequence" is the best hypothesis (S-S10: 3/4 vs H2 2/4, H3 2/4). Gloss revision not warranted.

## Key Evidence

| Property | Value | Significance |
|----------|-------|-------------|
| STAGING enrichment | 6.721x (87.50%) | #1 STAGING atom in system |
| Compound determinism | 6/6 at 100% purity | Perfect: sh=MON, ksh=MON, lsh=MON, os=OPER, es=STAG, cs=MARK |
| Macro-state | FQ 64.6% (3.59x) | Cycling operations, not AXM-confined |
| s->h junction | 208 observed (13.16x) | Intra-compound, not cross-token (ratio 208:1) |
| sh terminal rate | 73.9% | sh is compound-suffix unit |
| R4 PRECISION | 2.55x enrichment | High-precision contexts |
| NEUTRAL timing | 77.3% | Neither precedes nor follows state changes |
| Line position | 0.547 +/- 0.362 | Mid-line, broadly distributed |
| Battery score (Phase 501) | 6/12 PASS | Standard battery |
| Battery score (Phase 503) | 5/8 PASS | Modifier-focused battery |
| Combined score | 11/20 PASS | PLAUSIBLE maintained |
| Modifier consistency | cosine 0.966 | Extremely stable across corpus halves (SM-8) |

## Compound Architecture

The s-atom has a bifurcated compound architecture:
- **sh-family** (sh, ksh, lsh, osh, tsh): The h-junction transforms most sh-family compounds toward MONITORING (ksh, lsh, osh = 100% MONITORING), but tsh=FLOW and psh=MARKING — the h-junction is not universal, t and p override it.
- **non-h compounds** (os, es, cs): Each maps to a DIFFERENT category (OPERATION, STAGING, MARKING), demonstrating s acts as a structural modifier rather than a category-dominant element in non-h contexts.

This bifurcation explains the 0/3 glossed compound match: all 3 glossed compounds (sh="verify", ksh="scan", lsh="verify") are in the sh-family and therefore MONITORING — but standalone s is overwhelmingly STAGING.

## Modifier Characterization (Phase 503)

Phase 503 tested s with a purpose-built 8-test modifier battery (5/8 PASS). Key findings:

- **SM-8 (DECISIVE):** s's base-dependent modifier behavior is extremely stable (cosine 0.966 across independent corpus halves). All 5 testable compounds >= 0.925. s is a PREDICTABLE modifier, not noise.
- **SM-2:** s systematically shifts partner category (4/5 Xs compounds have different primary category from X alone). Every Xs compound is 100% single-category purity.
- **SM-3:** s-modifier PREFIXes amplify base selectivity (sa purity 52.3% beats 2/3 other a-base modifiers; sh beats ch).
- **SM-4:** s changes suffix selection — sh-initial MIDDLEs are 100% bare (vs h-initial mix), es shows dramatic suffix shift from e (chi2=822, p<0.001).
- **SM-7:** sh routes differently from ch at PREFIX level (chi2=211.2, p~0), replicating C1243 at 1.74x (stronger than original 1.33x).
- **SM-1 (INFORMATIVE FAIL):** h-junction not universal — tsh=FLOW, psh=MARKING. t and p atoms override the sh->MONITORING pathway.

s is best understood as a **sequencing modifier**: it doesn't inject a category, it systematically transforms its partner's category in a reproducible, deterministic way.

## Hypothesis Discrimination

| Hypothesis | Score | Evidence |
|-----------|-------|---------|
| H1 "sequence" (sequenzieren) | 3/4 | NEUTRAL timing, R4 enrichment, line position |
| H2 "sift" (sichten) | 2/4 | R4 enrichment, line position only |
| H3 "step" (Schritt) | 2/4 | R4 enrichment, line position only |

H2 "sift" rejected: MONITORING only 2.84% standalone, non-h compounds not MONITORING-dominant.

## Falsification

Would be falsified if s-initial tokens were shown to be MONITORING-dominant outside the sh compound family, or if additional s-compound glosses contradict the STAGING interpretation.

## Provenance

- `phases/S_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_s01_category_profile.py` through `p_s12_compositional_convergence.py` — 12 standard battery scripts (Phase 501)
- `phases/S_ATOM_SEMANTIC_DEEP_DIVE/results/s_atom_prediction_results.json` — Phase 501 structured results
- `phases/PARALLEL_MONITORING_TRACKS/PHASE_503_S_MODIFIER/scripts/sm01_*.py` through `sm08_*.py` — 8 modifier battery scripts (Phase 503)
- `phases/PARALLEL_MONITORING_TRACKS/PHASE_503_S_MODIFIER/results/s_modifier_results.json` — Phase 503 structured results
