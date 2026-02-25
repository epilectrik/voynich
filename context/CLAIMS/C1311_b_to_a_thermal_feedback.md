# C1311: B-to-A Thermal Feedback Signal

**Tier:** 2
**Scope:** B
**Phase:** CROSS_MODE_CATEGORY_COUPLING (460)
**Date:** 2026-02-25

## Finding

B line thermal state predicts the next A line's category composition through two signals (effect sizes are small-to-moderate):

1. **ke_ratio -> MARKING**: rho=-0.198, p=0.0006 (Bonferroni significant). B lines running thermally hot are followed by A lines with LESS marking content.
2. **ke_ratio -> THERMAL**: rho=+0.176, p=0.002 (Bonferroni significant). B lines running hot are followed by A lines with MORE thermal content.

Additional supporting correlations (p < 0.05 but not Bonferroni):
- e_frac -> THERMAL: rho=+0.167, p=0.004
- k_frac -> THERMAL: rho=+0.147, p=0.011
- qo_frac -> MARKING: rho=-0.156, p=0.007

## Method

- 300 BA consecutive line pairs within paragraphs
- B line thermal variables: e_frac, k_frac, qo_frac, ke_ratio
- A line category fractions: THERMAL, STAGING, CONTAINMENT, FLOW, MARKING
- Spearman correlation with Bonferroni correction (p < 0.00625)

## Interpretation

This is a cross-mode feedback signal: B's execution state statistically predicts A's next specification. When B is running hot (high kernel engagement), the next A line shifts toward more thermal specification and away from marking/administrative content. This suggests a reactive control pattern — the specification voice adjusts its emphasis based on what the execution voice is doing.

The feedback is narrow (only ke_ratio -> MARKING and ke_ratio -> THERMAL pass Bonferroni), modest in effect size (|rho| ~0.18-0.20), and directional (B->A only; A->B thermal handoff shows no signal, p>0.3). The asymmetry is consistent with Mode A being the re-specification voice that responds to Mode B's execution state.

The BA boundary handoff pattern supports this mechanistically: TRANSITION->THERMAL dominates BA transitions at 12.0% (C1312 P4), meaning B exits through TRANSITION vocabulary and the next A line responds with THERMAL specification.

## Extends

- C1260 (B-track thermal propagation) — extends thermal state tracking into cross-mode feedback
- C1258 (parallel mode tracks) — the tracks are not independent; B feeds back to A
- C1277 (THERMAL escape is qo-mediated) — thermal variables carry the feedback signal

## Does NOT Extend

- The feedback is NOT A->B specification-to-execution routing (T2 FAIL, V=0.170, p=0.146)
- The feedback is NOT symmetric (T7: AB direction rho=0.046, p=0.43)

## Falsifiability

Would be falsified if all B thermal variables show |rho| < 0.10 with all A category fractions (no cross-mode thermal signal).

## Evidence Files

- `phases/CROSS_MODE_CATEGORY_COUPLING/results/cross_mode_category_coupling.json` (T3)
