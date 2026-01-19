# SEL-F: MONOSTATE vs 2-Cycle Contradiction Resolution

**Phase:** SEL-F (Self-Evaluation - Contradiction Resolution)
**Date:** 2026-01-07
**Updated:** 2026-01-16 (H-only transcriber filter verified)
**Status:** RESOLVED (with Tier 0 revision required)

---

## Executive Summary

| Issue | Resolution |
|-------|------------|
| 2-cycle vs MONOSTATE contradiction | **DEFINITIONAL** - they measure different things |
| "100% convergence to STATE-C" claim | **EMPIRICALLY FALSE** - only 57.8% terminate in STATE-C |
| Tier 0 stability | **REVISION REQUIRED** - weaken convergence claim |

---

## The Original Contradiction (from SEL-B)

**Claim 1 (Tier 0):** "System is fundamentally MONOSTATE" - 100% execution convergence to STATE-C

**Claim 2 (OPS-R):** "dominant_cycle_order = 2" - execution oscillates between 2 states

SEL-B flagged this as "internally inconsistent" because:
- MONOSTATE = 1 state
- 2-cycle = 2 states alternating

---

## Resolution: Two Separate Issues

### Issue A: 2-cycle vs MONOSTATE (DEFINITIONAL)

**Finding:** These terms measure DIFFERENT phenomena.

| Term | What It Measures | Algorithm |
|------|------------------|-----------|
| 2-cycle | LOCAL periodicity in token sequences | Sliding window period detection |
| MONOSTATE | GLOBAL terminal state | Last instruction classification |

**2-cycle explanation:**
- `dominant_cycle_order = 2` means tokens repeat with period ~2
- This is about pattern structure, not state oscillation
- 100% of folios have dominant_cycle_order = 2
- This reflects LOCAL compositional patterns (e.g., `ch-ol-ch-ol`)

**MONOSTATE explanation:**
- STATE-C is the target terminal state
- Measured by what instruction a folio ENDS with
- ANCHOR_STATE, CONTINUE_CYCLE, LINK = STATE-C
- SHIFT_MODE, other = "other"

**These are COMPATIBLE:**
- A system can have periodic local patterns (2-cycle)
- While converging to a global attractor (MONOSTATE)
- Like a damped oscillator: swings locally, settles globally

**Verdict:** NOT a formal contradiction. Definitional ambiguity resolved.

---

### Issue B: "100% Convergence" Claim (EMPIRICALLY FALSE)

**Finding:** The "100% convergence to STATE-C" claim is not supported by data.

| Terminal State | Count | Percentage |
|----------------|-------|------------|
| STATE-C | 48 | 57.8% |
| other | 32 | 38.6% |
| initial | 3 | 3.6% |

**Source of error:**
- Phase 13 claimed "convergence_rate: 100.0"
- This measured whether paths CAN reach stable states (theoretical)
- Phase 22B measured actual terminal states (empirical)
- The metrics are different

**What "other" terminal state means:**
- Folio ends in SHIFT_MODE or non-stabilizing instruction
- NOT necessarily incomplete or anomalous
- May represent programs that intentionally end in transition
- Or programs designed for operator intervention at end

**Folios with reset_present=True (3):**
- f50v, f57r, f82v
- These are classified as "initial" terminal state
- Consistent with RESTART_PROTOCOL identification from Phase 23

---

## Tier 0 Impact Assessment

| Claim | Status | Action |
|-------|--------|--------|
| T0-04: "100% execution convergence to STATE-C" | **FALSE** | Revise to "dominant convergence (~58%)" |
| T0-05: "System is fundamentally MONOSTATE" | **WEAKENED** | Revise to "System targets MONOSTATE" |
| T0-06: "LINK = deliberate non-intervention" | UNCHANGED | Not affected by this analysis |

---

## Revised Constraint Language

### Constraint 74 (REVISED)

**OLD:** "100% execution convergence to stable states"

**NEW:** "Dominant execution convergence to stable states (57.8% STATE-C terminal, 100% theoretical reachability)"

### Constraint 84 (REVISED)

**OLD:** "System is fundamentally MONOSTATE"

**NEW:** "System targets MONOSTATE (STATE-C) as primary attractor; 42.2% of folios terminate in transitional or initial states"

---

## Folios NOT Terminating in STATE-C (35 total)

### Terminal State = "other" (32 folios)
f26r, f31v, f34v, f39v, f40r, f40v, f41r, f43r, f43v, f46v, f50r, f55r, f57r, f66r, f75r, f76r, f76v, f79r, f79v, f82v, f95r1, f95v1, f103r, f103v, f106r, f106v, f107v, f111v, f112v, f114r, f114v, f115r, f115v, f116r

### Terminal State = "initial" (3 folios)
f50v, f57r, f82v (all have reset_present=True)

### Common Properties:
- kernel_dominance: k (all but 1)
- kernel_contact_ratio: 0.51-0.71 (normal range)
- reset_present: False (29), True (3)

**Interpretation:** These are not anomalous. They represent programs that:
1. End in transition (operator continues manually)
2. End in restart/reset state (for cycling)
3. Are designed for external completion

---

## LINK Role Clarification (TZ-5)

The SEL-B audit also flagged LINK as potentially inconsistent.

**Resolution:** LINK is a CLASS, not a contradiction.

| Definition | Context |
|------------|---------|
| "Non-intervention" | LINK doesn't change system state |
| "Class of trajectories" | Multiple surface forms with same function |
| "Participates in 2-cycle" | LINK tokens appear in periodic patterns |

These are compatible:
- LINK doesn't change STATE (non-intervention)
- LINK does appear in TOKEN sequences (participates in 2-cycle)
- 2-cycle is about token patterns, not state changes

**Verdict:** No contradiction. LINK is non-intervention at state level, periodic at token level.

---

## Final Verdict

### Contradiction Status: **RESOLVED**

| Tension Zone | Resolution |
|--------------|------------|
| TZ-2 (MONOSTATE vs 2-cycle) | **DEFINITIONAL** - different metrics |
| TZ-5 (LINK role) | **DEFINITIONAL** - state vs token level |

### Empirical Finding: **100% CONVERGENCE IS FALSE**

The "100% convergence to STATE-C" claim must be revised.

**Actual convergence:** 57.8% terminate in STATE-C

### Tier 0 Action Required:

1. **Revise Constraint 74** - Change "100%" to "dominant (~58%)"
2. **Revise Constraint 84** - Change "fundamentally MONOSTATE" to "targets MONOSTATE"
3. **Add new constraint** - Document the 42.2% non-STATE-C terminal rate

---

## Open Questions

1. **Why do some folios end in transition?**
   - Intentional design?
   - Operator-dependent completion?
   - Incomplete transcription?

2. **Are "other" terminal folios functionally different?**
   - Do they cluster by section?
   - Do they have different hazard profiles?

3. **What is the relationship between terminal state and program purpose?**
   - Do restart folios serve special function?
   - Are transition-end folios for specific materials?

---

## Files

| File | Purpose |
|------|---------|
| `monostate_2cycle_resolution.py` | Analysis script |
| `SEL_F_RESOLUTION_REPORT.md` | This document |

---

*SEL-F COMPLETE. Contradiction RESOLVED. Tier 0 revision REQUIRED.*

*Generated: 2026-01-07*
