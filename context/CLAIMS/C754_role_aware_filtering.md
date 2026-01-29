# C754: Role-Aware Infrastructure Filtering

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_REASSESSMENT | **Scope:** A<>B

## Finding

A→B filtering preserves grammatical infrastructure while being harsh on auxiliary vocabulary. CORE_CONTROL tokens (daiin, k, ol) survive filtering at 95-100% regardless of A folio pool size. AUXILIARY tokens drop to 20% survival under small pools.

### Survival Rates by Pool Size Tertile

| Role | Small Pool | Large Pool | Gradient |
|------|------------|------------|----------|
| CORE_CONTROL | 94.9% | 100.0% | -5.1pp |
| FLOW_OPERATOR | 40.7% | 66.1% | -25.5pp |
| FREQUENT_OPERATOR | 46.8% | 66.8% | -20.0pp |
| ENERGY_OPERATOR | 29.1% | 53.4% | -24.2pp |
| AUXILIARY | 20.5% | 42.8% | -22.3pp |
| HT | 8.6% | 21.5% | -13.0pp |

### Statistical Confirmation

- Pool-survival correlation for CORE_CONTROL: rho = 0.152 (near-flat, always high)
- Pool-survival correlation for AUXILIARY: rho = 0.766 (steep gradient)
- McNemar test for asymmetric exclusion: chi2 = 49.02, p < 0.0001

## Implication

The filtering mechanism is "role-aware" — it unconditionally preserves the kernel control tokens that B grammar requires for operational completeness, while allowing auxiliary vocabulary to vary by A context.

This is **infrastructure preservation**, not content routing. The system guarantees that any A context provides sufficient vocabulary for B programs to execute their core control loops.

### Alignment with Existing Constraints

- C584: Near-universal pipeline purity (CC/EN/FL/FQ at 100% PP)
- C568: AX pipeline ubiquity (97.2% of A records carry AX vocabulary)
- BCSC kernel guarantees: k/h/e operators must be available

## Provenance

- Phase: AZC_REASSESSMENT
- Script: t4_exclusion_asymmetry.py
