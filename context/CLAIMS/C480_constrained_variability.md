# C480: Constrained Execution Variability

**Tier:** 3 | **Status:** PROVISIONAL | **Scope:** A→B | **Source:** Phase SSD (2026-01-12)

---

## Statement

Currier A survivor-set rate shows marginal correlation with B execution variability (rho = 0.306, p = 0.078, n=34), suggesting that multiplicity may influence micro-state freedom within fixed grammar.

---

## PROVISIONAL STATUS

This constraint is Tier 3 (provisional) because:

1. **Effect is marginal** (p = 0.078, not < 0.05)
2. **Touches load-bearing constraint** (C254)
3. **Confirmatory controls produced mixed results**

Retain as refinement note, not binding constraint.

---

## Structural Interpretation (if confirmed)

Multiplicity affects **where within an equivalence class execution wanders**, not which class exists.

- This is **micro-state freedom**, not grammar freedom
- B grammar remains invariant; survivor-set size affects **variance**, not **structure**

---

## Evidence

```
Phase SSD Test 2 Results:
- Survivor rate vs B transition entropy: rho = 0.357, p = 0.038
- n = 34 matched B folios

Confirmatory Control Results:
- Within-regime: n=5, insufficient power
- Tail-pressure: rho = 0.306, p = 0.078 (marginal PASS)
- Section stratification: insufficient data
```

---

## Relationship to C254

C254 states: "Multiplicity does NOT interact with B; isolated from operational grammar"

C480 proposes a **refinement**, not contradiction:

| Aspect | C254 Status | C480 Finding |
|--------|-------------|--------------|
| Grammar structure | Unchanged ✅ | Unchanged ✅ |
| Hazard topology | Unchanged ✅ | Unchanged ✅ |
| State-space size | Unchanged ✅ | Unchanged ✅ |
| Micro-variability | Not addressed | Possibly affected |

**This constraint does NOT alter C121, C254, or hazard topology.**

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C254 | **Refines** (not contradicts) |
| C458 | **Compatible**: B complexity remains clamped |
| F-AZC-016 | **Extends**: Causal transfer may include variability dimension |

---

## Promotion Criteria

To promote C480 to Tier 2, require:

1. Replication with p < 0.05
2. Within-regime confirmation with adequate power (n > 15)
3. Section-stratified confirmation

Until then, treat as **suggestive observation** only.

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
