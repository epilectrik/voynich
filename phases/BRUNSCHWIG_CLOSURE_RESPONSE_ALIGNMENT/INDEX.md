# Phase 600: BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT

**Status:** COMPLETE
**Verdict:** CLOSURE_RESPONSE_NOT_CONFIRMED (0/4)
**Constraints:** C1739–C1740
**Script:** `scripts/closure_response_alignment_test.py` (23s)
**Results:** `results/closure_response_alignment_results.json`
**Pre-registration:** `PREDICTIONS.md` (SHA-256: `eb6824e86b0cc4c08c68f7a3c2a2ed93be637bd200cc162dc78a8e23afa1898a`)

## Motivation

Phase 599 showed method-bundle taxonomy fails to predict apparatus profile shape (C1737). Expert review: the Voynich apparatus manifold encodes **control burdens**, not named devices. The strongest validated signals are in closure quality (C1632-C1648), safety substitution (C1732-C1733), and authenticity thresholds (C1644-C1648). Phase 600 tests whether historical closure demands predict these closure-response phenotypes.

## Design

### Historical Side: 3 Predictor Axes (from 431 Brunschwig recipes)
- **H1: CONTAINMENT_BURDEN** — sealing/standing keyword density from full English text (dual lexicon: strict/broad)
- **H2: OPEN_INTERVENTION** — intervention keyword density (pour/transfer/stir/remove/open)
- **H3: RECYCLE_COMPLEXITY** — max(distill_references, named_distillations × 2)

Annotation quality: H1 strict-broad Spearman = 0.744, H2 strict-broad = 0.842 (both STABLE).

### Voynich Side: 7D Closure-Response Phenotype (76 folios)
[mean_CTS, strong_close_fraction, DYE_advantage, mean_dv_magnitude, mean_ACS, ey_rate, ii_rate]

### 5 Viable Cells (same as Phase 599)
H:R2(11), H:R3(5), H:R4(9), S:R1(10), S:R3(12)

### Method-Class Prototypes (3D: H1, H2, H3)
| Class | n | H1 | H2 | H3 |
|-------|---|----|----|-----|
| SEALED_RECIRCULATION | 29 | 1.696 | 0.056 | 5.24 |
| PRECISION_CONTROLLED | 14 | 0.400 | 0.185 | 12.00 |
| GENTLE_SUSTAINED | 230 | 0.254 | 0.028 | 2.07 |
| OPEN_CYCLE_ELEVATED | 56 | 0.253 | 0.141 | 4.86 |

## Results

| Test | Metric | Result | Verdict |
|------|--------|--------|---------|
| P1 | Mantel geometry (3D→7D) | r=-0.385, p=0.866 | **FAIL** |
| P2 | Stars R1-R3 direction (4 axes) | 3/4 concordant, combined p=0.319 | **FAIL** |
| P3 | Rank concordance (3 taus) | 0/3 concordant | **FAIL** |
| P4 | Herbal R2-R4 direction (3 axes) | 0/3 concordant | **FAIL** |
| S1 | Annotation audit | H1 corr=0.744, H2 corr=0.842 | STABLE |
| S2 | Safety balance ordering | tau=0.200, p=0.817 | DISCORDANT |
| S3 | H:R3 sensitivity | P1 r=0.086 without H:R3 | FRAGILE |

**Final verdict: CLOSURE_RESPONSE_NOT_CONFIRMED (0/4)**

## Key Findings

### 1. Safety Substitution Works Within Stars (Individual Axes)
Despite P2 failing the combined 4-axis test, the safety substitution prediction succeeds at the individual axis level:
- **ey_rate**: R1=0.1823 > R3=0.1039, p=0.0003 (replicates C1735)
- **ii_rate**: R1=0.0605 < R3=0.0918, p=0.0259 (NEW — confirms C1732/C1733 safety substitution)
- **strong_close_fraction**: R1=0.2548 > R3=0.1667, p=0.168 (right direction, not significant)
- **DYE_advantage**: R1=0.0645 < R3=0.1265, p=0.999 (REVERSED — open-cycle has MORE productive disruption)

The combined permutation fails (p=0.319) because DYE reversal dilutes the concordance score; random shuffles can achieve 3/4 concordant.

### 2. H:R2 Reversal — Highest Sealed ≠ Highest Preventive Safety
H:R2 (SEALED_RECIRCULATION) was predicted to have the highest preventive safety but shows the OPPOSITE pattern:
- ey_rate = 0.0604 (LOWEST of all cells)
- ii_rate = 0.1136 (HIGHEST of all cells)
- safety_balance = -0.053 (only NEGATIVE cell)

This completely reverses the P4 predictions (0/3 concordant) and corrupts the Mantel geometry. The most "sealed" cell deploys the most transformative, not preventive, safety. This may reflect that sealed processes, when they fail, require aggressive transformative intervention (ii) rather than gradual preventive stability (e→y).

### 3. DYE Reversal — Open-Cycle Has MORE Productive Disruption
Within Stars, R3 (open-cycle) has higher DYE_advantage (0.127) than R1 (gentle sustained, 0.065). This contradicts the prediction that high containment = more productive disruption. Instead, open-cycle processes may require MORE active grammar engagement during closure events because the system is frequently disturbed.

### 4. Cross-Section Predictions Fail Comprehensively
P3 rank concordance: 0/3. The historical containment ordering (SEALED > PRECISION > GENTLE > OPEN) does not predict the Voynich ey_rate, ii_rate, or CTS ordering across sections. The method-class-to-REGIME mapping does not transfer from thermal intensity alignment to closure-response alignment.

## What This Means

The closure-demand → closure-response bridge fails at the cell-level (0/4), joining the method-bundle → apparatus-profile bridge (C1737, 0/4) and the thermal intensity 5-axis test (Phase 598d, FAIL). The Brunschwig-Voynich alignment remains limited to:

1. **Thermal intensity within Stars**: ey_rate R1>R3 (C1735, p=0.0007; replicated here p=0.0003)
2. **Safety substitution within Stars**: ii_rate R1<R3 (p=0.0259, NEW — this phase)
3. **Within-folio thermal gradient**: THERMAL→ke-depth (C1736, rho=0.303)

The cross-section and cross-REGIME predictions fail because:
- H:R2 reverses safety predictions (highest sealed ≠ highest preventive)
- DYE_advantage reverses in Stars (open-cycle > gentle sustained)
- The cell-to-method-class mapping may be structurally wrong for non-Stars cells

The annotation system itself works well (dual lexicon stable, audit sensible), and the Voynich response variables clearly differentiate cells. The failure is in the bridge between historical closure demands and Voynich closure responses at the multi-cell level.
