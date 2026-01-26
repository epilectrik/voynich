# C545: REGIME Instruction Class Profiles

**Tier:** 2 | **Status:** CLOSED | **Scope:** REGIME_INTERPRETATION

---

## Statement

> Each REGIME has a distinctive instruction class profile: REGIME_3 shows 1.83x CORE_CONTROL enrichment; REGIME_1 concentrates qo-family (Class 32 at 52%); REGIME_2 enriches FLOW and FREQUENT operators.

---

## Role Enrichment by REGIME

| REGIME | Enriched Role | Enrichment | Depleted Role | Depletion |
|--------|---------------|------------|---------------|-----------|
| REGIME_1 | ENERGY_OPERATOR | 1.19x | FREQUENT_OPERATOR | 0.68x |
| REGIME_2 | FREQUENT_OPERATOR | 1.21x | ENERGY_OPERATOR | 0.86x |
| REGIME_3 | **CORE_CONTROL** | **1.83x** | ENERGY_OPERATOR | 0.89x |
| REGIME_4 | FREQUENT_OPERATOR | 1.17x | (balanced) | - |

---

## REGIME Signature Classes

**REGIME_1 (Control-infrastructure-heavy, 70% Section B):**
- Class 32: 2.01x vs others (qokal, qokar)
- Class 25: 1.82x vs others (olor, oldy)
- Class 8: 1.53x vs others (chedy, shedy)

**REGIME_2 (Output-intensive):**
- Class 45: 2.34x vs others (qoteol, qoar)
- Class 38: 2.21x vs others (aral, aldy)
- Class 4: 2.11x vs others (ykeody)

**REGIME_3 (Control without output):**
- Class 11: 2.06x vs others (ol)
- Class 17: 1.98x vs others (olaiin)
- Class 10: 1.84x vs others (daiin)

**REGIME_4 (Precision mode):**
- Class 19: 1.89x vs others (otchy)
- Class 26: 1.54x vs others (ykeedy)
- Class 13: 1.40x vs others (okaiin)

---

## REGIME_1 = qo-Family Concentrated

Class 32 (qokal/qokar/qol) shows 52% concentration in REGIME_1, the only class with >50% single-REGIME concentration.

This aligns with:
- REGIME_1 = 70% Section B (balneological/thermal processing)
- qo-family = escape routes (C397)
- Section B = complex thermal processing requiring escape mechanisms

---

## Evidence

**Test:** `phases/INSTRUCTION_CLASS_CHARACTERIZATION/scripts/class_regime_correlation.py`

- Analyzed 16,054 classified tokens across 82 REGIME-assigned folios
- Calculated enrichment vs baseline rates
- Identified signature classes (highest distinctiveness vs other REGIMEs)

---

## Interpretation

The class profiles confirm REGIME semantic interpretations:

| REGIME | Class Profile | Semantic |
|--------|---------------|----------|
| REGIME_1 | ENERGY-heavy, qo-concentrated | Thermal processing (Section B) |
| REGIME_2 | FREQUENT/FLOW-heavy | Output collection |
| REGIME_3 | CORE_CONTROL-heavy | Heavy intervention/monitoring |
| REGIME_4 | FREQUENT-moderate, balanced | Precision execution |

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C179 | Extended - class-level REGIME profiles |
| C180 | Consistent - REGIME_3 = aggressive/intervention-heavy |
| C412 | Consistent - qo-family in REGIME_1 |
| C494 | Extended - REGIME_4 precision via class balance |

---

## Provenance

- **Phase:** INSTRUCTION_CLASS_CHARACTERIZATION
- **Date:** 2026-01-25
- **Script:** class_regime_correlation.py

---

## Navigation

<- [C544_energy_interleaving.md](C544_energy_interleaving.md) | [C546_class40_safe_flow.md](C546_class40_safe_flow.md) ->
