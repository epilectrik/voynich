# C895: Kernel-Recovery Correlation Asymmetry

**Tier:** 2
**Scope:** B
**Phase:** BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (extended)

## Constraint

Kernel characters show asymmetric correlation with FQ (recovery) density:
- k correlates **positively** with FQ (r=+0.268, p<10^-6)
- h correlates **negatively** with FQ (r=-0.286, p<10^-6)
- e shows **no correlation** (r=0.040, p=0.36)

## Evidence

Spearman correlations across 527 B paragraphs:

| Kernel | Correlation with FQ | p-value | Interpretation |
|--------|---------------------|---------|----------------|
| k% | +0.268 | < 0.000001 | Fire control requires recovery |
| h% | -0.286 | < 0.000001 | Phase monitoring substitutes for recovery |
| e% | +0.040 | 0.36 (n.s.) | Equilibration neutral |

## Interpretation

**Phase management (h) substitutes for recovery (FQ):**
- h = PHASE_MANAGER = drip timing, phase transitions
- Drip timing provides FEEDBACK about process state
- Good feedback reduces error rate, reducing recovery need

**Energy application (k) requires recovery:**
- k = ENERGY_MODULATOR = fire adjustment
- Fire control without phase feedback is error-prone
- High k paragraphs need more escape routes

This explains why FQ (escape routes) bypass h entirely (C781): recovery operations don't need phase monitoring because they're correcting failures, not performing primary processing.

## Convergent Evidence

This finding is convergent with C781:
- C781: "FQ has exactly 0% 'h'; escape routes bypass phase management using k+e only"
- C895: Corpus-wide negative h-FQ correlation (r=-0.286) confirms architectural bypass

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C103 | EXTENDS - k=ENERGY_MODULATOR now quantified with FQ correlation |
| C104 | EXTENDS - h=PHASE_MANAGER now quantified with FQ anti-correlation |
| C105 | ALIGNS - e=STABILITY_ANCHOR is recovery-neutral (r=0.04) |
| C781 | CONVERGENT - FQ bypasses h; negative correlation confirms |

## Provenance

- Script: `process_type_threshold_analysis.py`
- Data: 527 B paragraphs with kernel percentages and FQ rates
- Phase: BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (extended 2026-01-30)

## Status

CONFIRMED - Highly significant (p < 0.000001 for k and h correlations)
