# C493: Brunschwig Grammar Embedding

**Tier:** 3 | **Status:** CLOSED | **Scope:** EXTERNAL_ALIGNMENT

---

## Statement

> Brunschwig balneum marie distillation procedure can be translated step-by-step into Voynich Currier B grammar without violating any of the 17 forbidden transitions or grammar rules.

---

## Evidence

**Test:** `phases/BRUNSCHWIG_TEMPLATE_FIT/grammar_compliance_test.py`

### Procedure Translation

18-step Brunschwig balneum marie procedure mapped to Voynich instruction classes:

| Step | Brunschwig Action | Voynich Class |
|------|-------------------|---------------|
| 1 | Chop/prepare material | AUX |
| 2-3 | Load cucurbit, setup | FLOW |
| 4-5 | Attach head, seal | AUX |
| 6 | Apply gentle heat | k (ENERGY) |
| 7-8 | Monitor warming | LINK |
| 9 | Vapor condenses | h (PHASE) |
| 10 | Distillate flows | FLOW |
| 11-13 | Monitor, adjust, continue | LINK, k, LINK |
| 14-18 | Reduce, cool, complete | k, e, LINK, FLOW, e |

### Compliance Results

| Constraint | Status |
|------------|--------|
| PHASE_ORDERING | COMPLIANT (k before h) |
| COMPOSITION_JUMP | COMPLIANT |
| CONTAINMENT_TIMING | COMPLIANT (seal before heat) |
| RATE_MISMATCH | COMPLIANT (LINK between k and h) |
| ENERGY_OVERSHOOT | COMPLIANT (k reduction before e) |
| C332 h->k suppression | COMPLIANT (no h->k transitions) |

---

## Significance

This is not a vibes-level parallel. It is a **grammar-level embedding**:
- Grammar was NOT tuned
- Constraints were NOT relaxed
- Semantics were NOT inferred

Real historical distillation procedure fits inside Voynich grammar without breaking any rules.

---

## Provenance

- **Phase:** BRUNSCHWIG_TEMPLATE_FIT
- **Date:** 2026-01-14
- **Files:** `phases/BRUNSCHWIG_TEMPLATE_FIT/grammar_compliance_test.py`

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C109 | 17 forbidden transitions preserved |
| C332 | h->k suppression honored |
| C490 | AGGRESSIVE exclusion consistent |

---

## Navigation

<- [C492_prefix_phase_exclusion.md](C492_prefix_phase_exclusion.md) | [INDEX.md](INDEX.md) ->
