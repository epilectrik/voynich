# Family Abstraction Sensitivity Analysis

*Phase X.4 Part III*

---

## Purpose

Test whether the "40 folio" correspondence survives:
- Alternative clustering methods
- Slightly altered family boundaries
- Random perturbation of equivalence criteria

---

## FINDING: THE "40" DOES NOT EXIST IN SOURCE DATA

Before testing sensitivity, we discovered that the claimed "40 folios" **does not appear in the actual clustering data**.

### Actual Family Sizes (from phase20c_recipe_clusters.json)

```
Family 6:  53 members
Family 3:  11 members
Family 1:   7 members
Family 5:   5 members
Family 4:   3 members
Family 2:   2 members
Family 7:   1 member
Family 8:   1 member
--------------------------
Total:     83 folios
```

**There is no family with 40 members.**

---

## SENSITIVITY ANALYSIS: NOT APPLICABLE

The question "does the 40-correspondence survive perturbation?" cannot be answered because there is no 40 in the data to perturb.

### What We Can Test: Could Perturbation CREATE a 40?

**Test:** What random perturbations would produce a family of exactly 40?

**Method:** Monte Carlo simulation of family boundary changes.

### Simplified Analysis

Given 83 folios and 8 families, a family of 40 would contain 48.2% of all folios.

Current largest family (53) = 63.9% of folios
A family of 40 would require = 48.2% of folios

**Gap:** 13 folios would need to migrate from Family 6 to other families.

**Probability:** Given that the source clustering produced 53/11/7/5/3/2/1/1, the probability of a different parameter set producing exactly 40 is **very low** without targeted adjustment.

---

## ALTERNATIVE INTERPRETATION

Perhaps "40" refers to something other than family size:

| Possible "40" Sources | Actual Value | Match? |
|-----------------------|--------------|--------|
| Total B-text folios | 83 | NO |
| Largest family size | 53 | NO |
| Number of tokens in specific folio | varies | UNKNOWN |
| Number of instruction classes | 49 | NO |
| Number of unique middles | varies | UNKNOWN |

**No obvious source for "40" found in the data.**

---

## SENSITIVITY VERDICT

| Test | Result |
|------|--------|
| Does "40" exist in source data? | **NO** |
| Could perturbation produce 40? | **LOW PROBABILITY** |
| Is the correspondence stable? | **N/A - no correspondence exists** |

---

## CONCLUSION

The "40 folio = 40 day" correspondence **fails the sensitivity test** at the most basic level: the number 40 does not appear in the source clustering data.

**The correspondence is not merely unstable - it is non-existent in the verified data.**
