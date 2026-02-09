# Phase: KERNEL_STATE_SEMANTICS

## Status: PLANNING

## Objective

Determine what k, h, e kernel states actually represent empirically, without assuming the "hazard" interpretation. Test whether the directional flow topology reflects danger-avoidance or some other structural principle.

---

## Background

### Current Model (Under Scrutiny)

The kernel operators have been labeled:
- **k** = ENERGY_MODULATOR (adjusts energy input)
- **h** = PHASE_MANAGER (manages phase transitions) — often called "hazard"
- **e** = STABILITY_ANCHOR (anchors to stable state)

The "hazard" framing assumes:
1. h represents a dangerous state
2. The 17 disfavored transitions are "failures to avoid"
3. Flow toward e is "recovery from danger"
4. h→k suppression prevents "oscillation between hazard states"

### What's Actually Observed (Tier 0-2)

1. **Directional asymmetry (C521):**
   - h→e: 7.00x elevated
   - k→e: 4.32x elevated
   - e→h: 0.00 (blocked)
   - h→k: 0.22 (suppressed)

2. **17 disfavored transitions (C109, C789):**
   - ~65% compliance (not absolute prohibition)
   - Cluster into 5 statistical groups
   - Labels are interpretive

3. **e is absorbing:**
   - Once reached, hard to leave
   - 54.7% of "recovery" paths pass through e

### Key Question

Is the k→h→e flow about:
- **(A) Hazard avoidance** — h is dangerous, must escape to e
- **(B) Sequential processing** — h is intermediate, naturally flows to e
- **(C) Energy dissipation** — k is high-energy, h is transition, e is ground state
- **(D) Something else entirely**

---

## Research Questions

### Q1: What contexts produce k, h, e tokens?

If h is truly "hazardous," we'd expect:
- h-tokens to appear in specific, constrained contexts
- h-tokens to be followed by "recovery" patterns
- h-tokens to co-occur with other "danger" indicators

If h is just "intermediate," we'd expect:
- h-tokens distributed across contexts
- h-tokens as normal part of processing flow
- No special "recovery" pattern after h

### Q2: What distinguishes the 17 disfavored transitions?

Without assuming "hazard," what do these 17 pairs have in common?
- Are they all h-adjacent?
- Are they sequence violations (wrong order)?
- Are they composition violations (wrong combination)?
- Are they positional violations (wrong line position)?

### Q3: What happens after h-tokens vs k-tokens vs e-tokens?

Trace the successor distributions:
- After h: Does the system "recover" or just continue?
- After k: Is there elevated "danger" or normal flow?
- After e: Is there stability or restart?

### Q4: Is the flow topology about energy levels?

Test the energy interpretation:
- k = high energy (input)
- h = transitional (processing)
- e = low energy (ground state)

If true:
- k→h→e would be natural energy cascade
- h→k suppression prevents "pumping energy back up"
- e→h blocking prevents "leaving ground state"

### Q5: Do the 5 "failure classes" have non-hazard interpretations?

Re-examine the 5 clusters without hazard framing:
- PHASE_ORDERING (41%) — sequence constraint?
- COMPOSITION_JUMP (24%) — compatibility constraint?
- CONTAINMENT_TIMING (24%) — timing constraint?
- RATE_MISMATCH (6%) — balance constraint?
- ENERGY_OVERSHOOT (6%) — magnitude constraint?

---

## Proposed Tests

### Test 1: Kernel Context Profiling

For each kernel operator (k, h, e), profile:
- Predecessor distribution (what comes before)
- Successor distribution (what comes after)
- Line position distribution
- Role co-occurrence (CC, EN, FL, FQ, AX)
- Section distribution
- REGIME distribution

**Null hypothesis:** All three have similar context profiles (just grammar markers)
**Alternative:** Distinct profiles suggest distinct functions

### Test 2: Disfavored Transition Decomposition

For each of the 17 disfavored pairs:
- What kernel characters are involved?
- What is the directional pattern (A→B vs B→A)?
- What roles are source and target?
- What MIDDLEs are involved?
- Is the "violation" rate consistent across contexts?

**Goal:** Find common thread without assuming hazard

### Test 3: Post-Kernel Trajectory Analysis

After k-containing tokens:
- What is the next token's kernel composition?
- How many tokens until e-containing?
- Is there a consistent "path" pattern?

After h-containing tokens:
- Same analysis
- Compare to post-k trajectory

After e-containing tokens:
- What breaks the e-state?
- How often does e lead to new k?

### Test 4: Energy Flow Model Test

If k=high, h=mid, e=low energy:
- Define energy score: E(token) = k_count - e_count (or similar)
- Track energy trajectory across lines
- Test if lines show energy dissipation pattern
- Test if "disfavored" transitions are energy-increasing

### Test 5: Alternative Framing Fit Test

Test which framing best fits the data:

| Framing | k | h | e | Prediction |
|---------|---|---|---|------------|
| Hazard | energy | danger | safety | h isolated, post-h recovery |
| Sequential | input | process | output | linear flow, h intermediate |
| Energy | high | mid | ground | energy decreases over line |
| Phase | init | active | complete | phase progression |

Score each framing against observed distributions.

### Test 6: Disfavored Transition Violation Context

When the 17 "forbidden" pairs DO occur (~35% of the time):
- What context allows the violation?
- Are violations clustered in specific folios/sections?
- Are violations associated with specific roles?
- Is there a "cost" visible in subsequent tokens?

---

## Success Criteria

Phase succeeds if we can answer:

1. **What is h?** — Hazard, intermediate, processing phase, or other?
2. **Why is h→k suppressed?** — Danger prevention, sequence enforcement, or energy conservation?
3. **What are the 17 transitions?** — Hazards, sequence violations, or compatibility constraints?
4. **Does the hazard framing add explanatory value?** — Or is a neutral framing equally good?

---

## Expected Outputs

1. **Kernel context profiles** — Empirical characterization of k, h, e usage
2. **Disfavored transition analysis** — What they have in common (without hazard assumption)
3. **Flow trajectory data** — Post-k, post-h, post-e patterns
4. **Framing comparison** — Which interpretation best fits observations
5. **Terminology recommendation** — Keep "hazard" or adopt neutral terms

---

## Constraints Potentially Affected

| Constraint | Current Framing | May Need Revision |
|------------|-----------------|-------------------|
| C104 | h = PHASE_MANAGER | Label may change |
| C107 | Kernel BOUNDARY_ADJACENT to hazards | "Hazards" may be reframed |
| C109 | 5 hazard failure classes | "Hazard" and "failure" labels |
| C110-C112 | Hazard topology properties | Terminology |
| C485 | Grammar minimality (hazard language) | Terminology |
| C521 | Kernel directional asymmetry | Interpretation |
| C601 | Hazard subgroup concentration | Terminology |
| C645 | CHSH post-hazard dominance | "Hazard" may be reframed |

---

## Phase Structure

```
phases/KERNEL_STATE_SEMANTICS/
├── README.md
├── scripts/
│   ├── t1_kernel_context_profiling.py
│   ├── t2_disfavored_transition_decomposition.py
│   ├── t3_post_kernel_trajectory.py
│   ├── t4_energy_flow_model.py
│   ├── t5_framing_fit_test.py
│   └── t6_violation_context_analysis.py
└── results/
```

---

## Epistemic Note

This phase is explicitly designed to QUESTION the hazard interpretation, not confirm it. We should be prepared for the possibility that:

1. "Hazard" is a useful metaphor that fits the data well
2. "Hazard" is misleading and should be replaced
3. The truth is somewhere in between (hazard for some, not others)

The goal is empirical clarity, not terminology change for its own sake.
