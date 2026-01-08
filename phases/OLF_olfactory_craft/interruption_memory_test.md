# TEST 3: Interruption & Memory Test

**Question:** If the operator left for hours or overnight, what would they need to remember on return?

> **SPECULATIVE** — Craft-level interpretation under perfumery hypothesis.

---

## Perfumery Context

Aromatic water production runs are **long**:

- A single distillation may take 4-12 hours
- Multiple passes may extend over days
- Physical needs (meals, sleep, other duties) interrupt operation
- Memory is unreliable over long intervals

Upon return, the operator needs to know:

1. **Where am I in the process?** (early, mid, late)
2. **What was happening when I left?** (steady, transitioning, critical)
3. **Has anything changed?** (new phase, degradation, problem)
4. **What vigilance level is needed?** (active monitoring, passive waiting)

---

## Token Behavior Analysis

### CF-5: PERSISTENCE_MARKER — Run Continuity

**Structural finding:** 41 tokens form extended runs
**Mean run length:** 1.33
**Maximum run length:** 20

**Interruption-recovery function:**

If a token appears *repeatedly*, it signals: *"This is still the same phase."*

Upon return, the operator can check:
- Is the same marker still appearing? → Run continues as before
- Has the marker changed? → A transition occurred during absence

This provides **temporal continuity** without requiring explicit timestamps.

**Craft plausibility:** PLAUSIBLE
Repetition = persistence. The operator can see at a glance: *same phase, or new phase?*

### Section-Exclusive Vocabulary — Position Recovery

**Structural finding:** 80.7% of uncategorized tokens are section-exclusive

**Section-exclusive token counts:**
- Section B: 29 exclusive tokens
- Section H: 90 exclusive tokens
- Section S: 36 exclusive tokens

**Interruption-recovery function:**

If the operator returns and cannot remember which section they were working:
- Look at the tokens on the current page
- Each section has *private vocabulary*
- The tokens themselves tell you: *you are in section H, not section S*

This provides **section-level orientation** without requiring the operator to
remember anything. The book itself encodes the answer.

**Craft plausibility:** STRONGLY PLAUSIBLE
This is exactly how reference books work: context-specific markers for navigation.

### CF-1/CF-2: SECTION_BOUNDARY — Phase Orientation

**Structural finding:** Entry and exit tokens are position-specific

**Interruption-recovery function:**

Upon return, the operator can quickly determine:
- Am I seeing ESTABLISHING tokens? → Early in the section, run is still developing
- Am I seeing EXHAUSTING tokens? → Late in the section, run is winding down
- Am I seeing neither? → Mid-section, steady state

This provides **phase-within-section orientation** at a glance.

**Craft plausibility:** STRONGLY PLAUSIBLE
Combined with section vocabulary, the operator knows both *where* and *when*.

### CF-6/CF-7: CONSTRAINT_GRADIENT — Vigilance State

**Structural finding:** Tokens signal entering/exiting critical zones

**Interruption-recovery function:**

The most dangerous moment after an interruption is not knowing:
*"Am I returning to a critical phase?"*

These markers answer that question:
- APPROACHING nearby → Resume with heightened attention
- RELAXING nearby → Resume with normal monitoring
- Neither → Steady state, standard vigilance

**Craft plausibility:** HIGHLY PLAUSIBLE
This could prevent the most dangerous error: returning inattentively to a critical moment.

### Physical Structure — Quire-Aligned Pause Points

**Structural finding:** Section boundaries align with quire changes
(f32v→f33r, f48v→f49r match codicology)

**Interruption-recovery function:**

The physical structure of the book supports interruption:
- Quire ends are natural stopping points
- The operator can close the book at a quire boundary
- Upon return, they reopen to that quire
- The section-specific markers immediately orient them

**Craft plausibility:** STRONGLY PLAUSIBLE
The book is designed for *putting down and picking up*—exactly what long
operations require.

---

## Synthesis: Interruption & Memory Test

**What the token system provides:**

| Recovery Need | Token Feature | Solution |
|---------------|---------------|----------|
| Where in manuscript? | Section-exclusive vocabulary | Read tokens → know section |
| Where in section? | Position-clustered markers | ESTABLISHING/EXHAUSTING → early/late |
| Same phase or new? | Run-forming persistence | Repeated token → same phase |
| What vigilance needed? | Constraint gradient markers | APPROACHING/RELAXING → alert/calm |
| Physical pause points? | Quire-aligned structure | Close at quire → resume at quire |

**Craft-level interpretation:**

The human-track token system is **optimized for interruption recovery**:

- You don't need to *remember* where you are—the book tells you
- You don't need to *remember* what phase—the tokens indicate it
- You don't need to *remember* your vigilance state—the markers signal it

This is **precisely** what long-running, attention-demanding craft operations require.
The author anticipated that operators would leave and return, and designed
accordingly.

---

*Test 3 complete. Token behavior strongly supports interruption-recovery function.*