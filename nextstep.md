# Next Research Direction: Post-Residual Closure

**Status:** OPEN — seeking new direction
**Current state:** v3.87 | 903 constraints | 360 phases | Both remotes need push

---

## Context

The AXM self-transition residual investigation is **complete**. Four consecutive phases (357-360) systematically eliminated every candidate stratum:

| Phase | Stratum | Result |
|-------|---------|--------|
| 357 (C1035) | Aggregate folio statistics | 0/7 pass, all dR² < 0.013 |
| 358 (C1036) | AXM boundary transitions | Frequency-proportional CV |
| 359 (C1037) | Within-AXM class composition | Redundant (+0.005 LOO incr) |
| 360 (C1038) | Micro-sequential dynamics | Size artifacts after control |

**Conclusion:** The 57% residual IS the design freedom space predicted by C458 (recovery freedom CV=0.72-0.82) and C980 (66.3% free variation envelope). Each program is independently parameterized within the grammar's constraints.

**New finding from Phase 360:** AXM runs converge monotonically (entropy 3.84→2.52 bits, slope -0.248). Grammar-level invariant, not program-specific.

---

## Possible New Directions

1. Consult expert on what characterization frontiers remain
2. Return to generative modeling (M2 improvements from C1034)
3. Explore Currier A / AZC structural questions
4. Application work (visualization, tools)

---

## Pending Action

1. Consult expert on next research direction
