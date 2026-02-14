# C1021: CP Factor Characterization — Tensor Factors Are Frequency-Dominated, Rank Is Continuous, Tensor-Automaton Orthogonality Is Complete

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** CP_FACTOR_CHARACTERIZATION (Phase 344)
**Extends:** C1019 (tensor rank-8 characterization), C1020 (tensor-automaton orthogonality)
**Strengthens:** C986 (frequency gradient), C1010 (macro-automaton independence confirmed at deepest level)
**Relates to:** C1007 (gatekeeper classes), C588 (suffix strata), C109 (forbidden transitions)

---

## Statement

Characterization of the rank-8 CP tensor factors (C1019) reveals that the tensor's dynamical predictive power (ΔR²=0.465) is frequency-dominated, rank-8 is not structurally special, and the tensor-automaton orthogonality is complete even under constraint filtering. Four findings:

**A. Factor 2 (rho=-0.738 with AXM) is a class-level frequency gradient.** Spearman correlation between Factor 2 class loadings and class token frequency is rho=0.854 (p<0.0001). Cosine with gatekeeper indicator (C1007) is only 0.059. Factor 2 is C986's frequency eigenmode projected onto the tensor — the AXM correlation is mediated by frequency, not by structural gating.

**B. Factor 3 (rho=0.090, AXM-orthogonal) also captures frequency.** Best structural indicator match is normalized class frequency (cosine=0.648). Factor 3 captures the frequency component decoupled from AXM dynamics — PREFIX-conditioned (ch-dominated) rather than bare-prefix frequency (Factor 2).

**C. Rank-8 is not structurally necessary.** Cross-validated cosine saturates at rank 4 (0.713), with rank 6-12 nearly identical (0.732-0.738). Dynamical ΔR² climbs smoothly from 0.293 (rank-2) to 0.481 (rank-12) with no knee at rank 8. The tensor's informational content is continuous, not quantized.

**D. Tensor-automaton orthogonality is complete under constraint filtering.** Applying forbidden/depleted transition constraints (C109) to the class similarity matrix does NOT improve macro-state recovery — constrained ARI=0.007 is WORSE than unconstrained ARI=0.050. Permutation z-score: -0.22 (below null). The tensor and macro-automaton are truly independent compressions that cannot be reconciled through constraint filtering.

---

## Evidence

### Sub-Analysis 1: Factor Semantic Identity

**All 8 factors have strong PREFIX selectivity:** Mean Gini coefficient = 0.803. Each factor loads on distinct PREFIXes:
- Factor 0: sh, ch (Gini=0.748)
- Factor 1: da, ok, sa (Gini=0.691)
- Factor 2: __BARE__ (Gini=0.796)
- Factor 3: ch, sh (Gini=0.724)
- Factor 4: qo (Gini=0.826)
- Factor 5: qo (Gini=0.916)
- Factor 6: ot, ok (Gini=0.795)
- Factor 7: qo (Gini=0.926)

**All 8 factors load dominantly on BIN 6** (the universal connector bin from affordance clustering). SUFFIX varies: Factors 4 (Y_FAMILY), 5 (IN_FAMILY), 7 (OL_FAMILY) select specific suffix strata; others default to NONE.

**Factor 2 deep dive:**
- Gatekeeper cosine: 0.059 (near zero — does NOT encode C1007 gating)
- Frequency Spearman: 0.854 (p<0.0001 — IS a frequency gradient)
- State cosines: FQ=0.586, AXM=0.420, FL_HAZ=0.259 — weights high-frequency states

**Factor 3 deep dive:**
- Best indicator: frequency (cosine=0.648)
- FQ cosine: 0.364, FL_HAZ: 0.205, CC: 0.171
- No strong alignment with any non-frequency structural dimension

**AXM correlation verification (matches C1020):**

| Factor | Spearman rho | AXM correlate? |
|--------|-------------|---------------|
| 0 | +0.545 | Yes |
| 1 | -0.602 | Yes |
| **2** | **-0.750** | **Strongest (frequency-mediated)** |
| **3** | **+0.090** | **No (AXM-orthogonal)** |
| 4 | +0.557 | Yes |
| 5 | +0.572 | Yes |
| 6 | -0.641 | Yes |
| 7 | +0.449 | Yes |

### Sub-Analysis 2: Rank Sensitivity

**Training variance by rank:**

| Rank | Variance | ΔR² | ARI vs C1010 |
|------|----------|------|-------------|
| 2 | 0.747 | 0.293 | 0.134 |
| 4 | 0.933 | 0.380 | 0.050 |
| 6 | 0.958 | 0.418 | 0.117 |
| 8 | 0.970 | 0.427 | 0.050 |
| 10 | 0.977 | 0.450 | 0.085 |
| 12 | 0.977 | 0.481 | -0.074 |

**Cross-validated cosine (20 folds, 5-folio holdout):**

| Rank | CV cosine (mean ± std) |
|------|----------------------|
| 2 | 0.638 ± 0.041 |
| 4 | 0.713 ± 0.053 |
| 6 | 0.732 ± 0.054 |
| 8 | 0.736 ± 0.054 |
| 10 | 0.736 ± 0.053 |
| 12 | 0.738 ± 0.055 |

CV saturates at rank 4. Rank 6-12 are within 0.006 of each other. No structural knee at rank 8.

**Forbidden transition compliance** does not increase monotonically with rank (Spearman rho=0.516). The tensor does not progressively encode constraint topology at higher ranks.

### Sub-Analysis 3: Constrained Consistency

- Unconstrained ARI: 0.050
- Constrained ARI (35 forbidden/depleted pairs zeroed): 0.007
- Null (1000 permutations): mean=0.015, std=0.035
- z-score: -0.22, p=0.588
- Constraint filtering made alignment WORSE, confirming complete orthogonality

---

## Interpretation

This phase resolves C1020's finding that Factor 2 has rho=-0.738 with AXM. The explanation is prosaic: Factor 2 is a class-level frequency gradient (C986), and frequency → AXM because high-frequency classes concentrate in the dominant macro-state. The tensor's ΔR²=0.465 (C1019/C1020) is largely frequency-driven.

However, this does not reduce the tensor to a trivial artifact:
1. The remaining 6 factors (|rho|>0.44 with AXM) also contribute dynamical information, and they have strong PREFIX selectivity (mean Gini=0.803).
2. Factor 3's AXM-orthogonality, combined with its frequency alignment, reveals two frequency components: one dynamics-coupled (Factor 2) and one dynamics-decoupled (Factor 3). This is structurally informative.
3. The rank-continuous finding means the tensor's information is diffuse, not concentrated at a discrete structural boundary.

The most important finding is Sub-3: constraint filtering CANNOT reconcile tensor and automaton. They are genuinely independent compressions at every level tested — unconstrained, archetype-level (C1020), HUB-level (C1020), and now constraint-filtered. The macro-automaton is not a variance structure, even partially.

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| S1 | Factor 2 loads on gatekeeper classes (cosine > 0.30) | cosine=0.059 | FAIL |
| S2 | Factor 2 is NOT frequency gradient (\|rho\| < 0.60) | rho=0.854 | FAIL |
| S3 | Factor 3 isolates known structural dimension (cosine > 0.40) | frequency cosine=0.648 | PASS |
| S4 | Factors have PREFIX selectivity (mean Gini > 0.30) | Gini=0.803 | PASS |
| R1 | Rank-8 structural boundary (ΔR² ratio 8/6 > 1.5) | ratio=1.023 | FAIL |
| R2 | CV gap rank-8 minus rank-6 > 0.05 | gap=0.004 | FAIL |
| R3 | Diminishing returns above rank-8 (ΔR² gap 10-8 < 0.03) | gap=0.023 | PASS |
| R4 | Compliance increases with rank (Spearman > 0.80) | rho=0.516 | FAIL |
| C1 | Constrained ARI > unconstrained (> 0.10) | ARI=0.007 | FAIL |
| C2 | Constrained ARI exceeds null (z > 2.0) | z=-0.22 | FAIL |
| C3 | Reconstruction variance preserved (> 0.85) | var=0.970 | PASS |

4/11 passed → FREQUENCY_ARTIFACT+FACTOR3_IDENTIFIED; RANK_CONTINUOUS; ORTHOGONAL_CONFIRMED

---

## Method

- 16,054 Currier B tokens mapped to 49 classes
- Full tensor T[20, 10, 5, 49] with 13,315 bigrams (same construction as C1019)
- Rank-8 non-negative CP via tensorly (300 iterations, tol=1e-6)
- Factor characterization: Gini coefficient, cosine similarity with structural indicators, Spearman with class frequency
- Rank sweep: CP at ranks 2, 4, 6, 8, 10, 12
- Cross-validation: 20 folds, 5-folio holdout, cosine similarity between test tensor and training reconstruction
- Constrained consistency: 35 forbidden/depleted pairs zeroed in class similarity matrix, Ward clustering, 1000 permutation null

**Script:** `phases/CP_FACTOR_CHARACTERIZATION/scripts/cp_factor_characterization.py`
**Results:** `phases/CP_FACTOR_CHARACTERIZATION/results/cp_factor_characterization.json`

---

## Verdict

**FREQUENCY_ARTIFACT+FACTOR3_IDENTIFIED; RANK_CONTINUOUS; ORTHOGONAL_CONFIRMED**: The tensor's strongest AXM predictor (Factor 2, rho=-0.750) is a class-level frequency gradient (C986, rho=0.854). Rank-8 is not structurally special (CV saturates at rank 4). Constraint filtering cannot reconcile tensor and automaton (constrained ARI=0.007 < unconstrained 0.050). The three compressions — tensor (variance), macro-automaton (topology), archetypes (dynamics) — remain irreducibly independent.
