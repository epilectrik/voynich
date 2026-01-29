# C788: CC Singleton Identity

**Tier:** 2 (Validated)
**Phase:** CC_MECHANICS_DEEP_DIVE
**Scope:** B-GRAMMAR

---

## Constraint

CC role classes are singleton or near-singleton token sets. Class 10 = "daiin" only, Class 11 = "ol" only, Class 17 = 9 "ol-" prefixed tokens. Class 12 = "k" but with zero B occurrences.

---

## Quantitative

| Class | Types | Tokens | Primary Token |
|-------|-------|--------|---------------|
| 10 | 1 | 314 | daiin |
| 11 | 1 | 421 | ol |
| 12 | 1 | 0 | k (absent from B) |
| 17 | 9 | 288 | olkeedy, olkeey, olchedy... |

Class 12 exists in the grammar but never appears in B text - it is a structural placeholder or theoretical position.

---

## Interpretation

CC "classes" are not broad behavioral categories but specific high-frequency tokens that were clustered together. The kernel bifurcation (C782) is explained by the specific morphology of these tokens:

- "daiin" and "ol" happen to have no kernel chars in their MIDDLEs
- The "ol-" compound tokens in class 17 have kernel-containing MIDDLEs

This reframes CC from "control role" to "specific control tokens."

---

## Dependencies

- C121 (49 classes)
- C782 (CC kernel paradox)

---

## Provenance

```
phases/CC_MECHANICS_DEEP_DIVE/scripts/t1_cc_token_inventory.py
phases/CC_MECHANICS_DEEP_DIVE/results/t1_cc_token_inventory.json
```
