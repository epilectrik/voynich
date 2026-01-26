# C540: Kernel Primitives Are Bound Morphemes

**Tier:** 2 | **Status:** CLOSED | **Scope:** MORPHOLOGY

---

## Statement

> The three kernel primitives (k, e, h) never appear as standalone tokens. They are bound morphemes that must attach to other morphological components.

---

## Evidence

**Test:** `phases/INSTRUCTION_CLASS_CHARACTERIZATION/scripts/temp_verify.py`

| Primitive | Currier A | Currier B | Total Standalone |
|-----------|-----------|-----------|------------------|
| k | 0 | 0 | 0 |
| e | 0 | 0 | 0 |
| h | 0 | 0 | 0 |

**Contrast with embedded occurrences:**
- k appears in 1,557 Currier B words
- All three primitives are productive as MIDDLE components

---

## Interpretation

Kernel primitives are **intervention markers/modifiers**, not independent instructions. They modify the behavior of their host tokens rather than executing as standalone operations.

This is consistent with:
- C089 (Core within core: k, h, e)
- C103 (k = ENERGY_MODULATOR)
- The kernel's role as intervention mechanism rather than primary operator

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C089 | Extended - kernel primitives are bound |
| C103 | Consistent - k modulates, doesn't standalone |
| C107 | Consistent - kernel nodes are boundary-adjacent |

---

## Provenance

- **Phase:** INSTRUCTION_CLASS_CHARACTERIZATION
- **Date:** 2026-01-25
- **Script:** temp_verify.py

---

## Navigation

<- [INDEX.md](INDEX.md) | [C541_hazard_class_enumeration.md](C541_hazard_class_enumeration.md) ->
