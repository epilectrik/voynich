# C1739: Closure-Response Alignment Not Confirmed

**Tier:** 2
**Phase:** BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT (Phase 600)
**Scope:** B, apparatus, Brunschwig, closure, REGIME, safety

## Finding

Historical closure-burden features (3 axes: containment density, intervention density, recycle complexity) extracted from 431 Brunschwig 1512 recipes do not predict the geometry of Voynich folio-level closure-response phenotype (7D: CTS, strong_close_fraction, DYE_advantage, DVA, ACS, ey_rate, ii_rate) across section×REGIME cells. 0/4 pre-registered tests pass:

1. **Mantel geometry**: r=-0.385, p=0.866 (anti-concordant between 3D predicted and 7D observed inter-cell distances)
2. **Stars R1-R3 direction**: 3/4 concordant but combined p=0.319 (ey and ii individually significant, DYE reversed)
3. **Rank concordance**: 0/3 concordant (containment rank does not predict ey_rate, ii_rate, or CTS rank)
4. **Herbal R2-R4 direction**: 0/3 concordant (all directions reversed)

The annotation system is stable (dual-lexicon H1 rho=0.744, H2 rho=0.842) and the Voynich response variables differentiate cells. The failure is structural: the historical predictor model assumes a monotone mapping from containment burden to closure-response phenotype, but the Voynich closure manifold is profile- and threshold-dependent. Sealedness, closure authenticity, and safety style are not aligned on a single scalar axis (C1642-C1648, C1732-C1733).

## What This Shows and Does Not Show

**Shows:** The frozen cell-to-method-class mapping (C494, C1247, C1248) does not transfer from thermal intensity alignment to closure-response alignment. H:R2 (SEALED_RECIRCULATION) comprehensively reverses predictions — highest sealed cell has lowest ey_rate and highest ii_rate. This is not random: high containment/recirculation does not map monotonically to preventive safety. In the Voynich apparatus architecture, strongly sealed or recirculatory regimes can load onto transformative safety when closure authenticity thresholds are demanding or counterfeitability is high (C1639-C1647, C1733). The bridge's conceptual error was equating sealedness with preventive safety discipline.

**Does NOT show:** That closure-response variables are uninformative for Brunschwig alignment. Individual safety axes within Stars show strong signal (ey p=0.0003, ii p=0.026 — see C1740). The failure is in the bridge's monotone-containment assumption, not in variable quality. The Brunschwig alignment is narrower and more section-conditioned than the broad multi-cell prototype models assumed. Alternative bridge designs targeting safety-substitution style rather than scalar closure burden remain untested.

## Key Metrics

- P1 Mantel r: -0.385 (p=0.866)
- P2 concordant: 3/4 (combined p=0.319)
- P3 concordant: 0/3
- P4 concordant: 0/3
- Annotation: H1 strict-broad rho=0.744, H2 strict-broad rho=0.842

## Provenance

- Source: `phases/BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT/results/closure_response_alignment_results.json`
- Pre-registration: `phases/BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT/PREDICTIONS.md`
- Depends on: C1737 (Phase 599 negative), C1735 (thermal intensity), C1732/C1733 (safety substitution), C494 (REGIME_4 precision), C1247 (aii R3), C1248 (apparatus profiles)
