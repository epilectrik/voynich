# C1360: Forbidden Transition Violations Are Dispersed and Rare

**Tier:** 2
**Scope:** B, line, forbidden transitions
**Phase:** LINE_MICRO_GRAMMAR (Phase 474)
**Depends on:** C109

## Statement

Forbidden MIDDLE-pair transitions are observed at a rate of 0.053% (11 violations in 20,676 transitions), far below the ~35% violation rate implied by C109's 65% compliance. This discrepancy likely reflects different counting methodologies. At the MIDDLE level, the 17 forbidden pairs are nearly absolutely obeyed. The 11 violations that do occur distribute uniformly across line positions (KS=0.232, p>=0.05). 10 of 11 violations are a single type: dy→aiin.

## Evidence

| Metric | Value |
|--------|-------|
| Total MIDDLE transitions | 20,676 |
| Forbidden violations | 11 |
| Violation rate | 0.053% |
| KS statistic vs uniform | 0.232 |
| Critical value (alpha=0.01) | 0.492 |
| Forbidden entropy | 2.187 bits |
| All-transition entropy | 2.307 bits |
| Dominant violation type | dy→aiin (10/11) |

## Structural Implication

The forbidden transitions are effectively absolute prohibitions at the MIDDLE level — the grammar avoids them almost perfectly. The rare violations that do occur show no positional preference; they are not concentrated at zone boundaries or any other line position. Hazard avoidance is uniform across the line, consistent with it being a global grammatical constraint rather than a position-specific mechanism.

**Results:** `phases/LINE_MICRO_GRAMMAR/results/line_micro_grammar.json`
