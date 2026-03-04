# C1384: k-Initial MIDDLE Fraction Predicts AXM Self-Transition

**Tier:** 2
**Scope:** B
**Phase:** GLOSS_PREDICTION_TESTS (Phase 495)
**Date:** 2026-03-02

## Statement

Folio-level k-initial MIDDLE fraction correlates with AXM self-transition rate at rho=+0.620 (p<0.0001, 72 folios). k is the only atom-initial with positive AXM correlation; a-initial (rho=-0.503), o-initial (rho=-0.427), and d-initial (rho=-0.411) all anticorrelate. The k-initial effect holds within sections (B rho=+0.496 p=0.011, H rho=+0.407 p=0.035). This connects sub-token morphology (MIDDLE initial atom) to folio-level macro-state dynamics through a four-level chain: k-initial → Mode A enrichment (C1382) → THERMAL category (C1309) → high AXM dwell (C1289).

## Hypothesis Tested

The crazy-expert predicted that k-initial MIDDLE fraction would positively correlate with AXM self-transition (more k = more dwell in main operational loop), based on the chain k-initial → Mode A (C1382) → THERMAL (C1309) → high AXM (C1289). Also predicted e-initial would anticorrelate (e → anti-clustering → routes out of AXM). k confirmed; e went the wrong direction (rho=+0.350, positive).

## Evidence

### T1: Atom-initial fraction vs AXM self-transition — k uniquely positive

| Atom-initial | Spearman rho | p-value | Direction |
|-------------|-------------|---------|-----------|
| k | +0.620 | <0.0001 | Positive (high dwell) |
| e | +0.350 | 0.0013 | Positive (opposite of prediction) |
| h | -0.120 | 0.255 | Not significant |
| a | -0.503 | 0.000001 | Negative (low dwell) |
| o | -0.427 | 0.00006 | Negative |
| d | -0.411 | 0.0001 | Negative |

k is the ONLY atom-initial with a positive AXM correlation. The axis is k vs {a, o, d}, not k vs e.

### T2: Within-section control — survives

| Section | n | k rho | k p |
|---------|---|-------|-----|
| B | 20 | +0.496 | 0.011 |
| C | 5 | +0.700 | 0.069 |
| H | 22 | +0.407 | 0.035 |
| S | 23 | +0.286 | 0.136 |

B and H significant within-section. S weakens (insufficient power at n=23 with reduced variance). The effect is not a section composition artifact.

### T3: e/k ratio anticorrelates

- e/k ratio vs AXM: rho=-0.323, p=0.003
- The relative balance between k and e predicts AXM dynamics even though both individually correlate positively. This is because k has a much steeper slope.

## Relationship to Existing Constraints

- **C1382** (Tier 2): k-initial MIDDLEs are 0.583x depleted in Mode B. C1384 extends this from line-level mode to folio-level dynamics — k-initial tokens don't just concentrate in Mode A lines, they predict the folio's overall AXM behavior.
- **C1289** (Tier 2): THERMAL category fraction predicts AXM self-transition (rho=+0.520). C1384 shows k-initial fraction is an even stronger predictor (rho=+0.620), suggesting k-initial is a more direct marker of the underlying process than the gloss-derived category.
- **C1309** (Tier 2): Mode A is THERMAL-enriched. C1384 completes the four-level chain: atom → mode → category → dynamics.
- **C1208** (Tier 2): k is POSITIVE carryover (state persistence). C1384 shows this carryover property manifests at folio level as AXM dwell — k-enriched folios persist longer in their main operational state.

## What the e-initial Inversion Means

The prediction was e-initial → anti-clustering → low AXM. The data shows e-initial → positive AXM (rho=+0.350). This means e-initial MIDDLEs do NOT route out of AXM as predicted. Instead, e accompanies k in high-dwell folios. This is consistent with C105 (e = STABILITY_ANCHOR, 54.7% recovery paths): e stabilizes the system WITHIN AXM rather than routing it OUT. The anti-clustering property (C1208) operates at token-to-token level, not at folio-level vocabulary composition.

The true AXM-opposing atoms are a (rho=-0.503), o (rho=-0.427), and d (rho=-0.411) — the atoms associated with continuation/apparatus/transition, not with stability.

## Origin

Prediction P13 from crazy-expert agent's third batch of gloss predictions (P12-P14). P12 (h-terminal CHSH enrichment) inverted; P14 (y-terminal paragraph-final) was null; P13 was half-confirmed (k correct, e wrong direction).
