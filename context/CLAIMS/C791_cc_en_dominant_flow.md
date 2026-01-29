# C791: CC-EN Dominant Flow

**Tier:** 2 (Validated)
**Phase:** CC_MECHANICS_DEEP_DIVE
**Scope:** B-GRAMMAR

---

## Constraint

CC tokens primarily route to EN (not FQ). EN is the dominant successor for all CC classes at ~33%, while FQ receives only ~12-13%. CC->EN flow dominates CC->FQ by nearly 3:1.

---

## Quantitative

**Successor distribution:**

| CC Group | -> EN | -> FQ | -> UN | -> AX |
|----------|-------|-------|-------|-------|
| Group A (10,11) | 34.4% | 12.2% | 21.8% | 13.3% |
| Group B (17) | 32.6% | 13.2% | 25.0% | 11.8% |

**Raw counts (Group A):**
- EN: 253 transitions
- FQ: 90 transitions
- Ratio: 2.8:1

**By class:**
- Class 10 -> EN: 36.6% (115)
- Class 11 -> EN: 32.8% (138)
- Class 17 -> EN: 32.6% (94)

---

## Interpretation

Despite 8 CC->FQ forbidden pairs, the dominant outflow from CC is to EN, not escape (FQ). This suggests:

1. CC primarily hands off to kernel operations (EN is 92% kernel, h+e dominant)
2. CC->FQ escape is a minority path (~12%)
3. The forbidden CC->FQ pairs further restrict an already minority flow

CC acts as a gate that primarily routes to EN for phase/stability management.

---

## Dependencies

- C778 (EN kernel profile)
- C782 (CC kernel paradox)
- C789 (forbidden pair permeability)

---

## Provenance

```
phases/CC_MECHANICS_DEEP_DIVE/scripts/t3_cc_successor_analysis.py
phases/CC_MECHANICS_DEEP_DIVE/results/t3_cc_successor_analysis.json
```
