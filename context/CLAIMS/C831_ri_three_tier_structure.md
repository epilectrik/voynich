# C831: RI Three-Tier Population Structure

**Tier:** 2
**Scope:** A
**Phase:** A_RECORD_B_ROUTING_TOPOLOGY

## Constraint

> **Scope Note (2026-01-30):** RI structure analysis uses paragraph-level positions (INITIAL,
> MIDDLE, FINAL). Paragraph is the A-internal record unit (C881). For A-B vocabulary
> correspondence, folio is the operational unit (C885: 81% coverage).

RI (Registry-Internal) MIDDLEs partition into three distinct population tiers based on repetition and positional behavior:

| Tier | Rate | Count | Behavior |
|------|------|-------|----------|
| Singletons | 95.3% | 674 | Appear exactly once corpus-wide |
| Position-locked | ~4% | 29 | Repeat but stay within INITIAL, MIDDLE, or FINAL |
| Linkers | 0.6% | 4 | Appear as FINAL in one paragraph, INITIAL in another |

## Evidence

From t17_ri_repeater_position.py:

```
Total RI types: 707
  Singletons (1 occurrence): 674 (95.3%)
  Repeaters (2+ occurrences): 33 (4.7%)

Repeater position patterns:
  FINAL+MIDDLE                   10
  MIDDLE                          8
  INITIAL+MIDDLE                  7
  FINAL+INITIAL+MIDDLE            3
  INITIAL                         3
  FINAL+INITIAL                   1
  FINAL                           1
```

The 4 linkers (FINAL+INITIAL or FINAL+INITIAL+MIDDLE) are:
- cthody, ctho, ctheody, qokoiiin

## Interpretation

The three-tier structure suggests different RI functions:

1. **Singletons** - Unique situation identifiers; each marks a specific condition that appears exactly once in the corpus
2. **Position-locked** - Category markers that can recur but maintain consistent positional role (always INITIAL, always FINAL, etc.)
3. **Linkers** - Cross-reference markers that connect the output of one record to the input of another

## Provenance

- t17_ri_repeater_position.json: singleton_count=674, repeater_count=33, linking_candidates=4
- Related: C498 (RI definition), C832-C836 (RI structure details)

## Status

CONFIRMED - Three-tier structure is distributional fact with clear boundaries.
