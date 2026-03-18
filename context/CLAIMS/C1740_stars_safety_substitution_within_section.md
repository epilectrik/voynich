# C1740: Stars Safety Substitution Within-Section Concordance

**Tier:** 2
**Phase:** BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT (Phase 600)
**Scope:** B, Stars, safety, e-to-y, ii, REGIME, Brunschwig

## Finding

Within Stars section, the predicted safety substitution pattern holds at the individual axis level:

| Axis | S:R1 (gentle) | S:R3 (open-cycle) | Predicted | Match | p |
|------|--------------|-------------------|-----------|-------|---|
| ey_rate | 0.1823 | 0.1039 | R1 > R3 | YES | 0.0003 |
| ii_rate | 0.0605 | 0.0918 | R1 < R3 | YES | 0.0259 |
| strong_close_fraction | 0.2548 | 0.1667 | R1 > R3 | YES | 0.168 |
| DYE_advantage | 0.0645 | 0.1265 | R1 > R3 | NO | 0.999 |

The ey_rate result replicates C1735 (p=0.0007 in Phase 598; p=0.0003 here). The ii_rate result is NEW and significant: gentle sustained REGIMEs deploy less transformative safety than open-cycle REGIMEs, consistent with C1732/C1733 safety substitution architecture.

## What This Shows and Does Not Show

**Shows:** The Brunschwig thermal/operational intensity alignment (C1735/C1736) extends to the transformative safety axis (ii). Within Stars, gentle sustained processes (R1) use more preventive safety (e→y) while open-cycle elevated processes (R3) use more transformative safety (ii). This is the first direct confirmation that the safety substitution model (C1732/C1733) aligns with the historical Brunschwig operational framework.

**Does NOT show:** That this extends beyond Stars. The Herbal cross-REGIME test (P4) fails 0/3 — H:R2 reverses predictions. The within-Stars safety signal does not generalize to a multi-section closure-response bridge. DYE_advantage also reverses within Stars (open-cycle has MORE productive disruption), suggesting process quality and safety style are orthogonal dimensions.

## Significance

The safety substitution alignment strengthens the Brunschwig-Voynich connection at the within-section level:
- C1735: ey_rate differentiates REGIMEs (thermal intensity) — Phase 598
- C1740: ii_rate differentiates REGIMEs (safety substitution) — Phase 600
- C1736: THERMAL→ke-depth within folios — Phase 598

All three operate within-section or within-folio. No cross-section bridge has succeeded (C1737, C1739).

## Key Metrics

- ey_rate: Stars R1=0.1823 vs R3=0.1039 (p=0.0003, Mann-Whitney)
- ii_rate: Stars R1=0.0605 vs R3=0.0918 (p=0.0259, Mann-Whitney)
- DYE_advantage: Stars R1=0.0645 vs R3=0.1265 (REVERSED)
- Combined 4-axis permutation: p=0.319 (fails due to DYE reversal)

## Provenance

- Source: `phases/BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT/results/closure_response_alignment_results.json`
- Depends on: C1735 (ey_rate within Stars), C1732 (ey-ii folio anti-correlation), C1733 (safety substitution architecture), C1247 (aii R3 specificity)
