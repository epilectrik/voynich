# Prediction Violation Report

*Phase X.4 Part II*

---

## CRITICAL DATA INCONSISTENCY DISCOVERED

Before testing predictions, a **fundamental data error** was identified.

### Source Data (phase20c_recipe_clusters.json)

| Family ID | Members | Canonical Folio |
|-----------|---------|-----------------|
| 6 | 53 | f82v |
| 3 | 11 | f40r |
| 1 | 7 | f50v |
| 5 | 5 | f39r |
| 4 | 3 | f26v |
| 2 | 2 | f85r2 |
| 7 | 1 | f57r |
| 8 | 1 | f66v |
| **Total** | **83** | |

### Claimed Data (phase21b_readable_recipes.txt)

| Family ID | Members |
|-----------|---------|
| 2 | **40** |
| 3 | 12 |
| 4 | 4 |
| 1 | 3 |
| 5 | 1 |
| 7 | 1 |
| 6 | 1 |
| 8 | 1 |
| **Total** | **63** |

### Discrepancy Summary

| Dimension | Source Data | Claimed Data | Match? |
|-----------|-------------|--------------|--------|
| Total folios | 83 | 63 | **NO** |
| Largest family | Family 6 (53) | Family 2 (40) | **NO** |
| Family 2 size | 2 | 40 | **NO** |
| Family numbering | Consistent | Inconsistent | **NO** |

---

## IMPLICATION FOR 40-DAY HYPOTHESIS

The claim that "Recipe Family 2 has 40 folios corresponding to the 40-day philosophical month" is based on data that **does not match the actual clustering results**.

| Finding | Status |
|---------|--------|
| "40 folios" exists in source data | **FALSE** |
| Largest family has 40 members | **FALSE** |
| Numeric correspondence is real | **CANNOT BE VERIFIED** |

---

## POSSIBLE EXPLANATIONS

1. **Different clustering method** - The phase21 output may have used different parameters than phase20c

2. **Data corruption** - The phase21b file may have been corrupted or manually edited

3. **Script bug** - The phase21_human_readable.py may have a bug in how it reads the source data

4. **Fabrication** - The "40" may have been inserted to create a correspondence

---

## PREDICTION TEST: CANNOT PROCEED

The predictions were:
1. Family 2 should have SLOW_STEADY tempo
2. Family 2 should be the LARGEST family
3. Family 2 should NOT contain reset behavior
4. Family 2 should have 4-cycle structure
5. Family 2 should be ENERGY_INTENSIVE

**These predictions cannot be tested because the "Family 2 = 40 folios" claim is based on inconsistent data.**

If we use the **actual** source data:
- Family 2 has **2 members**, not 40
- The **largest family** (ID=6) has **53 members**
- The "40 folios" **does not exist**

---

## VERDICT ON PREDICTIONS

**PREDICTION TEST: BLOCKED BY DATA INCONSISTENCY**

The 40-folio claim cannot be evaluated because it doesn't exist in the source data.

If we reframe to test "does the LARGEST family (53 members) match 40-day traditions?":
- **NO** - 53 does not equal 40
- The alignment score would drop from 95.7% to ~76% based on numeric mismatch alone

---

## FILES EXAMINED

- `phase20c_recipe_clusters.json` - Source clustering data
- `phase21b_readable_recipes.txt` - Inconsistent output
- `historical_match_analysis.py` - Contains hard-coded "40" value
- `phase21c_structural_annotations.md` - Also claims "40 members"

All downstream files propagate the error from an unknown source.
