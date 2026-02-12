# C968: Folio Drift Is Emergent Not Intrinsic

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Within-folio QO fraction drift is not statistically significant (Spearman rho=0.059, p=0.292). Partial correlation controlling for EN density is also non-significant (rho=0.030, p=0.590). All four REGIMEs show no significant drift individually. Apparent within-folio lane drift emerges from section composition and hazard topology, not from an intrinsic within-folio dynamic. Drift is excluded from the generative model.

---

## Evidence

**Test:** `phases/LANE_OSCILLATION_CONTROL_LAW/scripts/t5_folio_drift_estimation.py`

### Overall Drift

| Metric | Value |
|--------|-------|
| Folio-quartile observations | 324 (82 folios x ~4 quartiles) |
| Raw Spearman rho (QO fraction vs quartile) | 0.059 |
| p-value | 0.292 |
| Partial rho (controlling EN density) | 0.030 |
| Partial p-value | 0.590 |

### Per-REGIME Drift

No REGIME shows significant drift. Classification: all `no_significant_drift`.

### Intrinsic vs Density-Emergent Test

Raw correlation not significant, making the intrinsic/emergent distinction moot. If any drift existed, partial correlation suggests it would be density-emergent (partial rho drops from 0.059 to 0.030).

---

## Interpretation

The generative model does not need a drift parameter. Within-folio lane balance is stationary. This simplifies the control law: lanes oscillate around a folio-specific set point determined by section and REGIME (C674), with no systematic movement across lines within a folio. This strengthens the stationary control envelope claim: the system operates at a fixed operating point per folio.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C674 | Confirmed: autocorrelation is entirely folio-driven, not sequential |
| C668 | Contextualized: observed late-folio CHSH shift is not intrinsic drift |
| C966 | Related: drift excluded from optimal model |
| C608 | Extended: no lane coherence confirmed at within-folio trajectory level |

---

## Provenance

- **Phase:** LANE_OSCILLATION_CONTROL_LAW
- **Date:** 2026-02-10
- **Script:** t5_folio_drift_estimation.py
- **Results:** `phases/LANE_OSCILLATION_CONTROL_LAW/results/t5_folio_drift.json`

---

## Navigation

<- [C967_hazard_gate_one_token_duration.md](C967_hazard_gate_one_token_duration.md) | [INDEX.md](INDEX.md) ->
