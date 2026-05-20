# C479: Survivor-Set Discrimination Scaling

**Tier:** 2 | **Status:** CLOSED | **Scope:** A+AZC+HT | **Source:** Phase SSD (2026-01-12)

---

## Statement

Larger AZC-admissible survivor sets correlate with increased HT morphological diversity (partial rho = 0.395, p < 10^-29, n=774, controlling for line length).

---

## Structural Interpretation

Survivor-set SIZE scales **discrimination responsibility**, not execution complexity.

- More admissible distinctions → broader discrimination envelope → more HT nuance required
- The correlation is with HT **morphology** (prefix entropy), not HT **density**
- This distinguishes "how much discriminative nuance to hold" from "how often to intervene"

---

## Evidence

```
Phase SSD Test 1 Results:
- Raw correlation: rho = 0.185, p < 0.0001
- Partial correlation (line length controlled): rho = 0.395, p = 2.4e-30
- n = 774 A lines with both survivors and HT tokens
- Effect size: STRONG
```

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C477 | **Extends**: HT correlates with tail pressure AND survivor-set size |
| ~~C475~~ | ~~Explains: 95.7% MIDDLE incompatibility~~ — **C475 DEMOTED 2026-05-19** (sparsity denominator); the 95.7% framing is sparsity-driven. C479's measurement (partial correlation rho=0.395, p=2.4e-30) is methodologically independent and stands at Tier 2. |
| ~~C481~~ | ~~implicitly related to survivor-set uniqueness~~ — **C481 RETRACTED 2026-05-19** (value doesn't reproduce, direction wrong). C479's survivor-set SIZE measurement is distinct from C481's UNIQUENESS claim and is unaffected. |
| C254 | **Compatible**: No grammar branching involved; discrimination layer only |
| C404-C405 | **Preserves**: HT remains non-operational |

## Audit notes (2026-05-19 batch-sweep)

C479 reviewed in 2026-01-12 cohort batch-sweep (`phases/BATCH_SWEEP_2026_01_12/`). **Verdict: SURVIVES.** Methodology (partial correlation between survivor-set size and HT morphological diversity, controlling for line length) is independent of the framework issues that retracted C476 and C481. The numerical result (partial rho=0.395, p=2.4e-30, n=774) stands as Tier 2 measurement. Cross-references to C475 (now demoted) and implicit C481 dependency (now retracted) updated above; the constraint's substantive claim is unaffected by those retractions.

---

## Does NOT Alter

- Grammar structure (C124)
- Hazard topology (C109)
- Execution logic (C171)
- HT non-operational status (C404-C405)
- B grammar (C254)

---

## Architectural Role

This constraint closes the last open gap in A→AZC→HT integration:

> **Survivor-set width is a discrimination envelope, and HT morphology scales with that envelope.**

The question "what does a large survivor set MEAN?" is now answered:

- NOT more execution steps
- NOT more procedures
- NOT more semantic content
- **YES**: broader discrimination responsibility absorbed by human operator

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
