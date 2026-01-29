# LANE_FUNCTIONAL_PROFILING

**Status:** COMPLETE | **Date:** 2026-01-27 | **Constraints:** C648-C651

## Objective

Six expert-recommended structural tests on QO/CHSH execution lane behavior, examining monitoring correlates (LINK, HT) and oscillation dynamics (REGIME stratification, post-hazard recovery, hazard entropy). Plus bonus: EN-exclusive MIDDLE distribution by lane.

All results are Tier 2 structural. Sensory interpretation deferred to INTERPRETATION_SUMMARY.md.

## Key Findings

### LINK-Lane Independence (C648)

LINK monitoring is completely lane-indifferent. QO 15.4% vs CHSH 14.7% LINK rate (chi2=0.44, p=0.506, V=0.0095). Excluding AX_FINAL: 11.0% vs 11.1% -- identical. The AX_FINAL marginal signal (p=0.052) is fully explained by C617/C599. LINK operates above lane identity.

### EN-Exclusive MIDDLE Deterministic Lane Partition (C649)

The strongest finding. 22/30 testable EN-exclusive MIDDLEs show **100% deterministic lane assignment** (13 QO-only, 9 CHSH-only, all FDR < 0.05). k/t/p-initial MIDDLEs are exclusively QO; e/o-initial MIDDLEs are exclusively CHSH. Not probabilistic -- absolute. Massively strengthens C647 (V=0.654) and C576 (Jaccard=0.133).

### Section-Driven Oscillation Rate (C650)

QO/CHSH oscillation rate is driven by section (material type), not REGIME (execution stage). Two-way permutation test: section partial eta2=0.174, p=0.024; REGIME partial eta2=0.158, p=0.069 (NS after controlling section). BIO=0.593 (highest), HERBAL=0.457 (lowest). Refines C643.

### Fast Uniform Post-Hazard Recovery (C651)

C645 replicated exactly: 75.2% CHSH first-EN post-hazard (504 events). Recovery is fast: mean 0.77 CHSH before QO return (45.1% immediate, 40.4% after one). No section (p=0.42), REGIME (p=0.18), or hazard class (p=0.12) variation. Recovery timing is unconditionally stable.

### HT Findings (Informative Nulls)

**HT at switch points:** HT appears elevated at continuations (25.2%) vs switches (17.7%), but this is an artifact of gap length -- 59.2% of gaps are zero-length, and switches have more zero-length gaps (66.9% vs 49.3%). Among non-zero gaps: 53.3% vs 49.7% (near-equal). Not a genuine HT-lane association.

**HT by lane balance:** Bivariate rho=-0.361 (p=0.001) disappears under partial correlation controlling section/REGIME/tail_pressure (r=-0.071, p=0.531). Entirely confound-driven.

### Hazard Entropy (Null)

Hazard content diversity (Shannon entropy over classes 7/30) does not predict oscillation rate. Folio-level rho=-0.20, p=0.11; partial r=-0.15, p=0.23.

## Constraints Produced

| # | Name | Tier |
|---|------|------|
| C648 | LINK-Lane Independence | 2 |
| C649 | EN-Exclusive MIDDLE Deterministic Lane Partition | 2 |
| C650 | Section-Driven EN Oscillation Rate | 2 |
| C651 | Fast Uniform Post-Hazard QO Recovery | 2 |

## Annotations to Existing Constraints

| Constraint | Annotation |
|------------|-----------|
| C576 | C649 confirms: exclusive MIDDLEs partition deterministically |
| C647 | C649 confirms: morphological signature is absolute for exclusive vocabulary |
| C643 | C650 clarifies: oscillation is section-driven, not REGIME-driven |
| C645 | Independently replicated (504 events, 75.2%). Timing in C651 |
| C608 | HT density also lane-independent (partial r=-0.071) |

## Scripts

| Script | Purpose | Results |
|--------|---------|---------|
| `scripts/lane_monitoring_correlates.py` | LINK by lane, HT at switches, HT lane balance, exclusive MIDDLEs | `results/lane_monitoring_correlates.json` |
| `scripts/lane_oscillation_dynamics.py` | REGIME oscillation, post-hazard recovery, hazard entropy | `results/lane_oscillation_dynamics.json` |

## Data Dependencies

- class_token_map.json (CLASS_COSURVIVAL_TEST)
- en_census.json (EN_ANATOMY)
- regime_folio_mapping.json (REGIME_SEMANTIC_INTERPRETATION)
