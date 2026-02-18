# C1097: Rosettes Bridge-Concentrated Affordance Profile

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** ROSETTES
**Phase:** ROSETTES_STRUCTURAL_VALIDATION (Phase 389)
**Strengthens:** C1095 (metalayer status), C1096 (bridge enrichment)
**Extends:** C995 (affordance bins), C996 (forbidden topology)

---

## Statement

Rosettes MIDDLEs concentrate in the 4 bridge-enriched affordance bins (0, 6, 8, 9) which account for 69.2% of all mapped MIDDLEs, while the 4 specialized bins (1, 3, 5, 7) are depleted. All 4 bridge bins show >1.0x enrichment vs B corpus; 3 of 4 specialized bins are depleted. The ENERGY_SPECIALIZED bin (7) is almost absent at 0.13x. This is the functional signature of a cross-system index: it concentrates connective vocabulary and excludes specialized operations.

---

## Evidence

### Bin Distribution (type-level, 172 mapped of 308 unique MIDDLEs)

| Bin | Label | Ros | Ros% | B | B% | Enrichment | Bridge? |
|-----|-------|-----|------|---|----|-----------:|---------|
| 0 | FLOW_TERMINAL | 45 | 26.2% | 62 | 16.4% | 1.60x | Yes |
| 6 | HUB_UNIVERSAL | 23 | 13.4% | 23 | 6.1% | 2.20x | Yes |
| 8 | STABILITY_CRITICAL | 31 | 18.0% | 44 | 11.6% | 1.55x | Yes |
| 9 | PHASE_SENSITIVE | 20 | 11.6% | 25 | 6.6% | 1.76x | Yes |
| 1 | ROUTINE_SPECIALIZED | 15 | 8.7% | 46 | 12.2% | 0.72x | No |
| 3 | COMPOUND_TERMINAL | 14 | 8.1% | 43 | 11.4% | 0.72x | No |
| 5 | SETTLING_SPECIALIZED | 10 | 5.8% | 49 | 13.0% | 0.45x | No |
| 7 | ENERGY_SPECIALIZED | 3 | 1.7% | 52 | 13.8% | 0.13x | No |
| 2 | PRECISION_SPECIALIZED | 6 | 3.5% | 28 | 7.4% | 0.47x | No |
| 4 | BULK_OPERATIONAL | 5 | 2.9% | 6 | 1.6% | 1.83x | - |

### Per Region Type

| Region Type | Bridge Bin Fraction | Evenness |
|-------------|--------------------:|----------|
| LABEL | 79.4% | 0.722 |
| DESCRIPTION | 86.5% | 0.668 |
| Overall | 69.2% | 0.891 |

### Key Observations

1. **HUB_UNIVERSAL (Bin 6)**: 23/23 MIDDLEs present in Rosettes (100% coverage). These are the universal connectors — the 23 most topologically central MIDDLEs in the grammar.

2. **ENERGY_SPECIALIZED (Bin 7)**: Only 3/52 MIDDLEs present (0.13x). Rosettes almost completely excludes energy-specialized operations.

3. **FLOW_TERMINAL (Bin 0)**: Largest Rosettes bin at 26.2% (vs 16.4% B). Flow operations are over-represented.

4. **Bridge bin concentration increases with specificity**: LABEL regions (79.4%) < DESCRIPTION regions (86.5%). The more detailed B-like text is even more bridge-concentrated.

---

## Implication

The affordance profile confirms the index interpretation: Rosettes uses vocabulary concentrated in bins that serve cross-system connective functions (HUB, FLOW, STABILITY, PHASE) and excludes specialized bins that serve narrow operational roles (ENERGY, SETTLING, PRECISION). This is not a program performing operations — it is a vocabulary reference organized by functional category.

---

## Provenance

- Phase: 389 (ROSETTES_STRUCTURAL_VALIDATION), Test V3
- Script: `phases/ROSETTES_STRUCTURAL_VALIDATION/scripts/rosettes_structural_validation.py`
- Results: `phases/ROSETTES_STRUCTURAL_VALIDATION/results/rosettes_structural_validation.json`
- Related: C995, C996, C1013, C1095, C1096, C1098
