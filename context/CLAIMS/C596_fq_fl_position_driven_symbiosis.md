# C596: FQ-FL Position-Driven Symbiosis

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FQ-FL class-level adjacency is structured (chi2=20.5, p=0.015, 310 pairs) but hazard alignment is NOT significant (p=0.33). FL Class 7 connects preferentially to FQ Class 9; FL Class 30 connects to FQ Classes 13/14. The FQ-FL symbiosis (C550) is position-driven, not hazard-mediated.

---

## Evidence

**Test:** `phases/FQ_ANATOMY/scripts/fq_transition_context.py`

### FQ→FL Matrix (167 pairs)

| FQ \ FL | 7 | 30 | 38 | 40 |
|---------|---|----|----|-----|
| 9 | 24 | 7 | 6 | 3 |
| 13 | 24 | 20 | 2 | 0 |
| 14 | 25 | 29 | 1 | 4 |
| 23 | 14 | 6 | 1 | 1 |

### FL→FQ Matrix (143 pairs)

| FL \ FQ | 9 | 13 | 14 | 23 |
|---------|---|----|----|-----|
| 7 | **33** | 14 | 9 | 15 |
| 30 | 16 | **21** | **21** | 11 |
| 38 | 1 | 0 | 2 | 0 |
| 40 | 0 | 0 | 0 | 0 |

### Key Patterns

| Pattern | Observation |
|---------|-------------|
| FL 7 → FQ 9 | 33 (46.5% of FL 7 transitions to FQ) — medial-to-medial |
| FL 30 → FQ 13/14 | 42 (60.9% of FL 30 transitions to FQ) — final-to-medial |
| FL 38/40 → FQ | Only 3 pairs — too sparse for analysis |

### Hazard Alignment Test

| Pair Type | Count |
|-----------|-------|
| Hazard → Hazard | 126 |
| Hazard → Safe | 12 |
| Safe → Hazard | 163 |
| Safe → Safe | 9 |

Fisher's exact p = **0.33** — hazard alignment is NOT significant.

### Statistical Summary

| Test | Value |
|------|-------|
| Chi-square (FQ→FL) | 20.5 |
| p-value | 0.015 |
| Hazard alignment p | 0.33 (NS) |

---

## Interpretation

The FQ-FL bidirectional affinity (C550: 1.34-1.38x) operates through positional matching, not hazard compatibility:
- **FL Class 7** (medial-biased) connects to **FQ Class 9** (medial connector)
- **FL Class 30** (final-biased) connects to **FQ Classes 13/14** (medial-to-final workhorses)
- Hazard status is irrelevant to pairing (p=0.33)

This means the "symbiosis" between FQ and FL is a natural consequence of positional grammar — adjacent tokens in similar line positions pair up regardless of hazard properties.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C550 | Decomposed - role-level FQ-FL affinity now explained at class level |
| C586 | Contextualized - FL hazard-safe split does NOT drive FQ pairing |
| C593 | Extended - CONNECTOR pairs with FL 7, PREFIXED_PAIR pairs with FL 30 |
| C543 | Consistent - positional grammar governs cross-role adjacency |

---

## Provenance

- **Phase:** FQ_ANATOMY
- **Date:** 2026-01-26
- **Script:** fq_transition_context.py

---

## Navigation

<- [C595_fq_internal_transition_grammar.md](C595_fq_internal_transition_grammar.md) | [INDEX.md](INDEX.md) ->
