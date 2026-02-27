# C1345: Paragraph Opener Mode Weakly Propagates to Flexible MIDDLEs

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_CONTEXT (470)

## Constraint

Paragraph opener mode (A vs B) has a small but real effect on suffix choice for flexible MIDDLEs on subsequent body lines. A-opened paragraphs show slightly higher terminal fraction (38.8% vs 36.1%) and slight deviation rate difference. Cramer's V=0.048 (p=0.018), conditional MI I(suffix_cat; opener_mode | MIDDLE) = 0.016 bits. The effect is section-heterogeneous: Section C shows V=0.185, while Sections B and T show near-zero effect. Fisher-combined p=0.017.

## Evidence

From suffix_mode_context.py test T4 (4,090 non-opener flexible MIDDLE tokens):

**Opener mode suffix profiles:**

| Opener | n | terminal | bare | dev_rate |
|--------|---|----------|------|----------|
| A | 1,927 | 38.8% | 30.5% | 46.0% |
| B | 2,163 | 36.1% | 30.1% | 45.8% |

**Statistics:**

| Metric | Value |
|--------|-------|
| Chi2 | 9.5 |
| Cramer's V | 0.048 |
| Chi2 p | 0.018 |
| Conditional MI | 0.016 bits |

**Section stratification:**

| Section | n | V | p |
|---------|---|---|---|
| B | 1,517 | 0.040 | 0.494 |
| C | 296 | 0.185 | 0.014 |
| H | 647 | 0.086 | 0.152 |
| S | 1,521 | 0.074 | 0.031 |
| T | 109 | 0.030 | 0.991 |

Fisher-combined p = 0.017.

## Interpretation

The opener mode propagation effect is the weakest of the four contextual factors (conditional MI: PREFIX 0.097 > environment 0.057 > position 0.024 > opener 0.016). The effect is real but modest. In A-opened paragraphs, flexible MIDDLEs carry terminal suffix +2.7pp more than in B-opened paragraphs.

The section heterogeneity is notable: Section C (V=0.185) drives most of the effect, while Section B (the largest) shows near-zero effect (V=0.040, p=0.494). This suggests opener mode propagation is not a universal mechanism but a section-specific property — possibly reflecting Section C's higher mode-locking rate (47.2% per C1339 section breakdown).

This partially extends C1256 (opener mode selection, V=0.30): the opener selects mode at the line level but only weakly propagates that preference to individual token suffix choices on subsequent lines. The opener's effect on paragraph composition (C1256: 54% A lines in A-opened paragraphs vs 28.9% in B-opened) is primarily a compositional effect (which MIDDLEs appear), not a suffix-modulation effect.

## Provenance

- suffix_mode_context.json: test T4
- Extends: C1256 (opener mode selection — propagation to individual suffix is weak, V=0.048 vs line-level V=0.30)
- Extends: C1341 (mode emergent — opener contributes only 0.016 bits to the ~20% residual)
- Relates to: C1339 (Section C mode-locking — opener effect concentrates in Section C)

## Status

CONFIRMED (WEAK) — opener mode propagates to flexible MIDDLE suffix choice but below standard significance thresholds (p=0.018, V=0.048). Section-heterogeneous.
