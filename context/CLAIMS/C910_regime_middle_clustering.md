# C910: REGIME-MIDDLE Clustering

**Tier:** 2 | **Scope:** B | **Status:** CLOSED

---

## Statement

MIDDLEs cluster by folio-level execution REGIME. **67% of MIDDLEs** show significant REGIME-dependence (p < 0.01). REGIME_4 (precision) folios show **extreme enrichment** for specific MIDDLEs (up to 7.24x), establishing that MIDDLE selection encodes execution mode requirements.

---

## Evidence

### REGIME_1 (k-dominant, energy-intensive)
*26 folios, 5,342 tokens*

| MIDDLE | Enrichment | n | Profile |
|--------|------------|---|---------|
| ek | 1.80x | 166 | Extended energy |
| lk | 1.71x | 58 | Energy |
| eck | 1.57x | 88 | Extended energy |
| dy | 1.56x | 594 | Terminal |
| eek | 1.52x | 54 | Deep energy |
| k | 1.49x | 2081 | Core energy |
| ck | 1.35x | 196 | Energy |

**Interpretation:** Energy-intensive folios concentrate k-family MIDDLEs.

### REGIME_2 (balanced)
*41 folios, 13,960 tokens*

No MIDDLEs >1.3x enriched - this is the "default" execution mode.

### REGIME_3 (e-dominant, stability-focused)
*13 folios, 3,500 tokens*

| MIDDLE | Enrichment | n | Profile |
|--------|------------|---|---------|
| eed | 2.36x | 84 | Deep stability |
| eod | 2.06x | 80 | Terminal stability |
| ed | 2.01x | 377 | Light stability |
| i | 1.88x | 137 | Initial |
| eeo | 1.88x | 130 | Extended stability |
| ai | 1.86x | 174 | State |
| eo | 1.59x | 340 | Transition |
| ee | 1.58x | 146 | Core stability |

**Interpretation:** Stability-focused folios concentrate e-extended MIDDLEs.

### REGIME_4 (precision, low variance)
*2 folios, 294 tokens*

| MIDDLE | Enrichment | n | Profile |
|--------|------------|---|---------|
| **m** | **7.24x** | 76 | Fine measurement |
| ek | 3.79x | 166 | Energy precision |
| et | 2.71x | 58 | Terminal precision |
| y | 2.57x | 458 | Terminal marker |
| d | 2.52x | 312 | Instruction |
| a | 2.49x | 63 | State marker |
| s | 2.21x | 142 | Precision |
| dy | 1.98x | 594 | Terminal |

**Interpretation:** Precision folios use specific MIDDLEs at **extreme** enrichment ratios. The `m` MIDDLE is 7.24x enriched - the strongest signal in the entire analysis.

---

## Key Finding: Precision Vocabulary

REGIME_4 represents precision operations (C494). The extreme enrichment of specific MIDDLEs (m, ek, y, d, s) in these folios suggests a **specialized precision vocabulary**:

- **m** (7.24x): Likely encodes measurement or fine control
- **ek** (3.79x): Energy + precision combination
- **y, dy** (2-2.6x): Terminal markers for precise completion
- **d** (2.52x): Instructional/monitoring marker
- **s** (2.21x): Precision operation marker

---

## Summary

| REGIME | Execution Mode | MIDDLE Profile | Enrichment Range |
|--------|---------------|----------------|------------------|
| 1 | Energy-intensive | k-family | 1.3-1.8x |
| 2 | Balanced (default) | None specific | ~1.0x |
| 3 | Stability-focused | e-extended | 1.4-2.4x |
| 4 | **Precision** | **m, ek, y, d, s** | **2-7x** |

---

## Provenance

- **Phase:** MIDDLE_SEMANTIC_MAPPING (2026-02-04)
- **Method:** Folio-level REGIME classification, chi-square enrichment testing
- **Sample:** 82 folios, 53 MIDDLEs with n≥50

---

## Related Constraints

- C494 (REGIME_4 precision axis)
- C908 (MIDDLE-Kernel Correlation)
- C909 (Section-Specific MIDDLE Vocabularies)
- C893 (Kernel signature predicts operation type)
