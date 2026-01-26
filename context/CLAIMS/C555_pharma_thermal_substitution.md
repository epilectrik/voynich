# C555: PHARMA Thermal Operator Substitution

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> PHARMA section shows Class 33/34 operator substitution: Class 33 depleted 0.20x while Class 34 enriched 1.90x (~10x divergence). This is section-specific, not REGIME-driven (PHARMA is 84% REGIME_1, where Class 33 is normally 1.26x enriched). ENERGY operators are not interchangeable; sections select specific thermal operations.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/class33_anomaly.py`

### ENERGY Classes in PHARMA

| Class | PHARMA Rate | Corpus Rate | Enrichment |
|-------|-------------|-------------|------------|
| 8 | 4.4% | 6.3% | 0.70x |
| 31 | 5.0% | 5.4% | 0.93x |
| 32 | 4.1% | 4.7% | 0.86x |
| **33** | 2.2% | 11.0% | **0.20x** |
| **34** | 12.9% | 6.8% | **1.90x** |
| 36 | 1.6% | 1.5% | 1.04x |

### PHARMA REGIME Composition

| REGIME | Tokens | % |
|--------|--------|---|
| REGIME_1 | 442 | 84% |
| REGIME_4 | 87 | 16% |

### Class 33 by REGIME (Control)

| REGIME | Class 33 Rate | Enrichment |
|--------|---------------|------------|
| REGIME_1 | 13.8% | **1.26x** |
| REGIME_2 | 7.4% | 0.68x |
| REGIME_3 | 8.0% | 0.73x |
| REGIME_4 | 11.5% | 1.05x |

**Key finding:** PHARMA is 84% REGIME_1, where Class 33 is normally 1.26x enriched. Yet PHARMA shows 0.20x Class 33 depletion. This is a **section-specific** effect, not REGIME-explained.

### Class 33 Token Forms

Class 33 = qo-family tokens: qokaiin, qokain, qokedy, qokeedy, qokeey, etc.

| Context | Class 33 Tokens | Common Forms |
|---------|-----------------|--------------|
| PHARMA | 7 | qokedy (2), qokeedy (2) |
| Elsewhere | 1,752 | qokeedy (304), qokain (275) |

PHARMA lacks the common qo-aiin/qo-ain forms entirely.

---

## Interpretation

### Operator Substitution Pattern

PHARMA section uses Class 34 **instead of** Class 33, not in addition to:

| Operation Type | Elsewhere | PHARMA |
|----------------|-----------|--------|
| Class 33 (qo-family) | Common (11%) | Rare (2.2%) |
| Class 34 | Moderate (6.8%) | High (12.9%) |

### Functional Distinction

If thermal interpretation holds:
- **Class 33 (qo-family):** Rapid venting/escape operations
- **Class 34:** Sustained heating/application operations

PHARMA (pharmaceutical recipes) may require:
- Controlled, sustained thermal application (Class 34)
- NOT rapid venting/escape (Class 33)

### Not Interchangeable

This demonstrates that ENERGY operators are **functionally distinct** even within the same role category. Sections select specific operators based on procedural requirements.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C552 | Extended - section profiles include within-role operator selection |
| C547 | Contextualized - qo-chain (Class 33) enrichment is section-conditional |
| C551 | Refined - REGIME effects can be overridden by section requirements |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** class33_anomaly.py

---

## Navigation

<- [C554_hazard_clustering.md](C554_hazard_clustering.md) | [INDEX.md](INDEX.md) ->
