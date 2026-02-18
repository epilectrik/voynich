# C1103: REGIME-Bridge Density Is Pure Section Confound

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** SECTION_BRIDGE_DYNAMICS (Phase 391)
**Resolves:** C1102 (bridge density REGIME dependence)
**Confirms:** C979 (REGIME modulates weights not topology)

---

## Statement

The C1102 finding that bridge density varies by REGIME (F=16.1, p<0.0001) is entirely explained by section composition. After controlling for section (B/H/S dummies), the partial correlation between bridge density and REGIME drops to r=0.0007 (p=0.995) — indistinguishable from zero.

---

## Evidence

### Raw vs Controlled Correlation
- Raw Spearman rho(bridge_density, REGIME): 0.466, p=0.0001
- Partial r(bridge_density, REGIME | section): 0.0007, p=0.995

### Mechanism: Section-REGIME Entanglement
The REGIME × section contingency table reveals near-complete confounding:

| REGIME | B (Bio) | H (Herbal) | S (Stars/Recipe) |
|--------|---------|-----------|-------------------|
| REGIME_1 | 17 | 0 | 13 |
| REGIME_2 | 0 | 1 | 5 |
| REGIME_3 | 3 | 6 | 5 |
| REGIME_4 | 0 | 15 | 0 |

REGIME_4 is exclusively Herbal (highest bridge density, C1099). REGIME_1 is Bio+Stars (lower bridge density). The REGIME-bridge effect is arithmetic: REGIME composition mirrors section composition.

---

## Implication

C979 stands without qualification. REGIME modulates transition weights, not vocabulary topology. Bridge density — the fraction of a folio's vocabulary that consists of cross-system bridge MIDDLEs — is a section property, not a REGIME property. C1102 should be read as: "bridge density varies by REGIME because REGIME and section are entangled, not because REGIME independently determines vocabulary composition."

---

## Provenance

- Phase: 391 (SECTION_BRIDGE_DYNAMICS), Test P1
- Script: `phases/SECTION_BRIDGE_DYNAMICS/scripts/section_bridge_dynamics.py`
- Results: `phases/SECTION_BRIDGE_DYNAMICS/results/section_bridge_dynamics.json`
- Related: C979, C1099, C1102
