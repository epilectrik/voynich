# C1381: o-Initial MIDDLE Enrichment in AZC

**Tier:** 2
**Scope:** CROSS
**Phase:** GLOSS_PREDICTION_TESTS (Phase 495)
**Date:** 2026-03-02

## Statement

o-initial MIDDLEs are 1.9x enriched in AZC (apparatus classification layer) versus Currier B text (22.4% vs 11.8%, chi2=281.3, p<0.0001). Within B, words shared with AZC have higher o-initial rates than B-exclusive words (13.5% vs 9.8%). Section C (structurally closest to AZC) has the highest B-internal o-initial rate (18.9%). The enrichment forms a smooth gradient from the apparatus classification layer into the execution layer.

## Hypothesis Tested

The crazy-expert agent proposed that the initial atom of a MIDDLE carries operational semantics, with o encoding "apparatus/operation." If true, o-initial MIDDLEs should be disproportionately present in AZC, the layer that classifies vocabulary by positional operational character. This would connect atom-level gloss hypotheses (Tier 4) to established cross-system structural behavior (Tier 2).

## Evidence

### T1: AZC vs Currier B o-initial rate — PASS

| Population | o-initial | Total | Rate |
|-----------|-----------|-------|------|
| AZC | 723 | 3,227 | 22.4% |
| Currier B | 2,717 | 23,096 | 11.8% |

- AZC/B ratio: 1.905x
- Chi-squared: 281.257, p < 0.0001
- 3,227 AZC tokens, 1,660 unique words

### T2: B-internal gradient by AZC sharing — PASS

| B subset | o-initial | Total | Rate |
|---------|-----------|-------|------|
| Shared with AZC | 1,671 | 12,404 | 13.5% |
| B-exclusive | 1,046 | 10,692 | 9.8% |

- Shared/exclusive ratio: 1.377x
- Words that appear in both AZC and B carry higher o-initial MIDDLE rates than B-exclusive words

### T3: B section breakdown — PASS

| Section | o-initial | Total | Rate |
|---------|-----------|-------|------|
| B | 627 | 6,850 | 9.2% |
| C | 279 | 1,480 | 18.9% |
| H | 456 | 3,433 | 13.3% |
| S | 1,267 | 10,671 | 11.9% |
| T | 88 | 662 | 13.3% |

- Section C (structurally closest to AZC per C1269) has highest B-internal o-initial rate (18.9%)
- Section B (most distant from AZC) has lowest (9.2%)
- Gradient: AZC (22.4%) → Section C (18.9%) → H/T (13.3%) → S (11.9%) → B (9.2%)

## Relationship to Existing Constraints

- **C496** (Tier 2): Nymph-adjacent S-positions show 75% o-PREFIX rate. C1381 extends this from PREFIX to MIDDLE initial atom, and from nymph positions to all of AZC.
- **C525** (Tier 3): Label morphological stratification shows o-prefix 50% vs 20% text. C1381 provides a cross-system mechanism for why o concentrates where it does.
- **C1269** (Tier 2): AZC zones specialize by operational category; C zone is OPERATION-enriched. C1381 shows o-initial MIDDLEs follow this same pattern.
- **C1273** (Tier 2): AZC-exclusive vocabulary is MARKING/THERMAL-enriched. C1381 adds that the shared vocabulary is o-initial-enriched.
- **C1274** (Tier 2): THERMAL category fraction in AZC-shared vocabulary predicts B escape rate. C1381 suggests the initial atom of MIDDLEs is part of the mechanism connecting AZC classification to B dynamics.

## What This Does NOT Prove

- Does not prove o "means" apparatus or operation (semantic ceiling, C171)
- Does not prove atom-level glosses are correct
- Does prove that the initial atom of a MIDDLE predicts cross-system vocabulary distribution, which is a novel structural finding at the atom level

## Origin

Prediction P7 from crazy-expert agent's analysis of Tier 4 gloss/etymology tables. The crazy-expert proposed 8 testable predictions; 5 were already confirmed by existing constraints, 3 were tested in Phase 495. P7 was the only clean confirmation; P6 (n-terminal at mode boundaries) was inverted, P8 (f-atoms in REGIME_3) was wrong direction.
