# C1441: Active Terminal-Suffix Exclusion Grammar Rule

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, suffix, exclusion, grammar, rule, C1440, C1438, C1412
**Phase:** 522 (TWO_LEVEL_CLOSURE)
**Date:** 2026-03-05

## Claim

In the body-line-final, non-paragraph-final population (N=1,439, baseline suffix rate 45.8%), three terminals actively suppress suffix attachment: y (O/E=0.159, suffix rate 7.3%), m (O/E=0.105, suffix rate 4.8%), n (O/E=0.168, suffix rate 7.7%). l and r are neutral (O/E ~0.95-1.22), h is always suffixed (100%). The three-tier opacity gradient (C1440) is a grammar rule, not a distributional artifact.

## Evidence

### Matched population test

To distinguish active exclusion from passive population separation, the test restricts to body-line-final tokens that are NOT paragraph-final -- positions where both MIDDLE-terminal closure and suffix attachment are structurally plausible.

| Terminal | N in population | Suffix Rate | Population baseline | O/E | Verdict |
|----------|----------------|------------|---------------------|-----|---------|
| y | 302 | 7.3% | 45.8% | 0.159 | ACTIVE_EXCLUSION |
| m | 166 | 4.8% | 45.8% | 0.105 | ACTIVE_EXCLUSION |
| n | 104 | 7.7% | 45.8% | 0.168 | ACTIVE_EXCLUSION |
| l | 205 | 43.4% | 45.8% | 0.948 | NEUTRAL |
| r | 122 | 55.7% | 45.8% | 1.217 | NEUTRAL |
| h | 44 | 100% | 45.8% | 2.184 | NEUTRAL (always suffixed) |

### m/am specific exclusion test

The -am suffix (117 tokens) and m-terminal MIDDLE (166 tokens) co-occur at only 1 token (expected 13.5). Fisher exact test: odds ratio = 0.06, p = 0.000012. This is 13.5x depletion in a population where both are plausible.

## Interpretation

The opacity gradient is enforced by the grammar, not by vocabulary separation. When y, m, or n appear as the MIDDLE terminal atom, the grammar actively blocks suffix attachment even in positions where suffix is the norm. This confirms that MIDDLE terminal atoms ACT AS suffix gatekeepers (C1412) via active suppression, not passive absence.

## Falsification Criteria

1. If y/m/n show O/E > 0.5 in the matched population under alternative definitions
2. If the m/am co-occurrence O/E exceeds 0.3 under replication

## Method

- Population: body-line-final (not first line of paragraph, not last line of paragraph)
- Baseline suffix rate computed from all tokens in population
- Per-terminal suffix rate compared to baseline via O/E ratio
- m/am specific test: Fisher exact on 2x2 table (m-term yes/no x am-suffix yes/no)

**Script:** `phases/TWO_LEVEL_CLOSURE/scripts/two_level_closure.py`
**Results:** `phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json` (T10)

## Dependencies

- C1440 (three-tier terminal opacity gradient)
- C1438 (m-terminal categorical suffix suppression)
- C1439 (m-terminal and -am suffix orthogonal)
- C1412 (MIDDLE dominates suffix determination)
