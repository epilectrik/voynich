# C890: Recovery Rate-Pathway Independence

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Escape frequency (FQ density) and recovery pathway composition (post-FQ kernel distribution) vary independently across REGIMEs. REGIMEs with high escape rates do not systematically use different recovery kernels than REGIMEs with low escape rates.

---

## Evidence

**Test:** `phases/REVERSE_BRUNSCHWIG_TEST/scripts/09_recovery_orthogonality.py`

### FQ Rate vs Post-FQ Kernel Rankings

| Measure | REGIME Ranking (high to low) |
|---------|------------------------------|
| FQ rate (escape frequency) | R4 > R2 > R1 > R3 |
| Post-FQ e% (equilibration recovery) | R2 > R1 > R3 > R4 |

These rankings are **nearly inverse**, demonstrating independence.

### Per-REGIME Data

| REGIME | FQ Rate | Post-FQ e% | Post-FQ h% | Post-FQ k% |
|--------|---------|------------|------------|------------|
| R4 | 0.151 (highest) | 2.8% (lowest) | 25.0% | 22.1% |
| R2 | 0.132 | 8.1% (highest) | 24.2% | 19.1% |
| R1 | 0.121 | 6.6% | 31.1% | 25.3% |
| R3 | 0.112 (lowest) | 5.0% | 36.4% | 17.3% |

---

## Interpretation

This finding extends C458 (recovery is free). Not only does aggregate recovery vary freely across REGIMEs, but the two components of recovery - HOW OFTEN escapes occur and WHICH PATHWAY recovery takes - are independent parameters.

**Closed-loop insight:** In a state-responsive control system, escape frequency reflects operational challenge (how often things go wrong), while recovery pathway reflects corrective strategy (how to fix it). These can be tuned independently:

- **R4 (precision):** Escapes often (tight tolerances), low e-recovery (no time for equilibration)
- **R3 (intense):** Escapes rarely (robust process), high h-recovery (phase-checking when needed)
- **R2 (gentle):** Moderate escapes, highest e-recovery (can afford to stabilize)

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C458 | Extended - recovery freedom decomposes into rate and pathway |
| C892 | Related - h dominates post-FQ across all REGIMEs |
| C891 | Related - ENERGY/FREQUENT inverse also shows orthogonality |

---

## Provenance

- **Phase:** REVERSE_BRUNSCHWIG_TEST
- **Date:** 2026-01-30
- **Script:** 09_recovery_orthogonality.py

---

## Navigation

<- [C889_ct_ho_reserved_vocabulary.md](C889_ct_ho_reserved_vocabulary.md) | [INDEX.md](INDEX.md) ->
