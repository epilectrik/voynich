# C556: ENERGY Medial Concentration

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> ENERGY operators are medial-concentrated, avoiding both line boundaries: 0.45x initial enrichment, 0.50x final enrichment. Lines have positional grammar: UNCLASSIFIED/AUXILIARY open (1.55x, 0.97x), FLOW/FREQUENT close (1.65x, 1.67x), ENERGY operates in centers. Chi-square p=3e-89 confirms significant positional bias.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/line_initial_patterns.py`

### Role Positional Enrichment

| Role | Initial | Final | Corpus | Init Enrich | Final Enrich | Position |
|------|---------|-------|--------|-------------|--------------|----------|
| CORE_CONTROL | 5.1% | 3.8% | 4.4% | 1.16x | 0.85x | Initial |
| **ENERGY** | 11.2% | 12.4% | 24.8% | **0.45x** | **0.50x** | **Medial** |
| FLOW | 3.5% | 7.7% | 4.7% | 0.74x | **1.65x** | Final |
| FREQUENT | 3.9% | 9.4% | 5.6% | 0.70x | **1.67x** | Final |
| AUXILIARY | 29.2% | 23.6% | 30.0% | 0.97x | 0.79x | Initial |
| UNCLASSIFIED | 47.1% | 43.3% | 30.5% | **1.55x** | 1.42x | Initial |

### ENERGY Class Detail

| Class | Role | Initial Enrich | Final Enrich | Pattern |
|-------|------|----------------|--------------|---------|
| 8 | ENERGY | **0.19x** | - | Strongly medial |
| 31 | ENERGY | **0.30x** | - | Strongly medial |
| 34 | ENERGY | **0.25x** | - | Strongly medial |
| 33 | ENERGY | 0.50x | - | Medial |

### Top Line-Initial Classes

| Class | Role | Initial Enrich | Token Example |
|-------|------|----------------|---------------|
| 5 | AUX | **3.24x** | - |
| 4 | AUX | **3.20x** | - |
| 10 | CC | **2.58x** | daiin |
| 24 | AUX | **2.16x** | sol, sor, sar |

### Statistical Test

| Test | Value |
|------|-------|
| Chi-square | 423.1 |
| p-value | 3.06e-89 |
| Result | **Highly significant** |

---

## Interpretation

### Line Structure Model

Lines follow a positional template:

```
[INITIAL zone]     [MEDIAL zone]      [FINAL zone]
UNCLASSIFIED       ENERGY             FLOW
AUXILIARY          ENERGY             FREQUENT
CORE_CONTROL       ENERGY
```

### ENERGY Medial Concentration

ENERGY's double boundary-avoidance (0.45x initial, 0.50x final) means thermal operations:
- **Start after** line setup (AUXILIARY, CORE_CONTROL)
- **End before** line closure (FLOW, FREQUENT)
- **Occupy** line centers where main processing occurs

### Functional Interpretation

If lines are control blocks:
1. **Opening:** Context setup, parameter initialization
2. **Body:** Thermal/energy operations (main processing)
3. **Closing:** Flow control, state finalization

### "daiin" as Canonical Opener

"daiin" (Class 10, CORE_CONTROL) opens 3.5% of lines. This token may serve as a **control block initiator** - a signal that a new processing sequence begins.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C357 | Extended - line regularity (3.3x) now characterized by role positions |
| C358 | Extended - boundary markers (daiin initial, dy final) align with role positions |
| C360 | Consistent - line-invariant grammar has positional structure |
| C543 | Extended - positional grammar now quantified with enrichment values |
| C550 | Related - ENERGY self-chaining occurs in medial zone |
| C554 | Contextualized - hazard clustering happens in ENERGY-rich medial zones |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** line_initial_patterns.py

---

## Navigation

<- [C555_pharma_thermal_substitution.md](C555_pharma_thermal_substitution.md) | [INDEX.md](INDEX.md) ->
