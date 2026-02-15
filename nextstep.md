# Next Research Phase: AXM Run Curvature & Micro-Sequence Geometry

**Status:** READY
**Current state:** v3.86 | 902 constraints | 359 phases | Both remotes need push

---

## Context

Three consecutive phases have eliminated candidate strata for C1035's 57% irreducible AXM self-transition residual:

1. **C1035 (Phase 357):** Aggregate folio-level statistics — no signal
2. **C1036 (Phase 358):** AXM boundary transition proportions — frequency-neutral
3. **C1037 (Phase 359):** Within-AXM class composition profiles — redundant with existing predictors

**What remains:** The only untested stratum is **micro-sequential dynamics** — the temporal ordering of tokens within AXM runs. C1024 shows MIDDLE carries 0.070 bits of execution asymmetry (vs PREFIX 0.018 bits). This directional information lives in token sequences, which are not captured by composition profiles.

---

## Proposed Phase 360: AXM Run Curvature & Micro-Sequence Geometry

From external expert consultation. This is the last testable stratum before declaring the residual genuinely irreducible.

### Core Measures (from expert outline)

1. **Conditional transition entropy gradients inside AXM runs** — Does per-step entropy rise, fall, or curve as a function of position within an AXM run? Per-folio gradient slope/curvature.

2. **Signed transition imbalance within run segments** — Split each AXM run into early/middle/late segments. Compute directed transition counts (class A→B minus B→A). Do folios differ in which direction dominates?

3. **Higher-order mutual information per folio** — C969 shows CMI = 0.012 bits corpus-wide. Does per-folio CMI decomposition reveal folio-specific structure invisible in the aggregate?

4. **Local motif replication curvature** — Within AXM runs, do specific 2-grams or 3-grams (class-level) replicate at rates above/below chance? Is replication curvature folio-specific?

5. **AXM internal cycle basis weights** — Construct per-folio directed class transition graphs within AXM. Extract cycle basis. Do cycle weights differ across folios in structured ways?

6. **Per-folio MIDDLE asymmetry distribution** — C1024 shows MIDDLE asymmetry = 0.070 bits corpus-wide. Decompose per folio: does the distribution of signed MIDDLE JSD values differ across folios?

### Key Constraints

| Constraint | Relevance |
|-----------|-----------|
| C1024 | PREFIX symmetric router, MIDDLE carries execution asymmetry (0.070 bits) |
| C969 | 2nd-order alternation bias exists (CMI=0.012 bits) but small |
| C1027 | Hazard violations are structurally conditioned |
| C966 | First-order Markov sufficiency for EN lane oscillation |
| C1006 | AXM runs are diverse class sequences (mean class run = 1.054) |

---

## Pending Action

1. Consult expert on which measures to prioritize (or run all)
2. Design and execute Phase 360
