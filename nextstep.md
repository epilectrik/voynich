# Next Research Direction: Post-Variance Architecture

**Status:** OPEN — seeking new direction
**Current state:** v3.88 | 903 constraints | 62 fits | 361 phases

---

## Context

Phase 361 established **Brunschwig variance architecture alignment** (F-BRU-027). The comparison shows:

| Metric | Brunschwig | Voynich | Match? |
|--------|-----------|---------|--------|
| Process-side mean H_norm | 0.427 | Hazard CV=0.04-0.11 | Both constrained |
| Output-side mean H_norm | 0.827 | Recovery CV=0.72-0.82 | Both free |
| Variance ratio | 49.6/50.4 | 43/57 | Within 6.6pp |
| Permutation p | 0.0019 | — | Significant |
| Within/between ratio | 9.19 | C980: 66.3% free | Both dominated by within-category |

This is the first fit to test variance distributions (not just categorical mappings), establishing a sixth alignment axis alongside grammar, hazard, regime, suppression, and recovery.

Combined with Phases 357-360 (four-phase residual elimination confirming 57% design freedom), the characterization of B's variance architecture is now complete at both the internal (Voynich) and external (Brunschwig) levels.

---

## Possible New Directions

1. Consult expert on remaining characterization frontiers
2. Return to generative modeling (M2 improvements from C1034)
3. Explore Currier A / AZC structural questions
4. Application work (visualization, tools)
5. Deeper Brunschwig comparison (per-recipe parameter extraction from OCR)

---

## Pending Action

1. Consult expert on next research direction
