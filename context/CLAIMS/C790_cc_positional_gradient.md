# C790: CC Positional Gradient

**Tier:** 2 (Validated)
**Phase:** CC_MECHANICS_DEEP_DIVE
**Scope:** B-GRAMMAR

---

## Constraint

CC classes show positional differentiation within lines. Group A (classes 10, 11) appears earlier in lines (mean position 0.469) than Group B (class 17, mean 0.515). Statistical significance: p=0.045.

---

## Quantitative

| Class | Mean Position | Median | Line-Initial % |
|-------|---------------|--------|----------------|
| 10 (daiin) | 0.413 | 0.400 | 27.1% |
| 11 (ol) | 0.511 | 0.500 | 5.0% |
| 17 | 0.515 | 0.545 | 6.2% |

Group comparison:
- Group A (10,11): mean 0.469
- Group B (17): mean 0.515
- Mann-Whitney U: p = 0.0451

Class 10 ("daiin") is distinctively early:
- 45.5% in first third of line
- 27.1% line-initial

---

## Interpretation

The CC position gradient aligns with the source/target pattern (C782):

- Group A (hazard sources, 0% kernel) appears earlier
- Group B (hazard targets, 88% kernel) appears later

This suggests a temporal/sequential relationship: sources precede targets in the line structure.

---

## Dependencies

- C782 (CC kernel paradox)
- C783 (forbidden pair asymmetry)

---

## Provenance

```
phases/CC_MECHANICS_DEEP_DIVE/scripts/t4_cc_positional_profile.py
phases/CC_MECHANICS_DEEP_DIVE/results/t4_cc_positional_profile.json
```
