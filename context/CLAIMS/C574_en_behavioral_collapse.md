# C574 - EN Distributional Convergence

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Statement
EN prefix families (QO and CHSH) exhibit distributional convergence: identical line positions, REGIME patterns, and right-context profiles (J-S divergence 0.0024). k=2 silhouette = 0.180. Only 2/13 distributional features distinguish QO from CHSH at p<0.05. However, the two prefix families maintain vocabulary divergence (MIDDLE Jaccard=0.133, 87% non-overlapping) and trigger divergence (chi-square=133.97, p<0.001). The prefix families are grammatically equivalent but lexically and contextually partitioned — consistent with PREFIX-MIDDLE binding (C276, C423) operating within a single execution role.

## Evidence
- Distributional convergence:
  - k=2 silhouette: 0.180
  - J-S divergence QO vs CHSH: 0.0024
  - Context prediction: 59.9% (majority baseline 55.6%, +4.3pp)
  - Section dependence: Cramer's V=0.092 (significant but weak)
  - Regime dependence: Cramer's V=0.048 (very weak)
- Vocabulary divergence:
  - MIDDLE Jaccard=0.133 (87% non-overlapping)
  - QO: 25 MIDDLEs, CHSH: 43 MIDDLEs, 8 shared
- Trigger divergence:
  - CHSH from AX/CC context; QO from EN-self/boundary
  - Chi-square=133.97, p<0.001

## Interpretation
Two PREFIX channels serve as different entry points into identical distributional behavior. They carry different MIDDLE subvocabularies (C576) and are triggered by different contexts (C580), but once placed, they behave identically. This instantiates C276 (MIDDLE is PREFIX-BOUND) and C423 (PREFIX-bound vocabulary domains) within a single role, and parallels C506.b (positionally compatible but behaviorally distinct) at the PREFIX level.

## Source
Phase: EN_ANATOMY (Script 3: en_subfamily_test.py)

## Related
C276 (MIDDLE is PREFIX-BOUND), C423 (PREFIX-bound vocabulary domains), C506.b (intra-class heterogeneity), C572 (AX collapse), C573, C576, C577, C580
