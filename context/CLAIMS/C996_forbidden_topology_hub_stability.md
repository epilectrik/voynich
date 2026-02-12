# C996: Forbidden Topology Concentrates at HUB-STABILITY Interface

**Tier:** 2
**Scope:** B
**Phase:** AFFORDANCE_STRESS_TEST

## Constraint

13 of 17 forbidden transitions (C109, C783) involve HUB_UNIVERSAL MIDDLEs. 5 of 17 involve STABILITY_CRITICAL MIDDLEs. No other affordance bin's MIDDLEs participate in any forbidden transition. The hazard zone is localized at the interface between universal compatibility carriers (Bin 6) and stability operators (Bin 8).

## Evidence

### Forbidden Transition Bin Mapping

| Source Bin | Target Bin | Count |
|------------|------------|-------|
| HUB_UNIVERSAL (6) → HUB_UNIVERSAL (6) | | 8 |
| HUB_UNIVERSAL (6) → STABILITY_CRITICAL (8) | | 2 |
| STABILITY_CRITICAL (8) → HUB_UNIVERSAL (6) | | 3 |
| HUB_UNIVERSAL (6) → FLOW_TERMINAL (0) | | 1 |
| FLOW_TERMINAL (0) → HUB_UNIVERSAL (6) | | 1 |
| ROUTINE_SPECIALIZED (1) → HUB_UNIVERSAL (6) | | 2 |

### Hazard MIDDLEs by Bin

15 unique MIDDLEs participate in forbidden transitions:
- **HUB_UNIVERSAL (Bin 6)**: aiin, al, ar, c*, dy, ee, ey, l, o, ol, or, r, t (11 MIDDLEs as source and/or target)
- **STABILITY_CRITICAL (Bin 8)**: edy (source + target)
- **FLOW_TERMINAL (Bin 0)**: c (source + target)
- **ROUTINE_SPECIALIZED (Bin 1)**: he (source only)

*c appears in both Bin 0 and the forbidden inventory

### Statistical Significance

- Chi-square on bin x forbidden-MIDDLE membership: chi2=3928.3, df=8, p~0
- Chi-square on bin x hazard-class membership: chi2=596.4, df=8, p=1.42e-123

### Structural Interpretation

The hazard boundary lives at the interface where "do almost anything" tokens (HUB_UNIVERSAL: highest compat_degree, broadest folio_spread) meet "lock-in equilibrium" tokens (STABILITY_CRITICAL: 0% QO, e_ratio=0.515). This is a phase-boundary hazard phenomenon: the danger zone is where maximum compatibility meets maximum stability commitment.

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C109 | EXTENDS - hazard classes now mapped to bin-level forbidden topology |
| C601 | EXTENDS - hazard sub-group concentration now localized to specific bin interface |
| C783 | EXTENDS - 17 forbidden transitions mapped to bin-pair structure |
| C645 | CONSISTENT - post-hazard CHSH dominance aligns with STABILITY_CRITICAL as hazard-adjacent |
| C995 | COMPLEMENTS - bin behavioral coherence validated; this adds forbidden-topology specificity |

## Provenance

- Script: `phases/AFFORDANCE_STRESS_TEST/scripts/t1_hazard_exposure.py`
- Data: `phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json`, `data/middle_affordance_table.json`
- Results: `phases/AFFORDANCE_STRESS_TEST/results/t1_hazard_exposure.json`
- Phase: AFFORDANCE_STRESS_TEST

## Status

VALIDATED
