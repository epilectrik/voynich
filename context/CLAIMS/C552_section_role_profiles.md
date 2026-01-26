# C552: Section-Specific Role Profiles

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Manuscript sections have statistically distinct role distributions (Chi2=565.8, p<0.001). BIO section shows +CC +EN -FL (thermal-intensive processing); HERBAL_B shows +FQ -EN (repetitive non-thermal); PHARMA shows +FL (flow-dominated); RECIPE_B shows -CC (reduced control overhead). Sections encode different procedural types.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/section_specialists.py`

### Section Definitions

| Section | Folios | Description | Tokens |
|---------|--------|-------------|--------|
| BIO | f74-f84 | Biological/Balneological | 5,324 |
| HERBAL_B | f26-f56 | Herbal section B | 1,818 |
| PHARMA | f57-f67 | Pharmaceutical | 317 |
| RECIPE_A | f87-f102 | Recipe section A | 128 |
| RECIPE_B | f103+ | Recipe section B | 8,467 |

### Role Distribution by Section

| Section | CC% | EN% | FL% | FQ% | AX% |
|---------|-----|-----|-----|-----|-----|
| BIO | **8.7** | **45.2** | 5.0 | 6.2 | 35.0 |
| HERBAL_B | 5.6 | **25.7** | 8.9 | **13.5** | 46.4 |
| PHARMA | 6.0 | 30.3 | **10.7** | 12.3 | 40.7 |
| RECIPE_B | 5.1 | 32.2 | 7.2 | 7.9 | 47.5 |
| BASELINE | 6.4 | 35.7 | 6.7 | 8.1 | 43.1 |

### Section Enrichment (vs Baseline)

| Section | CC | EN | FL | FQ | Signature |
|---------|----|----|----|----|-----------|
| BIO | **1.36x** | **1.27x** | 0.74x | 0.76x | +CC +EN -FL -FQ |
| HERBAL_B | 0.87x | **0.72x** | 1.32x | **1.66x** | +FQ -EN |
| PHARMA | 0.94x | 0.85x | **1.60x** | 1.52x | +FL +FQ |
| RECIPE_B | **0.79x** | 0.90x | 1.07x | 0.98x | -CC |

### Statistical Test

| Test | Value |
|------|-------|
| Chi-square | 565.79 |
| df | 16 |
| p-value | < 0.000001 |
| Cramer's V | 0.094 |

### Class-Level Specialists

**Section-enriched classes (>1.5x):**

| Class | Role | Section | Enrichment |
|-------|------|---------|------------|
| 23 | FREQUENT | PHARMA | **3.22x** |
| 32 | ENERGY | BIO | **1.71x** |
| 11 | CORE_CONTROL | BIO | **1.67x** |
| 9 | FREQUENT | HERBAL_B | **1.81x** |
| 30 | FLOW | PHARMA | **1.84x** |

**Section-depleted classes (<0.5x):**

| Class | Role | Section | Depletion |
|-------|------|---------|-----------|
| 33 | ENERGY | PHARMA | **0.20x** |
| 7 | FLOW | BIO | **0.31x** |
| 33 | ENERGY | RECIPE_A | **0.36x** |

---

## Interpretation

### Procedural Type Encoding

Sections appear to encode **different types of procedures**:

1. **BIO (Thermal-Intensive):**
   - ENERGY 45.2% (1.27x enriched)
   - CORE_CONTROL 8.7% (1.36x enriched)
   - Interpretation: High-temperature processing with active monitoring

2. **HERBAL_B (Repetitive Non-Thermal):**
   - FREQUENT 13.5% (1.66x enriched)
   - ENERGY 25.7% (0.72x depleted)
   - Interpretation: Repetitive operations without thermal component

3. **PHARMA (Flow-Dominated):**
   - FLOW 10.7% (1.60x enriched)
   - Class 33 (ENERGY) depleted 0.20x
   - Interpretation: Transfer/preparation procedures

4. **RECIPE_B (Autonomous Execution):**
   - CORE_CONTROL 0.79x depleted
   - No strong enrichments
   - Interpretation: Streamlined procedures with less intervention

### ENERGY Distribution Pattern

The 1.76x ENERGY ratio between BIO (45.2%) and HERBAL_B (25.7%) suggests BIO sections describe thermally-intensive processes (possibly related to the balneological imagery).

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C551 | Extended - universality operates within section-specific profiles |
| C547 | Related - REGIME_1 ENERGY enrichment may correlate with BIO sections |
| C545 | Contextualized - REGIME profiles now intersect with section profiles |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** section_specialists.py

---

## Navigation

<- [C551_grammar_universality.md](C551_grammar_universality.md) | [INDEX.md](INDEX.md) ->
