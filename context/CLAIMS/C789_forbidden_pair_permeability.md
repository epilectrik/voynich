# C789: Forbidden Pair Permeability

**Tier:** 2 (Validated)
**Phase:** CC_MECHANICS_DEEP_DIVE
**Scope:** B-GRAMMAR

---

## Constraint

Forbidden class pairs are NOT absolute barriers. Approximately 34% of CC->FQ transitions violate the 8 forbidden CC->FQ pairs. Forbidden pairs represent statistical disfavor, not prohibition.

---

## Quantitative

**CC->FQ violations:**
- Total CC->FQ transitions: 128
- Forbidden transitions: 44 (34.4%)
- Permitted transitions: 84 (65.6%)

**CC->CC violations:**
- 10->17: 5 occurrences [FORBIDDEN]
- 11->17: 7 occurrences [FORBIDDEN]
- Total CC->CC forbidden: 12 transitions

**EN->CC violations:**
- EN 31 -> CC 17: 4 occurrences [FORBIDDEN]
- EN 32 -> CC 17: 11 occurrences [FORBIDDEN]
- Total EN->CC forbidden: 15 transitions

---

## Interpretation

The 17 "forbidden" pairs identified in C467 are strongly disfavored but not absolutely prohibited. The system shows ~65% compliance, meaning:

1. Forbidden pairs create statistical bias, not hard blocks
2. The hazard topology (C783) is a gradient, not a wall
3. ~35% of "hazard" transitions occur despite the restriction

This suggests forbidden pairs represent "cost" or "difficulty" rather than "impossibility."

---

## Revision to C467

C467 (MIDDLE incompatibility/forbidden pairs) should be interpreted as statistical tendency, not absolute rule. The pairs are "disfavored" not "forbidden."

---

## Dependencies

- C467 (forbidden pairs)
- C783 (forbidden pair asymmetry)
- C782 (CC kernel paradox)

---

## Provenance

```
phases/CC_MECHANICS_DEEP_DIVE/scripts/t2_cc_predecessor_analysis.py
phases/CC_MECHANICS_DEEP_DIVE/scripts/t3_cc_successor_analysis.py
phases/CC_MECHANICS_DEEP_DIVE/results/t2_cc_predecessor_analysis.json
phases/CC_MECHANICS_DEEP_DIVE/results/t3_cc_successor_analysis.json
```
