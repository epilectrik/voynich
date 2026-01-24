# Pipeline Gap Analysis: A->B Triangulation Tests

## Executive Summary

Three diagnostic tests were run to determine why recipe triangulation fails to identify specific Voynich tokens for specific Brunschwig materials.

**Result: PP vocabulary is NOT discriminative by recipe type.**

Different recipes (rose water vs animals) with different fire degrees (1 vs 4) trace to 90.8% of the same A folios. The constraint C384 (no entry-level A-B coupling) is CONFIRMED.

---

## Test 1: REGIME_4 Vocabulary Distinctiveness

**Question**: Does REGIME_4 have exclusive PP vocabulary that could identify fire degree 4 recipes?

**Result**:
- REGIME_4 has 159 PP MIDDLEs total
- 19 are exclusive to REGIME_4 (11.9%)
- **BUT** only 31 A entries contain any REGIME_4-exclusive PP
- **AND** 0 entries have 2+ REGIME_4-exclusive PP
- **AND** 0 entries overlap with animal RI tokens

**Verdict**: REGIME provides weak vocabulary-level selection. Not useful for triangulation.

---

## Test 2: Multi-Dimensional Conjunction Narrowing

**Question**: Does combining multiple recipe dimensions narrow candidates synergistically?

**Dimensions tested**:
- REGIME_4: 25 folios (30.5%)
- High qo (>=18.54%): 41 folios (50.0%)
- High aux (>=15.64%): 41 folios (50.0%)
- Low da (<=6.46%): 45 folios (54.9%)

**Result**:
| Conjunction | Expected | Actual | Ratio |
|-------------|----------|--------|-------|
| Full 4D | 3.4 folios | 1 folio | 0.29x |

Single folio selected: **f95v1**
- 16 PP MIDDLEs
- 6 overlap with animal A entries

**Verdict**: Conjunction is synergistic (better than independent). Multi-dimensional triangulation CAN narrow to single B folios. But the PP vocabulary from that folio still doesn't uniquely identify animal A entries.

---

## Test 3: Rose Water Control

**Question**: Does a different recipe (plant-based, fire degree 1) trace to different A entries than animals (fire degree 4)?

**Recipe comparison**:
| Property | Rose Water | Animals |
|----------|------------|---------|
| Fire degree | 1 | 4 |
| Source | cold_moist_flower | animal |
| REGIME | REGIME_1 (31 folios) | REGIME_4 (25 folios) |

**Result**:
- Rose-matched A entries: 298
- Animal-matched A entries: 247
- **A folio overlap: 89 folios (90.8%)**

**Verdict**: Completely different recipes trace to nearly identical A folios. PP vocabulary is NOT discriminative by recipe type.

---

## Implications for C384

Original C384 statement: "No entry-level A-B coupling"

**This analysis CONFIRMS C384** - the original single-token tests were not an artifact. Even multi-dimensional triangulation cannot establish entry-level coupling because:

1. PP vocabulary is structurally shared across recipes
2. Different fire degrees (REGIME_1 vs REGIME_4) don't create discriminative PP subsets
3. The 43.4% PP vocabulary (285 MIDDLEs) participates in ALL recipe execution

---

## Why Animal Identification Fails

We found 9 folio-exclusive animal tokens matching Brunschwig's 9 animals:
- chald, hyd, olfcho, eoschso, hdaoto, cthso, eyd, teold, olar

But we cannot map specific tokens to specific animals because:

1. **All animals use fire degree 4** - no REGIME discrimination within animal class
2. **PP vocabulary overlaps 90%** - even rose water maps to same A folios as animals
3. **RI tokens encode material identity** - but RI stays in A, never enters B
4. **B receives operations, not identities** - C384 is structural, not statistical

The grammar encodes **operational behavior** (what to do with animals), not **material identity** (which animal this is). This is exactly what constraint C171 (closed-loop control) predicts.

---

## Architectural Interpretation

```
A (catalog)        AZC (filter)       B (executor)
[chicken] -------> [REGIME_4] -------> [process_animal]
[goose]   -------> [REGIME_4] -------> [process_animal]
[frog]    -------> [REGIME_4] -------> [process_animal]
[rose]    -------> [REGIME_1] -------> [process_plant]

All REGIME_4 animals share PP vocabulary -> same B folios
Different REGIMEs still trace to 90% same A folios (shared infrastructure)
```

The PP vocabulary is **infrastructural**, not **discriminative**. It encodes the grammar of processing, not the taxonomy of materials.

---

## Files

- Test 1: `scripts/test1_regime_vocabulary.py`
- Test 2: `scripts/test2_conjunction_narrowing.py`
- Test 3: `scripts/test3_rose_water.py`
