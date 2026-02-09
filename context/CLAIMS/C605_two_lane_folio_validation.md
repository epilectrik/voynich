# C605: Two-Lane Folio-Level Validation

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

> **TERMINOLOGY NOTE (2026-01-31):** "Escape density" replaced with "qo_density"
> per C397/C398 revision. QO is the energy lane (k-rich) operating hazard-distant.
> The correlation with lane balance reflects lane composition, not escape behavior.

---

## Statement

> The two-lane model (CHSH-lane vs QO-lane) validated at the folio level. Lane balance (= en_chsh_proportion * cc_daiin_fraction vs en_qo_proportion * cc_old_fraction) predicts qo_density better than ch_preference alone (|rho|=0.506 vs |rho|=0.301). Lane balance adds independent information beyond ch_preference (partial rho=-0.452, p<0.0001). Lane balance also correlates positively with ch_preference (rho=0.355, p=0.001). The two-lane model captures folio-level execution profiles better than any single PREFIX-based metric.

---

## Evidence

**Test:** `phases/SISTER_PAIR_DECOMPOSITION/scripts/sister_pair_decomposition.py`

### Lane Construction

For each folio (n=81 with complete data):
- **CHSH-lane intensity** = en_chsh_proportion * cc_daiin_fraction
- **QO-lane intensity** = en_qo_proportion * cc_old_fraction
- **Lane balance** = CHSH-lane / (CHSH-lane + QO-lane)

Lane balance ranges from 0 (pure QO) to 1 (pure CHSH). Mean=0.647, Std=0.298.

### Predictive Power

| Predictor | Target | rho | p |
|-----------|--------|-----|---|
| Lane balance | qo_density | **-0.506** | <0.0001 |
| ch_preference | qo_density | -0.301 | 0.006 |
| Lane balance | ch_preference | **0.355** | 0.001 |

Lane balance is 68% stronger than ch_preference at predicting qo_density (|rho|=0.506 vs |rho|=0.301).

### Independence Test

Partial correlation: qo_density ~ lane_balance | ch_preference: rho=-0.452, p<0.0001. Lane balance captures substantial qo_density variation that ch_preference alone cannot explain.

### Correlation Matrix (Key Pairs)

| Pair | rho | p | Bonferroni |
|------|-----|---|------------|
| qo_density ~ en_qo_proportion | **0.726** | <0.0001 | ** |
| qo_density ~ en_chsh_proportion | **-0.704** | <0.0001 | ** |
| qo_density ~ cc_daiin_fraction | **-0.431** | 0.0001 | ** |
| en_chsh ~ en_qo | **-0.988** | <0.0001 | ** |
| en_chsh ~ cc_daiin_fraction | **0.345** | 0.002 | ** |
| en_qo ~ cc_old_fraction | **0.355** | 0.001 | ** |
| cc_daiin ~ cc_old_fraction | **-0.597** | <0.0001 | ** |

The correlation structure confirms the two-lane model: EN subfamily and CC composition are tightly coupled, and their interaction predicts lane balance.

---

## Interpretation (Revised 2026-01-31)

The two-lane model — proposed as a Tier 3 interpretation in SUB_ROLE_INTERACTION — now has Tier 2 validation at the folio level. A folio's "processing profile" is captured by the balance between:

1. **CHSH lane:** Activated by CC_DAIIN, produces ch/sh-prefixed EN tokens (e-rich, 68.7%), operates hazard-adjacent
2. **QO lane:** Activated by CC_OL_D, produces qo-prefixed EN tokens (k-rich, 70.7%), operates hazard-distant

The lane balance variable (a composite of EN subfamily and CC trigger composition) is a better predictor of folio behavior than any single metric. This confirms that EN subfamily and CC triggers are not independently varying but are parts of an integrated processing architecture.

> **Note:** Original "escape routes" interpretation corrected. QO lane is the energy-intensive pathway
> operating hazard-distant, not an "escape" mechanism. The correlation reflects lane composition.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C600 | Foundation — CC trigger selectivity defines the two lanes |
| C601 | Connected — hazard concentration in CHSH explains lane → escape coupling |
| C603 | Extended — CC composition predicts EN subfamily; here the composite predicts escape |
| C604 | Complementary — C412 decomposes through REGIME; lane balance captures the residual |
| C576 | Validated — EN QO/CHSH bifurcation has functional consequences at folio level |
| C412 | Supersedes — lane balance is a more accurate predictor than ch_preference |

---

## Provenance

- **Phase:** SISTER_PAIR_DECOMPOSITION
- **Date:** 2026-01-26
- **Script:** sister_pair_decomposition.py

---

## Navigation

<- [C604_c412_regime_decomposition.md](C604_c412_regime_decomposition.md) | [INDEX.md](INDEX.md) ->
