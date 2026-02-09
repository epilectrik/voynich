# C894: REGIME_4 Recovery Specialization Concentration

**Tier:** 2
**Scope:** B
**Phase:** BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (extended)

## Constraint

Recovery-specialized folios (HIGH_K paragraph signature) cluster in REGIME_4 (33% vs 0-3% other REGIMEs). Chi-square = 28.41, p = 0.0001. This validates C494's precision interpretation at paragraph level: precision operations require high recovery capacity.

## Evidence

### Folio Specialization by REGIME

| REGIME | Recovery-Specialized Folios | K/(K+H) Ratio |
|--------|---------------------------|---------------|
| REGIME_4 | 33% (8/24) | 0.32 (highest) |
| REGIME_1 | 3% (1/31) | 0.21 |
| REGIME_2 | 0% (0/10) | 0.27 |
| REGIME_3 | 0% (0/16) | 0.10 (lowest) |

**Definition:** Recovery-specialized folio = >=50% HIGH_K paragraphs
**HIGH_K paragraph:** k-characters >35% of kernel (k+h+e)

### Statistical Test

Chi-square test for REGIME x SPECIALIZATION:
- Chi-square = 28.41
- df = 6
- p = 0.0001

### Confounding Analysis

The effect persists within sections (controlling for section composition):

**Section H across REGIMEs:**
| REGIME | K/(K+H) | HIGH_K | HIGH_H |
|--------|---------|--------|--------|
| REGIME_3 | 0.25 | 5 | 15 |
| REGIME_4 | 0.39 | 20 | 31 |

REGIME_4 has 56% higher K/(K+H) than REGIME_3 within Section H, proving the effect is not entirely section-driven.

## Interpretation

This validates C494 (REGIME_4 = precision-constrained execution) at paragraph level:

1. **Precision requires recovery capacity**: When tolerances are tight, errors are more likely. High FQ density provides grammatical escape routes for error correction.

2. **HIGH_K paragraphs supply recovery vocabulary**: Per C893, HIGH_K paragraphs have 19.7% FQ rate vs 9.7% for HIGH_H. REGIME_4's concentration of recovery-specialized folios provides the FQ-rich vocabulary needed for precision operations.

3. **The causal chain**:
   - C494: REGIME_4 = precision (lowest qo_density, highest FQ_density)
   - C780: FQ tokens are k-rich (45.8% k, 0% h)
   - C893: HIGH_K paragraphs = recovery procedures
   - **C894: Recovery-specialized folios cluster in REGIME_4**

## Cross-Level Validation

This constraint completes a multi-level validation:

| Level | Constraint | Finding |
|-------|------------|---------|
| Token | C780 | FQ tokens have k-rich, h-absent kernel profile |
| Paragraph | C893 | HIGH_K paragraphs concentrate FQ (recovery) |
| Folio | C894 | Recovery-specialized folios exist |
| REGIME | C894 | REGIME_4 concentrates recovery-specialized folios |

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C494 | VALIDATES - paragraph-level confirmation of precision interpretation |
| C893 | EXTENDS - from paragraph-level to folio/REGIME aggregation |
| C780 | ALIGNS - FQ is k-rich explains HIGH_K -> recovery link |
| C636 | COMPLEMENTS - recovery pathway features vs recovery specialization concentration |

## Provenance

- Scripts: `paragraph_type_spatial_analysis.py`, `regime_specialization_test.py`, `regime_section_confound_test.py`
- Data: `results/paragraph_type_spatial.json`, `results/regime_specialization.json`
- Phase: BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (extended 2026-01-30)

## Status

CONFIRMED - Highly significant (p=0.0001), confound-controlled
