# C1214: Line Compositional Homogeneity

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** LINE_COMPOSITIONAL_MODES (Phase 431)
**Relates to:** C1207 (atom correlation clusters), C1212 (cross-token chaining, MEDIAL co-occurrence), C1213 (axis switching), C678 (no discrete line types), C909 (section-specific MIDDLEs)

---

## Statement

Lines are mildly more compositionally homogeneous than within-folio shuffled baselines (z=-7.0, 3.8% entropy reduction). The effect is genuine (survives within-folio control and daiin exclusion z=-6.78) but modest. All three positional slots (INITIAL, MEDIAL, TERMINAL) show comparable homogeneity, indicating whole-token tuning rather than slot-specific specialization.

### Homogeneity by Slot

| Slot | N lines | Obs entropy | Shuf entropy | z-score | Reduction |
|------|---------|-------------|--------------|---------|-----------|
| INITIAL | 2,342 | 0.6260 | 0.6461 | -8.1 | 3.1% |
| MEDIAL | 1,668 | 0.7026 | 0.7306 | -7.0 | 3.8% |
| TERMINAL | 2,342 | 0.7335 | 0.7530 | -8.2 | 2.6% |

### PCA on Line Axis Profiles

The main axis of line-to-line variation is CLOSURE vs ITERATION:

| Component | Variance | Primary loadings |
|-----------|----------|------------------|
| PC1 | 36.2% | CLOSURE +0.73, ITERATION -0.67 |
| PC2 | 23.9% | STABILITY -0.70, ITERATION +0.56, CLOSURE +0.41 |

Section explains only 12.6% of PC1 variance. 87% of line variation is within-section.

### Section Mean Axis Profiles (MEDIAL)

| Section | ITER | MONITOR | ENERGY | CLOSURE | STRUCT | STABIL |
|---------|------|---------|--------|---------|--------|--------|
| BIO | 0.186 | 0.119 | 0.043 | **0.395** | 0.091 | 0.116 |
| COSMO | **0.353** | 0.118 | 0.051 | 0.205 | 0.089 | 0.140 |
| HERBAL | 0.306 | 0.096 | 0.069 | 0.230 | 0.109 | 0.138 |
| STARS | 0.285 | 0.103 | 0.044 | 0.183 | 0.122 | **0.236** |
| TEXT | 0.180 | 0.086 | 0.054 | 0.270 | 0.158 | 0.149 |

BIO is dramatically CLOSURE-heavy (0.395). COSMO is the most ITERATION-heavy (0.353). STARS is STABILITY-heavy (0.236).

### No Position Gradient

Axis profiles do NOT vary with line position within the folio. All position correlations are near zero (|r| < 0.06). This is distinct from C1206's kernel gradient, which operates at the PREFIX level (k/h/e operators), not at the MEDIAL atom level.

---

## Interpretation

Lines have a weak compositional mode — a mild preference for certain C1207 axes — but this is a small effect (3-4% entropy reduction). The dominant axis of variation (CLOSURE vs ITERATION) is consistent with C1207's strongest clusters and suggests lines mildly specialize in either referent-closing or iteration-loading operations. However, C1213's finding that tokens switch axes 85% of the time means this specialization is a slight bias, not a strong constraint. Lines remain multi-axis instruction sequences with a modest operational tilt.

The equal homogeneity across all three slots (INITIAL, MEDIAL, TERMINAL) means the tuning is at the whole-token level — when a line favors certain axes, entire tokens from those axes are selected, not just specific positional atoms.

This explains C1212's finding that MEDIAL→MEDIAL had high raw MI but low shuffle z-score: the co-occurrence signal comes from this mild whole-token compositional homogeneity, not from sequential MEDIAL-to-MEDIAL chaining.

---

## Method

- 2,416 Currier B lines, filtered to lines with >= 3 atoms at each slot
- Per-line normalized Shannon entropy (observed / max possible for line length)
- Within-folio shuffle baseline: 1000 iterations, randomly reassigning atoms across lines within the same folio
- PCA via power iteration on 8-axis line profile vectors
- Position quintiles: lines sorted within folio, assigned to 5 equal bins

**Script:** `phases/LINE_COMPOSITIONAL_MODES/scripts/line_modes_test.py` (T1-T4)
**Results:** `phases/LINE_COMPOSITIONAL_MODES/results/line_modes_results.json`
