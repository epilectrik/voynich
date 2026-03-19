# Phase 604: Pre-Registration of Predictions

**Status:** FROZEN -- do not modify after SHA-256 hash is recorded.

## Pre-registered Limitation

Fixation is used as an operational proxy for recirculatory stabilization-sensitive doctrine because the direct circulation-family sample size is insufficient (n=1). Any positive match should be interpreted as alignment to a fixation/recirculation-like family rather than literal family identity.

## S1: Calibration Anchor

Stars ey_rate: R1 > R3, Mann-Whitney p < 0.05.
If FAIL: CALIBRATION_FAILURE, stop all tests.

## Stage 1: Internal Discrimination Gate

### Selected Families (operational chapters only, theory_practice != "theoretical")
- distillation (expected ~16 chapters)
- fixation (expected ~10 chapters)
- sublimation (expected ~7 chapters)
- dissolution (expected ~12 chapters)
- theoretical negative control (chapters from operational parts tagged "theoretical" or "mixed")

### 7D Signature Dimensions
monitoring_density, correction_rate, heat_rate, judgment_rate, termination_rate, chain_rate, operational_density

### Gate A (Univariate)
Kruskal-Wallis per dimension across 4 operational families.
Pass: >= 1 dimension at Bonferroni p < 0.0071 OR >= 2 dimensions at nominal p < 0.05 with consistent effect directions.

### Gate B (Multivariate)
Leave-one-out nearest-centroid classifier on 7D chapter signatures.
Pass: LOO accuracy > chance (proportion of largest family).

### Gate passes if Gate A OR Gate B passes.

## Approach A: Folio-Level Control Signature Matching

### PL->V Dimension Mapping (PRIMARY: 3D)
- monitoring_density -> h_ratio (C1744)
- correction_rate -> safety_balance (C1745, C1747)
- heat_rate -> k_ratio (C1735)

### Method
Z-score both PL and V signatures within own spaces. Cosine similarity. Assign folio to nearest family.

### Sensitivity (FULL: 5D)
Add: judgment_rate -> strong_close_fraction, chain_rate -> kernel_contact_ratio

## Approach B: Paragraph Zone Distribution Matching

### Mapping Matrix (PL 7D -> C1398 4-zone weights)
Zone 0 (THERMAL)     = 0.5 * heat_rate_z + 0.3 * operational_density_z + 0.2 * termination_rate_z
Zone 1 (CONTAINMENT) = 0.4 * correction_rate_z + 0.3 * termination_rate_z + 0.3 * judgment_rate_z
Zone 2 (ITERATION)   = 0.4 * chain_rate_z + 0.3 * operational_density_z + 0.3 * heat_rate_z
Zone 3 (MONITORING)  = 0.5 * monitoring_density_z + 0.3 * judgment_rate_z + 0.2 * correction_rate_z

Softmax-normalize to sum to 1.0 per family.
EMD distance between folio actual zone distribution and family derived profile.
Minimum 3 qualifying paragraphs per folio.

## P3: Safety Discriminant (LOAD-BEARING)

Fixation-assigned folios have lower safety_balance than distillation-assigned folios.
Mann-Whitney one-sided. Pass: p < 0.05.

## P4: Monitoring Contrast (LOAD-BEARING)

Sublimation-assigned folios have higher h_ratio than distillation-assigned folios.
Mann-Whitney one-sided. Pass: p < 0.10.

## P1: Conservative Anchor

Distillation-assigned folios enriched in Stars and/or A3.
Fisher exact test. Within-stratum: among A3, distillation-assigned have higher k_ratio.
Pass: Fisher p < 0.10 on Stars or A3, OR within-stratum p < 0.10.

## P2: Bold Target

Fixation-assigned folios enriched in A2 and/or Herbal.
Fisher exact test. Within-stratum: among Herbal, fixation-assigned have lower safety_balance.
Pass: Fisher p < 0.10 on A2 or Herbal, OR within-stratum p < 0.10.

## P5: Cross-Approach Concordance (Diagnostic)

Cohen's kappa between Approach A and Approach B assignments. Pass: kappa > 0.10.

## N1: Theoretical Negative Control

Theoretical is worst-fitting family on BOTH approaches.
Approach A: lowest mean cosine similarity.
Approach B: highest mean EMD.
Pass: worst on both.

## N2: Permutation Control

Discriminability = mean margin (best - second-best cosine) per folio.
Permute family labels 1000 times.
Pass: real discriminability > 95th percentile of null.

## Verdict Tree

```
S1 fails -> CALIBRATION_FAILURE
S1 passes:
  Stage 1 gate fails -> FAMILIES_NOT_SEPARABLE
  Stage 1 passes:
    N1 fails -> SPECIFICITY_FAILURE
    N2 fails -> ALIGNMENT_NOT_SIGNIFICANT
    Both N pass:
      (P3 or P4) + (P1 or P2) pass -> PROCEDURE_FAMILY_ALIGNMENT_CONFIRMED
      (P3 or P4) pass, P1/P2 fail -> DOCTRINAL_ALIGNMENT_WITHOUT_LOCALIZATION
      P1 + P2 pass, P3/P4 fail -> LOCALIZATION_WITHOUT_DOCTRINE
      < 2 of P1-P4 pass -> PROCEDURE_FAMILY_ALIGNMENT_NOT_CONFIRMED
    P5, D1-D5: diagnostics (no verdict impact)
```
