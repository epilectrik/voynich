# C894: REGIME Recovery Specialization Concentration

**Tier:** 2
**Scope:** B
**Phase:** BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (extended, reverified 2026-02-11)

## Constraint

Recovery-specialized folios (HIGH_K paragraph signature) cluster in REGIME_2 (42% vs 0-4% other REGIMEs). Chi-square = 38.73, df=6, p = 0.000001. K/(K+H) ratio differs significantly across REGIMEs (Kruskal-Wallis H=33.49, p<0.0001), with REGIME_2 at 0.683 vs 0.05-0.19 for others. The effect survives within-section confound control (Section H: Kruskal-Wallis p=0.0001).

## Reverification History

**2026-02-11: REGIME REASSIGNMENT.** The original C894 attributed recovery concentration to REGIME_4 using a broken regime mapping (two old sources agreed on only 39% of folios, kappa=0.175). Re-testing with the authoritative GMM k=4 regime mapping (data/regime_folio_mapping.json) shows the signal is **stronger** (chi2 38.73 vs 28.41) but in **REGIME_2**, not REGIME_4. The old causal chain linking precision (C494) to recovery is severed — recovery clusters with routine/frequent operations, not precision.

## Evidence

### Folio Specialization by REGIME

| REGIME | Recovery-Specialized Folios | K/(K+H) Ratio |
|--------|---------------------------|---------------|
| REGIME_2 | 42% (5/12) | 0.683 (highest) |
| REGIME_1 | 4% (1/28) | 0.188 |
| REGIME_3 | 0% (0/18) | 0.062 |
| REGIME_4 | 0% (0/12) | 0.050 (lowest) |

**Definition:** Recovery-specialized folio = >=50% HIGH_K paragraphs (>=3 paragraphs minimum)
**HIGH_K paragraph:** k-characters >35% of kernel (k+h+e)

### Statistical Tests

Chi-square test for REGIME x SPECIALIZATION:
- Chi-square = 38.73
- df = 6
- p = 0.000001

Fisher exact test (REGIME_2 vs others):
- Odds ratio = 40.71
- p = 0.0004

Kruskal-Wallis on continuous K/(K+H) ratio:
- H = 33.487
- p < 0.0001

### Confounding Analysis

The effect persists within Section H (controlling for section composition):

**Section H across REGIMEs:**
| REGIME | K/(K+H) | N folios |
|--------|---------|----------|
| REGIME_2 | 0.724 | 13 |
| REGIME_1 | 0.500 | 1 |
| REGIME_4 | 0.048 | 7 |
| REGIME_3 | 0.040 | 5 |

Kruskal-Wallis within Section H: H=18.31, p=0.0001 — REGIME effect is not section-driven.

### Recovery-Specialized Folios

| Folio | Section | REGIME | Probability |
|-------|---------|--------|-------------|
| f39v | H | REGIME_2 | 1.000 |
| f40r | H | REGIME_2 | 0.991 |
| f50r | H | REGIME_2 | 1.000 |
| f50v | H | REGIME_2 | 0.992 |
| f94r | H | REGIME_2 | 0.995 |
| f107v | S | REGIME_1 | 0.992 |

5/6 recovery-specialized folios are Herbal section in REGIME_2 (all with >0.99 regime probability).

## Interpretation

Recovery-specialized folios concentrate in REGIME_2 (routine/frequent operations), not in precision operations as originally claimed. This suggests:

1. **Recovery capacity accompanies routine operations**: The highest recovery vocabulary density occurs in the regime characterized by high frequent_rate and k_ratio — suggesting recovery mechanisms are built into standard operating procedures, not reserved for exceptional precision situations.

2. **HIGH_K paragraphs supply recovery vocabulary**: Per C893, HIGH_K paragraphs have 19.7% FQ rate vs 9.7% for HIGH_H. REGIME_2's concentration of recovery-specialized folios provides the FQ-rich vocabulary for error correction during routine operations.

3. **The precision→recovery causal chain (C494→C780→C893→C894) is SEVERED**: Recovery does not cluster with precision (REGIME_4). The old interpretation that "precision requires high recovery capacity" is not supported by the corrected regime mapping. Recovery and precision appear to be independent operational dimensions.

## Cross-Level Validation

| Level | Constraint | Finding |
|-------|------------|---------|
| Token | C780 | FQ tokens have k-rich, h-absent kernel profile |
| Paragraph | C893 | HIGH_K paragraphs concentrate FQ (recovery) |
| Folio | C894 | Recovery-specialized folios exist (6 folios) |
| REGIME | C894 | REGIME_2 concentrates recovery-specialized folios |

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C494 | DECOUPLED - recovery does NOT cluster with precision (REGIME_4) as originally claimed |
| C893 | EXTENDS - from paragraph-level to folio/REGIME aggregation |
| C780 | ALIGNS - FQ is k-rich explains HIGH_K -> recovery link |
| C636 | COMPLEMENTS - recovery pathway features vs recovery specialization concentration |

## Provenance

- Scripts: `paragraph_type_spatial_analysis.py`, `c894_reverification.py`
- Data: `results/paragraph_type_spatial.json`, `results/c894_reverification.json`
- Regime mapping: `data/regime_folio_mapping.json` (v2, GMM k=4 on 15 features)
- Phase: BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (extended 2026-01-30, reverified 2026-02-11)

## Status

REVERIFIED - Signal stronger than original (chi2=38.73 vs 28.41), but assigned to REGIME_2 instead of REGIME_4. Causal chain to C494 (precision) severed.
