# C597: FQ Class 23 Boundary Dominance

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FQ Class 23 dominates FQ boundary behavior: 29.8% final rate (vs 3.7% for Class 9), providing 39% of all FQ final-position tokens despite being only 12.5% of FQ by count. Class 23 also has the highest initial rate (12.2%). Mean FQ run length is 1.19 (84% singletons). FQ operates as mostly isolated tokens, not extended runs.

---

## Evidence

**Test:** `phases/FQ_ANATOMY/scripts/fq_transition_context.py`

### Per-Class Boundary Rates

| Class | Tokens | Initial Rate | Final Rate | Final Share |
|-------|--------|-------------|------------|-------------|
| 9 | 630 | 3.2% | 3.7% | 8.3% |
| 13 | 1,191 | 3.9% | 5.6% | 24.2% |
| 14 | 707 | 1.3% | 11.2% | 28.5% |
| **23** | **362** | **12.2%** | **29.8%** | **39.0%** |

### Class 23 Dominance

- Final rate: **29.8%** — 8.1x Class 9's rate, 5.3x Class 13's rate
- Initial rate: **12.2%** — 3.8x Class 9's rate
- Final share: **39.0%** — disproportionate to 12.5% token share
- Class 23 is 12.5% of FQ but provides 39% of FQ line-final tokens

### Run Length Distribution

| Run Length | Count | % |
|-----------|-------|---|
| 1 | 2,040 | 84.3% |
| 2 | 305 | 12.6% |
| 3 | 61 | 2.5% |
| 4 | 13 | 0.5% |
| 5 | 1 | 0.04% |

- Total runs: 2,420
- Mean run length: **1.19**

---

## Interpretation

Class 23 functions as FQ's **boundary specialist**:
- It closes FQ sequences (29.8% final, 39% of finals)
- It also opens FQ sequences (12.2% initial — highest among FQ classes)
- Combined with C595 (23→9 enriched 2.85x), this creates a cycle: Class 23 closes, then re-initiates through Class 9

FQ is fundamentally a **singleton-dominant** role (84% run-length-1). When FQ does chain, it follows the 3-group grammar (C593, C595): CONNECTOR → PREFIXED_PAIR → CLOSER → restart.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C593 | Extended - Class 23 is the CLOSER in the 3-group structure |
| C595 | Extended - 23→9 restart pattern consistent with boundary role |
| C556 | Corrected - old FQ final enrichment (1.67x) was inflated by AX_FINAL classes; actual FQ is position-neutral (0.92x), with Class 23 providing localized final behavior |
| C587 | Quantified - Class 23 "minimal final-biased" now precisely measured |

---

## Provenance

- **Phase:** FQ_ANATOMY
- **Date:** 2026-01-26
- **Script:** fq_transition_context.py

---

## Navigation

<- [C596_fq_fl_position_driven_symbiosis.md](C596_fq_fl_position_driven_symbiosis.md) | [INDEX.md](INDEX.md) ->
