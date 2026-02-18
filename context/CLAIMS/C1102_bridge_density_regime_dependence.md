# C1102: Bridge Density REGIME Dependence

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** BRIDGE_BACKBONE_MANUSCRIPT_SURVEY (Phase 390)
**Tension with:** C979 (REGIME modulates weights not topology)

---

## Statement

Per-folio bridge MIDDLE density varies significantly by REGIME (one-way ANOVA F=16.1, p<0.0001):

| REGIME | N Folios | Mean Density | Std |
|--------|----------|-------------|-----|
| REGIME_2 | 13 | 0.738 | 0.070 |
| REGIME_4 | 14 | 0.638 | 0.108 |
| REGIME_1 | 32 | 0.578 | 0.068 |
| REGIME_3 | 17 | 0.518 | 0.112 |

This creates tension with C979, which states that REGIME modulates transition **weights** not transition **topology**. Bridge density is a vocabulary-level property (fraction of unique MIDDLEs that are bridges), which is topological rather than parametric. If C979 is correct, bridge density should be REGIME-independent.

---

## Evidence

### ANOVA
- F statistic: 16.1
- p-value: <0.0001 (reported as 0.0 at machine precision)
- 76 folios with REGIME assignments (from data/regime_folio_mapping.json)

### Possible Confound: Section
REGIME and section are partially correlated:
- REGIME_2 (highest bridge density) is heavily Herbal
- Section H has the highest bridge density (C1099: 0.697)
- The REGIME effect may be mediated by section composition

A controlled test (ANOVA with section as covariate, or within-section REGIME comparison) is needed to determine whether REGIME has an independent effect on bridge density beyond section.

---

## Implication

**If section fully explains the REGIME effect:** C979 stands — REGIME modulates weights within a section-determined topology, and bridge density is a section property that REGIME inherits through section composition.

**If REGIME has independent effect after section control:** C979 needs qualification — REGIME also modulates which vocabulary items a folio uses (not just how it transitions between them), which would mean REGIME partially determines topology.

This remains unresolved. The test is well-defined (within-section REGIME comparison) and should be performed in a follow-up phase.

---

## Provenance

- Phase: 390 (BRIDGE_BACKBONE_MANUSCRIPT_SURVEY), Test P6
- Script: `phases/BRIDGE_BACKBONE_MANUSCRIPT_SURVEY/scripts/bridge_backbone_survey.py`
- Results: `phases/BRIDGE_BACKBONE_MANUSCRIPT_SURVEY/results/bridge_backbone_survey.json`
- Related: C979, C1099, C1013
