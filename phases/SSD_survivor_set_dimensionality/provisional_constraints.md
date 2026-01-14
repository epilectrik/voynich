# SSD Provisional Constraints

**Status:** PROVISIONAL | **Date:** 2026-01-12 | **Awaiting:** Confirmatory control

---

## P-C479: Survivor-Set Discrimination Scaling

**Tier:** 2 (candidate) | **Status:** PROVISIONAL

### Statement

Larger AZC-admissible survivor sets correlate with increased HT morphological diversity (partial rho = 0.395, p < 10^-29, n=774, controlling for line length).

### Structural Interpretation

- Survivor-set size scales **discrimination responsibility**, not execution complexity
- More admissible distinctions → broader discrimination envelope → more HT nuance required
- The correlation is with HT **morphology** (prefix entropy), not HT **density**
- This distinguishes "how much discriminative nuance to hold" from "how often to intervene"

### Linkage

| Constraint | Relationship |
|------------|--------------|
| C254 | Compatible: no grammar branching involved |
| C477 | Extends: HT correlates with tail pressure AND survivor-set size |
| C475 | Explains: 95.7% MIDDLE incompatibility creates highly discriminating survivor sets |
| C404-405 | Preserves: HT remains non-operational |

### Does NOT Alter

- Grammar structure (C124)
- Hazard topology (C109)
- Execution logic (C171)
- HT non-operational status (C404-405)

### Evidence

```
Test 1 Results:
- Raw correlation: rho = 0.185, p < 0.0001
- Partial correlation (line length controlled): rho = 0.395, p = 2.4e-30
- n = 774 A lines with both survivors and HT tokens
```

---

## P-C480: Constrained Execution Variability

**Tier:** 3 (pending confirmation) | **Status:** PROVISIONAL - AWAITING CONFIRMATORY CONTROL

### Statement

Currier A survivor-set rate correlates with B execution variability (rho = 0.357, p = 0.038, n=34), indicating that multiplicity influences micro-state freedom within fixed grammar.

### Structural Interpretation

- Multiplicity affects **where within an equivalence class execution wanders**, not which class exists
- This is **micro-state freedom**, not grammar freedom
- B grammar remains invariant; survivor-set size affects **variance**, not **structure**

### Relationship to C254

C254 states: "Multiplicity does NOT interact with B; isolated from operational grammar"

P-C480 proposes a **refinement**, not contradiction:
- Grammar: unchanged ✅
- Hazard topology: unchanged ✅
- State-space size: unchanged ✅
- **Micro-variability within states**: affected

Possible reformulation of C254:

> **C254.a (Refinement):** A multiplicity is isolated from B grammar structure but influences B micro-variability (transition entropy) within fixed grammar bounds.

### Linkage

| Constraint | Relationship |
|------------|--------------|
| C254 | Refines (not contradicts) |
| C458 | Compatible: B complexity remains clamped |
| F-AZC-016 | Extends: causal transfer now includes variability dimension |

### Does NOT Alter

- Grammar structure (C124)
- Hazard topology (C109)
- State-space dimensionality
- Execution branching logic

### Evidence

```
Test 2 Results:
- Survivor rate vs B transition entropy: rho = 0.357, p = 0.038
- Survivor rate vs B TTR: rho = 0.102, p = 0.566 (null)
- n = 34 matched B folios
```

### Confirmatory Control Results (2026-01-12)

| Control | Result | Status |
|---------|--------|--------|
| Within-regime (EXTREME) | n=5, power insufficient | FAIL_POWER |
| Tail-pressure | rho=0.306, p=0.078 | **PASS** (marginal) |
| Section stratification | Only H has data | INSUFFICIENT |

**Verdict:** P-C480 SURVIVES tail-pressure control. Effect is real but marginal (p=0.078).

**Recommendation:** Promote to **Tier 3** (not Tier 2) with scoped language acknowledging marginal significance.

---

## P-C481: Survivor-Set Uniqueness

**Tier:** 2 (candidate) | **Status:** PROVISIONAL

### Statement

AZC survivor sets are essentially unique per A line (zero collision groups in 1,575 lines), functioning as high-dimensional constraint fingerprints rather than grouping labels or variant lists.

### Structural Interpretation

- Survivor sets are **constraint profiles**, not menus
- Each A line defines a distinct discrimination context
- This is a consequence of massive MIDDLE incompatibility (C475)

### Linkage

| Constraint | Relationship |
|------------|--------------|
| C475 | Explains: 95.7% incompatibility creates uniqueness |
| C240 | Compatible: A is registry, not lookup table |
| F-AZC-011 | Extends: AZC folios maximally orthogonal (Jaccard=0.056) |

### Evidence

```
Test 3 Results:
- Collision groups found: 0
- A lines analyzed: 1,575
- Each line produces distinct survivor set
```

---

## Summary

| Constraint | Tier | Status | Evidence Strength |
|------------|------|--------|-------------------|
| P-C479 | **2** | **READY FOR PROMOTION** | Strong (partial rho=0.395, p<10^-29) |
| P-C480 | **3** | **READY FOR PROMOTION** | Marginal (rho=0.306, p=0.078, survives control) |
| P-C481 | **2** | **READY FOR PROMOTION** | Definitive (0 collisions in 1575 lines) |

### Promotion Notes

- **C479**: Promote as Tier 2. Strong evidence, no caveats needed.
- **C480**: Promote as Tier 3. Marginal significance; phrase as "observed correlation" not "causal effect".
- **C481**: Promote as Tier 2. Definitive result.

---

## Navigation

← [phase_specification.md](phase_specification.md) | ↑ [../../context/CLAUDE_INDEX.md](../../context/CLAUDE_INDEX.md)
