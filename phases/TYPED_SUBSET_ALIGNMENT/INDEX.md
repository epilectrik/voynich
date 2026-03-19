# Phase 607: Typed Subset Alignment

## Status: COMPLETE
## Verdict: FRAMEWORK_MARGINAL

## Overview

Tests whether PL-internal co-variate structure transfers to V Stars under a specific a priori
feature mapping. Follows expert direction to abandon named-family comparison (Phases 604-606)
in favor of typed behavioral subsets.

**Two-layer design:**
- Layer A: Conservative heat-monitoring anchor (replicate C1752 within Stars)
- Layer B: Bold threshold-authenticity probe (novel mappings: termination→strong_close_fraction, judgment→checkpoint_rate)

**Key methodological innovation:** Co-variate structure transfer tests whether PL-internal
relationships between features mirror V-internal relationships between mapped features, with
N1 (mapping shuffle) and N2 (random PL subset) controls for specificity.

## Data

- 209 PL chapters (E1_chapters), 7 per-chapter behavioral rates
- 23 Stars folios with joined V features from 3 sources
- S_T strict (3-condition: term>med, judg>med, chain<med): n=6 (too small)
- S_T relaxed (2-condition: term>med, judg>med): n=37 (used)
- S_HM_hot: n=37, S_HM_mon: n=39

## Results

### Gates
| Gate | Result | Detail |
|------|--------|--------|
| C0a | PASS | S_HM_hot=37, S_HM_mon=39 (both >= 12) |
| C0b | PASS (relaxed) | S_T strict n=6 < 12; relaxed n=37 >= 12 |
| C1a | PASS (4/5) | S_T separable: monitoring (p<0.0001), correction (p=0.0055), operational (p<0.0001), chain (p<0.0001); heat (p=0.122 FAIL) |
| C1b | FAIL | A1 rho=-0.340, p=0.056 (marginal) |

### Layer A: Conservative Anchor
| ID | Test | rho | p (one-sided) | Result |
|----|------|-----|---------------|--------|
| A1 | thermo_ke vs h_ratio (negative) | -0.340 | 0.056 | FAIL (marginal) |

A1 direction is correct (negative) but p=0.056 misses threshold. C1752 confirmed this
relationship at broader scope (n=41, rho=-0.40 to -0.47). Within Stars alone (n=23),
insufficient power to reach conventional significance.

### Layer B: Threshold-Authenticity Probe
| ID | Test | rho | p (one-sided) | Result |
|----|------|-----|---------------|--------|
| P1 | strong_close_fraction vs checkpoint_rate (positive) | -0.278 | 0.901 | FAIL |
| P2 | h_ratio vs checkpoint_rate (positive) | +0.249 | 0.126 | FAIL |

**P1 is directionally wrong** (negative, not positive). This is a genuine prediction failure:
the PL co-variate (termination↔judgment positive) does NOT predict the V co-variate
(strong_close_fraction↔checkpoint_rate). The mapped features are anti-correlated in Stars.

**P2 is directionally correct** but not significant (p=0.126). Monitoring and checkpointing
show a weak positive relationship in Stars, consistent with PL's monitoring↔judgment, but
insufficient evidence at n=23.

### PL-Internal Co-variates (S_T, n=37)
| Pair | rho | p | Note |
|------|-----|---|------|
| term ↔ judg | +0.357 | 0.030 | PASS — defining co-variate exists |
| term ↔ chain | +0.324 | 0.051 | Marginal — threshold procedures ARE iterative |
| mon ↔ judg | +0.255 | 0.127 | Not significant |

S_T has the expected termination↔judgment positive co-variate (p=0.030). But term↔chain is
POSITIVE (+0.324), not negative — chapters with more termination also have more chaining.
This validates the expert's concern: threshold procedures can be iterative (C1579, C1642-C1648).

### Secondary Battery
| ID | Test | Result | Detail |
|----|------|--------|--------|
| S1 | SCF vs iteration_rate (negative) | FAIL | rho=-0.291, p=0.089 (marginal) |
| S2 | S_HM discrimination | PASS | 6/7 features differ |
| S3 | All-PL transfer | K=0 | All-PL signs predict positive but V doesn't confirm |
| S4 | S_T internal | see above | term↔judg positive confirmed |

### Negative Controls
| ID | Result | Detail |
|----|--------|--------|
| N1 | FAIL | K_obs=0, frac=1.000 (all random mappings do at least as well — moot since K=0) |
| N2 | FAIL | K_obs=0, frac=1.000 (all random subsets do at least as well — moot since K=0) |

N1/N2 are uninformative: with K_obs=0, every control trivially exceeds it.

### Exploratory
| ID | Test | Detail |
|----|------|--------|
| D1 | Kruskal-Wallis | All 7 features discriminate across subsets (all p<0.0001) |
| D2 | N1 per-prediction | P1: 9.0% of shuffles pass, P2: 13.0% of shuffles pass |

## Verdict Determination

```
C0a: PASS (Layer A subsets adequate)
C0b: PASS (relaxed S_T n=37)
C1a: PASS (S_T separable on 4/5 held-out features)
C1b: FAIL (A1 marginal, p=0.056)

Layer B: K=0 (P1 FAIL, P2 FAIL)
N1: FAIL (moot, K_obs=0)
N2: FAIL (moot, K_obs=0)
K_ctrl = 0

Verdict: FRAMEWORK_MARGINAL
```

## Key Findings

### 1. The PL→V co-variate transfer DOES NOT HOLD for novel mappings
P1 is the decisive failure: strong_close_fraction and checkpoint_rate are anti-correlated
(rho=-0.28) in Stars, directly contradicting the PL-motivated prediction of a positive
relationship. The mapping termination_rate→strong_close_fraction and judgment_rate→checkpoint_rate
is wrong or at best captures a different structural relationship than what PL's
termination↔judgment represents.

### 2. The heat-monitoring anchor is marginal within Stars
A1 (rho=-0.34, p=0.056) is in the right direction but underpowered. C1752 established this
at broader scope (n=41 across sections), but Stars alone (n=23) doesn't have enough folios
to confirm the contrast at conventional significance. This is a power issue, not a
directional failure.

### 3. S_T IS a real typed PL subset
C1a passes 4/5: threshold-authenticity chapters genuinely differ from the rest on monitoring,
correction, operational density, and chain rate. The subset definition captures a real
cluster of PL procedural behavior. The problem is not subset definition — it's that
the PL→V mapping for the novel features doesn't hold.

### 4. Threshold procedures are iterative (expert confirmed)
S4 shows term↔chain = +0.324 (positive, not negative). PL chapters with high termination
also have high chaining. This validates the expert's pre-analysis correction that "threshold
procedures can often be highly iterative" (motivating the demotion of P2 from primary).

### 5. The conservative heat-monitoring subsets are well-discriminated
S2 shows 6/7 features differ between S_HM_hot and S_HM_mon. D1 shows all 7 features
discriminate across all subsets. The PL subset framework is structurally sound — the
subsets capture real behavioral variation. What fails is the transfer to V.

## Interpretation

The typed-subset approach was the correct methodological repair after Phases 604-606, but the
specific novel feature mappings (termination→strong_close_fraction, judgment→checkpoint_rate)
are not supported. This narrows the PL→V overlap to two established axes:

- **heat ↔ thermo_ke** (C1752, marginal within Stars)
- **monitoring ↔ h_ratio** (C1752, C1755, marginal within Stars)

The remaining feature correspondences (termination/judgment/chain/correction → V features)
are either wrong (P1: directional contradiction) or unpowered (P2: p=0.126). This constrains
the interpretive scope: PL and V share thermal-monitoring procedural vocabulary, but the
threshold-authenticity dimension of PL procedure-space does not map onto V's
closure/checkpoint architecture via the proposed correspondence.

**What this does NOT invalidate:**
- C1744-C1748 (midprocess control alignment) — these operate at vocabulary/register level
- C1752 (thermal axis) — confirmed in broader scope, marginal in Stars
- C1755, C1757 (paragraph shape discrimination) — independent of feature mapping

## Constraints Registered
- C1758: Threshold-authenticity subset is internally coherent in PL (C1a 4/5 held-out features pass, term↔judg rho=+0.357 p=0.030) but its co-variate structure does NOT transfer to V Stars (P1 rho=-0.278 directional contradiction, P2 rho=+0.249 p=0.126 not significant). The novel feature mappings (termination→strong_close_fraction, judgment→checkpoint_rate) are rejected.
- C1759: Heat-monitoring anchor is marginal within Stars (A1 rho=-0.340, p=0.056). The thermal-monitoring contrast established by C1752 at broader scope (n=41) is underpowered within the Stars section alone (n=23). Not a directional failure — a power limitation that bounds where within-section co-variate transfer can be tested.
- C1760: PL threshold-authenticity procedures are iterative (term↔chain rho=+0.324, p=0.051 within S_T relaxed). Chapters with high termination also have high chaining, contradicting the pre-registered assumption that threshold procedures avoid iteration. Validates expert's pre-analysis correction (C1579, C1642-C1648).

## Script
- `scripts/typed_subset_alignment.py` (~580 lines, runtime <5s)
- Pre-registration: `PREDICTIONS.md` (SHA-256: b3d96e77acd589be48ffd8b9943b62ec8a31cf45072d20bfc4c5e92ad2646d2f)
- S_T relaxed used (2-condition, dropped chain requirement; strict n=6 < minimum 12)
