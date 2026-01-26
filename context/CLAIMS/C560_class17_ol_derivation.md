# C560: Class 17 ol-Derived Control Operators

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Class 17 (CORE_CONTROL) contains 9 tokens, all morphologically derived from singleton ol (Class 11) via ol-PREFIX + ENERGY-like elaboration. Tokens: olaiin, olchedy, olchey, olkaiin, olkain, olkedy, olkeedy, olkeey, olshedy. Class 17 is BIO-enriched (1.72x), PHARMA-absent (0 occurrences), and REGIME_3 enriched (1.90x). The non-singleton CC class is structurally derived from singleton ol.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/class17_analysis.py`

### Class 17 Membership

| Token | Prefix | Middle | Suffix |
|-------|--------|--------|--------|
| olaiin | ol | aiin | - |
| olchedy | ol | ch | edy |
| olchey | ol | ch | ey |
| olkaiin | ol | k | aiin |
| olkain | ol | k | ain |
| olkedy | ol | k | edy |
| olkeedy | ol | ke | edy |
| olkeey | ol | k | eey |
| olshedy | ol | sh | edy |

**Pattern:** ALL tokens have PREFIX=ol. MIDDLEs (k, ch, ke, aiin, sh) and SUFFIXes (edy, ey, aiin, ain, eey) match ENERGY-class morphology.

### CORE_CONTROL Class Comparison

| Class | Tokens | Total | Structure |
|-------|--------|-------|-----------|
| 10 | daiin | 314 | PREFIX:da + MIDDLE:iin |
| 11 | ol | 421 | MIDDLE:ol (pure) |
| 17 | 9 forms | 288 | PREFIX:ol + ENERGY-morph |

### Positional Patterns

| Class | Initial% | Final% | Bias |
|-------|----------|--------|------|
| 10 (daiin) | 27.7% | 7.6% | INITIAL |
| 11 (ol) | 5.2% | 9.5% | FINAL |
| 17 | 6.6% | 9.7% | NEUTRAL |

Class 17 is positionally neutral, between the singleton biases.

### Section Distribution

| Section | Class 17 | Enrichment |
|---------|----------|------------|
| BIO | 147 (2.1%) | **1.72x** |
| RECIPE | 126 (1.0%) | 0.78x |
| HERBAL | 15 (0.6%) | 0.45x |
| PHARMA | **0** (0.0%) | **0.00x** |

PHARMA complete avoidance is notable. BIO enrichment parallels ENERGY.

### REGIME Distribution

| REGIME | Class 17 | Enrichment |
|--------|----------|------------|
| REGIME_3 | 41 (2.4%) | **1.90x** |
| REGIME_1 | 106 (1.4%) | 1.10x |
| REGIME_2 | 68 (1.1%) | 0.87x |
| REGIME_4 | 73 (1.0%) | 0.80x |

### ENERGY Trigger Comparison

| CC Class | ENERGY Followers |
|----------|------------------|
| 10 (daiin) | 30.0% |
| 11 (ol) | 31.8% |
| 17 | 29.1% |

All CC classes trigger ENERGY at similar rates (~30%).

---

## Interpretation

### Morphological Derivation

Class 17 is **ol-prefixed elaboration**:
- Base: ol (Class 11 singleton)
- Elaboration: ENERGY-like MIDDLEs and SUFFIXes
- Result: compound control operators

This suggests:
- ol = atomic control unit
- ol+X = modified control with specific operational context

### BIO-PHARMA Asymmetry

- **BIO:** 1.72x enriched (thermal processing context)
- **PHARMA:** Complete absence (0/529 tokens)

Class 17 operators are used in BIO thermal contexts but completely avoided in PHARMA. This mirrors but intensifies the ENERGY operator substitution pattern (C555).

### Structural Hierarchy

CORE_CONTROL has hierarchical structure:
1. **Singletons:** daiin (initial), ol (final) - atomic control signals
2. **Derived:** Class 17 (ol+elaboration) - compound control operators

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C558 | Extended - non-singleton CC is derived from singleton ol |
| C557 | Complementary - daiin triggers ENERGY, Class 17 elaborates control |
| C555 | Parallel - PHARMA avoidance pattern stronger in Class 17 (0%) than Class 33 (0.20x) |
| C553 | Contextualized - BIO enrichment shared with ENERGY patterns |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** class17_analysis.py

---

## Navigation

<- [C559_frequent_role_structure.md](C559_frequent_role_structure.md) | [INDEX.md](INDEX.md) ->
