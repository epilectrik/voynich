# C1341: Suffix Mode Is an Emergent Property

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_ASSIGNMENT (469)

## Constraint

Line suffix mode (A or B) is ~80% predictable from token composition alone, without observing actual suffixes. When each token is assigned its most common suffix category (its "modal suffix"), the resulting predicted mode matches actual mode with 80.0% accuracy (baseline 59.7%, lift 1.34x). Mode is primarily an emergent property of which MIDDLEs are on a line, not an imposed line-level property.

## Evidence

From suffix_mode_assignment.py test S4 (1,927 classified body lines):

**Prediction accuracy:**

| Metric | Value |
|--------|-------|
| Accuracy | **80.0%** (1541/1927) |
| Baseline (majority B) | 59.7% |
| Lift | 1.34x |

**Per-mode performance:**

| Mode | Precision | Recall |
|------|-----------|--------|
| A | 0.696 | 0.894 |
| B | 0.912 | 0.736 |

**Confusion matrix:**

|  | Pred A | Pred B |
|--|--------|--------|
| Actual A | 695 | 82 |
| Actual B | 304 | 846 |

Mode A recall (89.4%) is high — when a line is Mode A, its token composition almost always predicts that. Mode B has higher precision (91.2%) — when the model says B, it's almost always right.

## Interpretation

The four Phase 469 tests together establish a clear mechanistic model:

1. **Each MIDDLE has an intrinsic suffix preference** (C1338: MI ratio 11.57x)
2. **MIDDLEs are NOT locked to modes** (C1339: only 7.7% mode-locked)
3. **The same MIDDLE keeps its suffix across modes** (C1340: median JSD 0.020)
4. **Line mode emerges from token composition** (C1341: 80% accuracy)

**The generative story:** A B line is assembled from MIDDLEs. Each MIDDLE brings its own suffix preference (terminal, bare, or mixed). The aggregate suffix profile of the line determines whether it classifies as Mode A (terminal-heavy) or Mode B (bare-heavy). The mode is not imposed on tokens — it emerges from them.

The ~20% accuracy gap represents real contextual modulation: some MIDDLEs (the 23% "low selectivity" group, C1338) have flexible suffixes that respond to line-level or paragraph-level context. The opener MIDDLE selects mode (C1256, V=0.30) not by imposing mode on the line, but because the opener's own suffix preference seeds the profile that other tokens then reinforce or dilute.

This resolves the architectural puzzle of why mode proportion is FLAT across body position (C1259, rho=-0.027): the MIDDLE vocabulary pool is position-independent, so the mode emerges at the same rate everywhere.

## Provenance

- suffix_mode_assignment.json: test S4
- Synthesizes: C1338 (suffix selectivity), C1339 (mode flexibility), C1340 (suffix stability)
- Explains: C1256 (opener mode selection), C1259 (flat mode proportion), C1229 (alternating modes)
- Relates to: C1258 (parallel tracks — Mode B continuity may reflect continuity of bare-preferring MIDDLEs)

## Status

CONFIRMED — suffix mode is ~80% emergent from token composition. Identity model dominates with contextual modulation.
