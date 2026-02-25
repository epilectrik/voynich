# C1280: Hazard Concentrates in FLOW/CONTAINMENT Categories

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_B_EXECUTION (Phase 454)
**Date:** 2026-02-24

## Statement

Tokens whose MIDDLEs participate in forbidden transitions are massively FLOW-enriched (50.4% vs 8.8% safe baseline) and CONTAINMENT-enriched (11.5% vs 2.5%). THERMAL is hazard-depleted (2.6% vs 30.8%). Chi2=7227.5, V=0.560. 5,887 hazard-MIDDLE tokens vs 17,199 safe. At folio level, FLOW correlates with hazard density (rho=+0.558, p<0.001) and THERMAL anti-correlates (rho=-0.602, p<0.001).

## Architecture

- **Hazard is categorical.** The 17 forbidden transitions (C109) are not randomly distributed across categories. They concentrate overwhelmingly in FLOW and CONTAINMENT vocabulary. This maps to the physical interpretation: flow and containment operations create the dangerous state transitions that the grammar forbids.
- **THERMAL is hazard-immune.** Only 2.6% of tokens with THERMAL MIDDLEs are hazard-involved (vs 30.8% of safe tokens being THERMAL). Combined with C1277 (THERMAL→qo routing), THERMAL vocabulary is doubly protected: routed into the safe QO lane AND intrinsically non-hazardous.
- **FLOW is the hazard source.** 66.1% of FLOW-category tokens have hazard-participating MIDDLEs. CONTAINMENT is second at 61.4%. These two categories produce the forbidden transition topology.
- **V=0.560 is the strongest effect in the battery.** Category-hazard association is not subtle — it's the dominant structural relationship.

## Key Findings

| Category | Hazard Rate | Safe Rate | Hazard/Safe |
|----------|-------------|-----------|-------------|
| FLOW | 0.504 | 0.088 | 5.7x |
| CONTAINMENT | 0.115 | 0.025 | 4.6x |
| STAGING | 0.145 | 0.123 | 1.2x |
| TRANSITION | 0.142 | 0.152 | 0.9x |
| OPERATION | 0.066 | 0.180 | 0.4x |
| THERMAL | 0.026 | 0.308 | 0.08x |
| MARKING | 0.002 | 0.104 | 0.02x |
| MONITORING | 0.000 | 0.021 | 0x |

| Metric | Value |
|--------|-------|
| Chi-squared | 7227.5 |
| Cramer's V | 0.560 |
| FLOW-hazard density rho | +0.558 |
| THERMAL-hazard density rho | -0.602 |

## Provenance

- Extends C109 (5 hazard classes) with category concentration
- Extends C541/C622 (6/49 hazard-involved classes) with category mapping
- Extends C1000 (HUB sub-roles) with category classification
- Complements C1277 (THERMAL escape mediation) -- THERMAL is both qo-routed AND hazard-immune
