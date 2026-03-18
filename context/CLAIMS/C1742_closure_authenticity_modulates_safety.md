# C1742: Closure Authenticity Modulates Safety Strategy

**Tier:** 2
**Phase:** SAFETY_STYLE_MODERATION (Phase 601)
**Scope:** B, closure, safety, authenticity, strong_close_fraction

## Finding

Per-folio strong_close_fraction (fraction of eligible close events that are STRONG) positively predicts safety_balance (ey_rate - ii_rate) after section control. Folios with more authentic closures sustain preventive safety (e→y); folios where closures are mostly weak/counterfeitable shift toward transformative rescue (ii).

Section-controlled partial Spearman: rho=0.304, p=0.008 (n=76).
Raw Spearman: rho=0.010, p=0.932.

The authenticity-safety link only emerges after section control — within sections, folios with higher strong_close_fraction have higher safety_balance. Between sections, the relationship is masked by section-specific closure profiles and baseline safety levels.

## What This Shows and Does Not Show

**Shows:** Closure authenticity (C1642: strong-vs-weak closure events) connects to the safety substitution architecture (C1732/C1733) via a within-section mechanism. This is not an artifact of A2 profile (which operates between families, not within sections). The P4 finding is mechanistically distinct from the A2 categorical shift (C1741): P4 operates within sections at the folio level, while C1741 operates across families. Together they identify two independent modulators of safety polarity: (1) apparatus profile (A2 vs A3, discrete) and (2) closure authenticity (continuous, within-section).

**Does NOT show:** Causal direction. Higher strong_close_fraction could cause preventive safety to be sustainable (authentic closures make e→y sufficient), or preventive safety could produce more strong closures (successful e→y tokens close well). The correlation is consistent with either direction or with a common cause (e.g., certain folio programs produce both strong closures and preventive safety due to apparatus profile or content demands).

## Key Metrics

- Section-controlled partial Spearman: rho=0.304, p=0.008 (n=76)
- Raw Spearman: rho=0.010, p=0.932
- DYE_advantage orthogonal to safety_balance: Stars rho=-0.282, p=0.204; all folios rho=0.045, p=0.702

## Provenance

- Source: `phases/SAFETY_STYLE_MODERATION/results/safety_style_moderation_results.json`
- Pre-registration: `phases/SAFETY_STYLE_MODERATION/PREDICTIONS.md`
- Depends on: C1642 (strong-vs-weak closure architecture), C1732/C1733 (safety substitution), C1741 (A2 categorical shift)
